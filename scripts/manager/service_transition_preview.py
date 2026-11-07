"""Non-executing service handover plan, from actual observation and policy.

This interface is useful to the model-first Wizard before any P2/P3/P5/P6
runtime executor is qualified. It *cannot* stop, start, switch or approve.
"""
from __future__ import annotations

from typing import Any

from scripts.manager.service_manifest import policy


def preview_transition(target: str, *, service: dict[str, Any],
                       checkpoint_ready: bool = False,
                       runtime_qualified: bool = False,
                       api_identity_verified: bool = False,
                       gpu_exclusivity_verified: bool = False,
                       rollback_verified: bool = False) -> dict[str, Any]:
    cfg = policy()
    models = cfg["models"]
    if target not in models:
        raise ValueError("UNKNOWN_TRANSITION_TARGET")
    source = service.get("observed_model")
    if source is not None and source not in models:
        raise ValueError("UNKNOWN_OBSERVED_MODEL")
    errors: list[str] = []
    if service.get("status") != "OBSERVED_UNQUALIFIED":
        errors.append("LIVE_SERVICE_INVENTORY_UNVERIFIED")
    if source == target:
        errors.append("TARGET_ALREADY_ACTIVE_NO_SWITCH_REQUIRED")
    if not checkpoint_ready:
        errors.append("TARGET_CHECKPOINT_NOT_QUALIFIED")
    if not runtime_qualified:
        errors.append("TARGET_RUNTIME_NOT_QUALIFIED")
    if source is not None and not api_identity_verified:
        errors.append("SOURCE_API_IDENTITY_UNVERIFIED")
    if not gpu_exclusivity_verified:
        errors.append("GPU_EXCLUSIVITY_UNVERIFIED")
    if source is not None and not rollback_verified:
        errors.append("RESTORE_SOURCE_NOT_VERIFIED")
    if service.get("download_running") and target == "27b":
        errors.append("TARGET_DOWNLOAD_IN_PROGRESS")
    errors.append("SERVICE_TRANSITION_EXECUTOR_NOT_IMPLEMENTED")
    steps = [
        {"phase": "OBSERVED", "action": "read-live-state",
         "description": "Verify actual Docker, GPU, API served ID and host port 8000"},
        {"phase": "PLANNED", "action": "approve",
         "description": "Pin target recipe/image/revision and independently verified rollback"},
        {"phase": "OLD_STOPPING", "action": "stop-current",
         "description": "Stop only the exact approved source inference container",
         "condition": "source is not None"},
        {"phase": "OLD_STOPPED", "action": "verify-port-free",
         "description": "Verify :8000 released; ensure no GPU inference model remains"},
        {"phase": "NEW_STARTING", "action": "start-target",
         "description": "Start only the selected qualified recipe on host port 8000"},
        {"phase": "NEW_VERIFYING", "action": "api-verify",
         "description": "Wait for health, exact /v1/models ID and bounded probes"},
        {"phase": "COMMITTED", "action": "journal-success",
         "description": "Append result and actual observed service state"},
    ]
    rollback = [
        {"phase": "ROLLBACK_STARTING", "action": "remove-failed-target",
         "description": "Stop only the exact failed target if it was launched"},
        {"phase": "ROLLBACK_STARTING", "action": "restore-old",
         "description": "Restore original pinned source image, recipe and API :8000"},
        {"phase": "RESTORED", "action": "verify-restored-api",
         "description": "Require original served model ID and health before reporting recovery"},
        {"phase": "RECOVERY_FAILED", "action": "report-manual-intervention",
         "description": "Do not falsely claim recovery if old API is unavailable"},
    ]
    return {
        "schema_version": 1,
        "interface": "SERVICE_TRANSITION_PREVIEW",
        "status": "BLOCKED", "executed": False, "approval_accepted": False,
        "plan_id": None, "operations_enabled": False, "runtime": "NOT_RUN",
        "source_model": source, "target_model": target,
        "api_host_port": 8000, "max_active_gpu_models": 1,
        "steps": steps, "rollback": rollback,
        "issues": sorted(set(errors)),
        "notice": "Read-only design plan. No service stop, start, switch, GPU operation or approval is permitted.",
    }
