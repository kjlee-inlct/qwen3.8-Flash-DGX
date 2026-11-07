"""P3-E bounded *read-only* host asset evidence for the preserved Flash view.

This is neither a canonical recipe nor permission to launch. Docker inspect is
read-only and output is allowlisted: never print Env values, host paths, Docker
Config/HostConfig, tokenizer/template contents, or arbitrary inspect payloads.
Large safetensors shards are stat-checked, NOT hashed or integrity-qualified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
from typing import Any

from scripts.manager import flash_recipe_review as review

MAX_META_BYTES = 8 * 1024 * 1024
# Large modelopt/NVFP4 weight maps may be much larger than ordinary metadata.
# A separate 128 MiB hard ceiling bounds read/JSON allocation; do NOT use
# this limit for smaller config/tokenizer files or the mounted chat template.
MAX_INDEX_BYTES = 128 * 1024 * 1024
MAX_TEMPLATE_BYTES = 256 * 1024
MAX_INDEX_SHARDS = 256
MAX_INDEX_WEIGHTS = 100000
SHARD_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*\.safetensors$")


# Public diagnostic tokens are explicit allowlist entries: do not print the
# raw exception text, since filesystem/JSON errors may include private paths.
SAFE_ERROR_CODES = frozenset({
    "MISSING_MOUNT_INVENTORY", "REQUIRED_BIND_MOUNT_UNQUALIFIED",
    "HOST_MOUNT_SOURCE_UNQUALIFIED", "FILE_OUTSIDE_HF_CACHE",
    "FILE_NOT_REGULAR_OR_EMPTY", "FILE_EXCEEDS_BOUNDED_READ",
    "FILE_CHANGED_DURING_READ", "INVALID_DOCKER_DOC",
    "IMAGE_CONTAINER_OR_ENTRYPOINT_DRIFT", "COMMAND_UNVERIFIED",
    "REQUIRED_ENV_UNVERIFIED", "TEMPLATE_NOT_READ_ONLY",
    "HF_CACHE_NOT_A_DIRECTORY", "FLASH_VIEW_OUTSIDE_CACHE",
    "FLASH_SHARD_INDEX_UNQUALIFIED", "FLASH_SHARD_INDEX_PATH_UNQUALIFIED",
    "FLASH_WEIGHT_MAP_MISSING_OR_WRONG_TYPE", "FLASH_WEIGHT_MAP_EMPTY",
    "FLASH_WEIGHT_MAP_ENTRY_LIMIT_EXCEEDED",
    "INVALID_FLASH_COMMAND", "UNQUALIFIED_FLASH_CHECKPOINT",
    "DUPLICATE_FLASH_OPTION", "BOOLEAN_FLASH_OPTION_WITH_VALUE",
    "MISSING_FLASH_OPTION_VALUE", "EMPTY_FLASH_OPTION_VALUE",
    "INVALID_FLASH_JSON_OPTION", "INVALID_FLASH_SPLITTING_OPS",
    "INVALID_FLASH_SPECIAL_OPTION", "UNKNOWN_FLASH_OPTION_OR_POSITIONAL",
    "DUPLICATE_ENV_KEYS",
})


def _public_reason(exc: Exception) -> str:
    """Return only fixed diagnostic codes, never exception descriptions."""
    if isinstance(exc, json.JSONDecodeError):
        return "INVALID_JSON"
    if isinstance(exc, FileNotFoundError):
        return "FILE_NOT_FOUND"
    if isinstance(exc, PermissionError):
        return "PERMISSION_DENIED"
    if isinstance(exc, IsADirectoryError):
        return "IS_DIRECTORY"
    if type(exc) is ValueError and str(exc) in SAFE_ERROR_CODES:
        return str(exc)
    if isinstance(exc, OSError):
        return "IO_UNAVAILABLE"
    if isinstance(exc, (ValueError, TypeError, KeyError)):
        return "INVALID_DATA"
    return "INTERNAL_ERROR"


def _mounted(doc: dict, dest: str) -> dict:
    mounts = doc.get("Mounts")
    if not isinstance(mounts, list):
        raise ValueError("MISSING_MOUNT_INVENTORY")
    selected = [x for x in mounts if isinstance(x, dict)
                and x.get("Destination") == dest]
    if len(selected) != 1 or selected[0].get("Type") != "bind":
        raise ValueError("REQUIRED_BIND_MOUNT_UNQUALIFIED")
    source = selected[0].get("Source")
    if not isinstance(source, str) or not Path(source).is_absolute():
        raise ValueError("HOST_MOUNT_SOURCE_UNQUALIFIED")
    return selected[0]


def _regular(path: Path, *, root: Path | None = None,
             allow_empty: bool = False) -> tuple[Path, int]:
    resolved = path.resolve(strict=True)
    if root is not None and not resolved.is_relative_to(root):
        raise ValueError("FILE_OUTSIDE_HF_CACHE")
    size = resolved.stat()
    if not stat.S_ISREG(size.st_mode) or (size.st_size == 0 and not allow_empty):
        raise ValueError("FILE_NOT_REGULAR_OR_EMPTY")
    return resolved, size.st_size


def _small_digest(path: Path, *, limit: int, root: Path | None = None) -> tuple[str, bytes]:
    resolved, n = _regular(path, root=root)
    if n > limit:
        raise ValueError("FILE_EXCEEDS_BOUNDED_READ")
    # A second size check while reading enforces the cap even if the file
    # grows after stat; never use unbounded Path.read_bytes() on host files.
    with resolved.open("rb") as handle:
        payload = handle.read(limit + 1)
    if len(payload) > limit:
        raise ValueError("FILE_EXCEEDS_BOUNDED_READ")
    if len(payload) != n:
        raise ValueError("FILE_CHANGED_DURING_READ")
    return hashlib.sha256(payload).hexdigest(), payload


def inspect_assets(docker: dict, *, draft_loader=review.load_draft) -> dict[str, Any]:
    """Host cache/template provenance evidence; never promote installability."""
    result: dict[str, Any] = {
        "schema_version": 1,
        "action": "FLASH_HOST_ASSET_READ_ONLY_PREFLIGHT",
        "status": "BLOCKED",
        "issues": [],
        "verified_model_revision": False,
        "pinned_command_identity_matched": False,
        "prepared_view_path_observed": False,
        "failed_stage": None,
        "failure_reason_code": None,
        "metadata_sha256": {},
        "index_file_size_bytes_observed": None,
        "index_file_size_limit_bytes": MAX_INDEX_BYTES,
        # Counts and schema status only; never emit tensor names or mappings.
        "index_weight_map_entry_count_observed": None,
        "index_weight_map_entry_limit": MAX_INDEX_WEIGHTS,
        "index_weight_map_structure": "NOT_PARSED",
        "template_sha256": None,
        "indexed_shard_count": 0,
        "indexed_shard_bytes_observed": 0,
        "large_shard_hashes_verified": False,
        "full_docker_runtime_reinstall_qualified": False,
        "launch_allowed": False,
        "canonical_recipe_registered": False,
        "executed": False,
        "operations_enabled": False,
        "production_released": False,
    }
    stage = "LOAD_PINNED_DRAFT"
    try:
        recipe, draft_sha = draft_loader()
        result["draft_recipe_sha256"] = draft_sha
        stage = "CHECK_DOCKER_IDENTITY"
        if not isinstance(docker, dict):
            raise ValueError("INVALID_DOCKER_DOC")
        dc = recipe["docker"]
        if (docker.get("Name") != "/" + dc["container_name"]
                or docker.get("Image") != dc["image_id"]
                or (docker.get("Config") or {}).get("Entrypoint") != dc["entrypoint"]):
            raise ValueError("IMAGE_CONTAINER_OR_ENTRYPOINT_DRIFT")
        cmd = (docker.get("Config") or {}).get("Cmd")
        if not isinstance(cmd, list):
            raise ValueError("COMMAND_UNVERIFIED")
        stage = "NORMALIZE_PINNED_FLASH_COMMAND"
        review.normalize_fp8hybrid_cmd(cmd, draft_loader=draft_loader)
        result["pinned_command_identity_matched"] = True
        stage = "VALIDATE_REQUIRED_ENV"
        required_env = review._environment(docker)
        if any(required_env.get(k) != v for k, v in
               recipe["required_environment"].items()):
            raise ValueError("REQUIRED_ENV_UNVERIFIED")
        stage = "VALIDATE_HF_AND_TEMPLATE_BINDS"
        hf = _mounted(docker, "/hf")
        template = _mounted(docker, dc["required_ro_template_mount"])
        if template.get("RW") is not False:
            raise ValueError("TEMPLATE_NOT_READ_ONLY")
        stage = "RESOLVE_HOST_HF_CACHE"
        cache = Path(hf["Source"]).resolve(strict=True)
        if not cache.is_dir():
            raise ValueError("HF_CACHE_NOT_A_DIRECTORY")
        result["legacy_hf_bind_writable"] = hf.get("RW") is True
        # A pinned *command and directory name* do not cryptographically prove
        # that HF cache bytes equal the published NVIDIA source revision.
        rev = recipe["model"]["source_revision"]
        view = (cache / "hub" / "models--nvidia--Qwen3.8-Flash-Next-NVFP4"
                / "snapshots" / (rev + "-fp8hybrid"))
        stage = "RESOLVE_PREPARED_VIEW"
        view_root = view.resolve(strict=True)
        if not view_root.is_dir() or not view_root.is_relative_to(cache):
            raise ValueError("FLASH_VIEW_OUTSIDE_CACHE")
        stage = "CHECK_PREPARED_MARKER"
        _regular(view / ".prepared", root=cache, allow_empty=True)
        result["prepared_view_path_observed"] = True
        hashes: dict[str, str] = {}
        for name in ("config.json", "tokenizer_config.json",
                     "model.safetensors.index.json"):
            stage = {
                "config.json": "READ_MODEL_CONFIG",
                "tokenizer_config.json": "READ_TOKENIZER_CONFIG",
                "model.safetensors.index.json": "READ_SHARD_INDEX",
            }[name]
            if name == "model.safetensors.index.json":
                # Numeric size is nonsecret and useful if the dedicated limit
                # still blocks. Metadata digest and shard count remain unknown
                # until the bounded read and index parse both succeed.
                _, index_size = _regular(view / name, root=cache)
                result["index_file_size_bytes_observed"] = index_size
            digest, payload = _small_digest(
                view / name,
                limit=(MAX_INDEX_BYTES if name == "model.safetensors.index.json"
                       else MAX_META_BYTES),
                root=cache)
            hashes[name] = digest
            if name == "model.safetensors.index.json":
                stage = "PARSE_SHARD_INDEX"
                idx = json.loads(payload)
                weight_map = idx.get("weight_map") if isinstance(idx, dict) else None
                if not isinstance(weight_map, dict):
                    result["index_weight_map_structure"] = "MISSING_OR_WRONG_TYPE"
                    raise ValueError("FLASH_WEIGHT_MAP_MISSING_OR_WRONG_TYPE")
                result["index_weight_map_structure"] = "OBJECT"
                result["index_weight_map_entry_count_observed"] = len(weight_map)
                if not weight_map:
                    raise ValueError("FLASH_WEIGHT_MAP_EMPTY")
                if len(weight_map) > MAX_INDEX_WEIGHTS:
                    # Do not raise the entry-count policy merely because
                    # unknown data exceeded it: publish a safe numeric count
                    # for an explicit bounded policy review.
                    raise ValueError("FLASH_WEIGHT_MAP_ENTRY_LIMIT_EXCEEDED")
                shards = set(weight_map.values())
                if (not 0 < len(shards) <= MAX_INDEX_SHARDS
                        or any(not isinstance(s, str) or
                               not SHARD_NAME.fullmatch(s) for s in shards)):
                    raise ValueError("FLASH_SHARD_INDEX_PATH_UNQUALIFIED")
                total = 0
                stage = "CHECK_INDEXED_SHARDS"
                for shard in shards:
                    _, size = _regular(view / shard, root=cache)
                    total += size
                result["indexed_shard_count"] = len(shards)
                result["indexed_shard_bytes_observed"] = total
        # The full tokenizer may exceed metadata cap; existence/size only.
        stage = "CHECK_TOKENIZER_FILE"
        _regular(view / "tokenizer.json", root=cache)
        stage = "READ_MOUNTED_CHAT_TEMPLATE"
        template_hash, _ = _small_digest(Path(template["Source"]),
                                          limit=MAX_TEMPLATE_BYTES)
        result["metadata_sha256"] = hashes
        result["template_sha256"] = template_hash
        result["status"] = "LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED"
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        # Never emit source paths, raw exception text or operator env values.
        reason = _public_reason(exc)
        result["failed_stage"] = stage
        result["failure_reason_code"] = reason
        result["issues"] = ["FLASH_HOST_ASSET_PREFLIGHT:" + stage + ":" + reason]
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Flash host assets, strictly read-only")
    ap.add_argument("--json", action="store_true", help="Structured redacted JSON")
    args = ap.parse_args(argv)
    try:
        from scripts.manager.p2_27b_gpu_trial import docker_info
        result = inspect_assets(docker_info("qwen38-flash"))
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        result = {
            "schema_version": 1, "action": "FLASH_HOST_ASSET_READ_ONLY_PREFLIGHT",
            "status": "BLOCKED",
            "issues": ["DOCKER_READ_ONLY_INSPECT_UNAVAILABLE:" + type(exc).__name__],
            "launch_allowed": False, "executed": False,
            "production_released": False,
        }
    print(json.dumps(result, indent=2 if args.json else None, sort_keys=True))
    return 0 if not result.get("issues") else 3


if __name__ == "__main__":
    raise SystemExit(main())
