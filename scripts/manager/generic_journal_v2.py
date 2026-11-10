"""P6-E versioned generic journal schema proposal and READ-ONLY migration preview.

Never reads/writes the actual operating journal. The historic V1
service_journal.py / operational_audit.py remain untouched and limited to two
models. A proposed v2 hash is not a durable, authenticated event or approval.
"""
from __future__ import annotations

import hashlib
import json
import re

from scripts.manager.generic_operations import model_catalog
from scripts.manager.service_journal import PHASES

_ID = re.compile(r"^[0-9a-f]{64}$")
PHASE_LABELS = tuple(sorted(x for x in PHASES if x is not None))
REQUIRED_V2 = frozenset((
    "schema_version", "record_origin", "phase", "source_model",
    "target_model", "source_container_id", "target_container_id",
    "source_role", "target_role", "plan_id", "event_index",
    "legacy_v1_anchor_hash", "previous_hash", "api_host_port",
    "max_active_gpu_models", "live_revalidation_required",
    "approval_authentication_required", "nonce_ledger_required", "event_hash",
))
V2_ORIGIN = "UNTRUSTED_V2_IN_MEMORY_PROPOSAL_ONLY"


def _digest(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                                     separators=(",", ":")).encode()).hexdigest()


def _models(source: str, target: str) -> dict:
    names = model_catalog()["models"]
    if source == target or source not in names or target not in names:
        raise ValueError("UNREGISTERED_OR_SAME_MODEL_PAIR")
    return names


def draft_v2_event(source: str, target: str, *,
                   source_id: str, target_id: str, plan_id: str,
                   legacy_anchor: str | None = None,
                   prior: dict | None = None,
                   phase: str = "OBSERVED") -> dict:
    """Emit a synthetic v2 event for schema testing. Never persist it."""
    _models(source, target)
    if (not all(isinstance(x, str) and _ID.fullmatch(x)
                for x in (source_id, target_id, plan_id))
            or source_id == target_id
            or (legacy_anchor is not None and
                (not isinstance(legacy_anchor, str) or not _ID.fullmatch(legacy_anchor)))):
        raise ValueError("V2_PROPOSED_IDENTITY_OR_PLAN_INVALID")
    if phase not in PHASE_LABELS:
        raise ValueError("V2_PHASE_UNREGISTERED")
    previous_phase = prior.get("phase") if isinstance(prior, dict) else None
    if phase not in PHASES.get(previous_phase, set()):
        raise ValueError("V2_DRAFT_ILLEGAL_PHASE_TRANSITION")
    if prior is not None and (prior.get("schema_version") != 2
                              or prior.get("source_model") != source
                              or prior.get("target_model") != target
                              or prior.get("source_container_id") != source_id
                              or prior.get("target_container_id") != target_id
                              or prior.get("plan_id") != plan_id
                              or prior.get("legacy_v1_anchor_hash") != legacy_anchor):
        raise ValueError("V2_DRAFT_PREVIOUS_EVENT_DRIFT")
    body = {
        "schema_version": 2,
        "record_origin": V2_ORIGIN,
        "phase": phase, "source_model": source, "target_model": target,
        "source_container_id": source_id, "target_container_id": target_id,
        # NO silent promotion of an Orcarouter development trial.
        "source_role": "CANONICAL_REQUIRED",
        "target_role": "CANONICAL_REQUIRED",
        "plan_id": plan_id,
        "event_index": 0 if prior is None else prior["event_index"] + 1,
        "legacy_v1_anchor_hash": legacy_anchor,
        "previous_hash": None if prior is None else prior["event_hash"],
        "api_host_port": 8000, "max_active_gpu_models": 1,
        "live_revalidation_required": True,
        "approval_authentication_required": True,
        "nonce_ledger_required": True,
    }
    body["event_hash"] = _digest(body)
    return body


