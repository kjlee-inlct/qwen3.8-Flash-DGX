"""Source-only CPU regression matrix for consolidated model-first Wizard."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import patch

from wizard import main as router
from wizard import quickstart as q


def live(model="flash-next", *, downloading=False):
    return {
        "status": "OBSERVED_UNQUALIFIED",
        "observed_state": "ONE_MANAGED_MODEL_RUNNING",
        "observed_model": model,
        "api_port_8000_listening": True,
        "download_running": downloading,
        "issues": [],
    }


def checkpoint(present):
    return {
        "source_files_present": present,
        "checkpoint_status": ("SOURCE_FILES_PRESENT_PINNED_CANDIDATE"
                              if present else "NOT_READY"),
        "issues": [] if present else ["NO_PINNED_LOCAL_SNAPSHOT"],
    }


class QuickstartCPU(unittest.TestCase):
    def test_existing_flash_next_is_never_restarted(self):
        plan = q.selection_plan("flash-next", service=live())
        self.assertEqual(plan["status"], "RUNNING_OBSERVED")
        self.assertEqual(plan["next_action"], "none")
        self.assertEqual(plan["observed_model"], "flash-next")
        self.assertFalse(plan["api_identity_verified"])
        self.assertFalse(plan["executed"])
        self.assertEqual(plan["api_host_port"], 8000)

    def test_downloading_27b_suppresses_duplicate_download(self):
        plan = q.selection_plan("27b", service=live(downloading=True),
                                checkpoint=checkpoint(False))
        self.assertEqual(plan["status"], "DOWNLOADING")
        self.assertEqual(plan["next_action"], "monitor_download")
        self.assertNotIn("download", [x["action"] for x in plan["steps"]])
        self.assertFalse(plan["operations_enabled"])

    def test_absent_27b_offers_download_only_and_blocks_switch(self):
        plan = q.selection_plan("27b", service=live(), checkpoint=checkpoint(False))
        self.assertEqual(plan["status"], "ABSENT")
        self.assertEqual(plan["next_action"], "download")
        self.assertEqual(plan["steps"][0]["approval_scope"],
                         "checkpoint_download_only")
        self.assertEqual(plan["steps"][-1]["state"], "BLOCKED")
        self.assertEqual(plan["steps"][-1]["approval_scope"],
                         "service_transition")

    def test_present_27b_remains_runtime_unqualified(self):
        plan = q.selection_plan("27b", service=live(), checkpoint=checkpoint(True))
        self.assertEqual(plan["status"], "SOURCE_PRESENT_UNQUALIFIED")
        self.assertEqual(plan["next_action"], "blocked")
        self.assertFalse(plan["runtime_qualified"])

    def test_active_27b_is_only_observed_not_api_verified(self):
        plan = q.selection_plan("27b", service=live("27b"),
                                checkpoint=checkpoint(True))
        self.assertEqual(plan["status"], "RUNNING_OBSERVED")
        self.assertEqual(plan["next_action"], "none")
        self.assertFalse(plan["api_identity_verified"])

    def test_unknown_service_blocks_download_automation(self):
        service = {"status": "BLOCKED",
                   "issues": ["docker_inventory_incomplete"],
                   "observed_model": None, "download_running": True}
        plan = q.selection_plan("27b", service=service, checkpoint=checkpoint(False))
        self.assertEqual(plan["status"], "UNKNOWN")
        self.assertEqual(plan["next_action"], "blocked")
        self.assertIn("LIVE_SERVICE_STATE_UNVERIFIED", plan["issues"])

    def test_checkpoint_probe_unknown_does_not_offer_download(self):
        plan = q.selection_plan(
            "27b", service=live(),
            checkpoint={"source_files_present": False,
                        "checkpoint_status": "UNKNOWN",
                        "issues": ["CACHE_UNREADABLE"]})
        self.assertEqual(plan["status"], "UNKNOWN")
        self.assertIn("CACHE_UNREADABLE", plan["issues"])

    def test_orcarouter_unqualified_and_no_start(self):
        plan = q.selection_plan("orcarouter", service=live())
        self.assertEqual(plan["status"], "SOURCE_UNQUALIFIED")
        self.assertEqual(plan["next_action"], "blocked")
        self.assertIn("ORCAROUTER_RUNTIME_ADAPTER_UNQUALIFIED", plan["issues"])
        self.assertFalse(plan["executed"])

    def test_model_aliases_and_invalid_selection(self):
        self.assertEqual(q.normalize("next-flash"), "flash-next")
        self.assertEqual(q.normalize("orcarouter-flash-next"), "orcarouter")
        with self.assertRaises(ValueError):
            q.normalize("unknown-model")

    def test_unobserved_flash_next_uses_existing_p1_backend(self):
        plan = q.selection_plan("flash-next", service=live(None))
        self.assertEqual(plan["next_action"], "open_p1_guided")
        self.assertIn("review_p1", [x["action"] for x in plan["steps"]])
        self.assertFalse(plan["executed"])

    def test_download_prompt_no_does_not_dispatch(self):
        plan = q.selection_plan("27b", service=live(),
                                checkpoint=checkpoint(False))
        with patch.object(q, "selection_plan", return_value=plan), \
             patch("builtins.input", return_value="n"), \
             patch("wizard.menus.models.qwen_27b.run") as runner, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(q.interactive_select("27b"), 0)
        runner.assert_not_called()

    def test_download_prompt_yes_reuses_exact_approval_backend(self):
        plan = q.selection_plan("27b", service=live(),
                                checkpoint=checkpoint(False))
        with patch.object(q, "selection_plan", return_value=plan), \
             patch("builtins.input", return_value="y"), \
             patch("wizard.menus.models.qwen_27b.run", return_value=0) as runner, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(q.interactive_select("27b"), 0)
        runner.assert_called_once_with(["download", "--guided"])

    def test_downloading_never_prompts_or_dispatches(self):
        plan = q.selection_plan("27b", service=live(downloading=True),
                                checkpoint=checkpoint(False))
        with patch.object(q, "selection_plan", return_value=plan), \
             patch("builtins.input", side_effect=AssertionError("no prompt")), \
             patch("wizard.menus.models.qwen_27b.run") as runner, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(q.interactive_select("27b"), 0)
        runner.assert_not_called()

    def test_model_selection_cli_is_read_only(self):
        plan = q.selection_plan("27b", service=live(downloading=True),
                                checkpoint=checkpoint(False))
        with patch.object(q, "selection_plan", return_value=plan), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main(["select", "27b", "--json"])
        self.assertEqual(rc, 0)
        data = json.loads(output.getvalue())
        self.assertFalse(data["executed"])
        self.assertEqual(data["selected_model"], "27b")
        self.assertEqual(data["next_action"], "monitor_download")

    def test_model_choose_alias_and_dry_run_are_safe(self):
        plan = q.selection_plan("flash-next", service=live())
        with patch.object(q, "selection_plan", return_value=plan), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main(["model", "choose", "flash-next",
                              "--dry-run", "--json"])
        self.assertEqual(rc, 0)
        self.assertTrue(json.loads(output.getvalue())["dry_run"])

    def test_selection_rejects_execution_flags_and_missing_model(self):
        for args in (["select"], ["select", "27b", "--execute"],
                     ["select", "nonsense", "--json"]):
            with self.subTest(args=args), contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(router.main(args), 2)

    def test_three_choice_root_menu_does_not_run_p1_without_approval(self):
        plan = q.selection_plan("flash-next", service=live())
        with patch("scripts.manager.service_manifest.inspect_service",
                   return_value=live()), \
             patch("builtins.input", side_effect=["1", "1", "0", "0"]), \
             patch.object(router.sys.stdin, "isatty", return_value=True), \
             patch.object(q, "selection_plan", return_value=plan), \
             patch("scripts.manager.p1_wizard.main") as old_backend, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main([])
        self.assertEqual(rc, 0)
        old_backend.assert_not_called()
        self.assertIn("1. Select / run model", output.getvalue())
        self.assertIn("3. Advanced", output.getvalue())


if __name__ == "__main__":
    unittest.main()
