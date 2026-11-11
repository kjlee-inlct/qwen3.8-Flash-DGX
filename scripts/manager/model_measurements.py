"""Generic, non-authorizing model metrics and local measurement history.

Metric definitions are extensible; a missing observation is never inferred from a
recipe, mapped file size, or another process's memory accounting.
No model start/stop, GPU mutation or inference occurs in inventory/history/plan.
History is separate from the operating transition journal and saved only on opt-in.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import math
import os
import shlex
from pathlib import Path
import re
import subprocess
import uuid

from scripts.manager.generic_operations import model_catalog
from scripts.manager.resource_diagnostics import snapshot

STATE = Path.home() / ".local/state/blazux-wizard/model-measurements"
MAX_LOG_CHARS = 1_000_000
MAX_HISTORY_ITEMS = 50
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FILE_NAME = re.compile(r"^[a-z0-9-]+--[0-9]{8}T[0-9]{6}[0-9]{6}Z--[a-f0-9]{12}\.json$")
MODEL_NAME = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
METRICS = {
    "host_mem_total_bytes": ("B", "host"),
    "host_mem_available_bytes": ("B", "host"),
    "host_mem_free_bytes": ("B", "host"),
    "host_cached_bytes": ("B", "host"),
    "host_swap_used_bytes": ("B", "host"),
    "cgroup_memory_current_bytes": ("B", "container"),
    "cgroup_memory_peak_bytes": ("B", "container"),
    "cgroup_anon_bytes": ("B", "container"),
    "cgroup_file_bytes": ("B", "container"),
    "cgroup_inactive_file_bytes": ("B", "container"),
    "cgroup_swap_current_bytes": ("B", "container"),
    "process_rss_bytes": ("B", "process"),
    "process_pss_bytes": ("B", "process"),
    "ple_mapped_declared_bytes": ("B", "recipe"),
    "ple_resident_bytes": ("B", "process"),
    "weight_load_reported_gib": ("GiB", "runtime-log"),
    "kv_available_reported_gib": ("GiB", "runtime-log"),
    "kv_capacity_reported_tokens": ("tokens", "runtime-log"),
    "memory_psi_some_avg10_pct": ("%", "host"),
    "cpu_psi_some_avg10_pct": ("%", "host"),
    "io_psi_some_avg10_pct": ("%", "host"),
    "cpu_frequency_mean_mhz": ("MHz", "host"),
    "gpu_utilization_pct": ("%", "host"),
    "gpu_temperature_celsius": ("C", "host"),
    "thermal_max_celsius": ("C", "host"),
    "loaded_ttfc_seconds": ("s", "benchmark"),
    "loaded_ttft_seconds": ("s", "benchmark"),
    "loaded_generation_tps": ("tok/s", "benchmark"),
    "loaded_e2e_seconds": ("s", "benchmark"),
    "actual_input_tokens": ("tokens", "benchmark"),
    "actual_output_tokens": ("tokens", "benchmark"),
}
FLAG_NAMES = (
    "max-model-len", "max-num-seqs", "gpu-memory-utilization",
    "kv-cache-dtype", "dtype", "num-speculative-tokens",
    "speculative-config", "cpu-offload-gb", "enforce-eager",
    "enable-prefix-caching", "block-size",
)
ENV_NAMES = ("VLLM_PLE_MMAP", "VLLM_PLE_MMAP_WORKERS", "VLLM_PLE_MMAP_PREWARM",
             "VLLM_PLE_MMAP_MADVISE", "VLLM_PLE_MMAP_FAST_ROWS")
LOG_PATTERNS = {
    # This value is an engine log's weight allocation claim, NOT host RSS.
    "weight_load_reported_gib": re.compile(
        r"Loading model weights took\s+([0-9]+(?:\.[0-9]+)?)\s+GiB", re.I),
    "kv_available_reported_gib": re.compile(
        r"Available KV cache memory:\s*([0-9]+(?:\.[0-9]+)?)\s+GiB", re.I),
    "kv_capacity_reported_tokens": re.compile(
        r"(?:GPU|Total) KV cache size:\s*([0-9][0-9,]*)\s+tokens", re.I),
}


def _metric(key, value, source, *, note=None, status=None):
    unit, scope = METRICS[key]
    valid = isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and value >= 0
    return {
        "value": value if valid else None, "unit": unit, "scope": scope,
        "status": status or ("OBSERVED" if valid else "NOT_OBSERVED"),
        "source": source if valid else None,
        "note": note,
    }


def metric_catalog():
    """Add new metric IDs here without changing history or the Wizard route."""
    return {k: {"unit": v[0], "scope": v[1]} for k, v in sorted(METRICS.items())}


def _call(argv, *, runner=subprocess.run, limit=MAX_LOG_CHARS, include_stderr=False):
    try:
        out = runner(argv, capture_output=True, text=True, check=False, timeout=8)
        if out.returncode != 0 or not isinstance(out.stdout, str):
            return None
        return ((out.stdout + (getattr(out, "stderr", "") or "")) if include_stderr else out.stdout)[-limit:]
    except (OSError, subprocess.TimeoutExpired, ValueError, TypeError):
        return None


def _flags(argv):
    if not isinstance(argv, list) or not all(isinstance(x, str) for x in argv):
        return {}
    # Docker commonly wraps vLLM in `bash -lc "vllm serve --flag ..."`.
    # Parse shell text as data only; never execute it or expose other arguments.
    words = []
    for arg in argv:
        if "--" in arg and any(char.isspace() for char in arg):
            try:
                words.extend(shlex.split(arg)[:1024])
            except ValueError:
                words.append(arg)
        else:
            words.append(arg)
    found = {}
    for i, token in enumerate(words):
        for name in FLAG_NAMES:
            flag = "--" + name
            if token == flag:
                if name in ("enforce-eager", "enable-prefix-caching"):
                    found[name] = True
                elif i + 1 < len(words) and not words[i + 1].startswith("--"):
                    found[name] = words[i + 1]
            elif token.startswith(flag + "="):
                found[name] = token[len(flag) + 1:]
    return found


def parse_runtime_log(raw):
    """Extract only known vLLM numeric labels. Never store raw Docker logs."""
    result = {}
    for key, pattern in LOG_PATTERNS.items():
        matches = pattern.findall(raw or "")
        value = None
        if matches:
            try:
                value = int(matches[-1].replace(",", "")) if key.endswith("_tokens") else float(matches[-1])
            except ValueError:
                pass
        result[key] = _metric(key, value, "docker-logs:bounded-matched-label",
                              note=("Engine-reported value, not independently measured host RSS"
                                    if key == "weight_load_reported_gib" else
                                    "From current container's bounded log tail; may be absent"))
    return result


def _runtime(container, *, runner=subprocess.run):
    """Bind runtime configuration and log parsing to the exact observed ID."""
    cid = container.get("id") if isinstance(container, dict) else None
    name = container.get("name") if isinstance(container, dict) else None
    if not isinstance(cid, str) or not HEX64.fullmatch(cid) or not isinstance(name, str):
        return {"status": "NOT_OBSERVED", "launch_flags": {}, "selected_env": {},
                "log_metrics": parse_runtime_log(None), "issues": ["CONTAINER_ID_NOT_VERIFIED"]}
    raw = _call(["docker", "inspect", "--format", "{{json .}}", cid], runner=runner)
    try:
        obj = json.loads(raw) if raw is not None else None
        if (not isinstance(obj, dict) or obj.get("Id") != cid
                or obj.get("Name", "").lstrip("/") != name
                or obj.get("State", {}).get("Running") is not True):
            raise ValueError("identity drift")
        cfg = obj.get("Config") or {}
        argv = (cfg.get("Entrypoint") or []) + (cfg.get("Cmd") or [])
        env = {}
        for item in cfg.get("Env") or []:
            if isinstance(item, str) and "=" in item:
                key, value = item.split("=", 1)
                if key in ENV_NAMES:
                    env[key] = value
    except (ValueError, TypeError, AttributeError):
        return {"status": "NOT_OBSERVED", "launch_flags": {}, "selected_env": {},
                "log_metrics": parse_runtime_log(None), "issues": ["RUNTIME_INSPECT_IDENTITY_UNBOUND"]}
    log = _call(["docker", "logs", "--tail", "2500", cid],
                runner=runner, limit=MAX_LOG_CHARS, include_stderr=True)
    return {"status": "OBSERVED_CONFIG" if log is not None else "OBSERVED_CONFIG_LOG_MISSING",
            "container_id": cid, "launch_flags": _flags(argv),
            "selected_env": env,
            "log_metrics": parse_runtime_log(log),
            "raw_log_saved": False, "issues": []}


def _candidate_profile(model):
    from scripts.manager.resource_diagnostics import _recipe_for_model
    recipe = _recipe_for_model(model)
    selected = (recipe.get("trial") or {}).get("profile", "mtp0")
    return {
        "recipe_path": model_catalog()["models"][model]["recipe_path"],
        "declared_profile": selected,
        "candidate_settings": (recipe.get("profiles") or {}).get(selected),
        "runtime_settings_proven": False,
        "note": "Recipe is desired/candidate state; only observed launch flags are runtime evidence.",
    }


def _nested(obj, *keys):
    for key in keys:
        obj = obj.get(key) if isinstance(obj, dict) else None
    return obj


def inventory(model, *, capture=snapshot, runner=subprocess.run):
    """One read-only existing resource snapshot plus exact-ID log/config inspection."""
    catalog = model_catalog()
    if model not in catalog["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    observed = capture(model=model)
    docker = observed.get("docker") or {}
    container = docker.get("container") or {}
    runtime = _runtime(container, runner=runner) if docker.get("status") == "OBSERVED" else {
        "status": "NOT_OBSERVED", "launch_flags": {}, "selected_env": {},
        "log_metrics": parse_runtime_log(None), "issues": ["TARGET_MODEL_NOT_RUNNING"]}
    host = observed.get("host_memory") or {}
    group = _nested(docker, "cgroup_v2", "metrics") or {}
    stat = group.get("memory_stat_bytes") or {}
    proc = docker.get("process_smaps_rollup_bytes") or {}
    metrics = {}
    for key, val in (
        ("host_mem_total_bytes", host.get("MemTotal_bytes")),
        ("host_mem_available_bytes", host.get("MemAvailable_bytes")),
        ("host_mem_free_bytes", host.get("MemFree_bytes")),
        ("host_cached_bytes", host.get("Cached_bytes")),
        ("host_swap_used_bytes", host.get("swap_used_bytes")),
        ("cgroup_memory_current_bytes", group.get("memory.current")),
        ("cgroup_memory_peak_bytes", group.get("memory.peak")),
        ("cgroup_swap_current_bytes", group.get("memory.swap.current")),
        ("cgroup_anon_bytes", stat.get("anon")),
        ("cgroup_file_bytes", stat.get("file")),
        ("cgroup_inactive_file_bytes", stat.get("inactive_file")),
        ("process_rss_bytes", proc.get("Rss")),
        ("process_pss_bytes", proc.get("Pss")),
        ("ple_mapped_declared_bytes", observed.get("ple_declared_mmap_bytes")),
        ("ple_resident_bytes", docker.get("ple_specific_resident_bytes")),
        ("memory_psi_some_avg10_pct", _nested(observed, "pressure", "memory", "some", "avg10")),
        ("cpu_psi_some_avg10_pct", _nested(observed, "pressure", "cpu", "some", "avg10")),
        ("io_psi_some_avg10_pct", _nested(observed, "pressure", "io", "some", "avg10")),
        ("cpu_frequency_mean_mhz", _nested(observed, "cpu_frequency", "current_mhz_mean")),
        ("thermal_max_celsius", _nested(observed, "thermal", "max_celsius")),
    ):
        if isinstance(val, str) and val.isdecimal():
            val = int(val)
        metrics[key] = _metric(key, val, "resource-diagnostics:snapshot",
                               status=("DECLARED_NOT_RESIDENT" if key == "ple_mapped_declared_bytes" and
                                       isinstance(val, (int, float)) else None))
    gpu_rows = _nested(observed, "gpu", "metrics")
    gpu = gpu_rows[0] if isinstance(gpu_rows, list) and len(gpu_rows) == 1 else {}
    metrics["gpu_utilization_pct"] = _metric(
        "gpu_utilization_pct", gpu.get("utilization.gpu"), "nvidia-smi:utilization.gpu")
    metrics["gpu_temperature_celsius"] = _metric(
        "gpu_temperature_celsius", gpu.get("temperature.gpu"), "nvidia-smi:temperature.gpu")
    metrics.update(runtime["log_metrics"])
    for key in ("loaded_ttfc_seconds", "loaded_ttft_seconds", "loaded_generation_tps",
                "loaded_e2e_seconds", "actual_input_tokens", "actual_output_tokens"):
        metrics[key] = _metric(key, None, None,
                               note="Requires separately approved inference benchmark")
    return {
        "schema_version": 1, "action": "inventory", "status": "READ_ONLY_PARTIAL",
        "model": model, "identity": catalog["models"][model],
        "timestamp_utc": observed.get("timestamp_utc"),
        "git_head": observed.get("git_head"),
        "container": container if docker.get("status") == "OBSERVED" else None,
        "profile": _candidate_profile(model), "runtime": runtime,
        "metrics": metrics, "resource_snapshot": observed,
        "scope": "READ_ONLY_SNAPSHOT_AND_EXACT_CONTAINER_LOG_LABELS",
        "inference_executed": False, "service_mutated": False, "production_released": False,
        "note": "Missing engine log fields remain NOT_OBSERVED. Full underlying telemetry retained.",
    }


def save_record(doc, *, directory=None):
    """0600 opt-in measurement receipt, independent of operating Journal."""
    root = STATE if directory is None else Path(directory)
    model = doc.get("model")
    if not isinstance(model, str) or not MODEL_NAME.fullmatch(model):
        raise ValueError("INVALID_HISTORY_MODEL")
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    if root.is_symlink():
        raise ValueError("UNSAFE_HISTORY_DIRECTORY")
    name = model + "--" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "--" + uuid.uuid4().hex[:12] + ".json"
    path = root / name
    data = json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=2)
    if len(data.encode("utf-8")) > 8_000_000:
        raise ValueError("HISTORY_RECEIPT_TOO_LARGE")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(data + "\n")
        f.flush()
        os.fsync(f.fileno())
    return str(path)


def history(model, *, directory=None, limit=20):
    if model not in model_catalog()["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    if not 1 <= limit <= MAX_HISTORY_ITEMS:
        raise ValueError("HISTORY_LIMIT_OUT_OF_RANGE")
    root = STATE if directory is None else Path(directory)
    rows = []
    if root.exists() and not root.is_symlink():
        files = sorted((p for p in root.iterdir() if FILE_NAME.fullmatch(p.name)
                        and p.name.startswith(model + "--") and p.is_file()
                        and not p.is_symlink()), reverse=True)[:limit]
        for p in files:
            try:
                if p.stat().st_size > 8_000_000:
                    continue
                doc = json.loads(p.read_text(encoding="utf-8"))
                if doc.get("model") != model or doc.get("schema_version") != 1:
                    continue
                rows.append({
                    "timestamp_utc": doc.get("timestamp_utc"),
                    "action": doc.get("action"), "status": doc.get("status"),
                    "git_head": doc.get("git_head"),
                    "container_id": _nested(doc, "container", "id"),
                    "profile": _nested(doc, "profile", "declared_profile"),
                    "summary": doc.get("summary") or {
                        k: v.get("value") for k, v in (doc.get("metrics") or {}).items()
                        if isinstance(v, dict) and v.get("value") is not None},
                    "file": str(p),
                })
            except (OSError, ValueError, TypeError, AttributeError):
                continue
    return {"schema_version": 1, "action": "history", "model": model,
            "status": "READ_ONLY_HISTORY", "records": rows, "count": len(rows),
            "service_mutated": False, "inference_executed": False,
            "note": "Local opt-in measurement receipts; not operating transition journal."}


def compact(doc):
    return {k: doc.get(k) for k in (
        "schema_version", "action", "status", "model", "timestamp_utc",
        "git_head", "container", "profile", "runtime", "metrics",
        "summary", "results", "evidence_file", "note")
        if k in doc}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Generic DGX model measurement workspace")
    parser.add_argument("action", choices=("catalog", "inventory", "history",
                                           "benchmark-plan", "benchmark-execute"))
    parser.add_argument("--model", default="orcarouter")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--summary-only", action="store_true")
    parser.add_argument("--contexts-k", default="1,4,8")
    parser.add_argument("--max-output-tokens", type=int, default=128)
    parser.add_argument("--ack-live-inference")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.action == "catalog":
            doc = {"schema_version": 1, "action": "catalog", "status": "SOURCE_CATALOG_ONLY",
                   "metrics": metric_catalog(), "models": model_catalog()["models"],
                   "service_mutated": False}
        elif args.action == "history":
            doc = history(args.model)
        elif args.action == "inventory":
            doc = inventory(args.model)
        else:
            from scripts.manager.measurement_bench import benchmark_plan, benchmark_execute
            params = {"contexts_k": args.contexts_k, "max_output_tokens": args.max_output_tokens}
            doc = (benchmark_plan(args.model, **params) if args.action == "benchmark-plan"
                   else benchmark_execute(args.model, ack=args.ack_live_inference, **params))
        if args.save and args.action in ("inventory", "benchmark-execute"):
            doc["evidence_file"] = save_record(doc)
    except (OSError, ValueError, RuntimeError, TypeError) as exc:
        doc = {"schema_version": 1, "action": args.action, "model": args.model,
               "status": "BLOCKED", "issues": [type(exc).__name__ + ":" + str(exc)],
               "service_mutated": False, "production_released": False}
    print(json.dumps(compact(doc) if args.summary_only and args.action != "history"
                     and doc.get("status") != "BLOCKED" else doc,
                     ensure_ascii=False, indent=2, sort_keys=True))
    return 3 if doc["status"] == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
