"""P5 retired test containers: narrow cleanup contract and live verify routing."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest
from unittest.mock import patch

from scripts.manager import p5_trial_cleanup as clean
from scripts.manager import p5_live_trial as live


def done(args, rc=0, output="", errors=""):
    return subprocess.CompletedProcess(args, rc, output, errors)


class P5TrialRetirementCPU(unittest.TestCase):
    def test_allowlist_omits_live_v3_and_unrelated_containers(self):
        self.assertNotIn(live.TARGET, clean.ALLOWED)
        self.assertNotIn("qwen38-27b", clean.ALLOWED)
        self.assertEqual(set(clean.ALLOWED), {
            "qwen38-orcarouter",
            "qwen38-orcarouter-qsa62318",
            "qwen38-orcarouter-qsa62318-lmhead",
        })

    def test_plan_is_only_exact_failed_candidates_and_read_only(self):
        active = {"name": live.TARGET, "container_id": "a"*64,
                  "image_id": "sha256:"+"b"*64, "api_model_id": live.ALIAS}
        old = {"name": clean.ALLOWED[0], "container_id": "c"*64,
               "image_id": "sha256:"+"d"*64, "exit_code": 1}
        observed = []
        def candidate(name):
            observed.append(name)
            return old if name == clean.ALLOWED[0] else None
        with patch.object(clean, "_read_live", return_value=active), \
             patch.object(clean, "_candidate", side_effect=candidate), \
             patch.object(live, "command",
                          side_effect=AssertionError("no Docker mutation")):
            result = clean.plan(now=900000)
        self.assertEqual(result["status"], "READY_TO_APPROVE")
        self.assertEqual(result["targets"], [old])
        self.assertEqual(observed, list(clean.ALLOWED))
        self.assertTrue(result["preserve_live_v3"])
        self.assertFalse(result["executed"])

    def test_foreign_or_running_container_never_passes_candidate_identity(self):
        doc = {"Name": "/" + clean.ALLOWED[0], "Id": "c"*64,
               "Image": "sha256:"+"d"*64,
               "State": {"Running": True, "Status": "running", "ExitCode": 0},
               "Config": {"Cmd": [live.MODEL_IN_CONTAINER,
                                 "--served-model-name", live.ALIAS,
                                 "--port", "8000"]},
               "HostConfig": {"PortBindings": {
                   "8000/tcp": [{"HostPort": "8000"}]}},
               "Mounts": [{"Type": "bind", "Source": str(live.CACHE),
                           "Destination": "/hf", "RW": False}]}
        with patch.object(clean, "_inspect_if_exists", return_value=doc):
            with self.assertRaisesRegex(ValueError, "UNVERIFIED_OR_NONFAILED"):
                clean._candidate(clean.ALLOWED[0])
        doc["State"] = {"Running": False, "Status": "exited", "ExitCode": 1}
        with patch.object(clean, "_inspect_if_exists", return_value=doc):
            self.assertEqual(clean._candidate(clean.ALLOWED[0])["exit_code"], 1)
        with self.assertRaisesRegex(ValueError, "NOT_ALLOWLISTED"):
            clean._candidate(live.TARGET)

    def test_cleanup_rejects_missing_ack_before_any_docker(self):
        with patch.object(live, "command", side_effect=AssertionError("Docker called")):
            result = clean.execute("a"*64, "not-acknowledged")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["executed"])

    def test_cleanup_writes_evidence_and_only_removes_a_failed_container(self):
        active = {"name": live.TARGET, "container_id": "a"*64,
                  "image_id": "sha256:"+"b"*64, "api_model_id": live.ALIAS}
        failed = {"name": clean.ALLOWED[0], "container_id": "c"*64,
                  "image_id": "sha256:"+"d"*64, "exit_code": 1}
        expiry = time.time() + 120
        planned = {"status": "READY_TO_APPROVE", "plan_id": "e"*64,
                   "expires_at_epoch_seconds": expiry,
                   "active": active, "targets": [failed]}
        removed = []
        def command(argv, timeout=30):
            if argv[:2] == ["docker", "logs"]:
                return done(argv, output="Traceback: previous P5 failure")
            if argv[:2] == ["docker", "rm"]:
                removed.append(argv[2])
                return done(argv)
            raise AssertionError(argv)
        with tempfile.TemporaryDirectory() as temp, \
             patch.object(live, "STATE", Path(temp)), \
             patch.object(clean, "plan", return_value=planned), \
             patch.object(clean, "_read_live", return_value=active), \
             patch.object(clean, "_candidate", return_value=failed), \
             patch.object(clean, "_inspect_if_exists", return_value=None), \
             patch.object(live, "command", side_effect=command):
            result = clean.execute("e"*64, clean.ACK)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["deleted"], [failed["name"]])
            self.assertEqual(removed, [failed["name"]])
            self.assertEqual(len(list((Path(temp)/"cleanup").glob("*.log"))), 1)
            self.assertEqual(len(list((Path(temp)/"cleanup").glob("*.json"))), 1)

    def test_p5_trial_cli_exposes_safe_cleanup_and_live_inference(self):
        with patch.object(clean, "plan", return_value={
            "status": "NOTHING_TO_CLEAN", "issues": []}), \
             contextlib.redirect_stdout(io.StringIO()) as out:
            code = live.main(["cleanup-plan", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["status"], "NOTHING_TO_CLEAN")
        with patch.object(live, "verify_live", return_value={
            "status": "PASS_LIVE_INFERENCE", "inference_verified": True,
            "issues": []}), contextlib.redirect_stdout(io.StringIO()) as out:
            code = live.main(["verify", "--json"])
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out.getvalue())["inference_verified"])


if __name__ == "__main__":
    unittest.main()
