"""Common model-lifecycle action catalog and guarded dispatch for P1–P7.

This owns *planning* and UX composition. Existing P1/P2 engines alone own
approved execution. Later adapters can implement these slots without changing
the root UI or weakening approval boundaries.
"""
from __future__ import annotations

import json
from typing import Any

from wizard.quickstart import MODEL_CHOICES, normalize, selection_plan
from wizard.menus import HANDLERS

MODEL_ACTIONS: dict[str, tuple[str, ...]] = {
    "flash-next": ("inspect", "download", "prepare", "start", "wait",
                   "verify", "benchmark", "switch", "rollback", "recipe"),
    "27b": ("inspect", "download", "prepare", "start", "wait",
             "verify", "benchmark", "switch", "rollback", "recipe"),
    "orcarouter": ("inspect", "download", "prepare", "start", "wait",
                   "verify", "benchmark", "switch", "rollback", "recipe"),
}
REQUIRES_SEPARATE_APPROVAL = frozenset((
    "download", "prepare", "start", "switch", "rollback",
))
STAGES = ("P1", "P2", "P3", "P4", "P5", "P6", "P7")


def action_capability(model: str, action: str, selected: dict) -> dict[str, Any]:
    """Safety-first action availability; never infer execution from displayed plan."""
    model = normalize(model)
    if action not in MODEL_ACTIONS[model]:
        raise ValueError("UNKNOWN_MODEL_ACTION")
    observed = selected.get("observed_model")
    current = selected.get("status")
    issues: list[str] = []
    stage = MODEL_CHOICES[model]["stage"]

    if action == "inspect":
        availability = "READ_ONLY"
        reason = "Inspect checkpoint and actual service state"
    elif action == "download" and model == "27b":
        if current == "DOWNLOADING":
            availability, reason = "IN_PROGRESS", "Existing download is active"
        elif selected.get("next_action") == "download":
            availability, reason = "APPROVAL_REQUIRED", "Use pinned P2 download plan"
        else:
            availability, reason = "BLOCKED", "Download is not needed or state is uncertain"
            issues.append("CHECKPOINT_NOT_CONFIRMED_ABSENT")
    elif action == "download":
        availability, reason = "BLOCKED", "No reviewed download executor for this model"
        issues.append("MODEL_DOWNLOAD_ADAPTER_NOT_IMPLEMENTED")
    elif action == "recipe":
        availability, reason = "READ_ONLY", "Show pinned recipe and qualification blockers"
    elif action in ("prepare", "start", "wait", "verify", "benchmark") and model == "flash-next":
        availability, reason = "GUARDED_P1", "Reuse existing exact-action P1 plans and approvals"
    elif action == "switch":
        availability, reason = "BLOCKED", "Service handover executor and restore tests not qualified"
        issues.extend(("SERVICE_TRANSITION_EXECUTOR_NOT_IMPLEMENTED",
                       "TARGET_RUNTIME_QUALIFICATION_REQUIRED"))
    elif action == "rollback":
        availability, reason = "BLOCKED", "Rollback executor has not passed recovery tests"
        issues.append("ROLLBACK_NOT_VERIFIED")
    else:
        availability, reason = "BLOCKED", "Model-specific runtime adapter not qualified"
        issues.append("MODEL_RUNTIME_ADAPTER_NOT_IMPLEMENTED")
    return {
        "schema_version": 1,
        "model": model, "stage": stage, "action": action,
        "status": availability, "reason": reason,
        "requires_approval": action in REQUIRES_SEPARATE_APPROVAL,
        "approval_scope": (
            "checkpoint_download_only" if action == "download" else
            "service_transition" if action in ("switch", "rollback") else
            "model_lifecycle" if action in ("prepare", "start") else
            "none"
        ),
        "executed": False, "approval_accepted": False,
        "operations_enabled": availability in ("READ_ONLY", "GUARDED_P1", "APPROVAL_REQUIRED"),
        "issues": issues,
        "active_model": observed, "selection_status": current,
        "api_host_port": 8000,
    }


