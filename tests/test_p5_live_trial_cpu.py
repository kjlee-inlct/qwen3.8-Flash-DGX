"""P5 real-GPU trial controller CPU/Fake-DGX gates: no automatic restore."""
from __future__ import annotations
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import subprocess

from scripts.manager import p5_live_trial as live
from wizard.main import main as wizard


def mock_plan():
    return {"status": "READY_TO_APPROVE", "plan_id": "b" * 64, "issues": [],
            "details": {"source": {"container_id": "a" * 64,
                                   "image_id": "sha256:" + "a" * 64},
                        "candidate_image_id": "sha256:" + "c" * 64}}


class P5LiveTrialCPU(unittest.TestCase):
    def test_pinned_identity_mtp0_port_and_ack(self):
        self.assertEqual(live.ORCA_REV,
                         "3a3b63161c0745390e5270179af42e46efc70799")
        self.assertEqual(live.ALIAS,
                         "qwen3.8-flash-next-orca-uncensored-bf16")
        self.assertEqual(live.TARGET, "qwen38-orcarouter")
        self.assertEqual(live.ACK, "I_ACCEPT_P5_NO_ROLLBACK")
        self.assertEqual(live.IMAGE_TAG, "blazux-p5-orcarouter:vllm032-mtp0")

    def test_preapproval_never_stops_or_builds(self):
        with patch.object(live, "command", side_effect=AssertionError("should not execute")):
            report = live.execute(None, live.ACK)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertFalse(report["executed"])
        self.assertFalse(report["source_stopped"])

    def test_wrong_token_does_not_mutate_docker(self):
        with patch.object(live, "command", side_effect=AssertionError("docker mutation")):
            report = live.execute("b" * 64, "wrong")
        self.assertEqual(report["status"], "BLOCKED")

    def test_docker_run_command_offline_pinned_and_no_mtp(self):
        cmd = live._args("sha256:" + "a" * 64)
        self.assertIn("VLLM_PLE_MMAP=1", cmd)
        self.assertIn("VLLM_P5_ORCAROUTER=1", cmd)
        self.assertIn("HF_HUB_OFFLINE=1", cmd)
        self.assertIn("safetensors", cmd)
        self.assertIn("--enforce-eager", cmd)
        self.assertIn("--enable-auto-tool-choice", cmd)
        self.assertIn(live.ALIAS, cmd)
        self.assertEqual(cmd[cmd.index("-p") + 1], "8000:8000")
        self.assertNotIn("--speculative-config", cmd)
        self.assertNotIn("--auto-function-choice", cmd)
        self.assertEqual(cmd[cmd.index("--restart") + 1], "no")

    def test_scoped_source_is_27b_stopped_then_target_and_not_restored(self):
        calls = []
        def fake_run(args, timeout=30):
            calls.append(args)
            if args[:2] == ["docker", "stop"]:
                return subprocess.CompletedProcess(args, 0, "qwen38-27b\n", "")
            if args[:2] == ["docker", "run"]:
                return subprocess.CompletedProcess(args, 1, "", "GPU allocation failed")
            raise AssertionError(f"unexpected shell command: {args}")
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live, "STATE", Path(temp)), \
                 patch.object(live, "_private_state", return_value=None), \
                 patch.object(live, "_save", return_value="/tmp/test-fake.json"), \
                 patch.object(live, "_plan_data", return_value=mock_plan()), \
                 patch.object(live, "_port_open", return_value=False), \
                 patch.object(live, "_gpu_collisions", return_value=[]), \
                 patch.object(live, "_unmanaged_gpu_pids", return_value=[]), \
                 patch.object(live, "command", side_effect=fake_run):
                result = live.execute("b" * 64, live.ACK)
        self.assertEqual(result["status"], "FAIL_NO_ROLLBACK")
        self.assertTrue(result["source_stopped"])
        self.assertTrue(result["executed"])
        self.assertFalse(result["gpu_verified"])
        self.assertTrue(result["automatic_restore"] is False)
        self.assertEqual([a[1] for a in calls], ["stop", "run"])
        self.assertNotIn("start", [a[1] for a in calls])
        self.assertNotIn("rm", [a[1] for a in calls])

    def test_gpu_process_survives_stop_no_target_start_and_no_restore(self):
        calls = []
        def fake_run(args, timeout=30):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, "qwen38-27b\n", "")
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live, "STATE", Path(temp)), \
                 patch.object(live, "_private_state", return_value=None), \
                 patch.object(live, "_save", return_value="/tmp/test-fake.json"), \
                 patch.object(live, "_plan_data", return_value=mock_plan()), \
                 patch.object(live, "_port_open", return_value=False), \
                 patch.object(live, "_unmanaged_gpu_pids", return_value=["1234"]), \
                 patch.object(live.time, "sleep", return_value=None), \
                 patch.object(live, "command", side_effect=fake_run):
                result = live.execute("b" * 64, live.ACK)
        self.assertEqual(result["status"], "FAIL_NO_ROLLBACK")
        self.assertEqual(result["issues"], ["GPU_COMPUTE_PROCESS_STILL_RUNNING"])
        self.assertTrue(result["source_stopped"])
        self.assertEqual([a[1] for a in calls], ["stop"])

    def test_stopped_27b_port_unknown_does_not_start_target(self):
        calls = []
        def fake_run(args, timeout=30):
            calls.append(args)
            return subprocess.CompletedProcess(args, 0, "qwen38-27b\n", "")
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live, "STATE", Path(temp)), \
                 patch.object(live, "_private_state", return_value=None), \
                 patch.object(live, "_save", return_value="/tmp/test-fake.json"), \
                 patch.object(live, "_plan_data", return_value=mock_plan()), \
                 patch.object(live, "_port_open", return_value=True), \
                 patch.object(live.time, "sleep", return_value=None), \
                 patch.object(live, "command", side_effect=fake_run):
                result = live.execute("b" * 64, live.ACK)
        self.assertEqual(result["status"], "FAIL_NO_ROLLBACK")
        self.assertEqual(result["issues"], ["PORT_8000_STILL_OCCUPIED"])
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][:2], ["docker", "stop"])

    def test_stale_or_changed_plan_aborts_before_docker_stop(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live, "STATE", Path(temp)), \
                 patch.object(live, "_private_state", return_value=None), \
                 patch.object(live, "_plan_data", return_value=mock_plan()), \
                 patch.object(live, "command", side_effect=AssertionError("no stop")):
                result = live.execute("c" * 64, live.ACK)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["executed"])
        self.assertFalse(result["source_stopped"])

    def test_docker_candidate_image_label_rejects_wrong_arch_or_untagged(self):
        doc = {"Architecture": "arm64", "Os": "linux", "Config": {
            "Labels": {"blazux.p5.vllm": "0.32.0",
                       "blazux.p5.state": "SOURCE_CANDIDATE_NOT_QUALIFIED"}}}
        self.assertTrue(live._candidate_label(doc))
        doc["Architecture"] = "amd64"
        self.assertFalse(live._candidate_label(doc))
        doc["Architecture"] = "arm64"
        doc["Config"]["Labels"]["blazux.p5.vllm"] = "0.31.0"
        self.assertFalse(live._candidate_label(doc))

    def test_wizard_p5_trial_router_is_new_scoped_executable_path(self):
        result = {"status": "READY_TO_APPROVE", "executed": False, "plan_id": "a"*64}
        with patch.object(live, "_plan_data", return_value=result), \
             contextlib.redirect_stdout(io.StringIO()) as stdout:
            rc = wizard(["p5", "trial", "plan", "--json"])
        self.assertEqual(rc, 0)
        doc = json.loads(stdout.getvalue())
        self.assertEqual(doc["status"], "READY_TO_APPROVE")
        self.assertFalse(doc["executed"])

    def test_wizard_prepare_dry_run_cannot_build_image(self):
        with patch.object(live, "prepare",
                          side_effect=AssertionError("dry run must not build")):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                rc = wizard(["p5", "trial", "prepare", "--dry-run", "--json"])
        self.assertEqual(rc, 3)
        self.assertEqual(json.loads(output.getvalue())["status"], "BLOCKED")

    def test_existing_local_base_alias_must_match_exact_image_id(self):
        src_id = "sha256:" + "9" * 64
        alias = live._local_base_ref(src_id)
        self.assertEqual(alias, "blazux-p5-source:v032-" + "9" * 64)
        with patch.object(live, "command", return_value=subprocess.CompletedProcess(
                 [], 0, "sha256:" + "8" * 64 + "\n", "")) as run:
            with self.assertRaisesRegex(ValueError, "LOCAL_BASE_IMAGE_ALIAS_COLLISION"):
                live._ensure_local_base_tag(src_id)
        self.assertEqual(run.call_count, 1)

    def test_missing_base_alias_is_tagged_locally_from_exact_image_id(self):
        src_id = "sha256:" + "9" * 64
        alias = live._local_base_ref(src_id)
        calls = []
        def run(argv, timeout=30):
            calls.append(argv)
            if argv[:4] == ["docker", "image", "inspect", "--format"]:
                return subprocess.CompletedProcess(argv, 1, "", "No such image")
            if argv[:2] == ["docker", "tag"]:
                return subprocess.CompletedProcess(argv, 0, "", "")
            raise AssertionError(argv)
        with patch.object(live, "command", side_effect=run), \
             patch.object(live, "docker_json",
                          return_value={"Id": src_id}) as inspect:
            self.assertEqual(live._ensure_local_base_tag(src_id), alias)
        self.assertEqual(calls[1], ["docker", "tag", src_id, alias])
        self.assertFalse(any(args[:2] in (["docker", "stop"], ["docker", "rm"],
                                          ["docker", "rmi"]) for args in calls))
        inspect.assert_called_once_with(alias, image=True)

    def test_preexisting_correct_base_alias_is_read_only(self):
        src_id = "sha256:" + "9" * 64
        with patch.object(live, "command", return_value=subprocess.CompletedProcess(
                 [], 0, src_id + "\n", "")) as run, \
             patch.object(live, "docker_json", return_value={"Id": src_id}):
            self.assertEqual(live._ensure_local_base_tag(src_id),
                             live._local_base_ref(src_id))
        self.assertEqual(run.call_count, 1)

    def test_base_alias_inspect_failure_other_than_not_found_blocks_tag(self):
        with patch.object(live, "command", return_value=subprocess.CompletedProcess(
                 [], 125, "", "docker daemon unavailable")) as run:
            with self.assertRaisesRegex(ValueError, "LOCAL_BASE_IMAGE_ALIAS_INSPECT_FAILED"):
                live._ensure_local_base_tag("sha256:" + "9" * 64)
        self.assertEqual(run.call_count, 1)

    def test_prepare_build_uses_local_tag_separate_from_source_image_id(self):
        src_id = "sha256:" + "9" * 64
        candidate_id = "sha256:" + "a" * 64
        base_tag = live._local_base_ref(src_id)
        candidate = {
            "Id": candidate_id, "Architecture": "arm64", "Os": "linux",
            "Config": {"Labels": {
                "blazux.p5.vllm": "0.32.0",
                "blazux.p5.state": "SOURCE_CANDIDATE_NOT_QUALIFIED",
                "blazux.p5.base_image": src_id,
            }},
        }
        def inspect(name, *, image=False):
            if name == src_id:
                return {"Architecture": "arm64", "Id": src_id}
            if name == live.IMAGE_TAG:
                if state["built"]:
                    return candidate
                raise ValueError("DOCKER_INSPECT_FAILED")
            raise AssertionError(name)
        state = {"built": False}
        calls = []
        def run(argv, timeout=30):
            calls.append(argv)
            self.assertNotIn(["docker", "stop"], [argv[:2]])
            self.assertNotIn(["docker", "rm"], [argv[:2]])
            self.assertNotIn(["docker", "rmi"], [argv[:2]])
            self.assertEqual(argv[:4],
                             ["docker", "build", "--pull=false", "--network=none"])
            self.assertIn("P5_QUALIFIED_BASE_IMAGE=" + base_tag, argv)
            self.assertIn("P5_QUALIFIED_BASE_IMAGE_ID=" + src_id, argv)
            self.assertNotIn("P5_QUALIFIED_BASE_IMAGE=" + src_id, argv)
            state["built"] = True
            return subprocess.CompletedProcess(argv, 0, "Successfully built", "")
        with patch.object(live, "_metadata_gate",
                          return_value=([], {"metadata_verified": True})), \
             patch.object(live, "_source",
                          return_value={"image_id": src_id}), \
             patch.object(live, "docker_json", side_effect=inspect), \
             patch.object(live, "_ensure_local_base_tag", return_value=base_tag), \
             patch.object(live, "command", side_effect=run):
            result = live.prepare()
        self.assertEqual(result["status"], "PASS")
        self.assertTrue(result["executed"])
        self.assertEqual(result["source_image_id"], src_id)
        self.assertEqual(result["image_id"], candidate_id)
        self.assertEqual(len(calls), 1)

    def test_builded_candidate_with_wrong_source_provenance_is_rejected(self):
        src_id = "sha256:" + "9" * 64
        wrong_id = "sha256:" + "8" * 64
        candidate = {
            "Id": "sha256:" + "a" * 64, "Architecture": "arm64", "Os": "linux",
            "Config": {"Labels": {
                "blazux.p5.vllm": "0.32.0",
                "blazux.p5.state": "SOURCE_CANDIDATE_NOT_QUALIFIED",
                "blazux.p5.base_image": wrong_id,
            }},
        }
        state = {"built": False}
        def inspect(name, *, image=False):
            if name == src_id:
                return {"Architecture": "arm64", "Id": src_id}
            if name == live.IMAGE_TAG:
                if state["built"]:
                    return candidate
                raise ValueError("DOCKER_INSPECT_FAILED")
            raise AssertionError(name)
        def run(argv, timeout=30):
            state["built"] = True
            return subprocess.CompletedProcess(argv, 0, "", "")
        with patch.object(live, "_metadata_gate",
                          return_value=([], {"metadata_verified": True})), \
             patch.object(live, "_source",
                          return_value={"image_id": src_id}), \
             patch.object(live, "docker_json", side_effect=inspect), \
             patch.object(live, "_ensure_local_base_tag",
                          return_value=live._local_base_ref(src_id)), \
             patch.object(live, "command", side_effect=run):
            result = live.prepare()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("BUILT_IMAGE_IDENTITY_INVALID", result["issues"])

    def test_p5_dockerfile_requires_local_tag_and_separate_immutable_id_label(self):
        content = Path("Dockerfile.p5.candidate").read_text(encoding="utf-8")
        self.assertIn("FROM ${P5_QUALIFIED_BASE_IMAGE}", content)
        self.assertIn('blazux.p5.base_image="${P5_QUALIFIED_BASE_IMAGE_ID}"', content)
        self.assertIn("blazux-p5-source:explicit-local-override-required", content)
        self.assertNotIn('blazux.p5.base_image="${P5_QUALIFIED_BASE_IMAGE}"', content)

    def test_old_wizard_p5_gpu_trial_stays_separate_and_blocked(self):
        from scripts.manager.p5_orcarouter import source_plan
        result = source_plan("mtp0")
        self.assertFalse(result["operations_enabled"])
        self.assertIsNone(result["plan_id"])


if __name__ == "__main__":
    unittest.main()
