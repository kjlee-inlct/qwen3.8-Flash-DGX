"""CPU-only P2 benchmark approval/metrics/Wizard integration tests.

No real Docker calls, HTTP, CUDA, model loads or service mutations.
"""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from scripts.manager import p2_27b_benchmark as bench
from scripts.manager import p2_27b_gpu_trial as trial
from wizard import main as wizard


class Stream:
    status = 200
    def __init__(self):
        self.lines = [
            b'data: {"choices":[{"delta":{"role":"assistant"}}]}\n',
            b'data: {"choices":[{"delta":{"reasoning_content":"work"}}]}\n',
            b'data: {"choices":[{"delta":{"content":"done"}}]}\n',
            b'data: {"choices":[],"usage":{"prompt_tokens":8,"completion_tokens":6}}\n',
            b'data: [DONE]\n',
        ]
    def __enter__(self): return self
    def __exit__(self, *args): return False
    def __iter__(self): return iter(self.lines)


class BenchmarkCPU(unittest.TestCase):
    def fake_plan(self):
        return {
            "status": "READY_TO_REQUEST_TRIAL_APPROVAL",
            "plan_id": "1"*64, "source_container_id": "2"*64,
            "image_id": "sha256:"+"3"*64, "issues": [],
            "expires_at_epoch_seconds": 5000000000,
            "executed": False,
        }

    def test_benchmark_plan_is_distinct_from_smoke_plan(self):
        p = bench.make_plan(trial_planner=self.fake_plan)
        self.assertEqual(p["status"], "READY_TO_REQUEST_TRIAL_APPROVAL")
        self.assertNotEqual(p["plan_id"], "1"*64)
        self.assertEqual(len(p["plan_id"]), 64)
        self.assertEqual(p["benchmark_profile"]["requests"], 3)
        self.assertFalse(p["executed"])
        self.assertIn("downtime", p["notice"])

    def test_blocked_trial_plan_remains_blocked(self):
        p = bench.make_plan(trial_planner=lambda: {
            "status":"BLOCKED","plan_id":None,"issues":["NO_SOURCE"],"executed":False})
        self.assertEqual(p["status"], "BLOCKED")
        self.assertIsNone(p["plan_id"])

    def test_memory_samples_never_mislabel_peak(self):
        good = lambda *args, **kw: SimpleNamespace(returncode=0, stdout="2048, 128000\n")
        sample = bench.memory_snapshot(run=good)
        self.assertEqual(sample["used_mib"], 2048)
        self.assertEqual(sample["status"], "POINT_SAMPLE_NOT_PEAK")
        bad = lambda *args, **kw: SimpleNamespace(returncode=0, stdout="[N/A], [N/A]\n")
        self.assertEqual(bench.memory_snapshot(run=bad)["status"], "UNAVAILABLE")

    def test_stream_reasoning_token_counts_as_first_generated_chunk(self):
        ticks = iter([5.5])
        result = bench._stream_sample(Stream(), 5.0, clock=lambda:next(ticks))
        self.assertEqual(result["first_token_at"], 5.5)
        self.assertEqual(result["usage"]["completion_tokens"], 6)
        self.assertTrue(result["stream_complete"])
        self.assertTrue(result["generated"])

    def test_stream_rejects_oversized_payload(self):
        class TooBig:
            def __iter__(self):
                return iter([b"x"*262145])
        with self.assertRaises(ValueError):
            bench._stream_sample(TooBig(), 0, clock=lambda:0)

    def test_bounded_metrics_no_fake_prefill_or_peak(self):
        self.requests = []
        times = iter([1.0, 1.2, 2.0, 3.0, 3.2, 4.0,
                      5.0, 5.2, 6.0])
        def opener(request, *, timeout):
            self.requests.append((request,timeout))
            return Stream()
        doc = bench.measure(
            opener=opener, clock=lambda: next(times),
            identity=lambda model: model == trial.SERVED,
            memory_reader=lambda: {"status":"UNAVAILABLE","used_mib":None})
        self.assertEqual(doc["status"], "PASS")
        self.assertEqual(len(doc["samples"]), 3)
        self.assertEqual(doc["metrics"]["ttft_p50_sec"], 0.2)
        self.assertAlmostEqual(doc["metrics"]["mean_decode_tokens_per_sec_proxy"], 6.25)
        self.assertEqual(doc["metrics"]["mean_prompt_ingest_tokens_per_sec_proxy"], 40.0)
        self.assertIsNone(doc["metrics"]["prefill_tokens_per_sec"])
        self.assertIsNone(doc["metrics"]["gpu_peak_mib"])
        self.assertEqual(len(self.requests), 3)
        for req, timeout in self.requests:
            self.assertEqual(timeout, 120)
            self.assertTrue(req.full_url.endswith("/v1/chat/completions"))
            payload = json.loads(req.data)
            self.assertEqual(payload["model"], trial.SERVED)
            self.assertEqual(payload["max_tokens"], 64)
            self.assertTrue(payload["stream"])

    def test_nonmatching_api_blocks_before_any_inference(self):
        with self.assertRaises(RuntimeError):
            bench.measure(identity=lambda model: False,
                          opener=lambda *args, **kw:self.fail("unexpected HTTP"))

    def test_existing_guarded_trial_performs_restoration_and_metrics_capture(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp)/"base.json"
            evidence.write_text("{}")
            seen = {}
            def core(plan, ack, **kwargs):
                seen["plan"] = plan
                seen["ack"] = ack
                self.assertTrue(kwargs["inference"]())
                return 0, {
                    "status":"PASS_RESTORED", "trial":"PASS",
                    "executed":True, "evidence":str(evidence),
                    "restoration":{"status":"RESTORED","issues":[]}}
            rc, result = bench.execute(
                "f"*64, trial.ACK, core=core, measurement=lambda:{
                    "status":"PASS", "metrics":{"ttft_p50_sec":0.2}},
                status_inspector=lambda:{
                    "status":"LIVE_SERVICE_VERIFIED", "observed_model":"flash-next",
                    "expected_served_id":"qwen3.8-flash-next", "issues":[]})
            self.assertEqual(rc, 0)
            self.assertEqual(result["status"], "BENCH_PASS_RESTORED_VERIFIED")
            self.assertEqual(seen["plan"],"f"*64)
            self.assertEqual(seen["ack"],trial.ACK)
            record = Path(result["benchmark_evidence"])
            self.assertTrue(record.is_file())
            self.assertIn("ttft_p50_sec", record.read_text())
            self.assertEqual(json.loads(record.read_text())["status"],
                             "BENCH_PASS_RESTORED_VERIFIED")

    def test_inconsistent_restored_api_identity_blocks_full_benchmark_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            evidence = Path(temp) / "base.json"
            evidence.write_text("{}")
            def core(plan, ack, **kwargs):
                self.assertTrue(kwargs["inference"]())
                return 0, {"status": "PASS_RESTORED", "trial": "PASS",
                           "executed": True, "evidence": str(evidence),
                           "restoration": {"status": "RESTORED", "issues": []}}
            rc, result = bench.execute("f"*64, trial.ACK, core=core,
                measurement=lambda: {"status": "PASS", "metrics": {}},
                status_inspector=lambda: {
                    "status": "LIVE_SERVICE_VERIFIED", "observed_model": "flash-next",
                    "expected_served_id": "qwen3.8-27b", "issues": []})
            self.assertEqual(rc, 4)
            self.assertEqual(result["status"], "BENCH_PARTIAL_RESTORED")
            self.assertEqual(json.loads(Path(result["benchmark_evidence"]).read_text())["status"],
                             "BENCH_PARTIAL_RESTORED")

    def test_no_execute_never_creates_benchmark_evidence(self):
        rc, obj = bench.execute(
            "bad", trial.ACK,
            core=lambda *args,**kw:(3,{"status":"BLOCKED","executed":False,
                                       "issues":["INVALID_APPROVAL"]}),
            measurement=lambda:self.fail("benchmark attempted"))
        self.assertEqual(rc,3)
        self.assertIsNone(obj["benchmark"])

    def test_wizard_plan_and_execute_require_explicit_flags(self):
        with patch("scripts.manager.p2_27b_benchmark.main",return_value=0) as runner, \
             contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(wizard.main(["model","27b","benchmark","--plan","--json"]), 0)
            runner.assert_called_once_with(["plan"])
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(wizard.main(["model","27b","benchmark","--plan",
                                          "--approve-plan","f"*64,"--json"]),2)
        self.assertEqual(json.loads(out.getvalue())["status"],"BLOCKED")
        with contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(wizard.main(["model","27b","benchmark","--execute",
                                          "--dry-run","--json"]),3)
        self.assertFalse(json.loads(out.getvalue())["executed"])


if __name__ == "__main__":
    unittest.main()
