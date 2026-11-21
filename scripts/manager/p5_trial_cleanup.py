"""P5 failed trial container retirement with exact approval, never implicit deletion.

Keeps the live v3 development service intact. Preserves bounded private log
evidence before deleting ONLY an allowlisted, exited nonzero P5 trial container.
Images, pinned checkpoint, PLE mmap backing, caches and other services untouched.
"""
from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import time

from scripts.manager import p5_live_trial as live

ACK = "I_APPROVE_P5_FAILED_TRIAL_CONTAINERS_ONLY"
ALLOWED = (
    "qwen38-orcarouter",
    "qwen38-orcarouter-qsa62318",
    "qwen38-orcarouter-qsa62318-lmhead",
)
LOG_LIMIT = 1024 * 1024
PRIVATE_LOG_TAIL = 200
PLAN_RE = re.compile(r"[0-9a-f]{64}\Z")


def _blocked(*issues: str) -> dict:
    return {"status": "BLOCKED", "issues": sorted(set(issues)),
            "action": "P5_FAILED_TRIAL_CLEANUP", "executed": False,
            "plan_id": None, "preserve_live_v3": True,
            "preserve_images_and_checkpoints": True}


def _inspect_if_exists(name: str) -> dict | None:
    response = live.command(["docker", "container", "inspect", name])
    if response.returncode:
        if response.returncode == 1 and (
            "No such object" in response.stderr
            or "No such container" in response.stderr
        ):
            return None
        raise ValueError("DOCKER_CLEANUP_TARGET_INVENTORY_UNAVAILABLE")
    obj = json.loads(response.stdout)
    if not isinstance(obj, list) or len(obj) != 1 or not isinstance(obj[0], dict):
        raise ValueError("DOCKER_CLEANUP_TARGET_INVALID_JSON")
    return obj[0]


def _valid_command(doc: dict) -> bool:
    cmd = (doc.get("Config") or {}).get("Cmd")
    if not isinstance(cmd, list) or any(not isinstance(v, str) for v in cmd):
        return False
    # Legacy P5 attempts must be proven to contain the exact pinned source.
    return (
        live.MODEL_IN_CONTAINER in cmd
        and "--served-model-name" in cmd
        and live.ALIAS in cmd
        and "--port" in cmd
        and "8000" in cmd
    )


def _port_binding(doc: dict) -> bool:
    port_bindings = ((doc.get("HostConfig") or {}).get("PortBindings") or {})
    return any(
        item.get("HostPort") == "8000"
        for item in (port_bindings.get("8000/tcp") or [])
        if isinstance(item, dict)
    )


def _valid_mount(doc: dict) -> bool:
    mounts = doc.get("Mounts") or []
    return any(
        isinstance(item, dict)
        and item.get("Destination") == "/hf"
        and item.get("RW") is False
        and item.get("Type") == "bind"
        and item.get("Source") == str(live.CACHE)
        for item in mounts
    )


def _read_live() -> dict:
    doc = live.docker_json(live.TARGET)
    state = doc.get("State") or {}
    if (doc.get("Name") != "/" + live.TARGET
        or state.get("Running") is not True
        or state.get("Status") != "running"
        or not live.DIGEST.fullmatch(doc.get("Image") or "")
        or not isinstance(doc.get("Id"), str)
        or not re.fullmatch(r"[0-9a-f]{64}", doc["Id"])
        or not _port_binding(doc)
        or not _valid_command(doc)
        or live.api_ids() != [live.ALIAS]):
        raise ValueError("ACTIVE_P5_V3_IDENTITY_NOT_VERIFIED")
    return {"name": live.TARGET, "container_id": doc["Id"],
            "image_id": doc["Image"], "api_model_id": live.ALIAS}


def _candidate(name: str) -> dict | None:
    if name not in ALLOWED:
        raise ValueError("P5_CLEANUP_TARGET_NOT_ALLOWLISTED")
    doc = _inspect_if_exists(name)
    if doc is None:
        return None
    state = doc.get("State") or {}
    cid = doc.get("Id")
    image_id = doc.get("Image")
    if (doc.get("Name") != "/" + name
        or not isinstance(cid, str)
        or not re.fullmatch(r"[0-9a-f]{64}", cid)
        or not isinstance(image_id, str)
        or not live.DIGEST.fullmatch(image_id)
        or state.get("Running") is not False
        or state.get("Status") != "exited"
        or type(state.get("ExitCode")) is not int
        or state["ExitCode"] == 0
        or not _valid_command(doc)
        or not _port_binding(doc)
        or not _valid_mount(doc)):
        raise ValueError("P5_CLEANUP_UNVERIFIED_OR_NONFAILED_TARGET_" + name)
    return {"name": name, "container_id": cid, "image_id": image_id,
            "exit_code": state["ExitCode"]}


