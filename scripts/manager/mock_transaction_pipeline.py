"""P6 source-only executor-to-journal bridge with an exact Fake-DGX backend.

This module DOES NOT write the service operating journal or provide a Docker
executor.  It consumes transition_safety's in-memory step trace and produces a
hash-linked, replay-auditable mock event sequence.  Real durable fsync,
approval fencing, lock ownership, host state and recovery remain unqualified.
"""
from __future__ import annotations

import hashlib
import json
import re

from scripts.manager.generic_operations import model_catalog
from scripts.manager.transition_safety import simulate_transaction, FAULTS

_SHA = re.compile(r"^[0-9a-f]{64}$")
_NEXT = {
    None: {"OBSERVED"},
    "OBSERVED": {"PLANNED"},
    "PLANNED": {"OLD_STOPPING", "CANCELLED"},
    "OLD_STOPPING": {"OLD_STOPPED", "FAILED"},
    "OLD_STOPPED": {"NEW_STARTING", "FAILED"},
    "NEW_STARTING": {"NEW_VERIFYING", "ROLLBACK_STARTING"},
    "NEW_VERIFYING": {"COMMITTED", "ROLLBACK_STARTING"},
    "ROLLBACK_STARTING": {"RESTORED", "RECOVERY_FAILED"},
}
_TERMINAL = {"COMMITTED", "RESTORED", "CANCELLED"}


def _hash(payload: dict | list) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def mock_plan_id(source: str, target: str, *, config: dict | None = None) -> str:
    """Deterministic MOCK correlator, intentionally not an executable approval."""
    catalog = model_catalog(config)
    names = catalog["models"]
    if source == target or source not in names or target not in names:
        raise ValueError("UNREGISTERED_OR_SAME_MODEL_PAIR")
    return _hash({"kind": "NON_AUTHORIZING_FAKE_DGX_PLAN",
                  "source": source, "target": target,
                  "source_checkpoint": names[source]["checkpoint"],
                  "target_checkpoint": names[target]["checkpoint"],
                  "source_served_id": names[source]["served_id"],
                  "target_served_id": names[target]["served_id"],
                  "api_port": 8000})


def _chain(trace: list[dict], source: str, target: str, plan_id: str) -> list[dict]:
    result = []
    previous = None
    for index, record in enumerate(trace):
        event = {
            "schema_version": 1, "index": index,
            "phase": record["phase"],
            "synthetic_action": record["action"],
            "source_model": source, "target_model": target,
            "plan_id": plan_id,
            "active_models": record["active_models"],
            "port_8000_owner": record["port_8000_owner"],
            "docker_id": record["docker_id"],
            "host_port": 8000, "max_active_gpu_models": 1,
            "record_origin": "IN_MEMORY_ONLY_NEVER_FSYNCED",
            "previous_hash": previous,
        }
        event["event_hash"] = _hash(event)
        result.append(event)
        previous = event["event_hash"]
    return result


