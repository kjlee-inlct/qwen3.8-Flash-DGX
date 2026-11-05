"""Read-only P2 NVIDIA 27B runtime qualification evidence, never launch authority.

Inspect immutable HF source, existing Docker image metadata and actual managed
service observations. No network requests, inference, Docker run/stop, GPU
allocation, model download, cache writes or approval construction.
"""
from __future__ import annotations

import json
import platform
from pathlib import Path
import re
import subprocess
from typing import Any, Callable

from scripts.manager.p2_27b_download import IMAGE, REVISION
from scripts.manager.p2_27b_inventory import inspect_27b
from scripts.manager.service_manifest import inspect_service

IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")
MAX_IMAGE_JSON = 256 * 1024
EXPECTED_ARCHITECTURE = "Qwen3_5ForConditionalGeneration"
EXPECTED_MODEL_TYPE = "qwen3_5"
EXPECTED_QUANT_METHOD = "modelopt"


def _image_facts(runner: Callable[..., Any]) -> dict[str, Any]:
    """Docker image *inspect* is metadata-only; no executable Docker subcommand."""
    result: dict[str, Any] = {
        "status": "UNVERIFIED", "tag": IMAGE, "image_id": None,
        "architecture": None, "os": None, "base_label": None,
        "repo_digests": [], "vllm032_label_matches": False,
    }
    try:
        cmd = ["docker", "image", "inspect", IMAGE, "--format", "{{json .}}"]
        process = runner(cmd, check=False, capture_output=True,
                         text=True, timeout=10)
        if process.returncode != 0:
            result["status"] = "IMAGE_INSPECT_FAILED"
            return result
        payload = process.stdout
        if len(payload.encode("utf-8")) > MAX_IMAGE_JSON:
            result["status"] = "IMAGE_METADATA_TOO_LARGE"
            return result
        doc = json.loads(payload)
        if not isinstance(doc, dict):
            raise ValueError("image metadata not an object")
        image_id = doc.get("Id")
        config = doc.get("Config")
        labels = config.get("Labels") if isinstance(config, dict) else None
        labels = labels if isinstance(labels, dict) else {}
        digests = doc.get("RepoDigests")
        result.update({
            "image_id": image_id if isinstance(image_id, str)
                         and IMAGE_ID.fullmatch(image_id) else None,
            "architecture": doc.get("Architecture"),
            "os": doc.get("Os"),
            "base_label": labels.get("qwen38.base"),
            "repo_digests": [v for v in digests[:16]
                             if isinstance(v, str) and len(v) <= 256]
                            if isinstance(digests, list) else [],
        })
        result["vllm032_label_matches"] = result["base_label"] == "v0.32"
        result["status"] = "METADATA_OBSERVED_UNQUALIFIED"
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError,
            UnicodeError, RuntimeError):
        result["status"] = "IMAGE_INSPECT_UNAVAILABLE"
    return result


