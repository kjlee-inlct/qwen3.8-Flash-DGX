"""CPU-only fake-DGX regressions for the short-lived post-download bundle."""
from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.temporary import p1_post_download as flow

PLAN = "b" * 64


class FakeDGX:
    def __init__(self):
        self.events = []
        self.active = False
        self.branch = flow.BRANCH
        self.dirty = False
        self.verify_status = "PASS"
        self.benchmark_status = "PASS"
        self.ready = True

    def __call__(self, argv, **kwargs):
        self.events.append(list(argv))
        if argv[:3] == ["git", "branch", "--show-current"]:
            body = self.branch + "\n"
        elif argv[:3] == ["git", "status", "--porcelain"]:
            body = " M flash\n" if self.dirty else ""
        elif argv[:2] == ["ps", "-eo"]:
            body = ("4321 /usr/bin/bash ./flash setup default\n" if self.active else
                    "9000 bash\n")
        elif "plan" in argv and "--for-action" in argv:
            action = argv[argv.index("--for-action") + 1]
            body = json.dumps({
                "status": "READY_TO_REQUEST_APPROVAL" if self.ready else "BLOCKED",
                "action": action, "plan_id": PLAN,
                "issues": [] if self.ready else ["hybrid_not_ready"],
            })
        elif "--execute" in argv:
            action = argv[3]
            status = self.verify_status if action == "verify" else self.benchmark_status
            body = json.dumps({"status": status, "evidence": "/tmp/mock-evidence.json"})
        elif argv and argv[0] == "curl" and argv[-1].endswith("/v1/models"):
            body = json.dumps({"data": [{"id": "qwen3.8-flash-next"}]})
        else:
            body = "{}" if "--json" in argv else "ok\n"
        return subprocess.CompletedProcess(argv, 0, body, "")


