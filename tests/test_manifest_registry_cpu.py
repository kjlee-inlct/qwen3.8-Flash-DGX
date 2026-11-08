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
        self.assertEqual(d["manifest_files_verified"], 6)
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
