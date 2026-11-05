"""CPU-only tests for Wizard P1-P7 modular menu and automation CLI."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from wizard import main as router
from wizard.menus import HANDLERS
from wizard.menus.common import describe, plan


class WizardRouterCPU(unittest.TestCase):
    def call(self, args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            result = router.main(args)
        return result, out.getvalue()

    def test_catalog_contains_seven_distinct_modules(self):
        doc = router.catalog()
        self.assertEqual([x["stage"] for x in doc["stages"]],
                         ["p1", "p2", "p3", "p4", "p5", "p6", "p7"])
        self.assertEqual(doc["api_host_port"], 8000)
        for key, module in HANDLERS.items():
            with self.subTest(stage=key):
                self.assertEqual(module.__name__, "wizard.menus." + key)

    def test_catalog_machine_json(self):
        rc, s = self.call(["list", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(s)["schema_version"], 1)
        self.assertIn("INTERFACE_ONLY", s)

    def test_no_tty_lists_stages_instead_of_prompt(self):
        with patch.object(router.sys.stdin, "isatty", return_value=False):
            rc, s = self.call(["--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(len(json.loads(s)["stages"]), 7)

    def test_future_stage_status_is_read_only(self):
        for key in ("p2", "p3", "p4", "p5", "p6", "p7"):
            with self.subTest(stage=key):
                rc, s = self.call([key, "status", "--json"])
                obj = json.loads(s)
                self.assertEqual(rc, 0)
                self.assertEqual(obj["stage"], key)
                self.assertFalse(obj["operations_enabled"])
                self.assertEqual(obj["runtime"], "NOT_RUN")

    def test_future_stage_plans_are_all_blocked(self):
        for key in ("p2", "p3", "p4", "p5", "p6", "p7"):
            module = HANDLERS[key]
            for action in module.SPEC.actions:
                with self.subTest(stage=key, action=action):
                    rc, s = self.call([key, action, "--json"])
                    obj = json.loads(s)
                    self.assertEqual(rc, 3)
                    self.assertEqual(obj["status"], "BLOCKED")
                    self.assertFalse(obj["executed"])
                    self.assertFalse(obj["operations_enabled"])
                    self.assertIsNone(obj["plan_id"])

    def test_future_stage_execute_cannot_be_unlocked_by_fake_approval(self):
        for key in ("p2", "p3", "p4", "p5", "p6", "p7"):
            action = HANDLERS[key].SPEC.actions[0]
            with self.subTest(stage=key):
                rc, s = self.call([key, action, "--execute",
                                   "--approve-plan", "a" * 64, "--json"])
                self.assertEqual(rc, 3)
                obj = json.loads(s)
                self.assertFalse(obj["executed"])
                self.assertFalse(obj["approval_accepted"])
                self.assertIn("UNVERIFIED_APPROVAL_CANNOT_EXECUTE", obj["issues"])

    def test_p3_valid_pair_remains_source_only(self):
        rc, s = self.call(["p3", "plan", "--for-action", "switch",
                           "--from-model", "flash-next",
                           "--to-model", "27b", "--json"])
        self.assertEqual(rc, 3)
        doc = json.loads(s)
        self.assertNotIn("INVALID_OR_MISSING_SWITCH_PAIR", doc["issues"])
        self.assertEqual(doc["destination_model"], "27b")
        self.assertFalse(doc["executed"])

    def test_p3_rejects_wrong_direction(self):
        rc, s = self.call(["p3", "switch", "--from-model", "27b",
                           "--to-model", "27b", "--json"])
        self.assertEqual(rc, 3)
        self.assertIn("INVALID_OR_MISSING_SWITCH_PAIR", json.loads(s)["issues"])

    def test_p6_supports_only_defined_model_pair(self):
        rc, s = self.call(["p6", "switch", "--from-model", "orcarouter",
                           "--to-model", "27b", "--json"])
        self.assertEqual(rc, 3)
        self.assertNotIn("INVALID_OR_MISSING_SWITCH_PAIR", json.loads(s)["issues"])

    def test_p4_cleanup_cannot_run_without_specific_approval(self):
        rc, s = self.call(["p4", "retire", "--target", "flash-next",
                           "--execute", "--json"])
        self.assertEqual(rc, 3)
        obj = json.loads(s)
        self.assertIn("NO_SEPARATE_PATH_SPECIFIC_APPROVAL", obj["issues"])
        self.assertFalse(obj["executed"])

    def test_p4_wrong_target_cannot_be_accepted(self):
        rc, s = self.call(["p4", "retire", "--target", "orcarouter", "--json"])
        self.assertEqual(rc, 3)
        self.assertIn("NO_EXACT_FLASH_NEXT_TARGET_SELECTED", json.loads(s)["issues"])

    def test_cli_stage_action_long_options(self):
        rc, s = self.call(["--stage", "p3", "--action", "switch",
                           "--from-model", "flash-next", "--to-model", "27b",
                           "--json"])
        self.assertEqual(rc, 3)
        self.assertEqual(json.loads(s)["action"], "switch")

    def test_explicit_dry_run_cannot_execute_p1(self):
        with patch("scripts.manager.p1_wizard.main") as fn:
            rc, _ = self.call(["p1", "start", "--dry-run", "--execute",
                               "--approve-plan", "x"])
        self.assertEqual(rc, 3)
        fn.assert_not_called()

    def test_explicit_dry_run_cannot_execute_future_stage(self):
        rc, s = self.call(["p5", "prepare", "--dry-run", "--execute", "--json"])
        self.assertEqual(rc, 3)
        self.assertIn("DRY_RUN_EXECUTION_CONFLICT", json.loads(s)["issues"])

    def test_p1_delegate_preserves_exact_args(self):
        with patch("scripts.manager.p1_wizard.main", return_value=0) as mock_main:
            rc, _ = self.call(["p1", "plan", "--for-action", "benchmark",
                               "--requests", "3", "--json"])
        self.assertEqual(rc, 0)
        mock_main.assert_called_once_with(
            ["plan", "--for-action", "benchmark", "--requests", "3"])

    def test_p1_status_default_no_network_when_no_args(self):
        with patch("scripts.manager.p1_wizard.main", return_value=0) as mock_main:
            rc, _ = self.call(["p1", "--json"])
        self.assertEqual(rc, 0)
        mock_main.assert_called_once_with(["status"])

    def test_json_guided_is_rejected_without_prompt(self):
        with patch("scripts.manager.p1_wizard.main") as fn:
            rc, text = self.call(["p1", "guided", "--json"])
        self.assertEqual(rc, 3)
        self.assertEqual(json.loads(text)["status"], "BLOCKED")
        fn.assert_not_called()

    def test_p1_guided_default_on_tty(self):
        with patch.object(router.sys.stdin, "isatty", return_value=True), \
             patch("scripts.manager.p1_wizard.main", return_value=0) as fn:
            rc, _ = self.call(["p1"])
        self.assertEqual(rc, 0)
        fn.assert_called_once_with(["guided"])

    def test_invalid_stage_returns_error_without_execution(self):
        rc, _ = self.call(["p99", "start"])
        self.assertEqual(rc, 2)

    def test_invalid_stage_option_returns_error(self):
        rc, s = self.call(["--stage", "--json"])
        self.assertEqual(rc, 2)
        self.assertIn("BLOCKED", s)

    def test_stage_menu_files_exist(self):
        root = Path(__file__).resolve().parents[1]
        for n in range(1, 8):
            with self.subTest(stage=n):
                self.assertTrue((root / "wizard/menus" / f"p{n}.py").is_file())
        self.assertTrue((root / "wizard.sh").is_file())

    def test_future_stage_status_does_not_inspect_docker(self):
        with patch("subprocess.run", side_effect=AssertionError("no subprocess")):
            for stage in ("p2", "p3", "p4", "p5", "p6", "p7"):
                rc, _ = self.call([stage, "status", "--json"])
                self.assertEqual(rc, 0)

    def test_schema_version_in_future_plans(self):
        for stage in ("p2", "p3", "p4", "p5", "p6", "p7"):
            obj = plan(HANDLERS[stage].SPEC, HANDLERS[stage].SPEC.actions[0])
            self.assertEqual(obj["schema_version"], 1)
            self.assertEqual(describe(HANDLERS[stage].SPEC)["stage"], stage)


if __name__ == "__main__":
    unittest.main()
