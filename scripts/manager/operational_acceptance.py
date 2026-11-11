"""One-switch DGX acceptance-trial entry, separately from production release.

Only a real human TTY can approve a bounded live test of the recurring
operating executor. This is *not* the ordinary production menu release gate.
Never re-run P3 A/B/C, auto-switch back or delete preserved model assets.
The default --plan reads state only, no journal writes or API inference.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any, Callable

from scripts.manager.operational_switch import make_plan, READY, SUPPORTED
from scripts.manager.operational_executor import (
    execute, execution_plan_id, ACK_DOWNTIME, ACK_TARGET,
)

ACCEPTANCE_ACK = "I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL"
MIN_REMAINING_SECONDS = 180


def trial_plan(target: str, *, planner: Callable[[str], dict] = make_plan,
               clock: Callable[[], float] = time.time) -> dict[str, Any]:
    if target not in SUPPORTED:
        return {"status": "BLOCKED", "target_model": target,
                "issues": ["UNSUPPORTED_MODEL"], "executed": False,
                "approval_accepted": False}
    try:
        preview = planner(target)
    except (OSError, RuntimeError, ValueError, TypeError):
        return {"status": "BLOCKED", "target_model": target,
                "issues": ["CURRENT_PREFLIGHT_UNAVAILABLE"], "executed": False,
                "approval_accepted": False}
    token = execution_plan_id(preview)
    try:
        remaining = int(preview["expires_at_epoch_seconds"] - clock())
    except (KeyError, ValueError, TypeError, OverflowError):
        remaining = 0
    issues = list(preview.get("issues") or [])
    if preview.get("status") != READY or not token:
        issues.append("PREVIEW_NOT_EXECUTION_QUALIFIED")
    if remaining < MIN_REMAINING_SECONDS:
        issues.append("INSUFFICIENT_APPROVAL_TIME_WINDOW")
    status = "READY_FOR_SEPARATE_TRIAL_APPROVAL" if not issues else "BLOCKED"
    return {"schema_version": 1, "scope": "ONE_OFF_REAL_DGX_OPERATING_ACCEPTANCE",
            "status": status, "source_model": preview.get("source_model"),
            "target_model": target, "served_id": preview.get("target_served_id"),
            "api_port": 8000, "expires_at_epoch_seconds":
            preview.get("expires_at_epoch_seconds"),
            "seconds_remaining": max(0, remaining),
            "execution_plan_id": token if status != "BLOCKED" else None,
            "issues": sorted(set(issues)),
            "executed": False, "approval_accepted": False,
            "production_release": False,
            "notice": (
                "Plan only. If explicitly executed by an operator, this ONE action "
                "will stop the currently active model and may fail restoration. "
                "No automatic switch-back. Historical P3 A/B/C are never replayed.")
            }


def run_trial(target: str, *, planner: Callable[[str], dict] = make_plan,
              executor: Callable[..., tuple[int, dict]] = execute,
              input_fn: Callable[[str], str] = input,
              emit: Callable[[str], None] = print,
              clock: Callable[[], float] = time.time,
              is_tty: Callable[[], bool] = lambda: sys.stdin.isatty()) -> int:
    if not is_tty():
        emit("BLOCKED: actual operating acceptance requires an interactive TTY.")
        return 3
    report = trial_plan(target, planner=planner, clock=clock)
    emit("\nOne-switch operating acceptance — independent DGX test")
    emit("  Source: " + str(report.get("source_model") or "unverified"))
    emit("  Target: " + target + " / port :8000")
    emit("  Status: " + report["status"])
    emit("  This action WILL interrupt the active API. Open WebUI and clients may fail.")
    emit("  Existing Flash/27B containers, images, HF caches stay preserved.")
    emit("  There will be NO automatic return to the original active model after PASS.")
    for issue in report["issues"]:
        emit("  Blocker: " + issue)
    if report["status"] != "READY_FOR_SEPARATE_TRIAL_APPROVAL":
        emit("  No GPU/HTTP mutation dispatched.")
        return 3

    token = report["execution_plan_id"]
    emit("  Approval plan SHA: " + token)
    emit("  Expires at epoch seconds: " + str(report["expires_at_epoch_seconds"]))
    approvals = (
        (ACCEPTANCE_ACK,
         "Type " + ACCEPTANCE_ACK + " (Enter cancels): "),
        (token, "Type the exact displayed plan SHA (Enter cancels): "),
        (ACK_DOWNTIME, "Type " + ACK_DOWNTIME + " (Enter cancels): "),
        (ACK_TARGET[target],
         "Type " + ACK_TARGET[target] + " (Enter cancels): "),
    )
    for expected, prompt in approvals:
        try:
            supplied = input_fn(prompt)
        except (EOFError, KeyboardInterrupt, StopIteration):
            emit("CANCELLED: zero model-switch actions dispatched.")
            return 0
        if supplied != expected:
            emit("CANCELLED: exact approval mismatch; no switch dispatched.")
            return 0

    # User input may cross the ten-minute window. Do NOT substitute a new
    # plan SHA automatically or silently carry approvals to another window.
    if trial_plan(target, planner=planner, clock=clock).get("execution_plan_id") != token:
        emit("BLOCKED: plan changed/expired after the four approvals; replan needed.")
        return 3
    code, result = executor(target, token, ACK_DOWNTIME, ACK_TARGET[target])
    emit("  Live transition result: " + str(result.get("status")))
    emit("  Observed model: " + str(result.get("active_model") or "UNVERIFIED"))
    if result.get("evidence"):
        emit("  Private execution receipt: " + str(result["evidence"]))
    for issue in result.get("issues") or []:
        emit("  Issue: " + str(issue))
    if code != 0:
        emit("  NO BLIND RETRY. Inspect actual API and private journal first.")
    return code


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Separate approved ordinary switch acceptance")
    p.add_argument("--target", required=True)
    group = p.add_mutually_exclusive_group()
    group.add_argument("--plan", action="store_true")
    group.add_argument("--execute", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    if args.execute and args.json:
        print(json.dumps({"status": "BLOCKED", "executed": False,
                          "issues": ["LIVE_ACCEPTANCE_JSON_MODE_FORBIDDEN"]}))
        return 3
    if args.execute:
        return run_trial(args.target)
    report = trial_plan(args.target)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print("Operating acceptance plan: " + report["status"])
        print("Current: " + str(report.get("source_model") or "unknown")
              + " -> " + args.target)
        for issue in report.get("issues", []):
            print("  " + issue)
        print("Read-only. No model change has occurred.")
    return 0 if report["status"] == "READY_FOR_SEPARATE_TRIAL_APPROVAL" else 3


if __name__ == "__main__":
    raise SystemExit(main())