def _fingerprint(doc: dict) -> str:
    return hashlib.sha256(json.dumps(
        doc, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def plan(*, now: float | None = None) -> dict:
    """Read-only exact target and current running v3 inventory; never stop/rm."""
    try:
        active = _read_live()
        targets = []
        for name in ALLOWED:
            entry = _candidate(name)
            if entry is not None:
                targets.append(entry)
        if not targets:
            return {"status": "NOTHING_TO_CLEAN", "action": "P5_FAILED_TRIAL_CLEANUP",
                    "executed": False, "issues": [], "plan_id": None,
                    "active": active, "targets": [], "preserve_live_v3": True}
        window = int(time.time() if now is None else now) // 900
        facts = {"active": active, "targets": targets, "window": window,
                 "operation": "P5_EXITED_FAILED_CONTAINERS_ONLY"}
        return {"status": "READY_TO_APPROVE",
                "action": "P5_FAILED_TRIAL_CLEANUP",
                "issues": [], "executed": False,
                "approval_accepted": False,
                "plan_id": _fingerprint(facts),
                "expires_at_epoch_seconds": (window + 1) * 900,
                "acknowledgement": ACK, "active": active, "targets": targets,
                "preserve_live_v3": True,
                "preserve_images_and_checkpoints": True,
                "log_archive": str(live.STATE / "cleanup"),
                "notice": "Requires exact plan and ACK. Archive private logs before "
                          "docker rm of exited P5 failures. Never stop live v3 or "
                          "remove images, cached checkpoints, OpenWebUI, Portainer."}
    except (OSError, ValueError, TypeError, KeyError, RuntimeError,
            json.JSONDecodeError) as exc:
        return _blocked("P5_FAILED_CLEANUP_PLAN_" + type(exc).__name__ +
                        ":" + str(exc)[:100])


def _write_private(path: Path, data: bytes) -> None:
    if path.is_symlink():
        raise ValueError("P5_CLEANUP_EVIDENCE_SYMLINK")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "wb") as file:
        file.write(data)
        file.flush()
        os.fsync(file.fileno())


def execute(plan_id: str | None, acknowledgement: str | None) -> dict:
    """Explicit opt-in cleanup: exact-identity recheck before each docker rm."""
    if (not isinstance(plan_id, str) or not PLAN_RE.fullmatch(plan_id)
        or acknowledgement != ACK):
        return _blocked("P5_CLEANUP_EXACT_PLAN_AND_ACK_REQUIRED")
    result = _blocked("P5_CLEANUP_NOT_EXECUTED")
    try:
        live._private_state()
        log_dir = live.STATE / "cleanup"
        if log_dir.is_symlink():
            raise ValueError("P5_CLEANUP_LOG_DIRECTORY_SYMLINK")
        log_dir.mkdir(mode=0o700, exist_ok=True)
        if log_dir.stat().st_mode & 0o077:
            raise ValueError("P5_CLEANUP_EVIDENCE_DIR_PERMISSIONS")
        with (live.STATE / "p5-trial.lock").open("a+") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            current = plan()
            if current["status"] != "READY_TO_APPROVE" or current["plan_id"] != plan_id:
                return _blocked("P5_CLEANUP_CHANGED_OR_EXPIRED_PLAN")
            if time.time() >= current["expires_at_epoch_seconds"]:
                return _blocked("P5_CLEANUP_EXPIRED_PLAN")
            result = {"status": "CLEANUP_IN_PROGRESS",
                      "action": "P5_FAILED_TRIAL_CLEANUP", "executed": False,
                      "issues": [], "deleted": [], "evidence": [],
                      "preserve_live_v3": True,
                      "preserve_images_and_checkpoints": True}
            active_id = current["active"]["container_id"]
            for entry in current["targets"]:
                if _read_live()["container_id"] != active_id:
                    raise ValueError("P5_CLEANUP_ACTIVE_SERVICE_CHANGED")
                fresh = _candidate(entry["name"])
                if fresh != entry:
                    raise ValueError("P5_CLEANUP_FAILED_CONTAINER_CHANGED")
                logs = live.command(["docker", "logs", "--timestamps",
                                     "--tail", str(PRIVATE_LOG_TAIL),
                                     entry["name"]], timeout=30)
                if logs.returncode:
                    raise ValueError("P5_CLEANUP_DOCKER_LOGS_FAILED")
                data = (logs.stdout + logs.stderr).encode()
                if not data or len(data) > LOG_LIMIT:
                    raise ValueError("P5_CLEANUP_LOGS_EMPTY_OR_TOO_LARGE")
                basename = entry["name"] + "-" + entry["container_id"][:12]
                filename = log_dir / (basename + ".log")
                _write_private(filename, data)
                receipt = {
                    "schema_version": 1, "operation": "P5_FAILED_TRIAL_CONTAINER_CLEANUP",
                    "plan_id": plan_id, "target": entry,
                    "log_file": str(filename), "log_sha256": hashlib.sha256(data).hexdigest(),
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                }
                _write_private(log_dir / (basename + ".json"),
                               (json.dumps(receipt, indent=2, sort_keys=True) + "\n").encode())
                result["evidence"].append(str(filename))
                if _read_live()["container_id"] != active_id:
                    raise ValueError("P5_CLEANUP_ACTIVE_SERVICE_CHANGED")
                if _candidate(entry["name"]) != entry:
                    raise ValueError("P5_CLEANUP_FAILED_CONTAINER_CHANGED")
                response = live.command(["docker", "rm", entry["name"]], timeout=60)
                if response.returncode:
                    raise ValueError("P5_CLEANUP_DOCKER_RM_FAILED")
                if _inspect_if_exists(entry["name"]) is not None:
                    raise ValueError("P5_CLEANUP_RM_NOT_CONFIRMED")
                result["executed"] = True
                result["deleted"].append(entry["name"])
            if _read_live()["container_id"] != active_id:
                raise ValueError("P5_CLEANUP_ACTIVE_SERVICE_CHANGED_AFTER")
            result["status"] = "PASS"
            return result
    except (OSError, ValueError, TypeError, KeyError, RuntimeError,
            BlockingIOError) as exc:
        result["status"] = ("PARTIAL_CLEANUP_REQUIRES_RECONCILIATION"
                            if result.get("deleted") else "BLOCKED")
        result["issues"] = ["P5_CLEANUP_" + type(exc).__name__ + ":" + str(exc)[:120]]
        return result
