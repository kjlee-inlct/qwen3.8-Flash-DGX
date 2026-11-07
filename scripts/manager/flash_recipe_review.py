"""P3-E Flash-Next FP8-hybrid recipe *draft* review; no install/release.

The preserved original Flash container has a separate large-context/Yarn/MTP
runtime distinct from the canonical NVIDIA 27B. This read-only comparator
records whether the known observed fields still match the versioned draft,
but deliberately CANNOT qualify a new Flash installation or authorize Docker.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / "recipes/qwen38-flash-next.runtime.draft.json"
FULL_SHA = re.compile(r"^sha256:[0-9a-f]{64}$")
SOURCE_REV = "fc694b54fb0174e0913e6adf86691ef85a4ead47"
MODEL_REPO = "nvidia/Qwen3.8-Flash-Next-NVFP4"
SOURCE_PREFIX = "/hf/hub/models--nvidia--Qwen3.8-Flash-Next-NVFP4/snapshots/"


def load_draft(*, file: Path = DRAFT) -> tuple[dict, str]:
    """Trust repo-pinned source state, not the currently observed Docker argv."""
    if file.is_symlink() or not file.is_file():
        raise ValueError("FLASH_DRAFT_NOT_FOUND_OR_SYMLINK")
    raw = file.read_bytes()
    if len(raw) > 16384:
        raise ValueError("FLASH_DRAFT_TOO_LARGE")
    recipe = json.loads(raw)
    if (not isinstance(recipe, dict)
            or recipe.get("schema_version") != 1
            or recipe.get("recipe_id") != "qwen38-flash-next-fp8hybrid-source-draft-v1"
            or recipe.get("status") != "SOURCE_DRAFT_NOT_RUNTIME_QUALIFIED"
            or recipe.get("engine") != "vllm"
            or recipe.get("vllm_version") != "0.32.0"
            or recipe.get("launch_allowed") is not False
            or recipe.get("register_as_runtime_recipe") is not False
            or recipe.get("model", {}).get("repo_id") != MODEL_REPO
            or recipe.get("model", {}).get("source_revision") != SOURCE_REV
            or recipe.get("model", {}).get("checkpoint_view_suffix") != "-fp8hybrid"
            or recipe.get("model", {}).get("served_id") != "qwen3.8-flash-next"
            or recipe.get("docker", {}).get("container_name") != "qwen38-flash"
            or recipe.get("docker", {}).get("host_port") != 8000
            or recipe.get("docker", {}).get("internal_port") != 8000
            or recipe.get("docker", {}).get("gpu_request") != "all"
            or recipe.get("docker", {}).get("entrypoint") != ["vllm", "serve"]
            or recipe.get("docker", {}).get("image_id") is None
            or not FULL_SHA.fullmatch(str(recipe["docker"]["image_id"]))
            or recipe.get("docker", {}).get("hf_mount", {}).get("destination") != "/hf"
            or recipe.get("docker", {}).get("hf_mount", {}).get("type") != "bind"
            or recipe.get("docker", {}).get("required_ro_template_mount") !=
                    "/qwen38/chat_template.jinja"
            or recipe.get("required_environment", {}).get("HF_HOME") != "/hf"
            or recipe.get("required_environment", {}).get("HF_HUB_OFFLINE") != "1"
            or recipe.get("required_environment", {}).get("VLLM_FP8_HYBRID") != "1"
            or recipe.get("preserve_assets") is not True
            or not recipe.get("release_blockers")):
        raise ValueError("FLASH_SOURCE_DRAFT_POLICY_INVALID")
    return recipe, hashlib.sha256(raw).hexdigest()


def _flag(argv: list[str], flag: str) -> str | None:
    """Strictly one value of --flag <value> or --flag=<value>."""
    values: list[str] = []
    for i, token in enumerate(argv):
        if token == flag:
            if i + 1 >= len(argv) or argv[i + 1].startswith("--"):
                return None
            values.append(argv[i + 1])
        elif token.startswith(flag + "="):
            values.append(token[len(flag) + 1:])
    return values[0] if len(values) == 1 else None


def _environment(doc: dict) -> dict[str, str]:
    found: dict[str, str] = {}
    duplicates: set[str] = set()
    for line in (doc.get("Config") or {}).get("Env") or []:
        if isinstance(line, str) and "=" in line:
            key, value = line.split("=", 1)
            if key in found:
                duplicates.add(key)
            found[key] = value
    if duplicates:
        raise ValueError("DUPLICATE_ENV_KEYS")
    return found


def _mounts(doc: dict) -> list[dict]:
    mounts = doc.get("Mounts")
    if not isinstance(mounts, list):
        raise ValueError("FLASH_DOCKER_MOUNTS_MISSING")
    return [m for m in mounts if isinstance(m, dict)]


def compare_observation(observed: dict, docker: dict, *,
                        draft_loader=load_draft) -> dict:
    """Compare only pinned, documented runtime fields, never auto-promote."""
    try:
        recipe, sha = draft_loader()
        issues: list[str] = []
        def check(ok: bool, code: str) -> None:
            if not ok:
                issues.append(code)
        cfg = docker.get("Config") or {}
        host = docker.get("HostConfig") or {}
        cmd = cfg.get("Cmd")
        if (not isinstance(cmd, list) or len(cmd) > 256
                or not cmd or not all(isinstance(s, str) for s in cmd)):
            raise ValueError("FLASH_DOCKER_CMD_INVALID")
        dr = recipe["docker"]
        check(docker.get("Image") == dr["image_id"], "IMAGE_DIGEST_CHANGED")
        check(cfg.get("Entrypoint") == dr["entrypoint"], "ENTRYPOINT_CHANGED")
        check(docker.get("Name") == "/" + dr["container_name"], "CONTAINER_NAME_CHANGED")
        check(observed.get("source_revision") == recipe["model"]["source_revision"],
              "NVIDIA_SOURCE_REVISION_CHANGED")
        check(observed.get("checkpoint_variant") == "LOCAL_PREPARED_FP8HYBRID",
              "FLASH_VIEW_NOT_FP8HYBRID")
        check(observed.get("hybrid_preparation_verified") is True,
              "FP8_HYBRID_PREPARATION_NOT_VERIFIED")
        view = (SOURCE_PREFIX + recipe["model"]["source_revision"]
                + recipe["model"]["checkpoint_view_suffix"])
        check(cmd[0] == view, "CHECKPOINT_VIEW_NOT_MATCHED")
        check(observed.get("checkpoint_observed_in_cmd") == view,
              "OBSERVED_CHECKPOINT_VIEW_DRIFT")
        check(observed.get("served_id_observed_in_cmd") ==
              recipe["model"]["served_id"], "SERVED_MODEL_ID_CHANGED")
        for key, value in recipe["observed_vllm"]["value_flags"].items():
            check(_flag(cmd, key) == value,
                  "REQUIRED_VLLM_VALUE_FLAG_CHANGED:" + key)
        for flag in recipe["observed_vllm"]["boolean_flags"]:
            check(cmd.count(flag) == 1, "REQUIRED_VLLM_BOOL_FLAG_CHANGED:" + flag)
        for prefix in recipe["observed_vllm"]["prefix_flags"]:
            check(sum(token.startswith(prefix) for token in cmd) == 1,
                  "REQUIRED_SPECIAL_VLLM_FLAG_CHANGED:" + prefix)
        for key, value in recipe["observed_vllm"]["json_flags"].items():
            raw = _flag(cmd, key)
            try:
                json_value = json.loads(raw) if raw is not None else None
            except (ValueError, TypeError):
                json_value = None
            check(json_value == value, "REQUIRED_VLLM_JSON_FLAG_CHANGED:" + key)
        mounts = _mounts(docker)
        hf = [m for m in mounts if m.get("Destination") == "/hf"]
        template = [m for m in mounts
                    if m.get("Destination") == dr["required_ro_template_mount"]]
        check(len(hf) == 1 and hf[0].get("Type") == "bind"
              and hf[0].get("Destination") == "/hf", "HF_BIND_MOUNT_UNVERIFIED")
        # The draft explicitly describes the HISTORICAL writable HF mount.
        # It is a review risk, not permission for a new writable deployment.
        if len(hf) == 1:
            check(hf[0].get("RW") is (not dr["hf_mount"]["read_only"]),
                  "HF_MOUNT_LEGACY_ACCESS_MODE_CHANGED")
            check(isinstance(hf[0].get("Source"), str)
                  and hf[0]["Source"].startswith("/"),
                  "HF_MOUNT_SOURCE_NOT_ABSOLUTE")
        check(len(template) == 1 and template[0].get("Type") == "bind"
              and template[0].get("RW") is False,
              "EFFORT_ALIAS_TEMPLATE_READ_ONLY_MOUNT_UNVERIFIED")
        check(host.get("IpcMode") == dr["ipc_mode"], "IPC_MODE_CHANGED")
        check(host.get("ShmSize") == dr["shm_size_bytes"], "SHARED_MEMORY_CHANGED")
        reqs = host.get("DeviceRequests") or []
        gpu_all = any(isinstance(q, dict) and q.get("Count") == -1
                      and any(isinstance(g, list) and "gpu" in g
                              for g in q.get("Capabilities") or [])
                      for q in reqs)
        check(gpu_all and observed.get("gpu") == "all", "GPU_REQUEST_CHANGED")
        bindings = (host.get("PortBindings") or {}).get("8000/tcp")
        check(isinstance(bindings, list) and bool(bindings)
              and all(isinstance(v, dict) and v.get("HostPort") == "8000"
                      for v in bindings), "HOST_PORT_BINDING_CHANGED")
        try:
            environment = _environment(docker)
        except ValueError:
            environment = {}
            issues.append("ENVIRONMENT_DUPLICATED_OR_UNTRUSTED")
        for k, value in recipe["required_environment"].items():
            check(environment.get(k) == value, "REQUIRED_ENV_CHANGED:" + k)
        return {
            "schema_version": 1,
            "action": "FLASH_RECIPE_DRAFT_FIELD_REVIEW",
            "status": ("MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED"
                       if not issues else "DRAFT_FIELD_MISMATCH_REVIEW_REQUIRED"),
            "issues": sorted(set(issues)),
            "draft_recipe_sha256": sha,
            "draft_recipe_id": recipe["recipe_id"],
            "checked_documented_fields_only": True,
            "host_specific_extra_env_and_mounts_qualified": False,
            "complete_docker_runtime_reinstall_qualified": False,
            "launch_allowed": False, "executed": False, "production_released": False,
            "notice": "Source draft only; exact documented fields are not a launch or reinstall qualification.",
        }
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        return {
            "schema_version": 1, "action": "FLASH_RECIPE_DRAFT_FIELD_REVIEW",
            "status": "DRAFT_REVIEW_UNAVAILABLE",
            "issues": ["DRAFT_REVIEW_UNAVAILABLE:" + type(exc).__name__],
            "launch_allowed": False, "executed": False,
            "production_released": False,
        }
