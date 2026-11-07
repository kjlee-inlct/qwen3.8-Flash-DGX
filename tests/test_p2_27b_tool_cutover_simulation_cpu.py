"""Fake-DGX only: Native Tools V1 transaction state and rollback matrix."""
from __future__ import annotations

import unittest
from scripts.manager import p2_27b_tool_cutover_simulation as mod


def facts():
    return {
        "kind": "P2_FINAL_NATIVE_TOOLS_V1_SIMULATION",
        "variant_id": mod.VARIANT_ID,
        "original": mod.SOURCE_CONTAINER,
        "target": mod.VARIANT_CONTAINER,
        "fallback": mod.FALLBACK_CONTAINER,
        "served_id": mod.SERVED,
        "pinned_revision": mod.REVISION,
        "port": 8000,
        "source_container_id": "a" * 64,
        "source_image": "sha256:" + "b" * 64,
        "fallback_container_id": "c" * 64,
        "fallback_image": "sha256:" + "d" * 64,
        "parser_audited": True, "tokenizer_audited": True,
        "one_active_gpu_model": True, "expires_at": 1794024300,
    }


class FakeDGX:
    def __init__(self, original, **kwargs):
        self.original = original
        self.source_up = True
        self.variant_up = False
        self.foreign_gpu = False
        self.options = kwargs
        self.calls = []
        self.source_reads = 0
        self.lock_released = False

    def locked(self):
        self.calls.append("lock")
        return not self.options.get("lock_failed", False)

    def journal_clean(self):
        self.calls.append("journal")
        return not self.options.get("journal_dirty", False)

    def source(self):
        self.calls.append("source")
        self.source_reads += 1
        if self.options.get("source_drift") and self.source_reads == 2:
            return "0" * 64, self.original["source_image"], True
        return (self.original["source_container_id"],
                self.original["source_image"], self.source_up)

    def fallback(self):
        self.calls.append("fallback")
        if self.options.get("fallback_drift"):
            return "0" * 64, self.original["fallback_image"], False
        return (self.original["fallback_container_id"],
                self.original["fallback_image"], False)

    def variant_absent(self):
        self.calls.append("variant_absent")
        return not self.options.get("variant_collision", False)

    def gpu_running(self):
        self.calls.append("gpu_running")
        names = []
        if self.source_up:
            names.append(mod.SOURCE_CONTAINER)
        if self.variant_up:
            names.append(mod.VARIANT_CONTAINER)
        if self.foreign_gpu:
            names.append("foreign")
        return names

    def stop_original(self):
        self.calls.append("stop_original")
        if self.options.get("stop_failed"):
            raise RuntimeError("DOCKER_STOP_FAILED")
        self.source_up = False

    def confirm_original_stopped(self):
        self.calls.append("confirm_original_stopped")
        return not self.source_up

    def port_free(self):
        self.calls.append("port_free")
        return not self.options.get("port_busy", False)

    def start_variant(self):
        self.calls.append("start_variant")
        self.variant_up = True
        if self.options.get("start_failed"):
            raise RuntimeError("PARTIAL_START_ERROR")

    def verify_variant(self, served):
        self.calls.append("verify_variant")
        return (self.variant_up and served == mod.SERVED
                and not self.options.get("verify_failed", False))

    def confirm_original_preserved(self, cid, image):
        self.calls.append("confirm_original_preserved")
        return (cid == self.original["source_container_id"]
                and image == self.original["source_image"]
                and not self.source_up)

    def stop_variant(self):
        self.calls.append("stop_variant")
        self.variant_up = False
        if self.options.get("variant_stop_failed"):
            raise RuntimeError("VARIANT_STOP_FAILED")

    def restore_original(self):
        self.calls.append("restore_original")
        if self.options.get("restore_failed"):
            raise RuntimeError("RESTORE_ERROR")
        self.source_up = True

    def confirm_original_restored(self, cid, image, served):
        self.calls.append("confirm_original_restored")
        return (self.source_up and not self.variant_up
                and cid == self.original["source_container_id"]
                and image == self.original["source_image"]
                and served == mod.SERVED)

    def release(self):
        self.calls.append("release")
        self.lock_released = True


def simulate(*, fx=None, **kwargs):
    plan = facts() if fx is None else fx
    adapter = FakeDGX(plan, **kwargs)
    approval = mod.simulated_approval_digest(plan)
    result = mod.simulate_transaction(plan, approval, mod.ACK, mod.ACK_TARGET,
                                      adapter=adapter, now=1794024000)
    return result, adapter


