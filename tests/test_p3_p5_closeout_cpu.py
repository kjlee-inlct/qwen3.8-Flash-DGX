"""P3-P5 consolidation must not authorize mutating DGX operations."""
import contextlib
import io
import json
import subprocess
import unittest
from unittest.mock import patch

from scripts.manager import p3_p5_closeout as c

SHA = "a" * 40


def fake(cmd, **kwargs):
    if cmd == ["git", "rev-parse", "HEAD"]:
        return subprocess.CompletedProcess(cmd, 0, SHA + "\n", "")
    if cmd == ["git", "status", "--porcelain"]:
        return subprocess.CompletedProcess(cmd, 0, "", "")
    if "-p" in cmd and "unittest" in cmd:
        return subprocess.CompletedProcess(cmd, 0, "", "Ran 4 tests in 0.002s\n\nOK\n")
    if "scripts.manager.p3_dg_acceptance" in cmd:
        status = ("CPU_ONLY_SOURCE_PASS_NOT_DGX" if "--cpu-only" in cmd
                  else "DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED")
        return subprocess.CompletedProcess(cmd, 0, json.dumps({"status": status,
            "production_released": False, "executed": False}), "")
    if "scripts.manager.p5_orcarouter" in cmd:
        if "--cpu-only" in cmd:
            return subprocess.CompletedProcess(cmd, 0, '{"status":"PASS","executed":false}', "")
        return subprocess.CompletedProcess(cmd, 3, '{"status":"BLOCKED","executed":false}', "")
    if "scripts.manager.p4_bc_dry_run" in cmd:
        return subprocess.CompletedProcess(cmd, 0, '{"status":"READ_ONLY_DRY_RUN_PASS","executed":false}', "")
    if "scripts.manager.model_measurements" in cmd:
        status = "PLAN_ONLY_ACK_REQUIRED" if "benchmark-plan" in cmd else "READ_ONLY_PARTIAL"
        return subprocess.CompletedProcess(cmd, 0,
            json.dumps({"status": status, "inference_executed": False}), "")
    raise AssertionError("unexpected subprocess: " + repr(cmd))


