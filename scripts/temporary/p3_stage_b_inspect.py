"""D-016 read-only P3-B inspection after verified, persistent P3-A success.

This module deliberately exposes NO execute mode. It proves staged identity,
P3-A receipt provenance and a fresh but short-lived P3-B *plan*. It neither
requests nor grants downtime permission, and it never stops/starts services.
"""
from __future__ import annotations

from datetime import datetime, timezone
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any
from uuid import uuid4

from scripts.temporary.p1_pre_a_readiness import private_json
from scripts.temporary.p3_stage_a_operator import run_readonly, git_clean

HOME = Path.home()
ROOT = Path(__file__).resolve().parents[2]
STATE = HOME / ".local/state/blazux-wizard/p3"
REPORTS = HOME / "blazux-p3-reports"
FLASH = "flash-next"
MODEL = "27b"
FLASH_ID = "qwen3.8-flash-next"
MODEL_ID = "qwen3.8-27b"
SHA64 = re.compile(r"^[0-9a-f]{64}$")
IMAGE = re.compile(r"^sha256:[0-9a-f]{64}$")


def receipt_issues(doc: dict[str, Any]) -> list[str]:
    issues = []
    if (doc.get("schema_version") != 1 or doc.get("stage") != "a"
            or doc.get("status") != "PASS" or doc.get("executed") is not True
            or doc.get("live_verified") is not True
            or doc.get("source_model") != FLASH or doc.get("target_model") != MODEL):
        issues.append("P3_A_SUCCESS_RECEIPT_NOT_QUALIFIED")
    for key in ("plan_id", "source_id", "target_id", "flash_id",
                "id_27b", "p2_receipt_sha256"):
        if not SHA64.fullmatch(str(doc.get(key) or "")):
            issues.append("P3_A_RECEIPT_IMMUTABLE_IDS_MISSING")
            break
    for key in ("source_image", "target_image", "flash_image", "image_27b"):
        if not IMAGE.fullmatch(str(doc.get(key) or "")):
            issues.append("P3_A_RECEIPT_IMMUTABLE_IMAGES_MISSING")
            break
    if (doc.get("source_id") != doc.get("flash_id")
            or doc.get("target_id") != doc.get("id_27b")
            or doc.get("source_image") != doc.get("flash_image")
            or doc.get("target_image") != doc.get("image_27b")):
        issues.append("P3_A_RECEIPT_INTERNAL_IDENTITY_DRIFT")
    try:
        t = datetime.fromisoformat(doc["finished_at_utc"].replace("Z", "+00:00"))
        if t.tzinfo is None or t > datetime.now(timezone.utc):
            raise ValueError()
    except (KeyError, ValueError, TypeError, AttributeError):
        issues.append("P3_A_RECEIPT_TIMESTAMP_INVALID")
    return sorted(set(issues))


def preflight_issues(receipt: dict[str, Any], live: dict[str, Any],
                     plan: dict[str, Any], *, now_epoch: int | None = None) -> list[str]:
    """Inspection assertions only. Even READY does not imply permission to execute."""
    from time import time
    now = time() if now_epoch is None else now_epoch
    issues = receipt_issues(receipt)
    active = live.get("active_container") or {}
    if (live.get("status") != "LIVE_SERVICE_VERIFIED"
            or live.get("observed_model") != MODEL
            or live.get("expected_served_id") != MODEL_ID
            or live.get("observed_model_ids") != [MODEL_ID]
            or live.get("issues") != []
            or live.get("host_port") != 8000
            or active.get("name") != "qwen38-27b"
            or active.get("image_id") != receipt.get("target_image")):
        issues.append("P3_B_SOURCE_27B_LIVE_MANIFEST_API_UNVERIFIED")
    if (plan.get("status") != "READY_TO_REQUEST_TRANSITION_APPROVAL"
            or plan.get("stage") != "b" or plan.get("source_model") != MODEL
            or plan.get("target_model") != FLASH
            or plan.get("issues") != []
            or plan.get("executed") is not False
            or plan.get("operations_enabled") is not False
            or plan.get("approval_accepted") is not False
            or not SHA64.fullmatch(str(plan.get("plan_id") or ""))):
        issues.append("P3_B_FRESH_PLAN_NOT_READY")
    if (plan.get("source_container_id") != receipt.get("target_id")
            or plan.get("target_container_id") != receipt.get("source_id")
            or plan.get("source_image") != receipt.get("target_image")
            or plan.get("target_image") != receipt.get("source_image")
            or plan.get("flash_id") != receipt.get("flash_id")
            or plan.get("image_27b") != receipt.get("image_27b")
            or plan.get("p3_a_plan_id") != receipt.get("plan_id")
            or plan.get("p2_receipt_sha256") != receipt.get("p2_receipt_sha256")):
        issues.append("P3_B_PRESERVED_CONTAINERS_OR_PROVENANCE_DRIFT")
    if (plan.get("required_downtime_acknowledgement")
            != "I_ACCEPT_FLASH_NEXT_DOWNTIME"
            or plan.get("required_p3_entry_acknowledgement") is not None):
        issues.append("P3_B_APPROVAL_CONTRACT_CHANGED")
    expires = plan.get("expires_at_epoch_seconds")
    if type(expires) not in (int, float) or expires <= now:
        issues.append("P3_B_PLAN_ALREADY_EXPIRED")
    return sorted(set(issues))


