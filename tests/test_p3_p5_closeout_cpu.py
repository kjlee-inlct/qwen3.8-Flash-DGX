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
    if "p3_dg_acceptance" in cmd:
        status = ("CPU_ONLY_SOURCE_PASS_NOT_DGX" if "--cpu-only" in cmd
                  else "DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED")
        return subprocess.CompletedProcess(cmd, 0, json.dumps({"status": status,
            "production_released": False, "executed": False}), "")
    if "p5_orcarouter" in cmd:
        if "--cpu-only" in cmd:
            return subprocess.CompletedProcess(cmd, 0, '{"status":"PASS","executed":false}', "")
        return subprocess.CompletedProcess(cmd, 3, '{"status":"BLOCKED","executed":false}', "")
    if "p4_bc_dry_run" in cmd:
        return subprocess.CompletedProcess(cmd, 0, '{"status":"READ_ONLY_DRY_RUN_PASS","executed":false}', "")
    if "model_measurements" in cmd:
        return subprocess.CompletedProcess(cmd, 0,
            '{"status":"OBSERVED_PARTIAL","inference_executed":false}', "")
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
            if "p3_dg_acceptance" in cmd:
                return subprocess.CompletedProcess(cmd, 3,
                    '{"status":"BLOCKED","issues":["CPU_REGRESSION_FAILED"]}', "")
            return fake(cmd, **kw)
        out = c.collect("cpu-only", runner=blocked)
        self.assertEqual(out["status"], "INCOMPLETE_OR_BLOCKED")

    def test_readonly_collects_denial_without_calling_it_pass(self):
        out = c.collect("read-only", runner=fake)
        self.assertEqual(out["status"], "READ_ONLY_COLLECTED_NOT_RELEASED")
        self.assertEqual(len(out["tasks"]), 5)
        self.assertTrue(out["tasks"][2]["accepted"])
        self.assertEqual(out["tasks"][2]["returncode"], 3)
        self.assertEqual(out["tasks"][2]["summary"]["status"], "BLOCKED")
        self.assertFalse(out["inference_executed"])
        self.assertFalse(out["operating_journal_written"])

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
