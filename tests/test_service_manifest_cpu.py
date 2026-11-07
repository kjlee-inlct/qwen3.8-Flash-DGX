"""Pure CPU tests of the single-model service policy and observed manifest."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import patch

from scripts.manager.service_manifest import (
    policy, manifest_from_observation, inspect_service
)
from wizard import main as wizard


class ServiceManifestCPU(unittest.TestCase):
    def setUp(self):
        self.inv = {
            "errors": [], "observed_listen_ports": [8000],
            "containers": [{
                "name": "qwen38-flash", "status": "Up 1 hour",
                "image_id": "sha256:" + "a" * 64,
                "ports": "0.0.0.0:8000->8000/tcp",
            }],
        }

    def test_committed_policy_shares_port_and_excludes_simultaneous_models(self):
        cfg = policy()
        self.assertEqual(cfg["max_active_gpu_models"], 1)
        self.assertEqual(cfg["api"]["host_port"], 8000)
        self.assertTrue(cfg["transitions"]["stop_old_before_start_new"])
        self.assertTrue(cfg["transitions"]["failed_new_model_rollback_to_old"])
        self.assertTrue(cfg["download"]["may_overlap_live_inference"])

    def test_manifest_observes_flash_next_but_does_not_claim_api_or_gpu_verification(self):
        doc = manifest_from_observation(self.inv, desired="flash-next")
        self.assertEqual(doc["status"], "OBSERVED_UNQUALIFIED")
        self.assertEqual(doc["observed_model"], "flash-next")
        self.assertEqual(doc["policy"]["api_host_port"], 8000)
        self.assertFalse(doc["drift"])
        self.assertFalse(doc["api_model_identity_verified"])
        self.assertFalse(doc["gpu_exclusivity_verified"])
        self.assertFalse(doc["operations_enabled"])

    def test_two_managed_models_running_blocks_manifest(self):
        inv = {**self.inv, "containers": [
            *self.inv["containers"],
            {"name": "qwen38-27b", "status": "Up 4 min",
             "image_id": "sha256:" + "b" * 64,
             "ports": "0.0.0.0:18310->8000/tcp"}]}
        doc = manifest_from_observation(inv)
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIn("SINGLE_ACTIVE_MODEL_POLICY_VIOLATION", doc["issues"])
        self.assertFalse(doc["operations_enabled"])

    def test_inflight_27b_download_visible_without_gpu_or_api_claim(self):
        inventory = {**self.inv, "containers": [
            *self.inv["containers"],
            {"name": "qwen38-27b-dl", "status": "Up 2 minutes",
             "image_id": "sha256:" + "c" * 64, "ports": ""},
        ]}
        observed = manifest_from_observation(inventory)
        self.assertTrue(observed["download_running"])
        self.assertEqual(observed["download_containers"][0]["name"],
                         "qwen38-27b-dl")
        self.assertEqual(observed["observed_model"], "flash-next")
        self.assertFalse(observed["api_model_identity_verified"])
        self.assertFalse(observed["operations_enabled"])

    def test_completed_or_exited_download_not_reported_running(self):
        inventory = {**self.inv, "containers": [
            *self.inv["containers"],
            {"name": "qwen38-27b-dl", "status": "Exited (0)",
             "image_id": "sha256:" + "c" * 64, "ports": ""},
        ]}
        self.assertFalse(manifest_from_observation(inventory)["download_running"])

    def test_orcarouter_registered_but_unqualified(self):
        config = policy()
        self.assertIn("orcarouter", config["models"])
        self.assertEqual(config["models"]["orcarouter"]["qualification"],
                         "NOT_VERIFIED")

    def test_desired_27b_requires_actual_transition(self):
        doc = manifest_from_observation(self.inv, desired="27b")
        self.assertTrue(doc["drift"])
        self.assertEqual(doc["observed_model"], "flash-next")
        self.assertTrue(doc["safety"]["new_service_start_requires_old_stop_and_free_port"])

    def test_observation_failures_are_never_assumed_empty(self):
        doc = manifest_from_observation({
            "errors": ["docker_inventory_incomplete"], "containers": [],
            "observed_listen_ports": []})
        self.assertEqual(doc["observed_state"], "UNKNOWN")
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIsNone(doc["observed_model"])

    def test_live_inventory_menu_is_read_only(self):
        fake = manifest_from_observation(self.inv)
        with patch("wizard.menus.operations.service.inspect_service", return_value=fake), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wizard.main(["service", "manager", "inventory", "--json"])
        self.assertEqual(rc, 0)
        actual = json.loads(output.getvalue())
        self.assertEqual(actual["observed_model"], "flash-next")
        self.assertFalse(actual["executed"])

    def test_live_inspector_passes_observation_without_mutation(self):
        fake = lambda **kwargs: self.inv
        doc = inspect_service(inspector=fake)
        self.assertEqual(doc["observed_model"], "flash-next")


if __name__ == "__main__":
    unittest.main()
