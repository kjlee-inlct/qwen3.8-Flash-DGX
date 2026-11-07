"""Manifest-owned one-shot retirement of exactly two preserved 27B test containers.

Does not stop/recreate any model. Never removes an image, volume, checkpoint,
cache, user data, P3 receipt, benchmark or migration journal. Read-only plan
unless executed under TTY with fresh SHA and two independent acknowledgements.
The manifest's exact two targets are mandatory; no arbitrary names/flags.
"""
from __future__ import annotations

from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager import p3_persistent_switch as p3
from scripts.manager import p2_27b_recipe_migration as migration
from scripts.manager.service_manifest import policy, POLICY_PATH
from scripts.manager.p2_27b_tool_variant import (
    SOURCE_CONTAINER, FALLBACK_CONTAINER, VARIANT_CONTAINER,
    TOOL_CHAT_TEMPLATE, _run_names, _image_and_id, _protected_mount,
)
from scripts.manager.p2_27b_launch_preview import SERVED, REVISION

ROOT = Path.home() / ".local/state/blazux-wizard/manifest-container-cleanup"
READY = "READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL"
DONE = "MANIFEST_RETIRED_CONTAINERS_CLEANED"
ACK = "I_APPROVE_MANIFEST_TWO_STOPPED_CONTAINERS_ONLY"
ACK_PRESERVE = "I_CONFIRM_ACTIVE_27B_AND_ALL_MODEL_EVIDENCE_PRESERVED"
SHA = re.compile(r"^[0-9a-f]{64}$")
EXPECTED_NAMES = ("qwen38-27b-failed-6d9ede0904c2", VARIANT_CONTAINER)
EXPECTED_IMAGE = "sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137"


def _hash(data: dict) -> str:
    return hashlib.sha256(json.dumps(data, sort_keys=True,
                          separators=(",", ":")).encode()).hexdigest()


def _deny(*issues: str) -> dict[str, Any]:
    return {
        "schema_version": 1, "action": "MANIFEST_RETIRED_27B_CONTAINER_CLEANUP",
        "status": "BLOCKED", "issues": sorted(set(issues)), "executed": False,
        "approval_accepted": False, "plan_id": None, "target_count": 2,
        "docker_state_mutated": False, "active_service_preserved": None,
        "delete_scope": "DOCKER_CONTAINERS_ONLY",
    }


def _load() -> tuple[dict, str]:
    doc = policy()
    subset = doc.get("retired_containers")
    if (not isinstance(subset, dict)
            or subset.get("cleanup_mode") != "OPERATOR_APPROVED_CONTAINER_ONLY"
            or subset.get("requires_active_model") != "27b"
            or subset.get("requires_served_id") != SERVED
            or subset.get("requires_host_port") != 8000
            or subset.get("requires_promoted_recipe") != "recipes/qwen38-27b.runtime.json"
            or subset.get("expected_image_id") != EXPECTED_IMAGE
            or subset.get("preserve_images") is not True
            or subset.get("preserve_hf_cache") is not True
            or subset.get("preserve_p3_and_benchmark_receipts") is not True):
        raise ValueError("MANIFEST_RETIREMENT_POLICY_INVALID")
    entries = subset.get("targets")
    if (not isinstance(entries, list) or len(entries) != 2
            or tuple(entry.get("name") for entry in entries) != EXPECTED_NAMES):
        raise ValueError("RETIREMENT_TARGETS_NOT_EXACT_ALLOWLIST")
    if (doc["models"]["27b"]["container_name"] != SOURCE_CONTAINER
            or doc["models"]["flash-next"]["container_name"] != FALLBACK_CONTAINER
            or doc["models"]["27b"].get("recipe_state") != "CANONICAL_DEFAULT"):
        raise ValueError("PROTECTED_MODEL_NAMES_OR_RECIPE_UNQUALIFIED")
    # This is an exact, already-qualified retirement BATCH, not a global
    # deletion ban for canonical 27B or Flash. Both remain operator-removable
    # through their own separately approved lifecycle action.
    for item in entries:
        if (item.get("managed_model") != "27b"
                or item.get("role") not in (
                    "failed_first_canonical_recipe_migration_candidate",
                    "successful_one_shot_native_tools_trial_variant",
                ) or not isinstance(item.get("expected_labels"), dict)
                or not isinstance(item.get("evidence_result"), str)
                or not isinstance(item.get("evidence_root"), str)):
            raise ValueError("INCOMPLETE_RETIREMENT_MANIFEST_RECORD")
    return subset, hashlib.sha256(POLICY_PATH.read_bytes()).hexdigest()


