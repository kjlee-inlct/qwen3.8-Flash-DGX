"""Model-first read-only lifecycle planner and explicit operator invitations.

Existing P1 and P2 adapters own real actions; no new execution path bypasses
their gates. Docker/socket observations are read-only and runtime-unqualified.
"""
from __future__ import annotations

import json
from typing import Any

MODEL_CHOICES = {
    "flash-next": {"title": "NVIDIA Flash-Next", "stage": "p1"},
    "27b": {"title": "NVIDIA 27B", "stage": "p2"},
    "orcarouter": {"title": "Orcarouter Flash-Next", "stage": "p5"},
}
ALIASES = {"next-flash": "flash-next", "orcarouter-flash-next": "orcarouter"}
API_PORT = 8000


def normalize(model: str) -> str:
    selected = ALIASES.get(model.lower(), model.lower())
    if selected not in MODEL_CHOICES:
        raise ValueError("UNKNOWN_MODEL_SELECTION")
    return selected


def _step(action: str, state: str, reason: str, *, scope: str = "none") -> dict:
    return {
        "action": action, "state": state,
        "reason": reason, "approval_scope": scope,
    }


def selection_plan(model: str, *, service: dict[str, Any] | None = None,
                   checkpoint: dict[str, Any] | None = None) -> dict[str, Any]:
    """Pure decision logic: supplied observation is data, not execution authority."""
    selected = normalize(model)
    spec = MODEL_CHOICES[selected]
    if service is None:
        from scripts.manager.service_manifest import inspect_service
        try:
            service = inspect_service()
        except (OSError, ValueError, RuntimeError) as exc:
            service = {
                "status": "BLOCKED",
                "issues": ["SERVICE_OBSERVATION_FAILED:" + type(exc).__name__],
                "observed_model": None, "managed_containers": [],
                "download_running": False,
            }
    if selected == "27b" and checkpoint is None:
        from scripts.manager.p2_27b_inventory import inspect_27b
        from scripts.manager.p2_27b_download import REVISION
        try:
            checkpoint = inspect_27b(expected_revision=REVISION)
        except (OSError, ValueError, RuntimeError) as exc:
            checkpoint = {
                "source_files_present": False,
                "issues": ["CHECKPOINT_OBSERVATION_FAILED:" + type(exc).__name__],
                "checkpoint_status": "UNKNOWN",
            }

    observed = service.get("observed_model")
    if observed is not None and observed not in MODEL_CHOICES:
        observed = None
    download_running = service.get("download_running") is True
    source_present = bool(checkpoint and checkpoint.get("source_files_present"))
    service_ok = service.get("status") == "OBSERVED_UNQUALIFIED"
    issues = list(service.get("issues", []))
    steps: list[dict] = []

    # Discovery never proves that a live API serves the expected ID or that
    # the same model is the only GPU resident. Stateful operations stay locked.
    if not service_ok:
        state, next_action = "UNKNOWN", "blocked"
        issues.append("LIVE_SERVICE_STATE_UNVERIFIED")
        steps.append(_step("inspect", "BLOCKED", "Live service inventory incomplete"))
    elif observed == selected:
        state, next_action = "RUNNING_OBSERVED", "none"
        steps.append(_step("verify_api", "OPTIONAL",
                           "Running container observed; API identity not yet verified"))
    elif selected == "27b" and download_running:
        state, next_action = "DOWNLOADING", "monitor_download"
        steps.append(_step("monitor_download", "IN_PROGRESS",
                           "An existing NVIDIA 27B download container is running"))
        steps.append(_step("verify_checkpoint", "PENDING",
                           "Inspect exact pinned revision after transfer exits"))
        steps.append(_step("qualify_runtime", "BLOCKED",
                           "vLLM 0.32/GB10 loader and image qualification pending"))
    elif selected == "27b" and not source_present:
        if checkpoint and checkpoint.get("checkpoint_status") == "UNKNOWN":
            state, next_action = "UNKNOWN", "blocked"
            issues.extend(checkpoint.get("issues", []))
        else:
            state, next_action = "ABSENT", "download"
            steps.append(_step("download", "AVAILABLE",
                               "Pinned NVIDIA 27B checkpoint absent",
                               scope="checkpoint_download_only"))
            steps.append(_step("qualify_runtime", "BLOCKED",
                               "Runtime and model recipe not yet qualified"))
            if observed:
                steps.append(_step("switch", "BLOCKED",
                                   "Requires a separately approved stop/rollback transaction",
                                   scope="service_transition"))
    elif selected == "27b":
        state, next_action = "SOURCE_PRESENT_UNQUALIFIED", "blocked"
        steps.append(_step("qualify_runtime", "BLOCKED",
                           "Pinned source present; image/architecture/GPU unverified"))
        if observed:
            steps.append(_step("switch", "BLOCKED",
                               "Stop old model, release port 8000, start and verify",
                               scope="service_transition"))
    elif selected == "flash-next" and observed is not None:
        # Never run the P1 guided start path while 27B/Orcarouter is active.
        # Only the separately tested, approved service handover may do this.
        state, next_action = "TRANSITION_UNQUALIFIED", "blocked"
        issues.append("EXCLUSIVE_ACTIVE_MODEL_SWITCH_REQUIRED")
        steps.append(_step("switch", "BLOCKED",
                           "Stop the other model via qualified atomic handover",
                           scope="service_transition"))
    elif selected == "flash-next":
        state, next_action = "REVIEW_REQUIRED", "open_p1_guided"
        steps.append(_step("review_p1", "AVAILABLE",
                           "Reuse the existing guarded P1 prepare/start/wait/verify backend",
                           scope="p1_individual_plan_approval"))
        if observed:
            steps.append(_step("switch", "BLOCKED",
                               "Active model needs separately qualified transition",
                               scope="service_transition"))
    else:
        state, next_action = "SOURCE_UNQUALIFIED", "blocked"
        issues.append("ORCAROUTER_RUNTIME_ADAPTER_UNQUALIFIED")
        steps.append(_step("qualify_runtime", "BLOCKED",
                           "Review and qualify the separate Orcarouter adapter before starting"))
        if observed:
            steps.append(_step("switch", "BLOCKED",
                               "One active GPU model only; rollback gate required",
                               scope="service_transition"))

    # A transfer running in the background is a read-only fact. The currently
    # observed inference model is never stopped by model selection.
    preview = None
    if observed is not None and observed != selected:
        from scripts.manager.service_transition_preview import preview_transition
        preview = preview_transition(
            selected, service=service,
            checkpoint_ready=source_present if selected == "27b" else False,
            runtime_qualified=False, api_identity_verified=False,
            gpu_exclusivity_verified=False, rollback_verified=False,
        )
    ple_registration = None
    if selected == "orcarouter":
        from scripts.manager.ple_assets import catalog
        try:
            ple_registration = catalog()["assets"][0]
        except (OSError, ValueError, KeyError, TypeError):
            ple_registration = {"asset_id": "orcarouter-bf16-ple",
                                "registered": False, "runtime_qualified": False}
    return {
        "schema_version": 1,
        "interface": "MODEL_SELECTION_PLAN",
        "selected_model": selected, "title": spec["title"],
        "source_stage": spec["stage"],
        "ple_registration": ple_registration,
        "observed_model": observed, "api_host_port": API_PORT,
        "status": state, "next_action": next_action,
        "download_state": ("IN_PROGRESS" if download_running else
                           "SOURCE_PRESENT" if source_present else
                           "NOT_OBSERVED"),
        "checkpoint_state": (checkpoint or {}).get("checkpoint_status",
                                                 "NOT_INSPECTED"),
        "runtime_qualified": False if selected != "flash-next" else None,
        "api_identity_verified": False,
        "gpu_exclusivity_verified": False,
        "operations_enabled": False, "executed": False,
        "approval_accepted": False,
        "issues": sorted(set(issues)), "steps": steps,
        "transition_preview": preview,
        "service_manifest": {
            "status": service.get("status"),
            "observed_state": service.get("observed_state"),
            "observed_model": service.get("observed_model"),
            "download_running": download_running,
            "api_port_8000_listening": service.get("api_port_8000_listening"),
        },
        "notice": "Selection is read-only. Download and P1 actions use existing exact approval gates; service switch/stop is not yet enabled.",
    }


