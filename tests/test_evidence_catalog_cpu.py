"""CPU-only tests for model-keyed history and safe P2/P3 copy-only import."""
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.manager import evidence_catalog as cat
from wizard import console
from wizard import main as wizard_main


class EvidenceCatalogCPU(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(prefix="evidence-ux-")
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.legacy = self.base / "state"
        self.operator = self.base / "legacy-p3-operators"
        self.reports = self.base / "project" / "reports"
        self.policy = self.base / "service-policy.json"
        self.policy.write_text(json.dumps({"models": {
            "flash-next": {"served_id": "qwen3.8-flash-next"},
            "27b": {"served_id": "qwen3.8-27b"},
            "orcarouter": {"served_id": None},
        }}))
        self.p1_verify = self._put(
            self.legacy / "p1" / "20261106T232627Z-verify.json",
            {"action": "verify", "status": "PASS", "served_model": "qwen3.8-flash-next",
             "finished_at_utc": "2026-11-06T23:26:27+00:00",
             "result": {"status": "PASS", "baseline_status": "PASS",
                        "extended_status": "PASS", "probes": {
                            "chat": {"status": "PASS"}, "tools": {"status": "PASS"}}}})
        self.p1_bench = self._put(
            self.legacy / "p1" / "20261106T233031Z-bench.json",
            {"action": "benchmark", "status": "PASS",
             "finished_at_utc": "2026-11-06T23:30:31+00:00",
             "result": {"benchmark": {
                 "status": "PASS", "requests": 3, "concurrency": 1,
                 "max_tokens": 64,
                 "metrics": {"ttft_p50_sec": 1.384594,
                             "mean_tokens_per_sec": 37.9527}}}})
        self.p2_bench = self._put(
            self.legacy / "p2" / "20261106T042642Z-27b.benchmark.json",
            {"status": "BENCH_PASS_RESTORED_VERIFIED", "executed": True,
             "benchmark": {"status": "PASS", "model": "qwen3.8-27b",
                           "requests": 3, "concurrency": 1,
                           "metrics": {"mean_e2e_tokens_per_sec": 7.9002,
                                       "mean_decode_tokens_per_sec_proxy": 11.1801,
                                       "ttft_p50_sec": 0.179349}}})
        self.p2_trial = self._put(
            self.legacy / "p2" / "20261105T230229Z-trial.json",
            {"trial": "PASS", "model": "nvidia/Qwen3.8-27B-NVFP4",
             "finished_utc": "2026-11-05T23:02:29+00:00"})
        self.p2_download = self._put(
            self.legacy / "p2" / "evidence" / "20261105T150433Z-download.json",
            {"action": "download", "stage": "p2", "status": "PASS"})
        self.p3_b = self._put(
            self.legacy / "p3" / "stage-b.json",
            {"stage": "b", "status": "PASS", "live_verified": True,
             "source_model": "27b", "target_model": "flash-next",
             "finished_at_utc": "2026-11-06T22:31:24+00:00"})
        self.p3_diag = self._put(
            self.legacy / "p3" / "p1-diagnostics-20261106T232509Z.json",
            {"stage": "P1_POST_B_READ_ONLY_DIAGNOSTICS",
             "status": "PASS", "finished_at_utc": "2026-11-06T23:25:09+00:00"})
        self.p3_operator = self._put(
            self.operator / "p3-a-operator-20261106T223124Z.json",
            {"stage": "P3_B_OPERATOR_GUARDED_HANDOFF",
             "status": "P3_B_PASS_FLASH_NEXT_ACTIVE",
             "post_switch_observed_model": "flash-next"})
        # Locks and active journaling must NOT be treated as reports.
        self._put(self.legacy / "p3" / "journal" / "service-state.json",
                  {"status": "ACTIVE_LOCK_STATE"})
        (self.legacy / "p2" / "27b-gpu-trial.lock").write_text("lock")
        (self.legacy / "p3" / "p3-execution.lock").write_text("lock")

    def _put(self, path, value):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))
        path.chmod(0o600)
        return path

    def _kw(self):
        return dict(legacy=self.legacy, operator=self.operator,
                    reports=self.reports, policy=self.policy)

    def test_history_shows_real_metrics_without_running_any_service(self):
        before = list(self.legacy.rglob("*"))
        flash = cat.history(model="flash-next", **self._kw())
        self.assertEqual(flash["status"], "READ_ONLY_HISTORY")
        self.assertGreaterEqual(flash["count"], 3)
        bench = next(x for x in flash["records"] if x["category"] == "benchmark")
        self.assertEqual(bench["summary"]["mean_tokens_per_sec"], 37.9527)
        verify = next(x for x in flash["records"] if x["category"] == "verify")
        self.assertEqual(verify["summary"]["baseline_status"], "PASS")
        self.assertEqual(verify["summary"]["probes"]["tools"], "PASS")
        self.assertEqual(before, list(self.legacy.rglob("*")))
        self.assertFalse(self.reports.exists())

    def test_27b_e2e_and_decode_proxy_are_not_mislabeled_as_same_metric(self):
        doc = cat.history(model="27b", kind="benchmark", **self._kw())
        self.assertEqual(doc["count"], 1)
        m = doc["records"][0]["summary"]
        self.assertEqual(m["mean_e2e_tokens_per_sec"], 7.9002)
        self.assertEqual(m["mean_decode_tokens_per_sec_proxy"], 11.1801)
        self.assertNotIn("mean_tokens_per_sec", m)

    def test_transition_included_for_both_involved_models(self):
        for model in ("flash-next", "27b"):
            with self.subTest(model=model):
                doc = cat.history(model=model, kind="transition", **self._kw())
                self.assertTrue(any(x["action"] == "b" for x in doc["records"]),
                                doc)

    def test_copy_requires_exact_fresh_plan_and_is_idempotent(self):
        before_p2 = self.p2_bench.read_bytes()
        before_p3 = self.p3_b.read_bytes()
        blocked = cat.copy_approved(None, **self._kw())
        self.assertEqual(blocked["status"], "BLOCKED")
        self.assertFalse(self.reports.exists())
        plan = cat.migration_plan(**self._kw())
        self.assertEqual(plan["status"], "READY_TO_REQUEST_COPY_APPROVAL", plan["issues"])
        self.assertEqual(plan["copy_count"], 8)
        blocked = cat.copy_approved("f" * 64, **self._kw())
        self.assertEqual(blocked["status"], "BLOCKED")
        result = cat.copy_approved(plan["plan_id"], **self._kw())
        self.assertEqual(result["status"], "COPY_COMPLETE", result)
        self.assertEqual(result["copied"], 8)
        self.assertEqual(self.p2_bench.read_bytes(), before_p2)
        self.assertEqual(self.p3_b.read_bytes(), before_p3)
        self.assertEqual(self.p2_bench.stat().st_mode & 0o777, 0o600)
        self.assertTrue(any("/reports/models/qwen3.8-27b/" in x
                            for x in result["files"]))
        self.assertTrue(any("/reports/transitions/27b--to--flash-next/" in x
                            for x in result["files"]))
        self.assertTrue(all(Path(x).stat().st_mode & 0o777 == 0o600
                            for x in result["files"]))
        self.assertFalse(any("journal" in x or "lock" in x
                             for x in result["files"]))
        second = cat.migration_plan(**self._kw())
        self.assertEqual(second["copy_count"], 0)
        self.assertEqual(second["already_copied"], 8)
        result2 = cat.copy_approved(second["plan_id"], **self._kw())
        self.assertEqual(result2["status"], "COPY_COMPLETE")
        self.assertEqual(result2["copied"], 0)
        after = cat.history(model="flash-next", **self._kw())
        self.assertEqual(after["count"], cat.history(
            model="flash-next", reports=self.base / "empty", legacy=self.legacy,
            operator=self.operator, policy=self.policy)["count"])

    def test_mutated_source_invalidates_prior_plan_without_writes(self):
        plan = cat.migration_plan(**self._kw())
        self._put(self.p2_bench, {"status": "FAIL"})
        result = cat.copy_approved(plan["plan_id"], **self._kw())
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(self.reports.exists())

    def test_symlink_and_wrong_permissions_are_rejected_and_cannot_be_imported(self):
        self.p2_download.chmod(0o644)
        plan = cat.migration_plan(**self._kw())
        self.assertEqual(plan["status"], "BLOCKED")
        self.assertTrue(any("MIGRATION_SOURCE_INVALID:" in x for x in plan["issues"]))
        self.assertIsNone(plan["plan_id"])
        self.assertFalse(self.reports.exists())
        self.p2_download.chmod(0o600)
        other = self.base / "outside.json"
        self._put(other, {"status": "PASS"})
        link = self.legacy / "p2" / "fake.json"
        link.symlink_to(other)
        plan = cat.migration_plan(**self._kw())
        self.assertEqual(plan["status"], "BLOCKED")
        link.unlink()

    def test_guided_import_repeats_exact_sha_and_cancel_stays_read_only(self):
        plan = cat.migration_plan(**self._kw())
        with patch.object(cat, "migration_plan", return_value=plan), \
             patch.object(cat, "copy_approved", return_value={
                 "status": "COPY_COMPLETE", "executed": True,
                 "copied": 8}) as copier, \
             patch("builtins.input", return_value=plan["plan_id"]) as typed, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cat.main(["migrate", "--guided"]), 0)
        self.assertIn("Type exactly [" + plan["plan_id"] + "]",
                      typed.call_args.args[0])
        copier.assert_called_once_with(plan["plan_id"])
        with patch.object(cat, "migration_plan", return_value=plan), \
             patch.object(cat, "copy_approved") as copier, \
             patch("builtins.input", return_value=""), \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(cat.main(["migrate", "--guided"]), 0)
        copier.assert_not_called()
        self.assertFalse(self.reports.exists())

    def test_copy_preserves_original_timestamp_from_filename(self):
        before = cat.history(model="27b", kind="benchmark", **self._kw())
        original_time = before["records"][0]["timestamp_utc"]
        self.assertEqual(original_time, "2026-11-06T04:26:42+00:00")
        plan = cat.migration_plan(**self._kw())
        self.assertEqual(cat.copy_approved(plan["plan_id"], **self._kw())["status"],
                         "COPY_COMPLETE")
        after = cat.history(model="27b", kind="benchmark", **self._kw())
        self.assertEqual(after["records"][0]["timestamp_utc"], original_time)

    def test_historically_misnamed_p3_b_operator_classified_by_stage(self):
        doc = cat.history(model="flash-next", kind="transition", **self._kw())
        historical = [r for r in doc["records"] if "legacy-p3-operators" in r["path"]]
        self.assertEqual(len(historical), 1)
        self.assertEqual(historical[0]["summary"]["from_model"], "27b")
        self.assertEqual(historical[0]["summary"]["to_model"], "flash-next")

    def test_unknown_model_and_kind_are_blocked(self):
        self.assertEqual(cat.history(model="orcarouter", **self._kw())["count"], 0)
        self.assertEqual(cat.history(model="unknown", **self._kw())["status"], "BLOCKED")
        self.assertEqual(cat.history(kind="exploit", **self._kw())["status"], "BLOCKED")

    def test_wizard_cli_route_stays_read_only(self):
        with patch.object(cat, "main", return_value=0) as routed:
            self.assertEqual(wizard_main.main([
                "evidence", "list", "--model", "flash-next"]), 0)
        routed.assert_called_once_with(["list", "--model", "flash-next"])

    def test_integrated_console_history_is_read_only(self):
        with patch.object(cat, "history", return_value={
            "status": "READ_ONLY_HISTORY", "model": "qwen3.8-27b",
            "category": "benchmark", "count": 1, "issues": [],
            "records": [{"timestamp_utc": "2026-11-06T04:26:42+00:00",
                         "category": "benchmark", "status": "PASS",
                         "summary": {"mean_e2e_tokens_per_sec": 7.9,
                                     "mean_decode_tokens_per_sec_proxy": 11.18},
                         "path": "/tmp/placeholder.json"}]}) as reader, \
             patch.object(console, "_input", side_effect=["3", "0"]), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            console._history_menu("27b")
        reader.assert_called_once_with(model="27b", kind="benchmark", limit=20)
        self.assertIn("Mean E2E throughput", output.getvalue())
        self.assertIn("Decode proxy", output.getvalue())


if __name__ == "__main__":
    unittest.main()
