"""P5 read-only pinned Orcarouter LM-head quantization checkpoint preflight.

Reads only config, sharded index, and small safetensors JSON headers.  Never
imports CUDA, loads weight payloads, edits HF cache, or starts Docker.
A metadata PASS does NOT prove vLLM parameter registration or GPU readiness.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import struct

MAX_CONFIG = 2 * 1024 * 1024
MAX_INDEX = 128 * 1024 * 1024
MAX_HEADER = 64 * 1024 * 1024
MAX_KEYS = 500_000
NAME = "lm_head"


def _bounded_json(path: Path, limit: int, cache: Path) -> dict:
    resolved = path.resolve(strict=True)
    if not resolved.is_relative_to(cache) or not resolved.is_file():
        raise ValueError("P5_LMHEAD_SNAPSHOT_PATH_OUTSIDE_CACHE")
    if resolved.stat().st_size > limit:
        raise ValueError("P5_LMHEAD_METADATA_SIZE_EXCEEDED")
    obj = json.loads(resolved.read_bytes())
    if not isinstance(obj, dict):
        raise ValueError("P5_LMHEAD_METADATA_NOT_OBJECT")
    return obj


def _tensor_metadata(shard: Path, key: str, cache: Path) -> dict:
    resolved = shard.resolve(strict=True)
    if not resolved.is_relative_to(cache) or not resolved.is_file():
        raise ValueError("P5_LMHEAD_SHARD_PATH_OUTSIDE_CACHE")
    with resolved.open("rb") as f:
        size = resolved.stat().st_size
        first = f.read(8)
        if len(first) != 8:
            raise ValueError("P5_LMHEAD_INVALID_SAFETENSORS_HEADER")
        length = struct.unpack("<Q", first)[0]
        if length == 0 or length > MAX_HEADER or length + 8 > size:
            raise ValueError("P5_LMHEAD_UNBOUNDED_SAFETENSORS_HEADER")
        header = json.loads(f.read(length))
    if not isinstance(header, dict) or key not in header:
        raise ValueError("P5_LMHEAD_INDEX_HEADER_MISMATCH")
    value = header[key]
    if not isinstance(value, dict):
        raise ValueError("P5_LMHEAD_INVALID_TENSOR_METADATA")
    shape, dtype, offsets = (value.get("shape"), value.get("dtype"),
                             value.get("data_offsets"))
    if (not isinstance(shape, list) or
        any(type(n) is not int or n < 0 for n in shape) or
        not isinstance(dtype, str) or
        not isinstance(offsets, list) or len(offsets) != 2 or
        any(type(n) is not int or n < 0 for n in offsets) or
        offsets[0] > offsets[1] or offsets[1] > size - 8 - length):
        raise ValueError("P5_LMHEAD_INVALID_TENSOR_METADATA")
    return {"shape": shape, "dtype": dtype, "shard": shard.name}


def _matches(pattern: str, name: str) -> bool:
    if len(pattern) > 512:
        raise ValueError("P5_LMHEAD_UNBOUNDED_CONFIG_TARGET")
    if pattern.startswith("re:"):
        try:
            return re.search(pattern[3:], name) is not None
        except re.error as exc:
            raise ValueError("P5_LMHEAD_INVALID_QUANT_REGEX") from exc
    return pattern == name


def _target_groups(groups: dict) -> list[str]:
    matched = []
    if not groups:
        raise ValueError("P5_LMHEAD_QUANT_CONFIG_GROUPS_MISSING")
    for name, group in groups.items():
        if not isinstance(name, str) or not isinstance(group, dict):
            raise ValueError("P5_LMHEAD_QUANT_CONFIG_GROUP_INVALID")
        targets = group.get("targets")
        if not isinstance(targets, list) or not all(
            isinstance(x, str) for x in targets
        ):
            raise ValueError("P5_LMHEAD_QUANT_TARGETS_INVALID")
        # In vLLM 0.32 ParallelLMHead is *not* LinearBase.  A generic
        # 'Linear' target alone therefore does not establish a head scheme.
        if any(_matches(target, NAME) or target == "ParallelLMHead"
               for target in targets):
            weights = group.get("weights")
            if not isinstance(weights, dict) or weights.get("type") != "float" or (
                weights.get("num_bits") != 8
            ):
                raise ValueError("P5_LMHEAD_TARGET_NOT_FP8")
            matched.append(name)
    return matched


def inspect(snapshot: Path, cache_root: Path) -> dict:
    """Fail closed on unverifiable pinned metadata; never assert GPU success."""
    report = {
        "status": "BLOCKED", "issues": [],
        "checkpoint_metadata_verified": False,
        "weight_registration_verified": False,
        "gpu_verified": False, "executed": False,
        "scope": "LOCAL_PINNED_SNAPSHOT_READ_ONLY",
        "lm_head": {},
    }
    try:
        cache = cache_root.resolve(strict=True)
        snap = snapshot.resolve(strict=True)
        if not cache.is_dir() or not snapshot.is_dir() or snapshot.is_symlink() or (
            not snap.is_relative_to(cache)
        ):
            raise ValueError("P5_LMHEAD_PINNED_SNAPSHOT_UNVERIFIED")
        cfg = _bounded_json(snapshot / "config.json", MAX_CONFIG, cache)
        q = cfg.get("quantization_config")
        if not isinstance(q, dict) or q.get("quant_method") != "compressed-tensors":
            raise ValueError("P5_LMHEAD_COMPRESSED_TENSORS_CONFIG_MISSING")
        groups = q.get("config_groups")
        if not isinstance(groups, dict):
            raise ValueError("P5_LMHEAD_QUANT_CONFIG_GROUPS_MISSING")
        ignore = q.get("ignore", [])
        if not isinstance(ignore, list) or not all(isinstance(x, str) for x in ignore):
            raise ValueError("P5_LMHEAD_IGNORE_CONFIG_INVALID")
        ignored = [x for x in ignore if _matches(x, NAME)]
        matched = _target_groups(groups)
        index = _bounded_json(
            snapshot / "model.safetensors.index.json", MAX_INDEX, cache
        )
        weight_map = index.get("weight_map")
        if (not isinstance(weight_map, dict) or
            not 0 < len(weight_map) <= MAX_KEYS):
            raise ValueError("P5_LMHEAD_WEIGHT_MAP_INVALID")
        keys = {}
        for suffix in ("weight", "weight_scale"):
            found = [k for k in weight_map if k == f"{NAME}.{suffix}"]
            if len(found) != 1:
                raise ValueError("P5_LMHEAD_" + suffix.upper() + "_INDEX_MISSING")
            keys[suffix] = found[0]
        head = {}
        for suffix, key in keys.items():
            shard_name = weight_map[key]
            if (not isinstance(shard_name, str) or
                not re.fullmatch(r"[A-Za-z0-9_.-]+\.safetensors", shard_name)):
                raise ValueError("P5_LMHEAD_SHARD_FILENAME_UNVERIFIED")
            head[suffix] = _tensor_metadata(
                snapshot / shard_name, key, cache
            )
        report["lm_head"] = {
            "ignored_by_quant_config": bool(ignored),
            "matched_quant_groups": matched,
            "weight": head["weight"],
            "weight_scale": head["weight_scale"],
        }
        if ignored:
            raise ValueError("P5_LMHEAD_SCALE_PRESENT_BUT_HEAD_IGNORED")
        if len(matched) != 1:
            raise ValueError("P5_LMHEAD_FP8_QUANT_TARGET_UNVERIFIED")
        if not head["weight"]["dtype"].startswith("F8_"):
            raise ValueError("P5_LMHEAD_WEIGHT_NOT_FP8")
        if not head["weight_scale"]["shape"]:
            raise ValueError("P5_LMHEAD_SCALE_SHAPE_UNVERIFIED")
        report["status"] = "PASS"
        report["checkpoint_metadata_verified"] = True
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        report["issues"] = [str(exc)[:180] or type(exc).__name__]
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--snapshot", type=Path)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.snapshot is None or args.cache_root is None:
        from scripts.manager.p5_live_trial import CACHE, SNAPSHOT
        cache = args.cache_root or CACHE
        snapshot = args.snapshot or SNAPSHOT
    else:
        cache, snapshot = args.cache_root, args.snapshot
    result = inspect(snapshot, cache)
    print(json.dumps(result, sort_keys=True, indent=2 if args.json else None))
    return 0 if result["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