def inspect_27b_runtime(*, cache_root: Path | None = None,
                        inspector=inspect_27b,
                        service_observer=inspect_service,
                        runner=subprocess.run,
                        machine=platform.machine) -> dict[str, Any]:
    """Gather source/host facts and precise unresolved gates; always fail closed."""
    issues: list[str] = []
    try:
        source = inspector(cache_root, expected_revision=REVISION)
    except (OSError, ValueError, RuntimeError) as exc:
        source = {"source_files_present": False, "configuration": None,
                  "issues": ["CHECKPOINT_INSPECTION_FAILED:" + type(exc).__name__],
                  "checkpoint_status": "UNKNOWN"}
    if not source.get("source_files_present") or source.get("local_revision") != REVISION:
        issues.append("PINNED_CHECKPOINT_NOT_CONFIRMED")
    issues.extend("CHECKPOINT:" + str(item) for item in source.get("issues", []))
    configuration = source.get("configuration") or {}
    metadata_matches = (
        configuration.get("status") == "PARSED_UNQUALIFIED"
        and configuration.get("architecture") == [EXPECTED_ARCHITECTURE]
        and configuration.get("model_type") == EXPECTED_MODEL_TYPE
        and configuration.get("quant_method") == EXPECTED_QUANT_METHOD
    )
    if not metadata_matches:
        issues.append("MODEL_ARCHITECTURE_OR_QUANT_METADATA_UNEXPECTED")
    if configuration.get("context_length") is None:
        issues.append("MODEL_CONTEXT_METADATA_NOT_CONFIRMED")
    try:
        host_arch = machine()
    except (OSError, ValueError):
        host_arch = None
    if host_arch not in ("aarch64", "arm64"):
        issues.append("HOST_NOT_CONFIRMED_ARM64")

    image = _image_facts(runner)
    if image["status"] != "METADATA_OBSERVED_UNQUALIFIED":
        issues.append(image["status"])
    else:
        if not image["image_id"]:
            issues.append("IMAGE_ID_INVALID")
        if image["architecture"] != "arm64" or image["os"] != "linux":
            issues.append("IMAGE_PLATFORM_MISMATCH")
        if not image["vllm032_label_matches"]:
            issues.append("IMAGE_VLLM032_LABEL_MISSING")

    try:
        service = service_observer()
    except (OSError, ValueError, RuntimeError) as exc:
        service = {"status": "BLOCKED", "observed_model": None,
                   "issues": ["SERVICE_INSPECTION_FAILED:" + type(exc).__name__]}
    if service.get("status") != "OBSERVED_UNQUALIFIED":
        issues.append("LIVE_SERVICE_UNVERIFIED")
    issues.extend("SERVICE:" + str(item) for item in service.get("issues", []))
    if service.get("download_running"):
        issues.append("DOWNLOAD_STILL_RUNNING")
    if service.get("observed_model") not in (None, "27b"):
        issues.append("ACTIVE_MODEL_REQUIRES_SEPARATE_TRANSITION_APPROVAL")

    # An image tag/ID, cached files and compatible-looking config NEVER prove
    # the loader, ModelOpt kernels, unified-memory fit or recovery plan.
    issues.extend((
        "VLLM032_27B_LOADER_NOT_QUALIFIED",
        "MODEL_OPT_MIXED_NVFP4_FP8_GPU_NOT_QUALIFIED",
        "IMAGE_DIGEST_NOT_PINNED_IN_VALIDATED_RECIPE",
        "GPU_MEMORY_AND_CONTEXT_PROFILE_UNVERIFIED",
        "27B_START_AND_FLASH_NEXT_ROLLBACK_NOT_VERIFIED",
    ))
    return {
        "schema_version": 1, "stage": "p2", "action": "runtime-preflight",
        "scope": "DGX_READ_ONLY_NO_GPU", "status": "BLOCKED",
        "runtime": "NOT_RUN", "executed": False,
        "operations_enabled": False, "approval_accepted": False,
        "plan_id": None, "gpu_verified": False, "runtime_qualified": False,
        "source_checkpoint_status": source.get("checkpoint_status"),
        "source_files_present": bool(source.get("source_files_present")),
        "revision": REVISION, "configuration": configuration,
        "expected": {
            "architecture": EXPECTED_ARCHITECTURE,
            "model_type": EXPECTED_MODEL_TYPE,
            "quant_method": EXPECTED_QUANT_METHOD,
            "service_model_id": "qwen3.8-27b", "host_port": 8000,
        },
        "metadata_matches_expected": metadata_matches,
        "host_architecture": host_arch, "image": image,
        "observed_service": {
            "status": service.get("status"),
            "observed_model": service.get("observed_model"),
            "download_running": service.get("download_running"),
            "api_port_8000_listening": service.get("api_port_8000_listening"),
        },
        "issues": sorted(set(issues)),
        "next_actions": [
            "Audit pinned local config, hf_quant_config and source vLLM 0.32 model registry",
            "Qualify immutable 27B image digest, loader, ARM64 NVFP4/FP8 and memory",
            "Prepare separately approved stop-before-start and verified Flash-Next recovery",
        ],
        "notice": "Read-only evidence only: never run 27B through Flash-Next's generic serve.sh.",
    }
