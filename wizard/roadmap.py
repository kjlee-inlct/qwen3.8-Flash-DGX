"""Operator's full P1–P7 readiness dashboard, evidence scoped and read-only.

This is an overview for debugging milestones as P2→P7 are qualified. It never
promotes source files, an existing Docker container or historic P1 evidence into
new runtime/GPU/benchmark/rollback PASS.
"""
from __future__ import annotations

import json
from typing import Any


MILESTONES = (
    ("P1", "Flash-Next install / API / benchmark"),
    ("P2", "NVIDIA 27B download / runtime / API / benchmark"),
    ("P3", "Flash-Next <-> 27B switch and restore"),
    ("P4", "Conditional storage / protected cleanup"),
    ("P5", "Orcarouter Flash-Next runtime / benchmark"),
    ("P6", "Orcarouter <-> 27B switch and restore"),
    ("P7", "Full service / proxy / gateway / release acceptance"),
)


def _local_history(model: str, kind: str) -> dict[str, Any]:
    """Show locally readable history, never treat it as live qualification."""
    from scripts.manager.evidence_catalog import history
    try:
        doc = history(model=model, kind=kind, limit=20)
        if doc.get("status") != "READ_ONLY_HISTORY":
            return {"status": "UNAVAILABLE", "count": 0}
        rows = doc.get("records") or []
        latest = rows[0] if rows else {}
        return {"status": "LOCAL_HISTORY_OBSERVED" if rows else "UNAVAILABLE",
                "count": doc.get("count", 0),
                "latest_record_status": latest.get("status"),
                "latest_timestamp_utc": latest.get("timestamp_utc"),
                "issues": doc.get("issues") or []}
    except (OSError, ValueError, TypeError, KeyError):
        return {"status": "UNAVAILABLE", "count": 0}


