"""CPU-only manifest-led Wizard service status tests; no Docker or HTTP."""
from __future__ import annotations

import contextlib
import io
import json
from unittest.mock import patch
import unittest

from scripts.manager.service_status import inspect_live_status
from wizard import main as router


def good_manifest():
    return {
        "status": "OBSERVED_UNQUALIFIED",
        "observed_model": "flash-next",
        "api_port_8000_listening": True,
        "issues": [],
        "managed_containers": [{
            "model": "flash-next", "container_name": "qwen38-flash",
            "image_id": "sha256:" + "a" * 64,
            "status": "Up 2 hours", "ports": "0.0.0.0:8000->8000/tcp",
        }]
    }


def good_health(**kwargs):
    return {
        "status": "API_IDENTITY_CONFIRMED",
        "observed_model": "flash-next",
        "health_http_ok": True,
        "api_identity_verified": True,
        "expected_model_id": "qwen3.8-flash-next",
        "model_ids": ["qwen3.8-flash-next"],
        "issues": [],
    }


class ServiceStatusCPU(unittest.TestCase):
    def status(self, manifest=None, probe=good_health):
        return inspect_live_status(manifest_inspector=lambda: (
            good_manifest() if manifest is None else manifest),
            health_inspector=probe)

    def test_valid_manifest_and_api_respond_as_one_status(self):
        s = self.status()
        self.assertEqual(s["status"], "LIVE_SERVICE_VERIFIED")
        self.assertTrue(all(s["checks"].values()))
        self.assertEqual(s["observed_model"], "flash-next")
        self.assertEqual(s["expected_served_id"], "qwen3.8-flash-next")
        self.assertFalse(s["gpu_exclusivity_verified"])
        self.assertFalse(s["previous_trial_provenance_verified"])
        self.assertFalse(s["executed"])

    def test_27b_runtime_has_a_distinct_expected_id(self):
        m = good_manifest()
        m["observed_model"] = "27b"
        m["managed_containers"][0].update(
            model="27b", container_name="qwen38-27b")
        def probe(**kwargs):
            return {**good_health(), "observed_model": "27b",
                    "expected_model_id": "qwen3.8-27b",
                    "model_ids": ["qwen3.8-27b"]}
        s = self.status(m, probe)
        self.assertEqual(s["status"], "LIVE_SERVICE_VERIFIED")
        self.assertEqual(s["expected_served_id"], "qwen3.8-27b")

    def test_wrong_served_id_is_blocked(self):
        def probe(**kwargs):
            return {**good_health(), "status": "BLOCKED",
                    "api_identity_verified": False,
                    "model_ids": ["qwen3.8-27b"],
                    "issues": ["SERVED_MODEL_ID_MISMATCH"]}
        s = self.status(probe=probe)
        self.assertEqual(s["status"], "BLOCKED")
        self.assertIn("SERVED_MODEL_ID_MISMATCH", s["issues"])

    def test_missing_port_mapping_cannot_claim_verified(self):
        m = good_manifest()
        m["managed_containers"][0]["ports"] = ""
        s = self.status(m)
        self.assertEqual(s["status"], "BLOCKED")
        self.assertIn("ACTIVE_CONTAINER_PORT_8000_PUBLISHED_FAILED", s["issues"])

    def test_two_managed_models_cannot_claim_healthy(self):
        m = good_manifest()
        m["managed_containers"].append({
            "model": "27b", "container_name": "qwen38-27b",
            "status": "Up 1 min", "ports": "0.0.0.0:8001->8000/tcp"})
        self.assertEqual(self.status(m)["status"], "BLOCKED")

    def test_unknown_manifest_never_claims_success(self):
        m = {"status": "BLOCKED", "observed_model": None,
             "issues": ["docker_inventory_incomplete"]}
        s = self.status(m, probe=lambda **kwargs:{
            "status": "BLOCKED", "issues": ["SERVICE_MANIFEST_UNVERIFIED"]})
        self.assertEqual(s["status"], "BLOCKED")
        self.assertIn("docker_inventory_incomplete", s["issues"])

    def test_status_uses_same_manifest_for_api_check(self):
        m = good_manifest()
        called = []
        def probe(*, service):
            called.append(service)
            return good_health()
        s = self.status(m, probe)
        self.assertEqual(s["status"], "LIVE_SERVICE_VERIFIED")
        self.assertIs(called[0], m)

    def test_wizard_status_cli_exposes_integrated_json(self):
        s = self.status()
        with patch("wizard.menus.operations.service.inspect_live_status",
                   return_value=s) as f,              contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main(["service", "manager", "status", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["status"],
                         "LIVE_SERVICE_VERIFIED")
        f.assert_called_once()

    def test_inventory_keeps_old_read_only_manifest_contract(self):
        m = good_manifest()
        with patch("wizard.menus.operations.service.inspect_service",
                   return_value=m) as f,              contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main(["service", "manager", "inventory", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["status"],
                         "OBSERVED_UNQUALIFIED")
        f.assert_called_once()


if __name__ == "__main__":
    unittest.main()
