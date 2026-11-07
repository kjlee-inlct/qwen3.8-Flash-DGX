"""CPU/Fake-DGX state-machine, exact approval, and recovery regressions."""
from __future__ import annotations

import unittest
from unittest.mock import patch
import contextlib
import io

from scripts.manager import model_lifecycle as lifecycle


class FakeDGX:
    def __init__(self, **states):
        self.states = dict(states)
        self.calls = []
        self.fail = set()
        self.verify_ok = True
        self.benchmark_ok = True
        self.port_ok = True
        self.exclusive_ok = True

    def _step(self, name, *detail):
        self.calls.append((name, *detail))
        if name in self.fail:
            raise RuntimeError("FAKE_" + name + "_FAILURE")

    def exists(self, name):
        return name in self.states

    def running(self, name):
        return self.states.get(name, False)

    def stop(self, name):
        self._step("stop", name)
        if name not in self.states:
            raise ValueError("unknown")
        self.states[name] = False

    def start(self, name):
        self._step("start", name)
        if name not in self.states:
            raise ValueError("missing")
        self.states[name] = True

    def rename(self, old, new):
        self._step("rename", old, new)
        if old not in self.states or new in self.states:
            raise RuntimeError("NAME_CONFLICT")
        self.states[new] = self.states.pop(old)

    def remove(self, name):
        self._step("remove", name)
        if self.states.get(name, False):
            raise RuntimeError("RUNNING_RM")
        del self.states[name]

    def port_free(self):
        self._step("port_free")
        return self.port_ok and not any(self.states.values())

    def exclusive(self, name):
        self._step("exclusive", name)
        return self.exclusive_ok and self.states.get(name) is True

    def create(self, *, name, recipe, cache_source, plan_id):
        self._step("create", name)
        if name in self.states or not cache_source:
            raise RuntimeError("CONFLICT_OR_CACHE_MISSING")
        self.states[name] = True

    def verify(self, model):
        self._step("verify", model)
        return self.verify_ok

    def benchmark(self, model):
        self._step("benchmark", model)
        return self.benchmark_ok


def preview(action, decision, *, active=None, running=False):
    return {
        "model": "27b", "requested_action": action, "decision": decision,
        "active_model": active, "running": running,
        "container_name": "qwen38-27b", "plan_id": "a"*64,
    }


