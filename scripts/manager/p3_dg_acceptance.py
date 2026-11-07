"""P3-D/E/F/G single-entry automatic DRAFT acceptance runner.

No Docker mutation, model download, service restart, benchmark promotion,
historic P3 stage replay, or hidden execution path. The launcher runs local
CPU tests and bounded read-only DGX inspections, then returns explicit
per-stage verdicts. Real P3-G transfer/rollback requires an independent
operator acceptance tool and is ALWAYS unexecuted here.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Callable

from scripts.manager import model_lifecycle, operational_switch, recipe_drift
from scripts.manager import flash_recipe_review
from scripts.manager import operational_audit, p2_27b_gpu_trial as gpu
from scripts.manager.service_status import inspect_live_status

ROOT = Path(__file__).resolve().parents[2]
CPU_SUITES = (
    "test_recipe_drift_cpu.py",
    "test_model_lifecycle_cpu.py",
    "test_operational_switch_cpu.py",
    "test_operational_executor_cpu.py",
    "test_p3_dg_acceptance_cpu.py",
    "test_flash_recipe_draft_cpu.py",
)
PROC_ROOT = Path("/proc")
MODEL_NAMES = ("27b", "flash-next")
SHA = re.compile(r"^[0-9a-f]{64}$")
PID = re.compile(r"pid=(\d+)")
# P1/P3 accepted NVIDIA source snapshot. -fp8hybrid is a prepared local
# derivative (NOT a 40-hex Hugging Face revision or an independent model).
FLASH_PINNED_REVISION = "fc694b54fb0174e0913e6adf86691ef85a4ead47"
FLASH_REPO_CACHE = "models--nvidia--Qwen3.8-Flash-Next-NVFP4"
FLASH_SNAPSHOT_PREFIX = "/hf/hub/" + FLASH_REPO_CACHE + "/snapshots/"


def result(stage: str, status: str, *, issues: list[str] | None = None,
           **facts: Any) -> dict:
    return {"stage": stage, "status": status, "issues": sorted(set(issues or [])),
            "executed": False, "operations_enabled": False, **facts}


def proc_belongs(pid: int, docker_id: str, *, root: Path = PROC_ROOT) -> bool:
    """Conservative proof via a readable Linux process cgroup identity.

    No permission, namespace ambiguity or missing proc info can yield PASS.
    """
    if not isinstance(pid, int) or pid < 1 or not SHA.fullmatch(str(docker_id)):
        return False
    path = root / str(pid) / "cgroup"
    try:
        content = path.read_text()
    except (OSError, UnicodeError):
        return False
    return docker_id in content or docker_id[:12] in content


def _ss_local_port_8000(row: str) -> bool:
    """Parse the LOCAL listening socket, never the peer's ':8000' text."""
    columns = row.split()
    if len(columns) < 5 or columns[0] != "LISTEN":
        return False
    host, sep, port = columns[3].rpartition(":")
    return bool(sep and host and port == "8000")


def _ss_port_listeners(output: str) -> list[str]:
    """Permit IPv4 + IPv6 dual-stack listeners and reject unrelated sockets."""
    rows = output.splitlines()
    if len(rows) > 32 or any(len(row) > 4096 for row in rows):
        raise ValueError("UNBOUNDED_SS_OUTPUT")
    return [row for row in rows if _ss_local_port_8000(row)]


