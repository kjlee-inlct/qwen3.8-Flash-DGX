"""Bounded localhost SSE Native tool-call probe for an ALREADY running 27B.

The probe never launches/stops/reconfigures Docker and does not execute tools.
Successful SSE parsing is only one P2-FINAL acceptance gate, not WebUI PASS.
"""
from __future__ import annotations

import argparse
import json
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from scripts.manager.p2_27b_tool_calling import HOST, SERVED, _read_json

MAX_STREAM_BYTES = 196608
MAX_STREAM_EVENTS = 256


def evaluate_stream(lines: Any) -> dict[str, Any]:
    """Fail closed on malformed, truncated or unstructured SSE tool output."""
    issues: list[str] = []
    total_bytes = 0
    count = 0
    seen_done = False
    finish_reason = None
    call_id = ""
    call_type = ""
    name = ""
    arguments = ""
    answer_content = ""
    for raw in lines:
        if not isinstance(raw, bytes):
            issues.append("SSE_LINE_NOT_BYTES")
            break
        total_bytes += len(raw)
        if total_bytes > MAX_STREAM_BYTES or len(raw) > 65536:
            issues.append("SSE_RESPONSE_TOO_LARGE")
            break
        line = raw.strip()
        if not line or line.startswith(b":"):
            continue
        if not line.startswith(b"data:"):
            issues.append("INVALID_SSE_PREFIX")
            break
        data = line[5:].strip()
        if data == b"[DONE]":
            seen_done = True
            break
        count += 1
        if count > MAX_STREAM_EVENTS:
            issues.append("TOO_MANY_STREAM_EVENTS")
            break
        try:
            event = json.loads(data)
            if not isinstance(event, dict) or event.get("model") != SERVED:
                raise ValueError("SSE_MODEL_MISMATCH")
            choices = event.get("choices")
            if not isinstance(choices, list) or len(choices) != 1:
                raise ValueError("SSE_CHOICE_MISMATCH")
            choice = choices[0]
            if not isinstance(choice, dict):
                raise ValueError("SSE_CHOICE_NOT_OBJECT")
            if finish_reason is not None:
                raise ValueError("CHUNKS_AFTER_FINISH")
            delta = choice.get("delta") or {}
            if not isinstance(delta, dict):
                raise ValueError("SSE_DELTA_NOT_OBJECT")
            content = delta.get("content")
            if content is not None:
                if not isinstance(content, str):
                    raise ValueError("SSE_CONTENT_NOT_TEXT")
                answer_content += content
            tool_calls = delta.get("tool_calls") or []
            if not isinstance(tool_calls, list):
                raise ValueError("SSE_TOOLS_NOT_LIST")
            for call in tool_calls:
                if not isinstance(call, dict) or call.get("index") != 0:
                    raise ValueError("SSE_TOOL_INDEX_UNVERIFIED")
                frag_id = call.get("id", "")
                frag_type = call.get("type", "")
                func = call.get("function") or {}
                if (not isinstance(frag_id, str) or not isinstance(frag_type, str)
                        or not isinstance(func, dict)):
                    raise ValueError("SSE_TOOL_FIELD_TYPE_UNVERIFIED")
                call_id += frag_id
                call_type += frag_type
                for field in ("name", "arguments"):
                    fragment = func.get(field, "")
                    if not isinstance(fragment, str):
                        raise ValueError("SSE_FUNCTION_FIELD_NOT_TEXT")
                    if field == "name":
                        name += fragment
                    else:
                        arguments += fragment
            if choice.get("finish_reason") is not None:
                finish_reason = choice["finish_reason"]
        except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
            issues.append("MALFORMED_SSE_EVENT:" + str(exc)[:80])
            break
    if not seen_done:
        issues.append("SSE_DONE_MISSING")
    if count == 0:
        issues.append("SSE_NO_EVENTS")
    if finish_reason != "tool_calls":
        issues.append("SSE_TOOL_FINISH_REASON_MISSING")
    if not call_id or call_type != "function" or name != "get_probe_token":
        issues.append("SSE_STRUCTURED_TOOL_ID_OR_NAME_MISMATCH")
    try:
        args = json.loads(arguments)
        if args != {"key": "test"}:
            issues.append("SSE_TOOL_ARGUMENTS_INVALID")
    except (ValueError, TypeError):
        issues.append("SSE_TOOL_ARGUMENTS_INVALID")
    if "<think" in answer_content or "</think>" in answer_content:
        issues.append("SSE_REASONING_LEAKED_IN_FINAL_CONTENT")
    issues = sorted(set(issues))
    return {
        "status": "LOCAL_STREAMED_TOOL_CALL_PASS" if not issues else "BLOCKED",
        "issues": issues,
        "streamed_tool_call": not issues,
        "reasoning_separation": not issues,
        "stream_event_count": count,
        "executed_tool": False,
    }


def probe_stream(*, opener: Callable[..., Any] = urlopen) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema_version": 1, "status": "BLOCKED",
        "scope": "LOCAL_27B_SSE_TOOL_CALL_NO_DOCKER_CHANGE",
        "api_model_id": SERVED,
        "streamed_tool_call": False, "reasoning_separation": False,
        "executed_tool": False, "issues": [],
    }
    try:
        ids = _read_json(opener, Request(HOST + "/v1/models", method="GET"),
                         timeout=10).get("data")
        if not isinstance(ids, list) or [x.get("id") for x in ids] != [SERVED]:
            report["issues"].append("ACTIVE_27B_SOLE_MODEL_ID_NOT_VERIFIED")
            return report
        payload = {
            "model": SERVED,
            "messages": [
                {"role": "system",
                 "content": "Call get_probe_token with key=test before answering."},
                {"role": "user", "content": "Call get_probe_token for key test."},
            ],
            "tools": [{
                "type": "function",
                "function": {
                    "name": "get_probe_token",
                    "description": "Return a fixed safe token for a key.",
                    "parameters": {
                        "type": "object",
                        "properties": {"key": {"type": "string"}},
                        "required": ["key"],
                        "additionalProperties": False,
                    },
                },
            }],
            "tool_choice": "auto",
            "stream": True, "temperature": 0, "max_tokens": 256,
            "chat_template_kwargs": {"enable_thinking": False},
        }
        req = Request(
            HOST + "/v1/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST",
        )
        with opener(req, timeout=90) as response:
            if response.status != 200:
                raise ValueError("SSE_HTTP_STATUS_NOT_200")
            outcome = evaluate_stream(response)
        report.update(outcome)
    except HTTPError as exc:
        report["issues"] = ["LOCAL_STREAM_HTTP_ERROR_" + str(exc.code)]
    except (URLError, OSError, RuntimeError, ValueError, TypeError, KeyError,
            TimeoutError, json.JSONDecodeError) as exc:
        report["issues"] = ["LOCAL_STREAM_PROBE_UNAVAILABLE:" + type(exc).__name__]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded 27B local SSE tools probe")
    parser.add_argument("--json", action="store_true")
    parser.parse_args()
    report = probe_stream()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "LOCAL_STREAMED_TOOL_CALL_PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
