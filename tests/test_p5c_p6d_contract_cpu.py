"""P5-C/P6-D CPU tests: no Docker, network, inference, operating writes."""
from __future__ import annotations
import contextlib
import copy
import io
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.manager.generic_operations import model_catalog
from scripts.manager.observation_binding import observation_review, observation_capture
from scripts.manager.generic_operating_gate import gate_review
from wizard.main import main as wizard_main


class P5CObservationCPU(unittest.TestCase):
    def setUp(self):
        self.model = "orcarouter"
        identity = model_catalog()["models"][self.model]
        self.name = "qwen38-orcarouter-qsa62318-lmhead-v3"
        self.service = {
            "status": "LIVE_P5_TRIAL_API_VERIFIED",
            "runtime_role": "DEVELOPMENT_TRIAL", "p5_development_trial": True,
            "observed_model": self.model,
            "expected_served_id": identity["served_id"],
            "observed_model_ids": [identity["served_id"]],
            "host_port": 8000, "checks": {"manifest": True, "api": True},
            "active_container": {
                "name": self.name, "image_id": "sha256:" + "f" * 64,
                "status": "Up", "ports": "0.0.0.0:8000->8000/tcp"},
            "issues": [], "gpu_exclusivity_verified": False,
            "port_process_ownership_verified": False,
        }
        self.resource = {
            "status": "OBSERVED_PARTIAL", "model": self.model,
            "model_repo": identity["checkpoint"],
            "api_served_id_declared": identity["served_id"],
            "model_identity_verified_by_api": False,
            "docker": {
                "status": "OBSERVED",
                "container": {"name": self.name, "id": "a" * 64,
                              "image_id": "sha256:" + "f" * 64, "running": True}},
        }

    def test_trial_observations_correlate_without_release(self):
        doc = observation_review(self.model, self.service, self.resource)
        self.assertEqual(doc["status"], "SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE")
        self.assertEqual(doc["runtime_role"], "DEVELOPMENT_TRIAL")
        self.assertEqual(doc["container_id"], "a" * 64)
        self.assertFalse(doc["gpu_exclusivity_verified"])
        self.assertFalse(doc["port_process_ownership_verified"])
        self.assertFalse(doc["benchmark_verified"])
        self.assertFalse(doc["production_released"])

    def test_mismatch_does_not_promote_trial(self):
        for change, issue in (
            (lambda s,r: r["docker"]["container"].update(id="bad"), "FULL_CONTAINER_ID_UNOBSERVED"),
            (lambda s,r: r["docker"]["container"].update(name="wrong"), "SERVICE_RESOURCE_CONTAINER_NAME_DRIFT"),
            (lambda s,r: r.update(api_served_id_declared="unmatched"), "RESOURCE_DECLARED_API_ID_MISMATCH"),
            (lambda s,r: s.update(observed_model_ids=["wrong"]), "API_MODEL_LIST_UNBOUND"),
            (lambda s,r: s.update(runtime_role="CANONICAL"), "SERVICE_ROLE_UNOBSERVED_OR_CONTRADICTORY"),
            (lambda s,r: s.update(status="BLOCKED"), "SERVICE_API_NOT_VERIFIED"),
        ):
            with self.subTest(issue=issue):
                s,r = copy.deepcopy(self.service),copy.deepcopy(self.resource)
                change(s,r)
                result = observation_review(self.model,s,r)
                self.assertEqual(result["status"],"BLOCKED")
                self.assertIn(issue,result["issues"])

    def test_canonical_role_requires_exact_container(self):
        identity = model_catalog()["models"]["27b"]
        s = copy.deepcopy(self.service);r=copy.deepcopy(self.resource)
        s.update(runtime_role="CANONICAL",p5_development_trial=False,
                 status="LIVE_SERVICE_VERIFIED",observed_model="27b",
                 expected_served_id=identity["served_id"],
                 observed_model_ids=[identity["served_id"]])
        s["active_container"]["name"]=identity["container"]
        r.update(model="27b",model_repo=identity["checkpoint"],
                 api_served_id_declared=identity["served_id"])
        r["docker"]["container"]["name"]=identity["container"]
        self.assertEqual(observation_review("27b",s,r)["issues"],[])
        s["active_container"]["name"]="qwen38-27b-trial"
        self.assertIn("CANONICAL_CONTAINER_NAME_MISMATCH",
                      observation_review("27b",s,r)["issues"])

    def test_injected_readonly_capture_never_calls_runtime_mutation(self):
        with patch("subprocess.run",side_effect=AssertionError("no external command")), \
             patch("subprocess.Popen",side_effect=AssertionError("no subprocess")):
            result=observation_capture(
                self.model,service_probe=lambda: self.service,
                resource_probe=lambda *,model: self.resource)
        self.assertEqual(result["status"],"SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE")
        self.assertTrue(result["probe_performed"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["scope"],"READ_ONLY_SEQUENTIAL_PROBES_NOT_ATOMIC")

    def test_cli_review_from_json_files(self):
        with tempfile.TemporaryDirectory() as root:
            a,b=Path(root)/"service.json",Path(root)/"resource.json"
            a.write_text(json.dumps(self.service));b.write_text(json.dumps(self.resource))
            with patch("subprocess.run",side_effect=AssertionError("no Docker")):
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    rc=wizard_main(["operations","generic","observation-review",
                                    "--model",self.model,"--service-evidence",str(a),
                                    "--resource-evidence",str(b),"--json"])
            self.assertEqual(rc,0)
            self.assertFalse(json.loads(out.getvalue())["real_dgx_verified"])


class P6DGateCPU(unittest.TestCase):
    def setUp(self):
        reg=model_catalog()["models"]
        self.source="27b";self.target="flash-next"
        self.service={"observed_model":self.source,"status":"LIVE_SERVICE_VERIFIED",
                      "runtime_role":"CANONICAL","p5_development_trial":False,
                      "expected_served_id":reg[self.source]["served_id"],
                      "checks":{"api":True},"host_port":8000,
                      "gpu_exclusivity_verified":True,
                      "port_process_ownership_verified":True}
        self.journal={"status":"VERIFIED","issues":[]}
        self.approval={"kind":"INDEPENDENT_OPERATOR_DOWNTIME_APPROVAL",
                       "scope":"EXACT_MODEL_PAIR_AND_CONTAINER_IDS",
                       "source_model":self.source,"target_model":self.target,
                       "source_container_id":"a"*64,"target_container_id":"b"*64,
                       "host_port":8000,"plan_id":"c"*64,
                       "expires_at_utc":"2026-11-10T03:00:00Z",
                       "nonce_unused_independently_verified":True}

    def review(self):
        return gate_review(self.source,self.target,self.service,"a"*64,"b"*64,
                           self.journal,self.approval,
                           now_utc="2026-11-10T02:00:00Z")

    def test_even_perfect_supplied_json_cannot_authorize_execution(self):
        d=self.review()
        self.assertTrue(d["structural_fields_consistent"])
        self.assertEqual(d["status"],"BLOCKED_LIVE_EXECUTOR_NOT_QUALIFIED")
        self.assertFalse(d["approval_accepted"])
        self.assertFalse(d["operations_enabled"])
        self.assertFalse(d["resume_eligible"])
        self.assertIn("NO_INDEPENDENT_APPROVAL_AUTHENTICATION",d["issues"])
        self.assertIn("NO_QUALIFIED_GENERIC_OPERATING_EXECUTOR",d["issues"])

    def test_trials_unsupported_old_journal_and_clock_expiry(self):
        d=gate_review("orcarouter","27b",{},None,None,{},{} )
        self.assertIn("LEGACY_JOURNAL_ORCAROUTER_SCHEMA_UNSUPPORTED",d["issues"])
        self.assertFalse(d["structural_fields_consistent"])
        self.approval["expires_at_utc"]="2026-11-10T01:00:00Z"
        self.assertIn("APPROVAL_EXPIRY_NOT_INDEPENDENTLY_VERIFIED",self.review()["issues"])

    def test_replay_source_drift_or_unresolved_journal_block(self):
        self.approval["nonce_unused_independently_verified"]=False
        self.assertIn("DURABLE_REPLAY_FENCE_UNVERIFIED",self.review()["issues"])
        self.approval["nonce_unused_independently_verified"]=True
        self.journal["status"]="BLOCKED"
        self.assertIn("OPERATING_JOURNAL_UNRESOLVED_OR_UNTRUSTED",self.review()["issues"])
        self.journal["status"]="VERIFIED"
        self.service["gpu_exclusivity_verified"]=False
        self.assertIn("GPU_EXCLUSIVITY_UNVERIFIED",self.review()["issues"])

    def test_cli_never_accepts_the_gate(self):
        with contextlib.redirect_stdout(io.StringIO()) as out:
            rc=wizard_main(["operations","generic","operating-gate-review",
                            "--from-model","orcarouter","--to-model","27b","--json"])
        self.assertEqual(rc,3)
        result=json.loads(out.getvalue())
        self.assertEqual(result["status"],"BLOCKED_LIVE_EXECUTOR_NOT_QUALIFIED")
        self.assertFalse(result["executed"])


if __name__=="__main__":
    unittest.main()
