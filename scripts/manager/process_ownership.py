"""P5-D bounded READ-ONLY host process evidence; never a launch admission.

No shell, sudo, write, model inference, stop, or start. Port 8000 may be Docker
NAT (no docker-proxy PID), and even a visible host listener PID is not by itself
proof that the Docker container owns it. GPU query may omit processes on GB10.
"""
from __future__ import annotations

import json
import re
import subprocess
from typing import Callable

from scripts.manager.generic_operations import model_catalog
from scripts.manager.observation_binding import observation_capture

_ID = re.compile(r"^[0-9a-f]{64}$")
_PID = re.compile(r"^[1-9][0-9]*$")
_SS_PID = re.compile(r"pid=([1-9][0-9]*)")


def _run(argv: list[str], runner: Callable = subprocess.run) -> str | None:
    """Fixed bounded argv and stdout. Arbitrary shell and user commands forbidden."""
    try:
        result = runner(argv, capture_output=True, text=True, timeout=6, check=False)
        if result.returncode or not isinstance(result.stdout, str) or len(result.stdout) > 65536:
            return None
        return result.stdout
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None


def _parse_top(text: str | None) -> set[int]:
    if not isinstance(text, str):
        return set()
    lines = [s.strip() for s in text.splitlines() if s.strip()]
    if not lines or lines[0].lower() not in ("pid", "pid "):
        return set()
    values = [line.split()[0] for line in lines[1:]]
    return {int(x) for x in values if _PID.fullmatch(x)}


def _parse_gpu(text: str | None) -> set[int]:
    if not isinstance(text, str):
        return set()
    lines = [s.strip() for s in text.splitlines() if s.strip()]
    if any("not supported" in x.lower() or "no devices" in x.lower()
           for x in lines):
        return set()
    return {int(x.split(",")[0].strip()) for x in lines
            if _PID.fullmatch(x.split(",")[0].strip())}


def _parse_ss(text: str | None) -> set[int]:
    if not isinstance(text, str):
        return set()
    matches = [line for line in text.splitlines() if re.search(
        r":8000(?:\s|$)", line)]
    return {int(pid) for line in matches for pid in _SS_PID.findall(line)}


def ownership_review(model: str, observation: dict | None,
                     inspect: dict | None, docker_top: str | None,
                     ss: str | None, gpu: str | None) -> dict:
    names = model_catalog()["models"]
    if model not in names:
        raise ValueError("UNREGISTERED_MODEL")
    obs = observation if isinstance(observation, dict) else {}
    info = inspect if isinstance(inspect, dict) else {}
    issues = []
    name, cid = obs.get("observed_container"), obs.get("container_id")
    state = info.get("State") if isinstance(info.get("State"), dict) else {}
    image = info.get("Image")
    pid = state.get("Pid")
    if obs.get("status") != "SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE":
        issues.append("P5_C_OBSERVATION_NOT_CORRELATED")
    if (not isinstance(cid, str) or not _ID.fullmatch(cid)
            or info.get("Id") != cid
            or info.get("Name") != "/" + str(name)
            or state.get("Running") is not True
            or not isinstance(pid, int) or isinstance(pid, bool) or pid <= 0):
        issues.append("DOCKER_INSPECT_ID_OR_PID_MISMATCH")
    top_pids = _parse_top(docker_top)
    gpu_pids = _parse_gpu(gpu)
    ss_pids = _parse_ss(ss)
    if not top_pids or pid not in top_pids:
        issues.append("DOCKER_HOST_PID_SET_UNVERIFIED")
    if gpu is None or not gpu_pids:
        issues.append("GPU_PROCESS_QUERY_UNSUPPORTED_OR_EMPTY")
    if gpu_pids and top_pids and not gpu_pids.issubset(top_pids):
        issues.append("FOREIGN_GPU_COMPUTE_PID_OBSERVED")
    if ss is None or not ss_pids:
        issues.append("PORT_8000_HOST_LISTENER_PID_UNAVAILABLE_OR_NAT")
    return {
        "schema_version": 1, "stage": "p5", "action": "ownership-review",
        "scope": "READ_ONLY_PORT_AND_GPU_PID_EVIDENCE_UNQUALIFIED",
        "status": ("OBSERVED_PID_SETS_CONSISTENT_NOT_AUTHORIZED"
                   if not issues else "BLOCKED_PARTIAL_PROCESS_EVIDENCE"),
        "model": model, "runtime_role": obs.get("runtime_role"),
        "container": {"name": name, "id": cid, "inspect_id": info.get("Id"),
                      "image_id": image, "init_pid": pid},
        "docker_host_pids": sorted(top_pids),
        "gpu_compute_pids": sorted(gpu_pids),
        "host_port_8000_listener_pids": sorted(ss_pids),
        "docker_identity_match": not any("DOCKER_INSPECT" in x for x in issues),
        "gpu_pid_subset_of_container": bool(gpu_pids and top_pids
                                            and gpu_pids.issubset(top_pids)),
        "host_port_pid_to_container_verified": False,
        "gpu_exclusivity_verified": False,
        "port_process_ownership_verified": False,
        "issues": sorted(set(issues)), "executed": False,
        "operations_enabled": False, "production_released": False,
        "real_dgx_verified": False, "benchmark_verified": False,
        "note": ("PIDs are volatile and probes are sequential. ss listener may be "
                 "docker-proxy or NAT; no independently authenticated PID-to-container "
                 "mapping, GPU kernel exclusivity, or operator authorization."),
    }


def ownership_capture(model: str, *, observation_probe: Callable | None = None,
                      runner: Callable = subprocess.run) -> dict:
    """Read-only sequential Docker/ss/nvidia-smi snapshots; never model traffic."""
    if model not in model_catalog()["models"]:
        raise ValueError("UNREGISTERED_MODEL")
    observation = (observation_probe or observation_capture)(model)
    name = observation.get("observed_container")
    # Exact model-derived name; may not be shell metacharacters or arbitrary user input.
    if (not isinstance(name, str) or not
            re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,100}", name)):
        return ownership_review(model, observation, {}, None, None, None)
    inspect_text = _run(["docker", "inspect", "--format", "{{json .}}", name], runner)
    try:
        info = json.loads(inspect_text) if inspect_text else {}
        if not isinstance(info, dict):
            info = {}
    except (ValueError, TypeError):
        info = {}
    top = _run(["docker", "top", name, "-eo", "pid"], runner)
    ss = _run(["ss", "-H", "-ltnp", "sport", "=", ":8000"], runner)
    gpu = _run(["nvidia-smi", "--query-compute-apps=pid",
                "--format=csv,noheader,nounits"], runner)
    result = ownership_review(model, observation, info, top, ss, gpu)
    result["action"] = "ownership-capture"
    result["scope"] = "SEQUENTIAL_READ_ONLY_HOST_PROBES_NOT_ATOMIC"
    result["probe_performed"] = True
    return result
