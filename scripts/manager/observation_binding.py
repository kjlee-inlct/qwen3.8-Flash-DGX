"""P5-C read-only, model-bound reconciliation of existing service/resource observations.

Capture mode invokes ONLY the existing read-only status and diagnostics probes.
It never sends an inference request, changes the host, or claims GPU/port-process
ownership. Review mode accepts untrusted JSON and cannot authenticate provenance.
"""
from __future__ import annotations

import re
from typing import Callable

from scripts.manager.generic_operations import model_catalog

_SHA = re.compile(r"^[0-9a-f]{64}$")


def observation_review(model: str, service: dict | None, resource: dict | None,
                       *, config: dict | None = None) -> dict:
    catalog = model_catalog(config)
    if model not in catalog["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    spec = catalog["models"][model]
    s = service if isinstance(service, dict) else {}
    r = resource if isinstance(resource, dict) else {}
    issues = []
    role = s.get("runtime_role")
    trial = s.get("p5_development_trial") is True
    if role not in ("DEVELOPMENT_TRIAL", "CANONICAL") or (role == "DEVELOPMENT_TRIAL") != trial:
        issues.append("SERVICE_ROLE_UNOBSERVED_OR_CONTRADICTORY")
    if trial and model != "orcarouter":
        issues.append("UNREGISTERED_TRIAL_ROLE")
    if s.get("observed_model") != model or r.get("model") != model:
        issues.append("MODEL_OBSERVATIONS_NOT_BOUND")
    if s.get("status") not in ("LIVE_P5_TRIAL_API_VERIFIED", "LIVE_SERVICE_VERIFIED"):
        issues.append("SERVICE_API_NOT_VERIFIED")
    if (trial and s.get("status") != "LIVE_P5_TRIAL_API_VERIFIED") or (
            not trial and s.get("status") != "LIVE_SERVICE_VERIFIED"):
        issues.append("SERVICE_STATUS_ROLE_MISMATCH")
    if s.get("issues"):
        issues.append("SERVICE_HAS_UNRESOLVED_ISSUES")
    checks = s.get("checks")
    if not isinstance(checks, dict) or not checks or any(x is not True for x in checks.values()):
        issues.append("SERVICE_CHECKS_NOT_ALL_TRUE")
    served_id = s.get("expected_served_id")
    if not isinstance(served_id, str) or not served_id:
        issues.append("API_SERVED_ID_MISSING")
    if served_id != spec["served_id"]:
        issues.append("API_SERVED_ID_REGISTRY_DRIFT")
    ids = s.get("observed_model_ids")
    if not isinstance(ids, list) or ids != [served_id]:
        issues.append("API_MODEL_LIST_UNBOUND")
    active = s.get("active_container")
    active = active if isinstance(active, dict) else {}
    name = active.get("name")
    if not isinstance(name, str) or not name:
        issues.append("ACTIVE_CONTAINER_NAME_MISSING")
    if not trial and name != spec["container"]:
        issues.append("CANONICAL_CONTAINER_NAME_MISMATCH")
    if trial and name == spec["container"]:
        issues.append("TRIAL_MUST_NOT_BE_CANONICAL")
    if s.get("host_port") != 8000 or r.get("model_identity_verified_by_api") is True:
        # Resource diagnostic alone deliberately does not verify the API identity.
        if s.get("host_port") != 8000:
            issues.append("FIXED_PORT_MISMATCH")
    if r.get("status") != "OBSERVED_PARTIAL":
        issues.append("RESOURCE_HOST_OBSERVATION_INCOMPLETE")
    if r.get("model_repo") != spec["checkpoint"]:
        issues.append("RESOURCE_CHECKPOINT_MISMATCH")
    if r.get("api_served_id_declared") != served_id:
        issues.append("RESOURCE_DECLARED_API_ID_MISMATCH")
    docker = r.get("docker")
    docker = docker if isinstance(docker, dict) else {}
    container = docker.get("container")
    container = container if isinstance(container, dict) else {}
    cid = container.get("id")
    if docker.get("status") != "OBSERVED":
        issues.append("RESOURCE_DOCKER_NOT_OBSERVED")
    if not isinstance(cid, str) or not _SHA.fullmatch(cid):
        issues.append("FULL_CONTAINER_ID_UNOBSERVED")
    if container.get("name") != name:
        issues.append("SERVICE_RESOURCE_CONTAINER_NAME_DRIFT")
    if container.get("image_id") != active.get("image_id"):
        issues.append("SERVICE_RESOURCE_IMAGE_ID_DRIFT")
    if container.get("running") is not True:
        issues.append("RESOURCE_CONTAINER_NOT_RUNNING")
    if r.get("model_identity_verified_by_api") is not False:
        issues.append("RESOURCE_API_PROBE_SEMANTICS_INVALID")
    return {
        "schema_version": 1, "stage": "p5", "action": "observation-review",
        "scope": "SERVICE_RESOURCE_CORRELATION_NOT_RUNTIME_ACCEPTANCE",
        "model": model, "runtime_role": role,
        "canonical_container": spec["container"],
        "observed_container": name, "container_id": cid,
        "served_id": served_id, "api_port": 8000,
        "status": ("SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE"
                   if not issues else "BLOCKED"),
        "issues": sorted(set(issues)),
        "service_api_identity_claimed": s.get("status") in (
            "LIVE_P5_TRIAL_API_VERIFIED", "LIVE_SERVICE_VERIFIED"),
        "gpu_exclusivity_verified": False,
        "port_process_ownership_verified": False,
        "ple_residency_verified": False,
        "benchmark_verified": False, "executed": False,
        "production_released": False, "operations_enabled": False,
        "real_dgx_verified": False,
        "note": ("Even consistent paired observations cannot establish independently "
                 "authenticated Docker ID, GPU exclusivity, port PID ownership, "
                 "PLE residency, benchmark quality, or launch authorization."),
    }


def observation_capture(model: str, *, service_probe: Callable | None = None,
                        resource_probe: Callable | None = None) -> dict:
    """Perform exactly one service and one resource read-only probe, sequentially.

    No inference workloads or writes. Since probes are sequential, container
    replacement between them is detected via name/image only; there is no
    independent service-side Docker ID and no atomic ownership guarantee.
    """
    model_catalog()  # policy check
    from scripts.manager.service_status import inspect_live_status
    from scripts.manager.resource_diagnostics import snapshot
    s = (service_probe or inspect_live_status)()
    r = (resource_probe or snapshot)(model=model)
    result = observation_review(model, s, r)
    result["action"] = "observation-capture"
    result["scope"] = "READ_ONLY_SEQUENTIAL_PROBES_NOT_ATOMIC"
    result["probe_performed"] = True
    result["service_status"] = s.get("status") if isinstance(s, dict) else None
    result["resource_status"] = r.get("status") if isinstance(r, dict) else None
    result["real_dgx_verified"] = False
    return result
