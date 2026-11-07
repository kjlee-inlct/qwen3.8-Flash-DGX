"""P2-FINAL 27B Native Tools V1: bounded ONE-SHOT operator trial, original restore.

An explicit human-approved maintenance experiment, NEVER a production Wizard
release. Preserves BOTH original Docker containers/images, never replays P3,
never uses a second API port, and restores original 27B after the probe.
A host crash, SIGKILL, Docker failure or OOM may defeat automatic restore:
any prior attempt marker blocks a new trial pending manual reconciliation.
"""
from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager import p3_persistent_switch as p3
from scripts.manager.operational_audit import inspect_journal
from scripts.manager.operational_probe import verify_chat
from scripts.manager.operational_switch import ROOT as OPERATING_ROOT, historical_p3_receipts
from scripts.manager.p2_27b_launch_preview import SERVED
from scripts.manager.p2_27b_tool_variant import (
    SOURCE_CONTAINER, VARIANT_CONTAINER, FALLBACK_CONTAINER, VARIANT_ID,
    inspect_variant, _run_names, _gpu_access, _image_and_id,
)
from scripts.manager.p2_27b_tool_template_audit import (
    EXPECTED_TEMPLATE_SHA256, inspect_template_cpu,
)
from scripts.manager.p2_27b_tool_calling import probe as tool_probe
from scripts.manager.p2_27b_tool_streaming import probe_stream

ROOT = Path.home() / ".local/state/blazux-wizard/p2-final-tools-v1"
READY = "READY_FOR_INDEPENDENT_NATIVE_TOOLS_TRIAL_APPROVAL"
ACK = "I_ACCEPT_P2_FINAL_NATIVE_TOOLS_DOWNTIME"
ACK_TARGET = "I_APPROVE_DISTINCT_27B_NATIVE_TOOLS_V1"
TRIAL_LABEL = "blazux.p2-final-native-tools-trial"
TIMEOUT_START = 600


def _blocked(*issues: str) -> dict:
    return {
        "schema_version": 1, "action": "P2_FINAL_NATIVE_TOOLS_ONESHOT",
        "status": "BLOCKED", "issues": sorted(set(issues)),
        "execution_enabled": False, "executed": False,
        "approval_accepted": False, "plan_id": None, "api_port": 8000,
        "source_container": SOURCE_CONTAINER, "variant_container": VARIANT_CONTAINER,
        "restore_original_after_trial": True,
    }


def _private(root: Path) -> None:
    p3._private_dir(root)
    if root.is_symlink() or root.stat().st_mode & 0o077:
        raise ValueError("UNSAFE_TOOLS_TRIAL_STATE_DIRECTORY")


def _prior_attempts(root: Path) -> bool:
    if root.is_symlink():
        raise ValueError("TOOLS_TRIAL_STATE_SYMLINK")
    return root.exists() and any(root.glob("attempt-*.json"))