def docker_proxy_belongs(pid: int, doc: dict, *, root: Path = PROC_ROOT) -> bool:
    """Read-only Docker proxy attribution: exact target container IP + :8000.

    docker-proxy runs in the HOST cgroup, so /proc/PID/cgroup never carries
    the application container's Docker ID. Accept it only if its real /proc
    argv is the TCP proxy for :8000 and forwards to an IP recorded by Docker
    inspect for the qualified active container, with a matching published
    HostConfig port. Missing/ambiguous evidence ALWAYS fails closed.
    """
    if not isinstance(pid, int) or pid < 1 or not isinstance(doc, dict):
        return False
    net = doc.get("NetworkSettings") or {}
    networks = net.get("Networks") or {}
    ips = set()
    for details in networks.values() if isinstance(networks, dict) else []:
        if isinstance(details, dict):
            ips.update(x for x in (details.get("IPAddress"),
                                   details.get("GlobalIPv6Address"))
                       if isinstance(x, str) and x)
    bindings = ((doc.get("HostConfig") or {}).get("PortBindings") or {}).get("8000/tcp")
    if not ips or not isinstance(bindings, list) or not bindings:
        return False
    try:
        raw = (root / str(pid) / "cmdline").read_bytes()
        if not raw or len(raw) > 8192:
            return False
        argv = [x.decode("utf-8") for x in raw.split(bytes([0])) if x]
        if not argv or Path(argv[0]).name not in ("docker-proxy", "docker-proxy-current"):
            return False
        opts: dict[str, str] = {}
        i = 1
        while i + 1 < len(argv):
            if argv[i] in ("-proto", "-host-ip", "-host-port",
                           "-container-ip", "-container-port"):
                if argv[i] in opts:
                    return False
                opts[argv[i]] = argv[i + 1]
                i += 2
            else:
                i += 1
        if (opts.get("-proto") != "tcp"
                or opts.get("-host-port") != "8000"
                or opts.get("-container-port") != "8000"
                or opts.get("-container-ip") not in ips):
            return False
        host_ip = opts.get("-host-ip")
        return bool(host_ip and any(
            isinstance(bind, dict) and str(bind.get("HostPort")) == "8000"
            and bind.get("HostIp", "") in ("", host_ip)
            for bind in bindings))
    except (OSError, UnicodeError, ValueError, TypeError):
        return False


