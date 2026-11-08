"""Shared Wizard manifest registry CPU contract: fail closed, no Docker/GPU."""
from __future__ import annotations
import contextlib
import copy
import io
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import manifest_registry as registry
from wizard.main import main as wizard


class ManifestRegistryCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for rel in (registry.REGISTRY_FILE, *registry.FILES.values()):
            src, dest = registry.ROOT / rel, self.root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)

    def modify(self, name, fn):
        path = self.root / (registry.FILES[name] if name in registry.FILES else name)
        d = json.loads(path.read_text(encoding="utf-8"))
        fn(d)
        path.write_text(json.dumps(d), encoding="utf-8")

    def test_full_bundle_consistent_declarative_only(self):
        d = registry.validate(root=self.root)
        self.assertEqual(d["status"], "PASS", d["issues"])
        self.assertEqual(d["manifest_files_verified"], 7)
        self.assertEqual(d["registered_models"], ["27b", "flash-next", "orcarouter"])
        self.assertEqual(d["registered_ple_assets"], ["orcarouter-bf16-ple"])
        self.assertEqual(d["scope"], "DECLARATIVE_MANIFEST_ONLY")
        self.assertFalse(d["runtime_qualified"])
        self.assertFalse(d["gpu_verified"])
        self.assertFalse(d["operations_enabled"])

    def test_ple_id_drift_fails_cross_reference(self):
        self.modify("model_discovery", lambda d: d["models"]["orcarouter"].update(
            ple_asset_id="not-the-registered-asset"))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_ple_loader_matrix_is_not_execution_permission(self):
        d = registry.validate(root=self.root)
        self.assertEqual(d["registered_ple_loader_profiles"],
                         ["blazux-vllm032-orcarouter-bf16"])
        self.assertEqual(d["registered_ple_formats"], {"orcarouter-bf16-ple": "BF16"})
        self.assertEqual(d["ple_manifest_schema"], 2)
        self.assertEqual(d["external_ple_references_count"], 2)
        self.assertFalse(d["execution_release"])

    def test_loader_profile_abuse_fails_closed(self):
        self.modify("ple_loader_profiles", lambda d: d["profiles"]
                    ["blazux-vllm032-orcarouter-bf16"].update(autostart_released=True))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_external_profile_runtime_import_forbidden(self):
        self.modify("ple_loader_profiles", lambda d:
                    d["external_references"][0].update(import_as_runtime=True))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_future_model_fp8_per_table_ple_can_register_without_runtime_release(self):
        def add_service(doc):
            doc["models"]["future"] = {
                "checkpoint": "example/FutureFP8PLE",
                "served_id": None, "container_name": "future-fp8",
                "ple_asset_id": "future-fp8-ple",
            }
        def add_discovery(doc):
            doc["models"]["future"] = {
                "repo_id": "example/FutureFP8PLE",
                "pinned_revision": "a" * 40,
                "ple_asset_id": "future-fp8-ple",
                "recipe_view": None,
            }
        def add_asset(doc):
            asset = copy.deepcopy(doc["assets"]["orcarouter-bf16-ple"])
            asset["owner_model"] = "future"
            asset["source"]["repo_id"] = "example/FutureFP8PLE"
            asset["source"]["revision"] = "a" * 40
            asset["reference"] = None
            asset["format"].update(storage_dtype="F8_E4M3",
                                   scale_mode="PER_TABLE", scale_dtype="BF16")
            asset["layout"].update(dtype="F8_E4M3",
                                    mmap_bytes=51200245760,
                                    weight_scale_present=True)
            asset["profiles"] = ["mtp0"]
            asset["verification"]["method"] = "UNQUALIFIED_ADAPTER"
            doc["assets"]["future-fp8-ple"] = asset
        self.modify("service_policy", add_service)
        self.modify("model_discovery", add_discovery)
        self.modify("ple_assets", add_asset)
        report = registry.validate(root=self.root)
        self.assertEqual(report["status"], "PASS", report["issues"])
        self.assertEqual(report["registered_ple_formats"]["future-fp8-ple"],
                         "F8_E4M3")
        self.assertFalse(report["runtime_qualified"])
        self.assertFalse(report["execution_release"])

    def test_ple_v2_transition_policy_tamper_fails(self):
        self.modify("ple_assets", lambda d:
                    d["transition_policy"].update(verify_gpu_allocation_release=False))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_ple_layout_drift_fails(self):
        self.modify("ple_assets", lambda d: d["assets"]["orcarouter-bf16-ple"]
                    ["layout"].update(width=161))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_model_service_repo_drift_fails(self):
        self.modify("service_policy", lambda d: d["models"]["orcarouter"].update(
            checkpoint="example/changed"))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_donor_pin_or_count_tamper_fails(self):
        self.modify("orcarouter_recipe", lambda d: d["mtp_donor"].update(
            tensor_count=30))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_27b_runtime_reference_drift_fails(self):
        self.modify("service_policy", lambda d: d["models"]["27b"].update(
            runtime_recipe="recipes/unknown.json"))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_active_orcarouter_not_released_even_if_source_known(self):
        self.modify("orcarouter_recipe", lambda d: d.update(launch_allowed=True))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_registry_path_injection_fails_closed(self):
        self.modify(registry.REGISTRY_FILE, lambda d: d["entries"].update(
            ple_assets="../../tmp/sneaky.json"))
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_registry_duplicate_key_fails(self):
        p = self.root / registry.REGISTRY_FILE
        p.write_text('{"schema_version":1,"registry_id":"bad","registry_id":"bad"}')
        self.assertEqual(registry.validate(root=self.root)["status"], "FAIL")

    def test_symlink_and_nonfinite_json_refused(self):
        p = self.root / "invalid.json"
        p.write_text('{"schema_version":1,"value":NaN}')
        with self.assertRaises(registry.ManifestContractError):
            registry.read_json(p)
        q = self.root / "alias.json"
        q.symlink_to(p)
        with self.assertRaises(registry.ManifestContractError):
            registry.read_json(q)

    def test_unregistered_kind_refused(self):
        with self.assertRaises(registry.ManifestContractError):
            registry.load("../../secret")

    def test_wizard_manifest_status_is_read_only(self):
        with patch("subprocess.run", side_effect=AssertionError("no Docker")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(wizard(["manifest", "status", "--json"]), 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["stage"], "manifest")
        self.assertFalse(report["executed"])

    def test_wizard_manifest_rejects_execute(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(wizard(["manifest", "validate", "--execute", "--json"]), 3)
        self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")

    def test_recipe_uses_shared_strict_manifest_reader(self):
        doc = registry.load("orcarouter_recipe")
        self.assertEqual(doc["model"]["ple_asset_id"], "orcarouter-bf16-ple")
        doc = registry.load("service_policy")
        self.assertEqual(doc["api"]["host_port"], 8000)


if __name__ == "__main__":
    unittest.main()
