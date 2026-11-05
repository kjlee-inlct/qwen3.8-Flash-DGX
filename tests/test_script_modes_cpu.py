"""Ensure entrypoint executable bits survive GitHub tree edits (CPU-only)."""
from pathlib import Path
import os
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ExecutableScriptsTest(unittest.TestCase):
    def test_entrypoint_permissions(self):
        for name in ("flash", "scripts/serve.sh",
                     "wizard/00-doctor.sh", "wizard/10-plan.sh",
                     "wizard/p1.sh", "wizard.sh"):
            with self.subTest(name=name):
                p = ROOT / name
                self.assertTrue(p.is_file(), f"missing {name}")
                self.assertTrue(os.access(p, os.X_OK), f"not executable: {name}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
