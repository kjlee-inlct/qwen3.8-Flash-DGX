"""Guarded, source-only generic model-container lifecycle transaction.

Production dispatch is intentionally NOT released. CPU/Fake-DGX tests use
_run_transaction with an injected backend; there is no CLI override of this
release gate. Historic P3 receipts, model images and HF cache are untouched.
"""
from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager import p3_persistent_switch as p3
from scripts.manager import recipe_drift as drift

ROOT = Path.home() / ".local/state/blazux-wizard/model-lifecycle"
PRODUCTION_LIFECYCLE_RELEASED = False
ACK_DOWNTIME = "I_APPROVE_DGX_MODEL_LIFECYCLE_DOWNTIME"
ACK_REMOVE = "I_APPROVE_CONTAINER_ONLY_REMOVAL_KEEP_IMAGES_AND_CACHE"
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _blocked(*issues: str) -> dict:
    return {"status": "BLOCKED", "issues": sorted(set(issues)),
            "executed": False, "approval_accepted": False,
            "production_released": False}


def approval_valid(preview: dict, model: str, action: str, plan_id: str,
                   downtime: str, removal: str | None, *,
                   now: float, tty: bool) -> bool:
    """Exact fresh SHA, separate real TTY and destructive-action consent."""
    return bool(
        tty and isinstance(plan_id, str) and SHA256.fullmatch(plan_id)
        and preview.get("model") == model
        and preview.get("requested_action") == action
        and preview.get("status") == "READY_FOR_OPERATOR_REVIEW_ONLY"
        and preview.get("plan_id") == plan_id
        and isinstance(preview.get("expires_at_epoch_seconds"), int)
        and 30 < preview["expires_at_epoch_seconds"] - now <= drift.PLAN_WINDOW_SECONDS
        and not preview.get("issues")
        and downtime == ACK_DOWNTIME
        and (action != "remove" or removal == ACK_REMOVE)
    )


class DockerBackend:
    """Concrete Docker adapter, unreachable from normal CLI until live release.

    Only container-level verbs are permitted. Never Docker prune, image rm,
    volume rm, HF cache write, or model download. The pinned 27B launcher is
    reused rather than maintaining a second command source.
    """

    def __init__(self, *, run=gpu.call, inspect=gpu.docker_info):
        self.run = run
        self.inspect = inspect

    def _call(self, argv: list[str], timeout: int = 90) -> None:
        if argv[:2] not in (
                ["docker", "stop"], ["docker", "start"], ["docker", "rename"],
                ["docker", "rm"], ["docker", "run"]):
            raise ValueError("UNSUPPORTED_DOCKER_MUTATION")
        result = self.run(argv, timeout=timeout)
        if result.returncode:
            raise RuntimeError("DOCKER_MUTATION_FAILED:" + argv[1])

    def exists(self, name: str) -> bool:
        from scripts.manager.p2_27b_tool_variant import _run_names
        return name in _run_names(self.run, all_containers=True)

    def running(self, name: str) -> bool:
        return gpu.running(name, self.run)

    def stop(self, name: str) -> None:
        self._call(["docker", "stop", "--time", "45", name])
        if self.running(name):
            raise RuntimeError("STOP_NOT_CONFIRMED")

    def start(self, name: str) -> None:
        self._call(["docker", "start", name])
        if not self.running(name):
            raise RuntimeError("START_NOT_CONFIRMED")

    def rename(self, old: str, new: str) -> None:
        self._call(["docker", "rename", old, new])
        if self.exists(old) or not self.exists(new):
            raise RuntimeError("RENAME_NOT_CONFIRMED")

    def remove(self, name: str) -> None:
        if self.running(name):
            raise ValueError("RUNNING_CONTAINER_RM_DENIED")
        self._call(["docker", "rm", name])
        if self.exists(name):
            raise RuntimeError("REMOVE_NOT_CONFIRMED")

    def port_free(self) -> bool:
        return gpu.port_free(self.run)

    def exclusive(self, name: str) -> bool:
        from scripts.manager import p3_persistent_switch as sw
        return not sw._gpu_conflicts(name, self.run, self.inspect)

    def create(self, *, name: str, recipe: dict,
               cache_source: str, plan_id: str) -> None:
        from scripts.manager.p2_27b_recipe_migration import _candidate
        if name != "qwen38-27b" or recipe.get("recipe_id") != "qwen38-27b":
            raise ValueError("ONLY_QUALIFIED_27B_LAUNCH_ADAPTER_PRESENT")
        if not cache_source.startswith("/"):
            raise ValueError("UNPINNED_CACHE_SOURCE")
        argv = _candidate(recipe, Path(cache_source),
                          recipe["runtime"]["local_image_id"], plan_id)
        self._call(argv)

    def verify(self, model: str) -> bool:
        from scripts.manager.service_status import inspect_live_status
        from scripts.manager.operational_probe import verify_chat
        from scripts.manager.p2_27b_tool_calling import probe as tools
        from scripts.manager.p2_27b_tool_streaming import probe_stream
        from scripts.manager.service_manifest import policy
        desc = policy()["models"][model]
        if not gpu.wait_for(desc["container_name"], desc["served_id"], 600, run=self.run):
            return False
        live = inspect_live_status()
        if (live.get("status") != "LIVE_SERVICE_VERIFIED"
                or live.get("observed_model") != model
                or live.get("expected_served_id") != desc["served_id"]
                or live.get("issues")
                or not verify_chat(desc["served_id"])):
            return False
        if model == "27b":
            tool = tools()
            stream = probe_stream()
            return bool(tool.get("status") == "LOCAL_STRUCTURED_TOOL_CYCLE_PASS"
                        and tool.get("structured_tool_call") is True
                        and tool.get("tool_result_continuation") is True
                        and stream.get("status") == "LOCAL_STREAMED_TOOL_CALL_PASS"
                        and stream.get("streamed_tool_call") is True)
        return True

    def benchmark(self, model: str) -> bool:
        if model != "27b":
            raise ValueError("MODEL_BENCHMARK_ADAPTER_NOT_QUALIFIED")
        from scripts.manager.p2_27b_recipe_migration import _canonical_benchmark
        result = _canonical_benchmark()
        return bool(result.get("status") == "PASS"
                    and result.get("model") == "qwen3.8-27b"
                    and result.get("requests") == 3
                    and len(result.get("samples") or []) == 3
                    and all(x.get("success") is True for x in result["samples"]))


