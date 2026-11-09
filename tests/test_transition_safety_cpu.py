"""Extra P6/P8 fault coverage with no Docker/GPU/network interaction."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import patch

from scripts.manager import transition_safety as t
from scripts.manager.service_manifest import policy
from wizard.main import main as wizard_main


class ExtendedFakeDGXCPU(unittest.TestCase):
    def test_every_model_pair_and_extended_fault_has_expected_result(self):
        doc = t.extended_fault_matrix()
        self.assertEqual(doc["pair_count"], 6)
        self.assertEqual(doc["fault_count"], len(t.FAULTS))
        self.assertEqual(doc["test_count"], 6 * len(t.FAULTS))
        self.assertEqual(doc["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")
        for c in doc["cases"]:
            self.assertEqual(c["status"], t.EXPECTED[c["injected_fault"]])
            self.assertFalse(c["executed"])
            self.assertFalse(c["production_released"])
            self.assertFalse(c["invariant_issues"])
            self.assertLessEqual(len(c["synthetic_mutations"]), 4)

    def test_new_model_is_not_hardcoded(self):
        cfg = json.loads(json.dumps(policy()))
        cfg["models"]["future"] = {
            "checkpoint": "future/checkpoint",
            "container_name": "future-container",
            "served_id": "future-id"}
        doc = t.extended_fault_matrix(config=cfg)
        self.assertEqual(doc["pair_count"], 12)
        self.assertEqual(doc["test_count"], 12 * len(t.FAULTS))
        self.assertEqual(doc["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")

    def test_all_pre_stop_failures_cannot_mutate(self):
        for fault in ("source-stop", "container-drift", "journal-write",
                      "approval-expired", "state-drift", "duplicate-execution"):
            with self.subTest(fault=fault):
                case = t.simulate_transaction("27b", "flash-next", fault=fault)
                self.assertEqual(case["status"], "BLOCKED_FAKE_BEFORE_STOP")
                self.assertEqual(case["synthetic_mutations"], [])
                self.assertEqual(case["final_active_model"], "27b")
                self.assertEqual(case["final_port_owner"], "27b")

    def test_port_release_failure_never_starts_target(self):
        case = t.simulate_transaction("27b", "flash-next", fault="port-release")
        self.assertEqual(case["status"], "FAIL_FAKE_PORT_RELEASE")
        self.assertEqual(case["synthetic_mutations"], ["stop:27b"])
        self.assertEqual(case["final_port_owner"], "27b")
        self.assertIn("PORT_8000_NOT_RELEASED", case["issues"])

    def test_target_errors_recover_only_when_source_restart_succeeds(self):
        for fault in ("target-start", "target-api"):
            case = t.simulate_transaction("27b", "flash-next", fault=fault)
            self.assertEqual(case["status"], "PASS_FAKE_RECOVERY")
            self.assertEqual(case["final_active_model"], "27b")
            self.assertEqual(case["final_port_owner"], "27b")
        case = t.simulate_transaction("27b", "flash-next", fault="restore-source")
        self.assertEqual(case["status"], "FAIL_FAKE_RECOVERY")
        self.assertIsNone(case["final_active_model"])
        self.assertIsNone(case["final_port_owner"])

    def test_duplicate_nonce_rejected_on_second_transaction(self):
        backend = t.InMemoryBackend("27b", "27b")
        first = t.simulate_transaction("27b", "flash-next", backend=backend)
        self.assertEqual(first["status"], "PASS_FAKE_SWITCH")
        # Reconstruct original state without clearing the consumed nonce.
        backend.active = "27b"
        backend.port_owner = "27b"
        recorded = len(backend.mutations)
        second = t.simulate_transaction("27b", "flash-next", backend=backend)
        self.assertEqual(second["status"], "BLOCKED_FAKE_BEFORE_STOP")
        self.assertIn("EXECUTION_NONCE_ALREADY_CONSUMED", second["issues"])
        self.assertEqual(len(backend.mutations), recorded)

    def test_arbitrary_backends_and_unregistered_pairs_refused(self):
        with self.assertRaises(TypeError):
            t.simulate_transaction("27b", "flash-next", backend=object())
        with self.assertRaises(ValueError):
            t.simulate_transaction("27b", "27b")
        with self.assertRaises(ValueError):
            t.simulate_transaction("unknown", "27b")
        with self.assertRaises(ValueError):
            t.simulate_transaction("27b", "flash-next", fault="nonexistent")

    def test_cli_extended_matrix_is_source_only_and_compact(self):
        with patch("subprocess.run", side_effect=AssertionError("no Docker")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc = wizard_main(["operations", "generic", "extended-fault-matrix",
                              "--summary-only", "--json"])
        self.assertEqual(rc, 0)
        doc = json.loads(out.getvalue())
        self.assertEqual(doc["test_count"], 6 * len(t.FAULTS))
        self.assertNotIn("cases", doc)
        self.assertTrue(doc["full_journals_omitted"])
        self.assertFalse(doc["real_dgx_verified"])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = wizard_main(["operations", "generic", "transaction-simulate",
                              "--from-model", "27b", "--to-model", "flash-next",
                              "--extended-fault", "port-release", "--json"])
        self.assertEqual(rc, 3)
        self.assertEqual(json.loads(out.getvalue())["status"], "FAIL_FAKE_PORT_RELEASE")


if __name__ == "__main__":
    unittest.main()