def stage_d(snapshot: dict, live: dict, *,
            run: Callable[..., Any] = gpu.call,
            proc_owner: Callable[[int, str], bool] = proc_belongs,
            proxy_owner: Callable[[int, dict], bool] = docker_proxy_belongs,
            allow_sudo_ss: bool = False) -> dict:
    """GPU/container + host port/process checks; unknown is NOT a pass."""
    issues: list[str] = []
    running = snapshot.get("running")
    gpu_names = snapshot.get("gpu_running")
    ports = snapshot.get("port_owners")
    docs = snapshot.get("containers")
    if not all(isinstance(x, list) for x in (running, gpu_names, ports)) or not isinstance(docs, dict):
        return result("P3-D", "BLOCKED", issues=["DOCKER_SNAPSHOT_MALFORMED"])
    active = live.get("observed_model")
    expected_name = recipe_drift.policy().get("models", {}).get(active or "", {}).get("container_name")
    doc = docs.get(expected_name)
    if live.get("status") != "LIVE_SERVICE_VERIFIED" or live.get("issues"):
        issues.append("ACTIVE_API_IDENTITY_NOT_VERIFIED")
    if not isinstance(doc, dict) or expected_name not in running:
        issues.append("ACTIVE_DOCKER_CONTAINER_UNKNOWN")
        docker_id = None
    else:
        docker_id = doc.get("Id")
        if not SHA.fullmatch(str(docker_id)):
            issues.append("ACTIVE_DOCKER_ID_UNVERIFIED")
    if gpu_names != [expected_name] and sorted(gpu_names) != [expected_name]:
        issues.append("DOCKER_GPU_EXCLUSIVITY_NOT_VERIFIED")
    if sorted(ports) != [expected_name]:
        issues.append("DOCKER_HOST_8000_OWNER_NOT_EXCLUSIVE")
    listener_pids: list[int] = []
    gpu_pids: list[int] = []
    port_listener_rows: list[str] = []
    ss_returncode: int | None = None
    ss_diagnostic: str | None = None
    port_pid_verified = False
    port_pid_attribution: dict[str, str] = {}
    gpu_pid_verified = False
    try:
        observed = run(["ss", "-H", "-ltnp", "sport = :8000"], timeout=12)
        ss_returncode = observed.returncode
        if observed.returncode:
            ss_diagnostic = str(getattr(observed, "stderr", "") or "")[:300]
            issues.append("HOST_PORT_SS_QUERY_FAILED")
        else:
            # Docker can publish BOTH 0.0.0.0:8000 and [::]:8000.
            # Every listening socket must have independently attributable PIDs.
            port_listener_rows = _ss_port_listeners(observed.stdout)
            if not port_listener_rows:
                issues.append("HOST_PORT_8000_LISTENER_NOT_OBSERVED")
            elif len(port_listener_rows) > 4:
                issues.append("HOST_PORT_8000_LISTENER_COUNT_UNEXPECTED")
            else:
                if any(not PID.findall(row) for row in port_listener_rows) and allow_sudo_ss:
                    # Only explicitly requested, non-interactive, read-only
                    # root socket inventory. A changed/partial snapshot is not
                    # allowed to attest ownership of the earlier sockets.
                    elevated = run(
                        ["sudo", "-n", "ss", "-H", "-ltnp", "sport = :8000"],
                        timeout=12)
                    if elevated.returncode:
                        issues.append("HOST_PORT_PRIVILEGED_SS_UNAVAILABLE")
                    else:
                        fresh_rows = _ss_port_listeners(elevated.stdout)
                        local = lambda rows: sorted(row.split()[3] for row in rows)
                        if local(fresh_rows) != local(port_listener_rows):
                            issues.append("HOST_PORT_PRIVILEGED_SS_SNAPSHOT_CHANGED")
                        else:
                            port_listener_rows = fresh_rows
                if any(not PID.findall(row) for row in port_listener_rows):
                    issues.append("HOST_PORT_PROCESS_PID_UNAVAILABLE")
                else:
                    listener_pids = sorted({int(pid) for row in port_listener_rows
                                           for pid in PID.findall(row)})
                    if docker_id and isinstance(doc, dict):
                        for pid in listener_pids:
                            if proc_owner(pid, docker_id):
                                port_pid_attribution[str(pid)] = "CONTAINER_CGROUP"
                            elif proxy_owner(pid, doc):
                                port_pid_attribution[str(pid)] = "QUALIFIED_DOCKER_PROXY"
                            else:
                                port_pid_attribution[str(pid)] = "UNVERIFIED"
                        port_pid_verified = all(v != "UNVERIFIED"
                                                for v in port_pid_attribution.values())
                        if not port_pid_verified:
                            issues.append("HOST_PORT_PROCESS_CONTAINER_OWNERSHIP_UNVERIFIED")
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
        issues.append("HOST_PORT_PROCESS_AUDIT_UNAVAILABLE")
    try:
        gpu_observed = run(
            ["nvidia-smi", "--query-compute-apps=pid,process_name",
             "--format=csv,noheader"], timeout=15)
        if gpu_observed.returncode:
            issues.append("GPU_COMPUTE_PROCESS_QUERY_UNAVAILABLE")
        else:
            for row in gpu_observed.stdout.splitlines():
                if not row.strip():
                    continue
                first = row.split(",", 1)[0].strip()
                if not first.isdigit() or int(first) < 1:
                    issues.append("GPU_COMPUTE_PROCESS_ROW_UNRECOGNIZED")
                    continue
                gpu_pids.append(int(first))
            if not gpu_pids:
                issues.append("GPU_COMPUTE_PROCESS_OWNER_NOT_OBSERVED")
            elif docker_id:
                gpu_pid_verified = all(proc_owner(pid, docker_id) for pid in gpu_pids)
                if not gpu_pid_verified:
                    issues.append("GPU_COMPUTE_PROCESS_CONTAINER_OWNERSHIP_UNVERIFIED")
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired):
        issues.append("GPU_COMPUTE_PROCESS_AUDIT_UNAVAILABLE")
    return result(
        "P3-D", "READ_ONLY_PASS" if not issues and port_pid_verified and gpu_pid_verified
        else "BLOCKED", issues=issues,
        active_model=active, docker_gpu_containers=gpu_names,
        docker_host_port_owners=ports, observed_port_pids=listener_pids,
        observed_port_listener_rows=[row[:350] for row in port_listener_rows],
        ss_returncode=ss_returncode, ss_diagnostic=ss_diagnostic,
        port_pid_attribution=port_pid_attribution,
        observed_gpu_pids=sorted(set(gpu_pids)),
        port_process_ownership_verified=port_pid_verified,
        sudo_ss_requested=allow_sudo_ss,
        gpu_process_exclusivity_verified=gpu_pid_verified,
        limitation="Docker/ss/nvidia-smi/proc evidence only; no GPU workload or mutation.")


