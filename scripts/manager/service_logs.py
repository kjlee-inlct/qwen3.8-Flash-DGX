"""Opt-in bounded read-only Docker log tail for the currently observed model.

Never queries arbitrary containers, never streams continuously and never writes
logs to GitHub, evidence or a cache. Operator should review stdout locally as
model logs may contain prompt fragments or sensitive application data.
"""
from __future__ import annotations

import subprocess
from typing import Any, Callable

from scripts.manager.service_manifest import inspect_service, policy

MAX_TAIL_LINES = 40
MAX_DISPLAY_CHARS = 12_000


def inspect_logs(*, service: dict[str, Any] | None = None,
                 runner: Callable[..., Any] = subprocess.run,
                 tail: int = MAX_TAIL_LINES) -> dict[str, Any]:
    if not 1 <= tail <= MAX_TAIL_LINES:
        raise ValueError("invalid bounded log tail")
    if service is None:
        service = inspect_service()
    data = {
        "schema_version": 1, "stage": "svc", "action": "logs",
        "status": "BLOCKED", "scope": "DGX_READ_ONLY",
        "executed": False, "operations_enabled": False,
        "issues": [], "observed_model": service.get("observed_model"),
        "container_name": None, "tail_lines": tail,
        "logs": None, "truncated": False,
        "notice": "Read-only local log tail; contents may contain private application data. Do not upload unreviewed output.",
    }
    if service.get("status") != "OBSERVED_UNQUALIFIED":
        data["issues"].append("SERVICE_INVENTORY_UNVERIFIED")
        return data
    model = service.get("observed_model")
    allowed = policy().get("models", {}).get(model or "", {}).get("container_name")
    matching = [
        c for c in service.get("managed_containers", [])
        if c.get("name", c.get("container_name")) == allowed
        and str(c.get("status", "")).startswith("Up")
    ]
    if not allowed or len(matching) != 1:
        data["issues"].append("NO_SINGLE_VERIFIED_MANAGED_CONTAINER")
        return data
    data["container_name"] = allowed
    try:
        result = runner(["docker", "logs", "--tail", str(tail),
                         "--timestamps", allowed],
                        capture_output=True, text=True, check=False, timeout=6)
    except (OSError, subprocess.TimeoutExpired) as exc:
        data["issues"].append("DOCKER_LOG_OBSERVATION_FAILED:" + type(exc).__name__)
        return data
    if result.returncode != 0:
        data["issues"].append("DOCKER_LOG_READ_NONZERO")
        return data
    combined = (result.stdout or "") + (result.stderr or "")
    data["truncated"] = len(combined) > MAX_DISPLAY_CHARS
    data["logs"] = combined[-MAX_DISPLAY_CHARS:]
    data["status"] = "READ_ONLY_LOGS"
    return data
