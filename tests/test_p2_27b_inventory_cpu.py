"""P2 27B read-only cache inspection fixtures: no Docker, HF network or GPU."""
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager.p2_27b_inventory import inspect_27b
from wizard import main as router


class P2CacheCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.cache = Path(self.temp.name) / "hf"
        self.repo = self.cache / "hub/models--RadixArk--Qwen3.8-27B-NVFP4"
        self.rev = "c" * 40

    def write(self, target, content="{}"):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)

    def snapshot(self):
        self.write(self.repo / "refs/main", self.rev)
        source = self.repo / "snapshots" / self.rev
        for n in ("config.json", "tokenizer.json", "tokenizer_config.json",
                  "generation_config.json", "chat_template.jinja",
                  "model.safetensors.index.json"):
            self.write(source / n)
        self.write(source / "hf_quant_config.json", '{"quant_method":"modelopt"}')
        self.write(source / "model.safetensors.index.json", json.dumps({
            "weight_map": {"layer_a": "model-00001.safetensors",
                           "layer_b": "model-00002.safetensors"}
        }))
        self.write(source / "model-00001.safetensors", "weight1")
        self.write(source / "model-00002.safetensors", "weight2")
        return source

    def test_absent_checkpoint_never_claims_runtime(self):
        x = inspect_27b(self.cache)
        self.assertFalse(x["source_files_present"])
        self.assertFalse(x["operations_enabled"])
        self.assertEqual(x["runtime"], "NOT_RUN")
        self.assertIn("NO_PINNED_LOCAL_SNAPSHOT", x["issues"])

    def test_all_indexed_shards_present_still_no_runtime_approval(self):
        self.snapshot()
        x = inspect_27b(self.cache)
        self.assertEqual(x["indexed_shard_count"], 2)
        self.assertTrue(x["source_files_present"], x)
        self.assertEqual(x["checkpoint_status"], "SOURCE_FILES_PRESENT_UNPINNED")
        self.assertFalse(x["recipe_pinned"])
        self.assertFalse(x["gpu_verified"])
        self.assertFalse(x["operations_enabled"])

    def test_indexed_shards_can_be_hf_symlinks(self):
        source = self.snapshot()
        outside = Path(self.temp.name) / "blob"
        outside.write_bytes(b"weights")
        (source / "model-00001.safetensors").unlink()
        (source / "model-00001.safetensors").symlink_to(outside)
        x = inspect_27b(self.cache)
        self.assertTrue(x["source_files_present"], x)
        self.assertTrue(x["shards"]["model-00001.safetensors"]["symlink"])

    def test_missing_shard_blocks_source_assets(self):
        source = self.snapshot()
        (source / "model-00002.safetensors").unlink()
        x = inspect_27b(self.cache)
        self.assertIn("MISSING_SHARD:model-00002.safetensors", x["issues"])
        self.assertFalse(x["source_files_present"])

    def test_bad_index_json_blocks(self):
        source = self.snapshot()
        (source / "model.safetensors.index.json").write_text("invalid")
        self.assertIn("INVALID_INDEX_JSON", inspect_27b(self.cache)["issues"])

    def test_shard_traversal_blocks(self):
        source = self.snapshot()
        (source / "model.safetensors.index.json").write_text(
            json.dumps({"weight_map": {"a": "../bad.safetensors"}}))
        self.assertIn("INVALID_SHARD_NAMES", inspect_27b(self.cache)["issues"])

    def test_incomplete_blob_blocks_even_with_valid_snapshot(self):
        self.snapshot()
        self.write(self.repo / "blobs/pending.incomplete", "partial")
        x = inspect_27b(self.cache)
        self.assertIn("INCOMPLETE_TRANSFER_FILES_PRESENT", x["issues"])
        self.assertFalse(x["source_files_present"])

    def test_wizard_read_only_p2_status_inspection(self):
        self.snapshot()
        buffer = io.StringIO()
        with patch("subprocess.run", side_effect=AssertionError("must not run")), \
             contextlib.redirect_stdout(buffer):
            rc = router.main(["model", "27b", "status", "--inspect-cache",
                              "--cache-root", str(self.cache), "--json"])
        self.assertEqual(rc, 0)
        result = json.loads(buffer.getvalue())
        self.assertEqual(result["stage"], "p2")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["operations_enabled"])
        self.assertTrue(result["inspection"]["source_files_present"])

    def test_inspect_option_cannot_unlock_prepare(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            rc = router.main(["model", "27b", "prepare", "--inspect-cache",
                              "--execute", "--approve-plan", "a" * 64, "--json"])
        self.assertEqual(rc, 3)
        self.assertFalse(json.loads(buffer.getvalue())["executed"])

    def test_read_only_probe_does_not_rewrite_cache(self):
        self.snapshot()
        prior = (self.repo / "refs/main").read_bytes()
        inspect_27b(self.cache)
        self.assertEqual((self.repo / "refs/main").read_bytes(), prior)


if __name__ == "__main__":
    unittest.main()
