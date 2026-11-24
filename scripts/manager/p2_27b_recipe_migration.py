"""One-time canonical 27B recipe migration: preserve, recreate, verify, benchmark.

Real DGX native tool-calls/SSE and original restore already passed as a separate
one-shot. This NEW action deliberately replaces the canonical qwen38-27b
container with a native-tool-enabled canonical recipe, and promotes a new
benchmark only after ALL checks pass. The original is renamed for rollback,
then deleted as a *container only* after success, per explicit operator policy.

Historical P3 receipts, vLLM image, HF cache, original benchmark files, Flash,
OpenWebUI and Portainer are NEVER modified. Old P3 container IDs then become
historical evidence, not runtime identity; ordinary switch will fail closed
until a separate lineage-aware upgrade. Host crash/SIGKILL/daemon loss may
defeat auto rollback; attempt marker blocks silent retries.
"""
from __future__ import annotations

import fcntl
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager import p3_persistent_switch as p3
from scripts.manager.operational_audit import inspect_journal
from scripts.manager.operational_probe import verify_chat
from scripts.manager.operational_switch import historical_p3_receipts, ROOT as OPS_ROOT
from scripts.manager.p2_27b_benchmark import (
    CANONICAL_MAX_TOKENS, CANONICAL_VERSION, SEED as BENCHMARK_SEED,
    REQUEST_COUNT as BENCHMARK_REQUEST_COUNT,
    measure as benchmark_measure,
)
from scripts.manager.p2_27b_tool_calling import probe as structured_probe
from scripts.manager.p2_27b_tool_streaming import probe_stream
from scripts.manager.p2_27b_tool_live_trial import ROOT as TRIAL_ROOT, TRIAL_LABEL
from scripts.manager.p2_27b_tool_variant import (
    SOURCE_CONTAINER, FALLBACK_CONTAINER, VARIANT_CONTAINER, VARIANT_ID,
    _image_and_id, _gpu_access, _protected_mount, _run_names,
)
from scripts.manager.p2_27b_tool_template_audit import EXPECTED_TEMPLATE_SHA256
from scripts.manager.p2_27b_tool_variant_status import _template_digest_from_mount
from scripts.manager.p2_27b_launch_preview import SERVED, REVISION

ROOT = Path.home() / ".local/state/blazux-wizard/27b-recipe-migration"
RECIPE = Path(__file__).resolve().parents[2] / "recipes/qwen38-27b.runtime.json"
READY = "READY_FOR_CANONICAL_27B_NATIVE_RECIPE_MIGRATION"
ACK = "I_ACCEPT_27B_RECIPE_MIGRATION_DOWNTIME"
ACK_DELETE = "I_APPROVE_VERIFIED_OLD_27B_CONTAINER_DELETION_AFTER_BENCH_PASS"
BACKUP_PREFIX = "qwen38-27b-pre-native-"
FAIL_PREFIX = "qwen38-27b-failed-"
PINNED_IMAGE = "sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137"
TRIAL_SUCCESS = "PASS_RESTORED"
TOOL_FLAGS = ("--enable-auto-tool-choice", "--tool-call-parser", "--reasoning-parser")


def _hash(obj: dict) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
                       separators=(",", ":")).encode()).hexdigest()


def _issue(*issues: str) -> dict:
    return {
        "schema_version": 1, "action": "CANONICAL_27B_NATIVE_RECIPE_MIGRATION",
        "status": "BLOCKED", "issues": sorted(set(issues)),
        "executed": False, "approval_accepted": False, "plan_id": None,
        "port": 8000, "one_active_gpu_model": True,
    }


def _safe_json(path: Path) -> dict:
    if path.is_symlink() or not path.is_file():
        raise ValueError("UNTRUSTED_EVIDENCE")
    st = path.stat()
    if st.st_mode & 0o077 or not 0 < st.st_size <= 65536:
        raise ValueError("UNTRUSTED_EVIDENCE_SIZE_OR_MODE")
    doc = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(doc, dict):
        raise ValueError("INVALID_EVIDENCE")
    return doc


def _trial_pass(label: str) -> bool:
    """Validate the actual existing 1-shot trial receipt and chained events."""
    if not isinstance(label, str) or not p3.SHA.fullmatch(label):
        return False
    try:
        if TRIAL_ROOT.is_symlink():
            return False
        attempt = _safe_json(TRIAL_ROOT / ("attempt-" + label + ".json"))
        receipt = _safe_json(TRIAL_ROOT / ("result-" + label + ".json"))
        if (attempt.get("plan_id") != label
                or receipt.get("status") != TRIAL_SUCCESS
                or receipt.get("original_restored") is not True
                or receipt.get("structured_tool_call") is not True
                or receipt.get("tool_result_continuation") is not True
                or receipt.get("streamed_tool_call") is not True
                or receipt.get("issues")):
            return False
        files = sorted(TRIAL_ROOT.glob("event-*.json"))
        if len(files) < 8:
            return False
        previous = None
        for index, file in enumerate(files, 1):
            e = _safe_json(file)
            digest = e.get("event_hash")
            body = {k: v for k, v in e.items() if k != "event_hash"}
            if (file.name != f"event-{index:04d}.json"
                    or e.get("seq") != index
                    or e.get("plan_id") != label
                    or e.get("previous_hash") != previous
                    or digest != _hash(body)):
                return False
            previous = digest
        return e.get("phase") == "RESTORED"
    except (OSError, RuntimeError, ValueError, KeyError, TypeError):
        return False


