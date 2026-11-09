"""P6 Fake-DGX executor/journal bridge: hashes cannot imply live provenance."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import unittest
from unittest.mock import patch

from scripts.manager.mock_transaction_pipeline import (
    audit_mock_journal, mock_pipeline, mock_plan_id,
)
from scripts.manager.transition_safety import FAULTS, EXPECTED
from scripts.manager.service_manifest import policy
from wizard.main import main as wizard_main


class PipelineCPU(unittest.TestCase):
    def test_six_directional_pairs_and_all_faults(self):
        names = ("27b", "flash-next", "orcarouter")
        for source in names:
            for target in names:
                if source == target:
                    continue
                for fault in FAULTS:
                    with self.subTest(source=source, target=target, fault=fault):
                        doc = mock_pipeline(source, target, fault=fault)
                        self.assertEqual(doc["transition_status"], EXPECTED[fault])
                        self.assertFalse(doc["executed"])
                        self.assertFalse(doc["durable_journal_verified"])
                        self.assertFalse(doc["live_executor_available"])
                        self.assertFalse(doc["production_released"])
                        self.assertEqual(len(doc["non_authorizing_plan_id"]), 64)
                        self.assertEqual(doc["journal_audit"]["event_count"],
                                         len(doc["mock_journal"]))
                        self.assertEqual(doc["invariant_issues"], [])
                        self.assertTrue(all(
                            ev["host_port"] == 8000 and
                            ev["max_active_gpu_models"] == 1
                            for ev in doc["mock_journal"]))

    def test_success_and_recovery_are_terminal_but_not_live(self):
        for fault, phase in (("none", "COMMITTED"),
                             ("target-start", "RESTORED"),
                             ("target-api", "RESTORED")):
            doc = mock_pipeline("orcarouter", "27b", fault=fault)
            self.assertEqual(doc["journal_audit"]["status"], "VERIFIED_MOCK_TERMINAL")
            self.assertEqual(doc["journal_audit"]["last_phase"], phase)
            self.assertEqual(doc["status"], "PASS_FAKE_PIPELINE_CONTRACT")
            self.assertFalse(doc["journal_audit"]["resume_eligible"])

    def test_port_and_recovery_failures_cannot_be_audited_as_safe(self):
        for fault in ("port-release", "source-stop", "restore-source"):
            doc = mock_pipeline("27b", "flash-next", fault=fault)
            self.assertEqual(doc["journal_audit"]["status"], "BLOCKED_MOCK_JOURNAL")
            self.assertEqual(doc["status"],
                             "EXPECTED_UNSAFE_FAKE_TERMINAL" if fault != "source-stop"
                             else "BLOCKED_FAKE_PIPELINE_CONTRACT")
            self.assertIn("MOCK_JOURNAL_UNRESOLVED_TRANSITION",
                          doc["journal_audit"]["issues"])

    def test_tamper_and_truncated_hash_chain_block(self):
        doc = mock_pipeline("27b", "orcarouter")
        events = copy.deepcopy(doc["mock_journal"])
        self.assertEqual(audit_mock_journal(events, "27b", "orcarouter")["status"],
                         "VERIFIED_MOCK_TERMINAL")
        events[1]["synthetic_action"] = "forged"
        audit = audit_mock_journal(events, "27b", "orcarouter")
        self.assertIn("MOCK_JOURNAL_HASH_MISMATCH", audit["issues"])
        events = copy.deepcopy(doc["mock_journal"])
        del events[2]
        audit = audit_mock_journal(events, "27b", "orcarouter")
        self.assertIn("MOCK_JOURNAL_CHAIN_OR_INDEX_MISMATCH", audit["issues"])
        events = copy.deepcopy(doc["mock_journal"])
        events[2]["port_8000_owner"] = "flash-next"
        audit = audit_mock_journal(events, "27b", "orcarouter")
        self.assertIn("ONE_MODEL_OR_PORT_OWNER_INVARIANT_VIOLATION", audit["issues"])

    def test_future_model_dynamic_and_invalid_inputs_block(self):
        cfg = json.loads(json.dumps(policy()))
        cfg["models"]["future"] = {
            "checkpoint": "future/checkpoint",
            "container_name": "future-container",
            "served_id": "future-id"}
        doc = mock_pipeline("orcarouter", "future", config=cfg)
        self.assertEqual(doc["status"], "PASS_FAKE_PIPELINE_CONTRACT")
        self.assertEqual(doc["journal_audit"]["status"], "VERIFIED_MOCK_TERMINAL")
        with self.assertRaises(ValueError):
            mock_pipeline("27b", "27b")
        with self.assertRaises(ValueError):
            mock_plan_id("unregistered", "27b")

    def test_cli_pipeline_never_calls_docker(self):
        with patch("subprocess.run", side_effect=AssertionError("NO RUNTIME I/O")), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc = wizard_main(["operations", "generic", "pipeline-mock",
                              "--from-model", "orcarouter",
                              "--to-model", "27b", "--json"])
        self.assertEqual(rc, 0)
        doc = json.loads(out.getvalue())
        self.assertEqual(doc["status"], "PASS_FAKE_PIPELINE_CONTRACT")
        self.assertFalse(doc["executed"])
        self.assertFalse(doc["durable_journal_verified"])
        self.assertFalse(doc["production_released"])


if __name__ == "__main__":
    unittest.main()
