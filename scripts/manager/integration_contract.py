"""P7 strict, source-only reconciliation of independently captured components.

Evidence documents are untrusted. Literal status: PASS strings and claimed
probe IDs are never sufficient for a live service/proxy/gateway/storage PASS.
"""
from __future__ import annotations

from datetime import datetime
import re

from scripts.manager.generic_operations import model_catalog

_SHA = re.compile(r"^[0-9a-f]{64}$")
_COMPONENTS = ("service", "proxy", "gateway", "storage")


def _timestamp(value):
    if not isinstance(value, str):
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if stamp.tzinfo is not None and stamp.utcoffset() is not None:
            return stamp
    except ValueError:
        pass
    return None


def integration_reconcile(model: str, evidence: dict | None,
                          *, config: dict | None = None) -> dict:
    catalog = model_catalog(config)
    if model not in catalog["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    expected = catalog["models"][model]
    data = evidence if isinstance(evidence, dict) else {}
    issues = []
    details = {}
    stamps = []

    if data.get("model") != model:
        issues.append("P7_ROOT_MODEL_UNBOUND")
    if data.get("active_gpu_models") != [model]:
        issues.append("ONE_ACTIVE_MODEL_NOT_INDEPENDENTLY_EVIDENCED")
    if data.get("api_port") != 8000:
        issues.append("FIXED_API_PORT_NOT_EVIDENCED")

    for component in _COMPONENTS:
        entry = data.get(component)
        reasons = []
        if not isinstance(entry, dict):
            entry = {}
        observed_at = _timestamp(entry.get("observed_at_utc"))
        if observed_at is None:
            reasons.append("OBSERVATION_TIME_MISSING")
        else:
            stamps.append(observed_at)
        probe_id = entry.get("probe_id")
        if not isinstance(probe_id, str) or not probe_id.strip():
            reasons.append("PROBE_ID_MISSING")
        if entry.get("model") != model:
            reasons.append("MODEL_MISMATCH")
        if entry.get("probe_mode") != "DIRECT_OBSERVATION":
            reasons.append("DIRECT_PROBE_NOT_EVIDENCED")
        if component == "service":
            if entry.get("container_name") != expected["container"]:
                reasons.append("CANONICAL_CONTAINER_MISMATCH")
            cid = entry.get("container_id")
            if not isinstance(cid, str) or not _SHA.fullmatch(cid):
                reasons.append("CONTAINER_ID_MISSING")
            if entry.get("served_id") != expected["served_id"]:
                reasons.append("SERVED_ID_MISMATCH")
            if entry.get("port") != 8000 or entry.get("http_status") != 200:
                reasons.append("DIRECT_API_HEALTH_MISSING")
        elif component in ("proxy", "gateway"):
            if entry.get("observed_served_id") != expected["served_id"]:
                reasons.append("UPSTREAM_MODEL_MISMATCH")
            if entry.get("upstream_port") != 8000 or entry.get("http_status") != 200:
                reasons.append("UPSTREAM_PROBE_MISSING")
        else:
            if entry.get("checkpoint") != expected["checkpoint"]:
                reasons.append("CHECKPOINT_NOT_VERIFIED")
            if entry.get("recipe_path") != expected["recipe_path"]:
                reasons.append("RECIPE_NOT_VERIFIED")
            if entry.get("assets_verified") is not True:
                reasons.append("STORAGE_ASSETS_NOT_VERIFIED")
        details[component] = {
            "status": "SOURCE_FIELDS_CONSISTENT" if not reasons else "NOT_OBSERVED",
            "issues": reasons}
        issues.extend(component.upper() + "_" + reason for reason in reasons)

    if len(stamps) == len(_COMPONENTS):
        spread = (max(stamps) - min(stamps)).total_seconds()
        if spread > 120:
            issues.append("COMPONENT_OBSERVATION_WINDOW_EXCEEDS_120_SECONDS")
    # All observations could have been authored in a JSON file rather than
    # captured from the actual services. No authenticated provenance exists.
    return {
        "schema_version": 1, "stage": "p7", "action": "integration-reconcile",
        "scope": "UNTRUSTED_OBSERVATION_DOCUMENT_CONSISTENCY_ONLY",
        "model": model, "api_port": 8000,
        "status": ("SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED"
                   if not issues else "BLOCKED"),
        "component_checks": details,
        "issues": sorted(set(issues)),
        "executed": False, "real_dgx_verified": False,
        "proxy_gateway_verified": False, "operations_enabled": False,
        "production_released": False,
        "note": "Live component state and source provenance require independent read-only probes.",
    }
