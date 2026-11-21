"""Read-only bounded service log preview; no real Docker or mutation."""
from __future__ import annotations

import contextlib
import io
import json
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts.manager.service_logs import MAX_DISPLAY_CHARS, inspect_logs
from wizard import main as router


class ServiceLogsCPU(unittest.TestCase):
    def setUp(self):
        self.observed = {
            "status": "OBSERVED_UNQUALIFIED",
            "observed_model": "flash-next", "issues": [],
            "managed_containers": [
                {"model": "flash-next", "container_name": "qwen38-flash",
                 "status": "Up 6 hours"},
            ],
        }

    def test_logs_read_only_approved_container_name(self):
        runner = Mock(return_value=SimpleNamespace(returncode=0,
                        stdout="model online\n", stderr=""))
        result = inspect_logs(service=self.observed, runner=runner)
        self.assertEqual(result["status"], "READ_ONLY_LOGS")
        self.assertEqual(result["container_name"], "qwen38-flash")
        self.assertFalse(result["executed"])
        self.assertFalse(result["operations_enabled"])
        command = runner.call_args.args[0]
        self.assertEqual(command, ["docker", "logs", "--tail", "40",
                                   "--timestamps", "qwen38-flash"])
        self.assertEqual(result["logs"], "model online\n")

    def test_unverified_or_no_running_model_blocks_subprocess(self):
        for service in (
            {**self.observed, "status": "BLOCKED"},
            {**self.observed, "observed_model": None},
            {**self.observed, "managed_containers": []},
        ):
            runner = Mock(side_effect=AssertionError("must not read Docker"))
            result = inspect_logs(service=service, runner=runner)
            self.assertEqual(result["status"], "BLOCKED")
            self.assertFalse(result["executed"])
            runner.assert_not_called()

    def test_log_output_truncated_and_line_count_bounded(self):
        runner = Mock(return_value=SimpleNamespace(returncode=0,
                      stdout="x" * (MAX_DISPLAY_CHARS + 150), stderr=""))
        result = inspect_logs(service=self.observed, runner=runner)
        self.assertTrue(result["truncated"])
        self.assertEqual(len(result["logs"]), MAX_DISPLAY_CHARS)
        with self.assertRaises(ValueError):
            inspect_logs(service=self.observed, runner=runner, tail=999)

    def test_nonzero_docker_exit_blocks_without_stdout_dump(self):
        runner = Mock(return_value=SimpleNamespace(
            returncode=1, stdout="SECRET_TOKEN", stderr="error"))
        result = inspect_logs(service=self.observed, runner=runner)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIsNone(result["logs"])

    def test_nested_wizard_logs_json(self):
        fake = {"status": "READ_ONLY_LOGS", "executed": False, "logs": "OK"}
        with patch("wizard.menus.operations.service.inspect_logs",
                   return_value=fake), \
             contextlib.redirect_stdout(io.StringIO()) as stdout:
            rc = router.main(["service", "manager", "logs", "--json"])
        self.assertEqual(rc, 0)
        self.assertFalse(json.loads(stdout.getvalue())["executed"])


if __name__ == "__main__":
    unittest.main()
