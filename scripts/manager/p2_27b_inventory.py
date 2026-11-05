"""P2 27B checkpoint discovery, read-only and deliberately NOT launch authorization.

The 27B candidate is not pinned or vLLM-0.32 qualified. The helper only
records which immutable-revision files are already in the local HF cache;
it never downloads, converts, serves or reads weight contents.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

MODEL_ID = "RadixArk/Qwen3.8-27B-NVFP4"
REPO_DIR = "models--RadixArk--Qwen3.8-27B-NVFP4"
SHA40 = re.compile(r"^[a-f0-9]{40}$")
MAX_INDEX = 64 * 1024 * 1024
MAX_ENTRIES = 500_000
MAX_SHARDS = 2048
ESSENTIAL = ("config.json", "tokenizer.json", "tokenizer_config.json",
             "generation_config.json", "chat_template.jinja",
             "model.safetensors.index.json")


def _file_info(path: Path) -> dict[str, Any]:
    """Resolve HF symlinks without disclosing resolved target paths."""
    try:
        if not path.is_file():
            return {"status": "MISSING_OR_DANGLING"}
        size = path.stat().st_size
        return {"status": "PRESENT" if size > 0 else "EMPTY",
                "size_bytes": size, "symlink": path.is_symlink()}
    except (OSError, RuntimeError):
        return {"status": "UNREADABLE"}


def _indexed_shards(snapshot: Path) -> tuple[list[str], list[str]]:
    index = snapshot / "model.safetensors.index.json"
    info = _file_info(index)
    if info["status"] != "PRESENT":
        return [], ["INDEX_ABSENT"]
    if info["size_bytes"] > MAX_INDEX:
        return [], ["INDEX_TOO_LARGE"]
    try:
        data = json.loads(index.read_text(encoding="utf-8"))
        weight_map = data.get("weight_map") if isinstance(data, dict) else None
        if (not isinstance(weight_map, dict) or not weight_map
                or len(weight_map) > MAX_ENTRIES):
            return [], ["INVALID_WEIGHT_MAP"]
        names = set(weight_map.values())
        if (not 1 <= len(names) <= MAX_SHARDS
                or any(not isinstance(n, str)
                       or not n.endswith(".safetensors")
                       or Path(n).name != n or n in (".", "..")
                       for n in names)):
            return [], ["INVALID_SHARD_NAMES"]
        return sorted(names), []
    except (OSError, UnicodeError, ValueError, TypeError):
        return [], ["INVALID_INDEX_JSON"]



def _configuration_facts(snapshot: Path) -> dict[str, Any]:
    """Bounded, read-only config facts. Never infer vLLM/GB10 compatibility."""
    path = snapshot / "config.json"
    info = _file_info(path)
    facts: dict[str, Any] = {
        "status": "NOT_INSPECTED", "architecture": [], "model_type": None,
        "quant_method": None, "context_length": None,
        "vision_config_present": False, "vllm032_qualified": False,
    }
    if info["status"] != "PRESENT":
        facts["status"] = info["status"]
        return facts
    if info["size_bytes"] > 1024 * 1024:
        facts["status"] = "CONFIG_TOO_LARGE"
        return facts
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("not an object")
        text = config.get("text_config")
        text = text if isinstance(text, dict) else {}
        architectures = config.get("architectures")
        if isinstance(architectures, list):
            facts["architecture"] = [
                item for item in architectures[:8]
                if isinstance(item, str) and 0 < len(item) <= 128
            ]
        model_type = config.get("model_type")
        if isinstance(model_type, str) and len(model_type) <= 128:
            facts["model_type"] = model_type
        quant = config.get("quantization_config")
        if not isinstance(quant, dict):
            quant = text.get("quantization_config")
        if isinstance(quant, dict):
            method = quant.get("quant_method")
            if isinstance(method, str) and len(method) <= 128:
                facts["quant_method"] = method
        context = text.get("max_position_embeddings",
                           config.get("max_position_embeddings"))
        if isinstance(context, int) and not isinstance(context, bool) and 0 < context <= 10_000_000:
            facts["context_length"] = context
        facts["vision_config_present"] = isinstance(
            config.get("vision_config"), dict
        )
        facts["status"] = "PARSED_UNQUALIFIED"
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
        facts["status"] = "INVALID_CONFIG_JSON"
    return facts


def inspect_27b(cache_root: Path | None = None) -> dict[str, Any]:
    cache = Path(cache_root or os.environ.get(
        "HF_CACHE", str(Path.home() / ".cache/huggingface"))).expanduser()
    repo = cache / "hub" / REPO_DIR
    refs: dict[str, str | None] = {}
    for name in ("main", "master"):
        try:
            v = (repo / "refs" / name).read_text(encoding="utf-8").strip()
            refs[name] = v if SHA40.fullmatch(v) else None
        except (OSError, UnicodeError):
            refs[name] = None
    revision = refs["main"] or refs["master"]
    snapshot = repo / "snapshots" / revision if revision else None
    metadata = {}
    configuration = None
    shards: dict[str, dict[str, Any]] = {}
    issues = []
    if snapshot is None or not snapshot.is_dir():
        issues.append("NO_PINNED_LOCAL_SNAPSHOT")
    else:
        configuration = _configuration_facts(snapshot)
        metadata = {n: _file_info(snapshot / n) for n in ESSENTIAL}
        for n, info in metadata.items():
            if info["status"] != "PRESENT":
                issues.append("MISSING_METADATA:" + n)
        indexed, parse_issues = _indexed_shards(snapshot)
        issues.extend(parse_issues)
        shards = {n: _file_info(snapshot / n) for n in indexed}
        for n, info in shards.items():
            if info["status"] != "PRESENT":
                issues.append("MISSING_SHARD:" + n)
        if not _file_info(snapshot / "hf_quant_config.json")["status"] == "PRESENT":
            try:
                cfg = json.loads((snapshot / "config.json").read_text())
                quant = cfg.get("quantization_config") or (
                    cfg.get("text_config") or {}).get("quantization_config")
                if not quant:
                    issues.append("QUANTIZATION_METADATA_NOT_FOUND")
            except (OSError, ValueError, AttributeError, TypeError):
                issues.append("CONFIG_INVALID_JSON")
    try:
        incomplete = sum(1 for _ in (repo / "blobs").glob("*.incomplete"))
    except OSError:
        incomplete = None
        issues.append("BLOB_LIST_UNAVAILABLE")
    if incomplete:
        issues.append("INCOMPLETE_TRANSFER_FILES_PRESENT")
    source_files_present = bool(snapshot is not None and snapshot.is_dir()
                                and not issues)
    return {
        "stage": "p2", "model_repo": MODEL_ID,
        "cache_root": str(cache.resolve()), "local_revision": revision,
        "refs": refs, "metadata": metadata,
        "configuration": configuration, "shards": shards,
        "indexed_shard_count": len(shards),
        "incomplete_blob_files": incomplete,
        "source_files_present": source_files_present,
        "issues": sorted(set(issues)),
        "checkpoint_status": ("SOURCE_FILES_PRESENT_UNPINNED"
                              if source_files_present else "NOT_READY"),
        "runtime": "NOT_RUN", "executed": False,
        "operations_enabled": False, "recipe_pinned": False,
        "image_verified": False, "gpu_verified": False,
        "notice": "Inspection is not a P2 launch/benchmark approval.",
    }
