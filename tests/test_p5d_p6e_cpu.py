"""P5-D/P6-E CPU-only process evidence and journal v2 proposal acceptance."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
from pathlib import Path
import subprocess
import unittest
from unittest.mock import patch

from scripts.manager.process_ownership import (
    ownership_capture, ownership_review, _parse_ss, _parse_gpu, _parse_top)
from scripts.manager.generic_journal_v2 import (
    draft_v2_event, audit_v2_draft, migration_preview, REQUIRED_V2)
from wizard.main import main as wizard_main


class P5DCPU(unittest.TestCase):
    def setUp(self):
        self.obs = {
            "status": "SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE",
            "runtime_role": "DEVELOPMENT_TRIAL",
            "observed_container": "qwen38-orcarouter-qsa62318-lmhead-v3",
            "container_id": "a" * 64,
        }
        self.inspect = {"Id": "a" * 64,
                        "Name": "/" + self.obs["observed_container"],
                        "State": {"Running": True, "Pid": 101},
                        "Image": "sha256:" + "f" * 64}

    def test_consistent_pids_never_claim_gpu_or_port_ownership(self):
        doc = ownership_review("orcarouter", self.obs, self.inspect,
                               "PID\n101\n102\n", 
                               'LISTEN 0 4096 0.0.0.0:8000 0.0.0.0:* users:(("docker-proxy",pid=201,fd=4))',
                               "102\n")
        self.assertEqual(doc["status"], "OBSERVED_PID_SETS_CONSISTENT_NOT_AUTHORIZED")
        self.assertEqual(doc["gpu_compute_pids"], [102])
        self.assertEqual(doc["host_port_8000_listener_pids"], [201])
        self.assertTrue(doc["gpu_pid_subset_of_container"])
        self.assertFalse(doc["port_process_ownership_verified"])
        self.assertFalse(doc["gpu_exclusivity_verified"])
        self.assertFalse(doc["production_released"])

    def test_foreign_gpu_and_docker_identity_drift_block(self):
        info = dict(self.inspect, Id="c" * 64)
        doc = ownership_review("orcarouter", self.obs, info, "PID\n101\n",
                               "LISTEN 0 4096 :8000 0.0.0.0:* users:((x,pid=201,fd=3))",
                               "999\n")
        self.assertIn("FOREIGN_GPU_COMPUTE_PID_OBSERVED",doc["issues"])
        self.assertIn("DOCKER_INSPECT_ID_OR_PID_MISMATCH",doc["issues"])
        self.assertEqual(doc["status"], "BLOCKED_PARTIAL_PROCESS_EVIDENCE")

    def test_missing_gpu_and_nat_denied_are_unqualified(self):
        doc = ownership_review("orcarouter", self.obs, self.inspect, "PID\n101",
                               None, "Not Supported\n")
        self.assertIn("GPU_PROCESS_QUERY_UNSUPPORTED_OR_EMPTY",doc["issues"])
        self.assertIn("PORT_8000_HOST_LISTENER_PID_UNAVAILABLE_OR_NAT",doc["issues"])

    def test_read_only_capture_uses_fixed_commands_and_never_infers_provenance(self):
        allowed = {
            "docker": json.dumps(self.inspect),
            "top": "PID\n101\n102\n",
            "ss": 'LISTEN 0 4096 0.0.0.0:8000 0.0.0.0:* users:(("docker-proxy",pid=201,fd=3))',
            "nvidia-smi": "102\n",
        }
        calls=[]
        def fake_runner(argv, **kwargs):
            calls.append(argv)
            self.assertNotIn("--rm", argv)
            self.assertNotIn("stop", argv)
            self.assertEqual(kwargs["timeout"], 6)
            key = "top" if argv[:2] == ["docker", "top"] else argv[0]
            return subprocess.CompletedProcess(argv,0,allowed[key],"")
        doc = ownership_capture(
            "orcarouter", observation_probe=lambda model: self.obs,
            runner=fake_runner)
        self.assertEqual(len(calls),4)
        self.assertTrue(doc["probe_performed"])
        self.assertFalse(doc["executed"])
        self.assertEqual(doc["status"],"OBSERVED_PID_SETS_CONSISTENT_NOT_AUTHORIZED")
        self.assertFalse(doc["real_dgx_verified"])

    def test_injected_observation_cli_review_no_runtime(self):
        bundle = dict(observation=self.obs, docker_inspect=self.inspect,
                      docker_top_stdout="PID\n101\n102\n",
                      ss_stdout="LISTEN 0 4096 127.0.0.1:8000 0.0.0.0:* users:((docker-proxy,pid=201,fd=4))",
                      gpu_stdout="102\n")
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"bundle.json"
            f.write_text(json.dumps(bundle))
            with patch("subprocess.run",side_effect=AssertionError("NO HOST PROBES")), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc=wizard_main(["operations","generic","ownership-review",
                                "--model","orcarouter","--ownership-evidence",str(f),
                                "--json"])
        self.assertEqual(rc,0)
        self.assertFalse(json.loads(out.getvalue())["port_process_ownership_verified"])


class P6ECPU(unittest.TestCase):
    def test_v2_in_memory_schema_and_chain(self):
        first = draft_v2_event("27b","flash-next",
                               source_id="a"*64,target_id="b"*64,plan_id="c"*64)
        self.assertEqual(set(first), REQUIRED_V2)
        second=draft_v2_event("27b","flash-next",source_id="a"*64,
                              target_id="b"*64,plan_id="c"*64,
                              prior=first,phase="PLANNED")
        doc=audit_v2_draft([first,second])
        self.assertEqual(doc["status"],"PASS_V2_DRAFT_CONSISTENCY")
        self.assertFalse(doc["durable"])
        self.assertFalse(doc["live_executor_available"])
        self.assertFalse(doc["approval_accepted"])

    def test_tamper_and_same_identity_rejected(self):
        first=draft_v2_event("27b","orcarouter",
                             source_id="a"*64,target_id="b"*64,plan_id="c"*64)
        forged=copy.deepcopy(first)
        forged["target_container_id"]="a"*64
        issues=audit_v2_draft([forged])["issues"]
        self.assertIn("V2_EVENT_HASH_MISMATCH",issues)
        self.assertIn("V2_IDS_OR_PLAN_INVALID",issues)
        with self.assertRaises(ValueError):
            draft_v2_event("27b","orcarouter",
                           source_id="a"*64,target_id="a"*64,plan_id="c"*64)
        with self.assertRaises(ValueError):
            draft_v2_event("orcarouter","orcarouter",
                           source_id="a"*64,target_id="b"*64,plan_id="c"*64)
        with self.assertRaises(ValueError):
            draft_v2_event("27b","orcarouter",
                           source_id="a"*64,target_id="b"*64,
                           plan_id="c"*64,phase="COMMITTED")

    def test_read_only_v1_state_never_migrates_or_admits_live(self):
        fixtures=[
            ({"status":"EMPTY","event_count":0,"issues":[]},
             "REQUIRES_APPROVED_EMPTY_V2_BOOTSTRAP"),
            ({"status":"VERIFIED","phase":"COMMITTED","event_count":3,
              "last_event_hash":"f"*64,"issues":[]},
             "REQUIRES_APPROVED_V1_ANCHOR_AND_READ_ONLY_RECONCILIATION"),
            ({"status":"BLOCKED","phase":"NEW_STARTING","issues":["DIRTY"]},
             "FREEZE_UNTRUSTED_OR_UNRESOLVED_V1"),
        ]
        for fixture,mode in fixtures:
            for source,target in [("27b","flash-next"),("orcarouter","27b")]:
                with self.subTest(mode=mode,source=source):
                    p=migration_preview(source,target,fixture)
                    self.assertEqual(p["mode"],mode)
                    self.assertEqual(p["status"],"BLOCKED_V2_MIGRATION_NOT_AUTHORIZED")
                    self.assertFalse(p["v1_journal_modified"])
                    self.assertFalse(p["v2_journal_written"])
                    self.assertFalse(p["approval_accepted"])
                    if source=="orcarouter":
                        self.assertIn("V1_JOURNAL_MODEL_SCOPE_EXCLUDES_ORCAROUTER",
                                      p["issues"])

    def test_cli_migration_preview_exit_3_and_no_file_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            f=Path(tmp)/"legacy.json"
            f.write_text(json.dumps({"status":"EMPTY","event_count":0,"issues":[]}))
            with patch("subprocess.run",side_effect=AssertionError("NO RUNTIME IO")), \
                 contextlib.redirect_stdout(io.StringIO()) as out:
                rc=wizard_main(["operations","generic","journal-v2-preview",
                                "--from-model","orcarouter","--to-model","27b",
                                "--operating-journal-evidence",str(f),"--json"])
            self.assertEqual(rc,3)
            doc=json.loads(out.getvalue())
            self.assertEqual(doc["status"],"BLOCKED_V2_MIGRATION_NOT_AUTHORIZED")
            self.assertFalse(doc["v1_journal_modified"])
            self.assertFalse(doc["v2_journal_written"])


if __name__=="__main__":
    unittest.main()
