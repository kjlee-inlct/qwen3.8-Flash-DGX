"""Live read-only service manifest with one-model and :8000 port invariants.

The committed policy is desired state. Actual Docker/socket observations remain
the source of truth. Never treat an old manifest as authority to stop/restart.
This module does not persist state or mutate Docker, GPU or the API.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.manager import manifest_registry
from scripts.manager.inventory import inspect_host

POLICY_PATH = Path(__file__).resolve().parents[2] / "runtimes/service-policy.json"


def policy() -> dict[str, Any]:
    doc = manifest_registry.load("service_policy")
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
    # Trial candidates are not canonical model registrations: recognize the
    # exact pinned P5 development container separately without promoting it.
    # Never use loose "qwen38-orcarouter*" prefix matching.
    errors = list(inv.get("errors", []))
    trial_name = None
    trial_served_id = None
    try:
        recipe = manifest_registry.load("orcarouter_recipe")
        trial = recipe["trial"]
        profile = recipe["profiles"][trial["profile"]]
        if (recipe["model"]["repo_id"] != models["orcarouter"]["checkpoint"]
            or recipe["model"]["revision"] != models["orcarouter"]["pinned_revision"]
            or recipe["vllm_version"] != "0.32.0"
            or recipe["launch_allowed"] is not False
            or recipe["register_as_runtime_recipe"] is not False
            or trial["profile"] != "mtp0"
            or not trial["container_name"].startswith("qwen38-orcarouter-")
            or trial["container_name"] == models["orcarouter"]["container_name"]
            or not trial["adapter"].startswith("qwen4exp-qsa62318-lmhead-v032-")
            or not isinstance(profile["served_id"], str)
            or profile["served_id"] != models["orcarouter"]["proposed_served_ids"]["mtp0"]):
            raise ValueError("P5_TRIAL_POLICY_IDENTITY_DRIFT")
        trial_name, trial_served_id = trial["container_name"], profile["served_id"]
    except (OSError, KeyError, ValueError, TypeError):
        errors.append("P5_TRIAL_RECIPE_OBSERVATION_UNAVAILABLE")
    present = []
    running = []
    for model_key, desc in models.items():
        allowed = [(desc["container_name"], False)]
        if model_key == "orcarouter" and trial_name:
            allowed.append((trial_name, True))
        for name, is_trial in allowed:
            for container in inv.get("containers", []):
                if container.get("name") != name:
                    continue
                row = {"model": model_key, "container_name": name,
                       "image_id": container.get("image_id"),
                       "status": container.get("status"),
                       "ports": container.get("ports"),
                       "p5_development_trial": is_trial,
                       "served_id": trial_served_id if is_trial else desc.get("served_id")}
                present.append(row)
                if str(container.get("status", "")).startswith("Up"):
                    running.append(row)
    # Managed-model removal/reinstallation is a separate lifecycle operation,
    # NOT prohibited by the selected test-container cleanup inventory.
    lifecycle = {
        key: desc.get("container_lifecycle", {})
        for key, desc in models.items()
    }
    retired_spec = cfg.get("retired_containers", {})
    retire_names = {
        row.get("name") for row in retired_spec.get("targets", [])
        if isinstance(row, dict) and isinstance(row.get("name"), str)
    }
    retired_seen = [
        {"name": c.get("name"), "status": c.get("status"),
         "image_id": c.get("image_id"),
         "manifest_registered": True}
        for c in inv.get("containers", [])
        if c.get("name") in retire_names
    ]
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
        "p5_trial_active": (len(running) == 1 and
                            running[0].get("p5_development_trial") is True),
        "p5_trial_candidate_name": trial_name,
        "managed_container_lifecycle": lifecycle,
        "retired_container_inventory": retired_seen,
        "retired_container_manifest_names": sorted(retire_names),
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
