"""Read-only PREVIEW for repeatable Flash-Next / 27B operating transfers.

P3 stage-A/B/C receipts qualify *historical* model/container lineage only.
They are NOT a fresh switch approval, execution plan, or reusable P3 stage.
No Docker stop/start, GPU inference, journal write, or filesystem mutation.
"""
from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import time
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager import p3_persistent_switch as p3
from scripts.manager.operational_audit import inspect_journal
from scripts.manager.service_status import inspect_live_status
from scripts.manager import recipe_drift

ROOT = Path.home() / ".local/state/blazux-wizard/operational-switch"
P3_ROOT = p3.ROOT
SUPPORTED = ("flash-next", "27b")
READY = "READY_FOR_OPERATOR_REVIEW_ONLY"


def _blocked(target: str, issues: list[str], **facts: Any) -> dict[str, Any]:
    return {
        "schema_version": 1, "action": "OPERATING_MODEL_SWITCH_PREVIEW",
        "target_model": target, "status": "BLOCKED",
        "issues": sorted(set(issues)), "executed": False,
        "execution_supported": False, "operations_enabled": False,
        "approval_accepted": False, "plan_id": None,
        "api_host_port": 8000, **facts,
    }


def historical_p3_receipts(*, root: Path = P3_ROOT) -> dict[str, Any]:
    """Validate immutable A/B/C provenance, not current operating authority."""
    records: dict[str, dict] = {}
    hashes: dict[str, str] = {}
    issues: list[str] = []
    try:
        for stage in "abc":
            records[stage], hashes[stage] = p3._read_receipt(root, stage)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        issues.append("P3_IMMUTABLE_STAGE_RECEIPTS_UNAVAILABLE")
    if not issues:
        a, b, c = (records[s] for s in "abc")
        if any(records[s].get("executed") is not True for s in "abc"):
            issues.append("P3_STAGE_EXECUTION_NOT_PROVEN")
        if any((records[s].get("source_model"), records[s].get("target_model"))
               != p3.DIRECTIONS[s] for s in "abc"):
            issues.append("P3_STAGE_DIRECTION_MISMATCH")
        for field in ("flash_id", "flash_image", "id_27b", "image_27b",
                      "p2_receipt_sha256"):
            if not a.get(field) or any(records[s].get(field) != a[field] for s in "bc"):
                issues.append("P3_STAGE_PINNED_LINEAGE_MISMATCH:" + field)
        if any(not p3.SHA.fullmatch(str(a.get(key) or ""))
               for key in ("flash_id", "id_27b", "p2_receipt_sha256")):
            issues.append("P3_STAGE_HASH_LINEAGE_INVALID")
        for field in ("flash_image", "image_27b"):
            image = a.get(field)
            if not isinstance(image, str) or not image.startswith("sha256:"):
                issues.append("P3_STAGE_IMAGE_LINEAGE_INVALID")
        try:
            stamps = [datetime.fromisoformat(
                str(records[s]["finished_at_utc"]).replace("Z", "+00:00"))
                for s in "abc"]
            if any(s.tzinfo is None for s in stamps) or stamps != sorted(stamps):
                issues.append("P3_STAGE_CHRONOLOGY_INVALID")
        except (ValueError, TypeError, KeyError):
            issues.append("P3_STAGE_FINISH_TIME_INVALID")
    return {
        "status": "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED" if not issues else "UNAVAILABLE",
        "issues": sorted(set(issues)),
        "records": records if not issues else {},
        "receipt_sha256": hashes if not issues else {},
        "live_service_verified": False, "new_switch_authorized": False,
    }



