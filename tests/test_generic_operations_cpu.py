"""CPU-only tests of all registered-model P5/P6/P7/P8 contracts."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.manager import generic_operations as g
from wizard.main import main as wizard_main


class GenericOperationsCPU(unittest.TestCase):
    def test_catalog_discovers_all_manifest_models_not_hardcoded_pair(self):
        cat = g.model_catalog()
        self.assertEqual(set(cat["models"]), {"flash-next", "27b", "orcarouter"})
        self.assertTrue(cat["models"]["orcarouter"]["served_id_provisional"])
        self.assertEqual(cat["api_port"], 8000)
        self.assertFalse(cat["production_released"])

    def test_future_model_addition_automatically_expands_fault_matrix(self):
        from scripts.manager.service_manifest import policy
        cfg = policy()
        cfg = json.loads(json.dumps(cfg))
        cfg["models"]["future"] = {
            "checkpoint": "example/model",
            "container_name": "example-service",
            "served_id": "example-id"}
        doc = g.fault_matrix(config=cfg)
        self.assertEqual(doc["pair_count"], 12)
        self.assertEqual(doc["test_count"], 48)
        self.assertEqual(doc["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")

    def test_all_pairs_and_failure_modes_obey_exclusivity(self):
        doc = g.fault_matrix()
        self.assertEqual(doc["pair_count"], 6)
        self.assertEqual(doc["test_count"], 24)
        self.assertEqual(doc["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")
        for case in doc["cases"]:
            self.assertFalse(case["invariant_issues"])
            self.assertFalse(case["executed"])
            self.assertIsNone(case["plan_id"])
            self.assertTrue(all(len(item["active_models"]) <= 1 for item in case["journal"]))
            actions = [step["action"] for step in case["journal"]]
            self.assertLess(actions.index("stop-source-and-release-port"),
                            actions.index("start-target") if "start-target" in actions
                            else actions.index("target-start-failed"))
            if case["injected_fault"] == "restore-source":
                self.assertIn("target-api-id-mismatch", actions)
                self.assertEqual(case["status"], "FAIL_FAKE_RECOVERY")

    def test_invalid_pairs_and_identity_fail_closed(self):
        with self.assertRaises(ValueError):
            g.simulate("27b", "27b")
        with self.assertRaises(ValueError):
            g.preflight("not-registered", "27b", live={})
        with self.assertRaises(ValueError):
            g.simulate("27b", "flash-next", fault="other")
        with self.assertRaises(ValueError):
            g.model_catalog({"models": {}, "api": {"host_port": 8000},
                             "max_active_gpu_models": 2})

    def test_preflight_never_executes_even_when_live_evidence_good(self):
        observed = {
            "observed_model": "27b", "status": "LIVE_SERVICE_VERIFIED",
            "expected_served_id": "qwen3.8-27b",
            "active_container": {"name": "qwen38-27b"},
            "gpu_exclusivity_verified": True,
            "port_process_ownership_verified": True}
        doc = g.preflight("27b", "flash-next", live=observed)
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIn("REAL_SWITCH_EXECUTOR_NOT_RELEASED", doc["issues"])
        self.assertNotIn("SOURCE_NOT_CANONICAL_RUNTIME", doc["issues"])
        self.assertFalse(doc["operations_enabled"])
        doc = g.preflight("27b", "orcarouter", live=observed)
        self.assertIn("TARGET_CANONICAL_RUNTIME_NOT_QUALIFIED", doc["issues"])

    def test_resource_review_needs_bound_interval_and_benchmark(self):
        base = g.resource_review("27b", {}, {})
        self.assertIn("RESOURCE_MODEL_IDENTITY_NOT_BOUND", base["issues"])
        self.assertEqual(base["status"], "INCOMPLETE_EVIDENCE")
        first = {
            "model": "27b", "timestamp_utc": "2026-11-09T00:00:00+00:00",
            "docker": {"container": {"id": "a" * 64},
                       "cgroup_v2": {"metrics": {
                           "memory.events": {"oom": 0, "oom_kill": 0}}}}}
        last = {
            "model": "27b", "timestamp_utc": "2026-11-09T00:00:10+00:00",
            "docker": {"container": {"id": "a" * 64},
                       "cgroup_v2": {"metrics": {
                           "memory.events": {"oom": 0, "oom_kill": 0}}}}}
        from scripts.manager.resource_diagnostics import observation_summary
        telemetry = {
            "model": "27b", "snapshots": [first, last],
            "interval_summary": observation_summary([first, last])}
        benchmark = {"model": "27b", "ttft_seconds": 0.25,
                     "tokens_per_second": 11.2}
        result = g.resource_review("27b", telemetry, benchmark)
        self.assertEqual(result["status"], "SOURCE_METRICS_PRESENT_NOT_LIVE_ACCEPTANCE")
        self.assertFalse(result["production_released"])
        last["docker"]["container"]["id"] = "b" * 64
        self.assertIn("RESOURCE_CONTAINER_IDENTITY_NOT_CONTINUOUS",
                      g.resource_review("27b", telemetry, benchmark)["issues"])
        last["docker"]["container"]["id"] = "a" * 64
        last["docker"]["cgroup_v2"]["metrics"]["memory.events"]["oom"] = 1
        self.assertIn("OOM_EVENTS_OBSERVED",
                      g.resource_review("27b", telemetry, benchmark)["issues"])
        last["docker"]["cgroup_v2"]["metrics"]["memory.events"]["oom"] = 0
        benchmark["tokens_per_second"] = float("nan")
        self.assertIn("BENCHMARK_THROUGHPUT_NOT_OBSERVED",
                      g.resource_review("27b", telemetry, benchmark)["issues"])

    def test_integration_requires_four_model_bound_components(self):
        doc = g.integration_review("flash-next", {})
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertEqual(len(doc["issues"]), 4)
        evidence = {
            key: {"status": "PASS", "model": "flash-next", "evidence_id": "sha256:demo"}
            for key in ("service", "proxy", "gateway", "storage")}
        doc = g.integration_review("flash-next", evidence)
        self.assertEqual(doc["status"], "SOURCE_EVIDENCE_COMPLETE_NOT_RUNTIME_ACCEPTANCE")
        self.assertFalse(doc["real_dgx_verified"])
        evidence["gateway"]["model"] = "27b"
        self.assertIn("GATEWAY_MODEL_BOUND_EVIDENCE_MISSING",
                      g.integration_review("flash-next", evidence)["issues"])

    def test_fault_matrix_summary_does_not_change_the_result_or_recovery_counts(self):
        matrix = g.fault_matrix()
        compact = g.fault_matrix_summary(matrix)
        self.assertEqual(compact["status"], matrix["status"])
        self.assertEqual(compact["test_count"], 24)
        self.assertEqual(compact["status_counts"]["PASS_FAKE_SWITCH"], 6)
        self.assertEqual(compact["status_counts"]["PASS_FAKE_RECOVERY"], 12)
        self.assertEqual(compact["status_counts"]["FAIL_FAKE_RECOVERY"], 6)
        self.assertEqual(compact["fault_counts"]["restore-source"], 6)
        self.assertFalse(compact["executed"])
        self.assertNotIn("cases", compact)
        with patch("subprocess.run", side_effect=AssertionError("no live runtime")), \\
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wizard_main(["operations", "generic", "fault-matrix",
                              "--summary-only", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["test_count"], 24)

    def test_cli_routing_is_read_only_and_all_model_matrix(self):
        with patch("subprocess.run", side_effect=AssertionError("no Docker")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc = wizard_main(["operations", "generic", "fault-matrix", "--json"])
        self.assertEqual(rc, 0)
        report = json.loads(out.getvalue())
        self.assertEqual(report["test_count"], 24)
        self.assertFalse(report["executed"])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc = wizard_main(["operations", "generic", "preflight",
                              "--from-model", "27b", "--to-model", "27b", "--json"])
        self.assertEqual(rc, 3)
        self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")

    def test_bounded_evidence_file_read_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "evidence.json"
            file.write_text(json.dumps({"model": "27b"}))
            self.assertEqual(g._load_evidence(str(file)), {"model": "27b"})
            with self.assertRaises(ValueError):
                g._load_evidence("relative/path")
            link = Path(temp) / "link.json"
            link.symlink_to(file)
            with self.assertRaises(ValueError):
                g._load_evidence(str(link))


if __name__ == "__main__":
    unittest.main()
