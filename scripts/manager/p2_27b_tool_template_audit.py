"""CPU-only diagnostic of the pinned NVIDIA 27B tool chat template.

Uses docker exec inside the EXISTING, running 27B container only to import the
installed tokenizer and render synthetic prompts. Never starts/stops Docker,
modifies files, loads model weights, launches GPU inference or makes API calls.
This does NOT qualify an actual tool-enabled runtime or grant downtime consent.
"""
from __future__ import annotations

import json
import subprocess
from typing import Any, Callable

from scripts.manager.p2_27b_tool_variant import (
    SOURCE_CONTAINER, TOOL_CHAT_TEMPLATE, VARIANT_ID,
)

# Executed inside the existing running container with -B and HF offline.
# Avoid printing any prompt bodies or private tokenizer contents.
CPU_PROBE = r'''
import hashlib
import importlib.metadata
import json
from pathlib import Path

template_path = Path("__TEMPLATE_PATH__")
r = {
    "kind": "P2_FINAL_PINNED_TEMPLATE_CPU_ONLY",
    "template_present": template_path.is_file(),
    "tokenizer_auto_template_present": False,
    "tool_prompt_rendered": False,
    "tool_result_rendered": False,
    "non_tool_prompt_rendered": False,
    "no_thinking_rendered": False,
    "issues": [],
}
try:
    if not r["template_present"]:
        raise ValueError("PINNED_CHAT_TEMPLATE_FILE_MISSING")
    source = template_path.read_text(encoding="utf-8")
    if not 1000 <= len(source.encode("utf-8")) <= 100000:
        raise ValueError("PINNED_CHAT_TEMPLATE_SIZE_UNEXPECTED")
    r["template_sha256"] = hashlib.sha256(source.encode("utf-8")).hexdigest()
    for marker in ("<tool_call>", "<function=", "<parameter=",
                   "<tool_response>", "enable_thinking"):
        if marker not in source:
            r["issues"].append("TEMPLATE_MARKER_MISSING_" +
                               marker.replace("<", "").replace(">", ""))
    from transformers import AutoTokenizer
    r["transformers_version"] = importlib.metadata.version("transformers")
    tok = AutoTokenizer.from_pretrained(
        str(template_path.parent), local_files_only=True,
        trust_remote_code=False, use_fast=True,
    )
    existing = getattr(tok, "chat_template", None)
    r["tokenizer_auto_template_present"] = bool(existing)
    # Test the EXACT pinned template even if the tokenizer ignored the
    # standalone .jinja file. Do not mutate the actual model snapshot.
    tok.chat_template = source
    tools = [{
        "type": "function",
        "function": {
            "name": "get_probe_token",
            "description": "Return a synthetic probe token",
            "parameters": {
                "type": "object",
                "properties": {"key": {"type": "string"}},
                "required": ["key"],
            },
        },
    }]
    msgs = [{"role": "user", "content": "Use get_probe_token for key test."}]
    prompted = tok.apply_chat_template(
        msgs, tools=tools, add_generation_prompt=True,
        tokenize=False, enable_thinking=False,
    )
    r["tool_prompt_rendered"] = (
        "get_probe_token" in prompted and
        "<tool_call>" in prompted and
        "<|im_start|>assistant" in prompted
    )
    # enable_thinking=False should NOT inject reasoning markup into the
    # assistant-generation prefix. An empty <think> block is not mandatory.
    r["no_thinking_rendered"] = (
        "<think>" not in prompted and "</think>" not in prompted
    )
    ordinary = tok.apply_chat_template(
        [{"role": "user", "content": "Say hello."}],
        add_generation_prompt=True, tokenize=False,
        enable_thinking=False,
    )
    r["non_tool_prompt_rendered"] = (
        "Say hello." in ordinary and "<|im_start|>assistant" in ordinary
    )
    cycle = msgs + [
        {"role": "assistant", "content": "",
         "tool_calls": [{"type": "function", "function": {
             "name": "get_probe_token", "arguments": {"key": "test"}}]},
        {"role": "tool", "tool_call_id": "synthetic-only",
         "content": "PROBE_TOKEN"},
    ]
    continued = tok.apply_chat_template(
        cycle, tools=tools, add_generation_prompt=True,
        tokenize=False, enable_thinking=False,
    )
    r["tool_result_rendered"] = (
        "<tool_response>" in continued and
        "PROBE_TOKEN" in continued and
        "<function=get_probe_token>" in continued
    )
    for key in ("tool_prompt_rendered", "no_thinking_rendered",
                "non_tool_prompt_rendered", "tool_result_rendered"):
        if not r[key]:
            r["issues"].append("TEMPLATE_RENDER_FAILED_" + key.upper())
except Exception as exc:
    r["issues"].append("CPU_RENDER_ERROR_" + type(exc).__name__)
    r["error_summary"] = str(exc)[:280]
r["status"] = ("CPU_TEMPLATE_RENDER_VALIDATED_ONLY"
               if not r["issues"] else "BLOCKED")
print(json.dumps(r, ensure_ascii=False, sort_keys=True))
'''.replace("__TEMPLATE_PATH__", TOOL_CHAT_TEMPLATE)


