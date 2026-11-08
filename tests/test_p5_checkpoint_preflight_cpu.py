"""CPU-only regression for the P5 one-shot read-only acceptance judge."""
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from scripts.manager import p5_checkpoint_preflight as one


class P5CheckpointOneShotCPU(unittest.TestCase):
    def test_success_remains_source_only_not_gpu_qualified(self):
        ok = {"status": "PASS", "checkpoint_metadata_verified": True,
              "gpu_verified": False, "issues": []}
        result = subprocess.CompletedProcess([], 0, "", "Ran 143 tests in 2.0s\n\nOK\n")
        with patch.object(one.manifest_registry, "validate",
                          return_value={"status": "PASS"}), \
             patch.object(one, "inspect", return_value=ok), \
             patch.object(one.subprocess, "run", return_value=result) as run:
            doc = one.evaluate(Path("/absent"), Path("/absent"))
        self.assertEqual(doc["status"], "PASS_SOURCE_ONLY")
        self.assertEqual(doc["cpu_tests"]["count"], 143)
        for flag in ("gpu_verified", "api_verified", "image_built",
                     "executed", "service_mutated", "hf_cache_mutated",
                     "approval_generated", "production_released"):
            self.assertFalse(doc[flag], flag)
        args = run.call_args.args[0]
        self.assertIn("unittest", args)
        self.assertNotIn("docker", args)

    def test_metadata_mismatch_blocks_without_cpu_execution(self):
        fail = {"status": "BLOCKED",
                "issues": ["P5_LMHEAD_SCALE_PRESENT_BUT_HEAD_IGNORED"],
                "checkpoint_metadata_verified": False}
        with patch.object(one.manifest_registry, "validate",
                          return_value={"status": "PASS"}), \
             patch.object(one, "inspect", return_value=fail), \
             patch.object(one.subprocess, "run",
                          side_effect=AssertionError("no tests")):
            doc = one.evaluate(Path("/none"), Path("/none"), with_tests=False)
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIn("P5_LMHEAD_SCALE_PRESENT_BUT_HEAD_IGNORED",
                      doc["issues"])
        self.assertEqual(doc["cpu_tests"]["status"], "NOT_RUN")

    def test_unit_test_nonzero_refuses_promotion(self):
        fake = subprocess.CompletedProcess([], 1, "", "Ran 2 tests\nFAILED")
        with patch.object(one.manifest_registry, "validate",
                          return_value={"status": "PASS"}), \
             patch.object(one, "inspect", return_value={"status": "PASS"}), \
             patch.object(one.subprocess, "run", return_value=fake):
            doc = one.evaluate(Path("/none"), Path("/none"))
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIn("P5_PREFLIGHT_CPU_TESTS_FAILED", doc["issues"])

    def test_manifest_failure_cannot_pass_even_if_checkpoint_passes(self):
        with patch.object(one.manifest_registry, "validate",
                          return_value={"status": "BLOCKED"}), \
             patch.object(one, "inspect", return_value={"status": "PASS"}):
            doc = one.evaluate(Path("/none"), Path("/none"), with_tests=False)
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertEqual(doc["manifest"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
