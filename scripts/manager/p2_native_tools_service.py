"""Guarded persisted switch: original NVIDIA 27B <-> proven Native Tools V1.

Uses the stopped variant produced by the successful DGX one-shot trial:
NO docker run/rm, no image or cache removal, NO P3 stage replay, API :8000.
All modifications require a fresh SHA, real TTY and two independent approvals.
Separate journal; do NOT modify existing ordinary Wizard/P3 receipts.
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
from scripts.manager.operational_switch import historical_p3_receipts, ROOT as OPS_ROOT
from scripts.manager.p2_27b_tool_calling import probe as tools_probe
from scripts.manager.p2_27b_tool_streaming import probe_stream
from scripts.manager.p2_27b_tool_live_trial import ROOT as TRIAL_ROOT, TRIAL_LABEL
from scripts.manager.p2_27b_tool_template_audit import EXPECTED_TEMPLATE_SHA256
from scripts.manager.p2_27b_tool_variant import (
    SOURCE_CONTAINER, VARIANT_CONTAINER, FALLBACK_CONTAINER, VARIANT_ID,
    TOOL_CHAT_TEMPLATE, SNAPSHOT, _image_and_id, _gpu_access,
    _protected_mount, _run_names,
)
from scripts.manager.p2_27b_launch_preview import SERVED

ROOT = Path.home() / ".local/state/blazux-wizard/native-tools-service"
TARGETS = {"native-tools": VARIANT_CONTAINER, "original-27b": SOURCE_CONTAINER}
BACK = {value: key for key, value in TARGETS.items()}
READY = "READY_FOR_NATIVE_TOOLS_SERVICE_SWITCH_APPROVAL"
ACK = "I_ACCEPT_NATIVE_TOOLS_SERVICE_DOWNTIME"
ACK_TARGET = {
    "native-tools": "I_APPROVE_NATIVE_TOOLS_AS_ACTIVE_SERVICE",
    "original-27b": "I_APPROVE_ORIGINAL_27B_AS_ACTIVE_SERVICE",
}
STARTUP_TIMEOUT = 600
TERMINAL = frozenset(("COMMITTED", "RESTORED", "CANCELLED"))


def _digest(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                        separators=(",", ":")).encode()).hexdigest()


def _blocked(target: str, *codes: str) -> dict:
    return {
        "schema_version": 1,
        "action": "P2_NATIVE_TOOLS_SERVICE_SWITCH",
        "target": target, "status": "BLOCKED",
        "issues": sorted(set(codes)), "plan_id": None,
        "executed": False, "approval_accepted": False,
        "api_host_port": 8000, "single_model_only": True,
    }


def _safe_file(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("UNTRUSTED_RECEIPT_FILE")
    st = path.stat()
    if st.st_mode & 0o077 or not 0 < st.st_size <= 65536:
        raise ValueError("UNTRUSTED_RECEIPT_PERMISSIONS_OR_SIZE")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("INVALID_RECEIPT_DATA")
    return data


def _old_trial_verified(label: str, *, root: Path = TRIAL_ROOT) -> bool:
    """Allow ONLY the preserved variant from an actually successful trial."""
    if not p3.SHA.fullmatch(label) or root.is_symlink():
        return False
    try:
        attempt = _safe_file(root / ("attempt-" + label + ".json"))
        result = _safe_file(root / ("result-" + label + ".json"))
        events = sorted(root.glob("event-*.json"))
        if (attempt.get("plan_id") != label or result.get("status") != "PASS_RESTORED"
                or result.get("original_restored") is not True
                or result.get("structured_tool_call") is not True
                or result.get("tool_result_continuation") is not True
                or result.get("streamed_tool_call") is not True
                or result.get("issues") or len(events) < 8):
            return False
        previous = None
        for number, file in enumerate(events, 1):
            doc = _safe_file(file)
            digest = doc.get("event_hash")
            body = {k: v for k, v in doc.items() if k != "event_hash"}
            if (file.name != f"event-{number:04d}.json"
                    or doc.get("seq") != number
                    or doc.get("plan_id") != label
                    or doc.get("previous_hash") != previous
                    or digest != _digest(body)):
                return False
            previous = digest
        return doc.get("phase") == "RESTORED"
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return False


def _audit_switch_records(root: Path) -> bool:
    """Check independent append-only chain and completed attempts; no reset."""
    if root.is_symlink():
        return False
    if not root.exists():
        return True
    try:
        events = sorted(root.glob("event-*.json"))
        previous = None
        last_phase = None
        for number, file in enumerate(events, 1):
            row = _safe_file(file)
            digest = row.get("event_hash")
            body = {k: v for k, v in row.items() if k != "event_hash"}
            if (file.name != f"event-{number:04d}.json"
                    or row.get("seq") != number
                    or row.get("previous_hash") != previous
                    or not p3.SHA.fullmatch(str(row.get("plan_id", "")))
                    or digest != _digest(body)):
                return False
            previous = digest
            last_phase = row.get("phase")
        attempts = sorted(root.glob("attempt-*.json"))
        results = sorted(root.glob("result-*.json"))
        if len(attempts) != len(results):
            return False
        for attempt in attempts:
            obj = _safe_file(attempt)
            plan = obj.get("plan_id")
            if (not isinstance(plan, str) or not p3.SHA.fullmatch(plan)
                    or attempt.name != "attempt-" + plan + ".json"):
                return False
            outcome = _safe_file(root / ("result-" + plan + ".json"))
            if outcome.get("plan_id") != plan or outcome.get("status") not in (
                    "COMMITTED", "RESTORED", "CANCELLED"):
                return False
        return last_phase in TERMINAL if events else not attempts
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
        return False


def _event(root: Path, plan: str, phase: str, detail: dict | None = None) -> None:
    if not _audit_switch_records(root) and phase == "PLANNED":
        raise RuntimeError("UNRESOLVED_PRIVATE_JOURNAL")
    files = sorted(root.glob("event-*.json"))
    previous = _safe_file(files[-1])["event_hash"] if files else None
    entry = {
        "schema_version": 1, "seq": len(files) + 1,
        "plan_id": plan, "phase": phase,
        "previous_hash": previous,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "detail": detail or {},
    }
    entry["event_hash"] = _digest(entry)
    p3._write_once(root, f"event-{len(files)+1:04d}.json", entry)


def _arg(cmd: list[str], name: str, value: str) -> bool:
    return cmd.count(name) == 1 and (
        cmd.index(name) + 1 < len(cmd)
        and cmd[cmd.index(name) + 1] == value
    )


def make_plan(target: str, *,
              run: Callable[..., Any] = gpu.call,
              inspect: Callable[[str], dict] = gpu.docker_info,
              historical: Callable[[], dict] = historical_p3_receipts,
              ordinary_journal: Callable[..., dict] = inspect_journal,
              ready_api: Callable[[str], bool] = gpu.api_ready,
              root: Path = ROOT, now: float | None = None) -> dict:
    """Strict read-only preflight; both containers must already exist."""
    if target not in TARGETS:
        return _blocked(target, "UNSUPPORTED_TARGET")
    issues: list[str] = []
    try:
        if not _audit_switch_records(root):
            issues.append("PRIVATE_SERVICE_JOURNAL_UNRESOLVED")
        ordinary = ordinary_journal(OPS_ROOT)
        if (ordinary.get("issues") or ordinary.get("status") not in ("VERIFIED", "EMPTY")
                or ordinary.get("phase") not in (None, "COMMITTED", "RESTORED", "CANCELLED")):
            issues.append("ORIGINAL_OPERATING_JOURNAL_UNQUALIFIED")
        hist = historical()
        a = (hist.get("records") or {}).get("a") or {}
        if hist.get("status") != "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED" or hist.get("issues"):
            issues.append("P3_IMMUTABLE_LINEAGE_UNQUALIFIED")
        names = _run_names(run, all_containers=True)
        running = _run_names(run, all_containers=False)
        if not all(n in names for n in (
                SOURCE_CONTAINER, VARIANT_CONTAINER, FALLBACK_CONTAINER)):
            issues.append("PROTECTED_CONTAINERS_MISSING")
            return _blocked(target, *issues)
        original = inspect(SOURCE_CONTAINER)
        variant = inspect(VARIANT_CONTAINER)
        flash = inspect(FALLBACK_CONTAINER)
        if any(not _image_and_id(d) for d in (original, variant, flash)):
            issues.append("PRESERVED_CONTAINER_ID_OR_IMAGE_UNVERIFIED")
        if (original.get("Id"), original.get("Image")) != (
                a.get("id_27b"), a.get("image_27b")):
            issues.append("ORIGINAL_P3_IDENTITY_DRIFT")
        if (flash.get("Id"), flash.get("Image")) != (
                a.get("flash_id"), a.get("flash_image")):
            issues.append("FLASH_P3_IDENTITY_DRIFT")
        if original.get("Image") != variant.get("Image"):
            issues.append("NATIVE_VARIANT_IMAGE_MISMATCH")
        if (flash.get("State") or {}).get("Running") or FALLBACK_CONTAINER in running:
            issues.append("FLASH_FALLBACK_NOT_STOPPED")
        configs = {SOURCE_CONTAINER: original, VARIANT_CONTAINER: variant}
        active = [n for n in configs
                  if (configs[n].get("State") or {}).get("Running") is True]
        if len(active) != 1 or active[0] not in running:
            issues.append("EXACTLY_ONE_PROTECTED_27B_NOT_ACTIVE")
            current = None
        else:
            current = active[0]
        if any((configs[n].get("State") or {}).get("Running") is True
               != (n in running) for n in configs):
            issues.append("DOCKER_RUNNING_INVENTORY_DRIFT")
        gpu_names = []
        for n in running:
            doc = configs.get(n) or inspect(n)
            if _gpu_access(doc):
                gpu_names.append(n)
        if len(gpu_names) != 1 or gpu_names != [current]:
            issues.append("OTHER_RUNNING_GPU_OR_MISMATCH")
        if not _gpu_access(original) or not _gpu_access(variant):
            issues.append("MODEL_GPU_REQUEST_UNVERIFIED")
        for n, doc in configs.items():
            hc = doc.get("HostConfig") or {}
            ports = (hc.get("PortBindings") or {}).get("8000/tcp")
            if (doc.get("Name") != "/" + n
                    or not isinstance(ports, list) or len(ports) != 1
                    or ports[0].get("HostPort") != "8000"
                    or (hc.get("RestartPolicy") or {}).get("Name") not in ("no",)
                    or hc.get("AutoRemove") is not False):
                issues.append("CONTAINER_PORT_RESTART_POLICY_UNSAFE_" + n)
        old_cmd = (original.get("Config") or {}).get("Cmd")
        cmd = (variant.get("Config") or {}).get("Cmd")
        if (not isinstance(old_cmd, list)
                or not _arg(old_cmd, "--served-model-name", SERVED)
                or not _arg(old_cmd, "--quantization", "modelopt_mixed")
                or not any(isinstance(s, str) and SNAPSHOT in s for s in old_cmd)
                or any(s in old_cmd for s in (
                    "--enable-auto-tool-choice", "--tool-call-parser",
                    "--reasoning-parser", "--chat-template"))):
            issues.append("ORIGINAL_27B_IMMUTABLE_CMD_UNVERIFIED")
        if (not isinstance(cmd, list)
                or "--enable-auto-tool-choice" not in cmd
                or cmd.count("--enable-auto-tool-choice") != 1
                or not any(isinstance(s, str) and SNAPSHOT in s for s in cmd)
                or not all(_arg(cmd, flag, value) for flag, value in (
                    ("--served-model-name", SERVED),
                    ("--quantization", "modelopt_mixed"),
                    ("--chat-template", TOOL_CHAT_TEMPLATE),
                    ("--tool-call-parser", "qwen3_coder"),
                    ("--reasoning-parser", "qwen3")))):
            issues.append("NATIVE_TOOLS_V1_CMD_UNVERIFIED")
        labels = (variant.get("Config") or {}).get("Labels") or {}
        trial_id = labels.get(TRIAL_LABEL)
        if (labels.get("blazux.variant") != VARIANT_ID
                or labels.get("blazux.preserved-original") != SOURCE_CONTAINER
                or not isinstance(trial_id, str) or not _old_trial_verified(trial_id)):
            issues.append("PROVEN_NATIVE_TOOLS_TRIAL_RECEIPT_UNVERIFIED")
        mount = _protected_mount(original)
        if mount is None or _protected_mount(variant) != mount:
            issues.append("PINNED_READ_ONLY_HF_CACHE_MISMATCH")
        if current == TARGETS[target]:
            issues.append("ALREADY_ACTIVE_NO_SWITCH_NEEDED")
        if current is not None and not ready_api(SERVED):
            issues.append("CURRENT_API_HEALTH_OR_MODEL_ID_UNVERIFIED")
        window = int(time.time() if now is None else now) // 600
        facts = {
            "kind": "PERSISTENT_NATIVE_TOOLS_V1_SERVICE_SWITCH",
            "target": target, "source": current,
            "source_id": configs[current]["Id"] if current else None,
            "target_id": configs[TARGETS[target]]["Id"],
            "original_id": original["Id"], "original_image": original["Image"],
            "native_id": variant["Id"], "native_image": variant["Image"],
            "flash_id": flash["Id"], "flash_image": flash["Image"],
            "trial_id": trial_id, "pinned_template_sha": EXPECTED_TEMPLATE_SHA256,
            "ordinary_journal_hash": ordinary.get("last_event_hash"),
            "time_window": window, "port": 8000,
        }
        if issues:
            return _blocked(target, *issues)
        return {
            "schema_version": 1,
            "action": "P2_NATIVE_TOOLS_SERVICE_SWITCH",
            "status": READY, "issues": [], "target": target,
            "source_container": current,
            "target_container": TARGETS[target],
            "source_id": configs[current]["Id"],
            "target_id": configs[TARGETS[target]]["Id"],
            "original_id": original["Id"],
            "native_id": variant["Id"], "image_id": original["Image"],
            "plan_id": _digest(facts),
            "expires_at_epoch_seconds": (window + 1) * 600,
            "approval_accepted": False, "executed": False,
            "api_host_port": 8000, "single_model_only": True,
            "stays_on_target_after_pass": True,
            "required_downtime_ack": ACK,
            "required_target_ack": ACK_TARGET[target],
            "notice": ("Read-only plan. Switching causes port-8000 downtime. "
                       "On failure, executor attempts to restore original active "
                       "container; power/daemon failure can defeat recovery."),
        }
    except (OSError, RuntimeError, ValueError, TypeError, KeyError,
            json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        return _blocked(target, "PREFLIGHT_ERROR_" + type(exc).__name__)


def execute(target: str, plan_id: str, downtime_ack: str, target_ack: str, *,
            run: Callable[..., Any] = gpu.call,
            inspect: Callable[[str], dict] = gpu.docker_info,
            planner: Callable[..., dict] = make_plan,
            waiter: Callable[..., bool] = gpu.wait_for,
            check_chat: Callable[[str], bool] = verify_chat,
            check_tools: Callable[[], dict] = tools_probe,
            check_stream: Callable[[], dict] = probe_stream,
            root: Path = ROOT, now: Callable[[], float] = time.time
            ) -> tuple[int, dict]:
    """Approved stop-before-start, persistent target; rollback source on error."""
    if (target not in TARGETS or not p3.SHA.fullmatch(plan_id)
            or downtime_ack != ACK or target_ack != ACK_TARGET[target]):
        return 3, _blocked(target, "EXACT_FRESH_PLAN_AND_TWO_ACKS_REQUIRED")
    fds = []
    try:
        p3._private_dir(root)
        p3._private_dir(OPS_ROOT)
        for path in (OPS_ROOT / "operating-execution.lock",
                     root / "native-tools-service.lock"):
            fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
            if os.fstat(fd).st_mode & 0o077:
                os.close(fd)
                raise ValueError("LOCK_PERMISSIONS_UNSAFE")
            fds.append(fd)
        for fd in fds:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        p = planner(target, root=root)
        expires = p.get("expires_at_epoch_seconds")
        if (p.get("status") != READY or p.get("plan_id") != plan_id
                or type(expires) is not int or not 60 < expires - now() <= 600):
            return 3, _blocked(target, "CHANGED_EXPIRED_OR_UNQUALIFIED_PLAN")
        source = p["source_container"]
        dest = p["target_container"]
        # The persistent attempt is written before the first Docker mutation.
        p3._write_once(root, "attempt-" + plan_id + ".json", {
            "schema_version": 1, "plan_id": plan_id,
            "source": source, "target": dest,
            "source_id": p["source_id"], "target_id": p["target_id"],
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        })
        _event(root, plan_id, "PLANNED", {"from": source, "to": dest})
        stopped = False
        result = {
            "schema_version": 1, "action": "P2_NATIVE_TOOLS_SERVICE_SWITCH",
            "plan_id": plan_id, "target": target, "source": source,
            "status": "BLOCKED", "executed": False, "issues": [],
            "structured_tool_call": False,
            "tool_result_continuation": False, "streamed_tool_call": False,
            "api_host_port": 8000, "source_restored": False,
        }
        try:
            docs = {name: inspect(name) for name in (source, dest)}
            if (docs[source].get("Id") != p["source_id"]
                    or docs[dest].get("Id") != p["target_id"]
                    or docs[source].get("Image") != p["image_id"]
                    or docs[dest].get("Image") != p["image_id"]
                    or not (docs[source].get("State") or {}).get("Running")
                    or (docs[dest].get("State") or {}).get("Running")
                    or _run_names(run, all_containers=False).count(source) != 1
                    or p3._gpu_conflicts(source, run, inspect)):
                raise RuntimeError("PRE_STOP_SERVICE_IDENTITY_CHANGED")
            _event(root, plan_id, "SOURCE_STOPPING")
            stopped = True
            r = run(["docker", "stop", "--time", "45", source], timeout=80)
            if r.returncode or gpu.running(source, run):
                raise RuntimeError("SOURCE_STOP_NOT_CONFIRMED")
            _event(root, plan_id, "SOURCE_STOPPED")
            for _ in range(30):
                if gpu.port_free(run):
                    break
                time.sleep(1)
            else:
                raise RuntimeError("HOST_PORT_8000_DID_NOT_RELEASE")
            if p3._gpu_conflicts(source, run, inspect,
                                 require_source_running=False):
                raise RuntimeError("GPU_NOT_EXCLUSIVE_BEFORE_TARGET_START")
            _event(root, plan_id, "TARGET_STARTING")
            r = run(["docker", "start", dest], timeout=90)
            if r.returncode or not gpu.running(dest, run):
                raise RuntimeError("TARGET_CONTAINER_START_FAILED")
            if not waiter(dest, SERVED, STARTUP_TIMEOUT, run=run):
                raise RuntimeError("TARGET_API_NOT_READY")
            if (inspect(dest).get("Id") != p["target_id"]
                    or p3._gpu_conflicts(dest, run, inspect)):
                raise RuntimeError("TARGET_IDENTITY_OR_GPU_DRIFT")
            if not check_chat(SERVED):
                raise RuntimeError("TARGET_NORMAL_CHAT_NOT_VERIFIED")
            if target == "native-tools":
                tools = check_tools()
                result["structured_tool_call"] = (
                    tools.get("structured_tool_call") is True)
                result["tool_result_continuation"] = (
                    tools.get("tool_result_continuation") is True)
                result["tool_probe_issues"] = tools.get("issues", [])
                if (tools.get("status") != "LOCAL_STRUCTURED_TOOL_CYCLE_PASS"
                        or not result["structured_tool_call"]
                        or not result["tool_result_continuation"]):
                    raise RuntimeError("TARGET_NATIVE_TOOLS_TOOL_CYCLE_UNVERIFIED")
                streamed = check_stream()
                result["streamed_tool_call"] = (
                    streamed.get("streamed_tool_call") is True)
                result["stream_probe_issues"] = streamed.get("issues", [])
                if (streamed.get("status") != "LOCAL_STREAMED_TOOL_CALL_PASS"
                        or not result["streamed_tool_call"]):
                    raise RuntimeError("TARGET_NATIVE_TOOLS_STREAM_UNVERIFIED")
            _event(root, plan_id, "COMMITTED", {"active": dest})
            result["executed"] = True
            result["status"] = "COMMITTED"
            result["active_container"] = dest
        except (OSError, RuntimeError, ValueError, TypeError,
                subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            result["issues"].append(
                "SWITCH_ERROR_" + type(exc).__name__ + (
                    ":" + str(exc)[:80] if isinstance(exc, RuntimeError) else ""))
            if stopped:
                try:
                    target_doc = inspect(dest)
                    if (target_doc.get("Id") != p["target_id"]
                            or target_doc.get("Image") != p["image_id"]):
                        raise RuntimeError("TARGET_IDENTITY_CHANGED_CANNOT_STOP")
                    if (target_doc.get("State") or {}).get("Running"):
                        r = run(["docker", "stop", "--time", "45", dest],
                                timeout=80)
                        if r.returncode or gpu.running(dest, run):
                            raise RuntimeError("TARGET_STOP_FOR_ROLLBACK_FAILED")
                    for _ in range(30):
                        if gpu.port_free(run):
                            break
                        time.sleep(1)
                    else:
                        raise RuntimeError("PORT_NOT_FREE_FOR_ROLLBACK")
                    if p3._gpu_conflicts(source, run, inspect,
                                         require_source_running=False):
                        raise RuntimeError("FOREIGN_GPU_PREVENTS_ROLLBACK")
                    if inspect(source).get("Id") != p["source_id"]:
                        raise RuntimeError("SOURCE_ID_CHANGED_CANNOT_ROLLBACK")
                    if not gpu.running(source, run):
                        r = run(["docker", "start", source], timeout=90)
                        if r.returncode:
                            raise RuntimeError("SOURCE_RESTART_FAILED")
                    if (not waiter(source, SERVED, STARTUP_TIMEOUT, run=run)
                            or not check_chat(SERVED)):
                        raise RuntimeError("SOURCE_API_OR_CHAT_NOT_RESTORED")
                    _event(root, plan_id, "RESTORED", {"active": source})
                    result["status"] = "RESTORED"
                    result["source_restored"] = True
                except (OSError, RuntimeError, ValueError, TypeError,
                        subprocess.TimeoutExpired) as restore_exc:
                    result["status"] = "RECOVERY_FAILED"
                    result["issues"].append("RESTORE_ERROR_" + type(restore_exc).__name__)
                    try:
                        _event(root, plan_id, "RECOVERY_FAILED")
                    except (OSError, RuntimeError, ValueError):
                        result["issues"].append("RECOVERY_JOURNAL_WRITE_FAILED")
            else:
                try:
                    _event(root, plan_id, "CANCELLED")
                    result["status"] = "CANCELLED"
                except (OSError, RuntimeError, ValueError):
                    result["status"] = "RECOVERY_FAILED"
                    result["issues"].append("CANCELLED_JOURNAL_WRITE_FAILED")
        result["executed"] = result["executed"] or stopped
        try:
            p3._write_once(root, "result-" + plan_id + ".json", result)
        except (OSError, ValueError):
            result["status"] = "RECOVERY_EVIDENCE_INCOMPLETE"
            result["issues"].append("FINAL_RESULT_WRITE_FAILED")
        return (0 if result["status"] == "COMMITTED" else 4), result
    except (OSError, RuntimeError, ValueError, TypeError,
            BlockingIOError, subprocess.TimeoutExpired) as exc:
        return 3, _blocked(target, "EXECUTION_GUARD_ERROR_" + type(exc).__name__)
    finally:
        for fd in reversed(fds):
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Persistent original-27B <-> Native Tools V1 service switch")
    parser.add_argument("action", choices=("plan", "execute"))
    parser.add_argument("target", choices=tuple(TARGETS))
    args = parser.parse_args(argv)
    plan = make_plan(args.target)
    if args.action == "plan":
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0 if plan["status"] == READY else 3
    if plan.get("status") != READY:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 3
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("BLOCKED: a real interactive TTY is required")
        return 3
    print("Fresh plan SHA: " + plan["plan_id"])
    print("Expiry (epoch): " + str(plan["expires_at_epoch_seconds"]))
    print("Switch PERMANENTLY to " + args.target + " until another approved switch.")
    print("Port 8000 downtime. On failure rollback is attempted; host/Docker crash"
          " may prevent recovery.")
    try:
        approved = input("Type exact fresh 64-hex plan SHA: ").strip()
        ack = input("Type downtime acknowledgement " + ACK + ": ").strip()
        target_ack = input("Type target acknowledgement "
                           + ACK_TARGET[args.target] + ": ").strip()
    except (EOFError, KeyboardInterrupt):
        print("CANCELLED: no Docker modification")
        return 3
    old_handler = signal.getsignal(signal.SIGTERM)
    def _sigterm(_s: int, _frame: Any) -> None:
        raise KeyboardInterrupt("SERVICE_SWITCH_SIGTERM")
    signal.signal(signal.SIGTERM, _sigterm)
    try:
        code, result = execute(args.target, approved, ack, target_ack)
    finally:
        signal.signal(signal.SIGTERM, old_handler)
    print(json.dumps(result, indent=2, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
