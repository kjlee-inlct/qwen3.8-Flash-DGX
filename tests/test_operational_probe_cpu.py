"""CPU-only localhost chat probe tests. Never open a real socket."""
from __future__ import annotations

import json
import unittest
from unittest.mock import Mock

from scripts.manager.operational_probe import verify_chat, ENDPOINT


class Reply:
    def __init__(self, document, *, status=200):
        self.data = (json.dumps(document).encode("utf-8")
                     if isinstance(document, dict) else document)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, maximum):
        return self.data[:maximum]


class OperatingProbeCPU(unittest.TestCase):
    def response(self, served="qwen3.8-27b", *, answer="ready",
                 finish="stop", status=200):
        document = {"model": served, "choices": [
            {"message": {"role": "assistant", "content": answer},
             "finish_reason": finish}]}
        return Reply(document, status=status)

    def test_real_generation_request_is_local_bounded_and_plain(self):
        for model in ("qwen3.8-27b", "qwen3.8-flash-next"):
            with self.subTest(model=model):
                calls = []
                def opener(request, *, timeout):
                    calls.append((request, timeout))
                    return self.response(model)
                self.assertTrue(verify_chat(model, opener=opener))
                self.assertEqual(len(calls), 1)
                request, timeout = calls[0]
                self.assertEqual(request.full_url, ENDPOINT)
                self.assertEqual(request.get_method(), "POST")
                self.assertLessEqual(timeout, 90)
                payload = json.loads(request.data)
                self.assertEqual(payload["model"], model)
                self.assertFalse(payload["stream"])
                self.assertEqual(payload["temperature"], 0)
                self.assertLessEqual(payload["max_tokens"], 128)
                self.assertEqual(payload["chat_template_kwargs"],
                                 {"enable_thinking": False})

    def test_unknown_model_never_calls_socket(self):
        opener = Mock(side_effect=AssertionError("network call forbidden"))
        self.assertFalse(verify_chat("orcarouter", opener=opener))
        opener.assert_not_called()

    def test_wrong_completion_identity_blocks(self):
        self.assertFalse(verify_chat(
            "qwen3.8-27b",
            opener=lambda *a, **k: self.response("qwen3.8-flash-next")))

    def test_empty_thinking_only_output_blocks(self):
        self.assertFalse(verify_chat(
            "qwen3.8-27b",
            opener=lambda *a, **k: self.response(answer="  ")))

    def test_nonstop_termination_blocks(self):
        self.assertFalse(verify_chat(
            "qwen3.8-27b",
            opener=lambda *a, **k: self.response(finish="length")))

    def test_non_200_http_error_blocks(self):
        self.assertFalse(verify_chat(
            "qwen3.8-27b",
            opener=lambda *a, **k: self.response(status=503)))

    def test_large_or_malformed_response_blocks(self):
        for payload in (b"not json", b"X" * 65538, b"", b"[]"):
            with self.subTest(payload_len=len(payload)):
                self.assertFalse(verify_chat(
                    "qwen3.8-27b", opener=lambda *a, **k: Reply(payload)))

    def test_timeout_blocks(self):
        def broken(*args, **kwargs):
            raise TimeoutError("request timed out")
        self.assertFalse(verify_chat("qwen3.8-27b", opener=broken))


if __name__ == "__main__":
    unittest.main()