def _evidence(entry: dict) -> tuple[str, str]:
    """Verify existing private event receipts and the exact trial provenance."""
    location = entry["evidence_root"]
    if not location.startswith("~/.local/state/blazux-wizard/"):
        raise ValueError("EVIDENCE_LOCATION_OUTSIDE_PROJECT_STATE")
    root = Path(location).expanduser()
    expected = entry["evidence_expected_status"]
    receipt = migration._safe_json(root / entry["evidence_result"])
    if receipt.get("status") != expected:
        raise ValueError("RETIREMENT_SOURCE_RECEIPT_NOT_QUALIFIED")
    if entry["name"] == VARIANT_CONTAINER and receipt.get("issues"):
        raise ValueError("SUCCESSFUL_TRIAL_RECEIPT_CONTAINS_ISSUES")
    if entry["name"] == EXPECTED_NAMES[0] and receipt.get("issues") != [
            "MIGRATION_ERROR_NEW_CANONICAL_BENCHMARK_NOT_QUALIFIED"]:
        raise ValueError("FAILED_CANDIDATE_RECEIPT_REASON_MISMATCH")
    if entry["name"] == VARIANT_CONTAINER:
        trial_id = entry["expected_labels"][
            "blazux.p2-final-native-tools-trial"]
        if (not migration._trial_pass(trial_id)
                or receipt.get("original_restored") is not True
                or receipt.get("structured_tool_call") is not True
                or receipt.get("streamed_tool_call") is not True):
            raise ValueError("TRIAL_VARIANT_PROVENANCE_NOT_VERIFIED")
    else:
        migrated = entry["expected_labels"]["blazux.migration"]
        attempt = migration._safe_json(root / ("attempt-" + migrated + ".json"))
        if (attempt.get("plan_id") != migrated
                or attempt.get("source_id") != entry["expected_original_id"]
                or receipt.get("plan_id") != migrated
                or receipt.get("native_tools_pass") is not True
                or receipt.get("original_restored") is not True
                or receipt.get("benchmark_pass") is not False):
            raise ValueError("FAILED_MIGRATION_EVIDENCE_UNVERIFIED")
    return expected, hashlib.sha256(
        (root / entry["evidence_result"]).read_bytes()).hexdigest()


def _command_valid(doc: dict, *, native_template: str) -> bool:
    cmd = (doc.get("Config") or {}).get("Cmd")
    return (isinstance(cmd, list)
            and "--enable-auto-tool-choice" in cmd
            and "--tool-call-parser" in cmd
            and "qwen3_coder" in cmd
            and "--reasoning-parser" in cmd
            and "qwen3" in cmd
            and "--chat-template" in cmd
            and native_template in cmd
            and "--served-model-name" in cmd
            and SERVED in cmd
            and "--quantization" in cmd
            and "modelopt_mixed" in cmd
            and any(isinstance(v, str) and "/snapshots/" + REVISION in v
                    for v in cmd))


