"""PLE asset registry and model/Wizard status CPU/Fake-DGX tests."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p5_orcarouter as p5
from scripts.manager import ple_assets
from scripts.manager.installed_models import installed_models
from wizard.main import main as wizard


class P5PLEManifestCPU(unittest.TestCase):
    def test_canonical_pinned_asset_and_recipe(self):
        spec = ple_assets.asset_spec()
        recipe = p5._recipe()
        self.assertEqual(recipe["model"]["ple_asset_id"], ple_assets.ASSET_ID)
        self.assertEqual(recipe["model"]["expected_ple"], spec["layout"])
        self.assertEqual(spec["layout"]["tensor_count"], 128)
        self.assertEqual(spec["layout"]["dtype"], "BF16")
        self.assertEqual(spec["layout"]["total_rows"], 320001536)
        self.assertEqual(spec["layout"]["width"], 160)
        self.assertEqual(spec["layout"]["mmap_bytes"], 102400491520)
        self.assertEqual(spec["profiles"], ["mtp0", "mtp2"])
        self.assertTrue(spec["lifecycle"]["cache_preserve"])
        self.assertTrue(spec["lifecycle"]["delete_requires_separate_approval"])
        self.assertFalse(spec["lifecycle"]["runtime_qualified"])

    def test_service_and_discovery_cross_references(self):
        from scripts.manager.service_manifest import policy
        from scripts.manager.manifest_registry import load
        discovery = load("model_discovery")
        self.assertEqual(discovery["ple_asset_manifest"], "runtimes/ple-assets.json")
        self.assertEqual(discovery["models"]["orcarouter"]["ple_asset_id"],
                         ple_assets.ASSET_ID)
        self.assertEqual(policy()["models"]["orcarouter"]["ple_asset_id"],
                         ple_assets.ASSET_ID)

    def test_absence_is_registered_but_not_runtime_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            doc = ple_assets.inspect_ple_asset(roots=[Path(temp)])
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertEqual(doc["registration"], "REGISTERED")
        self.assertEqual(doc["source_state"], "PINNED_SNAPSHOT_NOT_FOUND")
        self.assertFalse(doc["metadata_verified"])
        self.assertFalse(doc["gpu_verified"])
        self.assertFalse(doc["runtime_qualified"])
        self.assertEqual(doc["runtime_mmap_status"], "NOT_RUN")

    def test_invalid_geometry_or_revision_fails_closed(self):
        doc = json.loads(ple_assets.MANIFEST_PATH.read_text())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "asset.json"
            doc["assets"][ple_assets.ASSET_ID]["layout"]["width"] = 161
            path.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                ple_assets.asset_spec(path=path)
            doc["assets"][ple_assets.ASSET_ID]["layout"]["width"] = 160
            doc["assets"][ple_assets.ASSET_ID]["source"]["revision"] = "f" * 40
            path.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                ple_assets.asset_spec(path=path)

    def test_duplicate_key_and_unsafe_delete_permission_refused(self):
        doc = json.loads(ple_assets.MANIFEST_PATH.read_text())
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "asset.json"
            doc["assets"][ple_assets.ASSET_ID]["lifecycle"]["delete_requires_separate_approval"] = False
            path.write_text(json.dumps(doc))
            with self.assertRaises(ValueError):
                ple_assets.asset_spec(path=path)
            path.write_text('{"schema_version":1,"schema_version":1}')
            with self.assertRaises(ValueError):
                ple_assets.asset_spec(path=path)

    def test_fake_snapshot_directory_is_not_ple_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            snap = (root / "hub/models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4/snapshots" / p5.ORCA_REV)
            snap.mkdir(parents=True)
            (snap / "config.json").write_text('{"architectures":["not-qwen"]}')
            report = ple_assets.inspect_ple_asset(roots=[root])
        self.assertEqual(report["status"], "BLOCKED")
        self.assertFalse(report["metadata_verified"])

    def test_wizard_orcarouter_status_exposes_ple_independently(self):
        with tempfile.TemporaryDirectory() as temp:
            unavailable = ple_assets.inspect_ple_asset(roots=[Path(temp)])
            with patch("scripts.manager.p5_orcarouter.audit_ple", return_value=unavailable), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = wizard(["model", "orcarouter-flash-next", "status", "--json"])
        doc = json.loads(out.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(doc["ple_asset"]["asset_id"], ple_assets.ASSET_ID)
        self.assertEqual(doc["ple_asset"]["status"], "BLOCKED")
        self.assertEqual(doc["runtime"], "NOT_RUN")
        self.assertFalse(doc["operations_enabled"])

    def test_read_only_reports_shared_ple_gate_not_gpu(self):
        with tempfile.TemporaryDirectory() as temp:
            report = p5.read_only(
                roots=[Path(temp)], service_inspector=lambda: {
                    "status": "LIVE_SERVICE_VERIFIED", "observed_model": "27b",
                    "expected_served_id": "qwen3.8-27b", "host_port": 8000,
                    "issues": [],
                })
        self.assertEqual(report["ple_asset"], report["stages"][1])
        self.assertEqual(report["stages"][1]["status"], "BLOCKED")
        self.assertEqual(report["stages"][-1]["status"], "NOT_RUN")

    def test_installed_models_returns_ple_asset_without_runtime_promotion(self):
        with tempfile.TemporaryDirectory() as temp:
            data = {
                "schema_version": 1, "ple_asset_manifest": "runtimes/ple-assets.json",
                "cache_roots": ["~/.cache/huggingface"],
                "models": {"orcarouter": {
                    "repo_id": p5.ORCA_REPO, "pinned_revision": p5.ORCA_REV,
                    "ple_asset_id": ple_assets.ASSET_ID,
                    "recipe_view": None,
                }},
            }
            report = installed_models(
                manifest=data, home=Path(temp), environment={},
                service_inspector=lambda: {"status": "LIVE_SERVICE_VERIFIED",
                                           "observed_model": "27b", "issues": []})
        row = report["models"][0]
        self.assertEqual(row["ple_asset"]["asset_id"], ple_assets.ASSET_ID)
        self.assertEqual(row["ple_asset"]["status"], "BLOCKED")
        self.assertEqual(row["ple_asset"]["runtime_mmap_status"], "NOT_RUN")
        self.assertFalse(row["active_api_identity_verified"])

    def test_stopped_idle_service_can_pass_preflight_without_false_gpu_release(self):
        with tempfile.TemporaryDirectory() as temp:
            report = p5.read_only(
                roots=[Path(temp)],
                service_inspector=lambda: {
                    "status": "OBSERVED_UNQUALIFIED",
                    "observed_model": None,
                    "observed_state": "NO_MANAGED_MODEL_RUNNING",
                    "api_port_8000_listening": False,
                    "issues": [],
                })
        self.assertEqual(report["stages"][3]["status"], "PASS")
        self.assertEqual(report["stages"][3]["service_state"], "STOPPED_PORT_FREE")
        self.assertTrue(report["stages"][3]["downtime_27b_permitted"])
        self.assertFalse(report["production_released"])
        self.assertFalse(report["gpu_verified"])

    def test_loader_capability_profile_is_visible_but_not_qualified(self):
        report = p5.source_plan("mtp2")
        self.assertEqual(report["ple_loader_profile"]["runtime_version"], "0.32.0")
        self.assertEqual(report["ple_loader_profile"]["storage_dtype"], "BF16")
        self.assertFalse(report["ple_loader_profile"]["cuda_loader_verified"])
        self.assertFalse(report["ple_loader_profile"]["rollback_verified"])
        self.assertFalse(report["ple_loader_profile"]["autostart_released"])

    def test_unregistered_ple_ref_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            data = {
                "schema_version": 1, "cache_roots": [],
                "models": {"orcarouter": {
                    "repo_id": p5.ORCA_REPO, "pinned_revision": p5.ORCA_REV,
                    "ple_asset_id": "wrong-id", "recipe_view": None}},
            }
            with self.assertRaises(ValueError):
                installed_models(manifest=data, home=Path(temp),
                                 environment={}, service_inspector=lambda: {})
        
    def test_model_first_selection_exposes_registered_ple_without_runtime_pass(self):
        from wizard.quickstart import selection_plan
        plan = selection_plan("orcarouter", service={
            "status": "OBSERVED_UNQUALIFIED", "observed_model": None,
            "download_running": False, "issues": [],
        })
        self.assertEqual(plan["ple_registration"]["asset_id"], ple_assets.ASSET_ID)
        self.assertTrue(plan["ple_registration"]["registered"])
        self.assertFalse(plan["ple_registration"]["runtime_qualified"])
        self.assertFalse(plan["operations_enabled"])

    def test_plan_declares_asset_but_no_live_verification(self):
        doc = p5.source_plan()
        self.assertEqual(doc["ple_asset"]["asset_id"], ple_assets.ASSET_ID)
        self.assertEqual(doc["ple_asset"]["metadata_verified"], False)
        self.assertEqual(doc["ple_asset"]["runtime_mmap_status"], "NOT_RUN")
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIsNone(doc["plan_id"])


if __name__ == "__main__":
    unittest.main()
