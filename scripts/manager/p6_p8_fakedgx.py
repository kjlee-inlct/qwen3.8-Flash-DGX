"""P6 switch safety preview and P6/P8 deterministic Fake-DGX contracts.

All simulations are in-memory. They never call Docker, GPU, HTTP, filesystem
mutators or the real transition executor. No execution plan or approval token
is produced, even when a fake scenario passes.
"""
from __future__ import annotations

import argparse
import json
from typing import Any

from scripts.manager.service_manifest import policy
from scripts.manager.service_status import inspect_live_status

DIRECTIONS = (("orcarouter", "27b"), ("27b", "orcarouter"))
FAULTS = ("none", "target-start", "target-api", "restore-source")


def _ids(models: dict, name: str) -> dict:
    spec = models[name]
    return {
        "checkpoint": spec["checkpoint"],
        "container": spec["container_name"],
        "served_id": (spec.get("served_id") or
                      spec.get("proposed_served_ids", {}).get("mtp0")),
    }


def preflight(source: str, target: str, *, live: dict[str, Any] | None = None,
              service_policy: dict | None = None) -> dict:
    """Inspect current API identity and desired manifest, never authorize a switch."""
    config = policy() if service_policy is None else service_policy
    models = config["models"]
    if (source, target) not in DIRECTIONS:
        raise ValueError("P6_UNSUPPORTED_DIRECTION")
    if config["max_active_gpu_models"] != 1 or config["api"]["host_port"] != 8000:
        raise ValueError("P6_POLICY_INVARIANT_FAILED")
    observed = inspect_live_status() if live is None else live
    issues = []
    status = observed.get("status")
    source_id = _ids(models, source)
    target_id = _ids(models, target)
    if observed.get("observed_model") != source:
        issues.append("SOURCE_MODEL_NOT_ACTIVE")
    if status not in ("LIVE_SERVICE_VERIFIED", "LIVE_P5_TRIAL_API_VERIFIED"):
        issues.append("SOURCE_LIVE_API_NOT_VERIFIED")
    if observed.get("expected_served_id") != source_id["served_id"]:
        issues.append("SOURCE_SERVED_ID_MISMATCH")
    container = observed.get("active_container") or {}
    if not isinstance(container, dict) or not container.get("name"):
        issues.append("SOURCE_CONTAINER_IDENTITY_NOT_OBSERVED")
    elif (container.get("name") != source_id["container"]
          or observed.get("runtime_role") == "DEVELOPMENT_TRIAL"):
        issues.append("SOURCE_NOT_CANONICAL_RUNTIME")
    if observed.get("gpu_exclusivity_verified") is not True:
        issues.append("GPU_EXCLUSIVITY_NOT_INDEPENDENTLY_VERIFIED")
    if observed.get("port_process_ownership_verified") is not True:
        issues.append("PORT_PROCESS_OWNERSHIP_UNVERIFIED")
    if source == "orcarouter" and observed.get("p5_development_trial") is True:
        issues.append("ORCAROUTER_MTP0_TRIAL_NOT_PROMOTED")
    if target == "orcarouter":
        issues.append("ORCAROUTER_CANONICAL_IMAGE_NOT_QUALIFIED")
    # A source-only dry run cannot prove a fresh target load, benchmarks,
    # authentic rollback, journal commit or model identity after re-launch.
    issues.extend(("TARGET_RUNTIME_SWITCH_NOT_QUALIFIED",
                   "P6_BIDIRECTIONAL_DGX_ACCEPTANCE_NOT_RUN",
                   "P8_FAULT_RECOVERY_SEPARATELY_UNRELEASED"))
    return {
        "schema_version": 1, "stage": "p6", "action": "preflight",
        "status": "BLOCKED", "source_model": source, "target_model": target,
        "source_identity": source_id, "target_identity": target_id,
        "observed_service_status": status,
        "observed_runtime_role": observed.get("runtime_role"),
        "api_port": 8000, "max_active_gpu_models": 1,
        "requires_stop_before_start": True, "requires_exact_fresh_approval": True,
        "requires_live_rollback_qualification": True,
        "issues": sorted(set(issues)), "executed": False,
        "operations_enabled": False, "approval_accepted": False,
        "plan_id": None, "production_released": False,
    }


