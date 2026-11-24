"""P6-C CPU-only fsync/atomic-write experiment for a FAKE transaction journal.

NEVER opens service_journal.py's operating paths, NEVER calls Docker, and
NEVER treats a fixture lease as authorization. All writes are inside a fresh
0700 TemporaryDirectory with the unique blazux-p6-fake- prefix; the two
filename stems begin with 'fake-' and cannot be interpreted as service state.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile

from scripts.manager.mock_transaction_pipeline import (
    audit_mock_journal, mock_pipeline, mock_plan_id,
)
from scripts.manager.generic_operations import model_catalog

PREFIX = "blazux-p6-fake-"
LOG_NAME = "fake-events.jsonl"
STATE_NAME = "fake-state.json"
TICKET_TTL_NS = 60_000_000_000
MAX_BYTES = 256 * 1024
SCENARIOS = (
    "none", "target-api", "interrupted-snapshot", "expired-ticket",
    "duplicate-ticket", "tampered-snapshot", "unresolved-transition",
    "identity-drift",
)


def _sha(payload: object) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _ticket(source: str, target: str, src_id: str, dst_id: str,
            *, issued_at_ns: int = 1_000_000_000) -> dict:
    plan = mock_plan_id(source, target)
    data = {"scope": "FAKE_TICKET_NEVER_VALID_FOR_LIVE_EXECUTION",
            "plan_id": plan, "source_model": source, "target_model": target,
            "source_container_id": src_id, "target_container_id": dst_id,
            "issued_at_ns": issued_at_ns,
            "expires_at_ns": issued_at_ns + TICKET_TTL_NS}
    data["nonce"] = _sha(data)
    return data


def check_fake_ticket(ticket: dict, source: str, target: str,
                      src_id: str, dst_id: str, *, now_ns: int,
                      consumed: set[str]) -> list[str]:
    """Bounded mock clock guard, NO authentication and NO real operator consent."""
    issues = []
    if not isinstance(ticket, dict):
        return ["FAKE_TICKET_MISSING"]
    issue_value = ticket.get("issued_at_ns")
    safe_issue = (issue_value if isinstance(issue_value, int)
                  and not isinstance(issue_value, bool) and issue_value >= 0 else 0)
    expected = _ticket(source, target, src_id, dst_id,
                       issued_at_ns=safe_issue)
    if ticket != expected:
        issues.append("FAKE_TICKET_IDENTITY_OR_INTEGRITY_MISMATCH")
    issued = ticket.get("issued_at_ns")
    expiry = ticket.get("expires_at_ns")
    if (not isinstance(issued, int) or isinstance(issued, bool) or
            not isinstance(expiry, int) or isinstance(expiry, bool) or
            not isinstance(now_ns, int) or isinstance(now_ns, bool) or
            issued < 0 or expiry <= issued or
            expiry - issued > TICKET_TTL_NS or now_ns < issued or now_ns >= expiry):
        issues.append("FAKE_TICKET_EXPIRED_OR_INVALID")
    nonce = ticket.get("nonce")
    if not isinstance(nonce, str) or nonce in consumed:
        issues.append("FAKE_TICKET_REPLAY_OR_INVALID_NONCE")
    return issues


def _private_fixture_directory(folder: Path) -> None:
    """Deliberately refuse operating journal and arbitrary paths."""
    if (not isinstance(folder, Path) or not folder.is_absolute()
            or not folder.name.startswith(PREFIX)
            or folder.is_symlink() or not folder.is_dir()
            or folder.parent != Path(tempfile.gettempdir()).resolve()):
        raise ValueError("NOT_A_FRESH_FAKE_DGX_TEMP_DIRECTORY")
    if stat.S_IMODE(folder.stat().st_mode) != 0o700:
        raise ValueError("FAKE_DGX_TEMP_DIRECTORY_PERMISSIONS")


def _read_private(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("FAKE_JOURNAL_NOT_A_REGULAR_FILE")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    try:
        st = os.fstat(fd)
        if (not stat.S_ISREG(st.st_mode) or stat.S_IMODE(st.st_mode) != 0o600
                or st.st_size <= 0 or st.st_size > MAX_BYTES):
            raise ValueError("FAKE_JOURNAL_FILE_PERMISSIONS_OR_SIZE")
        return os.read(fd, MAX_BYTES + 1)
    finally:
        os.close(fd)


def audit_fake_store(folder: Path, source: str, target: str) -> dict:
    """Read-only log/snapshot audit. No repair, replay, or live-state promotion."""
    issues = []
    phase = None
    count = 0
    try:
        _private_fixture_directory(folder)
        log = folder / LOG_NAME
        state = folder / STATE_NAME
        if not log.exists() and not state.exists():
            issues.append("FAKE_JOURNAL_EMPTY")
        elif not log.exists() or not state.exists():
            issues.append("FAKE_JOURNAL_LOG_SNAPSHOT_MISMATCH")
        else:
            raw = _read_private(log)
            if not raw.endswith(b"\n"):
                issues.append("FAKE_JOURNAL_INCOMPLETE_LAST_RECORD")
            records = raw.splitlines()
            if not 1 <= len(records) <= 64:
                issues.append("FAKE_JOURNAL_EVENT_COUNT_INVALID")
            else:
                events = [json.loads(line) for line in records]
                count = len(events)
                last = json.loads(_read_private(state))
                if events[-1] != last:
                    issues.append("FAKE_JOURNAL_LAST_SNAPSHOT_MISMATCH")
                audit = audit_mock_journal(events, source, target)
                phase = audit["last_phase"]
                issues.extend(audit["issues"])
    except (ValueError, OSError, TypeError, KeyError, UnicodeDecodeError,
            json.JSONDecodeError) as exc:
        issues.append("FAKE_JOURNAL_UNTRUSTED:" + str(exc)[:100])
    return {
        "schema_version": 1, "stage": "p6", "action": "fake-store-audit",
        "scope": "TEST_TEMP_FILESYSTEM_CONTRACT_ONLY",
        "status": "VERIFIED_FAKE_FILES_ONLY" if not issues else "BLOCKED_FAKE_FILES",
        "issues": sorted(set(issues)), "event_count": count,
        "last_phase": phase,
        "executed": False, "real_dgx_verified": False,
        "production_released": False, "resume_eligible": False,
        "durable_operating_journal_verified": False,
    }


def write_fake_store(folder: Path, events: list[dict], *,
                     interrupt_after_log: bool = False) -> None:
    """One-shot log fsync, then atomic snapshot; interrupted state stays DIRTY."""
    _private_fixture_directory(folder)
    if not isinstance(events, list) or not 1 <= len(events) <= 64:
        raise ValueError("INVALID_FAKE_EVENTS")
    # O_EXCL is a process-local duplicate/overwrite barrier, not a cross-host
    # lease or crash-consistent authorization protocol.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    log = folder / LOG_NAME
    fd = os.open(log, flags, 0o600)
    with os.fdopen(fd, "wb") as stream:
        for ev in events:
            stream.write((json.dumps(ev, sort_keys=True) + "\n").encode())
        stream.flush()
        os.fsync(stream.fileno())
    if interrupt_after_log:
        return
    tmp = folder / ".fake-state-tmp"
    fd = os.open(tmp, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write((json.dumps(events[-1], sort_keys=True) + "\n").encode())
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, folder / STATE_NAME)
        dfd = os.open(folder, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(dfd)
        finally:
            os.close(dfd)
    finally:
        if tmp.exists():
            tmp.unlink()


def fake_disk_contract(source: str, target: str, *, scenario: str = "none") -> dict:
    """Execute deterministic fixture in an automatically cleaned temp directory."""
    if scenario not in SCENARIOS:
        raise ValueError("UNSUPPORTED_FAKE_DISK_SCENARIO")
    catalog = model_catalog()
    if source == target or source not in catalog["models"] or target not in catalog["models"]:
        raise ValueError("UNREGISTERED_OR_SAME_MODEL_PAIR")
    fault = "target-api" if scenario == "target-api" else (
        "source-stop" if scenario == "unresolved-transition" else "none")
    pipeline = mock_pipeline(source, target, fault=fault)
    src_id = pipeline["source_container_id"]
    dst_id = pipeline["target_container_id"]
    ticket = _ticket(source, target, src_id, dst_id)
    if scenario == "identity-drift":
        ticket["source_container_id"] = "e" * 64
    used: set[str] = set()
    now_ns = (ticket["expires_at_ns"] if scenario == "expired-ticket"
              else ticket["issued_at_ns"] + 1_000_000_000)
    preflight = check_fake_ticket(ticket, source, target, src_id, dst_id,
                                  now_ns=now_ns, consumed=used)
    duplicate_rejected = False
    with tempfile.TemporaryDirectory(prefix=PREFIX) as directory:
        folder = Path(directory)
        if not preflight:
            used.add(ticket["nonce"])
            write_fake_store(folder, pipeline["mock_journal"],
                             interrupt_after_log=scenario == "interrupted-snapshot")
            if scenario == "tampered-snapshot":
                state = folder / STATE_NAME
                corrupted = dict(pipeline["mock_journal"][-1])
                corrupted["synthetic_action"] = "tampered"
                state.write_text(json.dumps(corrupted) + "\n", encoding="utf-8")
                os.chmod(state, 0o600)
            if scenario == "duplicate-ticket":
                replay_issues = check_fake_ticket(
                    ticket, source, target, src_id, dst_id,
                    now_ns=now_ns, consumed=used)
                duplicate_rejected = "FAKE_TICKET_REPLAY_OR_INVALID_NONCE" in replay_issues
                preflight.extend(replay_issues)
                try:
                    write_fake_store(folder, pipeline["mock_journal"])
                except FileExistsError:
                    duplicate_rejected = duplicate_rejected and True
                else:
                    duplicate_rejected = False
        audit = audit_fake_store(folder, source, target)
    expected_ok = scenario in ("none", "target-api")
    expected_issue = {
        "interrupted-snapshot": "FAKE_JOURNAL_LOG_SNAPSHOT_MISMATCH",
        "unresolved-transition": "MOCK_JOURNAL_UNRESOLVED_TRANSITION",
        "tampered-snapshot": "FAKE_JOURNAL_LAST_SNAPSHOT_MISMATCH",
    }
    detected = (bool(preflight) if scenario in ("expired-ticket", "identity-drift")
                else duplicate_rejected if scenario == "duplicate-ticket"
                else expected_issue.get(scenario) in audit["issues"])
    ok = (audit["status"] == "VERIFIED_FAKE_FILES_ONLY"
          if expected_ok else bool(detected))
    return {
        "schema_version": 1, "stage": "p6", "action": "fake-disk-contract",
        "scope": "EPHEMERAL_PRIVATE_TEMP_DIRECTORY_ONLY",
        "scenario": scenario,
        "source_model": source, "target_model": target,
        "source_container_id": src_id, "target_container_id": dst_id,
        "status": ("PASS_FAKE_DISK_CONTRACT" if expected_ok and ok
                   else "PASS_FAKE_DISK_FAILURE_DETECTED" if ok
                   else "FAIL_FAKE_DISK_CONTRACT"),
        "ticket_issues": sorted(set(preflight)), "audit": audit,
        "temporary_folder_removed": True,
        "executed": False, "fake_executed": True,
        "approval_accepted": False, "operations_enabled": False,
        "real_dgx_verified": False, "production_released": False,
        "durable_operating_journal_verified": False,
        "note": "Temp-file fsync/atomic-write exercise only; no live approval, resume or service mutation.",
    }


def fake_disk_matrix() -> dict:
    names = sorted(model_catalog()["models"])
    cases = [fake_disk_contract(a, b, scenario=f)
             for a in names for b in names if a != b for f in SCENARIOS]
    passed = all(row["status"] in (
        "PASS_FAKE_DISK_CONTRACT", "PASS_FAKE_DISK_FAILURE_DETECTED")
        and not row["executed"] and not row["production_released"]
        for row in cases)
    return {
        "schema_version": 1, "stage": "p6",
        "action": "fake-disk-matrix", "scope": "EPHEMERAL_FAKE_DISK_MATRIX",
        "status": "PASS_FAKE_DGX_EXPECTED_OUTCOMES" if passed else "FAIL_FAKE_DGX",
        "models": names, "pair_count": len(names) * (len(names) - 1),
        "scenario_count": len(SCENARIOS), "test_count": len(cases),
        "status_counts": {status: sum(x["status"] == status for x in cases)
                          for status in sorted({x["status"] for x in cases})},
        "cases": cases, "executed": False, "fake_executed": True,
        "real_dgx_verified": False, "operations_enabled": False,
        "production_released": False,
    }