def _flash_arg(cmd: list[str], key: str) -> str | None:
    """Extract one exact vLLM flag without inventing defaults for old commands."""
    matches: list[str] = []
    for index, token in enumerate(cmd):
        if token == key:
            if index + 1 < len(cmd) and not cmd[index + 1].startswith("--"):
                matches.append(cmd[index + 1])
            else:
                return None
        elif token.startswith(key + "="):
            matches.append(token[len(key) + 1:])
    return matches[0] if len(matches) == 1 else None


def flash_observed_candidate(flash: dict) -> tuple[dict, list[str], list[str]]:
    """Inventory the *actual* legacy Flash argv, without 27B-only normalization.

    The original Flash launcher has a larger flag set than the canonical 27B
    runtime and historically used a writable /hf bind. Neither can be silently
    converted into a production reinstall recipe. Report exact observed facts
    and model-specific review gaps; reject uncertain model/port/GPU identity.
    """
    issues: list[str] = []
    advisories: list[str] = []
    config = flash.get("Config") or {}
    host = flash.get("HostConfig") or {}
    cmd = config.get("Cmd")
    if (not isinstance(cmd, list) or not 1 <= len(cmd) <= 256
            or any(not isinstance(x, str) or not x or len(x) > 4096 for x in cmd)):
        raise ValueError("FLASH_CMD_MISSING_OR_UNBOUNDED")
    checkpoints = [x for x in cmd if x.startswith(FLASH_SNAPSHOT_PREFIX)]
    checkpoint = checkpoints[0] if len(checkpoints) == 1 else None
    observed_revision = (checkpoint[len(FLASH_SNAPSHOT_PREFIX):]
                         if checkpoint else None)
    # Legacy Flash can run the NVIDIA pinned source snapshot in its original
    # form or from the *prepared* fp8hybrid derived view in the SAME cache.
    # The variant suffix is not an HF revision. No automatic requalification.
    checkpoint_variant = "SOURCE_NVFP4"
    if observed_revision == FLASH_PINNED_REVISION + "-fp8hybrid":
        checkpoint_variant = "LOCAL_PREPARED_FP8HYBRID"
    elif observed_revision != FLASH_PINNED_REVISION:
        issues.append("FLASH_CHECKPOINT_REVISION_UNVERIFIED")
    hybrid_preparation_verified = None
    if checkpoint_variant == "LOCAL_PREPARED_FP8HYBRID":
        cache = None
        for value in flash.get("Mounts") or []:
            if isinstance(value, dict) and value.get("Destination") == "/hf":
                cache = value.get("Source")
                break
        if not isinstance(cache, str) or not cache.startswith("/"):
            issues.append("FLASH_HYBRID_CACHE_SOURCE_UNVERIFIED")
            hybrid_preparation_verified = False
        else:
            view = Path(cache) / "hub" / FLASH_REPO_CACHE / "snapshots" / observed_revision
            # No writes: matches the exact .prepared sentinel and minimum
            # index/config/tokenizer assets checked by serve_flash-next.sh.
            essentials = ("config.json", "tokenizer.json",
                          "tokenizer_config.json", "model.safetensors.index.json")
            try:
                hybrid_preparation_verified = (
                    (view / ".prepared").is_file()
                    and all((view / name).is_file() for name in essentials))
            except (OSError, ValueError):
                hybrid_preparation_verified = False
            if not hybrid_preparation_verified:
                issues.append("FLASH_HYBRID_PREPARED_VIEW_UNVERIFIED")
    served = _flash_arg(cmd, "--served-model-name")
    if served != "qwen3.8-flash-next":
        issues.append("FLASH_SERVED_ID_NOT_QUALIFIED")
    if _flash_arg(cmd, "--port") != "8000":
        issues.append("FLASH_INTERNAL_PORT_UNVERIFIED")
    mounts = [m for m in flash.get("Mounts") or []
              if isinstance(m, dict) and m.get("Destination") == "/hf"]
    mount = mounts[0] if len(mounts) == 1 else {}
    mount_info = {
        "destination": mount.get("Destination"),
        "read_only": mount.get("RW") is False,
        "type": mount.get("Type"),
    }
    source = mount.get("Source")
    if (mount_info.get("destination") != "/hf"
            or mount_info.get("type") != "bind"
            or not isinstance(source, str) or not source.startswith("/")):
        issues.append("FLASH_HOST_HF_CACHE_BIND_UNVERIFIED")
    if mount and mount.get("RW") is True:
        advisories.append("FLASH_LEGACY_HF_MOUNT_WRITABLE_REINSTALL_REVIEW")
    env: dict[str, str] = {}
    for value in config.get("Env") or []:
        if isinstance(value, str) and "=" in value:
            k, v = value.split("=", 1)
            if k in ("HF_HOME", "HF_HUB_OFFLINE"):
                env[k] = v
    if env.get("HF_HOME") != "/hf" or env.get("HF_HUB_OFFLINE") != "1":
        issues.append("FLASH_OFFLINE_CACHE_ENV_UNVERIFIED")
    requests = host.get("DeviceRequests") or []
    all_gpu = any(isinstance(req, dict)
                  and req.get("Count") == -1
                  and any(isinstance(group, list) and "gpu" in group
                          for group in req.get("Capabilities") or [])
                  for req in requests)
    if not all_gpu:
        issues.append("FLASH_GPU_CONFIGURATION_UNVERIFIED")
    port_bindings = (host.get("PortBindings") or {}).get("8000/tcp")
    ports = sorted(str(v.get("HostPort")) for v in port_bindings
                   if isinstance(v, dict)) if isinstance(port_bindings, list) else []
    if not ports or any(v != "8000" for v in ports):
        issues.append("FLASH_HOST_PORT_CONFIGURATION_UNVERIFIED")
    normalized = None
    normalization_error = None
    normalizer_profile = ("FLASH_FP8HYBRID_READ_ONLY_V1"
                          if checkpoint_variant == "LOCAL_PREPARED_FP8HYBRID"
                          else "LEGACY_SOURCE_OBSERVATION_V1")
    try:
        if checkpoint_variant == "LOCAL_PREPARED_FP8HYBRID":
            normalized = flash_recipe_review.normalize_fp8hybrid_cmd(cmd)
        else:
            # Source-only historical fallback; never a canonical Flash
            # install/reinstall recipe.
            normalized = recipe_drift.command_flags(cmd)
    except (ValueError, TypeError) as exc:
        normalization_error = str(exc)[:120]
        advisories.append("FLASH_LEGACY_COMMAND_NEEDS_MODEL_SPECIFIC_NORMALIZER")
    candidate = {
        "container_id": flash.get("Id"),
        "image_id": flash.get("Image"),
        "raw_cmd": cmd,
        "entrypoint": config.get("Entrypoint"),
        "cmd": normalized,
        "cmd_normalization_error": normalization_error,
        "cmd_normalization_profile": normalizer_profile,
        "cmd_normalized": normalized is not None,
        "gpu": "all" if all_gpu else "UNVERIFIED",
        "ipc_mode": host.get("IpcMode"), "env": env,
        "hf_mount": mount_info, "hf_cache_source": source,
        "api_port_bindings": ports,
        "shm_size": host.get("ShmSize"),
        "served_id_observed_in_cmd": served,
        "checkpoint_observed_in_cmd": checkpoint,
        "source_revision": FLASH_PINNED_REVISION,
        "observed_checkpoint_revision_or_view": observed_revision,
        "checkpoint_variant": checkpoint_variant,
        "hybrid_preparation_verified": hybrid_preparation_verified,
    }
    return candidate, issues, advisories


