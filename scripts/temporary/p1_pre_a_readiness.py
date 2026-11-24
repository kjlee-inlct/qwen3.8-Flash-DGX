"""Read-only P1 evidence reconciliation before asking for P3-A downtime.

Tracked temporary DGX operator wrapper (D-016). No GPU inference, Docker
mutation, model switches, git pull, HF cache mutation, or approval generation.
Review both old and fresh P1 diagnostic stdout, saved P1 PASS receipts and
a newly observed Manifest/API model identity. Written JSON is local/private.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
import re
from pathlib import Path
import subprocess
from uuid import uuid4
from typing import Any

from scripts.manager.p3_p1_evidence_gate import _expected_active_flash_collision
from scripts.temporary.p1_post_download import cache_diagnosis_summary

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
REPORT_ROOT = HOME / "blazux-p1-reports"
P1_ROOT = HOME / ".local/state/blazux-wizard/p1"
HISTORIC = REPORT_ROOT / "20261105T113110Z-fdc179fa/result.json"
VERIFY = P1_ROOT / "20261105T113119Z-eca4ec724ede.json"
BENCH = P1_ROOT / "20261105T113125Z-586b2b46d93e.json"
REPO = "nvidia/Qwen3.8-Flash-Next-NVFP4"
SERVED = "qwen3.8-flash-next"
BRANCH = "feature/recipe-wizard-handoff"


def private_json(path: Path, root: Path, *, max_size: int) -> dict[str, Any]:
    if (path.is_symlink() or not path.is_file()
            or not path.resolve().is_relative_to(root.resolve())):
        raise ValueError("private_json_path_invalid")
    st = path.stat()
    if st.st_mode & 0o077 or not 0 < st.st_size <= max_size:
        raise ValueError("private_json_mode_or_size_invalid")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("private_json_not_object")
    return data


def run_readonly(args: list[str], *, timeout: int = 35) -> tuple[int | None, str]:
    try:
        result = subprocess.run(args, cwd=ROOT, text=True, capture_output=True,
                                timeout=timeout, check=False)
        if len(result.stdout) > 1024 * 1024:
            return None, ""
        return result.returncode, result.stdout
    except (OSError, subprocess.TimeoutExpired):
        return None, ""


def latest_report(root: Path) -> Path | None:
    candidates = sorted(root.glob("20*/result.json"), reverse=True)
    return candidates[0] if candidates else None


def check_collision(report: dict[str, Any], flash_image: str) -> dict[str, Any]:
    checks = report.get("checks") or {}
    result: dict[str, Any] = {"status": "BLOCKED", "rc3_expected": False}
    if not isinstance(checks, dict):
        return result
    raw: list[dict[str, Any]] = []
    for action in ("doctor", "inventory_plan"):
        entry = checks.get(action)
        if (not isinstance(entry, dict)
                or entry.get("returncode") != 3
                or entry.get("truncated") is not False):
            return result
        try:
            payload = json.loads(entry.get("stdout", ""))
        except (ValueError, TypeError):
            return result
        if not _expected_active_flash_collision(payload, flash_image):
            return result
        raw.append(payload)
    # This is evidence of a *consistent* existing-service collision, not
    # an independent host PID-to-port ownership or GPU exclusivity audit.
    result["status"] = "EXPECTED_ACTIVE_FLASH_COLLISION"
    result["rc3_expected"] = True
    result["check_count"] = len(raw)
    return result


def _positive(value: Any) -> bool:
    return (type(value) in (float, int) and math.isfinite(value) and value > 0)


def check_verify(doc: dict[str, Any], flash_image: str) -> bool:
    result = doc.get("result") or {}
    probes = result.get("probes") or {}
    identity = result.get("identity") or {}
    return (doc.get("status") == "PASS"
            and doc.get("executed") is True
            and doc.get("approval") == "explicit_plan_id"
            and doc.get("model_repo") == REPO
            and doc.get("served_model") == SERVED
            and doc.get("image_id") == flash_image
            and isinstance(result, dict)
            and result.get("status") == "PASS"
            and result.get("baseline_status") == "PASS"
            and result.get("extended_status") == "PASS"
            and isinstance(identity, dict)
            and identity.get("health") == "PASS"
            and isinstance(identity.get("models"), list)
            and SERVED in identity["models"]
            and isinstance(probes, dict)
            and all((probes.get(k) or {}).get("status") == "PASS"
                    for k in ("default_completion", "chat", "tools", "vision")))


def benchmark_metrics(doc: dict[str, Any], flash_image: str) -> dict[str, Any]:
    result = doc.get("result") or {}
    bench = result.get("benchmark") or {}
    metrics = bench.get("metrics") or {}
    samples = bench.get("samples") or []
    ok = (doc.get("status") == "PASS" and doc.get("executed") is True
          and doc.get("approval") == "explicit_plan_id"
          and doc.get("model_repo") == REPO
          and doc.get("served_model") == SERVED
          and doc.get("image_id") == flash_image
          and isinstance(bench, dict) and bench.get("status") == "PASS"
          and isinstance(metrics, dict) and isinstance(samples, list)
          and len(samples) >= 3
          and all(_positive(metrics.get(k)) for k in
                  ("latency_p50_sec", "latency_p95_sec",
                   "ttft_p50_sec", "ttft_p95_sec",
                   "mean_tokens_per_sec"))
          and all(isinstance(x, dict)
                  and type(x.get("completion_tokens")) is int
                  and x["completion_tokens"] > 0
                  and _positive(x.get("latency_sec"))
                  and type(x.get("ttft_sec")) in (int, float)
                  and math.isfinite(x["ttft_sec"]) and x["ttft_sec"] >= 0
                  for x in samples))
    return {"status": "PASS" if ok else "BLOCKED",
            "sample_count": len(samples) if isinstance(samples, list) else 0,
            "metrics": {k: metrics.get(k) for k in
                        ("ttft_p50_sec", "ttft_p95_sec", "latency_p50_sec",
                         "latency_p95_sec", "mean_tokens_per_sec",
                         "total_completion_tokens")}
            if ok else None}


def assessment(current: dict[str, Any], historic: dict[str, Any],
               verify: dict[str, Any], benchmark: dict[str, Any],
               live: dict[str, Any], *, git_head: str,
               branch: str, git_clean: bool,
               now: datetime | None = None) -> dict[str, Any]:
    """Pure fail-closed reconciliation; never mutates a model or grants approval."""
    now = now or datetime.now(timezone.utc)
    issues = []
    def issue(code: str, ok: bool) -> None:
        if not ok:
            issues.append(code)

    try:
        dt = datetime.fromisoformat(current["timestamp_utc"].replace("Z", "+00:00"))
        fresh = (dt.tzinfo is not None
                 and -120 <= (now - dt).total_seconds() <= 24 * 3600)
    except (ValueError, KeyError, TypeError):
        fresh = False
    issue("P1_INSPECT_REPORT_STALE_OR_INVALID", fresh)
    pf = current.get("preflight") or {}
    issue("P1_INSPECT_PREFLIGHT_INCOMPLETE",
          isinstance(pf, dict) and all(pf.get(k) is True
          for k in ("branch_ok", "tracked_tree_clean",
                    "expected_api_model_present", "runtime_allowed"))
          and (pf.get("operator_process") or {}).get("blocked") is False)
    issue("CURRENT_GIT_BRANCH_OR_WORKTREE_NOT_VERIFIED",
          branch == BRANCH and git_clean and bool(re.fullmatch("[0-9a-f]{40}", git_head)))
    # The persisted P1 report stores command output under checks.*.stdout.
    # The cache_diagnosis top-level object is printed as a console-only summary.
    # Reuse the original reader so the audit matches the actual saved schema.
    diagnosis = cache_diagnosis_summary(current.get("checks") or {})
    wa = diagnosis.get("wizard_audit") or {}
    issue("P1_ASSET_AUDIT_NOT_READY",
          wa.get("state") == "READY" and wa.get("source_complete") is True
          and wa.get("hybrid_ready") is True
          and wa.get("source_issues") == [] and wa.get("hybrid_issues") == []
          and wa.get("model_repo") == REPO)
    planned = current.get("plans") or {}
    issue("P1_FUNCTIONAL_AND_BENCH_PLANS_NOT_READY",
          isinstance(planned, dict) and all(
              isinstance(planned.get(k), dict)
              and planned[k].get("ready") is True
              and (planned[k].get("plan") or {}).get("issues") == []
              for k in ("verify", "benchmark")))
    revision = wa.get("revision")
    revision_verified = (isinstance(revision, str)
                         and bool(re.fullmatch("[0-9a-f]{40}", revision)))
    issue("P1_CURRENT_CHECKPOINT_REVISION_UNAVAILABLE", revision_verified)
    # Missing revision means UNKNOWN, not observed drift. Do not report drift
    # until two actual revisions are available for comparison.
    if revision_verified:
        issue("P1_RECEIPT_CHECKPOINT_REVISION_DRIFT",
              verify.get("model_revision") == revision
              and benchmark.get("model_revision") == revision)
    issue("CURRENT_MANIFEST_API_NOT_VERIFIED",
          live.get("status") == "LIVE_SERVICE_VERIFIED"
          and live.get("observed_model") == "flash-next"
          and live.get("expected_served_id") == SERVED
          and live.get("observed_model_ids") == [SERVED]
          and live.get("issues") == []
          and (live.get("active_container") or {}).get("name") == "qwen38-flash"
          and live.get("host_port") == 8000)
    image = (live.get("active_container") or {}).get("image_id")
    issue("LIVE_FLASH_IMAGE_UNVERIFIED",
          isinstance(image, str) and image.startswith("sha256:")
          and len(image) == 71)
    # No assumptions from rc3 values; parse both raw doctor/inventory outputs.
    current_coll = check_collision(current, image) if image else {"status": "BLOCKED"}
    old_coll = check_collision(historic, image) if image else {"status": "BLOCKED"}
    issue("CURRENT_P1_RC3_RAW_CAUSE_UNVERIFIED",
          current_coll["status"] == "EXPECTED_ACTIVE_FLASH_COLLISION")
    issue("HISTORICAL_P1_RC3_RAW_CAUSE_UNVERIFIED",
          old_coll["status"] == "EXPECTED_ACTIVE_FLASH_COLLISION")
    issue("P1_VERIFY_RECEIPT_NOT_QUALIFIED", check_verify(verify, image))
    metrics = benchmark_metrics(benchmark, image)
    issue("P1_BENCHMARK_NUMERICAL_EVIDENCE_NOT_QUALIFIED",
          metrics["status"] == "PASS")
    actions = current.get("actions") or {}
    issue("P1_INSPECT_ONLY_ACTIONS_UNEXPECTED",
          all((actions.get(k) or {}).get("reason") == "inspection_only"
              and (actions.get(k) or {}).get("status") == "BLOCKED"
              for k in ("verify", "benchmark")))
    status = "PRE_A_P1_REVIEW_READY" if not issues else "BLOCKED"
    return {
        "schema_version": 1, "stage": "P1_PRE_A_EVIDENCE_RECONCILIATION",
        "status": status, "issues": sorted(issues),
        "git_head": git_head, "current_model": live.get("observed_model"),
        "current_model_image": image, "current_rc3": current_coll,
        "historical_rc3": old_coll, "p1_verify": {
            "status": "PASS" if check_verify(verify, image) else "BLOCKED"},
        "p1_benchmark": metrics,
        "post_p3_b_p1_rebenchmark_required": True,
        "p3_a_executed": False, "p3_a_execution_authorized": False,
        "operations_enabled": False,
        "notice": ("Read-only PRE-A history review, not a new P1 GPU run. "
                   "A READY result is not P3-A runtime approval or proof of "
                   "post-stage-B P1 rebenchmark, GPU exclusivity or rollback.")
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path,
                    help="P1 inspect-only report; default: newest local report")
    ap.add_argument("--historical-report", type=Path, default=HISTORIC)
    ap.add_argument("--verify-receipt", type=Path, default=VERIFY)
    ap.add_argument("--benchmark-receipt", type=Path, default=BENCH)
    ap.add_argument("--report-root", type=Path, default=REPORT_ROOT)
    args = ap.parse_args(argv)
    report_root = args.report_root.expanduser().resolve()
    path = args.report or latest_report(report_root)
    issues: list[str] = []
    source: dict[str, Any] = {}
    def load(file: Path | None, root: Path, key: str, limit: int) -> dict:
        if file is None:
            issues.append(key + "_NOT_FOUND")
            return {}
        try:
            value = private_json(file.expanduser(), root, max_size=limit)
            source[key] = str(file)
            return value
        except (OSError, ValueError, UnicodeError):
            issues.append(key + "_UNREADABLE_OR_UNTRUSTED")
            return {}

    current = load(path, report_root, "current_report", 4 * 1024 * 1024)
    historic = load(args.historical_report, report_root, "historical_report",
                    4 * 1024 * 1024)
    verify = load(args.verify_receipt, P1_ROOT, "verify_receipt", 256 * 1024)
    bench = load(args.benchmark_receipt, P1_ROOT, "benchmark_receipt", 256 * 1024)

    rc, stdout = run_readonly(["./wizard.sh", "service", "manager",
                               "status", "--json"])
    try:
        live = json.loads(stdout) if rc == 0 else {}
    except (ValueError, TypeError):
        live = {}
    if not isinstance(live, dict):
        live = {}
    branch_rc, branch_out = run_readonly(["git", "branch", "--show-current"])
    head_rc, head_out = run_readonly(["git", "rev-parse", "HEAD"])
    clean_rc, clean_out = run_readonly(
        ["git", "status", "--porcelain", "--untracked-files=no"])
    result = assessment(current, historic, verify, bench, live,
                        git_head=head_out.strip() if head_rc == 0 else "",
                        branch=branch_out.strip() if branch_rc == 0 else "",
                        git_clean=clean_rc == 0 and not clean_out.strip())
    result["issues"] = sorted(set(result["issues"] + issues))
    if result["issues"]:
        result["status"] = "BLOCKED"
    result["evidence_sources"] = source
    result["observed_at_utc"] = datetime.now(timezone.utc).isoformat()
    # This is the sole persistent mutation: a private, new evidence file
    # outside Git and the HF cache. A zero exit code is never P3 approval.
    if (report_root.is_relative_to(ROOT.resolve())
            or report_root.is_relative_to(
                Path(os.environ.get("HF_CACHE", str(HOME / ".cache/huggingface"))).resolve())):
        ap.error("evidence report root must be outside Git/HF cache")
    report_root.mkdir(parents=True, mode=0o700, exist_ok=True)
    if report_root.stat().st_mode & 0o077:
        ap.error("evidence report root permissions unsafe")
    target = report_root / ("p1-pre-a-" +
                datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") +
                "-" + uuid4().hex[:8] + ".json")
    fd = os.open(target, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as output:
        json.dump(result, output, ensure_ascii=False, indent=2, sort_keys=True)
        output.write("\n")
    result["evidence_file"] = str(target)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["status"] == "PRE_A_P1_REVIEW_READY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
