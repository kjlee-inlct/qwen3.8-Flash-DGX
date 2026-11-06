"""D-016 CPU-only tests: tracked read-only pre-P3-A P1 evidence wrapper."""
from __future__ import annotations

from datetime import datetime, timezone
import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.temporary import p1_pre_a_readiness as audit

IMAGE = "sha256:" + "9" * 64
NOW = datetime(2026, 11, 6, 6, 20, tzinfo=timezone.utc)
HEAD = "a" * 40


def collision():
    return {
        "status": "PASS", "scope": "SOURCE", "dry_run": True,
        "name_conflict": True, "port_conflict": True, "collision_free": False,
        "errors": [], "proposed": {
            "container_name": "qwen38-flash", "port": 8000,
            "served_model_name": "qwen3.8-flash-next"},
        "containers": [{
            "name": "qwen38-flash", "image_id": IMAGE,
            "status": "Up About an hour",
            "ports": "0.0.0.0:8000->8000/tcp"}]
    }


def report(*, timestamp="2026-11-06T06:09:41+00:00"):
    raw = json.dumps(collision())
    return {
        "timestamp_utc": timestamp,
        "preflight": {"branch_ok": True, "tracked_tree_clean": True,
                      "expected_api_model_present": True,
                      "runtime_allowed": True,
                      "operator_process": {"blocked": False}},
        "cache_diagnosis": {"wizard_audit": {
            "state": "READY", "model_repo": audit.REPO,
            "source_complete": True, "hybrid_ready": True,
            "source_issues": [], "hybrid_issues": [],
            "revision": "f" * 40}},
        "plans": {k: {"ready": True, "plan": {"issues": []}}
                  for k in ("verify", "benchmark")},
        "actions": {
            "verify": {"status": "BLOCKED", "reason": "inspection_only"},
            "benchmark": {"status": "BLOCKED", "reason": "inspection_only"}},
        "checks": {
            "doctor": {"returncode": 3, "stdout": raw, "truncated": False},
            "inventory_plan": {"returncode": 3, "stdout": raw, "truncated": False}}
    }


def verify():
    return {
        "status": "PASS", "action": "verify", "executed": True,
        "model_revision": "f" * 40,
        "approval": "explicit_plan_id", "model_repo": audit.REPO,
        "served_model": audit.SERVED, "image_id": IMAGE,
        "result": {
            "status": "PASS", "baseline_status": "PASS",
            "extended_status": "PASS", "identity": {"status": "PASS"},
            "probes": {k: {"status": "PASS"} for k in
                       ("default_completion", "chat", "tools", "vision")}}}


def benchmark():
    return {
        "status": "PASS", "action": "benchmark", "executed": True,
        "model_revision": "f" * 40,
        "approval": "explicit_plan_id", "model_repo": audit.REPO,
        "served_model": audit.SERVED, "image_id": IMAGE,
        "result": {
            "status": "PASS", "benchmark": {
                "status": "PASS",
                "samples": [{"completion_tokens": 64, "latency_sec": 1.68,
                             "ttft_sec": 1.39}] * 3,
                "metrics": {"latency_p50_sec": 1.687357,
                            "latency_p95_sec": 1.780142,
                            "mean_tokens_per_sec": 38.2968,
                            "total_completion_tokens": 192,
                            "ttft_p50_sec": 1.398707,
                            "ttft_p95_sec": 1.751198}}}}


def live():
    return {"status": "LIVE_SERVICE_VERIFIED",
            "observed_model": "flash-next",
            "expected_served_id": audit.SERVED,
            "observed_model_ids": [audit.SERVED],
            "issues": [], "host_port": 8000,
            "active_container": {"name": "qwen38-flash", "image_id": IMAGE}}


def assess(cur=None, old=None, ver=None, bench=None, status=None, **kw):
    return audit.assessment(
        report() if cur is None else cur,
        report() if old is None else old,
        verify() if ver is None else ver,
        benchmark() if bench is None else bench,
        live() if status is None else status,
        git_head=kw.pop("git_head", HEAD),
        branch=kw.pop("branch", audit.BRANCH),
        git_clean=kw.pop("git_clean", True),
        now=kw.pop("now", NOW))


