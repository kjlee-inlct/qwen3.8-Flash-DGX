"""Offline SSE fake-HTTP tests; no runtime or GPU calls."""
from __future__ import annotations

import json
import unittest
from urllib.error import HTTPError

from scripts.manager import p2_27b_tool_streaming as mod


def event(delta, finish=None):
    return b"data: " + json.dumps({
        "model": mod.SERVED,
        "choices": [{"index": 0, "delta": delta, "finish_reason": finish}],
    }).encode() + b"\n"


def good_stream():
    return [
        event({"role": "assistant"}),
        event({"tool_calls": [{"index": 0, "id": "call_1",
                                "type": "function",
                                "function": {"name": "get_probe_token",
                                             "arguments": '{"key":'}}]}),
        event({"tool_calls": [{"index": 0, "function":
                                {"arguments": '"test"}'}}]}),
        event({}, finish="tool_calls"),
        b"data: [DONE]\n",
    ]


class Response:
    def __init__(self, obj=None, *, lines=None, status=200):
        self.status = status
        self.body = json.dumps(obj).encode() if obj is not None else b""
        self.lines = lines or []

    def read(self, n):
        return self.body[:n]

    def __iter__(self):
        return iter(self.lines)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class SSEProbeCPU(unittest.TestCase):
    def test_valid_incremental_tool_chunks_and_done(self):
        result = mod.evaluate_stream(good_stream())
        self.assertEqual(result["status"], "LOCAL_STREAMED_TOOL_CALL_PASS")
        self.assertTrue(result["streamed_tool_call"])
        self.assertEqual(result["stream_event_count"], 4)
        self.assertFalse(result["executed_tool"])

    def test_missing_done_blocks(self):
        r = mod.evaluate_stream(good_stream()[:-1])
        self.assertIn("SSE_DONE_MISSING", r["issues"])

    def test_missing_finish_blocks(self):
        chunks = good_stream()
        chunks[-2] = event({})
        self.assertIn("SSE_TOOL_FINISH_REASON_MISSING",
                      mod.evaluate_stream(chunks)["issues"])

    def test_wrong_function_arguments_blocks(self):
        chunks = good_stream()
        chunks[2] = event({"tool_calls": [{"index": 0,
                                           "function": {"arguments": '"bad"}'}}]})
        self.assertIn("SSE_TOOL_ARGUMENTS_INVALID",
                      mod.evaluate_stream(chunks)["issues"])

    def test_wrong_index_blocks(self):
        chunks = good_stream()
        chunks[1] = event({"tool_calls": [{"index": 1, "id": "call_1",
                                           "type": "function",
                                           "function": {"name": "get_probe_token",
                                                        "arguments": '{"key":'}}]})
        self.assertEqual(mod.evaluate_stream(chunks)["status"], "BLOCKED")

    def test_reasoning_in_content_blocks(self):
        chunks = good_stream()
        chunks[0] = event({"content": "<think>hidden</think>"})
        r = mod.evaluate_stream(chunks)
        self.assertIn("SSE_REASONING_LEAKED_IN_FINAL_CONTENT", r["issues"])

    def test_oversized_or_bad_sse_blocks(self):
        for chunks in ([b"data: " + b"x" * 65537],
                       [b"wrong prefix\n"],
                       [b"data: not json\n"],
                       [b"data: [DONE]\n"]):
            with self.subTest(chunks=chunks[:1]):
                self.assertEqual(mod.evaluate_stream(chunks)["status"], "BLOCKED")

    def test_full_fake_http_identity_and_stream_payload(self):
        requests = []
        def opener(request, *, timeout):
            requests.append(request)
            self.assertEqual(request.full_url.split("/v1")[0],
                             "http://127.0.0.1:8000")
            if len(requests) == 1:
                return Response({"data": [{"id": mod.SERVED}]})
            return Response(lines=good_stream())
        r = mod.probe_stream(opener=opener)
        self.assertEqual(r["status"], "LOCAL_STREAMED_TOOL_CALL_PASS")
        self.assertEqual(len(requests), 2)
        req = json.loads(requests[1].data)
        self.assertTrue(req["stream"])
        self.assertEqual(req["tool_choice"], "auto")
        self.assertEqual(req["chat_template_kwargs"], {"enable_thinking": False})
        self.assertEqual(req["max_tokens"], 256)

    def test_sole_model_id_mismatch_does_not_post(self):
        seen = []
        def opener(request, *, timeout):
            seen.append(request)
            return Response({"data": [{"id": "qwen3.8-flash-next"}]})
        r = mod.probe_stream(opener=opener)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertEqual(len(seen), 1)
        self.assertIn("ACTIVE_27B_SOLE_MODEL_ID_NOT_VERIFIED", r["issues"])

    def test_http_400_is_not_pass(self):
        def opener(request, *, timeout):
            if request.data is None:
                return Response({"data": [{"id": mod.SERVED}]})
            raise HTTPError(request.full_url, 400, "auto parser disabled", {}, None)
        r = mod.probe_stream(opener=opener)
        self.assertEqual(r["status"], "BLOCKED")
        self.assertIn("LOCAL_STREAM_HTTP_ERROR_400", r["issues"])


if __name__ == "__main__":
    unittest.main()