def _inspect_target(entry: dict, doc: dict, active: dict, expected_mount: Path) -> list[str]:
    issues: list[str] = []
    name = entry["name"]
    if (not _image_and_id(doc)
            or doc.get("Name") != "/" + name
            or doc.get("Image") != EXPECTED_IMAGE
            or (doc.get("State") or {}).get("Running") is not False
            or doc.get("Id") == active.get("Id")):
        issues.append("FOREIGN_RUNNING_OR_UNIDENTIFIED_TARGET_" + name)
    pinned_id = entry.get("expected_container_id")
    if pinned_id is not None and doc.get("Id") != pinned_id:
        issues.append("PINNED_TEST_CONTAINER_ID_MISMATCH_" + name)
    if (entry["name"] == EXPECTED_NAMES[0]
            and doc.get("Id") == entry.get("expected_original_id")):
        issues.append("FAILED_CANDIDATE_IS_ORIGINAL_HISTORY_ID")
    labels = (doc.get("Config") or {}).get("Labels") or {}
    if any(labels.get(k) != value
           for k, value in entry["expected_labels"].items()):
        issues.append("OWNERSHIP_LABELS_DO_NOT_MATCH_MANIFEST_" + name)
    if _protected_mount(doc) != expected_mount:
        issues.append("PINNED_READ_ONLY_HF_MOUNT_MISMATCH_" + name)
    if not _command_valid(doc, native_template=TOOL_CHAT_TEMPLATE):
        issues.append("PINNED_NATIVE_TOOLS_CMD_NOT_VERIFIED_" + name)
    return issues


