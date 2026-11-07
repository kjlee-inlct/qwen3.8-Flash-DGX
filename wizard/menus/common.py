"""Shared P2-P7 source-only stage and CLI contract.

Future adapters remain non-executable until individually implemented and tested.
No Docker, GPU, HTTP or filesystem mutation is performed here.
"""
from __future__ import annotations
from dataclasses import dataclass
import argparse
import json


@dataclass(frozen=True)
class Stage:
    key: str
    title: str
    actions: tuple[str, ...]
    prerequisites: tuple[str, ...]
    models: tuple[str, ...] = ()
    transitions: tuple[tuple[str, str], ...] = ()


def describe(spec: Stage) -> dict:
    return {
        "schema_version": 1, "stage": spec.key, "title": spec.title,
        "status": "BLOCKED", "implementation": "INTERFACE_ONLY",
        "runtime": "NOT_RUN", "executed": False, "operations_enabled": False,
        "actions": list(spec.actions), "models": list(spec.models),
        "prerequisites": list(spec.prerequisites),
    }


def plan(spec: Stage, action: str, *, source: str | None = None,
         destination: str | None = None, target: str | None = None,
         execute: bool = False) -> dict:
    if action not in spec.actions:
        raise ValueError("unsupported stage action")
    issues = ["ADAPTER_NOT_IMPLEMENTED", "NO_VALIDATED_RUNTIME_RECIPE",
              "NO_REAL_DGX_ACCEPTANCE_EVIDENCE"]
    if action in ("switch", "rollback"):
        if (source, destination) not in spec.transitions:
            issues.append("INVALID_OR_MISSING_SWITCH_PAIR")
    elif source is not None or destination is not None:
        issues.append("TRANSITION_OPTIONS_NOT_APPLICABLE")
    if spec.key == "p4":
        if target != "flash-next":
            issues.append("NO_EXACT_FLASH_NEXT_TARGET_SELECTED")
        issues.extend(["NO_INDEPENDENT_CAPACITY_PROOF",
                       "NO_CANONICAL_CANDIDATE_AND_REFERENCE_AUDIT",
                       "NO_SEPARATE_PATH_SPECIFIC_APPROVAL"])
    elif target is not None:
        issues.append("TARGET_OPTION_NOT_APPLICABLE")
    return {
        "schema_version": 1, "stage": spec.key, "action": action,
        "status": "BLOCKED", "implementation": "INTERFACE_ONLY",
        "runtime": "NOT_RUN", "executed": False,
        "execution_requested": execute, "operations_enabled": False,
        "approval_accepted": False, "plan_id": None,
        "issues": sorted(set(issues)), "source_model": source,
        "destination_model": destination, "target": target,
        "prerequisites": list(spec.prerequisites),
        "plan_steps": ["Verify model and DGX inventory",
                       "Verify exact immutable recipe and rollback",
                       "Collect operation-specific approval",
                       "Invoke a validated stage adapter",
                       "Collect API/benchmark/recovery evidence"],
    }


def run(spec: Stage, argv: list[str], *, as_json: bool = False,
        dry_run: bool = False) -> int:
    parser = argparse.ArgumentParser(prog="wizard " + spec.key)
    parser.add_argument("command", nargs="?", default="status",
                        choices=("status", "plan", *spec.actions))
    parser.add_argument("--for-action", choices=spec.actions)
    parser.add_argument("--from-model", choices=spec.models)
    parser.add_argument("--to-model", choices=spec.models)
    parser.add_argument("--target")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--approve-plan")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    as_json = as_json or args.json
    dry_run = dry_run or args.dry_run
    if args.command == "status" and not args.execute and not args.approve_plan:
        doc = describe(spec)
        result = 0
    else:
        action = args.for_action if args.command == "plan" else args.command
        if not action or action == "status":
            doc = describe(spec)
            doc["issues"] = ["INVALID_ACTION_OR_APPROVAL"]
        else:
            doc = plan(spec, action, source=args.from_model,
                       destination=args.to_model, target=args.target,
                       execute=args.execute)
        if args.approve_plan:
            doc.setdefault("issues", []).append("UNVERIFIED_APPROVAL_CANNOT_EXECUTE")
        result = 3
    if dry_run:
        doc["dry_run"] = True
    if as_json:
        print(json.dumps(doc, sort_keys=True, ensure_ascii=False, indent=2))
    else:
        print(f"{spec.key.upper()}: {spec.title} — {doc['status']}")
        for issue in doc.get("issues", doc.get("prerequisites", [])):
            print("  - " + issue)
    return result
