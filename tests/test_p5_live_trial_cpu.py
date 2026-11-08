"""P5 MTP0 recipe-first live trial: CPU/Fake-DGX tests, no source patch/build."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p5_live_trial as live
from wizard.main import main as wizard


SOURCE_IMAGE = "sha256:" + "9" * 64
TARGET_CID = "a" * 64


def completed(args, rc=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(args, rc, stdout, stderr)


def mock_plan():
    return {"status": "READY_TO_APPROVE", "plan_id": "b" * 64, "issues": [],
            "details": {"source": {"container_id": TARGET_CID,
                                   "image_id": SOURCE_IMAGE},
                        "runtime_image_id": SOURCE_IMAGE}}


def mock_existing_image():
    return {"Id": SOURCE_IMAGE, "Os": "linux", "Architecture": "arm64",
            "Config": {"Labels": {"qwen38.base": "v0.32"}}}


def mock_capabilities():
    return {"vllm_version": "0.32.0", "ple_mmap_hook": True,
            "bf16_ple_table": True, "ple_custom_op": True,
            "source_syntax_valid": True}


class P5RecipeFirstCPU(unittest.TestCase):
    def test_identity_and_development_ack(self):
        self.assertEqual(live.ORCA_REV,
                         "3a3b63161c0745390e5270179af42e46efc70799")
        self.assertEqual(live.ALIAS, "qwen3.8-flash-next-orca-uncensored-bf16")
        self.assertEqual(live.ACK, "I_ACCEPT_P5_NO_ROLLBACK")
        self.assertFalse(hasattr(live, "IMAGE_TAG"))

    def test_recipe_is_primary_run_spec_no_build_no_patch(self):
        recipe = live._trial_recipe()
        self.assertEqual(recipe["vllm_version"], "0.32.0")
        self.assertEqual(recipe["trial"]["runtime_strategy"],
                         "RECIPE_FIRST_EXISTING_VLLM032_IMAGE")
        self.assertFalse(recipe["trial"]["require_image_build"])
        self.assertFalse(recipe["trial"]["allow_source_patch"])
        self.assertEqual(recipe["model"]["expected_ple"]["dtype"], "BF16")
        self.assertEqual(recipe["profiles"]["mtp0"]["num_speculative_tokens"], 0)

    def test_recipe_driven_argv_preserves_runtime_policy(self):
        args = live._args(SOURCE_IMAGE)
        self.assertEqual(args[:3], ["docker", "run", "-d"])
        self.assertIn(SOURCE_IMAGE, args)
        self.assertIn("--gpus", args)
        self.assertIn("all", args)
        self.assertEqual(args[args.index("-p") + 1], "8000:8000")
        self.assertEqual(args[args.index("--max-model-len") + 1], "8192")
        self.assertEqual(args[args.index("--max-num-seqs") + 1], "1")
        self.assertEqual(args[args.index("--gpu-memory-utilization") + 1], "0.7")
        self.assertIn("VLLM_PLE_MMAP=1", args)
        self.assertIn("VLLM_PLE_MMAP_PREWARM=0", args)
        self.assertIn("HF_HUB_OFFLINE=1", args)
        self.assertIn("--enforce-eager", args)
        self.assertIn("--enable-auto-tool-choice", args)
        self.assertIn("qwen3_coder", args)
        self.assertIn("qwen3", args)
        self.assertIn(live.ALIAS, args)
        self.assertNotIn("--speculative-config", args)
        self.assertNotIn("VLLM_P5_ORCAROUTER=1", args)
        self.assertFalse(any(a in args for a in (
            "docker build", "P5_EXPLICIT_IMAGE_BUILD=1", "docker tag")))

    def test_derived_source_model_snapshot_pinned(self):
        args = live._args(SOURCE_IMAGE)
        at = args.index(SOURCE_IMAGE)
        self.assertEqual(args[at + 1],
             "/hf/hub/models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4/snapshots/"
             + live.ORCA_REV)
        self.assertEqual(args[args.index("-v") + 1], str(live.CACHE) + ":/hf:ro")

    def test_wrong_image_digest_is_rejected(self):
        with self.assertRaises(ValueError):
            live._args("alpine:latest")

    def test_image_cpu_probe_reads_existing_image_not_gpu(self):
        calls = []
        def run(args, timeout=30):
            calls.append(args)
            return completed(args, stdout=json.dumps(mock_capabilities()))
        with patch.object(live, "docker_json", return_value=mock_existing_image()), \
             patch.object(live, "command", side_effect=run):
            result = live._inspect_existing_image(SOURCE_IMAGE)
        self.assertEqual(result["vllm_version"], "0.32.0")
        self.assertEqual(calls[0][:6],
            ["docker", "run", "--rm", "--network=none", "--entrypoint", "python3"])
        self.assertEqual(calls[0][6], SOURCE_IMAGE)
        self.assertNotIn("--gpus", calls[0])
        self.assertNotIn("--pull", calls[0])
        self.assertNotIn("--volume", calls[0])

    def test_missing_bf16_mmap_capability_blocks(self):
        broken = {**mock_capabilities(), "bf16_ple_table": False}
        with patch.object(live, "docker_json", return_value=mock_existing_image()), \
             patch.object(live, "command", return_value=completed(
                 [], stdout=json.dumps(broken))):
            with self.assertRaisesRegex(ValueError,
                                        "EXISTING_IMAGE_BF16_PLE_MMAP_UNAVAILABLE"):
                live._inspect_existing_image(SOURCE_IMAGE)

    def test_wrong_image_id_arch_or_base_label_blocks(self):
        for key, value in [
            ("Id", "sha256:" + "a"*64), ("Architecture", "amd64"),
            ("Os", "windows")]:
            wrong = mock_existing_image()
            wrong[key] = value
            with self.subTest(key=key), \
                 patch.object(live, "docker_json", return_value=wrong), \
                 patch.object(live, "command", side_effect=AssertionError("must not run")):
                with self.assertRaises(ValueError):
                    live._inspect_existing_image(SOURCE_IMAGE)
        wrong = mock_existing_image()
        wrong["Config"]["Labels"]["qwen38.base"] = "v0.31"
        with patch.object(live, "docker_json", return_value=wrong), \
             patch.object(live, "command", side_effect=AssertionError("no run")):
            with self.assertRaises(ValueError):
                live._inspect_existing_image(SOURCE_IMAGE)

    def test_probing_failure_does_not_promote_gpu(self):
        with patch.object(live, "docker_json", return_value=mock_existing_image()), \
             patch.object(live, "command", return_value=completed([], rc=1)):
            with self.assertRaisesRegex(ValueError, "EXISTING_IMAGE_CPU_ABI_PROBE_FAILED"):
                live._inspect_existing_image(SOURCE_IMAGE)

    def test_prepare_is_read_only_no_build_or_tag(self):
        source = {"image_id": SOURCE_IMAGE}
        with patch.object(live, "_metadata_gate",
                          return_value=([], {"metadata_verified": True})), \
             patch.object(live, "_source", return_value=source), \
             patch.object(live, "_inspect_existing_image",
                          return_value=mock_capabilities()), \
             patch.object(live, "command", side_effect=AssertionError("no docker mutation")):
            result = live.prepare()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["image_id"], SOURCE_IMAGE)
        self.assertFalse(result["executed"])
        self.assertFalse(result["image_built"])
        self.assertFalse(result["source_patched"])
        self.assertFalse(result["gpu_verified"])
        self.assertEqual(result["recipe_id"], "qwen38-orcarouter-bf16ple-p5")

    def test_prepare_fails_closed_if_required_image_feature_absent(self):
        with patch.object(live, "_metadata_gate",
                          return_value=([], {"metadata_verified": True})), \
             patch.object(live, "_source",
                          return_value={"image_id": SOURCE_IMAGE}), \
             patch.object(live, "_inspect_existing_image",
                          side_effect=ValueError("EXISTING_IMAGE_BF16_PLE_MMAP_UNAVAILABLE")):
            result = live.prepare()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["executed"])
        self.assertEqual(result["issues"],
                         ["EXISTING_IMAGE_BF16_PLE_MMAP_UNAVAILABLE"])

    def test_plan_binds_unmodified_current_27b_image(self):
        with patch.object(live, "_metadata_gate",
                          return_value=([], {"metadata_verified": True})), \
             patch.object(live, "_source", return_value={
                 "container_id": TARGET_CID, "image_id": SOURCE_IMAGE}), \
             patch.object(live, "_inspect_existing_image",
                          return_value=mock_capabilities()), \
             patch.object(live, "_target_absent", return_value=None), \
             patch.object(live, "_gpu_collisions", return_value=[]), \
             patch.object(live, "_port_open", return_value=True), \
             patch.object(live, "_git_head", return_value="a"*40):
            doc = live._plan_data()
        self.assertEqual(doc["status"], "READY_TO_APPROVE")
        self.assertEqual(doc["details"]["runtime_image_id"], SOURCE_IMAGE)
        self.assertEqual(doc["details"]["strategy"],
                         "RECIPE_FIRST_EXISTING_VLLM032_IMAGE")
        self.assertIsNotNone(doc["plan_id"])
        self.assertFalse(doc["image_built"])
        self.assertFalse(doc["source_patched"])
        self.assertFalse(doc["executed"])

    def test_plan_cannot_approve_gpu_when_abi_missing(self):
        with patch.object(live, "_metadata_gate",
                          return_value=([], {"metadata_verified": True})), \
             patch.object(live, "_source", return_value={
                 "container_id": TARGET_CID, "image_id": SOURCE_IMAGE}), \
             patch.object(live, "_inspect_existing_image",
                          side_effect=ValueError("EXISTING_IMAGE_CPU_ABI_PROBE_FAILED")), \
             patch.object(live, "_git_head", return_value="a"*40):
            doc = live._plan_data()
        self.assertEqual(doc["status"], "BLOCKED")
        self.assertIsNone(doc["plan_id"])

    def test_preapproval_never_stops_docker(self):
        with patch.object(live, "command", side_effect=AssertionError("unexpected")):
            report = live.execute(None, live.ACK)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertFalse(report["executed"])

    def test_wrong_ack_cannot_dispatch(self):
        with patch.object(live, "command", side_effect=AssertionError("unexpected")):
            report = live.execute("b" * 64, "wrong")
        self.assertEqual(report["status"], "BLOCKED")

    def test_scoped_source_stopped_target_from_recipe_no_restore(self):
        calls = []
        def run(args, timeout=30):
            calls.append(args)
            if args[:2] == ["docker", "stop"]:
                return completed(args, stdout="qwen38-27b\n")
            if args[:2] == ["docker", "run"]:
                return completed(args, rc=1, stderr="GPU trial failure")
            raise AssertionError(args)
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live, "STATE", Path(temp)), \
                 patch.object(live, "_private_state", return_value=None), \
                 patch.object(live, "_save", return_value="/tmp/test.json"), \
                 patch.object(live, "_plan_data", return_value=mock_plan()), \
                 patch.object(live, "_port_open", return_value=False), \
                 patch.object(live, "_gpu_collisions", return_value=[]), \
                 patch.object(live, "_unmanaged_gpu_pids", return_value=[]), \
                 patch.object(live, "command", side_effect=run):
                result = live.execute("b"*64, live.ACK)
        self.assertEqual(result["status"], "FAIL_NO_ROLLBACK")
        self.assertTrue(result["source_stopped"])
        self.assertTrue(result["executed"])
        self.assertFalse(result["gpu_verified"])
        self.assertEqual([args[1] for args in calls], ["stop", "run"])
        self.assertEqual(result["target_image_id"], SOURCE_IMAGE)
        self.assertNotIn("start", [args[1] for args in calls])
        self.assertNotIn("rm", [args[1] for args in calls])

    def test_gpu_process_left_after_source_stop_blocks_launch(self):
        calls = []
        def run(args, timeout=30):
            calls.append(args)
            return completed(args, stdout="qwen38-27b\n")
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live, "STATE", Path(temp)), \
                 patch.object(live, "_private_state", return_value=None), \
                 patch.object(live, "_save", return_value="/tmp/test.json"), \
                 patch.object(live, "_plan_data", return_value=mock_plan()), \
                 patch.object(live, "_port_open", return_value=False), \
                 patch.object(live, "_unmanaged_gpu_pids", return_value=["1234"]), \
                 patch.object(live.time, "sleep", return_value=None), \
                 patch.object(live, "command", side_effect=run):
                result = live.execute("b"*64, live.ACK)
        self.assertEqual(result["status"], "FAIL_NO_ROLLBACK")
        self.assertEqual(result["issues"], ["GPU_COMPUTE_PROCESS_STILL_RUNNING"])
        self.assertEqual([args[1] for args in calls], ["stop"])

    def test_port_still_occupied_never_launches_second_model(self):
        calls = []
        def run(args, timeout=30):
            calls.append(args)
            return completed(args, stdout="qwen38-27b\n")
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live, "STATE", Path(temp)), \
                 patch.object(live, "_private_state", return_value=None), \
                 patch.object(live, "_save", return_value="/tmp/test.json"), \
                 patch.object(live, "_plan_data", return_value=mock_plan()), \
                 patch.object(live, "_port_open", return_value=True), \
                 patch.object(live.time, "sleep", return_value=None), \
                 patch.object(live, "command", side_effect=run):
                result = live.execute("b"*64, live.ACK)
        self.assertEqual(result["status"], "FAIL_NO_ROLLBACK")
        self.assertEqual(result["issues"], ["PORT_8000_STILL_OCCUPIED"])
        self.assertEqual([args[1] for args in calls], ["stop"])

    def test_changed_plan_no_stop(self):
        with tempfile.TemporaryDirectory() as temp:
            with patch.object(live, "STATE", Path(temp)), \
                 patch.object(live, "_private_state", return_value=None), \
                 patch.object(live, "_plan_data", return_value=mock_plan()), \
                 patch.object(live, "command", side_effect=AssertionError("should not execute")):
                report = live.execute("c"*64, live.ACK)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertFalse(report["executed"])

    def test_wizard_routes_recipe_only_plan(self):
        result = {"status": "READY_TO_APPROVE", "executed": False, "plan_id": "b"*64}
        with patch.object(live, "_plan_data", return_value=result), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wizard(["p5", "trial", "plan", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "READY_TO_APPROVE")

    def test_wizard_prepare_dry_run_still_rejects_dispatch(self):
        with patch.object(live, "prepare", side_effect=AssertionError("never called")), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wizard(["p5", "trial", "prepare", "--dry-run", "--json"])
        self.assertEqual(rc, 3)
        self.assertEqual(json.loads(output.getvalue())["status"], "BLOCKED")

    def test_legacy_p5_gpu_trial_remains_blocked(self):
        from scripts.manager.p5_orcarouter import source_plan
        old = source_plan("mtp0")
        self.assertFalse(old["operations_enabled"])
        self.assertIsNone(old["plan_id"])


if __name__ == "__main__":
    unittest.main()
