"""Service management menu: no unapproved mutation of active Docker/API resources.

Service management is intentionally separate from P7 integrated acceptance.
All requested state changes fail closed until runtime-specific preflight,
operator approval, API continuity and rollback have been implemented.
"""
from __future__ import annotations

import json
from ..common import Stage, run as run_stage
from scripts.manager.service_manifest import inspect_service
from scripts.manager.service_status import inspect_live_status
from scripts.manager.service_health import inspect_api_health
from scripts.manager.service_logs import inspect_logs

SPEC = Stage(
    "svc", "Service management",
    ("status", "inventory", "health", "logs", "start", "stop", "restart",
     "rollback", "proxy", "gateway"),
    ("read-only service/port/container inventory",
     "identified active model and exact runtime ownership",
     "scoped approval for stateful Docker/GPU/API actions",
     "verified fallback and recovery plan"),
)


def run(argv, *, as_json=False, dry_run=False):
    args = list(argv)
    if args == ["logs"]:
        try:
            document = inspect_logs()
        except (OSError, ValueError, RuntimeError) as exc:
            document = {"stage": "svc", "status": "BLOCKED",
                        "scope": "DGX_READ_ONLY", "executed": False,
                        "issues": ["SERVICE_LOGS_UNAVAILABLE:" + type(exc).__name__]}
        if dry_run:
            document["dry_run"] = True
        if as_json:
            print(json.dumps(document, sort_keys=True, indent=2))
        else:
            print("Service logs — " + document["status"])
            print(document.get("logs") or "\n".join(document.get("issues", [])))
        return 0 if document["status"] == "READ_ONLY_LOGS" else 3
    if args == ["health"]:
        try:
            document = inspect_api_health()
        except (OSError, ValueError, RuntimeError) as exc:
            document = {"stage": "svc", "status": "BLOCKED",
                        "scope": "LOCAL_API_READ_ONLY", "executed": False,
                        "operations_enabled": False,
                        "issues": ["API_HEALTH_UNAVAILABLE:" + type(exc).__name__]}
        if dry_run:
            document["dry_run"] = True
        if as_json:
            print(json.dumps(document, sort_keys=True, indent=2))
        else:
            print("Service health — " + document["status"])
            print(json.dumps(document, sort_keys=True, indent=2))
        return 0 if document["status"] == "API_IDENTITY_CONFIRMED" else 3
    if args in ([], ["status"]):
        try:
            document = inspect_live_status()
        except (OSError, ValueError, RuntimeError) as exc:
            document = {"stage": "svc", "action": "status",
                        "status": "BLOCKED", "scope": "DGX_READ_ONLY_MANIFEST_AND_API",
                        "executed": False, "operations_enabled": False,
                        "issues": ["LIVE_STATUS_UNAVAILABLE:" + type(exc).__name__]}
        if dry_run:
            document["dry_run"] = True
        if as_json:
            print(json.dumps(document, sort_keys=True, indent=2))
        else:
            print("Service status — " + document["status"])
            print(json.dumps(document, sort_keys=True, indent=2))
        return 0 if document["status"] == "LIVE_SERVICE_VERIFIED" else 3
    if args == ["inventory"]:
        try:
            document = inspect_service()
        except (OSError, ValueError, RuntimeError) as exc:
            document = {"stage": "svc", "runtime": "NOT_RUN",
                        "status": "BLOCKED", "scope": "DGX_READ_ONLY",
                        "issues": ["SERVICE_INVENTORY_UNAVAILABLE:" + type(exc).__name__],
                        "executed": False, "operations_enabled": False}
        if dry_run:
            document["dry_run"] = True
        if as_json:
            print(json.dumps(document, sort_keys=True, indent=2))
        else:
            print("Service management — " + document["status"])
            print(json.dumps(document, sort_keys=True, indent=2))
        return 0 if document["status"] == "OBSERVED_UNQUALIFIED" else 3
    return run_stage(SPEC, args, as_json=as_json, dry_run=dry_run)
