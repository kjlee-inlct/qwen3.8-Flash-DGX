"""Live read-only service manifest with one-model and :8000 port invariants.

The committed policy is desired state. Actual Docker/socket observations remain
the source of truth. Never treat an old manifest as authority to stop/restart.
This module does not persist state or mutate Docker, GPU or the API.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.manager.inventory import inspect_host

POLICY_PATH = Path(__file__).resolve().parents[2] / "runtimes/service-policy.json"


def policy() -> dict[str, Any]:
    doc = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    if (doc["max_active_gpu_models"] != 1
            or doc["api"]["host_port"] != 8000
            or not doc["transitions"]["stop_old_before_start_new"]):
        raise ValueError("service policy invariant changed")
    return doc


def manifest_from_observation(inv: dict, *, desired: str | None = None,
                              spec: dict | None = None) -> dict[str, Any]:
    cfg = policy() if spec is None else spec
    models = cfg["models"]
    if desired is not None and desired not in models:
        raise ValueError("invalid desired model")
    present = []
    running = []
    for model_key, desc in models.items():
        for container in inv.get("containers", []):
            if container.get("name") != desc["container_name"]:
                continue
            row = {"model": model_key, "container_name": desc["container_name"],
                   "image_id": container.get("image_id"),
                   "status": container.get("status"),
                   "ports": container.get("ports")}
            present.append(row)
            if str(container.get("status", "")).startswith("Up"):
                running.append(row)
    download_containers = [
        {"name": c.get("name"), "status": c.get("status"),
         "image_id": c.get("image_id")}
        for c in inv.get("containers", [])
        if c.get("name") == "qwen38-27b-dl"
    ]
    # Status is observed, not an authoritative byte-progress measurement.
    download_running = any(
        str(c.get("status", "")).startswith("Up")
        for c in download_containers
    )
    errors = list(inv.get("errors", []))
    if len(running) > 1:
        errors.append("SINGLE_ACTIVE_MODEL_POLICY_VIOLATION")
    host_port = cfg["api"]["host_port"]
    port_listening = host_port in inv.get("observed_listen_ports", [])
    # An unknown service may occupy 8000; never infer ownership from an open port.
    live_owner = running[0]["model"] if len(running) == 1 else None
    state = ("UNKNOWN" if errors else
             "MULTIPLE_MANAGED_MODELS_RUNNING" if len(running) > 1 else
             "ONE_MANAGED_MODEL_RUNNING" if len(running) == 1 else
             "NO_MANAGED_MODEL_RUNNING")
    return {
        "schema_version": 1, "stage": "svc", "runtime": "NOT_RUN",
        "scope": "DGX_READ_ONLY",
        "status": "BLOCKED" if errors else "OBSERVED_UNQUALIFIED",
        "executed": False, "operations_enabled": False,
        "policy": {"max_active_gpu_models": 1, "api_host_port": host_port,
                   "stop_old_before_start_new": True,
                   "rollback_required": True},
        "desired_model": desired,
        "observed_state": state, "observed_model": live_owner,
        "managed_containers": present,
        "download_containers": download_containers,
        "download_running": download_running,
        "api_port_8000_listening": port_listening,
        "api_model_identity_verified": False,
        "gpu_exclusivity_verified": False,
        "port_model_ownership_verified": False,
        "drift": (desired != live_owner if desired is not None
                  and not errors else None),
        "issues": sorted(set(errors)),
        "safety": {
            "old_service_stop_requires_scoped_approval": True,
            "new_service_start_requires_old_stop_and_free_port": True,
            "startup_failure_requires_old_restore": True,
            "download_does_not_stop_current_service": True,
        },
        "notice": "Live observation is not permission to stop/start/switch. API and GPU identity still need verification.",
    }


def inspect_service(*, inspector=inspect_host) -> dict[str, Any]:
    # The ordinary inventory checks port and name occupancy, but these are
    # informative for status: an active Flash-Next :8000 listener is expected.
    observed = inspector(name="qwen38-27b", port=8000)
    return manifest_from_observation(observed)