def _run_transaction(preview: dict, backend: Any, recipe: dict,
                     cache_source: str | None, *,
                     record: Callable[[str, dict], None] = lambda phase, data: None
                     ) -> dict:
    """Purely orchestrated state machine: tests inject Fake-DGX backend.

    The original active service is recovered on a failed start or recreate.
    A new, verified backup is intentionally preserved after successful
    recreation; cleanup requires a DIFFERENT independently approved operation.
    """
    model = preview["model"]
    action = preview["requested_action"]
    decision = preview["decision"]
    target = preview["container_name"]
    source_model = preview.get("active_model")
    from scripts.manager.service_manifest import policy
    source = (policy()["models"][source_model]["container_name"]
              if source_model is not None else None)
    plan_id = preview["plan_id"]
    backup = target + "-rollback-" + plan_id[:12]
    failed = target + "-failed-" + plan_id[:12]
    original_running = bool(preview.get("running"))
    source_was_stopped = False
    target_was_stopped = False
    renamed = False
    created = False
    result = {
        "status": "BLOCKED", "issues": [], "model": model,
        "decision": decision, "plan_id": plan_id,
        "executed": False, "restored_original": False,
        "backup_retained": False, "backup_name": None,
        "removed_model_image": False, "removed_hf_cache": False,
        "historical_p3_receipts_modified": False,
    }

    if decision == "NOOP":
        return {**result, "status": "NO_CHANGE", "executed": False}
    if decision in ("INSTALL", "RECREATE") and not cache_source:
        return {**result, "issues": ["TRUSTED_HF_CACHE_SOURCE_REQUIRED_FOR_CREATION"]}
    if decision not in (
            "STOP", "REMOVE_STOPPED", "REMOVE_ACTIVE", "START_EXISTING",
            "RESTART_EXISTING", "INSTALL", "RECREATE"):
        return {**result, "issues": ["UNSUPPORTED_LIFECYCLE_DECISION"]}
    if backend.exists(backup) or backend.exists(failed):
        return {**result, "issues": ["UNRECONCILED_BACKUP_OR_FAILED_NAME_EXISTS"]}

    try:
        record("BEGIN", {"source": source, "target": target, "decision": decision})
        if decision in ("REMOVE_STOPPED", "REMOVE_ACTIVE", "STOP"):
            if decision in ("REMOVE_ACTIVE", "STOP") and original_running:
                record("STOPPING_TARGET", {"name": target})
                backend.stop(target)
                target_was_stopped = True
            if decision.startswith("REMOVE"):
                record("REMOVING_CONTAINER_ONLY", {"name": target})
                backend.remove(target)
                if backend.exists(target):
                    raise RuntimeError("TARGET_REMOVE_NOT_CONFIRMED")
            record("COMPLETE", {"decision": decision})
            return {**result, "status": "PASS", "executed": True}

        if source is not None and source != target:
            record("STOPPING_ACTIVE_SOURCE", {"name": source})
            # Mark intent before the side effect: Docker may stop the source
            # and then report a timeout/error. Reconcile actual state below.
            source_was_stopped = True
            backend.stop(source)
        if original_running and decision in ("RESTART_EXISTING", "RECREATE"):
            record("STOPPING_TARGET", {"name": target})
            # A partially completed stop must still be considered in recovery.
            target_was_stopped = True
            backend.stop(target)
        if not backend.port_free():
            raise RuntimeError("HOST_PORT_8000_NOT_FREE")
        if decision == "RECREATE":
            record("PRESERVING_ROLLBACK_BACKUP", {"name": backup})
            backend.rename(target, backup)
            renamed = True
        if decision in ("RECREATE", "INSTALL"):
            record("CREATING_CANONICAL_CONTAINER", {"name": target})
            # A failed docker run may leave a partial named candidate.
            backend.create(name=target, recipe=recipe,
                           cache_source=cache_source, plan_id=plan_id)
            created = True
        else:
            record("STARTING_EXISTING_CONTAINER", {"name": target})
            backend.start(target)
        if not backend.exclusive(target):
            raise RuntimeError("MULTIPLE_GPU_MODELS_AFTER_START")
        record("VERIFYING_TARGET", {"name": target})
        if not backend.verify(model):
            raise RuntimeError("TARGET_API_CHAT_TOOLS_UNVERIFIED")
        if decision in ("RECREATE", "INSTALL"):
            record("BENCHMARKING_NEW_CONTAINER", {"name": target})
            if not backend.benchmark(model):
                raise RuntimeError("NEW_CONTAINER_BENCHMARK_FAILED")
        record("COMMITTED", {"name": target, "backup_retained": renamed})
        return {**result, "status": "PASS_BACKUP_RETAINED" if renamed else "PASS",
                "executed": True, "backup_retained": renamed,
                "backup_name": backup if renamed else None}
    except (OSError, ValueError, RuntimeError, TypeError, KeyError) as exc:
        reason = "LIFECYCLE_ERROR:" + type(exc).__name__ + ":" + str(exc)
        record("ROLLBACK_STARTED", {"reason": reason})
        try:
            if decision in ("INSTALL", "RECREATE"):
                if backend.exists(target):
                    if backend.running(target):
                        backend.stop(target)
                    # Keep failed candidates for analysis, not Docker rm.
                    backend.rename(target, failed)
                if renamed:
                    backend.rename(backup, target)
                    if original_running:
                        if not backend.running(target):
                            backend.start(target)
                        if not backend.verify(model):
                            raise RuntimeError("ORIGINAL_MODEL_RESTORE_VERIFY_FAILED")
            elif decision in ("START_EXISTING", "RESTART_EXISTING"):
                # A partially successful start must be STOPPED before the
                # previous GPU model is recovered. Never leave two GPU owners.
                if backend.exists(target) and backend.running(target):
                    backend.stop(target)
                if target_was_stopped and backend.exists(target):
                    if not backend.running(target):
                        backend.start(target)
                    if not backend.verify(model):
                        raise RuntimeError("TARGET_RESTART_RECOVERY_VERIFY_FAILED")
            elif decision.startswith("REMOVE") and not backend.exists(target):
                # Removal is irreversible at the container level. Never label
                # an absent original as successfully restored.
                raise RuntimeError("CONTAINER_REMOVED_CANNOT_ROLL_BACK")
            elif target_was_stopped and backend.exists(target):
                if not backend.running(target):
                    backend.start(target)
                if not backend.verify(model):
                    raise RuntimeError("TARGET_RESTART_RECOVERY_VERIFY_FAILED")
            if source_was_stopped and source is not None:
                if not backend.running(source):
                    backend.start(source)
                if not backend.verify(source_model):
                    raise RuntimeError("PRIOR_ACTIVE_SERVICE_RECOVERY_VERIFY_FAILED")
            # An unsuccessful first INSTALL may have no previously active
            # service at all. Retaining a failed candidate is not restoration.
            prior_service_preserved = bool(
                (renamed and backend.exists(target))
                or (source_was_stopped and source is not None
                    and backend.running(source))
                or (target_was_stopped and backend.exists(target)
                    and (not original_running or backend.running(target))))
            if not prior_service_preserved:
                record("NO_PRIOR_SERVICE_TO_RESTORE", {"reason": reason})
                return {**result, "status": "FAIL_NO_PRIOR_SERVICE_TO_RESTORE",
                        "executed": True, "restored_original": False,
                        "issues": [reason]}
            record("RESTORED", {"reason": reason})
            return {**result, "status": "FAIL_RESTORED", "executed": True,
                    "restored_original": True, "issues": [reason]}
        except (OSError, ValueError, RuntimeError, KeyError) as restore_exc:
            detail = "ROLLBACK_UNCERTAIN:" + type(restore_exc).__name__ + ":" + str(restore_exc)
            record("RECOVERY_UNCERTAIN", {"cause": reason, "recovery": detail})
            return {**result, "status": "RECOVERY_UNCERTAIN", "executed": True,
                    "issues": [reason, detail]}