def simulate(source: str, target: str, *, fault: str = "none") -> dict:
    """Exercise a deliberately *fake* service/port state machine only."""
    if (source, target) not in DIRECTIONS:
        raise ValueError("P6_UNSUPPORTED_DIRECTION")
    if fault not in FAULTS:
        raise ValueError("P6_UNSUPPORTED_FAULT")
    owner: str | None = source
    port_owner: str | None = source
    journal = []
    invariants = []
    def record(phase: str, action: str) -> None:
        active = [] if owner is None else [owner]
        if len(active) > 1 or port_owner != owner:
            invariants.append("ONE_MODEL_OR_PORT_INVARIANT_VIOLATION")
        journal.append({"phase": phase, "action": action,
                        "active_models": active, "port_8000_owner": port_owner})
    record("OBSERVED", "verify-source")
    owner = port_owner = None
    record("OLD_STOPPED", "stop-source-and-release-port")
    if fault != "target-start":
        owner = port_owner = target
        record("NEW_STARTING", "start-target")
    else:
        record("NEW_STARTING", "target-start-failed")
    if fault == "none":
        record("NEW_VERIFYING", "verify-target-api-id")
        record("COMMITTED", "append-success-journal")
        outcome = "PASS_FAKE_SWITCH"
    else:
        if fault == "target-api":
            record("NEW_VERIFYING", "target-api-id-mismatch")
        if owner == target:
            owner = port_owner = None
            record("ROLLBACK_STARTING", "stop-failed-target")
        if fault == "restore-source":
            record("RECOVERY_FAILED", "source-restore-failed")
            outcome = "FAIL_FAKE_RECOVERY"
        else:
            owner = port_owner = source
            record("ROLLBACK_STARTING", "restore-source")
            record("RESTORED", "verify-source-api-id")
            outcome = "PASS_FAKE_RECOVERY"
    if invariants:
        outcome = "FAIL_FAKE_INVARIANTS"
    return {
        "schema_version": 1, "stage": "p6" if fault == "none" else "p8",
        "scope": "IN_MEMORY_FAKE_DGX_ONLY",
        "status": outcome, "source_model": source, "target_model": target,
        "injected_fault": fault, "api_port": 8000,
        "journal": journal, "invariant_issues": invariants,
        "final_active_model": owner, "final_port_owner": port_owner,
        "fake_executed": True, "executed": False,
        "operations_enabled": False, "approval_accepted": False,
        "plan_id": None, "production_released": False,
        "real_dgx_verified": False, "automatic_real_recovery_verified": False,
    }


def fault_matrix() -> dict:
    """Run two directions plus bounded failure cases without touching a device."""
    cases = [simulate(source, target, fault=fault)
             for source, target in DIRECTIONS
             for fault in FAULTS]
    expected = {"none": "PASS_FAKE_SWITCH",
                "target-start": "PASS_FAKE_RECOVERY",
                "target-api": "PASS_FAKE_RECOVERY",
                "restore-source": "FAIL_FAKE_RECOVERY"}
    correct = all(
        case["status"] == expected[case["injected_fault"]]
        and not case["invariant_issues"]
        and case["final_active_model"] == (
            None if case["injected_fault"] == "restore-source" else
            case["target_model"] if case["injected_fault"] == "none" else
            case["source_model"])
        for case in cases)
    return {
        "schema_version": 1, "stage": "p8",
        "status": "PASS_FAKE_DGX_EXPECTED_OUTCOMES" if correct else "FAIL_FAKE_DGX",
        "test_count": len(cases), "cases": cases,
        "fake_executed": True, "executed": False,
        "real_dgx_verified": False, "production_released": False,
        "operations_enabled": False, "plan_id": None,
        "note": "Pure synthetic state machine, not the real runtime executor or fault-recovery acceptance.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P6 read-only and Fake-DGX checks")
    parser.add_argument("action", choices=("preflight", "simulate", "fault-matrix"))
    parser.add_argument("--from-model", choices=("orcarouter", "27b"))
    parser.add_argument("--to-model", choices=("orcarouter", "27b"))
    parser.add_argument("--fault", choices=FAULTS, default="none")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "fault-matrix":
            if args.from_model or args.to_model or args.fault != "none":
                raise ValueError("P8_FAULT_MATRIX_FIXED_SCENARIOS_ONLY")
            doc = fault_matrix()
        elif args.action == "preflight":
            observed = inspect_live_status()
            source = args.from_model or observed.get("observed_model")
            if source not in ("orcarouter", "27b") or args.to_model is None:
                raise ValueError("P6_EXACT_SOURCE_AND_TARGET_REQUIRED")
            doc = preflight(source, args.to_model, live=observed)
        else:
            if args.from_model is None or args.to_model is None:
                raise ValueError("P6_EXACT_SOURCE_AND_TARGET_REQUIRED")
            doc = simulate(args.from_model, args.to_model, fault=args.fault)
    except (ValueError, KeyError, TypeError) as exc:
        doc = {"stage": "p6", "status": "BLOCKED", "executed": False,
               "operations_enabled": False, "plan_id": None,
               "issues": [str(exc)]}
    print(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if doc["status"].startswith("PASS_FAKE") else 3


if __name__ == "__main__":
    raise SystemExit(main())
