"""Source-only operating-switch executor under independent exact approval.

NOT WIRED to Wizard CLI/TTY until real DGX operator trial separately approves
the release gate. CPU Fake-DGX callers exercise this with dependency injection.
Do not reuse, rewrite or re-run the immutable P3 A/B/C stage state machine.
"""
from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager import p3_persistent_switch as p3
from scripts.manager.operational_switch import make_plan, READY, ROOT, SUPPORTED
from scripts.manager.service_status import inspect_live_status

ACK_DOWNTIME = "I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME"
ACK_TARGET = {
    "flash-next": "I_APPROVE_FLASH_NEXT_AS_ACTIVE_MODEL",
    "27b": "I_APPROVE_27B_AS_ACTIVE_MODEL",
}


def _deny(target: str, issue: str) -> tuple[int, dict]:
    return 3, {"schema_version": 1, "action": "OPERATING_SWITCH",
               "target_model": target, "status": "BLOCKED", "executed": False,
               "approval_accepted": False, "live_verified": False,
               "issues": [issue]}


def execute(
    target: str, plan_id: str | None, ack_downtime: str | None,
    ack_target: str | None, *,
    root: Path = ROOT, planner: Callable[..., dict] = make_plan,
    run: Callable[..., Any] = gpu.call,
    inspect: Callable[..., dict] = gpu.docker_info,
    waiter: Callable[..., bool] = gpu.wait_for,
    live: Callable[..., dict] = inspect_live_status,
) -> tuple[int, dict]:
    """Guarded backend only; there is deliberately NO user-facing execute route.

    A source review or Fake-DGX PASS does NOT authorize this method on a live
    machine. Its eventual dispatcher must enforce the operator release gate.
    """
    if (target not in SUPPORTED or not isinstance(plan_id, str)
            or not p3.SHA.fullmatch(plan_id)
            or ack_downtime != ACK_DOWNTIME or ack_target != ACK_TARGET.get(target)):
        return _deny(target, "INDEPENDENT_EXACT_PLAN_AND_TWO_ACKS_REQUIRED")
    try:
        p3._private_dir(root)
        fd = os.open(root / "operating-execution.lock",
                     os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
        if os.fstat(fd).st_mode & 0o077:
            os.close(fd)
            return _deny(target, "INSECURE_OPERATING_LOCK_PERMISSIONS")
    except (OSError, ValueError):
        return _deny(target, "PRIVATE_OPERATING_LOCK_UNAVAILABLE")
    with os.fdopen(fd, "w+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return _deny(target, "CONCURRENT_OPERATING_SWITCH_BLOCKED")
        try:
            fresh = planner(target, root=root)
        except (OSError, RuntimeError, ValueError, TypeError,
                subprocess.TimeoutExpired):
            return _deny(target, "FRESH_OPERATING_PREFLIGHT_FAILED")
        if fresh.get("status") != READY or fresh.get("plan_id") != plan_id:
            return _deny(target, "EXPIRED_OR_CHANGED_OPERATING_PLAN")
        source = fresh.get("source_model")
        if source not in SUPPORTED or source == target:
            return _deny(target, "SOURCE_TARGET_NOT_DIFFERENT_OR_UNVERIFIED")
        source_id, target_id = (fresh.get("source_container_id"),
                                fresh.get("target_container_id"))
        source_image, target_image = (fresh.get("source_image"),
                                      fresh.get("target_image"))
        if (not p3.SHA.fullmatch(str(source_id or ""))
                or not p3.SHA.fullmatch(str(target_id or ""))
                or not all(isinstance(img, str) and img.startswith("sha256:")
                           for img in (source_image, target_image))):
            return _deny(target, "PLAN_PINNED_CONTAINER_IDENTITY_INVALID")
        phase = None
        old_stop_attempted = False
        error_code = None
        stage_for_restore = "b" if source == "27b" else "c"
        try:
            # Deterministic O_EXCL marker prevents retrying a possibly
            # interrupted exact SHA plan, even after apparent restoration.
            p3._write_once(root, "attempt-" + plan_id + ".json", {
                "schema_version": 1, "action": "OPERATING_SWITCH",
                "plan_id": plan_id, "source_model": source,
                "target_model": target,
                "started_at_utc": datetime.now(timezone.utc).isoformat(),
            })
            p3._record(root, "OBSERVED", source, target, source, plan_id)
            p3._record(root, "PLANNED", source, target, source, plan_id)
            p3._record(root, "OLD_STOPPING", source, target, source, plan_id)
            phase = "OLD_STOPPING"
            before = inspect(p3.NAMES[source])
            if p3._container_checks(before, name=p3.NAMES[source],
                                   image=source_image, expected_id=source_id,
                                   running=True):
                raise RuntimeError("SOURCE_DRIFT_BEFORE_STOP")
            old_stop_attempted = True
            if run(["docker", "stop", "--time", "45", p3.NAMES[source]],
                   timeout=80).returncode:
                raise RuntimeError("OLD_SERVICE_STOP_FAILED")
            if gpu.running(p3.NAMES[source], run):
                raise RuntimeError("OLD_SERVICE_STILL_RUNNING")
            p3._record(root, "OLD_STOPPED", source, target, None, plan_id)
            phase = "OLD_STOPPED"
            for _ in range(20):
                if gpu.port_free(run):
                    break
                time.sleep(1)
            else:
                raise RuntimeError("PORT_8000_NOT_RELEASED")
            names = p3._docker_names(run)
            if p3.NAMES[target] not in names:
                raise RuntimeError("PRESERVED_TARGET_MISSING")
            doc = inspect(p3.NAMES[target])
            if p3._container_checks(doc, name=p3.NAMES[target],
                                   image=target_image, expected_id=target_id,
                                   running=False):
                raise RuntimeError("PRESERVED_TARGET_DRIFT")
            if target == "27b":
                # Historical A provenance, not an approval token.
                # Rechecking ID/image matters even if the label was read earlier.
                if ((doc.get("Config") or {}).get("Labels") or {}).get(p3.LABEL) is None:
                    raise RuntimeError("PRESERVED_27B_PROVENANCE_MISSING")
            if p3._gpu_conflicts(p3.NAMES[source], run, inspect,
                                 require_source_running=False):
                raise RuntimeError("FOREIGN_GPU_CONSUMER_BEFORE_START")
            p3._record(root, "NEW_STARTING", source, target, None, plan_id)
            phase = "NEW_STARTING"
            if run(["docker", "start", p3.NAMES[target]], timeout=90).returncode:
                raise RuntimeError("NEW_SERVICE_START_FAILED")
            p3._record(root, "NEW_VERIFYING", source, target, target, plan_id)
            phase = "NEW_VERIFYING"
            if not waiter(p3.NAMES[target], p3.IDS[target], 600, run=run):
                raise RuntimeError("TARGET_API_WAIT_FAILED")
            new = inspect(p3.NAMES[target])
            if p3._container_checks(new, name=p3.NAMES[target],
                                   image=target_image, expected_id=target_id,
                                   running=True):
                raise RuntimeError("TARGET_DOCKER_IDENTITY_CHANGED")
            observed = live()
            if (observed.get("status") != "LIVE_SERVICE_VERIFIED"
                    or observed.get("observed_model") != target
                    or observed.get("expected_served_id") != p3.IDS[target]
                    or observed.get("issues")):
                raise RuntimeError("TARGET_SERVED_MODEL_ID_UNVERIFIED")
            old = inspect(p3.NAMES[source])
            if p3._container_checks(old, name=p3.NAMES[source],
                                   image=source_image, expected_id=source_id,
                                   running=False):
                raise RuntimeError("ORIGINAL_CONTAINER_NOT_PRESERVED")
            p3._record(root, "COMMITTED", source, target, target, plan_id)
            phase = "COMMITTED"
            receipt = {
                "schema_version": 1, "action": "OPERATING_SWITCH",
                "status": "PASS", "executed": True, "live_verified": True,
                "source_model": source, "target_model": target,
                "source_container_id": source_id,
                "target_container_id": target_id,
                "source_image": source_image, "target_image": target_image,
                "plan_id": plan_id, "served_id": p3.IDS[target],
                "finished_at_utc": datetime.now(timezone.utc).isoformat(),
            }
            name = "completed-" + plan_id + ".json"
            p3._write_once(root, name, receipt)
            return 0, {"status": "PASS", "executed": True,
                       "live_verified": True, "active_model": target,
                       "served_id": p3.IDS[target],
                       "evidence": str(root / name), "issues": [],
                       "notice": "Original model assets preserved; no automatic follow-up switch."}
        except (KeyboardInterrupt, SystemExit):
            error_code = "OPERATING_SWITCH_INTERRUPTED"
        except (OSError, RuntimeError, ValueError, TypeError,
                subprocess.TimeoutExpired) as exc:
            error_code = (str(exc) if isinstance(exc, RuntimeError)
                          else "OPERATING_SWITCH_" + type(exc).__name__)
        if phase == "COMMITTED":
            return 4, {"status": "COMMITTED_EVIDENCE_INCOMPLETE",
                       "executed": True, "active_model": target,
                       "issues": [error_code],
                       "notice": "Reconcile current API, journal and receipts manually."}
        try:
            if phase == "OLD_STOPPING":
                p3._record(root, "FAILED", source, target, None, plan_id)
                phase = "FAILED"
            if phase in ("FAILED", "OLD_STOPPED", "NEW_STARTING", "NEW_VERIFYING"):
                p3._record(root, "ROLLBACK_STARTING", source, target, None, plan_id)
                phase = "ROLLBACK_STARTING"
        except (OSError, RuntimeError, ValueError, TypeError):
            error_code += ":JOURNAL_UPDATE_FAILED"
        if old_stop_attempted:
            restored = p3._restore(
                stage_for_restore, source, target, source_id, source_image,
                target_image, plan_id, expected_target_id=target_id,
                run=run, inspect=inspect, waiter=waiter, live=live)
            try:
                if phase == "ROLLBACK_STARTING":
                    p3._record(root, restored["status"], source, target,
                               source if restored["status"] == "RESTORED" else None,
                               plan_id)
            except (OSError, RuntimeError, ValueError, TypeError):
                restored = {"status": "RECOVERY_FAILED",
                            "issues": ["RESTORE_JOURNAL_INCOMPLETE",
                                       *restored.get("issues", [])]}
        else:
            restored = {"status": "NOT_NEEDED", "issues": []}
        if restored["status"] == "RECOVERY_FAILED":
            outcome = "RECOVERY_FAILED"
        elif restored["status"] == "RESTORED":
            outcome = "FAIL_RESTORED"
        else:
            outcome = "BLOCKED"
        return 4, {
            "status": outcome, "executed": old_stop_attempted,
            "active_model": source if outcome == "FAIL_RESTORED" else None,
            "error_code": error_code, "restoration": restored,
            "issues": [error_code, *restored.get("issues", [])],
            "notice": "No blind retries; reconcile private journal and actual API.",
        }
