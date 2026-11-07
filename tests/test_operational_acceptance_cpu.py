"""One-off operating acceptance testing on Fake-DGX only."""
from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from scripts.manager import operational_acceptance as acc
from scripts.manager import operational_executor as exe
from scripts.manager import p3_persistent_switch as p3
import test_operational_executor_cpu as fake_module


class OperatingAcceptanceCPU(unittest.TestCase):
    def setUp(self):
        self.tx = fake_module.FakeOperatingTransactionCPU(
            "test_27b_to_flash_success_and_no_p3_receipt_mutation")
        self.tx.setUp()
        self.outputs = []
        self.inputs = []

    def tearDown(self):
        self.tx.tearDown()

    def planner(self, target):
        return self.tx.planner(target, root=self.tx.fake.ops)

    def executor(self, target, token, ack1, ack2):
        return exe.execute(target, token, ack1, ack2,
                           root=self.tx.fake.ops, planner=self.tx.planner,
                           run=self.tx.runner,
                           inspect=lambda name: self.tx.fake.docs[name],
                           waiter=lambda *args, **kw: True,
                           live=self.tx.live,
                           inference=lambda served: True)

    def try_run(self, target="flash-next", *, answers=(), tty=True,
                planner=None, executor=None, clock=lambda: 1000.0):
        it = iter(answers)
        def enter(prompt):
            self.inputs.append(prompt)
            return next(it)
        return acc.run_trial(
            target, planner=planner or self.planner,
            executor=executor or self.executor, input_fn=enter,
            emit=self.outputs.append, clock=clock,
            is_tty=lambda: tty)

    def good_answers(self, target="flash-next"):
        token = acc.trial_plan(
            target, planner=self.planner,
            clock=lambda: 1000.0)["execution_plan_id"]
        return (acc.ACCEPTANCE_ACK, token, exe.ACK_DOWNTIME,
                exe.ACK_TARGET[target])

    def test_plan_contains_one_off_scope_without_execution(self):
        data = acc.trial_plan("flash-next", planner=self.planner,
                              clock=lambda: 1000.0)
        self.assertEqual(data["status"], "READY_FOR_SEPARATE_TRIAL_APPROVAL")
        self.assertEqual(data["source_model"], "27b")
        self.assertEqual(data["target_model"], "flash-next")
        self.assertEqual(data["seconds_remaining"], 200)
        self.assertEqual(len(data["execution_plan_id"]), 64)
        self.assertFalse(data["executed"])
        self.assertFalse(data["production_release"])
        self.assertFalse(any(c[:2] == ["docker", "stop"] for c in self.tx.commands))

    def test_expiring_window_denies_before_asking(self):
        rc = self.try_run(answers=self.good_answers(), clock=lambda: 1040.0)
        self.assertEqual(rc, 3)
        self.assertFalse(self.inputs)
        self.assertEqual(self.tx.active(), "27b")

    def test_non_tty_denies_before_current_preflight(self):
        with patch.object(acc, "trial_plan") as plan:
            rc = self.try_run(tty=False)
        self.assertEqual(rc, 3)
        plan.assert_not_called()

    def test_any_of_four_missing_or_wrong_approvals_cancels_without_stop(self):
        good = self.good_answers()
        for answers in (("",), good[:1] + ("WRONG",),
                        good[:2] + ("WRONG",),
                        good[:3] + ("WRONG",), good[:2]):
            with self.subTest(answers=answers):
                self.inputs.clear()
                self.outputs.clear()
                rc = self.try_run(answers=answers)
                self.assertEqual(rc, 0)
                self.assertEqual(self.tx.active(), "27b")
                self.assertFalse(any(c[:2] == ["docker", "stop"]
                                     for c in self.tx.commands))
                self.assertTrue(any("CANCELLED" in msg for msg in self.outputs))

    def test_dgx_fake_27b_to_flash_pass_and_no_automatic_return(self):
        rc = self.try_run(answers=self.good_answers())
        self.assertEqual(rc, 0)
        self.assertEqual(self.tx.active(), "flash-next")
        self.assertTrue(any("Live transition result: PASS" in line
                            for line in self.outputs))
        self.assertEqual(len(self.inputs), 4)
        self.assertFalse(any(c[:2] == ["docker", "rm"] for c in self.tx.commands))

    def test_dgx_fake_flash_to_27b_pass(self):
        self.tx.fake.docs[p3.NAMES["flash-next"]]["State"]["Running"] = True
        self.tx.fake.docs[p3.NAMES["27b"]]["State"]["Running"] = False
        rc = self.try_run(target="27b", answers=self.good_answers("27b"))
        self.assertEqual(rc, 0)
        self.assertEqual(self.tx.active(), "27b")

    def test_plan_rotates_after_four_approvals_without_backend_dispatch(self):
        calls = []
        def changing_planner(target):
            doc = self.planner(target)
            calls.append(True)
            if len(calls) > 1:
                doc["plan_id"] = "f" * 64
            return doc
        rc = self.try_run(answers=self.good_answers(),
                          planner=changing_planner,
                          executor=lambda *args: self.fail("no dispatch"))
        self.assertEqual(rc, 3)
        self.assertEqual(self.tx.active(), "27b")
        self.assertFalse(any(c[:2] == ["docker", "stop"] for c in self.tx.commands))

    def test_backend_failure_is_displayed_without_blind_retry(self):
        def blocked(*args):
            return 4, {"status": "RECOVERY_FAILED", "issues": ["TEST_UNCERTAIN"],
                       "active_model": None}
        rc = self.try_run(answers=self.good_answers(), executor=blocked)
        self.assertEqual(rc, 4)
        self.assertIn("  Observed model: UNVERIFIED", self.outputs)
        self.assertTrue(any("NO BLIND RETRY" in item for item in self.outputs))

    def test_unattended_execute_json_is_always_denied(self):
        with patch.object(acc, "run_trial") as backend, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = acc.main(["--target", "flash-next", "--execute", "--json"])
        self.assertEqual(rc, 3)
        self.assertIn("LIVE_ACCEPTANCE_JSON_MODE_FORBIDDEN", output.getvalue())
        backend.assert_not_called()

    def test_cli_router_acceptance_is_a_separate_entrypoint(self):
        from wizard.menus.switching import flash_next_27b
        with patch.object(acc, "main", return_value=3) as wrapper:
            rc = flash_next_27b.run([
                "operational", "acceptance", "--target", "flash-next", "--plan"])
        self.assertEqual(rc, 3)
        wrapper.assert_called_once_with(["--target", "flash-next", "--plan"])


if __name__ == "__main__":
    unittest.main()
