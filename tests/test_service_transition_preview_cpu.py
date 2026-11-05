"""Source-only fail-closed service transition/rollback planner contract."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.manager.service_transition_preview import preview_transition


class TransitionPreviewCPU(unittest.TestCase):
    def setUp(self):
        self.live = {
            "status": "OBSERVED_UNQUALIFIED",
            "observed_model": "flash-next",
            "api_port_8000_listening": True,
            "download_running": False,
        }

    def test_stop_before_start_and_rollback_order_no_execution(self):
        with patch("subprocess.run",
                   side_effect=AssertionError("must not call Docker")):
            result = preview_transition("27b", service=self.live)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["executed"])
        self.assertIsNone(result["plan_id"])
        actions = [step["action"] for step in result["steps"]]
        self.assertLess(actions.index("stop-current"),
                        actions.index("verify-port-free"))
        self.assertLess(actions.index("verify-port-free"),
                        actions.index("start-target"))
        self.assertLess(actions.index("start-target"),
                        actions.index("api-verify"))
        rollback = [step["action"] for step in result["rollback"]]
        self.assertIn("restore-old", rollback)
        self.assertIn("verify-restored-api", rollback)
        self.assertEqual(result["api_host_port"], 8000)

    def test_even_perfect_external_facts_cannot_unlock_unimplemented_adapter(self):
        plan = preview_transition(
            "27b", service=self.live, checkpoint_ready=True,
            runtime_qualified=True, api_identity_verified=True,
            gpu_exclusivity_verified=True, rollback_verified=True)
        self.assertEqual(plan["status"], "BLOCKED")
        self.assertIn("SERVICE_TRANSITION_EXECUTOR_NOT_IMPLEMENTED", plan["issues"])
        self.assertFalse(plan["operations_enabled"])

    def test_running_download_blocks_switch_preview(self):
        plan = preview_transition(
            "27b", service={**self.live, "download_running": True})
        self.assertIn("TARGET_DOWNLOAD_IN_PROGRESS", plan["issues"])

    def test_unknown_service_and_target_block(self):
        plan = preview_transition(
            "27b", service={"status": "BLOCKED", "observed_model": None})
        self.assertIn("LIVE_SERVICE_INVENTORY_UNVERIFIED", plan["issues"])
        with self.assertRaises(ValueError):
            preview_transition("unknown", service=self.live)

    def test_same_target_is_noop_not_a_stop_start(self):
        plan = preview_transition(
            "flash-next", service=self.live,
            checkpoint_ready=True, runtime_qualified=True)
        self.assertIn("TARGET_ALREADY_ACTIVE_NO_SWITCH_REQUIRED", plan["issues"])
        self.assertFalse(plan["executed"])


if __name__ == "__main__":
    unittest.main()
