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
            self.assertEqual(len(out["metadata_sha256"]), 3)
            self.assertEqual(len(out["template_sha256"]), 64)
            self.assertTrue(out["legacy_hf_bind_writable"])
            self.assertFalse(out["large_shard_hashes_verified"])
            self.assertFalse(out["full_docker_runtime_reinstall_qualified"])
            self.assertFalse(out["launch_allowed"])
            self.assertFalse(out["executed"])
            self.assertNotIn(str(Path(tmp)), json.dumps(out))

    def test_missing_shard_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            (view / "model-00001.safetensors").unlink()
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertEqual(out["indexed_shard_count"], 0)
            self.assertFalse(out["canonical_recipe_registered"])

    def test_index_traversal_never_reads_outside_hf_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, view = self.make_complete(Path(tmp))
            (view / "model.safetensors.index.json").write_text(
                json.dumps({"weight_map": {"x": "../../secret.safetensors"}}))
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
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

    def test_unrecognized_flash_option_fails_even_with_valid_assets(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = self.make_complete(Path(tmp))
            doc["Config"]["Cmd"].append("--external-risky-option")
            out = assets.inspect_assets(doc)
            self.assertEqual(out["status"], "BLOCKED")
            self.assertFalse(out["verified_model_revision"])


if __name__ == "__main__":
    unittest.main()
