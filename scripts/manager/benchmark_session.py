"""P5 model-agnostic benchmark/resource session evidence contract (source only).

This is a verifier and read-only planning interface, NOT a benchmark runner.
No workload, Docker operation, GPU access, or admission action is performed.
External evidence is never treated as authenticated simply because it parses.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
import re

from scripts.manager.generic_operations import model_catalog
from scripts.manager.resource_diagnostics import observation_summary

_SESSION = re.compile(r"^[0-9a-f]{32}$")
_SHA = re.compile(r"^[0-9a-f]{64}$")


def _utc(value):
    if not isinstance(value, str):
        return None
    try:
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return stamp if stamp.tzinfo is not None and stamp.utcoffset() is not None else None


def _number(value, *, positive=False):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and (value > 0 if positive else value >= 0))


def _ns(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def session_plan(model: str, *, config: dict | None = None) -> dict:
    """Registry-derived, non-authorizing plan with no invented benchmark settings."""
    catalog = model_catalog(config)
    if model not in catalog["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    identity = catalog["models"][model]
    payload = {"model": model, "checkpoint": identity["checkpoint"],
               "served_id": identity["served_id"],
               "container": identity["container"],
               "recipe_path": identity["recipe_path"], "port": 8000}
    fingerprint = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema_version": 1, "stage": "p5", "action": "session-plan",
        "scope": "SOURCE_ONLY_NO_BENCHMARK_EXECUTOR",
        "status": "BLOCKED_WORKLOAD_PROFILE_AND_APPROVAL_REQUIRED",
        "model": model, "identity": identity, "api_port": 8000,
        "identity_fingerprint": fingerprint,
        "required_evidence": [
            "session_id", "profile_sha256", "checkpoint", "served_id",
            "container_id", "UTC_and_monotonic_benchmark_window",
            "same_window_resource_snapshots", "request_metrics",
            "independent_API_and_Docker_identity_verification"],
        "issues": ["NO_VERIFIED_COMMON_WORKLOAD_EXECUTOR",
                   "NO_FRESH_BENCHMARK_OPERATOR_APPROVAL"],
        "executed": False, "approval_accepted": False,
        "operations_enabled": False, "production_released": False,
    }


def session_review(model: str, resource: dict | None, benchmark: dict | None,
                   *, config: dict | None = None) -> dict:
    """Cross-check resource and benchmark windows, metrics and identity.

    The review is intentionally not cryptographic provenance validation; a
    manually authored PASS field or a matching timestamp is not live evidence.
    """
    cat = model_catalog(config)
    if model not in cat["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    identity = cat["models"][model]
    res = resource if isinstance(resource, dict) else {}
    bench = benchmark if isinstance(benchmark, dict) else {}
    issues = []

    sid = bench.get("session_id")
    if not isinstance(sid, str) or not _SESSION.fullmatch(sid) or res.get("session_id") != sid:
        issues.append("SESSION_ID_UNBOUND")
    digest = bench.get("profile_sha256")
    if not isinstance(digest, str) or not _SHA.fullmatch(digest) or res.get("profile_sha256") != digest:
        issues.append("WORKLOAD_PROFILE_HASH_UNBOUND")

    for field, expected in (("model", model), ("checkpoint", identity["checkpoint"]),
                            ("served_id", identity["served_id"])):
        if bench.get(field) != expected or res.get(field) != expected:
            issues.append(field.upper() + "_IDENTITY_UNBOUND")

    container_id = bench.get("container_id")
    if not isinstance(container_id, str) or not _SHA.fullmatch(container_id):
        issues.append("BENCHMARK_CONTAINER_ID_UNOBSERVED")
    if res.get("container_id") != container_id:
        issues.append("SESSION_CONTAINER_ID_UNBOUND")

    snapshots = res.get("snapshots")
    if not isinstance(snapshots, list) or len(snapshots) < 2 or not all(
            isinstance(row, dict) for row in snapshots):
        issues.append("RESOURCE_SNAPSHOTS_INSUFFICIENT")
        snapshots = []
        interval = {"status": "NOT_OBSERVED"}
    else:
        interval = observation_summary(snapshots)
        if interval.get("status") != "OBSERVED_INTERVAL":
            issues.append("RESOURCE_INTERVAL_INVALID")
        if interval.get("cgroup_container_identity_continuous") is not True:
            issues.append("CONTAINER_IDENTITY_DRIFT_OR_UNOBSERVED")
        for row in snapshots:
            observed_id = ((row.get("docker") or {}).get("container") or {}).get("id")
            if row.get("model") != model or observed_id != container_id:
                issues.append("SAMPLE_IDENTITY_DRIFT")
            if row.get("model_identity_verified_by_api") is not True:
                issues.append("API_IDENTITY_NOT_INDEPENDENTLY_VERIFIED")

    # Each window must have BOTH UTC and monotonic timing, and samples must
    # bracket the actual request interval; overlapping is not sufficient.
    bs, be = _utc(bench.get("started_utc")), _utc(bench.get("ended_utc"))
    bms, bme = bench.get("started_monotonic_ns"), bench.get("ended_monotonic_ns")
    if bs is None or be is None or bs >= be or not _ns(bms) or not _ns(bme) or bms >= bme:
        issues.append("BENCHMARK_WINDOW_UNOBSERVED")
    if snapshots:
        sample_utc = [_utc(s.get("timestamp_utc")) for s in snapshots]
        sample_ns = [s.get("monotonic_ns") for s in snapshots]
        if any(s is None for s in sample_utc) or any(not _ns(n) for n in sample_ns):
            issues.append("SAMPLER_TIMING_UNOBSERVED")
        elif (any(a >= b for a, b in zip(sample_utc, sample_utc[1:]))
              or any(a >= b for a, b in zip(sample_ns, sample_ns[1:]))):
            issues.append("SAMPLER_TIME_NON_MONOTONIC")
        elif (bs is None or be is None or not _ns(bms) or not _ns(bme)
              or sample_utc[0] > bs or sample_utc[-1] < be
              or sample_ns[0] > bms or sample_ns[-1] < bme):
            issues.append("BENCHMARK_OUTSIDE_RESOURCE_WINDOW")

    for field in ("requests", "successes", "failures"):
        if not _ns(bench.get(field)):
            issues.append("REQUEST_COUNTS_UNOBSERVED")
            break
    else:
        if (bench["requests"] == 0 or
                bench["successes"] + bench["failures"] != bench["requests"]):
            issues.append("REQUEST_COUNTS_INCONSISTENT")
        if bench["failures"]:
            issues.append("BENCHMARK_REQUEST_FAILURES")
        rate = bench["failures"] / bench["requests"] if bench["requests"] else None
        if not _number(bench.get("error_rate")) or (
                rate is not None and not math.isclose(
                    bench["error_rate"], rate, abs_tol=1e-9, rel_tol=1e-9)):
            issues.append("ERROR_RATE_NOT_REPRODUCIBLE")

    metrics = bench.get("metrics")
    if not isinstance(metrics, dict):
        issues.append("BENCHMARK_METRICS_UNOBSERVED")
        metrics = {}
    for key in ("ttft_p50_seconds", "ttft_p95_seconds", "tokens_per_second"):
        if not _number(metrics.get(key), positive=True):
            issues.append("BENCHMARK_METRIC_MISSING:" + key)
    if (all(_number(metrics.get(k), positive=True) for k in
            ("ttft_p50_seconds", "ttft_p95_seconds"))
            and metrics["ttft_p50_seconds"] > metrics["ttft_p95_seconds"]):
        issues.append("TTFT_PERCENTILE_ORDER_INVALID")
    events = interval.get("cgroup_memory_event_deltas") or {}
    if any(not isinstance(events.get(key), int) or events[key] != 0
           for key in ("oom_delta", "oom_kill_delta")):
        issues.append("OOM_UNOBSERVED_OR_DETECTED")
    return {
        "schema_version": 1, "stage": "p5", "action": "session-review",
        "scope": "UNAUTHENTICATED_SOURCE_EVIDENCE_REVIEW",
        "status": ("SOURCE_SESSION_CORRELATED_NOT_LIVE_ACCEPTANCE" if not issues
                   else "INCOMPLETE_SESSION_EVIDENCE"),
        "model": model, "session_id": sid, "container_id": container_id,
        "api_port": 8000, "interval_summary": interval,
        "issues": sorted(set(issues)), "executed": False,
        "real_dgx_verified": False, "benchmark_verified": False,
        "approval_accepted": False, "operations_enabled": False,
        "production_released": False,
        "note": "Correlated author-supplied evidence does not establish provenance, loaded benchmark acceptance, or release.",
    }
