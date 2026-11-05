"""CPU-only P1 HF snapshot and image pinning tests; never touch actual HF cache."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts.manager.p1_assets import audit_checkpoint, inspect_image


class AssetAuditCPU(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="p1-asset-")
        self.addCleanup(self.tmp.cleanup)
        self.cache = Path(self.tmp.name) / "hf"
        self.repo = self.cache / "hub/models--nvidia--Qwen3.8-Flash-Next-NVFP4"
        self.rev = "a" * 40

    def write(self, p: Path, content="{}"):
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)

    def complete(self):
        self.write(self.repo / "refs/main", self.rev)
        src = self.repo / "snapshots" / self.rev
        for fn in ("config.json", "generation_config.json", "tokenizer.json",
                   "tokenizer_config.json", "chat_template.jinja",
                   "preprocessor_config.json"):
            self.write(src / fn, "{\"quantization_config\":{\"method\":\"nvfp4\"}}")
        self.write(src / "model.safetensors.index.json", json.dumps({
            "weight_map": {"l1": "model-00001.safetensors",
                           "l2": "model-00002.safetensors"}}))
        self.write(src / "model-00001.safetensors", "x")
        self.write(src / "model-00002.safetensors", "y")
        return src

    def hybrid(self):
        src = self.complete()
        dst = self.repo / "snapshots" / (self.rev + "-fp8hybrid")
        for p in src.iterdir():
            self.write(dst / p.name, p.read_text())
        self.write(dst / ".prepared", "")
        return dst

    def test_downloading_without_main_ref_not_ready(self):
        x = audit_checkpoint(self.cache)
        self.assertEqual(x["state"], "INCOMPLETE")
        self.assertFalse(x["source_complete"])
        self.assertIsNone(x["revision"])

    def test_complete_source_requires_hybrid(self):
        self.complete()
        x = audit_checkpoint(self.cache)
        self.assertTrue(x["source_complete"])
        self.assertEqual(x["state"], "SOURCE_COMPLETE")
        self.assertFalse(x["hybrid_ready"])

    def test_hybrid_prepared_empty_marker_is_allowed(self):
        self.hybrid()
        x = audit_checkpoint(self.cache)
        self.assertTrue(x["hybrid_ready"], x)
        self.assertEqual(x["state"], "READY")

    def test_missing_shard_fails_closed(self):
        src = self.complete()
        (src / "model-00002.safetensors").unlink()
        x = audit_checkpoint(self.cache)
        self.assertFalse(x["source_complete"])
        self.assertIn("model-00002.safetensors", x["source_issues"])

    def test_zero_byte_shard_fails_closed(self):
        src = self.complete()
        (src / "model-00002.safetensors").write_bytes(b"")
        self.assertFalse(audit_checkpoint(self.cache)["source_complete"])

    def test_dangling_symlink_fails_closed(self):
        src = self.complete()
        (src / "model-00001.safetensors").unlink()
        (src / "model-00001.safetensors").symlink_to("../../blobs/missing")
        self.assertFalse(audit_checkpoint(self.cache)["source_complete"])

    def test_escaping_symlink_fails_closed(self):
        src = self.complete()
        outside = Path(self.tmp.name) / "outside.safetensors"
        outside.write_text("secret")
        (src / "model-00002.safetensors").unlink()
        (src / "model-00002.safetensors").symlink_to(outside)
        self.assertFalse(audit_checkpoint(self.cache)["source_complete"])

    def test_external_shared_metadata_links_match_default_flash(self):
        source = self.complete()
        shared = Path(self.tmp.name) / "shared-metadata"
        shared.mkdir()
        for name in ("tokenizer.json", "model.safetensors.index.json"):
            original = source / name
            dest = shared / name
            dest.write_bytes(original.read_bytes())
            original.unlink()
            original.symlink_to(dest)
        outcome = audit_checkpoint(self.cache)
        self.assertTrue(outcome["source_complete"], outcome)
        self.assertEqual(outcome["source_issues"], [])

    def test_external_shared_metadata_works_in_hybrid(self):
        hybrid = self.hybrid()
        external = Path(self.tmp.name) / "shared-tokenizer.json"
        external.write_bytes((hybrid / "tokenizer.json").read_bytes())
        (hybrid / "tokenizer.json").unlink()
        (hybrid / "tokenizer.json").symlink_to(external)
        outcome = audit_checkpoint(self.cache)
        self.assertTrue(outcome["hybrid_ready"], outcome)

    def test_missing_external_metadata_target_still_blocks(self):
        source = self.complete()
        (source / "tokenizer.json").unlink()
        (source / "tokenizer.json").symlink_to(
            Path(self.tmp.name) / "no-tokenizer.json")
        outcome = audit_checkpoint(self.cache)
        self.assertFalse(outcome["source_complete"])
        self.assertIn("tokenizer.json", outcome["source_issues"])

    def test_external_shard_symlink_still_blocked(self):
        source = self.complete()
        outside = Path(self.tmp.name) / "external-shard.safetensors"
        outside.write_bytes(b"weight")
        (source / "model-00001.safetensors").unlink()
        (source / "model-00001.safetensors").symlink_to(outside)
        outcome = audit_checkpoint(self.cache)
        self.assertFalse(outcome["source_complete"])
        self.assertIn("model-00001.safetensors", outcome["source_issues"])

    def test_operator_shape_eleven_external_shards_and_two_hybrid(self):
        source = self.complete()
        shared = Path(self.tmp.name) / "shared-shards"
        shared.mkdir()
        names = [f"model-{n:05d}-of-00010.safetensors" for n in range(1, 11)]
        names += ["model-fp8-mtp-ple.safetensors"]
        self.write(source / "model.safetensors.index.json", json.dumps({
            "weight_map": {f"tensor-{n}": name for n, name in enumerate(names)}
        }))
        for original in ("model-00001.safetensors", "model-00002.safetensors"):
            (source / original).unlink()
        for name in names:
            blob = shared / name
            blob.write_bytes(b"regular nonempty shard")
            (source / name).symlink_to(blob)
        # Hybrid retains the ordinary config/tokenizer, but has a rewritten
        # index referencing only its two converted/shared weights.
        hybrid = self.repo / "snapshots" / (self.rev + "-fp8hybrid")
        for name in ("config.json", "generation_config.json", "tokenizer.json",
                     "tokenizer_config.json", "chat_template.jinja",
                     "preprocessor_config.json"):
            self.write(hybrid / name, (source / name).read_text())
        self.write(hybrid / "model.safetensors.index.json", json.dumps({
            "weight_map": {"x": names[-2], "y": names[-1]}
        }))
        for name in names[-2:]:
            (hybrid / name).symlink_to(shared / name)
        self.write(hybrid / ".prepared", "")
        result = audit_checkpoint(self.cache)
        self.assertTrue(result["source_complete"], result)
        self.assertTrue(result["hybrid_ready"], result)
        self.assertEqual(result["state"], "READY")

    def test_shard_path_traversal_fails_closed(self):
        src = self.complete()
        self.write(src / "model.safetensors.index.json", json.dumps({
            "weight_map": {"l1": "../../evil.safetensors"}}))
        self.assertFalse(audit_checkpoint(self.cache)["source_complete"])

    def test_invalid_revision_fails_closed(self):
        self.complete()
        self.write(self.repo / "refs/main", "moving-main")
        self.assertFalse(audit_checkpoint(self.cache)["source_complete"])

    def test_incomplete_blob_fails_closed(self):
        self.complete()
        self.write(self.repo / "blobs/a.incomplete", "pending")
        self.assertIn("blob_incomplete_present",
                      audit_checkpoint(self.cache)["source_issues"])

    def test_large_nvidia_index_under_64_mib_is_accepted(self):
        src = self.complete()
        index = src / "model.safetensors.index.json"
        with index.open("ab") as fp:
            fp.write(b" " * (17 * 1024 * 1024))
        data = audit_checkpoint(self.cache)
        self.assertTrue(data["source_complete"], data)
        self.assertNotIn("index_missing_or_oversize", data["source_issues"])

    def test_oversize_index_still_refused_without_json_parse(self):
        src = self.complete()
        index = src / "model.safetensors.index.json"
        with index.open("ab") as fp:
            fp.truncate(64 * 1024 * 1024 + 1)
        data = audit_checkpoint(self.cache)
        self.assertFalse(data["source_complete"], data)
        self.assertIn("index_missing_or_oversize", data["source_issues"])

    def test_wrong_label_rejected(self):
        def fake(cmd, **_):
            return subprocess.CompletedProcess(cmd, 0, "sha256:" + "b" * 64 + "|v0.29\n", "")
        self.assertFalse(inspect_image(fake)["ready"])

    def test_valid_image_label(self):
        def fake(cmd, **_):
            return subprocess.CompletedProcess(cmd, 0, "sha256:" + "b" * 64 + "|v0.32\n", "")
        self.assertTrue(inspect_image(fake)["ready"])

    def test_missing_image_not_ready(self):
        def fake(cmd, **_):
            return subprocess.CompletedProcess(cmd, 1, "", "")
        self.assertFalse(inspect_image(fake)["ready"])


if __name__ == "__main__":
    unittest.main()
