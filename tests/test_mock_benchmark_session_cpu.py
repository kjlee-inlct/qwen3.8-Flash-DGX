"""P5 synthetic coordinated benchmark/resource collector contract (CPU only)."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import patch

from scripts.manager.mock_benchmark_session import (
    FAULTS, mock_session, mock_session_matrix,
)
from scripts.manager.service_manifest import policy
from wizard.main import main as wizard_main


class MockSessionCPU(unittest.TestCase):
    def test_all_models_have_bound_bracketing_and_no_runtime(self):
        with patch("subprocess.run", side_effect=AssertionError("NO RUNTIME I/O")):
            cases = mock_session_matrix()
        self.assertEqual(cases["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")
        self.assertEqual(cases["test_count"], 3 * len(FAULTS))
        for entry in cases["cases"]:
            self.assertFalse(entry["executed"])
            self.assertFalse(entry["benchmark_verified"])
            self.assertFalse(entry["production_released"])
            self.assertFalse(entry["real_dgx_verified"])
            self.assertEqual(entry["api_port"], 8000)
            self.assertTrue(entry["synthetic"])
            self.assertEqual([e["action"] for e in entry["events"]],
                             ["sample-before", "benchmark-start", "mock-requests",
                              "benchmark-end", "sample-after"])
            if entry["injected_fault"] == "none":
                self.assertEqual(entry["status"], "PASS_FAKE_P5_SESSION")
                self.assertEqual(entry["review"]["issues"], [])
                self.assertEqual(entry["review"]["status"],
                                 "SOURCE_SESSION_CORRELATED_NOT_LIVE_ACCEPTANCE")
            else:
                self.assertEqual(entry["status"], "PASS_FAKE_P5_FAULT_BLOCKED")
                self.assertTrue(entry["review"]["issues"])

    def test_each_fault_reaches_expected_guard(self):
        expected = {
            "sampler-missing": "RESOURCE_SNAPSHOTS_INSUFFICIENT",
            "container-drift": "CONTAINER_IDENTITY_DRIFT_OR_UNOBSERVED",
            "api-identity": "API_IDENTITY_NOT_INDEPENDENTLY_VERIFIED",
            "clock-drift": "BENCHMARK_OUTSIDE_RESOURCE_WINDOW",
            "request-failure": "BENCHMARK_REQUEST_FAILURES",
            "oom": "OOM_UNOBSERVED_OR_DETECTED",
        }
        for fault, issue in expected.items():
            with self.subTest(fault=fault):
                result = mock_session("orcarouter", fault=fault)
                self.assertIn(issue, result["review"]["issues"])

    def test_future_registered_model_requires_no_code_change(self):
        cfg = json.loads(json.dumps(policy()))
        cfg["models"]["future"] = {
            "checkpoint": "future/checkpoint",
            "container_name": "future-container",
            "served_id": "future-id"}
        matrix = mock_session_matrix(config=cfg, summary_only=True)
        self.assertEqual(matrix["test_count"], 4 * len(FAULTS))
        self.assertEqual(matrix["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")
        self.assertNotIn("cases", matrix)

    def test_invalid_model_and_fault_block(self):
        with self.assertRaises(ValueError):
            mock_session("not-registered")
        with self.assertRaises(ValueError):
            mock_session("27b", fault="real-workload")

    def test_cli_mock_session_and_summary_matrix(self):
        with patch("subprocess.run", side_effect=AssertionError("NO RUNTIME I/O")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc = wizard_main(["operations", "generic", "session-mock",
                              "--model", "orcarouter", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out.getvalue())["status"], "PASS_FAKE_P5_SESSION")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = wizard_main(["operations", "generic", "session-matrix",
                              "--summary-only", "--json"])
        self.assertEqual(rc, 0)
        doc = json.loads(out.getvalue())
        self.assertEqual(doc["test_count"], 3 * len(FAULTS))
        self.assertNotIn("cases", doc)
        self.assertFalse(doc["real_dgx_verified"])


if __name__ == "__main__":
    unittest.main()
