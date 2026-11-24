#!/usr/bin/env python3
"""Bounded, single-stream local vLLM baseline benchmark (stdlib only).

No request is sent without an explicit Wizard execute approval. Record measured
values only; absent server usage stays null (never guessed from text length).
"""
from __future__ import annotations

import hashlib
import json
import statistics
import time
from typing import Any, Callable
from urllib.request import Request, urlopen

PROMPTS = (
    "Reply in one short sentence: why should a power rail be decoupled? /no_think",
    "State one benefit of a hardware watchdog in embedded systems. /no_think",
    "Explain in one sentence what an FPGA timing slack indicates. /no_think",
)
CLIENT_VERSION = "p1-wizard-baseline-v2"


def http_json(url: str, method: str = "GET", payload: dict | None = None,
              timeout: float = 30.0, opener: Callable[..., Any] = urlopen) -> dict:
    body = json.dumps(payload, separators=(",", ":")).encode() if payload is not None else None
    request = Request(url, data=body, method=method,
                      headers={"Content-Type": "application/json"} if body else {})
    with opener(request, timeout=timeout) as response:
        content = response.read(1024 * 1024 + 1)
        if len(content) > 1024 * 1024:
            raise ValueError("HTTP JSON response exceeds 1 MiB")
        obj = json.loads(content)
        if not isinstance(obj, dict):
            raise ValueError("HTTP response must be an object")
        return obj


def require_model(api_base: str, expected: str,
                  opener: Callable[..., Any] = urlopen) -> dict:
    if api_base != "http://127.0.0.1:8000":
        raise ValueError("only local P1 endpoint is allowed")
    health = Request(api_base + "/health", method="GET")
    with opener(health, timeout=5) as response:
        if response.status != 200:
            raise ValueError("health_failed")
    models = http_json(api_base + "/v1/models", timeout=5, opener=opener)
    ids = [x.get("id") for x in models.get("data", []) if isinstance(x, dict)]
    if expected not in ids:
        raise ValueError("served_model_id_mismatch")
    return {"health": "PASS", "models": sorted(x for x in ids if isinstance(x, str))}


def _percentile(values: list[float], quantile: float) -> float:
    xs = sorted(values)
    if len(xs) == 1:
        return round(xs[0], 6)
    pos = (len(xs) - 1) * quantile
    lo = int(pos)
    f = pos - lo
    return round(xs[lo] * (1 - f) + xs[min(lo + 1, len(xs) - 1)] * f, 6)


def run_benchmark(api_base: str, model: str, *, requests: int = 3,
                  max_tokens: int = 64, seed: int = 1234,
                  opener: Callable[..., Any] = urlopen,
                  clock: Callable[[], float] = time.perf_counter) -> dict[str, Any]:
    if api_base != "http://127.0.0.1:8000":
        raise ValueError("benchmark limited to local port 8000")
    if not 1 <= requests <= 20 or not 1 <= max_tokens <= 256 or not 0 <= seed <= 2**31 - 1:
        raise ValueError("unbounded benchmark parameters")
    samples: list[dict[str, Any]] = []
    for i in range(requests):
        prompt = PROMPTS[i % len(PROMPTS)]
        body = {
            "model": model, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0, "seed": seed, "max_tokens": max_tokens,
            "stream": True, "stream_options": {"include_usage": True},
        }
        req = Request(api_base + "/v1/chat/completions",
                      method="POST", data=json.dumps(body).encode("utf-8"),
                      headers={"Content-Type": "application/json"})
        start = clock()
        first = None
        usage = None
        text_seen = False
        with opener(req, timeout=120) as response:
            if response.status != 200:
                raise ValueError("benchmark HTTP non-200")
            for idx, raw in enumerate(response):
                if idx > 20000 or len(raw) > 256 * 1024:
                    raise ValueError("SSE response exceeds bounds")
                line = raw.decode("utf-8").strip()
                if not line.startswith("data:"):
                    continue
                content = line[5:].strip()
                if content == "[DONE]":
                    break
                obj = json.loads(content)
                if isinstance(obj.get("usage"), dict):
                    usage = obj["usage"]
                for choice in obj.get("choices", []):
                    delta = choice.get("delta", {})
                    if isinstance(delta, dict) and delta.get("content"):
                        text_seen = True
                        if first is None:
                            first = clock()
        done = clock()
        output_tokens = usage.get("completion_tokens") if usage else None
        if type(output_tokens) is not int or output_tokens < 0:
            output_tokens = None
        elapsed = max(done - start, 0)
        samples.append({
            "index": i, "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "latency_sec": round(elapsed, 6),
            "ttft_sec": round(first - start, 6) if first is not None else None,
            "completion_tokens": output_tokens,
            "text_seen": text_seen,
            "tokens_per_sec": (round(output_tokens / elapsed, 4)
                               if output_tokens is not None and elapsed > 0 else None),
        })
    lat = [s["latency_sec"] for s in samples]
    ttft = [s["ttft_sec"] for s in samples if s["ttft_sec"] is not None]
    tps = [s["tokens_per_sec"] for s in samples if s["tokens_per_sec"] is not None]
    complete = all(s["text_seen"] and s["completion_tokens"] is not None
                   and s["ttft_sec"] is not None for s in samples)
    return {
        "status": "PASS" if complete else "PARTIAL",
        "scope": "API/GPU", "client_version": CLIENT_VERSION,
        "requests": requests, "max_tokens": max_tokens, "seed": seed,
        "concurrency": 1, "samples": samples,
        "metrics": {
            "latency_p50_sec": _percentile(lat, .5),
            "latency_p95_sec": _percentile(lat, .95),
            "ttft_p50_sec": _percentile(ttft, .5) if ttft else None,
            "ttft_p95_sec": _percentile(ttft, .95) if ttft else None,
            "mean_tokens_per_sec": (round(statistics.mean(tps), 4) if len(tps) == requests else None),
            "total_completion_tokens": (sum(s["completion_tokens"] for s in samples)
                                        if all(s["completion_tokens"] is not None for s in samples) else None),
        },
    }
