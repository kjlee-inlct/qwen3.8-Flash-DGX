"""Synthetic CPU-only port/NAT and PLE smaps parser tests, no host reads."""
import unittest

from scripts.manager.p5_readonly_attribution import review_ple_smaps, review_port_publication


class PortPublicationCPU(unittest.TestCase):
    def _inspect(self):
        return {"HostConfig": {"NetworkMode": "bridge", "PortBindings": {
                    "8000/tcp": [{"HostIp": "", "HostPort": "8000"}]}},
                "NetworkSettings": {"Ports": {
                    "8000/tcp": [{"HostIp": "0.0.0.0", "HostPort": "8000"}]}}}

    def test_bridge_nat_is_never_attested_as_host_owner(self):
        row = review_port_publication(self._inspect())
        self.assertEqual(row["status"], "DOCKER_DECLARATION_CONSISTENT_NOT_HOST_VERIFIED")
        self.assertTrue(row["nat_candidate_not_verified"])
        self.assertFalse(row["port_process_ownership_verified"])
        self.assertFalse(row["host_listener_verified"])

    def test_host_mismatch_missing_and_malformed_fail_closed(self):
        doc = self._inspect()
        doc["NetworkSettings"]["Ports"]["8000/tcp"][0]["HostPort"] = "8001"
        self.assertEqual(review_port_publication(doc)["status"], "NOT_OBSERVED")
        doc = self._inspect()
        doc["NetworkSettings"]["Ports"]["8000/tcp"][0]["HostIp"] = "127.0.0.1"
        self.assertEqual(review_port_publication(doc)["status"], "DOCKER_DECLARATION_MISMATCH")
        self.assertEqual(review_port_publication({})["status"], "NOT_OBSERVED")
        self.assertFalse(review_port_publication({})["nat_candidate_not_verified"])


class PleAttributionCPU(unittest.TestCase):
    path = "/hf/hub/snapshots/abc/ple.safetensors"
    raw = ("1000-2000 r--s 00000000 00:01 123 /hf/hub/snapshots/abc/ple.safetensors\n"
           "Size: 128 kB\nRss: 64 kB\nPss: 32 kB\n"
           "2000-3000 r--s 00001000 00:01 124 /hf/hub/snapshots/abc/ple.safetensors\n"
           "Size: 128 kB\nRss: 16 kB\nPss: 8 kB\n")

    def _review(self, **override):
        opts = dict(raw=self.raw, expected_paths=[self.path], pid=42,
                    container_id="a" * 64, observed_container_id="a" * 64,
                    docker_host_pids={42, 43})
        return review_ple_smaps(**(opts | override))

    def test_exact_mapped_rss_and_pss_not_unique_physical(self):
        out = self._review()
        self.assertEqual(out["mapped_rss_bytes"], 80 * 1024)
        self.assertEqual(out["mapped_pss_bytes"], 40 * 1024)
        self.assertEqual(out["matched_mapping_count"], 2)
        self.assertTrue(out["complete_expected_file_coverage"])
        self.assertIsNone(out["ple_unique_resident_bytes"])
        self.assertFalse(out["checkpoint_paths_authenticated"])
        self.assertFalse(out["pid_container_membership_authenticated"])

    def test_wrong_pid_docker_or_untrusted_paths_block(self):
        for opts in ({"pid": 44}, {"observed_container_id": "b" * 64},
                     {"expected_paths": ["/hf/../etc/passwd"]},
                     {"raw": self.raw[:-2]}):
            with self.subTest(opts=opts):
                out = self._review(**opts)
                self.assertEqual(out["status"], "BLOCKED_UNQUALIFIED")
                self.assertIsNone(out["mapped_rss_bytes"])

    def test_partial_mapping_and_missing_metrics(self):
        out = self._review(expected_paths=[self.path, "/hf/other.safetensors"])
        self.assertEqual(out["status"], "SOURCE_MAPPING_ATTRIBUTION_NOT_AUTHENTICATED")
        self.assertIn("EXPECTED_PLE_MAPPING_COVERAGE_PARTIAL", out["issues"])
        out = self._review(raw=self.raw.replace("Pss: 32 kB\n", ""))
        self.assertEqual(out["status"], "BLOCKED_UNQUALIFIED")
        self.assertIn("SMAPS_INCOMPLETE_OR_INCONSISTENT_MAPPING", out["issues"])

    def test_anonymous_mapping_does_not_inherit_previous_filename(self):
        raw = (self.raw + "3000-4000 rw-p 00000000 00:00 0\n"
               "Size: 4096 kB\nRss: 4096 kB\nPss: 4096 kB\n")
        out = self._review(raw=raw)
        self.assertEqual(out["mapped_rss_bytes"], 80 * 1024)
        self.assertEqual(out["mapped_pss_bytes"], 40 * 1024)

    def test_no_matching_file_not_observed(self):
        out = self._review(expected_paths=["/hf/another.safetensors"])
        self.assertEqual(out["status"], "NOT_OBSERVED")
        self.assertIsNone(out["mapped_rss_bytes"])


if __name__ == "__main__":
    unittest.main()
