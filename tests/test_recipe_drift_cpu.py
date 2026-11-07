"""CPU/Fake-DGX tests for the generic recipe drift planner. No Docker/GPU/API."""
from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import recipe_drift as drift
from scripts.manager.service_manifest import policy
from wizard import main as router


def canonical():
    recipe, sha = drift.load_desired("27b")
    return recipe, sha


def docker_doc(*, running=True, image=None, name="qwen38-27b"):
    recipe, _ = canonical()
    expected = drift.desired_runtime(recipe)
    flags = expected["cmd"]
    cmd = [flags["_checkpoint"]]
    for key, value in flags.items():
        if key == "_checkpoint":
            continue
        cmd.append(key)
        if value is not True:
            cmd.append(str(value))
    return {
        "Id": "a" * 64, "Name": "/" + name,
        "Image": image or expected["image_id"],
        "State": {"Running": running},
        "Config": {
            "Cmd": cmd,
            "Env": ["PATH=/usr/bin", "HF_HOME=/hf", "HF_HUB_OFFLINE=1"],
            "Labels": {"blazux.recipe": "qwen38-27b",
                       "blazux.migration": "historical-plan-dynamic"},
        },
        "HostConfig": {
            "DeviceRequests": [{"Count": -1, "Capabilities": [["gpu"]]}],
            "PortBindings": {"8000/tcp": [{"HostPort": "8000", "HostIp": ""}]},
            "ShmSize": 16 * 1024 ** 3, "IpcMode": "host",
        },
        "Mounts": [{"Source": "/hf-cache", "Destination": "/hf",
                    "RW": False, "Type": "bind"}],
    }


def observe(target=None, *, running=False, flash_running=False, foreign=False):
    all_docs = {}
    live = []
    gpu = []
    if target is not None:
        all_docs["qwen38-27b"] = target
        if running:
            live.append("qwen38-27b")
            gpu.append("qwen38-27b")
    if flash_running:
        all_docs["qwen38-flash"] = {"Id": "b" * 64, "Name": "/qwen38-flash"}
        live.append("qwen38-flash")
        gpu.append("qwen38-flash")
    if foreign:
        all_docs["foreign-gpu"] = {"Id": "c" * 64, "Name": "/foreign-gpu"}
        live.append("foreign-gpu")
        gpu.append("foreign-gpu")
    return {"containers": all_docs, "running": live, "gpu_running": gpu}


def preview(target=None, *, action="status", running=False,
            flash_running=False, foreign=False):
    return drift.plan("27b", action,
                      observer=lambda: observe(target, running=running,
                                               flash_running=flash_running,
                                               foreign=foreign),
                      now=1794050000.0)


