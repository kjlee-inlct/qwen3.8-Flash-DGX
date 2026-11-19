"""Non-elevated, non-authorizing P5-D procfs permission preflight.

Refresh Docker PIDs, sample only exact /proc targets, classify errno and
return no process memory, private symlink target or credentials. No sudo, shell,
Docker exec, inference, host writes, model/cache mutation, or release.
"""
from __future__ import annotations

import errno
import json
import os
from pathlib import Path
import re

from scripts.manager.p5d_manifest_binding import source_binding
from scripts.manager.p5d_live_audit import _cmd, _model_ro_mounts
from scripts.manager.process_ownership import ownership_capture

_ID = re.compile(r"[0-9a-f]{64}\Z")
_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,100}\Z")
_PROC = Path("/proc")


def _error(exc):
    status = ("ACCESS_DENIED" if exc.errno in (errno.EACCES, errno.EPERM)
              else "GONE" if exc.errno in (errno.ENOENT, errno.ESRCH)
              else "IO_UNAVAILABLE")
    return {"status": status, "errno": exc.errno}


def _smaps(path):
    try:
        with path.open("rb") as stream:
            sample = stream.read(256)
        return {"status": "READABLE_SAMPLE_ONLY", "bytes_sampled": len(sample)}
    except OSError as exc:
        return _error(exc)


def _stat_ticks(pid, proc):
    try:
        with (proc / str(pid) / "stat").open(encoding="utf-8") as stream:
            raw = stream.read(4097)
        if len(raw) > 4096 or not raw.startswith(str(pid) + " ("):
            return None
        close = raw.rfind(")")
        if close < 0:
            return None
        tail = raw[close + 1:].split()
        if len(tail) <= 19:
            return None
        ticks = int(tail[19])
        return ticks if ticks > 0 else None
    except (OSError, ValueError, UnicodeError):
        return None


def _uid(pid, proc):
    try:
        with (proc / str(pid) / "status").open(encoding="utf-8") as stream:
            data = stream.read(8192)
        m = re.search(r"^Uid:\s+(\d+)\s+(\d+)", data, re.M)
        return {"status": "OBSERVED", "real": int(m[1]), "effective": int(m[2])} if m else {"status": "UNQUALIFIED"}
    except (OSError, UnicodeError) as exc:
        return _error(exc) if isinstance(exc, OSError) else {"status": "UNQUALIFIED"}


def _link(path, pattern=None):
    try:
        value = os.readlink(path)
        if pattern and not re.fullmatch(pattern, value):
            return {"status": "UNQUALIFIED"}
        return {"status": "OBSERVED", "value": value} if pattern else {"status": "READABLE"}
    except OSError as exc:
        return _error(exc)


def _fd(path):
    try:
        with os.scandir(path) as entries:
            first = next(iter(entries), None)
            if first is None:
                return {"status": "EMPTY"}
            os.readlink(first.path)
        return {"status": "SAMPLE_READABLE"}
    except OSError as exc:
        return _error(exc)


def _pinned_directory(proc, init, mounts, source):
    marker = "models--" + source["repo_id"].replace("/", "--")
    responses = []
    for mount in mounts[:8]:
        rels = ("/" + marker,) if mount.endswith("/hub") else (
            "/hub/" + marker, "/" + marker)
        for rel in rels:
            path = Path(str(proc / str(init) / "root") + mount + rel
                        + "/snapshots/" + source["revision"])
            try:
                with os.scandir(path):
                    pass
                responses.append("READABLE_DIRECTORY")
            except OSError as exc:
                responses.append(_error(exc)["status"])
    return {"status": "READABLE_CANDIDATE_ONLY" if "READABLE_DIRECTORY" in responses
            else "UNQUALIFIED", "candidate_count": len(responses),
            "results": {s: responses.count(s) for s in sorted(set(responses))},
            "ple_tensor_identity_authenticated": False}


def _scope(proc):
    try:
        with (proc / "sys/kernel/yama/ptrace_scope").open(encoding="ascii") as stream:
            val = stream.read(16).strip()
        if val in ("0", "1", "2", "3"):
            return {"status": "OBSERVED", "value": int(val),
                    "note": "Policy context, not an authenticated EACCES root cause."}
        return {"status": "UNQUALIFIED"}
    except OSError as exc:
        return _error(exc)


