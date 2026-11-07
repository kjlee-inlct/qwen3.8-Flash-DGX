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
from scripts.manager import operational_audit, p2_27b_gpu_trial as gpu
from scripts.manager.service_status import inspect_live_status

ROOT = Path(__file__).resolve().parents[2]
CPU_SUITES = (
    "test_recipe_drift_cpu.py",
    "test_model_lifecycle_cpu.py",
    "test_operational_switch_cpu.py",
    "test_operational_executor_cpu.py",
    "test_p3_dg_acceptance_cpu.py",
)
PROC_ROOT = Path("/proc")
MODEL_NAMES = ("27b", "flash-next")
SHA = re.compile(r"^[0-9a-f]{64}$")
PID = re.compile(r"pid=(\d+)")


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


def stage_d(snapshot: dict, live: dict, *,
            run: Callable[..., Any] = gpu.call,
            proc_owner: Callable[[int, str], bool] = proc_belongs) -> dict:
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
    port_pid_verified = False
    gpu_pid_verified = False
    try:
        observed = run(["ss", "-H", "-ltnp", "sport = :8000"], timeout=12)
        rows = observed.stdout.splitlines() if observed.returncode == 0 else []
        if len(rows) != 1 or "8000" not in rows[0] or "LISTEN" not in rows[0]:
            issues.append("HOST_PORT_8000_LISTENER_NOT_UNAMBIGUOUS")
        else:
            listener_pids = sorted({int(x) for x in PID.findall(rows[0])})
            if not listener_pids:
                issues.append("HOST_PORT_PROCESS_PID_UNAVAILABLE")
            elif docker_id:
                port_pid_verified = all(proc_owner(pid, docker_id) for pid in listener_pids)
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
        observed_gpu_pids=sorted(set(gpu_pids)),
        port_process_ownership_verified=port_pid_verified,
        gpu_process_exclusivity_verified=gpu_pid_verified,
        limitation="Docker/ss/nvidia-smi/proc evidence only; no GPU workload or mutation.")


def stage_e(snapshot: dict, *, historical: dict | None = None) -> dict:
    """Record observed Flash runtime candidate without QUALIFYING an install."""
    issues: list[str] = []
    docs = snapshot.get("containers") or {}
    flash = docs.get("qwen38-flash")
    qualified = historical if historical is not None else operational_switch.historical_p3_receipts()
    candidate: dict[str, Any] | None = None
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
            details = recipe_drift.observed_runtime(flash)
            candidate = {
                "container_id": ident,
                "image_id": details["image_id"],
                "cmd": details["cmd"],
                "gpu": details["gpu"], "ipc_mode": details["ipc_mode"],
                "env": details["env"], "hf_mount": details["hf_mount"],
                "hf_cache_source": details.get("hf_cache_source"),
                "api_port_bindings": details["api_port_bindings"],
                "shm_size": details["shm_size"],
                "served_id_observed_in_cmd": details["cmd"].get("--served-model-name"),
                "checkpoint_observed_in_cmd": details["cmd"].get("_checkpoint"),
            }
            if candidate["served_id_observed_in_cmd"] != "qwen3.8-flash-next":
                issues.append("FLASH_SERVED_ID_NOT_QUALIFIED")
            if candidate["gpu"] != "all" or candidate["api_port_bindings"] != ["8000"]:
                issues.append("FLASH_GPU_OR_PORT_CONFIG_UNVERIFIED")
            if candidate["hf_mount"] != {"destination": "/hf", "read_only": True, "type": "bind"}:
                issues.append("FLASH_HF_BIND_NOT_READ_ONLY")
        except (ValueError, TypeError, KeyError):
            issues.append("FLASH_RUNTIME_CONFIG_UNPARSEABLE")
    if qualified.get("status") != "LOCAL_P3_A_B_C_RECEIPTS_VERIFIED":
        issues.extend(qualified.get("issues") or ["FLASH_P3_PROVENANCE_MISSING"])
    try:
        recipe, _ = recipe_drift.load_desired("flash-next")
        canonical_recipe_registered = True
        if candidate is not None and isinstance(flash, dict):
            desired = recipe_drift.desired_runtime(
                recipe, cache_source=candidate.get("hf_cache_source"))
            observed = recipe_drift.observed_runtime(flash)
            issues.extend("FLASH_CANONICAL_RECIPE_DRIFT:" + row["field"]
                          for row in recipe_drift.difference(desired, observed))
    except (OSError, ValueError, TypeError, KeyError):
        canonical_recipe_registered = False
    if not canonical_recipe_registered:
        issues.append("FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED")
    return result(
        "P3-E", "READ_ONLY_PASS" if not issues and canonical_recipe_registered
        else "DRAFT_REVIEW_REQUIRED" if candidate and
             set(issues) == {"FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED"}
        else "BLOCKED", issues=issues,
        observed_candidate=candidate, canonical_recipe_registered=canonical_recipe_registered,
        limitation="Observed Docker values are NOT a qualified/released reinstall recipe.")


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


def acceptance(*, cpu_only: bool = False, snapshot_fn=recipe_drift.collect_docker,
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
                ("P3-D", lambda: d_fn(snapshot, live)),
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
    parser.add_argument("--strict", action="store_true",
                        help="nonzero unless all stages actually accepted (not possible in draft)")
    parser.add_argument("--report", help="save the resulting JSON (local file only)")
    args = parser.parse_args(argv)
    if args.plan:
        data = {"action": "P3_D_G_DRAFT_ACCEPTANCE", "status": "PLAN_ONLY",
                "stage_order": ["P3-D", "P3-E", "P3-F", "P3-G"],
                "D": "GPU process/Docker exclusivity and :8000 PID provenance",
                "E": "preserved Flash observed candidate; canonical reinstall recipe qualification",
                "F": "CPU/Fake-DGX regression; generic lifecycle remains unreleased",
                "G": "read-only operating switch/journal; real transfer + rollback not run",
                "executed": False, "production_released": False}
    else:
        data = acceptance(cpu_only=args.cpu_only)
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