def audit_v2_draft(events: object) -> dict:
    """Hash/schema/phase consistency on untrusted synthetic bytes ONLY."""
    issues = []
    if not isinstance(events, list) or not 1 <= len(events) <= 64:
        issues.append("V2_EVENT_LIST_MISSING_OR_UNBOUNDED")
        events = []
    previous = None
    for index, event in enumerate(events):
        if not isinstance(event, dict) or frozenset(event) != REQUIRED_V2:
            issues.append("V2_EVENT_SCHEMA_INVALID")
            break
        body = {k: v for k, v in event.items() if k != "event_hash"}
        if event["event_hash"] != _digest(body):
            issues.append("V2_EVENT_HASH_MISMATCH")
        if event["record_origin"] != V2_ORIGIN or event["schema_version"] != 2:
            issues.append("V2_PROPOSAL_ORIGIN_MISMATCH")
        if (event["event_index"] != index or
                event["previous_hash"] != (previous["event_hash"] if previous else None)):
            issues.append("V2_EVENT_SEQUENCE_MISMATCH")
        if event["phase"] not in PHASES.get(previous["phase"] if previous else None, set()):
            issues.append("V2_PHASE_ILLEGAL")
        if (event["api_host_port"] != 8000 or event["max_active_gpu_models"] != 1
                or event["live_revalidation_required"] is not True
                or event["approval_authentication_required"] is not True
                or event["nonce_ledger_required"] is not True):
            issues.append("V2_POLICY_CONTRACT_MISMATCH")
        src, dst = event["source_model"], event["target_model"]
        try:
            _models(src, dst)
        except ValueError:
            issues.append("V2_UNREGISTERED_PAIR")
        a, b = event["source_container_id"], event["target_container_id"]
        if (not isinstance(a, str) or not _ID.fullmatch(a)
                or not isinstance(b, str) or not _ID.fullmatch(b) or a == b
                or not isinstance(event["plan_id"], str)
                or not _ID.fullmatch(event["plan_id"])):
            issues.append("V2_IDS_OR_PLAN_INVALID")
        if (event["source_role"] != "CANONICAL_REQUIRED"
                or event["target_role"] != "CANONICAL_REQUIRED"):
            issues.append("V2_RUNTIME_ROLE_DRIFT")
        anchor = event["legacy_v1_anchor_hash"]
        if anchor is not None and (not isinstance(anchor, str) or not _ID.fullmatch(anchor)):
            issues.append("V2_LEGACY_ANCHOR_INVALID")
        if previous is not None and any(event[k] != previous[k] for k in (
                "source_model", "target_model", "source_container_id",
                "target_container_id", "plan_id", "legacy_v1_anchor_hash")):
            issues.append("V2_JOURNAL_IDENTITY_DRIFT")
        previous = event
    return {
        "schema_version": 2, "stage": "p6", "action": "journal-v2-draft-audit",
        "scope": "IN_MEMORY_SCHEMA_CONSISTENCY_NOT_PRODUCTION_JOURNAL",
        "status": "PASS_V2_DRAFT_CONSISTENCY" if not issues else "BLOCKED_V2_DRAFT",
        "event_count": len(events), "issues": sorted(set(issues)),
        "durable": False, "executed": False, "approval_accepted": False,
        "production_released": False, "resume_eligible": False,
        "live_executor_available": False,
    }


def migration_preview(source: str, target: str, audit: dict | None) -> dict:
    """Accept external read-only V1 audit summary, never migrate any file."""
    models = _models(source, target)
    v1 = audit if isinstance(audit, dict) else {}
    state = v1.get("status")
    issues = []
    if state == "EMPTY" and v1.get("event_count") == 0 and v1.get("issues") == []:
        mode = "REQUIRES_APPROVED_EMPTY_V2_BOOTSTRAP"
        anchor = None
    elif (state == "VERIFIED" and v1.get("phase") in ("COMMITTED","RESTORED","CANCELLED")
          and isinstance(v1.get("last_event_hash"), str)
          and _ID.fullmatch(v1["last_event_hash"]) and v1.get("issues") == []
          and isinstance(v1.get("event_count"), int)
          and v1["event_count"] > 0):
        mode = "REQUIRES_APPROVED_V1_ANCHOR_AND_READ_ONLY_RECONCILIATION"
        anchor = v1["last_event_hash"]
    else:
        mode = "FREEZE_UNTRUSTED_OR_UNRESOLVED_V1"
        anchor = None
        issues.append("V1_AUDIT_NOT_CLEANLY_ANCHORED")
    if source == "orcarouter" or target == "orcarouter":
        issues.append("V1_JOURNAL_MODEL_SCOPE_EXCLUDES_ORCAROUTER")
    if models[source]["served_id"] is None or models[target]["served_id"] is None:
        issues.append("CANONICAL_API_MODEL_ID_UNQUALIFIED")
    return {
        "schema_version": 2, "stage": "p6", "action": "journal-v2-preview",
        "scope": "READ_ONLY_SCHEMA_MIGRATION_PLAN_NOT_EXECUTOR",
        "status": "BLOCKED_V2_MIGRATION_NOT_AUTHORIZED",
        "source_model": source, "target_model": target,
        "mode": mode, "legacy_anchor_hash": anchor,
        "v2_required_fields": sorted(REQUIRED_V2),
        "v2_phase_graph": {str(key): sorted(values)
                           for key, values in PHASES.items()},
        "issues": sorted(set(issues + [
            "V2_DURABLE_MIGRATION_NOT_IMPLEMENTED",
            "V2_JOURNAL_REPLAY_AND_RECEIPT_FENCE_NOT_IMPLEMENTED",
            "INDEPENDENT_OPERATOR_APPROVAL_REQUIRED",
            "ATOMIC_LIVE_DOCKER_AND_PORT_OWNERSHIP_VERIFICATION_REQUIRED",
        ])),
        "v1_journal_modified": False, "v2_journal_written": False,
        "executed": False, "approval_accepted": False,
        "production_released": False, "resume_eligible": False,
    }
