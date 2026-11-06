"""Tracked D-016 P3-B operator runner. Default --plan is strictly read-only.

Unlike P3-A, stage B interrupts the ACTIVE NVIDIA 27B and restores the
ORIGINAL Flash-Next container. --execute requires an independently and
manually typed fresh stage-B SHA, B-specific 27B downtime acknowledgment and
B-specific phase-entry acknowledgment. No B runtime authorization is inferred
from any previous stage. No automatic post-B P1 or final P3-C.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
from pathlib import Path
import sys
import time
from typing import Any

from scripts.temporary.p1_pre_a_readiness import private_json
from scripts.temporary.p3_stage_a_operator import (
    git_clean, run_readonly, persist, summarize_runtime
)
from scripts.temporary import p3_stage_b_inspect as inspector

P3_ROOT = Path.home() / ".local/state/blazux-wizard/p3"
A_RECEIPT = P3_ROOT / "stage-a.json"
DOWNTIME_ACK = "I_ACCEPT_27B_DOWNTIME"
ENTRY_ACK = "I_SEPARATELY_AUTHORIZE_P3_STAGE_B"
MODEL = "27b"
FLASH = "flash-next"
FLASH_API = "qwen3.8-flash-next"


def get_plan_and_live() -> tuple[int | None, dict, int | None, dict]:
    live_rc, live = run_readonly(["./wizard.sh", "service", "manager", "status", "--json"])
    plan_rc, plan = run_readonly(
        ["./wizard.sh", "switch", "flash-next-27b", "stage-b", "--plan", "--json"])
    return live_rc, live, plan_rc, plan


def expiry_kst(epoch: Any) -> str:
    if type(epoch) not in (float, int):
        return "UNKNOWN"
    return datetime.fromtimestamp(epoch, timezone(timedelta(hours=9))).strftime(
        "%Y-%m-%d %H:%M:%S KST")


def confirm(plan: dict[str, Any], *, input_fn=input) -> bool:
    try:
        items = (
            ("1/3 CURRENT P3-B plan_id", plan["plan_id"]),
            ("2/3 Shutdown CURRENT NVIDIA 27B on :8000", DOWNTIME_ACK),
            ("3/3 Authorize ONLY P3-B 27B to Flash-Next", ENTRY_ACK),
        )
        print("\nP3-B requires three NEW independent confirmations.", flush=True)
        print("P3-A acknowledgments cannot be reused.", flush=True)
        print("Expiry: " + expiry_kst(plan["expires_at_epoch_seconds"]), flush=True)
        for label, value in items:
            print(f"{label}: {value}", flush=True)
            if input_fn(f"Type exactly [{value}] (Enter cancels): ").strip() != value:
                return False
        return True
    except (KeyError, TypeError, ValueError, OverflowError, EOFError, KeyboardInterrupt):
        return False


def post_status_ok(live: dict[str, Any], receipt: dict[str, Any]) -> bool:
    active = live.get("active_container") or {}
    return (live.get("status") == "LIVE_SERVICE_VERIFIED"
            and live.get("observed_model") == FLASH
            and live.get("expected_served_id") == FLASH_API
            and live.get("observed_model_ids") == [FLASH_API]
            and live.get("issues") == []
            and live.get("host_port") == 8000
            and active.get("name") == "qwen38-flash"
            and active.get("image_id") == receipt.get("flash_image"))


def review(areceipt: dict[str, Any], live: dict[str, Any], plan: dict[str, Any],
           live_rc: int | None, plan_rc: int | None, *,
           clean: bool, now_epoch: float | None = None) -> list[str]:
    issues = inspector.preflight_issues(
        areceipt, live, plan, now_epoch=now_epoch)
    if live_rc != 0:
        issues.append("P3_B_LIVE_API_STATUS_COMMAND_FAILED")
    if plan_rc != 0:
        issues.append("P3_B_CANONICAL_PLAN_COMMAND_FAILED")
    if not clean:
        issues.append("P3_B_GIT_WORKTREE_NOT_VERIFIED")
    if (plan.get("required_downtime_acknowledgement") != DOWNTIME_ACK
            or plan.get("required_p3_entry_acknowledgement") != ENTRY_ACK):
        issues.append("P3_B_EXPECTED_APPROVAL_STRINGS_CHANGED")
    return sorted(set(issues))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true", help="read-only default")
    mode.add_argument("--execute", action="store_true",
                      help="ACTUAL 27B downtime; separate exact typed P3-B approval required")
    args = parser.parse_args(argv)
    try:
        areceipt = private_json(A_RECEIPT, P3_ROOT, max_size=65536)
        issues = []
    except (OSError, ValueError, TypeError):
        areceipt = {}
        issues = ["P3_A_STAGE_RECEIPT_MISSING_OR_UNTRUSTED"]
    live_rc, live, plan_rc, plan = get_plan_and_live()
    issues.extend(review(areceipt, live, plan, live_rc, plan_rc, clean=git_clean()))
    report = {
        "schema_version": 1,
        "stage": "P3_B_OPERATOR_GUARDED_HANDOFF",
        "status": "BLOCKED" if issues else "READY_FOR_SEPARATE_P3_B_OPERATOR_APPROVAL",
        "issues": sorted(set(issues)),
        "source_model": MODEL, "target_model": FLASH,
        "current_model": live.get("observed_model"),
        "current_model_ids": live.get("observed_model_ids"),
        "source_container_id": plan.get("source_container_id"),
        "preserved_flash_container_id": plan.get("target_container_id"),
        "source_image": plan.get("source_image"),
        "preserved_flash_image": plan.get("target_image"),
        "plan_id": plan.get("plan_id") if not issues else None,
        "expires_at_epoch_seconds": plan.get("expires_at_epoch_seconds"),
        "expires_at_kst": expiry_kst(plan.get("expires_at_epoch_seconds")),
        "stage_a_plan_id": areceipt.get("plan_id"),
        "stage_a_receipt": str(A_RECEIPT),
        "executed": False, "operations_enabled": False,
        "approval_accepted": False,
        "notice": (
            "No stage-B authorization from P3-A. Plan-only mode is strictly "
            "read-only. Execution requires live terminal, independent current "
            "stage-B SHA and new explicit 27B downtime + stage-B-entry inputs. "
            "The ACTIVE 27B service on :8000 will stop; preserved Flash is "
            "started. Host/daemon faults may defeat rollback. Never auto-run "
            "P1 probes/benchmark or P3-C."),
    }
    if issues or not args.execute:
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
        return 3 if issues else 0
    if not sys.stdin.isatty():
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_B_OPERATOR_TTY_REQUIRED"]
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    expires = plan.get("expires_at_epoch_seconds")
    if type(expires) not in (float, int) or expires - time.time() < 120:
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_B_INSUFFICIENT_TIME_FOR_MANUAL_CONFIRMATIONS"]
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), flush=True)
    print("\nCAUTION: P3-B stops the live NVIDIA 27B API on port 8000.",
          "It attempts to start the original preserved Flash-Next container.",
          "On failure, source 27B restoration is best effort.", flush=True)
    if not confirm(plan):
        report["status"] = "CANCELLED"
        report["issues"] = ["P3_B_EXACT_MANUAL_APPROVAL_INCOMPLETE"]
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    # Re-observe before the service-changing core; never silently substitute
    # a newly rotated plan for the value actually typed by the operator.
    now = time.time()
    next_live_rc, next_live, next_plan_rc, next_plan = get_plan_and_live()
    if (type(expires) not in (int, float) or expires - now < 15
            or next_plan.get("plan_id") != plan.get("plan_id")
            or review(areceipt, next_live, next_plan, next_live_rc, next_plan_rc,
                      clean=git_clean(), now_epoch=now)):
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_B_APPROVED_PLAN_EXPIRED_OR_SOURCE_CHANGED"]
        report["evidence_file"] = persist(report)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3
    cmd = ["./wizard.sh", "switch", "flash-next-27b", "stage-b",
           "--execute", "--approve-plan", plan["plan_id"],
           "--ack-downtime", DOWNTIME_ACK,
           "--enter-p3", ENTRY_ACK, "--json"]
    run_rc, done = run_readonly(cmd, timeout=900)
    report["wizard_result"] = done
    report["execute_command_exit_code"] = run_rc
    report["executed"] = done.get("executed") is True
    if (run_rc == 0 and done.get("status") == "PASS"
            and done.get("stage") == "b"
            and done.get("active_model") == FLASH
            and done.get("live_verified") is True
            and report["executed"]):
        check_rc, after = run_readonly(
            ["./wizard.sh", "service", "manager", "status", "--json"])
        report["post_switch_status"] = after.get("status")
        report["post_switch_observed_model"] = after.get("observed_model")
        if check_rc == 0 and post_status_ok(after, areceipt):
            report["status"] = "P3_B_PASS_FLASH_NEXT_ACTIVE"
            report["issues"] = []
        else:
            report["status"] = "OPERATOR_REVIEW_REQUIRED"
            report["issues"] = ["P3_B_FLASH_API_RECHECK_FAILED"]
    elif (run_rc == 3 and done.get("executed") is False
          and "P3_STALE_PLAN_OR_CHANGED_PREFLIGHT" in done.get("issues", [])):
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_B_WIZARD_REFUSED_STALE_PLAN_PRE_MUTATION"]
    else:
        report["status"] = "OPERATOR_REVIEW_REQUIRED"
        report["issues"] = done.get("issues") or [
            "P3_B_EXECUTION_OR_RECOVERY_UNVERIFIED"]
    report["evidence_file"] = persist(report)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return (0 if report["status"] == "P3_B_PASS_FLASH_NEXT_ACTIVE"
            else 3 if report["status"] == "BLOCKED" else 4)


if __name__ == "__main__":
    raise SystemExit(main())
