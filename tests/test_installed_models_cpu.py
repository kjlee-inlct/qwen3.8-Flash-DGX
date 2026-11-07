"""CPU/read-only tests for installed-model discovery across legacy HF caches."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

from scripts.manager.installed_models import installed_models
from wizard import main as router

ORCA_REV = "3a3b63161c0745390e5270179af42e46efc70799"
REV_27B = "482ca0f3832238542f8f5295dde86b5f22711d80"
LEGACY = "Workspace/llm/yslab-qwen38-bf16ple-dgx-spark"


def manifest():
    return {
        "schema_version": 1,
        "cache_roots": ["~/.cache/huggingface", "~/" + LEGACY + "/hf-cache"],
        "include_hf_cache_environment": True,
        "models": {
            "flash-next": {"repo_id": "nvidia/Qwen3.8-Flash-Next-NVFP4",
                           "pinned_revision": None, "recipe_view": None},
            "27b": {"repo_id": "nvidia/Qwen3.8-27B-NVFP4",
                    "pinned_revision": REV_27B, "recipe_view": None},
            "orcarouter": {"repo_id": "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4",
                           "pinned_revision": ORCA_REV,
                           "recipe_view": "~/" + LEGACY +
                                          "/recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2"},
        }
    }


def service():
    return {"status": "LIVE_SERVICE_VERIFIED", "observed_model": "flash-next",
            "issues": []}


def create_snapshot(root, repo_id, revision, *, omit_shard=False, symlink=False):
    repo = root / "hub" / ("models--" + repo_id.replace("/", "--", 1))
    snap = repo / "snapshots" / revision
    snap.mkdir(parents=True)
    (snap / "config.json").write_text('{"model_type":"qwen3_5"}', encoding="utf-8")
    (snap / "tokenizer.json").write_text('{"version":"1"}', encoding="utf-8")
    (snap / "model.safetensors.index.json").write_text(json.dumps({
        "weight_map": {"layer1": "model-00001-of-00001.safetensors"}}), encoding="utf-8")
    if not omit_shard:
        shard = snap / "model-00001-of-00001.safetensors"
        if symlink:
            blob = repo / "blobs" / "abc"
            blob.parent.mkdir()
            blob.write_bytes(b"dummy-unloaded-weights")
            shard.symlink_to(blob)
        else:
            shard.write_bytes(b"dummy-unloaded-weights")
    return snap


class InstalledModelsCPU(unittest.TestCase):
    def setUp(self):
        self.ctx = tempfile.TemporaryDirectory()
        self.addCleanup(self.ctx.cleanup)
        self.home = Path(self.ctx.name)
        self.cfg = manifest()
        self.env = {}

    def scan(self, **kwargs):
        return installed_models(manifest=self.cfg, home=self.home,
                                environment=self.env,
                                service_inspector=service, **kwargs)

    def model(self, doc, name):
        return next(row for row in doc["models"] if row["model"] == name)

    def test_missing_cache_must_not_be_claimed_deleted_or_installed(self):
        doc = self.scan()
        self.assertEqual(doc["status"], "READ_ONLY_INVENTORY")
        self.assertEqual(len(doc["models"]), 3)
        self.assertEqual(self.model(doc, "orcarouter")["source_state"],
                         "NOT_FOUND_IN_CONFIGURED_ROOTS")
        self.assertFalse(doc["executed"])
        self.assertFalse(doc["operations_enabled"])
        self.assertTrue(self.model(doc, "flash-next")["active_api_identity_verified"])
        self.assertFalse(self.model(doc, "orcarouter")["active_api_identity_verified"])

    def test_orcarouter_legacy_pinned_cache_and_view_are_visible(self):
        legacy = self.home / LEGACY
        create_snapshot(legacy / "hf-cache",
                        "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4",
                        ORCA_REV)
        view = legacy / "recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2"
        view.mkdir(parents=True)
        doc = self.scan()
        row = self.model(doc, "orcarouter")
        self.assertEqual(row["source_state"], "SOURCE_FILES_PRESENT_UNQUALIFIED")
        self.assertTrue(row["source_files_present"])
        self.assertTrue(row["legacy_recipe_view"]["directory_present"])
        self.assertEqual(row["cache_snapshots"][0]["revision"], ORCA_REV)
        self.assertFalse(row["runtime_qualified"])
        self.assertFalse(row["installation_authorized"])

    def test_missing_weight_stays_incomplete_but_source_not_hidden(self):
        legacy = self.home / LEGACY
        create_snapshot(legacy / "hf-cache",
                        "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4",
                        ORCA_REV, omit_shard=True)
        row = self.model(self.scan(), "orcarouter")
        self.assertEqual(row["source_state"], "SNAPSHOT_INCOMPLETE_OR_UNVERIFIED")
        self.assertEqual(row["cache_snapshots"][0]["missing_or_unreadable_shards"], 1)
        self.assertFalse(row["source_files_present"])

    def test_symlinked_hf_weight_blobs_resolve(self):
        legacy = self.home / LEGACY
        snap = create_snapshot(legacy / "hf-cache",
                               "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4",
                               ORCA_REV, symlink=True)
        row = self.model(self.scan(), "orcarouter")
        # The test creates a symlink; a dangling symlink cannot qualify.
        self.assertTrue((snap / "model-00001-of-00001.safetensors").is_symlink())
        self.assertTrue(row["source_files_present"])

    def test_dangling_symlink_cannot_qualify_source(self):
        legacy = self.home / LEGACY
        snap = create_snapshot(legacy / "hf-cache",
                               "orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4",
                               ORCA_REV)
        shard = snap / "model-00001-of-00001.safetensors"
        shard.unlink()
        shard.symlink_to(snap / "nonexistent-blob")
        row = self.model(self.scan(), "orcarouter")
        self.assertFalse(row["source_files_present"])
        self.assertEqual(row["source_state"], "SNAPSHOT_INCOMPLETE_OR_UNVERIFIED")

    def test_env_cache_27b_immutable_snapshot(self):
        cache = self.home / "custom"
        self.env["HF_CACHE"] = str(cache)
        create_snapshot(cache, "nvidia/Qwen3.8-27B-NVFP4", REV_27B)
        row = self.model(self.scan(), "27b")
        self.assertEqual(row["cache_snapshots"][0]["revision"], REV_27B)
        self.assertEqual(row["source_state"], "SOURCE_FILES_PRESENT_UNQUALIFIED")

    def test_unknown_cache_repo_is_discovered_without_registration(self):
        cache = self.home / ".cache/huggingface"
        create_snapshot(cache, "example/model-test", "a"*40)
        doc = self.scan()
        self.assertEqual(doc["other_cached_repos"][0]["repo_id"],
                         "example/model-test")
        self.assertEqual(doc["other_cached_repos"][0]["state"],
                         "UNREGISTERED_CACHE_SNAPSHOT_OBSERVED")

    def test_recipe_view_alone_is_not_qualified_source(self):
        view = (self.home / LEGACY /
                "recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2")
        view.mkdir(parents=True)
        row = self.model(self.scan(), "orcarouter")
        self.assertEqual(row["source_state"], "RECIPE_VIEW_ONLY_SOURCE_UNVERIFIED")
        self.assertFalse(row["source_files_present"])

    def test_cli_model_list_read_only_routes_and_rejects_mutation_flags(self):
        doc = self.scan()
        with patch("scripts.manager.installed_models.installed_models", return_value=doc), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc = router.main(["model", "list", "--installed", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out.getvalue())["models"][2]["model"],
                         "orcarouter")
        for args in (["model", "list", "--execute", "--json"],
                     ["model", "list", "--installed", "--execute", "--json"]):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                self.assertEqual(router.main(args), 2)
                self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")

    def test_cli_model_list_without_installed_fails_closed(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(router.main(["model", "list", "--json"]), 2)
        self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")

    def test_manifest_rejects_untrusted_repo_id(self):
        self.cfg["models"]["orcarouter"]["repo_id"] = "../../bad"
        with self.assertRaises(ValueError):
            self.scan()


if __name__ == "__main__":
    unittest.main()
