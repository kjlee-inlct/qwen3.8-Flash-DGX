"""Blazux P5: isolated, opt-in Qwen4Exp vLLM 0.32 source patch candidate.

Only patch a separately approved Docker build. Not a runtime qualification.
NVIDIA/27B remain unchanged with VLLM_P5_ORCAROUTER unset.
"""
from __future__ import annotations

import argparse
import ast
from importlib.metadata import version
import json
import os
from pathlib import Path
import re

VLLM = "0.32.0"
FLAG = "VLLM_P5_ORCAROUTER"
HEAD_MARKER = "# blazux-p5-v032: optional quantized lm_head"
IGNORE_MARKER = "# blazux-p5-v032: compressed-tensors ignore remap"
GUARD_MARKER = "# blazux-p5-v032: exact native BF16 MTP names"
MTP_NAMES = (
    "mtp.fc_embedding.weight",
    "mtp.fc_hidden.weight",
    "mtp.hyper_connection_mixer.hc_norm.weight",
    "mtp.hyper_connection_mixer.input_mix_weight_down.weight",
    "mtp.hyper_connection_mixer.input_mix_weight_up.weight",
    "mtp.layers.0.attn_hyper_connection.block_inject_weight.weight",
    "mtp.layers.0.attn_hyper_connection.hc_norm.weight",
    "mtp.layers.0.attn_hyper_connection.input_mix_weight_down.weight",
    "mtp.layers.0.attn_hyper_connection.input_mix_weight_up.weight",
    "mtp.layers.0.mlp.experts.down_proj",
    "mtp.layers.0.mlp.experts.gate_up_proj",
    "mtp.layers.0.mlp.gate.weight",
    "mtp.layers.0.mlp.shared_expert.down_proj.weight",
    "mtp.layers.0.mlp.shared_expert.gate_proj.weight",
    "mtp.layers.0.mlp.shared_expert.up_proj.weight",
    "mtp.layers.0.mlp.shared_expert_gate.weight",
    "mtp.layers.0.mlp_hyper_connection.block_inject_weight.weight",
    "mtp.layers.0.mlp_hyper_connection.hc_norm.weight",
    "mtp.layers.0.mlp_hyper_connection.input_mix_weight_down.weight",
    "mtp.layers.0.mlp_hyper_connection.input_mix_weight_up.weight",
    "mtp.layers.0.self_attn.indexer.index_qk_proj.weight",
    "mtp.layers.0.self_attn.indexer.k_layernorm.weight",
    "mtp.layers.0.self_attn.indexer.q_layernorm.weight",
    "mtp.layers.0.self_attn.k_norm.weight",
    "mtp.layers.0.self_attn.k_proj.weight",
    "mtp.layers.0.self_attn.o_proj.weight",
    "mtp.layers.0.self_attn.q_norm.weight",
    "mtp.layers.0.self_attn.q_proj.weight",
    "mtp.layers.0.self_attn.v_proj.weight",
    "mtp.pre_fc_norm_embedding.weight",
    "mtp.pre_fc_norm_hidden.weight",
)
HEAD_ANCHOR = re.compile(
    r'^(?P<indent>[ ]+)prefix=maybe_prefix\(prefix, "lm_head"\),$', re.MULTILINE
)


def once(source: str, fragment: str, label: str) -> None:
    count = source.count(fragment)
    if count != 1:
        raise ValueError(f"{label}: expected one vLLM0.32 anchor, got {count}")


def os_import(source: str) -> str:
    if "import os as _blazux_p5_os\n" in source:
        return source
    once(source, "import torch\n", "torch import")
    return source.replace("import torch\n", "import os as _blazux_p5_os\nimport torch\n", 1)


def patch_head(source: str, kind: str) -> str:
    if kind not in ("model", "mtp"):
        raise ValueError("unknown Qwen4Exp target")
    if HEAD_MARKER in source:
        return source
    cls = "class Qwen4ExpForCausalLM(" if kind == "model" else "class Qwen4ExpMTP("
    if cls not in source:
        raise ValueError("unexpected model architecture")
    matches = list(HEAD_ANCHOR.finditer(source))
    if len(matches) != 1:
        raise ValueError(f"quantized head anchor count {len(matches)}")
    found = matches[0]
    pad = found.group("indent")
    add = (f"{pad}{HEAD_MARKER}\n{pad}quant_config=(self.quant_config if "
           f'_blazux_p5_os.environ.get("{FLAG}", "0") == "1" else None),\n')
    patched = os_import(source[:found.start()] + add + source[found.start():])
    ast.parse(patched)
    return patched


