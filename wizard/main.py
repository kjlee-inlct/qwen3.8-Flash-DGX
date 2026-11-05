"""Domain-grouped Wizard router, preserving legacy P1-P7 CLI aliases."""
from __future__ import annotations

import json
import sys

from wizard.menus import (
    GROUPS, GROUP_ALIASES, GROUP_TITLES, HANDLERS, STAGE_LOCATIONS,
)

USAGE = """Blazux Wizard (vLLM 0.32 only)

  ./wizard.sh                                simple model-first interactive menu\n  ./wizard.sh select 27b --json              read-only lifecycle selection plan\n  ./wizard.sh model choose flash-next --json same planner
  ./wizard.sh list --json                    model/switch/storage/operations catalog\n  ./wizard.sh workflow 27b --json            full model lifecycle actions and gates\n  ./wizard.sh roadmap --json                 complete P1-P7 acceptance checklist\n  ./wizard.sh workflow 27b --for-action start --json  read-only action capability
  ./wizard.sh model flash-next status --json
  ./wizard.sh model 27b plan --for-action prepare --json
  ./wizard.sh model orcarouter-flash-next status --json
  ./wizard.sh switch flash-next-27b plan --for-action switch \
    --from-model flash-next --to-model 27b --json
  ./wizard.sh storage flash-next status --json
  ./wizard.sh operations system status --json
  ./wizard.sh service manager status --json\n  ./wizard.sh service manager health --json  read-only local API identity\n  ./wizard.sh service manager logs --json    bounded local log tail
  ./wizard.sh service manager plan --for-action restart --json
  ./wizard.sh model 27b status --inspect-runtime --json  read-only qualification
  ./wizard.sh model 27b plan --for-action start --launch-preview --json  blocked dedicated 27B preview
  ./wizard.sh model 27b plan --for-action download --json
  ./wizard.sh model 27b download --guided

Compatibility (same handler, same safety boundaries):
  ./wizard.sh p1 status --json
  ./wizard.sh --stage p3 --action switch --from-model flash-next --to-model 27b --json

P1 execution and P2 download retain exact plan ID approval; 27B start/switch and service mutations remain blocked until runtime qualification.
"""


def catalog() -> dict:
    stages = []
    for stage_id, module in HANDLERS.items():
        group, selection = STAGE_LOCATIONS[stage_id]
        if stage_id == "p1":
            stages.append({
                "stage": stage_id, "title": "NVIDIA Flash-Next",
                "group": group, "selection": selection,
                "module": module.__name__,
                "implementation": "P1_SOURCE_READY_NEEDS_DGX_VALIDATION",
                "runtime": "NOT_VERIFIED", "interface": "status/plan/execute",
                "operations_require_live_plan_approval": True,
            })
        else:
            spec = module.SPEC
            stages.append({
                "stage": stage_id, "title": spec.title,
                "group": group, "selection": selection,
                "module": module.__name__,
                "implementation": (
                    "SOURCE_DOWNLOAD_GUARDED_RUNTIME_BLOCKED" if stage_id == "p2"
                    else "LIVE_READ_ONLY_GUARDED_MUTATIONS" if stage_id == "svc"
                    else "INTERFACE_ONLY"
                ),
                "runtime": "NOT_RUN", "interface": "status/plan",
                "operations_require_live_plan_approval": True,
                "actions": list(spec.actions),
            })
    groups = [{
        "group": name,
        "title": GROUP_TITLES[name],
        "choices": [{"selection": choice, "stage": stage}
                    for choice, stage in choices.items()],
    } for name, choices in GROUPS.items()]
    return {
        "schema_version": 1, "engine": "vllm-0.32",
        "api_host_port": 8000, "groups": groups, "stages": stages,
        "primary_menus": ["select_model", "service", "advanced"],
        "model_selector": "select",
    }


def _advanced_menu() -> int:
    """Keep all legacy module workflows in a secondary, explicit menu."""
    groups = ["model", "switch", "storage", "operations", "service"]
    while True:
        print("\nAdvanced actions (0 back)")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group}: {GROUP_TITLES[group]}")
        try:
            value = input("Advanced group (0 back): ").strip().lower()
        except EOFError:
            return 0
        if value == "0":
            return 0
        group = (groups[int(value) - 1]
                 if value.isdigit() and 1 <= int(value) <= len(groups)
                 else GROUP_ALIASES.get(value, value))
        if group not in GROUPS:
            print("Unknown group.")
            continue
        choices = list(GROUPS[group])
        print("  " + GROUP_TITLES[group])
        for i, selected in enumerate(choices, 1):
            print(f"    {i}. {selected}")
        try:
            picked = input("Item (0 back): ").strip().lower()
        except EOFError:
            return 0
        if picked == "0":
            continue
        selection = (choices[int(picked) - 1]
                     if picked.isdigit() and 1 <= int(picked) <= len(choices)
                     else picked)
        stage = GROUPS[group].get(selection)
        if stage is None:
            print("Unknown selection.")
            continue
        module = HANDLERS[stage]
        if stage == "p1":
            print("Opening the existing, individually approved Flash-Next Wizard.")
            module.run(["guided"])
            continue
        module.run(["status"])
        print("Available plan actions: " + ", ".join(module.SPEC.actions))
        try:
            action = input("Plan action (Enter returns): ").strip().lower()
        except EOFError:
            return 0
        if stage == "p2" and action == "download":
            module.run(["download", "--guided"])
        elif action in module.SPEC.actions:
            module.run(["plan", "--for-action", action])
        elif action:
            print("Unsupported action; no operation executed.")


