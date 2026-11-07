"""Pure CPU/Fake-DGX regression for protected P2 Native Tools V1 recipe.

No Docker, port, model, GPU or receipt is touched by these tests.
"""
from __future__ import annotations

from copy import deepcopy
from types import SimpleNamespace
import unittest

from scripts.manager import p2_27b_tool_variant as mod


def fixtures():
    source = {
        "Id": "a" * 64, "Image": "sha256:" + "b" * 64,
        "State": {"Running": True},
        "Config": {"Cmd": ["/hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/"
                           + mod.REVISION,
                           "--served-model-name", mod.SERVED]},
        "HostConfig": {"AutoRemove": False, "DeviceRequests": [{"Count": -1}],
                       "PortBindings": {"8000/tcp": [{"HostPort": "8000"}]}},
        "Mounts": [{"Destination": "/hf", "Source": "/protected/hf-cache",
                    "RW": False, "Type": "bind"}],
    }
    flash = {
        "Id": "c" * 64, "Image": "sha256:" + "d" * 64,
        "State": {"Running": False},
        "HostConfig": {"AutoRemove": False, "DeviceRequests": []},
    }
    webui = {
        "Id": "e" * 64, "Image": "sha256:" + "f" * 64,
        "State": {"Running": True},
        "HostConfig": {"AutoRemove": False, "DeviceRequests": [],
                       "Runtime": "runc"},
        "Config": {"Env": []},
    }
    live = {
        "status": "LIVE_SERVICE_VERIFIED", "issues": [],
        "observed_model": "27b", "expected_served_id": mod.SERVED,
        "observed_model_ids": [mod.SERVED], "host_port": 8000,
        "active_container": {"name": mod.SOURCE_CONTAINER},
    }
    return {"source": source, "flash": flash, "webui": webui, "live": live,
            "all": [mod.SOURCE_CONTAINER, mod.FALLBACK_CONTAINER, "webui"],
            "running": [mod.SOURCE_CONTAINER, "webui"]}


def preview(fx):
    def inspect(name):
        return deepcopy({
            mod.SOURCE_CONTAINER: fx["source"],
            mod.FALLBACK_CONTAINER: fx["flash"],
            "webui": fx["webui"],
        }[name])
    def run(args):
        if args[:3] == ["docker", "ps", "-a"]:
            return SimpleNamespace(returncode=0, stdout="\n".join(fx["all"]) + "\n")
        if args[:2] == ["docker", "ps"]:
            return SimpleNamespace(returncode=0, stdout="\n".join(fx["running"]) + "\n")
        raise AssertionError("Unexpected mutation/command: " + str(args))
    return mod.inspect_variant(live=lambda: deepcopy(fx["live"]),
                               inspect=inspect, run=run, now=1794024000)


