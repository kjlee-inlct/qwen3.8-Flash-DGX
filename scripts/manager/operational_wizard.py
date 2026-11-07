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
    release_qualified: bool = False,
    require_tty: bool = True,
    is_tty: Callable[[], bool] = lambda: sys.stdin.isatty(),
) -> int:
    """Review first; only test-injected qualified flows can dispatch.

    CLI/TTY always calls with the default non-executable release gate.
    Acceptance tests inject a mock executor and release_qualified=True.
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
    if not release_qualified or not PRODUCTION_EXECUTION_RELEASED:
        # Neither a menu click nor a typed preview SHA can release a real GPU.
        # The fake-CPU tests patch PRODUCTION_EXECUTION_RELEASED while injecting
        # a mock executor; the production constant stays false.
        emit("RELEASE_GATED: guided review works; live execution NOT QUALIFIED.")
        emit("  No Docker stop/start, no P3 replay, no new operating journal.")
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
    """Only a read-only guided review is currently exposed to users."""
    import argparse
    parser = argparse.ArgumentParser(description="Guided routine operating switch")
    parser.add_argument("--target", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    parser.add_argument("--ack-target")
    args = parser.parse_args(argv)
    if (args.execute or args.approve_plan is not None
            or args.ack_downtime is not None or args.ack_target is not None):
        print(json.dumps({"status": "RELEASE_GATED", "executed": False,
                          "issues": ["GENERAL_OPERATING_SWITCH_NOT_DGX_QUALIFIED"]}))
        return 3
    return guided(args.target)


if __name__ == "__main__":
    raise SystemExit(main())
