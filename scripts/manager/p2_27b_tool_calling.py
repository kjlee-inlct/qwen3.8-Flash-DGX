"""P2 final item: opt-in Qwen3.8-27B native automatic tool-calling profile.

Source profile is intentionally non-dispatching. The original P2/P3 27B
container was created without these flags; changing Python files will not
retrofit its Docker Config.Cmd. A separately approved migration must preserve
both original images/containers and a rollback route.

The `probe` command only performs bounded, LOCAL read-only inference against
an already-serving API; it cannot stop/start Docker or run an external tool.
"""
from __future__ import annotations

import argparse
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any, Callable

from scripts.manager.p2_27b_launch_preview import (
    MODEL, SERVED, HOST_PORT, TOOL_CALLING_ARGS,
)

HOST = "http://127.0.0.1:8000"
MAX_RESPONSE_BYTES = 65536


def profile() -> dict[str, Any]:
    return {
        "schema_version": 1, "action": "P2_FINAL_27B_TOOL_CALLING_PROFILE",
        "status": "SOURCE_PROFILE_ONLY_DGX_NOT_QUALIFIED",
        "model_repo": MODEL, "api_model_id": SERVED,
        "vllm_version_policy": "0.32",
        "flags": list(TOOL_CALLING_ARGS),
        "api_port": HOST_PORT,
        "container_recreated": False, "executed": False,
        "production_enabled": False,
        "requirements": [
            "verify_preserved_27b_container_config_cmd_read_only",
            "independent_tool_profile_migration_and_rollback_plan",
            "separate_approved_model_downtime",
            "live_tool_choice_auto_structured_call",
            "tool_result_continuation",
            "tool_streaming_and_reasoning_separation",
            "openwebui_native_tool_calling_acceptance",
        ],
        "notice": "No Docker changes. Historical P2/P3 receipts and existing "
                  "27B container are immutable. Flags are candidate only until "
                  "a separately approved live DGX parser and tool cycle passes.",
    }


def _read_json(opener: Callable[..., Any], request: Request, *,
               timeout: int) -> dict[str, Any]:
    with opener(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError("HTTP_STATUS_NOT_200")
        raw = response.read(MAX_RESPONSE_BYTES + 1)
        if not raw or len(raw) > MAX_RESPONSE_BYTES:
            raise ValueError("INVALID_RESPONSE_SIZE")
        data = json.loads(raw)
        if not isinstance(data, dict):
            raise ValueError("JSON_RESPONSE_NOT_OBJECT")
        return data


def _post(opener, messages: list[dict], tools: list[dict]) -> dict:
    payload = {
        "model": SERVED, "messages": messages, "tools": tools,
        "tool_choice": "auto", "temperature": 0,
        "max_tokens": 256, "stream": False,
        "chat_template_kwargs": {"enable_thinking": False},
    }
    return _read_json(opener, Request(
        HOST + "/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"}, method="POST",
    ), timeout=90)


