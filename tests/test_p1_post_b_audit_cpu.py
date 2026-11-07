"""CPU-only POST-B P1 audit / rc3 evidence and immutable file regressions."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import tempfile
import unittest

from scripts.temporary import p1_post_b_audit as audit

IMAGE = "sha256:" + "f" * 64
B_CID = "b" * 64
REV = "c" * 40
DONE = "2026-11-06T22:31:24+00:00"


def b_receipt():
    return {"schema_version": 1, "stage": "b", "status": "PASS",
            "executed": True, "live_verified": True, "source_model": "27b",
            "target_model": "flash-next", "flash_image": IMAGE,
            "target_image": IMAGE, "target_id": B_CID,
            "finished_at_utc": DONE}


def live():
    return {"status": "LIVE_SERVICE_VERIFIED", "issues": [],
            "observed_model": "flash-next", "expected_served_id": "qwen3.8-flash-next",
            "observed_model_ids": ["qwen3.8-flash-next"], "host_port": 8000,
            "active_container": {"name": "qwen38-flash", "image_id": IMAGE}}


def collision():
    return {"status": "PASS", "errors": [], "scope": "SOURCE", "dry_run": True,
            "name_conflict": True, "port_conflict": True, "collision_free": False,
            "proposed": {"container_name": "qwen38-flash", "port": 8000,
                         "served_model_name": "qwen3.8-flash-next"},
            "containers": [{"name": "qwen38-flash", "image_id": IMAGE,
                            "status": "Up About an hour",
                            "ports": "0.0.0.0:8000->8000/tcp"}]}


def inspection():
    check = lambda: {"returncode": 3, "truncated": False,
                     "stdout": json.dumps(collision())}
    diag = {"type": "P1_READ_ONLY_CACHE_DIAGNOSIS",
            "wizard_audit": {"state": "READY", "source_complete": True,
                             "hybrid_ready": True, "source_issues": [], "hybrid_issues": [],
                             "model_repo": "nvidia/Qwen3.8-Flash-Next-NVFP4",
                             "revision": REV}}
    return {
        "scope": "DGX_INSPECTION_AND_EXPLICITLY_APPROVED_API",
        "preflight": {"branch_ok": True, "tracked_tree_clean": True,
                      "runtime_allowed": True, "expected_api_model_present": True,
                      "operator_process": {"blocked": False}},
        "checks": {
            "doctor": check(), "inventory_plan": check(),
            "cache_diagnosis": {"returncode": 0, "truncated": False,
                                "stdout": json.dumps(diag)},
            "models": {"returncode": 0, "truncated": False,
                       "stdout": json.dumps({"data": [{"id": "qwen3.8-flash-next"}]})}},
        "plans": {k: {"ready": True, "plan": {"issues": []}}
                  for k in ("verify", "benchmark")},
        "actions": {k: {"status": "BLOCKED", "reason": "inspection_only",
                        "executed": False} for k in ("verify", "benchmark")},
    }


class P1PostBAuditCPU(unittest.TestCase):
    def assess(self, b=None, l=None, i=None):
        return audit.assess(b if b is not None else b_receipt(), 0,
                            l if l is not None else live(),
                            i if i is not None else inspection(),
                            stage_b_sha256="a" * 64,
                            now=datetime(2026, 11, 7, 1, 0, tzinfo=timezone.utc))

    def test_real_shaped_inspect_only_rc3_is_diagnostic_pass_not_gpu_pass(self):
        result = self.assess()
        self.assertEqual(result["status"], "PASS", result["issues"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["post_b_verify"], "NOT_RUN")
        self.assertEqual(result["post_b_benchmark"], "NOT_RUN")
        self.assertFalse(result["p3_c_authorized"])
        self.assertEqual(result["doctor_exit_code"], 3)
        self.assertEqual(result["inventory_plan_exit_code"], 3)

    def test_foreign_container_or_image_is_not_a_benign_rc3(self):
        i = inspection()
        d = collision()
        d["containers"][0]["image_id"] = "sha256:" + "0" * 64
        i["checks"]["doctor"]["stdout"] = json.dumps(d)
        self.assertIn("POST_B_DOCTOR_INVENTORY_RC3_CAUSE_UNVERIFIED",
                      self.assess(i=i)["issues"])

    def test_wrong_api_id_or_image_blocks(self):
        l = live()
        l["observed_model_ids"] = ["qwen3.8-27b"]
        self.assertIn("POST_B_FLASH_LIVE_IDENTITY_NOT_VERIFIED",
                      self.assess(l=l)["issues"])
        b = b_receipt()
        b["flash_image"] = "sha256:" + "0" * 64
        self.assertEqual(self.assess(b=b)["status"], "BLOCKED")

    def test_not_executed_b_or_future_b_receipt_blocks(self):
        b = b_receipt()
        b["executed"] = False
        self.assertIn("P3_B_ACTUAL_SUCCESS_RECEIPT_NOT_QUALIFIED",
                      self.assess(b=b)["issues"])
        b = b_receipt()
        b["finished_at_utc"] = "2027-01-01T00:00:00Z"
        self.assertIn("P3_B_TIMESTAMP_INVALID", self.assess(b=b)["issues"])

    def test_verify_benchmark_are_inspect_only_and_plans_must_be_ready(self):
        i = inspection()
        i["actions"]["verify"]["executed"] = True
        i["plans"]["benchmark"]["ready"] = False
        self.assertEqual(self.assess(i=i)["status"], "BLOCKED")

    def test_missing_revision_or_corrupt_raw_doctor_fails_closed(self):
        i = inspection()
        i["checks"]["cache_diagnosis"]["stdout"] = "{}"
        i["checks"]["doctor"]["stdout"] = "not-json"
        codes = self.assess(i=i)["issues"]
        self.assertIn("P1_POST_B_PINNED_ASSET_AUDIT_NOT_READY", codes)
        self.assertIn("POST_B_DOCTOR_INVENTORY_RC3_CAUSE_UNVERIFIED", codes)

    def test_private_diagnostic_is_unique_0600_and_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "p3"
            first = audit.save_immutable({"status": "PASS"}, root=root)
            second = audit.save_immutable({"status": "BLOCKED"}, root=root)
            self.assertNotEqual(first, second)
            self.assertEqual(json.loads(first.read_text())["status"], "PASS")
            self.assertEqual(first.stat().st_mode & 0o777, 0o600)
            self.assertTrue(first.name.startswith("p1-diagnostics-"))
            self.assertEqual(json.loads(second.read_text())["status"], "BLOCKED")

    def test_symlinked_private_root_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            target = base / "target"
            target.mkdir()
            (base / "link").symlink_to(target, target_is_directory=True)
            with self.assertRaises(ValueError):
                audit.save_immutable({"status": "PASS"}, root=base / "link")


if __name__ == "__main__":
    unittest.main()
