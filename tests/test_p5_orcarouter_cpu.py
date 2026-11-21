"""P5 Orcarouter pinned-source and Fake-DGX safety tests; no CUDA/Docker/network."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p5_orcarouter as p5
from scripts.p5_vendor.manifest import load_manifest
from scripts.p5_vendor.mtp import MTP_TENSOR_NAMES, MTP_QUANTIZATION_IGNORE, mtp_overlay_fingerprint
from scripts.p5_vendor.safetensors import SafetensorsError, read_header, strict_json_loads
from wizard.main import main as wizard_main


class P5CPU(unittest.TestCase):
    def test_immutable_pins_and_vllm032(self):
        recipe = p5._recipe()
        self.assertEqual(recipe["vllm_version"], "0.32.0")
        self.assertEqual(recipe["model"]["revision"], p5.ORCA_REV)
        self.assertEqual(recipe["mtp_donor"]["revision"], p5.DONOR_REV)
        self.assertEqual(recipe["runtime"]["host_port"], 8000)
        self.assertTrue(recipe["runtime"]["one_active_model_only"])
        self.assertFalse(recipe["launch_allowed"])
        self.assertFalse(recipe["register_as_runtime_recipe"])

    def test_source_ple_bf16_exact_layout(self):
        manifest = load_manifest(p5.VENDOR / "compatibility.json")
        t = manifest.target("orca-uncensored")
        self.assertEqual((t.expected_ple.tensor_count, t.expected_ple.total_rows,
                          t.expected_ple.width, t.expected_ple.dtype),
                         (128, 320001536, 160, "BF16"))
        self.assertEqual(320001536 * 160 * 2, 102400491520)

    def test_exact_mtp_names_no_loose_globs(self):
        self.assertEqual(len(MTP_TENSOR_NAMES), 31)
        self.assertEqual(len(set(MTP_TENSOR_NAMES)), 31)
        self.assertNotIn("mtp.*", MTP_QUANTIZATION_IGNORE)
        self.assertNotIn("model.mtp.*", MTP_QUANTIZATION_IGNORE)
        self.assertEqual(len(MTP_QUANTIZATION_IGNORE),
                         len(set(MTP_QUANTIZATION_IGNORE)))

    def test_three_pinned_donor_shard_hashes(self):
        r = p5._recipe()
        donor = r["mtp_donor"]
        self.assertEqual(len(donor["shards"]), 3)
        for shard in donor["shards"]:
            self.assertTrue(shard["filename"].endswith(".safetensors"))
            self.assertEqual(len(shard["sha256"]), 64)
            self.assertGreater(shard["size"], 0)

    def test_deterministic_overlay_fingerprint(self):
        t = load_manifest(p5.VENDOR / "compatibility.json").target(
            "orca-uncensored-bf16-mtp")
        a, b = mtp_overlay_fingerprint(t), mtp_overlay_fingerprint(t)
        self.assertEqual(a, b)
        self.assertEqual(len(a), 16)

    def test_source_abi_gate_is_not_gpu_pass(self):
        doc = p5.abi_source_audit()
        self.assertEqual(doc["status"], "PASS")
        self.assertTrue(doc["ple_bf16_static_hook"])
        self.assertFalse(doc["gpu_abi_verified"])
        self.assertFalse(doc["mtp_runtime_abi_verified"])

    def test_mtp0_and_mtp2_independent_model_names(self):
        profiles = p5._recipe()["profiles"]
        self.assertEqual(profiles["mtp0"]["num_speculative_tokens"], 0)
        self.assertEqual(profiles["mtp2"]["num_speculative_tokens"], 2)
        self.assertNotEqual(profiles["mtp0"]["served_id"],
                            profiles["mtp2"]["served_id"])
        self.assertNotIn(profiles["mtp0"]["served_id"],
                         ("qwen3.8-27b", "qwen3.8-flash-next"))

    def test_plan_never_generates_approval_id(self):
        for profile in ("mtp0", "mtp2"):
            p = p5.source_plan(profile)
            self.assertEqual(p["status"], "BLOCKED")
            self.assertIsNone(p["plan_id"])
            self.assertFalse(p["approval_accepted"])
            self.assertFalse(p["executed"])
            self.assertEqual(p["stages"][-1]["status"], "NOT_RUN")
            self.assertEqual(len(p["preview_fingerprint_not_approval"]), 64)

    def test_unsupported_profile_rejected(self):
        with self.assertRaises(ValueError):
            p5.source_plan("mtp3")

    def test_absent_pinned_caches_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.assertEqual(p5.audit_ple(roots=[root])["status"], "BLOCKED")
            self.assertEqual(p5.audit_donor(roots=[root])["status"], "BLOCKED")

    def test_foreign_checkpoint_revision_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                p5._repo_snapshot(Path(temp), p5.ORCA_REPO, "f" * 40)

    def test_readonly_no_false_gpu_pass_with_missing_sources(self):
        live = lambda: {"status": "LIVE_SERVICE_VERIFIED", "observed_model": "27b",
                        "expected_served_id": "qwen3.8-27b", "host_port": 8000,
                        "issues": []}
        with tempfile.TemporaryDirectory() as temp:
            result = p5.read_only(roots=[Path(temp)], service_inspector=live)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["stages"][3]["status"], "PASS")
        self.assertEqual(result["stages"][-1]["status"], "NOT_RUN")
        self.assertFalse(result["operations_enabled"])
        self.assertFalse(result["gpu_verified"])

    def test_readonly_rejects_other_model_at_8000(self):
        live = lambda: {"status": "LIVE_SERVICE_VERIFIED", "observed_model": "flash-next",
                        "expected_served_id": "qwen3.8-flash-next", "host_port": 8000,
                        "issues": []}
        with tempfile.TemporaryDirectory() as temp:
            result = p5.read_only(roots=[Path(temp)], service_inspector=live)
        self.assertEqual(result["stages"][3]["status"], "BLOCKED")

    def test_strict_json_duplicate_key(self):
        with self.assertRaises(ValueError):
            strict_json_loads('{"weight_map":{},"weight_map":{}}')

    def test_truncated_safetensors_header_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "test.safetensors"
            path.write_bytes(b"\x01\x00")
            with self.assertRaises(SafetensorsError):
                read_header(path)

    def test_recipe_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            bad = Path(temp) / "candidate.json"
            content = p5._recipe()
            content["runtime"]["host_port"] = 18300
            bad.write_text(json.dumps(content), encoding="utf-8")
            with patch.object(p5, "RECIPE_PATH", bad):
                with self.assertRaises(ValueError):
                    p5._recipe()

    def test_wizard_p5_status_not_claiming_runtime_pass(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = wizard_main(["model", "orcarouter-flash-next", "status", "--json"])
        report = json.loads(output.getvalue())
        self.assertEqual(rc, 0)
        self.assertEqual(report["stage"], "p5")
        self.assertEqual(report["runtime"], "NOT_RUN")
        self.assertFalse(report["operations_enabled"])

    def test_wizard_p5_start_and_approval_never_execute(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = wizard_main(["p5", "start", "--execute", "--approve-plan",
                              "a" * 64, "--json"])
        report = json.loads(output.getvalue())
        self.assertEqual(rc, 3)
        self.assertIn("UNVERIFIED_APPROVAL_CANNOT_EXECUTE", report["issues"])
        self.assertIsNone(report["plan_id"])
        self.assertFalse(report["executed"])

    def test_gpu_trial_never_starts_even_with_fake_approval(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = p5.main(["--gpu-trial", "--approve-plan", "a" * 64,
                          "--ack-downtime", "I_ACCEPT_27B_DOWNTIME", "--json"])
        report = json.loads(output.getvalue())
        self.assertEqual(rc, 3)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIn("P5_GPU_TRIAL_EXECUTOR_NOT_RELEASED", report["issues"])
        self.assertFalse(report["approval_accepted"])
        self.assertFalse(report["executed"])

    def test_vendored_reference_not_used_as_runtime_image(self):
        r = p5._recipe()
        self.assertFalse(r["reference"]["production_image_allowed"])
        self.assertIsNone(r["runtime"]["image_id"])
        self.assertTrue(r["safety"]["preserve_active_27b"])
        self.assertEqual(r["numerical_gate"]["strict_first_token_logprob_abs_max"],
                         1e-4)


if __name__ == "__main__":
    unittest.main()
