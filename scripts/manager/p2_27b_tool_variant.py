"""P2-FINAL opt-in NVIDIA 27B native-tools V1: read-only protected variant preview.

NO execution/approval code here. Never replace the original qwen38-27b or
replay P3. A successful preview is not parser qualification or downtime consent.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager.p2_27b_launch_preview import (
    IMAGE_RE, MODEL, PROFILE, REVISION, SERVED, TOOL_CALLING_ARGS,
    TARGET_CONTAINER, _candidate_argv,
)
from scripts.manager.service_status import inspect_live_status

VARIANT_ID = "nvidia-27b-native-tools-v1"
VARIANT_CONTAINER = "qwen38-27b-native-tools-v1"
SOURCE_CONTAINER = TARGET_CONTAINER
FALLBACK_CONTAINER = "qwen38-flash"
SNAPSHOT = "/snapshots/" + REVISION
FULL_SHA = re.compile(r"^[0-9a-f]{64}$")


def variant_command(cache: Path, image_id: str) -> list[str]:
    """Return inert argv, with a DIFFERENT container identity from original P2."""
    if not IMAGE_RE.fullmatch(image_id):
        raise ValueError("INVALID_PINNED_VLLM_IMAGE_ID")
    command = _candidate_argv(Path(cache), image_id, tool_calling=True)
    name_at = command.index("--name") + 1
    if command[name_at] != SOURCE_CONTAINER:
        raise ValueError("ORIGINAL_RECIPE_IDENTITY_DRIFT")
    command[name_at] = VARIANT_CONTAINER
    image_at = command.index(image_id)
    command[image_at:image_at] = [
        "--label", "blazux.variant=" + VARIANT_ID,
        "--label", "blazux.preserved-original=" + SOURCE_CONTAINER,
    ]
    if (command[command.index("--name") + 1] == SOURCE_CONTAINER
            or command[-len(TOOL_CALLING_ARGS):] != list(TOOL_CALLING_ARGS)):
        raise ValueError("NATIVE_TOOLS_VARIANT_IDENTITY_OR_FLAGS_CHANGED")
    return command


def _image_and_id(doc: dict) -> bool:
    return (
        isinstance(doc.get("Id"), str)
        and FULL_SHA.fullmatch(doc["Id"]) is not None
        and isinstance(doc.get("Image"), str)
        and IMAGE_RE.fullmatch(doc["Image"]) is not None
        and (doc.get("HostConfig") or {}).get("AutoRemove") is False
    )


def _gpu_access(doc: dict) -> bool:
    host = doc.get("HostConfig") or {}
    if host.get("DeviceRequests"):
        return True
    env = (doc.get("Config") or {}).get("Env") or []
    visible = next(
        (s.split("=", 1)[1] for s in env if isinstance(s, str)
         and s.startswith("NVIDIA_VISIBLE_DEVICES=")), "",
    )
    return host.get("Runtime") == "nvidia" and visible not in ("none", "void")


def _run_names(run: Callable[..., Any], *, all_containers: bool) -> list[str]:
    args = ["docker", "ps"]
    if all_containers:
        args.append("-a")
    args += ["--format", "{{.Names}}"]
    result = run(args)
    if result.returncode:
        raise RuntimeError("DOCKER_PS_FAILED")
    names = result.stdout.splitlines()
    if any(not n or n.strip() != n for n in names) or len(names) != len(set(names)):
        raise ValueError("UNVERIFIED_DOCKER_NAME_INVENTORY")
    return names


def _protected_mount(doc: dict) -> Path | None:
    mounts = [
        m for m in (doc.get("Mounts") or [])
        if isinstance(m, dict) and m.get("Destination") == "/hf"
        and m.get("RW") is False and m.get("Type") == "bind"
    ]
    if len(mounts) != 1:
        return None
    source = mounts[0].get("Source")
    if not isinstance(source, str) or not source.startswith("/") or ":" in source:
        return None
    return Path(source)


def inspect_variant(
    *,
    live: Callable[..., dict] = inspect_live_status,
    inspect: Callable[..., dict] = gpu.docker_info,
    run: Callable[..., Any] = gpu.call,
    now: float | None = None,
) -> dict[str, Any]:
    """Read-only Docker/API evidence; ALWAYS non-executable.

    Even if local static checks pass, parser registry, tokenizer compatibility,
    rollback-injection and real WebUI acceptance remain unqualified.
    """
    issues: list[str] = []
    source_doc: dict = {}
    fallback_doc: dict = {}
    mount: Path | None = None
    candidate: list[str] | None = None
    try:
        status = live()
        if (
            status.get("status") != "LIVE_SERVICE_VERIFIED"
            or status.get("issues")
            or status.get("observed_model") != "27b"
            or status.get("expected_served_id") != SERVED
            or status.get("observed_model_ids") != [SERVED]
            or status.get("host_port") != 8000
            or (status.get("active_container") or {}).get("name") != SOURCE_CONTAINER
        ):
            issues.append("PRESERVED_27B_LIVE_IDENTITY_NOT_VERIFIED")
        all_names = _run_names(run, all_containers=True)
        running_names = _run_names(run, all_containers=False)
        if VARIANT_CONTAINER in all_names:
            issues.append("VARIANT_CONTAINER_NAME_OCCUPIED")
        if SOURCE_CONTAINER not in running_names:
            issues.append("PRESERVED_27B_NOT_RUNNING")
        if FALLBACK_CONTAINER not in all_names:
            issues.append("FLASH_FALLBACK_CONTAINER_MISSING")

        if SOURCE_CONTAINER in all_names:
            source_doc = inspect(SOURCE_CONTAINER)
        else:
            issues.append("PRESERVED_27B_CONTAINER_MISSING")
        if FALLBACK_CONTAINER in all_names:
            fallback_doc = inspect(FALLBACK_CONTAINER)
        if not _image_and_id(source_doc):
            issues.append("PRESERVED_27B_ID_IMAGE_AUTOREMOVE_UNVERIFIED")
        else:
            host = source_doc.get("HostConfig") or {}
            mapping = (host.get("PortBindings") or {}).get("8000/tcp")
            if (
                not (source_doc.get("State") or {}).get("Running")
                or not isinstance(mapping, list) or len(mapping) != 1
                or mapping[0].get("HostPort") != "8000"
            ):
                issues.append("PRESERVED_27B_RUNNING_PORT_MISMATCH")
            cmd = (source_doc.get("Config") or {}).get("Cmd") or []
            if (
                not isinstance(cmd, list)
                or not any(SNAPSHOT in x for x in cmd if isinstance(x, str))
                or not ("--served-model-name" in cmd and SERVED in cmd)
            ):
                issues.append("ORIGINAL_PINNED_CHECKPOINT_OR_SERVED_ID_MISMATCH")
            if any(flag in cmd for flag in ("--enable-auto-tool-choice",
                                           "--tool-call-parser", "--reasoning-parser")):
                issues.append("PRESERVED_ORIGINAL_CMD_ALREADY_CHANGED")
            if (status.get("active_container") or {}).get("image_id") != source_doc["Image"]:
                issues.append("LIVE_STATUS_DOCKER_IMAGE_ID_MISMATCH")
            if not ("--quantization" in cmd and "modelopt_mixed" in cmd):
                issues.append("PINNED_MODEL_OPT_MIXED_LOADER_MISMATCH")
            mount = _protected_mount(source_doc)
            if mount is None:
                issues.append("ORIGINAL_READ_ONLY_HF_BIND_NOT_VERIFIED")
        if not _image_and_id(fallback_doc):
            issues.append("FLASH_FALLBACK_ID_IMAGE_AUTOREMOVE_UNVERIFIED")
        elif (fallback_doc.get("State") or {}).get("Running"):
            issues.append("FLASH_FALLBACK_MUST_BE_STOPPED")

        for name in running_names:
            doc = source_doc if name == SOURCE_CONTAINER else inspect(name)
            if not isinstance(doc, dict):
                issues.append("RUNNING_CONTAINER_INSPECTION_UNVERIFIED")
                continue
            if name != SOURCE_CONTAINER and _gpu_access(doc):
                issues.append("OTHER_GPU_CONTAINER_RUNNING")
        if not _gpu_access(source_doc):
            issues.append("SOURCE_GPU_REQUEST_NOT_VERIFIED")
        if not issues and mount is not None:
            candidate = variant_command(mount, source_doc["Image"])
    except (OSError, ValueError, RuntimeError, TypeError, KeyError,
            subprocess.TimeoutExpired):
        issues.append("READ_ONLY_INSPECTION_UNAVAILABLE")

    checks_passed = not issues
    evidence = {
        "kind": "P2_FINAL_27B_NATIVE_TOOLS_V1_PREVIEW_ONLY",
        "variant": VARIANT_ID,
        "source_id": source_doc.get("Id"),
        "source_image": source_doc.get("Image"),
        "fallback_id": fallback_doc.get("Id"),
        "fallback_image": fallback_doc.get("Image"),
        "revision": REVISION,
        "port": 8000,
        "time_window": int(time.time() if now is None else now) // 600,
    }
    fingerprint = (
        hashlib.sha256(json.dumps(evidence, sort_keys=True).encode()).hexdigest()
        if checks_passed else None
    )
    return {
        "schema_version": 1, "action": "P2_FINAL_27B_TOOL_VARIANT_READ_ONLY",
        "status": "BLOCKED_PENDING_PARSER_AND_LIVE_ACCEPTANCE"
                  if checks_passed else "BLOCKED",
        "issues": sorted(set(issues)),
        "read_only_preflight_pass": checks_passed,
        "execution_enabled": False, "executed": False,
        "approval_accepted": False, "plan_id": None,
        "preview_fingerprint_not_approval": fingerprint,
        "variant_id": VARIANT_ID, "variant_container": VARIANT_CONTAINER,
        "preserved_original_container": SOURCE_CONTAINER,
        "preserved_flash_container": FALLBACK_CONTAINER,
        "model_repo": MODEL, "pinned_revision": REVISION,
        "api_model_id": SERVED, "host_port": 8000,
        "vllm_version_policy": "0.32",
        "tool_calling_args": list(TOOL_CALLING_ARGS),
        "launch_profile": dict(PROFILE),
        "candidate_command_NOT_EXECUTABLE": candidate,
        "outstanding_gates": [
            "verify_exact_vllm032_image_parser_registry_qwen3_coder_and_qwen3",
            "verify_pinned_nvidia_tokenizer_chat_template_tool_and_reasoning_compatibility",
            "qualify_isolated_variant_start_stop_original_rollback_with_fault_injection",
            "integrate_variant_into_service_manifest_and_journal_before_any_execute",
            "independent_fresh_operator_downtime_approval_and_TTY",
            "DGX_structured_auto_tool_result_streaming_reasoning_and_nontool_chat",
            "Open_WebUI_Native_end_to_end_acceptance",
        ],
        "notice": (
            "Source-only candidate. NEVER run command preview or stop/start Docker. "
            "Original 27B/Flash containers, images, caches and P2/P3 receipts remain "
            "untouched. No executable migration exists and no old P3 stage is replayed."
        ),
    }


def main() -> int:
    print(json.dumps(inspect_variant(), indent=2, sort_keys=True))
    return 3  # REVIEW ONLY, never conveys an executable authorization


if __name__ == "__main__":
    raise SystemExit(main())
