"""P6-E isolated fake durable nonce: CPU only, no Docker or operating files."""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager.mock_nonce_fence_v2 import (
    PREFIX, fake_nonce_claim, fake_nonce_audit, fake_replay_fence_demo,
)
from scripts.manager.generic_operations import model_catalog
from wizard.main import main as wizard_main


def claim(folder, *, source="27b", target="flash-next", plan="c" * 64,
          nonce="d" * 64, now=100, expires=200):
    return fake_nonce_claim(folder, source, target, "a" * 64, "b" * 64,
                            plan, nonce, now_ns=now, expires_ns=expires)


def audit(folder, *, plan="c" * 64):
    return fake_nonce_audit(folder, "27b", "flash-next", "a" * 64, "b" * 64,
                             plan, "d" * 64, now_ns=100, expires_ns=200)


class MockNonceFenceV2CPU(unittest.TestCase):
    def test_all_registered_ordered_pairs_have_isolated_replay_fixture(self):
        names = list(model_catalog()["models"])
        with patch("subprocess.run", side_effect=AssertionError("NO DOCKER")):
            for src in names:
                for dst in names:
                    if src != dst:
                        with self.subTest(src=src, dst=dst):
                            result = fake_replay_fence_demo(src, dst)
                            self.assertEqual(
                                result["status"],
                                "PASS_FAKE_NONCE_REPLAY_FENCE_EXPECTATIONS")
                            self.assertTrue(result["duplicate_blocked"])
                            self.assertTrue(result["changed_plan_replay_blocked"])
                            self.assertTrue(result["temporary_folder_removed"])
                            self.assertFalse(result["durable_operating_nonce_verified"])
                            self.assertFalse(result["automatic_recovery_authorized"])

    def test_durable_marker_reused_even_for_different_plan_and_model_pair(self):
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            self.assertEqual(claim(folder)["status"],
                             "PASS_FAKE_NONCE_MARKER_CREATED")
            self.assertEqual(audit(folder)["status"],
                             "PASS_FAKE_NONCE_MARKER_CONSISTENCY")
            self.assertEqual(claim(folder)["status"], "BLOCKED_FAKE_NONCE_REPLAY")
            self.assertEqual(
                claim(folder, plan="e" * 64)["status"], "BLOCKED_FAKE_NONCE_REPLAY")
            self.assertEqual(
                claim(folder, source="orcarouter", target="27b")["status"],
                "BLOCKED_FAKE_NONCE_REPLAY")
            marker = folder / ("fake-nonce-" + "d" * 64 + ".json")
            self.assertEqual(marker.stat().st_mode & 0o777, 0o600)

    def test_partial_or_tampered_marker_blocks_and_never_auto_clears(self):
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            claim(folder)
            marker = next(folder.iterdir())
            marker.write_text('{"record_hash":"broken"', encoding="utf-8")
            self.assertEqual(audit(folder)["status"], "BLOCKED_FAKE_NONCE_AUDIT")
            self.assertEqual(claim(folder)["status"], "BLOCKED_FAKE_NONCE_REPLAY")
            self.assertTrue(marker.exists())

    def test_symlink_and_world_readable_fixtures_fail_closed(self):
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            marker = folder / ("fake-nonce-" + "d" * 64 + ".json")
            marker.symlink_to(folder / "missing")
            self.assertEqual(claim(folder)["status"], "BLOCKED_FAKE_NONCE_REPLAY")
            self.assertEqual(audit(folder)["status"], "BLOCKED_FAKE_NONCE_AUDIT")
            marker.unlink()
            claim(folder)
            os.chmod(marker, 0o644)
            self.assertEqual(audit(folder)["status"], "BLOCKED_FAKE_NONCE_AUDIT")
            os.chmod(marker, 0o600)

    def test_bad_root_expiry_nonce_and_pair_never_write(self):
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            for kwargs in ({"nonce": "x" * 64}, {"now": 200, "expires": 200},
                           {"now": 100, "expires": 100 + 61_000_000_000},
                           {"source": "27b", "target": "27b"}):
                with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                    claim(folder, **kwargs)
            self.assertEqual(list(folder.iterdir()), [])
            with self.assertRaises(ValueError):
                claim(folder.parent)

    def test_two_independent_python_processes_cannot_claim_same_nonce(self):
        # Real CPU subprocess race on a disposable fixture, NEVER a DGX/operating lock.
        script = (
            "import json,sys;from pathlib import Path;"
            "from scripts.manager.mock_nonce_fence_v2 import fake_nonce_claim;"
            "print(json.dumps(fake_nonce_claim(Path(sys.argv[1]),"
            "'27b','flash-next','a'*64,'b'*64,'c'*64,'d'*64,"
            "now_ns=100,expires_ns=200)))"
        )
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            children = [
                subprocess.Popen([sys.executable, "-c", script, root],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True)
                for _ in range(2)
            ]
            statuses = []
            for child in children:
                stdout, stderr = child.communicate(timeout=15)
                self.assertEqual(child.returncode, 0, stderr)
                statuses.append(json.loads(stdout)["status"])
            self.assertEqual(statuses.count("PASS_FAKE_NONCE_MARKER_CREATED"), 1)
            self.assertEqual(statuses.count("BLOCKED_FAKE_NONCE_REPLAY"), 1)
            self.assertEqual(audit(Path(root))["status"],
                             "PASS_FAKE_NONCE_MARKER_CONSISTENCY")
            self.assertEqual(len(list(Path(root).iterdir())), 1)

    def test_hardlink_marker_cannot_be_audited_as_unique(self):
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            self.assertEqual(claim(folder)["status"], "PASS_FAKE_NONCE_MARKER_CREATED")
            marker = next(folder.iterdir())
            os.link(marker, folder / "extra-hardlink")
            self.assertEqual(audit(folder)["status"], "BLOCKED_FAKE_NONCE_AUDIT")
            self.assertEqual(claim(folder)["status"], "BLOCKED_FAKE_NONCE_REPLAY")

    def test_marker_swapped_to_valid_outside_symlink_during_open_is_blocked(self):
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root, \\
             tempfile.TemporaryDirectory(prefix="external-fake-nonce-") as outside:
            folder = Path(root)
            claim(folder)
            marker = next(folder.iterdir())
            outside_path = Path(outside) / "valid-copy.json"
            outside_path.write_bytes(marker.read_bytes())
            original_open = os.open
            replaced = False

            def swap_before_open(path, flags, *args, **kwargs):
                nonlocal replaced
                if path == marker.name and not replaced:
                    replaced = True
                    marker.unlink()
                    marker.symlink_to(outside_path)
                return original_open(path, flags, *args, **kwargs)

            with patch("scripts.manager.mock_nonce_fence_v2.os.open",
                       side_effect=swap_before_open):
                self.assertEqual(audit(folder)["status"], "BLOCKED_FAKE_NONCE_AUDIT")
            self.assertTrue(replaced)
            self.assertTrue(marker.is_symlink())
            self.assertEqual(claim(folder)["status"], "BLOCKED_FAKE_NONCE_REPLAY")

    def test_cli_fixture_only_and_non_authorizing(self):
        with patch("subprocess.run", side_effect=AssertionError("NO RUNTIME")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            code = wizard_main(["operations", "generic", "nonce-fence-mock",
                                "--from-model", "orcarouter",
                                "--to-model", "27b", "--json"])
        self.assertEqual(code, 0)
        doc = json.loads(out.getvalue())
        self.assertEqual(doc["test_count"], 4)
        self.assertTrue(doc["changed_plan_replay_blocked"])
        self.assertFalse(doc["approval_accepted"])
        self.assertFalse(doc["operating_journal_written"])

    def test_cli_invalid_model_fails_closed(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = wizard_main(["operations", "generic", "nonce-fence-mock",
                                "--from-model", "27b",
                                "--to-model", "unregistered", "--json"])
        self.assertEqual(code, 3)
        self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
