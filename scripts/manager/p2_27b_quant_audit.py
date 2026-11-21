"""Bounded inspection of *pinned local* NVIDIA 27B hf_quant_config.json.

Pure read-only; never loads tensors, invokes Docker or assumes GPU compatibility.
"""
from __future__ import annotations
from collections import Counter
import json
import os
from pathlib import Path
from typing import Any

from scripts.manager.p2_27b_download import REVISION
from scripts.manager.p2_27b_inventory import REPO_DIR

MAX_BYTES = 2 * 1024 * 1024
MAX_LAYERS = 20000
ALLOWED = frozenset(("NVFP4", "FP8", "MIXED_PRECISION", "FP8_PB_WO",
                     "FP8_PER_CHANNEL_PER_TOKEN", "W4A16_NVFP4"))


def inspect_pinned_quantization(cache_root: Path | None = None) -> dict[str, Any]:
    root = Path(cache_root or os.environ.get(
        "HF_CACHE", str(Path.home() / ".cache/huggingface"))).expanduser()
    path = root / "hub" / REPO_DIR / "snapshots" / REVISION / "hf_quant_config.json"
    result: dict[str, Any] = {
        "revision": REVISION, "status": "BLOCKED",
        "source_present": False, "quant_algo": None,
        "producer": None, "layer_count": 0, "layer_algorithms": {},
        "mixed_fp8_nvfp4_metadata": False,
        "runtime_qualified": False, "gpu_verified": False,
        "issues": [],
    }
    try:
        if not path.is_file():
            result["issues"].append("PINNED_HF_QUANT_CONFIG_MISSING")
            return result
        size = path.stat().st_size
        if not 0 < size <= MAX_BYTES:
            result["issues"].append("HF_QUANT_CONFIG_SIZE_INVALID")
            return result
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("root must be an object")
        quant = document.get("quantization")
        producer = document.get("producer")
        if not isinstance(quant, dict):
            raise ValueError("quantization missing")
        result["source_present"] = True
        result["producer"] = producer.get("name") if isinstance(producer, dict) else None
        result["quant_algo"] = quant.get("quant_algo")
        raw = quant.get("quantized_layers")
        if not isinstance(raw, dict) or not 1 <= len(raw) <= MAX_LAYERS:
            raise ValueError("invalid quantized_layers")
        counts: Counter[str] = Counter()
        for layer_name, item in raw.items():
            if (not isinstance(layer_name, str) or len(layer_name) > 256
                    or not isinstance(item, dict)):
                raise ValueError("invalid layer")
            algo = item.get("quant_algo")
            if not isinstance(algo, str) or algo not in ALLOWED:
                raise ValueError("unrecognized layer algorithm")
            counts[algo] += 1
        result["layer_count"] = len(raw)
        result["layer_algorithms"] = dict(sorted(counts.items()))
        if result["producer"] != "modelopt":
            result["issues"].append("MODEL_OPT_PRODUCER_UNCONFIRMED")
        if result["quant_algo"] != "MIXED_PRECISION":
            result["issues"].append("EXPECTED_MIXED_PRECISION_NOT_FOUND")
        if not {"NVFP4", "FP8"}.issubset(counts):
            result["issues"].append("NVFP4_AND_FP8_LAYER_MIX_NOT_FOUND")
        result["mixed_fp8_nvfp4_metadata"] = not result["issues"]
        result["status"] = ("PINNED_METADATA_PARSED_UNQUALIFIED"
                            if not result["issues"] else "BLOCKED")
    except (OSError, UnicodeError, ValueError, TypeError, RecursionError):
        result["issues"].append("HF_QUANT_CONFIG_INVALID")
    result["issues"] = sorted(set(result["issues"]))
    return result