def patch_mtp(source: str) -> str:
    if all(marker in source for marker in (HEAD_MARKER, IGNORE_MARKER, GUARD_MARKER)):
        return source
    source = patch_head(source, "mtp")
    if IGNORE_MARKER in source or GUARD_MARKER in source:
        raise ValueError("partial P5 MTP patch refused")
    anchor = "        configure_quant_config(draft_quant_config, Qwen4ExpMTP)\n"
    once(source, anchor, "MTP draft quant config")
    ignore = """        # blazux-p5-v032: compressed-tensors ignore remap
        if _blazux_p5_os.environ.get("VLLM_P5_ORCAROUTER", "0") == "1":
            _p5_ignore = getattr(draft_quant_config, "ignore", None)
            if _p5_ignore:
                if not isinstance(_p5_ignore, list) or not all(
                    isinstance(item, str) for item in _p5_ignore
                ):
                    raise RuntimeError("invalid compressed-tensors ignore list")
                draft_quant_config.ignore = _remap_ignored_layers(
                    _p5_ignore, mtp_start_layer_idx
                )
"""
    source = source.replace(anchor, anchor + ignore, 1)
    klass = "class Qwen4ExpMTP(nn.Module, SupportsHCSP, SupportsPP, Qwen4ExpMixtureOfExperts):"
    once(source, klass, "MTP class")
    prefix, body = source.split(klass, 1)
    start = "    def load_weights(self, weights: Iterable[tuple[str, torch.Tensor]]) -> set[str]:\n"
    once(body, start, "MTP load_weights")
    original = """        def remap_weight_names():
            for name, weight in weights:
                remapped_name = _remap_mtp_weight_name(name)
"""
    once(body, original, "MTP generator")
    replaced = """        _p5_seen: dict[str, torch.dtype] = {}

        def remap_weight_names():
            for name, weight in weights:
                if _blazux_p5_os.environ.get("VLLM_P5_ORCAROUTER", "0") == "1":
                    _p5_name = name
                    for _p5_prefix in ("model.language_model.", "language_model."):
                        if _p5_name.startswith(_p5_prefix):
                            _p5_name = _p5_name[len(_p5_prefix):]
                            break
                    if _p5_name.startswith("model.mtp."):
                        _p5_name = _p5_name[len("model."):]
                    if _p5_name.startswith("mtp."):
                        if _p5_name in _p5_seen:
                            raise RuntimeError("duplicate native MTP tensor")
                        _p5_seen[_p5_name] = weight.dtype
                remapped_name = _remap_mtp_weight_name(name)
"""
    body = body.replace(original, replaced, 1)
    ending = "        return loader.load_weights(remap_weight_names(), mapper=mapper)"
    once(body, ending, "MTP loader return")
    guard = """        _p5_loaded = loader.load_weights(remap_weight_names(), mapper=mapper)
        if _blazux_p5_os.environ.get("VLLM_P5_ORCAROUTER", "0") == "1":
            _p5_found = set(_p5_seen)
            if _p5_found != _BLZ_P5_MTP_NAMES:
                raise RuntimeError(
                    "native BF16 MTP tensor mismatch: "
                    f"missing={len(_BLZ_P5_MTP_NAMES - _p5_found)} "
                    f"extra={len(_p5_found - _BLZ_P5_MTP_NAMES)}"
                )
            if any(dtype != torch.bfloat16 for dtype in _p5_seen.values()):
                raise RuntimeError("native MTP tensors must all be BF16")
        return _p5_loaded"""
    body = body.replace(ending, guard, 1)
    prefix += (f"{GUARD_MARKER}\n"
               f"_BLZ_P5_MTP_NAMES = frozenset({MTP_NAMES!r})\n\n\n")
    patched = prefix + klass + body
    ast.parse(patched)
    return patched


def inspect(site_packages: Path, apply: bool = False) -> dict:
    root = site_packages.resolve(strict=True)
    folder = root / "vllm/models/qwen4_exp/nvidia"
    if not folder.is_dir():
        raise ValueError("unrecognized vLLM Qwen4Exp path")
    if version("vllm") != VLLM:
        raise ValueError("only vLLM 0.32.0 is supported")
    paths = {"model": folder / "model.py", "mtp": folder / "mtp.py"}
    original = {name: path.read_text(encoding="utf-8") for name, path in paths.items()}
    candidates = {"model": patch_head(original["model"], "model"),
                  "mtp": patch_mtp(original["mtp"])}
    result = {"status": "PASS", "scope": "SOURCE_ONLY", "version": VLLM,
              "executed": False, "gpu_verified": False,
              "launch_authorized": False,
              "changes": {name: original[name] != candidates[name] for name in paths}}
    if apply:
        if os.environ.get("P5_EXPLICIT_IMAGE_BUILD") != "1":
            raise ValueError("operator-approved isolated image build required")
        for name, path in paths.items():
            path.write_text(candidates[name], encoding="utf-8")
        result["executed"] = True
        result["scope"] = "ISOLATED_IMAGE_BUILD_ONLY"
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-packages", required=True, type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        value = inspect(args.site_packages, args.apply)
    except (OSError, ValueError, SyntaxError) as exc:
        value = {"status": "BLOCKED", "issues": [str(exc)],
                 "executed": False, "gpu_verified": False}
    print(json.dumps(value, sort_keys=True, indent=2 if args.json else None))
    return 0 if value["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