def save_summary(doc: dict[str, Any], root: Path = REPORTS) -> Path:
    root = root.expanduser()
    if root.is_symlink():
        raise ValueError("REPORT_DIRECTORY_SYMLINK")
    root = root.resolve()
    cache = Path(os.environ.get("HF_CACHE", str(HOME / ".cache/huggingface"))).resolve()
    if root.is_relative_to(ROOT.resolve()) or root.is_relative_to(cache):
        raise ValueError("REPORT_DIRECTORY_INSIDE_GIT_OR_CACHE")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.stat().st_mode & 0o077:
        raise ValueError("REPORT_DIRECTORY_PERMISSIONS_UNSAFE")
    path = root / ("p3-b-inspect-" +
                   datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") +
                   "-" + uuid4().hex[:8] + ".json")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as fp:
        json.dump(doc, fp, indent=2, sort_keys=True, ensure_ascii=False)
        fp.write("\n")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage-a-receipt", type=Path, default=STATE / "stage-a.json")
    args = ap.parse_args(argv)
    try:
        receipt = private_json(args.stage_a_receipt, STATE, max_size=65536)
        issues = []
    except (OSError, ValueError, TypeError):
        receipt = {}
        issues = ["P3_A_PRIVATE_RECEIPT_MISSING_OR_UNTRUSTED"]
    if not git_clean():
        issues.append("GIT_BRANCH_OR_WORKTREE_UNVERIFIED")
    live_rc, live = run_readonly(
        ["./wizard.sh", "service", "manager", "status", "--json"])
    plan_rc, plan = run_readonly(
        ["./wizard.sh", "switch", "flash-next-27b", "stage-b", "--plan", "--json"])
    if live_rc != 0:
        issues.append("P3_B_CURRENT_SERVICE_OBSERVATION_FAILED")
    if plan_rc != 0:
        issues.append("P3_B_CANONICAL_PLAN_BLOCKED")
    issues.extend(preflight_issues(receipt, live, plan))
    report = {
        "schema_version": 1, "stage": "P3_B_READ_ONLY_PREPARATION",
        "status": "READY_FOR_SEPARATE_P3_B_APPROVAL" if not issues else "BLOCKED",
        "issues": sorted(set(issues)), "executed": False,
        "operations_enabled": False, "approval_accepted": False,
        "current_model": live.get("observed_model"),
        "current_model_ids": live.get("observed_model_ids"),
        "expected_source_id": MODEL_ID, "expected_target_id": FLASH_ID,
        "stage_a_plan_id": receipt.get("plan_id"),
        "stage_a_receipt": str(args.stage_a_receipt),
        "stage_b_plan_id": plan.get("plan_id") if not issues else None,
        "stage_b_plan_expires_at_epoch_seconds": plan.get("expires_at_epoch_seconds"),
        "source_container_id": plan.get("source_container_id"),
        "preserved_flash_container_id": plan.get("target_container_id"),
        "current_27b_image": plan.get("source_image"),
        "preserved_flash_image": plan.get("target_image"),
        "p2_receipt_sha256": receipt.get("p2_receipt_sha256"),
        "notice": ("READ-ONLY. P3-B has NOT been separately authorized. "
                   "No Docker stop/start, GPU workload, approval injection, "
                   "automatic P1 benchmark, or stage C. Stage B would "
                   "interrupt the live 27B API on :8000, restore preserved "
                   "Flash-Next and need fresh operator approval."),
    }
    report["evidence_file"] = str(save_summary(report))
    print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if not report["issues"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