class FakeCutoverCPU(unittest.TestCase):
    def test_happy_path_never_claims_live_dgx(self):
        r, d = simulate()
        self.assertEqual(r["status"], "SIMULATED_PASS")
        self.assertFalse(r["executed_on_real_dgx"])
        self.assertFalse(r["production_executor_available"])
        self.assertTrue(d.variant_up)
        self.assertFalse(d.source_up)
        self.assertLess(d.calls.index("stop_original"),
                        d.calls.index("port_free"))
        self.assertLess(d.calls.index("port_free"),
                        d.calls.index("start_variant"))
        self.assertTrue(d.lock_released)

    def test_wrong_approval_cannot_mutate_even_fake(self):
        f = facts()
        d = FakeDGX(f)
        r = mod.simulate_transaction(f, "0" * 64, mod.ACK, mod.ACK_TARGET,
                                     adapter=d, now=1794024000)
        self.assertEqual(r["status"], "SIMULATED_BLOCKED")
        self.assertEqual(d.calls, [])

    def test_missing_downtime_ack_or_target_ack_denied(self):
        for downtime, target in ((None, mod.ACK_TARGET), (mod.ACK, None)):
            f = facts()
            d = FakeDGX(f)
            r = mod.simulate_transaction(
                f, mod.simulated_approval_digest(f), downtime, target,
                adapter=d, now=1794024000,
            )
            self.assertEqual(r["status"], "SIMULATED_BLOCKED")
            self.assertEqual(d.calls, [])

    def test_expired_or_too_short_plan_blocks(self):
        for expiry in (1794023900, 1794024050, 1794024701):
            f = facts()
            f["expires_at"] = expiry
            d = FakeDGX(f)
            r = mod.simulate_transaction(f, mod.simulated_approval_digest(f),
                                         mod.ACK, mod.ACK_TARGET,
                                         adapter=d, now=1794024000)
            self.assertEqual(r["status"], "SIMULATED_BLOCKED")
            self.assertEqual(d.calls, [])

    def test_parser_and_model_identity_both_required(self):
        for key in ("parser_audited", "tokenizer_audited", "one_active_gpu_model"):
            f = facts()
            f[key] = False
            self.assertIsNone(mod.simulated_approval_digest(f))

    def test_lock_denial_no_docker_steps(self):
        r, d = simulate(lock_failed=True)
        self.assertEqual(r["status"], "SIMULATED_BLOCKED")
        self.assertNotIn("stop_original", d.calls)

    def test_dirty_journal_fail_closed(self):
        r, d = simulate(journal_dirty=True)
        self.assertEqual(r["status"], "SIMULATED_BLOCKED")
        self.assertNotIn("stop_original", d.calls)
        self.assertTrue(d.lock_released)

    def test_source_drift_before_stop_no_downtime(self):
        r, d = simulate(source_drift=True)
        self.assertEqual(r["status"], "SIMULATED_BLOCKED")
        self.assertNotIn("stop_original", d.calls)
        self.assertTrue(d.source_up)

    def test_fallback_drift_no_downtime(self):
        r, d = simulate(fallback_drift=True)
        self.assertEqual(r["status"], "SIMULATED_BLOCKED")
        self.assertNotIn("stop_original", d.calls)

    def test_variant_name_collision_no_downtime(self):
        r, d = simulate(variant_collision=True)
        self.assertEqual(r["status"], "SIMULATED_BLOCKED")
        self.assertNotIn("stop_original", d.calls)

    def test_port_busy_causes_restored_original(self):
        r, d = simulate(port_busy=True)
        self.assertEqual(r["status"], "SIMULATED_FAIL_RESTORED")
        self.assertTrue(d.source_up)
        self.assertFalse(d.variant_up)
        self.assertNotIn("start_variant", d.calls)
        self.assertIn("restore_original", d.calls)

    def test_partial_variant_start_failure_restores(self):
        r, d = simulate(start_failed=True)
        self.assertEqual(r["status"], "SIMULATED_FAIL_RESTORED")
        self.assertTrue(d.source_up)
        self.assertFalse(d.variant_up)
        self.assertIn("stop_variant", d.calls)

    def test_verify_failure_stops_variant_and_restores(self):
        r, d = simulate(verify_failed=True)
        self.assertEqual(r["status"], "SIMULATED_FAIL_RESTORED")
        self.assertIn("verify_variant", d.calls)
        self.assertIn("stop_variant", d.calls)
        self.assertTrue(d.source_up)

    def test_restore_failure_is_not_success(self):
        r, d = simulate(port_busy=True, restore_failed=True)
        self.assertEqual(r["status"], "SIMULATED_RECOVERY_FAILED")
        self.assertFalse(d.source_up)
        self.assertTrue(d.lock_released)

    def test_variant_stop_failure_is_ambiguous_not_success(self):
        r, d = simulate(verify_failed=True, variant_stop_failed=True)
        self.assertEqual(r["status"], "SIMULATED_RECOVERY_FAILED")
        self.assertFalse(d.source_up)

    def test_original_stop_error_requests_restore(self):
        r, d = simulate(stop_failed=True)
        self.assertEqual(r["status"], "SIMULATED_FAIL_RESTORED")
        self.assertTrue(d.source_up)
        self.assertIn("restore_original", d.calls)


if __name__ == "__main__":
    unittest.main()
