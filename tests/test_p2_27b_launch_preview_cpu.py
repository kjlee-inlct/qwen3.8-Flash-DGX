"""P2 27B source-only launch preview guards: no Docker/GPU execution."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p2_27b_launch_preview as mod
from wizard import main as router


def valid_runtime():
    return {
        "status": "BLOCKED", "source_files_present": True,
        "source_checkpoint_status": "SOURCE_FILES_PRESENT_PINNED_CANDIDATE",
        "revision": mod.REVISION, "metadata_matches_expected": True,
        "host_architecture": "aarch64",
        "quantization_audit": {
            "status": "PINNED_METADATA_PARSED_UNQUALIFIED",
            "revision": mod.REVISION,
            "mixed_fp8_nvfp4_metadata": True,
            "layer_count": 401, "layer_algorithms": {"FP8":208, "NVFP4":193},
        },
        "image": {
            "image_id": "sha256:" + "a" * 64, "architecture":"arm64",
            "os":"linux", "vllm032_label_matches":True, "repo_digests":[],
        },
        "issues": ["VLLM032_27B_LOADER_NOT_QUALIFIED"],
    }


def valid_service():
    return {
        "status":"OBSERVED_UNQUALIFIED",
        "observed_model":"flash-next",
        "api_port_8000_listening": True, "download_running":False,
        "managed_containers":[{
            "model":"flash-next", "container_name":"qwen38-flash",
            "image_id":"sha256:"+"f"*64, "status":"Up 2 hours",
        }],
        "issues":[],
    }


def valid_health(**kwargs):
    return {
        "status":"API_IDENTITY_CONFIRMED", "api_identity_verified":True,
        "expected_model_id":"qwen3.8-flash-next",
        "model_ids":["qwen3.8-flash-next"], "issues":[],
    }


class P2LaunchPreviewCPU(unittest.TestCase):
    def inspect(self, runtime=None, service=None, health=valid_health):
        return mod.build_27b_launch_preview(
            cache_root=Path("/hf"),
            runtime_inspector=lambda **kwargs: runtime if runtime is not None else valid_runtime(),
            service_inspector=lambda: service if service is not None else valid_service(),
            health_inspector=health)

    def test_correct_data_is_still_blocked_and_never_approved(self):
        result = self.inspect()
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["executed"])
        self.assertFalse(result["operations_enabled"])
        self.assertIsNone(result["plan_id"])
        self.assertFalse(result["gpu_verified"])
        self.assertEqual(result["source_quantization"]["algorithms"],
                         {"FP8":208,"NVFP4":193})
        self.assertTrue(result["observed_source"]["api_identity_confirmed"])
        json.dumps(result)

    def test_argv_has_exact_revision_image_id_and_modelopt_mixed(self):
        cmd=self.inspect()["command_preview"]
        self.assertIsNotNone(cmd)
        self.assertEqual(cmd[:2],["docker","run"])
        self.assertIn("--quantization",cmd)
        self.assertEqual(cmd[cmd.index("--quantization")+1], "modelopt_mixed")
        self.assertIn(mod.REVISION, " ".join(cmd))
        self.assertIn("sha256:"+"a"*64,cmd)
        self.assertIn("qwen3.8-27b",cmd)
        self.assertIn("--enforce-eager",cmd)
        self.assertNotIn("--speculative-config",cmd)
        self.assertNotIn("VLLM_PLE_MMAP", " ".join(cmd))
        self.assertNotIn("scripts/serve.sh", " ".join(cmd))
        self.assertNotIn("--restart",cmd)
        self.assertIn("8000:8000",cmd)
        self.assertIn("/hf:ro", " ".join(cmd))

    def test_transition_order_never_parallel_GPU(self):
        steps=self.inspect()["transition_order"]
        self.assertLess(steps.index("stop-only-approved-source-container"),
                        steps.index("start-approved-27b-command"))
        self.assertIn("commit-or-restore-original-Flash-Next-and-verify",steps)

    def test_missing_image_or_bad_digest_never_generates_command(self):
        for image_id in ("nonsense", None, "sha256:"+ "x"*64):
            data=valid_runtime()
            data["image"]["image_id"]=image_id
            r=self.inspect(runtime=data)
            self.assertIsNone(r["command_preview"])
            self.assertIn("LOCAL_VLLM032_IMAGE_NOT_QUALIFIED",r["issues"])

    def test_quantization_mismatch_never_unlocks(self):
        data=valid_runtime()
        data["quantization_audit"]["mixed_fp8_nvfp4_metadata"]=False
        r=self.inspect(runtime=data)
        self.assertIn("PINNED_MODEL_OPT_MIX_NOT_CONFIRMED",r["issues"])
        self.assertFalse(r["operations_enabled"])

    def test_unknown_live_state_skips_health(self):
        service=valid_service()
        service["status"]="BLOCKED"
        with self.assertRaisesRegex(AssertionError,"should not probe"):
            pass
        def prohibited(**kwargs): raise AssertionError("should not probe")
        r=self.inspect(service=service,health=prohibited)
        self.assertIn("LIVE_SERVICE_INVENTORY_UNVERIFIED",r["issues"])
        self.assertIn("SOURCE_API_IDENTITY_NOT_CONFIRMED",r["issues"])

    def test_unknown_original_container_fails_closed(self):
        service=valid_service()
        service["managed_containers"]=[]
        result=self.inspect(service=service)
        self.assertIn("SOURCE_CONTAINER_IMAGE_NOT_UNAMBIGUOUS",result["issues"])
        self.assertIsNone(result["observed_source"]["container_image_id"])

    def test_source_health_mismatch_fails_closed(self):
        def mismatch(**kwargs):
            return {"status":"BLOCKED","api_identity_verified":False,"model_ids":[]}
        r=self.inspect(health=mismatch)
        self.assertIn("SOURCE_API_IDENTITY_NOT_CONFIRMED",r["issues"])

    def test_existing_target_container_name_blocks(self):
        service=valid_service()
        service["managed_containers"].append({
            "model":"27b", "container_name":"qwen38-27b",
            "image_id":"sha256:"+"a"*64,"status":"Exited (0)"})
        self.assertIn("TARGET_CONTAINER_NAME_ALREADY_EXISTS",
                      self.inspect(service=service)["issues"])

    def test_no_subprocess_or_gpu_code_path(self):
        with patch("subprocess.run",side_effect=AssertionError("never run Docker")):
            r=self.inspect()
        self.assertFalse(r["executed"])

    def test_cli_preview_accepts_only_read_only_actions(self):
        with patch("wizard.menus.models.qwen_27b.build_27b_launch_preview",
                   return_value=self.inspect()) as f, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            status=router.main(["model","27b","plan","--for-action","start",
                                "--launch-preview","--json"])
        self.assertEqual(status,0)
        self.assertEqual(json.loads(output.getvalue())["status"],"BLOCKED")
        f.assert_called_once()

    def test_cli_extra_execute_options_rejected(self):
        with patch("wizard.menus.models.qwen_27b.build_27b_launch_preview",
                   side_effect=AssertionError("no bypass")) as f, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            status=router.main(["model","27b","plan","--for-action","start",
                                "--launch-preview","--execute",
                                "--approve-plan","a"*64,"--json"])
        self.assertEqual(status,3)
        self.assertFalse(json.loads(output.getvalue())["executed"])
        f.assert_not_called()


if __name__ == "__main__":
    unittest.main()