def stage_e(snapshot: dict, *, historical: dict | None = None) -> dict:
    """Flash discovery is read-only; observed legacy argv is NOT install approval."""
    issues: list[str] = []
    advisories: list[str] = []
    docs = snapshot.get("containers") or {}
    flash = docs.get("qwen38-flash")
    qualified = historical if historical is not None else operational_switch.historical_p3_receipts()
    candidate: dict[str, Any] | None = None
    draft_review: dict[str, Any] | None = None
    if not isinstance(flash, dict):
        issues.append("FLASH_PRESERVED_CONTAINER_NOT_FOUND")
    else:
        ident = flash.get("Id")
        a = (qualified.get("records") or {}).get("a") or {}
        if (not SHA.fullmatch(str(ident or "")) or ident != a.get("flash_id")
                or flash.get("Image") != a.get("flash_image")):
            issues.append("FLASH_HISTORICAL_PROVENANCE_UNVERIFIED")
        if (flash.get("State") or {}).get("Running") is True:
            issues.append("FLASH_ACTIVE_SOURCE_NOT_SAFE_TO_CLASSIFY_AS_PRESERVED")
        try:
            candidate, command_issues, advisories = flash_observed_candidate(flash)
            issues.extend(command_issues)
            draft_review = flash_recipe_review.compare_observation(candidate, flash)
        except (ValueError, TypeError, KeyError):
            issues.append("FLASH_RUNTIME_CONFIG_UNPARSEABLE")
    if qualified.get("status") != "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED":
        issues.extend(qualified.get("issues") or ["FLASH_P3_PROVENANCE_MISSING"])
    try:
        recipe, _ = recipe_drift.load_desired("flash-next")
        canonical_recipe_registered = True
        if candidate is not None and isinstance(flash, dict):
            try:
                desired = recipe_drift.desired_runtime(
                    recipe, cache_source=candidate.get("hf_cache_source"))
                observed = recipe_drift.observed_runtime(flash)
                issues.extend("FLASH_CANONICAL_RECIPE_DRIFT:" + row["field"]
                              for row in recipe_drift.difference(desired, observed))
            except (ValueError, TypeError, KeyError):
                issues.append("FLASH_CANONICAL_RECIPE_NORMALIZER_UNQUALIFIED")
    except (OSError, ValueError, TypeError, KeyError):
        canonical_recipe_registered = False
    if not canonical_recipe_registered:
        issues.append("FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED")
    only_recipe_missing = (
        set(issues) == {"FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED"})
    return result(
        "P3-E", "READ_ONLY_PASS" if not issues and canonical_recipe_registered
        else "DRAFT_REVIEW_REQUIRED" if candidate and only_recipe_missing
        else "BLOCKED", issues=issues, advisories=advisories,
        observed_candidate=candidate, canonical_recipe_registered=canonical_recipe_registered,
        source_draft_field_review=draft_review,
        limitation="Legacy observed Flash argv, flags and writable cache are NOT a qualified reinstall recipe.")


