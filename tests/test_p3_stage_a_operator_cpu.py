"""CPU-only fake DGX regressions for D-016 P3-A operator wrapper."""
from __future__ import annotations

from datetime import datetime, timezone
import contextlib
import io
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.temporary import p3_stage_a_operator as op

IMAGE = "sha256:" + "9" * 64
PLAN = "a" * 64
SOURCE_ID = "b" * 64
P2_HASH = "c" * 64


def p1():
    return {
        "schema_version": 1, "stage": "P1_PRE_A_EVIDENCE_RECONCILIATION",
        "status": "PRE_A_P1_REVIEW_READY", "issues": [],
        "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "current_model": "flash-next", "current_model_image": IMAGE,
        "git_head": "d" * 40,
        "current_rc3": {"rc3_expected": True, "check_count": 2,
                        "status": "EXPECTED_ACTIVE_FLASH_COLLISION"},
        "historical_rc3": {"rc3_expected": True, "check_count": 2,
                           "status": "EXPECTED_ACTIVE_FLASH_COLLISION"},
        "p1_verify": {"status": "PASS"},
        "p1_benchmark": {"status": "PASS", "sample_count": 3,
                         "metrics": {"ttft_p50_sec": 1.398707,
                                     "latency_p50_sec": 1.687357,
                                     "mean_tokens_per_sec": 38.2968}},
        "p3_a_executed": False,
        "post_p3_b_p1_rebenchmark_required": True,
    }


def live(source=True):
    return {
        "status": "LIVE_SERVICE_VERIFIED",
        "observed_model": "flash-next" if source else "27b",
        "expected_served_id": op.SOURCE_ID if source else op.TARGET_ID,
        "observed_model_ids": [op.SOURCE_ID if source else op.TARGET_ID],
        "host_port": 8000,
        "issues": [],
        "active_container": {
            "name": op.SOURCE_NAME if source else op.TARGET_NAME,
            "image_id": IMAGE},
    }


def plan():
    return {
        "status": "READY_TO_REQUEST_TRANSITION_APPROVAL",
        "stage": "a", "source_model": "flash-next", "target_model": "27b",
        "issues": [], "executed": False, "operations_enabled": False,
        "approval_accepted": False, "source_image": IMAGE,
        "flash_image": IMAGE, "target_image": IMAGE,
        "source_container_id": SOURCE_ID, "target_container_id": None,
        "plan_id": PLAN, "p2_receipt_sha256": P2_HASH,
        "expires_at_epoch_seconds": 1000120,
        "required_downtime_acknowledgement": op.DOWNTIME_ACK,
        "required_p3_entry_acknowledgement": op.P3_ENTRY_ACK,
    }


