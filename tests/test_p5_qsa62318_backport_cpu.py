"""CPU regression for upstream vLLM #62318 Qwen4Exp scoped source backport."""
import ast
import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from src import p5_qsa_quant_backport_v032 as abi

MODEL = '''class Qwen4ExpForCausalLM(object):
    packed_modules_mapping = {
        "qkv_proj": ["q_proj", "k_proj", "v_proj", "indexer.index_qk_proj"],
    }
class Qwen4ExpForConditionalGeneration(object):
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


# Mirrors the *already installed Blazux* Dockerfile QSA source edits;
# Dockerfile: sed -i replace original fusion guard and QKV quant_config,
# but leave the positional fused-wrapper argument unchanged.
BLAZUX_QSA = (QSA.replace(
    "class Qwen4ExpQSAAttention(object):",
    "from vllm_fp8_hybrid_modelopt import excluded_quant_config as _fp8_hybrid_excluded, qsa_requires_separate_projections as _fp8_hybrid_separate_qsa\n"
    "class Qwen4ExpQSAAttention(object):"
).replace(
    "        self.indexer = QSAIndexer()",
    "        self.qkv_proj = QKVParallelLinear(quant_config=_fp8_hybrid_excluded(quant_config))\n"
    "        self.indexer = QSAIndexer()"
).replace(
    "self.fuse_indexer_projection = vllm_config.lora_config is None",
    "self.fuse_indexer_projection = (vllm_config.lora_config is None and not _fp8_hybrid_separate_qsa(quant_config, prefix))"
))

class UpstreamQSA62318CPU(unittest.TestCase):
    def test_p5_adapter_full_manifest_contract(self):
        from scripts.manager import manifest_registry as registry
        parts = {kind: registry.load(kind) for kind in registry.FILES}
        registry._validate_bundle(parts)

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

    def test_installed_blazux_dockerfile_declares_exact_hybrid_abi(self):
        base = Path("Dockerfile").read_text(encoding="utf-8")
        self.assertIn(
            "self.fuse_indexer_projection = (vllm_config.lora_config is None "
            "and not _fp8_hybrid_separate_qsa(quant_config, prefix))", base)
        self.assertIn("quant_config=_fp8_hybrid_excluded(quant_config)", base)
        self.assertIn("from vllm_fp8_hybrid_modelopt import", base)
        self.assertIn(abi.BLAZUX_FUSE.strip(), BLAZUX_QSA)
        self.assertIn(abi.OLD_QUANT_CALL.strip(), BLAZUX_QSA)

    def test_actual_blazux_fp8_hybrid_guard_is_retained_with_upstream_fix(self):
        # This is the exact missing regression from the first DGX build.
        model, qsa = abi._patched_pair(MODEL, BLAZUX_QSA)
        ast.parse(model)
        ast.parse(qsa)
        self.assertNotIn(abi.OLD_MAPPING, model)
        self.assertIn(abi.NEW_MAPPING, model)
        self.assertNotIn(abi.BLAZUX_FUSE, qsa)
        self.assertNotIn(abi.OLD_QUANT_CALL, qsa)
        self.assertIn(abi.MARKER, qsa)
        self.assertIn("fused_quant_config = _fp8_hybrid_excluded(quant_config)", qsa)
        self.assertIn("and not _fp8_hybrid_separate_qsa(quant_config, prefix)", qsa)
        self.assertIn("projection_method is type(self.indexer.index_qk_proj.quant_method)", qsa)
        self.assertIn("fused_quant_config,", qsa)
        self.assertEqual(abi._patched_pair(model, qsa), (model, qsa))

    def test_blazux_missing_hybrid_quant_helper_fails_closed(self):
        broken=BLAZUX_QSA.replace(
            "quant_config=_fp8_hybrid_excluded(quant_config)",
            "quant_config=model.without_modelopt_fp4(quant_config)")
        with self.assertRaisesRegex(ValueError, "BLAZUX_HYBRID_ABI_INVALID"):
            abi._patched_pair(MODEL, broken)

    def test_blazux_unknown_fusion_layout_fails_closed(self):
        broken=BLAZUX_QSA.replace(
            abi.BLAZUX_FUSE,
            "        self.fuse_indexer_projection = True\n"
            "        if self.fuse_indexer_projection:\n")
        with self.assertRaisesRegex(ValueError, "QSA_FUSE_GUARD_ANCHOR_COUNT_0"):
            abi._patched_pair(MODEL, broken)

    def test_blazux_candidate_patch_apply_isolates_modified_files(self):
        with TemporaryDirectory() as temp:
            root=Path(temp); folder=root/"vllm/models/qwen4_exp/nvidia"
            folder.mkdir(parents=True)
            m=folder/"model.py"; q=folder/"qsa.py"
            m.write_text(MODEL); q.write_text(BLAZUX_QSA)
            with patch("src.p5_qsa_quant_backport_v032.version",return_value="0.32.0"), \
                 patch.dict(os.environ,{"P5_EXPLICIT_QSA62318_IMAGE_BUILD":"1"}):
                result=abi.inspect(root,apply=True)
            self.assertEqual(result["status"],"PASS")
            self.assertTrue(result["changes"]["qsa"])
            self.assertIn("fused_quant_config = _fp8_hybrid_excluded(quant_config)",q.read_text())
            self.assertIn("and not _fp8_hybrid_separate_qsa",q.read_text())
            self.assertIn(abi.NEW_MAPPING,m.read_text())
            self.assertNotIn(abi.BLAZUX_FUSE,q.read_text())

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
