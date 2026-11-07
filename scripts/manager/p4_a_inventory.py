"""P4-A read-only capacity/state inventory before ANY cleanup decision.

Output is strictly allowlisted. HF paths, environment values, Docker inspect,
private model names and usage command stderr never leave this module.
No deletion plan, approval SHA, Docker mutation, model download or cache write.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any, Callable

from scripts.manager import recipe_drift
from scripts.manager.service_manifest import policy
from scripts.manager.service_status import inspect_live_status
from scripts.manager.installed_models import DISCOVERY_MANIFEST, _roots

VALID_DF_TYPES = frozenset(("Images", "Containers", "Local Volumes", "Build Cache"))
MAX_ROOTS = 8
MAX_DF_OUTPUT = 32 * 1024
MAX_SIZE_LINE = 1024
UINT = re.compile(r"^[0-9]{1,24}$")
SIZE = re.compile(r"^[0-9]+(?:\.[0-9]+)?\s?(?:B|kB|MB|GB|TB|PB|KiB|MiB|GiB|TiB|PiB)$")
RECLAIM = re.compile(r"^[0-9]+(?:\.[0-9]+)?\s?(?:B|kB|MB|GB|TB|PB|KiB|MiB|GiB|TiB|PiB)(?: \([0-9]{1,3}%\))?$")


def _run(cmd: list[str], *, timeout: int) -> subprocess.CompletedProcess:
    """Exact read-only command vector. Shell=False, no implicit expansion."""
    if not ((cmd == ["docker", "system", "df", "--format", "{{json .}}"])
            or (len(cmd) == 5 and cmd[:4] == ["du", "-s", "-B1", "--"]
                and Path(cmd[4]).is_absolute())):
        raise ValueError("P4_A_COMMAND_NOT_READ_ONLY")
    return subprocess.run(cmd, capture_output=True, text=True,
                          timeout=timeout, check=False)


def _docker_df(run: Callable[..., Any]) -> dict:
    try:
        proc = run(["docker", "system", "df", "--format", "{{json .}}"], timeout=20)
        if proc.returncode or len(proc.stdout) > MAX_DF_OUTPUT:
            raise ValueError("DOCKER_DF_UNAVAILABLE")
        rows = []
        for line in proc.stdout.splitlines():
            if not line:
                continue
            entry = json.loads(line)
            if not isinstance(entry, dict):
                raise ValueError("DOCKER_DF_INVALID_FORMAT")
            kind = entry.get("Type")
            if kind not in VALID_DF_TYPES or kind in [r["type"] for r in rows]:
                raise ValueError("DOCKER_DF_INVALID_CATEGORY")
            # String fields are display estimates supplied by Docker. They
            # are NOT guaranteed unshared bytes or safe reclaimable amounts.
            size = entry.get("Size")
            reclaim = entry.get("Reclaimable")
            if (not isinstance(size, str) or not SIZE.fullmatch(size)
                    or not isinstance(reclaim, str)
                    or not RECLAIM.fullmatch(reclaim)
                    or not UINT.fullmatch(str(entry.get("TotalCount", "")))
                    or not UINT.fullmatch(str(entry.get("Active", "")))):
                raise ValueError("DOCKER_DF_INVALID_SIZE")
            rows.append({
                "type": kind,
                "total_count": str(entry.get("TotalCount", ""))[:18],
                "active_count": str(entry.get("Active", ""))[:18],
                "docker_reported_size": size,
                "docker_reported_reclaimable": reclaim,
                "reclaimable_is_deletion_approval": False,
            })
        if not rows:
            raise ValueError("DOCKER_DF_EMPTY")
        return {"status": "OBSERVED_DOCKER_ESTIMATES", "rows": rows}
    except (OSError, TypeError, ValueError, subprocess.TimeoutExpired,
            json.JSONDecodeError):
        return {"status": "UNAVAILABLE", "rows": []}


def _configured_cache_roots(*, home: Path | None = None,
                            environment: dict | None = None) -> list[Path]:
    with DISCOVERY_MANIFEST.open(encoding="utf-8") as f:
        doc = json.load(f)
    if doc.get("schema_version") != 1:
        raise ValueError("P4_A_INVALID_DISCOVERY_MANIFEST")
    return _roots(doc, Path.home() if home is None else home,
                  os.environ if environment is None else environment)


def _du_bytes(path: Path, run: Callable[..., Any]) -> int | None:
    try:
        proc = run(["du", "-s", "-B1", "--", str(path)], timeout=90)
        if proc.returncode or len(proc.stdout) > MAX_SIZE_LINE:
            return None
        amount = proc.stdout.split(None, 1)[0]
        if not UINT.fullmatch(amount):
            return None
        return int(amount)
    except (OSError, TypeError, ValueError, IndexError, subprocess.TimeoutExpired):
        return None


def inspect_p4_a(*,
                 snapshot_fn: Callable[[], dict] = recipe_drift.collect_docker,
                 live_fn: Callable[[], dict] = inspect_live_status,
                 policy_fn: Callable[[], dict] = policy,
                 cache_roots_fn: Callable[[], list[Path]] = _configured_cache_roots,
                 run: Callable[..., Any] = _run) -> dict[str, Any]:
    """Read-only facts only; never approve removal or infer safe reclaimable GB."""
    result: dict[str, Any] = {
        "schema_version": 1, "stage": "P4-A",
        "action": "STORAGE_CAPACITY_AND_MODEL_STATE_INVENTORY",
        "status": "BLOCKED", "scope": "DGX_READ_ONLY",
        "issues": [], "observed_active_model": None,
        "active_api_verified": False,
        "managed_containers": [],
        "other_container_count": None,
        "gpu_running_container_count": None,
        "port_8000_owner_count": None,
        "docker_disk_usage": {"status": "NOT_OBSERVED", "rows": []},
        "cache_storage": [],
        "cache_roots_truncated": False,
        "candidate_review": "INSUFFICIENT_EVIDENCE_FOR_REMOVAL",
        "preservation": {
            "flash_reinstall_reference_for_p8": True,
            "active_model_assets": True,
            "hf_cache_and_other_models": True,
            "historical_receipts": True,
        },
        "counts_and_sizes_are_not_additive": True,
        "reclaimable_bytes_verified": False,
        "next_step": "REVIEW_CAPACITY_AND_SHARED_ASSET_REFERENCES_BEFORE_ANY_P4_B_PLAN",
        "removal_plan_id": None, "approval_accepted": False,
        "executed": False, "operations_enabled": False,
        "containers_deleted": False, "images_deleted": False,
        "hf_files_deleted": False, "production_released": False,
    }
    try:
        cfg = policy_fn()
        snap = snapshot_fn()
        live = live_fn()
        docs = snap["containers"]
        running = snap["running"]
        gpu = snap["gpu_running"]
        ports = snap["port_owners"]
        managed = {k: v["container_name"] for k, v in cfg["models"].items()
                   if isinstance(v, dict) and isinstance(v.get("container_name"), str)}
        if (not isinstance(docs, dict)
                or not all(isinstance(x, list) for x in (running, gpu, ports))
                or not set(running).issubset(docs)):
            raise ValueError("UNTRUSTED_DOCKER_INVENTORY")
        result["other_container_count"] = len(set(docs) - set(managed.values()))
        result["gpu_running_container_count"] = len(gpu)
        result["port_8000_owner_count"] = len(ports)
        for model, name in managed.items():
            doc = docs.get(name)
            result["managed_containers"].append({
                "model": model,
                "container_present": doc is not None,
                "container_running": name in running,
                "image_id_observed": bool(
                    isinstance(doc, dict)
                    and isinstance(doc.get("Image"), str)
                    and re.fullmatch(r"sha256:[0-9a-f]{64}", doc["Image"])),
                "canonical_recipe_registered": model == "27b",
                "real_reinstall_qualified_by_this_inventory": False,
                "removal_authorized": False,
            })
        result["managed_containers"].sort(key=lambda r: r["model"])
        active = live.get("observed_model")
        if live.get("status") == "LIVE_SERVICE_VERIFIED" and not live.get("issues"):
            result["observed_active_model"] = active
            result["active_api_verified"] = True
        else:
            result["issues"].append("LIVE_API_IDENTITY_NOT_VERIFIED")
        actual = [m for m, name in managed.items() if name in running]
        if len(actual) != 1 or actual[0] != result["observed_active_model"]:
            result["issues"].append("ACTIVE_MODEL_SNAPSHOT_INCONSISTENT")
        if len(gpu) != 1 or gpu[0] not in managed.values():
            result["issues"].append("GPU_OWNERSHIP_REQUIRES_FURTHER_VERIFICATION")
        if len(ports) != 1 or ports[0] not in managed.values():
            result["issues"].append("HOST_PORT_8000_OWNERSHIP_UNVERIFIED")
        # No Docker inspect mount sources, env secrets, other container names,
        # or full paths are copied into the output.
    except (OSError, ValueError, RuntimeError, TypeError, KeyError):
        result["issues"].append("P4_A_DOCKER_AND_API_INSPECTION_UNAVAILABLE")
    result["docker_disk_usage"] = _docker_df(run)
    if result["docker_disk_usage"]["status"] == "UNAVAILABLE":
        result["issues"].append("DOCKER_CAPACITY_ESTIMATES_UNAVAILABLE")

    try:
        roots = cache_roots_fn()
        if not isinstance(roots, list):
            raise ValueError("INVALID_CACHE_ROOT_LIST")
        # The preserved Flash container's /hf bind may point to a cache
        # outside discovery-manifest roots. Inspect only managed /hf mounts,
        # never enumerate foreign container mounts. All source paths stay
        # private and are only used as argv to a no-shell disk usage check.
        configured = [(Path(p), "CONFIGURED_CACHE_ROOT") for p in roots]
        for model, name in managed.items() if "managed" in locals() else []:
            doc = docs.get(name) if "docs" in locals() else None
            if not isinstance(doc, dict):
                continue
            for mount in doc.get("Mounts") or []:
                if (isinstance(mount, dict) and mount.get("Destination") == "/hf"
                        and mount.get("Type") == "bind"
                        and isinstance(mount.get("Source"), str)
                        and Path(mount["Source"]).is_absolute()
                        and Path(mount["Source"]).is_dir()
                        and (Path(mount["Source"]) / "hub").is_dir()):
                    configured.append((Path(mount["Source"]), "MANAGED_CONTAINER_HF_BIND"))
        seen: set[str] = set()
        roots_uniq: list[tuple[Path, str]] = []
        for path, origin in configured:
            # The lexical path may differ for the same inode; realpath
            # deduplication below prevents duplicate cache root readings.
            canonical = str(path.resolve(strict=False))
            if canonical not in seen:
                seen.add(canonical)
                roots_uniq.append((path, origin))
        result["cache_roots_truncated"] = len(roots_uniq) > MAX_ROOTS
        for index, (candidate, origin) in enumerate(roots_uniq[:MAX_ROOTS]):
            root = Path(candidate)
            item = {
                "root_index": index + 1,
                "source": origin,
                "exists": False,
                "filesystem_total_bytes": None,
                "filesystem_free_bytes": None,
                "cache_allocated_bytes": None,
                "known_model_repo_allocated_bytes": {
                    "flash-next": None, "27b": None, "orcarouter": None,
                },
                "flash_repo_present": False,
                "27b_repo_present": False,
                "orcarouter_repo_present": False,
                "measurement_scope": "ENTIRE_CONFIGURED_CACHE_ROOT",
            }
            try:
                root = root.resolve(strict=True)
                if (root.is_dir() and (root / "hub").is_dir()
                        and len(root.parts) >= 3):
                    item["exists"] = True
                    usage = shutil.disk_usage(root)
                    item["filesystem_total_bytes"] = usage.total
                    item["filesystem_free_bytes"] = usage.free
                    item["cache_allocated_bytes"] = _du_bytes(root, run)
                    for model, repo in (
                        ("flash", "models--nvidia--Qwen3.8-Flash-Next-NVFP4"),
                        ("27b", "models--nvidia--Qwen3.8-27B-NVFP4"),
                        ("orcarouter", "models--orcarouter--Qwen3.8-Flash-Next-Uncensored-NVFP4"),
                    ):
                        model_dir = root / "hub" / repo
                        item[model + "_repo_present"] = model_dir.is_dir()
                        if model_dir.is_dir():
                            item["known_model_repo_allocated_bytes"][
                                "flash-next" if model == "flash" else model
                            ] = _du_bytes(model_dir, run)
                            if item["known_model_repo_allocated_bytes"][
                                    "flash-next" if model == "flash" else model] is None:
                                result["issues"].append("MODEL_REPO_CAPACITY_ESTIMATE_UNAVAILABLE")
                else:
                    result["issues"].append("CACHE_ROOT_UNAVAILABLE_OR_UNSAFE")
            except (OSError, ValueError, RuntimeError):
                result["issues"].append("CACHE_ROOT_INSPECTION_UNAVAILABLE")
            if item["exists"] and item["cache_allocated_bytes"] is None:
                result["issues"].append("CACHE_CAPACITY_ESTIMATE_UNAVAILABLE")
            result["cache_storage"].append(item)
        if result["cache_roots_truncated"]:
            result["issues"].append("CACHE_ROOT_COUNT_TRUNCATED")
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        result["issues"].append("CACHE_ROOT_DISCOVERY_UNAVAILABLE")
    result["issues"] = sorted(set(result["issues"]))
    result["status"] = ("READ_ONLY_INVENTORY_COMPLETE" if not result["issues"]
                        else "READ_ONLY_INVENTORY_PARTIAL")
    result["candidate_review"] = (
        "KEEP_ASSETS_PENDING_P8_AND_OPERATOR_DECISION"
        if not result["issues"] else "DO_NOT_DECIDE_WITH_PARTIAL_EVIDENCE")
    return result


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="P4-A capacity inventory, READ ONLY")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    doc = inspect_p4_a()
    print(json.dumps(doc, sort_keys=True, ensure_ascii=False,
                     indent=2 if args.json else None))
    return 0 if doc["status"] == "READ_ONLY_INVENTORY_COMPLETE" else 3


if __name__ == "__main__":
    raise SystemExit(main())
