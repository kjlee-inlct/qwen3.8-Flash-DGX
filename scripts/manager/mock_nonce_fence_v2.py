"""P6-E FAKE-ONLY persistent nonce replay experiment for registered model pairs.

All writes are confined to an ephemeral 0700 blazux-p6e-fake-* directory.
Never opens the operating journal, authenticates approvals, starts Docker,
or grants migration, switching, or recovery permission. A crash/partial marker
is retained and blocks reuse; it is never automatically reclaimed.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

from scripts.manager.generic_operations import model_catalog

PREFIX = "blazux-p6e-fake-"
ORIGIN = "FAKE_P6E_NONCE_LEDGER_NO_OPERATING_AUTHORITY"
MAX_TTL_NS = 60_000_000_000
MAX_MARKER_BYTES = 4096


def _hash(doc: dict) -> str:
    return hashlib.sha256(json.dumps(
        doc, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")).hexdigest()


def _root(folder: Path) -> Path:
    folder = Path(folder)
    if not folder.name.startswith(PREFIX):
        raise ValueError("FAKE_DIRECTORY_PREFIX_REQUIRED")
    mode = os.lstat(folder).st_mode
    if not stat.S_ISDIR(mode) or (mode & 0o077):
        raise ValueError("FAKE_DIRECTORY_PRIVATE_REAL_DIRECTORY_REQUIRED")
    return folder


def _record(source: str, target: str, source_id: str, target_id: str,
            plan_id: str, nonce: str, *, now_ns: int, expires_ns: int) -> dict:
    names = model_catalog()["models"]
    if source not in names or target not in names or source == target:
        raise ValueError("UNREGISTERED_OR_SAME_MODEL_PAIR")
    ids = (source_id, target_id, plan_id, nonce)
    if (any(not isinstance(x, str) or len(x) != 64
            or any(c not in "0123456789abcdef" for c in x) for x in ids)
            or source_id == target_id):
        raise ValueError("FAKE_IDENTITY_PLAN_NONCE_INVALID")
    if (type(now_ns) is not int or type(expires_ns) is not int
            or not 0 < expires_ns - now_ns <= MAX_TTL_NS):
        raise ValueError("FAKE_TTL_EXPIRED_OR_UNBOUNDED")
    doc = {
        "schema_version": 2, "record_origin": ORIGIN,
        "source_model": source, "target_model": target,
        "source_container_id": source_id, "target_container_id": target_id,
        "plan_id": plan_id, "nonce": nonce, "expires_at_ns": expires_ns,
        "api_host_port": 8000, "max_active_gpu_models": 1,
        "requires_independent_approval": True,
        "requires_live_revalidation": True,
    }
    doc["record_hash"] = _hash(doc)
    return doc


def _result(status: str, issues: list[str], *, marker_created: bool = False) -> dict:
    return {
        "schema_version": 2, "stage": "p6",
        "action": "fake-nonce-replay-fence",
        "scope": "TEMPORARY_FAKE_DISK_ONLY_NOT_OPERATING_JOURNAL",
        "status": status, "issues": sorted(set(issues)),
        "fake_durable_marker_created": marker_created,
        "real_operating_nonce_fence_verified": False,
        "approval_accepted": False, "executed": False,
        "operations_enabled": False, "resume_eligible": False,
        "automatic_recovery_authorized": False,
        "production_released": False, "real_dgx_verified": False,
    }


def fake_nonce_claim(folder: Path, source: str, target: str,
                     source_id: str, target_id: str, plan_id: str,
                     nonce: str, *, now_ns: int, expires_ns: int) -> dict:
    """O_EXCL is atomic across processes on the local fake filesystem.

    A duplicate nonce is rejected globally within this fake ledger even when
    the pair, Docker IDs or plan differ. A partial marker stays blocked.
    This is a fixture experiment, NOT an operating cross-process authority.
    """
    root = _root(folder)
    doc = _record(source, target, source_id, target_id, plan_id,
                  nonce, now_ns=now_ns, expires_ns=expires_ns)
    path = root / ("fake-nonce-" + nonce + ".json")
    raw = (json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(raw) > MAX_MARKER_BYTES:
        raise ValueError("FAKE_MARKER_TOO_LARGE")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, 0o600)
    except FileExistsError:
        return _result("BLOCKED_FAKE_NONCE_REPLAY",
                       ["FAKE_NONCE_REPLAY_OR_COLLISION"])
    except OSError:
        return _result("BLOCKED_FAKE_NONCE_IO",
                       ["FAKE_NONCE_MARKER_CREATE_FAILED"])
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        directory_fd = os.open(
            root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError:
        # Do NOT unlink: ambiguous partial/crash state must stop replay.
        return _result("BLOCKED_FAKE_NONCE_IO",
                       ["FAKE_NONCE_DURABILITY_UNKNOWN"])
    return _result("PASS_FAKE_NONCE_MARKER_CREATED", [], marker_created=True)


def fake_nonce_audit(folder: Path, source: str, target: str,
                     source_id: str, target_id: str, plan_id: str,
                     nonce: str, *, now_ns: int, expires_ns: int) -> dict:
    """Read-back detects tamper/partial/permission errors; never authorizes."""
    root = _root(folder)
    expected = _record(source, target, source_id, target_id, plan_id, nonce,
                       now_ns=now_ns, expires_ns=expires_ns)
    path = root / ("fake-nonce-" + nonce + ".json")
    try:
        info = os.lstat(path)
        if not stat.S_ISREG(info.st_mode) or stat.S_IMODE(info.st_mode) != 0o600:
            raise ValueError("FAKE_MARKER_NOT_PRIVATE_REGULAR_FILE")
        if info.st_size > MAX_MARKER_BYTES or info.st_size == 0:
            raise ValueError("FAKE_MARKER_TRUNCATED_OR_UNBOUNDED")
        with path.open("rb") as stream:
            raw = stream.read(MAX_MARKER_BYTES + 1)
        if len(raw) > MAX_MARKER_BYTES:
            raise ValueError("FAKE_MARKER_UNBOUNDED")
        actual = json.loads(raw)
        if type(actual) is not dict or actual != expected:
            raise ValueError("FAKE_MARKER_IDENTITY_OR_HASH_MISMATCH")
    except (OSError, ValueError, TypeError, UnicodeError) as exc:
        return _result("BLOCKED_FAKE_NONCE_AUDIT", [str(exc)])
    return _result("PASS_FAKE_NONCE_MARKER_CONSISTENCY", [])


def fake_replay_fence_demo(source: str, target: str) -> dict:
    """One isolated 3-check CPU rehearsal; no caller-controlled disk path."""
    source_id, target_id = "a" * 64, "b" * 64
    plan_id, nonce = "c" * 64, "d" * 64
    with tempfile.TemporaryDirectory(prefix=PREFIX) as temp:
        folder = Path(temp)
        first = fake_nonce_claim(folder, source, target, source_id, target_id,
                                 plan_id, nonce, now_ns=100, expires_ns=200)
        audit = fake_nonce_audit(folder, source, target, source_id, target_id,
                                 plan_id, nonce, now_ns=100, expires_ns=200)
        replay = fake_nonce_claim(folder, source, target, source_id, target_id,
                                  plan_id, nonce, now_ns=100, expires_ns=200)
        changed_plan = fake_nonce_claim(folder, source, target, source_id,
                                        target_id, "e" * 64, nonce,
                                        now_ns=100, expires_ns=200)
        passed = (first["status"] == "PASS_FAKE_NONCE_MARKER_CREATED"
                  and audit["status"] == "PASS_FAKE_NONCE_MARKER_CONSISTENCY"
                  and replay["status"] == "BLOCKED_FAKE_NONCE_REPLAY"
                  and changed_plan["status"] == "BLOCKED_FAKE_NONCE_REPLAY")
    return {
        "schema_version": 2, "stage": "p6", "action": "nonce-fence-mock",
        "scope": "ISOLATED_FAKE_DGX_DISK_EXPERIMENT",
        "source_model": source, "target_model": target,
        "status": ("PASS_FAKE_NONCE_REPLAY_FENCE_EXPECTATIONS"
                   if passed else "BLOCKED_FAKE_NONCE_FENCE_EXPECTATIONS"),
        "test_count": 4, "marker_created": first["fake_durable_marker_created"],
        "readback_consistent": not audit["issues"],
        "duplicate_blocked": replay["status"] == "BLOCKED_FAKE_NONCE_REPLAY",
        "changed_plan_replay_blocked": changed_plan["status"] == "BLOCKED_FAKE_NONCE_REPLAY",
        "temporary_folder_removed": True, "issues": [] if passed else [
            "FAKE_REPLAY_FENCE_EXPECTATIONS_FAILED"],
        "executed": False, "approval_accepted": False,
        "operating_journal_written": False, "operations_enabled": False,
        "durable_operating_nonce_verified": False,
        "resume_eligible": False, "automatic_recovery_authorized": False,
        "real_dgx_verified": False, "production_released": False,
    }
