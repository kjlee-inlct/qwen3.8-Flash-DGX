"""Read-only desired-vs-observed model recipe diff and lifecycle planning.

Historical P3 receipts and migration journals are evidence, NEVER live Docker
identity. The canonical 27B JSON stays immutable. This module does not mutate
Docker, model caches, images, journal, or the active service.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from typing import Any, Callable

from scripts.manager import p2_27b_gpu_trial as gpu
from scripts.manager.service_manifest import policy

ROOT = Path(__file__).resolve().parents[2]
ACTIONS = frozenset(("status", "start", "stop", "restart", "switch", "remove",
                     "install", "reinstall", "recreate"))
PLAN_WINDOW_SECONDS = 600
SHA256 = re.compile(r"^[0-9a-f]{64}$")
IMAGE_ID = re.compile(r"^sha256:[0-9a-f]{64}$")
VALUE_FLAGS = frozenset((
    "--served-model-name", "--host", "--port", "--load-format", "--quantization",
    "--dtype", "--max-model-len", "--max-num-seqs", "--gpu-memory-utilization",
    "--chat-template", "--tool-call-parser", "--reasoning-parser",
))
BOOL_FLAGS = frozenset(("--enforce-eager", "--enable-auto-tool-choice"))
ENV_KEYS = ("HF_HOME", "HF_HUB_OFFLINE")


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True).encode("utf-8")).hexdigest()


def _deny(model: str, action: str, *issues: str) -> dict:
    return {
        "schema_version": 1, "action": "MODEL_RECIPE_LIFECYCLE",
        "model": model, "requested_action": action, "status": "BLOCKED",
        "issues": sorted(set(issues)), "plan_id": None,
        "executed": False, "approval_accepted": False,
        "operations_enabled": False, "production_released": False,
    }


def load_desired(model: str, *, spec: dict | None = None,
                 root: Path = ROOT) -> tuple[dict, str]:
    """Qualified recipes only; never invent Flash/Orcarouter launch parameters."""
    cfg = policy() if spec is None else spec
    if model not in cfg["models"]:
        raise ValueError("UNKNOWN_MODEL")
    desc = cfg["models"][model]
    rel = desc.get("runtime_recipe")
    if not isinstance(rel, str) or not rel.startswith("recipes/"):
        raise ValueError("NO_QUALIFIED_RUNTIME_RECIPE")
    file = root / rel
    if file.is_symlink() or not file.is_file():
        raise ValueError("RECIPE_MISSING_OR_UNTRUSTED")
    raw = file.read_bytes()
    if len(raw) > 32768:
        raise ValueError("RECIPE_TOO_LARGE")
    recipe = json.loads(raw)
    if (recipe.get("schema_version") != 1
            or recipe.get("engine") != "vllm"
            or recipe.get("vllm_version") != "0.32.0"
            or recipe.get("service", {}).get("container_name") != desc["container_name"]
            or recipe.get("model", {}).get("served_id") != desc["served_id"]
            or recipe.get("runtime", {}).get("port") != 8000
            or recipe.get("service", {}).get("api_port") != 8000
            or recipe.get("service", {}).get("one_active_model_only") is not True
            or not IMAGE_ID.fullmatch(str(recipe.get("runtime", {}).get("local_image_id", "")))
            or not re.fullmatch(r"[0-9a-f]{40}", str(recipe.get("model", {}).get("revision", "")))):
        raise ValueError("RECIPE_POLICY_OR_PIN_MISMATCH")
    return recipe, hashlib.sha256(raw).hexdigest()


def command_flags(cmd: Any) -> dict:
    """Normalize vLLM --option=value and --option value without order sensitivity."""
    if (not isinstance(cmd, list) or not cmd or
            not all(isinstance(x, str) and x for x in cmd)):
        raise ValueError("INVALID_DOCKER_CMD")
    result: dict[str, Any] = {}
    positional: list[str] = []
    index = 0
    while index < len(cmd):
        token = cmd[index]
        if not token.startswith("--"):
            positional.append(token)
            index += 1
            continue
        key, sep, inline = token.partition("=")
        key = key.replace("_", "-")
        if key in result:
            raise ValueError("DUPLICATE_DOCKER_CMD_FLAG")
        if key in BOOL_FLAGS:
            if sep:
                raise ValueError("BOOLEAN_FLAG_WITH_VALUE")
            result[key] = True
        elif sep:
            result[key] = inline
        elif index + 1 < len(cmd) and not cmd[index + 1].startswith("--"):
            index += 1
            result[key] = cmd[index]
        else:
            result[key] = True
        index += 1
    if len(positional) != 1 or not positional[0].startswith("/hf/"):
        raise ValueError("UNEXPECTED_MODEL_CHECKPOINT_POSITIONAL")
    result["_checkpoint"] = positional[0]
    for key in ("--max-model-len", "--max-num-seqs", "--port"):
        if key in result:
            try:
                result[key] = str(int(result[key]))
            except (TypeError, ValueError) as exc:
                raise ValueError("INVALID_NUMERIC_DOCKER_CMD_FLAG") from exc
    if "--gpu-memory-utilization" in result:
        try:
            result["--gpu-memory-utilization"] = str(float(result["--gpu-memory-utilization"]))
        except (TypeError, ValueError) as exc:
            raise ValueError("INVALID_GPU_MEMORY_OPTION") from exc
    return dict(sorted(result.items()))


def desired_runtime(recipe: dict, *, cache_source: str | None = None) -> dict:
    m, r = recipe["model"], recipe["runtime"]
    native = recipe.get("native_tools") or {}
    checkpoint = ("/hf/hub/models--" + m["repo_id"].replace("/", "--")
                  + "/snapshots/" + m["revision"])
    cmd = [
        checkpoint, "--served-model-name", m["served_id"],
        "--host", "0.0.0.0", "--port", "8000",
        "--load-format", r["load_format"], "--quantization", m["quantization"],
        "--dtype", r["dtype"], "--max-model-len", str(r["max_model_len"]),
        "--max-num-seqs", str(r["max_num_seqs"]),
        "--gpu-memory-utilization", str(r["gpu_memory_utilization"]),
    ]
    if r.get("enforce_eager") is True:
        cmd.append("--enforce-eager")
    if native.get("enabled") is True:
        cmd += ["--chat-template", native["chat_template"],
                "--enable-auto-tool-choice",
                "--tool-call-parser", native["tool_call_parser"],
                "--reasoning-parser", native["reasoning_parser"]]
    expected = {
        "image_id": r["local_image_id"],
        "cmd": command_flags(cmd),
        "api_port_bindings": ["8000"],
        "hf_mount": {"destination": "/hf", "read_only": True, "type": "bind"},
        "gpu": "all" if r["gpus"] == "all" else "UNQUALIFIED",
        "shm_size": 16 * 1024 ** 3 if r["shm_size"] == "16g" else None,
        "ipc_mode": "host",
        "env": {"HF_HOME": "/hf", "HF_HUB_OFFLINE": "1"},
        "recipe_label": recipe["recipe_id"],
    }
    if cache_source is not None:
        if not isinstance(cache_source, str) or not cache_source.startswith("/"):
            raise ValueError("INVALID_PINNED_CACHE_SOURCE")
        expected["hf_cache_source"] = str(Path(cache_source).resolve())
    return expected


def observed_runtime(doc: dict) -> dict:
    if not isinstance(doc, dict):
        raise ValueError("INVALID_DOCKER_INSPECTION")
    config = doc.get("Config") or {}
    host = doc.get("HostConfig") or {}
    mount = [x for x in (doc.get("Mounts") or [])
             if isinstance(x, dict) and x.get("Destination") == "/hf"]
    if len(mount) != 1:
        hf = {"destination": None, "read_only": None, "type": None}
        source = None
    else:
        hf = {"destination": mount[0]["Destination"],
              "read_only": mount[0].get("RW") is False,
              "type": mount[0].get("Type")}
        source = mount[0].get("Source")
        if isinstance(source, str) and source.startswith("/"):
            source = str(Path(source).resolve())
    env = {}
    for item in config.get("Env") or []:
        if isinstance(item, str) and "=" in item:
            key, value = item.split("=", 1)
            if key in ENV_KEYS:
                env[key] = value
    requests = host.get("DeviceRequests") or []
    gpu_all = any(isinstance(x, dict) and x.get("Count") == -1
                  and any("gpu" in group for group in (x.get("Capabilities") or [])
                          if isinstance(group, list))
                  for x in requests)
    ports = (host.get("PortBindings") or {}).get("8000/tcp")
    return {
        "image_id": doc.get("Image"),
        "cmd": command_flags(config.get("Cmd")),
        "api_port_bindings": sorted(str(x.get("HostPort")) for x in ports
                                    if isinstance(x, dict)) if isinstance(ports, list) else None,
        "hf_mount": hf,
        "hf_cache_source": source,
        "gpu": "all" if gpu_all else "MISSING_OR_PARTIAL",
        "shm_size": host.get("ShmSize"),
        "ipc_mode": host.get("IpcMode"),
        "env": env,
        "recipe_label": (config.get("Labels") or {}).get("blazux.recipe"),
    }


def difference(expected: dict, observed: dict) -> list[dict]:
    """Report semantic runtime deltas, excluding dynamic migration labels and IDs."""
    return [{"field": key, "desired": value, "observed": observed.get(key)}
            for key, value in sorted(expected.items())
            if observed.get(key) != value]


def collect_docker(*, run: Callable[..., Any] = gpu.call,
                   inspect: Callable[..., dict] = gpu.docker_info) -> dict:
    def names(all_containers: bool) -> list[str]:
        argv = ["docker", "ps"] + (["-a"] if all_containers else []) + ["--format", "{{.Names}}"]
        result = run(argv)
        if result.returncode:
            raise RuntimeError("DOCKER_PS_FAILED")
        rows = result.stdout.splitlines()
        if any(not x or x != x.strip() for x in rows) or len(rows) != len(set(rows)):
            raise ValueError("INVALID_DOCKER_NAMES")
        return rows

    all_names = names(True)
    running = names(False)
    if any(x not in all_names for x in running):
        raise ValueError("DOCKER_OBSERVATION_INCONSISTENT")
    docs = {name: inspect(name) for name in all_names}
    if any((d.get("Name") != "/" + name
            or not SHA256.fullmatch(str(d.get("Id") or "")))
           for name, d in docs.items()):
        raise ValueError("DOCKER_IDENTITY_UNVERIFIED")
    from scripts.manager.p2_27b_tool_variant import _gpu_access
    gpu_running = [name for name in running if _gpu_access(docs[name])]
    return {"containers": docs, "running": running, "gpu_running": gpu_running}


def plan(model: str, action: str = "status", *,
         desired_loader: Callable[[str], tuple[dict, str]] = load_desired,
         observer: Callable[[], dict] = collect_docker,
         live: Callable[[], dict] | None = None,
         cache_source: str | None = None,
         now: float | None = None) -> dict:
    """Read-only fresh identity-bound decision. plan_id is NOT execution approval."""
    if action not in ACTIONS:
        return _deny(model, action, "UNSUPPORTED_LIFECYCLE_ACTION")
    try:
        cfg = policy()
        if model not in cfg["models"]:
            return _deny(model, action, "UNKNOWN_MODEL")
        recipe, recipe_sha = desired_loader(model)
        expected = desired_runtime(recipe, cache_source=cache_source)
        snapshot = observer()
        docs = snapshot["containers"]
        running_names = set(snapshot["running"])
        gpu_names = set(snapshot["gpu_running"])
        if not isinstance(docs, dict) or not running_names.issubset(docs):
            raise ValueError("INCOMPLETE_DOCKER_OBSERVATION")
        managed = {key: item["container_name"] for key, item in cfg["models"].items()}
        known = {key: docs.get(name) for key, name in managed.items()}
        current = [key for key, name in managed.items() if name in running_names]
        foreign = sorted(gpu_names - set(managed.values()))
        issues: list[str] = []
        if len(current) > 1 or len(gpu_names) > 1:
            issues.append("ONE_ACTIVE_MODEL_ONLY_VIOLATED")
        if foreign:
            issues.append("FOREIGN_GPU_CONTAINER_RUNNING")
        active = current[0] if len(current) == 1 else None
        target_name = managed[model]
        target = known[model]
        installed = target is not None
        running = target_name in running_names
        if installed:
            observed = observed_runtime(target)
            diffs = difference(expected, observed)
            identity = target.get("Id")
            if not SHA256.fullmatch(str(identity or "")):
                issues.append("TARGET_CONTAINER_ID_UNVERIFIED")
        else:
            observed, diffs, identity = None, [], None
        if active is not None and live is not None:
            live_doc = live()
            if (live_doc.get("status") != "LIVE_SERVICE_VERIFIED"
                    or live_doc.get("observed_model") != active
                    or live_doc.get("issues")):
                issues.append("ACTIVE_API_NOT_VERIFIED")
        decision = "NOOP"
        if action == "status":
            decision = "OBSERVE_ONLY"
        elif action == "stop":
            decision = "STOP" if running else "NOOP"
        elif action == "remove":
            decision = "REMOVE_ACTIVE" if running else ("REMOVE_STOPPED" if installed else "NOOP")
        elif action == "recreate":
            decision = "RECREATE" if installed else "INSTALL"
        elif action == "reinstall":
            decision = "RECREATE" if installed else "INSTALL"
        elif action == "install":
            decision = "NOOP" if installed and not diffs else ("RECREATE" if installed else "INSTALL")
        elif action == "switch" and active == model and not diffs:
            decision = "NOOP"
        elif not installed:
            decision = "INSTALL"
        elif diffs:
            decision = "RECREATE"
        elif running and action == "restart":
            decision = "RESTART_EXISTING"
        elif not running:
            decision = "START_EXISTING"
        if model == "orcarouter":
            issues.append("ORCAROUTER_NOT_RUNTIME_QUALIFIED")
        if action != "status" and decision in ("START_EXISTING", "INSTALL", "RECREATE", "RESTART_EXISTING"):
            if active not in (None, model):
                # A service interruption is required, not implicit consent.
                pass
        if installed and "hf_cache_source" not in expected:
            # The committed recipe pins /hf read-only but not its host path.
            # This is not evidence of a stable host-cache source across recreates.
            advisory = ["HOST_HF_CACHE_SOURCE_NOT_PINNED_IN_RECIPE"]
        else:
            advisory = []
        facts = {
            "kind": "MODEL_LIFECYCLE_READ_ONLY_PLAN_V1",
            "target_model": model, "action": action,
            "recipe_sha": recipe_sha, "target_id": identity,
            "managed_ids": {k: d.get("Id") if d else None for k, d in known.items()},
            "gpu_running": sorted(gpu_names), "active_model": active,
            "decision": decision, "diff": diffs, "window": int((now if now is not None else time.time()) // PLAN_WINDOW_SECONDS),
        }
        plan_id = _digest(facts) if not issues else None
        return {
            "schema_version": 1, "action": "MODEL_RECIPE_LIFECYCLE",
            "model": model, "requested_action": action,
            "status": "BLOCKED" if issues else (
                "DRIFT_REQUIRES_RECREATE" if action == "status" and diffs else
                "READ_ONLY_STATUS" if action == "status" else
                "NO_CHANGE_REQUIRED" if decision == "NOOP" else
                "READY_FOR_OPERATOR_REVIEW_ONLY"),
            "issues": sorted(set(issues)), "advisories": advisory,
            "decision": decision, "installed": installed, "running": running,
            "active_model": active, "container_name": target_name,
            "container_id": identity, "recipe_sha256": recipe_sha,
            "recipe_revision": recipe["model"]["revision"],
            "served_id": recipe["model"]["served_id"], "desired": expected,
            "observed": observed, "diff": diffs, "plan_id": plan_id,
            "expires_at_epoch_seconds": (facts["window"] + 1) * PLAN_WINDOW_SECONDS,
            "executed": False, "approval_accepted": False,
            "operations_enabled": False, "production_released": False,
            "historical_p3_receipts_used_as_live_identity": False,
            "notice": "Read-only preview, NOT an executable approval. "
                      "Production lifecycle executor and live DGX acceptance remain gated.",
        }
    except (OSError, ValueError, TypeError, KeyError, RuntimeError, subprocess.TimeoutExpired,
            json.JSONDecodeError) as exc:
        return _deny(model, action, "LIFECYCLE_PREFLIGHT_UNAVAILABLE:" + type(exc).__name__)
