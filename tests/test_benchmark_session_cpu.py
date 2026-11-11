"""P5 session verification must never mistake supplied JSON for real DGX proof."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.manager.benchmark_session import session_plan, session_review
from scripts.manager.generic_operations import model_catalog
from wizard.main import main as wizard_main


class SessionContractCPU(unittest.TestCase):
    def setUp(self):
        model = "27b"
        identity = model_catalog()["models"][model]
        self.model = model
        self.container = "b" * 64
        self.benchmark = {
            "model": model, "session_id": "a" * 32,
            "profile_sha256": "f" * 64,
            "checkpoint": identity["checkpoint"],
            "served_id": identity["served_id"],
            "container_id": self.container,
            "started_utc": "2026-11-09T00:00:02+00:00",
            "ended_utc": "2026-11-09T00:00:08+00:00",
            "started_monotonic_ns": 3_000_000_000,
            "ended_monotonic_ns": 9_000_000_000,
            "requests": 3, "successes": 3, "failures": 0,
            "error_rate": 0.0,
            "metrics": {"ttft_p50_seconds": 0.2,
                        "ttft_p95_seconds": 0.4,
                        "tokens_per_second": 12.5},
        }
        snaps = []
        for stamp, mono in (("2026-11-09T00:00:00+00:00", 1_000_000_000),
                            ("2026-11-09T00:00:10+00:00", 11_000_000_000)):
            snaps.append({
                "model": model, "timestamp_utc": stamp,
                "monotonic_ns": mono,
                "model_identity_verified_by_api": True,
                "docker": {"container": {"id": self.container},
                           "cgroup_v2": {"metrics": {
                               "memory.events": {"oom": 0, "oom_kill": 0}}}},
            })
        self.resource = {
            "model": model, "session_id": self.benchmark["session_id"],
            "profile_sha256": self.benchmark["profile_sha256"],
            "checkpoint": identity["checkpoint"],
            "served_id": identity["served_id"],
            "container_id": self.container, "snapshots": snaps,
        }

    def review(self):
        return session_review(self.model, self.resource, self.benchmark)

    def test_source_contract_pass_never_promotes_live_or_production(self):
        doc = self.review()
        self.assertEqual(doc["status"], "SOURCE_SESSION_CORRELATED_NOT_LIVE_ACCEPTANCE")
        self.assertFalse(doc["benchmark_verified"])
        self.assertFalse(doc["real_dgx_verified"])
        self.assertFalse(doc["production_released"])
        self.assertFalse(doc["executed"])

    def test_plan_never_acts_or_invents_workload(self):
        doc = session_plan("27b")
        self.assertEqual(doc["identity"]["served_id"], self.benchmark["served_id"])
        self.assertEqual(doc["status"], "BLOCKED_WORKLOAD_PROFILE_AND_APPROVAL_REQUIRED")
        self.assertFalse(doc["approval_accepted"])
        self.assertEqual(len(doc["identity_fingerprint"]), 64)
        with self.assertRaises(ValueError):
            session_plan("future-model-without-registry")

    def test_clock_window_must_be_bracketed_in_both_domains(self):
        self.benchmark["started_monotonic_ns"] = 0
        self.assertIn("BENCHMARK_OUTSIDE_RESOURCE_WINDOW", self.review()["issues"])
        self.benchmark["started_monotonic_ns"] = 3_000_000_000
        self.resource["snapshots"][0]["monotonic_ns"] = None
        self.assertIn("SAMPLER_TIMING_UNOBSERVED", self.review()["issues"])
        self.resource["snapshots"][0]["monotonic_ns"] = 12_000_000_000
        self.assertIn("SAMPLER_TIME_NON_MONOTONIC", self.review()["issues"])

    def test_source_id_mutation_and_container_drift_fail_closed(self):
        self.resource["snapshots"][-1]["docker"]["container"]["id"] = "c" * 64
        issues = self.review()["issues"]
        self.assertIn("CONTAINER_IDENTITY_DRIFT_OR_UNOBSERVED", issues)
        self.assertIn("SAMPLE_IDENTITY_DRIFT", issues)
        self.resource["snapshots"][-1]["docker"]["container"]["id"] = self.container
        self.benchmark["served_id"] = "wrong-model"
        self.assertIn("SERVED_ID_IDENTITY_UNBOUND", self.review()["issues"])

    def test_unsafe_or_absent_runtime_provenance_never_counts(self):
        self.resource["snapshots"][-1]["model_identity_verified_by_api"] = False
        self.assertIn("API_IDENTITY_NOT_INDEPENDENTLY_VERIFIED",
                      self.review()["issues"])
        self.resource["snapshots"][-1]["model_identity_verified_by_api"] = True
        self.resource["session_id"] = "different-session"
        self.assertIn("SESSION_ID_UNBOUND", self.review()["issues"])
        self.resource["session_id"] = self.benchmark["session_id"]
        self.resource["profile_sha256"] = "9" * 64
        self.assertIn("WORKLOAD_PROFILE_HASH_UNBOUND", self.review()["issues"])

    def test_metrics_request_accounting_and_oom(self):
        self.benchmark["successes"] = 4
        self.assertIn("REQUEST_COUNTS_INCONSISTENT", self.review()["issues"])
        self.benchmark["successes"] = 2
        self.benchmark["failures"] = 1
        self.assertIn("BENCHMARK_REQUEST_FAILURES", self.review()["issues"])
        self.assertIn("ERROR_RATE_NOT_REPRODUCIBLE", self.review()["issues"])
        self.benchmark["successes"] = 3
        self.benchmark["failures"] = 0
        self.benchmark["metrics"]["ttft_p50_seconds"] = float("nan")
        self.assertIn("BENCHMARK_METRIC_MISSING:ttft_p50_seconds",
                      self.review()["issues"])
        self.benchmark["metrics"]["ttft_p50_seconds"] = 0.2
        self.resource["snapshots"][-1]["docker"]["cgroup_v2"]["metrics"]["memory.events"]["oom"] = 1
        self.assertIn("OOM_UNOBSERVED_OR_DETECTED", self.review()["issues"])

    def test_one_sample_or_missing_samples_fail_closed(self):
        self.resource["snapshots"] = self.resource["snapshots"][:1]
        self.assertEqual(self.review()["status"], "INCOMPLETE_SESSION_EVIDENCE")
        self.assertIn("RESOURCE_SNAPSHOTS_INSUFFICIENT", self.review()["issues"])

    def test_wizard_cli_session_plan_and_review_are_read_only(self):
        with patch("subprocess.run", side_effect=AssertionError("must not touch runtime")), \
             contextlib.redirect_stdout(io.StringIO()) as stdout:
            rc = wizard_main(["operations", "generic", "session-plan",
                              "--model", "27b", "--json"])
        self.assertEqual(rc, 3)
        self.assertFalse(json.loads(stdout.getvalue())["executed"])
        with tempfile.TemporaryDirectory() as temp:
            resource_file = Path(temp) / "resource.json"
            benchmark_file = Path(temp) / "benchmark.json"
            resource_file.write_text(json.dumps(self.resource), encoding="utf-8")
            benchmark_file.write_text(json.dumps(self.benchmark), encoding="utf-8")
            with patch("subprocess.run", side_effect=AssertionError("no runtime")), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = wizard_main([
                    "operations", "generic", "session-review",
                    "--model", "27b",
                    "--session-resource-evidence", str(resource_file),
                    "--session-benchmark-evidence", str(benchmark_file),
                    "--json"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(stdout.getvalue())["status"],
                             "SOURCE_SESSION_CORRELATED_NOT_LIVE_ACCEPTANCE")


if __name__ == "__main__":
    unittest.main()
