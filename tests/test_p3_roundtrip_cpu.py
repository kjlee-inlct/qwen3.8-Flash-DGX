"""CPU-only P3 revised manual sequence and retired legacy runner tests."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
import unittest

from scripts.manager import p3_27b_roundtrip as legacy
from scripts.manager import p3_transition_sequence as p3
from wizard import main as wizard


def good_live():
    return {"status": "LIVE_SERVICE_VERIFIED",
            "observed_model": "flash-next",
            "expected_served_id": "qwen3.8-flash-next", "issues": []}


def good_receipt():
    return {"path": "/private/benchmark.json", "sha256": "4"*64}, None


class P3ManualSequenceCPU(unittest.TestCase):
    def test_no_p2_receipt_blocks_manual_entry(self):
        result = p3.plan(
            receipt_reader=lambda: (None, "P2_BENCHMARK_RECEIPT_NOT_FOUND"),
            service_inspector=good_live)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("P2_BENCHMARK_RECEIPT_NOT_FOUND", result["issues"])
        self.assertFalse(result["automatic_progression_from_p2"])
        self.assertFalse(result["operations_enabled"])
        self.assertIsNone(result["plan_id"])

    def test_after_p2_pass_still_requires_explicit_p3_operator_entry(self):
        result = p3.plan(receipt_reader=good_receipt,
                         service_inspector=good_live)
        self.assertTrue(result["p2_benchmark_receipt_present"])
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("P3_SEPARATE_OPERATOR_ENTRY_REQUIRED", result["issues"])
        self.assertFalse(result["operations_enabled"])
        self.assertFalse(result["automatic_progression_from_p2"])
        self.assertEqual(result["intended_final_model"], "27b")
        self.assertIsNone(result["plan_id"])
        self.assertFalse(result["permanent_switch_executor_ready"])
        self.assertTrue(result["persistent_switch_source_implemented"])
        self.assertFalse(result["persistent_switch_dgx_qualified"])
        self.assertEqual(len(result["stage_plan_commands"]), 3)
        self.assertTrue(all("--plan" in command for command in result["stage_plan_commands"]))
        self.assertIn("not DGX-qualified", result["notice"])

    def test_order_targets_flash_next_p1_remediation_then_final_27b(self):
        result = p3.plan(receipt_reader=good_receipt,
                         service_inspector=good_live)
        actions = [phase["action"] for phase in result["phases"]]
        self.assertEqual(actions, [
            "manually-approve-p3",
            "switch-flash-next-to-27b",
            "switch-27b-to-flash-next",
            "audit-fix-and-benchmark-p1",
            "switch-flash-next-to-27b"])
        self.assertEqual(result["phases"][2]["required_observed_model"], "27b")
        self.assertEqual(result["phases"][3]["required_observed_model"], "flash-next")
        self.assertTrue(result["p1_remediation_and_rebenchmark_required"])
        self.assertIn("TTFT", " ".join(result["p1_open_checks"]))

    def test_only_flash_next_observed_after_p2_is_accepted(self):
        def wrong_model():
            return {**good_live(), "observed_model": "27b",
                    "expected_served_id": "qwen3.8-27b"}
        result = p3.plan(receipt_reader=good_receipt,
                         service_inspector=wrong_model)
        self.assertIn("P2_MUST_RESTORE_FLASH_NEXT_BEFORE_SEPARATE_P3_ENTRY",
                      result["issues"])
        self.assertIn("FLASH_NEXT_API_IDENTITY_NOT_VERIFIED", result["issues"])

    def test_missing_live_api_blocks_even_with_p2_receipt(self):
        result = p3.plan(receipt_reader=good_receipt,
                         service_inspector=lambda: {
                             "status": "BLOCKED", "observed_model": None,
                             "issues": ["API_UNAVAILABLE"]})
        self.assertIn("LIVE_SERVICE_STATE_UNVERIFIED", result["issues"])
        self.assertIn("API_UNAVAILABLE", result["issues"])

    def test_read_only_observation_failure_never_implies_success(self):
        def bad():
            raise OSError("unavailable")
        result = p3.plan(receipt_reader=bad, service_inspector=bad)
        self.assertIn("P2_BENCHMARK_RECEIPT_UNAVAILABLE", result["issues"])
        self.assertIn("LIVE_SERVICE_STATE_UNVERIFIED", result["issues"])

    def test_old_roundtrip_direct_api_never_performs_mutation(self):
        plan = legacy.make_plan(base_planner=lambda:self.fail("no planner"))
        self.assertEqual(plan["status"], "BLOCKED")
        self.assertIsNone(plan["plan_id"])
        self.assertIn("P3_LEGACY_ROUNDTRIP_RETIRED", plan["issues"])
        code, result = legacy.execute("a"*64, "I_ACCEPT_FLASH_NEXT_DOWNTIME",
                                      core=lambda *a,**k:self.fail("no GPU"))
        self.assertEqual(code, 3)
        self.assertFalse(result["executed"])

    def test_legacy_cli_plan_execute_are_both_blocked(self):
        for mode in ("plan", "execute"):
            with self.subTest(mode=mode), contextlib.redirect_stdout(io.StringIO()) as out:
                code = legacy.main([mode, "--approve-plan", "a"*64,
                                    "--ack-downtime", "I_ACCEPT_FLASH_NEXT_DOWNTIME"])
            self.assertEqual(code, 3)
            self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")

    def test_latest_qualifying_p2_benchmark_receipt_remains_read_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            good = {
                "status": "BENCH_PASS_RESTORED_VERIFIED",
                "benchmark": {"status": "PASS",
                              "benchmark_version": "p2-27b-api-benchmark-v1"},
                "restoration": {"status": "RESTORED", "issues": []},
                "post_restore_wizard_status": {
                    "status": "LIVE_SERVICE_VERIFIED",
                    "observed_model": "flash-next",
                    "expected_served_id": "qwen3.8-flash-next",
                    "issues": []},
            }
            path = root / "20261106T110000Z-receipt.benchmark.json"
            path.write_text(json.dumps(good))
            result, issue = legacy.latest_p2_benchmark(root)
            self.assertIsNone(issue)
            self.assertEqual(result["path"], str(path))
            bad = root / "20261106T120000Z-receipt.benchmark.json"
            bad.write_text(json.dumps({**good, "status":"BENCH_PARTIAL_RESTORED"}))
            result, issue = legacy.latest_p2_benchmark(root)
            self.assertIsNone(result)
            self.assertEqual(issue, "P2_BENCHMARK_NOT_QUALIFIED")

    def test_wizard_sequence_route_is_plan_only_and_explicit(self):
        with patch("scripts.manager.p3_transition_sequence.plan", return_value={
                "status": "BLOCKED", "executed": False,
                "operations_enabled": False, "plan_id": None,
                "issues": ["P3_SEPARATE_OPERATOR_ENTRY_REQUIRED"]}) as maker, \
             contextlib.redirect_stdout(io.StringIO()) as out:
            code = wizard.main(["switch", "flash-next-27b",
                                "sequence", "--plan", "--json"])
        self.assertEqual(code, 3)
        self.assertFalse(json.loads(out.getvalue())["executed"])
        maker.assert_called_once()

        for command in (
            ["switch", "flash-next-27b", "sequence", "--execute", "--json"],
            ["switch", "flash-next-27b", "roundtrip", "--execute",
             "--approve-plan", "a"*64, "--json"],
        ):
            with self.subTest(command=command), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                code = wizard.main(command)
            self.assertEqual(code, 3)
            self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
