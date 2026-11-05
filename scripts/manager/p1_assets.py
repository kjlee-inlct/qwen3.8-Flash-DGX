#!/usr/bin/env python3
"""Read-only, fail-closed NVIDIA Flash-Next checkpoint and image audit.

Never creates or changes a HF cache file. A refs/main revision alone is not proof
that the download finished. All indexed safetensors shards must resolve to
nonempty files, without escaping the checkpoint repository.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
from typing import Any, Callable

MODEL_ID = "nvidia/Qwen3.8-Flash-Next-NVFP4"
IMAGE = "qwen38-flash-dgx:v0.32"
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
ESSENTIAL = (
    "config.json", "generation_config.json", "tokenizer.json",
    "tokenizer_config.json", "chat_template.jinja",
    "preprocessor_config.json", "model.safetensors.index.json",
)


def _inside(path: Path, root: Path) -> bool:
    try:
        return path.resolve(strict=True).is_relative_to(root.resolve(strict=True))
    except (OSError, RuntimeError):
        return False


# Blazux's default Flash-Next launcher tests whether these metadata files
# exist; its legitimate HF snapshots may symlink tokenizer/index metadata into
# a shared location outside the model repository. These two *read-only*
# metadata names must not be rejected solely for that link layout.
# Shard data remains confined to the pinned model repository.
SHARED_METADATA = frozenset(("tokenizer.json", "model.safetensors.index.json"))


def _good_file(path: Path, root: Path) -> bool:
    try:
        if not path.is_file() or path.stat().st_size <= 0:
            return False
        if _inside(path, root):
            return True
        return (path.name in SHARED_METADATA and path.is_symlink()
                and path.resolve(strict=True).is_file())
    except (OSError, RuntimeError):
        return False


def _indexed_files(snapshot: Path, root: Path) -> list[str]:
    index = snapshot / "model.safetensors.index.json"
    # NVIDIA publishes a ~31.3 MB index. The old 16 MiB gate rejected valid metadata.
    # Retain a 64 MiB upper bound to avoid unbounded JSON parsing.
    if not _good_file(index, root) or index.stat().st_size > 64 * 1024 * 1024:
        raise ValueError("index_missing_or_oversize")
    try:
        data = json.loads(index.read_text(encoding="utf-8"))
    except (UnicodeError, OSError, ValueError) as exc:
        raise ValueError("index_invalid_json") from exc
    mapping = data.get("weight_map") if isinstance(data, dict) else None
    if not isinstance(mapping, dict) or not mapping or len(mapping) > 500000:
        raise ValueError("index_invalid_weight_map")
    try:
        shards = set(mapping.values())
    except TypeError as exc:
        raise ValueError("index_unhashable_shard_name") from exc
    if not 1 <= len(shards) <= 2048:
        raise ValueError("index_invalid_shard_count")
    if any(not isinstance(x, str) or not x.endswith(".safetensors")
           or Path(x).name != x or x in (".", "..") for x in shards):
        raise ValueError("index_invalid_shard_name")
    return sorted(shards)


def _audit_files(snapshot: Path, root: Path) -> list[str]:
    missing = [name for name in ESSENTIAL
               if not _good_file(snapshot / name, root)]
    if not missing:
        try:
            shards = _indexed_files(snapshot, root)
            missing += [name for name in shards
                        if not _good_file(snapshot / name, root)]
        except ValueError as exc:
            missing.append(str(exc))
        try:
            config = json.loads((snapshot / "config.json").read_text(encoding="utf-8"))
            q = config.get("quantization_config") or (
                config.get("text_config") or {}).get("quantization_config")
            if not _good_file(snapshot / "hf_quant_config.json", root) and not q:
                missing.append("quantization_config_missing")
        except (OSError, ValueError, TypeError, AttributeError):
            missing.append("config_invalid_json")
    return sorted(set(missing))


def audit_checkpoint(cache_root: Path) -> dict[str, Any]:
    cache = Path(cache_root).expanduser()
    repo = cache / "hub/models--nvidia--Qwen3.8-Flash-Next-NVFP4"
    rev_file = repo / "refs/main"
    revision = None
    problems: list[str] = []
    try:
        if rev_file.is_file():
            content = rev_file.read_text(encoding="utf-8").strip()
            if SHA40.fullmatch(content):
                revision = content
            else:
                problems.append("refs/main_invalid_revision")
        else:
            problems.append("refs/main_missing")
    except (OSError, UnicodeError):
        problems.append("refs/main_unreadable")
    source = repo / "snapshots" / revision if revision else None
    if source is None or not source.is_dir():
        problems.append("source_snapshot_missing")
    elif not _inside(source, repo):
        problems.append("source_snapshot_escapes_cache")
    else:
        problems.extend(_audit_files(source, repo))
    source_ready = source is not None and source.is_dir() and not problems
    # HF transfer temp files can outlive an interrupted download. Do not claim
    # readiness when transient shard downloads are still present in this repo.
    try:
        if repo.is_dir() and any(repo.glob("blobs/*.incomplete")):
            problems.append("blob_incomplete_present")
    except OSError:
        problems.append("blob_directory_unreadable")
    source_ready = source_ready and not problems

    hybrid = repo / "snapshots" / (revision + "-fp8hybrid") if revision else None
    hybrid_problems: list[str] = []
    if hybrid is None or not hybrid.is_dir():
        hybrid_problems.append("hybrid_snapshot_missing")
    elif not _inside(hybrid, repo):
        hybrid_problems.append("hybrid_snapshot_escapes_cache")
    elif not _good_file(hybrid / ".prepared", repo):
        # The upstream marker can be an empty file; existence is sufficient.
        if not (hybrid / ".prepared").is_file():
            hybrid_problems.append("hybrid_not_marked_prepared")
    if source_ready and hybrid is not None and hybrid.is_dir():
        hybrid_problems.extend(_audit_files(hybrid, repo))
    return {
        "model_repo": MODEL_ID, "revision": revision,
        "cache_root": str(cache.resolve()), "source_complete": source_ready,
        "hybrid_ready": bool(source_ready and not hybrid_problems),
        "source_issues": sorted(set(problems)),
        "hybrid_issues": sorted(set(hybrid_problems)),
        "state": ("READY" if source_ready and not hybrid_problems
                  else "SOURCE_COMPLETE" if source_ready else "INCOMPLETE"),
    }


def inspect_image(run: Callable[..., Any] = subprocess.run,
                  image: str = IMAGE) -> dict[str, Any]:
    """Reads only Docker image ID + qwen38.base label, never environment/secrets."""
    args = ["docker", "image", "inspect", "--format",
            '{{.Id}}|{{index .Config.Labels "qwen38.base"}}', image]
    try:
        result = run(args, capture_output=True, text=True, timeout=10, check=False)
        if result.returncode:
            return {"id": None, "vllm_base": None, "ready": False}
        image_id, base = result.stdout.strip().split("|", 1)
        good = bool(SHA256.fullmatch(image_id) and base == "v0.32")
        return {"id": image_id if SHA256.fullmatch(image_id) else None,
                "vllm_base": base, "ready": good}
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return {"id": None, "vllm_base": None, "ready": False}
