"""P5 coordinated *synthetic* workload/resource timelines (NO host I/O).

The only provider in this module is an exact in-memory fixture.  API identity
flags, request measurements and Docker IDs here are invented MOCK values and
are NEVER accepted as real DGX or production qualification.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json

from scripts.manager.benchmark_session import session_review
from scripts.manager.generic_operations import model_catalog

FAULTS = (
    "none", "sampler-missing", "container-drift", "api-identity",
    "clock-drift", "request-failure", "oom",
)


def _hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def mock_session(model: str, *, fault: str = "none", config: dict | None = None) -> dict:
    """Coordinate pre/post samples around a fake request window.

    The time values, service identity and measurements are fixed fixtures;
    neither the operating resource observer nor an inference client is called.
    """
    catalog = model_catalog(config)
    if model not in catalog["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    if fault not in FAULTS:
        raise ValueError("UNSUPPORTED_P5_MOCK_FAULT")
    identity = catalog["models"][model]
    profile = {"kind": "FAKE_DGX_CPU_ONLY", "requests": 3,
               "max_tokens": 32, "concurrency": 1, "stream": True}
    digest = _hash(profile)
    sid = _hash(["p5-mock", model, fault, digest])[:32]
    cid = _hash(["mock-container", model])
    fixture_start = "2026-11-09T00:00:00+00:00"
    fixture_end = "2026-11-09T00:00:10+00:00"
    events = []

    def event(action: str) -> None:
        events.append({"index": len(events), "action": action,
                       "origin": "SYNTHETIC_FIXTURE_NO_IO"})

    def sample(timestamp: str, monotonic: int, *, last: bool) -> dict:
        return {
            "model": model, "timestamp_utc": timestamp, "monotonic_ns": monotonic,
            "model_identity_verified_by_api": not (last and fault == "api-identity"),
            "measurement_origin": "SYNTHETIC_FIXTURE_NOT_LIVE",
            "docker": {
                "container": {
                    "id": ("f" * 64 if last and fault == "container-drift" else cid),
                    "name": identity["container"],
                },
                "cgroup_v2": {"metrics": {
                    "memory.events": {
                        "oom": 1 if last and fault == "oom" else 0,
                        "oom_kill": 0,
                    },
                }},
            },
        }

    event("sample-before")
    snapshots = [sample(fixture_start, 1_000_000_000, last=False)]
    event("benchmark-start")
    event("mock-requests")
    event("benchmark-end")
    event("sample-after")
    if fault != "sampler-missing":
        snapshots.append(sample(
            fixture_end,
            2_000_000_000 if fault == "clock-drift" else 11_000_000_000,
            last=True))
    bench = {
        "model": model, "session_id": sid, "profile_sha256": digest,
        "checkpoint": identity["checkpoint"], "served_id": identity["served_id"],
        "container_id": cid, "started_utc": "2026-11-09T00:00:02+00:00",
        "ended_utc": "2026-11-09T00:00:08+00:00",
        "started_monotonic_ns": 3_000_000_000,
        "ended_monotonic_ns": 9_000_000_000,
        "requests": 3,
        "successes": 2 if fault == "request-failure" else 3,
        "failures": 1 if fault == "request-failure" else 0,
        "error_rate": 1 / 3 if fault == "request-failure" else 0.0,
        "metrics": {"ttft_p50_seconds": 0.2,
                    "ttft_p95_seconds": 0.4,
                    "tokens_per_second": 12.5},
        "measurement_origin": "SYNTHETIC_FIXTURE_NOT_LIVE",
    }
    resource = {
        "model": model, "session_id": sid, "profile_sha256": digest,
        "checkpoint": identity["checkpoint"], "served_id": identity["served_id"],
        "container_id": cid, "snapshots": snapshots,
        "measurement_origin": "SYNTHETIC_FIXTURE_NOT_LIVE",
    }
    review = session_review(model, resource, bench, config=config)
    expected_ok = fault == "none"
    consistent = review["status"] == "SOURCE_SESSION_CORRELATED_NOT_LIVE_ACCEPTANCE"
    # Unexpected successful correlation of an injected fault is a regression.
    status = ("PASS_FAKE_P5_SESSION" if expected_ok and consistent
              else "PASS_FAKE_P5_FAULT_BLOCKED" if not expected_ok and not consistent
              else "FAIL_FAKE_P5_CONTRACT")
    return {
        "schema_version": 1, "stage": "p5", "action": "session-mock",
        "scope": "EXACT_IN_MEMORY_SYNTHETIC_SESSION_ONLY",
        "model": model, "injected_fault": fault, "status": status,
        "session_id": sid, "profile_sha256": digest, "api_port": 8000,
        "events": events, "review": review, "resource_evidence": resource,
        "benchmark_evidence": bench,
        "synthetic": True, "fake_executed": True, "executed": False,
        "real_dgx_verified": False, "benchmark_verified": False,
        "approval_accepted": False, "operations_enabled": False,
        "production_released": False,
        "note": "Synthetic metrics and identity claims; no API, Docker, GPU, disk, or workload I/O.",
    }


def mock_session_matrix(*, config: dict | None = None, summary_only: bool = False) -> dict:
    names = sorted(model_catalog(config)["models"])
    cases = [mock_session(model, fault=fault, config=config)
             for model in names for fault in FAULTS]
    expected = {"PASS_FAKE_P5_SESSION", "PASS_FAKE_P5_FAULT_BLOCKED"}
    passed = all(case["status"] in expected and
                 case["review"]["real_dgx_verified"] is False and
                 case["executed"] is False and
                 case["production_released"] is False for case in cases)
    result = {
        "schema_version": 1, "stage": "p5", "action": "session-matrix",
        "scope": "MODEL_AGNOSTIC_FAKE_DGX_SESSION_MATRIX",
        "status": "PASS_FAKE_DGX_EXPECTED_OUTCOMES" if passed else "FAIL_FAKE_DGX",
        "models": names, "test_count": len(cases),
        "fault_count": len(FAULTS),
        "status_counts": dict(sorted(Counter(x["status"] for x in cases).items())),
        "fault_counts": {f: len(names) for f in FAULTS},
        "executed": False, "fake_executed": True,
        "real_dgx_verified": False, "operations_enabled": False,
        "production_released": False,
    }
    if summary_only:
        result["summary_only"] = True
        result["full_cases_omitted"] = True
    else:
        result["cases"] = cases
    return result
