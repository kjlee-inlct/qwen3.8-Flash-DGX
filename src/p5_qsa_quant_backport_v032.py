"""Scoped upstream vLLM #62318 Qwen4Exp QSA quantized-indexer backport.

Reference: https://github.com/vllm-project/vllm/pull/62318
Fixed upstream in fe833b1 (2026-10-27), after vLLM v0.32.0.

Apply ONLY to a separately built P5 Orcarouter recipe adapter image.
Never modify running/source Blazux images, host code or HF model snapshots.
"""

from __future__ import annotations

import argparse
import ast
from importlib.metadata import version
import json
import os
from pathlib import Path

VERSION = "0.32.0"
ADAPTER = "qwen4exp-qsa-62318-v032-v1"
MARKER = "# blazux-p5-qsa62318: scoped upstream fused QKV/indexer fix"
OLD_MAPPING = '"qkv_proj": ["q_proj", "k_proj", "v_proj", "indexer.index_qk_proj"],'
NEW_MAPPING = '"qkv_proj": ["q_proj", "k_proj", "v_proj"],'
OLD_FUSE = """        self.fuse_indexer_projection = vllm_config.lora_config is None
        if self.fuse_indexer_projection:
"""
NEW_FUSE = """        # blazux-p5-qsa62318: scoped upstream fused QKV/indexer fix
        # Based on vllm-project/vllm#62318. An unquantized indexer must
        # not share the QKV quantization scheme or GEMM.
        fused_quant_config = model.without_modelopt_fp4(quant_config)
        projection_method = type(self.qkv_proj.quant_method)
        self.fuse_indexer_projection = vllm_config.lora_config is None and (
            fused_quant_config is None
            or projection_method is type(self.indexer.index_qk_proj.quant_method)
        )
        if self.fuse_indexer_projection:
"""
OLD_QUANT_CALL = """                model.without_modelopt_fp4(quant_config),
            )
            del self.indexer.index_qk_proj"""
NEW_QUANT_CALL = """                fused_quant_config,
            )
            del self.indexer.index_qk_proj"""


# The canonical Blazux 0.32 image is NOT the unmodified vLLM 0.32 wheel.
# Its Dockerfile updates QSA with an independent, optional FP8 hybrid shim:
#   sed -i 's/self.fuse_indexer_projection = .../<hybrid guard>/' qsa.py
# and redirects qkv_proj quant_config to _fp8_hybrid_excluded(quant_config).
# The *fused wrapper* still calls model.without_modelopt_fp4(quant_config).
# Match the proven Blazux form exactly and retain BOTH the hybrid veto and
# the upstream PR #62318 quant-method equality check.
BLAZUX_FUSE = """        self.fuse_indexer_projection = (vllm_config.lora_config is None and not _fp8_hybrid_separate_qsa(quant_config, prefix))
        if self.fuse_indexer_projection:
"""
BLAZUX_NEW_FUSE = """        # blazux-p5-qsa62318: scoped upstream fused QKV/indexer fix
        # Retain Blazux's existing FP8-hybrid separation policy.
        fused_quant_config = _fp8_hybrid_excluded(quant_config)
        projection_method = type(self.qkv_proj.quant_method)
        self.fuse_indexer_projection = (
            vllm_config.lora_config is None
            and not _fp8_hybrid_separate_qsa(quant_config, prefix)
            and (
                fused_quant_config is None
                or projection_method is type(self.indexer.index_qk_proj.quant_method)
            )
        )
        if self.fuse_indexer_projection:
"""


def exact_once(source: str, needle: str, name: str) -> None:
    count = source.count(needle)
    if count != 1:
        raise ValueError(f"P5_QSA62318_{name}_ANCHOR_COUNT_{count}")


