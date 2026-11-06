"""Fake-DGX CPU tests: isolated stage-B exact approval, no automatic downtime."""
from __future__ import annotations

from datetime import datetime, timezone
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.temporary import p3_stage_b_operator as op

SHA = "a" * 64
A_PLAN = "b" * 64
FLASH_CID = "c" * 64
B_CID = "d" * 64
P2_HASH = "e" * 64
IMAGE = "sha256:" + "f" * 64


def a_receipt():
    return {
        "schema_version": 1, "stage": "a", "status": "PASS",
        "executed": True, "live_verified": True,
        "plan_id": A_PLAN, "source_model": "flash-next", "target_model": "27b",
        "source_id": FLASH_CID, "target_id": B_CID,
        "flash_id": FLASH_CID, "id_27b": B_CID,
        "source_image": IMAGE, "target_image": IMAGE,
        "flash_image": IMAGE, "image_27b": IMAGE,
        "p2_receipt_sha256": P2_HASH,
        "finished_at_utc": "2026-11-06T07:43:06+00:00",
    }


def live(source=True):
    name = "27b" if source else "flash-next"
    model_id = "qwen3.8-27b" if source else "qwen3.8-flash-next"
    return {"status": "LIVE_SERVICE_VERIFIED",
            "observed_model": name, "expected_served_id": model_id,
            "observed_model_ids": [model_id], "issues": [],
            "host_port": 8000, "active_container": {
                "name": "qwen38-27b" if source else "qwen38-flash",
                "image_id": IMAGE}}


def plan(expires=None):
    return {
        "status": "READY_TO_REQUEST_TRANSITION_APPROVAL",
        "schema_version": 1, "issues": [],
        "executed": False, "operations_enabled": False,
        "approval_accepted": False,
        "stage": "b", "source_model": "27b", "target_model": "flash-next",
        "plan_id": SHA,
        "expires_at_epoch_seconds": expires if expires is not None else
            datetime.now(timezone.utc).timestamp() + 300,
        "source_container_id": B_CID,
        "target_container_id": FLASH_CID,
        "source_image": IMAGE, "target_image": IMAGE,
        "flash_id": FLASH_CID, "image_27b": IMAGE,
        "p3_a_plan_id": A_PLAN,
        "p2_receipt_sha256": P2_HASH,
        "required_downtime_acknowledgement": op.DOWNTIME_ACK,
        "required_p3_entry_acknowledgement": op.ENTRY_ACK,
    }


