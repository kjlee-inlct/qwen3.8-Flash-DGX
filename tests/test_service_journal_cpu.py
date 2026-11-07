"""CPU-only tests for durable service transition manifest/journal."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.manager.service_journal import append_transition, read_snapshot


class ServiceJournalCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "state"

    def test_append_only_observation_and_stale_generation_guard(self):
        first = append_transition(self.root, phase="OBSERVED",
                                  from_model=None, to_model=None,
                                  observed_model="flash-next",
                                  expected_previous_hash=None)
        self.assertEqual(first["api_host_port"], 8000)
        self.assertEqual(first["max_active_gpu_models"], 1)
        self.assertTrue(first["live_state_revalidation_required"])
        with self.assertRaises(RuntimeError):
            append_transition(self.root, phase="PLANNED",
                              from_model="flash-next", to_model="27b",
                              observed_model="flash-next",
                              expected_previous_hash=None)
        second = append_transition(self.root, phase="PLANNED",
                                   from_model="flash-next", to_model="27b",
                                   observed_model="flash-next",
                                   expected_previous_hash=first["event_hash"],
                                   plan_id="f" * 64)
        self.assertEqual(read_snapshot(self.root)["event_hash"], second["event_hash"])
        lines = (self.root / "service-events.jsonl").read_text().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[0])["phase"], "OBSERVED")
        self.assertEqual(json.loads(lines[1])["previous_hash"], first["event_hash"])

    def test_stop_before_start_is_enforced_by_state_machine(self):
        initial = append_transition(self.root, phase="OBSERVED",
                                    from_model=None, to_model=None,
                                    observed_model="flash-next",
                                    expected_previous_hash=None)
        with self.assertRaises(ValueError):
            append_transition(self.root, phase="NEW_STARTING",
                              from_model="flash-next", to_model="27b",
                              observed_model="flash-next",
                              expected_previous_hash=initial["event_hash"])

    def test_no_unknown_model_or_bad_plan_id(self):
        with self.assertRaises(ValueError):
            append_transition(self.root, phase="OBSERVED",
                              from_model=None, to_model=None,
                              observed_model="orcarouter",
                              expected_previous_hash=None)
        with self.assertRaises(ValueError):
            append_transition(self.root, phase="OBSERVED",
                              from_model=None, to_model=None,
                              observed_model="flash-next",
                              expected_previous_hash=None, plan_id="../bad")

    def test_corrupt_snapshot_never_reinterpreted_as_clean(self):
        self.root.mkdir()
        (self.root / "service-state.json").write_text("{invalid json")
        with self.assertRaises(ValueError):
            read_snapshot(self.root)
        with self.assertRaises(ValueError):
            append_transition(self.root, phase="OBSERVED",
                              from_model=None, to_model=None,
                              observed_model="flash-next",
                              expected_previous_hash=None)


if __name__ == "__main__":
    unittest.main()