class RecipeDriftCPU(unittest.TestCase):
    def test_pinned_recipe_hash_is_not_rewritten(self):
        _, sha = canonical()
        self.assertRegex(sha, r"^[a-f0-9]{64}$")
        self.assertEqual(drift.policy()["api"]["host_port"], 8000)

    def test_normalizer_permits_equivalent_option_order_equals_and_numeric(self):
        left = drift.command_flags(["/hf/path", "--max-model-len", "8192",
                                    "--enforce-eager", "--gpu-memory-utilization", "0.70"])
        right = drift.command_flags(["/hf/path", "--gpu-memory-utilization=0.7",
                                     "--enforce-eager", "--max_model_len=8192"])
        self.assertEqual(left, right)

    def test_normalizer_rejects_duplicates_bad_checkpoint_and_numeric(self):
        for command in (
            ["/hf/path", "--port", "8000", "--port=8000"],
            ["/tmp/unpinned", "--port", "8000"],
            ["/hf/path", "--max-model_len", "invalid"],
            ["/hf/path", "--enforce-eager=true"],
        ):
            with self.subTest(command=command), self.assertRaises(ValueError):
                drift.command_flags(command)

    def test_equal_canonical_container_is_noop_and_does_not_use_p3_id(self):
        doc = docker_doc()
        result = preview(doc, action="start", running=True)
        self.assertEqual(result["status"], "NO_CHANGE_REQUIRED")
        self.assertEqual(result["decision"], "NOOP")
        self.assertEqual(result["diff"], [])
        self.assertEqual(result["container_id"], "a"*64)
        self.assertFalse(result["historical_p3_receipts_used_as_live_identity"])
        self.assertFalse(result["operations_enabled"])
        self.assertTrue(result["plan_id"])
        self.assertIn("HOST_HF_CACHE_SOURCE_NOT_PINNED_IN_RECIPE", result["advisories"])

    def test_migration_label_is_historical_not_drift(self):
        doc = docker_doc()
        doc["Config"]["Labels"]["blazux.migration"] = "other-old-receipt"
        self.assertEqual(preview(doc, running=True)["diff"], [])

    def test_stopped_match_is_start_existing_not_recreate(self):
        result = preview(docker_doc(running=False), action="start")
        self.assertEqual(result["decision"], "START_EXISTING")
        self.assertEqual(result["status"], "READY_FOR_OPERATOR_REVIEW_ONLY")

    def test_flags_drift_requires_recreate(self):
        doc = docker_doc()
        cmd = doc["Config"]["Cmd"]
        cmd[cmd.index("--tool-call-parser") + 1] = "wrong_parser"
        result = preview(doc, action="restart", running=True)
        self.assertEqual(result["decision"], "RECREATE")
        self.assertTrue(any(x["field"] == "cmd" for x in result["diff"]))

    def test_template_and_reasoning_drift_requires_recreate(self):
        doc = docker_doc()
        cmd = doc["Config"]["Cmd"]
        cmd[cmd.index("--chat-template") + 1] = "/hf/other.jinja"
        cmd[cmd.index("--reasoning-parser") + 1] = "incorrect"
        result = preview(doc, action="switch")
        self.assertEqual(result["decision"], "RECREATE")

    def test_revision_change_and_unrecognized_flag_detected(self):
        doc = docker_doc()
        doc["Config"]["Cmd"][0] = "/hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/" + "f"*40
        doc["Config"]["Cmd"].append("--unexpected-new-serving-option")
        result = preview(doc, action="reinstall")
        self.assertEqual(result["decision"], "RECREATE")
        self.assertGreater(len(result["diff"]), 0)

    def test_image_mount_and_env_diff(self):
        doc = docker_doc(image="sha256:" + "b"*64)
        doc["Mounts"][0]["RW"] = True
        doc["Config"]["Env"] = ["HF_HOME=/not-hf"]
        result = preview(doc, action="start")
        fields = {v["field"] for v in result["diff"]}
        self.assertTrue({"image_id", "hf_mount", "env"} <= fields)

    def test_different_source_mount_when_pinned(self):
        doc = docker_doc()
        result = drift.plan("27b", observer=lambda: observe(doc),
                            cache_source="/known-canonical-hf", now=1794050000)
        self.assertIn("hf_cache_source", {v["field"] for v in result["diff"]})

    def test_missing_model_install_reinstall_or_remove(self):
        self.assertEqual(preview(action="install")["decision"], "INSTALL")
        self.assertEqual(preview(action="reinstall")["decision"], "INSTALL")
        self.assertEqual(preview(action="remove")["decision"], "NOOP")

    def test_remove_and_reinstall_supported_not_hard_blocked_by_name(self):
        doc = docker_doc()
        self.assertEqual(preview(doc, action="remove")["decision"], "REMOVE_STOPPED")
        self.assertEqual(preview(doc, action="reinstall")["decision"], "RECREATE")
        self.assertEqual(preview(doc, action="remove", running=True)["decision"], "REMOVE_ACTIVE")

    def test_switch_requires_stop_old_and_not_two_gpu_models(self):
        doc = docker_doc()
        result = preview(doc, action="switch", flash_running=True)
        self.assertEqual(result["decision"], "START_EXISTING")
        self.assertEqual(result["active_model"], "flash-next")
        self.assertEqual(result["issues"], [])
        denied = preview(doc, action="switch", flash_running=True, foreign=True)
        self.assertIn("ONE_ACTIVE_MODEL_ONLY_VIOLATED", denied["issues"])
        self.assertIsNone(denied["plan_id"])

    def test_foreign_gpu_is_blocker_even_if_target_is_missing(self):
        denied = preview(action="install", foreign=True)
        self.assertIn("FOREIGN_GPU_CONTAINER_RUNNING", denied["issues"])
        self.assertFalse(denied["operations_enabled"])

    def test_missing_runtime_recipe_fails_closed_for_flash_and_orcarouter(self):
        for model in ("flash-next", "orcarouter"):
            with self.subTest(model=model):
                result = drift.plan(model, "install",
                                    observer=lambda: observe(), now=1794050000)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIsNone(result["plan_id"])

    def test_pinned_json_and_service_policy_mismatch_blocks(self):
        recipe, _ = canonical()
        cfg = policy()
        cfg["models"]["27b"]["served_id"] = "unexpected"
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / "recipes"
            p.mkdir()
            (p / "qwen38-27b.runtime.json").write_text(json.dumps(recipe), encoding="utf-8")
            with self.assertRaises(ValueError):
                drift.load_desired("27b", root=Path(folder), spec=cfg)

    def test_plan_is_stable_in_window_and_changes_with_live_id(self):
        first = preview(docker_doc(), action="start", running=True)
        next_ = preview(docker_doc(), action="start", running=True)
        changed = docker_doc()
        changed["Id"] = "f" * 64
        later = preview(changed, action="start", running=True)
        self.assertEqual(first["plan_id"], next_["plan_id"])
        self.assertNotEqual(first["plan_id"], later["plan_id"])
        self.assertTrue(first["expires_at_epoch_seconds"] > 1794050000)

    def test_malformed_observed_config_blocks_without_unsafe_guess(self):
        doc = docker_doc()
        doc["Config"]["Cmd"] = ["--port", "8000"]
        result = preview(doc, action="restart")
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("LIFECYCLE_PREFLIGHT_UNAVAILABLE:ValueError", result["issues"])

    def test_docker_failure_is_not_misread_as_missing_model(self):
        def run(args):
            raise OSError("no docker daemon")
        result = drift.plan("27b", "install",
                            observer=lambda: drift.collect_docker(run=run))
        self.assertEqual(result["status"], "BLOCKED")

    def test_approval_flags_cannot_force_read_only_cli_execution(self):
        from scripts.manager.recipe_drift import _deny
        fake = preview(docker_doc(), action="remove", running=True)
        with patch("scripts.manager.recipe_drift.plan", return_value=fake):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = router.main(["model", "27b", "lifecycle", "remove",
                                  "--execute", "--approve-plan", "a"*64, "--json"])
        self.assertEqual(rc, 3)
        self.assertFalse(json.loads(out.getvalue())["executed"])

    def test_wizard_read_only_recipe_diff_route_and_legacy_preservation(self):
        fake = preview(docker_doc(), running=True)
        with patch("scripts.manager.recipe_drift.plan", return_value=fake):
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = router.main(["model", "27b", "recipe-diff", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out.getvalue())["requested_action"], "status")


if __name__ == "__main__":
    unittest.main()