class ProtectedVariantCPU(unittest.TestCase):
    def test_isolated_candidate_identity_without_execution(self):
        r = preview(fixtures())
        self.assertTrue(r["read_only_preflight_pass"], r["issues"])
        self.assertEqual(r["status"], "BLOCKED_PENDING_PARSER_AND_LIVE_ACCEPTANCE")
        self.assertIsNone(r["plan_id"])
        self.assertFalse(r["execution_enabled"])
        self.assertFalse(r["executed"])
        self.assertFalse(r["approval_accepted"])
        self.assertEqual(r["variant_id"], "nvidia-27b-native-tools-v1")
        cmd = r["candidate_command_NOT_EXECUTABLE"]
        self.assertEqual(cmd[cmd.index("--name") + 1], mod.VARIANT_CONTAINER)
        self.assertNotEqual(cmd[cmd.index("--name") + 1], mod.SOURCE_CONTAINER)
        self.assertIn("blazux.variant=" + mod.VARIANT_ID, cmd)
        self.assertIn("qwen3_coder", cmd)
        self.assertIn("qwen3", cmd)
        self.assertIn("/protected/hf-cache:/hf:ro", cmd)
        self.assertEqual(r["host_port"], 8000)
        self.assertTrue(r["preview_fingerprint_not_approval"])
        self.assertIn("integrate_variant_into_service_manifest_and_journal_before_any_execute",
                      r["outstanding_gates"])

    def test_original_default_recipe_remains_unchanged(self):
        from pathlib import Path
        from scripts.manager.p2_27b_launch_preview import _candidate_argv
        img = "sha256:" + "b" * 64
        baseline = _candidate_argv(Path("/protected/hf-cache"), img)
        self.assertEqual(baseline[baseline.index("--name") + 1],
                         mod.SOURCE_CONTAINER)
        self.assertNotIn("--enable-auto-tool-choice", baseline)

    def test_other_running_gpu_container_denied(self):
        f = fixtures()
        f["webui"]["HostConfig"]["DeviceRequests"] = [{"Count": 1}]
        r = preview(f)
        self.assertIn("OTHER_GPU_CONTAINER_RUNNING", r["issues"])
        self.assertFalse(r["read_only_preflight_pass"])
        self.assertIsNone(r["candidate_command_NOT_EXECUTABLE"])

    def test_existing_variant_name_denied(self):
        f = fixtures()
        f["all"].append(mod.VARIANT_CONTAINER)
        self.assertIn("VARIANT_CONTAINER_NAME_OCCUPIED", preview(f)["issues"])

    def test_source_id_change_denied(self):
        f = fixtures()
        f["source"]["Image"] = "not-an-image"
        self.assertIn("PRESERVED_27B_ID_IMAGE_AUTOREMOVE_UNVERIFIED",
                      preview(f)["issues"])

    def test_wrong_served_model_denied(self):
        f = fixtures()
        f["live"]["observed_model_ids"] = ["qwen3.8-flash-next"]
        self.assertIn("PRESERVED_27B_LIVE_IDENTITY_NOT_VERIFIED",
                      preview(f)["issues"])

    def test_original_container_not_running_denied(self):
        f = fixtures()
        f["running"].remove(mod.SOURCE_CONTAINER)
        self.assertIn("PRESERVED_27B_NOT_RUNNING", preview(f)["issues"])

    def test_flash_fallback_running_denied(self):
        f = fixtures()
        f["flash"]["State"]["Running"] = True
        self.assertIn("FLASH_FALLBACK_MUST_BE_STOPPED", preview(f)["issues"])

    def test_writable_hf_mount_denied(self):
        f = fixtures()
        f["source"]["Mounts"][0]["RW"] = True
        self.assertIn("ORIGINAL_READ_ONLY_HF_BIND_NOT_VERIFIED",
                      preview(f)["issues"])

    def test_changed_original_cmd_denied(self):
        f = fixtures()
        f["source"]["Config"]["Cmd"] += ["--enable-auto-tool-choice"]
        self.assertIn("PRESERVED_ORIGINAL_CMD_ALREADY_CHANGED", preview(f)["issues"])

    def test_source_port_mismatch_denied(self):
        f = fixtures()
        f["source"]["HostConfig"]["PortBindings"]["8000/tcp"][0]["HostPort"] = "8001"
        self.assertIn("PRESERVED_27B_RUNNING_PORT_MISMATCH", preview(f)["issues"])

    def test_missing_source_gpu_request_denied(self):
        f = fixtures()
        f["source"]["HostConfig"]["DeviceRequests"] = []
        self.assertIn("SOURCE_GPU_REQUEST_NOT_VERIFIED", preview(f)["issues"])

    def test_inventory_error_fails_closed(self):
        f = fixtures()
        def failed_run(args):
            return SimpleNamespace(returncode=1, stdout="")
        r = mod.inspect_variant(live=lambda: f["live"],
                                inspect=lambda _: f["source"],
                                run=failed_run, now=1794024000)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertIn("READ_ONLY_INSPECTION_UNAVAILABLE", r["issues"])

    def test_preview_fingerprint_not_reusable_approval(self):
        one = preview(fixtures())
        two = preview(fixtures())
        self.assertEqual(one["preview_fingerprint_not_approval"],
                         two["preview_fingerprint_not_approval"])
        self.assertIsNone(one["plan_id"])
        self.assertFalse(one["execution_enabled"])


if __name__ == "__main__":
    unittest.main()