def _plan_hash(facts: dict) -> str:
    return hashlib.sha256(
        json.dumps(facts, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def make_plan(
    *, preview: Callable[[], dict] = inspect_variant,
    template: Callable[[], dict] = inspect_template_cpu,
    historical: Callable[[], dict] = historical_p3_receipts,
    journal: Callable[..., dict] = inspect_journal,
    inspect: Callable[..., dict] = gpu.docker_info,
    root: Path = ROOT, operating_root: Path = OPERATING_ROOT,
    now: float | None = None,
) -> dict:
    """Source-on, zero-mutation preview; never grants execution approval."""
    issues: list[str] = []
    try:
        if _prior_attempts(root):
            issues.append("PRIOR_TOOLS_TRIAL_REQUIRES_MANUAL_RECONCILIATION")
        v = preview()
        t = template()
        h = historical()
        j = journal(operating_root)
        source = inspect(SOURCE_CONTAINER)
        fallback = inspect(FALLBACK_CONTAINER)
        if v.get("read_only_preflight_pass") is not True or v.get("issues"):
            issues.append("NATIVE_TOOLS_VARIANT_PREVIEW_NOT_READY")
        if (t.get("status") != "CPU_TEMPLATE_RENDER_VALIDATED_ONLY"
                or t.get("issues") or t.get("template_sha256") != EXPECTED_TEMPLATE_SHA256
                or any(t.get(k) is not True for k in (
                    "tool_prompt_rendered", "tool_result_rendered",
                    "non_tool_prompt_rendered", "no_thinking_rendered",
                    "thinking_prompt_rendered",
                ))):
            issues.append("PINNED_TEMPLATE_CPU_RUNTIME_NOT_QUALIFIED")
        if (h.get("status") != "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED"
                or h.get("issues")):
            issues.append("P3_PROTECTED_ORIGINAL_LINEAGE_NOT_VERIFIED")
        a = (h.get("records") or {}).get("a") or {}
        if (source.get("Id") != a.get("id_27b")
                or source.get("Image") != a.get("image_27b")):
            issues.append("P3_ORIGINAL_27B_CONTAINER_OR_IMAGE_CHANGED")
        if (fallback.get("Id") != a.get("flash_id")
                or fallback.get("Image") != a.get("flash_image")):
            issues.append("P3_FLASH_FALLBACK_CONTAINER_OR_IMAGE_CHANGED")
        if j.get("issues") or j.get("status") not in ("EMPTY", "VERIFIED"):
            issues.append("EXISTING_OPERATING_JOURNAL_NOT_CLEAN")
        if j.get("status") == "VERIFIED" and j.get("phase") not in (
            "COMMITTED", "RESTORED", "CANCELLED",
        ):
            issues.append("EXISTING_OPERATING_JOURNAL_UNRESOLVED")
        command = v.get("candidate_command_NOT_EXECUTABLE")
        if (not isinstance(command, list)
                or command[:3] != ["docker", "run", "-d"]
                or "--chat-template" not in command
                or "--enable-auto-tool-choice" not in command
                or "--tool-call-parser" not in command
                or "--reasoning-parser" not in command
                or source.get("Image") not in command):
            issues.append("PROTECTED_TOOLS_LAUNCH_SPEC_NOT_VERIFIED")
        # Immutable source/fallback identity is part of the separate plan hash.
        image = source.get("Image")
        if not isinstance(image, str) or not p3.SHA.fullmatch(image.removeprefix("sha256:")):
            issues.append("PINNED_LOCAL_IMAGE_ID_INVALID")
        window = int(time.time() if now is None else now) // 600
        facts = {
            "kind": "P2_FINAL_NATIVE_TOOLS_V1_REAL_ONESHOT_APPROVAL",
            "original_id": source.get("Id"), "original_image": image,
            "flash_id": fallback.get("Id"), "flash_image": fallback.get("Image"),
            "variant_name": VARIANT_CONTAINER, "variant_id": VARIANT_ID,
            "served_id": SERVED, "port": 8000,
            "template_sha256": EXPECTED_TEMPLATE_SHA256,
            "argv_sha256": _plan_hash({"argv": command}) if command else None,
            "p3_receipt_hashes": h.get("receipt_sha256"),
            "operating_journal_last": j.get("last_event_hash"),
            "window": window,
        }
        if issues:
            result = _blocked(*issues)
            result["candidate_command_NOT_EXECUTABLE"] = None
            return result
        expires = (window + 1) * 600
        return {
            "schema_version": 1, "action": "P2_FINAL_NATIVE_TOOLS_ONESHOT",
            "status": READY, "issues": [], "plan_id": _plan_hash(facts),
            "expires_at_epoch_seconds": expires,
            "source_container_id": source["Id"],
            "source_image": image, "fallback_id": fallback["Id"],
            "fallback_image": fallback["Image"],
            "api_port": 8000, "api_model_id": SERVED,
            "template_sha256": EXPECTED_TEMPLATE_SHA256,
            "command_private_for_guarded_executor": command,
            "restore_original_after_trial": True,
            "approval_accepted": False, "executed": False,
            "execution_enabled": False,
            "required_downtime_ack": ACK, "required_target_ack": ACK_TARGET,
            "notice": (
                "Read-only independent plan. A future one-shot execute requires "
                "fresh TTY SHA+two independent acknowledgements. Original 27B "
                "will be restored after the trial even on probe success; "
                "recovery may fail after host crash/OOM/Docker error."
            ),
        }
    except (OSError, RuntimeError, ValueError, TypeError, KeyError,
            subprocess.TimeoutExpired, json.JSONDecodeError):
        return _blocked("TOOLS_TRIAL_PREFLIGHT_UNAVAILABLE")


def _record(root: Path, plan: str, phase: str, *, detail: dict | None = None) -> None:
    """One immutable, fsync'd event file for each phase. Any failure stops progress."""
    names = sorted(root.glob("event-*.json"))
    seq = len(names) + 1
    previous = None
    if names:
        prior = names[-1]
        if prior.is_symlink() or prior.stat().st_mode & 0o077:
            raise RuntimeError("UNTRUSTED_PRIOR_TOOLS_EVENT")
        record = json.loads(prior.read_text())
        previous = record.get("event_hash")
        if not isinstance(previous, str) or not p3.SHA.fullmatch(previous):
            raise RuntimeError("INVALID_PRIOR_EVENT_HASH")
    event = {
        "schema_version": 1, "plan_id": plan, "seq": seq,
        "phase": phase, "previous_hash": previous,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "detail": detail or {},
    }
    event["event_hash"] = _plan_hash(event)
    p3._write_once(root, f"event-{seq:04d}.json", event)


def _inspect_original(id_: str, image: str, *, inspect: Callable) -> bool:
    doc = inspect(SOURCE_CONTAINER)
    return (
        _image_and_id(doc)
        and doc.get("Id") == id_ and doc.get("Image") == image
        and (doc.get("Config") or {}).get("Cmd") is not None
    )


def _restore(
    plan: dict, *, run: Callable, inspect: Callable,
    waiter: Callable, chat: Callable, root: Path,
) -> dict:
    """Only stop the trial-OWNED variant, never remove original/Flash."""
    issues = []
    try:
        names = _run_names(run, all_containers=True)
        if VARIANT_CONTAINER in names:
            target = inspect(VARIANT_CONTAINER)
            labels = (target.get("Config") or {}).get("Labels") or {}
            if (labels.get(TRIAL_LABEL) != plan["plan_id"]
                    or labels.get("blazux.variant") != VARIANT_ID
                    or not _image_and_id(target)
                    or target.get("Image") != plan["source_image"]):
                raise RuntimeError("FOREIGN_VARIANT_CANNOT_STOP")
            if (target.get("State") or {}).get("Running"):
                action = run(
                    ["docker", "stop", "--time", "45", VARIANT_CONTAINER],
                    timeout=80,
                )
                if action.returncode:
                    raise RuntimeError("TRIAL_VARIANT_STOP_FAILED")
            if (inspect(VARIANT_CONTAINER).get("State") or {}).get("Running"):
                raise RuntimeError("TRIAL_VARIANT_STILL_RUNNING")
        if not gpu.port_free(run):
            raise RuntimeError("RESTORE_PORT_8000_BUSY")
        if p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect,
                             require_source_running=False):
            raise RuntimeError("FOREIGN_GPU_BEFORE_ORIGINAL_RESTORE")
        if not _inspect_original(plan["source_container_id"],
                                 plan["source_image"], inspect=inspect):
            raise RuntimeError("ORIGINAL_ID_IMAGE_CHANGED_DURING_TRIAL")
        old = inspect(SOURCE_CONTAINER)
        if not (old.get("State") or {}).get("Running"):
            r = run(["docker", "start", SOURCE_CONTAINER], timeout=90)
            if r.returncode:
                raise RuntimeError("ORIGINAL_27B_RESTART_FAILED")
        if not waiter(SOURCE_CONTAINER, SERVED, 600, run=run):
            raise RuntimeError("ORIGINAL_27B_API_NOT_RESTORED")
        if not chat(SERVED):
            raise RuntimeError("ORIGINAL_27B_CHAT_NOT_RESTORED")
        if not _inspect_original(plan["source_container_id"],
                                 plan["source_image"], inspect=inspect):
            raise RuntimeError("ORIGINAL_27B_ID_IMAGE_DRIFT_AFTER_RESTORE")
        if p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect):
            raise RuntimeError("FOREIGN_GPU_AFTER_ORIGINAL_RESTORE")
        _record(root, plan["plan_id"], "RESTORED")
        return {"status": "RESTORED", "issues": []}
    except (OSError, RuntimeError, ValueError, TypeError,
            subprocess.TimeoutExpired) as exc:
        issues.append(str(exc) if isinstance(exc, RuntimeError)
                      else "RESTORE_" + type(exc).__name__)
        try:
            _record(root, plan["plan_id"], "RECOVERY_FAILED")
        except (OSError, RuntimeError, ValueError):
            issues.append("RECOVERY_JOURNAL_UNAVAILABLE")
        return {"status": "RECOVERY_FAILED", "issues": issues}


