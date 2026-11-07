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
            live=self.tx.live,
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

    def test_public_cli_execute_denied_without_any_preflight(self):
        with patch.object(wiz, "make_plan") as planner, contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wiz.main(["--target", "flash-next", "--execute",
                           "--approve-plan", "a" * 64,
                           "--ack-downtime", exe.ACK_DOWNTIME])
        self.assertEqual(rc, 3)
        self.assertIn("RELEASE_GATED", output.getvalue())
        planner.assert_not_called()

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
