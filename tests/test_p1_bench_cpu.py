"""Fake local HTTP/SSE benchmark. Never opens a socket or requires CUDA."""
import json
from urllib.request import Request
import unittest
from scripts.manager.p1_bench import run_benchmark, require_model, _percentile


class FakeResponse:
    def __init__(self, body=b"", stream=None, status=200):
        self.body = body
        self.stream = stream or []
        self.status = status
    def __enter__(self):
        return self
    def __exit__(self, *_):
        pass
    def read(self, _n):
        return self.body
    def __iter__(self):
        return iter(self.stream)


class BenchCPU(unittest.TestCase):
    def test_local_model_identity(self):
        def open_fn(req, **_):
            url = req.full_url
            if url.endswith("/health"):
                return FakeResponse()
            if url.endswith("/v1/models"):
                return FakeResponse(body=json.dumps(
                    {"data": [{"id": "qwen3.8-flash-next"}]}).encode())
            self.fail("unapproved URL: " + url)
        self.assertEqual(require_model("http://127.0.0.1:8000",
                                       "qwen3.8-flash-next", opener=open_fn)["health"], "PASS")

    def test_model_id_mismatch_rejected(self):
        def open_fn(req, **_):
            return FakeResponse(body=json.dumps({"data": [{"id": "other"}]}).encode())
        with self.assertRaises(ValueError):
            require_model("http://127.0.0.1:8000", "qwen3.8-flash-next", opener=open_fn)

    def test_non_local_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            run_benchmark("http://example.com", "bad", requests=1)

    def test_bounds_reject_unlimited_load(self):
        for kwargs in ({"requests": 21}, {"requests": 0},
                       {"max_tokens": 10000}, {"seed": -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                run_benchmark("http://127.0.0.1:8000", "model", **kwargs)

    def test_default_bench_prompts_avoid_reasoning_only_token_budget(self):
        from scripts.manager.p1_bench import PROMPTS
        self.assertEqual(len(PROMPTS), 3)
        self.assertTrue(all(p.endswith("/no_think") for p in PROMPTS))

    def test_fake_stream_measures_ttft_and_tokens(self):
        calls = []
        def opener(req: Request, **_):
            calls.append((req.full_url, json.loads(req.data)))
            content = [
                b'data: {"choices":[{"delta":{"content":"hello"}}]}\n',
                b'data: {"choices":[{"delta":{"content":" world"}}]}\n',
                b'data: {"choices":[],"usage":{"completion_tokens":8}}\n',
                b"data: [DONE]\n",
            ]
            return FakeResponse(stream=content)
        ticks = iter([float(i) * .1 for i in range(15)])
        result = run_benchmark("http://127.0.0.1:8000", "qwen3.8-flash-next",
                               requests=3, max_tokens=32,
                               opener=opener, clock=lambda: next(ticks))
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["metrics"]["total_completion_tokens"], 24)
        self.assertEqual(result["concurrency"], 1)
        self.assertEqual(len(calls), 3)
        self.assertTrue(all(url.endswith("/v1/chat/completions")
                            and p["stream"] is True for url, p in calls))
        self.assertEqual(len(result["samples"]), 3)
        self.assertEqual(result["samples"][0]["ttft_sec"], .1)
        self.assertNotIn("prompt", result["samples"][0])

    def test_no_usage_yields_partial_not_guessed_tps(self):
        def opener(req, **_):
            return FakeResponse(stream=[
                b'data: {"choices":[{"delta":{"content":"hello"}}]}\n',
                b"data: [DONE]\n",
            ])
        ticks = iter([0, 1, 2])
        x = run_benchmark("http://127.0.0.1:8000", "model", requests=1,
                          opener=opener, clock=lambda: next(ticks))
        self.assertEqual(x["status"], "PARTIAL")
        self.assertIsNone(x["metrics"]["mean_tokens_per_sec"])
        self.assertIsNone(x["samples"][0]["completion_tokens"])

    def test_percentiles_interpolate(self):
        self.assertEqual(_percentile([1, 3, 5], .5), 3.0)
        self.assertEqual(_percentile([1, 3], .95), 2.9)


if __name__ == "__main__":
    unittest.main()
