#!/usr/bin/env python3
"""N2 read-only Docker/port/HF-cache inventory and deterministic Flash-Next plan.

No docker run/rm/stop/start, no GPU, no image/model pulls, no network requests.
This is NOT an executor or a launch approval. Actual operator approval remains
a separate gate. No operational output is committed automatically.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any, Callable

DEFAULT_NAME = "qwen38-flash"
DEFAULT_PORT = 8000
DEFAULT_MODEL = "nvidia/Qwen3.8-Flash-Next-NVFP4"
DEFAULT_IMAGE = "qwen38-flash-dgx:v0.32"
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{1,99}$")
DOCKER_PORT_RE = re.compile(r":([0-9]{2,5})->")


class InventoryBlocked(RuntimeError):
    """An observation failed; cannot safely infer that the service is absent."""


def _read(command: list[str], run: Callable[..., Any]) -> str:
    try:
        result = run(command, check=False, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InventoryBlocked("unavailable:" + command[0]) from exc
    if result.returncode != 0:
        raise InventoryBlocked("read_failed:" + " ".join(command[:2]))
    return result.stdout.strip()


def _port_from_socket_line(line: str) -> int | None:
    fields = line.split()
    if len(fields) < 5:
        return None
    local = fields[3]
    try:
        port = int(local.rsplit(":", 1)[-1])
    except ValueError:
        return None
    return port if 0 <= port <= 65535 else None


def _under(a: Path, b: Path) -> bool:
    """Include equality; canonicalize symlinks before checking shared mounts."""
    try:
        return os.path.commonpath((str(a.resolve()), str(b.resolve()))) == str(b.resolve())
    except (OSError, ValueError):
        return False


def inspect_host(
    *,
    name: str = DEFAULT_NAME,
    port: int = DEFAULT_PORT,
    cache_root: Path | None = None,
    run: Callable[..., Any] = subprocess.run,
    disk_usage: Callable[..., Any] = shutil.disk_usage,
) -> dict[str, Any]:
    """Collect local read-only facts. Fail closed on incomplete Docker/port reads."""
    if not NAME_RE.fullmatch(name) or type(port) is not int or not 1024 <= port <= 65535:
        raise ValueError("invalid proposed container name or port")
    cache = Path(cache_root or os.environ.get("HF_CACHE", str(Path.home() / ".cache/huggingface")))
    containers: list[dict[str, Any]] = []
    ports: set[int] = set()
    errors: list[str] = []

    try:
        raw = _read(["docker", "ps", "-a", "--format", "{{json .}}"], run)
        for entry in raw.splitlines():
            if not entry.strip():
                continue
            obj = json.loads(entry)
            if not isinstance(obj, dict) or not isinstance(obj.get("Names"), str):
                raise ValueError("invalid Docker ps entry")
            ports.update(int(n) for n in DOCKER_PORT_RE.findall(str(obj.get("Ports", ""))))
            cname = obj["Names"]
            mounts_raw = json.loads(_read(
                ["docker", "inspect", "--format", "{{json .Mounts}}", cname], run))
            if not isinstance(mounts_raw, list):
                raise ValueError("invalid Docker mounts response")
            mounts = []
            cache_shared = False
            for mount in mounts_raw:
                source = mount.get("Source")
                if isinstance(source, str) and source.startswith("/"):
                    p = Path(source)
                    mounts.append({"source": str(p.resolve()), "destination": str(mount.get("Destination", ""))})
                    cache_shared = cache_shared or _under(cache, p) or _under(p, cache)
            image_id = _read(["docker", "inspect", "--format", "{{.Image}}", cname], run)
            containers.append({
                "name": cname,
                "image": str(obj.get("Image", "")),
                "image_id": image_id,
                "status": str(obj.get("Status", "")),
                "ports": str(obj.get("Ports", "")),
                "mounts": sorted(mounts, key=lambda x: (x["source"], x["destination"])),
                "shares_hf_cache": cache_shared,
            })
    except (InventoryBlocked, ValueError, json.JSONDecodeError, TypeError) as exc:
        errors.append("docker_inventory_incomplete:" + type(exc).__name__)

    try:
        sockets = _read(["ss", "-H", "-ltn"], run)
        ports.update(p for line in sockets.splitlines() if (p := _port_from_socket_line(line)) is not None)
    except InventoryBlocked:
        errors.append("socket_inventory_incomplete")

    try:
        base = cache if cache.exists() else Path.home()
        total, used, free = disk_usage(base)
        disk = {"total_bytes": int(total), "used_bytes": int(used), "free_bytes": int(free)}
    except (OSError, ValueError):
        disk = None
        errors.append("disk_inventory_incomplete")

    repo_dir = cache / "hub/models--nvidia--Qwen3.8-Flash-Next-NVFP4"
    revision_file = repo_dir / "refs/main"
    revision = ""
    try:
        if revision_file.is_file():
            revision = revision_file.read_text(encoding="utf-8").strip()
    except (OSError, UnicodeError):
        errors.append("checkpoint_revision_unreadable")
    valid_sha = bool(re.fullmatch(r"[0-9a-f]{40}", revision))
    snapshot = repo_dir / "snapshots" / revision if valid_sha else None
    checkpoint = {
        "cache_root_present": cache.exists(),
        "revision": revision if valid_sha else None,
        "snapshot_present": bool(snapshot and snapshot.is_dir()),
        "hybrid_prepared": bool(snapshot and (repo_dir / "snapshots" / (revision + "-fp8hybrid") / ".prepared").is_file()),
    }

    # This is a read-only capacity/occupancy plan, not a service executor.
    name_conflict = any(c["name"] == name for c in containers)
    port_conflict = port in ports
    return {
        "scope": "SOURCE",
        "status": "BLOCKED" if errors else "PASS",
        "dry_run": True,
        "launch_authorized": False,
        "proposed": {
            "container_name": name, "port": port, "api_base": f"http://127.0.0.1:{port}/v1",
            "model_repo": DEFAULT_MODEL, "served_model_name": "qwen3.8-flash-next",
            "profile": "default", "image_tag": DEFAULT_IMAGE, "command": "./flash serve default",
        },
        "name_conflict": name_conflict,
        "port_conflict": port_conflict,
        "collision_free": not errors and not name_conflict and not port_conflict,
        "observed_listen_ports": sorted(ports),
        "containers": sorted(containers, key=lambda x: x["name"]),
        "disk": disk,
        "checkpoint": checkpoint,
        "errors": sorted(set(errors)),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only source inventory; never starts a service")
    parser.add_argument("command", choices=("doctor", "plan"), nargs="?", default="doctor")
    parser.add_argument("--name", default=DEFAULT_NAME)
    parser.add_argument("--port", default=DEFAULT_PORT, type=int)
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="default and only mode")
    args = parser.parse_args(argv)
    try:
        data = inspect_host(name=args.name, port=args.port, cache_root=args.cache_root)
    except (ValueError, OSError) as exc:
        print(json.dumps({"scope": "SOURCE", "status": "BLOCKED", "launch_authorized": False,
                          "error": type(exc).__name__}, sort_keys=True))
        return 3
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0 if data["status"] == "PASS" and data["collision_free"] else 3


if __name__ == "__main__":
    sys.exit(main())