def render_plan(doc: dict) -> None:
    print("\nSelected: " + doc["title"])
    print("  Service: " + (doc["observed_model"] or "unknown / no managed model"))
    print("  Port:    :" + str(doc["api_host_port"]))
    print("  State:   " + doc["status"])
    ple = doc.get("ple_registration")
    if ple:
        print("  PLE:     " + ple["asset_id"] + " / " +
              ("REGISTERED" if ple.get("registered") else "MANIFEST_BLOCKED") +
              " / GPU runtime NOT_VERIFIED")
    for item in doc["steps"]:
        print("  - " + item["action"] + ": " + item["state"]
              + " — " + item["reason"])
    if doc["issues"]:
        print("  Issues: " + ", ".join(doc["issues"]))


def interactive_select(model: str) -> int:
    """One model choice and only the necessary offer; no implicit action."""
    plan = selection_plan(model)
    render_plan(plan)
    if plan["next_action"] == "download" and model == "27b":
        approval = input("Download the pinned 27B checkpoint? [y/N]: ").strip().lower()
        if approval == "y":
            from wizard.menus.models import qwen_27b
            return qwen_27b.run(["download", "--guided"])
    elif plan["next_action"] == "open_p1_guided":
        approval = input("Open existing guarded Flash-Next actions? [y/N]: ").strip().lower()
        if approval == "y":
            from wizard.menus.models import flash_next
            return flash_next.run(["guided"])
    return 0


def run_cli(argv: list[str], *, as_json: bool = False, dry_run: bool = False) -> int:
    if not argv or len(argv) != 1:
        document = {"status": "BLOCKED", "executed": False,
                    "issues": ["SELECT_REQUIRES_EXACT_MODEL"]}
        print(json.dumps(document) if as_json else str(document))
        return 2
    try:
        document = selection_plan(argv[0])
    except ValueError as exc:
        document = {"status": "BLOCKED", "executed": False,
                    "issues": [str(exc)]}
        print(json.dumps(document) if as_json else str(document))
        return 2
    if dry_run:
        document["dry_run"] = True
    if as_json:
        print(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        render_plan(document)
    return 3 if document["next_action"] == "blocked" else 0
