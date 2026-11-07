"""Unified, manifest-led, read-only live service status for the Blazux Wizard.

Desired policy/manifest is NOT runtime truth. Combine fresh Docker/socket
observation with bounded localhost /health and /v1/models, checking the
observed service against its declared model identity. A past trial journal
cannot substitute for current health or prove rollback provenance.
"""
from __future__ import annotations

from typing import Any, Callable

from scripts.manager.service_manifest import inspect_service, policy
from scripts.manager.service_health import inspect_api_health


def inspect_live_status(
    *, manifest_inspector: Callable[[], dict[str, Any]] = inspect_service,
    health_inspector: Callable[..., dict[str, Any]] = inspect_api_health,
) -> dict[str, Any]:
    try:
        manifest = manifest_inspector()
    except (OSError, RuntimeError, ValueError) as exc:
        manifest = {
            "status": "BLOCKED", "observed_model": None,
            "issues": ["MANIFEST_OBSERVATION_FAILED:" + type(exc).__name__],
            "managed_containers": [], "api_port_8000_listening": False,
        }
    observed = manifest.get("observed_model")
    candidates = manifest.get("managed_containers")
    candidates = candidates if isinstance(candidates, list) else []
    running = [entry for entry in candidates if isinstance(entry, dict)
               and str(entry.get("status", "")).startswith("Up")]
    selected = [entry for entry in running if entry.get("model") == observed]
    active = selected[0] if len(selected) == 1 else None
    policies = policy()
    model_info = policies.get("models", {}).get(observed or "", {})
    expected_id = model_info.get("served_id")
    expected_container = model_info.get("container_name")

    checks = {
        "manifest_live_observation_valid": manifest.get("status") == "OBSERVED_UNQUALIFIED",
        "single_managed_model_running": len(running) == 1 and len(selected) == 1,
        "active_container_matches_manifest": (
            active is not None and active.get("container_name") == expected_container),
        "api_port_8000_listening": manifest.get("api_port_8000_listening") is True,
        "active_container_port_8000_published": (
            active is not None
            and isinstance(active.get("ports"), str)
            and ":8000->8000/tcp" in active["ports"]),
        "expected_served_id_defined": isinstance(expected_id, str) and bool(expected_id),
    }

    # Reuse the same observation for the HTTP health probe, avoiding a second
    # independently changing Docker snapshot. Its fail-closed behavior means
    # incomplete inventory never performs HTTP requests.
    try:
        health = health_inspector(service=manifest)
    except (OSError, RuntimeError, ValueError) as exc:
        health = {"status": "BLOCKED", "health_http_ok": False,
                  "api_identity_verified": False, "model_ids": [],
                  "issues": ["API_HEALTH_OBSERVATION_FAILED:" + type(exc).__name__]}
    model_ids = health.get("model_ids")
    model_ids = model_ids if isinstance(model_ids, list) else []
    checks["api_http_health_ok"] = health.get("health_http_ok") is True
    checks["api_model_identity_matches_manifest"] = (
        health.get("status") == "API_IDENTITY_CONFIRMED"
        and health.get("api_identity_verified") is True
        and health.get("expected_model_id") == expected_id
        and expected_id in model_ids
        and health.get("observed_model") == observed)

    issues = set(manifest.get("issues") or [])
    issues.update(health.get("issues") or [])
    issues.update(k.upper() + "_FAILED" for k, value in checks.items() if not value)
    ok = not issues
    return {
        "schema_version": 1, "stage": "svc", "action": "status",
        "scope": "DGX_READ_ONLY_MANIFEST_AND_API",
        "status": "LIVE_SERVICE_VERIFIED" if ok else "BLOCKED",
        "observed_model": observed, "expected_served_id": expected_id,
        "active_container": (
            {"name": active.get("container_name"),
             "image_id": active.get("image_id"),
             "status": active.get("status"),
             "ports": active.get("ports")} if active is not None else None),
        "host_port": 8000, "observed_model_ids": model_ids,
        "checks": checks, "issues": sorted(issues),
        "manifest_status": manifest.get("status"),
        "api_health_status": health.get("status"),
        "executed": False, "operations_enabled": False,
        "gpu_exclusivity_verified": False,
        "port_process_ownership_verified": False,
        "previous_trial_provenance_verified": False,
        "notice": (
            "Fresh manifest-led Docker and API identity check; not GPU process "
            "exclusivity, performance qualification, or proof of a past trial's "
            "rollback history. No Docker or API mutation.")
    }
