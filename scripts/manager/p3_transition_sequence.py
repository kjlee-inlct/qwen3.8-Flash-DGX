"""P3 model switching sequence: strictly read-only manual-entry gate.

P2 completion MUST NOT launch P3. Once a separately approved P3 begins,
the intended order is: 27B active -> Flash-Next active -> finish P1
remediation/benchmark -> 27B active. No persistent switch executor is
implemented here; no plan ID is issued, and no GPU or Docker mutation.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from scripts.manager.service_status import inspect_live_status
from scripts.manager.p3_27b_roundtrip import latest_p2_benchmark

SCHEMA = 1
PHASES = (
    {"phase": "P3_ENTRY", "required_observed_model": "flash-next",
     "action": "manually-approve-p3", "gate": "P2_BENCH_PASS_AND_SEPARATE_P3_APPROVAL",
     "description": "P2 completes, restores original Flash-Next, and stops. Do not enter P3 automatically."},
    {"phase": "P3_ACTIVATE_27B", "required_observed_model": "flash-next",
     "action": "switch-flash-next-to-27b",
     "gate": "FRESH_TRANSITION_APPROVAL_AND_VERIFIED_27B_SERVICE",
     "description": "Explicitly establish 27B as the source model for testing the return to Flash-Next."},
    {"phase": "P3_RETURN_TO_FLASH_NEXT", "required_observed_model": "27b",
     "action": "switch-27b-to-flash-next",
     "gate": "FRESH_TRANSITION_APPROVAL_AND_VERIFIED_FLASH_NEXT_SERVICE",
     "description": "Switch 27B to Flash-Next; verify exact :8000 model ID and fallback readiness."},
    {"phase": "P1_REMEDIATION_AND_REBENCHMARK", "required_observed_model": "flash-next",
     "action": "audit-fix-and-benchmark-p1",
     "gate": "P1_GAP_CLOSURE_AND_ACTUAL_BENCHMARK_EVIDENCE",
     "description": "Resolve P1 shortcomings and gather real Flash-Next benchmark measurements before another switch."},
    {"phase": "P3_FINAL_27B", "required_observed_model": "flash-next",
     "action": "switch-flash-next-to-27b",
     "gate": "FRESH_FINAL_APPROVAL_AND_VERIFIED_27B_SERVICE",
     "description": "Finally switch back to 27B and verify the intended final active model; do not auto-run."},
)

P1_OPEN_CHECKS = (
    "Reconcile historical P1 doctor/inventory-plan nonzero results using real evidence",
    "Verify original Flash-Next functional/API probes still pass after 27B->Flash-Next switch",
    "Capture real Flash-Next latency, TTFT and token throughput in a newly approved benchmark",
    "Record actual measurement values and evidence; do not infer metrics from prior PASS labels",
    "Verify current API model ID and original service/rollback readiness before final 27B switch",
)


def plan(*, receipt_reader: Callable[..., tuple[dict | None, str | None]] = latest_p2_benchmark,
         service_inspector: Callable[..., dict[str, Any]] = inspect_live_status) -> dict[str, Any]:
    try:
        receipt, issue = receipt_reader()
    except (OSError, RuntimeError, ValueError, TypeError):
        receipt, issue = None, "P2_BENCHMARK_RECEIPT_UNAVAILABLE"
    try:
        service = service_inspector()
    except (OSError, RuntimeError, ValueError, TypeError):
        service = {"status": "BLOCKED", "observed_model": None,
                   "issues": ["P3_READ_ONLY_SERVICE_OBSERVATION_UNAVAILABLE"]}
    issues = []
    if issue:
        issues.append(issue)
    if service.get("status") != "LIVE_SERVICE_VERIFIED":
        issues.append("LIVE_SERVICE_STATE_UNVERIFIED")
    if service.get("observed_model") != "flash-next":
        issues.append("P2_MUST_RESTORE_FLASH_NEXT_BEFORE_SEPARATE_P3_ENTRY")
    if service.get("expected_served_id") != "qwen3.8-flash-next":
        issues.append("FLASH_NEXT_API_IDENTITY_NOT_VERIFIED")
    if service.get("issues"):
        issues.extend(str(v) for v in service["issues"])
    # Even after P2 passes the operator must explicitly enter P3. A plan is
    # not entry, execution authorization or an action to change models.
    if not issues:
        issues.append("P3_SEPARATE_OPERATOR_ENTRY_REQUIRED")
    return {
        "schema_version": SCHEMA, "stage": "p3", "action": "sequence-plan",
        "status": "BLOCKED", "executed": False, "operations_enabled": False,
        "approval_accepted": False, "plan_id": None,
        "automatic_progression_from_p2": False,
        "p2_benchmark_receipt_present": receipt is not None,
        "p2_benchmark_receipt": receipt,
        "current_api_status": service.get("status"),
        "current_observed_model": service.get("observed_model"),
        "intended_final_model": "27b",
        "source_stage": "P2", "next_stage": "P3",
        "p3_entries_require_new_explicit_approval": True,
        "permanent_switch_executor_ready": False,
        "p1_remediation_and_rebenchmark_required": True,
        "phases": list(PHASES),
        "p1_open_checks": list(P1_OPEN_CHECKS),
        "issues": sorted(set(issues)),
        "notice": ("P2 completion is a stop point, never an automatic P3 trigger. "
                   "Old two-roundtrip script is retired. The sequence is "
                   "27B->Flash-Next, P1 gap closure and benchmark, then 27B. "
                   "No persistent switch executor or live service operation is authorized."),
    }


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Read-only P3 manual-entry sequence")
    parser.add_argument("mode", choices=("plan",), nargs="?", default="plan")
    args = parser.parse_args(argv)
    doc = plan()
    print(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True))
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
