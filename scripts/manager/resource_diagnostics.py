"""Non-mutating DGX resource observations for active P5 Orcarouter.

No Docker start/stop, inference, sysctl, governor, power or cgroup writes.
All unavailable sensor values remain explicitly unsupported/unobserved.
Use --save only to persist private JSON evidence, never runtime state.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parents[2]
RECIPE = ROOT / "recipes/qwen38-orcarouter.runtime.json"
PROC = Path("/proc")
SYS = Path("/sys")
GIB = 1024 ** 3
_ALLOWED = re.compile(r"^[A-Za-z0-9_.-]{2,100}$")


def _read(path: Path, limit: int = 65536) -> str | None:
    try:
        if path.is_symlink() or not path.is_file() or path.stat().st_size > limit:
            return None
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except (OSError, UnicodeError, ValueError):
        return None


def _kv_bytes(raw: str | None) -> dict[str, int]:
    values = {}
    for line in (raw or "").splitlines():
        match = re.fullmatch(r"([A-Za-z_()]+):\s+(\d+)\s*(kB)?\s*", line)
        if match:
            values[match[1]] = int(match[2]) * (1024 if match[3] else 1)
    return values



def _flat_counts(raw: str | None) -> dict[str, int]:
    """Read space-delimited kernel counters without inventing absent entries."""
    result = {}
    for line in (raw or "").splitlines():
        match = re.fullmatch(r"([a-zA-Z0-9_]+)\s+(\d+)\s*", line)
        if match:
            result[match[1]] = int(match[2])
    return result


def _vmstat(proc: Path) -> dict:
    """Host-wide cumulative page/swap counters, not evidence of live swap churn."""
    fields = _flat_counts(_read(proc / "vmstat"))
    names = ("pswpin", "pswpout", "pgmajfault")
    return {"status": "OBSERVED_CUMULATIVE" if any(k in fields for k in names)
            else "UNSUPPORTED",
            "counters": {k: fields.get(k) for k in names}}

def _pressure(path: Path) -> dict:
    raw = _read(path)
    if raw is None:
        return {"status": "UNSUPPORTED", "some": None, "full": None}
    values = {}
    for line in raw.splitlines():
        words = line.split()
        if not words or words[0] not in ("some", "full"):
            continue
        try:
            fields = dict(x.split("=", 1) for x in words[1:])
            values[words[0]] = {
                key: float(fields[key]) if key.startswith("avg") else int(fields[key])
                for key in ("avg10", "avg60", "avg300", "total") if key in fields
            }
        except (ValueError, TypeError):
            continue
    return {"status": "OBSERVED" if values else "UNSUPPORTED",
            "some": values.get("some"), "full": values.get("full")}


def _cpu(sysfs: Path) -> dict:
    observed = []
    per_cpu = {}
    governors = set()
    bounds = []
    for folder in sorted((sysfs / "devices/system/cpu").glob("cpu[0-9]*/cpufreq")):
        raw = _read(folder / "scaling_cur_freq")
        if raw is None:
            continue
        try:
            mhz = round(int(raw.strip()) / 1000, 1)
            observed.append(mhz)
            per_cpu[folder.parent.name] = mhz
        except ValueError:
            continue
        gov = _read(folder / "scaling_governor")
        if gov:
            governors.add(gov.strip())
        minimum = _read(folder / "scaling_min_freq")
        maximum = _read(folder / "scaling_max_freq")
        if minimum and maximum:
            try:
                bounds.append([round(int(minimum.strip()) / 1000, 1),
                               round(int(maximum.strip()) / 1000, 1)])
            except ValueError:
                pass
    return {"status": "OBSERVED" if observed else "UNSUPPORTED",
            "count": len(observed), "per_cpu_current_mhz": per_cpu,
            "current_mhz_min": min(observed) if observed else None,
            "current_mhz_max": max(observed) if observed else None,
            "current_mhz_mean": round(sum(observed) / len(observed), 1) if observed else None,
            "governors": sorted(governors),
            "policy_min_mhz": min(x[0] for x in bounds) if bounds else None,
            "policy_max_mhz": max(x[1] for x in bounds) if bounds else None,
            "throttling_verified": False}


def _thermal(sysfs: Path) -> dict:
    values = {}
    for zone in sorted((sysfs / "class/thermal").glob("thermal_zone[0-9]*")):
        raw = _read(zone / "temp")
        if raw is None:
            continue
        try:
            temp = int(raw.strip()) / 1000
            if -50 <= temp <= 180:
                values[zone.name] = round(temp, 2)
        except ValueError:
            pass
    return {"status": "OBSERVED" if values else "UNSUPPORTED",
            "max_celsius": max(values.values()) if values else None,
            "zones_celsius": values}


def _nvme(sysfs: Path) -> dict:
    drives = {}
    for drive in sorted((sysfs / "block").glob("nvme*n*")):
        raw = _read(drive / "stat")
        try:
            fields = [int(x) for x in raw.split()] if raw else []
            if len(fields) >= 7:
                drives[drive.name] = {"read_ios": fields[0],
                                     "read_sectors": fields[2],
                                     "write_ios": fields[4],
                                     "write_sectors": fields[6],
                                     "read_time_ms": fields[3],
                                     "write_time_ms": fields[7] if len(fields) > 7 else None}
        except ValueError:
            pass
    return {"status": "OBSERVED" if drives else "UNSUPPORTED",
            "cumulative_counters_only": True, "drives": drives}


def _command(args: list[str], runner=subprocess.run) -> str | None:
    try:
        completed = runner(args, text=True, capture_output=True, timeout=5, check=False)
        if completed.returncode != 0 or len(completed.stdout) > 131072:
            return None
        return completed.stdout.strip()
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None



def _cpu_usage_counters(proc: Path) -> dict:
    """Linux cumulative /proc/stat ticks; rate requires a timed pair."""
    raw = _read(proc / "stat")
    line = next((x for x in (raw or "").splitlines() if x.startswith("cpu ")), None)
    if not line:
        return {"status": "UNSUPPORTED"}
    try:
        fields = [int(x) for x in line.split()[1:]]
    except ValueError:
        return {"status": "UNSUPPORTED"}
    if len(fields) < 5:
        return {"status": "UNSUPPORTED"}
    idle = fields[3] + (fields[4] if len(fields) > 4 else 0)
    return {"status": "OBSERVED_CUMULATIVE", "total_ticks": sum(fields[:8]),
            "idle_ticks": idle}

def _gpu(runner) -> dict:
    columns = ["memory.used", "memory.total", "temperature.gpu",
               "power.draw", "utilization.gpu"]
    raw = _command(["nvidia-smi", "--query-gpu=" + ",".join(columns),
                    "--format=csv,noheader,nounits"], runner)
    if raw is None:
        return {"status": "UNSUPPORTED", "metrics": None}
    records = []
    for line in raw.splitlines():
        fields = [x.strip() for x in line.split(",")]
        if len(fields) != len(columns):
            continue
        record = {}
        for key, value in zip(columns, fields):
            try:
                record[key] = float(value)
            except ValueError:
                record[key] = None
        records.append(record)
    return {"status": "OBSERVED" if records else "UNSUPPORTED",
            "units": {"memory": "MiB", "temperature": "C", "power": "W",
                      "utilization": "percent"},
            "metrics": records if records else None,
            "unified_memory_cannot_be_added_to_host_memory": True}


def _cgroup(proc: Path, sysfs: Path, pid: int) -> dict:
    raw = _read(proc / str(pid) / "cgroup")
    if raw is None:
        return {"status": "UNSUPPORTED"}
    lines = [x.split(":", 2) for x in raw.splitlines()]
    v2 = [x[2] for x in lines if len(x) == 3 and x[:2] == ["0", ""]]
    if len(v2) != 1:
        return {"status": "UNSUPPORTED"}
    parts = Path(v2[0]).parts
    if ".." in parts:
        return {"status": "UNSUPPORTED"}
    folder = sysfs / "fs/cgroup" / v2[0].lstrip("/")
    values = {}
    for key in ("memory.current", "memory.peak", "memory.max",
                "memory.high", "cpu.max"):
        raw_value = _read(folder / key)
        values[key] = raw_value.strip() if raw_value is not None else None
    # memory.current includes file cache; Docker CLI subtracts inactive_file
    # from cgroup v2 to display its "MEM USAGE" field.
    memstat_raw = _read(folder / "memory.stat")
    memstat = _flat_counts(memstat_raw)
    bytes_fields = ("anon", "file", "kernel", "shmem", "file_mapped",
                    "active_file", "inactive_file", "slab")
    counter_fields = ("pgfault", "pgmajfault", "workingset_refault_file")
    values["memory_stat_bytes"] = (
        {k: memstat.get(k) for k in bytes_fields} if memstat_raw is not None
        else None)
    values["memory_stat_counters"] = (
        {k: memstat.get(k) for k in counter_fields} if memstat_raw is not None
        else None)
    try:
        current = int(values["memory.current"])
        inactive = memstat["inactive_file"]
        values["docker_cli_derived_usage_bytes"] = (
            current - inactive if 0 <= inactive <= current else None)
    except (ValueError, TypeError, KeyError):
        values["docker_cli_derived_usage_bytes"] = None
    for key in ("memory.swap.current", "memory.swap.max"):
        value = _read(folder / key)
        values[key] = value.strip() if value is not None else None
    values["memory_pressure"] = _pressure(folder / "memory.pressure")
    events = _read(folder / "memory.events")
    values["memory.events"] = {
        k: int(v) for k, v in re.findall(r"(?m)^([a-z_]+)\s+(\d+)$", events or "")
    } if events is not None else None
    return {"status": "OBSERVED" if values["memory.current"] is not None
            else "UNSUPPORTED", "metrics": values}


def _docker(recipe: dict, proc: Path, sysfs: Path, runner) -> dict:
    candidate = recipe.get("trial", {}).get("container_name")
    canonical = recipe.get("runtime", {}).get("container_name")
    allowed = {candidate, canonical}
    if not all(isinstance(n, str) and _ALLOWED.fullmatch(n) for n in allowed):
        return {"status": "BLOCKED", "issues": ["INVALID_RECIPE_CONTAINER_ID"]}
    listed = _command(["docker", "ps", "--format", "{{.Names}}"], runner)
    if listed is None:
        return {"status": "UNSUPPORTED", "container": None}
    active = [x for x in listed.splitlines() if x in allowed]
    if len(active) != 1:
        return {"status": "NOT_OBSERVED", "active_candidates": len(active),
                "container": None}
    name = active[0]
    raw = _command(["docker", "inspect", "--format", "{{json .}}", name], runner)
    if raw is None:
        return {"status": "UNSUPPORTED", "container": None}
    try:
        obj = json.loads(raw)
        state = obj.get("State", {})
        if obj.get("Name", "").lstrip("/") != name or state.get("Running") is not True:
            raise ValueError("identity mismatch")
        pid = state.get("Pid")
        if not isinstance(pid, int) or pid <= 0:
            raise ValueError("missing PID")
        identity = {"name": name, "id": obj["Id"], "image_id": obj["Image"],
                    "pid": pid, "running": True,
                    "memory_limit_bytes": obj.get("HostConfig", {}).get("Memory"),
                    "memory_reservation_bytes": obj.get("HostConfig", {}).get("MemoryReservation"),
                    "nano_cpus": obj.get("HostConfig", {}).get("NanoCpus")}
    except (ValueError, TypeError, KeyError, AttributeError):
        return {"status": "BLOCKED", "issues": ["DOCKER_IDENTITY_UNVERIFIED"]}
    stats_raw = _command(["docker", "stats", "--no-stream", "--format", "{{json .}}", name], runner)
    stats = None
    try:
        stats = json.loads(stats_raw) if stats_raw else None
        stats = {key: stats.get(key) for key in ("MemUsage", "MemPerc", "CPUPerc", "PIDs")}
        if not isinstance(stats, dict):
            stats = None
    except (ValueError, TypeError, AttributeError):
        stats = None
    smaps_raw = _read(proc / str(pid) / "smaps_rollup", 32768)
    smaps = _kv_bytes(smaps_raw)
    proc_status = _read(proc / str(pid) / "status", 32768)
    thread_match = re.search(r"(?m)^Threads:\s*(\d+)\s*$", proc_status or "")
    return {"status": "OBSERVED", "container": identity, "docker_stats": stats,
            "cgroup_v2": _cgroup(proc, sysfs, pid),
            "process_thread_count": int(thread_match.group(1)) if thread_match else None,
            "process_smaps_rollup_status": "OBSERVED" if smaps else "NOT_OBSERVED",
            "process_smaps_rollup_bytes": {k: smaps.get(k) for k in
                ("Rss", "Pss", "Pss_File", "Pss_Anon", "Swap")},
            "ple_specific_resident_bytes": None,
            "ple_specific_residency_status": "NOT_OBSERVED"}


def snapshot(*, proc: Path = PROC, sysfs: Path = SYS, runner=subprocess.run,
             recipe: dict | None = None) -> dict:
    recipe = recipe if recipe is not None else json.loads(RECIPE.read_text(encoding="utf-8"))
    mem = _kv_bytes(_read(proc / "meminfo"))
    selected = ("MemTotal", "MemAvailable", "MemFree", "Cached",
                "SReclaimable", "Dirty", "Writeback", "SwapTotal", "SwapFree")
    memory = {k + "_bytes": mem.get(k) for k in selected}
    memory["swap_used_bytes"] = (
        mem["SwapTotal"] - mem["SwapFree"]
        if "SwapTotal" in mem and "SwapFree" in mem else None)
    doc = {"schema_version": 1,
           "timestamp_utc": datetime.now(timezone.utc).isoformat(),
           "scope": "READ_ONLY_HOST_AND_ALLOWED_DOCKER_INSPECTION",
           "status": "OBSERVED_PARTIAL" if "MemAvailable" in mem else "BLOCKED",
           "executed": False, "resource_limits_changed": False,
           "model_repo": recipe.get("model", {}).get("repo_id"),
           "model_revision": recipe.get("model", {}).get("revision"),
           "api_served_id_declared": recipe.get("profiles", {}).get("mtp0", {}).get("served_id"),
           "recipe_resource_policy": recipe.get("resource_policy"),
           "model_identity_verified_by_api": False,
           "ple_declared_mmap_bytes": recipe.get("model", {}).get("expected_ple", {}).get("mmap_bytes"),
           "ple_declared_size_is_runtime_measurement": False,
           "host_memory": memory,
           "pressure": {kind: _pressure(proc / "pressure" / kind)
                        for kind in ("memory", "cpu", "io")},
           "cpu_frequency": _cpu(sysfs), "cpu_usage_counters": _cpu_usage_counters(proc),
           "vmstat": _vmstat(proc),
           "thermal": _thermal(sysfs),
           "nvme": _nvme(sysfs), "gpu": _gpu(runner),
           "docker": _docker(recipe, proc, sysfs, runner),
           "unsupported_notes": ["GPU memory on GB10 shares physical memory; do not add GPU and host memory totals.",
                                 "smaps_rollup is process-wide, not PLE-specific residency.",
                                 "NVMe counters are cumulative, not measured throughput.",
                                 "Current CPU frequency does not prove thermal throttling."]}
    git_sha = _command(["git", "-C", str(ROOT), "rev-parse", "HEAD"], runner)
    doc["git_head"] = git_sha if git_sha and re.fullmatch(r"[0-9a-f]{40}", git_sha) else None
    return doc



def observation_summary(samples: list[dict]) -> dict:
    """Interval deltas; block sectors are 512-byte units, not filesystem bytes."""
    if len(samples) < 2:
        return {"status": "NOT_OBSERVED"}
    try:
        before = datetime.fromisoformat(samples[0]["timestamp_utc"])
        after = datetime.fromisoformat(samples[-1]["timestamp_utc"])
        seconds = (after - before).total_seconds()
    except (ValueError, TypeError, KeyError):
        return {"status": "UNSUPPORTED"}
    if seconds <= 0:
        return {"status": "UNSUPPORTED"}
    disk_rates = {}
    prev_disks = samples[0].get("nvme", {}).get("drives", {})
    last_disks = samples[-1].get("nvme", {}).get("drives", {})
    for device in sorted(prev_disks.keys() & last_disks.keys()):
        a, b = prev_disks[device], last_disks[device]
        keys = ("read_ios", "read_sectors", "write_ios",
                "write_sectors", "read_time_ms", "write_time_ms")
        if not all(isinstance(a.get(k), int) and isinstance(b.get(k), int)
                   for k in keys):
            continue
        delta = {key: b[key] - a[key] for key in keys}
        if any(value < 0 for value in delta.values()):
            continue
        disk_rates[device] = {
            "read_bytes_per_second": round(delta["read_sectors"] * 512 / seconds),
            "write_bytes_per_second": round(delta["write_sectors"] * 512 / seconds),
            "avg_read_time_ms_per_io": (
                round(delta["read_time_ms"] / delta["read_ios"], 2)
                if delta["read_ios"] else None),
            "avg_write_time_ms_per_io": (
                round(delta["write_time_ms"] / delta["write_ios"], 2)
                if delta["write_ios"] else None),
        }
    available = [row.get("host_memory", {}).get("MemAvailable_bytes")
                 for row in samples]
    available = [x for x in available if isinstance(x, int)]
    swaps = [row.get("host_memory", {}).get("swap_used_bytes")
             for row in samples]
    swaps = [x for x in swaps if isinstance(x, int)]
    psi = [row.get("pressure", {}).get("memory", {}).get("some") or {}
           for row in samples]
    psi_avg10 = [p.get("avg10") for p in psi
                 if isinstance(p.get("avg10"), (float, int))]
    first_cpu = samples[0].get("cpu_usage_counters", {})
    last_cpu = samples[-1].get("cpu_usage_counters", {})
    cpu_busy_pct = None
    if first_cpu.get("status") == last_cpu.get("status") == "OBSERVED_CUMULATIVE":
        total_delta = last_cpu["total_ticks"] - first_cpu["total_ticks"]
        idle_delta = last_cpu["idle_ticks"] - first_cpu["idle_ticks"]
        if total_delta > 0 and 0 <= idle_delta <= total_delta:
            cpu_busy_pct = round(100 * (total_delta - idle_delta) / total_delta, 2)
    first_vm = samples[0].get("vmstat", {}).get("counters") or {}
    last_vm = samples[-1].get("vmstat", {}).get("counters") or {}
    swap_page_rates = {}
    for key in ("pswpin", "pswpout", "pgmajfault"):
        old, new = first_vm.get(key), last_vm.get(key)
        swap_page_rates[key + "_per_second"] = (
            round((new - old) / seconds, 3)
            if isinstance(old, int) and isinstance(new, int) and new >= old
            else None)
    # Counters from a different Docker instance/PID are not comparable.
    # Missing identity is NOT proof of continuity, even if the name matches.
    containers = [(row.get("docker") or {}).get("container") or {}
                  for row in samples]
    ids = [c.get("id") if isinstance(c, dict) else None for c in containers]
    identity_observed = all(isinstance(x, str) and len(x) >= 12 for x in ids)
    identity_continuous = identity_observed and len(set(ids)) == 1
    first_cgroup = (samples[0].get("docker", {}).get("cgroup_v2", {})
                    .get("metrics", {}).get("memory_stat_counters") or {})
    last_cgroup = (samples[-1].get("docker", {}).get("cgroup_v2", {})
                   .get("metrics", {}).get("memory_stat_counters") or {})
    cgroup_fault_deltas = {}
    for key in ("pgmajfault", "workingset_refault_file"):
        old, new = first_cgroup.get(key), last_cgroup.get(key)
        cgroup_fault_deltas[key + "_delta"] = (
            new - old if identity_continuous
            and isinstance(old, int) and isinstance(new, int)
            and new >= old else None)
    first_events = (samples[0].get("docker", {}).get("cgroup_v2", {})
                    .get("metrics", {}).get("memory.events") or {})
    last_events = (samples[-1].get("docker", {}).get("cgroup_v2", {})
                   .get("metrics", {}).get("memory.events") or {})
    memory_event_deltas = {}
    for key in ("low", "high", "max", "oom", "oom_kill"):
        before_count, after_count = first_events.get(key), last_events.get(key)
        memory_event_deltas[key + "_delta"] = (
            after_count - before_count if identity_continuous
            and isinstance(before_count, int) and isinstance(after_count, int)
            and after_count >= before_count else None)
    return {"status": "OBSERVED_INTERVAL",
            "duration_seconds": round(seconds, 3),
            "host_cpu_busy_percent": cpu_busy_pct,
            "host_vmstat_rates": swap_page_rates,
            "cgroup_fault_deltas": cgroup_fault_deltas,
            "cgroup_memory_event_deltas": memory_event_deltas,
            "cgroup_container_identity_continuous": (
                identity_continuous if identity_observed else None),
            "cgroup_identity_discontinuity_detected": (
                identity_observed and not identity_continuous),
            "min_mem_available_bytes": min(available) if available else None,
            "max_swap_used_bytes": max(swaps) if swaps else None,
            "max_memory_psi_some_avg10_pct": max(psi_avg10) if psi_avg10 else None,
            "nvme_rates": disk_rates,
            "nvme_latency_scope": "kernel cumulative per-I/O time delta; not PLE-only"}


def evaluate_warnings(last: dict) -> dict:
    """Advisory comparisons only, no actuator and no fabricated thresholds."""
    policy = last.get("recipe_resource_policy") or {}
    thresholds = {
        "max_memory_psi_some_avg10_pct_warn": (
            (last.get("pressure", {}).get("memory", {}).get("some") or {}).get("avg10")),
        "max_swap_used_gib_warn": (
            last.get("host_memory", {}).get("swap_used_bytes") / GIB
            if isinstance(last.get("host_memory", {}).get("swap_used_bytes"), int)
            else None),
    }
    issues, uncalibrated, unobserved = [], [], []
    for name, actual in thresholds.items():
        threshold = policy.get(name)
        if not isinstance(threshold, (int, float)) or threshold < 0:
            uncalibrated.append(name)
        elif not isinstance(actual, (int, float)):
            unobserved.append(name)
        elif actual > threshold:
            issues.append(name.upper() + "_EXCEEDED")
    return {"status": ("WARNING" if issues else
                       "UNOBSERVED" if unobserved else
                       "UNCALIBRATED" if uncalibrated else
                       "WITHIN_CONFIGURED_ADVISORY_LIMITS"),
            "issues": issues, "uncalibrated": uncalibrated,
            "unobserved": unobserved, "mode": "ADVISORY_ONLY",
            "resource_limits_changed": False}

def admission(snapshot_doc: dict) -> dict:
    """Read-only candidate gate; missing thresholds never imply safe admission."""
    policy = snapshot_doc.get("recipe_resource_policy") or {}
    configured = policy.get("min_mem_available_gib_for_start")
    available = snapshot_doc.get("host_memory", {}).get("MemAvailable_bytes")
    if not isinstance(configured, (float, int)) or configured <= 0:
        status, reasons = "BLOCKED_UNCALIBRATED", ["MIN_START_MEMORY_THRESHOLD_NOT_APPROVED"]
    elif not isinstance(available, int):
        status, reasons = "BLOCKED_UNOBSERVED", ["MEM_AVAILABLE_NOT_OBSERVED"]
    elif available < configured * GIB:
        status, reasons = "BLOCKED_CAPACITY", ["MEM_AVAILABLE_BELOW_RECIPE_THRESHOLD"]
    else:
        status, reasons = "CAPACITY_CHECK_PASS_NOT_LAUNCH_APPROVAL", []
    return {"status": status, "issues": reasons, "observed_mem_available_bytes": available,
            "threshold_gib": configured, "source_only": True, "launch_authorized": False,
            "integrated_with_live_start": False,
            "note": "After current model stops, memory can change; any future runtime gate requires fresh recheck."}


def _save_private(doc: dict) -> str:
    root = Path.home() / ".local/state/blazux-wizard/resource-diagnostics"
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = root / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + ".json")
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(doc, stream, indent=2, sort_keys=True, ensure_ascii=False)
        stream.write("\n")
    return str(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Non-mutating DGX resource diagnostics")
    parser.add_argument("action", choices=("snapshot", "observe", "preflight"))
    parser.add_argument("--samples", type=int, default=2)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--save", action="store_true", help="write private 0600 evidence JSON only")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if not 1 <= args.samples <= 5 or not 0 <= args.interval <= 30:
        parser.error("bounded observation: samples=1..5, interval=0..30 seconds")
    count = args.samples if args.action == "observe" else 1
    samples = []
    for i in range(count):
        if i:
            time.sleep(args.interval)
        samples.append(snapshot())
    doc = {"stage": "p5", "action": args.action, "executed": False,
           "service_mutated": False, "snapshots": samples}
    doc["warnings"] = evaluate_warnings(samples[-1])
    if args.action == "observe":
        doc["interval_summary"] = observation_summary(samples)
    if args.action == "preflight":
        doc["admission"] = admission(samples[-1])
    if args.save:
        doc["evidence_file"] = _save_private(doc)
    print(json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True))
    good = all(x["status"] != "BLOCKED" for x in samples)
    if args.action == "preflight" and doc["admission"]["status"] != "CAPACITY_CHECK_PASS_NOT_LAUNCH_APPROVAL":
        good = False
    return 0 if good else 3


if __name__ == "__main__":
    raise SystemExit(main())