def _previous_failure_file_audit(root: Path) -> tuple[dict | None, list[str]]:
    """Verify the PREVIOUS failed run's immutable receipts and complete chain.

    Do not treat a mere FAIL_RESTORED JSON value as trustworthy without the
    event hashes, exact attempt SHA, and terminal RESTORED phase.
    """
    issues = []
    try:
        if root.is_symlink() or not root.is_dir() or root.stat().st_mode & 0o077:
            return None, ["PRIVATE_MIGRATION_DIRECTORY_UNTRUSTED"]
        attempts = sorted(root.glob("attempt-*.json"))
        if len(attempts) != 1:
            return None, ["EXACTLY_ONE_PRIOR_ATTEMPT_REQUIRED"]
        attempt = _safe_json(attempts[0])
        plan = attempt.get("plan_id")
        if (not isinstance(plan, str) or not p3.SHA.fullmatch(plan)
                or attempts[0].name != "attempt-" + plan + ".json"):
            return None, ["PRIOR_ATTEMPT_ID_INVALID"]
        receipt_path = root / ("result-" + plan + ".json")
        result = _safe_json(receipt_path)
        if (result.get("plan_id") != plan
                or result.get("status") != "FAIL_RESTORED"
                or result.get("executed") is not True
                or result.get("native_tools_pass") is not True
                or result.get("benchmark_pass") is not False
                or result.get("benchmark_promoted") is not False
                or result.get("backup_container_deleted") is not False
                or result.get("original_restored") is not True
                or result.get("issues") != [
                    "MIGRATION_ERROR_NEW_CANONICAL_BENCHMARK_NOT_QUALIFIED"
                ]):
            issues.append("PRIOR_RESULT_NOT_EXACT_BENCHMARK_FAIL_RESTORED")
        files = sorted(root.glob("event-*.json"))
        previous = None
        phases = []
        for idx, file in enumerate(files, 1):
            event = _safe_json(file)
            digest = event.get("event_hash")
            body = {k: v for k, v in event.items() if k != "event_hash"}
            if (file.name != f"event-{idx:04d}.json"
                    or event.get("seq") != idx
                    or event.get("plan_id") != plan
                    or event.get("previous_hash") != previous
                    or digest != _hash(body)):
                issues.append("PRIOR_MIGRATION_EVENT_CHAIN_INVALID")
                break
            previous = digest
            phases.append(event.get("phase"))
        required = [
            "PLANNED", "OLD_STOPPING", "OLD_STOPPED", "BACKUP_PRESERVED",
            "NEW_STARTING", "NATIVE_TOOLS_VERIFIED", "RESTORED",
        ]
        if phases != required:
            issues.append("PRIOR_MIGRATION_NOT_TERMINALLY_RESTORED")
        if (root / "latest-27b-benchmark.json").exists():
            issues.append("LATEST_BENCHMARK_ALREADY_PROMOTED")
        if (root / ("benchmark-" + plan + ".json")).exists():
            issues.append("PRIOR_BENCHMARK_MUST_NOT_HAVE_BEEN_PROMOTED")
        result_sha = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
        if issues:
            return None, issues
        return {
            "prior_plan_id": plan,
            "prior_original_id": attempt.get("source_id"),
            "prior_result_sha256": result_sha,
            "last_event_hash": previous,
        }, []
    except (OSError, ValueError, TypeError, KeyError, UnicodeError,
            json.JSONDecodeError):
        return None, ["PRIOR_MIGRATION_EVIDENCE_UNAVAILABLE"]


def inspect_failed_rollback(*,
        root: Path = ROOT, run: Callable[..., Any] = gpu.call,
        inspect: Callable[..., dict] = gpu.docker_info,
        api: Callable[[str], bool] = gpu.api_ready,
        historical: Callable[[], dict] = historical_p3_receipts,
        ordinary_audit: Callable[..., dict] = inspect_journal) -> dict:
    """Read-only independent post-FAIL_RESTORED reconciliation evidence."""
    report = {
        "schema_version": 1,
        "action": "P2_27B_RECIPE_MIGRATION_FAILED_ROLLBACK_AUDIT",
        "status": "BLOCKED", "issues": [], "executed": False,
        "docker_state_mutated": False, "prior_plan_id": None,
        "manual_reconciliation_recorded": False,
    }
    previous, issues = _previous_failure_file_audit(root)
    if issues or previous is None:
        report["issues"] = issues
        return report
    report["prior_plan_id"] = previous["prior_plan_id"]
    report["prior_result_sha256"] = previous["prior_result_sha256"]
    report["last_event_hash"] = previous["last_event_hash"]
    try:
        names = _run_names(run, all_containers=True)
        running = _run_names(run, all_containers=False)
        old_id = previous["prior_original_id"]
        failed_name = FAIL_PREFIX + str(old_id)[:12]
        backup_name = BACKUP_PREFIX + str(old_id)[:12]
        if not all(n in names for n in (
                SOURCE_CONTAINER, FALLBACK_CONTAINER, VARIANT_CONTAINER,
                failed_name)):
            issues.append("PROTECTED_OR_FAILED_CONTAINERS_MISSING")
        if backup_name in names:
            issues.append("OLD_BACKUP_NAME_STILL_OCCUPIED")
        if issues:
            report["issues"] = sorted(set(issues))
            return report
        original, failed, flash, variant = (
            inspect(SOURCE_CONTAINER), inspect(failed_name),
            inspect(FALLBACK_CONTAINER), inspect(VARIANT_CONTAINER),
        )
        historical_result = historical()
        lineage = (historical_result.get("records") or {}).get("a") or {}
        if (historical_result.get("status") != "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED"
                or historical_result.get("issues")
                or lineage.get("id_27b") != old_id
                or lineage.get("image_27b") != PINNED_IMAGE):
            issues.append("P3_ORIGINAL_LINEAGE_UNVERIFIED")
        if (original.get("Id") != old_id
                or original.get("Image") != PINNED_IMAGE
                or original.get("Name") != "/" + SOURCE_CONTAINER
                or original.get("State", {}).get("Running") is not True
                or SOURCE_CONTAINER not in running):
            issues.append("ORIGINAL_27B_RESTORED_IDENTITY_UNVERIFIED")
        labels = (failed.get("Config") or {}).get("Labels") or {}
        if (failed.get("Name") != "/" + failed_name
                or failed.get("Image") != PINNED_IMAGE
                or (failed.get("State") or {}).get("Running") is not False
                or failed_name in running
                or labels.get("blazux.migration") != previous["prior_plan_id"]):
            issues.append("FAILED_NEW_NATIVE_CONTAINER_NOT_STOPPED_OR_OWNED")
        if (flash.get("State") or {}).get("Running") or (
                variant.get("State") or {}).get("Running"):
            issues.append("PRESERVED_FLASH_OR_TRIAL_VARIANT_RUNNING")
        if p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect):
            issues.append("FOREIGN_GPU_OWNER_AFTER_ROLLBACK")
        if not api(SERVED):
            issues.append("ORIGINAL_27B_API_HEALTH_UNVERIFIED")
        operation = ordinary_audit(OPS_ROOT)
        if (operation.get("status") != "VERIFIED"
                or operation.get("phase") != "COMMITTED"
                or operation.get("issues")):
            issues.append("ORDINARY_OPERATING_JOURNAL_NOT_CLEAN")
        marker = root / ("reconciled-" + previous["prior_plan_id"] + ".json")
        if marker.exists():
            item = _safe_json(marker)
            report["manual_reconciliation_recorded"] = (
                item.get("prior_plan_id") == previous["prior_plan_id"]
                and item.get("prior_result_sha256") == previous["prior_result_sha256"]
                and item.get("last_event_hash") == previous["last_event_hash"]
                and item.get("original_id") == old_id
            )
            if not report["manual_reconciliation_recorded"]:
                issues.append("RECONCILIATION_MARKER_DOES_NOT_MATCH_EVIDENCE")
    except (OSError, RuntimeError, ValueError, TypeError, KeyError,
            subprocess.TimeoutExpired):
        issues.append("READ_ONLY_RECONCILIATION_INSPECTION_FAILED")
    report["issues"] = sorted(set(issues))
    if not issues:
        report["status"] = "PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY"
        report["original_container_id"] = previous["prior_original_id"]
    return report


