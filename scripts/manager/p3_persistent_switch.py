"""P3 staged persistent switch executor: A flash->27B, B 27B->flash, C flash->27B.

No operation occurs from plan. Every stage is a distinct manually approved
stop-before-start action, with exact identity verification and best-effort
source restoration. Host/SIGKILL/daemon failures can defeat recovery.
This code is NOT evidence of a real DGX transition or GPU qualification.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager.p3_27b_roundtrip import latest_p2_benchmark
from scripts.manager.p3_p1_evidence_gate import assess_p1
from scripts.manager.service_journal import append_transition, read_snapshot
from scripts.manager.service_status import inspect_live_status

ROOT = Path.home() / ".local/state/blazux-wizard/p3"
LABEL = "blazux.p3.approved-stage-a"
ACK = gpu.ACK
ENTRY_ACK = "I_SEPARATELY_AUTHORIZE_P3_ENTRY"
NAMES = {"flash-next": gpu.ORIGINAL_CONTAINER, "27b": gpu.TARGET_CONTAINER}
IDS = {"flash-next": gpu.ORIGINAL_ID, "27b": gpu.SERVED}
DIRECTIONS = {"a": ("flash-next", "27b"),
              "b": ("27b", "flash-next"),
              "c": ("flash-next", "27b")}
SHA = re.compile(r"^[0-9a-f]{64}$")
SUCCESS = "READY_TO_REQUEST_TRANSITION_APPROVAL"


def _issue(code: str, *, stage: str, extra: list[str] | None = None) -> dict:
    return {"schema_version": 1, "stage": stage, "status": "BLOCKED",
            "executed": False, "plan_id": None,
            "operations_enabled": False, "approval_accepted": False,
            "issues": sorted(set([code, *(extra or [])]))}


def _private_dir(root: Path) -> None:
    if root.is_symlink():
        raise ValueError("P3_STATE_DIR_SYMLINK")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.stat().st_mode & 0o077:
        raise ValueError("P3_STATE_DIR_PERMISSIONS_UNSAFE")


def _read_receipt(root: Path, stage: str) -> tuple[dict, str]:
    path = root / ("stage-" + stage + ".json")
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 65536:
        raise ValueError("P3_STAGE_RECEIPT_MISSING_OR_UNTRUSTED")
    if path.stat().st_mode & 0o077:
        raise ValueError("P3_STAGE_RECEIPT_PERMISSIONS_UNSAFE")
    raw = path.read_bytes()
    doc = json.loads(raw)
    if (not isinstance(doc, dict) or doc.get("stage") != stage
            or doc.get("status") != "PASS" or doc.get("live_verified") is not True
            or not SHA.fullmatch(str(doc.get("plan_id", "")))):
        raise ValueError("P3_STAGE_RECEIPT_NOT_QUALIFIED")
    return doc, hashlib.sha256(raw).hexdigest()


def _write_once(root: Path, name: str, doc: dict) -> None:
    encoded = (json.dumps(doc, indent=2, sort_keys=True) + "\n").encode()
    fd = os.open(root / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as target:
        target.write(encoded)
        target.flush()
        os.fsync(target.fileno())


def _docker_names(run: Callable[..., Any]) -> list[str]:
    p = run(["docker", "ps", "-a", "--format", "{{.Names}}"])
    if p.returncode:
        raise RuntimeError("DOCKER_NAME_INVENTORY_FAILED")
    return p.stdout.splitlines()


def _gpu_conflicts(source: str, run: Callable[..., Any],
                   inspect: Callable[..., dict]) -> list[str]:
    p = run(["docker", "ps", "--format", "{{.Names}}"])
    if p.returncode or source not in p.stdout.splitlines():
        return ["RUNNING_GPU_SOURCE_UNVERIFIED"]
    issues = []
    for name in p.stdout.splitlines():
        if name == source:
            continue
        doc = inspect(name)
        host = doc.get("HostConfig") or {}
        env = (doc.get("Config") or {}).get("Env") or []
        visible = next((x.split("=", 1)[1] for x in env
                        if isinstance(x, str) and x.startswith("NVIDIA_VISIBLE_DEVICES=")), "")
        if host.get("DeviceRequests") or (host.get("Runtime") == "nvidia"
                                           and visible not in ("none", "void")):
            issues.append("OTHER_GPU_CONTAINER_RUNNING")
    return issues


def _container_checks(doc: dict, *, name: str, image: str,
                      expected_id: str | None, running: bool) -> list[str]:
    host = doc.get("HostConfig") or {}
    bindings = (host.get("PortBindings") or {}).get("8000/tcp")
    issues = []
    if doc.get("Name") != "/" + name:
        issues.append("CONTAINER_NAME_MISMATCH")
    if doc.get("Image") != image or not isinstance(image, str) or not image.startswith("sha256:"):
        issues.append("CONTAINER_IMAGE_MISMATCH")
    if expected_id and doc.get("Id") != expected_id:
        issues.append("CONTAINER_ID_MISMATCH")
    if not SHA.fullmatch(str(doc.get("Id") or "")):
        issues.append("CONTAINER_ID_UNVERIFIED")
    if (doc.get("State") or {}).get("Running") is not running:
        issues.append("CONTAINER_RUNNING_STATE_MISMATCH")
    if host.get("AutoRemove") is not False:
        issues.append("CONTAINER_AUTOREMOVE_UNSAFE")
    if (host.get("RestartPolicy") or {}).get("Name") not in ("no", "unless-stopped"):
        issues.append("CONTAINER_RESTART_POLICY_UNSAFE")
    if not isinstance(bindings, list) or len(bindings) != 1 or bindings[0].get("HostPort") != "8000":
        issues.append("CONTAINER_PORT_BINDING_MISMATCH")
    return issues


def make_plan(stage: str, *, root: Path = ROOT, reader=latest_p2_benchmark,
              live=inspect_live_status, trial_planner=gpu.make_plan,
              inspect=gpu.docker_info, run=gpu.call, now: float | None = None,
              p1_gate=assess_p1) -> dict[str, Any]:
    if stage not in DIRECTIONS:
        return _issue("P3_STAGE_INVALID", stage=stage)
    source, target = DIRECTIONS[stage]
    issues = []
    earlier = None
    earlier_sha = None
    first = None
    try:
        if root.is_symlink():
            raise ValueError("STATE_DIRECTORY_SYMLINK")
        if (root / ("stage-" + stage + ".json")).exists() or (root / ("attempt-" + stage + ".json")).exists():
            issues.append("P3_STAGE_ALREADY_ATTEMPTED")
        snapshot = read_snapshot(root / "journal")
        if snapshot and snapshot["phase"] not in ("COMMITTED", "RESTORED", "CANCELLED"):
            issues.append("UNRESOLVED_P3_TRANSITION_JOURNAL")
        if stage in ("b", "c"):
            first, _ = _read_receipt(root, "a")
            earlier, earlier_sha = _read_receipt(root, "a" if stage == "b" else "b")
            if stage == "b" and (root / "stage-c.json").exists():
                issues.append("P3_STAGE_ORDER_INVALID")
            if stage == "c" and earlier.get("source_model") != "27b":
                issues.append("P3_STAGE_B_PROVENANCE_INVALID")
        else:
            if any((root / ("stage-" + s + ".json")).exists() for s in ("a", "b", "c")):
                issues.append("P3_STAGE_ORDER_INVALID")
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        issues.append("P3_LOCAL_EVIDENCE_UNAVAILABLE:" + type(exc).__name__)
    try:
        observation = live()
    except (OSError, RuntimeError, TypeError, ValueError):
        observation = {"status": "BLOCKED", "issues": ["LIVE_OBSERVATION_UNAVAILABLE"]}
    if (observation.get("status") != "LIVE_SERVICE_VERIFIED"
            or observation.get("observed_model") != source
            or observation.get("expected_served_id") != IDS[source]
            or observation.get("issues")):
        issues.append("SOURCE_LIVE_API_IDENTITY_UNVERIFIED")

    try:
        names = _docker_names(run)
        if NAMES[source] not in names:
            issues.append("SOURCE_CONTAINER_MISSING")
        if stage == "a" and NAMES[target] in names:
            issues.append("P3_A_TARGET_CONTAINER_ALREADY_EXISTS")
        if stage in ("b", "c") and NAMES[target] not in names:
            issues.append("P3_TARGET_PRESERVED_CONTAINER_MISSING")
        if NAMES[source] in names:
            issues.extend(_gpu_conflicts(NAMES[source], run, inspect))
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
        issues.append("DOCKER_GPU_INVENTORY_UNVERIFIED")

    receipt = None
    evidence_sha = None
    try:
        receipt, receipt_issue = reader()
        if receipt_issue:
            issues.append(receipt_issue)
        elif not isinstance(receipt, dict) or not SHA.fullmatch(str(receipt.get("sha256") or "")):
            issues.append("P2_RECEIPT_HASH_UNVERIFIED")
        else:
            evidence_sha = receipt["sha256"]
    except (OSError, RuntimeError, ValueError, TypeError):
        issues.append("P2_RECEIPT_UNAVAILABLE")

    base = None
    if stage == "a":
        try:
            base = trial_planner()
            if base.get("status") != "READY_TO_REQUEST_TRIAL_APPROVAL":
                issues.extend(base.get("issues") or ["P2_REUSABLE_SOURCE_PREFLIGHT_BLOCKED"])
        except (OSError, RuntimeError, ValueError, TypeError, subprocess.TimeoutExpired):
            issues.append("P3_A_PINNED_TARGET_PREFLIGHT_UNAVAILABLE")

    flash_id = (base or {}).get("source_container_id") if stage == "a" else (first or {}).get("flash_id")
    flash_image = (base or {}).get("image_id") if stage == "a" else (first or {}).get("flash_image")
    target_image = (base or {}).get("image_id") if stage == "a" else (first or {}).get("image_27b")
    id_27b = (first or {}).get("id_27b")
    if (stage != "a" and first and first.get("p2_receipt_sha256") != evidence_sha):
        issues.append("P2_RECEIPT_CHANGED_SINCE_STAGE_A")
    if stage == "c" and earlier:
        evidence = p1_gate(stage_b=earlier, flash_image=flash_image, p3_root=root)
        if evidence.get("status") != "PASS":
            issues.extend(evidence.get("issues") or ["P1_REMEDIATION_NOT_QUALIFIED"])
    else:
        evidence = None

    source_image = flash_image if source == "flash-next" else target_image
    target_image_actual = flash_image if target == "flash-next" else target_image
    source_id = flash_id if source == "flash-next" else id_27b
    expected_target_id = None if stage == "a" else (flash_id if target == "flash-next" else id_27b)
    src_doc = None
    tgt_doc = None
    try:
        if isinstance(source_image, str):
            src_doc = inspect(NAMES[source])
            issues.extend(_container_checks(src_doc, name=NAMES[source], image=source_image,
                                             expected_id=source_id, running=True))
            source_id = src_doc.get("Id")
        else:
            issues.append("SOURCE_IMAGE_NOT_PINNED")
        if stage != "a" and isinstance(target_image_actual, str):
            tgt_doc = inspect(NAMES[target])
            issues.extend(_container_checks(tgt_doc, name=NAMES[target], image=target_image_actual,
                                             expected_id=expected_target_id, running=False))
            if (target == "27b" and
                    ((tgt_doc.get("Config") or {}).get("Labels") or {}).get(LABEL) != first.get("plan_id")):
                issues.append("TARGET_27B_PROVENANCE_UNVERIFIED")
            if (source == "27b" and
                    ((src_doc.get("Config") or {}).get("Labels") or {}).get(LABEL) != first.get("plan_id")):
                issues.append("SOURCE_27B_PROVENANCE_UNVERIFIED")
    except (OSError, RuntimeError, ValueError, TypeError, subprocess.TimeoutExpired):
        issues.append("SOURCE_TARGET_DOCKER_INSPECTION_UNVERIFIED")
    if stage == "a" and (base or {}).get("source_container_id") != source_id:
        issues.append("P2_SOURCE_IDENTITY_DRIFT")

    window = int(time.time() if now is None else now) // 600
    facts = {"kind": "P3-PERSISTENT-SWITCH-V1", "stage": stage, "source": source,
             "target": target, "source_id": source_id, "source_image": source_image,
             "target_image": target_image_actual, "expected_target_id": expected_target_id,
             "flash_id": flash_id, "flash_image": flash_image, "image_27b": target_image,
             "id_27b": id_27b, "prior_sha256": earlier_sha,
             "p2_receipt_sha256": evidence_sha, "p1_evidence": evidence,
             "port": 8000, "window": window}
    pid = (hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()
           if not issues else None)
    return {"schema_version": 1, "stage": stage,
            "action": "P3_MANUAL_PERSISTENT_SWITCH", "source_model": source,
            "target_model": target, "status": SUCCESS if not issues else "BLOCKED",
            "issues": sorted(set(issues)), "executed": False, "operations_enabled": False,
            "approval_accepted": False, "plan_id": pid,
            "expires_at_epoch_seconds": (window + 1) * 600,
            "source_container_id": source_id, "source_image": source_image,
            "target_image": target_image_actual, "target_container_id": expected_target_id,
            "flash_id": flash_id, "flash_image": flash_image,
            "image_27b": target_image, "id_27b": id_27b,
            "p2_receipt_sha256": evidence_sha,
            "p3_a_plan_id": (first or {}).get("plan_id"),
            "p1_evidence": evidence,
            "required_downtime_acknowledgement": ACK,
            "required_p3_entry_acknowledgement": ENTRY_ACK if stage == "a" else None,
            "notice": "PLAN ONLY: no Docker/GPU changes. Any execution requires fresh exact plan, explicit downtime and (stage A) separate P3 entry. Stage C requires P1 actual evidence."}


def _record(root: Path, phase: str, source: str, target: str,
            observed: str | None, plan_id: str) -> None:
    folder = root / "journal"
    previous = read_snapshot(folder)
    append_transition(folder, phase=phase, from_model=source, to_model=target,
                      observed_model=observed,
                      expected_previous_hash=previous["event_hash"] if previous else None,
                      plan_id=plan_id)


def _restore(stage: str, source: str, target: str, source_id: str,
             source_image: str, target_image: str, plan_id: str, *,
             expected_target_id: str | None = None,
             run, inspect, waiter, live) -> dict[str, Any]:
    issues = []
    try:
        names = _docker_names(run)
        if NAMES[target] in names:
            doc = inspect(NAMES[target])
            if stage == "a":
                label = ((doc.get("Config") or {}).get("Labels") or {}).get(LABEL)
                if label != plan_id or doc.get("Image") != target_image:
                    return {"status": "RECOVERY_FAILED", "issues": ["FOREIGN_TARGET_PRESERVED"]}
            elif doc.get("Image") != target_image or doc.get("Id") != expected_target_id:
                return {"status": "RECOVERY_FAILED", "issues": ["FOREIGN_TARGET_ID_OR_IMAGE_CHANGED"]}
            if (doc.get("State") or {}).get("Running"):
                if run(["docker", "stop", "--time", "30", NAMES[target]], timeout=55).returncode:
                    return {"status": "RECOVERY_FAILED", "issues": ["TARGET_STOP_FAILED"]}
                if gpu.running(NAMES[target], run):
                    return {"status": "RECOVERY_FAILED", "issues": ["TARGET_STILL_RUNNING"]}
            if stage == "a" and run(["docker", "rm", NAMES[target]]).returncode:
                issues.append("OWNED_FAILED_27B_REMOVE_FAILED")
        elif stage != "a":
            issues.append("PRESERVED_TARGET_DISAPPEARED")
        src = inspect(NAMES[source])
        if src.get("Id") != source_id or src.get("Image") != source_image:
            return {"status": "RECOVERY_FAILED", "issues": ["SOURCE_ID_IMAGE_DRIFT"]}
        if not gpu.port_free(run):
            return {"status": "RECOVERY_FAILED", "issues": ["PORT_8000_NOT_FREE_FOR_RESTORE"]}
        if not (src.get("State") or {}).get("Running") and run(
                ["docker", "start", NAMES[source]], timeout=90).returncode:
            return {"status": "RECOVERY_FAILED", "issues": ["SOURCE_RESTART_FAILED"]}
        if not waiter(NAMES[source], IDS[source], 240, run=run):
            issues.append("SOURCE_API_NOT_RESTORED")
        observed = live()
        if (observed.get("status") != "LIVE_SERVICE_VERIFIED"
                or observed.get("observed_model") != source
                or observed.get("expected_served_id") != IDS[source]):
            issues.append("SOURCE_LIVE_SERVICE_NOT_RESTORED")
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        issues.append("RECOVERY_EXCEPTION:" + type(exc).__name__)
    return {"status": "RESTORED" if not issues else "RECOVERY_FAILED",
            "issues": issues}


def execute(stage: str, plan_id: str | None, ack: str | None,
            enter_p3: str | None = None, *, root: Path = ROOT,
            planner=make_plan, run=gpu.call, inspect=gpu.docker_info,
            waiter=gpu.wait_for, live=inspect_live_status) -> tuple[int, dict]:
    if (stage not in DIRECTIONS or not isinstance(plan_id, str)
            or not SHA.fullmatch(plan_id) or ack != ACK
            or (stage == "a" and enter_p3 != ENTRY_ACK)
            or (stage != "a" and enter_p3 is not None)):
        return 3, _issue("P3_STAGE_PLAN_DOWNTIME_AND_ENTRY_ACK_REQUIRED", stage=stage)
    try:
        _private_dir(root)
        fd = os.open(root / "p3-execution.lock", os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    except (OSError, ValueError):
        return 3, _issue("P3_PRIVATE_STATE_LOCK_UNAVAILABLE", stage=stage)
    with os.fdopen(fd, "w+") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return 3, _issue("P3_CONCURRENT_EXECUTION_BLOCKED", stage=stage)
        fresh = planner(stage, root=root)
        if fresh.get("status") != SUCCESS or fresh.get("plan_id") != plan_id:
            return 3, _issue("P3_STALE_PLAN_OR_CHANGED_PREFLIGHT", stage=stage,
                              extra=fresh.get("issues"))
        source, target = DIRECTIONS[stage]
        source_id = fresh["source_container_id"]
        source_image, target_image = fresh["source_image"], fresh["target_image"]
        started = False
        old_stop_attempted = False
        phase = None
        recovered = None
        try:
            # An immutable local attempt marker blocks same-window retries after interruption.
            _write_once(root, "attempt-" + stage + ".json",
                        {"stage": stage, "plan_id": plan_id,
                         "started_at_utc": datetime.now(timezone.utc).isoformat()})
            previous = read_snapshot(root / "journal")
            if previous is None or previous["phase"] in ("COMMITTED", "RESTORED", "CANCELLED"):
                _record(root, "OBSERVED", source, target, source, plan_id)
            _record(root, "PLANNED", source, target, source, plan_id)
            _record(root, "OLD_STOPPING", source, target, source, plan_id)
            phase = "OLD_STOPPING"
            src = inspect(NAMES[source])
            if src.get("Id") != source_id or src.get("Image") != source_image:
                raise RuntimeError("SOURCE_CHANGED_BEFORE_STOP")
            old_stop_attempted = True
            if run(["docker", "stop", "--time", "45", NAMES[source]], timeout=80).returncode:
                raise RuntimeError("SOURCE_STOP_FAILED")
            if gpu.running(NAMES[source], run):
                raise RuntimeError("SOURCE_STILL_RUNNING")
            _record(root, "OLD_STOPPED", source, target, None, plan_id)
            phase = "OLD_STOPPED"
            for _ in range(20):
                if gpu.port_free(run):
                    break
                time.sleep(1)
            else:
                raise RuntimeError("PORT_8000_NOT_RELEASED")
            # Re-observe before mutating another Docker object. A free name
            # or a preserved target ID from the plan is never sufficient on
            # its own at execution time.
            names_before_start = _docker_names(run)
            if stage == "a":
                if NAMES[target] in names_before_start:
                    raise RuntimeError("P3_A_TARGET_NAME_BECAME_OCCUPIED")
            else:
                if NAMES[target] not in names_before_start:
                    raise RuntimeError("PRESERVED_TARGET_DISAPPEARED")
                target_before = inspect(NAMES[target])
                if _container_checks(
                        target_before, name=NAMES[target], image=target_image,
                        expected_id=fresh["target_container_id"], running=False):
                    raise RuntimeError("PRESERVED_TARGET_CHANGED_BEFORE_START")
                if (target == "27b" and
                        ((target_before.get("Config") or {}).get("Labels") or {}).get(LABEL)
                        != fresh.get("p3_a_plan_id")):
                    raise RuntimeError("P3_TARGET_27B_PROVENANCE_CHANGED")
            _record(root, "NEW_STARTING", source, target, None, plan_id)
            phase = "NEW_STARTING"
            if stage == "a":
                command = gpu.trial_command(target_image, plan_id)
                command = [x.replace(gpu.LABEL + "=" + plan_id, LABEL + "=" + plan_id)
                           for x in command]
            else:
                command = ["docker", "start", NAMES[target]]
            if run(command, timeout=90).returncode:
                raise RuntimeError("TARGET_START_FAILED")
            started = True
            _record(root, "NEW_VERIFYING", source, target, target, plan_id)
            phase = "NEW_VERIFYING"
            if not waiter(NAMES[target], IDS[target], 600, run=run):
                raise RuntimeError("TARGET_API_NOT_READY")
            target_doc = inspect(NAMES[target])
            if (target_doc.get("Image") != target_image or
                    target_doc.get("Name") != "/" + NAMES[target] or
                    (stage != "a" and target_doc.get("Id") != fresh["target_container_id"]) or
                    not (target_doc.get("State") or {}).get("Running")):
                raise RuntimeError("TARGET_IDENTITY_CHANGED")
            observed = live()
            if (observed.get("status") != "LIVE_SERVICE_VERIFIED"
                    or observed.get("observed_model") != target
                    or observed.get("expected_served_id") != IDS[target]
                    or observed.get("issues")):
                raise RuntimeError("TARGET_LIVE_MANIFEST_API_MISMATCH")
            source_after = inspect(NAMES[source])
            if (source_after.get("Id") != source_id or
                    source_after.get("Image") != source_image or
                    (source_after.get("State") or {}).get("Running")):
                raise RuntimeError("PRESERVED_SOURCE_NOT_VERIFIED")
            _record(root, "COMMITTED", source, target, target, plan_id)
            phase = "COMMITTED"
            receipt = {"schema_version": 1, "stage": stage, "status": "PASS",
                       "plan_id": plan_id, "source_model": source, "target_model": target,
                       "source_id": source_id, "target_id": target_doc["Id"],
                       "source_image": source_image, "target_image": target_image,
                       "flash_id": fresh["flash_id"],
                       "flash_image": fresh["flash_image"],
                       "image_27b": fresh["image_27b"],
                       "id_27b": (target_doc["Id"] if stage == "a" else fresh["id_27b"]),
                       "p2_receipt_sha256": fresh["p2_receipt_sha256"],
                       "p1_evidence": fresh.get("p1_evidence"),
                       "live_verified": True, "executed": True,
                       "finished_at_utc": datetime.now(timezone.utc).isoformat()}
            _write_once(root, "stage-" + stage + ".json", receipt)
            return 0, {"status": "PASS", "stage": stage, "executed": True,
                       "active_model": target, "live_verified": True,
                       "evidence": str(root / ("stage-" + stage + ".json")),
                       "notice": "Target intentionally remains running; no automatic next phase."}
        except (KeyboardInterrupt, SystemExit):
            error_code = "P3_EXECUTION_INTERRUPTED"
        except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
            error_code = str(exc) if isinstance(exc, RuntimeError) else "P3_EXECUTION_" + type(exc).__name__
        if phase == "COMMITTED":
            # Journal committed but immutable success receipt could not be written.
            # Never secretly rollback a verified live target without a journal entry.
            return 4, {"status": "COMMITTED_EVIDENCE_INCOMPLETE",
                       "stage": stage, "executed": True, "active_model": target,
                       "live_verified": True, "issues": [error_code],
                       "notice": "Manual reconciliation; cannot proceed to next stage."}
        if phase != "COMMITTED":
            try:
                if phase == "OLD_STOPPING":
                    _record(root, "FAILED", source, target, None, plan_id)
                    phase = "FAILED"
                if phase in ("FAILED", "OLD_STOPPED", "NEW_STARTING", "NEW_VERIFYING"):
                    _record(root, "ROLLBACK_STARTING", source, target, None, plan_id)
                    phase = "ROLLBACK_STARTING"
            except (OSError, RuntimeError, ValueError):
                error_code += ":JOURNAL_UPDATE_FAILED"
        if old_stop_attempted:
            recovered = _restore(stage, source, target, source_id, source_image,
                                 target_image, plan_id,
                                 expected_target_id=fresh["target_container_id"],
                                 run=run, inspect=inspect, waiter=waiter, live=live)
            try:
                if phase == "ROLLBACK_STARTING":
                    _record(root, recovered["status"], source, target,
                            source if recovered["status"] == "RESTORED" else None, plan_id)
            except (OSError, ValueError, RuntimeError):
                recovered = {"status": "RECOVERY_FAILED",
                             "issues": ["RESTORE_JOURNAL_WRITE_FAILED", *recovered.get("issues", [])]}
        else:
            recovered = {"status": "NOT_NEEDED", "issues": []}
        return 4, {"status": ("RECOVERY_FAILED" if recovered["status"] == "RECOVERY_FAILED"
                             else "FAIL_RESTORED" if recovered["status"] == "RESTORED"
                             else "BLOCKED"),
                   "stage": stage, "executed": old_stop_attempted, "error_code": error_code,
                   "restoration": recovered, "active_model": source if recovered["status"] == "RESTORED" else None,
                   "issues": [error_code, *recovered.get("issues", [])]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Guarded P3 persistent transition, separate approval per stage")
    parser.add_argument("stage", choices=("a", "b", "c"))
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    parser.add_argument("--enter-p3")
    args = parser.parse_args(argv)
    if args.plan:
        if args.approve_plan or args.ack_downtime or args.enter_p3:
            doc = _issue("P3_PLAN_MUST_NOT_INCLUDE_EXECUTION_APPROVAL", stage=args.stage)
        else:
            doc = make_plan(args.stage)
        print(json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=2))
        return 0 if doc["status"] == SUCCESS else 3
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    rc, doc = execute(args.stage, args.approve_plan, args.ack_downtime, args.enter_p3)
    print(json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=2))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