def audit_mock_journal(events: object, source: str, target: str, *,
                       config: dict | None = None) -> dict:
    """Verify synthetic hash chain and phase/identity/port invariants.

    Even a valid chain is merely user-authored bytes; no authenticated
    provenance, live runtime authority, durable commit or resume permission.
    """
    expected_plan = mock_plan_id(source, target, config=config)
    issues = []
    prior_hash = None
    prior_phase = None
    previous_docker = None
    if not isinstance(events, list) or not (1 <= len(events) <= 64):
        issues.append("MISSING_OR_UNBOUNDED_MOCK_JOURNAL")
        events = []
    for index, event in enumerate(events):
        if not isinstance(event, dict):
            issues.append("INVALID_EVENT_TYPE")
            break
        if set(event) != {
            "schema_version", "index", "phase", "synthetic_action",
            "source_model", "target_model", "plan_id", "active_models",
            "port_8000_owner", "docker_id", "host_port",
            "max_active_gpu_models", "record_origin", "previous_hash",
            "event_hash",
        }:
            issues.append("EVENT_SCHEMA_MISMATCH")
            break
        digest = event.get("event_hash")
        if not isinstance(digest, str) or not _SHA.fullmatch(digest) or (
                _hash({k: v for k, v in event.items() if k != "event_hash"}) != digest):
            issues.append("MOCK_JOURNAL_HASH_MISMATCH")
        if event.get("previous_hash") != prior_hash or event.get("index") != index:
            issues.append("MOCK_JOURNAL_CHAIN_OR_INDEX_MISMATCH")
        phase = event.get("phase")
        if phase not in _NEXT.get(prior_phase, set()):
            issues.append("MOCK_JOURNAL_ILLEGAL_PHASE_TRANSITION")
        if (event.get("source_model") != source or
                event.get("target_model") != target or
                event.get("plan_id") != expected_plan or
                event.get("host_port") != 8000 or
                event.get("max_active_gpu_models") != 1 or
                event.get("record_origin") != "IN_MEMORY_ONLY_NEVER_FSYNCED" or
                event.get("schema_version") != 1):
            issues.append("MOCK_JOURNAL_POLICY_OR_IDENTITY_DRIFT")
        active = event.get("active_models")
        owner = event.get("port_8000_owner")
        if (not isinstance(active, list) or len(active) > 1 or
                any(m not in (source, target) for m in active) or
                owner not in (None, source, target) or
                (owner is not None and active != [owner])):
            issues.append("ONE_MODEL_OR_PORT_OWNER_INVARIANT_VIOLATION")
        docker = event.get("docker_id")
        if not isinstance(docker, str) or not _SHA.fullmatch(docker):
            issues.append("MOCK_DOCKER_ID_INVALID")
        if previous_docker is not None and docker != previous_docker:
            issues.append("MOCK_DOCKER_ID_DRIFT")
        previous_docker = docker
        prior_hash = digest
        prior_phase = phase
    if events and prior_phase not in _TERMINAL:
        issues.append("MOCK_JOURNAL_UNRESOLVED_TRANSITION")
    return {
        "schema_version": 1, "stage": "p6", "action": "mock-journal-audit",
        "scope": "UNTRUSTED_IN_MEMORY_CHAIN_CONSISTENCY_ONLY",
        "status": ("VERIFIED_MOCK_TERMINAL" if not issues else "BLOCKED_MOCK_JOURNAL"),
        "source_model": source, "target_model": target,
        "event_count": len(events), "last_phase": prior_phase,
        "last_event_hash": prior_hash, "issues": sorted(set(issues)),
        "executed": False, "real_dgx_verified": False,
        "approval_accepted": False, "operations_enabled": False,
        "production_released": False, "resume_eligible": False,
    }


def mock_pipeline(source: str, target: str, *, fault: str = "none",
                  config: dict | None = None) -> dict:
    """Connect existing exact in-memory step executor to a mock journal."""
    if fault not in FAULTS:
        raise ValueError("UNSUPPORTED_EXTENDED_FAULT")
    plan_id = mock_plan_id(source, target, config=config)
    transition = simulate_transaction(source, target, fault=fault, config=config)
    journal = _chain(transition["journal"], source, target, plan_id)
    audit = audit_mock_journal(journal, source, target, config=config)
    safe_terminal = transition["status"] in (
        "PASS_FAKE_SWITCH", "PASS_FAKE_RECOVERY", "BLOCKED_FAKE_BEFORE_STOP")
    if (safe_terminal and not audit["issues"] and not transition["invariant_issues"]
            and not transition["executed"]):
        report_status = "PASS_FAKE_PIPELINE_CONTRACT"
    elif safe_terminal:
        report_status = "BLOCKED_FAKE_PIPELINE_CONTRACT"
    else:
        report_status = "EXPECTED_UNSAFE_FAKE_TERMINAL"
    return {
        "schema_version": 1, "stage": "p6", "action": "pipeline-mock",
        "scope": "IN_MEMORY_EXECUTOR_AND_HASH_JOURNAL_ONLY",
        "status": report_status, "transition_status": transition["status"],
        "expected_transition_status": transition["expected_status"],
        "source_model": source, "target_model": target,
        "injected_fault": fault, "non_authorizing_plan_id": plan_id,
        "mock_journal": journal, "journal_audit": audit,
        "synthetic_mutations": transition["synthetic_mutations"],
        "invariant_issues": transition["invariant_issues"],
        "final_active_model": transition["final_active_model"],
        "final_port_owner": transition["final_port_owner"],
        "executed": False, "fake_executed": True, "approval_accepted": False,
        "real_dgx_verified": False, "operations_enabled": False,
        "production_released": False,
        "durable_journal_verified": False, "live_executor_available": False,
        "note": "No Docker executor, lock, disk fsync, live permission, or recovery.",
    }