def probe(*, opener: Callable[..., Any] = urlopen) -> dict[str, Any]:
    """Bounded benign local tool-call/continuation probe. No tool is executed."""
    report = {
        "schema_version": 1, "status": "BLOCKED",
        "scope": "P2_27B_LOCAL_API_TOOL_CALLING_PROBE",
        "executed": False, "api_model_id": SERVED,
        "parser_flags_observed": False,
        "structured_tool_call": False,
        "tool_result_continuation": False,
        "reasoning_separation": False,
        "issues": [],
    }
    try:
        ids = _read_json(opener, Request(HOST + "/v1/models", method="GET"),
                         timeout=10).get("data")
        actual = ([entry.get("id") for entry in ids]
                  if isinstance(ids, list) else [])
        if actual != [SERVED]:
            report["issues"].append("ACTIVE_27B_SOLE_MODEL_ID_NOT_VERIFIED")
            return report
        tools = [{
            "type": "function", "function": {
                "name": "get_probe_token",
                "description": "Return a test token for a named key. No external action.",
                "parameters": {
                    "type": "object",
                    "properties": {"key": {"type": "string"}},
                    "required": ["key"], "additionalProperties": False,
                },
            },
        }]
        messages = [
            {"role": "system",
             "content": "For this test, call get_probe_token with key=test "
                        "before answering. Never invent a token."},
            {"role": "user",
             "content": "Use get_probe_token for key test, then tell me the result."},
        ]
        first = _post(opener, messages, tools)
        if first.get("model") != SERVED:
            report["issues"].append("FIRST_RESPONSE_MODEL_ID_MISMATCH")
            return report
        choices = first.get("choices")
        if not isinstance(choices, list) or len(choices) != 1:
            report["issues"].append("FIRST_RESPONSE_CHOICES_UNVERIFIED")
            return report
        assistant = choices[0].get("message") or {}
        calls = assistant.get("tool_calls")
        if not isinstance(calls, list) or len(calls) != 1:
            report["issues"].append("AUTO_TOOL_CALL_NOT_STRUCTURED")
            return report
        call = calls[0]
        func = call.get("function") or {}
        if (call.get("type") != "function" or func.get("name") != "get_probe_token"
                or not isinstance(call.get("id"), str) or not call["id"]):
            report["issues"].append("TOOL_NAME_ID_UNVERIFIED")
            return report
        args = json.loads(func.get("arguments") or "")
        if not isinstance(args, dict) or args != {"key": "test"}:
            report["issues"].append("TOOL_ARGUMENTS_UNVERIFIED")
            return report
        report["structured_tool_call"] = True
        # No action on host: this reply is fixed test data, not an executed tool.
        messages.extend([
            {"role": "assistant", "content": assistant.get("content"),
             "tool_calls": calls},
            {"role": "tool", "tool_call_id": call["id"],
             "content": "DGX_TOOL_PROBE_OK"},
        ])
        last = _post(opener, messages, tools)
        if last.get("model") != SERVED:
            report["issues"].append("CONTINUATION_MODEL_ID_MISMATCH")
            return report
        second_choices = last.get("choices")
        if not isinstance(second_choices, list) or len(second_choices) != 1:
            report["issues"].append("CONTINUATION_CHOICES_UNVERIFIED")
            return report
        message = second_choices[0].get("message") or {}
        answer = message.get("content")
        report["tool_result_continuation"] = (
            isinstance(answer, str) and "DGX_TOOL_PROBE_OK" in answer
            and not message.get("tool_calls"))
        report["reasoning_separation"] = (
            isinstance(answer, str)
            and "<think" not in answer and "</think>" not in answer)
        if not report["tool_result_continuation"]:
            report["issues"].append("TOOL_RESULT_CONTINUATION_UNVERIFIED")
        if not report["reasoning_separation"]:
            report["issues"].append("REASONING_MARKUP_IN_FINAL_CONTENT")
        if not report["issues"]:
            report["status"] = "LOCAL_STRUCTURED_TOOL_CYCLE_PASS"
        return report
    except HTTPError as exc:
        report["issues"].append("LOCAL_API_HTTP_ERROR_" + str(exc.code))
    except (URLError, OSError, RuntimeError, ValueError, TypeError, KeyError,
            IndexError, TimeoutError, json.JSONDecodeError) as exc:
        report["issues"].append("LOCAL_TOOL_PROBE_UNAVAILABLE:"
                                + type(exc).__name__)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="P2 pinned 27B read-only tool profile and bounded local API test")
    parser.add_argument("action", choices=("profile", "probe"), nargs="?",
                        default="profile")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = profile() if args.action == "profile" else probe()
    print(json.dumps(result, indent=2, sort_keys=True))
    return (0 if result["status"] in (
        "SOURCE_PROFILE_ONLY_DGX_NOT_QUALIFIED",
        "LOCAL_STRUCTURED_TOOL_CYCLE_PASS") else 3)


if __name__ == "__main__":
    raise SystemExit(main())
