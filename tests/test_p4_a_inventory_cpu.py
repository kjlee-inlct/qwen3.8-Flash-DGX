"""P4-A read-only storage inventory safety and actual Wizard route tests."""
from __future__ import annotations

import contextlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import p4_a_inventory as inv
from wizard import main as router

ID = "a" * 64


def fake_snapshot():
    return {
        "running": ["qwen38-27b"], "gpu_running": ["qwen38-27b"],
        "port_owners": ["qwen38-27b"],
        "containers": {
            "qwen38-27b": {"Image": "sha256:" + "b"*64, "Id": "c"*64},
            "qwen38-flash": {
                "Image": "sha256:" + "d"*64, "Id": ID,
                "Config": {"Env": ["ACCESS_TOKEN=private-secret"]},
                "Mounts": [{"Source": "/private/path/hf", "Destination": "/hf",
                             "Type": "bind"}],
            },
            "other-service": {"Id": "e"*64},
        },
    }


def fake_policy():
    return {"models": {
        "27b": {"container_name": "qwen38-27b", "served_id": "qwen3.8-27b"},
        "flash-next": {"container_name": "qwen38-flash",
                       "served_id": "qwen3.8-flash-next"},
        "orcarouter": {"container_name": "qwen38-orcarouter", "served_id": None},
    }}


def fake_live():
    return {"status": "LIVE_SERVICE_VERIFIED", "observed_model": "27b",
            "issues": [], "expected_served_id": "qwen3.8-27b"}


def fake_run(argv, *, timeout):
    if argv[:2] == ["docker", "system"]:
        return subprocess.CompletedProcess(argv, 0,
            '{"Type":"Images","TotalCount":"3","Active":"2","Size":"120GB","Reclaimable":"20GB (16%)"}\n'
            '{"Type":"Containers","TotalCount":"3","Active":"1","Size":"20MB","Reclaimable":"10MB (50%)"}\n', "")
    if argv[:4] == ["du", "-s", "-B1", "--"]:
        return subprocess.CompletedProcess(argv, 0, "4096\t/private/secret-path\n", "")
    raise AssertionError("Unexpected command " + str(argv))


