"""Strict read-only integrity audit for the independent operating journal.

Never trust the last snapshot alone: service_journal appends a durable event
before replacing the current snapshot. SIGKILL or disk errors may leave those
two representations inconsistent. An unresolved/dirty event sequence BLOCKS a
new operating switch; only separately reviewed manual recovery can resolve it.
This never changes Docker, API, journal, or model assets.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.manager.service_journal import MODELS, PHASES, SHA256

MAX_JOURNAL_BYTES = 4 * 1024 * 1024
MAX_EVENT_BYTES = 16 * 1024


def _restricted_file(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError("UNTRUSTED_FILE_TYPE")
    st = path.stat()
    if st.st_mode & 0o077 or st.st_size > MAX_JOURNAL_BYTES:
        raise ValueError("UNTRUSTED_FILE_PERMISSIONS_OR_SIZE")
    return path.read_bytes()


def inspect_journal(root: Path) -> dict[str, Any]:
    """Verify append-only event chain AND snapshot byte-level logical state.

    No file or journal means no operating transition has yet occurred.
    A sole event log, sole snapshot, interrupted write, modified hash chain,
    incomplete transaction, or COMMITTED event without a terminal receipt
    blocks fresh switching. A failure must never be auto-marked reconciled.
    """
    folder = root / "journal"
    journal = folder / "service-events.jsonl"
    snapshot = folder / "service-state.json"
    if folder.is_symlink():
        return {"status": "BLOCKED", "phase": None,
                "issues": ["OPERATING_JOURNAL_DIRECTORY_SYMLINK"]}
    if not journal.exists() and not snapshot.exists():
        return {"status": "EMPTY", "phase": None, "issues": [],
                "event_count": 0}
    if not journal.exists() or not snapshot.exists():
        return {"status": "BLOCKED", "phase": None,
                "issues": ["OPERATING_JOURNAL_SNAPSHOT_LOG_MISMATCH"]}
    try:
        raw = _restricted_file(journal)
        records = raw.splitlines()
        if not raw or not raw.endswith(b"\n") or len(records) > 2048:
            raise ValueError("JOURNAL_INCOMPLETE_OR_TOO_LARGE")
        previous = None
        for entry in records:
            if not entry or len(entry) > MAX_EVENT_BYTES:
                raise ValueError("INVALID_JOURNAL_RECORD")
            event = json.loads(entry)
            if not isinstance(event, dict):
                raise ValueError("INVALID_EVENT_TYPE")
            claimed = event.get("event_hash")
            body = {k: v for k, v in event.items() if k != "event_hash"}
            digest = hashlib.sha256(
                json.dumps(body, sort_keys=True,
                           separators=(",", ":")).encode()).hexdigest()
            if not isinstance(claimed, str) or claimed != digest:
                raise ValueError("BROKEN_JOURNAL_EVENT_HASH")
            if event.get("previous_hash") != (previous["event_hash"] if previous else None):
                raise ValueError("BROKEN_JOURNAL_CHAIN")
            phase = event.get("phase")
            if phase not in PHASES.get(previous["phase"] if previous else None, set()):
                raise ValueError("INVALID_JOURNAL_STATE_TRANSITION")
            if (event.get("api_host_port") != 8000
                    or event.get("max_active_gpu_models") != 1
                    or event.get("schema_version") != 1
                    or event.get("live_state_revalidation_required") is not True
                    or not SHA256.fullmatch(str(event.get("plan_id") or ""))):
                raise ValueError("INVALID_JOURNAL_POLICY_OR_PLAN")
            if any(v is not None and v not in MODELS for v in (
                    event.get("from_model"), event.get("to_model"),
                    event.get("observed_model"))):
                raise ValueError("UNSUPPORTED_JOURNAL_MODEL")
            previous = event
        actual = json.loads(_restricted_file(snapshot))
        if not isinstance(actual, dict) or actual != previous:
            raise ValueError("JOURNAL_SNAPSHOT_LAST_EVENT_MISMATCH")
        phase = previous["phase"]
        if phase not in ("COMMITTED", "RESTORED", "CANCELLED"):
            return {"status": "BLOCKED", "phase": phase,
                    "event_count": len(records),
                    "issues": ["UNRESOLVED_OPERATING_SWITCH_JOURNAL"]}
        if phase == "COMMITTED":
            receipt_path = root / ("completed-" + previous["plan_id"] + ".json")
            if receipt_path.is_symlink() or not receipt_path.exists():
                return {"status": "BLOCKED", "phase": phase,
                        "event_count": len(records),
                        "issues": ["COMMITTED_OPERATING_RECEIPT_MISSING"]}
            receipt = json.loads(_restricted_file(receipt_path))
            if (not isinstance(receipt, dict)
                    or receipt.get("status") != "PASS"
                    or receipt.get("executed") is not True
                    or receipt.get("live_verified") is not True
                    or receipt.get("plan_id") != previous["plan_id"]
                    or receipt.get("source_model") != previous["from_model"]
                    or receipt.get("target_model") != previous["to_model"]):
                raise ValueError("COMMITTED_RECEIPT_MISMATCH")
        return {"status": "VERIFIED", "phase": phase,
                "event_count": len(records), "issues": [],
                "last_event_hash": previous["event_hash"]}
    except (OSError, ValueError, TypeError, KeyError,
            UnicodeError, json.JSONDecodeError) as exc:
        return {"status": "BLOCKED", "phase": None,
                "issues": ["OPERATING_JOURNAL_UNTRUSTED:" + str(exc)[:96]]}


def main(argv: list[str] | None = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="Read-only operating switch journal audit")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    from scripts.manager.operational_switch import ROOT
    result = inspect_journal(ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Operating journal: " + result["status"]
              + " / last phase: " + str(result["phase"]))
        for issue in result.get("issues", []):
            print("  " + issue)
        print("This audit is READ ONLY. It never attempts a model restart.")
    return 0 if result["status"] in ("EMPTY", "VERIFIED") else 3


if __name__ == "__main__":
    raise SystemExit(main())