def accept_reconciliation() -> tuple[int, dict]:
    """Operator records explicit review; NO Docker or model-state mutation."""
    report = inspect_failed_rollback()
    if report.get("status") != "PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY":
        return 3, report
    if report["manual_reconciliation_recorded"]:
        return 3, {**report, "status": "ALREADY_RECONCILED"}
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return 3, {**report, "status": "BLOCKED",
                   "issues": ["REAL_OPERATOR_TTY_REQUIRED"]}
    expected = report["prior_plan_id"]
    print("Verified restored original Docker/API, event chain, and failed"
          " new container (read-only). This does not restart anything.")
    print("Prior failed migration ID: " + expected)
    try:
        typed = input("Type exact PRIOR failed plan SHA to record reconciliation: ")
        ack = input("Type I_REVIEWED_27B_BENCHMARK_FAILURE_AND_RESTORED_SERVICE: ")
    except (EOFError, KeyboardInterrupt):
        return 3, {**report, "status": "CANCELLED"}
    if (typed != expected
            or ack != "I_REVIEWED_27B_BENCHMARK_FAILURE_AND_RESTORED_SERVICE"):
        return 3, {**report, "status": "CANCELLED"}
    try:
        p3._private_dir(ROOT)
        # Re-verify after operator input; no blind assertion from stale stdout.
        updated = inspect_failed_rollback()
        if (updated.get("status") != "PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY"
                or updated.get("prior_plan_id") != expected):
            return 3, {**updated, "status": "BLOCKED"}
        path = ROOT / ("result-" + expected + ".json")
        previous = _safe_json(path)
        p3._write_once(ROOT, "reconciled-" + expected + ".json", {
            "prior_plan_id": expected,
            "prior_result_sha256": updated["prior_result_sha256"],
            "last_event_hash": updated["last_event_hash"],
            "original_id": updated["original_container_id"],
            "previous_status": previous["status"],
            "reconciled_at_utc": datetime.now(timezone.utc).isoformat(),
        })
        return 0, {**updated, "status": "RECONCILIATION_RECORDED",
                   "manual_reconciliation_recorded": True}
    except (OSError, ValueError, RuntimeError):
        return 3, {**report, "status": "BLOCKED",
                   "issues": ["RECONCILIATION_MARKER_WRITE_FAILED"]}


def _load_recipe() -> tuple[dict, str]:
    raw = RECIPE.read_bytes()
    if len(raw) > 32768:
        raise ValueError("RECIPE_TOO_LARGE")
    obj = json.loads(raw)
    if (obj.get("recipe_id") != "qwen38-27b"
            or obj.get("engine") != "vllm"
            or obj.get("vllm_version") != "0.32.0"
            or obj["runtime"]["local_image_id"] != PINNED_IMAGE
            or obj["model"]["revision"] != REVISION
            or obj["model"]["served_id"] != SERVED
            or obj["model"]["quantization"] != "modelopt_mixed"
            or obj["service"]["container_name"] != SOURCE_CONTAINER
            or obj["service"]["api_port"] != 8000
            or obj["native_tools"]["enabled"] is not True
            or obj["native_tools"]["tool_call_parser"] != "qwen3_coder"
            or obj["native_tools"]["reasoning_parser"] != "qwen3"
            or obj["native_tools"]["chat_template_sha256"] != EXPECTED_TEMPLATE_SHA256
            or obj["acceptance"]["fresh_benchmark_required"] is not True
            or obj["acceptance"]["backup_deletion_only_after_all_pass"] is not True
            or obj["benchmark"]["version"] != CANONICAL_VERSION
            or obj["benchmark"]["model"] != SERVED
            or obj["benchmark"]["requests"] != BENCHMARK_REQUEST_COUNT
            or obj["benchmark"]["max_tokens"] != CANONICAL_MAX_TOKENS
            or obj["benchmark"]["seed"] != BENCHMARK_SEED
            or obj["benchmark"]["temperature"] != 0
            or obj["benchmark"]["concurrency"] != 1
            or obj["benchmark"]["stream"] is not True
            or obj["benchmark"]["stream_options"] != {"include_usage": True}
            or obj["benchmark"]["chat_template_kwargs"] != {"enable_thinking": False}):
        raise ValueError("CANONICAL_27B_RECIPE_POLICY_MISMATCH")
    return obj, hashlib.sha256(raw).hexdigest()


def _canonical_benchmark() -> dict[str, Any]:
    """Read ONLY the pinned canonical benchmark profile from recipe."""
    recipe, _ = _load_recipe()
    profile = recipe["benchmark"]
    return benchmark_measure(
        chat_template_kwargs=profile["chat_template_kwargs"],
        max_tokens=profile["max_tokens"],
        version=profile["version"],
    )


def _candidate(recipe: dict, mount: Path, image_id: str, plan: str) -> list[str]:
    """Use the SINGLE CANONICAL pinned runtime JSON as launch source of truth."""
    m = recipe["model"]
    r = recipe["runtime"]
    n = recipe["native_tools"]
    if image_id != r["local_image_id"] or not p3.SHA.fullmatch(plan):
        raise ValueError("CANONICAL_RECIPE_IMAGE_OR_PLAN_CHANGED")
    if (r["max_model_len"] != 8192 or r["max_num_seqs"] != 1
            or r["gpu_memory_utilization"] != "0.70"
            or r["shm_size"] != "16g" or r["gpus"] != "all"
            or r["load_format"] != "safetensors"
            or r["dtype"] != "bfloat16"
            or r["enforce_eager"] is not True or r["port"] != 8000
            or n["chat_template"] != (
                "/hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/"
                + REVISION + "/chat_template.jinja")):
        raise ValueError("CANONICAL_27B_EXACT_LIVE_TEST_PROFILE_CHANGED")
    checkpoint = (
        "/hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/" + m["revision"]
    )
    return [
        "docker", "run", "-d", "--pull", "never",
        "--restart", "no", "--name", SOURCE_CONTAINER,
        "--gpus", r["gpus"], "--ipc=host", "--shm-size", r["shm_size"],
        "-p", str(r["port"]) + ":8000",
        "-v", str(mount) + ":/hf:ro",
        "-e", "HF_HOME=/hf", "-e", "HF_HUB_OFFLINE=1",
        "--label", "blazux.recipe=" + recipe["recipe_id"],
        "--label", "blazux.migration=" + plan,
        image_id, checkpoint,
        "--served-model-name", m["served_id"],
        "--host", "0.0.0.0", "--port", "8000",
        "--load-format", r["load_format"],
        "--quantization", m["quantization"],
        "--dtype", r["dtype"],
        "--max-model-len", str(r["max_model_len"]),
        "--max-num-seqs", str(r["max_num_seqs"]),
        "--gpu-memory-utilization", r["gpu_memory_utilization"],
        "--enforce-eager",
        "--chat-template", n["chat_template"],
        "--enable-auto-tool-choice",
        "--tool-call-parser", n["tool_call_parser"],
        "--reasoning-parser", n["reasoning_parser"],
    ]