def stage_f(*, suites: tuple[str, ...] = CPU_SUITES,
            test_runner: Callable[..., Any] = subprocess.run,
            root: Path = ROOT) -> dict:
    """CPU-only Fake-DGX regression tests, without hardware mutation."""
    tests: list[dict[str, Any]] = []
    issues: list[str] = []
    count = 0
    for suite in suites:
        if suite not in CPU_SUITES:
            issues.append("UNAPPROVED_TEST_SUITE:" + str(suite))
            continue
        args = [sys.executable, "-m", "unittest", "discover", "-s", "tests",
                "-p", suite, "-v"]
        try:
            out = test_runner(args, cwd=str(root), capture_output=True,
                              text=True, timeout=120, check=False)
            log = (out.stdout or "") + "\n" + (out.stderr or "")
            counts = re.findall(r"Ran (\d+) tests? in ", log)
            n = int(counts[-1]) if len(counts) == 1 else 0
            passed = out.returncode == 0 and n > 0 and "\nOK" in log
            if passed:
                count += n
            else:
                issues.append("CPU_REGRESSION_FAILED:" + suite)
            tests.append({"suite": suite, "status": "PASS" if passed else "FAILED",
                          "tests": n, "exit_code": out.returncode,
                          "diagnostic_tail": "" if passed else log[-1600:]})
        except (OSError, ValueError, subprocess.TimeoutExpired) as exc:
            issues.append("CPU_REGRESSION_UNAVAILABLE:" + suite)
            tests.append({"suite": suite, "status": "BLOCKED",
                          "exception": type(exc).__name__})
    release_gated = model_lifecycle.PRODUCTION_LIFECYCLE_RELEASED is False
    if not release_gated:
        issues.append("LIFECYCLE_RELEASE_GATE_UNEXPECTEDLY_ENABLED")
    return result("P3-F", "SOURCE_CPU_PASS_NOT_RELEASED" if not issues else "BLOCKED",
                  issues=issues, suites=tests, passed_test_count=count,
                  production_lifecycle_released=not release_gated,
                  limitation="CPU tests do not prove actual DGX failover, recovery or safety.")