def current_container_lineage(model: str, doc: dict, *, history: dict
                              ) -> tuple[str, str, str, str | None, list[str]]:
    """Resolve CURRENT Docker ID, independently of P3 historical container ID.

    Until a qualified Flash recipe is recorded, Flash must still be the
    exact historically accepted instance. 27B may be the old accepted
    instance OR a verified, recipe-matching canonical replacement.
    """
    entry = (history.get("records") or {}).get("a") or {}
    issues: list[str] = []
    identity = doc.get("Id")
    image = doc.get("Image")
    if not p3.SHA.fullmatch(str(identity or "")):
        issues.append("CURRENT_CONTAINER_ID_INVALID")
    if not isinstance(image, str) or not image.startswith("sha256:"):
        issues.append("CURRENT_CONTAINER_IMAGE_INVALID")
    if model == "flash-next":
        kind = "HISTORICAL_P3_INSTANCE"
        if identity != entry.get("flash_id") or image != entry.get("flash_image"):
            issues.append("FLASH_NEW_INSTANCE_NEEDS_QUALIFIED_RECIPE")
        return identity, image, kind, None, issues
    if model != "27b":
        return identity, image, "UNQUALIFIED", None, ["MODEL_NOT_QUALIFIED"]
    labels = ((doc.get("Config") or {}).get("Labels") or {})
    if labels.get("blazux.recipe") == "qwen38-27b":
        kind = "CANONICAL_RECIPE"
        try:
            recipe, recipe_sha = recipe_drift.load_desired("27b")
            expected = recipe_drift.desired_runtime(recipe)
            actual = recipe_drift.observed_runtime(doc)
            diffs = recipe_drift.difference(expected, actual)
            issues.extend("CANONICAL_27B_RUNTIME_DRIFT:" + row["field"]
                          for row in diffs)
            if image != recipe["runtime"]["local_image_id"]:
                issues.append("CANONICAL_27B_IMAGE_CHANGED")
        except (OSError, RuntimeError, ValueError, TypeError, KeyError,
                json.JSONDecodeError):
            issues.append("CANONICAL_27B_RECIPE_UNVERIFIED")
            recipe_sha = None
        return identity, image, kind, recipe_sha, issues
    kind = "HISTORICAL_P3_INSTANCE"
    if (identity != entry.get("id_27b")
            or image != entry.get("image_27b")
            or labels.get(p3.LABEL) != entry.get("plan_id")):
        issues.append("27B_UNQUALIFIED_INSTANCE_OR_LINEAGE")
    return identity, image, kind, None, issues


