"""Pinned NVIDIA 27B mixed NVFP4/FP8 metadata tests, CPU-only."""
from __future__ import annotations
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p2_27b_quant_audit as quant
from scripts.manager import p2_27b_qualification as qual


class P2PinnedQuantCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name)
        self.path = (self.cache / "hub" / quant.REPO_DIR /
                     "snapshots" / quant.REVISION / "hf_quant_config.json")

    def put(self, obj):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(obj))

    @staticmethod
    def good():
        return {
            "producer": {"name": "modelopt", "version": "fixture"},
            "quantization": {
                "quant_algo": "MIXED_PRECISION", "kv_cache_quant_algo": None,
                "quantized_layers": {
                    "model.layers.0.mlp.up_proj": {"quant_algo": "NVFP4", "group_size":16},
                    "model.layers.0.self_attn.q_proj": {"quant_algo": "FP8"},
                },
            },
        }

    def test_correct_local_pinned_config_is_still_not_gpu_pass(self):
        self.put(self.good())
        result = quant.inspect_pinned_quantization(self.cache)
        self.assertEqual(result["status"], "PINNED_METADATA_PARSED_UNQUALIFIED")
        self.assertEqual(result["layer_count"], 2)
        self.assertEqual(result["layer_algorithms"], {"FP8": 1, "NVFP4":1})
        self.assertTrue(result["mixed_fp8_nvfp4_metadata"])
        self.assertFalse(result["gpu_verified"])
        self.assertFalse(result["runtime_qualified"])

    def test_missing_pinned_file_fails_closed(self):
        self.assertIn("PINNED_HF_QUANT_CONFIG_MISSING",
                      quant.inspect_pinned_quantization(self.cache)["issues"])

    def test_wrong_revision_does_not_fall_back_to_refs_main(self):
        other = self.cache / "hub" / quant.REPO_DIR / "snapshots" / ("f"*40) / "hf_quant_config.json"
        other.parent.mkdir(parents=True, exist_ok=True)
        other.write_text(json.dumps(self.good()))
        self.assertFalse(quant.inspect_pinned_quantization(self.cache)["source_present"])

    def test_unrecognized_algo_blocks(self):
        doc = self.good()
        doc["quantization"]["quantized_layers"]["model.layers.0.mlp.up_proj"]["quant_algo"] = "UNKNOWN"
        self.put(doc)
        self.assertIn("HF_QUANT_CONFIG_INVALID",
                      quant.inspect_pinned_quantization(self.cache)["issues"])

    def test_no_fp8_mix_blocks(self):
        doc = self.good()
        for layer in doc["quantization"]["quantized_layers"].values():
            layer["quant_algo"] = "NVFP4"
        self.put(doc)
        self.assertIn("NVFP4_AND_FP8_LAYER_MIX_NOT_FOUND",
                      quant.inspect_pinned_quantization(self.cache)["issues"])

    def test_bad_json_blocks(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("broken")
        self.assertEqual(quant.inspect_pinned_quantization(self.cache)["status"], "BLOCKED")

    def test_too_large_is_rejected_before_parse(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("x" * (quant.MAX_BYTES+1))
        self.assertIn("HF_QUANT_CONFIG_SIZE_INVALID",
                      quant.inspect_pinned_quantization(self.cache)["issues"])

    def test_runtime_audit_includes_pinned_quantization_evidence(self):
        quant_result = {"status":"PINNED_METADATA_PARSED_UNQUALIFIED",
                        "mixed_fp8_nvfp4_metadata":True,"issues":[]}
        source={"source_files_present":True,"local_revision":qual.REVISION,
                "checkpoint_status":"SOURCE_FILES_PRESENT_PINNED_CANDIDATE",
                "issues":[],"configuration":{
                    "status":"PARSED_UNQUALIFIED",
                    "architecture":["Qwen3_5ForConditionalGeneration"],
                    "model_type":"qwen3_5","quant_method":"modelopt",
                    "context_length":262144}}
        service={"status":"OBSERVED_UNQUALIFIED","observed_model":"flash-next",
                 "download_running":False,"issues":[]}
        with patch("scripts.manager.p2_27b_qualification._image_facts",
                   return_value={"status":"IMAGE_INSPECT_FAILED"}) :
            result=qual.inspect_27b_runtime(
                inspector=lambda cache_root,expected_revision: source,
                service_observer=lambda:service,
                quant_auditor=lambda cache_root: quant_result,
                machine=lambda:"aarch64")
        self.assertEqual(result["quantization_audit"],quant_result)
        self.assertFalse(result["runtime_qualified"])
        self.assertNotIn("PINNED_HF_QUANT_CONFIG_UNQUALIFIED", result["issues"])

    def test_runtime_audit_blocks_malformed_pinned_quant_config(self):
        with patch("scripts.manager.p2_27b_qualification._image_facts",
                   return_value={"status":"IMAGE_INSPECT_FAILED"}):
            result=qual.inspect_27b_runtime(
                inspector=lambda cache_root,expected_revision: {
                    "source_files_present": False,"issues":[]},
                service_observer=lambda:{"status":"BLOCKED","issues":[]},
                quant_auditor=lambda cache_root:{"status":"BLOCKED","issues":["HF_QUANT_CONFIG_INVALID"]},
                machine=lambda:"aarch64")
        self.assertIn("PINNED_HF_QUANT_CONFIG_UNQUALIFIED",result["issues"])
        self.assertIn("HF_QUANT:HF_QUANT_CONFIG_INVALID",result["issues"])


if __name__=="__main__":
    unittest.main()
