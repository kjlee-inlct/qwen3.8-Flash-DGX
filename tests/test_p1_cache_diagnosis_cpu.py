"""CPU-only read-only diagnosis fixture tests. No Docker/GPU/API requests."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.temporary.p1_cache_diagnosis import inspect


class CacheDiagnosisCPU(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.cache = Path(tmp.name) / "cache"
        self.repo = self.cache / "hub/models--nvidia--Qwen3.8-Flash-Next-NVFP4"
        self.rev = "b" * 40

    def write(self, path, data="{}"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(data)

    def complete(self):
        src = self.repo / "snapshots" / self.rev
        for f in ("config.json", "generation_config.json", "tokenizer.json",
                  "tokenizer_config.json", "chat_template.jinja",
                  "preprocessor_config.json"):
            self.write(src / f, '{"quantization_config":{"quant_method":"nvfp4"}}')
        self.write(src / "model.safetensors.index.json", json.dumps({
            "weight_map": {"one": "model-00001.safetensors"}}))
        self.write(src / "model-00001.safetensors", "weights")
        return src

    def test_missing_cache_returns_structured_facts(self):
        data = inspect(self.cache)
        self.assertIsNone(data["refs"]["main"])
        self.assertFalse(data["wizard_audit"]["source_complete"])
        self.assertEqual(data["snapshots"], [])
        self.assertFalse(data["mutation_performed"])

    def test_master_ref_complete_but_p1_main_ref_missing(self):
        self.complete()
        self.write(self.repo / "refs/master", self.rev)
        data = inspect(self.cache)
        self.assertFalse(data["wizard_audit"]["source_complete"])
        self.assertIsNone(data["refs"]["main"])
        self.assertEqual(data["refs"]["master"], self.rev)
        self.assertEqual(data["snapshots"][0]["source_issues"], [])

    def test_normal_main_snapshot_complete_hybrid_missing(self):
        self.complete()
        self.write(self.repo / "refs/main", self.rev)
        data = inspect(self.cache)
        self.assertTrue(data["wizard_audit"]["source_complete"])
        self.assertFalse(data["wizard_audit"]["hybrid_ready"])
        self.assertFalse(data["snapshots"][0]["hybrid_marker_present"])

    def test_legacy_blob_incomplete_does_not_hide_reason(self):
        self.complete()
        self.write(self.repo / "refs/main", self.rev)
        self.write(self.repo / "blobs/pending.incomplete", "partial")
        data = inspect(self.cache)
        self.assertEqual(data["uncompleted_blob_files"], 1)
        self.assertIn("blob_incomplete_present",
                      data["wizard_audit"]["source_issues"])
        self.assertEqual(data["snapshots"][0]["source_issues"], [])

    def test_missing_metadata_reasons_are_explicit(self):
        self.complete()
        self.write(self.repo / "refs/main", self.rev)
        source = self.repo / "snapshots" / self.rev
        (source / "tokenizer.json").unlink()
        (source / "model.safetensors.index.json").unlink()
        row = inspect(self.cache)["snapshots"][0]
        self.assertEqual(row["source_metadata"]["tokenizer.json"]["status"], "MISSING")
        self.assertEqual(row["source_metadata"]["model.safetensors.index.json"]["status"], "MISSING")

    def test_dangling_hf_symlink_is_distinguished_from_missing(self):
        self.complete()
        self.write(self.repo / "refs/main", self.rev)
        p = self.repo / "snapshots" / self.rev / "tokenizer.json"
        p.unlink()
        p.symlink_to("../../blobs/not-there")
        row = inspect(self.cache)["snapshots"][0]
        self.assertEqual(row["source_metadata"]["tokenizer.json"]["status"], "DANGLING_SYMLINK")
        self.assertTrue(row["source_metadata"]["tokenizer.json"]["symlink"])

    def test_snapshot_metadata_size_reports_old_gate(self):
        self.complete()
        self.write(self.repo / "refs/main", self.rev)
        p = self.repo / "snapshots" / self.rev / "model.safetensors.index.json"
        with p.open("ab") as file:
            file.write(b" " * (17 * 1024 * 1024))
        row = inspect(self.cache)["snapshots"][0]
        self.assertEqual(row["source_metadata"]["model.safetensors.index.json"]["status"],
                         "PRESENT_NONEMPTY")
        self.assertTrue(row["source_metadata"]["model.safetensors.index.json"]["exceeds_old_16mib_gate"])
        self.assertFalse(row["source_metadata"]["model.safetensors.index.json"]["exceeds_current_64mib_gate"])

    def test_shared_metadata_symlink_is_visible_and_compatible(self):
        self.complete()
        self.write(self.repo / "refs/main", self.rev)
        path = self.repo / "snapshots" / self.rev / "tokenizer.json"
        external = Path(self.cache.parent) / "shared-tokenizer.json"
        external.write_bytes(path.read_bytes())
        path.unlink()
        path.symlink_to(external)
        data = inspect(self.cache)
        info = data["snapshots"][0]["source_metadata"]["tokenizer.json"]
        self.assertEqual(info["status"], "TARGET_OUTSIDE_REPOSITORY")
        self.assertTrue(info["p1_metadata_link_compatible"])
        self.assertTrue(data["wizard_audit"]["source_complete"])

    def test_partial_weight_shard_is_reported_by_name(self):
        self.complete()
        self.write(self.repo / "refs/main", self.rev)
        (self.repo / "snapshots" / self.rev /
         "model-00001.safetensors").unlink()
        data = inspect(self.cache)
        self.assertIn("model-00001.safetensors",
                      data["snapshots"][0]["source_issues"])


if __name__ == "__main__":
    unittest.main()