class P4AInventoryCPU(unittest.TestCase):
    def make_cache(self, root):
        (root / "hub" / "models--nvidia--Qwen3.8-Flash-Next-NVFP4").mkdir(
            parents=True)
        (root / "hub" / "models--nvidia--Qwen3.8-27B-NVFP4").mkdir()
        return root

    def observe(self, root, *, run=fake_run, snapshot=fake_snapshot,
                live=fake_live):
        return inv.inspect_p4_a(
            snapshot_fn=snapshot, live_fn=live,
            policy_fn=fake_policy,
            cache_roots_fn=lambda: [root],
            run=run)

    def test_read_only_model_and_cache_inventory_never_estimates_safe_deletion(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_cache(Path(tmp) / "hf")
            doc = self.observe(root)
            self.assertEqual(doc["status"], "READ_ONLY_INVENTORY_COMPLETE")
            self.assertEqual(doc["observed_active_model"], "27b")
            self.assertTrue(doc["active_api_verified"])
            self.assertTrue(doc["managed_containers"][1]["container_present"])
            self.assertEqual(doc["cache_storage"][0]["cache_allocated_bytes"], 4096)
            self.assertTrue(doc["cache_storage"][0]["flash_repo_present"])
            self.assertTrue(doc["cache_storage"][0]["27b_repo_present"])
            self.assertEqual(doc["docker_disk_usage"]["rows"][0]["type"], "Images")
            self.assertFalse(doc["reclaimable_bytes_verified"])
            self.assertTrue(doc["preservation"]["flash_reinstall_reference_for_p8"])
            self.assertIsNone(doc["removal_plan_id"])
            self.assertFalse(doc["executed"])
            self.assertFalse(doc["containers_deleted"])
            self.assertFalse(doc["images_deleted"])
            self.assertFalse(doc["hf_files_deleted"])
            self.assertNotIn("private-secret", json.dumps(doc))
            self.assertNotIn("/private/path", json.dumps(doc))
            self.assertNotIn(str(root), json.dumps(doc))

    def test_foreign_gpu_container_or_api_mismatch_is_partial_not_cleanup_approval(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_cache(Path(tmp) / "hf")
            s = fake_snapshot()
            s["gpu_running"].append("other-service")
            d = self.observe(root, snapshot=lambda: s)
            self.assertEqual(d["status"], "READ_ONLY_INVENTORY_PARTIAL")
            self.assertIn("GPU_OWNERSHIP_REQUIRES_FURTHER_VERIFICATION", d["issues"])
            self.assertFalse(d["operations_enabled"])
            d = self.observe(root, live=lambda: {"status": "BLOCKED"})
            self.assertIn("LIVE_API_IDENTITY_NOT_VERIFIED", d["issues"])

    def test_unavailable_docker_df_is_not_falsely_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_cache(Path(tmp) / "hf")
            def bad_run(args, *, timeout):
                if args[0] == "docker":
                    return subprocess.CompletedProcess(args, 1, "", "private error")
                return fake_run(args, timeout=timeout)
            doc = self.observe(root, run=bad_run)
            self.assertEqual(doc["status"], "READ_ONLY_INVENTORY_PARTIAL")
            self.assertEqual(doc["docker_disk_usage"]["rows"], [])
            self.assertIn("DOCKER_CAPACITY_ESTIMATES_UNAVAILABLE", doc["issues"])
            self.assertNotIn("private error", json.dumps(doc))

    def test_docker_df_values_are_validated_not_secret_leaked(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_cache(Path(tmp) / "hf")
            def bad_run(args, *, timeout):
                if args[0] == "docker":
                    return subprocess.CompletedProcess(args, 0,
                        '{"Type":"Images","TotalCount":"1","Active":"1","Size":"/secret","Reclaimable":"x"}\n', "")
                return fake_run(args, timeout=timeout)
            doc = self.observe(root, run=bad_run)
            self.assertEqual(doc["status"], "READ_ONLY_INVENTORY_PARTIAL")
            self.assertNotIn("/secret", json.dumps(doc))

    def test_missing_cache_directory_does_not_claim_capacity(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "no-hf"
            doc = self.observe(root)
            self.assertEqual(doc["status"], "READ_ONLY_INVENTORY_PARTIAL")
            self.assertEqual(doc["cache_storage"][0]["cache_allocated_bytes"], None)
            self.assertFalse(doc["cache_storage"][0]["exists"])

    def test_wizard_p4_a_inventory_route_readonly_and_execute_denied(self):
        fake = {
            "schema_version": 1, "stage": "P4-A", "status": "READ_ONLY_INVENTORY_COMPLETE",
            "action": "STORAGE_CAPACITY_AND_MODEL_STATE_INVENTORY",
            "issues": [], "executed": False, "operations_enabled": False,
            "removal_plan_id": None,
        }
        with patch("scripts.manager.p4_a_inventory.inspect_p4_a", return_value=fake) as probe:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = router.main(["storage", "flash-next", "inventory", "--json"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(out.getvalue())["stage"], "P4-A")
            probe.assert_called_once()
        with patch("scripts.manager.p4_a_inventory.inspect_p4_a") as probe:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = router.main(["p4", "inventory", "--execute",
                                  "--approve-plan", "a"*64, "--json"])
            self.assertEqual(rc, 3)
            self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")
            probe.assert_not_called()

    def test_du_command_is_bounded_to_read_only_whitelist(self):
        with self.assertRaisesRegex(ValueError, "P4_A_COMMAND_NOT_READ_ONLY"):
            inv._run(["docker", "rm", "-f", "qwen38-flash"], timeout=1)
        with self.assertRaisesRegex(ValueError, "P4_A_COMMAND_NOT_READ_ONLY"):
            inv._run(["du", "-s", "-B1", "--", "relative/path"], timeout=1)


if __name__ == "__main__":
    unittest.main()
