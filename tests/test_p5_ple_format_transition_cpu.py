"""CPU tests: PLE storage dtype independence, future FP8 registration, safe switching."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import manifest_registry as registry
from scripts.manager import ple_assets
from scripts.manager.ple_format import validate_asset, transition_contract
from scripts.manager.service_transition_preview import preview_transition


def future_fp8():
    asset = copy.deepcopy(ple_assets.asset_spec())
    asset["owner_model"] = "flash-next"
    asset["source"] = {
        "kind": "PINNED_HF_SNAPSHOT",
        "repo_id": "example/FutureFP8PLE",
        "revision": "a" * 40,
    }
    asset["reference"] = None
    asset["verification"]["method"] = "UNQUALIFIED_ADAPTER"
    asset["format"] = {
        "storage_dtype": "F8_E4M3FN",
        "scale_mode": "PER_TENSOR",
        "scale_dtype": "F32",
        "scale_block_shape": None,
        "packing": "ELEMENT_ALIGNED",
        "loader_qualified": False,
    }
    asset["layout"]["dtype"] = "F8_E4M3FN"
    asset["layout"]["weight_scale_present"] = True
    asset["layout"]["mmap_bytes"] //= 2
    asset["profiles"] = ["mtp0"]
    return asset


class PLEFormatAndSwitchCPU(unittest.TestCase):
    def test_current_bf16_pinned_contract_remains_unchanged(self):
        f = validate_asset(ple_assets.ASSET_ID, ple_assets.asset_spec())
        self.assertEqual(f.dtype, "BF16")
        self.assertEqual(f.scale_mode, "NONE")
        self.assertEqual(f.payload_bytes, 102400491520)
        self.assertEqual(f.scale_bytes, 0)
        self.assertFalse(f.loader_qualified)

    def test_future_fp8_with_scale_validated_without_false_runtime_support(self):
        f = validate_asset("future-fp8-ple", future_fp8())
        self.assertEqual(f.dtype, "F8_E4M3FN")
        self.assertEqual(f.scale_mode, "PER_TENSOR")
        self.assertEqual(f.payload_bytes, 51200245760)
        self.assertEqual(f.scale_bytes, 128 * 4)
        self.assertFalse(f.loader_qualified)

    def test_external_nvidia_fp8_global_bf16_scale_contract(self):
        # Official NVIDIA NVFP4: the PLE is F8_E4M3, independently
        # quantified from NVFP4 model body; one global BF16 scale.
        asset = future_fp8()
        asset["format"].update(
            storage_dtype="F8_E4M3", scale_mode="PER_TABLE",
            scale_dtype="BF16")
        asset["layout"]["dtype"] = "F8_E4M3"
        result = validate_asset("nvidia-fp8-ple-candidate", asset)
        self.assertEqual(result.scale_bytes, 2)
        self.assertEqual(result.expected_scale_tensors, 1)
        self.assertFalse(result.loader_qualified)

    def test_scale_per_block_needs_shape_and_is_not_assumed_bf16(self):
        asset = future_fp8()
        asset["format"].update(scale_mode="PER_BLOCK", scale_block_shape=None)
        with self.assertRaises(ValueError):
            validate_asset("fp8-ple-block", asset)
        asset["format"]["scale_block_shape"] = [32, 32]
        result = validate_asset("fp8-ple-block", asset)
        self.assertIsNone(result.scale_bytes)
        self.assertIsNone(result.expected_scale_tensors)
        self.assertFalse(result.loader_qualified)

    def test_future_fp16_and_fp32_have_independent_payload_sizes(self):
        for dtype, bytes_per_value in (("F16", 2), ("F32", 4)):
            a = future_fp8()
            a["format"].update(storage_dtype=dtype, scale_mode="NONE", scale_dtype=None)
            a["layout"].update(dtype=dtype, weight_scale_present=False,
                               mmap_bytes=320001536 * 160 * bytes_per_value)
            out = validate_asset("future-other-ple", a)
            self.assertEqual(out.payload_bytes, 320001536 * 160 * bytes_per_value)

    def test_fp8_cannot_claim_unqualified_gpu_loader(self):
        a = future_fp8()
        a["format"]["loader_qualified"] = True
        with self.assertRaises(ValueError):
            validate_asset("future-fp8-ple", a)

    def test_fp8_missing_scale_rejected(self):
        a = future_fp8()
        a["layout"]["weight_scale_present"] = False
        with self.assertRaises(ValueError):
            validate_asset("future-fp8-ple", a)
        a["layout"]["weight_scale_present"] = True
        a["format"]["scale_dtype"] = None
        with self.assertRaises(ValueError):
            validate_asset("future-fp8-ple", a)

    def test_fp8_invalid_mmap_and_packing_rejected(self):
        a = future_fp8()
        a["layout"]["mmap_bytes"] *= 2
        with self.assertRaises(ValueError):
            validate_asset("future-fp8-ple", a)
        a = future_fp8()
        a["format"]["packing"] = "PACKED_INT4"
        with self.assertRaises(ValueError):
            validate_asset("future-fp8-ple", a)

    def test_other_type_without_qualified_reference_cannot_pass_audit(self):
        doc = json.loads(ple_assets.MANIFEST_PATH.read_text())
        doc["assets"]["future-fp8-ple"] = future_fp8()
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "manifest.json"
            p.write_text(json.dumps(doc))
            spec = ple_assets.asset_spec("future-fp8-ple", path=p)
            self.assertEqual(spec["format"]["storage_dtype"], "F8_E4M3FN")
            result = ple_assets.inspect_ple_asset(
                asset_id="future-fp8-ple", roots=[Path(temp)], manifest_path=p)
        self.assertFalse(result["gpu_verified"])
        self.assertFalse(result["runtime_qualified"])
        self.assertEqual(result["status"], "BLOCKED")

    def test_no_ple_to_fp8_must_release_resources_and_qualify_loader(self):
        t = {**future_fp8(), "asset_id": "future-fp8-ple"}
        diff = transition_contract(None, t, target_profile="mtp0")
        self.assertEqual(diff["transition"], "LOAD_PLE")
        self.assertEqual(diff["target_dtype"], "F8_E4M3FN")
        self.assertTrue(diff["require_gpu_allocation_release"])
        self.assertFalse(diff["hot_reuse_allowed"])
        self.assertTrue(diff["require_target_loader_abi"])

    def test_bf16_to_fp8_is_not_hot_swappable(self):
        src = {**ple_assets.asset_spec(), "asset_id": ple_assets.ASSET_ID}
        dst = {**future_fp8(), "asset_id": "future-fp8-ple"}
        x = transition_contract(src, dst, source_profile="mtp0", target_profile="mtp0")
        self.assertEqual(x["transition"], "CHANGE_PLE_DTYPE")
        self.assertEqual((x["source_dtype"], x["target_dtype"]), ("BF16", "F8_E4M3FN"))
        self.assertTrue(x["require_ple_mmap_release"])
        self.assertTrue(x["require_rollback_assets_preserved"])
        self.assertFalse(x["hot_reuse_allowed"])

    def test_same_asset_new_mtp_profile_requires_reload(self):
        src = {**ple_assets.asset_spec(), "asset_id": ple_assets.ASSET_ID}
        x = transition_contract(src, src, source_profile="mtp0", target_profile="mtp2")
        self.assertEqual(x["transition"], "RELOAD_PROFILE")
        self.assertFalse(x["hot_reuse_allowed"])

    def test_live_27b_to_orcarouter_preview_reports_ple_transition(self):
        service = {
            "status": "OBSERVED_UNQUALIFIED",
            "observed_model": "27b", "issues": [],
            "download_running": False,
        }
        plan = preview_transition("orcarouter", service=service,
                                  checkpoint_ready=True,
                                  api_identity_verified=True,
                                  gpu_exclusivity_verified=True,
                                  rollback_verified=True, target_profile="mtp0")
        self.assertEqual(plan["ple_transition"]["transition"], "LOAD_PLE")
        self.assertEqual(plan["ple_transition"]["target_dtype"], "BF16")
        self.assertIn("TARGET_PLE_FORMAT_LOADER_NOT_QUALIFIED", plan["issues"])
        self.assertFalse(plan["operations_enabled"])
        self.assertFalse(plan["executed"])

    def test_runtime_not_released_by_operator_downtime_permission(self):
        x = transition_contract(None, {**future_fp8(), "asset_id": "future-fp8-ple"})
        self.assertFalse(x["runtime_qualified"])
        self.assertFalse(x["executed"])


if __name__ == "__main__":
    unittest.main()
