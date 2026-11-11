"""CPU regressions for P5 v3 checkpoint-targeted LM-head scale registration."""
import ast
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from src import p5_lm_head_quant_backport_v032_v3 as head

MODEL = """class Qwen4ExpForCausalLM(object):
    def __init__(self, vllm_config, config, prefix):
        self.quant_config = vllm_config.quant_config
        self.lm_head = ParallelLMHead(
            config.vocab_size,
            config.hidden_size,
            prefix=maybe_prefix(prefix, "lm_head"),
        )
"""
META = """class VocabParallelEmbedding(object):
    def __init__(self):
        self.output_partition_sizes = [self.output_size_per_partition]
class ParallelLMHead(VocabParallelEmbedding):
    def __init__(self, quant_config, bias):
        self.has_bias = bias
        self.quant_config = quant_config
"""


class P5QuantizedHeadV3CPU(unittest.TestCase):
    def test_exact_idempotent_patch_with_vllm032_metadata(self):
        self.assertEqual(head.VERSION, "0.32.0")
        changed = head.patch_source(MODEL, META)
        ast.parse(changed)
        self.assertIn(head.MARKER, changed)
        self.assertIn("quant_config=self.quant_config,", changed)
        self.assertIn('prefix="lm_head",', changed)
        self.assertNotIn('prefix=maybe_prefix(prefix, "lm_head"),', changed)
        self.assertEqual(head.patch_source(changed, META), changed)

    def test_fail_closed_on_unknown_and_partial_source(self):
        for bad in (MODEL.replace("ParallelLMHead", "UnknownHead"),
                    MODEL + MODEL,
                    MODEL.replace("self.quant_config = vllm_config.quant_config",
                                  "self.quant_config = None")):
            with self.subTest(case=bad[:60]), self.assertRaises(ValueError):
                head.patch_source(bad, META)
        with self.assertRaises(ValueError):
            head.patch_source(MODEL, META.replace("self.has_bias = bias", "pass"))
        with self.assertRaises(ValueError):
            head.patch_source(MODEL.replace(
                '            prefix=maybe_prefix(prefix, "lm_head"),',
                '            quant_config=self.quant_config,\n'
                '            prefix=maybe_prefix(prefix, "lm_head"),'
            ), META)

    def test_read_only_default_and_explicit_isolated_apply(self):
        with TemporaryDirectory() as d:
            root = Path(d)
            model = root / "vllm/models/qwen4_exp/nvidia/model.py"
            metadata = root / "vllm/model_executor/layers/vocab_parallel_embedding.py"
            model.parent.mkdir(parents=True)
            metadata.parent.mkdir(parents=True)
            model.write_text(MODEL)
            metadata.write_text(META)
            with patch("src.p5_lm_head_quant_backport_v032_v3.version", return_value="0.32.0"):
                self.assertFalse(head.inspect(root)["executed"])
                self.assertEqual(model.read_text(), MODEL)
                with patch.dict(os.environ, {"P5_EXPLICIT_LMHEAD_IMAGE_BUILD": "0"}):
                    with self.assertRaisesRegex(ValueError, "NOT_APPROVED"):
                        head.inspect(root, apply=True)
                self.assertEqual(model.read_text(), MODEL)
                with patch.dict(os.environ, {"P5_EXPLICIT_LMHEAD_IMAGE_BUILD": "1"}):
                    self.assertTrue(head.inspect(root, apply=True)["executed"])
                    self.assertFalse(head.inspect(root)["source_changed"])
                self.assertIn(head.MARKER, model.read_text())
            with patch("src.p5_lm_head_quant_backport_v032_v3.version", return_value="0.33.0"):
                with self.assertRaisesRegex(ValueError, "VERSION_MISMATCH"):
                    head.inspect(root)

    def test_dockerfile_keeps_qsa_fix_and_27b_source_immutable(self):
        dockerfile = Path("Dockerfile.p5.qsa62318-lmhead-v3").read_text()
        self.assertIn("src/p5_qsa_quant_backport_v032.py", dockerfile)
        self.assertIn("src/p5_lm_head_quant_backport_v032_v3.py", dockerfile)
        self.assertIn("P5_EXPLICIT_LMHEAD_IMAGE_BUILD=1", dockerfile)
        self.assertIn('blazux.p5.lmhead="v0.32-v3"', dockerfile)
        self.assertNotIn("pip install", dockerfile)
        self.assertNotIn("P5_EXPLICIT_LMHEAD_IMAGE_BUILD=1",
                         Path("Dockerfile").read_text())


if __name__ == "__main__":
    unittest.main()