def make_plan(*, run: Callable[..., Any] = gpu.call,
              inspect: Callable[..., dict] = gpu.docker_info,
              active_status: Callable[..., dict] = migration.inspect_promoted_service,
              root: Path = ROOT, now: float | None = None) -> dict:
    """Read-only manifest/live/evidence crosscheck, no cleanup side effects."""
    issues: list[str] = []
    try:
        cfg, manifest_sha = _load()
        if root.is_symlink() or (root.exists() and list(root.glob("attempt-*.json"))):
            issues.append("PREVIOUS_CLEANUP_ATTEMPT_REQUIRES_MANUAL_RECONCILIATION")
        status = active_status()
        if status.get("status") != "LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED" or status.get("issues"):
            issues.append("ACTIVE_CANONICAL_27B_AND_BENCHMARK_NOT_VERIFIED")
        names = _run_names(run, all_containers=True)
        running = _run_names(run, all_containers=False)
        if any(name not in names for name in (SOURCE_CONTAINER, FALLBACK_CONTAINER)):
            issues.append("PROTECTED_MODEL_CONTAINERS_MISSING")
            return _deny(*issues)
        if set(EXPECTED_NAMES) - set(names):
            issues.append("RETIREMENT_TARGET_MISSING_OR_ALREADY_CLEANED")
        if SOURCE_CONTAINER not in running or FALLBACK_CONTAINER in running:
            issues.append("PROTECTED_MODELS_NOT_IN_EXPECTED_RUNNING_STATE")
        active = inspect(SOURCE_CONTAINER)
        fallback = inspect(FALLBACK_CONTAINER)
        if (not _image_and_id(active)
                or active.get("Image") != EXPECTED_IMAGE
                or (active.get("State") or {}).get("Running") is not True
                or (fallback.get("State") or {}).get("Running") is not False):
            issues.append("PROTECTED_LIVE_SERVICE_IDENTITY_INVALID")
        mount = _protected_mount(active)
        if mount is None:
            issues.append("PROTECTED_CANONICAL_READ_ONLY_HF_MOUNT_UNVERIFIED")
        # Docker ps is whole-host inventory. No foreign GPU workload allowed.
        if p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect):
            issues.append("OTHER_GPU_MODEL_RUNNING")
        if set(EXPECTED_NAMES) & set(running):
            issues.append("RETIREMENT_TARGET_IS_RUNNING")
        observations = []
        for entry in cfg["targets"]:
            name = entry["name"]
            if name not in names:
                continue
            doc = inspect(name)
            if mount is not None:
                issues.extend(_inspect_target(entry, doc, active, mount))
            expected_status, receipt_sha = _evidence(entry)
            observations.append({
                "name": name, "container_id": doc.get("Id"),
                "image_id": doc.get("Image"), "receipt_status": expected_status,
                "receipt_sha256": receipt_sha,
                "running": (doc.get("State") or {}).get("Running"),
            })
        if issues:
            return _deny(*issues)
        window = int(time.time() if now is None else now) // 600
        facts = {
            "kind": "EXACTLY_TWO_MANIFEST_RETIRED_CONTAINER_DELETE",
            "manifest_sha256": manifest_sha,
            "canonical_active_id": active["Id"],
            "canonical_image_id": active["Image"],
            "targets": observations,
            "window": window, "port": 8000,
        }
        return {
            "schema_version": 1,
            "action": "MANIFEST_RETIRED_27B_CONTAINER_CLEANUP",
            "status": READY, "issues": [],
            "plan_id": _hash(facts),
            "expires_at_epoch_seconds": (window + 1) * 600,
            "manifest_sha256": manifest_sha,
            "active_container": SOURCE_CONTAINER,
            "active_container_id": active["Id"],
            "targets": observations,
            "target_count": 2, "api_port": 8000,
            "delete_scope": "DOCKER_CONTAINERS_ONLY",
            "preserve_images_and_caches": True,
            "preserve_all_evidence": True,
            "approval_accepted": False, "executed": False,
            "docker_state_mutated": False,
            "required_cleanup_ack": ACK,
            "required_preservation_ack": ACK_PRESERVE,
            "notice": ("No active service stop/restart. Exact manifest candidates "
                       "ONLY; delete two stopped containers after separate "
                       "operator approval. Old evidence/benchmark/image/HF cache "
                       "and model services are preserved."),
        }
    except (OSError, RuntimeError, ValueError, TypeError, KeyError,
            subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        return _deny("READ_ONLY_CLEANUP_PREFLIGHT_FAILED_" + type(exc).__name__)


def execute(plan_id: str, cleanup_ack: str, preservation_ack: str, *,
            root: Path = ROOT, planner: Callable[..., dict] = make_plan,
            run: Callable[..., Any] = gpu.call,
            inspect: Callable[..., dict] = gpu.docker_info,
            clock: Callable[[], float] = time.time) -> tuple[int, dict]:
    if (not isinstance(plan_id, str) or not SHA.fullmatch(plan_id)
            or cleanup_ack != ACK or preservation_ack != ACK_PRESERVE):
        return 3, _deny("FRESH_PLAN_AND_TWO_OPERATOR_ACKNOWLEDGEMENTS_REQUIRED")
    fds: list[int] = []
    try:
        for folder in (ROOT, migration.ROOT, migration.TRIAL_ROOT,
                       migration.OPS_ROOT):
            p3._private_dir(folder)
        for path in (
            migration.OPS_ROOT / "operating-execution.lock",
            migration.TRIAL_ROOT / "native-tools-trial.lock",
            migration.ROOT / "recipe-migration.lock",
            ROOT / "manifest-container-cleanup.lock",
        ):
            fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            if os.fstat(fd).st_mode & 0o077:
                os.close(fd)
                raise ValueError("UNSAFE_CLEANUP_LOCK_PERMISSIONS")
            fds.append(fd)
        for fd in fds:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        fresh = planner(root=root)
        until = fresh.get("expires_at_epoch_seconds", 0) - clock()
        if (fresh.get("status") != READY or fresh.get("plan_id") != plan_id
                or not 30 < until <= 600):
            return 3, _deny("CHANGED_EXPIRED_OR_UNQUALIFIED_CLEANUP_PLAN")
        # Immutable write-ahead transaction marker prevents accidental replays.
        p3._write_once(root, "attempt-" + plan_id + ".json", {
            "schema_version": 1, "plan_id": plan_id,
            "targets": fresh["targets"],
            "active_container_id": fresh["active_container_id"],
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        })
        result: dict[str, Any] = {
            "schema_version": 1,
            "action": "MANIFEST_RETIRED_27B_CONTAINER_CLEANUP",
            "status": "BLOCKED", "issues": [],
            "plan_id": plan_id, "executed": False,
            "deleted": [], "remaining": [],
            "active_container_id": fresh["active_container_id"],
            "preserved_images_and_caches": True,
            "preserved_original_model_service": False,
        }
        try:
            for target in fresh["targets"]:
                # Re-verify each EXACT target by current Docker Id and labels,
                # with same whole-host identity and single GPU model.
                active = inspect(SOURCE_CONTAINER)
                if (active.get("Id") != fresh["active_container_id"]
                        or active.get("State", {}).get("Running") is not True
                        or p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect)):
                    raise RuntimeError("ACTIVE_SERVICE_IDENTITY_CHANGED_DURING_CLEANUP")
                current_names = _run_names(run, all_containers=True)
                if target["name"] not in current_names:
                    raise RuntimeError("TARGET_MISSING_DURING_APPROVED_CLEANUP")
                doc = inspect(target["name"])
                if (doc.get("Id") != target["container_id"]
                        or doc.get("Image") != target["image_id"]
                        or (doc.get("State") or {}).get("Running") is not False):
                    raise RuntimeError("RETIRED_TARGET_IDENTITY_CHANGED")
                entry = next(e for e in _load()[0]["targets"]
                             if e["name"] == target["name"])
                if _inspect_target(entry, doc, active, _protected_mount(active)):
                    raise RuntimeError("RETIRED_TARGET_NO_LONGER_MATCHES_MANIFEST")
                if _evidence(entry)[1] != target["receipt_sha256"]:
                    raise RuntimeError("RETIRED_EVIDENCE_CHANGED")
                result["executed"] = True
                cmd = run(["docker", "rm", target["name"]], timeout=45)
                if cmd.returncode:
                    raise RuntimeError("DOCKER_RM_FAILED_" + target["name"])
                if target["name"] in _run_names(run, all_containers=True):
                    raise RuntimeError("DOCKER_RM_UNCONFIRMED_" + target["name"])
                result["deleted"].append({
                    "name": target["name"], "container_id": target["container_id"]
                })
            active = inspect(SOURCE_CONTAINER)
            if (active.get("Id") != fresh["active_container_id"]
                    or active.get("State", {}).get("Running") is not True
                    or p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect)):
                raise RuntimeError("ACTIVE_SERVICE_STATE_CHANGED_AFTER_CLEANUP")
            result["preserved_original_model_service"] = True
            result["status"] = DONE
        except (OSError, RuntimeError, ValueError, TypeError,
                subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            result["issues"].append(
                (str(exc) if isinstance(exc, RuntimeError)
                 else "CLEANUP_INTERRUPTED_" + type(exc).__name__))
            result["status"] = ("PARTIAL_CLEANUP_REQUIRES_RECONCILIATION"
                                if result["deleted"] else
                                "CLEANUP_ABORTED_REQUIRES_RECONCILIATION")
        result["remaining"] = [
            item["name"] for item in fresh["targets"]
            if item["name"] not in [x["name"] for x in result["deleted"]]
        ]
        try:
            p3._write_once(root, "result-" + plan_id + ".json", result)
        except (OSError, RuntimeError, ValueError):
            result["status"] = "CLEANUP_EVIDENCE_WRITE_FAILED"
            result["issues"].append("CLEANUP_RESULT_RECEIPT_UNAVAILABLE")
        return (0 if result["status"] == DONE else 4), result
    except (OSError, RuntimeError, ValueError, TypeError,
            subprocess.TimeoutExpired, BlockingIOError):
        return 3, _deny("CLEANUP_LOCK_OR_TRANSACTION_UNAVAILABLE")
    finally:
        for fd in reversed(fds):
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)


