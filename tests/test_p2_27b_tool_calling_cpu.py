"""Offline P2 final 27B Tool Calling profile and one-tool roundtrip regressions."""
from __future__ import annotations

import json
from pathlib import Path
import unittest
from urllib.error import HTTPError

from scripts.manager import p2_27b_tool_calling as mod
from scripts.manager import p2_27b_launch_preview as launch


class Response:
    def __init__(self, data, status=200):
        self.body = json.dumps(data).encode("utf-8")
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, n):
        return self.body[:n]


def tool_answer():
    return {
        "model": mod.SERVED, "choices": [
            {"message": {"role": "assistant", "content": None,
                         "tool_calls": [{
                             "id": "call_1", "type": "function",
                             "function": {"name": "get_probe_token",
                                          "arguments": '{"key":"test"}'},
                         }]}}]
    }


def followup_answer(answer="The tool returned DGX_TOOL_PROBE_OK"):
    return {"model": mod.SERVED, "choices": [
        {"message": {"role": "assistant", "content": answer}}]}


class P2ToolCallingCPU(unittest.TestCase):
    def test_opt_in_exact_flags_and_default_immutability(self):
        image = "sha256:" + "a" * 64
        initial = launch._candidate_argv(Path("/cache"), image)
        enabled = launch._candidate_argv(Path("/cache"), image,
                                          tool_calling=True)
        self.assertNotIn("--enable-auto-tool-choice", initial)
        self.assertEqual(enabled[:len(initial)], initial)
        self.assertEqual(enabled[len(initial):],
                         ["--enable-auto-tool-choice", "--tool-call-parser",
                          "qwen3_coder", "--reasoning-parser", "qwen3"])
        self.assertIn("nvidia/Qwen3.8-27B-NVFP4", mod.MODEL)

    def test_profile_is_read_only_and_not_misleadingly_pass(self):
        p = mod.profile()
        self.assertFalse(p["executed"])
        self.assertFalse(p["container_recreated"])
        self.assertFalse(p["production_enabled"])
        self.assertEqual(p["status"], "SOURCE_PROFILE_ONLY_DGX_NOT_QUALIFIED")
        self.assertEqual(p["vllm_version_policy"], "0.32")
        self.assertIn("openwebui_native_tool_calling_acceptance",
                      p["requirements"])

    def test_fake_local_function_call_and_continuation(self):
        requests = []
        replies = [
            {"data": [{"id": mod.SERVED}]}, tool_answer(), followup_answer()]
        def opener(request, *, timeout):
            self.assertTrue(request.full_url.startswith("http://127.0.0.1:8000/"))
            self.assertLessEqual(timeout, 90)
            requests.append(request)
            return Response(replies[len(requests)-1])
        result = mod.probe(opener=opener)
        self.assertEqual(result["status"], "LOCAL_STRUCTURED_TOOL_CYCLE_PASS")
        self.assertTrue(result["structured_tool_call"])
        self.assertTrue(result["tool_result_continuation"])
        self.assertTrue(result["reasoning_separation"])
        self.assertEqual(len(requests), 3)
        self.assertEqual(requests[0].get_method(), "GET")
        first = json.loads(requests[1].data)
        self.assertEqual(first["tool_choice"], "auto")
        self.assertEqual(first["model"], mod.SERVED)
        self.assertFalse(first["stream"])
        self.assertEqual(first["chat_template_kwargs"], {"enable_thinking": False})
        second = json.loads(requests[2].data)
        self.assertEqual(second["messages"][-1]["role"], "tool")
        self.assertEqual(second["messages"][-1]["tool_call_id"], "call_1")
        self.assertEqual(second["messages"][-1]["content"], "DGX_TOOL_PROBE_OK")

    def test_wrong_active_model_blocks_before_tool_query(self):
        count = []
        def opener(request, *, timeout):
            count.append(request)
            return Response({"data": [{"id": "qwen3.8-flash-next"}]})
        result = mod.probe(opener=opener)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(len(count), 1)
        self.assertIn("ACTIVE_27B_SOLE_MODEL_ID_NOT_VERIFIED", result["issues"])

    def test_unstructured_auto_choice_fails_closed(self):
        responses = [
            {"data": [{"id": mod.SERVED}]},
            {"model": mod.SERVED, "choices": [
                {"message": {"role": "assistant", "content": "no call"}}]},
        ]
        def opener(request, *, timeout):
            return Response(responses.pop(0))
        result = mod.probe(opener=opener)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("AUTO_TOOL_CALL_NOT_STRUCTURED", result["issues"])

    def test_malformed_tool_arguments_fail_closed(self):
        first = tool_answer()
        first["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"] = "{broken"
        responses = [{"data": [{"id": mod.SERVED}]}, first]
        def opener(request, *, timeout):
            return Response(responses.pop(0))
        result = mod.probe(opener=opener)
        self.assertEqual(result["status"], "BLOCKED")

    def test_reasoning_markup_in_final_content_blocks(self):
        responses = [{"data": [{"id": mod.SERVED}]}, tool_answer(),
                     followup_answer("<think>internal</think> DGX_TOOL_PROBE_OK")]
        def opener(request, *, timeout):
            return Response(responses.pop(0))
        result = mod.probe(opener=opener)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("REASONING_MARKUP_IN_FINAL_CONTENT", result["issues"])

    def test_missing_tool_result_blocks(self):
        responses = [{"data": [{"id": mod.SERVED}]}, tool_answer(),
                     followup_answer("No data.")]
        def opener(request, *, timeout):
            return Response(responses.pop(0))
        result = mod.probe(opener=opener)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("TOOL_RESULT_CONTINUATION_UNVERIFIED", result["issues"])

    def test_http_400_auto_tool_choice_error_is_reported(self):
        calls = []
        def opener(request, *, timeout):
            calls.append(request)
            if len(calls) == 1:
                return Response({"data": [{"id": mod.SERVED}]})
            raise HTTPError(request.full_url, 400, "auto tool choice", {}, None)
        result = mod.probe(opener=opener)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertIn("LOCAL_API_HTTP_ERROR_400", result["issues"])
        self.assertEqual(len(calls), 2)


if __name__ == "__main__":
    unittest.main()