def _stderr_hint(stderr: str | None) -> str | None:
    """Short, redacted last error line; never copy full tracebacks to JSON."""
    if not isinstance(stderr, str):
        return None
    import re
    lines = [line.strip() for line in stderr.splitlines() if line.strip()]
    if not lines:
        return None
    last = lines[-1]
    last = re.sub(r"/home/[^/\s]+", "/home/<redacted>", last)
    last = re.sub(r"(?i)(token|api[_-]?key|authorization)\s*[:=]\s*[^,\s]+",
                  r"\1=<redacted>", last)
    return last[:360]


def _structured_stdout(stdout: str | None) -> dict[str, Any] | None:
    """Accept single-line structured JSON, optionally after library log noise."""
    if not isinstance(stdout, str) or not stdout or len(stdout) > 16384:
        return None
    candidates = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not candidates:
        return None
    try:
        result = json.loads(candidates[-1])
    except (json.JSONDecodeError, ValueError):
        return None
    return result if isinstance(result, dict) else None


def inspect_template_cpu(
    *, run: Callable[..., Any] = subprocess.run,
) -> dict[str, Any]:
    """One bounded, read-only docker-exec CPU prompt-render experiment."""
    report: dict[str, Any] = {
        "schema_version": 1, "action": "P2_FINAL_TEMPLATE_CPU_ONLY",
        "status": "BLOCKED", "variant_id": VARIANT_ID,
        "original_container": SOURCE_CONTAINER,
        "template_path": TOOL_CHAT_TEMPLATE,
        "docker_state_mutated": False, "gpu_inference_executed": False,
        "execution_enabled": False, "approval_accepted": False,
        "plan_id": None, "issues": [],
    }
    command = [
        "docker", "exec", "-i",
        "-e", "PYTHONDONTWRITEBYTECODE=1",
        "-e", "HF_HUB_OFFLINE=1",
        "-e", "TRANSFORMERS_OFFLINE=1",
        "-e", "CUDA_VISIBLE_DEVICES=-1",
        "-e", "TOKENIZERS_PARALLELISM=false",
        SOURCE_CONTAINER, "python3", "-B", "-",
    ]
    try:
        result = run(command, input=CPU_PROBE, text=True,
                     capture_output=True, timeout=90, check=False)
        if result.returncode:
            report["issues"].append("DOCKER_EXEC_CPU_PROBE_NONZERO_EXIT")
            report["docker_exec_returncode"] = result.returncode
            hint = _stderr_hint(getattr(result, "stderr", None))
            if hint:
                report["docker_exec_stderr_last_line"] = hint
            data = _structured_stdout(getattr(result, "stdout", None))
            if data is not None:
                report["inner_probe_status"] = data.get("status")
                report["inner_probe_issues"] = data.get("issues", [])
                if data.get("error_summary"):
                    report["inner_error_summary"] = str(data["error_summary"])[:360]
            return report
        data = _structured_stdout(getattr(result, "stdout", None))
        if data is None:
            report["issues"].append("CPU_PROBE_RESPONSE_INVALID_OR_NON_JSON")
            hint = _stderr_hint(getattr(result, "stderr", None))
            if hint:
                report["docker_exec_stderr_last_line"] = hint
            return report
        for key in ("template_present", "tokenizer_auto_template_present",
                    "template_sha256", "transformers_version",
                    "tool_prompt_rendered", "tool_result_rendered",
                    "no_thinking_rendered", "non_tool_prompt_rendered"):
            if key in data:
                report[key] = data[key]
        reported_issues = data.get("issues")
        if not isinstance(reported_issues, list) or any(
            not isinstance(i, str) for i in reported_issues
        ):
            raise ValueError("CPU_PROBE_ISSUES_INVALID")
        report["issues"].extend(reported_issues)
        if data.get("error_summary"):
            report["inner_error_summary"] = str(data["error_summary"])[:360]
        if data.get("status") != "CPU_TEMPLATE_RENDER_VALIDATED_ONLY":
            report["issues"].append("CPU_TEMPLATE_NOT_VALIDATED")
        if not report["issues"]:
            report["status"] = "CPU_TEMPLATE_RENDER_VALIDATED_ONLY"
    except subprocess.TimeoutExpired:
        report["issues"].append("DOCKER_EXEC_CPU_PROBE_TIMEOUT")
    except (OSError, ValueError, RuntimeError, TypeError,
            json.JSONDecodeError) as exc:
        report["issues"].append("CPU_TEMPLATE_AUDIT_UNAVAILABLE_" +
                                type(exc).__name__)
    return report


def main() -> int:
    result = inspect_template_cpu()
    print(json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True))
    # A CPU-only PASS never authorizes production service modification.
    return 0 if result["status"] == "CPU_TEMPLATE_RENDER_VALIDATED_ONLY" else 3


if __name__ == "__main__":
    raise SystemExit(main())
