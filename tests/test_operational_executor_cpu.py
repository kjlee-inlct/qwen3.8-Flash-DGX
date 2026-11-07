"""CPU-only simulation of an unreleased recurring-switch transaction.

Exercise via dependency injection only: no user-facing execute route, Docker,
GPU, localhost API or live DGX interaction. Never dispatch P3-A/B/C.
"""
from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.manager import operational_executor as exe
from scripts.manager import operational_switch as op
from scripts.manager import p3_persistent_switch as p3
from scripts.manager.service_journal import read_snapshot
from test_operational_switch_cpu import FakeDGX


class FakeOperatingTransactionCPU(unittest.TestCase):
    def setUp(self):
        self.fake = FakeDGX("test_current_target_does_not_offer_downtime")
        self.fake.setUp()
        self.commands: list[list[str]] = []
        self.fail_start = False
        self.fail_restore = False
        self.fail_wait = False
        self.api_mismatch = False

    def tearDown(self):
        self.fake.tearDown()

    def active(self):
        for model in ("flash-next", "27b"):
            if self.fake.docs[p3.NAMES[model]]["State"]["Running"]:
                return model
        return None

    def live(self):
        model = self.active()
        if model is None:
            return {"status": "BLOCKED", "issues": ["NO_MODEL_ACTIVE"]}
        return {"status": "LIVE_SERVICE_VERIFIED",
                "observed_model": model,
                "expected_served_id": ("wrong-id" if self.api_mismatch
                                       else p3.IDS[model]),
                "issues": []}

    def runner(self, cmd, timeout=35):
        self.commands.append(cmd)
        if cmd[:3] == ["docker", "inspect", "--format"]:
            model_name = cmd[-1]
            return SimpleNamespace(returncode=0,
                                   stdout=str(self.fake.docs[model_name]
                                              ["State"]["Running"]).lower() + "\n")
        if cmd[:2] == ["docker", "stop"]:
            self.fake.docs[cmd[-1]]["State"]["Running"] = False
            return SimpleNamespace(returncode=0, stdout="")
        if cmd[:2] == ["docker", "start"]:
            if self.fail_start or (self.fail_restore and cmd[-1] == p3.NAMES["27b"]):
                return SimpleNamespace(returncode=1, stdout="")
            self.fake.docs[cmd[-1]]["State"]["Running"] = True
            return SimpleNamespace(returncode=0, stdout="")
        if cmd[:3] == ["ss", "-H", "-ltn"]:
            listener = ("LISTEN 0 128 127.0.0.1:8000\n"
                        if self.active() is not None else "")
            return SimpleNamespace(returncode=0, stdout=listener)
        return self.fake.docker_run(cmd, timeout=timeout)

    def planner(self, target, *, root):
        # The same fake observation powers both preflight and executor.
        return op.make_plan(target, live=self.live, run=self.runner,
                            inspect=lambda name: self.fake.docs[name],
                            p3_root=self.fake.p3_root, root=root, now=1000)

    def execute(self, target="flash-next", *, sha=None, ack=True):
        if sha is None:
            sha = self.planner(target, root=self.fake.ops).get("plan_id")
        return exe.execute(
            target, sha, exe.ACK_DOWNTIME if ack else "not approved",
            exe.ACK_TARGET[target], root=self.fake.ops,
            planner=self.planner, run=self.runner,
            inspect=lambda name: self.fake.docs[name],
            waiter=lambda name, model, timeout, run: not self.fail_wait,
            live=self.live,
        )

    def test_27b_to_flash_success_and_no_p3_receipt_mutation(self):
        original = {s: (self.fake.p3_root / ("stage-" + s + ".json")).read_bytes()
                    for s in "abc"}
        rc, doc = self.execute()
        self.assertEqual(rc, 0)
        self.assertEqual(doc["status"], "PASS")
        self.assertEqual(doc["active_model"], "flash-next")
        self.assertEqual(self.active(), "flash-next")
        self.assertTrue(doc["live_verified"])
        self.assertEqual(read_snapshot(self.fake.ops / "journal")["phase"], "COMMITTED")
        for stage, bytes_before in original.items():
            self.assertEqual((self.fake.p3_root / ("stage-" + stage + ".json")).read_bytes(),
                             bytes_before)
        self.assertFalse(any(cmd[:2] == ["docker", "rm"] for cmd in self.commands))

    def test_flash_to_27b_success(self):
        self.fake.docs[p3.NAMES["27b"]]["State"]["Running"] = False
        self.fake.docs[p3.NAMES["flash-next"]]["State"]["Running"] = True
        rc, doc = self.execute("27b")
        self.assertEqual(rc, 0)
        self.assertEqual(doc["served_id"], "qwen3.8-27b")
        self.assertEqual(self.active(), "27b")

    def test_no_approval_or_incorrect_sha_never_stops(self):
        for sha, ack in (("b" * 64, True), ("a" * 64, False), ("bad", True)):
            with self.subTest(sha=sha, ack=ack):
                before = len([c for c in self.commands if c[:2] == ["docker", "stop"]])
                rc, doc = self.execute(sha=sha, ack=ack)
                self.assertEqual(rc, 3)
                self.assertFalse(doc["executed"])
                after = len([c for c in self.commands if c[:2] == ["docker", "stop"]])
                self.assertEqual(before, after)
                self.assertEqual(self.active(), "27b")

    def test_expired_or_changed_fingerprint_rejected_pre_dispatch(self):
        good = self.planner("flash-next", root=self.fake.ops)["plan_id"]
        def drifted(target, *, root):
            data = self.planner(target, root=root)
            data["plan_id"] = "0" * 64
            return data
        rc, doc = exe.execute(
                "flash-next", good, exe.ACK_DOWNTIME,
                exe.ACK_TARGET["flash-next"], root=self.fake.ops,
                planner=drifted, run=self.runner,
                inspect=lambda name: self.fake.docs[name],
                waiter=lambda name, model, timeout, run: True,
                live=self.live)
        self.assertEqual(rc, 3)
        self.assertIn("EXPIRED_OR_CHANGED_OPERATING_PLAN", doc["issues"])
        self.assertFalse(any(c[:2] == ["docker", "stop"] for c in self.commands))

    def test_target_start_fails_old_model_restored(self):
        self.fail_start = True
        rc, doc = self.execute()
        # Failure applies to all starts, including rollback of 27B.
        self.assertEqual(rc, 4)
        self.assertEqual(doc["status"], "RECOVERY_FAILED")

    def test_target_start_fails_restore_success(self):
        def failing_target(cmd, timeout=35):
            if cmd[:2] == ["docker", "start"] and cmd[-1] == p3.NAMES["flash-next"]:
                self.commands.append(cmd)
                return SimpleNamespace(returncode=1, stdout="")
            return self.runner(cmd, timeout=timeout)
        good = self.planner("flash-next", root=self.fake.ops)["plan_id"]
        rc, doc = exe.execute(
            "flash-next", good, exe.ACK_DOWNTIME,
            exe.ACK_TARGET["flash-next"], root=self.fake.ops,
            planner=self.planner, run=failing_target,
            inspect=lambda name: self.fake.docs[name],
            waiter=lambda name, model, timeout, run: True,
            live=self.live)
        self.assertEqual(rc, 4)
        self.assertEqual(doc["status"], "FAIL_RESTORED")
        self.assertEqual(self.active(), "27b")
        self.assertEqual(read_snapshot(self.fake.ops / "journal")["phase"], "RESTORED")

    def test_wait_failure_triggers_successful_restore(self):
        self.fail_wait = True
        rc, doc = self.execute()
        self.assertEqual(rc, 4)
        self.assertEqual(doc["status"], "RECOVERY_FAILED")
        # Same waiter is used to verify restoration; mock fails both.

    def test_api_id_mismatch_after_start_triggers_restore(self):
        # Override live check only once target starts to fail target API ID.
        initial_live = self.live
        def active_checked():
            d = initial_live()
            if d.get("observed_model") == "flash-next":
                d["expected_served_id"] = "incorrect"
            return d
        good = self.planner("flash-next", root=self.fake.ops)["plan_id"]
        rc, doc = exe.execute(
            "flash-next", good, exe.ACK_DOWNTIME,
            exe.ACK_TARGET["flash-next"], root=self.fake.ops,
            planner=self.planner, run=self.runner,
            inspect=lambda name: self.fake.docs[name],
            waiter=lambda name, model, timeout, run: True,
            live=active_checked)
        self.assertEqual(rc, 4)
        self.assertEqual(doc["status"], "FAIL_RESTORED")
        self.assertEqual(self.active(), "27b")

    def test_attempt_marker_blocks_same_plan_replay(self):
        first, result = self.execute()
        self.assertEqual(first, 0)
        # Restore fixture state without modifying attempt marker or journal.
        self.fake.docs[p3.NAMES["flash-next"]]["State"]["Running"] = False
        self.fake.docs[p3.NAMES["27b"]]["State"]["Running"] = True
        rc, data = self.execute()
        self.assertEqual(rc, 4)
        self.assertFalse(data.get("active_model") == "flash-next")
        self.assertEqual(self.active(), "27b")

    def test_old_model_stopped_before_new_started(self):
        rc, _ = self.execute()
        self.assertEqual(rc, 0)
        stops = [i for i, c in enumerate(self.commands)
                 if c[:2] == ["docker", "stop"]]
        starts = [i for i, c in enumerate(self.commands)
                  if c[:2] == ["docker", "start"]]
        self.assertEqual(len(stops), 1)
        self.assertEqual(len(starts), 1)
        self.assertLess(stops[0], starts[0])

    def test_dgx_unqualified_model_fails_closed(self):
        rc, doc = exe.execute(
            "orcarouter", "a" * 64, exe.ACK_DOWNTIME, "yes",
            root=self.fake.ops, planner=self.planner,
            run=self.runner, inspect=lambda n: self.fake.docs[n],
            live=self.live)
        self.assertEqual(rc, 3)
        self.assertFalse(doc["executed"])


if __name__ == "__main__":
    unittest.main()