class PreAP1AuditCPU(unittest.TestCase):
    def test_good_historical_and_current_rc3_and_numeric_p1_readiness(self):
        d = assess()
        self.assertEqual(d["status"], "PRE_A_P1_REVIEW_READY", d["issues"])
        self.assertFalse(d["p3_a_execution_authorized"])
        self.assertFalse(d["operations_enabled"])
        self.assertTrue(d["post_p3_b_p1_rebenchmark_required"])
        self.assertEqual(d["p1_benchmark"]["metrics"]["mean_tokens_per_sec"], 38.2968)
        self.assertEqual(d["p1_benchmark"]["sample_count"], 3)

    def test_historical_rc3_without_raw_stdout_blocks(self):
        old = report()
        old["checks"]["doctor"]["stdout"] = ""
        d = assess(old=old)
        self.assertIn("HISTORICAL_P1_RC3_RAW_CAUSE_UNVERIFIED", d["issues"])

    def test_current_rc3_with_foreign_container_image_blocks(self):
        cur = report()
        payload = collision()
        payload["containers"][0]["image_id"] = "sha256:" + "f"*64
        cur["checks"]["inventory_plan"]["stdout"] = json.dumps(payload)
        d = assess(cur=cur)
        self.assertIn("CURRENT_P1_RC3_RAW_CAUSE_UNVERIFIED", d["issues"])

    def test_inventory_errors_even_if_return_code_three_block(self):
        cur = report()
        payload = collision()
        payload["errors"] = ["docker_inventory_incomplete:ValueError"]
        cur["checks"]["doctor"]["stdout"] = json.dumps(payload)
        d = assess(cur=cur)
        self.assertIn("CURRENT_P1_RC3_RAW_CAUSE_UNVERIFIED", d["issues"])

    def test_missing_p1_performance_numbers_block(self):
        bench = benchmark()
        bench["result"]["benchmark"]["metrics"]["mean_tokens_per_sec"] = None
        d = assess(bench=bench)
        self.assertIn("P1_BENCHMARK_NUMERICAL_EVIDENCE_NOT_QUALIFIED",
                      d["issues"])

    def test_historical_verified_legacy_features_missing_blocks(self):
        ver = verify()
        ver["result"]["probes"]["vision"]["status"] = "FAIL"
        d = assess(ver=ver)
        self.assertIn("P1_VERIFY_RECEIPT_NOT_QUALIFIED", d["issues"])

    def test_changed_checkpoint_revision_blocks(self):
        v = verify()
        v["model_revision"] = "e" * 40
        d = assess(ver=v)
        self.assertIn("P1_RECEIPT_CHECKPOINT_REVISION_DRIFT", d["issues"])

    def test_blocked_latest_verify_plan_blocks(self):
        cur = report()
        cur["plans"]["verify"]["ready"] = False
        d = assess(cur=cur)
        self.assertIn("P1_FUNCTIONAL_AND_BENCH_PLANS_NOT_READY", d["issues"])

    def test_stale_inspection_report_blocks_without_gpu(self):
        d = assess(cur=report(timestamp="2026-11-01T00:00:00+00:00"))
        self.assertIn("P1_INSPECT_REPORT_STALE_OR_INVALID", d["issues"])

    def test_different_served_model_blocks(self):
        current = live()
        current["observed_model_ids"] = ["qwen3.8-27b"]
        d = assess(status=current)
        self.assertIn("CURRENT_MANIFEST_API_NOT_VERIFIED", d["issues"])

    def test_changed_live_image_blocks_receipt_or_collision(self):
        current = live()
        current["active_container"]["image_id"] = "sha256:" + "e" * 64
        d = assess(status=current)
        self.assertIn("P1_VERIFY_RECEIPT_NOT_QUALIFIED", d["issues"])
        self.assertIn("CURRENT_P1_RC3_RAW_CAUSE_UNVERIFIED", d["issues"])

    def test_git_worktree_dirty_blocks(self):
        d = assess(git_clean=False)
        self.assertIn("CURRENT_GIT_BRANCH_OR_WORKTREE_NOT_VERIFIED", d["issues"])

    def test_interactive_reconciliation_never_runs_service_mutation(self):
        self.assertEqual(audit.check_collision(report(), IMAGE)["rc3_expected"],
                         True)
        self.assertNotIn("docker stop", str(audit.run_readonly))
        self.assertNotIn("git pull", str(audit.run_readonly))

    def test_private_evidence_rejects_world_readable_file_and_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            good = root / "good.json"
            good.write_text(json.dumps(report()))
            good.chmod(0o600)
            self.assertEqual(audit.private_json(good, root, max_size=65536),
                             report())
            good.chmod(0o644)
            with self.assertRaises(ValueError):
                audit.private_json(good, root, max_size=65536)
            bad = root / "shortcut.json"
            bad.symlink_to(good)
            with self.assertRaises(ValueError):
                audit.private_json(bad, root, max_size=65536)

    def test_main_persists_0600_summary_outside_git_and_never_executes_gpu(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            reports = root / "reports"
            reports.mkdir(mode=0o700)
            p1 = root / "p1"
            p1.mkdir(mode=0o700)
            cur_path = reports / "20261106T060941Z-test" / "result.json"
            cur_path.parent.mkdir(mode=0o700)
            old_path = reports / "20261105T113110Z-old" / "result.json"
            old_path.parent.mkdir(mode=0o700)
            verify_path = p1 / "verify.json"
            bench_path = p1 / "benchmark.json"
            for path, obj in ((cur_path, report(timestamp=datetime.now(timezone.utc).isoformat())),
                              (old_path, report()), (verify_path, verify()),
                              (bench_path, benchmark())):
                path.write_text(json.dumps(obj))
                path.chmod(0o600)

            def fake_readonly(args, **kwargs):
                if args[:3] == ["./wizard.sh", "service", "manager"]:
                    return 0, json.dumps(live())
                if args[:3] == ["git", "branch", "--show-current"]:
                    return 0, audit.BRANCH + "\n"
                if args[:3] == ["git", "rev-parse", "HEAD"]:
                    return 0, HEAD + "\n"
                if args[:3] == ["git", "status", "--porcelain"]:
                    return 0, ""
                raise AssertionError("unexpected subprocess: " + repr(args))

            with patch.object(audit, "P1_ROOT", p1),                  patch.object(audit, "run_readonly", side_effect=fake_readonly),                  contextlib.redirect_stdout(io.StringIO()) as output:
                rc = audit.main(["--report-root", str(reports),
                                 "--report", str(cur_path),
                                 "--historical-report", str(old_path),
                                 "--verify-receipt", str(verify_path),
                                 "--benchmark-receipt", str(bench_path)])
            self.assertEqual(rc, 0)
            data = json.loads(output.getvalue())
            self.assertEqual(data["status"], "PRE_A_P1_REVIEW_READY")
            self.assertFalse(data["operations_enabled"])
            self.assertFalse(data["p3_a_execution_authorized"])
            receipt = Path(data["evidence_file"])
            self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
            self.assertEqual(json.loads(receipt.read_text())["status"],
                             "PRE_A_P1_REVIEW_READY")


if __name__ == "__main__":
    unittest.main()
