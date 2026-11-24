"""CPU-only UX regression: no GPU/API/network calls or service mutations."""
import argparse
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p1_wizard as wiz
from wizard import console


PLAN_ID = "a" * 64


def args(for_action):
    return argparse.Namespace(
        for_action=for_action, cache_root=None, evidence_dir=None,
        requests=3, max_tokens=64, seed=1234)


def plan(action="verify"):
    return {
        "action": action, "status": "READY_TO_REQUEST_APPROVAL",
        "plan_id": PLAN_ID, "parameters": {
            "requests": 3, "max_tokens": 64, "seed": 1234},
        "issues": [],
    }


class OperatorUXCPU(unittest.TestCase):
    def test_new_default_receipts_stay_inside_repository_with_model_name(self):
        path = wiz._evidence_dir(None)
        self.assertEqual(path, wiz.ROOT / "reports" / "models" / wiz.SERVED)
        self.assertNotIn("/p1/", str(path))
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(wiz._evidence_dir(Path(tmp)), Path(tmp))

    def test_exact_plan_id_is_repeated_in_the_p1_input_prompt(self):
        captured = io.StringIO()
        with patch.object(wiz, "build_plan", return_value=plan()), \
             patch.object(wiz, "execute_approved", return_value=(
                 0, {"action": "verify", "status": "PASS",
                     "baseline_status": "PASS", "extended_status": "PASS"}
             )) as perform, \
             patch("builtins.input", return_value=PLAN_ID) as prompt, \
             contextlib.redirect_stdout(captured):
            self.assertEqual(wiz.guided(args("verify")), 0)
        self.assertIn("Type exactly [" + PLAN_ID + "]", prompt.call_args.args[0])
        self.assertIn("Baseline: PASS | Extended: PASS", captured.getvalue())
        self.assertEqual(perform.call_args.args[1], PLAN_ID)
        self.assertEqual(perform.call_count, 1)

    def test_empty_or_wrong_approval_fails_closed(self):
        for response in ("", "wrong", "b" * 64):
            with self.subTest(response=response):
                with patch.object(wiz, "build_plan", return_value=plan()), \
                     patch("builtins.input", return_value=response), \
                     patch.object(wiz, "execute_approved") as execute, \
                     contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(wiz.guided(args("benchmark")), 0)
                execute.assert_not_called()

    def test_blocked_plan_never_requests_approval(self):
        blocked = dict(plan("benchmark"), status="BLOCKED",
                       issues=["running_model_unverified"])
        with patch.object(wiz, "build_plan", return_value=blocked), \
             patch("builtins.input") as prompted, \
             patch.object(wiz, "execute_approved") as execute, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wiz.guided(args("benchmark")), 3)
        prompted.assert_not_called()
        execute.assert_not_called()

    def test_benchmark_result_shows_numerics_and_individual_samples(self):
        result = {"action": "benchmark", "status": "PASS",
                  "evidence": "/project/reports/models/qwen3.8-flash-next/x.json",
                  "benchmark": {
                      "requests": 3, "concurrency": 1,
                      "metrics": {"ttft_p50_sec": 1.3,
                                  "latency_p50_sec": 1.7,
                                  "mean_tokens_per_sec": 38.1,
                                  "total_completion_tokens": 192},
                      "samples": [{"index": 0, "ttft_sec": 1.3,
                                   "latency_sec": 1.7,
                                   "tokens_per_sec": 37.1}]}}
        shown = io.StringIO()
        with contextlib.redirect_stdout(shown):
            wiz._display_result(result)
        for expected in ("TTFT P50", "Mean throughput: 38.1 tokens/s",
                         "request #0", "Evidence: /project/reports"):
            self.assertIn(expected, shown.getvalue())

    def test_unified_menu_does_not_reselect_p1_action(self):
        fake_workflow = {
            "title": "NVIDIA Flash-Next",
            "actions": [{"action": "verify", "status": "GUARDED_P1"}]
        }
        seen = io.StringIO()
        with patch.object(console, "model_workflow", return_value=fake_workflow), \
             patch.object(console, "_input", side_effect=["6", "y", "0"]), \
             patch("wizard.menus.models.flash_next.run", return_value=0) as invoke, \
             contextlib.redirect_stdout(seen):
            console._actions_menu("flash-next")
        invoke.assert_called_once_with(["guided", "--for-action", "verify"])
        self.assertIn("APPROVAL_REQUIRED", seen.getvalue())
        self.assertNotIn("[GUARDED_P1]", seen.getvalue())


if __name__ == "__main__":
    unittest.main()
