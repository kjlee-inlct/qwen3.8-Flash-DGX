"""P1 Wizard CPU-only state machine, approval and evidence tests. All backends mocked."""
import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p1_wizard as wiz


IMAGE_ID = "sha256:" + "b" * 64
REV = "a" * 40


class WizardCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="p1-wizard-")
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.inv = {
            "status": "PASS", "errors": [], "name_conflict": False,
            "port_conflict": False, "containers": [],
            "disk": {"free_bytes": 500_000_000_000},
        }
        self.chk = {
            "model_repo": wiz.MODEL, "revision": REV,
            "cache_root": str(self.path), "source_complete": True,
            "hybrid_ready": False, "source_issues": [],
            "hybrid_issues": ["hybrid_snapshot_missing"], "state": "SOURCE_COMPLETE",
        }
        self.img = {"id": IMAGE_ID, "vllm_base": "v0.32", "ready": True}

    @contextlib.contextmanager
    def fake_facts(self, *, active=False):
        with patch.object(wiz, "inspect_host", return_value=self.inv), \
             patch.object(wiz, "audit_checkpoint", return_value=self.chk), \
             patch.object(wiz, "inspect_image", return_value=self.img), \
             patch.object(wiz, "transfer_running",
                          return_value=(active, "active_model_transfer_or_setup" if active else None)):
            yield

    def plan(self, action="prepare", active=False):
        with self.fake_facts(active=active):
            return wiz.build_plan(action, cache_root=self.path)

    def running(self):
        self.chk["hybrid_ready"] = True
        self.chk["hybrid_issues"] = []
        self.inv["name_conflict"] = True
        self.inv["port_conflict"] = True
        self.inv["containers"] = [{
            "name": wiz.NAME, "image_id": IMAGE_ID, "status": "Up 2 minutes",
            "ports": "0.0.0.0:8000->8000/tcp",
        }]

    def test_prepare_plan_ready_after_source_download(self):
        p = self.plan()
        self.assertEqual(p["status"], "READY_TO_REQUEST_APPROVAL")
        self.assertFalse(p["executed"])
        self.assertTrue(len(p["plan_id"]) == 64)

    def test_incomplete_checkpoint_blocks_every_action(self):
        self.chk["source_complete"] = False
        for action in wiz.ACTIONS:
            with self.subTest(action=action):
                self.assertIn("checkpoint_downloading_or_incomplete",
                              self.plan(action)["issues"])

    def test_low_disk_blocks_hybrid_prepare(self):
        self.inv["disk"]["free_bytes"] = 10 * 1024**3
        self.assertIn("insufficient_free_disk_for_hybrid_preparation",
                      self.plan("prepare")["issues"])

    def test_active_transfer_blocks_mutation(self):
        for action in ("prepare", "start"):
            with self.subTest(action=action):
                self.assertIn("active_model_transfer_or_setup",
                              self.plan(action, active=True)["issues"])

    def test_hybrid_prepared_prohibits_reprep(self):
        self.chk["hybrid_ready"] = True
        self.assertEqual(self.plan("prepare")["status"], "BLOCKED")

    def test_wrong_image_base_blocks_launch(self):
        self.chk["hybrid_ready"] = True
        self.img["ready"] = False
        self.assertIn("vllm_032_image_missing_or_wrong_label",
                      self.plan("start")["issues"])

    def test_name_and_port_collision_blocks_start(self):
        self.chk["hybrid_ready"] = True
        self.inv["name_conflict"] = self.inv["port_conflict"] = True
        p = self.plan("start")
        self.assertIn("name_occupied", p["issues"])
        self.assertIn("port_8000_occupied", p["issues"])

    def test_healthy_running_service_allows_verify_plan(self):
        self.running()
        p = self.plan("verify")
        self.assertEqual(p["status"], "READY_TO_REQUEST_APPROVAL", p["issues"])

    def test_wrong_serving_image_blocks_verify(self):
        self.running()
        self.inv["containers"][0]["image_id"] = "sha256:" + "c" * 64
        self.assertIn("container_image_id_mismatch", self.plan("verify")["issues"])

    def test_wrong_port_mapping_blocks_verify(self):
        self.running()
        self.inv["containers"][0]["ports"] = "127.0.0.1:9000->8000/tcp"
        self.assertIn("target_port_mapping_missing", self.plan("verify")["issues"])

    def test_stable_approval_hash_changes_when_revision_changes(self):
        a = self.plan("prepare")["plan_id"]
        self.assertEqual(a, self.plan("prepare")["plan_id"])
        self.chk["revision"] = "d" * 40
        self.assertNotEqual(a, self.plan("prepare")["plan_id"])

    def test_invalid_approval_never_calls_shell(self):
        p = self.plan("prepare")
        with self.fake_facts(), patch.object(wiz, "perform") as perform:
            rc, result = wiz.execute_approved(
                p, "incorrect-id", cache_root=self.path,
                evidence_dir=self.path / "records")
        self.assertEqual(rc, 3)
        self.assertFalse(result["executed"])
        perform.assert_not_called()

    def test_stale_preflight_blocks_execution(self):
        p = self.plan("prepare")
        self.chk["revision"] = "f" * 40
        with self.fake_facts(), patch.object(wiz, "perform") as perform:
            rc, result = wiz.execute_approved(
                p, p["plan_id"], cache_root=self.path,
                evidence_dir=self.path / "records")
        self.assertEqual(rc, 3)
        self.assertIn("preflight_changed", result["issues"])
        perform.assert_not_called()

    def test_approved_prepare_executes_fixed_script_and_writes_evidence(self):
        p = self.plan("prepare")
        calls = []
        def runner(argv, **kwargs):
            calls.append((argv, kwargs))
            return subprocess.CompletedProcess(argv, 0, "", "")
        with self.fake_facts():
            rc, result = wiz.execute_approved(
                p, p["plan_id"], cache_root=self.path,
                evidence_dir=self.path / "records", runner=runner)
        self.assertEqual(rc, 0, result)
        self.assertEqual(result["status"], "PREPARED_PENDING_AUDIT")
        self.assertTrue(calls[0][0][0].endswith("/scripts/prepare-hybrid.sh"))
        self.assertNotIn("DOCKER_EXTRA", {k for k, v in calls[0][1]["env"].items() if v})
        evidence = json.loads(Path(result["evidence"]).read_text())
        self.assertEqual(evidence["model_revision"], REV)
        self.assertEqual(evidence["approval"], "explicit_plan_id")

    def test_approved_start_does_not_call_setup_or_download(self):
        self.chk["hybrid_ready"] = True
        p = self.plan("start")
        commands = []
        def runner(argv, **kwargs):
            commands.append(argv)
            return subprocess.CompletedProcess(argv, 0, "", "")
        with self.fake_facts():
            rc, result = wiz.execute_approved(
                p, p["plan_id"], cache_root=self.path,
                evidence_dir=self.path / "records", runner=runner)
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "STARTED_PENDING_HEALTH")
        self.assertEqual(commands[0][1:], ["serve", "default"])

    def test_failed_command_generates_failure_evidence(self):
        p = self.plan("prepare")
        def runner(argv, **_):
            return subprocess.CompletedProcess(argv, 2, "", "")
        with self.fake_facts():
            rc, result = wiz.execute_approved(
                p, p["plan_id"], cache_root=self.path,
                evidence_dir=self.path / "records", runner=runner)
        self.assertEqual(rc, 2)
        self.assertEqual(result["status"], "FAIL")
        evidence = json.loads(Path(result["evidence"]).read_text())
        self.assertEqual(evidence["error_type"], "RuntimeError")

    def test_explicit_env_discards_injected_launch_flags(self):
        with patch.dict(os.environ, {"DOCKER_EXTRA": "--privileged",
                                     "EXTRA": "--trust-remote-code",
                                     "LD_PRELOAD": "/tmp/fake.so"}):
            env = wiz._safe_env(str(self.path))
        self.assertEqual(env["DOCKER_EXTRA"], "")
        self.assertEqual(env["EXTRA"], "")
        self.assertNotIn("LD_PRELOAD", env)
        self.assertEqual(env["PORT"], "8000")
        self.assertEqual(env["MODEL"], wiz.MODEL)

    def test_cli_status_does_not_execute(self):
        p = self.plan()
        buffer = io.StringIO()
        with patch.object(wiz, "build_plan", return_value=p), \
             patch.object(wiz, "perform") as perform, \
             contextlib.redirect_stdout(buffer):
            code = wiz.main(["status"])
        self.assertEqual(code, 0)
        perform.assert_not_called()
        self.assertIn("plan_id", buffer.getvalue())

    def test_verify_probe_checks_tools_and_vision_without_live_api(self):
        def fake_http(url, **kwargs):
            body = kwargs["payload"]
            if "tools" in body:
                return {"choices": [{"message": {"tool_calls": [{"id": "call_1"}]}}]}
            return {"choices": [{"message": {"content": "pong"}}]}
        with patch.object(wiz, "http_json", side_effect=fake_http):
            for kind in ("text", "tools", "vision"):
                self.assertEqual(wiz._chat_probe(kind=kind)["status"], "PASS")

    def test_verify_empty_text_fails(self):
        with patch.object(wiz, "http_json", return_value={"choices": [
            {"message": {"content": ""}}]}):
            with self.assertRaises(ValueError):
                wiz._chat_probe(kind="text")

    def test_default_blazux_completion_is_a_separate_probe(self):
        with patch.object(wiz, "http_json", return_value={
            "choices": [{"text": " Paris."}]
        }) as mock_http:
            self.assertEqual(wiz._default_completion()["status"], "PASS")
            self.assertTrue(mock_http.call_args.args[0].endswith("/v1/completions"))
            self.assertEqual(mock_http.call_args.kwargs["payload"]["max_tokens"], 12)

    def test_default_completion_empty_is_not_pass(self):
        with patch.object(wiz, "http_json", return_value={
            "choices": [{"text": ""}]
        }):
            self.assertEqual(wiz._checked_probe(wiz._default_completion)["error_code"],
                             "completion_text_missing")

    def test_wizard_verification_separates_blazux_baseline_and_optional_features(self):
        def fake_probe(*, kind="text", **_):
            if kind == "vision":
                raise ValueError("response_content_missing")
            return {"status": "PASS", "kind": kind}
        with patch.object(wiz, "require_model", return_value={"health": "PASS"}), \
             patch.object(wiz, "_default_completion", return_value={"status": "PASS"}), \
             patch.object(wiz, "_chat_probe", side_effect=fake_probe):
            data = wiz.verify_api()
        self.assertEqual(data["status"], "PARTIAL")
        self.assertEqual(data["baseline_status"], "PASS")
        self.assertEqual(data["extended_status"], "FAIL")
        self.assertEqual(data["probes"]["default_completion"]["status"], "PASS")
        self.assertEqual(data["probes"]["vision"]["error_code"], "response_content_missing")

    def test_default_chat_failure_skips_extra_probes(self):
        calls = []
        def fake_chat(*, kind="text", **_):
            calls.append(kind)
            raise ValueError("response_content_missing")
        with patch.object(wiz, "require_model", return_value={"health": "PASS"}), \
             patch.object(wiz, "_default_completion", return_value={"status": "PASS"}), \
             patch.object(wiz, "_chat_probe", side_effect=fake_chat):
            data = wiz.verify_api()
        self.assertEqual(data["status"], "FAIL")
        self.assertEqual(data["baseline_status"], "FAIL")
        self.assertEqual(data["extended_status"], "NOT_RUN")
        self.assertEqual(calls, ["text"])

    def test_all_baseline_and_extended_features_pass(self):
        with patch.object(wiz, "require_model", return_value={"health": "PASS"}), \
             patch.object(wiz, "_default_completion", return_value={"status": "PASS"}), \
             patch.object(wiz, "_chat_probe", return_value={"status": "PASS"}):
            data = wiz.verify_api()
        self.assertEqual(data["status"], "PASS")
        self.assertEqual(data["baseline_status"], "PASS")
        self.assertEqual(data["extended_status"], "PASS")

    def test_benchmark_plan_checks_parameter_bounds(self):
        with self.fake_facts():
            with self.assertRaises(ValueError):
                wiz.build_plan("benchmark", cache_root=self.path, requests=100)


if __name__ == "__main__":
    unittest.main()