def permission_preflight(model, *, capture=ownership_capture,
                         run_command=_cmd, proc=_PROC):
    result = {"schema_version": 1, "action": "p5d-permission-preflight",
              "model": model, "status": "BLOCKED_PERMISSION_PREFLIGHT",
              "scope": "BOUNDED_NON_ELEVATED_READ_ONLY_HOST_PROBE",
              "issues": [], "audit_effective_uid": os.geteuid(),
              "ready_for_full_readonly_audit": False,
              "executed_inference": False, "service_mutated": False,
              "operations_enabled": False, "ple_residency_authenticated": False,
              "host_nat_owner_authenticated": False, "production_released": False}
    binding = source_binding(model)
    result["manifest_binding_status"] = binding["status"]
    if binding["status"] != "DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED":
        result["issues"] = ["MANIFEST_SOURCE_BINDING_UNQUALIFIED"]
        return result
    if model != "orcarouter":
        result["issues"] = ["ONLY_ORCAROUTER_LIVE_AUDIT_IMPLEMENTED"]
        return result
    current = capture(model)
    c = current.get("container") or {}
    cid, name, init, pids = (c.get("id"), c.get("name"), c.get("init_pid"),
                              current.get("docker_host_pids"))
    if not (isinstance(cid, str) and _ID.fullmatch(cid)
            and isinstance(name, str) and _NAME.fullmatch(name)
            and type(init) is int and init > 0
            and isinstance(pids, list) and 1 <= len(pids) <= 32
            and init in pids and len(set(pids)) == len(pids)
            and all(type(pid) is int and pid > 0 for pid in pids)
            and current.get("model") == model
            and current.get("docker_identity_match") is True):
        result["issues"] = ["FRESH_DOCKER_PID_SET_UNQUALIFIED"]
        return result
    raw = run_command(["docker", "inspect", "--format", "{{json .}}", name])
    try:
        info = json.loads(raw) if isinstance(raw, str) else {}
    except (ValueError, TypeError):
        info = {}
    if (not isinstance(info, dict) or info.get("Id") != cid
            or info.get("Name") != "/" + name
            or (info.get("State") or {}).get("Pid") != init
            or (info.get("State") or {}).get("Running") is not True):
        result["issues"] = ["FRESH_DOCKER_INSPECT_IDENTITY_UNQUALIFIED"]
        return result
    mounts = _model_ro_mounts(info)
    result["container"] = {"id": cid, "init_pid": init, "pid_count": len(pids)}
    result["yama_ptrace_scope_hint"] = _scope(proc)
    result["read_only_cache_mount_count"] = len(mounts)
    rows, issues = [], []
    for pid in sorted(pids):
        base = proc / str(pid)
        ticks_before = _stat_ticks(pid, proc)
        ns = {k: _link(base / "ns" / k, k + r":\[\d+\]")
              for k in ("net", "mnt", "pid")}
        smaps = _smaps(base / "smaps")
        fd = _fd(base / "fd")
        row = {"pid": pid, "process_uid": _uid(pid, proc),
               "start_ticks_before": ticks_before,
               "start_ticks_after": _stat_ticks(pid, proc),
               "smaps": smaps, "namespaces": ns, "fd": fd}
        if pid == init:
            row["root_link"] = _link(base / "root")
        row["start_ticks_stable"] = (
            ticks_before is not None and ticks_before == row["start_ticks_after"])
        rows.append(row)
        if not row["start_ticks_stable"]:
            issues.append("STARTTIME_UNQUALIFIED_OR_CHANGED")
        if smaps["status"] != "READABLE_SAMPLE_ONLY":
            issues.append("SMAPS_" + smaps["status"])
        for value in ns.values():
            if value["status"] != "OBSERVED":
                issues.append("NAMESPACE_" + value["status"])
        if fd["status"] != "SAMPLE_READABLE":
            issues.append("FD_" + fd["status"])
        if pid == init and row["root_link"]["status"] != "READABLE":
            issues.append("CONTAINER_ROOT_" + row["root_link"]["status"])
    snapshot = _pinned_directory(proc, init, mounts, binding["source"])
    result["pinned_snapshot_directory"] = snapshot
    result["pids"] = rows
    if snapshot["status"] != "READABLE_CANDIDATE_ONLY":
        issues.append("PINNED_SNAPSHOT_DIRECTORY_UNQUALIFIED")
    if not mounts:
        issues.append("READONLY_CACHE_MOUNT_UNQUALIFIED")
    result["smaps_access_denied_pid_count"] = sum(
        row["smaps"]["status"] == "ACCESS_DENIED" for row in rows)
    result["issues"] = sorted(set(issues))
    if not issues:
        result["status"] = "READABLE_PROCFS_PREFLIGHT_NOT_ATTESTED"
        result["ready_for_full_readonly_audit"] = True
    return result
