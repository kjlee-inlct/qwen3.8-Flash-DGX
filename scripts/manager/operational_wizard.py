"""Guided ordinary-switch operator experience; production dispatch remains locked.

P3 A/B/C are immutable historical evidence, never the recurring switch entry.
The operator selects one target, reviews an observed candidate, then supplies a
fresh execution-specific SHA and two exact, independent acknowledgments.
A source-only CPU simulation can inject a qualified gate to exercise the
backend; the user-facing Wizard MUST remain non-executable until real DGX
qualification and explicit release. No flag, environment variable, or input
can override this production gate.
"""
from __future__ import annotations

import json
import sys
import time
from typing import Any, Callable

from scripts.manager import operational_executor
from scripts.manager.operational_switch import make_plan, READY, SUPPORTED


# Deliberately not a CLI flag or environment toggle. Changing this requires
# reviewed source, CPU CI, and independently approved live switch acceptance.
PRODUCTION_EXECUTION_RELEASED = False


def guided(
    target: str, *, planner: Callable[[str], dict] = make_plan,
    executor: Callable[..., tuple[int, dict]] = operational_executor.execute,
    input_fn: Callable[[str], str] = input,
    emit: Callable[[str], None] = print,
    release_qualified: bool | None = None,
    review_only: bool = False,
    require_tty: bool = True,
    is_tty: Callable[[], bool] = lambda: sys.stdin.isatty(),
    clock: Callable[[], float] = time.time,
) -> int:
    """Review first; production dispatch stays locked pending DGX acceptance.

    Tests explicitly inject a fake executor, clock and release_qualified=True.
    After a future independently reviewed source release, the normal menu
    needs no hidden second flag to reach the same approval flow.
    """
    if target not in SUPPORTED:
        emit("BLOCKED: target is not a qualified Flash-Next/27B model.")
        return 3
    try:
        preview = planner(target)
    except (OSError, ValueError, RuntimeError, TypeError):
        emit("BLOCKED: fresh ordinary-switch preflight unavailable.")
        return 3

    emit("\nOrdinary operating model switch — guided review")
    emit("  Active: " + str(preview.get("source_model") or "unverified"))
    emit("  Requested: " + target)
    emit("  Stable external API: :8000/v1")
    emit("  Preview status: " + str(preview.get("status")))
    emit("  Planned service downtime: required; no automatic approval")
    emit("  Existing model image, container, and HF cache stay preserved")
    emit("  Historical P3 A/B/C will NOT be replayed")
    for issue in preview.get("issues") or []:
        emit("  Blocker: " + str(issue))
    if preview.get("status") != READY:
        emit("BLOCKED: candidate has not passed current identity checks.")
        return 3

    fingerprint = preview.get("plan_id")
    emit("  Read-only preview fingerprint (NOT executable): " + str(fingerprint))
    token = operational_executor.execution_plan_id(preview)
    if token is None:
        emit("BLOCKED: independent execution approval cannot be constructed.")
        return 3
    expiry = preview.get("expires_at_epoch_seconds")
    try:
        remaining = int(float(expiry) - clock())
    except (TypeError, ValueError, OverflowError):
        emit("BLOCKED: invalid plan expiry; no operating action.")
        return 3
    emit("  Seconds remaining in plan window: " + str(max(0, remaining)))
    if review_only:
        emit("REVIEW_ONLY: no approval solicited, no service changes.")
        return 0
    if release_qualified is None:
        release_qualified = PRODUCTION_EXECUTION_RELEASED
    if not release_qualified or not PRODUCTION_EXECUTION_RELEASED:
        # Source gate is not a runtime environment toggle. An earlier P3
        # successful transition is not approval to release this new backend.
        emit("RELEASE_GATED: guided review works; live execution NOT QUALIFIED.")
        emit("  No Docker stop/start, no P3 replay, no new operating journal.")
        return 3
    if remaining < 120:
        emit("BLOCKED: approval window has less than 120 seconds remaining.")
        emit("  Refresh the review after the plan window rotates; old SHA is invalid.")
        return 3
    if require_tty and not is_tty():
        emit("BLOCKED: independent approval requires an interactive TTY.")
        return 3

    emit("  Exact independent execution plan: " + token)
    emit("  Expires at epoch seconds: "
         + str(preview.get("expires_at_epoch_seconds")))
    approvals = (
        (token, "Type exact execution plan SHA (Enter cancels): "),
        (operational_executor.ACK_DOWNTIME,
         "Type I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME (Enter cancels): "),
        (operational_executor.ACK_TARGET[target],
         "Type " + operational_executor.ACK_TARGET[target]
         + " (Enter cancels): "),
    )
    for expected, prompt in approvals:
        try:
            entered = input_fn(prompt)
        except (EOFError, KeyboardInterrupt):
            emit("CANCELLED: no execution dispatched.")
            return 0
        if entered != expected:
            emit("CANCELLED: exact approval mismatch; nothing dispatched.")
            return 0

    # The backend independently re-evaluates current API, Docker, receipts,
    # protected containers, journal, exact SHA and two acknowledgements.
    code, result = executor(
        target, token, operational_executor.ACK_DOWNTIME,
        operational_executor.ACK_TARGET[target],
    )
    emit("  Operating result: " + str(result.get("status")))
    emit("  Current model after action: "
         + str(result.get("active_model") or "UNVERIFIED"))
    for issue in result.get("issues") or []:
        emit("  Issue: " + str(issue))
    if result.get("evidence"):
        emit("  Local private evidence: " + str(result["evidence"]))
    return code


def main(argv: list[str] | None = None) -> int:
    """Read-only by default; --execute always requires a released TTY Wizard."""
    import argparse
    parser = argparse.ArgumentParser(description="Guided routine operating switch")
    parser.add_argument("--target", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    parser.add_argument("--ack-target")
    args = parser.parse_args(argv)
    # No approval secrets may be supplied non-interactively on argv.
    if (args.approve_plan is not None or args.ack_downtime is not None
            or args.ack_target is not None or
            (args.execute and not PRODUCTION_EXECUTION_RELEASED)):
        print(json.dumps({"status": "RELEASE_GATED", "executed": False,
                          "issues": ["GENERAL_OPERATING_SWITCH_NOT_DGX_QUALIFIED"
                                     if args.execute and not PRODUCTION_EXECUTION_RELEASED
                                     else "NONINTERACTIVE_APPROVAL_REFUSED"]}))
        return 3
    return guided(args.target, review_only=not args.execute)


if __name__ == "__main__":
    raise SystemExit(main())
