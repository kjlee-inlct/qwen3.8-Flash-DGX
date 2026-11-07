"""Offline CPU regressions for explicit, non-disruptive 27B curl smoke."""
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SMOKE = ROOT / "scripts/temporary/operational-27b-curl-smoke.sh"
MOCK_CURL = r'''#!/usr/bin/env python3
import json
import os
import sys

args = sys.argv[1:]
url = args[-1] if args else ""
mode = os.environ.get("FAKE_CURL_MODE", "pass")
trace = os.environ.get("FAKE_CURL_TRACE")
if trace:
    with open(trace, "a", encoding="utf-8") as output:
        output.write(url + "\n")
if mode == "transport_fail" and url.endswith("/v1/models"):
    sys.exit(7)
if url.endswith("/health"):
    print("503" if mode == "health_bad" else "200", end="")
elif url.endswith("/v1/models"):
    if mode == "json_bad":
        print("not json")
    else:
        identifier = "qwen3.8-flash-next" if mode == "wrong_model" else "qwen3.8-27b"
        print(json.dumps({"data": [{"id": identifier}]}))
elif url.endswith("/v1/chat/completions"):
    if "--data-binary" not in args:
        sys.exit(8)
    payload = json.loads(args[args.index("--data-binary") + 1])
    if (payload["model"] != "qwen3.8-27b" or payload["stream"] is not False
            or payload["max_tokens"] > 256):
        sys.exit(9)
    reply_model = "qwen3.8-flash-next" if mode == "wrong_chat_model" else "qwen3.8-27b"
    content = ("" if mode == "empty_reply" else
               "Thinking-style prose\n</think>\n\nDGX_OK"
               if mode == "reasoning_in_content" else
               "WRONG_ANSWER" if mode == "non_exact_reply" else "DGX_OK")
    print(json.dumps({"model": reply_model, "choices": [
        {"message": {"content": content}, "finish_reason": "stop"}]}))
else:
    sys.exit(10)
'''


class OperationalCurlSmokeCPU(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        curl = self.root / "curl"
        curl.write_text(MOCK_CURL, encoding="utf-8")
        curl.chmod(0o755)
        self.trace = self.root / "curl.trace"

    def tearDown(self):
        self.temp.cleanup()

    def execute(self, mode="pass", extra_args=()):
        env = dict(os.environ)
        env.update(PATH=str(self.root) + os.pathsep + env.get("PATH", ""),
                   FAKE_CURL_MODE=mode, FAKE_CURL_TRACE=str(self.trace))
        return subprocess.run(
            ["bash", str(SMOKE), *extra_args],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=15,
            check=False,
        )

    def test_health_identity_and_real_generation_are_distinct(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        for expected in ("HEALTH_PASS", "IDENTITY_PASS", "INFERENCE_PASS",
                         "FORMAT_PASS exact DGX_OK", "27B_CURL_SMOKE_PASS"):
            self.assertIn(expected, result.stdout)
        self.assertEqual(self.trace.read_text().splitlines(), [
            "http://127.0.0.1:8000/health",
            "http://127.0.0.1:8000/v1/models",
            "http://127.0.0.1:8000/v1/chat/completions",
        ])

    def test_health_failure_never_requests_inference(self):
        result = self.execute("health_bad")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL: /health", result.stderr)
        self.assertEqual(len(self.trace.read_text().splitlines()), 1)

    def test_wrong_served_model_never_requests_inference(self):
        result = self.execute("wrong_model")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL: /v1/models identity", result.stderr)
        self.assertEqual(len(self.trace.read_text().splitlines()), 2)

    def test_unparseable_models_block(self):
        result = self.execute("json_bad")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL: /v1/models identity", result.stderr)

    def test_transport_error_blocks(self):
        result = self.execute("transport_fail")
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("INFERENCE_PASS", result.stdout)

    def test_empty_inference_is_not_a_pass(self):
        result = self.execute("empty_reply")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FAIL: 27B inference", result.stderr)

    def test_real_dgx_style_thinking_text_keeps_inference_pass_but_flags_format(self):
        result = self.execute("reasoning_in_content")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("INFERENCE_PASS", result.stdout)
        self.assertIn("FORMAT_DEVIATION", result.stdout)
        self.assertIn("think_end_marker_present=true", result.stdout)
        self.assertNotIn("FORMAT_PASS", result.stdout)
        self.assertIn("27B_CURL_SMOKE_PASS", result.stdout)

    def test_wrong_nonempty_answer_does_not_get_exact_format_pass(self):
        result = self.execute("non_exact_reply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("INFERENCE_PASS", result.stdout)
        self.assertIn("FORMAT_DEVIATION", result.stdout)
        self.assertIn("think_end_marker_present=false", result.stdout)

    def test_wrong_completion_model_is_not_a_pass(self):
        result = self.execute("wrong_chat_model")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("model identity mismatch", result.stderr)

    def test_arguments_refused_without_any_network_call(self):
        result = self.execute(extra_args=("http://somewhere-else",))
        self.assertEqual(result.returncode, 2)
        self.assertFalse(self.trace.exists())


if __name__ == "__main__":
    unittest.main()
