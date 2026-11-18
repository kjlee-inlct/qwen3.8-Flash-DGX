"""One-shot, bounded, operator-approved P5 visible-output measurement.

Only an already-active Orcarouter MTP0 on localhost:8000 is eligible. No
Docker/CPU/GPU reconfiguration, switching, restart, cleanup or auto-retry.
A private O_EXCL claim is persisted BEFORE any inference; even a failed
attempt cannot be silently repeated. Prompts and generated text are discarded.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError, URLError

from scripts.manager.measurement_bench import (
    ACK, _identity_gate, _stream_chat, _synthetic_prompt, _token_count,
)
from scripts.manager.model_measurements import STATE, save_record
from scripts.manager.resource_diagnostics import snapshot, observation_summary

MODEL = "orcarouter"
CONTEXTS_K = (1, 4, 7)
OUTPUT_CAP = 256
SUFFIX = (
    "\n\nTask: List the integers from 1 to 120 in ascending order, "
    "separated by commas. Output only the numbered sequence; "
    "do not discuss the preceding text."
)


def _claim_once(root: Path, docker_id: str) -> str:
    if not re.fullmatch(r"[a-f0-9]{64}", docker_id):
        raise ValueError("DOCKER_IDENTITY_INVALID")
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    if root.is_symlink():
        raise ValueError("UNSAFE_CLAIM_DIRECTORY")
    path = root / ("p5-visible-mtp0-v1--" + docker_id[:24] + ".claim")
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        stream.write(json.dumps({
            "kind": "P5_VISIBLE_ONESHOT_CONSUMED_ON_ATTEMPT",
            "docker_id": docker_id, "mode": "enable_thinking_false",
            "contexts_k": CONTEXTS_K, "max_output_tokens": OUTPUT_CAP,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())
    return str(path)


def run_once(ack: str | None, *, gate=_identity_gate, stream=_stream_chat,
             build_prompt=_synthetic_prompt, token_count=_token_count,
             capture=snapshot, save=save_record, claim=_claim_once,
             state_dir: Path = STATE) -> dict:
    if ack != ACK:
        return {"schema_version": 1, "action": "benchmark-execute",
                "model": MODEL, "status": "BLOCKED",
                "issues": ["EXACT_LIVE_INFERENCE_ACK_REQUIRED"],
                "inference_executed": False, "service_mutated": False}

    # Existing gate enforces active service/API model, real full Docker ID,
    # and observed max_model_len before any GPU inference.
    spec, before, container, max_len = gate(MODEL)
    if not isinstance(max_len, int) or isinstance(max_len, bool) or max_len < 8192:
        raise ValueError("REQUIRES_ACTIVE_CONTEXT_LIMIT_AT_LEAST_8192")
    docker_id = container["id"]
    if not re.fullmatch(r"[a-f0-9]{64}", docker_id) or not container.get("running"):
        raise ValueError("ACTIVE_CONTAINER_UNQUALIFIED")
    receipt_claim = claim(state_dir, docker_id)

    samples = [before]
    results = []
    inference_executed = False
    started_utc = datetime.now(timezone.utc).isoformat()
    started_ns = time.monotonic_ns()
    reason = None
    for context in CONTEXTS_K:
        target = context * 1024
        if target + OUTPUT_CAP > max_len:
            reason = "ACTIVE_CONTEXT_LIMIT_EXCEEDED"
            break
        try:
            # Existing model-tokenizer-derived deterministic filler, followed
            # by a fixed instruction; no user data, secrets or prompt retained.
            filler, _ = build_prompt(spec["served_id"], target - 60)
            prompt = filler + SUFFIX
            actual = token_count(spec["served_id"], prompt)
            if not isinstance(actual, int) or isinstance(actual, bool) or (
                abs(actual - target) > target * 0.05 or
                actual + OUTPUT_CAP + 64 > max_len
            ):
                reason = "TOKENIZATION_OR_CONTEXT_LIMIT_MISMATCH"
                break
            inference_executed = True
            metrics = stream(spec["served_id"], prompt, OUTPUT_CAP,
                             enable_thinking=False)
            case_status = ("MEASURED_VISIBLE" if
                           metrics.get("stream_done_observed") is True and
                           metrics.get("ttfc_seconds") is not None and
                           metrics.get("visible_characters", 0) > 0 and
                           metrics.get("completion_tokens_reported") is not None
                           else "INCOMPLETE_VISIBLE_OUTPUT")
            results.append({"context_k": context, "status": case_status,
                            "requested_input_tokens": target,
                            "tokenizer_input_tokens": actual,
                            "metrics": metrics})
            after = capture(model=MODEL)
            samples.append(after)
            observed_id = ((after.get("docker") or {}).get("container") or {}).get("id")
            if observed_id != docker_id or after.get("model") != MODEL:
                reason = "DOCKER_IDENTITY_DRIFT"
                break
            if case_status != "MEASURED_VISIBLE":
                reason = "NO_VERIFIED_VISIBLE_CONTENT_STOP"
                break
        except (ValueError, RuntimeError, TimeoutError, URLError,
                HTTPError, OSError, TypeError) as exc:
            # Never retry. Do not preserve prompt/response/HTTP body.
            reason = "INCOMPLETE_CASE_" + type(exc).__name__
            break

    if len(samples) == 1:
        try:
            samples.append(capture(model=MODEL))
        except (OSError, ValueError, TypeError):
            pass
    final = samples[-1]
    stable = (all(((s.get("docker") or {}).get("container") or {}).get("id")
                  == docker_id for s in samples)
              and all(s.get("model") == MODEL for s in samples))
    accepted = (len(results) == len(CONTEXTS_K)
                and all(c["status"] == "MEASURED_VISIBLE" for c in results)
                and stable)
    doc = {
        "schema_version": 1, "action": "benchmark-execute",
        "benchmark_variant": "P5_VISIBLE_NO_THINKING_ONESHOT_V1",
        "model": MODEL, "profile": {"declared_profile": "mtp0"},
        "status": "COLLECTED_UNQUALIFIED" if accepted else "INCOMPLETE_MEASUREMENT",
        "timestamp_utc": started_utc,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "started_monotonic_ns": started_ns,
        "ended_monotonic_ns": time.monotonic_ns(),
        "git_head": before.get("git_head"),
        "identity": spec, "container": container,
        "active_max_model_len": max_len,
        "requested_context_k": list(CONTEXTS_K),
        "max_output_tokens": OUTPUT_CAP,
        "concurrency": 1, "repeat_count": 1,
        "chat_template_kwargs": {"enable_thinking": False},
        "results": results, "resource_snapshots": samples,
        "resource_interval": observation_summary(samples),
        "summary": {"requested_cases": len(CONTEXTS_K),
                    "visible_measured_cases": sum(
                        c["status"] == "MEASURED_VISIBLE" for c in results),
                    "ttfc_observed_cases": sum(
                        c["metrics"].get("ttfc_seconds") is not None for c in results),
                    "tps_observed_cases": sum(
                        c["metrics"].get("generation_tps_after_first_token") is not None
                        for c in results),
                    "container_id_continuous": stable,
                    "stop_issue": reason},
        "claim_file": receipt_claim,
        "inference_executed": inference_executed,
        "service_mutated": False, "production_released": False,
        "benchmark_verified": False, "approval_accepted_for_inference_only": True,
        "raw_prompts_or_generated_text_saved": False,
        "note": ("Each request opts out of thinking via vLLM chat_template_kwargs. "
                 "If the served model ignores it or emits no visible delta, stop "
                 "without retry. Resource snapshots are sequential, NOT independent "
                 "PLE RSS, host-port/NAT owner or GPU exclusivity evidence."),
    }
    doc["evidence_file"] = save(doc)
    return doc


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="P5 visible-answer GPU one-shot")
    parser.add_argument("--ack-live-inference")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        doc = run_once(args.ack_live_inference)
    except (ValueError, OSError, RuntimeError, TypeError) as exc:
        doc = {"schema_version": 1, "action": "benchmark-execute",
               "benchmark_variant": "P5_VISIBLE_NO_THINKING_ONESHOT_V1",
               "model": MODEL, "status": "BLOCKED",
               "issues": [type(exc).__name__ + ":" + str(exc)],
               "service_mutated": False, "production_released": False,
               "note": "No automatic retry; a private claim may already have been consumed."}
    summary = {k: doc.get(k) for k in (
        "schema_version", "action", "benchmark_variant", "model", "status",
        "timestamp_utc", "git_head", "container", "active_max_model_len",
        "requested_context_k", "max_output_tokens", "chat_template_kwargs",
        "results", "summary", "claim_file", "evidence_file", "issues",
        "inference_executed", "service_mutated", "production_released", "note"
    ) if k in doc}
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
    return 0 if doc["status"] == "COLLECTED_UNQUALIFIED" else 3


if __name__ == "__main__":
    sys.exit(main())
