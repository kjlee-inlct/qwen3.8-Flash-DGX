"""P4 Flash storage/container disposition: read-only snapshot, no removal.

P4 is OPTIONAL, and Flash is still a P8 reinstall/recovery reference asset.
Never invoke Docker stop/start/rm/prune or write to model/cache/receipts.
Unrelated WebUI, Portainer etc may coexist, but unmanaged GPU or :8000
owners cannot be silently treated as a safe model disposition.
"""
from __future__ import annotations

import argparse
import json
import re
from typing import Any, Callable

from scripts.manager import recipe_drift
from scripts.manager.service_manifest import policy
from scripts.manager.service_status import inspect_live_status

SHA = re.compile(r"^[0-9a-f]{64}$")


def inspect_p4(*, snapshot_fn: Callable[[], dict] = recipe_drift.collect_docker,
               live_fn: Callable[[], dict] = inspect_live_status,
               policy_fn: Callable[[], dict] = policy) -> dict[str, Any]:
    result = {
        "schema_version": 1, "stage": "P4",
        "action": "FLASH_ASSET_DISPOSITION_READ_ONLY",
        "status": "BLOCKED",
        "issues": [],
        "recommended_disposition": "RETAIN_ALL_PENDING_P8",
        "scope": "DGX_READ_ONLY_DOCKER_AND_API",
        "active_model": None,
        "flash_container_present": None,
        "flash_container_running": None,
        "flash_image_observed": False,
        "historical_retired_cleanup_completed": None,
        "other_gpu_owners": 0,
        "other_port_8000_owners": 0,
        "removal_plan_id": None,
        "approval_accepted": False, "executed": False,
        "operations_enabled": False, "production_released": False,
        "removed_containers": False, "removed_images": False,
        "removed_hf_cache": False,
        "p3_receipts_modified": False,
    }
    try:
        cfg = policy_fn()
        snapshot = snapshot_fn()
        live = live_fn()
        models = cfg["models"]
        managed_names = {v["container_name"]: k for k, v in models.items()
                         if isinstance(v, dict) and isinstance(v.get("container_name"), str)}
        docs = snapshot["containers"]
        running = set(snapshot["running"])
        gpu = set(snapshot["gpu_running"])
        ports = set(snapshot["port_owners"])
        if (not isinstance(docs, dict)
                or not isinstance(snapshot["running"], list)
                or not isinstance(snapshot["gpu_running"], list)
                or not isinstance(snapshot["port_owners"], list)
                or not running.issubset(docs)):
            raise ValueError("INVALID_DOCKER_INVENTORY")
        issue_codes: list[str] = []
        foreign_gpu = gpu - set(managed_names)
        foreign_ports = ports - set(managed_names)
        result["other_gpu_owners"] = len(foreign_gpu)
        result["other_port_8000_owners"] = len(foreign_ports)
        if foreign_gpu:
            issue_codes.append("UNMANAGED_GPU_CONTAINER_RUNNING")
        if foreign_ports:
            issue_codes.append("UNMANAGED_HOST_PORT_8000_OWNER")
        if len(gpu) > 1 or len(ports) > 1:
            issue_codes.append("MULTIPLE_ACTIVE_GPU_OR_PORT_OWNERS")
        selected = [managed_names[name] for name in running
                    if name in managed_names]
        if len(selected) != 1:
            issue_codes.append("MANAGED_ACTIVE_MODEL_NOT_UNIQUE")
        else:
            result["active_model"] = selected[0]
        if (live.get("status") != "LIVE_SERVICE_VERIFIED"
                or live.get("issues")
                or live.get("observed_model") != result["active_model"]
                or live.get("expected_served_id") !=
                models.get(result["active_model"], {}).get("served_id")):
            issue_codes.append("ACTIVE_API_IDENTITY_UNVERIFIED")
        flash_name = models["flash-next"]["container_name"]
        flash = docs.get(flash_name)
        result["flash_container_present"] = flash is not None
        result["flash_container_running"] = flash_name in running
        if flash is not None:
            if (not isinstance(flash, dict)
                    or not SHA.fullmatch(str(flash.get("Id") or ""))
                    or not isinstance(flash.get("Image"), str)
                    or not flash["Image"].startswith("sha256:")):
                issue_codes.append("FLASH_CONTAINER_IDENTITY_UNVERIFIED")
            else:
                result["flash_image_observed"] = True
                if (flash.get("State") or {}).get("Running") is not (flash_name in running):
                    issue_codes.append("FLASH_RUNNING_STATE_INCONSISTENT")
        result["historical_retired_cleanup_completed"] = (
            cfg.get("retired_containers", {}).get("completion", {}).get("state")
            == "OPERATOR_DGX_CLEANUP_COMPLETED_VERIFIED")
        result["issues"] = sorted(set(issue_codes))
        if not issue_codes:
            result["status"] = ("READ_ONLY_FLASH_RETAIN_RECOMMENDED"
                                if flash is not None else
                                "READ_ONLY_FLASH_ABSENT_NO_CLEANUP_REQUIRED")
    except (OSError, KeyError, TypeError, ValueError, RuntimeError) as exc:
        result["issues"] = ["P4_READ_ONLY_OBSERVATION_UNAVAILABLE:" + type(exc).__name__]
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="P4 Flash disposition, READ ONLY")
    parser.add_argument("--json", action="store_true")
    options = parser.parse_args(argv)
    result = inspect_p4()
    print(json.dumps(result, indent=2 if options.json else None, sort_keys=True))
    return 0 if not result["issues"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
