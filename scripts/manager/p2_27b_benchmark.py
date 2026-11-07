"""Bounded, separately approved P2 benchmark while NVIDIA 27B is serving.

The existing GPU trial owns ALL model lifecycle and original-container recovery.
This module only plans a distinct benchmark approval and invokes that proven
executor with a bounded HTTP measurement callback. No implicit service change.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import statistics
import subprocess
import time
from typing import Any, Callable
from urllib.request import Request, urlopen

from scripts.manager import p2_27b_gpu_trial as trial
from scripts.manager.service_status import inspect_live_status

VERSION = "p2-27b-api-benchmark-v1"
REQUEST_COUNT = 3
MAX_TOKENS = 64
SEED = 1234
ACK = trial.ACK
PROMPTS = (
    "Explain briefly what a hardware watchdog does. /no_think",
    "In one sentence, describe FPGA timing slack. /no_think",
    "State the purpose of power-supply decoupling. /no_think",
)


def make_plan(*, trial_planner=trial.make_plan) -> dict[str, Any]:
    base = trial_planner()
    result = dict(base)
    profile = {"version": VERSION, "requests": REQUEST_COUNT,
               "max_tokens": MAX_TOKENS, "seed": SEED, "concurrency": 1,
               "model": trial.SERVED, "stream": True}
    result["action"] = "Qwen3.8-27B-bounded-benchmark-and-original-restore"
    result["benchmark_profile"] = profile
    result["plan_id"] = None
    if base.get("status") == "READY_TO_REQUEST_TRIAL_APPROVAL":
        original_plan = base.get("plan_id")
        if isinstance(original_plan, str) and len(original_plan) == 64:
            bound = json.dumps({"kind": "BENCHMARK_NOT_SMOKE",
                                "trial_plan": original_plan, "profile": profile},
                               sort_keys=True, separators=(",", ":"))
            result["plan_id"] = hashlib.sha256(bound.encode()).hexdigest()
        else:
            result["status"] = "BLOCKED"
            result["issues"] = list(result.get("issues", [])) + ["TRIAL_PLAN_UNAVAILABLE"]
    result["notice"] = ("Requires NEW benchmark-specific plan and explicit Flash-Next downtime "
                        "ack. Stops original, runs bounded 27B benchmark, then attempts "
                        "restore of the exact preserved original container. "
                        "Power loss/Docker failure may defeat auto-restore.")
    return result


def _percentile(xs, q):
    if not xs:
        return None
    arr = sorted(xs)
    position = (len(arr) - 1) * q
    low = int(position)
    return round(arr[low] + (arr[min(low + 1, len(arr)-1)]-arr[low]) *
                 (position-low), 6)


def memory_snapshot(*, run=trial.call) -> dict[str, Any]:
    # DGX GB10 unified memory counters may show N/A: never claim a GPU peak.
    empty = {"status": "UNAVAILABLE", "used_mib": None, "total_mib": None}
    try:
        response = run(["nvidia-smi", "--query-gpu=memory.used,memory.total",
                        "--format=csv,noheader,nounits"], timeout=10)
        if response.returncode:
            return empty
        lines = response.stdout.strip().splitlines()
        if len(lines) != 1:
            return empty
        used, total = [int(v.strip()) for v in lines[0].split(",")]
        if used < 0 or total < used or total == 0:
            return empty
        return {"status": "POINT_SAMPLE_NOT_PEAK",
                "used_mib": used, "total_mib": total}
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return empty


def _stream_sample(response, start, *, clock=time.perf_counter):
    first_token = None
    usage = None
    generated = False
    done = False
    finish_reason = None
    content_observed = False
    reasoning_observed = False
    deadline = time.monotonic() + 180  # hard per-request ceiling, in addition to socket timeout
    for i, raw in enumerate(response):
        if time.monotonic() > deadline:
            raise TimeoutError("BENCHMARK_REQUEST_DEADLINE_EXCEEDED")
        if i >= 20000 or not isinstance(raw, bytes) or len(raw) > 262144:
            raise ValueError("SSE_BOUND_EXCEEDED")
        line = raw.decode("utf-8").strip()
        if not line.startswith("data:"):
            continue
        content = line[5:].strip()
        if content == "[DONE]":
            done = True
            break
        frame = json.loads(content)
        if not isinstance(frame, dict):
            raise ValueError("SSE_FRAME_INVALID")
        if isinstance(frame.get("usage"), dict):
            usage = frame["usage"]
        for choice in frame.get("choices", []):
            if not isinstance(choice, dict) or not isinstance(choice.get("delta"), dict):
                continue
            delta = choice["delta"]
            if choice.get("finish_reason") is not None:
                finish_reason = choice["finish_reason"]
            if isinstance(delta.get("content"), str) and delta["content"]:
                content_observed = True
            if (isinstance(delta.get("reasoning_content"), str)
                    and delta["reasoning_content"]):
                reasoning_observed = True
            if content_observed or reasoning_observed:
                generated = True
                if first_token is None:
                    first_token = clock()
    return {"first_token_at": first_token, "usage": usage,
            "stream_complete": done, "generated": generated,
            "finish_reason": finish_reason, "content_observed": content_observed,
            "reasoning_observed": reasoning_observed}


def measure(*, opener=urlopen, clock=time.perf_counter,
            memory_reader=memory_snapshot, identity=trial.api_ready,
            chat_template_kwargs: dict[str, Any] | None = None) -> dict[str, Any]:
    if identity(trial.SERVED) is not True:
        raise RuntimeError("TARGET_API_IDENTITY_CHANGED")
    before = memory_reader()
    samples = []
    for index, prompt in enumerate(PROMPTS):
        payload = {"model": trial.SERVED, "messages": [{"role": "user", "content": prompt}],
                   "temperature": 0, "seed": SEED, "max_tokens": MAX_TOKENS,
                   "stream": True, "stream_options": {"include_usage": True}}
        # The canonical Native Tools runtime is qualified with the exact
        # NVIDIA Jinja non-thinking path. Keep historic benchmark defaults.
        if chat_template_kwargs is not None:
            if chat_template_kwargs != {"enable_thinking": False}:
                raise ValueError("UNQUALIFIED_BENCHMARK_TEMPLATE_KWARGS")
            payload["chat_template_kwargs"] = dict(chat_template_kwargs)
        request = Request("http://127.0.0.1:8000/v1/chat/completions",
                          data=json.dumps(payload).encode("utf-8"),
                          method="POST", headers={"Content-Type": "application/json"})
        started = clock()
        with opener(request, timeout=120) as response:
            if response.status != 200:
                raise RuntimeError("HTTP_NON_200")
            parsed = _stream_sample(response, started, clock=clock)
        elapsed = max(0.0, clock() - started)
        usage = parsed["usage"] if isinstance(parsed["usage"], dict) else {}
        prompt_tokens = usage.get("prompt_tokens")
        tokens = usage.get("completion_tokens")
        if type(tokens) is not int or tokens < 1:
            tokens = None
        if type(prompt_tokens) is not int or prompt_tokens < 0:
            prompt_tokens = None
        ttft = (max(0.0, parsed["first_token_at"] - started)
                if parsed["first_token_at"] is not None else None)
        # Decode proxy is a client estimate, NOT engine timing.
        decode_proxy = (round((tokens - 1) / (elapsed - ttft), 4)
                        if tokens is not None and tokens > 1
                        and ttft is not None and elapsed > ttft else None)
        reasons = []
        if not parsed["stream_complete"]:
            reasons.append("STREAM_NOT_COMPLETED")
        if not parsed["generated"]:
            reasons.append("NO_TEXT_OR_REASONING_DELTAS")
        if tokens is None:
            reasons.append("COMPLETION_TOKEN_USAGE_MISSING_OR_ZERO")
        if ttft is None:
            reasons.append("TTFT_NOT_OBSERVED")
        if parsed["finish_reason"] == "length":
            reasons.append("MAX_TOKEN_LIMIT_REACHED")
        samples.append({
            "index": index,
            "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
            "prompt_tokens": prompt_tokens, "completion_tokens": tokens,
            "latency_sec": round(elapsed, 6),
            "ttft_sec": round(ttft, 6) if ttft is not None else None,
            "end_to_end_tokens_per_sec": (round(tokens/elapsed, 4)
                                          if tokens and elapsed > 0 else None),
            "prompt_ingest_tokens_per_sec_proxy": (
                round(prompt_tokens / ttft, 4)
                if prompt_tokens is not None and ttft and ttft > 0 else None),
            "decode_tokens_per_sec_proxy": decode_proxy,
            "stream_complete": parsed["stream_complete"],
            "stream_finish_reason": parsed["finish_reason"],
            "usage_reported": isinstance(parsed["usage"], dict),
            "content_observed": parsed["content_observed"],
            "reasoning_observed": parsed["reasoning_observed"],
            "failure_reasons": reasons,
            "success": bool(parsed["stream_complete"] and parsed["generated"]
                            and tokens and ttft is not None
                            and parsed["finish_reason"] != "length"),
        })
    after = memory_reader()
    complete = all(row["success"] for row in samples)
    return {
        "status": "PASS" if complete else "PARTIAL",
        "benchmark_version": VERSION, "model": trial.SERVED,
        "requests": REQUEST_COUNT, "max_tokens": MAX_TOKENS,
        "seed": SEED, "concurrency": 1,
        "chat_template_kwargs": (
            dict(chat_template_kwargs) if chat_template_kwargs is not None else None
        ),
        "samples": samples,
        "metrics": {
            "latency_p50_sec": _percentile([r["latency_sec"] for r in samples], .5),
            "latency_p95_sec": _percentile([r["latency_sec"] for r in samples], .95),
            "ttft_p50_sec": _percentile([r["ttft_sec"] for r in samples
                                        if r["ttft_sec"] is not None], .5),
            "ttft_p95_sec": _percentile([r["ttft_sec"] for r in samples
                                        if r["ttft_sec"] is not None], .95),
            "mean_e2e_tokens_per_sec": (
                round(statistics.mean(r["end_to_end_tokens_per_sec"] for r in samples), 4)
                if all(r["end_to_end_tokens_per_sec"] is not None for r in samples) else None),
            "mean_decode_tokens_per_sec_proxy": (
                round(statistics.mean(r["decode_tokens_per_sec_proxy"] for r in samples), 4)
                if all(r["decode_tokens_per_sec_proxy"] is not None for r in samples) else None),
            "mean_prompt_ingest_tokens_per_sec_proxy": (
                round(statistics.mean(r["prompt_ingest_tokens_per_sec_proxy"] for r in samples), 4)
                if all(r["prompt_ingest_tokens_per_sec_proxy"] is not None
                       for r in samples) else None),
            "prefill_tokens_per_sec": None,
            "gpu_peak_mib": None,
        },
        "gpu_memory": {"before": before, "after": after},
        "limitations": ("Client TTFT includes queue/network/prefill. Decode proxy is "
                        "not engine-measured throughput. Prompt-ingest proxy is "
                        "prompt_tokens/TTFT, not engine prefill throughput. True prefill "
                        "throughput and peak GPU memory are NOT measured; GB10 may "
                        "lack memory counters."),
    }


def execute(plan_id, ack, *, planner=make_plan, core=trial.execute,
            measurement=measure, state_root: Path | None = None,
            status_inspector=inspect_live_status):
    # Do not change original trial executor; its exact-plan guard, local lock,
    # original-container identity, port exclusivity and recovery stay authoritative.
    measured: dict[str, Any] | None = None
    def probe():
        nonlocal measured
        measured = measurement()
        return measured.get("status") == "PASS"

    args = {"planner": planner, "inference": probe}
    if state_root is not None:
        args["state_dir"] = state_root
    rc, outcome = core(plan_id, ack, **args)
    if not outcome.get("executed"):
        return rc, {**outcome, "benchmark": None}
    post_status = None
    if outcome.get("restoration", {}).get("status") == "RESTORED":
        try:
            live = status_inspector()
            post_status = {
                "status": live.get("status"), "observed_model": live.get("observed_model"),
                "expected_served_id": live.get("expected_served_id"),
                "issues": live.get("issues", []),
            }
        except (OSError, RuntimeError, ValueError):
            post_status = {"status": "UNAVAILABLE"}
    result = {**outcome, "benchmark": measured,
              "post_restore_wizard_status": post_status}
    if (result["status"] == "PASS_RESTORED"
            and measured is not None and measured["status"] == "PASS"
            and post_status and post_status.get("status") == "LIVE_SERVICE_VERIFIED"
            and post_status.get("observed_model") == "flash-next"
            and post_status.get("expected_served_id") == "qwen3.8-flash-next"
            and not post_status.get("issues")):
        result["status"] = "BENCH_PASS_RESTORED_VERIFIED"
    elif result["status"] == "PASS_RESTORED":
        result["status"] = "BENCH_PARTIAL_RESTORED"
        rc = 4

    # Save bounded metric-only report AFTER computing final status.
    evidence = outcome.get("evidence")
    if isinstance(evidence, str) and evidence.endswith(".json"):
        path = Path(evidence).with_suffix(".benchmark.json")
        result["benchmark_evidence"] = str(path)
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                stream.write(json.dumps(result, indent=2, sort_keys=True) + "\n")
        except OSError:
            result.pop("benchmark_evidence", None)
            result["benchmark_evidence_error"] = "UNAVAILABLE"
            result["status"] = "BENCHMARK_EVIDENCE_WRITE_FAILED" if rc == 0 else result["status"]
            rc = 4
    else:
        result["benchmark_evidence_error"] = "ORIGINAL_EVIDENCE_PATH_UNAVAILABLE"
        rc = 4
    return rc, result


def main(argv=None):
    parser = argparse.ArgumentParser(description="Explicit 27B benchmark then Flash-Next restore")
    parser.add_argument("mode", choices=("plan", "execute"))
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    opts = parser.parse_args(argv)
    if opts.mode == "plan":
        if opts.approve_plan or opts.ack_downtime:
            parser.error("plan accepts no approval")
        result = make_plan()
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["status"] == "READY_TO_REQUEST_TRIAL_APPROVAL" else 3
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    rc, result = execute(opts.approve_plan, opts.ack_downtime)
    print(json.dumps(result, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
