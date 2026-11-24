"""P2-FINAL Native Tools V1: variant-aware, read-only service identity audit.

This independent observer is intentionally NOT wired into the existing
ordinary Wizard service manager or runtime service-policy. It cannot switch,
stop, start, remove or rename a Docker container. It checks live identity
ONLY, not tool-call inference or deployment approval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any, Callable
from urllib.request import Request, urlopen

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager.operational_switch import historical_p3_receipts
from scripts.manager.p2_27b_launch_preview import IMAGE_RE, REVISION, SERVED
from scripts.manager.p2_27b_tool_variant import (
    FALLBACK_CONTAINER, SOURCE_CONTAINER, TOOL_CHAT_TEMPLATE,
    VARIANT_CONTAINER, VARIANT_ID, FULL_SHA, _gpu_access, _image_and_id,
    _protected_mount, _run_names,
)
from scripts.manager.p2_27b_tool_template_audit import EXPECTED_TEMPLATE_SHA256

API = "http://127.0.0.1:8000/v1/models"
SNAPSHOT = "/snapshots/" + REVISION


def _read_local_model_ids(*, opener: Callable[..., Any] = urlopen) -> list[str]:
    """Bounded localhost GET /v1/models; does not invoke GPU inference."""
    with opener(Request(API, method="GET"), timeout=10) as response:
        if response.status != 200:
            raise ValueError("LOCAL_MODEL_API_HTTP_NOT_200")
        payload = response.read(65537)
    if not payload or len(payload) > 65536:
        raise ValueError("LOCAL_MODEL_API_TOO_LARGE_OR_EMPTY")
    data = json.loads(payload)
    entries = data.get("data") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise ValueError("LOCAL_MODEL_API_NOT_A_NONEMPTY_LIST")
    ids = [entry.get("id") for entry in entries if isinstance(entry, dict)]
    if len(ids) != len(entries) or not all(isinstance(v, str) for v in ids):
        raise ValueError("LOCAL_MODEL_IDS_INVALID")
    return ids


def _template_digest_from_mount(mount: Path) -> str:
    """Read a pinned HF snapshot symlink inside the original read-only cache."""
    cache = mount.expanduser().resolve(strict=True)
    template = cache / TOOL_CHAT_TEMPLATE.removeprefix("/hf/")
    resolved = template.resolve(strict=True)
    if not resolved.is_relative_to(cache) or not resolved.is_file():
        raise ValueError("PINNED_TEMPLATE_OUTSIDE_PROTECTED_CACHE")
    if resolved.stat().st_size > 100000 or resolved.stat().st_size < 1000:
        raise ValueError("PINNED_TEMPLATE_SIZE_UNEXPECTED")
    return hashlib.sha256(resolved.read_bytes()).hexdigest()


def _required_arg(cmd: list[str], name: str, value: str) -> bool:
    return cmd.count(name) == 1 and (
        cmd.index(name) + 1 < len(cmd)
        and cmd[cmd.index(name) + 1] == value
    )


def inspect_variant_status(
    *, run: Callable[..., Any] = gpu.call,
    inspect: Callable[..., dict] = gpu.docker_info,
    lineage: Callable[[], dict] = historical_p3_receipts,
    model_ids: Callable[[], list[str]] = _read_local_model_ids,
    template_digest: Callable[[Path], str] = _template_digest_from_mount,
) -> dict[str, Any]:
    """Audit BOTH original and isolated variant without changing live state.

    Variant existence is not native Tool Calling PASS. The old service manager
    still expects the original qwen38-27b, so this standalone audit must not
    be connected to the main switch executor before policy/journal migration.
    """
    result: dict[str, Any] = {
        "schema_version": 1,
        "action": "P2_FINAL_VARIANT_AWARE_RUNTIME_IDENTITY_READ_ONLY",
        "status": "BLOCKED",
        "issues": [],
        "source_container": SOURCE_CONTAINER,
        "variant_container": VARIANT_CONTAINER,
        "variant_id": VARIANT_ID,
        "fallback_container": FALLBACK_CONTAINER,
        "api_port": 8000,
        "api_model_id": SERVED,
        "expected_template_sha256": EXPECTED_TEMPLATE_SHA256,
        "read_only": True,
        "executed": False,
        "variant_runtime_identity_verified": False,
        "native_tool_calling_qualified": False,
        "production_executor_enabled": False,
        "approval_accepted": False,
        "plan_id": None,
    }
    issues: list[str] = result["issues"]
    try:
        names = _run_names(run, all_containers=True)
        running = _run_names(run, all_containers=False)
        if SOURCE_CONTAINER not in names or FALLBACK_CONTAINER not in names:
            issues.append("PROTECTED_ORIGINAL_OR_FLASH_MISSING")
            return result
        source = inspect(SOURCE_CONTAINER)
        fallback = inspect(FALLBACK_CONTAINER)
        if not _image_and_id(source) or not _image_and_id(fallback):
            issues.append("PROTECTED_CONTAINER_IMAGE_OR_ID_INVALID")
            return result
        # Original P3 receipts are immutable lineage proof, NOT authorization.
        hist = lineage()
        a = (hist.get("records") or {}).get("a") or {}
        if hist.get("status") != "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED" or hist.get("issues"):
            issues.append("HISTORICAL_P3_LINEAGE_UNVERIFIED")
        if (source["Id"], source["Image"]) != (
            a.get("id_27b"), a.get("image_27b")
        ):
            issues.append("PROTECTED_ORIGINAL_P3_IDENTITY_DRIFT")
        if (fallback["Id"], fallback["Image"]) != (
            a.get("flash_id"), a.get("flash_image")
        ):
            issues.append("PROTECTED_FLASH_P3_IDENTITY_DRIFT")
        source_up = source.get("State", {}).get("Running") is True
        fallback_up = fallback.get("State", {}).get("Running") is True
        variant_exists = VARIANT_CONTAINER in names
        variant_up = VARIANT_CONTAINER in running
        if source_up != (SOURCE_CONTAINER in running):
            issues.append("SOURCE_DOCKER_STATE_INVENTORY_DRIFT")
        if fallback_up != (FALLBACK_CONTAINER in running):
            issues.append("FLASH_DOCKER_STATE_INVENTORY_DRIFT")
        if fallback_up:
            issues.append("FLASH_FALLBACK_NOT_STOPPED")
        old_cmd = (source.get("Config") or {}).get("Cmd")
        if (not isinstance(old_cmd, list)
                or not any(isinstance(x, str) and SNAPSHOT in x for x in old_cmd)
                or not _required_arg(old_cmd, "--served-model-name", SERVED)
                or not _required_arg(old_cmd, "--quantization", "modelopt_mixed")
                or any(f in old_cmd for f in (
                    "--enable-auto-tool-choice", "--tool-call-parser",
                    "--reasoning-parser", "--chat-template",
                ))):
            issues.append("ORIGINAL_IMMUTABLE_CMD_DRIFT")
        old_mount = _protected_mount(source)
        if old_mount is None:
            issues.append("PROTECTED_ORIGINAL_READ_ONLY_HF_MOUNT_MISSING")
        # Inspect every running container to reject foreign GPU owners.
        gpu_owners: list[str] = []
        docs: dict[str, dict] = {
            SOURCE_CONTAINER: source, FALLBACK_CONTAINER: fallback,
        }
        for name in running:
            doc = docs.get(name)
            if doc is None:
                doc = inspect(name)
                docs[name] = doc
            if not isinstance(doc, dict):
                raise ValueError("DOCKER_RUNNING_INSPECT_NON_OBJECT")
            if _gpu_access(doc):
                gpu_owners.append(name)
        if len(gpu_owners) != 1:
            issues.append("ONE_ACTIVE_GPU_CONTAINER_NOT_VERIFIED")
        if variant_exists and variant_up:
            variant = docs.get(VARIANT_CONTAINER) or inspect(VARIANT_CONTAINER)
            if not _image_and_id(variant) or not variant.get("State", {}).get("Running"):
                issues.append("VARIANT_RUNNING_IDENTITY_UNVERIFIED")
            else:
                flags = (variant.get("Config") or {}).get("Cmd")
                labels = (variant.get("Config") or {}).get("Labels") or {}
                binding = ((variant.get("HostConfig") or {})
                           .get("PortBindings") or {}).get("8000/tcp")
                if variant["Image"] != source["Image"]:
                    issues.append("VARIANT_IMAGE_NOT_ORIGINAL_PINNED_IMAGE")
                if (labels.get("blazux.variant") != VARIANT_ID
                        or labels.get("blazux.preserved-original") != SOURCE_CONTAINER):
                    issues.append("VARIANT_PROVENANCE_LABEL_MISMATCH")
                if (not isinstance(flags, list)
                        or not any(isinstance(x, str) and SNAPSHOT in x for x in flags)
                        or flags.count("--enable-auto-tool-choice") != 1
                        or not all(_required_arg(flags, k, v) for k, v in (
                            ("--tool-call-parser", "qwen3_coder"),
                            ("--reasoning-parser", "qwen3"),
                            ("--chat-template", TOOL_CHAT_TEMPLATE),
                            ("--quantization", "modelopt_mixed"),
                            ("--served-model-name", SERVED),
                        ))):
                    issues.append("VARIANT_NATIVE_TOOLS_FLAGS_OR_CHECKPOINT_MISMATCH")
                if (not isinstance(binding, list) or len(binding) != 1
                        or binding[0].get("HostPort") != "8000"):
                    issues.append("VARIANT_HOST_PORT_8000_UNVERIFIED")
                if _protected_mount(variant) != old_mount or old_mount is None:
                    issues.append("VARIANT_READ_ONLY_CACHE_MOUNT_MISMATCH")
            if source_up:
                issues.append("ORIGINAL_AND_VARIANT_RUNNING_TOGETHER")
            if gpu_owners != [VARIANT_CONTAINER]:
                issues.append("VARIANT_NOT_THE_SOLE_GPU_MODEL")
            if old_mount is not None:
                if template_digest(old_mount) != EXPECTED_TEMPLATE_SHA256:
                    issues.append("PINNED_TEMPLATE_DIGEST_MISMATCH")
            if not issues:
                if model_ids() != [SERVED]:
                    issues.append("VARIANT_LOCAL_API_MODEL_ID_MISMATCH")
            if not issues:
                result["status"] = "VARIANT_RUNTIME_IDENTITY_VERIFIED_ONLY"
                result["variant_runtime_identity_verified"] = True
        elif source_up and not variant_exists:
            if gpu_owners != [SOURCE_CONTAINER]:
                issues.append("ORIGINAL_NOT_THE_SOLE_GPU_MODEL")
            if not issues:
                result["status"] = "PROTECTED_ORIGINAL_27B_ACTIVE"
        else:
            issues.append("VARIANT_NOT_RUNNING_OR_INTERRUPTED_STATE")
    except (OSError, ValueError, RuntimeError, TypeError, KeyError,
            AttributeError, subprocess.TimeoutExpired, json.JSONDecodeError):
        issues.append("VARIANT_AUDIT_READ_ONLY_INSPECTION_FAILED")
    if issues:
        result["status"] = "BLOCKED"
    result["issues"] = sorted(set(issues))
    result["notice"] = (
        "Identity observation only. No Docker/GPU mutation or inferred approval. "
        "Native tool calls, Open WebUI and independent rollback qualification "
        "remain unverified; ordinary Wizard still uses original service-policy."
    )
    return result


def main() -> int:
    print(json.dumps(inspect_variant_status(), sort_keys=True, indent=2))
    # Only a live, independently inspected variant identity may exit 0;
    # that code NEVER signals native tools or deployment acceptance.
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
