"""CPU tests for DGX Native Tools V1 temporary operator wrapper.

Never invokes --plan or a TTY-approved --execute on the test runner.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts/temporary/p2-final-native-tools-operator.sh"


class NativeToolOperatorScriptCPU(unittest.TestCase):
    def call(self, *args):
        return subprocess.run(
            ["bash", str(WRAPPER), *args],
            input="", capture_output=True, text=True,
            timeout=10, check=False,
        )

    def test_shell_syntax(self):
        result = subprocess.run(
            ["bash", "-n", str(WRAPPER)],
            capture_output=True, text=True, timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_help_does_not_touch_containers(self):
        result = self.call("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--plan", result.stdout)
        self.assertIn("--execute", result.stdout)
        self.assertIn("original qwen38-27b restored", result.stdout)
        self.assertIn("power/host/Docker/OOM", result.stdout)

    def test_execute_noninteractive_denied_before_python_or_docker(self):
        result = self.call("--execute")
        self.assertEqual(result.returncode, 3)
        self.assertIn("interactive TTY", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_execute_with_any_extra_arguments_denied(self):
        result = self.call("--execute", "--approve-plan", "a" * 64)
        self.assertEqual(result.returncode, 2)
        self.assertIn("TTY approval only", result.stderr)

    def test_unrecognized_action_is_denied(self):
        result = self.call("--force")
        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported Native Tools V1", result.stderr)

    def test_plan_refuses_approval_flags(self):
        result = self.call("--plan", "--ack-downtime")
        self.assertEqual(result.returncode, 2)
        self.assertIn("--plan takes no arguments", result.stderr)

    def test_wrapper_is_not_old_p3_or_generic_switch(self):
        source = WRAPPER.read_text(encoding="utf-8")
        self.assertIn("scripts.manager.p2_27b_tool_live_trial plan", source)
        self.assertIn("scripts.manager.p2_27b_tool_live_trial execute", source)
        self.assertNotIn("docker stop", source)
        self.assertNotIn("docker run", source)
        self.assertNotIn("p3-stage-c", source)
        self.assertNotIn("operational-switch-acceptance", source)


if __name__ == "__main__":
    unittest.main()
