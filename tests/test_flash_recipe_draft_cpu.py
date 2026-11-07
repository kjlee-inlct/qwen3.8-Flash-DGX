"""P3-E source-only Flash-Next hybrid candidate comparison Fake-DGX tests."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.manager import flash_recipe_review as review
from scripts.manager import p3_dg_acceptance as dg

ID = "a" * 64


def make_flash(root: Path):
    recipe, _ = review.load_draft()
    data = recipe["docker"]
    cache = root / "hf"
    view_name = recipe["model"]["source_revision"] + "-fp8hybrid"
    view = cache / "hub" / dg.FLASH_REPO_CACHE / "snapshots" / view_name
    view.mkdir(parents=True)
    for name in (".prepared", "config.json", "tokenizer.json",
                 "tokenizer_config.json", "model.safetensors.index.json"):
        (view / name).write_text("{}")
    cmd = [review.SOURCE_PREFIX + view_name]
    for k, value in recipe["observed_vllm"]["value_flags"].items():
        cmd.extend((k, value))
    cmd += recipe["observed_vllm"]["boolean_flags"]
    cmd += ["-cc.cudagraph_mode=PIECEWISE",
            '-cc.splitting_ops=["vllm::unified_attention_with_output"]']
    for k, value in recipe["observed_vllm"]["json_flags"].items():
        cmd.extend((k, json.dumps(value)))
    doc = {
        "Id": ID, "Name": "/qwen38-flash", "Image": data["image_id"],
        "State": {"Running": False},
        "Config": {
            "Entrypoint": ["vllm", "serve"],
            "Cmd": cmd,
            "Env": [k + "=" + v for k, v in recipe["required_environment"].items()],
            "Labels": {},
        },
        "HostConfig": {
            "IpcMode": "host", "ShmSize": data["shm_size_bytes"],
            "DeviceRequests": [{"Count": -1, "Capabilities": [["gpu"]]}],
            "PortBindings": {"8000/tcp": [{"HostIp": "", "HostPort": "8000"}]},
        },
        "Mounts": [
            {"Type": "bind", "Destination": "/hf",
             "Source": str(cache), "RW": True},
            {"Type": "bind", "Destination": "/qwen38/chat_template.jinja",
             "Source": str(root / "chat_template.jinja"), "RW": False},
        ],
    }
    return doc, recipe


class FlashRecipeDraftCPU(unittest.TestCase):
    def test_draft_is_intentionally_unregistered_and_non_executable(self):
        r, sha = review.load_draft()
        self.assertEqual(len(sha), 64)
        self.assertEqual(r["status"], "SOURCE_DRAFT_NOT_RUNTIME_QUALIFIED")
        self.assertFalse(r["launch_allowed"])
        self.assertFalse(r["register_as_runtime_recipe"])
        self.assertEqual(r["engine"], "vllm")
        self.assertEqual(r["vllm_version"], "0.32.0")

    def test_matches_precise_observed_fields_but_never_claims_reinstall(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = make_flash(Path(tmp))
            candidate, issues, _ = dg.flash_observed_candidate(doc)
            self.assertFalse(issues)
            self.assertTrue(candidate["hybrid_preparation_verified"])
            out = review.compare_observation(candidate, doc)
            self.assertEqual(out["status"], "MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED")
            self.assertEqual(out["issues"], [])
            self.assertFalse(out["host_specific_extra_env_and_mounts_qualified"])
            self.assertFalse(out["launch_allowed"])
            self.assertFalse(out["complete_docker_runtime_reinstall_qualified"])

    def test_observed_drift_changes_review_not_historical_receipt(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = make_flash(Path(tmp))
            i = doc["Config"]["Cmd"].index("--max-model-len") + 1
            doc["Config"]["Cmd"][i] = "262144"
            candidate, _, _ = dg.flash_observed_candidate(doc)
            out = review.compare_observation(candidate, doc)
            self.assertEqual(out["status"], "DRAFT_FIELD_MISMATCH_REVIEW_REQUIRED")
            self.assertIn("REQUIRED_VLLM_VALUE_FLAG_CHANGED:--max-model-len", out["issues"])
            self.assertFalse(out["launch_allowed"])

    def test_missing_effort_alias_template_mount_cannot_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = make_flash(Path(tmp))
            doc["Mounts"] = [m for m in doc["Mounts"]
                             if m["Destination"] != "/qwen38/chat_template.jinja"]
            candidate, _, _ = dg.flash_observed_candidate(doc)
            out = review.compare_observation(candidate, doc)
            self.assertIn("EFFORT_ALIAS_TEMPLATE_READ_ONLY_MOUNT_UNVERIFIED",
                          out["issues"])

    def test_image_digest_drift_cannot_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = make_flash(Path(tmp))
            doc["Image"] = "sha256:" + "b" * 64
            candidate, _, _ = dg.flash_observed_candidate(doc)
            out = review.compare_observation(candidate, doc)
            self.assertIn("IMAGE_DIGEST_CHANGED", out["issues"])

    def test_malformed_recipe_cannot_enable_launch(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "draft.json"
            cfg, _ = review.load_draft()
            cfg["launch_allowed"] = True
            p.write_text(json.dumps(cfg))
            with self.assertRaisesRegex(ValueError, "FLASH_SOURCE_DRAFT_POLICY_INVALID"):
                review.load_draft(file=p)
            cfg["launch_allowed"] = False
            cfg["model"]["source_revision"] = "b" * 40
            p.write_text(json.dumps(cfg))
            with self.assertRaisesRegex(ValueError, "FLASH_SOURCE_DRAFT_POLICY_INVALID"):
                review.load_draft(file=p)

    def test_stage_e_keeps_nonrelease_even_on_exact_field_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = make_flash(Path(tmp))
            history = {"status": "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED",
                       "issues": [], "records": {
                           "a": {"flash_id": ID, "flash_image": doc["Image"]}}}
            out = dg.stage_e({"containers": {"qwen38-flash": doc}},
                             historical=history)
            self.assertEqual(out["status"], "DRAFT_REVIEW_REQUIRED")
            self.assertFalse(out["canonical_recipe_registered"])
            self.assertEqual(out["source_draft_field_review"]["status"],
                             "MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED")
            self.assertEqual(out["issues"],
                             ["FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED"])

    def test_json_semantic_drift_is_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = make_flash(Path(tmp))
            cmd = doc["Config"]["Cmd"]
            i = cmd.index("--speculative-config") + 1
            cmd[i] = json.dumps({"method": "mtp", "num_speculative_tokens": 99,
                                 "max_model_len": 500000})
            candidate, _, _ = dg.flash_observed_candidate(doc)
            out = review.compare_observation(candidate, doc)
            self.assertIn("REQUIRED_VLLM_JSON_FLAG_CHANGED:--speculative-config",
                          out["issues"])

    def test_coverage_reports_host_unknowns_without_leaking_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = make_flash(Path(tmp))
            doc["Config"]["Env"].append("PRIVATE_TOKEN=not-for-log")
            doc["Mounts"].append({
                "Type": "bind", "Destination": "/extra/private",
                "Source": str(Path(tmp) / "secret-file"), "RW": False,
            })
            candidate, _, _ = dg.flash_observed_candidate(doc)
            out = review.compare_observation(candidate, doc)
            self.assertEqual(out["status"], "MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED")
            c = out["host_runtime_qualification_coverage"]
            self.assertEqual(c["additional_environment_key_count"], 1)
            self.assertEqual(c["additional_mount_count"], 1)
            self.assertFalse(c["full_container_reinstall_qualified"])
            self.assertNotIn("not-for-log", json.dumps(out))
            self.assertNotIn("secret-file", json.dumps(out))

    def test_relative_template_source_is_not_treated_as_qualified_mount(self):
        with tempfile.TemporaryDirectory() as tmp:
            doc, _ = make_flash(Path(tmp))
            doc["Mounts"][1]["Source"] = "relative-template"
            candidate, _, _ = dg.flash_observed_candidate(doc)
            out = review.compare_observation(candidate, doc)
            self.assertIn("TEMPLATE_MOUNT_SOURCE_NOT_ABSOLUTE", out["issues"])

    def test_flash_draft_blockers_track_p8_not_completed_p3_g(self):
        draft, _ = review.load_draft()
        blockers = draft["release_blockers"]
        self.assertIn("P8_FAULT_RECOVERY_AND_FINAL_OPERATIONS_ACCEPTANCE_NOT_RUN", blockers)
        self.assertFalse(any("P3_G_REAL_BIDIRECTIONAL" in x for x in blockers))


if __name__ == "__main__":
    unittest.main()