def model_workflow(model: str, *, selection: dict | None = None) -> dict[str, Any]:
    selected_model = normalize(model)
    doc = selection if selection is not None else selection_plan(selected_model)
    actions = [
        action_capability(selected_model, action, doc)
        for action in MODEL_ACTIONS[selected_model]
    ]
    stages = {
        "P1": "EXISTING_GUARDED_BACKEND" if selected_model == "flash-next" else "NOT_APPLICABLE",
        "P2": "DOWNLOAD_IMPLEMENTED_RUNTIME_BLOCKED" if selected_model == "27b" else "NOT_APPLICABLE",
        "P3": "SOURCE_PREVIEW_ONLY",
        "P4": "SOURCE_PLAN_ONLY",
        "P5": "SOURCE_ADAPTER_UNQUALIFIED" if selected_model == "orcarouter" else "NOT_APPLICABLE",
        "P6": "SOURCE_PREVIEW_ONLY",
        "P7": "SOURCE_PLAN_ONLY",
    }
    return {
        "schema_version": 1, "interface": "UNIFIED_MODEL_WORKFLOW",
        "model": selected_model, "title": MODEL_CHOICES[selected_model]["title"],
        "api_host_port": 8000, "one_active_gpu_model": True,
        "observed_model": doc.get("observed_model"),
        "status": doc.get("status"),
        "next_action": doc.get("next_action"),
        "actions": actions, "roadmap": stages,
        "selection": doc, "executed": False, "approval_accepted": False,
        "notice": ("Workflow is source-only until each adapter qualifies. "
                   "Download and Flash-Next actions use existing separate approval gates; "
                   "no service stop/start, GPU switch or deletion is automated."),
    }


def invoke_model_action(model: str, action: str, *,
                        workflow: dict | None = None, guided: bool = False,
                        as_json: bool = False) -> int:
    """Dispatch only approved existing pathways, otherwise display a blocker.

    The direct model action UI never synthesizes an approval ID, never sets
    --execute and cannot stop/restart a container. P1 guided, P2 pinned
    downloader prompts are owned by their proven existing adapters.
    """
    selected = normalize(model)
    data = workflow if workflow is not None else model_workflow(selected)
    capability = next((a for a in data["actions"] if a["action"] == action), None)
    if capability is None:
        raise ValueError("UNKNOWN_MODEL_ACTION")
    if action == "download" and selected == "27b" and capability["status"] == "APPROVAL_REQUIRED":
        from wizard.menus.models import qwen_27b
        return qwen_27b.run(["download", "--guided"] if guided else
                            ["plan", "--for-action", "download"],
                            as_json=as_json)
    if selected == "flash-next" and action in ("prepare", "start", "wait",
                                                "verify", "benchmark"):
        from wizard.menus.models import flash_next
        return flash_next.run(["guided"] if guided else ["plan", "--for-action", action],
                              as_json=as_json)
    if action == "inspect":
        from wizard.quickstart import render_plan
        if as_json:
            print(json.dumps(data["selection"], ensure_ascii=False, indent=2))
        else:
            render_plan(data["selection"])
        return 0
    if action == "recipe":
        result = {
            "model": selected, "status": "SOURCE_ONLY",
            "executed": False,
            "recipe_validation": "UNQUALIFIED" if selected != "flash-next" else "P1_BACKEND_MANAGED",
            "notice": "Use committed model recipe and legacy stage for exact details.",
        }
        print(json.dumps(result, ensure_ascii=False, indent=2) if as_json else
              f"{selected} recipe: {result['recipe_validation']}; no execution.")
        return 0
    issues = capability["issues"] or ["NO_ACTION_EXECUTOR_AUTHORIZED"]
    result = {
        **capability, "status": "BLOCKED", "issues": issues,
        "operations_enabled": False, "executed": False, "approval_accepted": False,
        "plan_id": None,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2) if as_json else
          f"{selected} {action}: BLOCKED — {', '.join(issues)}")
    return 3


def run_cli(args: list[str], *, as_json: bool = False,
            dry_run: bool = False) -> int:
    if not args:
        print(json.dumps({"status": "BLOCKED", "executed": False,
                          "issues": ["MODEL_REQUIRED"]}))
        return 2
    model = args[0]
    tail = args[1:]
    action = None
    if tail:
        if len(tail) != 2 or tail[0] != "--for-action":
            print(json.dumps({"status": "BLOCKED", "executed": False,
                              "issues": ["ONLY_READ_ONLY_WORKFLOW_PLAN_ALLOWED"]}))
            return 2
        action = tail[1]
    try:
        result = model_workflow(model)
        if action is not None:
            result = action_capability(normalize(model), action, result["selection"])
    except ValueError as exc:
        print(json.dumps({"status": "BLOCKED", "executed": False,
                          "issues": [str(exc)]}))
        return 2
    if dry_run:
        result["dry_run"] = True
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"Model workflow: {result['model']}")
        if action is None:
            for item in result["actions"]:
                print(f"  {item['action']:<11} {item['status']}")
        else:
            print(f"  {action}: {result['status']}")
    return 0  # planning is inspectable even when the actual operation is blocked