class LifecycleTransactionCPU(unittest.TestCase):
    def run_core(self, p, fake, *, cache="/hf-cache"):
        events = []
        result = lifecycle._run_transaction(
            p, fake, {"recipe_id": "qwen38-27b"}, cache,
            record=lambda phase, data: events.append((phase, data)))
        return result, events

    def test_interactive_model_lifecycle_review_is_read_only(self):
        from wizard.console import _lifecycle_review
        report = {
            "status": "DRIFT_REQUIRES_RECREATE", "installed": True,
            "running": True, "container_id": "a"*64,
            "recipe_sha256": "b"*64, "decision": "RECREATE",
            "diff": [{"field": "cmd", "desired": {"a": 1}, "observed": {"a": 2}}],
            "issues": [], "advisories": [],
        }
        with (patch("wizard.console._input", side_effect=["4", "0"]),
              patch("scripts.manager.recipe_drift.plan", return_value=report) as planner,
              contextlib.redirect_stdout(io.StringIO()) as output):
            _lifecycle_review("27b")
        planner.assert_called_once_with("27b", "restart")
        self.assertIn("Changed cmd", output.getvalue())
        self.assertIn("No service, Docker or cache changes", output.getvalue())

    def test_post_remove_receipt_failure_never_reports_restored(self):
        fake = FakeDGX(**{"qwen38-27b": True})
        def record(phase, detail):
            if phase == "COMPLETE":
                raise RuntimeError("FAILED_TO_PERSIST_RECEIPT")
        out = lifecycle._run_transaction(
            preview("remove", "REMOVE_ACTIVE", active="27b", running=True),
            fake, {"recipe_id": "qwen38-27b"}, "/hf-cache", record=record)
        self.assertEqual(out["status"], "RECOVERY_UNCERTAIN")
        self.assertNotIn("qwen38-27b", fake.states)

    def test_production_dispatch_stays_locked(self):
        rc, result = lifecycle.execute(
            "27b", "remove", "a"*64, lifecycle.ACK_DOWNTIME,
            lifecycle.ACK_REMOVE)
        self.assertEqual(rc, 3)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("PRODUCTION_LIFECYCLE_NOT_RELEASED", result["issues"])

    def test_approval_requires_fresh_exact_sha_and_real_tty(self):
        p = {
            "model": "27b", "requested_action": "remove",
            "status": "READY_FOR_OPERATOR_REVIEW_ONLY",
            "plan_id": "a"*64, "expires_at_epoch_seconds": 1000,
            "issues": [],
        }
        args = ["27b", "remove", "a"*64, lifecycle.ACK_DOWNTIME,
                lifecycle.ACK_REMOVE]
        self.assertTrue(lifecycle.approval_valid(p, *args, now=900, tty=True))
        self.assertFalse(lifecycle.approval_valid(p, *args, now=975, tty=True))
        self.assertFalse(lifecycle.approval_valid(p, *args, now=399, tty=True))
        self.assertFalse(lifecycle.approval_valid(p, *args, now=900, tty=False))
        self.assertFalse(lifecycle.approval_valid(p, "27b", "remove", "b"*64,
                                                  args[3], args[4], now=900, tty=True))
        self.assertFalse(lifecycle.approval_valid(p, "27b", "remove", "a"*64,
                                                  args[3], None, now=900, tty=True))

    def test_noop_uses_zero_mutations(self):
        fake = FakeDGX(**{"qwen38-27b": True})
        result, events = self.run_core(preview("start", "NOOP", active="27b",
                                               running=True), fake)
        self.assertEqual(result["status"], "NO_CHANGE")
        self.assertFalse(result["executed"])
        self.assertEqual(fake.calls, [])
        self.assertEqual(events, [])

    def test_start_stopped_target_stops_active_model_first(self):
        fake = FakeDGX(**{"qwen38-flash": True, "qwen38-27b": False})
        result, events = self.run_core(preview("switch", "START_EXISTING",
                                               active="flash-next"), fake)
        self.assertEqual(result["status"], "PASS")
        self.assertFalse(fake.states["qwen38-flash"])
        self.assertTrue(fake.states["qwen38-27b"])
        self.assertLess(fake.calls.index(("stop", "qwen38-flash")),
                        fake.calls.index(("start", "qwen38-27b")))
        self.assertEqual(events[-1][0], "COMMITTED")

    def test_restart_existing_does_not_recreate(self):
        fake = FakeDGX(**{"qwen38-27b": True})
        result, _ = self.run_core(preview("restart", "RESTART_EXISTING",
                                          active="27b", running=True), fake)
        self.assertEqual(result["status"], "PASS")
        self.assertIn(("stop", "qwen38-27b"), fake.calls)
        self.assertIn(("start", "qwen38-27b"), fake.calls)
        self.assertNotIn(("create", "qwen38-27b"), fake.calls)

    def test_successful_recreate_keeps_backup_not_deleted(self):
        fake = FakeDGX(**{"qwen38-27b": True})
        result, events = self.run_core(preview("recreate", "RECREATE", active="27b",
                                               running=True), fake)
        self.assertEqual(result["status"], "PASS_BACKUP_RETAINED")
        backup = "qwen38-27b-rollback-" + "a"*12
        self.assertTrue(fake.states[backup] is False)
        self.assertTrue(fake.states["qwen38-27b"])
        self.assertNotIn(("remove", backup), fake.calls)
        self.assertEqual(events[-1][0], "COMMITTED")
        self.assertFalse(result["removed_hf_cache"])

    def test_install_missing_27b_uses_pinned_cache_no_image_delete(self):
        fake = FakeDGX()
        result, _ = self.run_core(preview("install", "INSTALL"), fake)
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(fake.states["qwen38-27b"])
        self.assertFalse(result["removed_model_image"])

    def test_install_without_trusted_host_cache_blocks(self):
        fake = FakeDGX()
        result, _ = self.run_core(preview("install", "INSTALL"), fake, cache=None)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(fake.calls, [])

    def test_benchmark_failed_recreate_restores_original(self):
        fake = FakeDGX(**{"qwen38-27b": True})
        fake.benchmark_ok = False
        result, events = self.run_core(preview("recreate", "RECREATE", active="27b",
                                               running=True), fake)
        self.assertEqual(result["status"], "FAIL_RESTORED")
        self.assertTrue(fake.states["qwen38-27b"])
        self.assertTrue("qwen38-27b-failed-" + "a"*12 in fake.states)
        self.assertEqual(events[-1][0], "RESTORED")

    def test_failed_restore_is_explicit_uncertain_and_never_retried(self):
        fake = FakeDGX(**{"qwen38-27b": True})
        fake.benchmark_ok = False
        fake.fail.add("start")
        result, events = self.run_core(preview("recreate", "RECREATE", active="27b",
                                               running=True), fake)
        self.assertEqual(result["status"], "RECOVERY_UNCERTAIN")
        self.assertEqual(events[-1][0], "RECOVERY_UNCERTAIN")

    def test_gpu_conflict_rollback_restores_source(self):
        fake = FakeDGX(**{"qwen38-flash": True, "qwen38-27b": False})
        fake.exclusive_ok = False
        result, _ = self.run_core(preview("switch", "START_EXISTING",
                                          active="flash-next"), fake)
        self.assertEqual(result["status"], "FAIL_RESTORED")
        self.assertTrue(fake.states["qwen38-flash"])

    def test_unfreed_port_blocks_then_restores_source(self):
        fake = FakeDGX(**{"qwen38-flash": True, "qwen38-27b": False})
        fake.port_ok = False
        result, _ = self.run_core(preview("switch", "START_EXISTING",
                                          active="flash-next"), fake)
        self.assertEqual(result["status"], "FAIL_RESTORED")
        self.assertTrue(fake.states["qwen38-flash"])

    def test_remove_stopped_and_remove_active_are_container_only(self):
        for running, decision in ((False, "REMOVE_STOPPED"), (True, "REMOVE_ACTIVE")):
            fake = FakeDGX(**{"qwen38-27b": running})
            p = preview("remove", decision,
                        active="27b" if running else None, running=running)
            result, _ = self.run_core(p, fake)
            self.assertEqual(result["status"], "PASS")
            self.assertNotIn("qwen38-27b", fake.states)
            self.assertFalse(result["removed_hf_cache"])
            self.assertFalse(result["historical_p3_receipts_modified"])

    def test_preexisting_backup_blocks_before_mutation(self):
        name = "qwen38-27b-rollback-" + "a"*12
        fake = FakeDGX(**{"qwen38-27b": True, name: False})
        result, _ = self.run_core(preview("recreate", "RECREATE", active="27b",
                                          running=True), fake)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(fake.calls, [])

    def test_failed_create_with_partial_named_candidate_preserved(self):
        fake = FakeDGX(**{"qwen38-27b": True})
        fake.fail.add("create")
        result, events = self.run_core(preview("recreate", "RECREATE", active="27b",
                                               running=True), fake)
        self.assertEqual(result["status"], "FAIL_RESTORED")
        self.assertTrue(fake.states["qwen38-27b"])
        self.assertEqual(events[-1][0], "RESTORED")


if __name__ == "__main__":
    unittest.main()