def execute(
    plan_id: str, downtime_ack: str, target_ack: str, *,
    root: Path = ROOT, operating_root: Path = OPERATING_ROOT,
    planner: Callable[..., dict] = make_plan,
    run: Callable[..., Any] = gpu.call,
    inspect: Callable[..., dict] = gpu.docker_info,
    waiter: Callable[..., bool] = gpu.wait_for,
    probe: Callable[[], dict] = tool_probe,
    streamed: Callable[[], dict] = probe_stream,
    chat: Callable[[str], bool] = verify_chat,
    now: Callable[[], float] = time.time,
) -> tuple[int, dict]:
    """Explicit one-shot human-approved trial. Source restored even after PASS."""
    if (not isinstance(plan_id, str) or not p3.SHA.fullmatch(plan_id)
            or downtime_ack != ACK or target_ack != ACK_TARGET):
        return 3, _blocked("FRESH_EXACT_PLAN_AND_TWO_ACKS_REQUIRED")
    try:
        _private(root)
        _private(operating_root)
        fds = []
        for path in (operating_root / "operating-execution.lock",
                     root / "native-tools-trial.lock"):
            fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            if os.fstat(fd).st_mode & 0o077:
                os.close(fd)
                raise RuntimeError("UNSAFE_TRIAL_LOCK_PERMISSIONS")
            fds.append(fd)
    except (OSError, ValueError, RuntimeError):
        return 3, _blocked("TOOLS_TRIAL_LOCKS_UNAVAILABLE")
    try:
        for fd in fds:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return 3, _blocked("CONCURRENT_SWITCH_LOCK_HELD")
        fresh = planner(root=root, operating_root=operating_root)
        expires = fresh.get("expires_at_epoch_seconds")
        if (fresh.get("status") != READY or fresh.get("plan_id") != plan_id
                or type(expires) is not int
                or not 120 <= expires - now() <= 600):
            return 3, _blocked("EXPIRED_CHANGED_OR_UNQUALIFIED_TOOLS_PLAN")
        cmd = fresh.get("command_private_for_guarded_executor")
        if not isinstance(cmd, list) or fresh["source_image"] not in cmd:
            return 3, _blocked("PINNED_VARIANT_COMMAND_NOT_VERIFIED")
        _record(root, plan_id, "PLANNED")
        # Immutable O_EXCL marker blocks any uncertain repeat after a crash.
        p3._write_once(root, "attempt-" + plan_id + ".json", {
            "plan_id": plan_id, "action": "P2_FINAL_NATIVE_TOOLS_ONESHOT",
            "source_id": fresh["source_container_id"],
            "source_image": fresh["source_image"],
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
        })
        old_stop_attempted = False
        result: dict[str, Any] = {
            "schema_version": 1, "action": "P2_FINAL_NATIVE_TOOLS_ONESHOT",
            "executed": False, "issues": [], "structured_tool_call": False,
            "tool_result_continuation": False, "streamed_tool_call": False,
            "original_restored": False,
        }
        try:
            # Guard source immediately before the first potentially destructive op.
            if not _inspect_original(fresh["source_container_id"],
                                     fresh["source_image"], inspect=inspect):
                raise RuntimeError("ORIGINAL_IDENTITY_DRIFT_BEFORE_STOP")
            if _run_names(run, all_containers=True).count(VARIANT_CONTAINER):
                raise RuntimeError("VARIANT_CONTAINER_ALREADY_EXISTS")
            if p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect):
                raise RuntimeError("OTHER_GPU_CONTAINER_RUNNING_BEFORE_STOP")
            _record(root, plan_id, "OLD_STOPPING")
            old_stop_attempted = True
            p = run(["docker", "stop", "--time", "45", SOURCE_CONTAINER],
                    timeout=80)
            if p.returncode or gpu.running(SOURCE_CONTAINER, run):
                raise RuntimeError("PROTECTED_ORIGINAL_STOP_UNVERIFIED")
            _record(root, plan_id, "OLD_STOPPED")
            for _ in range(25):
                if gpu.port_free(run):
                    break
                time.sleep(1)
            else:
                raise RuntimeError("PORT_8000_NOT_FREE")
            if p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect,
                                 require_source_running=False):
                raise RuntimeError("GPU_NOT_EXCLUSIVE_AFTER_STOP")
            _record(root, plan_id, "VARIANT_STARTING")
            image_index = cmd.index(fresh["source_image"])
            launch = list(cmd)
            launch[image_index:image_index] = [
                "--pull", "never", "--restart", "no",
                "--label", TRIAL_LABEL + "=" + plan_id,
            ]
            p = run(launch, timeout=90)
            if p.returncode:
                raise RuntimeError("NATIVE_TOOLS_VARIANT_START_FAILED")
            _record(root, plan_id, "VARIANT_STARTED")
            if not waiter(VARIANT_CONTAINER, SERVED, TIMEOUT_START, run=run):
                raise RuntimeError("NATIVE_TOOLS_VARIANT_API_NOT_READY")
            doc = inspect(VARIANT_CONTAINER)
            if (not _image_and_id(doc) or doc.get("Image") != fresh["source_image"]
                    or ((doc.get("Config") or {}).get("Labels") or {}).get(
                        TRIAL_LABEL) != plan_id):
                raise RuntimeError("VARIANT_IMAGE_PROVENANCE_MISMATCH")
            if p3._gpu_conflicts(VARIANT_CONTAINER, run, inspect):
                raise RuntimeError("VARIANT_GPU_EXCLUSIVITY_UNVERIFIED")
            # The originally requested EXACT milestone: structured tool_calls.
            report = probe()
            result["structured_tool_call"] = report.get("structured_tool_call") is True
            result["tool_result_continuation"] = (
                report.get("tool_result_continuation") is True)
            result["structured_probe_status"] = report.get("status")
            result["structured_probe_issues"] = report.get("issues", [])
            _record(root, plan_id, "STRUCTURED_PROBE_COMPLETED",
                    detail={"structured": result["structured_tool_call"],
                            "continued": result["tool_result_continuation"]})
            if not result["structured_tool_call"]:
                raise RuntimeError("STRUCTURED_TOOL_CALL_NOT_OBSERVED")
            # Additional bounded streaming check. Its failure does not hide the
            # structured result; restore always occurs below.
            stream = streamed()
            result["streamed_tool_call"] = stream.get("streamed_tool_call") is True
            result["stream_probe_status"] = stream.get("status")
            result["stream_probe_issues"] = stream.get("issues", [])
            _record(root, plan_id, "STREAM_PROBE_COMPLETED",
                    detail={"streamed": result["streamed_tool_call"]})
            result["trial"] = (
                "PASS" if result["structured_tool_call"]
                and result["tool_result_continuation"]
                and result["streamed_tool_call"] else "PARTIAL"
            )
        except (KeyboardInterrupt, SystemExit):
            result["issues"].append("TRIAL_INTERRUPTED")
        except (OSError, RuntimeError, ValueError, TypeError,
                subprocess.TimeoutExpired) as exc:
            result["issues"].append(
                str(exc) if isinstance(exc, RuntimeError)
                else "TRIAL_" + type(exc).__name__)
        finally:
            if old_stop_attempted:
                result["executed"] = True
                try:
                    _record(root, plan_id, "RESTORE_STARTING")
                except (OSError, RuntimeError, ValueError):
                    result["issues"].append("RESTORE_JOURNAL_START_FAILED")
                restoration = _restore(
                    fresh, run=run, inspect=inspect, waiter=waiter,
                    chat=chat, root=root,
                )
            else:
                restoration = {"status": "NOT_NEEDED", "issues": []}
            result["restoration"] = restoration
            result["original_restored"] = restoration["status"] == "RESTORED"
        if restoration["status"] == "RECOVERY_FAILED":
            result["status"] = "RECOVERY_FAILED"
            result["issues"].extend(restoration["issues"])
        elif restoration["status"] == "RESTORED":
            result["status"] = (
                "PASS_RESTORED" if result.get("trial") == "PASS"
                else "PARTIAL_RESTORED" if result.get("trial") == "PARTIAL"
                else "FAIL_RESTORED"
            )
        else:
            result["status"] = "BLOCKED"
        try:
            p3._write_once(root, "result-" + plan_id + ".json", result)
        except (OSError, ValueError):
            result["status"] = "RECOVERY_EVIDENCE_INCOMPLETE"
            result["issues"].append("RESULT_RECEIPT_UNAVAILABLE")
        return (0 if result["status"] == "PASS_RESTORED" else 4), result
    finally:
        for fd in reversed(fds):
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=(
        "ONE-SHOT independent DGX 27B native-tools experiment; ALWAYS restore "
        "original 27B, never use for ordinary Wizard switch"
    ))
    parser.add_argument("action", choices=("plan", "execute"))
    args = parser.parse_args(argv)
    plan = make_plan()
    # Do not print a runnable Docker command in the public CLI preview.
    display = {k: v for k, v in plan.items()
               if k != "command_private_for_guarded_executor"}
    if args.action == "plan":
        print(json.dumps(display, indent=2, sort_keys=True))
        return 0 if plan.get("status") == READY else 3
    if plan.get("status") != READY:
        print(json.dumps(display, indent=2, sort_keys=True))
        return 3
    if not sys.stdin.isatty():
        print("BLOCKED: three independent approvals require interactive TTY")
        return 3
    remaining = plan["expires_at_epoch_seconds"] - time.time()
    if remaining < 120:
        print("BLOCKED: plan expires too soon, re-run after renewal")
        return 3
    print("Temporary API downtime required; no guarantee after host/Docker crash.")
    print("Original 27B WILL be restored after the probe even if PASS.")
    print("Native Tools trial-only; historical P3 receipts are immutable.")
    try:
        exact = input("Type the full NEW 64-digit SHA from this preview: ").strip()
        downtime = input("Type independent acknowledgement " + ACK + ": ").strip()
        target = input("Type separate target acknowledgement " + ACK_TARGET + ": ").strip()
    except (KeyboardInterrupt, EOFError):
        print("CANCELLED; no service action")
        return 3
    code, outcome = execute(exact, downtime, target)
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
