"""Service management menu: no unapproved mutation of active Docker/API resources.

Service management is intentionally separate from P7 integrated acceptance.
All requested state changes fail closed until runtime-specific preflight,
operator approval, API continuity and rollback have been implemented.
"""
from __future__ import annotations

from ..common import Stage, run as run_stage

SPEC = Stage(
    "svc", "Service management",
    ("inventory", "health", "logs", "start", "stop", "restart",
     "rollback", "proxy", "gateway"),
    ("read-only service/port/container inventory",
     "identified active model and exact runtime ownership",
     "scoped approval for stateful Docker/GPU/API actions",
     "verified fallback and recovery plan"),
)


def run(argv, *, as_json=False, dry_run=False):
    return run_stage(SPEC, list(argv), as_json=as_json, dry_run=dry_run)
