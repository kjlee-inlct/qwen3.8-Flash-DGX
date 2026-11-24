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

    def test_ambiguous_duplicate_json_marker_is_never_audited_as_unique(self):
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            self.assertEqual(claim(folder)["status"],
                             "PASS_FAKE_NONCE_MARKER_CREATED")
            marker = next(folder.iterdir())
            # Same semantic dict under the permissive JSON decoder, but two
            # occurrences of schema_version: never permit ambiguous evidence.
            raw = marker.read_bytes()
            marker.write_bytes(b'{"schema_version":2,' + raw[1:])
            report = audit(folder)
            self.assertEqual(report["status"], "BLOCKED_FAKE_NONCE_AUDIT")
            self.assertIn("FAKE_MARKER_DUPLICATE_JSON_KEY", report["issues"])
            self.assertEqual(claim(folder)["status"], "BLOCKED_FAKE_NONCE_REPLAY")
            self.assertTrue(marker.exists())

    def test_same_value_wrong_json_type_marker_fails_closed(self):
        # Old dict equality would accept these without changing record_hash:
        # True == 1, 1 == True, and 8000 == 8000.0 in Python.
        substitutions = (
            ("requires_independent_approval", 1),
            ("requires_live_revalidation", 1),
            ("max_active_gpu_models", True),
            ("api_host_port", 8000.0),
            ("schema_version", 2.0),
        )
        for field, substitute in substitutions:
            with (self.subTest(field=field),
                  tempfile.TemporaryDirectory(prefix=PREFIX) as root):
                folder = Path(root)
                self.assertEqual(claim(folder)["status"],
                                 "PASS_FAKE_NONCE_MARKER_CREATED")
                marker = next(folder.iterdir())
                doc = json.loads(marker.read_text(encoding="utf-8"))
                self.assertEqual(doc[field], substitute)
                self.assertIsNot(type(doc[field]), type(substitute))
                doc[field] = substitute
                marker.write_text(
                    json.dumps(doc, sort_keys=True, separators=(",", ":")) + "\n",
                    encoding="utf-8",
                )
                result = audit(folder)
                self.assertEqual(result["status"], "BLOCKED_FAKE_NONCE_AUDIT")
                self.assertIn("FAKE_MARKER_IDENTITY_OR_HASH_MISMATCH",
                              result["issues"])
                self.assertFalse(result["real_operating_nonce_fence_verified"])
                self.assertEqual(claim(folder)["status"],
                                 "BLOCKED_FAKE_NONCE_REPLAY")
                self.assertTrue(marker.exists())

    def test_injected_fsync_failure_keeps_nonce_spent_and_never_recovers(self):
        # Failure at either file fsync or directory fsync is uncertain durable
        # state, not permission to retry, delete, resume, or claim approval.
        original_fsync = os.fsync
        for failing_call in (1, 2):
            with (self.subTest(failing_call=failing_call),
                  tempfile.TemporaryDirectory(prefix=PREFIX) as root):
                folder = Path(root)
                count = 0

                def injected_fsync(fd):
                    nonlocal count
                    count += 1
                    if count == failing_call:
                        raise OSError("INJECTED_FSYNC_FAILURE")
                    return original_fsync(fd)

                with patch("scripts.manager.mock_nonce_fence_v2.os.fsync",
                           side_effect=injected_fsync):
                    result = claim(folder)
                self.assertEqual(result["status"], "BLOCKED_FAKE_NONCE_IO")
                self.assertFalse(result["approval_accepted"])
                self.assertFalse(result["automatic_recovery_authorized"])
                marker = folder / ("fake-nonce-" + "d" * 64 + ".json")
                self.assertTrue(marker.exists())
                self.assertEqual(claim(folder)["status"], "BLOCKED_FAKE_NONCE_REPLAY")

    def test_marker_swap_after_directory_fsync_blocks_claim(self):
        # An O_EXCL write/fsync is not enough if a concurrent test writer
        # moves/replaces the path before the claim reports success.
        original_fsync = os.fsync
        for replacement in ("symlink", "same_bytes_new_inode"):
            with (self.subTest(replacement=replacement),
                  tempfile.TemporaryDirectory(prefix=PREFIX) as root):
                folder = Path(root)
                marker = folder / ("fake-nonce-" + "d" * 64 + ".json")
                calls = 0

                def swap_on_directory_fsync(fd):
                    nonlocal calls
                    calls += 1
                    if calls == 2:
                        raw = marker.read_bytes()
                        if replacement == "symlink":
                            marker.unlink()
                            marker.symlink_to(folder / "missing-target")
                        else:
                            # Keep the original inode alive so a byte-equal
                            # replacement cannot accidentally reuse it.
                            marker.rename(folder / "old-marker-held")
                            marker.write_bytes(raw)
                            os.chmod(marker, 0o600)
                    return original_fsync(fd)

                with patch("scripts.manager.mock_nonce_fence_v2.os.fsync",
                           side_effect=swap_on_directory_fsync):
                    result = claim(folder)
                self.assertEqual(calls, 2)
                self.assertEqual(result["status"], "BLOCKED_FAKE_NONCE_IO")
                self.assertIn(
                    "FAKE_NONCE_DURABILITY_OR_ROOT_IDENTITY_UNKNOWN",
                    result["issues"],
                )
                self.assertFalse(result["fake_durable_marker_created"])
                self.assertFalse(result["real_operating_nonce_fence_verified"])
                self.assertEqual(claim(folder)["status"],
                                 "BLOCKED_FAKE_NONCE_REPLAY")
                self.assertTrue(marker.exists() or marker.is_symlink())

    def test_same_inode_same_size_content_swap_after_fsync_blocks_claim(self):
        # A reused inode and unchanged length defeat a path-only check.
        original_fsync = os.fsync
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            marker = folder / ("fake-nonce-" + "d" * 64 + ".json")
            fsync_calls = 0
            original_inode = None

            def rewrite_on_directory_fsync(fd):
                nonlocal fsync_calls, original_inode
                fsync_calls += 1
                if fsync_calls == 2:
                    original_inode = marker.stat().st_ino
                    raw = marker.read_bytes()
                    edited = raw.replace(
                        b'"api_host_port":8000',
                        b'"api_host_port":8001',
                        1,
                    )
                    self.assertNotEqual(raw, edited)
                    self.assertEqual(len(raw), len(edited))
                    marker.write_bytes(edited)
                    self.assertEqual(marker.stat().st_ino, original_inode)
                return original_fsync(fd)

            with patch("scripts.manager.mock_nonce_fence_v2.os.fsync",
                       side_effect=rewrite_on_directory_fsync):
                result = claim(folder)
            self.assertEqual(fsync_calls, 2)
            self.assertEqual(result["status"], "BLOCKED_FAKE_NONCE_IO")
            self.assertIn(
                "FAKE_NONCE_DURABILITY_OR_ROOT_IDENTITY_UNKNOWN",
                result["issues"],
            )
            self.assertFalse(result["fake_durable_marker_created"])
            self.assertFalse(result["real_operating_nonce_fence_verified"])
            self.assertEqual(marker.stat().st_ino, original_inode)
            self.assertEqual(claim(folder)["status"],
                             "BLOCKED_FAKE_NONCE_REPLAY")
            self.assertTrue(marker.exists())

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
        with (tempfile.TemporaryDirectory(prefix=PREFIX) as root,
              tempfile.TemporaryDirectory(prefix="external-fake-nonce-") as outside):
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
