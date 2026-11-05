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


def readiness_report(*, service: dict[str, Any] | None = None,
                     checkpoint: dict[str, Any] | None = None) -> dict[str, Any]:
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
    scopes = {
        "P1": "GUARDED_BACKEND_PRESENT_LIVE_REVALIDATION_REQUIRED",
        "P2": p2,
        "P3": "SWITCH_EXECUTOR_NOT_QUALIFIED",
        "P4": "CONDITIONAL_SOURCE_ONLY_NO_DELETE_APPROVAL",
        "P5": "ORCAROUTER_ADAPTER_UNQUALIFIED",
        "P6": "SWITCH_EXECUTOR_NOT_QUALIFIED",
        "P7": "RELEASE_GATES_NOT_COMPLETED",
    }
    milestones = [
        {"stage": stage, "title": title, "state": scopes[stage],
         "source_implemented": True,
         "runtime_pass_claimed": False,
         "requires_separate_approval": stage in ("P2", "P3", "P4", "P5", "P6", "P7")}
        for stage, title in MILESTONES
    ]
    return {
        "schema_version": 1, "interface": "P1_P7_ACCEPTANCE_DASHBOARD",
        "stage": "p7", "scope": "DGX_READ_ONLY",
        "status": "NOT_RELEASE_QUALIFIED",
        "executed": False, "operations_enabled": False,
        "api_host_port": 8000, "max_active_gpu_models": 1,
        "observed_model": service.get("observed_model"),
        "download_running": download_running,
        "p2_checkpoint_status": checkpoint.get("checkpoint_status"),
        "milestones": milestones, "release_ready": False,
        "issues": sorted(set(service.get("issues", [])
                             + checkpoint.get("issues", []))),
        "notice": "Source/CI readiness is not runtime, GPU, API or recovery acceptance.",
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
        for row in document["milestones"]:
            print(f"  {row['stage']}: {row['title']}: {row['state']}")
    return 0  # Read-only status, not release success.