def _event(root: Path, plan: str, phase: str, extra: dict | None = None) -> None:
    files = sorted(root.glob("event-*.json"))
    seq = len(files) + 1
    previous = _safe_json(files[-1]).get("event_hash") if files else None
    doc = {
        "schema_version": 1, "plan_id": plan, "seq": seq, "phase": phase,
        "previous_hash": previous,
        "utc": datetime.now(timezone.utc).isoformat(),
        "detail": extra or {},
    }
    doc["event_hash"] = _hash(doc)
    p3._write_once(root, f"event-{seq:04d}.json", doc)


def _promote_benchmark(root: Path, result: dict) -> None:
    """New canonical pointer is replaced; old historical benchmark is NOT."""
    path = root / "latest-27b-benchmark.json"
    tmp = root / ("benchmark-update-" + result["plan_id"][:12] + ".tmp")
    payload = json.dumps(result, indent=2, sort_keys=True) + "\n"
    fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.write(payload)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(tmp, path)
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def make_plan(*,
              run: Callable[..., Any] = gpu.call,
              inspect: Callable[..., dict] = gpu.docker_info,
              historical: Callable[[], dict] = historical_p3_receipts,
              audit: Callable[..., dict] = inspect_journal,
              api: Callable[[str], bool] = gpu.api_ready,
              root: Path = ROOT, now: float | None = None) -> dict:
    """No state changes; this plan only applies to the ORIGINAL unmodified 27B."""
    issues: list[str] = []
    try:
        prior = None
        if root.is_symlink() or (
                root.exists() and (root / "latest-27b-benchmark.json").exists()):
            issues.append("PRIOR_RECIPE_MIGRATION_ALREADY_PROMOTED_OR_UNSAFE")
        if root.exists() and list(root.glob("attempt-*.json")):
            reviewed = inspect_failed_rollback(
                root=root, run=run, inspect=inspect, api=api,
                historical=historical, ordinary_audit=audit,
            )
            if (reviewed.get("status") !=
                    "PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY"
                    or reviewed.get("manual_reconciliation_recorded") is not True):
                issues.append("PRIOR_RECIPE_MIGRATION_REQUIRES_RECONCILIATION")
                issues.extend(reviewed.get("issues") or [])
            else:
                prior = reviewed["prior_plan_id"]
        recipe, recipe_sha = _load_recipe()
        hist = historical()
        old = (hist.get("records") or {}).get("a") or {}
        if hist.get("status") != "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED" or hist.get("issues"):
            issues.append("HISTORICAL_P3_LINEAGE_UNVERIFIED")
        ordinary = audit(OPS_ROOT)
        if (ordinary.get("status") not in ("EMPTY", "VERIFIED") or ordinary.get("issues")
                or ordinary.get("phase") not in (None, "COMMITTED", "RESTORED", "CANCELLED")):
            issues.append("OLD_OPERATING_JOURNAL_NOT_CLEAN")
        names = _run_names(run, all_containers=True)
        running = _run_names(run, all_containers=False)
        if not all(n in names for n in (
                SOURCE_CONTAINER, FALLBACK_CONTAINER, VARIANT_CONTAINER)):
            issues.append("ORIGINAL_FLASH_OR_PROVEN_NATIVE_TRIAL_VARIANT_MISSING")
            return _issue(*issues)
        source, flash, variant = (
            inspect(SOURCE_CONTAINER), inspect(FALLBACK_CONTAINER),
            inspect(VARIANT_CONTAINER))
        if not all(_image_and_id(d) for d in (source, flash, variant)):
            issues.append("UNSAFE_DOCKER_CONTAINER_IMAGE_OR_ID")
        if (source.get("Id"), source.get("Image")) != (
                old.get("id_27b"), old.get("image_27b")):
            issues.append("ORIGINAL_P3_CONTAINER_LINEAGE_CHANGED")
        if (flash.get("Id"), flash.get("Image")) != (
                old.get("flash_id"), old.get("flash_image")):
            issues.append("FLASH_P3_CONTAINER_LINEAGE_CHANGED")
        if source.get("Image") != PINNED_IMAGE or variant.get("Image") != PINNED_IMAGE:
            issues.append("PINNED_VLLM_IMAGE_CHANGED")
        issues.extend(p3._container_checks(
            source, name=SOURCE_CONTAINER, image=PINNED_IMAGE,
            expected_id=old.get("id_27b"), running=True))
        issues.extend(p3._container_checks(
            variant, name=VARIANT_CONTAINER, image=PINNED_IMAGE,
            expected_id=variant.get("Id"), running=False))
        if not (source.get("State") or {}).get("Running") or SOURCE_CONTAINER not in running:
            issues.append("ORIGINAL_27B_NOT_RUNNING")
        if (variant.get("State") or {}).get("Running") or VARIANT_CONTAINER in running:
            issues.append("TRIAL_VARIANT_MUST_BE_STOPPED")
        if (flash.get("State") or {}).get("Running") or FALLBACK_CONTAINER in running:
            issues.append("FLASH_FALLBACK_MUST_BE_STOPPED")
        cmd = (source.get("Config") or {}).get("Cmd")
        native = (variant.get("Config") or {}).get("Cmd")
        if (not isinstance(cmd, list)
                or any(flag in cmd for flag in (*TOOL_FLAGS, "--chat-template"))
                or "--served-model-name" not in cmd
                or SERVED not in cmd
                or not any(isinstance(x, str) and "/snapshots/" + REVISION in x
                           for x in cmd)):
            issues.append("ORIGINAL_UNMODIFIED_27B_COMMAND_NOT_VERIFIED")
        if (not isinstance(native, list)
                or any(flag not in native for flag in TOOL_FLAGS)
                or recipe["native_tools"]["chat_template"] not in native):
            issues.append("NATIVE_TRIAL_FLAGS_OR_TEMPLATE_NOT_VERIFIED")
        label = ((variant.get("Config") or {}).get("Labels") or {}).get(TRIAL_LABEL)
        if not _trial_pass(label):
            issues.append("REAL_DGX_NATIVE_TOOLS_TRIAL_PROVENANCE_NOT_VERIFIED")
        mount = _protected_mount(source)
        if mount is None or _protected_mount(variant) != mount:
            issues.append("READ_ONLY_HF_CACHE_MOUNT_UNVERIFIED")
        if mount is not None:
            try:
                if _template_digest_from_mount(mount) != EXPECTED_TEMPLATE_SHA256:
                    issues.append("PINNED_NVIDIA_CHAT_TEMPLATE_HASH_DRIFT")
            except (OSError, RuntimeError, ValueError):
                issues.append("PINNED_NVIDIA_CHAT_TEMPLATE_UNAVAILABLE")
        if not _gpu_access(source) or not _gpu_access(variant):
            issues.append("GPU_DEVICE_REQUIREMENTS_UNVERIFIED")
        if p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect):
            issues.append("OTHER_GPU_MODEL_RUNNING")
        backup = BACKUP_PREFIX + str(source.get("Id", ""))[:12]
        if backup in names:
            issues.append("RECIPE_MIGRATION_BACKUP_NAME_OCCUPIED")
        # A previous FAILED native candidate may be preserved for diagnosis.
        # The separate rollback audit has already verified its provenance.
        if not api(SERVED):
            issues.append("CANONICAL_27B_API_UNHEALTHY")
        if (source.get("HostConfig") or {}).get("AutoRemove") is not False:
            issues.append("ORIGINAL_AUTO_REMOVE_UNSAFE")
        if issues:
            return _issue(*issues)
        window = int(time.time() if now is None else now) // 600
        facts = {
            "operation": "ONE_TIME_CANONICAL_27B_NATIVE_RECIPE_REPLACEMENT",
            "source_id": source["Id"], "image": source["Image"],
            "variant_id": variant["Id"], "trial_approval": label,
            "flash_id": flash["Id"], "recipe_sha": recipe_sha,
            "old_journal_hash": ordinary.get("last_event_hash"),
            "previous_reconciled_attempt": prior,
            "window": window, "port": 8000,
        }
        plan = _hash(facts)
        # Failed migration container names are unique to each attempt. The
        # previously failed trial's preserved container remains untouched.
        failed = FAIL_PREFIX + plan[:12]
        if failed in names:
            return _issue("RECIPE_MIGRATION_NEW_FAILED_NAME_OCCUPIED")
        # Verify command generation with the actual pinned cache mount.
        _candidate(recipe, mount, source["Image"], plan)
        return {
            "schema_version": 1, "action": "CANONICAL_27B_NATIVE_RECIPE_MIGRATION",
            "status": READY, "issues": [], "plan_id": plan,
            "source_container_id": source["Id"],
            "variant_trial_container_id": variant["Id"],
            "flash_id": flash["Id"],
            "backup_name": backup, "failed_name": failed,
            "image_id": source["Image"], "cache_mount": str(mount),
            "recipe_sha256": recipe_sha,
            "benchmark_profile": recipe["benchmark"],
            "previous_reconciled_attempt": prior,
            "expires_at_epoch_seconds": (window+1)*600,
            "port": 8000, "target_container": SOURCE_CONTAINER,
            "retain_model_files_and_image": True,
            "delete_backup_only_after_benchmark_pass": True,
            "overwrite_latest_benchmark_pointer": True,
            "historical_p3_receipts_immutable": True,
            "executed": False, "approval_accepted": False,
            "required_downtime_ack": ACK, "required_cleanup_ack": ACK_DELETE,
            "notice": ("Read-only. Actual execution recreates canonical 27B, "
                       "validates chat/native tools/SSE and NEW bounded benchmark, "
                       "promotes new latest benchmark, and deletes only the "
                       "verified old backup container after PASS. Downtime required. "
                       "Original P3 container ID becomes historical."),
        }
    except (OSError, RuntimeError, ValueError, TypeError, KeyError,
            json.JSONDecodeError, subprocess.TimeoutExpired):
        return _issue("RECIPE_MIGRATION_READ_ONLY_PREFLIGHT_UNAVAILABLE", *issues)


