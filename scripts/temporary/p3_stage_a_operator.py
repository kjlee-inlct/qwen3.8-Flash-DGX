"""D-016 operator wrapper: staged P3-A ONLY, with three manual action gates.

Default --plan is read-only. --execute requires TTY and three independent
typed confirmations matching a *fresh* Wizard stage-A plan. All lifecycle
changes are made by the existing Wizard executor (never this wrapper).
No git pull, no model/cache deletion, no automatic stage B/C advancement.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any
from uuid import uuid4

from scripts.temporary.p1_pre_a_readiness import private_json

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
P1_REPORT_ROOT = HOME / "blazux-p1-reports"
P3_REPORT_ROOT = HOME / "blazux-p3-reports"
SOURCE = "flash-next"
TARGET = "27b"
SOURCE_ID = "qwen3.8-flash-next"
TARGET_ID = "qwen3.8-27b"
SOURCE_NAME = "qwen38-flash"
TARGET_NAME = "qwen38-27b"
BRANCH = "feature/recipe-wizard-handoff"
DOWNTIME_ACK = "I_ACCEPT_FLASH_NEXT_DOWNTIME"
P3_ENTRY_ACK = "I_SEPARATELY_AUTHORIZE_P3_ENTRY"
SHA64 = re.compile(r"^[0-9a-f]{64}$")
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def latest_p1_receipt(root: Path) -> Path | None:
    choices = sorted(root.glob("p1-pre-a-*.json"), reverse=True)
    return choices[0] if choices else None


def p1_evidence_issues(doc: dict[str, Any], *, now: datetime | None = None) -> list[str]:
    """Accept original P1 review receipt only, never infer action authorization."""
    now = now or datetime.now(timezone.utc)
    issues = []
    try:
        stamp = datetime.fromisoformat(doc["observed_at_utc"].replace("Z", "+00:00"))
        if stamp.tzinfo is None or not -120 <= (now-stamp).total_seconds() <= 86400:
            issues.append("P1_PRE_A_EVIDENCE_OLDER_THAN_24H_OR_FROM_FUTURE")
    except (KeyError, AttributeError, TypeError, ValueError):
        issues.append("P1_PRE_A_TIMESTAMP_INVALID")
    if (doc.get("schema_version") != 1
            or doc.get("stage") != "P1_PRE_A_EVIDENCE_RECONCILIATION"
            or doc.get("status") != "PRE_A_P1_REVIEW_READY"
            or doc.get("issues") != []
            or doc.get("current_model") != SOURCE
            or not isinstance(doc.get("current_model_image"), str)
            or not re.fullmatch(r"sha256:[0-9a-f]{64}", doc["current_model_image"])):
        issues.append("P1_PRE_A_RECEIPT_NOT_QUALIFIED")
    for key in ("historical_rc3", "current_rc3"):
        item = doc.get(key) or {}
        if (item.get("status") != "EXPECTED_ACTIVE_FLASH_COLLISION"
                or item.get("check_count") != 2 or item.get("rc3_expected") is not True):
            issues.append("P1_PRE_A_RAW_RC3_NOT_REVIEWED")
            break
    if (doc.get("p1_verify") or {}).get("status") != "PASS":
        issues.append("P1_BASELINE_VERIFY_NOT_ACCEPTED")
    bench = doc.get("p1_benchmark") or {}
    if (bench.get("status") != "PASS" or bench.get("sample_count", 0) < 3
            or not isinstance(bench.get("metrics"), dict)
            or any(type(bench["metrics"].get(k)) not in (float, int)
                   or bench["metrics"][k] <= 0
                   for k in ("ttft_p50_sec", "latency_p50_sec", "mean_tokens_per_sec"))):
        issues.append("P1_NUMERIC_BENCHMARK_NOT_ACCEPTED")
    if not SHA40.fullmatch(str(doc.get("git_head") or "")):
        issues.append("P1_PRE_A_SOURCE_SHA_UNVERIFIED")
    if doc.get("p3_a_executed") is not False or doc.get("post_p3_b_p1_rebenchmark_required") is not True:
        issues.append("P1_PRE_A_RECEIPT_PHASE_INVALID")
    return sorted(set(issues))


def run_readonly(argv: list[str], *, timeout: int = 90) -> tuple[int | None, dict[str, Any]]:
    try:
        cp = subprocess.run(argv, cwd=ROOT, text=True, capture_output=True,
                            timeout=timeout, check=False)
        if len(cp.stdout) > 1024 * 1024:
            return None, {}
        value = json.loads(cp.stdout)
        return cp.returncode, value if isinstance(value, dict) else {}
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        return None, {}


def git_clean() -> bool:
    try:
        b = subprocess.run(["git", "branch", "--show-current"], cwd=ROOT,
                           capture_output=True, text=True, timeout=10)
        d = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"],
                           cwd=ROOT, capture_output=True, text=True, timeout=10)
        return (b.returncode == 0 and b.stdout.strip() == BRANCH
                and d.returncode == 0 and not d.stdout.strip())
    except (OSError, subprocess.TimeoutExpired):
        return False


def plan_issues(plan: dict[str, Any], pre_a: dict[str, Any],
                live: dict[str, Any], *, now_epoch: float | None = None) -> list[str]:
    now_epoch = time.time() if now_epoch is None else now_epoch
    issues = []
    if (plan.get("status") != "READY_TO_REQUEST_TRANSITION_APPROVAL"
            or plan.get("issues") != []
            or plan.get("executed") is not False
            or plan.get("operations_enabled") is not False
            or plan.get("approval_accepted") is not False
            or not SHA64.fullmatch(str(plan.get("plan_id") or ""))):
        issues.append("P3_A_FRESH_PLAN_NOT_READY")
    if (plan.get("stage") != "a" or plan.get("source_model") != SOURCE
            or plan.get("target_model") != TARGET
            or plan.get("target_container_id") is not None
            or plan.get("source_image") != pre_a.get("current_model_image")
            or plan.get("flash_image") != pre_a.get("current_model_image")):
        issues.append("P3_A_PLAN_SOURCE_OR_TARGET_CHANGED")
    if (plan.get("required_downtime_acknowledgement") != DOWNTIME_ACK
            or plan.get("required_p3_entry_acknowledgement") != P3_ENTRY_ACK):
        issues.append("P3_A_APPROVAL_STRINGS_UNEXPECTED")
    expires = plan.get("expires_at_epoch_seconds")
    if not isinstance(expires, (int, float)) or expires <= now_epoch + 15:
        issues.append("P3_A_PLAN_EXPIRED_OR_EXPIRING")
    if (live.get("status") != "LIVE_SERVICE_VERIFIED"
            or live.get("observed_model") != SOURCE
            or live.get("expected_served_id") != SOURCE_ID
            or live.get("observed_model_ids") != [SOURCE_ID]
            or live.get("issues") != []
            or live.get("host_port") != 8000):
        issues.append("P3_A_CURRENT_FLASH_SERVICE_NOT_VERIFIED")
    active = live.get("active_container") or {}
    if (active.get("name") != SOURCE_NAME
            or active.get("image_id") != pre_a.get("current_model_image")
            or not SHA64.fullmatch(str(plan.get("source_container_id") or ""))):
        issues.append("P3_A_CURRENT_FLASH_CONTAINER_NOT_PINNED")
    if (not re.fullmatch(r"sha256:[0-9a-f]{64}", str(plan.get("target_image") or ""))
            or not SHA64.fullmatch(str(plan.get("p2_receipt_sha256") or ""))):
        issues.append("P3_A_TARGET_IMAGE_OR_P2_PROVENANCE_NOT_PINNED")
    return sorted(set(issues))


def prompts(plan: dict, *, input_fn=input) -> bool:
    """Show the precise live plan and three separate literal typed strings."""
    expires = plan.get("expires_at_epoch_seconds")
    try:
        kst = datetime.fromtimestamp(
            expires, timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S KST")
        approval = (
            ("1/3 CURRENT P3-A plan_id", plan["plan_id"]),
            ("2/3 Flash-Next downtime acknowledgment", DOWNTIME_ACK),
            ("3/3 Separate P3-entry acknowledgment", P3_ENTRY_ACK),
        )
        print("\\nCopy or type EXACTLY the value printed below each step.", flush=True)
        print(f"Plan expires at: {kst} (approximately "
              f"{max(0, int(expires - time.time()))} seconds left).", flush=True)
        for label, expected in approval:
            print(f"{label}: {expected}", flush=True)
            if input_fn(f"Enter {label} [exactly: {expected}]: ").strip() != expected:
                return False
        return True
    except (EOFError, KeyboardInterrupt, KeyError, TypeError, ValueError, OverflowError):
        return False


def summarize_runtime(doc: dict, plan: dict) -> bool:
    active = doc.get("active_container") or {}
    return (doc.get("status") == "LIVE_SERVICE_VERIFIED"
            and doc.get("observed_model") == TARGET
            and doc.get("expected_served_id") == TARGET_ID
            and doc.get("observed_model_ids") == [TARGET_ID]
            and doc.get("issues") == []
            and doc.get("host_port") == 8000
            and active.get("name") == TARGET_NAME
            and active.get("image_id") == plan.get("target_image"))


def persist(doc: dict[str, Any], *, root: Path = P3_REPORT_ROOT) -> str:
    root = root.expanduser()
    if root.is_symlink():
        raise ValueError("P3_REPORT_ROOT_SYMLINK_UNSAFE")
    root = root.resolve()
    cache = Path(os.environ.get(
        "HF_CACHE", str(HOME / ".cache/huggingface"))).expanduser().resolve()
    if root.is_relative_to(ROOT.resolve()) or root.is_relative_to(cache):
        raise ValueError("P3_REPORT_ROOT_UNSAFE")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.is_symlink() or root.stat().st_mode & 0o077:
        raise ValueError("P3_REPORT_ROOT_PERMISSIONS_UNSAFE")
    path = root / ("p3-a-operator-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                   + "-" + uuid4().hex[:8] + ".json")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(doc, stream, indent=2, sort_keys=True, ensure_ascii=False)
        stream.write("\n")
    return str(path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true", help="default: read-only P3-A plan")
    mode.add_argument("--execute", action="store_true", help="explicit interactive planned P3-A switch")
    ap.add_argument("--pre-a-report", type=Path, help="original P1 pre-A private evidence")
    args = ap.parse_args(argv)
    evidence = args.pre_a_report or latest_p1_receipt(P1_REPORT_ROOT)
    issues = []
    if evidence is None:
        pre_a = {}
        issues.append("P1_PRE_A_RECEIPT_MISSING")
    else:
        try:
            pre_a = private_json(evidence, P1_REPORT_ROOT, max_size=262144)
            issues.extend(p1_evidence_issues(pre_a))
        except (OSError, ValueError, TypeError):
            pre_a = {}
            issues.append("P1_PRE_A_RECEIPT_UNTRUSTED")
    if not git_clean():
        issues.append("GIT_BRANCH_OR_WORKTREE_UNVERIFIED")
    live_rc, live = run_readonly(["./wizard.sh", "service", "manager",
                                  "status", "--json"])
    plan_rc, plan = run_readonly(["./wizard.sh", "switch", "flash-next-27b",
                                  "stage-a", "--plan", "--json"])
    if live_rc != 0:
        issues.append("CURRENT_LIVE_STATUS_UNAVAILABLE")
    if plan_rc != 0:
        issues.append("STAGE_A_PLAN_UNAVAILABLE")
    issues.extend(plan_issues(plan, pre_a, live))
    report: dict[str, Any] = {
        "schema_version": 1, "stage": "P3_A_OPERATOR_GUARDED_HANDOFF",
        "status": "BLOCKED" if issues else "READY_TO_REQUEST_OPERATOR_INPUT",
        "issues": sorted(set(issues)), "p1_evidence_path": str(evidence) if evidence else None,
        "source_model": SOURCE, "target_model": TARGET,
        "current_source_image": pre_a.get("current_model_image"),
        "plan_id": plan.get("plan_id") if not issues else None,
        "plan_expires_at_epoch_seconds": plan.get("expires_at_epoch_seconds"),
        "source_container_id": plan.get("source_container_id"),
        "target_image": plan.get("target_image"),
        "p2_receipt_sha256": plan.get("p2_receipt_sha256"),
        "p1_pre_a_status": pre_a.get("status"),
        "live_status": live.get("status"),
        "executed": False, "operations_enabled": False,
        "notice": ("P3-A only. Default is read-only. Execute mode requires typed "
                   "action-specific plan, downtime and separate P3-entry acknowledgments. "
                   "Independent host GPU exclusivity and rollback fault injection are "
                   "NOT QUALIFIED; an actual switch interrupts :8000 and recovery is "
                   "best effort. No automatic P3-B or P3-C.")
    }
    if issues:
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    if not args.execute:
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    if not sys.stdin.isatty():
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_A_INTERACTIVE_TTY_REQUIRED"]
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    # Fixed ten-minute plans can have seconds left even when the preflight
    # itself is READY. Do not invite typing into an almost-expired window.
    remaining = int(plan["expires_at_epoch_seconds"] - time.time())
    if remaining < 120:
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_A_NOT_ENOUGH_TIME_FOR_MANUAL_CONFIRMATIONS"]
        report["plan_remaining_seconds"] = max(0, remaining)
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    print(json.dumps(report, indent=2, sort_keys=True), flush=True)
    print("\nP3-A will stop the LIVE Flash-Next service on :8000, attempt "
          "27B startup, and try original-container recovery if the stage fails. "
          "Host or Docker failure can prevent recovery. Type Enter to cancel.", flush=True)
    if not prompts(plan):
        report["status"] = "CANCELLED"
        report["issues"] = ["P3_A_OPERATOR_CONFIRMATION_NOT_COMPLETED"]
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    # The human may take several minutes to type. Never submit an expired
    # or changed plan after those inputs. A new hash needs new user input.
    fresh_rc, refreshed = run_readonly([
        "./wizard.sh", "switch", "flash-next-27b", "stage-a", "--plan", "--json"])
    if (time.time() >= plan["expires_at_epoch_seconds"] - 15
            or fresh_rc != 0
            or refreshed.get("status") != "READY_TO_REQUEST_TRANSITION_APPROVAL"
            or refreshed.get("plan_id") != plan["plan_id"]):
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_A_PLAN_EXPIRED_OR_CHANGED_DURING_OPERATOR_INPUT"]
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    # Only the canonical Wizard executor may perform service mutations.
    cmd = ["./wizard.sh", "switch", "flash-next-27b", "stage-a", "--execute",
           "--approve-plan", plan["plan_id"], "--ack-downtime", DOWNTIME_ACK,
           "--enter-p3", P3_ENTRY_ACK, "--json"]
    exec_rc, execution = run_readonly(cmd, timeout=900)
    report["execute_command_exit_code"] = exec_rc
    report["wizard_result"] = execution
    report["executed"] = execution.get("executed") is True
    report["status"] = "OPERATOR_REVIEW_REQUIRED"
    if (exec_rc == 0 and execution.get("status") == "PASS"
            and execution.get("stage") == "a"
            and execution.get("active_model") == TARGET
            and execution.get("live_verified") is True
            and report["executed"]):
        status_rc, after = run_readonly(
            ["./wizard.sh", "service", "manager", "status", "--json"])
        report["post_switch_status"] = after.get("status")
        report["post_switch_observed_model"] = after.get("observed_model")
        if status_rc == 0 and summarize_runtime(after, plan):
            report["status"] = "P3_A_PASS_27B_ACTIVE"
            report["issues"] = []
        else:
            report["issues"] = ["POST_SWITCH_MANIFEST_API_RECHECK_FAILED"]
    else:
        report["issues"] = (execution.get("issues") or
                            ["P3_A_EXECUTION_FAILED_OR_UNVERIFIED"])
        if (exec_rc == 3 and execution.get("executed") is False
                and "P3_STALE_PLAN_OR_CHANGED_PREFLIGHT" in report["issues"]):
            report["status"] = "BLOCKED"
            report["issues"] = ["P3_A_WIZARD_REJECTED_STALE_OR_CHANGED_PLAN",
                                *report["issues"]]
    report["evidence_file"] = persist(report)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return (0 if report["status"] == "P3_A_PASS_27B_ACTIVE" else
            3 if report["status"] == "BLOCKED" else 4)


if __name__ == "__main__":
    raise SystemExit(main())
