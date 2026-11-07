"""Fake-DGX P3-C operator tests; NO Docker/GPU/model/port mutations."""
from __future__ import annotations

import contextlib
import io
import json
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.temporary import p3_stage_c_operator as op

C_PLAN = "a" * 64
A_PLAN = "b" * 64
B_PLAN = "c" * 64
FLASH = "d" * 64
MODEL = "e" * 64
P2_HASH = "f" * 64
IMAGE = "sha256:" + "1" * 64
HASHES = {"verify": "2" * 64, "benchmark": "3" * 64,
          "diagnostics": "4" * 64}
A_TIME = "2026-11-06T07:43:06+00:00"
B_TIME = "2026-11-06T22:31:24.526447+00:00"


def a_receipt():
    return {
        "schema_version": 1, "stage": "a", "status": "PASS",
        "executed": True, "live_verified": True, "plan_id": A_PLAN,
        "source_model": "flash-next", "target_model": "27b",
        "source_id": FLASH, "target_id": MODEL,
        "flash_id": FLASH, "id_27b": MODEL,
        "source_image": IMAGE, "target_image": IMAGE,
        "flash_image": IMAGE, "image_27b": IMAGE,
        "p2_receipt_sha256": P2_HASH, "finished_at_utc": A_TIME,
    }


def b_receipt():
    return {
        "schema_version": 1, "stage": "b", "status": "PASS",
        "executed": True, "live_verified": True, "plan_id": B_PLAN,
        "source_model": "27b", "target_model": "flash-next",
        "source_id": MODEL, "target_id": FLASH,
        "flash_id": FLASH, "id_27b": MODEL,
        "source_image": IMAGE, "target_image": IMAGE,
        "flash_image": IMAGE, "image_27b": IMAGE,
        "p2_receipt_sha256": P2_HASH, "finished_at_utc": B_TIME,
    }


def c_receipt():
    return {
        "schema_version": 1, "stage": "c", "status": "PASS",
        "executed": True, "live_verified": True, "plan_id": C_PLAN,
        "source_model": "flash-next", "target_model": "27b",
        "source_id": FLASH, "target_id": MODEL,
        "p2_receipt_sha256": P2_HASH,
    }


def live(model="flash-next"):
    served = "qwen3.8-flash-next" if model == "flash-next" else "qwen3.8-27b"
    name = "qwen38-flash" if model == "flash-next" else "qwen38-27b"
    return {
        "status": "LIVE_SERVICE_VERIFIED", "observed_model": model,
        "expected_served_id": served, "observed_model_ids": [served],
        "host_port": 8000, "issues": [],
        "active_container": {"name": name, "image_id": IMAGE},
    }


def plan(expiry=None):
    return {
        "schema_version": 1, "status": op.READY,
        "stage": "c", "source_model": "flash-next", "target_model": "27b",
        "issues": [], "executed": False, "operations_enabled": False,
        "approval_accepted": False, "plan_id": C_PLAN,
        "source_container_id": FLASH, "target_container_id": MODEL,
        "source_image": IMAGE, "target_image": IMAGE,
        "flash_id": FLASH, "id_27b": MODEL, "image_27b": IMAGE,
        "p3_a_plan_id": A_PLAN, "p2_receipt_sha256": P2_HASH,
        "required_downtime_acknowledgement": op.DOWNTIME_ACK,
        "required_p3_entry_acknowledgement": None,
        "p1_evidence": {
            "status": "PASS", "issues": [], "evidence_hashes": HASHES,
            "stage_b_finished_at_utc": B_TIME,
        },
        "expires_at_epoch_seconds":
            expiry if expiry is not None else datetime.now(timezone.utc).timestamp() + 300,
    }


