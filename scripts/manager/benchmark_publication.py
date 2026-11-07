"""Publish deterministic, privacy-allowlisted benchmark summaries to Git.

This is SOURCE-ONLY: read one original private receipt, never call GPU/Docker,
never modify the receipt, never auto-stage/commit/push and never overwrite an
existing published summary. Public provenance references the raw SHA256 only.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LEGACY = Path.home() / ".local/state/blazux-wizard"
REPORTS = ROOT / "reports"
PUBLIC = ROOT / "benchmarks" / "published"
POLICY = ROOT / "runtimes" / "service-policy.json"
DISCOVERY = ROOT / "runtimes" / "model-discovery.json"
SHA64 = re.compile(r"^[0-9a-f]{64}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")
UTC_FILENAME = re.compile(r"(\d{8}T\d{6}Z)")
KINDS = {"flash-next": "p1", "27b": "p2"}
BASE_KEYS = (
    "ttft_p50_sec", "ttft_p95_sec", "latency_p50_sec", "latency_p95_sec",
)
FLASH_KEYS = BASE_KEYS + ("mean_tokens_per_sec", "total_completion_tokens")
MODEL27_KEYS = BASE_KEYS + (
    "mean_e2e_tokens_per_sec", "mean_decode_tokens_per_sec_proxy")
LIMIT_COMMON = "bounded_three_request_smoke_not_saturation_test"
LIMIT_27B = [
    LIMIT_COMMON, "client_ttft_includes_queue_network_prefill",
    "decode_proxy_not_engine_measured", "true_prefill_throughput_not_measured",
    "original_flash_service_restored_after_trial",
]


def _read_source(source: Path, roots: tuple[Path, ...]) -> tuple[dict, bytes, str]:
    """Accept only exact legacy/model-report folders; never arbitrary files."""
    if source.is_symlink() or not source.is_file() or source.suffix != ".json":
        raise ValueError("SOURCE_NOT_REGULAR_PRIVATE_JSON")
    trusted = any(
        not root.is_symlink()
        and source.resolve().parent == root.resolve()
        and source.parent.resolve() == root.resolve()
        for root in roots
    )
    if not trusted:
        raise ValueError("SOURCE_OUTSIDE_MODEL_EVIDENCE_ROOT")
    stat = source.stat()
    if stat.st_size < 1 or stat.st_size > 1_048_576 or stat.st_mode & 0o077:
        raise ValueError("SOURCE_PRIVATE_MODE_OR_SIZE_INVALID")
    raw = source.read_bytes()
    doc = json.loads(raw)
    if not isinstance(doc, dict):
        raise ValueError("SOURCE_NOT_JSON_OBJECT")
    return doc, raw, hashlib.sha256(raw).hexdigest()


def _number(value: Any) -> float | int:
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("NON_FINITE_OR_INVALID_METRIC")
    return value


def _profile(doc: dict, bench: dict) -> dict:
    raw = doc.get("parameters") if "parameters" in doc else bench
    if not isinstance(raw, dict):
        raise ValueError("MISSING_BENCHMARK_PROFILE")
    profile = {}
    for key in ("requests", "max_tokens", "seed", "concurrency"):
        if key == "concurrency" and "concurrency" not in raw:
            raw = {**raw, "concurrency": bench.get("concurrency")}
        value = raw.get(key)
        if type(value) is not int or (value < 0 if key == "seed" else value < 1):
            raise ValueError("INVALID_PROFILE_" + key.upper())
        profile[key] = value
    if profile["requests"] != 3 or profile["max_tokens"] != 64 or profile["concurrency"] != 1:
        # This initial registry covers a narrowly verified bounded profile.
        # Broader workloads require a separately qualified schema/method.
        raise ValueError("UNQUALIFIED_PUBLIC_PROFILE")
    return profile


def _model_details(model: str, policy: Path, discovery: Path,
                   doc: dict) -> tuple[str, str, str]:
    if model not in KINDS:
        raise ValueError("UNKNOWN_PUBLISHED_MODEL")
    p = json.loads(policy.read_text(encoding="utf-8"))
    d = json.loads(discovery.read_text(encoding="utf-8"))
    entry = (p.get("models") or {}).get(model) or {}
    installed = (d.get("models") or {}).get(model) or {}
    served, repository = entry.get("served_id"), entry.get("checkpoint")
    if not isinstance(served, str) or not isinstance(repository, str):
        raise ValueError("MISSING_MODEL_POLICY")
    revision = (doc.get("model_revision") if model == "flash-next"
                else installed.get("pinned_revision"))
    if not isinstance(revision, str) or not SHA40.fullmatch(revision):
        raise ValueError("MODEL_REVISION_UNVERIFIED")
    if model == "flash-next" and (doc.get("model_repo") != repository
                                  or doc.get("served_model") != served):
        raise ValueError("FLASH_MODEL_PROVENANCE_MISMATCH")
    if model == "27b" and installed.get("repo_id") != repository:
        raise ValueError("MODEL_DISCOVERY_POLICY_DRIFT")
    return served, repository, revision


def _benchmark(doc: dict, model: str) -> tuple[dict, str, str, list[str]]:
    if model == "flash-next":
        result = doc.get("result") or {}
        bench = result.get("benchmark") if isinstance(result, dict) else None
        if (doc.get("action") != "benchmark" or doc.get("status") != "PASS"
                or doc.get("executed") is not True
                or not isinstance(bench, dict) or bench.get("status") != "PASS"):
            raise ValueError("P1_BENCHMARK_NOT_QUALIFIED")
        return (bench, "PASS", "client_sse_e2e_completion_tps",
                [LIMIT_COMMON])
    if model == "27b":
        bench = doc.get("benchmark")
        restored = doc.get("post_restore_wizard_status") or {}
        if (doc.get("status") != "BENCH_PASS_RESTORED_VERIFIED"
                or doc.get("executed") is not True
                or not isinstance(bench, dict) or bench.get("status") != "PASS"
                or bench.get("model") != "qwen3.8-27b"
                or not isinstance(restored, dict)
                or restored.get("status") != "LIVE_SERVICE_VERIFIED"
                or restored.get("observed_model") != "flash-next"
                or restored.get("expected_served_id") != "qwen3.8-flash-next"
                or restored.get("issues") not in ([], None)):
            raise ValueError("P2_BENCH_OR_RESTORATION_NOT_QUALIFIED")
        return (bench, "BENCH_PASS_RESTORED_VERIFIED",
                "client_sse_trial_restore_e2e_and_decode_proxy", LIMIT_27B)
    raise ValueError("UNKNOWN_PUBLISHED_MODEL")


def build_summary(*, model: str, source: Path, legacy: Path = LEGACY,
                  reports: Path = REPORTS, policy: Path = POLICY,
                  discovery: Path = DISCOVERY) -> tuple[dict, Path]:
    if model not in KINDS:
        raise ValueError("UNKNOWN_PUBLISHED_MODEL")
    root = legacy / KINDS[model]
    entry = (json.loads(policy.read_text(encoding="utf-8")).get("models") or {}).get(model)
    if not isinstance(entry, dict) or not entry.get("served_id"):
        raise ValueError("MODEL_POLICY_MISSING")
    receipt_root = reports / "models" / entry["served_id"]
    doc, raw, digest = _read_source(source, (root, receipt_root))
    served, repository, revision = _model_details(model, policy, discovery, doc)
    bench, status, method, limits = _benchmark(doc, model)
    profile = _profile(doc, bench)
    if type(bench.get("requests")) is not int or bench["requests"] != profile["requests"]:
        raise ValueError("REQUEST_COUNT_MISMATCH")
    if type(bench.get("max_tokens")) is not int or bench["max_tokens"] != profile["max_tokens"]:
        raise ValueError("MAX_TOKENS_MISMATCH")
    if type(bench.get("seed")) is not int or bench["seed"] != profile["seed"]:
        raise ValueError("SEED_MISMATCH")
    if type(bench.get("concurrency")) is not int or bench["concurrency"] != profile["concurrency"]:
        raise ValueError("CONCURRENCY_MISMATCH")
    samples = bench.get("samples")
    if not isinstance(samples, list) or len(samples) != profile["requests"]:
        raise ValueError("BENCHMARK_SAMPLE_COUNT_MISMATCH")
    if model == "27b" and not all(isinstance(v, dict) and v.get("success") is True
                                   for v in samples):
        raise ValueError("INCOMPLETE_27B_SAMPLES")
    metrics = bench.get("metrics")
    if not isinstance(metrics, dict):
        raise ValueError("MISSING_BENCHMARK_METRICS")
    keys = FLASH_KEYS if model == "flash-next" else MODEL27_KEYS
    clean_metrics = {k: _number(metrics.get(k)) for k in keys}
    if "total_completion_tokens" in clean_metrics and type(clean_metrics["total_completion_tokens"]) is not int:
        raise ValueError("TOTAL_COMPLETION_TOKENS_NOT_INT")
    stamp = UTC_FILENAME.search(source.name)
    if not stamp:
        raise ValueError("SOURCE_FILENAME_UTC_TIMESTAMP_REQUIRED")
    when = datetime.strptime(stamp.group(1), "%Y%m%dT%H%M%SZ").replace(
        tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    policy_engine = json.loads(policy.read_text(encoding="utf-8")).get("engine")
    if policy_engine != "vllm-0.32":
        raise ValueError("UNEXPECTED_RUNTIME_ENGINE")
    summary = {
        "schema_version": 1, "record_kind": "benchmark_summary",
        "model_id": served, "model_repository": repository,
        "model_revision": revision, "runtime": policy_engine,
        "measurement_time_utc": when, "source_evidence_sha256": digest,
        "benchmark_status": "PASS", "execution_status": status,
        "profile": profile, "metrics": clean_metrics,
        "method": method, "limitations": limits,
    }
    # The publication path cannot expose an absolute/private source location.
    destination = ROOT / "benchmarks" / "published" / served / (digest[:16] + ".json")
    return summary, destination


def _serialized(doc: dict) -> bytes:
    return (json.dumps(doc, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def publish(summary: dict, destination: Path, *, expected_sha: str | None,
            public: Path = PUBLIC) -> dict:
    digest = summary["source_evidence_sha256"]
    if not isinstance(expected_sha, str) or not SHA64.fullmatch(expected_sha):
        return {"status": "BLOCKED", "issues": ["EXACT_RECEIPT_SHA256_REQUIRED"],
                "executed": False}
    if expected_sha != digest:
        return {"status": "BLOCKED", "issues": ["RECEIPT_SHA256_CHANGED"],
                "executed": False}
    if not destination.resolve().is_relative_to(public.resolve()):
        return {"status": "BLOCKED", "issues": ["PUBLICATION_OUTSIDE_APPROVED_ROOT"],
                "executed": False}
    for folder in (public.parent, public, destination.parent):
        if folder.is_symlink():
            return {"status": "BLOCKED", "issues": ["PUBLICATION_SYMLINK_FOLDER"],
                    "executed": False}
    data = _serialized(summary)
    if destination.exists() or destination.is_symlink():
        if destination.is_symlink() or not destination.is_file():
            return {"status": "BLOCKED", "issues": ["PUBLICATION_TARGET_NOT_REGULAR"],
                    "executed": False}
        if destination.read_bytes() == data:
            return {"status": "ALREADY_PUBLISHED", "executed": False, "issues": [],
                    "published_path": str(destination)}
        return {"status": "BLOCKED", "issues": ["PUBLISHED_CONTENT_MISMATCH"],
                "executed": False}
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(destination, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o644)
        with os.fdopen(fd, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
    except OSError:
        return {"status": "BLOCKED", "issues": ["PUBLICATION_WRITE_FAILED"],
                "executed": False}
    return {"status": "PUBLIC_SUMMARY_WRITTEN", "executed": False,
            "published_path": str(destination), "issues": [],
            "notice": "Summary was not committed or pushed; review Git diff first."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sanitized benchmark publication (no GPU, no Git push)")
    parser.add_argument("--model", choices=sorted(KINDS), required=True)
    parser.add_argument("--source", type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--verify-published", action="store_true")
    mode.add_argument("--write", action="store_true")
    parser.add_argument("--approve-sha256")
    args = parser.parse_args(argv)
    try:
        summary, destination = build_summary(
            model=args.model, source=args.source.expanduser(),
            legacy=LEGACY, reports=REPORTS, policy=POLICY, discovery=DISCOVERY)
        if args.plan:
            if args.approve_sha256:
                raise ValueError("PLAN_CANNOT_INCLUDE_APPROVAL")
            result = {"status": "READY_FOR_PUBLICATION_REVIEW",
                      "executed": False, "summary": summary,
                      "destination": str(destination), "issues": []}
        elif args.verify_published:
            if args.approve_sha256:
                raise ValueError("VERIFY_CANNOT_INCLUDE_APPROVAL")
            correct = (destination.is_file() and not destination.is_symlink()
                       and destination.read_bytes() == _serialized(summary))
            result = {"status": "VERIFIED" if correct else "PUBLIC_SUMMARY_MISMATCH",
                      "executed": False, "source_sha256": summary["source_evidence_sha256"],
                      "published_path": str(destination),
                      "issues": [] if correct else ["PUBLIC_SUMMARY_MISMATCH"]}
        else:
            result = publish(summary, destination, expected_sha=args.approve_sha256)
    except (ValueError, OSError, TypeError, json.JSONDecodeError) as exc:
        # Never print OS exception strings: they can contain private paths.
        result = {"status": "BLOCKED", "executed": False,
                  "issues": [str(exc) if isinstance(exc, ValueError)
                             and str(exc).isupper() else type(exc).__name__]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] in (
        "READY_FOR_PUBLICATION_REVIEW", "VERIFIED", "ALREADY_PUBLISHED",
        "PUBLIC_SUMMARY_WRITTEN") else 3


if __name__ == "__main__":
    raise SystemExit(main())