class StageBOperatorCPU(unittest.TestCase):
    def test_b_uses_distinct_27b_ack_and_distinct_stage_entry(self):
        self.assertEqual(op.DOWNTIME_ACK, "I_ACCEPT_27B_DOWNTIME")
        self.assertEqual(op.ENTRY_ACK, "I_SEPARATELY_AUTHORIZE_P3_STAGE_B")

    def test_read_only_preflight_is_ready_without_approval(self):
        self.assertEqual(op.review(a_receipt(), live(), plan(),
                                   0, 0, clean=True), [])

    def test_missing_original_receipt_and_foreign_model_block(self):
        issues = op.review({}, live(False), plan(), 0, 0, clean=True)
        self.assertIn("P3_A_SUCCESS_RECEIPT_NOT_QUALIFIED", issues)
        self.assertIn("P3_B_SOURCE_27B_LIVE_MANIFEST_API_UNVERIFIED", issues)

    def test_changed_immutable_flash_id_blocks(self):
        p = plan()
        p["target_container_id"] = "8" * 64
        self.assertIn("P3_B_PRESERVED_CONTAINERS_OR_PROVENANCE_DRIFT",
                      op.review(a_receipt(), live(), p, 0, 0, clean=True))

    def test_old_flash_ack_not_accepted_for_b(self):
        p = plan()
        p["required_downtime_acknowledgement"] = "I_ACCEPT_FLASH_NEXT_DOWNTIME"
        self.assertIn("P3_B_EXPECTED_APPROVAL_STRINGS_CHANGED",
                      op.review(a_receipt(), live(), p, 0, 0, clean=True))

    def test_wrong_git_branch_blocks(self):
        self.assertIn("P3_B_GIT_WORKTREE_NOT_VERIFIED",
                      op.review(a_receipt(), live(), plan(), 0, 0, clean=False))

    def test_all_required_literals_are_displayed_not_just_labels(self):
        inputs = iter([SHA, op.DOWNTIME_ACK, op.ENTRY_ACK])
        labels = []
        def answer(label):
            labels.append(label)
            return next(inputs)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertTrue(op.confirm(plan(), input_fn=answer))
        for value in (SHA, op.DOWNTIME_ACK, op.ENTRY_ACK):
            self.assertIn(value, out.getvalue())
            self.assertTrue(any(value in label for label in labels))
        self.assertIn("KST", out.getvalue())

    def test_manual_cancel_or_wrong_b_entry_blocks(self):
        self.assertFalse(op.confirm(plan(), input_fn=lambda _: ""))
        values = iter([SHA, op.DOWNTIME_ACK, "I_SEPARATELY_AUTHORIZE_P3_ENTRY"])
        self.assertFalse(op.confirm(plan(), input_fn=lambda _: next(values)))

    def test_stage_b_postcheck_requires_restored_flash_identity(self):
        self.assertTrue(op.post_status_ok(live(False), a_receipt()))
        foreign = live(False)
        foreign["observed_model_ids"] = ["qwen3.8-27b"]
        self.assertFalse(op.post_status_ok(foreign, a_receipt()))

    def invoke(self, *, execute=False, tty=False, approved=False,
               seconds=300, rotate=False, core_ok=True):
        calls = []
        report = []
        count = 0
        p = plan(datetime.now(timezone.utc).timestamp() + seconds)
        def get_plan_and_live():
            nonlocal count
            count += 1
            next_plan = dict(p)
            if rotate and count >= 2:
                next_plan["plan_id"] = "9" * 64
            return 0, live(), 0, next_plan
        def run(argv, **kwargs):
            calls.append(argv)
            if "--execute" in argv:
                if core_ok:
                    return 0, {"status": "PASS", "stage": "b", "executed": True,
                               "active_model": "flash-next", "live_verified": True}
                return 4, {"status": "RECOVERY_FAILED", "executed": True,
                           "issues": ["SOURCE_NOT_RESTORED"]}
            if argv[:3] == ["./wizard.sh", "service", "manager"]:
                return 0, live(False)
            raise AssertionError("unexpected command " + repr(argv))
        with patch.object(op, "private_json", return_value=a_receipt()), \
             patch.object(op, "get_plan_and_live", side_effect=get_plan_and_live), \
             patch.object(op, "git_clean", return_value=True), \
             patch.object(op, "run_readonly", side_effect=run), \
             patch.object(op, "persist", side_effect=lambda obj: report.append(dict(obj)) or "/private/receipt.json"), \
             patch.object(op, "confirm", return_value=approved), \
             patch.object(op.sys.stdin, "isatty", return_value=tty), \
             contextlib.redirect_stdout(io.StringIO()):
            rc = op.main(["--execute"] if execute else ["--plan"])
        return rc, calls, report, count

    def test_default_plan_does_not_execute_or_approve(self):
        rc, calls, reports, count = self.invoke()
        self.assertEqual(rc, 0)
        self.assertEqual(count, 1)
        self.assertEqual(calls, [])
        self.assertEqual(reports[-1]["status"], "READY_FOR_SEPARATE_P3_B_OPERATOR_APPROVAL")
        self.assertFalse(reports[-1]["approval_accepted"])

    def test_no_tty_rejects_actual_service_mutation(self):
        rc, calls, reports, _ = self.invoke(execute=True, approved=True, tty=False)
        self.assertEqual(rc, 3)
        self.assertEqual(calls, [])
        self.assertIn("P3_B_OPERATOR_TTY_REQUIRED", reports[-1]["issues"])

    def test_ten_minute_plan_near_expiry_blocks_without_input(self):
        rc, calls, reports, _ = self.invoke(execute=True, approved=True, tty=True, seconds=50)
        self.assertEqual(rc, 3)
        self.assertEqual(calls, [])
        self.assertIn("P3_B_INSUFFICIENT_TIME_FOR_MANUAL_CONFIRMATIONS",
                      reports[-1]["issues"])

    def test_operator_cancel_stops_without_mutation(self):
        rc, calls, reports, _ = self.invoke(execute=True, approved=False, tty=True)
        self.assertEqual(rc, 3)
        self.assertEqual(calls, [])
        self.assertEqual(reports[-1]["status"], "CANCELLED")

    def test_changed_sha_after_manual_input_fails_without_execute(self):
        rc, calls, reports, _ = self.invoke(
            execute=True, approved=True, tty=True, rotate=True)
        self.assertEqual(rc, 3)
        self.assertEqual(calls, [])
        self.assertIn("P3_B_APPROVED_PLAN_EXPIRED_OR_SOURCE_CHANGED",
                      reports[-1]["issues"])
        self.assertTrue(reports[-1]["approval_accepted"])
        self.assertFalse(reports[-1]["execution_dispatched"])
        self.assertFalse(reports[-1]["executed"])

    def test_stage_b_persist_uses_b_specific_prefix_and_preserves_a_prefix(self):
        from scripts.temporary import p3_stage_a_operator as a
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "private-p3"
            for stage, prefix in (("P3_A_OPERATOR_GUARDED_HANDOFF", "p3-a-operator-"),
                                  ("P3_B_OPERATOR_GUARDED_HANDOFF", "p3-b-operator-")):
                path = Path(a.persist({"stage": stage, "status": "BLOCKED"}, root=root))
                self.assertTrue(path.name.startswith(prefix))
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_execute_success_delegates_only_B_and_verifies_flash(self):
        rc, calls, reports, count = self.invoke(
            execute=True, approved=True, tty=True)
        self.assertEqual(rc, 0, reports)
        self.assertEqual(count, 2)
        cmds = [x for x in calls if "--execute" in x]
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0][:4], ["./wizard.sh", "switch", "flash-next-27b", "stage-b"])
        self.assertIn(op.DOWNTIME_ACK, cmds[0])
        self.assertIn(op.ENTRY_ACK, cmds[0])
        self.assertNotIn("stage-c", " ".join(cmds[0]))
        self.assertEqual(reports[-1]["status"], "P3_B_PASS_FLASH_NEXT_ACTIVE")
        self.assertTrue(reports[-1]["approval_accepted"])
        self.assertTrue(reports[-1]["operations_enabled"])
        self.assertTrue(reports[-1]["execution_dispatched"])

    def test_failed_restoration_does_not_retry_or_auto_run_C(self):
        rc, calls, reports, _ = self.invoke(
            execute=True, approved=True, tty=True, core_ok=False)
        self.assertEqual(rc, 4)
        self.assertEqual(reports[-1]["status"], "OPERATOR_REVIEW_REQUIRED")
        self.assertEqual(len([x for x in calls if "--execute" in x]), 1)

    def test_unexpected_cli_execute_without_approval_is_not_a_bypass(self):
        rc, calls, reports, _ = self.invoke(
            execute=True, approved=False, tty=True)
        self.assertEqual(rc, 3)
        self.assertFalse(any("--execute" in x for x in calls))


if __name__ == "__main__":
    unittest.main()
