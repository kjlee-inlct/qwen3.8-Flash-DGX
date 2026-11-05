"""CPU-only read-only P2 runtime preflight/CLI regression tests."""
import contextlib
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.manager import p2_27b_qualification as qual
from wizard import main as router


class P2RuntimeQualificationCPU(unittest.TestCase):
    def source(self, *, valid=True):
        return {
            "source_files_present": valid,
            "local_revision": qual.REVISION if valid else None,
            "checkpoint_status": "SOURCE_FILES_PRESENT_PINNED_CANDIDATE"
                                 if valid else "NOT_READY",
            "issues": [] if valid else ["NO_PINNED_LOCAL_SNAPSHOT"],
            "configuration": {
                "status": "PARSED_UNQUALIFIED",
                "architecture": ["Qwen3_5ForConditionalGeneration"],
                "model_type": "qwen3_5",
                "quant_method": "modelopt",
                "context_length": 262144,
                "vision_config_present": True,
                "vllm032_qualified": False,
            },
        }

    @staticmethod
    def service(model="flash-next"):
        return {"status": "OBSERVED_UNQUALIFIED", "observed_model": model,
                "download_running": False, "issues": [],
                "api_port_8000_listening": model is not None}

    @staticmethod
    def runner(cmd, **kwargs):
        assert cmd == ["docker", "image", "inspect", qual.IMAGE,
                       "--format", "{{json .}}"]
        assert kwargs["timeout"] == 10
        assert kwargs["check"] is False
        return type("Result", (), {
            "returncode": 0,
            "stdout": json.dumps({
                "Id": "sha256:" + "a" * 64, "Architecture": "arm64",
                "Os": "linux", "RepoDigests": [],
                "Config": {"Labels": {"qwen38.base": "v0.32"}},
            })
        })()

    def inspect(self, source=None, service=None, runner=None, machine=None):
        return qual.inspect_27b_runtime(
            inspector=lambda root, expected_revision: source or self.source(),
            service_observer=lambda: service or self.service(),
            runner=runner or self.runner, machine=machine or (lambda: "aarch64"),
        )

    def test_complete_source_and_matching_image_still_never_unlock_start(self):
        result = self.inspect()
        self.assertTrue(result["metadata_matches_expected"])
        self.assertTrue(result["source_files_present"])
        self.assertEqual(result["image"]["status"],
                         "METADATA_OBSERVED_UNQUALIFIED")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["operations_enabled"])
        self.assertIsNone(result["plan_id"])
        self.assertIn("VLLM032_27B_LOADER_NOT_QUALIFIED", result["issues"])
        self.assertIn("ACTIVE_MODEL_REQUIRES_SEPARATE_TRANSITION_APPROVAL",
                      result["issues"])

    def test_wrong_checkpoint_revision_stays_blocked(self):
        result = self.inspect(source=self.source(valid=False))
        self.assertIn("PINNED_CHECKPOINT_NOT_CONFIRMED", result["issues"])
        self.assertIn("CHECKPOINT:NO_PINNED_LOCAL_SNAPSHOT", result["issues"])

    def test_mismatched_model_metadata_never_qualified(self):
        source = self.source()
        source["configuration"]["architecture"] = ["OtherForCausalLM"]
        result = self.inspect(source=source)
        self.assertFalse(result["metadata_matches_expected"])
        self.assertIn("MODEL_ARCHITECTURE_OR_QUANT_METADATA_UNEXPECTED",
                      result["issues"])

    def test_image_inspection_failure_blocks_and_never_runs_docker(self):
        def fail(cmd, **kwargs):
            self.assertEqual(cmd[:3], ["docker", "image", "inspect"])
            return type("Result", (), {"returncode": 1, "stdout": ""})()
        result = self.inspect(runner=fail)
        self.assertIn("IMAGE_INSPECT_FAILED", result["issues"])
        self.assertFalse(result["operations_enabled"])

    def test_wrong_host_or_image_platform_blocks(self):
        def wrong(cmd, **kwargs):
            r = self.runner(cmd, **kwargs)
            payload = json.loads(r.stdout)
            payload["Architecture"] = "amd64"
            return type("Result", (), {"returncode": 0,
                                        "stdout": json.dumps(payload)})()
        result = self.inspect(runner=wrong, machine=lambda: "x86_64")
        self.assertIn("HOST_NOT_CONFIRMED_ARM64", result["issues"])
        self.assertIn("IMAGE_PLATFORM_MISMATCH", result["issues"])

    def test_unknown_live_state_is_not_treated_as_empty_gpu(self):
        result = self.inspect(service={"status": "BLOCKED", "issues": [
            "SINGLE_ACTIVE_MODEL_POLICY_VIOLATION"]})
        self.assertIn("LIVE_SERVICE_UNVERIFIED", result["issues"])
        self.assertIn("SERVICE:SINGLE_ACTIVE_MODEL_POLICY_VIOLATION",
                      result["issues"])

    def test_running_download_reports_in_progress(self):
        service = self.service()
        service["download_running"] = True
        self.assertIn("DOWNLOAD_STILL_RUNNING",
                      self.inspect(service=service)["issues"])

    def test_wizard_runtime_preflight_read_only_status(self):
        expected = self.inspect()
        with patch("wizard.menus.models.qwen_27b.inspect_27b_runtime",
                   return_value=expected) as probe, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main(["model", "27b", "status",
                              "--inspect-runtime", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "BLOCKED")
        probe.assert_called_once()

    def test_inspect_runtime_never_bypasses_execute_approval(self):
        with patch("wizard.menus.models.qwen_27b.inspect_27b_runtime",
                   side_effect=AssertionError("unapproved probe")) as probe, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = router.main(["model", "27b", "status", "--inspect-runtime",
                              "--execute", "--approve-plan", "a" * 64,
                              "--json"])
        self.assertEqual(rc, 3)
        self.assertFalse(json.loads(output.getvalue())["executed"])
        probe.assert_not_called()


if __name__ == "__main__":
    unittest.main()
