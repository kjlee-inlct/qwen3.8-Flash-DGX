"""Pure CPU tests of operating switch crash/journal evidence reconciliation."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.manager.operational_audit import inspect_journal
from scripts.manager.service_journal import append_transition, read_snapshot
from scripts.manager import operational_executor as executor
from scripts.manager import operational_switch as preview
import test_operational_executor_cpu as fake_module


SHA = "a" * 64


class OperatingJournalAuditCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.folder = self.root / "journal"

    def tearDown(self):
        self.temp.cleanup()

    def append(self, phase, last=None):
        last = last or read_snapshot(self.folder)
        return append_transition(
            self.folder, phase=phase,
            from_model="27b", to_model="flash-next",
            observed_model="27b", plan_id=SHA,
            expected_previous_hash=last["event_hash"] if last else None,
        )

    def test_brand_new_root_has_no_past_state(self):
        self.assertEqual(inspect_journal(self.root)["status"], "EMPTY")

    def test_unresolved_plan_blocks(self):
        self.append("OBSERVED")
        self.append("PLANNED")
        data = inspect_journal(self.root)
        self.assertEqual(data["status"], "BLOCKED")
        self.assertIn("UNRESOLVED_OPERATING_SWITCH_JOURNAL", data["issues"])

    def test_closed_cancelled_transaction_is_verified(self):
        self.append("OBSERVED")
        self.append("PLANNED")
        self.append("CANCELLED")
        data = inspect_journal(self.root)
        self.assertEqual(data["status"], "VERIFIED")
        self.assertEqual(data["phase"], "CANCELLED")
        self.assertEqual(data["event_count"], 3)

    def test_last_event_append_without_snapshot_is_blocked(self):
        self.append("OBSERVED")
        self.append("PLANNED")
        old = (self.folder / "service-state.json").read_bytes()
        self.append("CANCELLED")
        (self.folder / "service-state.json").write_bytes(old)
        self.assertIn("OPERATING_JOURNAL_UNTRUSTED:",
                      inspect_journal(self.root)["issues"][0])

    def test_missing_event_log_blocks_even_if_snapshot_looks_committed(self):
        self.append("OBSERVED")
        (self.folder / "service-events.jsonl").unlink()
        self.assertIn("OPERATING_JOURNAL_SNAPSHOT_LOG_MISMATCH",
                      inspect_journal(self.root)["issues"])

    def test_modified_journal_hash_is_blocked(self):
        self.append("OBSERVED")
        event_log = self.folder / "service-events.jsonl"
        events = event_log.read_text().replace('"event_hash": "', '"event_hash": "f')
        event_log.write_text(events)
        self.assertEqual(inspect_journal(self.root)["status"], "BLOCKED")

    def test_committed_without_receipt_blocks_new_switch(self):
        for phase in ("OBSERVED", "PLANNED", "OLD_STOPPING",
                      "OLD_STOPPED", "NEW_STARTING", "NEW_VERIFYING",
                      "COMMITTED"):
            self.append(phase)
        data = inspect_journal(self.root)
        self.assertIn("COMMITTED_OPERATING_RECEIPT_MISSING", data["issues"])

    def test_malformed_receipt_does_not_get_committed_pass(self):
        for phase in ("OBSERVED", "PLANNED", "OLD_STOPPING",
                      "OLD_STOPPED", "NEW_STARTING", "NEW_VERIFYING",
                      "COMMITTED"):
            self.append(phase)
        receipt = self.root / ("completed-" + SHA + ".json")
        receipt.write_text(json.dumps({"status": "PASS"}))
        self.assertEqual(inspect_journal(self.root)["status"], "BLOCKED")

    def test_symlinked_journal_directory_blocks_without_writes(self):
        other = self.root / "other"
        other.mkdir()
        self.folder.symlink_to(other, target_is_directory=True)
        self.assertIn("OPERATING_JOURNAL_DIRECTORY_SYMLINK",
                      inspect_journal(self.root)["issues"])

    def test_fake_success_receipt_matches_journal(self):
        fake = fake_module.FakeOperatingTransactionCPU(
            "test_27b_to_flash_success_and_no_p3_receipt_mutation")
        fake.setUp()
        try:
            rc, result = fake.execute()
            self.assertEqual(rc, 0, result)
            self.assertEqual(inspect_journal(fake.fake.ops)["status"], "VERIFIED")
            self.assertEqual(inspect_journal(fake.fake.ops)["phase"], "COMMITTED")
            self.assertEqual(fake.planner("27b", root=fake.fake.ops)["status"],
                             "READY_FOR_OPERATOR_REVIEW_ONLY")
        finally:
            fake.tearDown()

    def test_append_without_receipt_prevents_another_preview(self):
        fake = fake_module.FakeOperatingTransactionCPU(
            "test_27b_to_flash_success_and_no_p3_receipt_mutation")
        fake.setUp()
        try:
            self.assertEqual(fake.execute()[0], 0)
            paths = list(fake.fake.ops.glob("completed-*.json"))
            self.assertEqual(len(paths), 1)
            paths[0].unlink()
            after = fake.planner("27b", root=fake.fake.ops)
            self.assertEqual(after["status"], "BLOCKED")
            self.assertIn("COMMITTED_OPERATING_RECEIPT_MISSING", after["issues"])
        finally:
            fake.tearDown()


if __name__ == "__main__":
    unittest.main()
