"""CPU-only P4-B/C candidate review, rehearsal and CLI safety tests."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import patch

from scripts.manager import p4_bc_dry_run as bc
from wizard import main as wizard


def fake_inventory():
    return {
        "schema_version": 1, "stage": "P4-A",
        "status": "READ_ONLY_INVENTORY_COMPLETE", "issues": [],
        "active_api_verified": True, "executed": False, "operations_enabled": False,
        "observed_active_model": "27b",
        "managed_containers": [
            {"model": "27b", "container_present": True, "container_running": True},
            {"model": "flash-next", "container_present": True, "container_running": False},
            {"model": "orcarouter", "container_present": False, "container_running": False},
        ],
        "cache_storage": [
            {"root_index": 1, "exists": True, "flash_repo_present": True,
             "27b_repo_present": True, "orcarouter_repo_present": False,
             "filesystem_total_bytes": 982819848192, "filesystem_free_bytes": 324880961536,
             "known_model_repo_allocated_bytes": {
                 "flash-next": 75967504384, "27b": 21932584960, "orcarouter": None}},
            {"root_index": 2, "exists": True, "flash_repo_present": False,
             "27b_repo_present": False, "orcarouter_repo_present": True,
             "filesystem_total_bytes": 982819848192, "filesystem_free_bytes": 324880961536,
             "known_model_repo_allocated_bytes": {
                 "flash-next": None, "27b": None, "orcarouter": 177686446080}},
        ],
        "docker_disk_usage": {
            "status": "OBSERVED_DOCKER_ESTIMATES",
            "rows": [
                {"type": "Images", "docker_reported_size": "28.74GB",
                 "docker_reported_reclaimable": "0B (0%)"},
                {"type": "Containers", "docker_reported_size": "416.7MB",
                 "docker_reported_reclaimable": "182.7MB (43%)"},
                {"type": "Local Volumes", "docker_reported_size": "34.16kB",
                 "docker_reported_reclaimable": "0B (0%)"},
                {"type": "Build Cache", "docker_reported_size": "7.364MB",
                 "docker_reported_reclaimable": "2.088MB"},
            ],
        },
    }


class P4BCFakeDGXCPU(unittest.TestCase):
    def test_review_classifies_and_preserves_assets(self):
        b = bc.review_candidates(fake_inventory())
        self.assertEqual(b["status"], "READ_ONLY_REVIEW_COMPLETE", b["issues"])
        self.assertEqual(b["candidate_count"], 9)
        self.assertIsNone(b["safe_reclaimable_bytes"])
        self.assertIsNone(b["plan_id"])
        self.assertFalse(b["operations_enabled"])
        classes = {r["resource_key"]: r["review_class"] for r in b["resources"]}
        self.assertEqual(classes["container:27b"], "PRESERVE_ACTIVE_MODEL")
        self.assertEqual(classes["container:flash-next"], "PRESERVE_P8_FLASH_REINSTALL_REFERENCE")
        self.assertEqual(classes["root-2:orcarouter"], "PRESERVE_P5_ORCAROUTER_SOURCE")
        self.assertEqual(classes["docker:images"], "NOT_AN_EXACT_RESOURCE_TARGET")

    def test_all_operations_remain_unselected(self):
        c = bc.rehearse_cleanup(bc.review_candidates(fake_inventory()))
        self.assertEqual(c["status"], "DRY_RUN_COMPLETE_RELEASE_GATED")
        self.assertEqual(c["reviewed_resources"], 9)
        self.assertEqual(c["selected_resources"], 0)
        self.assertFalse(c["live_execution_released"])
        self.assertFalse(any(r["would_execute"] for r in c["simulated_operations"]))
        self.assertFalse(c["docker_mutation_performed"])
        self.assertFalse(c["hf_mutation_performed"])

    def test_single_collection_with_pure_stages(self):
        calls = []
        def inspect():
            calls.append("read_only")
            return fake_inventory()
        doc = bc.inspect_both(inventory_fn=inspect)
        self.assertEqual(calls, ["read_only"])
        self.assertEqual(doc["status"], "READ_ONLY_DRY_RUN_PASS")
        self.assertFalse(doc["executed"])

    def test_partial_inventory_fails_closed(self):
        inv = fake_inventory()
        inv["issues"] = ["DOCKER_CAPACITY_CATEGORIES_INCOMPLETE"]
        inv["status"] = "READ_ONLY_INVENTORY_PARTIAL"
        doc = bc.inspect_both(inventory_fn=lambda: inv)
        self.assertEqual(doc["status"], "READ_ONLY_DRY_RUN_BLOCKED")
        self.assertEqual(doc["candidate_review"]["status"], "REVIEW_BLOCKED")
        self.assertEqual(doc["cleanup_rehearsal"]["status"], "DRY_RUN_BLOCKED_INCOMPLETE_EVIDENCE")

    def test_second_running_model_blocks(self):
        inv = fake_inventory()
        inv["managed_containers"][1]["container_running"] = True
        self.assertIn("UNEXPECTED_NONACTIVE_RUNNING_MODEL",
                      bc.review_candidates(inv)["issues"])

    def test_untrusted_cache_size_is_redacted_and_blocked(self):
        inv = fake_inventory()
        inv["cache_storage"][0]["known_model_repo_allocated_bytes"]["27b"] = "/private/secret"
        b = bc.review_candidates(inv)
        self.assertIn("CACHE_MODEL_ALLOCATION_UNAVAILABLE", b["issues"])
        self.assertNotIn("/private/secret", json.dumps(b))
        inv["cache_storage"][0]["known_model_repo_allocated_bytes"]["27b"] = -3
        self.assertIn("CACHE_MODEL_ALLOCATION_UNAVAILABLE", bc.review_candidates(inv)["issues"])

    def test_duplicate_root_or_docker_category_rejected(self):
        inv = fake_inventory()
        inv["cache_storage"][1]["root_index"] = 1
        self.assertIn("CACHE_ROOT_IDENTITY_INCOMPLETE", bc.review_candidates(inv)["issues"])
        inv = fake_inventory()
        inv["docker_disk_usage"]["rows"].append(dict(inv["docker_disk_usage"]["rows"][0]))
        self.assertIn("DUPLICATE_DOCKER_CATEGORY", bc.review_candidates(inv)["issues"])

    def test_untrusted_docker_display_not_reflected(self):
        inv = fake_inventory()
        inv["docker_disk_usage"]["rows"][0]["docker_reported_size"] = "TOKEN_SECRET"
        b = bc.review_candidates(inv)
        self.assertIn("UNTRUSTED_DOCKER_ESTIMATE", b["issues"])
        self.assertNotIn("TOKEN_SECRET", json.dumps(b))

    def test_direct_execute_rejected_before_inspection(self):
        with patch.object(bc, "inspect_both") as probe, \
             contextlib.redirect_stdout(io.StringIO()) as out:
            rc = bc.main(["--execute", "--approve-plan", "a" * 64, "--json"])
        self.assertEqual(rc, 3)
        self.assertIn("P4_C_LIVE_EXECUTION_NOT_RELEASED", json.loads(out.getvalue())["issues"])
        probe.assert_not_called()

    def test_wizard_combined_dry_run_one_probe(self):
        with patch("scripts.manager.p4_bc_dry_run.inspect_p4_a", return_value=fake_inventory()) as probe:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = wizard.main(["storage", "flash-next", "dry-run", "--json"])
            self.assertEqual(rc, 0, out.getvalue())
            self.assertEqual(json.loads(out.getvalue())["status"], "READ_ONLY_DRY_RUN_PASS")
            probe.assert_called_once()

    def test_explicit_candidates_and_retire_dryrun(self):
        with patch("scripts.manager.p4_bc_dry_run.inspect_p4_a", return_value=fake_inventory()):
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = wizard.main(["p4", "candidates", "--dry-run", "--json"])
            self.assertEqual(rc, 0, out.getvalue())
            self.assertEqual(json.loads(out.getvalue())["stage"], "P4-B")
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = wizard.main(["p4", "retire", "--dry-run", "--json"])
            self.assertEqual(rc, 0, out.getvalue())
            self.assertEqual(json.loads(out.getvalue())["stage"], "P4-C")

    def test_legacy_plain_actions_still_block_without_host_probe(self):
        with patch("scripts.manager.p4_bc_dry_run.inspect_p4_a") as probe:
            for action in ("candidates", "retire"):
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    rc = wizard.main(["p4", action, "--json"])
                self.assertEqual(rc, 3)
                self.assertEqual(json.loads(out.getvalue())["status"], "BLOCKED")
            probe.assert_not_called()

    def test_execute_and_fake_approval_denied_without_host_probe(self):
        with patch("scripts.manager.p4_bc_dry_run.inspect_p4_a") as probe:
            with contextlib.redirect_stdout(io.StringIO()) as out:
                rc = wizard.main(["p4", "retire", "--execute", "--approve-plan",
                                  "a" * 64, "--json"])
            self.assertEqual(rc, 3)
            self.assertFalse(json.loads(out.getvalue())["executed"])
            probe.assert_not_called()


if __name__ == "__main__":
    unittest.main()
