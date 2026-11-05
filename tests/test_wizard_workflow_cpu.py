"""CPU-only contract for the full P1–P7 model workflow and console.
No Docker/API/GPU operations. Model selection must not mutate a live service.
"""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import patch, Mock

from wizard import main as router
from wizard import workflow
from wizard.console import _choice


def fixture(model="27b", *, next_action="blocked", status="SOURCE_PRESENT_UNQUALIFIED",
            observed="flash-next") -> dict:
    return {
        "selected_model": model, "title": model,
        "observed_model": observed,
        "status": status, "next_action": next_action,
        "steps": [], "issues": [],
        "transition_preview": None,
    }


class ModelWorkflowCPU(unittest.TestCase):
    def test_all_models_have_complete_menu_action_surface(self):
        expected = {"inspect", "download", "prepare", "start", "wait",
                    "verify", "benchmark", "switch", "rollback", "recipe"}
        for model in workflow.MODEL_ACTIONS:
            with self.subTest(model=model):
                result = workflow.model_workflow(model, selection=fixture(model))
                self.assertEqual(set(a["action"] for a in result["actions"]), expected)
                self.assertFalse(result["executed"])
                self.assertFalse(result["approval_accepted"])
                self.assertEqual(set(result["roadmap"]), set(workflow.STAGES))
                self.assertEqual(result["api_host_port"], 8000)

    def test_p1_actions_stay_on_existing_approved_backend(self):
        doc = workflow.model_workflow(
            "flash-next", selection=fixture("flash-next", status="REVIEW_REQUIRED"))
        available = {a["action"]: a["status"] for a in doc["actions"]}
        self.assertEqual(available["verify"], "GUARDED_P1")
        self.assertEqual(available["benchmark"], "GUARDED_P1")
        self.assertEqual(available["prepare"], "GUARDED_P1")
        self.assertEqual(available["download"], "BLOCKED")
        with patch("wizard.menus.models.flash_next.run", return_value=0) as execute:
            rc = workflow.invoke_model_action("flash-next", "verify",
                                              workflow=doc, guided=True)
        self.assertEqual(rc, 0)
        execute.assert_called_once_with(["guided"], as_json=False)

    def test_27b_can_only_offer_download_when_missing(self):
        missing = workflow.model_workflow(
            "27b", selection=fixture("27b", next_action="download", status="ABSENT"))
        self.assertEqual(missing["actions"][1]["status"], "APPROVAL_REQUIRED")
        self.assertFalse(any(a["status"] == "GUARDED_P1" for a in missing["actions"]))
        with patch("wizard.menus.models.qwen_27b.run", return_value=0) as existing:
            self.assertEqual(workflow.invoke_model_action(
                "27b", "download", workflow=missing, guided=True), 0)
        existing.assert_called_once_with(["download", "--guided"], as_json=False)

    def test_27b_download_in_progress_cannot_launch_duplicate(self):
        progress = workflow.model_workflow(
            "27b", selection=fixture("27b", next_action="monitor_download",
                                     status="DOWNLOADING"))
        self.assertEqual(progress["actions"][1]["status"], "IN_PROGRESS")
        with patch("wizard.menus.models.qwen_27b.run") as backend, \
             contextlib.redirect_stdout(io.StringIO()):
            rc = workflow.invoke_model_action("27b", "download",
                                              workflow=progress, guided=True)
        self.assertEqual(rc, 3)
        backend.assert_not_called()

    def test_p2_p5_start_switch_and_rollback_all_fail_closed(self):
        for model in ("27b", "orcarouter"):
            doc = workflow.model_workflow(model, selection=fixture(model))
            for action in ("prepare", "start", "wait", "verify", "benchmark",
                           "switch", "rollback"):
                with self.subTest(model=model, action=action), \
                     patch("subprocess.run", side_effect=AssertionError("NO Docker")), \
                     contextlib.redirect_stdout(io.StringIO()) as output:
                    rc = workflow.invoke_model_action(model, action,
                                                      workflow=doc, as_json=True)
                self.assertEqual(rc, 3)
                result = json.loads(output.getvalue())
                self.assertFalse(result["executed"])
                self.assertFalse(result["operations_enabled"])
                self.assertIsNone(result["plan_id"])

    def test_workflow_read_only_cli_is_complete(self):
        target = workflow.model_workflow("27b", selection=fixture("27b"))
        with patch("wizard.workflow.model_workflow", return_value=target), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main(["workflow", "27b", "--json"])
        self.assertEqual(rc, 0)
        parsed = json.loads(output.getvalue())
        self.assertEqual(parsed["model"], "27b")
        self.assertEqual(len(parsed["actions"]), 10)
        self.assertFalse(parsed["executed"])

    def test_workflow_specific_action_read_only(self):
        doc = fixture("27b")
        full = workflow.model_workflow("27b", selection=doc)
        with patch("wizard.workflow.model_workflow", return_value=full), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main(["workflow", "27b", "--for-action",
                              "start", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "BLOCKED")

    def test_workflow_rejects_execute_and_unknown_model(self):
        for command in (["workflow", "27b", "--execute", "--json"],
                        ["workflow", "unknown", "--json"],
                        ["workflow", "--json"]):
            with self.subTest(command=command), \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                rc = router.main(command)
            self.assertEqual(rc, 2)
            self.assertFalse(json.loads(output.getvalue())["executed"])

    def test_console_numeric_alias_bounded(self):
        self.assertEqual(_choice("2", ["flash-next", "27b"]), "27b")
        self.assertEqual(_choice("0", ["flash-next", "27b"]), None)
        self.assertEqual(_choice("200", ["flash-next", "27b"]), "")
        self.assertEqual(_choice("27b", ["flash-next", "27b"]), "27b")

    def test_console_model_inflight_continue_does_not_download(self):
        observing = {"status": "OBSERVED_UNQUALIFIED",
                     "observed_model": "flash-next", "download_running": True}
        doc = workflow.model_workflow(
            "27b", selection=fixture("27b", next_action="monitor_download",
                                      status="DOWNLOADING"))
        with patch("scripts.manager.service_manifest.inspect_service",
                   return_value=observing), \
             patch("wizard.console.model_workflow", return_value=doc), \
             patch("wizard.menus.models.qwen_27b.run") as download, \
             patch("builtins.input", side_effect=["1", "2", "1", "0", "0"]), \
             patch.object(router.sys.stdin, "isatty", return_value=True), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main([])
        self.assertEqual(rc, 0)
        download.assert_not_called()
        self.assertIn("already running", output.getvalue())

    def test_console_p3_two_directions_have_explicit_pair(self):
        observing = {"status": "OBSERVED_UNQUALIFIED",
                     "observed_model": "flash-next", "download_running": False}
        with patch("scripts.manager.service_manifest.inspect_service",
                   return_value=observing), \
             patch("wizard.menus.switching.flash_next_27b.run",
                   return_value=3) as guarded, \
             patch("builtins.input", side_effect=["3", "2", "2", "1",
                                                   "0", "0", "0"]), \
             patch.object(router.sys.stdin, "isatty", return_value=True), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(router.main([]), 0)
        guarded.assert_called_once_with(
            ["plan", "--for-action", "switch",
             "--from-model", "flash-next", "--to-model", "27b"])

    def test_console_service_operations_are_visible_but_not_implicit(self):
        observing = {"status": "OBSERVED_UNQUALIFIED",
                     "observed_model": "flash-next", "download_running": False}
        with patch("scripts.manager.service_manifest.inspect_service",
                   return_value=observing), \
             patch("wizard.menus.operations.service.run", return_value=3) as stub, \
             patch("builtins.input", side_effect=["2", "6", "0", "0"]), \
             patch.object(router.sys.stdin, "isatty", return_value=True), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(router.main([]), 0)
        stub.assert_called_once_with(["restart"])
        self.assertIn("restart", output.getvalue())

    def test_model_alias_workflow(self):
        doc = workflow.model_workflow(
            "next-flash", selection=fixture("flash-next"))
        self.assertEqual(doc["model"], "flash-next")


if __name__ == "__main__":
    unittest.main()
