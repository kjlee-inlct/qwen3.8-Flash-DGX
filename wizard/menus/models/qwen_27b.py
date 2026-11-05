"""P2 27B Wizard adapter: source-only plus opt-in read-only cache inspection."""
from __future__ import annotations

import json
from pathlib import Path

from ..common import Stage, run as run_stage
from scripts.manager.p2_27b_inventory import inspect_27b

SPEC = Stage(
    "p2", "27B",
    ("doctor", "recipe", "prepare", "start", "verify", "benchmark"),
    ("P1 bounded GPU benchmark PASS", "27B vLLM 0.32 compatibility verified",
     "immutable checkpoint revision"), ("27b",)
)


def run(argv, *, as_json=False, dry_run=False):
    args = list(argv)
    if "--inspect-cache" not in args:
        return run_stage(SPEC, args, as_json=as_json, dry_run=dry_run)
    # A diagnostic option is NEVER a backdoor to unlock prepare/start/bench.
    args.remove("--inspect-cache")
    cache_root = None
    if "--cache-root" in args:
        at = args.index("--cache-root")
        if at + 1 >= len(args) or args[at + 1].startswith("--"):
            raise ValueError("--cache-root requires a path")
        cache_root = Path(args[at + 1])
        del args[at:at + 2]
    if args not in ([], ["status"]):
        return run_stage(SPEC, args, as_json=as_json, dry_run=dry_run)
    inspection = inspect_27b(cache_root)
    result = {
        "schema_version": 1, "stage": "p2", "status": "BLOCKED",
        "implementation": "READ_ONLY_ASSET_DISCOVERY",
        "runtime": "NOT_RUN", "executed": False,
        "operations_enabled": False, "approval_accepted": False,
        "issues": ["P2_RUNTIME_ADAPTER_NOT_IMPLEMENTED",
                   "NO_VERIFIED_IMMUTABLE_27B_RECIPE"],
        "inspection": inspection,
    }
    if as_json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("P2 27B — read-only checkpoint inventory; execution BLOCKED")
        print(json.dumps(inspection, indent=2, sort_keys=True))
    return 0  # inspection succeeded, NOT deployment