def status(*, run: Callable[..., Any] = gpu.call,
           active_status: Callable[..., dict] = migration.inspect_promoted_service,
           root: Path = ROOT) -> dict:
    """Read-only inventory, current active recipe and cleanup receipt audit."""
    report = _deny()
    report["action"] = "MANIFEST_RETIRED_27B_CONTAINER_STATUS"
    report["scope"] = "EXACT_TWO_DIAGNOSTIC_CONTAINERS_NOT_MODEL_UNINSTALL_POLICY"
    try:
        names = _run_names(run, all_containers=True)
        report["remaining"] = [x for x in EXPECTED_NAMES if x in names]
        report["missing"] = [x for x in EXPECTED_NAMES if x not in names]
        results = sorted(root.glob("result-*.json")) if root.is_dir() else []
        approved = []
        for item in results:
            receipt = migration._safe_json(item)
            if (receipt.get("status") == DONE
                    and receipt.get("issues") == []
                    and len(receipt.get("deleted", [])) == 2
                    and {row["name"] for row in receipt["deleted"]} ==
                            set(EXPECTED_NAMES)):
                approved.append(item.name)
        active = active_status()
        report["active_service_preserved"] = (
            active.get("status") == "LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED"
            and active.get("issues") == []
        )
        if (not report["remaining"] and len(approved) == 1
                and report["active_service_preserved"]):
            report["status"] = DONE
            report["issues"] = []
            report["verified_result_receipt"] = approved[0]
        else:
            report["status"] = "RETIRED_CONTAINERS_PRESENT_OR_RECEIPT_NOT_VERIFIED"
            report["issues"] = (
                ["PENDING:" + x for x in report["remaining"]]
                + (["NO_COMPLETED_CLEANUP_RECEIPT"] if not approved else [])
                + (["ACTIVE_CANONICAL_27B_NOT_VERIFIED"]
                   if not report["active_service_preserved"] else [])
            )
    except (OSError, ValueError, RuntimeError, TypeError,
            subprocess.TimeoutExpired):
        report["issues"] = ["RETIRED_INVENTORY_READ_FAILED"]
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Manifest-owned two stopped 27B test containers cleanup"
    )
    parser.add_argument("action", choices=("plan", "execute", "status"))
    args = parser.parse_args(argv)
    if args.action == "status":
        out = status()
        print(json.dumps(out, indent=2, sort_keys=True))
        return 0 if out["status"] == DONE else 3
    plan = make_plan()
    if args.action == "plan":
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0 if plan["status"] == READY else 3
    if plan["status"] != READY:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 3
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("BLOCKED: cleanup requires interactive TTY")
        return 3
    print("Manifest-registered STOPPED 27B test containers ONLY:")
    for row in plan["targets"]:
        print("  " + row["name"] + " (" + str(row["container_id"])[:12] + ")")
    print("No Docker images/model files/evidence or active service will be removed.")
    print("Fresh exact plan SHA: " + plan["plan_id"])
    print("Expires epoch: " + str(plan["expires_at_epoch_seconds"]))
    try:
        typed = input("Type the new exact 64-hex plan SHA: ").strip()
        ack = input("Type independent cleanup acknowledgement " + ACK + ": ").strip()
        preserve = input("Type service preservation acknowledgement "
                         + ACK_PRESERVE + ": ").strip()
    except (EOFError, KeyboardInterrupt):
        print("CANCELLED: no container removal")
        return 3
    old = signal.getsignal(signal.SIGTERM)
    def on_term(_signal: int, _frame: Any) -> None:
        raise KeyboardInterrupt("RETIREMENT_INTERRUPTED")
    signal.signal(signal.SIGTERM, on_term)
    try:
        rc, result = execute(typed, ack, preserve)
    finally:
        signal.signal(signal.SIGTERM, old)
    print(json.dumps(result, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