def _patched_pair(model_src: str, qsa_src: str) -> tuple[str, str]:
    """All-or-nothing bounded source transformation for *isolated image*."""
    if ((MARKER in qsa_src) or (NEW_MAPPING in model_src and OLD_MAPPING not in model_src)):
        if (MARKER in qsa_src and OLD_MAPPING not in model_src
            and NEW_MAPPING in model_src and "fused_quant_config," in qsa_src
            and OLD_FUSE not in qsa_src and BLAZUX_FUSE not in qsa_src
            and OLD_QUANT_CALL not in qsa_src):
            ast.parse(model_src)
            ast.parse(qsa_src)
            return model_src, qsa_src
        raise ValueError("P5_QSA62318_PARTIAL_PATCH_REFUSED")
    if not all(marker in model_src for marker in (
        "class Qwen4ExpForCausalLM(", "class Qwen4ExpForConditionalGeneration(",
        '"qkv_proj": Qwen4ExpForCausalLM.packed_modules_mapping["qkv_proj"]')):
        raise ValueError("P5_QSA62318_MODEL_ARCH_MISMATCH")
    if not all(marker in qsa_src for marker in (
        "class Qwen4ExpQSAAttention(", "self.indexer = QSAIndexer(")):
        raise ValueError("P5_QSA62318_QSA_ARCH_MISMATCH")
    exact_once(model_src, OLD_MAPPING, "MODEL_MAPPING")

    # Two *known* input ABIs only. Do not attempt a fuzzy replacement:
    # Blazux builds carry the hybrid veto, and the original upstream wheel
    # carries a plain LoRA-only guard. Unknown or mixed forms block the build.
    if "_fp8_hybrid_separate_qsa(quant_config, prefix)" in qsa_src:
        if ("quant_config=_fp8_hybrid_excluded(quant_config)" not in qsa_src
            or "from vllm_fp8_hybrid_modelopt import" not in qsa_src
            or OLD_FUSE in qsa_src):
            raise ValueError("P5_QSA62318_BLAZUX_HYBRID_ABI_INVALID")
        fuse, replacement = BLAZUX_FUSE, BLAZUX_NEW_FUSE
    else:
        if BLAZUX_FUSE in qsa_src or "_fp8_hybrid_excluded" in qsa_src:
            raise ValueError("P5_QSA62318_UNKNOWN_QSA_HYBRID_ABI")
        fuse, replacement = OLD_FUSE, NEW_FUSE
    exact_once(qsa_src, fuse, "QSA_FUSE_GUARD")
    exact_once(qsa_src, OLD_QUANT_CALL, "QSA_FUSED_QUANT_CALL")

    new_model = model_src.replace(OLD_MAPPING, NEW_MAPPING, 1)
    new_qsa = qsa_src.replace(fuse, replacement, 1)
    new_qsa = new_qsa.replace(OLD_QUANT_CALL, NEW_QUANT_CALL, 1)
    if (OLD_MAPPING in new_model or OLD_FUSE in new_qsa
        or BLAZUX_FUSE in new_qsa or OLD_QUANT_CALL in new_qsa):
        raise ValueError("P5_QSA62318_UNPATCHED_FUSED_PATH")
    ast.parse(new_model)
    ast.parse(new_qsa)
    return new_model, new_qsa


def inspect(site_packages: Path, *, apply: bool = False) -> dict:
    base = site_packages.resolve(strict=True)
    folder = base / "vllm/models/qwen4_exp/nvidia"
    files = {"model": folder / "model.py", "qsa": folder / "qsa.py"}
    if version("vllm") != VERSION or any(not p.is_file() or p.is_symlink() for p in files.values()):
        raise ValueError("P5_QSA62318_BASE_ABI_NOT_V032")
    originals = {name: p.read_text(encoding="utf-8") for name, p in files.items()}
    model, qsa = _patched_pair(originals["model"], originals["qsa"])
    candidates = {"model": model, "qsa": qsa}
    report = {"status": "PASS", "adapter": ADAPTER,
              "upstream": "vllm-project/vllm#62318",
              "vllm": VERSION, "source_patched": False,
              "gpu_verified": False, "changes": {
                  k: originals[k] != candidates[k] for k in files}}
    if apply:
        if os.environ.get("P5_EXPLICIT_QSA62318_IMAGE_BUILD") != "1":
            raise ValueError("P5_QSA62318_BUILD_OPT_IN_REQUIRED")
        if not all(report["changes"].values()) and any(report["changes"].values()):
            raise ValueError("P5_QSA62318_PARTIAL_TARGET_FILES")
        # No side-effects until all anchors and both ASTs checked.
        for key, path in files.items():
            path.write_text(candidates[key], encoding="utf-8")
        report["source_patched"] = True
        report["scope"] = "ISOLATED_DERIVED_IMAGE_ONLY"
    else:
        report["scope"] = "CPU_READ_ONLY_SOURCE_AUDIT"
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-packages", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        report = inspect(args.site_packages, apply=args.apply)
    except (OSError, ValueError, SyntaxError, KeyError) as exc:
        report = {"status": "BLOCKED", "issues": [str(exc)[:180]],
                  "source_patched": False, "gpu_verified": False}
    print(json.dumps(report, sort_keys=True, indent=2 if args.json else None))
    return 0 if report["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
