"""P7 component evidence cannot be promoted by a user-authored PASS string."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.manager.integration_contract import integration_reconcile
from scripts.manager.generic_operations import model_catalog
from wizard.main import main as wizard_main


class P7IntegrationContractCPU(unittest.TestCase):
    def setUp(self):
        self.model = "27b"
        identity = model_catalog()["models"][self.model]
        time = "2026-11-09T00:00:00+00:00"
        shared = {"model": self.model, "observed_at_utc": time,
                  "probe_mode": "DIRECT_OBSERVATION"}
        def entry(tag, **extra):
            return dict(shared, probe_id=tag, **extra)
        self.doc = {
            "model": self.model, "api_port": 8000,
            "active_gpu_models": [self.model],
            "service": entry("service", container_name=identity["container"],
                             container_id="a" * 64,
                             served_id=identity["served_id"],
                             port=8000, http_status=200),
            "proxy": entry("proxy", observed_served_id=identity["served_id"],
                           upstream_port=8000, http_status=200),
            "gateway": entry("gateway", observed_served_id=identity["served_id"],
                             upstream_port=8000, http_status=200),
            "storage": entry("storage", checkpoint=identity["checkpoint"],
                             recipe_path=identity["recipe_path"],
                             assets_verified=True),
        }

    def test_pass_fields_alone_do_not_qualify_four_components(self):
        naive = {x: {"status": "PASS", "model": self.model,
                     "evidence_id": "faked"}
                 for x in ("service", "proxy", "gateway", "storage")}
        self.assertEqual(integration_reconcile(self.model, naive)["status"], "BLOCKED")
        self.assertEqual(len(integration_reconcile(self.model, naive)["component_checks"]), 4)

    def test_consistent_documents_are_still_never_live_verified(self):
        doc = integration_reconcile(self.model, self.doc)
        self.assertEqual(doc["status"], "SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED")
        self.assertFalse(doc["real_dgx_verified"])
        self.assertFalse(doc["proxy_gateway_verified"])
        self.assertFalse(doc["operations_enabled"])
        self.assertFalse(doc["production_released"])

    def test_canonical_container_and_port_constraints(self):
        self.doc["service"]["container_name"] = "trial-v3-not-canonical"
        self.assertIn("SERVICE_CANONICAL_CONTAINER_MISMATCH",
                      integration_reconcile(self.model, self.doc)["issues"])
        self.doc["service"]["container_name"] = "qwen38-27b"
        self.doc["gateway"]["upstream_port"] = 8001
        self.assertIn("GATEWAY_UPSTREAM_PROBE_MISSING",
                      integration_reconcile(self.model, self.doc)["issues"])
        self.doc["gateway"]["upstream_port"] = 8000
        self.doc["active_gpu_models"] = ["27b", "orcarouter"]
        self.assertIn("ONE_ACTIVE_MODEL_NOT_INDEPENDENTLY_EVIDENCED",
                      integration_reconcile(self.model, self.doc)["issues"])

    def test_unknown_or_stale_component_probe_fails_closed(self):
        self.doc["proxy"]["observed_at_utc"] = "2026-11-09T00:03:00+00:00"
        self.assertIn("COMPONENT_OBSERVATION_WINDOW_EXCEEDS_120_SECONDS",
                      integration_reconcile(self.model, self.doc)["issues"])
        self.doc["proxy"]["observed_at_utc"] = "invalid"
        self.assertIn("PROXY_OBSERVATION_TIME_MISSING",
                      integration_reconcile(self.model, self.doc)["issues"])

    def test_future_model_registry_is_automatically_supported(self):
        from scripts.manager.service_manifest import policy
        cfg = json.loads(json.dumps(policy()))
        cfg["models"]["future"] = {
            "checkpoint": "future/checkpoint", "container_name": "future",
            "served_id": "future-id"}
        report = integration_reconcile("future", {}, config=cfg)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertEqual(len(report["component_checks"]), 4)

    def test_cli_read_only_contract(self):
        with tempfile.TemporaryDirectory() as temp:
            f = Path(temp) / "components.json"
            f.write_text(json.dumps(self.doc), encoding="utf-8")
            with patch("subprocess.run", side_effect=AssertionError("no mutations")), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc = wizard_main(["operations", "generic", "integration-reconcile",
                                  "--model", self.model,
                                  "--component-evidence", str(f), "--json"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out.getvalue())["status"],
                             "SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED")


if __name__ == "__main__":
    unittest.main()
