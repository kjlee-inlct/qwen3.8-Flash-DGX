#!/usr/bin/env python3
"""P2 pinned NVIDIA 27B checkpoint acquisition via an approved Wizard plan.

Only a cache download is implemented here. Never calls flash setup/serve,
manages the active model container, allocates GPU, switches APIs or deletes
any cache content. Dry-run/plans do not create files or access the network.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
from typing import Any
from uuid import uuid4

from scripts.manager.inventory import inspect_host
from scripts.manager.p2_27b_inventory import MODEL_ID, inspect_27b

REVISION = "482ca0f3832238542f8f5295dde86b5f22711d80"
IMAGE = "qwen38-flash-dgx:v0.32"
NAME = "qwen38-27b-dl"
MIN_FREE_BYTES = 35 * (1024 ** 3)  # download size ~22 GB + safety/headroom
IMAGE_ID_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


def cache_path(value: Path | None = None) -> Path:
    return Path(value or os.environ.get(
        "HF_CACHE", str(Path.home() / ".cache/huggingface"))).expanduser().resolve()


def _read_image_id(runner) -> str | None:
    try:
        p = runner(["docker", "image", "inspect", IMAGE,
                    "--format", "{{.Id}}"], check=False, capture_output=True,
                   text=True, timeout=10)
        result = p.stdout.strip()
        return result if p.returncode == 0 and IMAGE_ID_RE.fullmatch(result) else None
    except (OSError, subprocess.TimeoutExpired):
        return None


def _other_transfer(runner) -> bool | None:
    """True: competing download; None: unable to inspect (fail closed)."""
    try:
        p = runner(["ps", "-eo", "args"], check=False,
                   capture_output=True, text=True, timeout=10)
        if p.returncode:
            return None
        return any(
            "scripts/download-weights.sh" in line
            or ("hf download" in line and "Qwen3.8-27B-NVFP4" in line)
            for line in p.stdout.splitlines()
        )
    except (OSError, subprocess.TimeoutExpired):
        return None


def _approval_facts(facts: dict[str, Any]) -> dict[str, Any]:
    """Bind safety-critical identity, not continuously changing telemetry.

    mkdir/download.lock consumes inodes after the first read. Container 'Up N
    hours' strings and free bytes also drift while the same approved operation
    remains safe. All minimum-capacity/inode and collision checks still run
    again under the lock; do NOT bypass them when constructing this digest.
    """
    return {
        "model_repo": facts["model_repo"],
        "revision": facts["revision"],
        "cache_root": facts["cache_root"],
        "container_name": facts["container_name"],
        "image_tag": facts["image_tag"],
        "image_id": facts["image_id"],
        "minimum_free_bytes": facts["minimum_free_bytes"],
        "containers": sorted((
            {"name": c["name"], "image_id": c["image_id"],
             "running": str(c["status"]).startswith("Up"),
             "ports": c["ports"]}
            for c in facts["containers"]
        ), key=lambda c: (c["name"] or "")),
        "port_8000_listening": facts["port_8000_listening"],
        "checkpoint_ready": facts["checkpoint_ready"],
        "transfer_busy": facts["transfer_busy"],
        "ten_minute_window": facts["ten_minute_window"],
    }


def build_plan(*, cache_root: Path | None = None, runner=subprocess.run,
               disk_usage=shutil.disk_usage, now: float | None = None) -> dict[str, Any]:
    """Read-only, deterministic bounded plan; no network or cache changes."""
    cache = cache_path(cache_root)
    issues: list[str] = []
    if not cache.is_dir():
        issues.append("HF_CACHE_DIRECTORY_ABSENT")
    try:
        observed = inspect_host(name=NAME, port=8000, cache_root=cache,
                                run=runner, disk_usage=disk_usage)
    except (OSError, ValueError):
        observed = {"errors": ["INVENTORY_UNAVAILABLE"], "containers": [],
                    "disk": None, "name_conflict": True}
    issues.extend(observed.get("errors", []))
    if observed.get("name_conflict"):
        issues.append("DOWNLOAD_CONTAINER_NAME_OCCUPIED")
    disk = observed.get("disk") or {}
    free = disk.get("free_bytes")
    if not isinstance(free, int) or free < MIN_FREE_BYTES:
        issues.append("INSUFFICIENT_VERIFIED_DISK_HEADROOM")
    try:
        st = os.statvfs(cache)
        free_inodes = st.f_favail
        if free_inodes < 128:
            issues.append("INSUFFICIENT_INODES")
    except OSError:
        free_inodes = None
        issues.append("INODE_INVENTORY_UNAVAILABLE")
    image_id = _read_image_id(runner)
    if not image_id:
        issues.append("DOWNLOAD_IMAGE_MISSING_OR_UNKNOWN")
    busy = _other_transfer(runner)
    if busy is None:
        issues.append("TRANSFER_PROCESS_INVENTORY_UNAVAILABLE")
    elif busy:
        issues.append("OTHER_CHECKPOINT_DOWNLOAD_RUNNING")
    checkpoint = inspect_27b(cache, expected_revision=REVISION)
    if checkpoint["source_files_present"]:
        issues.append("PINNED_CHECKPOINT_ALREADY_PRESENT")

    # The real :8000 listener and Flash-Next container are *not* a blocker:
    # download uses no host ports or GPU. Never omit them from the fingerprint.
    containers = [
        {"name": c.get("name"), "image_id": c.get("image_id"),
         "status": c.get("status"), "ports": c.get("ports")}
        for c in observed.get("containers", [])
    ]
    facts = {
        "model_repo": MODEL_ID, "revision": REVISION,
        "cache_root": str(cache), "container_name": NAME,
        "image_tag": IMAGE, "image_id": image_id,
        "minimum_free_bytes": MIN_FREE_BYTES,
        "free_gib_floor": free // (1024 ** 3) if isinstance(free, int) else None,
        "free_inodes": free_inodes,
        "containers": containers,
        "port_8000_listening": 8000 in observed.get("observed_listen_ports", []),
        "checkpoint_ready": checkpoint["source_files_present"],
        "transfer_busy": busy,
        "ten_minute_window": int((time.time() if now is None else now) // 600),
    }
    # Revalidate all live guards after acquiring the download lock, but only
    # bind stable, safety-relevant properties in the approval hash. The lock
    # and evidence folder creation themselves change free inode counts.
    plan_id = None if issues else hashlib.sha256(json.dumps(
        _approval_facts(facts), sort_keys=True,
        separators=(",", ":")).encode()).hexdigest()
    return {
        "stage": "p2", "action": "download",
        "status": "BLOCKED" if issues else "READY_TO_REQUEST_APPROVAL",
        "scope": "SOURCE/DGX_DISK", "executed": False,
        "approval_accepted": False, "plan_id": plan_id,
        "expires_within_minutes": 10,
        "expires_at_epoch_seconds": (facts["ten_minute_window"] + 1) * 600,
        "download_authorized": False,
        "exclusive_gpu_policy": "ONE_ACTIVE_MODEL_ONLY",
        "service_api_port": 8000,
        "issues": sorted(set(issues)), "facts": facts,
        "command_preview": ["docker", "run", "--rm", "--name", NAME,
                            "hf download", MODEL_ID,
                            "--revision", REVISION],
        "safety": {"touch_live_service": False, "host_port_binding": False,
                   "gpu": False, "delete": False, "switch": False},
    }


def _download_argv(cache: Path, image_id: str) -> list[str]:
    """No shell interpolation, no GPU flags, no ports, no service name reuse."""
    return [
        "docker", "run", "--rm", "--name", NAME,
        "--user", f"{os.getuid()}:{os.getgid()}",
        "--read-only", "--tmpfs", "/tmp:rw,nosuid,size=512m",
        "--security-opt", "no-new-privileges", "--cap-drop", "ALL",
        "-e", "HOME=/tmp", "-e", "HF_HOME=/hf",
        "-e", "HF_HUB_DISABLE_XET=0", "-e", "HF_XET_HIGH_PERFORMANCE=1",
        "-v", f"{cache}:/hf",
        *(["-e", "HF_TOKEN"] if os.environ.get("HF_TOKEN") else []),
        *(["-e", "HUGGING_FACE_HUB_TOKEN"] if os.environ.get("HUGGING_FACE_HUB_TOKEN") else []),
        "--entrypoint", "hf", image_id,
        "download", MODEL_ID, "--revision", REVISION, "--max-workers", "8",
    ]


def _write_evidence(doc: dict, state_dir: Path) -> str:
    dest_dir = state_dir / "evidence"
    dest_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = dest_dir / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
                       + "-" + uuid4().hex[:10] + ".json")
    fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as stream:
        json.dump(doc, stream, indent=2, sort_keys=True)
        stream.write("\n")
    return str(path)


def execute_approved(plan: dict, approval: str | None, *,
                     cache_root: Path | None = None,
                     runner=subprocess.run, disk_usage=shutil.disk_usage,
                     now: float | None = None, state_dir: Path | None = None
                     ) -> tuple[int, dict]:
    if plan["status"] != "READY_TO_REQUEST_APPROVAL" or not approval or approval != plan["plan_id"]:
        return 3, {"status": "BLOCKED", "executed": False,
                   "issues": ["APPROVAL_MISSING_OR_PLAN_BLOCKED"]}
    state = Path(state_dir or Path.home() / ".local/state/blazux-wizard/p2")
    operation_started = False
    try:
        state.mkdir(mode=0o700, parents=True, exist_ok=True)
        with (state / "download.lock").open("a+") as lock:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return 3, {"status": "BLOCKED", "executed": False,
                           "issues": ["DOWNLOAD_LOCK_OCCUPIED"]}
            fresh = build_plan(cache_root=cache_root, runner=runner,
                               disk_usage=disk_usage, now=now)
            if fresh["status"] != "READY_TO_REQUEST_APPROVAL" or fresh["plan_id"] != approval:
                issues = ["PREFLIGHT_CHANGED_REPLAN_REQUIRED"]
                if fresh["facts"]["ten_minute_window"] != plan["facts"]["ten_minute_window"]:
                    issues.append("DOWNLOAD_PLAN_TIME_WINDOW_EXPIRED")
                if fresh["status"] == "BLOCKED":
                    issues.extend(fresh["issues"])
                return 3, {"status": "BLOCKED", "executed": False,
                           "issues": sorted(set(issues))}
            cache = cache_path(cache_root)
            record = {
                "stage": "p2", "action": "download", "model_repo": MODEL_ID,
                "revision": REVISION, "plan_id": approval, "executed": True,
                "scope": "DGX_NETWORK_DISK", "status": "FAIL",
                "started_utc": datetime.now(timezone.utc).isoformat(),
            }
            try:
                # This is the only stateful operation: download model files.
                operation_started = True
                process = runner(_download_argv(cache, fresh["facts"]["image_id"]),
                                 check=False)
                record["download_exit_code"] = process.returncode
                post = inspect_27b(cache, expected_revision=REVISION)
                record["checkpoint_status"] = post["checkpoint_status"]
                record["indexed_shard_count"] = post["indexed_shard_count"]
                record["issues"] = post["issues"]
                record["status"] = ("PASS" if process.returncode == 0
                                    and post["source_files_present"] else "FAIL")
            except (OSError, subprocess.SubprocessError, ValueError) as exc:
                record["error_type"] = type(exc).__name__
            record["finished_utc"] = datetime.now(timezone.utc).isoformat()
            path = _write_evidence(record, state)
            return (0 if record["status"] == "PASS" else 2), {
                "status": record["status"], "scope": "DGX_NETWORK_DISK",
                "executed": True, "model_repo": MODEL_ID, "revision": REVISION,
                "evidence": path, "download_exit_code": record.get("download_exit_code"),
                "checkpoint_status": record.get("checkpoint_status"),
                "issues": record.get("issues", []),
                "runtime": "NOT_RUN", "gpu_verified": False,
            }
    except OSError as exc:
        return 3, {"status": "BLOCKED", "executed": operation_started,
                   "issues": ["LOCK_OR_EVIDENCE_UNAVAILABLE"],
                   "error_type": type(exc).__name__}


def main(argv: list[str] | None = None, *, as_json: bool = False,
         dry_run: bool = False) -> int:
    parser = argparse.ArgumentParser(description="P2 pinned NVIDIA 27B Wizard download")
    parser.add_argument("command", choices=("plan", "download"))
    parser.add_argument("--guided", action="store_true")
    parser.add_argument("--for-action", choices=("download",))
    parser.add_argument("--cache-root", type=Path)
    parser.add_argument("--approve-plan")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args(argv)
    if dry_run and args.execute:
        print(json.dumps({"status": "BLOCKED", "executed": False,
                          "issues": ["DRY_RUN_EXECUTION_CONFLICT"]}))
        return 3
    plan = build_plan(cache_root=args.cache_root)
    if args.guided:
        if args.command != "download" or args.execute or args.approve_plan or dry_run or not sys.stdin.isatty():
            print(json.dumps({"status": "BLOCKED", "executed": False,
                              "issues": ["GUIDED_REQUIRES_INTERACTIVE_DOWNLOAD"]}))
            return 3
        print(json.dumps(plan, indent=2, sort_keys=True))
        if plan["status"] != "READY_TO_REQUEST_APPROVAL":
            return 3
        approval = input("Type the full download plan_id to approve (Enter cancels): ").strip()
        rc, result = execute_approved(plan, approval, cache_root=args.cache_root)
        print(json.dumps(result, indent=2, sort_keys=True))
        return rc
    if args.command == "plan" or not args.execute:
        if args.command == "plan" and args.execute:
            print(json.dumps({"status": "BLOCKED", "executed": False,
                              "issues": ["PLAN_IS_READ_ONLY"]}))
            return 3
        print(json.dumps(plan, indent=2, sort_keys=True))
        return 0 if plan["status"] != "BLOCKED" else 3
    rc, result = execute_approved(plan, args.approve_plan,
                                  cache_root=args.cache_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