class PostDownloadCPU(unittest.TestCase):
    def test_only_expected_immutable_read_checks(self):
        self.assertEqual(flow.BRANCH, "feature/recipe-wizard-handoff")
        self.assertNotIn("docker rm", str(flow.CHECKS))
        self.assertNotIn("git pull", str(flow.CHECKS))
        self.assertTrue(all(isinstance(x[1], tuple) for x in flow.CHECKS))

    def test_inspection_never_runs_gpu(self):
        fake = FakeDGX()
        data = flow.session(runner=fake, inspect_only=True,
                            approve_verify=None, approve_benchmark=None)
        self.assertTrue(data["preflight"]["runtime_allowed"])
        self.assertFalse(any("--execute" in event for event in fake.events))
        self.assertEqual(data["actions"]["verify"]["status"], "BLOCKED")

    def test_noninteractive_without_plan_approvals_is_safe(self):
        fake = FakeDGX()
        data = flow.session(runner=fake, interactive=False)
        self.assertFalse(any("--execute" in args for args in fake.events))
        self.assertEqual(data["actions"]["benchmark"]["status"], "BLOCKED")

    def test_matching_approval_executes_both_in_order(self):
        fake = FakeDGX()
        data = flow.session(runner=fake, approve_verify=PLAN,
                            approve_benchmark=PLAN)
        self.assertEqual(data["actions"]["verify"]["status"], "PASS")
        self.assertEqual(data["actions"]["benchmark"]["status"], "PASS")
        executions = [x for x in fake.events if "--execute" in x]
        self.assertEqual([x[3] for x in executions], ["verify", "benchmark"])
        self.assertTrue(all("--approve-plan" in x for x in executions))

    def test_scoped_auto_gpu_executes_only_verify_then_benchmark(self):
        fake = FakeDGX()
        data = flow.session(runner=fake, auto_gpu=True)
        self.assertEqual(data["actions"]["verify"]["status"], "PASS")
        self.assertEqual(data["actions"]["benchmark"]["status"], "PASS")
        executed = [c for c in fake.events if "--execute" in c]
        self.assertEqual([x[3] for x in executed], ["verify", "benchmark"])
        self.assertTrue(all(c[c.index("--approve-plan") + 1] == PLAN
                            for c in executed))
        self.assertFalse(any(c[0] == "docker" and
                             any(x in c for x in ("stop", "rm", "run"))
                             for c in fake.events))

    def test_scoped_auto_gpu_never_ignores_wizard_block(self):
        fake = FakeDGX()
        fake.ready = False
        data = flow.session(runner=fake, auto_gpu=True)
        self.assertEqual(data["actions"]["verify"]["status"], "BLOCKED")
        self.assertFalse(any("--execute" in x for x in fake.events))

    def test_scoped_auto_gpu_never_benchmarks_on_verify_failure(self):
        fake = FakeDGX()
        fake.verify_status = "FAIL"
        data = flow.session(runner=fake, auto_gpu=True)
        self.assertEqual(data["actions"]["verify"]["status"], "FAIL")
        self.assertFalse(data["actions"]["benchmark"]["executed"])

    def test_missing_expected_model_id_blocks_auto_gpu(self):
        class WrongModel(FakeDGX):
            def __call__(self, argv, **kwargs):
                out = super().__call__(argv, **kwargs)
                if argv and argv[0] == "curl" and argv[-1].endswith("/v1/models"):
                    out.stdout = json.dumps({"data": [{"id": "other"}]})
                return out
        fake = WrongModel()
        data = flow.session(runner=fake, auto_gpu=True)
        self.assertFalse(data["preflight"]["expected_api_model_present"])
        self.assertFalse(any("--execute" in c for c in fake.events))

    def test_auto_gpu_cannot_be_combined_with_inspect_only(self):
        with self.assertRaises(SystemExit):
            flow.main(["--inspect-only", "--auto-gpu"])

    def test_missing_benchmark_approval_blocks_only_benchmark(self):
        fake = FakeDGX()
        data = flow.session(runner=fake, approve_verify=PLAN)
        self.assertEqual(data["actions"]["verify"]["status"], "PASS")
        self.assertFalse(data["actions"]["benchmark"]["executed"])

    def test_wrong_approval_blocks_everything(self):
        fake = FakeDGX()
        data = flow.session(runner=fake, approve_verify="a" * 64,
                            approve_benchmark=PLAN)
        self.assertFalse(any("--execute" in x for x in fake.events))
        self.assertEqual(data["actions"]["benchmark"]["reason"],
                         "verification_not_passed")

    def test_download_in_progress_blocks_all_gpu(self):
        fake = FakeDGX()
        fake.active = True
        data = flow.session(runner=fake, approve_verify=PLAN,
                            approve_benchmark=PLAN)
        self.assertTrue(data["preflight"]["operator_process"]["blocked"])
        self.assertFalse(any("--execute" in x for x in fake.events))

    def test_wrong_git_branch_blocks_all_gpu(self):
        fake = FakeDGX()
        fake.branch = "main"
        data = flow.session(runner=fake, approve_verify=PLAN,
                            approve_benchmark=PLAN)
        self.assertFalse(data["preflight"]["branch_ok"])
        self.assertFalse(any("--execute" in x for x in fake.events))

    def test_tracked_file_dirty_blocks_all_gpu(self):
        fake = FakeDGX()
        fake.dirty = True
        data = flow.session(runner=fake, approve_verify=PLAN,
                            approve_benchmark=PLAN)
        self.assertFalse(data["preflight"]["tracked_tree_clean"])
        self.assertFalse(any("--execute" in x for x in fake.events))

    def test_blocked_plan_must_not_be_bypassed(self):
        fake = FakeDGX()
        fake.ready = False
        data = flow.session(runner=fake, approve_verify=PLAN,
                            approve_benchmark=PLAN)
        self.assertFalse(any("--execute" in x for x in fake.events))
        self.assertFalse(data["plans"]["verify"]["ready"])

    def test_failed_verification_never_runs_benchmark(self):
        fake = FakeDGX()
        fake.verify_status = "FAIL"
        data = flow.session(runner=fake, approve_verify=PLAN,
                            approve_benchmark=PLAN)
        self.assertEqual(data["actions"]["verify"]["status"], "FAIL")
        self.assertFalse(data["actions"]["benchmark"]["executed"])

    def test_partial_benchmark_not_promoted_to_pass(self):
        fake = FakeDGX()
        fake.benchmark_status = "PARTIAL"
        data = flow.session(runner=fake, approve_verify=PLAN,
                            approve_benchmark=PLAN)
        self.assertEqual(data["actions"]["benchmark"]["status"], "PARTIAL")

    def test_interactive_exact_independent_confirmations(self):
        fake = FakeDGX()
        inputs = iter([PLAN, PLAN])
        data = flow.session(runner=fake, interactive=True,
                            input_fn=lambda _: next(inputs))
        self.assertEqual(data["actions"]["benchmark"]["status"], "PASS")

    def test_no_shell_true_and_bounded_output(self):
        def huge(cmd, **kwargs):
            self.assertFalse(kwargs.get("shell", False))
            self.assertLessEqual(kwargs["timeout"], 1800)
            return subprocess.CompletedProcess(cmd, 0, "X" * 70000, "")
        rec = flow.call(["echo", "test"], runner=huge)
        self.assertEqual(len(rec["stdout"]), 65536)
        self.assertTrue(rec["truncated"])

    def test_api_ids_are_extracted_from_successful_model_probe(self):
        raw = {"data": [{"id": "qwen3.8-flash-next"}, {"id": "another-id"}]}
        checks = {"models": {"returncode": 0, "stdout": json.dumps(raw),
                              "truncated": False}}
        self.assertEqual(flow.api_model_ids(checks), ["qwen3.8-flash-next", "another-id"])
        self.assertEqual(flow.api_model_ids({}), [])
        self.assertEqual(flow.api_model_ids({
            "models": {"returncode": 1, "stdout": json.dumps(raw)}
        }), [])

    def test_inspection_only_has_distinct_reason(self):
        fake = FakeDGX()
        data = flow.session(runner=fake, inspect_only=True)
        self.assertEqual(data["actions"]["verify"]["reason"], "inspection_only")
        self.assertFalse(any("--execute" in cmd for cmd in fake.events))

    def test_optional_diagnostic_missing_never_breaks_report(self):
        self.assertEqual(flow.cache_diagnosis_summary({}),
                         {"status": "UNAVAILABLE"})
        self.assertEqual(flow.cache_diagnosis_summary({
            "cache_diagnosis": {"returncode": 1, "stdout": "", "truncated": False}
        }), {"status": "UNAVAILABLE"})

    def test_diagnostic_result_parses_without_executing(self):
        facts = {"type": "P1_READ_ONLY_CACHE_DIAGNOSIS", "refs": {"main": "a" * 40}}
        check = {"cache_diagnosis": {
            "returncode": 0, "stdout": json.dumps(facts), "truncated": False
        }}
        self.assertEqual(flow.cache_diagnosis_summary(check), facts)

    def test_results_saved_outside_repository(self):
        fake_data = {"preflight": {}, "plans": {}, "actions": {},
                     "checks": {}, "stage": "P1"}
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(flow, "session", return_value=fake_data):
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                rc = flow.main(["--inspect-only", "--report-root", temp])
            self.assertEqual(rc, 0)
            report = list(Path(temp).glob("*/result.json"))
            self.assertEqual(len(report), 1)
            self.assertEqual(json.loads(report[0].read_text())["stage"], "P1")
            self.assertEqual(report[0].stat().st_mode & 0o777, 0o600)

    def test_bad_benchmark_bounds_abort(self):
        with self.assertRaises(SystemExit):
            flow.main(["--inspect-only", "--requests", "100"])

    def test_reports_not_allowed_under_hf_cache(self):
        with tempfile.TemporaryDirectory() as temp, \
             patch.dict(flow.os.environ, {"HF_CACHE": temp}):
            with self.assertRaises(SystemExit):
                flow.main(["--inspect-only", "--report-root",
                           str(Path(temp) / "reports")])

    def test_operator_work_start_after_plan_blocks_execution(self):
        class RacingDGX(FakeDGX):
            def __call__(self, argv, **kwargs):
                result = super().__call__(argv, **kwargs)
                if "plan" in argv and "--for-action" in argv:
                    self.active = True
                return result
        fake = RacingDGX()
        data = flow.session(runner=fake, approve_verify=PLAN,
                            approve_benchmark=PLAN)
        self.assertFalse(any("--execute" in x for x in fake.events))
        self.assertEqual(data["actions"]["verify"]["reason"],
                         "operator_work_started_after_preflight")

    def test_reports_not_allowed_under_git(self):
        with self.assertRaises(SystemExit):
            flow.main(["--inspect-only",
                       "--report-root", str(flow.ROOT / "bad-dir")])


if __name__ == "__main__":
    unittest.main()
