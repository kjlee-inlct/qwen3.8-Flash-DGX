"""P6-B/C fake Docker IDs, bounded tickets, ephemeral journal regression."""
from __future__ import annotations
import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager.mock_transaction_pipeline import audit_mock_journal, mock_pipeline
from scripts.manager.mock_persistent_contract import (
    PREFIX, LOG_NAME, STATE_NAME, SCENARIOS,
    _ticket, audit_fake_store, check_fake_ticket,
    fake_disk_contract, fake_disk_matrix, write_fake_store,
)
from scripts.manager.transition_safety import InMemoryBackend, simulate_transaction
from wizard.main import main as wizard_main


class P6BindingAndDiskCPU(unittest.TestCase):
    def test_distinct_source_target_ids_per_phase(self):
        doc = mock_pipeline("orcarouter", "27b")
        src, dst = doc["source_container_id"], doc["target_container_id"]
        self.assertEqual(len(src), 64)
        self.assertEqual(len(dst), 64)
        self.assertNotEqual(src, dst)
        self.assertEqual(doc["final_active_container_id"], dst)
        self.assertEqual(doc["final_port_owner_container_id"], dst)
        for ev in doc["mock_journal"]:
            self.assertEqual(ev["docker_id"], src)
            self.assertEqual(ev["source_container_id"], src)
            self.assertEqual(ev["target_container_id"], dst)
            active = ev["active_models"]
            if active == ["orcarouter"]:
                self.assertEqual(ev["active_container_id"], src)
                self.assertEqual(ev["port_owner_container_id"], src)
            elif active == ["27b"]:
                self.assertEqual(ev["active_container_id"], dst)
                self.assertEqual(ev["port_owner_container_id"], dst)
            else:
                self.assertIsNone(ev["active_container_id"])
                self.assertIsNone(ev["port_owner_container_id"])
        self.assertEqual(doc["journal_audit"]["status"], "VERIFIED_MOCK_TERMINAL")

    def test_restore_binds_original_source_not_target(self):
        doc = mock_pipeline("27b", "flash-next", fault="target-api")
        self.assertEqual(doc["journal_audit"]["last_phase"], "RESTORED")
        self.assertEqual(doc["final_active_container_id"], doc["source_container_id"])
        verifying = [ev for ev in doc["mock_journal"] if ev["phase"] == "NEW_VERIFYING"]
        self.assertEqual(verifying[0]["active_container_id"], doc["target_container_id"])

    def test_colliding_ids_block_before_stop(self):
        backend = InMemoryBackend("27b", "27b", docker_id="a" * 64,
                                  target_docker_id="a" * 64)
        result = simulate_transaction("27b", "orcarouter", backend=backend)
        self.assertEqual(result["status"], "BLOCKED_FAKE_BEFORE_STOP")
        self.assertEqual(result["synthetic_mutations"], [])
        self.assertIn("SOURCE_TARGET_DOCKER_ID_NOT_DISTINCT_OR_INVALID", result["issues"])

    def test_tamper_exact_active_and_port_id_without_changing_names(self):
        doc = mock_pipeline("27b", "orcarouter")
        events = copy.deepcopy(doc["mock_journal"])
        events[-1]["active_container_id"] = doc["source_container_id"]
        self.assertIn("ACTIVE_CONTAINER_ID_UNBOUND",
                      audit_mock_journal(events, "27b", "orcarouter")["issues"])
        events = copy.deepcopy(doc["mock_journal"])
        events[-1]["port_owner_container_id"] = doc["source_container_id"]
        self.assertIn("PORT_OWNER_CONTAINER_ID_UNBOUND",
                      audit_mock_journal(events, "27b", "orcarouter")["issues"])

    def test_all_pair_disk_scenarios(self):
        with patch("subprocess.run", side_effect=AssertionError("no Docker")):
            matrix = fake_disk_matrix()
        self.assertEqual(matrix["status"], "PASS_FAKE_DGX_EXPECTED_OUTCOMES")
        self.assertEqual(matrix["test_count"], 6 * len(SCENARIOS))
        for case in matrix["cases"]:
            self.assertIn(case["status"],
                          ("PASS_FAKE_DISK_CONTRACT", "PASS_FAKE_DISK_FAILURE_DETECTED"))
            self.assertNotEqual(case["source_container_id"], case["target_container_id"])
            self.assertTrue(case["temporary_folder_removed"])
            self.assertFalse(case["executed"])
            self.assertFalse(case["durable_operating_journal_verified"])

    def test_fault_detection_cases(self):
        expected = {
            "interrupted-snapshot": ("audit", "FAKE_JOURNAL_LOG_SNAPSHOT_MISMATCH"),
            "tampered-snapshot": ("audit", "FAKE_JOURNAL_LAST_SNAPSHOT_MISMATCH"),
            "unresolved-transition": ("audit", "MOCK_JOURNAL_UNRESOLVED_TRANSITION"),
            "expired-ticket": ("ticket_issues", "FAKE_TICKET_EXPIRED_OR_INVALID"),
            "identity-drift": ("ticket_issues", "FAKE_TICKET_IDENTITY_OR_INTEGRITY_MISMATCH"),
            "duplicate-ticket": ("ticket_issues", "FAKE_TICKET_REPLAY_OR_INVALID_NONCE"),
        }
        for scenario, (field, issue) in expected.items():
            with self.subTest(scenario=scenario):
                doc = fake_disk_contract("27b", "flash-next", scenario=scenario)
                self.assertEqual(doc["status"], "PASS_FAKE_DISK_FAILURE_DETECTED")
                actual = doc[field]["issues"] if field == "audit" else doc[field]
                self.assertIn(issue, actual)

    def test_ticket_ttl_boundary_and_replay(self):
        p = mock_pipeline("27b", "orcarouter")
        src, dst = p["source_container_id"], p["target_container_id"]
        ticket = _ticket("27b", "orcarouter", src, dst)
        now = ticket["issued_at_ns"] + 1
        consumed = set()
        self.assertEqual(check_fake_ticket(ticket, "27b", "orcarouter", src, dst,
                                           now_ns=now, consumed=consumed), [])
        consumed.add(ticket["nonce"])
        self.assertIn("FAKE_TICKET_REPLAY_OR_INVALID_NONCE",
                      check_fake_ticket(ticket, "27b", "orcarouter", src, dst,
                                        now_ns=now, consumed=consumed))
        consumed.clear()
        self.assertIn("FAKE_TICKET_EXPIRED_OR_INVALID",
                      check_fake_ticket(ticket, "27b", "orcarouter", src, dst,
                                        now_ns=ticket["expires_at_ns"], consumed=consumed))
        fake = dict(ticket, issued_at_ns="untrusted")
        self.assertIn("FAKE_TICKET_EXPIRED_OR_INVALID",
                      check_fake_ticket(fake, "27b", "orcarouter", src, dst,
                                        now_ns=now, consumed=set()))

    def test_temp_file_write_reopen_no_overwrite(self):
        p = mock_pipeline("orcarouter", "flash-next")
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            write_fake_store(folder, p["mock_journal"])
            audit = audit_fake_store(folder, "orcarouter", "flash-next")
            self.assertEqual(audit["status"], "VERIFIED_FAKE_FILES_ONLY")
            for name in (LOG_NAME, STATE_NAME):
                self.assertEqual((folder / name).stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                write_fake_store(folder, p["mock_journal"])
            self.assertEqual(audit_fake_store(folder, "orcarouter",
                                              "flash-next")["status"],
                             "VERIFIED_FAKE_FILES_ONLY")

    def test_interrupted_log_remains_blocked_and_unchanged(self):
        p = mock_pipeline("27b", "orcarouter")
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            write_fake_store(folder, p["mock_journal"], interrupt_after_log=True)
            initial = (folder / LOG_NAME).read_bytes()
            audit = audit_fake_store(folder, "27b", "orcarouter")
            self.assertEqual(audit["status"], "BLOCKED_FAKE_FILES")
            self.assertFalse(audit["resume_eligible"])
            self.assertEqual((folder / LOG_NAME).read_bytes(), initial)
            self.assertFalse((folder / STATE_NAME).exists())
            with self.assertRaises(FileExistsError):
                write_fake_store(folder, p["mock_journal"])

    def test_refuse_operating_paths_and_symlinks(self):
        p = mock_pipeline("27b", "orcarouter")
        with tempfile.TemporaryDirectory(prefix=PREFIX) as root:
            folder = Path(root)
            with self.assertRaises(ValueError):
                write_fake_store(Path("/tmp/blazux-operating-state"), p["mock_journal"])
            write_fake_store(folder, p["mock_journal"])
            state = folder / STATE_NAME
            state.unlink()
            state.symlink_to(folder / LOG_NAME)
            self.assertEqual(audit_fake_store(folder, "27b", "orcarouter")["status"],
                             "BLOCKED_FAKE_FILES")

    def test_cli_contract_and_summary(self):
        with patch("subprocess.run", side_effect=AssertionError("no Docker")):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = wizard_main(["operations", "generic", "fake-disk-contract",
                                  "--from-model", "orcarouter", "--to-model", "27b",
                                  "--json"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out.getvalue())["status"],
                             "PASS_FAKE_DISK_CONTRACT")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = wizard_main(["operations", "generic", "fake-disk-matrix",
                                  "--summary-only", "--json"])
            self.assertEqual(rc, 0)
            data = json.loads(out.getvalue())
            self.assertEqual(data["test_count"], 6 * len(SCENARIOS))
            self.assertNotIn("cases", data)
            self.assertFalse(data["real_dgx_verified"])


if __name__ == "__main__":
    unittest.main()