def stage_g(live: dict, *, planner: Callable[[str], dict] = operational_switch.make_plan,
            auditor: Callable[[], dict] = lambda: operational_audit.inspect_journal(operational_switch.ROOT)) -> dict:
    """Read-only recurrent-switch and historic journal preflight only."""
    target = "flash-next" if live.get("observed_model") == "27b" else "27b"
    issues: list[str] = []
    try:
        plan = planner(target)
        journal = auditor()
    except (OSError, RuntimeError, ValueError, TypeError) as exc:
        return result("P3-G", "BLOCKED", issues=["OPERATING_PREFLIGHT_FAILED:" + type(exc).__name__])
    if plan.get("status") != operational_switch.READY or plan.get("issues"):
        issues.extend(plan.get("issues") or ["OPERATING_PREVIEW_NOT_READY"])
    if plan.get("status") == operational_switch.READY and plan.get(
            "current_ids_from_live_docker") is not True:
        issues.append("OPERATING_PREVIEW_CURRENT_DOCKER_ID_NOT_VERIFIED")
    if (journal.get("status") not in ("VERIFIED", "EMPTY")
            or journal.get("issues")):
        issues.extend(journal.get("issues") or ["OPERATING_JOURNAL_NOT_VERIFIED"])
    return result(
        "P3-G", "PREVIEW_PASS_REAL_SWITCH_NOT_RUN" if not issues else "BLOCKED",
        issues=issues, source_model=plan.get("source_model"), target_model=target,
        source_lineage=plan.get("source_lineage"),
        target_lineage=plan.get("target_lineage"),
        current_ids_from_live_docker=plan.get("current_ids_from_live_docker") is True,
        journal_status=journal.get("status"), journal_phase=journal.get("phase"),
        real_bidirectional_switch_executed=False,
        real_fault_injection_and_rollback_verified=False,
        limitation="No mutation and no independent operator execution consent.")