def make_plan(
    target: str, *,
    live: Callable[[], dict] = inspect_live_status,
    run: Callable[..., Any] = gpu.call,
    inspect: Callable[..., dict] = gpu.docker_info,
    p3_root: Path = P3_ROOT,
    root: Path = ROOT,
    now: float | None = None,
) -> dict[str, Any]:
    """Build an identity-bound read-only candidate; never grant execution."""
    if target not in SUPPORTED:
        return _blocked(target, ["UNSUPPORTED_OR_UNQUALIFIED_MODEL"])
    issues: list[str] = []
    try:
        status = live()
    except (OSError, RuntimeError, ValueError, TypeError):
        status = {"status": "BLOCKED", "issues": ["LIVE_SERVICE_PROBE_FAILED"]}
    source = status.get("observed_model")
    if status.get("status") != "LIVE_SERVICE_VERIFIED" or status.get("issues"):
        issues.append("SOURCE_API_AND_MANIFEST_UNVERIFIED")
    if source not in SUPPORTED:
        issues.append("SOURCE_ACTIVE_MODEL_UNKNOWN_OR_UNSUPPORTED")
    elif status.get("expected_served_id") != p3.IDS[source]:
        issues.append("SOURCE_SERVED_MODEL_ID_MISMATCH")
    if source == target:
        return _blocked(target, ["MODEL_ALREADY_ACTIVE_NO_SWITCH_NEEDED", *issues],
                        source_model=source, current_live_status=status.get("status"))
    qualification = historical_p3_receipts(root=p3_root)
    if qualification["status"] != "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED":
        issues.extend(qualification["issues"])
    a = qualification["records"].get("a") or {}
    names = p3.NAMES
    source_doc, target_doc = None, None
    source_id, target_id = None, None
    source_image, target_image = None, None
    source_lineage, target_lineage = None, None
    source_recipe_sha, target_recipe_sha = None, None
    # Read the full write-ahead event chain, not just the current snapshot:
    # a SIGKILL between fsync(journal) and replace(snapshot) must fail closed.
    try:
        journal_audit = inspect_journal(root)
        issues.extend(journal_audit["issues"])
    except (OSError, RuntimeError, ValueError, KeyError, TypeError):
        issues.append("OPERATING_SWITCH_JOURNAL_UNTRUSTED")
    if source in SUPPORTED and not qualification["issues"]:
        try:
            found_names = p3._docker_names(run)
            if names[source] not in found_names or names[target] not in found_names:
                issues.append("SOURCE_OR_PRESERVED_TARGET_CONTAINER_MISSING")
            else:
                issues.extend(p3._gpu_conflicts(names[source], run, inspect))
                source_doc, target_doc = inspect(names[source]), inspect(names[target])
                (source_id, source_image, source_lineage,
                 source_recipe_sha, source_issues) = current_container_lineage(
                    source, source_doc, history=qualification)
                (target_id, target_image, target_lineage,
                 target_recipe_sha, target_issues) = current_container_lineage(
                    target, target_doc, history=qualification)
                issues.extend(source_issues)
                issues.extend(target_issues)
                issues.extend(p3._container_checks(
                    source_doc, name=names[source], image=source_image,
                    expected_id=source_id, running=True))
                issues.extend(p3._container_checks(
                    target_doc, name=names[target], image=target_image,
                    expected_id=target_id, running=False))
        except (OSError, RuntimeError, TypeError, ValueError,
                subprocess.TimeoutExpired):
            issues.append("DOCKER_EXCLUSIVITY_OR_IDENTITY_UNVERIFIED")
    window = int(time.time() if now is None else now) // 600
    facts = {
        "kind": "OPERATING_SWITCH_PREVIEW_V1",
        "source": source, "target": target,
        "source_id": source_id, "target_id": target_id,
        "source_image": source_image, "target_image": target_image,
        "source_lineage": source_lineage, "target_lineage": target_lineage,
        "source_recipe_sha": source_recipe_sha,
        "target_recipe_sha": target_recipe_sha,
        "p3_receipt_sha256": qualification["receipt_sha256"],
        "window": window, "port": 8000,
    }
    candidate_id = (hashlib.sha256(json.dumps(facts, sort_keys=True).encode()).hexdigest()
                    if not issues else None)
    result = _blocked(target, issues, source_model=source,
                      current_live_status=status.get("status"),
                      target_served_id=p3.IDS[target],
                      source_container_id=source_id, target_container_id=target_id,
                      source_image=source_image, target_image=target_image,
                      source_lineage=source_lineage, target_lineage=target_lineage,
                      source_recipe_sha256=source_recipe_sha,
                      target_recipe_sha256=target_recipe_sha,
                      p3_a_plan_id=a.get("plan_id"),
                      current_ids_from_live_docker=True,
                      historical_acceptance=qualification["status"],
                      expires_at_epoch_seconds=(window + 1) * 600,
                      plan_id=candidate_id)
    if not issues:
        result["status"] = READY
    result["notice"] = (
        "PREVIEW ONLY: P3 acceptance receipts verify history, not new authorization. "
        "General operating execution/rollback requires a separate qualified "
        "executor and a NEW scoped downtime approval. Never rerun P3 A/B/C.")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only generic model-switch preview")
    parser.add_argument("--target", required=True)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    args = parser.parse_args(argv)
    if (not args.plan or args.execute or args.approve_plan is not None
            or args.ack_downtime is not None):
        doc = _blocked(args.target, ["GENERAL_OPERATING_SWITCH_EXECUTOR_NOT_QUALIFIED"])
    else:
        doc = make_plan(args.target)
    print(json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if doc["status"] == READY else 3


if __name__ == "__main__":
    raise SystemExit(main())
