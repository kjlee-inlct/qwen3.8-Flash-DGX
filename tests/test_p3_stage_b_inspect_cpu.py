"""D-016 fake-DGX tests for read-only, post-A P3-B preflight."""
from __future__ import annotations

from datetime import datetime, timezone
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.temporary import p3_stage_b_inspect as audit

IMG = "sha256:" + "9" * 64
A_PLAN = "a" * 64
FLASH_CID = "b" * 64
MODEL_CID = "c" * 64
P2_SHA = "d" * 64
B_PLAN = "e" * 64


def stage_a():
    return {
        "schema_version": 1, "stage": "a",
        "status": "PASS", "executed": True, "live_verified": True,
        "plan_id": A_PLAN, "source_model": "flash-next", "target_model": "27b",
        "source_id": FLASH_CID, "target_id": MODEL_CID,
        "flash_id": FLASH_CID, "id_27b": MODEL_CID,
        "source_image": IMG, "target_image": IMG,
        "flash_image": IMG, "image_27b": IMG,
        "p2_receipt_sha256": P2_SHA,
        "finished_at_utc": "2026-11-06T07:43:06+00:00",
    }


def status():
    return {
        "status": "LIVE_SERVICE_VERIFIED", "observed_model": "27b",
        "expected_served_id": "qwen3.8-27b", "observed_model_ids": ["qwen3.8-27b"],
        "host_port": 8000, "issues": [],
        "active_container": {"name": "qwen38-27b", "image_id": IMG},
    }


def plan():
    return {
        "schema_version": 1, "stage": "b",
        "status": "READY_TO_REQUEST_TRANSITION_APPROVAL", "issues": [],
        "source_model": "27b", "target_model": "flash-next",
        "executed": False, "operations_enabled": False,
        "approval_accepted": False, "plan_id": B_PLAN,
        "source_container_id": MODEL_CID,
        "target_container_id": FLASH_CID,
        "source_image": IMG, "target_image": IMG,
        "flash_id": FLASH_CID, "image_27b": IMG,
        "p3_a_plan_id": A_PLAN,
        "p2_receipt_sha256": P2_SHA,
        "required_downtime_acknowledgement": "I_ACCEPT_27B_DOWNTIME",
        "required_p3_entry_acknowledgement": "I_SEPARATELY_AUTHORIZE_P3_STAGE_B",
        "expires_at_epoch_seconds": 1900000200,
    }


class P3BReadOnlyCPU(unittest.TestCase):
    def test_verified_A_and_live_B_planning_is_read_only_ready(self):
        self.assertEqual(audit.receipt_issues(stage_a()), [])
        self.assertEqual(
            audit.preflight_issues(stage_a(), status(), plan(), now_epoch=1900000000), [])

    def test_no_success_receipt_blocks(self):
        doc = stage_a()
        doc["executed"] = False
        self.assertIn("P3_A_SUCCESS_RECEIPT_NOT_QUALIFIED",
                      audit.preflight_issues(doc, status(), plan(), now_epoch=1900000000))

    def test_stage_a_identity_provenance_mismatch_blocks(self):
        doc = stage_a()
        doc["id_27b"] = "f" * 64
        self.assertIn("P3_A_RECEIPT_INTERNAL_IDENTITY_DRIFT",
                      audit.preflight_issues(doc, status(), plan(), now_epoch=1900000000))

    def test_foreign_live_api_id_blocks(self):
        live = status()
        live["observed_model_ids"] = ["qwen3.8-flash-next"]
        self.assertIn("P3_B_SOURCE_27B_LIVE_MANIFEST_API_UNVERIFIED",
                      audit.preflight_issues(stage_a(), live, plan(), now_epoch=1900000000))

    def test_foreign_p3_a_receipt_plan_blocks(self):
        p = plan()
        p["p3_a_plan_id"] = "f" * 64
        self.assertIn("P3_B_PRESERVED_CONTAINERS_OR_PROVENANCE_DRIFT",
                      audit.preflight_issues(stage_a(), status(), p, now_epoch=1900000000))

    def test_preserved_flash_docker_id_mismatch_blocks(self):
        p = plan()
        p["target_container_id"] = "f" * 64
        self.assertIn("P3_B_PRESERVED_CONTAINERS_OR_PROVENANCE_DRIFT",
                      audit.preflight_issues(stage_a(), status(), p, now_epoch=1900000000))

    def test_expired_stage_b_plan_blocks(self):
        self.assertIn("P3_B_PLAN_ALREADY_EXPIRED",
                      audit.preflight_issues(stage_a(), status(), plan(), now_epoch=1900000300))

    def test_explicit_manual_B_ack_cannot_be_reused_from_A_entry(self):
        p = plan()
        p["required_p3_entry_acknowledgement"] = "I_SEPARATELY_AUTHORIZE_P3_ENTRY"
        self.assertIn("P3_B_APPROVAL_CONTRACT_CHANGED",
                      audit.preflight_issues(stage_a(), status(), p, now_epoch=1900000000))

    def test_stage_A_flash_downtime_ack_cannot_authorize_B_27B_shutdown(self):
        p = plan()
        p["required_downtime_acknowledgement"] = "I_ACCEPT_FLASH_NEXT_DOWNTIME"
        self.assertIn("P3_B_APPROVAL_CONTRACT_CHANGED",
                      audit.preflight_issues(stage_a(), status(), p, now_epoch=1900000000))

    def test_missing_B_source_model_status_blocks(self):
        p = plan()
        p["status"] = "BLOCKED"
        p["issues"] = ["PRESERVED_TARGET_MISSING"]
        self.assertIn("P3_B_FRESH_PLAN_NOT_READY",
                      audit.preflight_issues(stage_a(), status(), p, now_epoch=1900000000))

    def test_main_only_uses_readonly_wizard_and_private_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls = []
            receipt = Path(tmp) / "stage-a.json"
            receipt.write_text(json.dumps(stage_a()))
            receipt.chmod(0o600)
            outdir = Path(tmp) / "private"
            def fake_readonly(args, **kwargs):
                calls.append(args)
                if args[:3] == ["./wizard.sh", "service", "manager"]:
                    return 0, status()
                if args[:3] == ["./wizard.sh", "switch", "flash-next-27b"]:
                    doc = plan()
                    doc["expires_at_epoch_seconds"] = int(datetime.now(timezone.utc).timestamp()) + 300
                    return 0, doc
                raise AssertionError(args)
            with patch.object(audit, "STATE", Path(tmp)), \
                 patch.object(audit, "git_clean", return_value=True), \
                 patch.object(audit, "run_readonly", side_effect=fake_readonly), \
                 patch.object(audit, "REPORTS", outdir), \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                rc = audit.main(["--stage-a-receipt", str(receipt)])
            self.assertEqual(rc, 0)
            result = json.loads(output.getvalue())
            self.assertEqual(result["status"], "READY_FOR_SEPARATE_P3_B_APPROVAL")
            self.assertFalse(result["executed"])
            self.assertFalse(result["operations_enabled"])
            self.assertFalse(result["approval_accepted"])
            self.assertEqual(len(calls), 2)
            self.assertTrue(all("--plan" in x or "status" in x for x in calls))
            self.assertFalse(any("--execute" in x for x in calls))
            saved = Path(result["evidence_file"])
            self.assertTrue(saved.is_file())
            self.assertEqual(saved.stat().st_mode & 0o777, 0o600)

    def test_explicit_execute_argument_not_supported(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                audit.main(["--execute"])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