def execute(plan_id: str, downtime_ack: str, delete_ack: str, *,
            planner: Callable[..., dict] = make_plan,
            run: Callable[..., Any] = gpu.call,
            inspect: Callable[..., dict] = gpu.docker_info,
            waiter: Callable[..., bool] = gpu.wait_for,
            chat: Callable[[str], bool] = verify_chat,
            tools: Callable[[], dict] = structured_probe,
            stream: Callable[[], dict] = probe_stream,
            benchmark: Callable[[], dict] = _canonical_benchmark,
            api: Callable[[str], bool] = gpu.api_ready,
            root: Path = ROOT, clock: Callable[[], float] = time.time
            ) -> tuple[int, dict]:
    if (not isinstance(plan_id, str) or not p3.SHA.fullmatch(plan_id)
            or downtime_ack != ACK or delete_ack != ACK_DELETE):
        return 3, _issue("NEW_EXACT_SHA_DOWNTIME_AND_DELETE_ACK_REQUIRED")
    locks: list[int] = []
    try:
        for folder in (OPS_ROOT, TRIAL_ROOT, root):
            p3._private_dir(folder)
        for name in (
            OPS_ROOT / "operating-execution.lock",
            TRIAL_ROOT / "native-tools-trial.lock",
            root / "recipe-migration.lock",
        ):
            fd = os.open(name, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
            if os.fstat(fd).st_mode & 0o077:
                os.close(fd)
                raise ValueError("UNSAFE_MIGRATION_LOCK")
            locks.append(fd)
        for fd in locks:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        p = planner(root=root)
        remain = p.get("expires_at_epoch_seconds", 0) - clock()
        if (p.get("status") != READY or p.get("plan_id") != plan_id
                or not 30 < remain <= 600):
            return 3, _issue("CHANGED_EXPIRED_OR_UNQUALIFIED_RECIPE_PLAN")
        recipe, current_sha = _load_recipe()
        if current_sha != p["recipe_sha256"]:
            return 3, _issue("RECIPE_SOURCE_CHANGED_BEFORE_EXECUTION")
        name, backup, failed = SOURCE_CONTAINER, p["backup_name"], p["failed_name"]
        # Consumed plan marker persists after a crash and blocks auto retry.
        p3._write_once(root, "attempt-" + plan_id + ".json", {
            "plan_id": plan_id, "source_id": p["source_container_id"],
            "recipe_sha256": current_sha, "utc": datetime.now(timezone.utc).isoformat(),
        })
        _event(root, plan_id, "PLANNED")
        stopped = False
        renamed = False
        committed = False
        new_id = None
        result: dict[str, Any] = {
            "schema_version": 1, "action": "CANONICAL_27B_NATIVE_RECIPE_MIGRATION",
            "plan_id": plan_id, "status": "BLOCKED",
            "executed": False, "issues": [], "original_restored": False,
            "native_tools_pass": False, "benchmark_pass": False,
            "benchmark_promoted": False, "backup_container_deleted": False,
            "served_id": SERVED, "api_port": 8000,
        }
        try:
            old = inspect(name)
            if (old.get("Id") != p["source_container_id"]
                    or old.get("Image") != p["image_id"]
                    or not (old.get("State") or {}).get("Running")
                    or backup in _run_names(run, all_containers=True)
                    or failed in _run_names(run, all_containers=True)
                    or p3._gpu_conflicts(name, run, inspect)):
                raise RuntimeError("MIGRATION_FINAL_ORIGINAL_IDENTITY_DRIFT")
            argv = _candidate(recipe, Path(p["cache_mount"]), p["image_id"], plan_id)
            _event(root, plan_id, "OLD_STOPPING")
            stopped = True
            r = run(["docker", "stop", "--time", "45", name], timeout=80)
            if r.returncode or gpu.running(name, run):
                raise RuntimeError("ORIGINAL_27B_STOP_NOT_CONFIRMED")
            _event(root, plan_id, "OLD_STOPPED")
            r = run(["docker", "rename", name, backup], timeout=30)
            if r.returncode:
                raise RuntimeError("BACKUP_RENAME_FAILED")
            renamed = True
            _event(root, plan_id, "BACKUP_PRESERVED", {"backup": backup})
            for _ in range(30):
                if gpu.port_free(run):
                    break
                time.sleep(1)
            else:
                raise RuntimeError("HOST_PORT_8000_NOT_RELEASED")
            if p3._gpu_conflicts(name, run, inspect, require_source_running=False):
                raise RuntimeError("GPU_NOT_EXCLUSIVE_BEFORE_NEW_SERVE")
            _event(root, plan_id, "NEW_STARTING")
            r = run(argv, timeout=90)
            if r.returncode:
                raise RuntimeError("CANONICAL_27B_NATIVE_CONTAINER_CREATE_FAILED")
            created = inspect(name)
            new_id = created.get("Id")
            if (not _image_and_id(created) or created.get("Image") != p["image_id"]
                    or not (created.get("State") or {}).get("Running")
                    or ((created.get("Config") or {}).get("Labels") or {}).get(
                        "blazux.migration") != plan_id):
                raise RuntimeError("NEW_CANONICAL_CONTAINER_PROVENANCE_MISMATCH")
            if not waiter(name, SERVED, 600, run=run):
                raise RuntimeError("NEW_CANONICAL_API_WAIT_FAILED")
            if not api(SERVED) or not chat(SERVED):
                raise RuntimeError("NEW_CANONICAL_NORMAL_CHAT_FAILED")
            if p3._gpu_conflicts(name, run, inspect):
                raise RuntimeError("NEW_CANONICAL_GPU_EXCLUSIVITY_FAILED")
            tool_result = tools()
            if (tool_result.get("status") != "LOCAL_STRUCTURED_TOOL_CYCLE_PASS"
                    or tool_result.get("structured_tool_call") is not True
                    or tool_result.get("tool_result_continuation") is not True):
                raise RuntimeError("NEW_CANONICAL_STRUCTURED_TOOLS_FAILED")
            sse = stream()
            if (sse.get("status") != "LOCAL_STREAMED_TOOL_CALL_PASS"
                    or sse.get("streamed_tool_call") is not True):
                raise RuntimeError("NEW_CANONICAL_STREAMED_TOOL_CALL_FAILED")
            result["native_tools_pass"] = True
            _event(root, plan_id, "NATIVE_TOOLS_VERIFIED")
            measured = benchmark()
            # Preserve per-request diagnostics BEFORE the acceptance test;
            # the prior failure discarded these values, leaving only a
            # generic NEW_CANONICAL_BENCHMARK_NOT_QUALIFIED error.
            # Benchmark output contains token counts, times and prompt hashes,
            # never generated text or user prompts.
            if not isinstance(measured, dict):
                raise ValueError("BENCHMARK_RETURNED_NON_OBJECT")
            samples = measured.get("samples")
            summary = {
                "status": measured.get("status"),
                "benchmark_version": measured.get("benchmark_version"),
                "model": measured.get("model"),
                "requests": measured.get("requests"),
                "chat_template_kwargs": measured.get("chat_template_kwargs"),
                "metrics": measured.get("metrics"),
                "samples": [{
                    "index": row.get("index"),
                    "success": row.get("success"),
                    "stream_complete": row.get("stream_complete"),
                    "stream_finish_reason": row.get("stream_finish_reason"),
                    "usage_reported": row.get("usage_reported"),
                    "content_observed": row.get("content_observed"),
                    "reasoning_observed": row.get("reasoning_observed"),
                    "completion_tokens": row.get("completion_tokens"),
                    "ttft_sec": row.get("ttft_sec"),
                    "failure_reasons": row.get("failure_reasons", []),
                } for row in samples if isinstance(row, dict)]
                if isinstance(samples, list) else None,
            }
            result["benchmark_diagnostics"] = summary
            p3._write_once(root, "benchmark-observed-" + plan_id + ".json", measured)
            _event(root, plan_id, "BENCHMARK_MEASURED", {
                "status": summary["status"],
                "all_samples_pass": (
                    isinstance(samples, list)
                    and len(samples) == 3
                    and all(isinstance(row, dict) and row.get("success") is True
                            for row in samples)
                ),
            })
            if (measured.get("status") != "PASS"
                    or measured.get("benchmark_version") !=
                        recipe["benchmark"]["version"]
                    or measured.get("max_tokens") !=
                        recipe["benchmark"]["max_tokens"]
                    or measured.get("chat_template_kwargs") !=
                        recipe["benchmark"]["chat_template_kwargs"]
                    or measured.get("model") != SERVED
                    or measured.get("requests") != 3
                    or not isinstance(measured.get("samples"), list)
                    or len(measured["samples"]) != 3
                    or not all(sample.get("success") is True
                               for sample in measured["samples"])
                    or not isinstance(measured.get("metrics"), dict)
                    or not isinstance(measured["metrics"].get(
                        "mean_e2e_tokens_per_sec"), (float, int))
                    or measured["metrics"]["mean_e2e_tokens_per_sec"] <= 0):
                raise RuntimeError("NEW_CANONICAL_BENCHMARK_NOT_QUALIFIED")
            result["benchmark_pass"] = True
            result["benchmark_version"] = measured.get("benchmark_version")
            result["metrics"] = measured["metrics"]
            _event(root, plan_id, "BENCHMARK_PASS")
            # The full benchmark receipt and current pointer precede deletion.
            p3._write_once(root, "benchmark-" + plan_id + ".json", measured)
            if not api(SERVED) or not chat(SERVED):
                raise RuntimeError("CANONICAL_API_DRIFT_AFTER_BENCH")
            actual = inspect(name)
            preserved = inspect(backup)
            if (actual.get("Id") != new_id or actual.get("Image") != p["image_id"]
                    or not (actual.get("State") or {}).get("Running")
                    or preserved.get("Id") != p["source_container_id"]
                    or preserved.get("Image") != p["image_id"]
                    or (preserved.get("State") or {}).get("Running")):
                raise RuntimeError("PRE_DELETE_PROVENANCE_OR_STATE_MISMATCH")
            _event(root, plan_id, "COMMIT_READY")
            latest = {
                "schema_version": 1, "status": "PASS",
                "model": SERVED, "recipe_sha256": current_sha,
                "container_id": new_id, "plan_id": plan_id,
                "benchmark": measured, "promoted_utc": datetime.now(timezone.utc).isoformat(),
            }
            _promote_benchmark(root, latest)
            result["benchmark_promoted"] = True
            # The latest benchmark now describes the NEW active container.
            # Do not silently roll back the model on any later bookkeeping
            # or cleanup failure, as that would make the pointer dishonest.
            committed = True
            # Independent immutable commit proof, before authorized cleanup.
            p3._write_once(root, "commit-" + plan_id + ".json", {
                "status": "BENCHMARK_VERIFIED_NATIVE_RECIPE_COMMITTED",
                "plan_id": plan_id, "recipe_sha256": current_sha,
                "source_id": p["source_container_id"],
                "new_id": new_id, "backup_name": backup,
                "benchmark_status": measured["status"],
            })
            _event(root, plan_id, "COMMITTED")
            # Explicit user-approved deletion of ONLY the stopped, verified backup.
            preserved = inspect(backup)
            if (preserved.get("Id") != p["source_container_id"]
                    or preserved.get("Image") != p["image_id"]
                    or (preserved.get("State") or {}).get("Running")):
                raise RuntimeError("BACKUP_CONTAINER_CHANGED_BEFORE_CLEANUP")
            removal = run(["docker", "rm", backup], timeout=45)
            if removal.returncode:
                result["issues"].append("BACKUP_CONTAINER_DELETE_FAILED")
                result["status"] = "COMMITTED_CLEANUP_PENDING"
            elif backup in _run_names(run, all_containers=True):
                result["issues"].append("BACKUP_CONTAINER_DELETE_NOT_CONFIRMED")
                result["status"] = "COMMITTED_CLEANUP_PENDING"
            else:
                result["backup_container_deleted"] = True
                result["status"] = "COMMITTED"
            result["executed"] = True
            result["active_container"] = name
            result["new_container_id"] = new_id
        except (OSError, RuntimeError, ValueError, TypeError,
                subprocess.TimeoutExpired, KeyboardInterrupt) as exc:
            reason = str(exc)[:100] if isinstance(exc, RuntimeError) else type(exc).__name__
            result["issues"].append("MIGRATION_ERROR_" + reason)
            if committed:
                result["status"] = "COMMITTED_CLEANUP_PENDING"
                result["executed"] = True
                result["active_container"] = name
                result["new_container_id"] = new_id
            elif stopped:
                try:
                    current_names = _run_names(run, all_containers=True)
                    if name in current_names and renamed:
                        created = inspect(name)
                        labels = (created.get("Config") or {}).get("Labels") or {}
                        if (created.get("Image") != p["image_id"]
                                or labels.get("blazux.migration") != plan_id):
                            raise RuntimeError("FOREIGN_NEW_CONTAINER_CANNOT_RENAME")
                        if (created.get("State") or {}).get("Running"):
                            if run(["docker", "stop", "--time", "45", name], timeout=80).returncode:
                                raise RuntimeError("NEW_NATIVE_STOP_FOR_RESTORE_FAILED")
                        if run(["docker", "rename", name, failed], timeout=30).returncode:
                            raise RuntimeError("FAILED_NATIVE_RENAME_FAILED")
                    if renamed:
                        backup_doc = inspect(backup)
                        if (backup_doc.get("Id") != p["source_container_id"]
                                or backup_doc.get("Image") != p["image_id"]):
                            raise RuntimeError("BACKUP_ORIGINAL_ID_DRIFT")
                        if run(["docker", "rename", backup, name], timeout=30).returncode:
                            raise RuntimeError("ORIGINAL_BACKUP_NAME_RESTORE_FAILED")
                    for _ in range(30):
                        if gpu.port_free(run):
                            break
                        time.sleep(1)
                    else:
                        raise RuntimeError("PORT_NOT_FREE_FOR_ORIGINAL_RECOVERY")
                    if p3._gpu_conflicts(name, run, inspect,
                                         require_source_running=False):
                        raise RuntimeError("FOREIGN_GPU_PREVENTS_ORIGINAL_RECOVERY")
                    old = inspect(name)
                    if old.get("Id") != p["source_container_id"]:
                        raise RuntimeError("ORIGINAL_CONTAINER_ID_CHANGED")
                    if not (old.get("State") or {}).get("Running"):
                        if run(["docker", "start", name], timeout=90).returncode:
                            raise RuntimeError("ORIGINAL_CONTAINER_RESTART_FAILED")
                    if not waiter(name, SERVED, 600, run=run) or not api(SERVED):
                        raise RuntimeError("ORIGINAL_API_NOT_RESTORED")
                    _event(root, plan_id, "RESTORED")
                    result["status"] = "FAIL_RESTORED"
                    result["original_restored"] = True
                    result["executed"] = True
                except (OSError, RuntimeError, ValueError, TypeError,
                        subprocess.TimeoutExpired) as error:
                    result["issues"].append("RECOVERY_ERROR_" + type(error).__name__)
                    result["status"] = "RECOVERY_FAILED"
                    result["executed"] = True
                    try:
                        _event(root, plan_id, "RECOVERY_FAILED")
                    except (OSError, RuntimeError, ValueError):
                        result["issues"].append("RECOVERY_JOURNAL_WRITE_FAILED")
            else:
                result["status"] = "CANCELLED"
                try:
                    _event(root, plan_id, "CANCELLED")
                except (OSError, RuntimeError, ValueError):
                    result["issues"].append("CANCELLED_JOURNAL_WRITE_FAILED")
        try:
            p3._write_once(root, "result-" + plan_id + ".json", result)
        except (OSError, RuntimeError, ValueError):
            result["status"] = "EVIDENCE_WRITE_FAILED"
            result["issues"].append("RESULT_RECEIPT_WRITE_FAILED")
        return (0 if result["status"] == "COMMITTED" else 4), result
    except (OSError, RuntimeError, ValueError, TypeError,
            subprocess.TimeoutExpired, BlockingIOError):
        return 3, _issue("RECIPE_MIGRATION_GUARD_OR_LOCK_FAILED")
    finally:
        for fd in reversed(locks):
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)