class P3P5CloseoutCPU(unittest.TestCase):
    def test_plan_never_runs_a_command(self):
        with patch.object(c.subprocess, "run", side_effect=AssertionError("unexpected")):
            out = c.collect("plan")
        self.assertEqual(out["status"], "PLAN_ONLY")
        self.assertFalse(out["commands_executed"])
        self.assertFalse(out["operations_enabled"])

    def test_cpu_collects_pass_but_never_claims_live_or_ci(self):
        out = c.collect("cpu-only", runner=fake)
        self.assertEqual(out["status"], "CPU_SELECTED_PASS_NOT_CI")
        self.assertEqual(out["source_head"], SHA)
        self.assertEqual(len(out["tasks"]), 6)
        self.assertTrue(all(t["accepted"] for t in out["tasks"]))
        self.assertFalse(out["actual_p3_p4_p5_complete"])
        self.assertFalse(out["ci_verified"])
        self.assertFalse(out["production_released"])

    def test_cpu_fail_closed_for_p3_draft_denial(self):
        def blocked(cmd, **kw):
            if "scripts.manager.p3_dg_acceptance" in cmd:
                return subprocess.CompletedProcess(cmd, 3,
                    '{"status":"BLOCKED","issues":["CPU_REGRESSION_FAILED"]}', "")
            return fake(cmd, **kw)
        out = c.collect("cpu-only", runner=blocked)
        self.assertEqual(out["status"], "INCOMPLETE_OR_BLOCKED")

    def test_readonly_collects_denial_without_calling_it_pass(self):
        out = c.collect("read-only", runner=fake)
        self.assertEqual(out["status"], "READ_ONLY_COLLECTED_WITH_GAPS")
        self.assertEqual(len(out["tasks"]), 5)
        self.assertEqual(out["receipts_collected"], 5)
        self.assertFalse(out["tasks"][3]["accepted"])  # inventory partial is not P5 acceptance
        self.assertTrue(out["tasks"][2]["collected"])
        self.assertFalse(out["tasks"][2]["accepted"])
        self.assertTrue(out["tasks"][2]["expected_non_authorizing_plan"])
        self.assertEqual(out["tasks"][2]["result"], "BLOCKED_RECEIPT")
        self.assertEqual(out["tasks"][2]["returncode"], 3)
        self.assertEqual(out["tasks"][2]["summary"]["status"], "BLOCKED")
        self.assertFalse(out["inference_executed"])
        self.assertFalse(out["operating_journal_written"])

    def test_readonly_real_blockers_have_valid_receipts_not_false_pass(self):
        def blocked(cmd, **kw):
            if "scripts.manager.p3_dg_acceptance" in cmd:
                return subprocess.CompletedProcess(cmd, 3, json.dumps({
                    "status": "BLOCKED", "blocked_stages": ["P3-D", "P3-G"],
                    "stages": {"P3-D": {"status": "BLOCKED", "issues": ["NO_HOST_PID"]},
                               "P3-G": {"status": "BLOCKED", "issues": ["PREVIEW_BLOCKED"]}}
                }), "")
            if "scripts.manager.p4_bc_dry_run" in cmd:
                return subprocess.CompletedProcess(cmd, 3, json.dumps({
                    "status": "READ_ONLY_DRY_RUN_BLOCKED",
                    "candidate_review": {"status": "BLOCKED", "issues": ["P4_A_UNAVAILABLE"]},
                    "cleanup_rehearsal": {"status": "BLOCKED", "issues": []},
                }), "")
            if "scripts.manager.model_measurements" in cmd and "inventory" in cmd:
                return subprocess.CompletedProcess(cmd, 0, json.dumps({
                    "status": "READ_ONLY_PARTIAL", "action": "inventory"}), "")
            return fake(cmd, **kw)
        out = c.collect("read-only", runner=blocked)
        self.assertEqual(out["status"], "READ_ONLY_COLLECTED_WITH_GAPS")
        self.assertEqual(out["receipts_collected"], 5)
        self.assertTrue(out["read_only_all_receipts_collected"])
        for t in out["tasks"][:2]:
            self.assertEqual(t["result"], "BLOCKED_RECEIPT")
            self.assertTrue(t["collected"])
            self.assertFalse(t["accepted"])
        self.assertIn("P3-D", out["tasks"][0]["summary"]["stages"])
        self.assertEqual(out["tasks"][1]["summary"]["candidate_review"]["issues"],
                         ["P4_A_UNAVAILABLE"])
        self.assertFalse(out["production_released"])

    def test_p5_cpu_failure_exposes_structured_parser_diagnostic_without_raw_log(self):
        def failed(cmd, **kw):
            if "scripts.manager.p5_orcarouter" in cmd and "--cpu-only" in cmd:
                return subprocess.CompletedProcess(cmd, 3, json.dumps({
                    "status": "FAIL", "issues": ["P5_CPU_TESTS_FAILED"],
                    "stages": [{"gate": "cpu_fake_dgx", "status": "FAIL",
                                "exit_code": 0, "test_summary": "Ran 91 tests in 1.3s",
                                "test_cases": ([{"case": f"test_ok_{i}", "status": "PASS"}
                                                for i in range(30)] +
                                               [{"case": "test_bad_after_25", "status": "FAIL"}]),
                                "failure_details": "secret private log must never escape"}]}), "")
            return fake(cmd, **kw)
        out = c.collect("cpu-only", runner=failed)
        self.assertEqual(out["status"], "INCOMPLETE_OR_BLOCKED")
        p5 = next(x for x in out["tasks"] if x["task"] == "p5_source_cpu")
        self.assertTrue(p5["collected"])
        self.assertFalse(p5["accepted"])
        self.assertEqual(p5["result"], "BLOCKED_RECEIPT")
        self.assertEqual(p5["summary"]["cpu_suite"]["failed_cases"], ["test_bad_after_25"])
        self.assertEqual(p5["summary"]["cpu_suite"]["parsed_case_count"], 31)
        self.assertTrue(p5["summary"]["cpu_suite"]["failure_detail_available_in_direct_p5_output"])
        self.assertNotIn("secret private", json.dumps(out))

    def test_only_allowlisted_readonly_commands_and_hashes_opt_in(self):
        plain = c.tasks_for("read-only")
        extra = c.tasks_for("read-only", with_p5_asset_hashes=True)
        self.assertEqual(len(extra), len(plain) + 1)
        self.assertEqual(extra[-1]["name"], "p5_asset_hash_read_only")
        for task in c.tasks_for("cpu-only") + extra:
            cmd = task["cmd"]
            self.assertEqual(cmd[:3], [c.PYTHON, "-B", "-m"])
            joined = " ".join(cmd)
            for forbidden in ("benchmark-execute", "--gpu-trial", "--execute",
                              "--approve-plan", "--ack-live-inference",
                              "docker stop", "docker rm", "rm -rf"):
                self.assertNotIn(forbidden, joined)

    def test_dirty_tree_does_not_issue_valid_cpu_receipt(self):
        def dirty(cmd, **kw):
            if cmd == ["git", "status", "--porcelain"]:
                return subprocess.CompletedProcess(cmd, 0, "?? untracked.txt\n", "")
            return fake(cmd, **kw)
        self.assertEqual(c.collect("cpu-only", runner=dirty)["status"],
                         "INCOMPLETE_OR_BLOCKED")

    def test_invalid_json_and_rc_are_not_admitted(self):
        task = c.tasks_for("read-only")[0]
        bad = c._execute(task, runner=lambda cmd, **kw:
                         subprocess.CompletedProcess(cmd, 0, '{"status":"BLOCKED",', ""))
        self.assertFalse(bad["accepted"])
        err = c._execute(task, runner=lambda cmd, **kw:
                         subprocess.CompletedProcess(cmd, 2, '{"status":"PASS"}', ""))
        self.assertFalse(err["accepted"])
        self.assertFalse(err["collected"])

    def test_cli_rejects_unapproved_modes(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                c.main(["--execute"])
        self.assertEqual(ctx.exception.code, 2)
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                c.main(["--plan", "--with-p5-asset-hashes"])
        self.assertEqual(ctx.exception.code, 2)

    def test_bad_mode_cannot_run(self):
        for mode in ("live", "execute", "", "../p5"):
            with self.assertRaises(ValueError):
                c.tasks_for(mode)


if __name__ == "__main__":
    unittest.main()