def acceptance(*, cpu_only: bool = False, allow_sudo_ss: bool = False,
               snapshot_fn=recipe_drift.collect_docker,
               live_fn=inspect_live_status, p3_fn=operational_switch.historical_p3_receipts,
               d_fn=stage_d, e_fn=stage_e, f_fn=stage_f, g_fn=stage_g) -> dict:
    """Continue through all stages after individual probe failures."""
    none = lambda stage: result(stage, "NOT_RUN_CPU_ONLY", issues=["ACTUAL_DGX_READ_ONLY_PROBE_NOT_RUN"])
    sections = {"P3-D": none("P3-D"), "P3-E": none("P3-E"),
                "P3-F": result("P3-F", "BLOCKED", issues=["CPU_REGRESSION_NOT_RUN"]),
                "P3-G": none("P3-G")}
    if not cpu_only:
        snapshot = None
        live = None
        try:
            snapshot = snapshot_fn()
            live = live_fn()
        except (OSError, ValueError, RuntimeError, TypeError,
                KeyError, subprocess.TimeoutExpired) as exc:
            for key in ("P3-D", "P3-E", "P3-G"):
                sections[key] = result(key, "BLOCKED", issues=[
                    "DGX_READ_ONLY_OBSERVATION_UNAVAILABLE:" + type(exc).__name__])
        if snapshot is not None and live is not None:
            for key, probe in (
                ("P3-D", lambda: (d_fn(snapshot, live, allow_sudo_ss=True)
                                  if allow_sudo_ss else d_fn(snapshot, live))),
                ("P3-E", lambda: e_fn(snapshot, historical=p3_fn())),
            ):
                try:
                    sections[key] = probe()
                except (OSError, ValueError, RuntimeError, TypeError, KeyError,
                        subprocess.TimeoutExpired) as exc:
                    sections[key] = result(key, "BLOCKED", issues=[
                        "STAGE_READ_ONLY_PROBE_FAILED:" + type(exc).__name__])
    try:
        sections["P3-F"] = f_fn()
    except (OSError, ValueError, RuntimeError, TypeError,
            subprocess.TimeoutExpired) as exc:
        sections["P3-F"] = result("P3-F", "BLOCKED", issues=[
            "CPU_TEST_RUNNER_UNAVAILABLE:" + type(exc).__name__])
    if not cpu_only and snapshot is not None and live is not None:
        try:
            sections["P3-G"] = g_fn(live)
        except (OSError, ValueError, RuntimeError, TypeError, KeyError,
                subprocess.TimeoutExpired) as exc:
            sections["P3-G"] = result("P3-G", "BLOCKED", issues=[
                "STAGE_READ_ONLY_PROBE_FAILED:" + type(exc).__name__])
    blocked = [key for key, part in sections.items() if part["status"] == "BLOCKED"]
    return {
        "schema_version": 1, "action": "P3_D_G_DRAFT_ACCEPTANCE",
        "status": "BLOCKED" if blocked else
                  "CPU_ONLY_SOURCE_PASS_NOT_DGX" if cpu_only else
                  "DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED",
        "stage_order": list(sections), "stages": sections,
        "blocked_stages": blocked, "acceptance_complete": False,
        "real_switch_executed": False, "executed": False,
        "operations_enabled": False, "production_released": False,
        "scope": "CPU_AND_DGX_READ_ONLY" if not cpu_only else "CPU_ONLY",
        "notice": ("Single-script D-G DRAFT only. No real transfer, reinstall, "
                   "fault injection or automatic execution. P3-G real acceptance "
                   "and production release require a separate explicit operator action."),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="P3-D through P3-G single-entry READ-ONLY draft acceptance")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true", help="show stage contract; no probes")
    mode.add_argument("--run", action="store_true", help="CPU tests + DGX read-only probes")
    mode.add_argument("--cpu-only", action="store_true", help="CPU regression only")
    parser.add_argument("--sudo-ss", action="store_true",
                        help="explicitly allow sudo -n ss read-only PID fallback; no password prompt")
    parser.add_argument("--strict", action="store_true",
                        help="nonzero unless all stages actually accepted (not possible in draft)")
    parser.add_argument("--report", help="save the resulting JSON (local file only)")
    args = parser.parse_args(argv)
    if args.sudo_ss and not args.run:
        parser.error("--sudo-ss requires --run, never --plan or --cpu-only")
    if args.plan:
        data = {"action": "P3_D_G_DRAFT_ACCEPTANCE", "status": "PLAN_ONLY",
                "stage_order": ["P3-D", "P3-E", "P3-F", "P3-G"],
                "D": "GPU process/Docker exclusivity and :8000 PID provenance",
                "E": "preserved Flash observed candidate; canonical reinstall recipe qualification",
                "F": "CPU/Fake-DGX regression; generic lifecycle remains unreleased",
                "G": "read-only operating switch/journal; real transfer + rollback not run",
                "executed": False, "production_released": False}
    else:
        data = acceptance(cpu_only=args.cpu_only, allow_sudo_ss=args.sudo_ss)
    encoded = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.report:
        path = Path(args.report).expanduser()
        if path.is_symlink() or not path.parent.is_dir():
            parser.error("report parent unavailable or symlink")
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as output:
            output.write(encoded)
    print(encoded, end="")
    if args.strict and not args.plan and not data.get("acceptance_complete"):
        return 3
    return 3 if data.get("status") == "BLOCKED" else 0


if __name__ == "__main__":
    raise SystemExit(main())