class P3StageAOperatorCPU(unittest.TestCase):
    def test_pre_a_p1_receipt_pass_does_not_authorize_automatic_execute(self):
        self.assertEqual(op.p1_evidence_issues(p1()), [])

    def test_pre_a_stale_and_nonpass_block(self):
        x = p1()
        x["status"] = "BLOCKED"
        x["issues"] = ["P1_ASSET_AUDIT_NOT_READY"]
        self.assertIn("P1_PRE_A_RECEIPT_NOT_QUALIFIED", op.p1_evidence_issues(x))

    def test_pre_a_missing_benchmark_or_rc3_blocks(self):
        x = p1()
        x["p1_benchmark"]["metrics"]["mean_tokens_per_sec"] = None
        x["current_rc3"]["status"] = "BLOCKED"
        codes = op.p1_evidence_issues(x)
        self.assertIn("P1_NUMERIC_BENCHMARK_NOT_ACCEPTED", codes)
        self.assertIn("P1_PRE_A_RAW_RC3_NOT_REVIEWED", codes)

    def test_valid_plan_and_verified_flash_accepted_as_preview_only(self):
        self.assertEqual(op.plan_issues(plan(), p1(), live(),
                                        now_epoch=1000000), [])

    def test_expired_plan_does_not_qualify(self):
        self.assertIn("P3_A_PLAN_EXPIRED_OR_EXPIRING",
                      op.plan_issues(plan(), p1(), live(),
                                     now_epoch=1000106))

    def test_wrong_service_or_image_blocks(self):
        original = live()
        original["observed_model"] = "27b"
        self.assertIn("P3_A_CURRENT_FLASH_SERVICE_NOT_VERIFIED",
                      op.plan_issues(plan(), p1(), original,
                                     now_epoch=1000000))
        wrong = plan()
        wrong["source_image"] = "sha256:" + "f" * 64
        self.assertIn("P3_A_PLAN_SOURCE_OR_TARGET_CHANGED",
                      op.plan_issues(wrong, p1(), live(), now_epoch=1000000))

    def test_missing_provenance_and_source_id_block(self):
        p = plan()
        p["p2_receipt_sha256"] = None
        p["source_container_id"] = None
        p["target_image"] = "unqualified"
        issues = op.plan_issues(p, p1(), live(), now_epoch=1000000)
        self.assertIn("P3_A_CURRENT_FLASH_CONTAINER_NOT_PINNED", issues)
        self.assertIn("P3_A_TARGET_IMAGE_OR_P2_PROVENANCE_NOT_PINNED", issues)

    def test_manual_prompts_reject_wrong_or_missing_confirmation(self):
        self.assertFalse(op.prompts(plan(), input_fn=lambda _: ""))
        answers = iter([PLAN, op.DOWNTIME_ACK, "NOT_THE_P3_ACK"])
        self.assertFalse(op.prompts(plan(), input_fn=lambda _: next(answers)))
        answers = iter([PLAN, op.DOWNTIME_ACK, op.P3_ENTRY_ACK])
        self.assertTrue(op.prompts(plan(), input_fn=lambda _: next(answers)))

    def test_prompt_shows_every_exact_character_not_just_an_abstract_label(self):
        labels = []
        answers = iter([PLAN, op.DOWNTIME_ACK, op.P3_ENTRY_ACK])
        def answer(label):
            labels.append(label)
            return next(answers)
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertTrue(op.prompts(plan(), input_fn=answer))
        self.assertEqual(len(labels), 3)
        for literal in (PLAN, op.DOWNTIME_ACK, op.P3_ENTRY_ACK):
            self.assertIn(literal, output.getvalue())
            self.assertTrue(any(literal in item for item in labels))
        self.assertIn("KST", output.getvalue())

    def test_post_execution_api_identity_must_match_27b(self):
        self.assertTrue(op.summarize_runtime(live(source=False), plan()))
        wrong = live(source=False)
        wrong["observed_model_ids"] = ["qwen3.8-flash-next"]
        self.assertFalse(op.summarize_runtime(wrong, plan()))

    def _invoke(self, *, execute=False, ready=True, tty=False,
                confirmations=False, execute_pass=True, seconds_left=300,
                rotate_after_confirmation=False, wizard_refuses_stale=False):
        calls = []
        now = datetime.now(timezone.utc)
        plan_count = 0
        def fake_run(argv, **kwargs):
            calls.append(list(argv))
            if argv[:4] == ["./wizard.sh", "service", "manager", "status"]:
                return 0, live(source=False) if any("--execute" in c for c in calls) and execute_pass else live()
            if "--plan" in argv:
                nonlocal plan_count
                plan_count += 1
                p = plan()
                p["expires_at_epoch_seconds"] = int(now.timestamp()) + seconds_left
                if rotate_after_confirmation and plan_count >= 2:
                    p["plan_id"] = "f" * 64
                return 0, p if ready else {**p, "status": "BLOCKED", "issues": ["TARGET_ALREADY_EXISTS"]}
            if "--execute" in argv:
                if wizard_refuses_stale:
                    return 3, {"status": "BLOCKED", "stage": "a",
                               "executed": False,
                               "issues": ["P3_STALE_PLAN_OR_CHANGED_PREFLIGHT"]}
                return (0, {"status": "PASS", "stage": "a", "executed": True,
                            "active_model": "27b", "live_verified": True}) if execute_pass else (
                    4, {"status": "RECOVERY_FAILED", "executed": True,
                        "issues": ["SOURCE_NOT_RESTORED"]})
            raise AssertionError("Unexpected command " + repr(argv))
        reports = []
        def fake_persist(data, **kwargs):
            reports.append(dict(data))
            return "/private/report.json"
        with patch.object(op, "latest_p1_receipt", return_value=Path("/fake/p1.json")), \
             patch.object(op, "private_json", return_value=p1()), \
             patch.object(op, "git_clean", return_value=True), \
             patch.object(op, "run_readonly", side_effect=fake_run), \
             patch.object(op, "prompts", return_value=confirmations), \
             patch.object(op, "persist", side_effect=fake_persist), \
             patch.object(op.sys.stdin, "isatty", return_value=tty), \
             contextlib.redirect_stdout(io.StringIO()):
            rc = op.main(["--execute"] if execute else ["--plan"])
        return rc, calls, reports

    def test_plan_by_default_never_executes_anything(self):
        rc, calls, reports = self._invoke()
        self.assertEqual(rc, 0)
        self.assertFalse(any("--execute" in c for c in calls))
        self.assertEqual(reports[-1]["status"], "READY_TO_REQUEST_OPERATOR_INPUT")
        self.assertFalse(reports[-1]["operations_enabled"])

    def test_blocked_plan_cannot_be_bypassed(self):
        rc, calls, reports = self._invoke(execute=True, ready=False, tty=True,
                                          confirmations=True)
        self.assertEqual(rc, 3)
        self.assertFalse(any("--execute" in c for c in calls))
        self.assertIn("P3_A_FRESH_PLAN_NOT_READY", reports[-1]["issues"])

    def test_execute_requires_real_tty_and_separate_prompts(self):
        rc, calls, reports = self._invoke(execute=True, tty=False, confirmations=True)
        self.assertEqual(rc, 3)
        self.assertFalse(any("--execute" in c for c in calls))
        self.assertIn("P3_A_INTERACTIVE_TTY_REQUIRED", reports[-1]["issues"])
        rc, calls, reports = self._invoke(execute=True, tty=True, confirmations=False)
        self.assertEqual(rc, 3)
        self.assertFalse(any("--execute" in c for c in calls))

    def test_execute_only_canonical_wizard_and_independent_postcheck(self):
        rc, calls, reports = self._invoke(execute=True, tty=True, confirmations=True)
        self.assertEqual(rc, 0, reports)
        executions = [c for c in calls if "--execute" in c]
        self.assertEqual(len(executions), 1)
        self.assertEqual(executions[0][:4], ["./wizard.sh", "switch",
                                              "flash-next-27b", "stage-a"])
        self.assertEqual(executions[0][executions[0].index("--approve-plan")+1], PLAN)
        self.assertIn(op.DOWNTIME_ACK, executions[0])
        self.assertIn(op.P3_ENTRY_ACK, executions[0])
        self.assertEqual(reports[-1]["status"], "P3_A_PASS_27B_ACTIVE")
        self.assertFalse(any("stage-b" in c for c in calls))

    def test_not_enough_manual_approval_time_stops_before_prompt(self):
        rc, calls, reports = self._invoke(execute=True, tty=True,
                                          confirmations=True, seconds_left=40)
        self.assertEqual(rc, 3)
        self.assertFalse(any("--execute" in c for c in calls))
        self.assertIn("P3_A_NOT_ENOUGH_TIME_FOR_MANUAL_CONFIRMATIONS",
                      reports[-1]["issues"])

    def test_changed_plan_after_typing_is_not_auto_substituted(self):
        rc, calls, reports = self._invoke(
            execute=True, tty=True, confirmations=True,
            rotate_after_confirmation=True)
        self.assertEqual(rc, 3)
        self.assertFalse(any("--execute" in c for c in calls))
        self.assertIn("P3_A_PLAN_EXPIRED_OR_CHANGED_DURING_OPERATOR_INPUT",
                      reports[-1]["issues"])

    def test_stale_plan_refusal_in_wizard_is_blocked_not_recovery_failed(self):
        rc, calls, reports = self._invoke(
            execute=True, tty=True, confirmations=True,
            wizard_refuses_stale=True)
        self.assertEqual(rc, 3)
        self.assertEqual(reports[-1]["status"], "BLOCKED")
        self.assertFalse(reports[-1]["executed"])
        self.assertIn("P3_A_WIZARD_REJECTED_STALE_OR_CHANGED_PLAN",
                      reports[-1]["issues"])
        self.assertEqual(len([c for c in calls if "--execute" in c]), 1)

    def test_execute_failed_recovery_does_not_auto_retry(self):
        rc, calls, reports = self._invoke(execute=True, tty=True, confirmations=True,
                                          execute_pass=False)
        self.assertEqual(rc, 4)
        self.assertEqual(reports[-1]["status"], "OPERATOR_REVIEW_REQUIRED")
        self.assertEqual(len([c for c in calls if "--execute" in c]), 1)

    def test_symlinked_report_directory_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            actual = Path(tmp) / "actual"
            actual.mkdir()
            shortcut = Path(tmp) / "shortcut"
            shortcut.symlink_to(actual, target_is_directory=True)
            with self.assertRaises(ValueError):
                op.persist({"status": "BLOCKED"}, root=shortcut)

    def test_local_private_report_is_0600_and_no_repo_cache_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "p3"
            file = op.persist({"status": "BLOCKED"}, root=root)
            self.assertEqual(Path(file).stat().st_mode & 0o777, 0o600)
            self.assertFalse(Path(file).is_relative_to(op.ROOT))
            self.assertEqual(root.stat().st_mode & 0o777, 0o700)


if __name__ == "__main__":
    unittest.main()
