"""TTY model-agnostic P5-P8 UX remains read-only and fail-closed."""
from __future__ import annotations

import contextlib
import io
import unittest
from unittest.mock import patch

from wizard import console


class CommonUXCPU(unittest.TestCase):
    def test_generic_menu_fault_matrix_does_not_call_docker(self):
        with patch.object(console, "_input", side_effect=["3", "0"]), \
             patch("subprocess.run", side_effect=AssertionError("No live operations")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            console._generic_qualification_menu("27b")
        self.assertIn("pairs: 6 | cases: 24", output.getvalue())

    def test_registered_unqualified_target_is_previewed_not_switched(self):
        live = {
            "status": "LIVE_SERVICE_VERIFIED", "observed_model": "27b",
            "expected_served_id": "qwen3.8-27b",
            "active_container": {"name": "qwen38-27b"},
            "gpu_exclusivity_verified": True,
            "port_process_ownership_verified": True}
        with patch.object(console, "_input", return_value="3"), \
             patch("scripts.manager.service_status.inspect_live_status",
                   return_value=live), \
             patch.object(console, "_switch_guided",
                          side_effect=AssertionError("must not trigger guided live switch")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            console._switch_selector()
        self.assertIn("Model-agnostic preflight: BLOCKED", out.getvalue())
        self.assertIn("TARGET_CANONICAL_RUNTIME_NOT_QUALIFIED", out.getvalue())

    def test_unknown_live_identity_blocks_without_starting_anything(self):
        with patch.object(console, "_input", return_value="1"), \
             patch("scripts.manager.service_status.inspect_live_status",
                   return_value={"status": "BLOCKED", "observed_model": None}), \
             patch.object(console, "_switch_guided",
                          side_effect=AssertionError("no guided action")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            console._switch_selector()
        self.assertIn("current API model identity is unverified", out.getvalue())


if __name__ == "__main__":
    unittest.main()
