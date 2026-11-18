"""Bounded, non-authorizing P5-D read-only host provenance one-shot.

Host reads: existing P5-C/P5-D probes, docker inspect, /proc/PID/smaps,
fd/net/cgroup/ns metadata, localhost GET /v1/models, optional iptables-save.
NO sudo, shell, docker exec, inferencing, service/config changes, or root writes.
Only optional private evidence JSON is created with existing 0600 writer.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import socket
import stat
import subprocess
from urllib.request import urlopen

from scripts.manager.generic_operations import model_catalog
from scripts.manager.model_measurements import save_record
from scripts.manager.p5_readonly_attribution import review_port_publication
from scripts.manager.process_ownership import ownership_capture

MODEL = "orcarouter"
_PORT = 8000
_HEX64 = re.compile(r"^[0-9a-f]{64}$")
_HEADER = re.compile(
    r"^([0-9a-fA-F]+)-([0-9a-fA-F]+)\s+([-rwxps]{4})\s+"
    r"([0-9a-fA-F]+)\s+([0-9a-fA-F]+):([0-9a-fA-F]+)\s+"
    r"(\d+)(?:\s+(.*))?$")
_NUMBER = re.compile(r"^(Size|Rss|Pss):\s+(\d+)\s+kB$")
_SOCKET = re.compile(r"^socket:\[(\d+)\]$")
_PID_LIMIT = 32
_MAP_LIMIT = 512
_SMAPS_BYTES_LIMIT = 96 * 1024 * 1024


def _cmd(argv, *, limit=262144, timeout=8):
    """Return no raw stderr; fixed argv only. Null means permission/timeout/unavailable."""
    try:
        p = subprocess.run(argv, text=True, capture_output=True, timeout=timeout,
                           check=False)
        if p.returncode != 0 or len(p.stdout) > limit:
            return None
        return p.stdout
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None


def _exact_api(served_id):
    """Read-only localhost model-identity GET; not proof of NAT kernel rule ownership."""
    try:
        with urlopen("http://127.0.0.1:8000/v1/models", timeout=5) as handle:
            if handle.getcode() != 200:
                return False
            data = handle.read(131073)
        if len(data) > 131072:
            return False
        obj = json.loads(data)
        ids = [x.get("id") for x in obj.get("data", [])
               if isinstance(x, dict)]
        return ids == [served_id]
    except (OSError, ValueError, TypeError, KeyError):
        return False


def _published_ip(info):
    """Get only exact container bridge IPv4 candidates from this Docker ID."""
    network = info.get("NetworkSettings") or {}
    items = network.get("Networks") or {}
    addresses = []
    if isinstance(items, dict):
        for value in items.values():
            if isinstance(value, dict):
                ip = value.get("IPAddress")
                if isinstance(ip, str) and re.fullmatch(r"\d{1,3}(?:\.\d{1,3}){3}", ip):
                    try:
                        socket.inet_aton(ip)
                        addresses.append(ip)
                    except OSError:
                        pass
    return sorted(set(addresses))


def _iptables_nat(ips, raw):
    """Only match a narrowly scoped DNAT target; no proof rules are traversed."""
    if not isinstance(raw, str):
        return {"status": "UNAVAILABLE", "matching_rule_found": False}
    matches = []
    for line in raw.splitlines():
        if (line.startswith("-A ") and "--dport 8000" in line
                and ("-j DNAT" in line or "-j DNAT " in line)):
            for ip in ips:
                if re.search(r"--to-destination\s+" + re.escape(ip) + r":8000(?:\s|$)", line):
                    matches.append(ip)
    return {"status": "READ_ONLY_RULES_OBSERVED",
            "matching_rule_found": bool(matches),
            "matched_container_ips": sorted(set(matches)),
            "active_nat_path_authenticated": False}


def _listener_inodes(text):
    """Linux /proc/PID/net/tcp[6] LISTEN inode set for local port 8000."""
    found = set()
    if not isinstance(text, str) or len(text) > 5_000_000:
        return found
    for line in text.splitlines()[1:]:
        columns = line.split()
        if len(columns) < 10 or columns[3] != "0A":
            continue
        try:
            port = int(columns[1].rsplit(":", 1)[1], 16)
        except (ValueError, IndexError):
            continue
        if port == _PORT and columns[9].isdigit():
            found.add(int(columns[9]))
    return found


def _socket_pid_evidence(pids, init_pid, proc=Path("/proc")):
    """Bind LISTEN inode from target net namespace to fd owners in Docker PID set."""
    issues = []
    sockets = set()
    for name in ("tcp", "tcp6"):
        try:
            s = (proc / str(init_pid) / "net" / name).read_text(encoding="utf-8")
            sockets.update(_listener_inodes(s))
        except (PermissionError, OSError, UnicodeError):
            issues.append("CONTAINER_NET_" + name.upper() + "_UNREADABLE")
    try:
        container_netns = os.readlink(proc / str(init_pid) / "ns" / "net")
    except OSError:
        container_netns = None
        issues.append("CONTAINER_NETNS_UNREADABLE")
    owners = []
    for pid in sorted(set(pids)):
        try:
            namespace = os.readlink(proc / str(pid) / "ns" / "net")
            if not container_netns or container_netns != namespace:
                issues.append("PID_NETNS_DRIFT")
                continue
            fd_dir = proc / str(pid) / "fd"
            has_match = False
            for ent in os.scandir(fd_dir):
                try:
                    ref = os.readlink(ent.path)
                except OSError:
                    continue
                match = _SOCKET.fullmatch(ref)
                if match and int(match.group(1)) in sockets:
                    has_match = True
                    break
            if has_match:
                owners.append(pid)
        except (OSError, PermissionError):
            issues.append("CONTAINER_FD_ENUMERATION_UNAVAILABLE")
    return {
        "status": "CONTAINER_LISTENER_PID_FD_CORRELATED" if owners else "PARTIAL_OR_UNOBSERVED",
        "container_netns": container_netns,
        "listening_inode_count": len(sockets),
        "matched_docker_host_pids": owners,
        "issues": sorted(set(issues)),
        "kernel_nat_owner_authenticated": False,
    }


def _cgroup_membership(pid, cid, proc=Path("/proc")):
    """Host cgroup evidence is separate from Docker top and subject to host layout."""
    try:
        data = (proc / str(pid) / "cgroup").read_text(encoding="utf-8")
        if len(data) > 4096:
            return None
        return cid in data
    except (OSError, UnicodeError):
        return None


def _model_ro_mounts(info):
    mounts = info.get("Mounts") or []
    result = []
    if isinstance(mounts, list):
        for m in mounts[:64]:
            if not isinstance(m, dict) or m.get("RW") is not False:
                continue
            dest = m.get("Destination")
            if (isinstance(dest, str) and dest.startswith("/")
                    and len(dest) < 4096 and ".." not in Path(dest).parts
                    and re.search(r"hf|cache|model|weight", dest, re.I)):
                result.append(dest.rstrip("/"))
    return sorted(set(result), key=len, reverse=True)


def _candidate_model_path(path, mounts, repo_marker):
    """Only model cache-backed file names, not every mapping in a process."""
    if not isinstance(path, str) or not path.startswith("/") or "\x00" in path:
        return False
    if " (deleted)" in path or len(path) > 4096:
        return False
    if not any(path.startswith(x + "/") for x in mounts):
        return False
    lower = path.lower()
    return (repo_marker.lower() in lower
            or lower.endswith(".safetensors")
            or lower.endswith(".bin")
            or "/blobs/" in lower)


def _scan_smaps(pid, mounts, repo_marker, *, proc=Path("/proc"),
                stat_function=os.stat):
    """Stream smaps, never retain raw text. Bound bytes, mappings, and trust."""
    result = {"pid": pid, "status": "NOT_OBSERVED", "mapped_files": [],
              "issues": [], "sampled_smaps_bytes": 0}
    rows = {}
    current = None
    metrics = {}
    count = 0
    def finish():
        nonlocal current, metrics, count
        if current is None:
            return
        if not all(k in metrics for k in ("Size", "Rss", "Pss")):
            result["issues"].append("SMAPS_MAPPING_METRICS_INCOMPLETE")
            return
        if metrics["Pss"] > metrics["Rss"] or metrics["Rss"] > metrics["Size"]:
            result["issues"].append("SMAPS_MAPPING_ACCOUNTING_INCONSISTENT")
            return
        path, maj, minor, inode, start, end = current
        if count >= _MAP_LIMIT:
            result["issues"].append("FILE_MAPPING_COUNT_LIMIT")
            return
        key = (path, maj, minor, inode)
        row = rows.setdefault(key, {"path": path, "dev_major": maj, "dev_minor": minor,
            "inode": inode, "rss_bytes": 0, "pss_bytes": 0, "mapping_count": 0,
            "inode_stat_match": None})
        row["rss_bytes"] += metrics["Rss"] * 1024
        row["pss_bytes"] += metrics["Pss"] * 1024
        row["mapping_count"] += 1
        count += 1
    try:
        with (proc / str(pid) / "smaps").open(encoding="utf-8", errors="replace") as handle:
            for line in handle:
                result["sampled_smaps_bytes"] += len(line)
                if result["sampled_smaps_bytes"] > _SMAPS_BYTES_LIMIT:
                    result["issues"].append("SMAPS_READ_LIMIT")
                    break
                if len(line) > 16384:
                    result["issues"].append("SMAPS_LINE_LIMIT")
                    break
                m = _HEADER.fullmatch(line.rstrip("\n"))
                if m:
                    finish()
                    path = m.group(8) or ""
                    if _candidate_model_path(path, mounts, repo_marker):
                        current = (path, int(m.group(5), 16), int(m.group(6), 16),
                                   int(m.group(7)), int(m.group(1), 16), int(m.group(2), 16))
                    else:
                        current = None
                    metrics = {}
                    continue
                x = _NUMBER.fullmatch(line.rstrip("\n"))
                if x and current is not None:
                    metrics[x.group(1)] = int(x.group(2))
            if "SMAPS_READ_LIMIT" not in result["issues"] and "SMAPS_LINE_LIMIT" not in result["issues"]:
                finish()
    except (OSError, UnicodeError):
        result["issues"].append("SMAPS_UNREADABLE")
        return result
    # Stat through the task's actual mount namespace, not host cache alias.
    for key, row in rows.items():
        mapped_path = row["path"]
        try:
            st = stat_function(str(proc / str(pid) / "root") + mapped_path)
            row["inode_stat_match"] = (st.st_ino == row["inode"]
                                       and os.major(st.st_dev) == row["dev_major"]
                                       and os.minor(st.st_dev) == row["dev_minor"]
                                       and stat.S_ISREG(st.st_mode))
        except (OSError, ValueError):
            row["inode_stat_match"] = None
            result["issues"].append("MAPPING_FILE_STAT_UNAVAILABLE")
    result["mapped_files"] = sorted(rows.values(), key=lambda x: (-x["rss_bytes"], x["path"]))
    if result["mapped_files"]:
        result["status"] = ("MAPPINGS_INODE_MATCHED_CANDIDATE_NOT_PLE_AUTHENTICATED"
                            if all(x["inode_stat_match"] for x in result["mapped_files"])
                            and not result["issues"] else "MAPPINGS_PARTIAL_OR_UNQUALIFIED")
    return result


def _collect(*, capture_ownership=ownership_capture, run_command=_cmd,
             scan=_scan_smaps, sockets=_socket_pid_evidence,
             api=_exact_api, proc=Path("/proc")):
    started = datetime.now(timezone.utc).isoformat()
    issues = []
    before = capture_ownership(MODEL)
    container = before.get("container") or {}
    cid, name, init_pid = (container.get("id"), container.get("name"),
                           container.get("init_pid"))
    pids = before.get("docker_host_pids")
    allowed = (isinstance(cid, str) and _HEX64.fullmatch(cid)
               and isinstance(name, str)
               and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{1,100}", name)
               and before.get("docker_identity_match") is True
               and isinstance(init_pid, int) and init_pid > 0
               and isinstance(pids, list)
               and 1 <= len(pids) <= _PID_LIMIT
               and init_pid in pids
               and all(type(p) is int and p > 0 for p in pids)
               and before.get("model") == MODEL)
    if not allowed:
        return {"schema_version": 1, "action": "p5d-live-readonly-audit",
                "status": "BLOCKED_PREFLIGHT", "model": MODEL,
                "issues": ["DOCKER_OR_PID_PREFLIGHT_UNQUALIFIED"],
                "initial_ownership": before, "executed_inference": False,
                "service_mutated": False, "production_released": False}

    raw = run_command(["docker", "inspect", "--format", "{{json .}}", name])
    try:
        info = json.loads(raw) if raw is not None else {}
    except (ValueError, TypeError):
        info = {}
    state = info.get("State") or {}
    if (info.get("Id") != cid or info.get("Name") != "/" + name
            or state.get("Running") is not True
            or state.get("Pid") != init_pid):
        issues.append("INDEPENDENT_INSPECT_IDENTITY_MISMATCH")
        info = {}
    publication = review_port_publication(info)
    mounts = _model_ro_mounts(info)
    ips = _published_ip(info)
    model_spec = model_catalog()["models"][MODEL]
    served_id = model_spec["served_id"]
    api_match = api(served_id)
    if not api_match:
        issues.append("API_MODEL_ID_NOT_CONFIRMED")
    if not mounts:
        issues.append("NO_READONLY_MODEL_CACHE_MOUNT_OBSERVED")
    pinned_id = "models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4"
    observed = []
    for pid in pids:
        row = scan(pid, mounts, pinned_id, proc=proc)
        membership = _cgroup_membership(pid, cid, proc=proc)
        row["cgroup_exact_container_id_present"] = membership
        if membership is not True:
            row["issues"].append("PID_CGROUP_CONTAINER_ID_UNVERIFIED")
        observed.append(row)
    ports = sockets(pids, init_pid, proc=proc)
    iptables = _iptables_nat(ips, run_command(["iptables-save", "-t", "nat"]))
    # Source switch and provenance details remain explicitly non-authorizing.
    after = capture_ownership(MODEL)
    after_container = after.get("container") or {}
    continuous = (after_container.get("id") == cid and
                  after_container.get("init_pid") == init_pid and
                  after.get("docker_host_pids") == pids and
                  after.get("docker_identity_match") is True and
                  after.get("model") == MODEL)
    if not continuous:
        issues.append("CONTAINER_OR_PID_DRIFT")
    candidate_files = sum(len(x["mapped_files"]) for x in observed)
    fully_statted = bool(candidate_files and
                         all(x.get("inode_stat_match") is True
                             for x in observed for x in x["mapped_files"]))
    all_pids_accessible = all(x["status"] != "NOT_OBSERVED"
                              and not x["issues"] for x in observed)
    if not candidate_files:
        issues.append("MODEL_CACHE_MAPPING_CANDIDATES_NOT_OBSERVED")
    if not fully_statted:
        issues.append("MAPPING_FILE_INODE_COVERAGE_INCOMPLETE")
    if not ports["matched_docker_host_pids"]:
        issues.append("CONTAINER_SOCKET_OWNER_FD_UNVERIFIED")
    if publication["status"] != "DOCKER_DECLARATION_CONSISTENT_NOT_HOST_VERIFIED":
        issues.append("DOCKER_PORT_PUBLISH_DECLARATION_NOT_CONSISTENT")
    # A correlation is a supported partial observation, never a production
    # proof that the kernel actually used a particular host NAT datapath.
    correlated = (continuous and api_match and bool(ports["matched_docker_host_pids"])
                  and fully_statted and all_pids_accessible
                  and publication["docker_port_declarations_consistent"])
    return {
        "schema_version": 1, "action": "p5d-live-readonly-audit",
        "status": ("CORRELATED_READ_ONLY_NOT_INDEPENDENTLY_AUTHENTICATED"
                   if correlated else "BLOCKED_PARTIAL_PROVENANCE"),
        "model": MODEL, "timestamp_utc": started,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "git_head": before.get("git_head"),
        "container": container,
        "initial_ownership": before,
        "final_ownership": after,
        "container_id_continuous": continuous,
        "service_api_model_id_confirmed": api_match,
        "port": {"publication": publication, "container_ips": ips,
                 "container_listener": ports, "iptables_nat": iptables,
                 "host_listener_pid_observed": bool(before.get("host_port_8000_listener_pids")),
                 "host_nat_path_authenticated": False,
                 "host_port_process_ownership_verified": False},
        "file_mappings": observed,
        "summary": {
            "examined_container_host_pids": len(pids),
            "candidate_file_mapping_rows": candidate_files,
            "all_candidate_inodes_statted": fully_statted,
            "all_pids_accessible_and_container_bound": all_pids_accessible,
            "socket_inode_to_container_pid_correlated": bool(ports["matched_docker_host_pids"]),
            "ple_specific_unique_resident_bytes": None,
            "ple_residency_authenticated": False,
            "kernel_nat_owner_authenticated": False,
            "independent_gpu_exclusivity_verified": False,
        },
        "issues": sorted(set(issues +
            [issue for item in observed for issue in item["issues"]] +
            ports["issues"])),
        "executed_inference": False, "service_mutated": False,
        "production_released": False, "operations_enabled": False,
        "note": ("Per-file RSS/PSS is a process mapping observation; it cannot establish "
                 "unique physical PLE residency. File candidates may be checkpoint "
                 "weights unrelated to PLE tensors. /proc/PID/net is namespace-wide "
                 "and requires matching FD inode to attribute PID. Docker port publish "
                 "+ exact API + internal listener is a correlation, not verified kernel "
                 "DNAT ownership. No actual service or operating state changed."),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="P5-D single bounded live read-only audit")
    parser.add_argument("--save", action="store_true", help="Private JSON receipt only, mode 0600")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        doc = _collect()
        if args.save:
            doc["evidence_file"] = save_record(doc)
        compact = {k: doc.get(k) for k in (
            "schema_version", "action", "status", "model", "timestamp_utc",
            "git_head", "container", "container_id_continuous",
            "service_api_model_id_confirmed", "port", "summary", "issues",
            "evidence_file", "executed_inference", "service_mutated",
            "production_released", "note") if k in doc}
        print(json.dumps(compact, indent=2, sort_keys=True, ensure_ascii=False))
        # Exit 3 marks unqualified evidence, NOT runtime service failure.
        return 0 if doc.get("status") == "CORRELATED_READ_ONLY_NOT_INDEPENDENTLY_AUTHENTICATED" else 3
    except (OSError, ValueError, TypeError, RuntimeError, KeyError) as err:
        print(json.dumps({"action": "p5d-live-readonly-audit", "status": "BLOCKED",
                          "issues": [type(err).__name__],
                          "note": "No automatic retry and no operating mutations.",
                          "production_released": False}, indent=2))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
