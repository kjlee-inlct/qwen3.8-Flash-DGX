"""P5-only vLLM 0.32.0 Orcarouter LM-head exact quantization target v3.

Isolated Orcarouter adapter only: no global vLLM patch, model/cache edit, or
changes to the canonical 27B/Flash images.
v2 passed quant_config but retained the nested prefix (language_model.lm_head),
which does not match the checkpoint's config target "lm_head". v3 passes
both quant_config and the exact checkpoint prefix "lm_head" to let
compressed-tensors register the output-head FP8 scale parameter.
Reference: YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark
src/patch_qwen4_exp_quantized_lm_head.py @ 9492b78c6bc04638587b42f2ffeb0680b0fcb3ef
"""
from __future__ import annotations

import argparse
import ast
from importlib.metadata import version
import json
import os
from pathlib import Path

VERSION = "0.32.0"
MARKER = "# blazux-p5-lmhead-v032-v3: checkpoint-target LM head registration"
OLD = (
    "        self.lm_head = ParallelLMHead(\n"
    "            config.vocab_size,\n"
    "            config.hidden_size,\n"
    '            prefix=maybe_prefix(prefix, "lm_head"),\n'
    "        )"
)
NEW = OLD.replace(
    '            prefix=maybe_prefix(prefix, "lm_head"),\n',
    f"            {MARKER}\n"
    "            quant_config=self.quant_config,\n"
    '            prefix="lm_head",\n',
)
HEAD_CLASS = "class Qwen4ExpForCausalLM("
HEAD_CONFIG = "self.quant_config = vllm_config.quant_config"
REQUIRED_METADATA = (
    "class ParallelLMHead(VocabParallelEmbedding):",
    "self.has_bias = bias",
    "self.output_partition_sizes = [self.output_size_per_partition]",
    "self.quant_config = quant_config",
)


def _once(source: str, value: str, code: str) -> None:
    observed = source.count(value)
    if observed != 1:
        raise ValueError(f"P5_LMHEAD_{code}_ANCHOR_COUNT_{observed}")


def patch_source(source: str, metadata_source: str) -> str:
    """Fail closed on unknown source ABIs, partial patches, or missing metadata."""
    ast.parse(source)
    ast.parse(metadata_source)
    _once(source, HEAD_CLASS, "MODEL_CLASS")
    _once(source, HEAD_CONFIG, "MODEL_QUANT_CONFIG")
    for anchor in REQUIRED_METADATA:
        _once(metadata_source, anchor, "PARALLEL_HEAD_METADATA")
    if MARKER in source:
        _once(source, MARKER, "PATCH_MARKER")
        _once(source, NEW, "PATCHED_HEAD")
        if OLD in source:
            raise ValueError("P5_LMHEAD_PARTIAL_PATCH")
        return source
    if "quant_config=self.quant_config," in source and OLD not in source:
        raise ValueError("P5_LMHEAD_UNMARKED_PREEXISTING_PATCH")
    _once(source, OLD, "UNQUANTIZED_HEAD")
    result = source.replace(OLD, NEW, 1)
    ast.parse(result)
    return result


def inspect(site_packages: Path, *, apply: bool = False) -> dict:
    if version("vllm") != VERSION:
        raise ValueError("P5_LMHEAD_VLLM_VERSION_MISMATCH")
    root = site_packages.resolve(strict=True)
    model = root / "vllm/models/qwen4_exp/nvidia/model.py"
    metadata = root / "vllm/model_executor/layers/vocab_parallel_embedding.py"
    if any(not p.is_file() or p.is_symlink() for p in (model, metadata)):
        raise ValueError("P5_LMHEAD_SOURCE_PATH_UNVERIFIED")
    original = model.read_text(encoding="utf-8")
    transformed = patch_source(
        original, metadata.read_text(encoding="utf-8")
    )
    report = {
        "status": "PASS", "vllm": VERSION,
        "scope": "ISOLATED_P5_IMAGE_ONLY",
        "executed": False, "gpu_verified": False,
        "source_changed": original != transformed,
        "parallel_lm_head_metadata": "VLLM_032_NATIVE_PRESENT",
    }
    if apply:
        if os.environ.get("P5_EXPLICIT_LMHEAD_IMAGE_BUILD") != "1":
            raise ValueError("P5_LMHEAD_ISOLATED_IMAGE_BUILD_NOT_APPROVED")
        if original != transformed:
            model.write_text(transformed, encoding="utf-8")
        report["executed"] = True
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-packages", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = inspect(args.site_packages, apply=args.apply)
    except (OSError, ValueError, SyntaxError) as exc:
        result = {"status": "BLOCKED", "issues": [str(exc)[:180]],
                  "executed": False, "gpu_verified": False}
    print(json.dumps(result, sort_keys=True, indent=2 if args.json else None))
    return 0 if result["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
