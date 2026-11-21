"""P5-D manifest/Wizard CPU-only pin contract; never reads Docker or /proc."""
from __future__ import annotations

import contextlib
import io
import json
import shutil
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.manager import manifest_registry as reg
from scripts.manager.p5d_manifest_binding import source_binding
from wizard.main import main as wizard_main


class P5DManifestBindingCPU(unittest.TestCase):
    def test_valid_manifest_pin_is_not_live_attestation(self):
        with patch("subprocess.run", side_effect=AssertionError("No host process")):
            doc = source_binding("orcarouter")
        self.assertEqual(doc["status"],
            "DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED")
        asset = reg.load("ple_assets")["assets"]["orcarouter-bf16-ple"]
        self.assertEqual(doc["asset_id"], "orcarouter-bf16-ple")
        self.assertEqual(doc["source"]["repo_id"], asset["source"]["repo_id"])
        self.assertEqual(doc["source"]["revision"], asset["source"]["revision"])
        self.assertTrue(doc["served_id_provisional"])
        self.assertTrue(doc["manifest_graph_validated"])
        for key in ("executed", "operations_enabled", "runtime_qualified",
                    "ple_residency_authenticated", "host_nat_owner_authenticated",
                    "production_released"):
            self.assertFalse(doc[key], key)

    def test_manifest_graph_drift_fails_closed_before_source_binding(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for rel in (reg.REGISTRY_FILE, *reg.FILES.values()):
                dest = root / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(reg.ROOT / rel, dest)
            path = root / reg.FILES["ple_assets"]
            value = json.loads(path.read_text())
            value["assets"]["orcarouter-bf16-ple"]["source"]["revision"] = "f" * 40
            path.write_text(json.dumps(value))
            doc = source_binding("orcarouter", root=root)
        self.assertEqual(doc["status"], "BLOCKED_MANIFEST_BINDING")
        self.assertIn("P5D_MANIFEST_GRAPH_INVALID", doc["issues"])
        self.assertFalse(doc["production_released"])

    def test_unregistered_and_no_asset_are_blocked(self):
        self.assertIn("P5D_MODEL_NOT_REGISTERED",
                      source_binding("unregistered")["issues"])
        self.assertIn("P5D_PLE_ASSET_NOT_REGISTERED",
                      source_binding("27b")["issues"])
        self.assertIn("P5D_MODEL_KEY_INVALID",
                      source_binding("../invalid")["issues"])

    def test_wizard_json_route_is_declarative_only(self):
        output = io.StringIO()
        with patch("subprocess.run", side_effect=AssertionError("No runtime")), \
             contextlib.redirect_stdout(output):
            rc = wizard_main(["operations", "generic",
                              "p5d-source-binding-review", "--model", "orcarouter",
                              "--json"])
        doc = json.loads(output.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(doc["status"],
                         "DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED")
        self.assertFalse(doc["production_released"])

    def test_wizard_missing_exact_model_fails_closed(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = wizard_main(["operations", "generic",
                              "p5d-source-binding-review", "--json"])
        self.assertEqual(rc, 3)
        self.assertIn("EXACT_MODEL_REQUIRED", output.getvalue())


if __name__ == "__main__":
    unittest.main()
