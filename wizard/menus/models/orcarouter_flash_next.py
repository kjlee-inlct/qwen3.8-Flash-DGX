"""P5 Orcarouter BF16PLE Wizard adapter (source-only until GPU ABI is qualified)."""
from __future__ import annotations

import argparse
import json

from ..common import Stage
from scripts.manager import p5_orcarouter as p5

SPEC = Stage(
    "p5", "Orcarouter Flash-Next",
    ("doctor", "recipe", "prepare", "start", "verify", "benchmark"),
    ("Blazux vLLM 0.32 ABI/loader qualification",
     "128/128 direct BF16 PLE audit", "31/31 pinned donor BF16 MTP audit",
     "fresh 27B preservation and exact rollback approval",
     "strict numerical reproducibility release gate"),
    ("orcarouter",),
)


def run(argv, *, as_json=False, dry_run=False):
    parser = argparse.ArgumentParser(prog="wizard p5")
    parser.add_argument("command", nargs="?", default="status",
                        choices=("status", "plan", *SPEC.actions))
    parser.add_argument("--for-action", choices=SPEC.actions)
    parser.add_argument("--profile", choices=("mtp0", "mtp2"), default="mtp0")
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--read-only", action="store_true")
    parser.add_argument("--cpu-only", action="store_true")
    parser.add_argument("--gpu-trial", action="store_true")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--ack-downtime")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    as_json = as_json or args.json
    dry_run = dry_run or args.dry_run
    if args.read_only and not (args.execute or args.approve_plan or args.gpu_trial):
        doc = p5.read_only()
    elif args.cpu_only and not (args.execute or args.approve_plan or args.gpu_trial):
        doc = p5.cpu_only()
    elif args.gpu_trial:
        doc = p5.source_plan(args.profile)
        doc["issues"] = ["P5_GPU_TRIAL_EXECUTOR_NOT_RELEASED",
                         "SEPARATE_APPROVAL_AND_VERIFIED_RESTORE_REQUIRED"]
        doc["action"] = "GPU_TRIAL"
    else:
        action = args.for_action if args.command == "plan" else args.command
        if not action or action == "plan":
            doc = p5.source_plan(args.profile)
        else:
            doc = p5.stage_action(action, profile=args.profile,
                                  execute=args.execute,
                                  approve_plan=args.approve_plan)
        if args.ack_downtime:
            doc["issues"] = sorted(set(doc["issues"] + [
                "UNVERIFIED_APPROVAL_CANNOT_EXECUTE"]))
    if dry_run:
        doc["dry_run"] = True
    if as_json:
        print(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("P5 Orcarouter: " + doc["status"] + " — no DGX GPU mutation")
        for issue in doc.get("issues", []):
            print("  - " + issue)
    return 0 if args.command == "status" and not (
        args.execute or args.approve_plan or args.ack_downtime
        or args.gpu_trial or args.read_only or args.cpu_only
    ) else (0 if doc["status"] == "PASS" else 3)