def execute(model: str, action: str, plan_id: str, downtime_ack: str,
            removal_ack: str | None = None, *,
            planner: Callable[..., dict] = drift.plan,
            clock: Callable[[], float] | None = None,
            root: Path = ROOT, backend: Any | None = None) -> tuple[int, dict]:
    """Production entrypoint; no override until independently accepted release."""
    if not PRODUCTION_LIFECYCLE_RELEASED:
        return 3, _blocked("PRODUCTION_LIFECYCLE_NOT_RELEASED")
    # Source for a future qualified release. No CLI path currently calls this.
    import time
    tick = time.time() if clock is None else clock()
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return 3, _blocked("REAL_OPERATOR_TTY_REQUIRED")
    from scripts.manager.operational_switch import ROOT as OP_ROOT
    from scripts.manager.p2_27b_recipe_migration import ROOT as MIG_ROOT
    locks = []
    try:
        for location in (OP_ROOT, MIG_ROOT, root):
            p3._private_dir(location)
        for location, filename in (
                (OP_ROOT, "operating-execution.lock"),
                (MIG_ROOT, "recipe-migration.lock"),
                (root, "lifecycle-execution.lock")):
            fd = os.open(location / filename,
                         os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            locks.append(fd)
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        for attempt in root.glob("attempt-*.json"):
            if not (root / attempt.name.replace("attempt-", "result-")).exists():
                return 3, _blocked("UNRECONCILED_PREVIOUS_ATTEMPT")
        fresh = planner(model, action)
        if not approval_valid(fresh, model, action, plan_id, downtime_ack,
                              removal_ack, now=tick, tty=True):
            return 3, _blocked("STALE_PLAN_OR_INSUFFICIENT_EXPLICIT_APPROVAL")
        recipe, sha = drift.load_desired(model)
        if sha != fresh["recipe_sha256"]:
            return 3, _blocked("RECIPE_CHANGED_DURING_APPROVAL")
        cache_source = ((fresh.get("observed") or {}).get("hf_cache_source")
                        or (fresh.get("desired") or {}).get("hf_cache_source"))
        if fresh["decision"] in ("RECREATE", "INSTALL") and not cache_source:
            return 3, _blocked("TRUSTED_HF_CACHE_SOURCE_REQUIRED")
        p3._write_once(root, "attempt-" + plan_id + ".json", {
            "plan_id": plan_id, "action": action, "model": model,
            "recipe_sha256": sha, "utc": datetime.now(timezone.utc).isoformat(),
        })
        events = []
        def record(phase: str, detail: dict) -> None:
            number = len(events) + 1
            doc = {
                "plan_id": plan_id, "seq": number, "phase": phase,
                "detail": detail, "previous_hash": events[-1] if events else None,
            }
            doc["hash"] = drift._digest(doc)
            p3._write_once(root, f"event-{plan_id}-{number:04d}.json", doc)
            events.append(doc["hash"])
        out = _run_transaction(fresh, backend or DockerBackend(), recipe,
                               cache_source, record=record)
        out["last_event_hash"] = events[-1] if events else None
        p3._write_once(root, "result-" + plan_id + ".json", out)
        return (0 if out["status"] in ("PASS", "PASS_BACKUP_RETAINED", "NO_CHANGE")
                else 3), out
    except (OSError, ValueError, RuntimeError, TypeError, KeyError) as exc:
        return 3, _blocked("LIFECYCLE_TRANSACTION_UNCERTAIN:" + type(exc).__name__)
    finally:
        for fd in reversed(locks):
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)
