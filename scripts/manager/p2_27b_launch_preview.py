"""Read-only P2 NVIDIA 27B *dedicated* launch specification and safety preview.

Deliberately no executor/approve path. This composes immutable source/image
identities, current live service + localhost API evidence, and a proposed
27B-specific argv. It never starts/stops Docker or loads a model.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any, Callable

from scripts.manager.p2_27b_download import REVISION
from scripts.manager.p2_27b_inventory import REPO_DIR
from scripts.manager.p2_27b_qualification import inspect_27b_runtime
from scripts.manager.service_manifest import inspect_service
from scripts.manager.service_health import inspect_api_health

IMAGE_RE = re.compile(r"^sha256:[0-9a-f]{64}$")
MODEL = "nvidia/Qwen3.8-27B-NVFP4"
SERVED = "qwen3.8-27b"
TARGET_CONTAINER = "qwen38-27b"
ORIGINAL_CONTAINER = "qwen38-flash"
ORIGINAL_ID = "qwen3.8-flash-next"
HOST_PORT = 8000

# Official vLLM Qwen3.8-27B recipe tool profile. Opt-in ONLY: the
# historical P2/P3 exact-approved container is immutable and may NOT be
# recreated or have its startup flags changed by merely updating source.
TOOL_CALLING_ARGS = (
    "--enable-auto-tool-choice",
    "--tool-call-parser", "qwen3_coder",
    "--reasoning-parser", "qwen3",
)

# Conservative *unvalidated* first-boot settings. Not a memory-fit claim.
PROFILE = {
    "max_model_len": 8192,
    "max_num_seqs": 1,
    "gpu_memory_utilization": "0.70",
    "quantization": "modelopt_mixed",
    "load_format": "safetensors",
    "enforce_eager": True,
    "enable_speculative_decoding": False,
    "enable_ple": False,
}


def _cache_path(cache_root: Path | None) -> Path:
    return Path(cache_root or os.environ.get(
        "HF_CACHE", str(Path.home() / ".cache/huggingface"))).expanduser().resolve()


def _candidate_argv(cache: Path, image_id: str, *,
                    tool_calling: bool = False) -> list[str]:
    """Source-only command candidate; opt-in tool profile never changes old trials.

    Existing P2/P3 executions use tool_calling=False by default. Do NOT use
    this command to replace the preserved 27B container; separate runtime
    migration, rollback planning, and operator downtime consent are required.
    """
    if not IMAGE_RE.fullmatch(image_id):
        raise ValueError("invalid immutable local image ID")
    snapshot = f"/hf/hub/{REPO_DIR}/snapshots/{REVISION}"
    command = [
        "docker", "run", "-d", "--name", TARGET_CONTAINER,
        "--gpus", "all", "--ipc=host", "--shm-size", "16g",
        "-p", f"{HOST_PORT}:8000",
        "-v", f"{cache}:/hf:ro", "-e", "HF_HOME=/hf",
        "-e", "HF_HUB_OFFLINE=1",
        image_id,
        snapshot, "--served-model-name", SERVED,
        "--host", "0.0.0.0", "--port", "8000",
        "--load-format", PROFILE["load_format"],
        "--quantization", PROFILE["quantization"],
        "--dtype", "bfloat16",
        "--max-model-len", str(PROFILE["max_model_len"]),
        "--max-num-seqs", str(PROFILE["max_num_seqs"]),
        "--gpu-memory-utilization", PROFILE["gpu_memory_utilization"],
        "--enforce-eager",
    ]
    if tool_calling:
        command.extend(TOOL_CALLING_ARGS)
    return command


def build_27b_launch_preview(
    *, cache_root: Path | None = None,
    runtime_inspector: Callable[..., dict[str, Any]] = inspect_27b_runtime,
    service_inspector: Callable[..., dict[str, Any]] = inspect_service,
    health_inspector: Callable[..., dict[str, Any]] = inspect_api_health,
) -> dict[str, Any]:
    """Collect evidence for a separately approved future transition; always blocked."""
    cache = _cache_path(cache_root)
    issues: list[str] = []
    try:
        runtime = runtime_inspector(cache_root=cache)
    except (OSError, ValueError, RuntimeError) as exc:
        runtime = {"status": "BLOCKED", "issues": [
            "RUNTIME_OBSERVATION_FAILED:" + type(exc).__name__]}
    try:
        service = service_inspector()
    except (OSError, ValueError, RuntimeError) as exc:
        service = {"status": "BLOCKED", "issues": [
            "SERVICE_OBSERVATION_FAILED:" + type(exc).__name__]}

    # Only read current local API when the observed service is unambiguous.
    health: dict[str, Any]
    if (service.get("status") == "OBSERVED_UNQUALIFIED"
            and service.get("observed_model") == "flash-next"
            and service.get("api_port_8000_listening") is True):
        try:
            health = health_inspector(service=service)
        except (OSError, ValueError, RuntimeError) as exc:
            health = {"status": "BLOCKED", "issues": [
                "API_HEALTH_OBSERVATION_FAILED:" + type(exc).__name__]}
    else:
        health = {"status": "NOT_QUERIED", "api_identity_verified": False,
                  "issues": ["SOURCE_SERVICE_NOT_UNAMBIGUOUS"]}

    if runtime.get("source_files_present") is not True:
        issues.append("PINNED_SOURCE_NOT_READY")
    if runtime.get("revision") != REVISION:
        issues.append("SOURCE_REVISION_MISMATCH")
    if runtime.get("metadata_matches_expected") is not True:
        issues.append("MODEL_METADATA_NOT_QUALIFIED")
    quant = runtime.get("quantization_audit") or {}
    if (quant.get("status") != "PINNED_METADATA_PARSED_UNQUALIFIED"
            or quant.get("mixed_fp8_nvfp4_metadata") is not True
            or quant.get("revision") != REVISION):
        issues.append("PINNED_MODEL_OPT_MIX_NOT_CONFIRMED")
    if runtime.get("host_architecture") not in ("arm64", "aarch64"):
        issues.append("HOST_PLATFORM_NOT_QUALIFIED")
    image = runtime.get("image") or {}
    image_id = image.get("image_id")
    image_valid = (isinstance(image_id, str)
                   and IMAGE_RE.fullmatch(image_id) is not None
                   and image.get("vllm032_label_matches") is True
                   and image.get("architecture") == "arm64"
                   and image.get("os") == "linux")
    if not image_valid:
        issues.append("LOCAL_VLLM032_IMAGE_NOT_QUALIFIED")
    if not image.get("repo_digests"):
        issues.append("REGISTRY_IMAGE_DIGEST_NOT_OBSERVED")

    managed = service.get("managed_containers")
    if service.get("status") != "OBSERVED_UNQUALIFIED":
        issues.append("LIVE_SERVICE_INVENTORY_UNVERIFIED")
    if service.get("observed_model") != "flash-next":
        issues.append("EXPECTED_FLASH_NEXT_SOURCE_NOT_OBSERVED")
    if service.get("api_port_8000_listening") is not True:
        issues.append("SOURCE_PORT_NOT_OBSERVED")
    if service.get("download_running") is not False:
        issues.append("MODEL_DOWNLOAD_ACTIVITY_UNVERIFIED")
    # An unqualified/older managed service manifest cannot prove no name clash.
    if not isinstance(managed, list):
        issues.append("MANAGED_CONTAINER_INVENTORY_MISSING")
        managed = []
    if any(c.get("container_name") == TARGET_CONTAINER for c in managed
           if isinstance(c, dict)):
        issues.append("TARGET_CONTAINER_NAME_ALREADY_EXISTS")
    source_containers = [
        c for c in managed if isinstance(c, dict)
        and c.get("model") == "flash-next"
        and c.get("container_name") == ORIGINAL_CONTAINER
        and str(c.get("status", "")).startswith("Up")
        and isinstance(c.get("image_id"), str)
        and IMAGE_RE.fullmatch(c["image_id"])
    ]
    if len(source_containers) != 1:
        issues.append("SOURCE_CONTAINER_IMAGE_NOT_UNAMBIGUOUS")
    if health.get("status") != "API_IDENTITY_CONFIRMED" or (
            health.get("api_identity_verified") is not True
            or health.get("expected_model_id") != ORIGINAL_ID
            or ORIGINAL_ID not in health.get("model_ids", [])):
        issues.append("SOURCE_API_IDENTITY_NOT_CONFIRMED")

    # These gates are intentionally unconditionally unresolved. Static symbols,
    # source files, argv, and live API identity do not qualify a GPU rollout.
    issues.extend((
        "27B_GPU_KERNEL_AND_LOADER_NOT_VERIFIED",
        "27B_MEMORY_CONTEXT_PROFILE_NOT_VERIFIED",
        "VERIFIED_IMAGE_RECIPE_AND_ROLLBACK_ABSENT",
        "SERVICE_TRANSITION_REQUIRES_SEPARATE_APPROVAL",
        "P2_RUNTIME_EXECUTOR_NOT_ENABLED",
    ))
    # A preview is only displayed when its source image identity is well-formed.
    # It is NOT an executable plan nor an approval token.
    preview = _candidate_argv(cache, image_id) if image_valid else None
    return {
        "schema_version": 1, "stage": "p2", "action": "start-preview",
        "scope": "DGX_LOCAL_READ_ONLY", "status": "BLOCKED",
        "executed": False, "approval_accepted": False,
        "operations_enabled": False, "plan_id": None, "gpu_verified": False,
        "runtime_qualified": False, "source_revision": REVISION,
        "source_checkpoint_status": runtime.get("source_checkpoint_status"),
        "source_quantization": {
            "status": quant.get("status"),
            "layer_count": quant.get("layer_count"),
            "algorithms": quant.get("layer_algorithms"),
        },
        "local_image_id": image_id if image_valid else None,
        "profile": dict(PROFILE),
        "observed_source": {
            "model": service.get("observed_model"),
            "container": ORIGINAL_CONTAINER if len(source_containers) == 1 else None,
            "container_image_id": (source_containers[0]["image_id"]
                                   if len(source_containers) == 1 else None),
            "api_identity_confirmed": (
                health.get("status") == "API_IDENTITY_CONFIRMED"
                and health.get("api_identity_verified") is True),
        },
        "command_preview": preview,
        "transition_order": [
            "verify-live-source-api-and-GPU",
            "approve-exact-source-target-recovery-transaction",
            "stop-only-approved-source-container",
            "verify-single-GPU-model-and-port-8000-free",
            "start-approved-27b-command",
            "wait-for-health-and-exact-model-ID",
            "run-bounded-chat-tools-vision-and-benchmark",
            "commit-or-restore-original-Flash-Next-and-verify",
        ],
        "issues": sorted(set(issues)),
        "notice": ("PLAN ONLY; command_preview is NOT authorized. "
                   "Do not paste into a shell or stop Flash-Next. "
                   "No Docker run/stop, GPU execution, cache mutation, or transition."),
    }
