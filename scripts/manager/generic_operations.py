"""Model-agnostic P5-P8 source-only contracts.

Registered model IDs come from the service manifest, never from a hardcoded
Orcarouter/27B pair. This module never starts/stops containers, calls the API
for inference, executes a switch, or releases a service. Fake-DGX is entirely
in memory. Passing it cannot authorize any live operation.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import re
from typing import Any

from scripts.manager.service_manifest import policy
from scripts.manager.service_status import inspect_live_status

FAULTS = ("none", "target-start", "target-api", "restore-source")
_COMPONENTS = ("service", "proxy", "gateway", "storage")
_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def model_catalog(config: dict | None = None) -> dict:
    cfg = policy() if config is None else config
    if (cfg.get("max_active_gpu_models") != 1
            or cfg.get("api", {}).get("host_port") != 8000
            or cfg.get("transitions", {}).get("stop_old_before_start_new") is not True):
        raise ValueError("ONE_MODEL_PORT_OR_STOP_FIRST_POLICY_VIOLATION")
    entries = cfg.get("models")
    if not isinstance(entries, dict) or not entries:
        raise ValueError("EMPTY_OR_INVALID_MODEL_REGISTRY")
    models = {}
    containers = set()
    served_ids = set()
    for name, entry in sorted(entries.items()):
        if not isinstance(name, str) or not _NAME.fullmatch(name):
            raise ValueError("INVALID_MODEL_KEY")
        if not isinstance(entry, dict):
            raise ValueError("INVALID_MODEL_SPEC:" + name)
        checkpoint = entry.get("checkpoint")
        container = entry.get("container_name")
        proposed = entry.get("proposed_served_ids") or {}
        served = entry.get("served_id")
        provisional = False
        if served is None and isinstance(proposed, dict):
            candidate = proposed.get("mtp0")
            if not candidate and proposed:
                candidate = proposed[sorted(proposed)[0]]
            served = candidate
            provisional = served is not None
        if (not isinstance(checkpoint, str) or not checkpoint.strip()
                or not isinstance(container, str) or not container.strip()
                or not isinstance(served, str) or not served.strip()):
            raise ValueError("INCOMPLETE_MODEL_IDENTITY:" + name)
        if container in containers:
            raise ValueError("DUPLICATE_CANONICAL_CONTAINER")
        if served in served_ids:
            raise ValueError("DUPLICATE_API_SERVED_ID")
        containers.add(container)
        served_ids.add(served)
        models[name] = {
            "checkpoint": checkpoint, "container": container,
            "served_id": served, "served_id_provisional": provisional,
            "qualification": entry.get("qualification", "UNSPECIFIED"),
            "recipe_path": entry.get("runtime_recipe") or entry.get("source_recipe"),
        }
    return {
        "schema_version": 1, "stage": "common", "status": "SOURCE_CATALOG_ONLY",
        "models": models, "model_count": len(models),
        "api_port": 8000, "max_active_gpu_models": 1,
        "executed": False, "production_released": False,
    }


def _pair(catalog: dict, source: str, target: str) -> None:
    if source == target or source not in catalog["models"] or target not in catalog["models"]:
        raise ValueError("UNREGISTERED_OR_SAME_MODEL_PAIR")


def preflight(source: str, target: str, *, live: dict | None = None,
              config: dict | None = None) -> dict:
    """P6 inspect-only: always blocks execution, even with matching evidence."""
    catalog = model_catalog(config)
    _pair(catalog, source, target)
    observed = inspect_live_status() if live is None else live
    a, b = catalog["models"][source], catalog["models"][target]
    issues = []
    if observed.get("observed_model") != source:
        issues.append("SOURCE_MODEL_NOT_ACTIVE")
    if observed.get("status") not in ("LIVE_SERVICE_VERIFIED", "LIVE_P5_TRIAL_API_VERIFIED"):
        issues.append("SOURCE_LIVE_API_NOT_VERIFIED")
    if observed.get("expected_served_id") != a["served_id"]:
        issues.append("SOURCE_SERVED_ID_MISMATCH")
    container = observed.get("active_container") or {}
    if not isinstance(container, dict) or not container.get("name"):
        issues.append("SOURCE_CONTAINER_IDENTITY_NOT_OBSERVED")
    elif container["name"] != a["container"]:
        issues.append("SOURCE_NOT_CANONICAL_RUNTIME")
    if (observed.get("runtime_role") == "DEVELOPMENT_TRIAL"
            or observed.get("p5_development_trial") is True):
        issues.append("SOURCE_TRIAL_NOT_PROMOTED")
    if observed.get("gpu_exclusivity_verified") is not True:
        issues.append("GPU_EXCLUSIVITY_NOT_INDEPENDENTLY_VERIFIED")
    if observed.get("port_process_ownership_verified") is not True:
        issues.append("PORT_PROCESS_OWNERSHIP_UNVERIFIED")
    if b["served_id_provisional"] or b["qualification"] == "NOT_VERIFIED":
        issues.append("TARGET_CANONICAL_RUNTIME_NOT_QUALIFIED")
    issues += ["REAL_SWITCH_EXECUTOR_NOT_RELEASED",
               "BIDIRECTIONAL_DGX_ACCEPTANCE_NOT_VERIFIED",
               "REAL_FAULT_RECOVERY_ACCEPTANCE_NOT_VERIFIED"]
    return {
        "schema_version": 1, "stage": "p6", "action": "preflight",
        "scope": "MODEL_AGNOSTIC_SOURCE_ONLY", "status": "BLOCKED",
        "source_model": source, "target_model": target,
        "source_identity": a, "target_identity": b,
        "observed_service_status": observed.get("status"),
        "observed_runtime_role": observed.get("runtime_role"),
        "api_port": 8000, "max_active_gpu_models": 1,
        "requires_stop_before_start": True,
        "requires_exact_fresh_approval": True,
        "issues": sorted(set(issues)), "executed": False,
        "operations_enabled": False, "approval_accepted": False,
        "plan_id": None, "production_released": False,
    }


def simulate(source: str, target: str, *, fault: str = "none",
             config: dict | None = None) -> dict:
    """Model-independent deterministic Fake-DGX switch/restore journal."""
    cat = model_catalog(config)
    _pair(cat, source, target)
    if fault not in FAULTS:
        raise ValueError("UNSUPPORTED_FAULT")
    active: str | None = source
    port: str | None = source
    journal: list[dict] = []
    issues: list[str] = []
    def record(phase: str, action: str) -> None:
        owners = [] if active is None else [active]
        if len(owners) > 1 or active != port:
            issues.append("ONE_ACTIVE_MODEL_PORT_INVARIANT")
        journal.append({
            "phase": phase, "action": action, "active_models": owners,
            "port_8000_owner": port,
        })

    record("OBSERVED", "verify-source")
    active = port = None
    record("OLD_STOPPED", "stop-source-and-release-port")
    if fault == "target-start":
        record("NEW_STARTING", "target-start-failed")
    else:
        active = port = target
        record("NEW_STARTING", "start-target")
    if fault == "none":
        record("NEW_VERIFYING", "verify-target-api-id")
        record("COMMITTED", "append-success-journal")
        outcome = "PASS_FAKE_SWITCH"
    else:
        if fault in ("target-api", "restore-source"):
            record("NEW_VERIFYING", "target-api-id-mismatch")
        if active == target:
            active = port = None
            record("ROLLBACK_STARTING", "stop-failed-target")
        if fault == "restore-source":
            record("RECOVERY_FAILED", "source-restore-failed")
            outcome = "FAIL_FAKE_RECOVERY"
        else:
            active = port = source
            record("ROLLBACK_STARTING", "restore-source")
            record("RESTORED", "verify-source-api-id")
            outcome = "PASS_FAKE_RECOVERY"
    if issues:
        outcome = "FAIL_FAKE_INVARIANTS"
    return {
        "schema_version": 1, "stage": "p6" if fault == "none" else "p8",
        "scope": "IN_MEMORY_FAKE_DGX_ONLY", "status": outcome,
        "source_model": source, "target_model": target,
        "injected_fault": fault, "api_port": 8000,
        "journal": journal, "invariant_issues": issues,
        "final_active_model": active, "final_port_owner": port,
        "fake_executed": True, "executed": False,
        "operations_enabled": False, "approval_accepted": False,
        "plan_id": None, "production_released": False,
        "real_dgx_verified": False, "automatic_real_recovery_verified": False,
    }


def fault_matrix(*, config: dict | None = None) -> dict:
    """Every ordered registered model pair × four controlled fault scenarios."""
    cat = model_catalog(config)
    keys = sorted(cat["models"])
    cases = [simulate(a, b, fault=f, config=config)
             for a in keys for b in keys if a != b for f in FAULTS]
    expected = {
        "none": "PASS_FAKE_SWITCH",
        "target-start": "PASS_FAKE_RECOVERY",
        "target-api": "PASS_FAKE_RECOVERY",
        "restore-source": "FAIL_FAKE_RECOVERY",
    }
    complete = bool(cases) and all(
        item["status"] == expected[item["injected_fault"]]
        and not item["invariant_issues"]
        and item["final_active_model"] == (
            item["target_model"] if item["injected_fault"] == "none"
            else None if item["injected_fault"] == "restore-source"
            else item["source_model"])
        for item in cases
    )
    return {
        "schema_version": 1, "stage": "p8",
        "scope": "MODEL_AGNOSTIC_IN_MEMORY_FAKE_DGX_ONLY",
        "status": ("PASS_FAKE_DGX_EXPECTED_OUTCOMES" if complete
                   else "FAIL_FAKE_DGX"),
        "models": keys, "pair_count": len(keys) * max(0, len(keys) - 1),
        "test_count": len(cases), "cases": cases,
        "fake_executed": True, "executed": False,
        "real_dgx_verified": False, "production_released": False,
        "operations_enabled": False, "plan_id": None,
        "note": "Expected simulated failure is not a real recovery PASS.",
    }


def resource_review(model: str, telemetry: dict | None, benchmark: dict | None,
                    *, config: dict | None = None) -> dict:
    """P5 source-level observation/benchmark correlation, no performance PASS.

    Recompute interval counters from actual sample data instead of accepting
    untrusted summary flags. This catches changed container identity, unknown
    model provenance, stale or forged rate numbers and invalid float metrics.
    """
    cat = model_catalog(config)
    if model not in cat["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    doc = telemetry if isinstance(telemetry, dict) else {}
    bench = benchmark if isinstance(benchmark, dict) else {}
    issues = []
    if doc.get("model") != model:
        issues.append("RESOURCE_MODEL_IDENTITY_NOT_BOUND")
    raw_samples = doc.get("snapshots")
    from scripts.manager.resource_diagnostics import observation_summary
    if not isinstance(raw_samples, list) or len(raw_samples) < 2:
        computed = {"status": "NOT_OBSERVED"}
        issues.append("RESOURCE_SAMPLES_MISSING")
    elif not all(isinstance(row, dict) for row in raw_samples):
        computed = {"status": "UNSUPPORTED"}
        issues.append("RESOURCE_SAMPLES_INVALID")
    else:
        computed = observation_summary(raw_samples)
        if any(row.get("model") != model for row in raw_samples):
            issues.append("RESOURCE_SAMPLE_MODEL_IDENTITY_MISMATCH")
    supplied = doc.get("interval_summary") or {}
    if computed.get("status") != "OBSERVED_INTERVAL":
        issues.append("RESOURCE_INTERVAL_MISSING")
    elif supplied != computed:
        issues.append("RESOURCE_INTERVAL_SUMMARY_NOT_REPRODUCIBLE")
    if computed.get("cgroup_container_identity_continuous") is not True:
        issues.append("RESOURCE_CONTAINER_IDENTITY_NOT_CONTINUOUS")
    events = computed.get("cgroup_memory_event_deltas") or {}
    if any(not isinstance(events.get(k), int) for k in ("oom_delta", "oom_kill_delta")):
        issues.append("OOM_DELTAS_UNOBSERVED")
    elif events["oom_delta"] or events["oom_kill_delta"]:
        issues.append("OOM_EVENTS_OBSERVED")
    if bench.get("model") != model:
        issues.append("BENCHMARK_MODEL_IDENTITY_NOT_BOUND")
    ttft = bench.get("ttft_seconds")
    tps = bench.get("tokens_per_second")
    if (not isinstance(ttft, (int, float)) or isinstance(ttft, bool)
            or not math.isfinite(ttft) or ttft < 0):
        issues.append("BENCHMARK_TTFT_NOT_OBSERVED")
    if (not isinstance(tps, (int, float)) or isinstance(tps, bool)
            or not math.isfinite(tps) or tps <= 0):
        issues.append("BENCHMARK_THROUGHPUT_NOT_OBSERVED")
    return {
        "schema_version": 1, "stage": "p5",
        "status": "SOURCE_METRICS_PRESENT_NOT_LIVE_ACCEPTANCE" if not issues else "INCOMPLETE_EVIDENCE",
        "scope": "MODEL_AGNOSTIC_OBSERVATION_CORRELATION",
        "model": model, "interval_summary": computed,
        "benchmark_metrics": {"ttft_seconds": ttft, "tokens_per_second": tps},
        "issues": sorted(set(issues)), "executed": False,
        "production_released": False, "limits_changed": False,
        "note": "Metrics have no authentication or live workload acceptance. Thresholds require calibration.",
    }


def integration_review(model: str, components: dict | None, *,
                       config: dict | None = None) -> dict:
    """P7 source evidence contract; no local proxy/gateway health inferred."""
    cat = model_catalog(config)
    if model not in cat["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    supplied = components if isinstance(components, dict) else {}
    issues = []
    rows = {}
    for kind in _COMPONENTS:
        item = supplied.get(kind)
        verified = (isinstance(item, dict) and item.get("status") == "PASS"
                    and item.get("model") == model
                    and isinstance(item.get("evidence_id"), str)
                    and bool(item["evidence_id"].strip()))
        rows[kind] = {"evidence_supplied": verified}
        if not verified:
            issues.append(kind.upper() + "_MODEL_BOUND_EVIDENCE_MISSING")
    return {
        "schema_version": 1, "stage": "p7", "model": model,
        "status": "SOURCE_EVIDENCE_COMPLETE_NOT_RUNTIME_ACCEPTANCE" if not issues else "BLOCKED",
        "scope": "MODEL_AGNOSTIC_SOURCE_EVIDENCE_CONTRACT",
        "components": rows, "issues": issues,
        "executed": False, "operations_enabled": False,
        "production_released": False, "real_dgx_verified": False,
    }


def _load_evidence(path: str | None) -> dict | None:
    if path is None:
        return None
    candidate = Path(path)
    if not candidate.is_absolute() or candidate.is_symlink():
        raise ValueError("EVIDENCE_PATH_MUST_BE_ABSOLUTE_REGULAR_FILE")
    if not candidate.is_file() or candidate.stat().st_size > 1024 * 1024:
        raise ValueError("EVIDENCE_FILE_MISSING_OR_TOO_LARGE")
    document = json.loads(candidate.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("EVIDENCE_MUST_BE_JSON_OBJECT")
    return document


def fault_matrix_summary(document: dict) -> dict:
    """Compact presentation of a *completed* synthetic matrix.

    Never changes the scenario evaluation, operation or release flags. Full
    journals remain available without --summary-only; this is not evidence.
    """
    cases = document["cases"]
    counts = {status: sum(row["status"] == status for row in cases)
              for status in sorted(set(row["status"] for row in cases))}
    fault_counts = {fault: sum(row["injected_fault"] == fault for row in cases)
                    for fault in FAULTS}
    return {
        "schema_version": document["schema_version"],
        "stage": document["stage"], "scope": document["scope"],
        "status": document["status"], "models": document["models"],
        "pair_count": document["pair_count"],
        "test_count": document["test_count"],
        "status_counts": counts,
        "fault_counts": fault_counts,
        "invariant_violation_cases": sum(bool(row["invariant_issues"])
                                         for row in cases),
        "executed": False, "fake_executed": True,
        "operations_enabled": False, "real_dgx_verified": False,
        "production_released": False, "plan_id": None,
        "summary_only": True,
        "full_journals_omitted": True,
        "note": "In-memory test only. Omitted journals are not missing execution evidence.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Model-agnostic source-only P5-P8")
    parser.add_argument("action", choices=(
        "catalog", "preflight", "simulate", "fault-matrix",
        "resource-review", "integration", "session-plan", "session-review",
        "transaction-simulate", "extended-fault-matrix", "integration-reconcile",
        "session-mock", "session-matrix", "pipeline-mock",
        "fake-disk-contract", "fake-disk-matrix",
        "observation-review", "observation-capture", "operating-gate-review",
        "ownership-review", "ownership-capture", "journal-v2-preview"))
    parser.add_argument("--from-model")
    parser.add_argument("--to-model")
    parser.add_argument("--model")
    parser.add_argument("--fault", choices=FAULTS, default="none")
    parser.add_argument("--extended-fault", default="none")
    parser.add_argument("--mock-fault", default="none")
    parser.add_argument("--mock-disk-scenario", default="none")
    parser.add_argument("--resource-evidence")
    parser.add_argument("--benchmark-evidence")
    parser.add_argument("--component-evidence")
    parser.add_argument("--ownership-evidence")
    parser.add_argument("--service-evidence")
    parser.add_argument("--operating-journal-evidence")
    parser.add_argument("--approval-evidence")
    parser.add_argument("--source-container-id")
    parser.add_argument("--target-container-id")
    parser.add_argument("--review-now-utc")
    parser.add_argument("--session-resource-evidence")
    parser.add_argument("--session-benchmark-evidence")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-only", action="store_true",
                        help="fault-matrix concise output; all cases still evaluated")
    args = parser.parse_args(argv)
    try:
        if args.summary_only and args.action not in ("fault-matrix", "extended-fault-matrix", "session-matrix", "fake-disk-matrix"):
            raise ValueError("SUMMARY_ONLY_SUPPORTED_FOR_FAULT_MATRIX")
        if args.action == "catalog":
            result = model_catalog()

        elif args.action in ("ownership-review", "ownership-capture"):
            if not args.model:
                raise ValueError("EXACT_MODEL_REQUIRED")
            from scripts.manager.process_ownership import ownership_capture, ownership_review
            if args.action == "ownership-capture":
                result = ownership_capture(args.model)
            else:
                bundle = _load_evidence(args.ownership_evidence) or {}
                result = ownership_review(
                    args.model, bundle.get("observation"),
                    bundle.get("docker_inspect"),
                    bundle.get("docker_top_stdout"),
                    bundle.get("ss_stdout"),
                    bundle.get("gpu_stdout"))
        elif args.action == "journal-v2-preview":
            if not args.from_model or not args.to_model:
                raise ValueError("EXACT_SOURCE_AND_TARGET_REQUIRED")
            from scripts.manager.generic_journal_v2 import migration_preview
            result = migration_preview(
                args.from_model, args.to_model,
                _load_evidence(args.operating_journal_evidence))
        elif args.action in ("observation-review", "observation-capture"):
            if not args.model:
                raise ValueError("EXACT_MODEL_REQUIRED")
            from scripts.manager.observation_binding import (
                observation_capture, observation_review)
            result = (observation_capture(args.model)
                      if args.action == "observation-capture"
                      else observation_review(
                          args.model, _load_evidence(args.service_evidence),
                          _load_evidence(args.resource_evidence)))
        elif args.action == "operating-gate-review":
            if not args.from_model or not args.to_model:
                raise ValueError("EXACT_SOURCE_AND_TARGET_REQUIRED")
            from scripts.manager.generic_operating_gate import gate_review
            result = gate_review(
                args.from_model, args.to_model,
                _load_evidence(args.service_evidence),
                args.source_container_id, args.target_container_id,
                _load_evidence(args.operating_journal_evidence),
                _load_evidence(args.approval_evidence),
                now_utc=args.review_now_utc)
        elif args.action == "session-mock":
            if not args.model:
                raise ValueError("EXACT_MODEL_REQUIRED")
            from scripts.manager.mock_benchmark_session import mock_session
            result = mock_session(args.model, fault=args.mock_fault)
        elif args.action == "session-matrix":
            from scripts.manager.mock_benchmark_session import mock_session_matrix
            result = mock_session_matrix(summary_only=args.summary_only)
        elif args.action == "fake-disk-matrix":
            from scripts.manager.mock_persistent_contract import fake_disk_matrix
            result = fake_disk_matrix()
            if args.summary_only:
                result.pop("cases")
                result["summary_only"] = True
                result["full_cases_omitted"] = True
        elif args.action == "fake-disk-contract":
            if not args.from_model or not args.to_model:
                raise ValueError("EXACT_SOURCE_AND_TARGET_REQUIRED")
            from scripts.manager.mock_persistent_contract import fake_disk_contract
            result = fake_disk_contract(args.from_model, args.to_model,
                                        scenario=args.mock_disk_scenario)
        elif args.action == "pipeline-mock":
            if not args.from_model or not args.to_model:
                raise ValueError("EXACT_SOURCE_AND_TARGET_REQUIRED")
            from scripts.manager.mock_transaction_pipeline import mock_pipeline
            result = mock_pipeline(args.from_model, args.to_model,
                                   fault=args.extended_fault)
        elif args.action == "fault-matrix":
            result = fault_matrix()
            if args.summary_only:
                result = fault_matrix_summary(result)
        elif args.action in ("transaction-simulate", "extended-fault-matrix"):
            from scripts.manager.transition_safety import simulate_transaction, extended_fault_matrix
            if args.action == "extended-fault-matrix":
                result = extended_fault_matrix()
                if args.summary_only:
                    cases = result.pop("cases")
                    result["summary_only"] = True
                    result["full_journals_omitted"] = True
                    result["status_counts"] = {
                        status: sum(c["status"] == status for c in cases)
                        for status in sorted({c["status"] for c in cases})}
                    result["fault_counts"] = {
                        fault: sum(c["injected_fault"] == fault for c in cases)
                        for fault in sorted({c["injected_fault"] for c in cases})}
            else:
                if not args.from_model or not args.to_model:
                    raise ValueError("EXACT_SOURCE_AND_TARGET_REQUIRED")
                result = simulate_transaction(args.from_model, args.to_model,
                                              fault=args.extended_fault)
        elif args.action in ("preflight", "simulate"):
            if not args.from_model or not args.to_model:
                raise ValueError("EXACT_SOURCE_AND_TARGET_REQUIRED")
            result = (preflight(args.from_model, args.to_model)
                      if args.action == "preflight"
                      else simulate(args.from_model, args.to_model,
                                    fault=args.fault))
        elif args.action in ("session-plan", "session-review"):
            if not args.model:
                raise ValueError("EXACT_MODEL_REQUIRED")
            from scripts.manager.benchmark_session import session_plan, session_review
            result = (session_plan(args.model) if args.action == "session-plan"
                      else session_review(args.model,
                          _load_evidence(args.session_resource_evidence),
                          _load_evidence(args.session_benchmark_evidence)))
        elif args.action == "integration-reconcile":
            if not args.model:
                raise ValueError("EXACT_MODEL_REQUIRED")
            from scripts.manager.integration_contract import integration_reconcile
            result = integration_reconcile(args.model, _load_evidence(args.component_evidence))
        elif args.action == "resource-review":
            if not args.model:
                raise ValueError("EXACT_MODEL_REQUIRED")
            result = resource_review(
                args.model, _load_evidence(args.resource_evidence),
                _load_evidence(args.benchmark_evidence))
        else:
            if not args.model:
                raise ValueError("EXACT_MODEL_REQUIRED")
            result = integration_review(
                args.model, _load_evidence(args.component_evidence))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as error:
        result = {
            "status": "BLOCKED", "issues": [str(error)],
            "executed": False, "production_released": False,
            "operations_enabled": False,
        }
    print(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if result["status"] in (
        "SOURCE_CATALOG_ONLY", "PASS_FAKE_SWITCH",
        "PASS_FAKE_RECOVERY", "PASS_FAKE_DGX_EXPECTED_OUTCOMES",
        "SOURCE_METRICS_PRESENT_NOT_LIVE_ACCEPTANCE",
        "SOURCE_SESSION_CORRELATED_NOT_LIVE_ACCEPTANCE",
        "PASS_FAKE_P5_SESSION", "PASS_FAKE_P5_FAULT_BLOCKED",
        "PASS_FAKE_PIPELINE_CONTRACT",
        "PASS_FAKE_DISK_CONTRACT", "PASS_FAKE_DISK_FAILURE_DETECTED",
        "SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE",
        "OBSERVED_PID_SETS_CONSISTENT_NOT_AUTHORIZED",
        "SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED",
        "SOURCE_EVIDENCE_COMPLETE_NOT_RUNTIME_ACCEPTANCE",
    ) else 3


if __name__ == "__main__":
    raise SystemExit(main())
