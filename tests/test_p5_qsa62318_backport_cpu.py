"""CPU regression for upstream vLLM #62318 Qwen4Exp scoped source backport."""
import ast
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from src import p5_qsa_quant_backport_v032 as abi

MODEL = '''class Qwen4ExpForCausalLM:
    packed_modules_mapping = {
        "qkv_proj": ["q_proj", "k_proj", "v_proj", "indexer.index_qk_proj"],
    }
class Qwen4ExpForConditionalGeneration:
    packed_modules_mapping = {
        "qkv_proj": Qwen4ExpForCausalLM.packed_modules_mapping["qkv_proj"],
    }
'''
QSA = '''class Qwen4ExpQSAAttention(object):
    def __init__(self, vllm_config, quant_config):
        self.indexer = QSAIndexer()
        self.fuse_indexer_projection = vllm_config.lora_config is None
        if self.fuse_indexer_projection:
            self.index_qk_size = self.indexer.index_qk_proj.output_size
            self.qkv_proj = Qwen4ExpQSAQKVIndexerLinear(
                self.qkv_proj,
                self.index_qk_size,
                model.without_modelopt_fp4(quant_config),
            )
            del self.indexer.index_qk_proj
'''

class UpstreamQSA62318CPU(unittest.TestCase):
    def test_correct_unchanged_vllm032_version_contract(self):
        self.assertEqual(abi.VERSION, "0.32.0")
        self.assertEqual(abi.ADAPTER, "qwen4exp-qsa-62318-v032-v1")

    def test_upstream_quantized_qkv_bf16_indexer(self):
        model,qsa=abi._patched_pair(MODEL,QSA)
        ast.parse(model); ast.parse(qsa)
        self.assertIn(abi.NEW_MAPPING,model)
        self.assertNotIn(abi.OLD_MAPPING,model)
        self.assertIn(abi.MARKER,qsa)
        self.assertIn("projection_method is type(self.indexer.index_qk_proj.quant_method)",qsa)
        self.assertIn("fused_quant_config,",qsa)
        self.assertNotIn(abi.OLD_FUSE,qsa)
        self.assertEqual(abi._patched_pair(model,qsa),(model,qsa))

    def test_bad_or_duplicate_anchor_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"MODEL_MAPPING_ANCHOR"):
            abi._patched_pair(MODEL.replace("indexer.index_qk_proj","unknown"),QSA)
        with self.assertRaisesRegex(ValueError,"QSA_FUSE_GUARD_ANCHOR"):
            abi._patched_pair(MODEL,QSA+QSA)
        with self.assertRaisesRegex(ValueError,"PARTIAL_PATCH_REFUSED"):
            model,_=abi._patched_pair(MODEL,QSA)
            abi._patched_pair(model,QSA)

    def test_malformed_abi_syntax_refused(self):
        with self.assertRaises(SyntaxError):
            abi._patched_pair(MODEL,QSA+"def (")

    def test_opt_in_and_no_changes_before_complete_validation(self):
        with TemporaryDirectory() as temp:
            root=Path(temp); folder=root/"vllm/models/qwen4_exp/nvidia"
            folder.mkdir(parents=True)
            m=folder/"model.py"; q=folder/"qsa.py"
            m.write_text(MODEL); q.write_text(QSA)
            with patch("src.p5_qsa_quant_backport_v032.version",return_value="0.32.0"), \
                 patch.dict(os.environ,{"P5_EXPLICIT_QSA62318_IMAGE_BUILD":"0"}):
                with self.assertRaisesRegex(ValueError,"BUILD_OPT_IN_REQUIRED"):
                    abi.inspect(root,apply=True)
            self.assertEqual(m.read_text(),MODEL)
            self.assertEqual(q.read_text(),QSA)
            with patch("src.p5_qsa_quant_backport_v032.version",return_value="0.32.0"), \
                 patch.dict(os.environ,{"P5_EXPLICIT_QSA62318_IMAGE_BUILD":"1"}):
                self.assertEqual(abi.inspect(root,apply=True)["status"],"PASS")
            self.assertIn(abi.NEW_MAPPING,m.read_text())
            self.assertIn(abi.MARKER,q.read_text())

    def test_wrong_engine_version_stops(self):
        with TemporaryDirectory() as temp:
            root=Path(temp); folder=root/"vllm/models/qwen4_exp/nvidia"
            folder.mkdir(parents=True)
            (folder/"model.py").write_text(MODEL)
            (folder/"qsa.py").write_text(QSA)
            with patch("src.p5_qsa_quant_backport_v032.version",return_value="0.32.1"):
                with self.assertRaisesRegex(ValueError,"BASE_ABI_NOT_V032"):
                    abi.inspect(root,apply=True)

    def test_build_uses_only_scoped_adapter(self):
        d=Path("Dockerfile.p5.qsa62318").read_text()
        self.assertIn("P5_EXPLICIT_QSA62318_IMAGE_BUILD=1",d)
        self.assertIn("blazux.p5.adapter=",d)
        self.assertIn('blazux.p5.base_image="${P5_BASE_IMAGE_ID}"',d)
        self.assertNotIn("p5_patch_qwen4exp_v032.py",d)
        self.assertNotIn("pip install",d)

if __name__=="__main__":
    unittest.main()
