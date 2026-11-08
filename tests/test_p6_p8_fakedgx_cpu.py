"""P6/P8 synthetic tests. Tests have no Docker/API or real transition effects."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import patch

from scripts.manager import p6_p8_fakedgx as p
from wizard.main import main as wizard_main


class P6P8FakeDGXCPU(unittest.TestCase):
    def test_directionality_and_stop_before_start(self):
        for source, target in p.DIRECTIONS:
            with self.subTest(source=source):
                doc = p.simulate(source, target)
                self.assertEqual(doc["status"], "PASS_FAKE_SWITCH")
                self.assertEqual(doc["final_port_owner"], target)
                actions = [row["action"] for row in doc["journal"]]
                self.assertLess(actions.index("stop-source-and-release-port"),
                                actions.index("start-target"))
                self.assertTrue(all(len(row["active_models"]) <= 1
                                    for row in doc["journal"]))
                self.assertTrue(all(row["port_8000_owner"] ==
                                    (row["active_models"][0]
                                     if row["active_models"] else None)
                                    for row in doc["journal"]))
                self.assertFalse(doc["executed"])
                self.assertIsNone(doc["plan_id"])

    def test_faults_restore_source_or_explicitly_fail(self):
        for source, target in p.DIRECTIONS:
            for fault in ("target-start", "target-api"):
                doc = p.simulate(source, target, fault=fault)
                self.assertEqual(doc["status"], "PASS_FAKE_RECOVERY")
                self.assertEqual(doc["final_active_model"], source)
                self.assertEqual(doc["journal"][-1]["phase"], "RESTORED")
            doc = p.simulate(source, target, fault="restore-source")
            self.assertEqual(doc["status"], "FAIL_FAKE_RECOVERY")
            self.assertIsNone(doc["final_active_model"])
            self.assertEqual(doc["journal"][-1]["phase"], "RECOVERY_FAILED")
            self.assertFalse(doc["automatic_real_recovery_verified"])

    def test_preflight_never_enables_trial_even_with_verifiable_api(self):
        live = {"status": "LIVE_P5_TRIAL_API_VERIFIED",
                "observed_model": "orcarouter",
                "expected_served_id": "qwen3.8-flash-next-orca-uncensored-bf16",
                "runtime_role": "DEVELOPMENT_TRIAL",
                "p5_development_trial": True,
                "active_container": {"name": "qwen38-orcarouter-qsa62318-lmhead-v3"},
                "gpu_exclusivity_verified": False,
                "port_process_ownership_verified": False}
        with patch("scripts.manager.p6_p8_fakedgx.inspect_live_status",
                   side_effect=AssertionError("injected live must be used")):
            doc = p.preflight("orcarouter", "27b", live=live)
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIn("ORCAROUTER_MTP0_TRIAL_NOT_PROMOTED", doc["issues"])
        self.assertIn("SOURCE_NOT_CANONICAL_RUNTIME", doc["issues"])
        self.assertEqual(doc["api_port"], 8000)
        self.assertFalse(doc["operations_enabled"])
        self.assertIsNone(doc["plan_id"])

    def test_preflight_reverse_requires_real_model_and_target_qualification(self):
        live = {"status": "LIVE_SERVICE_VERIFIED", "observed_model": "27b",
                "expected_served_id": "qwen3.8-27b", "runtime_role": "CANONICAL",
                "active_container": {"name": "qwen38-27b"},
                "gpu_exclusivity_verified": True,
                "port_process_ownership_verified": True}
        doc = p.preflight("27b", "orcarouter", live=live)
        self.assertIn("ORCAROUTER_CANONICAL_IMAGE_NOT_QUALIFIED", doc["issues"])
        self.assertNotIn("SOURCE_NOT_CANONICAL_RUNTIME", doc["issues"])
        self.assertFalse(doc["approval_accepted"])

    def test_wrong_pair_and_live_identity_block(self):
        with self.assertRaises(ValueError):
            p.simulate("flash-next", "27b")
        with self.assertRaises(ValueError):
            p.simulate("orcarouter", "27b", fault="unknown")
        doc = p.preflight("27b", "orcarouter", live={
            "observed_model": "orcarouter", "status": "BLOCKED"})
        self.assertIn("SOURCE_MODEL_NOT_ACTIVE", doc["issues"])
        self.assertIn("SOURCE_LIVE_API_NOT_VERIFIED", doc["issues"])

    def test_fault_matrix_covers_two_directions_and_expected_failures(self):
        doc = p.fault_matrix()
        self.assertEqual(doc["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")
        self.assertEqual(doc["test_count"], 8)
        self.assertEqual(sum(row["status"] == "FAIL_FAKE_RECOVERY"
                             for row in doc["cases"]), 2)
        self.assertFalse(doc["real_dgx_verified"])
        self.assertFalse(doc["production_released"])

    def test_wizard_p6_routes_only_fake_and_read_only(self):
        with patch("scripts.manager.p6_p8_fakedgx.inspect_live_status",
                   return_value={"status": "BLOCKED", "observed_model": "27b"}):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                rc = wizard_main(["switch", "orcarouter-27b", "preflight",
                                  "--from-model", "27b", "--to-model",
                                  "orcarouter", "--json"])
        self.assertEqual(rc, 3)
        self.assertFalse(json.loads(output.getvalue())["executed"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wizard_main(["switch", "orcarouter-27b", "simulate",
                              "--from-model", "27b", "--to-model",
                              "orcarouter", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["scope"],
                         "IN_MEMORY_FAKE_DGX_ONLY")

    def test_wizard_p8_matrix_does_not_release_or_actuate(self):
        with patch("subprocess.run", side_effect=AssertionError("no Docker")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wizard_main(["operations", "recovery-acceptance",
                              "fault-matrix", "--fake-dgx", "--json"])
        self.assertEqual(rc, 0)
        doc = json.loads(output.getvalue())
        self.assertEqual(doc["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")
        self.assertFalse(doc["operations_enabled"])
        self.assertFalse(doc["production_released"])


if __name__ == "__main__":
    unittest.main()
