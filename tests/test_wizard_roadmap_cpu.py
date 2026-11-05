"""P1-P7 operator readiness summary is read-only and never claims GPU PASS."""
from __future__ import annotations

import contextlib
import io
import json
import unittest
from unittest.mock import patch

from wizard import main as router
from wizard import roadmap


def service(*, downloading=False, good=True):
    return {"status": "OBSERVED_UNQUALIFIED" if good else "BLOCKED",
            "observed_model": "flash-next" if good else None,
            "download_running": downloading, "issues": []}


class RoadmapCPU(unittest.TestCase):
    def test_seven_milestones_all_have_scope_not_runtime_pass(self):
        r = roadmap.readiness_report(
            service=service(), checkpoint={"source_files_present": False,
                                            "checkpoint_status": "NOT_READY",
                                            "issues": []})
        self.assertEqual(len(r["milestones"]), 7)
        self.assertEqual([v["stage"] for v in r["milestones"]],
                         ["P1", "P2", "P3", "P4", "P5", "P6", "P7"])
        self.assertTrue(all(not v["runtime_pass_claimed"] for v in r["milestones"]))
        self.assertFalse(r["release_ready"])
        self.assertFalse(r["executed"])
        self.assertEqual(r["api_host_port"], 8000)

    def test_download_in_progress_is_not_completion(self):
        data = roadmap.readiness_report(
            service=service(downloading=True),
            checkpoint={"source_files_present": False, "checkpoint_status": "NOT_READY",
                        "issues": []})
        p2 = data["milestones"][1]
        self.assertEqual(p2["state"], "DOWNLOAD_IN_PROGRESS")
        self.assertFalse(p2["runtime_pass_claimed"])

    def test_post_download_source_present_still_runtime_unqualified(self):
        data = roadmap.readiness_report(
            service=service(),
            checkpoint={"source_files_present": True,
                        "checkpoint_status": "SOURCE_FILES_PRESENT_PINNED_CANDIDATE",
                        "issues": []})
        self.assertEqual(data["milestones"][1]["state"],
                         "SOURCE_PRESENT_RUNTIME_UNQUALIFIED")
        self.assertFalse(data["release_ready"])

    def test_failed_inventory_blocks_not_assumes_model_absent(self):
        data = roadmap.readiness_report(
            service=service(good=False),
            checkpoint={"source_files_present": False,
                        "checkpoint_status": "UNKNOWN",
                        "issues": ["CACHE_READ_FAILED"]})
        self.assertEqual(data["milestones"][1]["state"], "OBSERVATION_BLOCKED")
        self.assertIn("CACHE_READ_FAILED", data["issues"])
        self.assertIsNone(data["observed_model"])

    def test_readiness_cli_does_not_mutate_resources(self):
        data = roadmap.readiness_report(
            service=service(downloading=True),
            checkpoint={"source_files_present": False, "checkpoint_status": "NOT_READY",
                        "issues": []})
        with patch("wizard.roadmap.readiness_report", return_value=data), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(router.main(["roadmap", "--json"]), 0)
        doc = json.loads(output.getvalue())
        self.assertEqual(doc["status"], "NOT_RELEASE_QUALIFIED")
        self.assertFalse(doc["operations_enabled"])

    def test_roadmap_rejects_any_execute_switch_or_extra_arguments(self):
        for args in (["roadmap", "--execute", "--json"],
                     ["readiness", "switch", "--json"]):
            with self.subTest(args=args), contextlib.redirect_stdout(io.StringIO()) as output:
                rc = router.main(args)
            self.assertEqual(rc, 2)
            self.assertFalse(json.loads(output.getvalue())["executed"])


if __name__ == "__main__":
    unittest.main()
