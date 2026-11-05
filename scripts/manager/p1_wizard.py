#!/usr/bin/env python3
"""P1 Wizard: read-only plans, explicit approval, safe Flash-Next actions.

Never downloads model, runs setup, removes containers, or switches services.
Plan hashes bind actual checkpoint/image/port/container facts to one action.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
from urllib.error import HTTPError
from urllib.request import urlopen
from uuid import uuid4

from scripts.manager.inventory import inspect_host
from scripts.manager.p1_assets import audit_checkpoint, inspect_image
from scripts.manager.p1_bench import http_json, require_model, run_benchmark

ROOT = Path(__file__).resolve().parents[2]
MODEL = "nvidia/Qwen3.8-Flash-Next-NVFP4"
SERVED = "qwen3.8-flash-next"
NAME = "qwen38-flash"
PORT = 8000
IMAGE = "qwen38-flash-dgx:v0.32"
API = "http://127.0.0.1:8000"
ACTIONS = ("prepare", "start", "wait", "verify", "benchmark")


def transfer_running(runner=subprocess.run) -> tuple[bool, str | None]:
    """Conservative read-only process scan to avoid concurrent setup/preparation."""
    try:
        result = runner(["ps", "-eo", "args"], check=False, capture_output=True,
                        text=True, timeout=10)
        if result.returncode:
            return True, "process_inventory_failed"
        markers = ("scripts/download-weights.sh", "scripts/prepare-hybrid.sh",
                   "./flash setup ", "bash flash setup ",
                   "hf download nvidia/Qwen3.8-Flash-Next-NVFP4")
        for line in result.stdout.splitlines():
            if any(marker in line for marker in markers):
                return True, "active_model_transfer_or_setup"
        return False, None
    except (OSError, subprocess.TimeoutExpired):
        return True, "process_inventory_unavailable"


def _target(inv: dict) -> dict | None:
    return next((c for c in inv.get("containers", [])
                 if c.get("name") == NAME), None)


def build_plan(action: str, *, cache_root: Path | None = None,
               requests: int = 3, max_tokens: int = 64, seed: int = 1234,
               runner=subprocess.run) -> dict[str, Any]:
    if action not in ACTIONS:
        raise ValueError("unsupported P1 action")
    if not (1 <= requests <= 20 and 1 <= max_tokens <= 256 and
            0 <= seed <= 2**31 - 1):
        raise ValueError("benchmark parameters out of bounds")
    cache = Path(cache_root or os.environ.get(
        "HF_CACHE", str(Path.home() / ".cache/huggingface"))).expanduser()
    inv = inspect_host(name=NAME, port=PORT, cache_root=cache, run=runner)
    chk = audit_checkpoint(cache)
    img = inspect_image(run=runner)
    busy, busy_reason = transfer_running(runner)
    container = _target(inv)
    issues = list(inv.get("errors", []))
    if not img["ready"]:
        issues.append("vllm_032_image_missing_or_wrong_label")
    if action == "prepare" and (inv.get("disk") or {}).get("free_bytes", 0) < 20 * 1024**3:
        issues.append("insufficient_free_disk_for_hybrid_preparation")
    if not chk["source_complete"]:
        issues.append("checkpoint_downloading_or_incomplete")
    if action in ("start", "wait", "verify", "benchmark") and not chk["hybrid_ready"]:
        issues.append("hybrid_not_prepared_or_incomplete")
    if action == "prepare":
        if chk["hybrid_ready"]:
            issues.append("hybrid_already_prepared")
        if busy:
            issues.append(busy_reason or "active_setup_uncertain")
        if container:
            issues.append("container_exists_preparation_blocked")
    elif action == "start":
        if busy:
            issues.append(busy_reason or "active_setup_uncertain")
        if inv.get("name_conflict"):
            issues.append("name_occupied")
        if inv.get("port_conflict"):
            issues.append("port_8000_occupied")
    else:
        if container is None or not str(container.get("status", "")).startswith("Up"):
            issues.append("target_not_running")
        else:
            mapping = re.search(
                r"(?:^|,\s*)(?:0\.0\.0\.0|\[::\]|127\.0\.0\.1):8000->8000/tcp",
                container.get("ports", ""))
            if mapping is None:
                issues.append("target_port_mapping_missing")
            if container.get("image_id") != img["id"]:
                issues.append("container_image_id_mismatch")
    preview = {
        "prepare": ["scripts/prepare-hybrid.sh"],
        "start": ["flash", "serve", "default"],
        "wait": ["flash", "wait"],
        "verify": ["HTTP", "/health, /v1/models, text/tool/vision"],
        "benchmark": ["HTTP", "3 bounded SSE requests by default"],
    }[action]
    # Exclude dynamic free-space and timestamps; bind identities and execution flags.
    fingerprint = {
        "version": 1, "action": action, "model": MODEL, "served": SERVED,
        "image_id": img["id"], "image_base": img["vllm_base"],
        "revision": chk["revision"], "source_complete": chk["source_complete"],
        "hybrid_ready": chk["hybrid_ready"], "cache": str(cache.resolve()),
        "name": NAME, "port": PORT,
        "container_image_id": container.get("image_id") if container else None,
        "container_status": (str(container.get("status", "")).split(" ", 1)[0]
                             if container else None),
        "name_conflict": inv.get("name_conflict"),
        "port_conflict": inv.get("port_conflict"),
        "active_transfer": busy,
        "bench": {"requests": requests, "max_tokens": max_tokens, "seed": seed}
                 if action == "benchmark" else None,
    }
    plan_id = hashlib.sha256(json.dumps(
        fingerprint, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {
        "scope": "P1_WIZARD_PLAN", "action": action,
        "status": "BLOCKED" if issues else "READY_TO_REQUEST_APPROVAL",
        "executed": False, "approved": False, "plan_id": plan_id,
        "requires_explicit_approval": True, "command_preview": preview,
        "issues": sorted(set(issues)),
        "facts": {
            "checkpoint": chk, "image": img,
            "inventory_status": inv.get("status"),
            "container": ({"name": container["name"],
                           "image_id": container.get("image_id"),
                           "status": container.get("status"),
                           "ports": container.get("ports")}
                          if container else None),
            "name_conflict": inv.get("name_conflict"),
            "port_conflict": inv.get("port_conflict"),
            "transfer_active": busy,
            "disk_free_bytes": (inv.get("disk") or {}).get("free_bytes"),
        },
        "parameters": {"requests": requests, "max_tokens": max_tokens, "seed": seed},
        "rollback": "No automatic rm/stop/restart; inspect and explicitly approve recovery.",
    }


def _safe_env(cache: str) -> dict[str, str]:
    # Discard arbitrary overrides (EXTRA, DOCKER_EXTRA, DRAFT_MODEL, LD_PRELOAD).
    env = {k: os.environ[k] for k in ("HOME", "PATH", "LANG", "LC_ALL", "TERM")
           if k in os.environ}
    env.update({
        "HF_CACHE": cache, "IMAGE": IMAGE, "MODEL": MODEL, "NAME": NAME,
        "PORT": "8000", "MODE": "hybrid", "SERVED_MODEL_NAME": SERVED,
        "MTP": "2", "YARN": "1", "CTX": "500000", "DRY": "0",
        "DRAFT_MODEL": "", "EXTRA": "", "DOCKER_EXTRA": "",
        "GPU_MEM": "0.80", "SEQS": "8",
    })
    return env


def _chat_probe(*, opener=urlopen, kind: str = "text") -> dict:
    content: Any = "Answer with one word: pong. /no_think"
    if kind == "vision":
        # Original 1x1 synthetic PNG; no external URLs.
        pixel = ("iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFklEQVR4"
                 "nGP8//8/AwMDEwMDAwMDAwAkBgMB/DXemwAAAABJRU5ErkJggg==")
        content = [
            {"type": "text", "text": "Describe this tiny image in one sentence."},
            {"type": "image_url",
             "image_url": {"url": "data:image/png;base64," + pixel}},
        ]
    payload: dict[str, Any] = {
        "model": SERVED, "messages": [{"role": "user", "content": content}],
        "temperature": 0, "max_tokens": 256, "stream": False,
    }
    if kind == "tools":
        payload["messages"] = [{"role": "user",
                                "content": "Call multiply to calculate 3 times 7."}]
        payload["tools"] = [{
            "type": "function", "function": {
                "name": "multiply", "description": "Multiply two integers",
                "parameters": {"type": "object",
                               "properties": {"a": {"type": "integer"},
                                              "b": {"type": "integer"}},
                               "required": ["a", "b"]}}}]
        payload["tool_choice"] = "required"
    result = http_json(API + "/v1/chat/completions", method="POST",
                       payload=payload, timeout=90, opener=opener)
    choices = result.get("choices", [])
    if not choices or not isinstance(choices[0], dict):
        raise ValueError("chat_missing_choices")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise ValueError("chat_missing_message")
    if kind == "tools":
        if not message.get("tool_calls"):
            raise ValueError("tool_call_missing")
    elif not str(message.get("content") or "").strip():
        raise ValueError("response_content_missing")
    return {"status": "PASS", "kind": kind}


def _default_completion(*, opener=urlopen) -> dict[str, Any]:
    """Same ordinary /v1/completions coherence shape as Blazux smoke-test."""
    payload = {"model": SERVED, "prompt": "The capital of France is",
               "max_tokens": 12, "temperature": 0}
    result = http_json(API + "/v1/completions", method="POST",
                       payload=payload, timeout=120, opener=opener)
    choices = result.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ValueError("completion_choices_missing")
    if not str(choices[0].get("text") or "").strip():
        raise ValueError("completion_text_missing")
    return {"status": "PASS", "kind": "default_completion"}


def _checked_probe(fn, **kwargs) -> dict[str, Any]:
    """Capture safe failure codes, not prompts, responses or credential data."""
    try:
        return fn(**kwargs)
    except (HTTPError, TimeoutError, OSError, RuntimeError, TypeError,
            ValueError, KeyError) as exc:
        output = {"status": "FAIL", "error_type": type(exc).__name__}
        if isinstance(exc, HTTPError):
            output["http_status"] = exc.code
        if isinstance(exc, ValueError) and str(exc) in {
                "completion_choices_missing", "completion_text_missing",
                "chat_missing_choices", "chat_missing_message",
                "tool_call_missing", "response_content_missing",
                "health_failed", "served_model_id_mismatch"}:
            output["error_code"] = str(exc)
        return output


def verify_api(*, opener=urlopen) -> dict[str, Any]:
    """Blazux baseline is a gate; extra tool/vision probes are independent."""
    identity = _checked_probe(
        lambda **kwargs: require_model(API, SERVED, **kwargs), opener=opener)
    if identity.get("status") == "FAIL":
        return {
            "status": "FAIL", "scope": "API/GPU",
            "baseline_status": "FAIL", "extended_status": "NOT_RUN",
            "probes": {"identity": identity}, "identity": None,
        }
    baseline = {
        "default_completion": _checked_probe(_default_completion, opener=opener),
        "chat": _checked_probe(_chat_probe, opener=opener, kind="text"),
    }
    baseline_ok = all(x.get("status") == "PASS" for x in baseline.values())
    extended = {
        "tools": _checked_probe(_chat_probe, opener=opener, kind="tools"),
        "vision": _checked_probe(_chat_probe, opener=opener, kind="vision"),
    } if baseline_ok else {}
    extended_ok = bool(extended) and all(
        x.get("status") == "PASS" for x in extended.values())
    return {
        "status": ("FAIL" if not baseline_ok else
                   "PASS" if extended_ok else "PARTIAL"),
        "scope": "API/GPU",
        "baseline_status": "PASS" if baseline_ok else "FAIL",
        "extended_status": ("NOT_RUN" if not baseline_ok else
                            "PASS" if extended_ok else "FAIL"),
        "identity": identity,
        "probes": {**baseline, **extended},
    }


def perform(plan: dict, *, runner=subprocess.run, opener=urlopen) -> dict:
    action = plan["action"]
    if action in ("prepare", "start", "wait"):
        command = plan["command_preview"]
        argv = [str(ROOT / command[0]), *command[1:]]
        result = runner(argv, cwd=ROOT,
                        env=_safe_env(plan["facts"]["checkpoint"]["cache_root"]),
                        check=False, timeout=1800)
        if result.returncode:
            raise RuntimeError("command_failed:" + action)
        return {"scope": "DGX/ASSET" if action == "prepare" else "GPU/API",
                "status": ("PREPARED_PENDING_AUDIT" if action == "prepare"
                           else "STARTED_PENDING_HEALTH" if action == "start" else "PASS"),
                "exit_code": result.returncode}
    if action == "verify":
        return verify_api(opener=opener)
    if action == "benchmark":
        identity = require_model(API, SERVED, opener=opener)
        measurement = run_benchmark(
            API, SERVED, requests=plan["parameters"]["requests"],
            max_tokens=plan["parameters"]["max_tokens"],
            seed=plan["parameters"]["seed"], opener=opener)
        return {"scope": "API/GPU", "status": measurement["status"],
                "identity": identity, "benchmark": measurement}
    raise ValueError("invalid action")


def _write_evidence(directory: Path, document: dict) -> Path:
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    dest = directory / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                        + "-" + uuid4().hex[:12] + ".json")
    descriptor = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(document, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return dest


def execute_approved(plan: dict, approval: str | None, *, cache_root: Path,
                     evidence_dir: Path, requests: int = 3,
                     max_tokens: int = 64, seed: int = 1234,
                     runner=subprocess.run, opener=urlopen) -> tuple[int, dict]:
    if plan["status"] != "READY_TO_REQUEST_APPROVAL":
        return 3, {"status": "BLOCKED", "issues": plan["issues"], "executed": False}
    if not approval or approval != plan["plan_id"]:
        return 3, {"status": "BLOCKED",
                   "issues": ["approval_missing_or_stale"], "executed": False}
    fresh = build_plan(plan["action"], cache_root=cache_root, requests=requests,
                       max_tokens=max_tokens, seed=seed, runner=runner)
    if fresh["status"] != "READY_TO_REQUEST_APPROVAL" or fresh["plan_id"] != approval:
        return 3, {"status": "BLOCKED",
                   "issues": ["preflight_changed"], "executed": False}
    record = {
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "action": fresh["action"], "plan_id": approval,
        "model_repo": MODEL, "model_revision": fresh["facts"]["checkpoint"]["revision"],
        "image_id": fresh["facts"]["image"]["id"], "api_base": API + "/v1",
        "served_model": SERVED, "parameters": fresh["parameters"],
        "approval": "explicit_plan_id", "status": "FAIL",
        "scope": "SOURCE", "executed": True,
    }
    try:
        result = perform(fresh, runner=runner, opener=opener)
        record["result"] = result
        record["status"] = result["status"]
        record["scope"] = result["scope"]
    except (RuntimeError, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        # Log exception type only; error text may expose paths or request details.
        record["error_type"] = type(exc).__name__
        record["status"] = "FAIL"
    record["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    try:
        dest = _write_evidence(evidence_dir, record)
    except OSError:
        return 3, {"status": "BLOCKED", "issues": ["evidence_write_failed"],
                   "executed": True}
    return (0 if record["status"] in ("PASS", "STARTED_PENDING_HEALTH",
                                      "PREPARED_PENDING_AUDIT") else 2), {
        "status": record["status"], "scope": record["scope"],
        "action": plan["action"], "evidence": str(dest), "executed": True,
        "error_type": record.get("error_type"),
        "baseline_status": (record.get("result") or {}).get("baseline_status"),
        "extended_status": (record.get("result") or {}).get("extended_status"),
        "probes": (record.get("result") or {}).get("probes"),
    }


def _evidence_dir(arg: Path | None) -> Path:
    return Path(arg or Path(os.environ.get(
        "XDG_STATE_HOME", str(Path.home() / ".local/state"))) / "blazux-wizard/p1")


def guided(args: argparse.Namespace) -> int:
    actions = {"1": "prepare", "2": "start", "3": "wait",
               "4": "verify", "5": "benchmark"}
    print("Blazux P1 Wizard: 1 prepare, 2 start, 3 wait, 4 verify, 5 benchmark, 0 exit")
    while True:
        choice = input("Action (0 exits): ").strip()
        if choice == "0":
            return 0
        if choice not in actions:
            print("Unknown action, nothing executed.")
            continue
        action = actions[choice]
        plan = build_plan(action, cache_root=args.cache_root,
                          requests=args.requests, max_tokens=args.max_tokens,
                          seed=args.seed)
        print(json.dumps(plan, indent=2, sort_keys=True))
        if plan["status"] == "BLOCKED":
            continue
        approval = input("Type full plan_id to execute, or Enter to cancel: ").strip()
        if approval != plan["plan_id"]:
            print("Cancelled.")
            continue
        cache = Path(args.cache_root or os.environ.get(
            "HF_CACHE", str(Path.home() / ".cache/huggingface")))
        _, outcome = execute_approved(plan, approval, cache_root=cache,
                                      evidence_dir=_evidence_dir(args.evidence_dir),
                                      requests=args.requests,
                                      max_tokens=args.max_tokens, seed=args.seed)
        print(json.dumps(outcome, indent=2, sort_keys=True))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P1 Flash-Next Wizard; default is read-only")
    parser.add_argument("action", choices=("status", "plan", "guided", *ACTIONS))
    parser.add_argument("--for-action", choices=ACTIONS, default="prepare")
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--requests", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=64)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args(argv)
    if args.action == "guided":
        if args.execute or args.approve_plan:
            parser.error("guided asks its own confirmation")
        return guided(args)
    action = args.for_action if args.action in ("plan", "status") else args.action
    try:
        plan = build_plan(action, cache_root=args.cache_root,
                          requests=args.requests, max_tokens=args.max_tokens,
                          seed=args.seed)
    except (ValueError, OSError) as exc:
        print(json.dumps({"status": "BLOCKED", "error_type": type(exc).__name__}))
        return 3
    if args.action in ("plan", "status") or not args.execute:
        if args.execute and args.action in ("plan", "status"):
            parser.error("status and plan are read-only")
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0 if args.action == "status" or plan["status"] != "BLOCKED" else 3
    cache = Path(args.cache_root or os.environ.get(
        "HF_CACHE", str(Path.home() / ".cache/huggingface")))
    rc, outcome = execute_approved(
        plan, args.approve_plan, cache_root=cache,
        evidence_dir=_evidence_dir(args.evidence_dir),
        requests=args.requests, max_tokens=args.max_tokens, seed=args.seed)
    print(json.dumps(outcome, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    sys.exit(main())
