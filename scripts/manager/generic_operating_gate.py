"""P6-D generic operating admission review. NO execution and NO approval issuance.

This is a model-agnostic gate *design* bound to pre-supplied observations and
legacy read-only operating audit results. A passing consistency review is
still BLOCKED until a separately qualified live executor / authenticated
scoped approval / production journal schema are implemented.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from scripts.manager.generic_operations import model_catalog

_SHA = re.compile(r"^[0-9a-f]{64}$")


def gate_review(source: str, target: str, service: dict | None,
                source_id: str | None, target_id: str | None,
                journal: dict | None, approval: dict | None,
                *, config: dict | None = None, now_utc: str | None = None) -> dict:
    catalog = model_catalog(config)
    names = catalog["models"]
    if source == target or source not in names or target not in names:
        raise ValueError("UNREGISTERED_OR_SAME_MODEL_PAIR")
    s = service if isinstance(service, dict) else {}
    j = journal if isinstance(journal, dict) else {}
    a = approval if isinstance(approval, dict) else {}
    issues = []
    if not (_SHA.fullmatch(source_id or "") and _SHA.fullmatch(target_id or "")
            and source_id != target_id):
        issues.append("SOURCE_TARGET_FULL_CONTAINER_IDS_UNVERIFIED")
    if (s.get("observed_model") != source
            or s.get("status") != "LIVE_SERVICE_VERIFIED"
            or s.get("runtime_role") != "CANONICAL"
            or s.get("p5_development_trial") is not False):
        issues.append("CANONICAL_SOURCE_LIVE_IDENTITY_UNQUALIFIED")
    if s.get("expected_served_id") != names[source]["served_id"]:
        issues.append("SOURCE_API_ID_MISMATCH")
    checks = s.get("checks")
    if not isinstance(checks, dict) or not checks or any(v is not True for v in checks.values()):
        issues.append("SOURCE_SERVICE_CHECKS_FAILED")
    if s.get("host_port") != 8000:
        issues.append("HOST_PORT_POLICY_MISMATCH")
    if s.get("gpu_exclusivity_verified") is not True:
        issues.append("GPU_EXCLUSIVITY_UNVERIFIED")
    if s.get("port_process_ownership_verified") is not True:
        issues.append("PORT_PID_OWNERSHIP_UNVERIFIED")
    if j.get("status") not in ("EMPTY", "VERIFIED"):
        issues.append("OPERATING_JOURNAL_UNRESOLVED_OR_UNTRUSTED")
    if j.get("issues"):
        issues.append("OPERATING_JOURNAL_AUDIT_ISSUES")
    # Old journal only has qualified "flash-next" and "27b" identities.
    # Even if a supplied status looks clean, Orcarouter is not compatible
    # with the existing on-disk operating journal schema.
    if source == "orcarouter" or target == "orcarouter":
        issues.append("LEGACY_JOURNAL_ORCAROUTER_SCHEMA_UNSUPPORTED")
    # An in-memory/mock nonce, fixture plan hash or user-authored approval
    # never satisfies a real scoped downtime approval.
    if (a.get("kind") != "INDEPENDENT_OPERATOR_DOWNTIME_APPROVAL"
            or a.get("scope") != "EXACT_MODEL_PAIR_AND_CONTAINER_IDS"
            or a.get("source_model") != source or a.get("target_model") != target
            or a.get("source_container_id") != source_id
            or a.get("target_container_id") != target_id
            or a.get("host_port") != 8000
            or not _SHA.fullmatch(str(a.get("plan_id") or ""))):
        issues.append("EXACT_SCOPED_APPROVAL_UNVERIFIED")
    expiration = a.get("expires_at_utc")
    now = now_utc
    try:
        if not isinstance(expiration, str) or not isinstance(now, str):
            raise ValueError("no independent clock evidence")
        expiry = datetime.fromisoformat(expiration.replace("Z", "+00:00"))
        clock = datetime.fromisoformat(now.replace("Z", "+00:00"))
        if expiry.tzinfo is None or clock.tzinfo is None or clock >= expiry:
            raise ValueError("expired or naive timestamp")
    except ValueError:
        issues.append("APPROVAL_EXPIRY_NOT_INDEPENDENTLY_VERIFIED")
    if a.get("nonce_unused_independently_verified") is not True:
        issues.append("DURABLE_REPLAY_FENCE_UNVERIFIED")
    # An untrusted JSON object cannot prove that the approval signature,
    # clock, Docker state or nonce were checked by an independent authority.
    structural = not issues
    return {
        "schema_version": 1, "stage": "p6", "action": "operating-gate-review",
        "scope": "UNTRUSTED_SOURCE_CONSISTENCY_ONLY",
        "status": "BLOCKED_LIVE_EXECUTOR_NOT_QUALIFIED",
        "source_model": source, "target_model": target,
        "source_container_id": source_id, "target_container_id": target_id,
        "api_port": 8000,
        "structural_fields_consistent": structural,
        "issues": sorted(set(issues + [
            "NO_INDEPENDENT_APPROVAL_AUTHENTICATION",
            "NO_QUALIFIED_GENERIC_OPERATING_EXECUTOR",
            "NO_DURABLE_GENERIC_NONCE_LEDGER",
            "NO_ATOMIC_LIVE_IDENTITY_AND_JOURNAL_FENCE",
        ])),
        "executed": False, "approval_accepted": False,
        "operations_enabled": False, "production_released": False,
        "resume_eligible": False, "real_dgx_verified": False,
        "note": "Source review is intentionally incapable of approving a real switch.",
    }
