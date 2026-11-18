"""P5-D source-only Docker port declaration and PLE smaps attribution helpers.

No host probes, privilege requests, live inference, file writes or operation gates.
Configuration is not proof of a listener. A matched smaps path is not proof of
checkpoint identity, a uniquely resident allocation or GPU exclusivity.
"""
from __future__ import annotations

import re

_MAP = re.compile(r"^[0-9a-fA-F]+-[0-9a-fA-F]+\s+[-rwxps]{4}\s+[0-9a-fA-F]+\s+\S+\s+\d+\s+(.+)$")
_KB = re.compile(r"^(Rss|Pss|Size):\s+(\d+)\s+kB$")


def _published_bindings(raw: object) -> set[tuple[str, str]] | None:
    """Conservative Docker inspect HostConfig/NetworkSettings PortBindings."""
    if not isinstance(raw, dict) or "8000/tcp" not in raw:
        return None
    entries = raw["8000/tcp"]
    if not isinstance(entries, list) or not entries or len(entries) > 8:
        return None
    bound = set()
    for item in entries:
        if not isinstance(item, dict) or item.get("HostPort") != "8000":
            return None
        ip = item.get("HostIp")
        if not isinstance(ip, str) or len(ip) > 64:
            return None
        # Docker may normalize an empty HostIp to 0.0.0.0 after publishing.
        bound.add(("0.0.0.0" if not ip else ip, "8000/tcp"))
    return bound


def review_port_publication(inspect: object) -> dict:
    """Compare Docker's configured and effective publishing declarations only."""
    obj = inspect if isinstance(inspect, dict) else {}
    host = obj.get("HostConfig") if isinstance(obj.get("HostConfig"), dict) else {}
    network = (obj.get("NetworkSettings")
               if isinstance(obj.get("NetworkSettings"), dict) else {})
    mode = host.get("NetworkMode")
    mode = mode if isinstance(mode, str) and len(mode) <= 128 else None
    expected = _published_bindings(host.get("PortBindings"))
    observed = _published_bindings(network.get("Ports"))
    consistent = bool(expected and observed and expected == observed)
    if expected is None or observed is None:
        status = "NOT_OBSERVED"
    elif consistent:
        status = "DOCKER_DECLARATION_CONSISTENT_NOT_HOST_VERIFIED"
    else:
        status = "DOCKER_DECLARATION_MISMATCH"
    return {
        "status": status, "network_mode": mode,
        "declared_host_port_8000": bool(expected),
        "effective_host_port_8000": bool(observed),
        "docker_port_declarations_consistent": consistent,
        "nat_candidate_not_verified": bool(consistent and mode not in (None, "host", "none")),
        "host_listener_verified": False,
        "port_process_ownership_verified": False,
        "note": "Inspect-only declarations: no host NAT traversal, socket/PID owner attestation, or Docker identity continuity."
    }


def review_ple_smaps(raw: object, expected_paths: object, *, pid: object,
                     container_id: object, observed_container_id: object,
                     docker_host_pids: object, max_chars: int = 8_000_000) -> dict:
    """Attribute mapping RSS/PSS to exact caller-supplied paths for ONE PID.

    Raw /proc/PID/smaps text must come from a separately validated, bounded,
    read-only capture. This pure review cannot authenticate its provenance.
    Cross-PID RSS cannot be summed as unique resident bytes.
    """
    result = {
        "status": "BLOCKED_UNQUALIFIED", "pid": pid,
        "container_id": container_id if isinstance(container_id, str) else None,
        "matched_mapping_count": 0, "matched_file_count": 0,
        "mapped_rss_bytes": None, "mapped_pss_bytes": None,
        "complete_expected_file_coverage": False,
        "checkpoint_paths_authenticated": False,
        "pid_container_membership_authenticated": False,
        "ple_unique_resident_bytes": None,
        "operations_enabled": False, "production_released": False,
        "issues": [],
    }
    issues = result["issues"]
    valid_id = (isinstance(container_id, str) and re.fullmatch(r"[0-9a-f]{64}", container_id)
                and container_id == observed_container_id)
    valid_pid = (type(pid) is int and pid > 0
                 and isinstance(docker_host_pids, (set, list, tuple))
                 and pid in docker_host_pids and len(docker_host_pids) <= 128)
    if not valid_id or not valid_pid:
        issues.append("UNBOUND_DOCKER_ID_OR_PID")
    if (not isinstance(expected_paths, (list, tuple, set)) or not expected_paths
            or len(expected_paths) > 128 or not all(
                isinstance(p, str) and p.startswith("/") and "\n" not in p
                and "\r" not in p and len(p) < 4096 and ".." not in p.split("/")
                for p in expected_paths)):
        issues.append("UNBOUND_OR_UNSAFE_EXPECTED_PATHS")
    if (not isinstance(raw, str) or not 0 < len(raw) <= max_chars
            or not raw.endswith("\n")):
        issues.append("SMAPS_UNAVAILABLE_OR_TRUNCATED")
    if issues:
        return result
    wanted = set(expected_paths)
    mapped = {}
    current = None
    fields = {}
    bad = False

    def finish():
        nonlocal bad
        if current is None or current not in wanted:
            return
        if not all(k in fields for k in ("Rss", "Pss", "Size")):
            bad = True
            return
        if fields["Rss"] > fields["Size"] or fields["Pss"] > fields["Rss"]:
            bad = True
            return
        item = mapped.setdefault(current, {"rss": 0, "pss": 0, "count": 0})
        item["rss"] += fields["Rss"] * 1024
        item["pss"] += fields["Pss"] * 1024
        item["count"] += 1

    for line in raw.splitlines():
        header = _MAP.fullmatch(line)
        if header:
            finish()
            current, fields = header.group(1), {}
            continue
        pair = _KB.fullmatch(line)
        if pair and current is not None:
            fields[pair.group(1)] = int(pair.group(2))
    finish()
    if bad:
        issues.append("SMAPS_INCOMPLETE_OR_INCONSISTENT_MAPPING")
        return result
    result["matched_mapping_count"] = sum(x["count"] for x in mapped.values())
    result["matched_file_count"] = len(mapped)
    result["complete_expected_file_coverage"] = set(mapped) == wanted
    if not mapped:
        result["status"] = "NOT_OBSERVED"
        issues.append("NO_EXPECTED_PLE_MAPPINGS_FOUND")
        return result
    result["mapped_rss_bytes"] = sum(x["rss"] for x in mapped.values())
    result["mapped_pss_bytes"] = sum(x["pss"] for x in mapped.values())
    result["status"] = "SOURCE_MAPPING_ATTRIBUTION_NOT_AUTHENTICATED"
    if not result["complete_expected_file_coverage"]:
        issues.append("EXPECTED_PLE_MAPPING_COVERAGE_PARTIAL")
    return result
