"""Opt-in, bounded localhost benchmark for an already-active registered model.

No Docker mutations, downloads, switching, power/CPU controls or speculative
activation. Live inference is never run by plan, inventory, history or menu.
Only an exact acknowledgement enables synthetic requests against localhost:8000.
No generated content or prompts are retained in evidence files.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import math
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from scripts.manager.generic_operations import model_catalog
from scripts.manager.model_measurements import HEX64, _candidate_profile
from scripts.manager.resource_diagnostics import snapshot
from scripts.manager.service_status import inspect_live_status

ACK = "I_ACCEPT_ACTIVE_MODEL_INFERENCE"
API = "http://127.0.0.1:8000"
MAX_CONTEXT_K = 256
MAX_OUTPUT_TOKENS = 512
PROMPT_PATTERN = "The quick brown fox jumps over the lazy dog. "
MAX_PROMPT_CHARS = 3_000_000


def _contexts(raw):
    if not isinstance(raw, str) or not raw or len(raw) > 100:
        raise ValueError("INVALID_CONTEXT_LIST")
    parts = raw.split(",")
    if len(parts) > 8 or any(not x.strip().isdigit() for x in parts):
        raise ValueError("INVALID_CONTEXT_LIST")
    items = [int(x.strip()) for x in parts]
    if any(x < 1 or x > MAX_CONTEXT_K for x in items) or len(set(items)) != len(items):
        raise ValueError("CONTEXT_LIST_OUT_OF_RANGE_OR_DUPLICATED")
    return items


def _settings(model, contexts_k, max_output_tokens):
    cat = model_catalog()
    if model not in cat["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    contexts = _contexts(contexts_k)
    if (not isinstance(max_output_tokens, int) or isinstance(max_output_tokens, bool)
            or not 1 <= max_output_tokens <= MAX_OUTPUT_TOKENS):
        raise ValueError("OUTPUT_TOKENS_OUT_OF_RANGE")
    return cat["models"][model], contexts, max_output_tokens


def benchmark_plan(model, *, contexts_k="1,4,8", max_output_tokens=128):
    spec, contexts, output = _settings(model, contexts_k, max_output_tokens)
    return {
        "schema_version": 1, "action": "benchmark-plan",
        "model": model, "identity": spec, "profile": _candidate_profile(model),
        "status": "PLAN_ONLY_ACK_REQUIRED",
        "requested_context_k": contexts, "max_output_tokens": output,
        "repeat_count": 1, "concurrency": 1, "backend": "active-openai-chat-api",
        "api": API + "/v1", "requires_exact_ack": ACK,
        "requires_model_id_and_docker_identity": True,
        "requires_server_tokenization": True,
        "server_limit_enforced": True, "uses_synthetic_prompt_only": True,
        "supports_reasoning_first_visible_content_separation": True,
        "inference_executed": False, "service_mutated": False,
        "production_released": False,
        "note": "Explicit benchmark-execute acknowledgement is mandatory. No model restart, switch, or file writes in this plan.",
    }


def _json_request(path, *, payload=None, timeout=12):
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
    req = Request(API + path, data=body,
                  headers={"Content-Type": "application/json", "Accept": "application/json"},
                  method="POST" if body is not None else "GET")
    with urlopen(req, timeout=timeout) as response:
        data = response.read(12_000_000 + 1)
    if len(data) > 12_000_000:
        raise ValueError("API_RESPONSE_TOO_LARGE")
    return json.loads(data)


def _token_count(model, prompt):
    result = _json_request("/tokenize", payload={"model": model, "prompt": prompt}, timeout=30)
    count = result.get("count")
    if isinstance(count, int) and not isinstance(count, bool) and count >= 0:
        return count
    tokens = result.get("tokens")
    if isinstance(tokens, list):
        return len(tokens)
    raise ValueError("TOKENIZER_COUNT_NOT_RETURNED")


def _synthetic_prompt(model, target_tokens):
    """Iteratively size deterministic text; report actual tokenizer count."""
    count_per_phrase = _token_count(model, PROMPT_PATTERN * 20)
    if count_per_phrase < 1:
        raise ValueError("TOKENIZER_UNAVAILABLE")
    repeats = max(1, round(target_tokens * 20 / count_per_phrase))
    for _ in range(4):
        prompt = PROMPT_PATTERN * repeats
        if len(prompt) > MAX_PROMPT_CHARS:
            raise ValueError("PROMPT_CHAR_BUDGET_EXCEEDED")
        count = _token_count(model, prompt)
        if count <= 0:
            raise ValueError("TOKENIZER_ZERO_COUNT")
        if abs(count - target_tokens) / target_tokens <= 0.03:
            return prompt, count
        repeats = max(1, round(repeats * target_tokens / count))
    prompt = PROMPT_PATTERN * repeats
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError("PROMPT_CHAR_BUDGET_EXCEEDED")
    return prompt, _token_count(model, prompt)


def _stream_chat(model, prompt, output):
    """SSE: first emitted token may be reasoning; TTFC needs delta.content."""
    payload = {
        "model": model, "messages": [{"role": "user", "content": prompt}],
        "stream": True, "stream_options": {"include_usage": True},
        "max_tokens": output, "temperature": 0,
    }
    req = Request(API + "/v1/chat/completions",
                  data=json.dumps(payload, separators=(",", ":")).encode("utf-8"),
                  headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
                  method="POST")
    start = time.perf_counter()
    first_token = first_visible = None
    output_chars = 0
    usage = {}
    completion = None
    finish_reason = None
    received_done = False
    with urlopen(req, timeout=180) as response:
        for raw in response:
            if len(raw) > 1_000_000:
                raise ValueError("SSE_LINE_TOO_LARGE")
            line = raw.decode("utf-8", "replace").strip()
            if not line.startswith("data:"):
                continue
            content = line[5:].strip()
            if content == "[DONE]":
                received_done = True
                break
            try:
                item = json.loads(content)
            except json.JSONDecodeError:
                continue
            if not isinstance(item, dict):
                continue
            if isinstance(item.get("usage"), dict):
                usage = item["usage"]
            for choice in item.get("choices") or []:
                delta = choice.get("delta") or {}
                visible = delta.get("content") or ""
                reasoning = delta.get("reasoning_content") or ""
                if (visible or reasoning) and first_token is None:
                    first_token = time.perf_counter() - start
                if visible and first_visible is None:
                    first_visible = time.perf_counter() - start
                if visible:
                    output_chars += len(visible)
                finish_reason = choice.get("finish_reason") or finish_reason
    elapsed = time.perf_counter() - start
    completion = usage.get("completion_tokens")
    requested_prompt_tokens = usage.get("prompt_tokens")
    if not isinstance(completion, int) or isinstance(completion, bool) or completion < 0:
        completion = None
    if not isinstance(requested_prompt_tokens, int) or isinstance(requested_prompt_tokens, bool):
        requested_prompt_tokens = None
    # The model's generated text is never retained; vLLM usage is the token source.
    tps = (completion / (elapsed - first_token)
           if completion is not None and first_token is not None
           and elapsed > first_token else None)
    return {
        "ttft_seconds": round(first_token, 5) if first_token is not None else None,
        "ttfc_seconds": round(first_visible, 5) if first_visible is not None else None,
        "end_to_end_seconds": round(elapsed, 5),
        "generation_tps_after_first_token": round(tps, 3) if tps is not None else None,
        "prompt_tokens_reported": requested_prompt_tokens,
        "completion_tokens_reported": completion,
        "visible_characters": output_chars, "finish_reason": finish_reason,
        "stream_done_observed": received_done, "response_content_saved": False,
        "token_count_source": "SSE_USAGE" if completion is not None else "NOT_OBSERVED",
    }


def _identity_gate(model, *, service_probe=inspect_live_status, capture=snapshot,
                   http=_json_request):
    spec = model_catalog()["models"][model]
    service = service_probe()
    if (service.get("observed_model") != model or
            service.get("status") not in ("LIVE_P5_TRIAL_API_VERIFIED", "LIVE_SERVICE_VERIFIED") or
            service.get("expected_served_id") != spec["served_id"] or
            service.get("issues")):
        raise ValueError("ACTIVE_SERVICE_MODEL_IDENTITY_NOT_VERIFIED")
    resources = capture(model=model)
    container = (resources.get("docker") or {}).get("container") or {}
    if (resources.get("docker", {}).get("status") != "OBSERVED"
            or not isinstance(container.get("id"), str) or
            not HEX64.fullmatch(container["id"])
            or not container.get("running")):
        raise ValueError("TARGET_DOCKER_IDENTITY_NOT_OBSERVED")
    response = http("/v1/models")
    models = response.get("data")
    valid = [x for x in models if isinstance(x, dict) and x.get("id") == spec["served_id"]] if isinstance(models, list) else []
    if len(valid) != 1:
        raise ValueError("API_MODEL_IDENTITY_MISMATCH")
    max_len = valid[0].get("max_model_len")
    if not isinstance(max_len, int) or isinstance(max_len, bool) or max_len < 256:
        raise ValueError("ACTIVE_MAX_MODEL_LEN_NOT_OBSERVED")
    return spec, resources, container, max_len


def benchmark_execute(model, *, contexts_k="1,4,8", max_output_tokens=128,
                      ack=None, identity_gate=_identity_gate,
                      chat=_stream_chat, tokenize=_synthetic_prompt,
                      capture=snapshot):
    """Only explicit exact ack generates inference; all errors are fail-closed."""
    spec, contexts, output = _settings(model, contexts_k, max_output_tokens)
    plan = benchmark_plan(model, contexts_k=contexts_k, max_output_tokens=output)
    if ack != ACK:
        return {**plan, "action": "benchmark-execute", "status": "BLOCKED",
                "issues": ["EXACT_LIVE_INFERENCE_ACK_REQUIRED"],
                "inference_executed": False}
    identity, before, container, max_len = identity_gate(model)
    start = datetime.now(timezone.utc).isoformat()
    results = []
    inference_executed = False
    for context in contexts:
        target = context * 1024
        if target + output > max_len:
            results.append({"context_k": context, "requested_input_tokens": target,
                            "status": "SKIPPED_ACTIVE_CONTEXT_LIMIT",
                            "active_max_model_len": max_len})
            continue
        try:
            prompt, token_count = tokenize(identity["served_id"], target)
            if abs(token_count - target) / target > 0.05 or token_count + output > max_len:
                results.append({"context_k": context, "requested_input_tokens": target,
                                "tokenizer_input_tokens": token_count,
                                "status": "SKIPPED_TOKENIZATION_MISMATCH_OR_CONTEXT_LIMIT"})
                continue
            inference_executed = True
            sample = chat(identity["served_id"], prompt, output)
            results.append({
                "context_k": context, "requested_input_tokens": target,
                "tokenizer_input_tokens": token_count,
                "status": "MEASURED" if sample.get("stream_done_observed") else "INCOMPLETE_STREAM",
                "metrics": sample,
            })
        except (ValueError, TimeoutError, URLError, HTTPError, OSError) as exc:
            results.append({"context_k": context, "requested_input_tokens": target,
                            "status": "INCOMPLETE_BENCHMARK_CASE",
                            "error_type": type(exc).__name__})
            break
    after = capture(model=model)
    after_id = ((after.get("docker") or {}).get("container") or {}).get("id")
    stable = after_id == container["id"] and after.get("model") == model
    # Even a complete sample is not independently qualified loaded runtime proof.
    measured = [x for x in results if x["status"] == "MEASURED"]
    return {
        "schema_version": 1, "action": "benchmark-execute",
        "status": ("COLLECTED_UNQUALIFIED" if measured and stable and
                   all(x["status"] in ("MEASURED", "SKIPPED_ACTIVE_CONTEXT_LIMIT") for x in results)
                   else "INCOMPLETE_MEASUREMENT"),
        "model": model, "identity": spec, "container": container,
        "timestamp_utc": start, "ended_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": before.get("git_head"),
        "profile": _candidate_profile(model),
        "active_max_model_len": max_len,
        "requested_context_k": contexts, "max_output_tokens": output,
        "concurrency": 1, "repeat_count": 1,
        "results": results,
        "summary": {"measured_cases": len(measured),
                    "requested_cases": len(contexts),
                    "container_id_continuous": stable},
        "resource_snapshots": [before, after],
        "inference_executed": inference_executed, "service_mutated": False,
        "approval_accepted_for_inference_only": True,
        "benchmark_verified": False, "production_released": False,
        "raw_prompts_or_generated_text_saved": False,
        "note": "SSE TTFT includes reasoning deltas; TTFC is first visible content. TPS requires server token usage. No release or live provenance acceptance.",
    }