class StageCOperatorCPU(unittest.TestCase):
    def test_read_only_ready_with_exact_original_a_b_p1_and_flash_live(self):
        self.assertEqual(op.review(a_receipt(), b_receipt(), live(), plan(),
                                   0, 0, clean=True), [])

    def test_real_shaped_approval_literals_and_no_backend_entry_parameter(self):
        self.assertEqual(op.DOWNTIME_ACK, "I_ACCEPT_FLASH_NEXT_DOWNTIME")
        self.assertEqual(op.C_ENTRY_ACK, "I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C")
        self.assertIsNone(plan()["required_p3_entry_acknowledgement"])

    def test_wrong_a_b_past_identity_fails_closed(self):
        b = b_receipt()
        b["target_id"] = "7" * 64
        self.assertIn("P3_A_B_PRESERVED_CONTAINER_PROVENANCE_DRIFT",
                      op.review(a_receipt(), b, live(), plan(), 0, 0, clean=True))
        b["target_id"] = FLASH
        b["status"] = "FAIL"
        self.assertIn("P3_B_CANONICAL_SUCCESS_RECEIPT_INVALID",
                      op.review(a_receipt(), b, live(), plan(), 0, 0, clean=True))

    def test_foreign_active_api_or_image_blocks(self):
        wrong = live("27b")
        self.assertIn("P3_C_LIVE_FLASH_SOURCE_UNVERIFIED",
                      op.review(a_receipt(), b_receipt(), wrong, plan(),
                                0, 0, clean=True))
        wrong = live()
        wrong["active_container"]["image_id"] = "sha256:" + "9" * 64
        self.assertIn("P3_C_LIVE_FLASH_SOURCE_UNVERIFIED",
                      op.review(a_receipt(), b_receipt(), wrong, plan(),
                                0, 0, clean=True))

    def test_27b_container_or_p2_receipt_change_blocks(self):
        changed = plan()
        changed["target_container_id"] = "9" * 64
        self.assertIn("P3_C_PRESERVED_TARGET_OR_PROVENANCE_DRIFT",
                      op.review(a_receipt(), b_receipt(), live(), changed,
                                0, 0, clean=True))
        changed = plan()
        changed["p2_receipt_sha256"] = "0" * 64
        self.assertIn("P3_C_PRESERVED_TARGET_OR_PROVENANCE_DRIFT",
                      op.review(a_receipt(), b_receipt(), live(), changed,
                                0, 0, clean=True))

    def test_p1_verify_bench_or_doctor_missing_blocks(self):
        for key in ("verify", "benchmark", "diagnostics"):
            with self.subTest(key=key):
                changed = plan()
                changed["p1_evidence"] = dict(changed["p1_evidence"])
                changed["p1_evidence"]["evidence_hashes"] = dict(HASHES)
                changed["p1_evidence"]["evidence_hashes"].pop(key)
                self.assertIn(
                    "P3_C_POST_B_FLASH_VERIFY_BENCH_DIAGNOSTICS_NOT_QUALIFIED",
                    op.review(a_receipt(), b_receipt(), live(), changed,
                              0, 0, clean=True))

    def test_old_or_expired_sha_invalid_and_wrong_git_blocks(self):
        changed = plan()
        changed["plan_id"] = "historical-sha"
        self.assertIn("P3_C_FRESH_PLAN_NOT_READY",
                      op.review(a_receipt(), b_receipt(), live(), changed,
                                0, 0, clean=True))
        self.assertIn("P3_C_PLAN_EXPIRED",
                      op.review(a_receipt(), b_receipt(), live(), plan(1),
                                0, 0, clean=True))
        self.assertIn("P3_C_GIT_BRANCH_OR_WORKTREE_NOT_VERIFIED",
                      op.review(a_receipt(), b_receipt(), live(), plan(),
                                0, 0, clean=False))

    def test_approval_prompts_show_three_exact_literals(self):
        typed = iter([C_PLAN, op.DOWNTIME_ACK, op.C_ENTRY_ACK])
        prompts = []
        def answer(label):
            prompts.append(label)
            return next(typed)
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertTrue(op.confirm(plan(), input_fn=answer))
        for value in (C_PLAN, op.DOWNTIME_ACK, op.C_ENTRY_ACK):
            self.assertIn(value, out.getvalue())
            self.assertTrue(any(value in x for x in prompts))
        self.assertIn("KST", out.getvalue())
        self.assertIn("do not type '[' or ']'", out.getvalue())
        self.assertTrue(all("[" not in label and "]" not in label
                            for label in prompts))

    def test_sha_with_leading_bracket_is_rejected_without_dispatch(self):
        # Regression from actual DGX input: user typed [<sha> after seeing
        # the old bracket-decorated prompt and C was safely cancelled.
        typed = iter(["[" + C_PLAN, op.DOWNTIME_ACK, op.C_ENTRY_ACK])
        self.assertFalse(op.confirm(plan(), input_fn=lambda _: next(typed)))

    def test_wrong_ack_and_cancel_reject(self):
        self.assertFalse(op.confirm(plan(), input_fn=lambda _: ""))
        wrong = iter([C_PLAN, op.DOWNTIME_ACK, "I_SEPARATELY_AUTHORIZE_P3_ENTRY"])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(op.confirm(plan(), input_fn=lambda _: next(wrong)))
        wrong2 = iter([C_PLAN, "I_ACCEPT_27B_DOWNTIME", op.C_ENTRY_ACK])
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertFalse(op.confirm(plan(), input_fn=lambda _: next(wrong2)))

    def test_final_postcheck_checks_live_27b_and_immutable_c_receipt(self):
        self.assertTrue(op.post_status_ok(live("27b"), c_receipt(), plan()))
        changed = c_receipt()
        changed["target_id"] = "9" * 64
        self.assertFalse(op.post_status_ok(live("27b"), changed, plan()))
        wrong = live()
        self.assertFalse(op.post_status_ok(wrong, c_receipt(), plan()))

    def invoke(self, *, execute=False, tty=False, approved=False,
               expire_seconds=300, rotate=False, core_status="PASS",
               post_model="27b", c_ok=True, clean=True):
        pp = plan(datetime.now(timezone.utc).timestamp() + expire_seconds)
        calls, persisted = [], []
        probes = 0
        def get_plan_and_live():
            nonlocal probes
            probes += 1
            value = dict(pp)
            if rotate and probes > 1:
                value["plan_id"] = "8" * 64
            return 0, live(), 0, value

        def read_json(path, root, max_size):
            if path.name == "stage-a.json":
                return a_receipt()
            if path.name == "stage-b.json":
                return b_receipt()
            if path.name == "stage-c.json":
                return c_receipt() if c_ok else {}
            raise AssertionError(str(path))

        def run(cmd, **kw):
            calls.append(cmd)
            if "--execute" in cmd:
                if core_status == "PASS":
                    return 0, {
                        "status": "PASS", "stage": "c", "executed": True,
                        "active_model": "27b", "live_verified": True}
                if core_status == "STALE":
                    return 3, {
                        "status": "BLOCKED", "stage": "c", "executed": False,
                        "issues": ["P3_STALE_PLAN_OR_CHANGED_PREFLIGHT"]}
                return 4, {
                    "status": "RECOVERY_FAILED", "stage": "c", "executed": True,
                    "issues": ["SOURCE_RESTORE_FAILED"]}
            if cmd[:3] == ["./wizard.sh", "service", "manager"]:
                return 0, live(post_model)
            raise AssertionError("unexpected command: " + repr(cmd))

        with patch.object(op, "private_json", side_effect=read_json), \
             patch.object(op, "get_plan_and_live", side_effect=get_plan_and_live), \
             patch.object(op, "git_clean", return_value=clean), \
             patch.object(op, "run_readonly", side_effect=run), \
             patch.object(op, "persist", side_effect=lambda d: persisted.append(dict(d)) or "/ignored/reports.json"), \
             patch.object(op, "confirm", return_value=approved), \
             patch.object(op.sys.stdin, "isatty", return_value=tty), \
             contextlib.redirect_stdout(io.StringIO()):
            rc = op.main(["--execute"] if execute else ["--plan"])
        return rc, calls, persisted, probes

    def test_plan_default_nondisruptive_and_source_only(self):
        rc, calls, reports, probes = self.invoke()
        self.assertEqual(rc, 0)
        self.assertEqual(calls, [])
        self.assertEqual(probes, 1)
        self.assertFalse(reports[-1]["executed"])
        self.assertFalse(reports[-1]["approval_accepted"])
        self.assertEqual(reports[-1]["status"],
                         "READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL")

    def test_execute_requires_tty_and_approved_inputs(self):
        for tty, approved in ((False, False), (True, False)):
            with self.subTest(tty=tty, approved=approved):
                rc, calls, reports, _ = self.invoke(
                    execute=True, tty=tty, approved=approved)
                self.assertEqual(rc, 3)
                self.assertEqual(calls, [])
                self.assertFalse(reports[-1]["execution_dispatched"])

    def test_expiring_plan_blocks_without_prompt_or_mutation(self):
        rc, calls, reports, _ = self.invoke(
            execute=True, tty=True, approved=True, expire_seconds=45)
        self.assertEqual(rc, 3)
        self.assertEqual(calls, [])
        self.assertIn("P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS", reports[-1]["issues"])

    def test_clean_git_required_no_approval_inference(self):
        rc, calls, reports, _ = self.invoke(
            execute=True, tty=True, approved=True, clean=False)
        self.assertEqual(rc, 3)
        self.assertEqual(calls, [])
        self.assertIn("P3_C_GIT_BRANCH_OR_WORKTREE_NOT_VERIFIED", reports[-1]["issues"])

    def test_rotated_sha_fails_before_executor(self):
        rc, calls, reports, probes = self.invoke(
            execute=True, tty=True, approved=True, rotate=True)
        self.assertEqual(rc, 3)
        self.assertEqual(calls, [])
        self.assertEqual(probes, 2)
        self.assertTrue(reports[-1]["approval_accepted"])
        self.assertFalse(reports[-1]["execution_dispatched"])

    def test_fake_success_final_27b_active_and_no_switchback(self):
        rc, calls, reports, probes = self.invoke(
            execute=True, tty=True, approved=True)
        self.assertEqual(rc, 0)
        self.assertEqual(probes, 2)
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][:4], [
            "./wizard.sh", "switch", "flash-next-27b", "stage-c"])
        self.assertIn("--execute", calls[0])
        self.assertIn(C_PLAN, calls[0])
        self.assertIn(op.DOWNTIME_ACK, calls[0])
        self.assertNotIn("--enter-p3", calls[0])
        self.assertFalse(any("stage-a" in " ".join(cmd) or
                             "stage-b" in " ".join(cmd) for cmd in calls))
        self.assertEqual(reports[-1]["status"], "P3_C_PASS_FINAL_27B_ACTIVE")
        self.assertTrue(reports[-1]["executed"])
        self.assertTrue(reports[-1]["approval_accepted"])
        self.assertTrue(reports[-1]["execution_dispatched"])
        self.assertEqual(reports[-1]["post_switch_observed_model"], "27b")

    def test_fake_stale_core_and_recovery_failure_are_not_pass(self):
        for state in ("STALE", "RECOVERY_FAILED"):
            with self.subTest(state=state):
                rc, calls, reports, _ = self.invoke(
                    execute=True, tty=True, approved=True, core_status=state)
                self.assertEqual(rc, 3 if state == "STALE" else 4)
                self.assertEqual(len(calls), 1)
                self.assertNotEqual(reports[-1]["status"],
                                    "P3_C_PASS_FINAL_27B_ACTIVE")

    def test_final_api_mismatch_and_receipt_missing_requires_review(self):
        for opts in ({"post_model": "flash-next"}, {"c_ok": False}):
            with self.subTest(opts=opts):
                rc, calls, reports, _ = self.invoke(
                    execute=True, tty=True, approved=True, **opts)
                self.assertEqual(rc, 4)
                self.assertEqual(reports[-1]["status"], "OPERATOR_REVIEW_REQUIRED")
                self.assertEqual(len(calls), 2)

    def test_project_report_private_append_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            # In production report root is inside ROOT, but here patch both to
            # place test evidence in an isolated temporary repository.
            basedir = Path(tmp)
            reports = basedir / "reports" / "transitions" / "flash-next--to--27b"
            with patch.object(op, "ROOT", basedir):
                f1 = Path(op.persist({"status": "READY"}, root=reports))
                f2 = Path(op.persist({"status": "CANCELLED"}, root=reports))
            self.assertNotEqual(f1, f2)
            self.assertEqual(f1.stat().st_mode & 0o777, 0o600)
            self.assertEqual(f2.stat().st_mode & 0o777, 0o600)
            self.assertEqual((basedir / "reports").stat().st_mode & 0o777, 0o700)
            self.assertEqual(f1.parent.stat().st_mode & 0o777, 0o700)
            self.assertEqual(json.loads(f1.read_text())["status"], "READY")

    def test_report_symlink_untrusted_no_write(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_repo = root / "repo"
            fake_repo.mkdir()
            outside = root / "outside"
            outside.mkdir()
            (fake_repo / "reports").symlink_to(outside, target_is_directory=True)
            report = fake_repo / "reports" / "transitions" / "flash-next--to--27b"
            with patch.object(op, "ROOT", fake_repo):
                with self.assertRaises(ValueError):
                    op.persist({"status": "PASS"}, root=report)
            self.assertEqual(list(outside.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
