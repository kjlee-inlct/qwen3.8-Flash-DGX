"""P4: inventory FIRST (P4-A read-only); retirement is not authorized."""
from __future__ import annotations

import argparse
import json

from ..common import Stage, run as run_stage

SPEC = Stage(
    "p4", "Flash-Next storage: P4-A inspect first; cleanup gated",
    ("inventory", "inspect", "candidates", "retire", "restore"),
    ("P3 source handoff", "P4-A capacity / asset observation",
     "shared HF/image/rollback reference review", "separate scoped approval"),
    ("flash-next",),
)


def run(argv, *, as_json=False, dry_run=False):
    # Only a direct P4-A inventory command may probe the host. A "plan" for
    # inventory is still blocked; --execute/--approve-plan never invoke probes.
    if argv and argv[0] == "inventory":
        parser = argparse.ArgumentParser(prog="wizard p4 inventory")
        parser.add_argument("--json", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--execute", action="store_true")
        parser.add_argument("--approve-plan")
        opts = parser.parse_args(argv[1:])
        as_json = as_json or opts.json
        if opts.execute or opts.approve_plan:
            doc = {
                "schema_version": 1, "stage": "P4-A",
                "action": "STORAGE_CAPACITY_AND_MODEL_STATE_INVENTORY",
                "status": "BLOCKED",
                "issues": ["P4_A_NO_EXECUTION_ALLOWED",
                           "UNVERIFIED_APPROVAL_CANNOT_EXECUTE"],
                "executed": False, "operations_enabled": False,
                "approval_accepted": False, "removal_plan_id": None,
            }
            rc = 3
        else:
            from scripts.manager.p4_a_inventory import inspect_p4_a
            doc = inspect_p4_a()
            if dry_run or opts.dry_run:
                doc["dry_run"] = True
            rc = 0 if doc["status"] == "READ_ONLY_INVENTORY_COMPLETE" else 3
        if as_json:
            print(json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=2))
        else:
            print(f"P4-A storage inventory: {doc['status']} (READ ONLY)")
            print("  No model, image, container or cache deletion is authorized.")
            for item in doc.get("cache_storage", []):
                print("  Cache root #{}: allocated={} bytes, filesystem free={} bytes".format(
                    item["root_index"], item["cache_allocated_bytes"],
                    item["filesystem_free_bytes"]))
            for issue in doc.get("issues", []):
                print("  - " + issue)
        return rc
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
