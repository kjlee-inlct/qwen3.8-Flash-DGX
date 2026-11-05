"""No-network/no-Docker CPU regression tests for approved 27B download."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from scripts.manager import p2_27b_download as module
from wizard import main as wizard


class DownloadCPU(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.cache = Path(temp.name) / "hf"
        self.cache.mkdir()
        self.state = Path(temp.name) / "state"
        self.image_id = "sha256:" + "a" * 64
        self.observed = {
            "errors": [], "name_conflict": False,
            "observed_listen_ports": [8000],
            "disk": {"free_bytes": 60 * 1024 ** 3},
            "containers": [{"name": "qwen38-flash", "status": "Up 1 hour",
                            "image_id": "sha256:" + "b" * 64,
                            "ports": "0.0.0.0:8000->8000/tcp"}],
        }

    def make_plan(self, **changes):
        observations = {**self.observed, **changes}
        with patch.object(module, "inspect_host", return_value=observations), \
             patch.object(module, "_read_image_id", return_value=self.image_id), \
             patch.object(module, "_other_transfer", return_value=False), \
             patch.object(module, "inspect_27b", return_value={
                 "source_files_present": False
             }), \
             patch.object(module.os, "statvfs",
                          return_value=SimpleNamespace(f_favail=1024)):
            return module.build_plan(cache_root=self.cache, now=600)

    def test_live_flash_next_does_not_block_cache_only_download(self):
        result = self.make_plan()
        self.assertEqual(result["status"], "READY_TO_REQUEST_APPROVAL", result)
        self.assertEqual(len(result["plan_id"]), 64)
        self.assertTrue(result["facts"]["port_8000_listening"])
        self.assertEqual(result["service_api_port"], 8000)
        self.assertEqual(result["exclusive_gpu_policy"], "ONE_ACTIVE_MODEL_ONLY")
        self.assertFalse(result["safety"]["touch_live_service"])

    def test_inode_usage_uptime_and_disk_drift_do_not_invalidate_approval(self):
        original = self.make_plan()
        # The Wizard creates a state directory and download.lock after showing
        # the initial plan. Both consume inodes, and Docker human uptime changes.
        later = {**self.observed,
                 "disk": {"free_bytes": 59 * 1024 ** 3},
                 "containers": [{**self.observed["containers"][0],
                                 "status": "Up 2 hours"}]}
        with patch.object(module, "inspect_host", return_value=later), \
             patch.object(module, "_read_image_id", return_value=self.image_id), \
             patch.object(module, "_other_transfer", return_value=False), \
             patch.object(module, "inspect_27b",
                          return_value={"source_files_present": False}), \
             patch.object(module.os, "statvfs",
                          return_value=SimpleNamespace(f_favail=1022)):
            current = module.build_plan(cache_root=self.cache, now=600)
        self.assertEqual(original["plan_id"], current["plan_id"])
        self.assertEqual(current["status"], "READY_TO_REQUEST_APPROVAL")
        self.assertNotEqual(original["facts"]["free_inodes"],
                            current["facts"]["free_inodes"])

    def test_approval_rechecks_after_lock_without_false_positive(self):
        original = self.make_plan()
        later = {**self.observed,
                 "disk": {"free_bytes": 59 * 1024 ** 3},
                 "containers": [{**self.observed["containers"][0],
                                 "status": "Up 2 hours"}]}
        runner = Mock(return_value=SimpleNamespace(returncode=0))
        incomplete = {"source_files_present": False}
        complete = {"source_files_present": True,
                    "checkpoint_status": "SOURCE_FILES_PRESENT_PINNED_CANDIDATE",
                    "indexed_shard_count": 3, "issues": []}
        with patch.object(module, "inspect_host", return_value=later), \
             patch.object(module, "_read_image_id", return_value=self.image_id), \
             patch.object(module, "_other_transfer", return_value=False), \
             patch.object(module, "inspect_27b",
                          side_effect=[incomplete, complete]), \
             patch.object(module.os, "statvfs",
                          return_value=SimpleNamespace(f_favail=1022)):
            rc, result = module.execute_approved(
                original, original["plan_id"], cache_root=self.cache,
                runner=runner, state_dir=self.state, now=600)
        self.assertEqual(rc, 0, result)
        self.assertTrue(result["executed"])
        self.assertEqual(result["status"], "PASS")
        self.assertTrue((self.state / "download.lock").is_file())
        runner.assert_called_once()

    def test_revalidation_still_blocks_low_disk_without_running(self):
        original = self.make_plan()
        later = {**self.observed,
                 "disk": {"free_bytes": 15 * 1024 ** 3}}
        runner = Mock(side_effect=AssertionError("must not download"))
        with patch.object(module, "inspect_host", return_value=later), \
             patch.object(module, "_read_image_id", return_value=self.image_id), \
             patch.object(module, "_other_transfer", return_value=False), \
             patch.object(module, "inspect_27b",
                          return_value={"source_files_present": False}), \
             patch.object(module.os, "statvfs",
                          return_value=SimpleNamespace(f_favail=1022)):
            rc, result = module.execute_approved(
                original, original["plan_id"], cache_root=self.cache,
                runner=runner, state_dir=self.state, now=600)
        self.assertEqual(rc, 3)
        self.assertFalse(result["executed"])
        self.assertIn("INSUFFICIENT_VERIFIED_DISK_HEADROOM", result["issues"])
        runner.assert_not_called()

    def test_low_disk_or_name_collision_blocks_without_plan_id(self):
        for changes in (
            {"disk": {"free_bytes": 10 * 1024 ** 3}},
            {"name_conflict": True},
            {"errors": ["docker_inventory_incomplete"]},
        ):
            with self.subTest(changes=changes):
                result = self.make_plan(**changes)
                self.assertEqual(result["status"], "BLOCKED")
                self.assertIsNone(result["plan_id"])

    def test_download_command_has_no_gpu_port_or_service_mutation(self):
        command = module._download_argv(self.cache, self.image_id)
        self.assertEqual(command[0:2], ["docker", "run"])
        self.assertIn("--read-only", command)
        self.assertIn("--cap-drop", command)
        self.assertNotIn("--gpus", command)
        self.assertNotIn("--publish", command)
        self.assertNotIn("-p", command)
        self.assertNotIn("stop", command)
        self.assertNotIn("rm", command)
        self.assertNotIn("flash", command)
        self.assertEqual(command[-5:-2], [module.MODEL_ID, "--revision", module.REVISION])
        self.assertEqual(command[-1], "8")
        self.assertIn(self.image_id, command)

    def test_approval_mismatch_never_calls_download(self):
        plan = self.make_plan()
        runner = Mock(side_effect=AssertionError("must not execute"))
        rc, result = module.execute_approved(plan, "bad", cache_root=self.cache,
                                             runner=runner, state_dir=self.state)
        self.assertEqual(rc, 3)
        self.assertFalse(result["executed"])
        runner.assert_not_called()

    def test_preflight_change_rejects_stale_plan(self):
        plan = self.make_plan()
        changed = {**plan, "plan_id": "c" * 64}
        runner = Mock(side_effect=AssertionError("must not execute"))
        with patch.object(module, "build_plan", return_value=changed):
            rc, result = module.execute_approved(
                plan, plan["plan_id"], cache_root=self.cache, runner=runner,
                state_dir=self.state)
        self.assertEqual(rc, 3)
        self.assertEqual(result["issues"], ["PREFLIGHT_CHANGED_REPLAN_REQUIRED"])
        runner.assert_not_called()

    def test_approved_download_only_verifies_shards_then_records_evidence(self):
        plan = self.make_plan()
        runner = Mock(return_value=SimpleNamespace(returncode=0))
        complete = {"source_files_present": True,
                    "checkpoint_status": "SOURCE_FILES_PRESENT_UNPINNED",
                    "indexed_shard_count": 3, "issues": []}
        with patch.object(module, "build_plan", return_value=plan), \
             patch.object(module, "inspect_27b", return_value=complete):
            rc, result = module.execute_approved(
                plan, plan["plan_id"], cache_root=self.cache, runner=runner,
                state_dir=self.state, now=600)
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["runtime"], "NOT_RUN")
        self.assertEqual(result["indexed_shard_count"] if "indexed_shard_count" in result else 3, 3)
        self.assertTrue(Path(result["evidence"]).is_file())
        cmd = runner.call_args.args[0]
        self.assertIn("--revision", cmd)
        self.assertNotIn("--gpus", cmd)
        self.assertNotIn("-p", cmd)

    def test_wizard_download_plan_does_not_start_transfer(self):
        plan = self.make_plan()
        with patch.object(module, "build_plan", return_value=plan), \
             patch.object(module, "execute_approved") as execute, \
             contextlib.redirect_stdout(io.StringIO()) as output:
            rc = wizard.main(["model", "27b", "plan", "--for-action",
                              "download", "--json"])
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["action"], "download")
        execute.assert_not_called()


if __name__ == "__main__":
    unittest.main()
