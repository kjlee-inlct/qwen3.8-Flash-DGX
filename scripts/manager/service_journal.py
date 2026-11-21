"""Append-only local service transition journal and atomic state snapshot.

This is a storage primitive for the *future approved service executor*, not an
execution backend. Never infer that a recorded state reflects live Docker or
GPU reality. Each transition must re-observe the host before acting.
"""
from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
from uuid import uuid4

PHASES = {
    None: {"OBSERVED"},
    "OBSERVED": {"OBSERVED", "PLANNED"},
    "PLANNED": {"OBSERVED", "OLD_STOPPING", "CANCELLED"},
    "OLD_STOPPING": {"OLD_STOPPED", "FAILED"},
    "OLD_STOPPED": {"NEW_STARTING", "ROLLBACK_STARTING"},
    "NEW_STARTING": {"NEW_VERIFYING", "ROLLBACK_STARTING"},
    "NEW_VERIFYING": {"COMMITTED", "ROLLBACK_STARTING"},
    "ROLLBACK_STARTING": {"RESTORED", "RECOVERY_FAILED"},
    "COMMITTED": {"OBSERVED"},
    "RESTORED": {"OBSERVED"},
    "CANCELLED": {"OBSERVED"},
    "FAILED": {"OBSERVED", "ROLLBACK_STARTING"},
    "RECOVERY_FAILED": {"OBSERVED"},
}
MODELS = frozenset(("flash-next", "27b"))
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def read_snapshot(directory: Path) -> dict | None:
    file = directory / "service-state.json"
    if not file.exists():
        return None
    data = json.loads(file.read_text(encoding="utf-8"))
    if (not isinstance(data, dict) or data.get("phase") not in PHASES
            or not isinstance(data.get("event_hash"), str)
            or not SHA256.fullmatch(data["event_hash"])):
        raise ValueError("invalid existing service snapshot")
    return data


def append_transition(directory: Path, *, phase: str,
                      from_model: str | None, to_model: str | None,
                      observed_model: str | None,
                      expected_previous_hash: str | None,
                      plan_id: str | None = None) -> dict:
    if phase not in PHASES:
        raise ValueError("unsupported transition phase")
    if any(m is not None and m not in MODELS
           for m in (from_model, to_model, observed_model)):
        raise ValueError("unsupported managed model")
    if plan_id is not None and not SHA256.fullmatch(plan_id):
        raise ValueError("invalid plan ID")
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (directory / "service.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        prior = read_snapshot(directory)
        prior_hash = prior["event_hash"] if prior else None
        if prior_hash != expected_previous_hash:
            raise RuntimeError("stale service manifest generation")
        old_phase = prior["phase"] if prior else None
        if phase not in PHASES[old_phase]:
            raise ValueError("invalid service state transition")
        event = {
            "schema_version": 1, "phase": phase, "from_model": from_model,
            "to_model": to_model, "observed_model": observed_model,
            "plan_id": plan_id, "previous_hash": prior_hash,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "event_id": uuid4().hex,
            "api_host_port": 8000, "max_active_gpu_models": 1,
            "live_state_revalidation_required": True,
        }
        encoded = json.dumps(event, sort_keys=True, separators=(",", ":"))
        event["event_hash"] = hashlib.sha256(encoded.encode()).hexdigest()
        # Journal before current-state update: an interrupted operation must
        # be reconciled against actual Docker/API state, not blindly resumed.
        journal = directory / "service-events.jsonl"
        fd = os.open(journal, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        with os.fdopen(fd, "a", encoding="utf-8") as output:
            output.write(json.dumps(event, sort_keys=True) + "\n")
            output.flush()
            os.fsync(output.fileno())
        target = directory / "service-state.json"
        temporary = directory / (".service-state-" + uuid4().hex)
        try:
            fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                json.dump(event, output, sort_keys=True, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
        return event