def interactive() -> int:
    """Delegate all P1–P7 operator navigation to the complete TTY console."""
    from wizard.console import run
    return run()


def _extract_pair(args: list[str], name: str) -> tuple[str | None, list[str]]:
    values = list(args)
    if name not in values:
        return None, values
    at = values.index(name)
    if at + 1 >= len(values) or values[at + 1].startswith("--"):
        raise ValueError(name + " needs an argument")
    result = values[at + 1]
    del values[at:at + 2]
    return result, values


def _normalized(argv: list[str]) -> list[str]:
    """Normalize old --stage flags and category-based --group/--item flags."""
    result = list(argv)
    group, result = _extract_pair(result, "--group")
    item, result = _extract_pair(result, "--item")
    if group is not None or item is not None:
        if not group or not item:
            raise ValueError("--group and --item must be supplied together")
        if result and result[0] in HANDLERS:
            raise ValueError("stage specified twice")
        result = [group, item, *result]
    stage, result = _extract_pair(result, "--stage")
    if stage is not None:
        if result and (result[0] in HANDLERS
                       or result[0] in GROUPS
                       or result[0] in GROUP_ALIASES):
            raise ValueError("stage specified twice")
        result.insert(0, stage)
    action, result = _extract_pair(result, "--action")
    if action is not None:
        group_name = GROUP_ALIASES.get(result[0], result[0]) if result else None
        action_index = 2 if group_name in GROUPS else 1
        if len(result) > action_index and not result[action_index].startswith("--"):
            raise ValueError("command specified twice")
        result.insert(action_index, action)
    return result


def _resolve_stage(args: list[str]) -> list[str]:
    if not args:
        return args
    group = GROUP_ALIASES.get(args[0], args[0])
    if group not in GROUPS:
        return args
    if len(args) < 2 or args[1] not in GROUPS[group]:
        raise ValueError("choose a valid submenu item for " + group)
    return [GROUPS[group][args[1]], *args[2:]]


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    as_json, dry_run = "--json" in raw, "--dry-run" in raw
    args = [value for value in raw if value not in ("--json", "--dry-run")]
    if dry_run and "--execute" in args:
        print(json.dumps({"status": "BLOCKED",
                          "issues": ["DRY_RUN_EXECUTION_CONFLICT"],
                          "executed": False}))
        return 3
    try:
        args = _normalized(args)
        if not (len(args) >= 2 and args[:2] == ["model", "choose"]):
            args = _resolve_stage(args)
    except ValueError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}))
        return 2
    if not args:
        if sys.stdin.isatty() and not as_json:
            return interactive()
        args = ["list"]
    if args[0] in ("help", "--help", "-h"):
        print(USAGE)
        return 0
    if args[0] == "select" or (len(args) >= 2 and args[:2] == ["model", "choose"]):
        from wizard.quickstart import run_cli
        model_args = args[1:] if args[0] == "select" else args[2:]
        return run_cli(model_args, as_json=as_json, dry_run=dry_run)
    if args[0] in ("workflow", "journey"):
        from wizard.workflow import run_cli
        return run_cli(args[1:], as_json=as_json, dry_run=dry_run)
    if args[0] in ("roadmap", "readiness"):
        from wizard.roadmap import run_cli
        if len(args) != 1:
            print(json.dumps({"status": "BLOCKED", "executed": False,
                              "issues": ["ROADMAP_IS_READ_ONLY"]}))
            return 2
        return run_cli(as_json=as_json, dry_run=dry_run)
    if args[0] in ("list", "catalog"):
        data = catalog()
        if as_json:
            print(json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True))
        else:
            for group in data["groups"]:
                print(f"{group['group']}: {group['title']}")
                for item in group["choices"]:
                    print(f"  {item['selection']:<23} ({item['stage']})")
        return 0
    if args[0] not in HANDLERS:
        print("Unknown menu/stage. Run './wizard.sh list'.")
        return 2
    return HANDLERS[args[0]].run(args[1:], as_json=as_json, dry_run=dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
