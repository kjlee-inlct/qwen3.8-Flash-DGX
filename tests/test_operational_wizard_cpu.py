"""Offline model-first guided ordinary switch; NEVER connects to actual DGX."""
from __future__ import annotations

import contextlib
import io
from unittest import TestCase
from unittest.mock import patch

from scripts.manager import operational_executor as exe
from scripts.manager import operational_wizard as wiz
import test_operational_executor_cpu as fake_module


class GuidedOperatingWizardCPU(TestCase):
    def setUp(self):
        self.tx = fake_module.FakeOperatingTransactionCPU("test_27b_to_flash_success_and_no_p3_receipt_mutation")
        self.tx.setUp()
        self.lines = []
        self.prompts = []

    def tearDown(self):
        self.tx.tearDown()

    def preview(self, target):
        return self.tx.planner(target, root=self.tx.fake.ops)

    def fake_executor(self, target, sha, ack_downtime, ack_target):
        self.assertEqual(ack_downtime, exe.ACK_DOWNTIME)
        self.assertEqual(ack_target, exe.ACK_TARGET[target])
        return exe.execute(
            target, sha, ack_downtime, ack_target,
            root=self.tx.fake.ops,
            planner=self.tx.planner, run=self.tx.runner,
            inspect=lambda name: self.tx.fake.docs[name],
            waiter=lambda name, model, timeout, run: True,
            live=self.tx.live, inference=lambda model: True,
        )

    def guided(self, target="flash-next", *, release=False, answers=(), tty=True,
               executor=None):
        it = iter(answers)
        def prompt(message):
            self.prompts.append(message)
            return next(it)
        return wiz.guided(
            target, planner=self.preview,
            executor=self.fake_executor if executor is None else executor,
            input_fn=prompt, emit=self.lines.append,
            release_qualified=release,
            is_tty=lambda: tty,
            clock=lambda: 1000.0,
        )

    def token(self, target="flash-next"):
        return exe.execution_plan_id(self.preview(target))

    def test_production_gate_blocks_even_when_fixture_is_ready(self):
        with patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", False):
            self.assertEqual(self.guided(release=True), 3)
        self.assertTrue(any("RELEASE_GATED" in x for x in self.lines))
        self.assertFalse(self.prompts)
        self.assertEqual(self.tx.active(), "27b")
        self.assertFalse(any(c[:2] == ["docker", "stop"] for c in self.tx.commands))

    def test_no_model_is_ever_auto_started_from_preview(self):
        self.assertEqual(self.guided(), 3)
        self.assertIn("NOT executable", " ".join(self.lines))
        self.assertFalse(any(c[:2] == ["docker", "stop"] for c in self.tx.commands))

    def test_invalid_target_blocks_without_dgx_preflight(self):
        with patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", True):
            self.assertEqual(self.guided("orcarouter", release=True), 3)
        self.assertEqual(self.tx.commands, [])

    def test_approval_missing_or_wrong_cancels_before_backend(self):
        token = self.token()
        for answers in ((("",)), ((token, "wrong")), ((token, exe.ACK_DOWNTIME, "wrong"))):
            self.lines.clear()
            self.prompts.clear()
            self.tx.commands.clear()
            with self.subTest(answers=answers), patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", True):
                self.assertEqual(self.guided(release=True, answers=answers), 0)
            self.assertEqual(self.tx.active(), "27b")
            self.assertFalse(any(c[:2] == ["docker", "stop"] for c in self.tx.commands))
            self.assertTrue(any("CANCELLED" in x for x in self.lines))

    def test_non_tty_blocks_even_if_test_gate_enabled(self):
        with patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", True):
            self.assertEqual(self.guided(release=True, tty=False), 3)
        self.assertFalse(self.prompts)

    def test_fake_backend_27b_to_flash_guided_path_pass(self):
        token = self.token()
        answers = (token, exe.ACK_DOWNTIME, exe.ACK_TARGET["flash-next"])
        with patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", True):
            rc = self.guided(release=True, answers=answers)
        self.assertEqual(rc, 0)
        self.assertEqual(self.tx.active(), "flash-next")
        self.assertTrue(any("Operating result: PASS" in x for x in self.lines))
        self.assertEqual(len(self.prompts), 3)
        self.assertFalse(any(c[:2] == ["docker", "rm"] for c in self.tx.commands))

    def test_fake_backend_flash_to_27b_guided_path_pass(self):
        from scripts.manager import p3_persistent_switch as p3
        self.tx.fake.docs[p3.NAMES["flash-next"]]["State"]["Running"] = True
        self.tx.fake.docs[p3.NAMES["27b"]]["State"]["Running"] = False
        token = self.token("27b")
        with patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", True):
            rc = self.guided("27b", release=True, answers=(
                token, exe.ACK_DOWNTIME, exe.ACK_TARGET["27b"]))
        self.assertEqual(rc, 0)
        self.assertEqual(self.tx.active(), "27b")

    def test_stale_plan_at_backend_blocks_after_exact_prompt(self):
        token = self.token()
        def changing_executor(target, sha, ack1, ack2):
            def drifted(target, *, root):
                doc = self.tx.planner(target, root=root)
                doc["plan_id"] = "0" * 64
                return doc
            return exe.execute(target, sha, ack1, ack2,
                               root=self.tx.fake.ops, planner=drifted,
                               run=self.tx.runner,
                               inspect=lambda name: self.tx.fake.docs[name],
                               live=self.tx.live)
        with patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", True):
            rc = self.guided(release=True, executor=changing_executor,
                             answers=(token, exe.ACK_DOWNTIME,
                                      exe.ACK_TARGET["flash-next"]))
        self.assertEqual(rc, 3)
        self.assertEqual(self.tx.active(), "27b")
        self.assertFalse(any(c[:2] == ["docker", "stop"] for c in self.tx.commands))

    def test_review_only_returns_ready_without_executing_backend(self):
        with patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", False):
            rc = wiz.guided("flash-next", planner=self.preview,
                            executor=lambda *args: self.fail("must not execute"),
                            emit=self.lines.append, review_only=True,
                            clock=lambda: 1000.0)
        self.assertEqual(rc, 0)
        self.assertTrue(any("REVIEW_ONLY" in x for x in self.lines))

    def test_expiring_window_blocks_before_approvals_and_no_downtime(self):
        with patch.object(wiz, "PRODUCTION_EXECUTION_RELEASED", True):
            rc = wiz.guided("flash-next", planner=self.preview,
                            executor=lambda *args: self.fail("must not execute"),
                            input_fn=lambda prompt: self.fail("no approval prompt"),
                            emit=self.lines.append, release_qualified=True,
                            clock=lambda: 1185.0,
                            is_tty=lambda: True)
        self.assertEqual(rc, 3)
        self.assertTrue(any("less than 120" in x for x in self.lines))
        self.assertEqual(self.tx.active(), "27b")

    def test_public_cli_preview_always_avoids_executor(self):
        with patch.object(wiz, "guided", return_value=0) as guided:
            rc = wiz.main(["--target", "flash-next"])
        self.assertEqual(rc, 0)
        guided.assert_called_once_with("flash-next", review_only=True)

    def test_public_cli_execute_denied_without_any_preflight(self):
        with patch.object(wiz, "make_plan") as planner, contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wiz.main(["--target", "flash-next", "--execute",
                           "--approve-plan", "a" * 64,
                           "--ack-downtime", exe.ACK_DOWNTIME])
        self.assertEqual(rc, 3)
        self.assertIn("RELEASE_GATED", output.getvalue())
        planner.assert_not_called()

    def test_main_menu_switch_goes_to_model_first_guided_path(self):
        from wizard import console
        with patch.object(console, "_input", side_effect=["4", "1", "0"]), \
             patch("scripts.manager.service_manifest.inspect_service",
                   return_value={"status": "OBSERVED_UNQUALIFIED",
                                 "observed_model": "27b",
                                 "download_running": False}), \
             patch("scripts.manager.service_status.inspect_live_status",
                   return_value={"status": "LIVE_SERVICE_VERIFIED",
                                 "observed_model": "27b",
                                 "issues": []}), \
             patch.object(console, "_switch_guided") as chosen, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(console.run(), 0)
        chosen.assert_called_once_with("flash-next")
        self.assertIn("Switch active model", output.getvalue())

    def test_main_menu_does_not_switch_to_already_active_model(self):
        from wizard import console
        with patch.object(console, "_input", return_value="2"), \
             patch("scripts.manager.service_status.inspect_live_status",
                   return_value={"status": "LIVE_SERVICE_VERIFIED",
                                 "observed_model": "27b",
                                 "issues": []}), \
             patch.object(console, "_switch_guided") as chosen, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            console._switch_selector()
        chosen.assert_not_called()
        self.assertIn("already active", output.getvalue())

    def test_previewer_cli_route_is_integrated_in_wizard_handler(self):
        from wizard.menus.switching import flash_next_27b
        with patch.object(wiz, "main", return_value=3) as guided:
            rc = flash_next_27b.run([
                "operational", "guided", "--target", "flash-next"])
        self.assertEqual(rc, 3)
        guided.assert_called_once_with(["--target", "flash-next"])


if __name__ == "__main__":
    import unittest
    unittest.main()
