"""CPU-only sanitized benchmark publication tests. No GPU, Docker, Git write or network."""
from __future__ import annotations

import contextlib
import io
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import benchmark_publication as pub


def p1_record():
    return {
        "action": "benchmark", "status": "PASS", "executed": True,
        "model_repo": "nvidia/Qwen3.8-Flash-Next-NVFP4",
        "served_model": "qwen3.8-flash-next",
        "model_revision": "f" * 40,
        "parameters": {"requests": 3, "max_tokens": 64, "seed": 1234},
        "plan_id": "TOP_SECRET_APPROVAL",
        "api_base": "http://private-host:8000/v1",
        "result": {
            "benchmark": {
                "status": "PASS", "requests": 3, "max_tokens": 64,
                "seed": 1234, "concurrency": 1,
                "samples": [{"index": i, "completion_text": "PRIVATE_CONTENT"}
                            for i in range(3)],
                "metrics": {
                    "ttft_p50_sec": 1.384594,
                    "ttft_p95_sec": 1.779602,
                    "latency_p50_sec": 1.72456,
                    "latency_p95_sec": 1.813754,
                    "mean_tokens_per_sec": 37.9527,
                    "total_completion_tokens": 192,
                    "private_gpu_address": "SECRET",
                },
            }
        },
    }


def p2_record():
    return {
        "status": "BENCH_PASS_RESTORED_VERIFIED", "executed": True,
        "plan_id": "DO_NOT_COMMIT_THIS",
        "post_restore_wizard_status": {
            "status": "LIVE_SERVICE_VERIFIED", "observed_model": "flash-next",
            "expected_served_id": "qwen3.8-flash-next", "issues": [],
            "private_ip": "10.11.12.13"},
        "benchmark": {
            "status": "PASS", "model": "qwen3.8-27b",
            "requests": 3, "max_tokens": 64,
            "seed": 1234, "concurrency": 1,
            "samples": [{"success": True, "response_text": "SECRET"}
                        for _ in range(3)],
            "metrics": {
                "ttft_p50_sec": 0.179349,
                "ttft_p95_sec": 28.97799,
                "latency_p50_sec": 5.818283,
                "latency_p95_sec": 34.609889,
                "mean_e2e_tokens_per_sec": 7.9002,
                "mean_decode_tokens_per_sec_proxy": 11.1801,
                "mean_prompt_ingest_tokens_per_sec_proxy": 999.0,
            },
        },
    }


