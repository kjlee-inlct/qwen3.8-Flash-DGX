"""CPU-only vLLM0.32 Qwen4Exp P5 patched source guard tests."""
from __future__ import annotations
import ast
from pathlib import Path
import unittest
from unittest.mock import patch
from src import p5_patch_qwen4exp_v032 as abi
from scripts.p5_vendor.mtp import MTP_TENSOR_NAMES

MODEL = '''import torch
class Qwen4ExpForCausalLM(nn.Module):
    def __init__(self, config, prefix):
        self.quant_config = vllm_config.quant_config
        self.lm_head = ParallelLMHead(
            config.vocab_size,
            config.hidden_size,
            prefix=maybe_prefix(prefix, "lm_head"),
        )
'''
MTP = '''import torch
def _remap_ignored_layers(ignored_layers, mtp_start_layer_idx):
    return ignored_layers
def _make_draft_vllm_config(vllm_config, mtp_start_layer_idx):
    draft_quant_config = get_draft_quant_config(vllm_config)
    if draft_quant_config is not None:
        configure_quant_config(draft_quant_config, Qwen4ExpMTP)
    return draft_quant_config
class Qwen4ExpMTP(nn.Module, SupportsHCSP, SupportsPP, Qwen4ExpMixtureOfExperts):
    def __init__(self, vllm_config, prefix):
        self.quant_config = vllm_config.quant_config
        self.lm_head = ParallelLMHead(
            config.vocab_size,
            config.hidden_size,
            prefix=maybe_prefix(prefix, "lm_head"),
        )
    def load_weights(self, weights: Iterable[tuple[str, torch.Tensor]]) -> set[str]:
        def remap_weight_names():
            for name, weight in weights:
                remapped_name = _remap_mtp_weight_name(name)
                if remapped_name is not None:
                    yield remapped_name, weight
        mapper = WeightsMapper()
        loader = AutoWeightsLoader(self)
        return loader.load_weights(remap_weight_names(), mapper=mapper)
'''

class P5Vllm032PatchCPU(unittest.TestCase):
    def test_version_and_canonical_31_names(self):
        self.assertEqual(abi.VLLM, "0.32.0")
        self.assertEqual(abi.FLAG, "VLLM_P5_ORCAROUTER")
        self.assertEqual(abi.MTP_NAMES, MTP_TENSOR_NAMES)
        self.assertEqual(len(set(abi.MTP_NAMES)), 31)

    def test_quantized_head_opt_in_and_idempotency(self):
        result = abi.patch_head(MODEL, "model")
        ast.parse(result)
        self.assertIn('quant_config=(self.quant_config if _blazux_p5_os.environ.get("VLLM_P5_ORCAROUTER", "0") == "1" else None)', result)
        self.assertIn('prefix=maybe_prefix(prefix, "lm_head"),', result)
        self.assertEqual(abi.patch_head(result, "model"), result)

    def test_compressed_ignore_and_bf16_guard(self):
        result = abi.patch_mtp(MTP)
        ast.parse(result)
        self.assertIn('draft_quant_config.ignore = _remap_ignored_layers(', result)
        self.assertIn('native BF16 MTP tensor mismatch', result)
        self.assertIn('torch.bfloat16', result)
        self.assertIn('duplicate native MTP tensor', result)
        self.assertEqual(abi.patch_mtp(result), result)

    def test_guard_references_exact_31_names_no_globs(self):
        result = abi.patch_mtp(MTP)
        self.assertIn("_BLZ_P5_MTP_NAMES = frozenset(", result)
        self.assertIn("mtp.fc_embedding.weight", result)
        self.assertNotIn("'mtp.*'", result)

    def test_broken_head_and_load_anchor_fail_closed(self):
        with self.assertRaises(ValueError):
            abi.patch_head(MODEL.replace('prefix=maybe_prefix(prefix, "lm_head"),', ''), "model")
        with self.assertRaises(ValueError):
            abi.patch_head(MODEL.replace('prefix=maybe_prefix(prefix, "lm_head"),',
                'prefix=maybe_prefix(prefix, "lm_head"),\n            prefix=maybe_prefix(prefix, "lm_head"),'), "model")
        with self.assertRaises(ValueError):
            abi.patch_mtp(MTP.replace('return loader.load_weights(remap_weight_names(), mapper=mapper)', 'return set()'))

    def test_partial_mtp_patch_forbidden(self):
        with self.assertRaises(ValueError):
            abi.patch_mtp(MTP.replace('import torch\n',
                                      'import torch\n' + abi.IGNORE_MARKER + '\n'))

    def test_candidate_image_has_no_automatic_execution(self):
        docker = Path("Dockerfile.p5.candidate").read_text(encoding="utf-8")
        self.assertIn("P5_QUALIFIED_BASE_IMAGE", docker)
        self.assertIn("P5_EXPLICIT_IMAGE_BUILD=1", docker)
        self.assertNotIn("0.1.dev20073", docker)

    def test_incompatible_installed_vllm_fails_closed(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "vllm/models/qwen4_exp/nvidia").mkdir(parents=True)
            with patch("src.p5_patch_qwen4exp_v032.version", return_value="0.31.0"):
                with self.assertRaisesRegex(ValueError, "only vLLM 0.32.0"):
                    abi.inspect(root)

    def test_apply_requires_opt_in_before_any_files_change(self):
        from tempfile import TemporaryDirectory
        with TemporaryDirectory() as temp:
            root = Path(temp)
            folder = root / "vllm/models/qwen4_exp/nvidia"
            folder.mkdir(parents=True)
            (folder / "model.py").write_text(MODEL, encoding="utf-8")
            (folder / "mtp.py").write_text(MTP, encoding="utf-8")
            with patch("src.p5_patch_qwen4exp_v032.version", return_value="0.32.0"), patch.dict("os.environ", {"P5_EXPLICIT_IMAGE_BUILD": "0"}):
                with self.assertRaisesRegex(ValueError, "operator-approved isolated image"):
                    abi.inspect(root, apply=True)
            self.assertEqual((folder / "model.py").read_text(), MODEL)
            self.assertEqual((folder / "mtp.py").read_text(), MTP)

if __name__ == "__main__":
    unittest.main()
