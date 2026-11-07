"""P4-B review plus P4-C transaction rehearsal: read-only, no deletion adapter.

P5 or P8 must separately authorize/qualify any future exact-resource removal.
The CLI and Wizard cannot execute a delete or turn a review hash into approval.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from typing import Any, Callable

from scripts.manager.p4_a_inventory import inspect_p4_a

MODELS = frozenset(("27b", "flash-next", "orcarouter"))
DF_TYPES = frozenset(("Images", "Containers", "Local Volumes", "Build Cache"))
SIZE = re.compile(
    r"^[0-9]+(?:\.[0-9]+)? ?(?:B|kB|MB|GB|TB|PB|KiB|MiB|GiB|TiB|PiB)"
    r"(?: \([0-9]{1,3}%\))?$"
)
P4_C_LIVE_EXECUTION_RELEASED = False
FUTURE_PHASES = ("P5_OPERATIONAL_ISSUE", "P8_FINAL_OPERATIONS")


def _amount(value: Any) -> int | None:
    return value if type(value) is int and 0 <= value <= 2**63 - 1 else None


def _klass(model: str, active: str) -> str:
    if model == active:
        return "PRESERVE_ACTIVE_MODEL"
    if model == "flash-next":
        return "PRESERVE_P8_FLASH_REINSTALL_REFERENCE"
    if model == "orcarouter":
        return "PRESERVE_P5_ORCAROUTER_SOURCE"
    return "PRESERVE_PENDING_EXPLICIT_P5_OR_P8_DECISION"


def _resource(kind: str, key: str, klass: str, *, amount: int | None = None,
              observed: str = "UNVERIFIED") -> dict:
    return {
        "resource_kind": kind, "resource_key": key, "review_class": klass,
        "observed_state": observed, "allocated_bytes_observed": amount,
        "safe_reclaimable_bytes": None, "reference_ownership_verified": False,
        "eligible_for_deletion_now": False, "selected_for_deletion": False,
        "would_execute": False, "requires_exact_identity_audit": True,
    }


def review_candidates(inventory: dict) -> dict:
    """Pure allowlisted review of one *current* complete P4-A snapshot."""
    doc = {
        "schema_version": 1, "stage": "P4-B",
        "action": "STORAGE_CANDIDATE_REFERENCE_REVIEW",
        "status": "REVIEW_BLOCKED", "issues": [], "scope": "READ_ONLY",
        "resources": [], "candidate_count": 0, "active_model": None,
        "reference_gaps": [
            "HF_SNAPSHOT_BLOB_SYMLINK_HARDLINK_GRAPH_NOT_AUDITED",
            "CACHE_ROOT_MOUNT_DEVICE_ID_NOT_AUDITED",
            "FLASH_FP8_DERIVATIVE_P8_REFERENCE_NOT_AUDITED",
            "DOCKER_IMAGE_VOLUME_LAYER_OWNERSHIP_NOT_AUDITED",
            "HISTORICAL_RECEIPTS_AND_REINSTALL_ROLLBACK_NOT_AUDITED",
        ],
        "safe_reclaimable_bytes": None, "deletion_candidates_approved": False,
        "requires_separate_p5_or_p8_authorization": True,
        "plan_id": None, "approval_accepted": False, "executed": False,
        "operations_enabled": False, "production_released": False,
    }
    if not isinstance(inventory, dict):
        doc["issues"].append("INVALID_P4_A_EVIDENCE")
        return doc
    if (inventory.get("stage") != "P4-A"
            or inventory.get("status") != "READ_ONLY_INVENTORY_COMPLETE"
            or inventory.get("issues") != []
            or inventory.get("active_api_verified") is not True
            or inventory.get("operations_enabled") is not False
            or inventory.get("executed") is not False):
        doc["issues"].append("CURRENT_P4_A_COMPLETE_EVIDENCE_REQUIRED")
        return doc
    active = inventory.get("observed_active_model")
    if active not in MODELS:
        doc["issues"].append("ACTIVE_MODEL_UNVERIFIED")
        return doc
    containers = inventory.get("managed_containers")
    caches = inventory.get("cache_storage")
    df = inventory.get("docker_disk_usage")
    if (not isinstance(containers, list) or not isinstance(caches, list)
            or not caches or len(caches) > 8
            or not isinstance(df, dict) or df.get("status") != "OBSERVED_DOCKER_ESTIMATES"
            or not isinstance(df.get("rows"), list)):
        doc["issues"].append("CAPACITY_OR_REFERENCE_OBSERVATION_MISSING")
        return doc

    seen_models: set[str] = set()
    seen_roots: set[int] = set()
    seen_df: set[str] = set()
    resources: list[dict] = []
    for row in containers:
        if not isinstance(row, dict) or row.get("model") not in MODELS:
            doc["issues"].append("UNTRUSTED_MODEL_CONTAINER_ROW")
            return doc
        model = row["model"]
        if (model in seen_models or type(row.get("container_present")) is not bool
                or type(row.get("container_running")) is not bool):
            doc["issues"].append("DUPLICATE_OR_INVALID_MODEL_STATE")
            return doc
        seen_models.add(model)
        if row["container_running"] and model != active:
            doc["issues"].append("UNEXPECTED_NONACTIVE_RUNNING_MODEL")
            return doc
        if row["container_present"]:
            resources.append(_resource(
                "MANAGED_CONTAINER", "container:" + model, _klass(model, active),
                observed="RUNNING" if row["container_running"] else "STOPPED",
            ))
    if active not in seen_models or not any(r["resource_key"] == "container:" + active
                                          and r["observed_state"] == "RUNNING"
                                          for r in resources):
        doc["issues"].append("ACTIVE_MODEL_CONTAINER_NOT_OBSERVED")
        return doc

    for root in caches:
        if not isinstance(root, dict):
            doc["issues"].append("INVALID_CACHE_ROOT_OBSERVATION")
            return doc
        index = root.get("root_index")
        if (type(index) is not int or not 1 <= index <= 8
                or index in seen_roots or root.get("exists") is not True):
            doc["issues"].append("CACHE_ROOT_IDENTITY_INCOMPLETE")
            return doc
        seen_roots.add(index)
        sizes = root.get("known_model_repo_allocated_bytes")
        if not isinstance(sizes, dict):
            doc["issues"].append("CACHE_MODEL_SIZE_TABLE_MISSING")
            return doc
        for model in sorted(MODELS):
            flag = "flash_repo_present" if model == "flash-next" else model + "_repo_present"
            if type(root.get(flag)) is not bool:
                doc["issues"].append("CACHE_MODEL_PRESENCE_UNVERIFIED")
                return doc
            if root[flag]:
                amount = _amount(sizes.get(model))
                if amount is None:
                    doc["issues"].append("CACHE_MODEL_ALLOCATION_UNAVAILABLE")
                    return doc
                resources.append(_resource(
                    "HF_MODEL_REPOSITORY", "root-" + str(index) + ":" + model,
                    _klass(model, active), amount=amount, observed="DIRECTORY_PRESENT",
                ))

    for row in df["rows"]:
        if not isinstance(row, dict) or row.get("type") not in DF_TYPES:
            doc["issues"].append("INVALID_DOCKER_CATEGORY")
            return doc
        kind = row["type"]
        if kind in seen_df:
            doc["issues"].append("DUPLICATE_DOCKER_CATEGORY")
            return doc
        seen_df.add(kind)
        size, reclaim = row.get("docker_reported_size"), row.get("docker_reported_reclaimable")
        if (not isinstance(size, str) or not SIZE.fullmatch(size)
                or not isinstance(reclaim, str) or not SIZE.fullmatch(reclaim)):
            doc["issues"].append("UNTRUSTED_DOCKER_ESTIMATE")
            return doc
        item = _resource(
            "DOCKER_CATEGORY_ESTIMATE", "docker:" + kind.lower().replace(" ", "-"),
            "NOT_AN_EXACT_RESOURCE_TARGET", observed="DISPLAY_ESTIMATE_ONLY",
        )
        item["docker_reported_size"] = size
        item["docker_reported_reclaimable"] = reclaim
        resources.append(item)
    if seen_df != DF_TYPES:
        doc["issues"].append("DOCKER_CATEGORY_MISSING")
        return doc

    doc["status"] = "READ_ONLY_REVIEW_COMPLETE"
    doc["active_model"] = active
    doc["resources"] = resources
    doc["candidate_count"] = len(resources)
    serialized = json.dumps(
        {"active_model": active, "resources": resources},
        ensure_ascii=True, sort_keys=True, separators=(",", ":"),
    )
    doc["review_fingerprint_not_approval"] = hashlib.sha256(serialized.encode()).hexdigest()
    return doc


def rehearse_cleanup(review: dict) -> dict:
    """P4-C pure dry-run. All potentially destructive steps remain locked."""
    ready = (isinstance(review, dict)
             and review.get("stage") == "P4-B"
             and review.get("status") == "READ_ONLY_REVIEW_COMPLETE"
             and review.get("issues") == []
             and review.get("deletion_candidates_approved") is False
             and isinstance(review.get("resources"), list))
    return {
        "schema_version": 1, "stage": "P4-C",
        "action": "SELECTIVE_CLEANUP_TRANSACTION_DRY_RUN",
        "status": ("DRY_RUN_COMPLETE_RELEASE_GATED" if ready
                   else "DRY_RUN_BLOCKED_INCOMPLETE_EVIDENCE"),
        "issues": [] if ready else ["P4_B_COMPLETE_REVIEW_REQUIRED"],
        "scope": "SOURCE_AND_DGX_READ_ONLY",
        "review_fingerprint_not_approval": (
            review.get("review_fingerprint_not_approval") if ready else None),
        "reviewed_resources": len(review["resources"]) if ready else 0,
        "selected_resources": 0,
        "simulated_operations": [
            {"resource_key": row["resource_key"], "would_execute": False,
             "blocker": "P5_OR_P8_EXACT_RESOURCE_APPROVAL_AND_REFERENCE_AUDIT_REQUIRED"}
            for row in review["resources"]
        ] if ready else [],
        "transaction_steps": [
            {"step": "verify_current_p4_a_snapshot", "result": "PASS" if ready else "BLOCKED"},
            {"step": "enumerate_model_container_docker_references", "result": "PASS" if ready else "BLOCKED"},
            {"step": "verify_hardlink_shared_layers_and_rollback_references", "result": "DEFERRED_P5_OR_P8"},
            {"step": "fresh_exact_id_recheck_and_tty_approval", "result": "DEFERRED_P5_OR_P8"},
            {"step": "release_live_cleanup_adapter", "result": "NOT_RELEASED"},
            {"step": "delete_and_verify_api_gpu_port_disk", "result": "NOT_EXECUTED"},
        ],
        "future_authorization_phases": list(FUTURE_PHASES),
        "safe_reclaimable_bytes": None, "reclaimable_bytes_verified": False,
        "plan_id": None, "approval_accepted": False, "executed": False,
        "operations_enabled": False, "live_execution_released": P4_C_LIVE_EXECUTION_RELEASED,
        "docker_mutation_performed": False, "hf_mutation_performed": False,
        "production_released": False,
    }


def deny_execution() -> dict:
    """No host inspection occurs when --execute or approval is supplied."""
    return {
        "schema_version": 1, "stage": "P4-C", "status": "BLOCKED",
        "issues": ["P4_C_LIVE_EXECUTION_NOT_RELEASED",
                   "P5_OR_P8_SEPARATE_EXACT_RESOURCE_APPROVAL_REQUIRED",
                   "UNVERIFIED_APPROVAL_CANNOT_EXECUTE"],
        "executed": False, "operations_enabled": False, "approval_accepted": False,
        "plan_id": None, "live_execution_released": False,
    }


def inspect_both(*, inventory_fn: Callable[[], dict] = inspect_p4_a) -> dict:
    """Perform P4-A once; then P4-B and P4-C as pure in-memory transforms."""
    try:
        inventory = inventory_fn()
    except (OSError, RuntimeError, ValueError, TypeError, KeyError):
        inventory = {"stage": "P4-A", "status": "READ_ONLY_INVENTORY_PARTIAL",
                     "issues": ["P4_A_OBSERVATION_UNAVAILABLE"]}
    b = review_candidates(inventory)
    c = rehearse_cleanup(b)
    return {
        "schema_version": 1, "stage": "P4-B+C",
        "status": ("READ_ONLY_DRY_RUN_PASS" if not b["issues"] and not c["issues"]
                   else "READ_ONLY_DRY_RUN_BLOCKED"),
        "inventory_status": inventory.get("status", "UNAVAILABLE"),
        "candidate_review": b, "cleanup_rehearsal": c,
        "executed": False, "operations_enabled": False,
        "live_deletion_approved": False, "production_released": False,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="P4-B+C read-only dry-run", allow_abbrev=False)
    p.add_argument("--json", action="store_true")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--execute", action="store_true")
    p.add_argument("--approve-plan")
    args = p.parse_args(argv)
    doc = deny_execution() if args.execute or args.approve_plan else inspect_both()
    if args.json:
        print(json.dumps(doc, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print("P4-B/C: " + doc["status"] + " (NO DELETE)")
    return 0 if doc["status"] == "READ_ONLY_DRY_RUN_PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
