"""Flash host-cache asset evidence: CPU-only fake mount fixtures."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.manager import flash_host_assets as assets
from test_flash_recipe_draft_cpu import make_flash


class FlashHostAssetsCPU(unittest.TestCase):
    def make_complete(self, root: Path):
        doc, recipe = make_flash(root)
        model_view = (root / "hf" / "hub"
                      / "models--nvidia--Qwen3.8-Flash-Next-NVFP4"
                      / "snapshots"
                      / (recipe["model"]["source_revision"] + "-fp8hybrid"))
        (model_view / ".prepared").write_text("")
        (model_view / "tokenizer.json").write_text('{"model": "test"}')
        (model_view / "config.json").write_text('{"model_type":"qwen"}')
        (model_view / "tokenizer_config.json").write_text('{"model_max_length": 1024}')
        (model_view / "model-00001.safetensors").write_bytes(b"FAKE_SHA_RD")
        (model_view / "model.safetensors.index.json").write_text(
            json.dumps({"weight_map": {"layer.weight": "model-00001.safetensors"}}))
        (root / "chat_template.jinja").write_text("{{ messages | length }}")
        return doc, model_view

    def test_metadata_and_template_hashes_never_release_runtime(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = self.make_complete(Path(tmp))
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"],
                             "LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED")
            self.assertEqual(out["issues"], [])
            self.assertEqual(out["indexed_shard_count"], 1)
            self.assertEqual(out["index_weight_map_structure"], "OBJECT")
            self.assertEqual(out["index_weight_map_entry_count_observed"], 1)
            self.assertEqual(out["index_weight_map_entry_limit"], assets.MAX_INDEX_WEIGHTS)
            self.assertTrue(out["pinned_command_identity_matched"])
            self.assertTrue(out["prepared_view_path_observed"])
            self.assertFalse(out["verified_model_revision"])
            self.assertIsNone(out["failed_stage"])
            self.assertIsNone(out["failure_reason_code"])
            self.assertEqual(len(out["metadata_sha256"]), 3)
            self.assertEqual(len(out["template_sha256"]), 64)
            self.assertTrue(out["legacy_hf_bind_writable"])
            self.assertFalse(out["large_shard_hashes_verified"])
            self.assertFalse(out["full_docker_runtime_reinstall_qualified"])
            self.assertFalse(out["launch_allowed"])
            self.assertFalse(out["executed"])
            self.assertNotIn(str(Path(tmp)), json.dumps(out))

    def test_index_size_limit_diagnoses_stage_without_paths(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = self.make_complete(Path(tmp))
            with patch.object(assets, "MAX_META_BYTES", 5):
                out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertEqual(out["failed_stage"], "READ_MODEL_CONFIG")
            self.assertEqual(out["failure_reason_code"], "FILE_EXCEEDS_BOUNDED_READ")
            self.assertNotIn(str(Path(tmp)), json.dumps(out))
            self.assertFalse(out["verified_model_revision"])
            self.assertTrue(out["prepared_view_path_observed"])
            self.assertTrue(out["pinned_command_identity_matched"])

    def test_large_index_over_ordinary_metadata_limit_is_bounded_and_accepted(self):
        # Real NVFP4/ModelOpt weight maps are not 8 MiB config files.
        # Generate >8 MiB JSON but keep a single valid index shard.
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            index = view / "model.safetensors.index.json"
            padding = "a" * (assets.MAX_META_BYTES + 128)
            index.write_text(json.dumps({
                "weight_map": {"layer.weight": "model-00001.safetensors"},
                "metadata": {"description": padding},
            }))
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"],
                             "LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED")
            self.assertEqual(out["issues"], [])
            self.assertGreater(out["index_file_size_bytes_observed"], assets.MAX_META_BYTES)
            self.assertEqual(out["index_file_size_limit_bytes"], assets.MAX_INDEX_BYTES)
            self.assertEqual(out["indexed_shard_count"], 1)
            self.assertFalse(out["launch_allowed"])
            self.assertNotIn(padding[:128], json.dumps(out))
            self.assertNotIn(str(Path(tmp)), json.dumps(out))

    def test_index_dedicated_limit_exceeded_fails_closed_with_size(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            index = view / "model.safetensors.index.json"
            with patch.object(assets, "MAX_INDEX_BYTES", 5):
                out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertEqual(out["failed_stage"], "READ_SHARD_INDEX")
            self.assertEqual(out["failure_reason_code"], "FILE_EXCEEDS_BOUNDED_READ")
            self.assertEqual(out["index_file_size_bytes_observed"], index.stat().st_size)
            self.assertEqual(out["indexed_shard_count"], 0)
            self.assertFalse(out["verified_model_revision"])
            self.assertFalse(out["full_docker_runtime_reinstall_qualified"])

    def test_malformed_json_index_reports_bounded_diagnostic(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            (view / "model.safetensors.index.json").write_text("{untrusted-content")
            out = assets.inspect_assets(doc)
            self.assertEqual(out["failed_stage"], "PARSE_SHARD_INDEX")
            self.assertEqual(out["failure_reason_code"], "INVALID_JSON")
            self.assertNotIn("untrusted-content", json.dumps(out))

    def test_empty_or_missing_prepared_marker_and_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            # Original Flash prepare-hybrid.sh touches a zero-byte .prepared.
            self.assertTrue(assets.inspect_assets(doc)["prepared_view_path_observed"])
            marker = view / ".prepared"
            marker.unlink()
            out = assets.inspect_assets(doc)
            self.assertEqual(out["failed_stage"], "CHECK_PREPARED_MARKER")
            self.assertEqual(out["failure_reason_code"], "FILE_NOT_FOUND")
            outside = Path(tmp) / "sentinel-private"
            outside.write_text("private")
            marker.symlink_to(outside)
            # Symlinks resolving outside /hf cannot qualify the prepared view.
            out = assets.inspect_assets(doc)
            self.assertEqual(out["failed_stage"], "CHECK_PREPARED_MARKER")
            self.assertEqual(out["failure_reason_code"], "FILE_OUTSIDE_HF_CACHE")
            self.assertNotIn("sentinel-private", json.dumps(out))

    def test_unexpected_exception_text_is_never_returned(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = self.make_complete(Path(tmp))
            with patch.object(assets, "_small_digest",
                              side_effect=ValueError("sensitive_file_path_or_token")):
                out = assets.inspect_assets(doc)
            self.assertEqual(out["failed_stage"], "READ_MODEL_CONFIG")
            self.assertEqual(out["failure_reason_code"], "INVALID_DATA")
            self.assertNotIn("sensitive_file_path_or_token", json.dumps(out))

    def test_missing_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            (view / "model-00001.safetensors").unlink()
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertEqual(out["indexed_shard_count"], 0)
            self.assertFalse(out["canonical_recipe_registered"])
            self.assertEqual(out["failed_stage"], "CHECK_INDEXED_SHARDS")
            self.assertEqual(out["failure_reason_code"], "FILE_NOT_FOUND")

    def test_index_traversal_never_reads_outside_hf_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            (view / "model.safetensors.index.json").write_text(
                json.dumps({"weight_map": {"x": "../../secret.safetensors"}}))
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertFalse(out["launch_allowed"])
            self.assertEqual(out["failed_stage"], "PARSE_SHARD_INDEX")
            self.assertEqual(out["failure_reason_code"], "FLASH_SHARD_INDEX_PATH_UNQUALIFIED")

    def test_weight_map_entry_limit_reports_count_without_relaxing_policy(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            index = view / "model.safetensors.index.json"
            weight_map = {
                "layer." + str(i): "model-00001.safetensors"
                for i in range(9)
            }
            index.write_text(json.dumps({"weight_map": weight_map}))
            with patch.object(assets, "MAX_INDEX_WEIGHTS", 8):
                out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertEqual(out["failed_stage"], "PARSE_SHARD_INDEX")
            self.assertEqual(out["failure_reason_code"],
                             "FLASH_WEIGHT_MAP_ENTRY_LIMIT_EXCEEDED")
            self.assertEqual(out["index_weight_map_structure"], "OBJECT")
            self.assertEqual(out["index_weight_map_entry_count_observed"], 9)
            self.assertEqual(out["index_weight_map_entry_limit"], 8)
            self.assertFalse(out["launch_allowed"])
            self.assertFalse(out["full_docker_runtime_reinstall_qualified"])
            self.assertNotIn("layer.", json.dumps(out))

    def test_missing_empty_and_wrong_type_map_have_distinct_safe_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            index = view / "model.safetensors.index.json"
            for payload, expected_code, expected_shape, expected_count in (
                ({}, "FLASH_WEIGHT_MAP_MISSING_OR_WRONG_TYPE",
                 "MISSING_OR_WRONG_TYPE", None),
                ({"weight_map": []}, "FLASH_WEIGHT_MAP_MISSING_OR_WRONG_TYPE",
                 "MISSING_OR_WRONG_TYPE", None),
                ({"weight_map": {}}, "FLASH_WEIGHT_MAP_EMPTY", "OBJECT", 0),
            ):
                with self.subTest(code=expected_code, payload=payload):
                    index.write_text(json.dumps(payload))
                    out = assets.inspect_assets(doc)
                    self.assertEqual(out["failed_stage"], "PARSE_SHARD_INDEX")
                    self.assertEqual(out["failure_reason_code"], expected_code)
                    self.assertEqual(out["index_weight_map_structure"], expected_shape)
                    self.assertEqual(out["index_weight_map_entry_count_observed"],
                                     expected_count)
                    self.assertFalse(out["launch_allowed"])

    def test_observed_dgx_flash_299845_entry_index_passes_source_bounded_check(self):
        # Actual DGX read-only report: 299,845 keys, 31,907,813 bytes.
        # Synthetic shard data only; this does not validate GPU weights.
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            weights = {
                "tensor_" + str(i): "model-00001.safetensors"
                for i in range(299845)
            }
            (view / "model.safetensors.index.json").write_text(
                json.dumps({"weight_map": weights}))
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"],
                             "LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED")
            self.assertEqual(out["index_weight_map_entry_count_observed"], 299845)
            self.assertEqual(out["index_weight_map_entry_limit"], 400000)
            self.assertEqual(out["indexed_shard_count"], 1)
            self.assertEqual(out["issues"], [])
            self.assertFalse(out["launch_allowed"])
            self.assertFalse(out["full_docker_runtime_reinstall_qualified"])
            self.assertFalse(out["verified_model_revision"])

    def test_new_cardinality_ceiling_remains_strictly_enforced(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            (view / "model.safetensors.index.json").write_text(json.dumps({
                "weight_map": {str(i): "model-00001.safetensors" for i in range(9)}
            }))
            with patch.object(assets, "MAX_INDEX_WEIGHTS", 8):
                out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertEqual(out["failure_reason_code"],
                             "FLASH_WEIGHT_MAP_ENTRY_LIMIT_EXCEEDED")
            self.assertEqual(out["index_weight_map_entry_count_observed"], 9)
            self.assertEqual(out["index_weight_map_entry_limit"], 8)
            self.assertFalse(out["launch_allowed"])

    def test_missing_template_and_private_env_do_not_leak(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = self.make_complete(Path(tmp))
            doc["Config"]["Env"].append("ACCESS_TOKEN=secret_should_never_emit")
            doc["Mounts"][1]["Source"] = str(Path(tmp) / "secret_template.jinja")
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertNotIn("secret_should_never_emit", json.dumps(out))
            self.assertNotIn("secret_template.jinja", json.dumps(out))
            self.assertEqual(out["failed_stage"], "READ_MOUNTED_CHAT_TEMPLATE")
            self.assertEqual(out["failure_reason_code"], "FILE_NOT_FOUND")

    def test_unrecognized_flash_option_fails_even_with_valid_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = self.make_complete(Path(tmp))
            doc["Config"]["Cmd"].append("--external-risky-option")
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertFalse(out["verified_model_revision"])


if __name__ == "__main__":
    unittest.main()