class BenchmarkPublicationCPU(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "repo"
        self.root.mkdir()
        self.legacy = Path(temp.name) / "legacy"
        self.reports = self.root / "reports"
        self.policy = self.root / "policy.json"
        self.discovery = self.root / "discovery.json"
        self.policy.write_text(json.dumps({
            "engine": "vllm-0.32",
            "models": {
                "flash-next": {"served_id": "qwen3.8-flash-next",
                               "checkpoint": "nvidia/Qwen3.8-Flash-Next-NVFP4"},
                "27b": {"served_id": "qwen3.8-27b",
                        "checkpoint": "nvidia/Qwen3.8-27B-NVFP4"},
            }
        }))
        self.discovery.write_text(json.dumps({
            "models": {"27b": {"pinned_revision": "4" * 40,
                               "repo_id": "nvidia/Qwen3.8-27B-NVFP4"}}
        }))
        self.p1 = self._file(self.legacy / "p1" /
                             "20261106T233031Z-private.json", p1_record())
        self.p2 = self._file(self.legacy / "p2" /
                             "20261106T042642Z-private.benchmark.json", p2_record())

    @staticmethod
    def _file(path, doc):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(doc))
        path.chmod(0o600)
        return path

    def get(self, model, source=None):
        with patch.object(pub, "ROOT", self.root):
            return pub.build_summary(
                model=model, source=source or (
                    self.p1 if model == "flash-next" else self.p2),
                legacy=self.legacy, reports=self.reports, policy=self.policy,
                discovery=self.discovery)

    def test_p1_exact_metrics_revision_and_identity_provenance(self):
        report, dest = self.get("flash-next")
        self.assertEqual(report["model_id"], "qwen3.8-flash-next")
        self.assertEqual(report["metrics"]["mean_tokens_per_sec"], 37.9527)
        self.assertEqual(report["metrics"]["total_completion_tokens"], 192)
        self.assertEqual(report["model_revision"], "f" * 40)
        self.assertEqual(report["profile"], {
            "requests": 3, "max_tokens": 64, "seed": 1234, "concurrency": 1})
        self.assertEqual(report["measurement_time_utc"], "2026-11-06T23:30:31Z")
        self.assertEqual(report["source_evidence_sha256"],
                         hashlib.sha256(self.p1.read_bytes()).hexdigest())
        self.assertTrue(dest.name.endswith(".json"))

    def test_p2_exact_e2e_vs_decode_metrics_and_restoration(self):
        report, dest = self.get("27b")
        self.assertEqual(report["model_id"], "qwen3.8-27b")
        self.assertEqual(report["metrics"]["mean_e2e_tokens_per_sec"], 7.9002)
        self.assertEqual(report["metrics"]["mean_decode_tokens_per_sec_proxy"], 11.1801)
        self.assertNotIn("mean_tokens_per_sec", report["metrics"])
        self.assertEqual(report["execution_status"], "BENCH_PASS_RESTORED_VERIFIED")
        self.assertEqual(report["model_revision"], "4" * 40)

    def test_private_fields_and_run_contents_never_leak_into_summary(self):
        for model in ("flash-next", "27b"):
            with self.subTest(model=model):
                doc, _ = self.get(model)
                public = json.dumps(doc).lower()
                for secret in ("top_secret_approval", "do_not_commit_this",
                               "10.11.12.13", "private-host", "private_content",
                               "response_text", "private_gpu_address",
                               "private_ip", "completion_text", "samples",
                               "plan_id", "/home/"):
                    self.assertNotIn(secret, public)

    def test_plan_is_read_only_without_new_file(self):
        with patch.object(pub, "ROOT", self.root), \
             patch.object(pub, "LEGACY", self.legacy), \
             patch.object(pub, "REPORTS", self.reports), \
             patch.object(pub, "POLICY", self.policy), \
             patch.object(pub, "DISCOVERY", self.discovery), \
             contextlib.redirect_stdout(io.StringIO()) as stream:
            rc = pub.main(["--model", "27b", "--source", str(self.p2), "--plan"])
        self.assertEqual(rc, 0)
        doc = json.loads(stream.getvalue())
        self.assertEqual(doc["status"], "READY_FOR_PUBLICATION_REVIEW")
        self.assertFalse(doc["executed"])
        self.assertFalse((self.root / "benchmarks").exists())

    def test_explicit_publication_source_sha_required_and_no_overwrite(self):
        report, dest = self.get("flash-next")
        public = self.root / "benchmarks" / "published"
        blocked = pub.publish(report, dest, expected_sha=None, public=public)
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertFalse(dest.exists())
        blocked = pub.publish(report, dest, expected_sha="0" * 64, public=public)
        self.assertEqual(blocked["status"], "BLOCKED")
        result = pub.publish(report, dest, expected_sha=report["source_evidence_sha256"],
                             public=public)
        self.assertEqual(result["status"], "PUBLIC_SUMMARY_WRITTEN")
        self.assertEqual(json.loads(dest.read_text()), report)
        repeat = pub.publish(report, dest,
                             expected_sha=report["source_evidence_sha256"], public=public)
        self.assertEqual(repeat["status"], "ALREADY_PUBLISHED")
        self.assertFalse(repeat["executed"])
        dest.write_text('{"tampered":true}')
        denied = pub.publish(report, dest,
                             expected_sha=report["source_evidence_sha256"], public=public)
        self.assertEqual(denied["status"], "BLOCKED")
        self.assertEqual(denied["issues"], ["PUBLISHED_CONTENT_MISMATCH"])
        self.assertIn("tampered", dest.read_text())

    def test_verify_published_flags_reproducible_summary_mismatch(self):
        report, dest = self.get("27b")
        with patch.object(pub, "ROOT", self.root), \
             patch.object(pub, "LEGACY", self.legacy), \
             patch.object(pub, "REPORTS", self.reports), \
             patch.object(pub, "POLICY", self.policy), \
             patch.object(pub, "DISCOVERY", self.discovery), \
             contextlib.redirect_stdout(io.StringIO()) as stream:
            rc = pub.main(["--model", "27b", "--source", str(self.p2),
                           "--verify-published"])
        self.assertEqual(rc, 3)
        self.assertIn("PUBLIC_SUMMARY_MISMATCH", stream.getvalue())
        pub.publish(report, dest, expected_sha=report["source_evidence_sha256"],
                    public=self.root / "benchmarks" / "published")
        with patch.object(pub, "ROOT", self.root), \
             patch.object(pub, "LEGACY", self.legacy), \
             patch.object(pub, "REPORTS", self.reports), \
             patch.object(pub, "POLICY", self.policy), \
             patch.object(pub, "DISCOVERY", self.discovery), \
             contextlib.redirect_stdout(io.StringIO()) as stream:
            rc = pub.main(["--model", "27b", "--source", str(self.p2),
                           "--verify-published"])
        self.assertEqual(rc, 0)
        self.assertIn('"status": "VERIFIED"', stream.getvalue())

    def test_partial_fail_wrong_model_wrong_revision_wrong_status_rejected(self):
        for model, which in (("flash-next", "p1"), ("27b", "p2")):
            with self.subTest(model=model):
                path = self.p1 if which == "p1" else self.p2
                doc = json.loads(path.read_text())
                if which == "p1":
                    doc["status"] = "FAIL"
                else:
                    doc["post_restore_wizard_status"]["status"] = "UNKNOWN"
                self._file(path, doc)
                with self.assertRaises(ValueError):
                    self.get(model)
                self._file(path, p1_record() if which == "p1" else p2_record())

    def test_malformed_metrics_profile_or_samples_fail_closed(self):
        original = p1_record()
        for mismatch in ("NaN", "false", "samples", "profile"):
            with self.subTest(mismatch=mismatch):
                doc = json.loads(json.dumps(original))
                if mismatch == "NaN":
                    doc["result"]["benchmark"]["metrics"]["ttft_p50_sec"] = float("nan")
                elif mismatch == "false":
                    doc["result"]["benchmark"]["metrics"]["mean_tokens_per_sec"] = False
                elif mismatch == "samples":
                    doc["result"]["benchmark"]["samples"] = []
                else:
                    doc["parameters"]["requests"] = 4
                self._file(self.p1, doc)
                with self.assertRaises(ValueError):
                    self.get("flash-next")
        self._file(self.p1, original)

    def test_arbitrary_file_and_symlink_or_world_readable_source_rejected(self):
        outside = self._file(Path(self.root.parent) / "private.json", p1_record())
        with self.assertRaises(ValueError):
            self.get("flash-next", source=outside)
        self.p1.chmod(0o644)
        with self.assertRaises(ValueError):
            self.get("flash-next")
        self.p1.chmod(0o600)
        link = self.legacy / "p1" / "20261106T233031Z-link.json"
        link.symlink_to(self.p1)
        with self.assertRaises(ValueError):
            self.get("flash-next", source=link)

    def test_project_report_source_with_import_prefix_supported(self):
        dest = self.reports / "models" / "qwen3.8-flash-next" / (
            "import-" + "0" * 16 + "-20261106T233031Z-private.json")
        self._file(dest, p1_record())
        report, path = self.get("flash-next", source=dest)
        self.assertEqual(report["model_id"], "qwen3.8-flash-next")
        self.assertEqual(report["measurement_time_utc"], "2026-11-06T23:30:31Z")

    def test_publication_does_not_run_model_or_git_commands(self):
        report, dest = self.get("flash-next")
        with patch("subprocess.run", side_effect=AssertionError("side effect")), \
             patch("os.system", side_effect=AssertionError("side effect")):
            result = pub.publish(report, dest,
                                 expected_sha=report["source_evidence_sha256"],
                                 public=self.root / "benchmarks" / "published")
        self.assertEqual(result["status"], "PUBLIC_SUMMARY_WRITTEN")


if __name__ == "__main__":
    unittest.main()
