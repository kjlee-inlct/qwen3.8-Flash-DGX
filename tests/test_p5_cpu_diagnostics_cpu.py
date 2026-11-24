"""P5 CPU receipt must distinguish an actual test failure from a parse mismatch."""
import subprocess
import unittest
from unittest.mock import patch

from scripts.manager import p5_orcarouter as p5


def receipt(rc: int, text: str):
    return subprocess.CompletedProcess(["python", "unittest"], rc, "", text)


class P5CPUResultDiagnostics(unittest.TestCase):
    def _invoke(self, result):
        with (patch.object(p5, "abi_source_audit", return_value={"status": "PASS", "issues": []}),
              patch.object(p5.manifest_registry, "validate",
                           return_value={"status": "PASS", "issues": []}),
              patch.object(p5.subprocess, "run", return_value=result)):
            return p5.cpu_only()

    def test_real_unittest_failure_never_accepted(self):
        raw = ("test_bad (test_p5_orcarouter_cpu.P5CPU.test_bad) ... FAIL\n\n"
               "Ran 1 test in 0.010s\n\nFAILED (failures=1)\n")
        doc = self._invoke(receipt(1, raw))
        self.assertEqual(doc["status"], "FAIL")
        stage = doc["stages"][1]
        self.assertEqual(stage["issues"], ["P5_CPU_TESTS_FAILED"])
        self.assertEqual(stage["exit_code"], 1)
        self.assertEqual(stage["parsed_case_count"], 1)
        self.assertEqual(stage["test_cases"][0]["status"], "FAIL")
        self.assertFalse(doc["operations_enabled"])

    def test_exit_zero_but_unparseable_verbose_output_fails_closed(self):
        raw = "test_name ... ok\n\nRan 1 test in 0.005s\n\nOK\n"
        doc = self._invoke(receipt(0, raw))
        self.assertEqual(doc["status"], "FAIL")
        stage = doc["stages"][1]
        self.assertEqual(stage["issues"], ["P5_CPU_RESULT_PARSE_MISMATCH"])
        self.assertEqual(stage["parsed_case_count"], 0)
        self.assertEqual(stage["unittest_reported_count"], 1)
        self.assertFalse(doc["gpu_verified"])

    def test_consistent_verbose_unittest_output_passes_source_only(self):
        raw = ("test_alpha (test_p5_orcarouter_cpu.P5CPU.test_alpha) ... ok\n\n"
               "----------------------------------------------------------------------\n"
               "Ran 1 test in 0.004s\n\nOK\n")
        doc = self._invoke(receipt(0, raw))
        self.assertEqual(doc["status"], "PASS")
        stage = doc["stages"][1]
        self.assertEqual(stage["parsed_case_count"], 1)
        self.assertEqual(stage["unittest_reported_count"], 1)
        self.assertEqual(stage["issues"], [])
        self.assertFalse(doc["gpu_verified"])
        self.assertFalse(doc["operations_enabled"])


if __name__ == "__main__":
    unittest.main()
