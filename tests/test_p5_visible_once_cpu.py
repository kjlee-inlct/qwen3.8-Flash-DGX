"""CPU-only safety fixtures for the P5 one-shot visible-output measurement."""
import io
import json
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from scripts.manager import measurement_bench as bench
from scripts.manager import p5_visible_once as p5

CID = "a" * 64


def sample():
    return {
        "model": "orcarouter", "git_head": "b" * 40,
        "timestamp_utc": "2026-11-19T01:00:00+00:00",
        "monotonic_ns": 10000,
        "docker": {"container": {"id": CID}},
    }


def gate(model):
    assert model == "orcarouter"
    return {"served_id": "served-test", "checkpoint": "pin"}, sample(), {
        "id": CID, "running": True, "name": "test-container",
    }, 8192


def builder(model, target):
    return "target:" + str(target + 60), target


def tokens(model, prompt):
    return int(prompt.split("target:")[1].split("\n")[0])


def visible(model, prompt, output, *, enable_thinking=None):
    assert model == "served-test" and output == 256
    assert enable_thinking is False
    return {
        "stream_done_observed": True, "ttft_seconds": 0.2,
        "ttfc_seconds": 0.3, "visible_characters": 30,
        "completion_tokens_reported": 50,
        "generation_tps_after_first_token": 25.0,
        "stream_metrics_quality": "VISIBLE_CONTENT_AND_USAGE_OBSERVED",
        "finish_reason": "stop",
    }


class OneShotSafetyCPU(unittest.TestCase):
    def opts(self, **overrides):
        defaults = dict(
            gate=gate, build_prompt=builder, token_count=tokens,
            stream=visible, capture=lambda **kw: sample(),
            save=lambda doc: "/private/receipt.json",
            claim=lambda root, docker_id: "/private/claim",
            state_dir=Path("/private"),
        )
        defaults.update(overrides)
        return defaults

    def test_missing_ack_blocks_before_all_probes(self):
        def forbidden(*a, **kw):
            raise AssertionError("must not run")
        result = p5.run_once("incorrect", **self.opts(gate=forbidden))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertFalse(result["inference_executed"])

    def test_visible_one_shot_exact_three_cases_never_retries(self):
        calls = []
        def once(model, prompt, output, *, enable_thinking=None):
            calls.append(model)
            return visible(model, prompt, output, enable_thinking=enable_thinking)
        with patch.object(p5, "observation_summary", return_value={"status": "OBSERVED_INTERVAL"}):
            result = p5.run_once(bench.ACK, **self.opts(stream=once))
        self.assertEqual(len(calls), 3)
        self.assertEqual([c["context_k"] for c in result["results"]], [1, 4, 7])
        self.assertEqual(result["status"], "COLLECTED_UNQUALIFIED")
        self.assertEqual(result["summary"]["visible_measured_cases"], 3)
        self.assertTrue(result["summary"]["container_id_continuous"])
        self.assertFalse(result["production_released"])
        self.assertNotIn("target:", json.dumps(result))

    def test_reasoning_only_stops_after_first_gpu_request(self):
        calls = []
        def thinking(model, prompt, output, *, enable_thinking=None):
            calls.append(1)
            return {"stream_done_observed": True,
                    "ttft_seconds": 0.2, "ttfc_seconds": None,
                    "visible_characters": 0, "completion_tokens_reported": 256,
                    "stream_metrics_quality": "REASONING_ONLY_NO_VISIBLE_CONTENT"}
        with patch.object(p5, "observation_summary", return_value={"status": "OBSERVED_INTERVAL"}):
            result = p5.run_once(bench.ACK, **self.opts(stream=thinking))
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["status"], "INCOMPLETE_MEASUREMENT")
        self.assertEqual(result["summary"]["stop_issue"], "NO_VERIFIED_VISIBLE_CONTENT_STOP")

    def test_no_auto_retry_on_api_exception(self):
        calls = []
        def failure(*a, **kw):
            calls.append(1)
            raise ValueError("INJECTED_SERVER_REFUSAL")
        with patch.object(p5, "observation_summary", return_value={"status": "OBSERVED_INTERVAL"}):
            result = p5.run_once(bench.ACK, **self.opts(stream=failure))
        self.assertEqual(len(calls), 1)
        self.assertEqual(result["summary"]["stop_issue"], "INCOMPLETE_CASE_ValueError")

    def test_claim_is_exclusive_private_and_persistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "state"
            first = p5._claim_once(root, CID)
            self.assertEqual(Path(first).stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                p5._claim_once(root, CID)
            self.assertEqual(json.loads(Path(first).read_text())["docker_id"], CID)

    def test_docker_identity_drift_aborts_after_one_request(self):
        bad = sample()
        bad["docker"]["container"]["id"] = "c" * 64
        with patch.object(p5, "observation_summary", return_value={"status": "INVALID_INTERVAL"}):
            result = p5.run_once(bench.ACK, **self.opts(capture=lambda **kw: bad))
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["summary"]["stop_issue"], "DOCKER_IDENTITY_DRIFT")
        self.assertFalse(result["summary"]["container_id_continuous"])

    def test_sse_request_sends_thinking_override_only_when_explicit(self):
        events = (b'data: {"choices":[{"delta":{"content":"A"},'
                  b'"finish_reason":"stop"}]}\n'
                  b'data: {"choices":[],"usage":{"completion_tokens":2}}\n'
                  b'data: [DONE]\n')
        requests = []
        def fake_open(req, timeout):
            requests.append(json.loads(req.data))
            return io.BytesIO(events)
        with patch.object(bench, "urlopen", side_effect=fake_open):
            a = bench._stream_chat("served", "prompt", 16)
            b = bench._stream_chat("served", "prompt", 16, enable_thinking=False)
        self.assertNotIn("chat_template_kwargs", requests[0])
        self.assertEqual(requests[1]["chat_template_kwargs"], {"enable_thinking": False})
        self.assertIsNotNone(a["ttfc_seconds"])
        self.assertIsNotNone(b["ttfc_seconds"])
        self.assertNotIn("prompt", json.dumps(b))

    def test_invalid_thinking_flag_blocked_without_network(self):
        with self.assertRaises(ValueError):
            bench._stream_chat("served", "prompt", 16, enable_thinking="false")


if __name__ == "__main__":
    unittest.main()
