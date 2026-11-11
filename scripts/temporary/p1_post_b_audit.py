"""D-016 POST-B P1 READ-ONLY audit. No GPU inference or service mutation.

Reuses the exact P1 inspect-only checks and canonical P3-C rc3 predicate.
Creates a new 0600 append-only private diagnosis; never rewrites past evidence.
This does NOT execute Verify, Benchmark, or P3-C, and grants no approval.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any
from uuid import uuid4

from scripts.manager.p3_p1_evidence_gate import (
    _expected_active_flash_collision, _read_private, _time,
)
from scripts.temporary.p1_post_download import (
    ROOT, session, cache_diagnosis_summary, api_model_ids,
)
from scripts.temporary.p3_stage_a_operator import run_readonly

P3_ROOT = Path.home() / ".local/state/blazux-wizard/p3"
FLASH_API = "qwen3.8-flash-next"
SHA_IMAGE = re.compile(r"^sha256:[0-9a-f]{64}$")
SHA_CONTAINER = re.compile(r"^[0-9a-f]{64}$")


def _raw_collision(check: Any, image: str) -> tuple[int | None, dict, bool]:
    if not isinstance(check, dict):
        return None, {}, False
    rc = check.get("returncode")
    if check.get("truncated") is not False:
        return rc, {}, False
    try:
        raw = json.loads(check.get("stdout", ""))
    except (TypeError, ValueError):
        return rc, {}, False
    valid = (rc == 3 and _expected_active_flash_collision(raw, image))
    return rc, raw if isinstance(raw, dict) else {}, valid


def assess(stage_b: dict, live_rc: int | None, live: dict,
           inspection: dict, *, stage_b_sha256: str = "",
           now: datetime | None = None) -> dict[str, Any]:
    """Pure fail-closed evaluation. Inspection is from session(inspect_only=True)."""
    now = now or datetime.now(timezone.utc)
    issues: list[str] = []
    image = stage_b.get("flash_image")
    if (stage_b.get("schema_version") != 1 or stage_b.get("stage") != "b"
            or stage_b.get("status") != "PASS"
            or stage_b.get("executed") is not True
            or stage_b.get("live_verified") is not True
            or stage_b.get("source_model") != "27b"
            or stage_b.get("target_model") != "flash-next"
            or not isinstance(image, str) or SHA_IMAGE.fullmatch(image) is None
            or stage_b.get("target_image") != image
            or not SHA_CONTAINER.fullmatch(str(stage_b.get("target_id") or ""))):
        issues.append("P3_B_ACTUAL_SUCCESS_RECEIPT_NOT_QUALIFIED")
    try:
        when = _time(stage_b["finished_at_utc"])
        if when > now or when.year < 2026:
            issues.append("P3_B_TIMESTAMP_INVALID")
    except (KeyError, TypeError, ValueError):
        issues.append("P3_B_TIMESTAMP_INVALID")
    active = live.get("active_container") or {}
    if (live_rc != 0 or live.get("status") != "LIVE_SERVICE_VERIFIED"
            or live.get("issues") != []
            or live.get("observed_model") != "flash-next"
            or live.get("expected_served_id") != FLASH_API
            or live.get("observed_model_ids") != [FLASH_API]
            or live.get("host_port") != 8000
            or active.get("name") != "qwen38-flash"
            or active.get("image_id") != image):
        issues.append("POST_B_FLASH_LIVE_IDENTITY_NOT_VERIFIED")
    pre = inspection.get("preflight") or {}
    if (inspection.get("scope") != "DGX_INSPECTION_AND_EXPLICITLY_APPROVED_API"
            or any(pre.get(k) is not True for k in (
                "branch_ok", "tracked_tree_clean", "runtime_allowed",
                "expected_api_model_present"))
            or (pre.get("operator_process") or {}).get("blocked") is not False
            or api_model_ids(inspection.get("checks") or {}) != [FLASH_API]):
        issues.append("P1_POST_B_READ_ONLY_PREFLIGHT_INCOMPLETE")
    for action in ("verify", "benchmark"):
        info = (inspection.get("plans") or {}).get(action) or {}
        state = (inspection.get("actions") or {}).get(action) or {}
        if (info.get("ready") is not True
                or (info.get("plan") or {}).get("issues") != []
                or state.get("executed") is not False
                or state.get("status") != "BLOCKED"
                or state.get("reason") != "inspection_only"):
            issues.append("P1_" + action.upper() + "_INSPECTION_NOT_READY")
    checks = inspection.get("checks") or {}
    doctor_rc, doctor_raw, doctor_good = _raw_collision(checks.get("doctor"), image)
    inventory_rc, inventory_raw, inventory_good = _raw_collision(
        checks.get("inventory_plan"), image)
    if not doctor_good or not inventory_good:
        issues.append("POST_B_DOCTOR_INVENTORY_RC3_CAUSE_UNVERIFIED")
    assets = cache_diagnosis_summary(checks).get("wizard_audit") or {}
    if (assets.get("state") != "READY"
            or assets.get("source_complete") is not True
            or assets.get("hybrid_ready") is not True
            or assets.get("source_issues") != []
            or assets.get("hybrid_issues") != []
            or assets.get("model_repo") != "nvidia/Qwen3.8-Flash-Next-NVFP4"
            or not re.fullmatch(r"[0-9a-f]{40}", str(assets.get("revision") or ""))):
        issues.append("P1_POST_B_PINNED_ASSET_AUDIT_NOT_READY")
    return {
        "schema_version": 1, "stage": "P1_POST_B_READ_ONLY_DIAGNOSTICS",
        "status": "PASS" if not issues else "BLOCKED",
        "issues": sorted(set(issues)),
        "doctor_exit_code": doctor_rc, "inventory_plan_exit_code": inventory_rc,
        "doctor_output": doctor_raw, "inventory_plan_output": inventory_raw,
        "historical_rc3_disposition": (
            "Post-B doctor and inventory rc3 are both confirmed from full raw "
            "JSON as the expected running original Flash-Next container occupying "
            "its own name and port 8000; this is not an independent host-process "
            "or GPU exclusivity audit."
            if doctor_good and inventory_good else "UNVERIFIED"),
        "flash_image": image, "flash_revision": assets.get("revision"),
        "stage_b_receipt_sha256": stage_b_sha256,
        "post_b_verify": "NOT_RUN", "post_b_benchmark": "NOT_RUN",
        "p3_c_authorized": False, "executed": False,
        "finished_at_utc": now.astimezone(timezone.utc).isoformat(),
        "notice": ("Read-only source/manifest/HTTP and launch preflight only. "
                   "GPU Verify and Benchmark each require separate fresh approvals. "
                   "No P3-C execution or automatic model transition."),
    }


def save_immutable(doc: dict, *, root: Path = P3_ROOT) -> Path:
    """Private unique append-only output, never a mutable p1-diagnostics.json."""
    if root.is_symlink():
        raise ValueError("P3_EVIDENCE_ROOT_IS_SYMLINK")
    root = root.expanduser().resolve()
    cache = Path(os.environ.get(
        "HF_CACHE", str(Path.home() / ".cache/huggingface"))).expanduser().resolve()
    if root.is_relative_to(ROOT.resolve()) or root.is_relative_to(cache):
        raise ValueError("P3_EVIDENCE_ROOT_UNSAFE")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if root.stat().st_mode & 0o077:
        raise ValueError("P3_EVIDENCE_ROOT_PERMISSIONS_UNSAFE")
    filename = ("p1-diagnostics-" + datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:12] + ".json")
    path = root / filename
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(doc, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    return path


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--inspect-only", action="store_true",
                    help="compatibility flag; inspection is ALWAYS read-only")
    ns = ap.parse_args(argv)
    # No --execute or GPU/approve flags exist for this command.
    issues = []
    try:
        b, digest = _read_private(P3_ROOT / "stage-b.json", P3_ROOT)
    except (OSError, ValueError, TypeError, KeyError):
        b, digest = {}, ""
        issues.append("P3_B_PRIVATE_RECEIPT_MISSING_OR_UNTRUSTED")
    live_rc, live = run_readonly(
        ["./wizard.sh", "service", "manager", "status", "--json"])
    inspection = session(inspect_only=True)
    outcome = assess(b, live_rc, live, inspection, stage_b_sha256=digest)
    if issues:
        outcome["issues"] = sorted(set(outcome["issues"] + issues))
        outcome["status"] = "BLOCKED"
    try:
        path = save_immutable(outcome)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "issues": [
            "P3_EVIDENCE_WRITE_FAILED"], "error_type": type(exc).__name__,
            "executed": False, "p3_c_authorized": False}))
        return 3
    print(json.dumps({
        "status": outcome["status"], "issues": outcome["issues"],
        "evidence_file": str(path), "doctor_exit_code": outcome["doctor_exit_code"],
        "inventory_plan_exit_code": outcome["inventory_plan_exit_code"],
        "post_b_verify": "NOT_RUN", "post_b_benchmark": "NOT_RUN",
        "p3_c_authorized": False, "executed": False,
    }, indent=2, sort_keys=True))
    return 0 if outcome["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