def readiness_report(*, service: dict[str, Any] | None = None,
                     checkpoint: dict[str, Any] | None = None,
                     live_status: dict[str, Any] | None = None,
                     p3_history: dict[str, Any] | None = None,
                     model_history: dict[str, dict] | None = None,
                     operating_audit: dict[str, Any] | None = None) -> dict[str, Any]:
    probe_live = service is None
    if service is None:
        from scripts.manager.service_manifest import inspect_service
        try:
            service = inspect_service()
        except (OSError, ValueError, RuntimeError) as exc:
            service = {
                "status": "BLOCKED", "observed_model": None,
                "download_running": False, "issues": [
                    "SERVICE_INVENTORY_FAILED:" + type(exc).__name__
                ]
            }
    if checkpoint is None:
        from scripts.manager.p2_27b_inventory import inspect_27b
        from scripts.manager.p2_27b_download import REVISION
        try:
            checkpoint = inspect_27b(expected_revision=REVISION)
        except (OSError, ValueError, RuntimeError) as exc:
            checkpoint = {
                "source_files_present": False, "checkpoint_status": "UNKNOWN",
                "issues": ["P2_SOURCE_AUDIT_FAILED:" + type(exc).__name__]
            }
    download_running = service.get("download_running") is True
    source_present = checkpoint.get("source_files_present") is True
    if service.get("status") != "OBSERVED_UNQUALIFIED":
        p2 = "OBSERVATION_BLOCKED"
    elif download_running:
        p2 = "DOWNLOAD_IN_PROGRESS"
    elif source_present:
        p2 = "SOURCE_PRESENT_RUNTIME_UNQUALIFIED"
    else:
        p2 = "SOURCE_ABSENT_OR_INCOMPLETE"
    if live_status is None and probe_live:
        from scripts.manager.service_status import inspect_live_status
        try:
            # One Docker inventory is shared with the separate HTTP identity probe.
            live_status = inspect_live_status(manifest_inspector=lambda: service)
        except (OSError, RuntimeError, ValueError, TypeError):
            live_status = {"status": "BLOCKED", "issues": ["LIVE_STATUS_UNAVAILABLE"]}
    if p3_history is None:
        from scripts.manager.operational_switch import historical_p3_receipts
        p3_history = historical_p3_receipts()
    p3_pass = p3_history.get("status") == "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED"
    if operating_audit is None:
        from scripts.manager.operational_audit import inspect_journal
        from scripts.manager.operational_switch import ROOT as OPERATING_ROOT
        operating_audit = inspect_journal(OPERATING_ROOT)
    if model_history is None:
        model_history = {
            "flash_verify": _local_history("flash-next", "verify"),
            "flash_benchmark": _local_history("flash-next", "benchmark"),
            "27b_benchmark": _local_history("27b", "benchmark"),
        }
    scopes = {
        "P1": "GUARDED_BACKEND_PRESENT_LIVE_REVALIDATION_REQUIRED",
        "P2": p2,
        "P3": ("ONE_OFF_A_B_C_RECEIPTS_PRESENT_GUIDED_SOURCE_TRIAL_NOT_DGX_QUALIFIED"
               if p3_pass else "LOCAL_P3_RECEIPTS_UNAVAILABLE_GUIDED_SOURCE_ONLY"),
        "P4": "CONDITIONAL_SOURCE_ONLY_NO_DELETE_APPROVAL",
        "P5": "ORCAROUTER_ADAPTER_UNQUALIFIED",
        "P6": "SWITCH_EXECUTOR_NOT_QUALIFIED",
        "P7": "RELEASE_GATES_NOT_COMPLETED",
    }
    evidence = {
        "P1": {"verify": model_history.get("flash_verify", {"status": "UNAVAILABLE"}),
               "benchmark": model_history.get("flash_benchmark", {"status": "UNAVAILABLE"})},
        "P2": {"benchmark": model_history.get("27b_benchmark", {"status": "UNAVAILABLE"})},
        "P3": {"stage_a_b_c": p3_history.get("status", "UNAVAILABLE"),
               "issues": p3_history.get("issues", []),
               "independent_operating_journal": operating_audit},
    }
    milestones = [
        {"stage": stage, "title": title, "state": scopes[stage],
         "source_implemented": stage in ("P1", "P2", "P3"),
         "source_interface_present": True,
         "cpu_ci": "CHECK_GITHUB_ACTIONS_SEPARATELY",
         "historical_backend_evidence": evidence.get(stage, {"status": "UNVERIFIED"}),
         "runtime_pass_claimed": False,
         "general_operating_switch": (
             "GUIDED_SOURCE_PLUS_SEPARATE_TRIAL_UNRELEASED" if stage == "P3"
             else "NOT_QUALIFIED_OR_NOT_APPLICABLE"),
         "interactive_wizard_ux_acceptance": (
             "SOURCE_MENU_PRESENT_ACTUAL_DGX_NOT_VERIFIED"
             if stage == "P3" else "NOT_VERIFIED"),
         "requires_separate_approval": stage in ("P2", "P3", "P4", "P5", "P6", "P7")}
        for stage, title in MILESTONES
    ]
    observed_live = live_status if isinstance(live_status, dict) else {}
    return {
        "schema_version": 2, "interface": "P1_P7_ACCEPTANCE_DASHBOARD",
        "stage": "p7", "scope": "DGX_READ_ONLY",
        "status": "NOT_RELEASE_QUALIFIED",
        "executed": False, "operations_enabled": False,
        "api_host_port": 8000, "max_active_gpu_models": 1,
        "observed_model": service.get("observed_model"),
        "live_service_status": observed_live.get("status", "NOT_CHECKED"),
        "live_api_served_id": (observed_live.get("expected_served_id")
                               if observed_live.get("status") == "LIVE_SERVICE_VERIFIED"
                               else None),
        "download_running": download_running,
        "p2_checkpoint_status": checkpoint.get("checkpoint_status"),
        "operating_journal_audit": operating_audit,
        "ordinary_switch_production_released": False,
        "milestones": milestones, "release_ready": False,
        "issues": sorted(set((service.get("issues") or [])
                             + (checkpoint.get("issues") or [])
                             + (observed_live.get("issues") or []))),
        "notice": "Historical P1/P2 records, immutable P3 A/B/C receipts, current live API, "
                  "source-guided switch, trial acceptance and live production UX are separate. "
                  "No historical PASS substitutes for a current switch approval.",
    }


def run_cli(*, as_json: bool = False, dry_run: bool = False) -> int:
    document = readiness_report()
    if dry_run:
        document["dry_run"] = True
    if as_json:
        print(json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("P1–P7 acceptance status — NOT_RELEASE_QUALIFIED")
        print("Active model observed:", document["observed_model"] or "unknown/none")
        print("Current API:", document["live_service_status"],
              "| Served ID:", document["live_api_served_id"] or "unverified")
        for row in document["milestones"]:
            print(f"  {row['stage']}: {row['title']}: {row['state']}")
    return 0  # Read-only status, not release success.