def inspect_promoted_service(*,
        inspect: Callable[..., dict] = gpu.docker_info,
        run: Callable[..., Any] = gpu.call,
        api: Callable[[str], bool] = gpu.api_ready,
        root: Path = ROOT) -> dict:
    """Bounded read-only post-migration identity plus NEW benchmark evidence."""
    report = {
        "schema_version": 1, "action": "CANONICAL_27B_NATIVE_RECIPE_STATUS",
        "status": "BLOCKED", "issues": [], "executed": False,
        "api_model_id": SERVED, "api_port": 8000,
        "native_tools_qualified_by_one_shot": False,
        "latest_benchmark_verified": False,
        "backup_container_deleted": False,
    }
    try:
        recipe, recipe_sha = _load_recipe()
        names = _run_names(run, all_containers=True)
        active_names = _run_names(run, all_containers=False)
        if SOURCE_CONTAINER not in active_names:
            report["issues"].append("CANONICAL_27B_NOT_RUNNING")
            return report
        doc = inspect(SOURCE_CONTAINER)
        labels = (doc.get("Config") or {}).get("Labels") or {}
        cmd = (doc.get("Config") or {}).get("Cmd")
        if (not _image_and_id(doc)
                or doc.get("Image") != PINNED_IMAGE
                or doc.get("Name") != "/" + SOURCE_CONTAINER
                or labels.get("blazux.recipe") != "qwen38-27b"
                or not p3.SHA.fullmatch(str(labels.get("blazux.migration") or ""))):
            report["issues"].append("NEW_CANONICAL_CONTAINER_NOT_IDENTIFIED")
        if (not isinstance(cmd, list)
                or not all(flag in cmd for flag in TOOL_FLAGS)
                or recipe["native_tools"]["chat_template"] not in cmd):
            report["issues"].append("CANONICAL_NATIVE_TOOLS_FLAGS_NOT_OBSERVED")
        if p3._gpu_conflicts(SOURCE_CONTAINER, run, inspect):
            report["issues"].append("ANOTHER_GPU_CONTAINER_RUNNING")
        if not api(SERVED):
            report["issues"].append("CANONICAL_API_IDENTITY_UNVERIFIED")
        latest = _safe_json(root / "latest-27b-benchmark.json")
        if (latest.get("status") != "PASS"
                or latest.get("model") != SERVED
                or latest.get("container_id") != doc.get("Id")
                or latest.get("recipe_sha256") != recipe_sha
                or latest.get("plan_id") != labels.get("blazux.migration")
                or (latest.get("benchmark") or {}).get("status") != "PASS"):
            report["issues"].append("LATEST_BENCHMARK_IDENTITY_MISMATCH")
        else:
            report["latest_benchmark_verified"] = True
            report["benchmark_metrics"] = latest["benchmark"].get("metrics")
        backups = [name for name in names if name.startswith(BACKUP_PREFIX)]
        report["backup_container_deleted"] = not backups
        if backups:
            report["issues"].append("OLD_BACKUP_CONTAINER_CLEANUP_PENDING")
        if not report["issues"]:
            report["status"] = "LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED"
            report["native_tools_qualified_by_one_shot"] = True
    except (OSError, ValueError, RuntimeError, KeyError, TypeError,
            subprocess.TimeoutExpired):
        report["issues"].append("CANONICAL_NATIVE_RUNTIME_AUDIT_UNAVAILABLE")
    report["issues"] = sorted(set(report["issues"]))
    report["notice"] = (
        "Read-only current Docker/API and pinned benchmark identity. "
        "Historical P3 receipts remain immutable and identify the retired "
        "pre-native container; ordinary P3/operating switches are not "
        "qualified to reuse those historical container IDs."
    )
    return report


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Migrate original canonical 27B to pinned Native Tools recipe")
    parser.add_argument(
        "action",
        choices=("plan", "execute", "status", "audit-failure", "reconcile"),
    )
    args = parser.parse_args(argv)
    if args.action == "audit-failure":
        report = inspect_failed_rollback()
        print(json.dumps(report, indent=2, sort_keys=True))
        return (0 if report.get("status") ==
                "PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY" else 3)
    if args.action == "reconcile":
        code, report = accept_reconciliation()
        print(json.dumps(report, indent=2, sort_keys=True))
        return code
    if args.action == "status":
        summary = inspect_promoted_service()
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0 if summary["status"] == "LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED" else 3
    plan = make_plan()
    if args.action == "plan":
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0 if plan["status"] == READY else 3
    if plan.get("status") != READY:
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 3
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        print("BLOCKED: requires an actual interactive DGX terminal")
        return 3
    print("Fresh exact recipe migration plan SHA: " + plan["plan_id"])
    print("Expires at epoch: " + str(plan["expires_at_epoch_seconds"]))
    print("This WILL stop API :8000, replace the canonical 27B container,")
    print("run live chat, native-tool, SSE, 3-request benchmark, overwrite")
    print("ONLY the latest benchmark POINTER, then delete OLD BACKUP CONTAINER.")
    print("Old P3 receipts and original benchmark files remain immutable.")
    print("A host/Docker/OOM failure may defeat automatic rollback.")
    try:
        approved = input("Type exact fresh plan SHA: ").strip()
        down = input("Type downtime ack " + ACK + ": ").strip()
        cleanup = input("Type backup deletion ack " + ACK_DELETE + ": ").strip()
    except (EOFError, KeyboardInterrupt):
        print("CANCELLED: service untouched")
        return 3
    previous = signal.getsignal(signal.SIGTERM)
    def _interrupt(_s: int, _frame: Any) -> None:
        raise KeyboardInterrupt("MIGRATION_SIGTERM")
    signal.signal(signal.SIGTERM, _interrupt)
    try:
        rc, report = execute(approved, down, cleanup)
    finally:
        signal.signal(signal.SIGTERM, previous)
    print(json.dumps(report, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
