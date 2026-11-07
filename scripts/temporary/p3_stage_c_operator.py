"""Tracked P3-C operator: final preserved Flash-Next -> NVIDIA 27B.

Default --plan is non-disruptive; no GPU or Docker mutation. --execute
requires a *fresh* independent SHA plan, Flash-Next downtime acknowledgement,
and a C-only final-entry acknowledgement typed in a real TTY. Only the
canonical guarded Wizard executor may perform the actual transition.
P3-A/B approvals and old C plans are never reused. After successful C,
27B intentionally remains serving :8000 and Flash-Next stays preserved.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any
from uuid import uuid4

from scripts.temporary.p1_pre_a_readiness import private_json
from scripts.temporary.p3_stage_a_operator import git_clean, run_readonly

ROOT = Path(__file__).resolve().parents[2]
P3_ROOT = Path.home() / ".local/state/blazux-wizard/p3"
REPORT_ROOT = ROOT / "reports" / "transitions" / "flash-next--to--27b"
A_RECEIPT = P3_ROOT / "stage-a.json"
B_RECEIPT = P3_ROOT / "stage-b.json"
C_RECEIPT = P3_ROOT / "stage-c.json"
FLASH = "flash-next"
TARGET = "27b"
FLASH_ID = "qwen3.8-flash-next"
TARGET_ID = "qwen3.8-27b"
FLASH_CONTAINER = "qwen38-flash"
TARGET_CONTAINER = "qwen38-27b"
DOWNTIME_ACK = "I_ACCEPT_FLASH_NEXT_DOWNTIME"
# Wrapper-local, additional opt-in; core Stage C requires no --enter-p3.
C_ENTRY_ACK = "I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C"
SHA64 = re.compile(r"^[0-9a-f]{64}$")
IMAGE = re.compile(r"^sha256:[0-9a-f]{64}$")
READY = "READY_TO_REQUEST_TRANSITION_APPROVAL"


def get_plan_and_live() -> tuple[int | None, dict, int | None, dict]:
    """Both CLI calls are strictly read-only; never executes a switch."""
    live_rc, live = run_readonly(
        ["./wizard.sh", "service", "manager", "status", "--json"])
    plan_rc, plan = run_readonly(
        ["./wizard.sh", "switch", "flash-next-27b", "stage-c", "--plan", "--json"])
    return live_rc, live, plan_rc, plan


def expiry_kst(epoch: Any) -> str:
    try:
        if type(epoch) not in (int, float):
            return "UNKNOWN"
        return datetime.fromtimestamp(epoch, timezone(timedelta(hours=9))).strftime(
            "%Y-%m-%d %H:%M:%S KST")
    except (ValueError, OverflowError, OSError):
        return "UNKNOWN"


def _utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("TIMESTAMP_MISSING")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("TIMESTAMP_NAIVE")
    return dt.astimezone(timezone.utc)


def receipt_issues(a: dict, b: dict, *, now: datetime | None = None) -> list[str]:
    """Validate original canonical A and B facts, not historical operator names."""
    problems = []
    now = now or datetime.now(timezone.utc)
    for stage, doc, source, target in (("a", a, FLASH, TARGET),
                                       ("b", b, TARGET, FLASH)):
        if (doc.get("schema_version") != 1 or doc.get("stage") != stage
                or doc.get("status") != "PASS" or doc.get("executed") is not True
                or doc.get("live_verified") is not True
                or doc.get("source_model") != source
                or doc.get("target_model") != target):
            problems.append("P3_" + stage.upper() + "_CANONICAL_SUCCESS_RECEIPT_INVALID")
        for key in ("plan_id", "source_id", "target_id", "flash_id", "id_27b",
                    "p2_receipt_sha256"):
            if not SHA64.fullmatch(str(doc.get(key) or "")):
                problems.append("P3_" + stage.upper() + "_IMMUTABLE_IDS_INVALID")
                break
        for key in ("source_image", "target_image", "flash_image", "image_27b"):
            if not IMAGE.fullmatch(str(doc.get(key) or "")):
                problems.append("P3_" + stage.upper() + "_IMAGE_IDS_INVALID")
                break
    if (a.get("source_id") != a.get("flash_id")
            or a.get("target_id") != a.get("id_27b")
            or b.get("source_id") != a.get("id_27b")
            or b.get("target_id") != a.get("flash_id")
            or b.get("flash_id") != a.get("flash_id")
            or b.get("id_27b") != a.get("id_27b")
            or b.get("flash_image") != a.get("flash_image")
            or b.get("image_27b") != a.get("image_27b")
            or b.get("source_image") != a.get("image_27b")
            or b.get("target_image") != a.get("flash_image")
            or b.get("p2_receipt_sha256") != a.get("p2_receipt_sha256")):
        problems.append("P3_A_B_PRESERVED_CONTAINER_PROVENANCE_DRIFT")
    try:
        at, bt = _utc(a.get("finished_at_utc")), _utc(b.get("finished_at_utc"))
        if not (at <= bt <= now):
            problems.append("P3_A_B_RECEIPT_TIMELINE_INVALID")
    except (ValueError, TypeError, OverflowError):
        problems.append("P3_A_B_RECEIPT_TIMESTAMP_INVALID")
    return sorted(set(problems))


def review(a: dict, b: dict, live: dict, plan: dict,
           live_rc: int | None, plan_rc: int | None, *,
           clean: bool, now_epoch: float | None = None) -> list[str]:
    """A current, proven A+B+P1/P2 chain is required before any C approval."""
    now = time.time() if now_epoch is None else now_epoch
    problems = receipt_issues(a, b, now=datetime.fromtimestamp(now, timezone.utc))
    if live_rc != 0:
        problems.append("P3_C_LIVE_API_STATUS_COMMAND_FAILED")
    if plan_rc != 0:
        problems.append("P3_C_CANONICAL_PLAN_COMMAND_FAILED")
    if not clean:
        problems.append("P3_C_GIT_BRANCH_OR_WORKTREE_NOT_VERIFIED")
    active = live.get("active_container") or {}
    if (live.get("status") != "LIVE_SERVICE_VERIFIED"
            or live.get("observed_model") != FLASH
            or live.get("expected_served_id") != FLASH_ID
            or live.get("observed_model_ids") != [FLASH_ID]
            or live.get("host_port") != 8000
            or live.get("issues") != []
            or active.get("name") != FLASH_CONTAINER
            or active.get("image_id") != a.get("flash_image")):
        problems.append("P3_C_LIVE_FLASH_SOURCE_UNVERIFIED")
    if (plan.get("status") != READY or plan.get("schema_version") != 1
            or plan.get("stage") != "c"
            or plan.get("source_model") != FLASH
            or plan.get("target_model") != TARGET
            or plan.get("issues") != []
            or plan.get("executed") is not False
            or plan.get("operations_enabled") is not False
            or plan.get("approval_accepted") is not False
            or not SHA64.fullmatch(str(plan.get("plan_id") or ""))):
        problems.append("P3_C_FRESH_PLAN_NOT_READY")
    if (plan.get("source_container_id") != a.get("flash_id")
            or plan.get("target_container_id") != a.get("id_27b")
            or plan.get("source_image") != a.get("flash_image")
            or plan.get("target_image") != a.get("image_27b")
            or plan.get("flash_id") != a.get("flash_id")
            or plan.get("id_27b") != a.get("id_27b")
            or plan.get("image_27b") != a.get("image_27b")
            or plan.get("p3_a_plan_id") != a.get("plan_id")
            or plan.get("p2_receipt_sha256") != a.get("p2_receipt_sha256")):
        problems.append("P3_C_PRESERVED_TARGET_OR_PROVENANCE_DRIFT")
    gate = plan.get("p1_evidence")
    hashes = gate.get("evidence_hashes") if isinstance(gate, dict) else None
    if (not isinstance(gate, dict) or gate.get("status") != "PASS"
            or gate.get("issues") != []
            or gate.get("stage_b_finished_at_utc") != b.get("finished_at_utc")
            or not isinstance(hashes, dict)
            or not all(SHA64.fullmatch(str(hashes.get(k) or ""))
                       for k in ("verify", "benchmark", "diagnostics"))):
        problems.append("P3_C_POST_B_FLASH_VERIFY_BENCH_DIAGNOSTICS_NOT_QUALIFIED")
    if (plan.get("required_downtime_acknowledgement") != DOWNTIME_ACK
            or plan.get("required_p3_entry_acknowledgement") is not None):
        problems.append("P3_C_CANONICAL_APPROVAL_CONTRACT_CHANGED")
    expires = plan.get("expires_at_epoch_seconds")
    if type(expires) not in (int, float) or expires <= now:
        problems.append("P3_C_PLAN_EXPIRED")
    return sorted(set(problems))


def confirm(plan: dict, *, input_fn=input) -> bool:
    """Three independently typed values; no abbreviated COPY/y/auto approvals."""
    try:
        parts = (
            ("1/3 Current C-only SHA-256 plan", plan["plan_id"]),
            ("2/3 Stop ACTIVE Flash-Next on :8000", DOWNTIME_ACK),
            ("3/3 Final 27B activation; NO automatic switch back", C_ENTRY_ACK),
        )
        print("\nP3-C FINAL 27B requires THREE NEW confirmations.", flush=True)
        print("P3-A/B or evidence-import consent is NOT approval for C.", flush=True)
        print("Expires: " + expiry_kst(plan["expires_at_epoch_seconds"]), flush=True)
        for title, value in parts:
            print(f"{title}: {value}", flush=True)
            if input_fn(f"Type exactly [{value}] (Enter cancels): ").strip() != value:
                return False
        return True
    except (KeyError, TypeError, ValueError, EOFError, KeyboardInterrupt):
        return False


def post_status_ok(live: dict, c: dict, plan: dict) -> bool:
    active = live.get("active_container") or {}
    return (live.get("status") == "LIVE_SERVICE_VERIFIED"
            and live.get("observed_model") == TARGET
            and live.get("expected_served_id") == TARGET_ID
            and live.get("observed_model_ids") == [TARGET_ID]
            and live.get("issues") == []
            and live.get("host_port") == 8000
            and active.get("name") == TARGET_CONTAINER
            and active.get("image_id") == plan.get("target_image")
            and c.get("schema_version") == 1
            and c.get("stage") == "c"
            and c.get("status") == "PASS"
            and c.get("executed") is True
            and c.get("live_verified") is True
            and c.get("plan_id") == plan.get("plan_id")
            and c.get("source_id") == plan.get("source_container_id")
            and c.get("target_id") == plan.get("target_container_id")
            and c.get("source_model") == FLASH
            and c.get("target_model") == TARGET
            and c.get("p2_receipt_sha256") == plan.get("p2_receipt_sha256"))


def persist(doc: dict, *, root: Path = REPORT_ROOT) -> str:
    """Private append-only user report, Git ignored; canonical P3 state stays put."""
    if root.is_symlink() or not root.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError("P3_C_REPORT_PATH_UNSAFE")
    reports = ROOT / "reports"
    if not root.is_relative_to(reports):
        raise ValueError("P3_C_REPORT_OUTSIDE_PROJECT")
    directory = reports
    for part in ("", *root.relative_to(reports).parts):
        if part:
            directory = directory / part
        directory.mkdir(mode=0o700, parents=(directory == reports), exist_ok=True)
        if directory.is_symlink() or not directory.is_dir() or directory.stat().st_mode & 0o077:
            raise ValueError("P3_C_REPORT_DIRECTORY_UNSAFE")
    path = root / ("p3-c-operator-" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:12] + ".json")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(doc, stream, indent=2, sort_keys=True, ensure_ascii=False)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return str(path)


def emit(report: dict, *, rc: int) -> int:
    try:
        report["evidence_file"] = persist(report)
    except (OSError, ValueError, TypeError) as exc:
        report["evidence_write_error"] = type(exc).__name__
        if report.get("execution_dispatched"):
            report["status"] = "OPERATOR_REVIEW_REQUIRED"
            report["issues"] = sorted(set(report.get("issues", []) +
                                          ["P3_C_OPERATOR_REPORT_NOT_DURABLE"]))
            rc = 4
        else:
            report["status"] = "BLOCKED"
            report["issues"] = sorted(set(report.get("issues", []) +
                                          ["P3_C_OPERATOR_REPORT_PATH_UNAVAILABLE"]))
            rc = 3
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False), flush=True)
    return rc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--plan", action="store_true", help="default, read-only")
    mode.add_argument("--execute", action="store_true",
                      help="EXPLICIT real Flash-Next downtime, 3 new manual confirmations")
    args = parser.parse_args(argv)
    issues: list[str] = []
    try:
        a = private_json(A_RECEIPT, P3_ROOT, max_size=65536)
        b = private_json(B_RECEIPT, P3_ROOT, max_size=65536)
    except (OSError, ValueError, TypeError):
        a, b = {}, {}
        issues.append("P3_A_B_CANONICAL_RECEIPTS_MISSING_OR_UNTRUSTED")
    live_rc, live, plan_rc, plan = get_plan_and_live()
    issues.extend(review(a, b, live, plan, live_rc, plan_rc, clean=git_clean()))
    report = {
        "schema_version": 1,
        "stage": "P3_C_OPERATOR_GUARDED_FINAL_27B",
        "source_model": FLASH, "target_model": TARGET,
        "status": ("BLOCKED" if issues else
                   "READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL"),
        "issues": sorted(set(issues)),
        "current_model": live.get("observed_model"),
        "current_model_ids": live.get("observed_model_ids"),
        "source_container_id": plan.get("source_container_id"),
        "target_container_id": plan.get("target_container_id"),
        "flash_image": plan.get("flash_image"),
        "target_image": plan.get("target_image"),
        "plan_id": plan.get("plan_id") if not issues else None,
        "expires_at_epoch_seconds": plan.get("expires_at_epoch_seconds"),
        "expires_at_kst": expiry_kst(plan.get("expires_at_epoch_seconds")),
        "p1_evidence": plan.get("p1_evidence"),
        "p2_receipt_sha256": plan.get("p2_receipt_sha256"),
        "stage_a_receipt": str(A_RECEIPT),
        "stage_b_receipt": str(B_RECEIPT),
        "executed": False, "operations_enabled": False,
        "execution_dispatched": False, "approval_accepted": False,
        "notice": (
            "Stage-C FINAL Flash-Next -> preserved 27B. --plan does not stop "
            "services. --execute requires independent current exact C SHA, "
            "Flash downtime and final 27B-only manual acknowledgment. "
            "Canonical Wizard rechecks plan under its transition lock and "
            "retains Flash for rollback. On successful C, 27B stays active "
            "on :8000; no auto switch-back. On failure, stop and reconcile."),
    }
    if issues or not args.execute:
        return emit(report, rc=3 if issues else 0)
    if not sys.stdin.isatty():
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_C_REAL_TTY_REQUIRED"]
        return emit(report, rc=3)
    expires = plan.get("expires_at_epoch_seconds")
    if type(expires) not in (int, float) or expires - time.time() < 120:
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS"]
        return emit(report, rc=3)
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False),
          flush=True)
    print("\nDOWNTIME WARNING: The LIVE qwen3.8-flash-next API on :8000 will stop.",
          "The saved original NVIDIA 27B container will start, with the same",
          ":8000 port. OpenWebUI/clients may see an API outage.",
          "Flash cache/image/container are preserved; rollback on fault is",
          "best effort (host or Docker daemon failure may defeat recovery).",
          flush=True)
    if not confirm(plan):
        report["status"] = "CANCELLED"
        report["issues"] = ["P3_C_THREE_INDEPENDENT_CONFIRMATIONS_INCOMPLETE"]
        return emit(report, rc=3)
    report["approval_accepted"] = True
    # Fresh plan must match the plan *actually typed* by the operator.
    now = time.time()
    live2_rc, live2, plan2_rc, plan2 = get_plan_and_live()
    if (expires - now < 15
            or plan2.get("plan_id") != plan.get("plan_id")
            or review(a, b, live2, plan2, live2_rc, plan2_rc,
                      clean=git_clean(), now_epoch=now)):
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_C_TYPED_PLAN_EXPIRED_OR_RUNTIME_CHANGED"]
        return emit(report, rc=3)
    # NO --enter-p3: canonical C requires null (wrapper adds a third input).
    cmd = ["./wizard.sh", "switch", "flash-next-27b", "stage-c",
           "--execute", "--approve-plan", plan["plan_id"],
           "--ack-downtime", DOWNTIME_ACK, "--json"]
    report["operations_enabled"] = True
    report["execution_dispatched"] = True
    try:
        result_rc, result = run_readonly(cmd, timeout=900)
    except KeyboardInterrupt:
        report["status"] = "OPERATOR_REVIEW_REQUIRED"
        report["issues"] = ["P3_C_INTERRUPTED_AFTER_DISPATCH"]
        return emit(report, rc=4)
    report["wizard_result"] = result
    report["execute_command_exit_code"] = result_rc
    report["executed"] = result.get("executed") is True
    if (result_rc == 0 and result.get("status") == "PASS"
            and result.get("stage") == "c" and result.get("executed") is True
            and result.get("live_verified") is True
            and result.get("active_model") == TARGET):
        live3_rc, live3 = run_readonly(
            ["./wizard.sh", "service", "manager", "status", "--json"])
        try:
            c = private_json(C_RECEIPT, P3_ROOT, max_size=65536)
        except (OSError, ValueError, TypeError):
            c = {}
        report["post_switch_status"] = live3.get("status")
        report["post_switch_observed_model"] = live3.get("observed_model")
        report["canonical_c_receipt"] = str(C_RECEIPT)
        if live3_rc == 0 and post_status_ok(live3, c, plan):
            report["status"] = "P3_C_PASS_FINAL_27B_ACTIVE"
            report["issues"] = []
            return emit(report, rc=0)
        report["status"] = "OPERATOR_REVIEW_REQUIRED"
        report["issues"] = ["P3_C_FINAL_27B_OR_IMMUTABLE_RECEIPT_NOT_VERIFIED"]
        return emit(report, rc=4)
    if (result_rc == 3 and result.get("executed") is False
            and "P3_STALE_PLAN_OR_CHANGED_PREFLIGHT" in result.get("issues", [])):
        report["status"] = "BLOCKED"
        report["issues"] = ["P3_C_CANONICAL_WIZARD_REJECTED_STALE_PLAN"]
        return emit(report, rc=3)
    report["status"] = "OPERATOR_REVIEW_REQUIRED"
    report["issues"] = result.get("issues") or ["P3_C_EXECUTION_OR_RECOVERY_UNVERIFIED"]
    return emit(report, rc=4)


if __name__ == "__main__":
    raise SystemExit(main())
