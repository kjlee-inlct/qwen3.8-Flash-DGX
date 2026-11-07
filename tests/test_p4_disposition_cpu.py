"""P4 optional preservation/disposition policy: no Docker/GPU mutations."""
from __future__ import annotations

import unittest

from scripts.manager import p4_disposition as p4

ID = "a" * 64


def policy():
    return {
        "models": {
            "27b": {"container_name": "qwen38-27b", "served_id": "qwen3.8-27b"},
            "flash-next": {"container_name": "qwen38-flash",
                           "served_id": "qwen3.8-flash-next"},
        },
        "retired_containers": {"completion": {
            "state": "OPERATOR_DGX_CLEANUP_COMPLETED_VERIFIED"}},
    }


def snapshot():
    return {
        "running": ["qwen38-27b"],
        "gpu_running": ["qwen38-27b"],
        "port_owners": ["qwen38-27b"],
        "containers": {
            "qwen38-27b": {"Id": "b" * 64},
            "qwen38-flash": {
                "Id": ID, "Image": "sha256:" + "c"*64,
                "State": {"Running": False},
                "Config": {"Env": ["ACCESS_TOKEN=private-value"]},
                "Mounts": [{"Source": "/private/operator/hf", "Destination": "/hf"}],
            },
        },
    }


def live():
    return {"status": "LIVE_SERVICE_VERIFIED", "observed_model": "27b",
            "expected_served_id": "qwen3.8-27b", "issues": []}


class P4DispositionCPU(unittest.TestCase):
    def inspect(self, snapshot_fn=snapshot, live_fn=live):
        return p4.inspect_p4(snapshot_fn=snapshot_fn, live_fn=live_fn,
                             policy_fn=policy)

    def test_preserve_stopped_flash_for_p8_without_writing_anything(self):
        doc = snapshot()
        before = repr(doc)
        out = self.inspect(snapshot_fn=lambda: doc)
        self.assertEqual(out["status"], "READ_ONLY_FLASH_RETAIN_RECOMMENDED")
        self.assertEqual(out["recommended_disposition"], "RETAIN_ALL_PENDING_P8")
        self.assertEqual(out["active_model"], "27b")
        self.assertTrue(out["flash_container_present"])
        self.assertFalse(out["flash_container_running"])
        self.assertTrue(out["historical_retired_cleanup_completed"])
        self.assertFalse(out["executed"])
        self.assertFalse(out["operations_enabled"])
        self.assertFalse(out["removed_containers"])
        self.assertFalse(out["removed_images"])
        self.assertFalse(out["removed_hf_cache"])
        self.assertIsNone(out["removal_plan_id"])
        self.assertEqual(before, repr(doc))
        self.assertNotIn("private-value", str(out))
        self.assertNotIn("/private/operator", str(out))

    def test_foreign_gpu_owner_blocks_unsafe_cleanup_assumptions(self):
        doc = snapshot()
        doc["gpu_running"].append("foreign")
        doc["running"].append("foreign")
        doc["containers"]["foreign"] = {"Id": "d" * 64}
        out = self.inspect(snapshot_fn=lambda: doc)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("UNMANAGED_GPU_CONTAINER_RUNNING", out["issues"])
        self.assertEqual(out["recommended_disposition"], "RETAIN_ALL_PENDING_P8")

    def test_mismatched_api_identity_blocks(self):
        bad = dict(live(), expected_served_id="wrong-model")
        out = self.inspect(live_fn=lambda: bad)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertIn("ACTIVE_API_IDENTITY_UNVERIFIED", out["issues"])

    def test_missing_flash_does_not_infer_image_or_cache_deletion(self):
        doc = snapshot()
        del doc["containers"]["qwen38-flash"]
        out = self.inspect(snapshot_fn=lambda: doc)
        self.assertEqual(out["status"], "READ_ONLY_FLASH_ABSENT_NO_CLEANUP_REQUIRED")
        self.assertFalse(out["flash_container_present"])
        self.assertFalse(out["flash_image_observed"])
        self.assertFalse(out["removed_images"])
        self.assertFalse(out["removed_hf_cache"])

    def test_missing_docker_inspect_never_authorizes_removal(self):
        def raise_io():
            raise RuntimeError("hidden path or secret")
        out = self.inspect(snapshot_fn=raise_io)
        self.assertEqual(out["status"], "BLOCKED")
        self.assertEqual(out["issues"],
                         ["P4_READ_ONLY_OBSERVATION_UNAVAILABLE:RuntimeError"])
        self.assertFalse(out["approval_accepted"])
        self.assertFalse(out["production_released"])
        self.assertNotIn("hidden path", str(out))


if __name__ == "__main__":
    unittest.main()
