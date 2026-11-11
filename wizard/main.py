"""Domain-grouped Wizard router, preserving legacy P1-P8 CLI aliases."""
from __future__ import annotations

import json
import sys

from wizard.menus import (
    GROUPS, GROUP_ALIASES, GROUP_TITLES, HANDLERS, STAGE_LOCATIONS,
)

USAGE = """Blazux Wizard (vLLM 0.32 only)

  ./wizard.sh                                simple model-first interactive menu\n  ./wizard.sh select 27b --json              read-only lifecycle selection plan\n  ./wizard.sh model choose flash-next --json same planner
  ./wizard.sh list --json                    model/switch/storage/operations catalog\n  ./wizard.sh model list --installed --json   read-only pinned and legacy cache discovery\n  ./wizard.sh manifest status --json         shared manifest registry + cross-reference integrity\n  ./wizard.sh manifest validate --json       fails closed on mismatched PLE/model/service pins\n  ./wizard.sh workflow 27b --json            full model lifecycle actions and gates\n  ./wizard.sh roadmap --json                 complete P1-P8 acceptance checklist\n  ./wizard.sh workflow 27b --for-action start --json  read-only action capability
  ./wizard.sh model flash-next status --json
  ./wizard.sh model 27b recipe-diff --json  normalized desired/observed read-only diff\n  ./wizard.sh model 27b recipe-diff --cache-source /host/hf-cache --json  compare observed bind path\n  ./wizard.sh model 27b lifecycle restart --plan --json  read-only recreate decision\n  ./wizard.sh model 27b lifecycle remove --plan --json  scoped removal preview (no execute)\n  ./wizard.sh model 27b plan --for-action prepare --json
  ./wizard.sh model orcarouter-flash-next status --json
  ./wizard.sh model orcarouter-flash-next doctor --json
  ./wizard.sh model orcarouter-flash-next recipe --profile mtp0 --json
  ./wizard.sh p5 doctor --read-only --json  source/PLE/donor and live 27B audit\n  ./wizard.sh p5 trial prepare --json    build isolated vLLM0.32 P5 candidate (27B stays up)\n  ./wizard.sh p5 trial plan --json       exact no-rollback MTP0 GPU plan\n  ./wizard.sh p5 trial execute --approve-plan SHA64 --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json\n  ./wizard.sh p5 trial verify --json     chat inference against already running Orcarouter v3\n  ./wizard.sh p5 trial cleanup-plan --json   only exited failed P5 containers, never live v3\n  ./wizard.sh p5 trial cleanup-execute --approve-plan SHA64 --ack-cleanup I_APPROVE_P5_FAILED_TRIAL_CONTAINERS_ONLY --json
  bash scripts/temporary/p5-one-shot-acceptance.sh --plan --json
  bash scripts/temporary/p5-one-shot-acceptance.sh --cpu-only --json
  bash scripts/temporary/p5-one-shot-acceptance.sh --read-only --json
  bash scripts/temporary/p5-one-shot-acceptance.sh --gpu-trial --json  BLOCKED, separate approval

  ./wizard.sh switch flash-next-27b plan --for-action switch \
    --from-model flash-next --to-model 27b --json
  ./wizard.sh operations recovery-acceptance status --json  P8 fault/recovery/final signoff (source-only)\n  ./wizard.sh storage flash-next status --json
  ./wizard.sh storage flash-next inventory --json  P4-A read-only capacity and model state (NO DELETE)\n  ./wizard.sh storage flash-next dry-run --json  P4-B + P4-C combined review (NO DELETE)\n  ./wizard.sh p4 candidates --dry-run --json  P4-B only\n  ./wizard.sh p4 retire --dry-run --json  P4-C rehearsal only
  ./wizard.sh operations resources snapshot --json  P5 host/Docker/GPU read-only resource telemetry\n  ./wizard.sh operations resources observe --model 27b --samples 3 --interval 5 --json  registered-model telemetry\n  ./wizard.sh operations resources observe --model 27b --samples 3 --interval 5 --summary-only --save --json  compact stdout, full private receipt\n  ./wizard.sh operations generic catalog --json  P5-P8 generic registered model catalog
  ./wizard.sh operations generic observation-capture --model orcarouter --json  P5-C sequential read-only
  ./wizard.sh operations generic ownership-capture --model orcarouter --json  P5-D host process evidence, no inference
  ./wizard.sh operations generic operating-gate-review --from-model orcarouter --to-model 27b --json  P6-D always blocked
  ./wizard.sh operations generic journal-v2-preview --from-model orcarouter --to-model 27b --json  P6-E always blocked\n  ./wizard.sh operations generic fault-matrix --json  all registered pairs, Fake-DGX only\n  ./wizard.sh operations generic fault-matrix --summary-only --json  24-case compact summary\n  ./wizard.sh operations generic preflight --from-model 27b --to-model flash-next --json  read-only P6\n  ./wizard.sh operations generic resource-review --model 27b --resource-evidence /path/resource.json --benchmark-evidence /path/benchmark.json --json\n  ./wizard.sh operations generic integration --model 27b --component-evidence /path/components.json --json  P7 source evidence only\n  ./wizard.sh operations resources observe --samples 3 --interval 5 --json\n  ./wizard.sh operations resources preflight --json  non-authorizing capacity gate review\n  ./wizard.sh switch orcarouter-27b preflight --to-model 27b --json  P6 non-authorizing live review\n  ./wizard.sh switch orcarouter-27b simulate --from-model orcarouter --to-model 27b --json  Fake-DGX only\n  ./wizard.sh operations recovery-acceptance fault-matrix --fake-dgx --json  P8 synthetic failures only\n  ./wizard.sh operations system status --json
  ./wizard.sh service manager status --json   manifest + local API identity (read-only)\n  ./wizard.sh service manager health --json  read-only local API identity\n  ./wizard.sh service manager logs --json    bounded local log tail
  ./wizard.sh service manager plan --for-action restart --json
  ./wizard.sh model 27b benchmark --plan --json  read-only exact P2 benchmark plan\n  ./wizard.sh model 27b benchmark --execute --approve-plan SHA64 --ack-downtime ACK\n  ./wizard.sh switch flash-next-27b operational --target flash-next --plan --json  read-only ordinary switch preview\n  ./wizard.sh switch flash-next-27b operational guided --target flash-next  release-gated TTY review
  ./wizard.sh switch flash-next-27b operational acceptance --target flash-next --plan --json  separate read-only DGX trial preflight\n  ./wizard.sh switch flash-next-27b operational acceptance --target flash-next --execute  trial ONLY, separate TTY downtime approval\n  ./wizard.sh switch flash-next-27b sequence --plan --json  P3 manual-entry read-only sequence\n  ./wizard.sh switch flash-next-27b stage-a --plan --json  read-only planned activation Flash-Next -> 27B\n  ./wizard.sh switch flash-next-27b stage-b --plan --json  read-only planned return 27B -> Flash-Next\n  ./wizard.sh switch flash-next-27b stage-c --plan --json  read-only final plan after post-B P1 rebenchmark\n  ./wizard.sh switch flash-next-27b roundtrip --execute --approve-plan SHA64  RETIRED/BLOCKED\n  ./wizard.sh model 27b status --inspect-runtime --json  read-only qualification
  ./wizard.sh model 27b plan --for-action start --launch-preview --json  blocked dedicated 27B preview
  ./wizard.sh model 27b plan --for-action download --json
  ./wizard.sh model 27b download --guided

Compatibility (same handler, same safety boundaries):
  ./wizard.sh p1 status --json
  ./wizard.sh --stage p3 --action switch --from-model flash-next --to-model 27b --json

P1/P2 guarded actions retain original approval. Routine production switching remains release-gated; only the dedicated one-switch acceptance trial can request fresh independent TTY downtime consent. P3 A/B/C are historical and MUST NOT be replayed. P3-G bidirectional transfer PASS and P8 final fault/recovery acceptance remain distinct. P8 is source-only and not executable.
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
                    else "P4_A_READ_ONLY_INVENTORY_ONLY" if stage_id == "p4"
                    else "P5_SOURCE_ADAPTER_GPU_RELEASE_GATED" if stage_id == "p5"
                    else "GENERIC_COMMON_SOURCE_ONLY_NO_LIVE_EXECUTOR"
                         if stage_id in ("p6", "p7", "p8")
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
        "manifest_registry": {"path": "runtimes/manifest-registry.json",
                              "commands": ["manifest status", "manifest validate"],
                              "read_only": True},
    }


def _advanced_menu() -> int:
    """Keep all legacy module workflows in a secondary, explicit menu."""
    groups = ["model", "switch", "storage", "operations", "service", "manifest"]
    while True:
        print("\nAdvanced actions (0 back)")
        for i, group in enumerate(groups, 1):
            print(f"  {i}. {group}: {GROUP_TITLES.get(group, 'Manifest registry / 읽기 전용 무결성')}")
        try:
            value = input("Advanced group (0 back): ").strip().lower()
        except EOFError:
            return 0
        if value == "0":
            return 0
        group = (groups[int(value) - 1]
                 if value.isdigit() and 1 <= int(value) <= len(groups)
                 else GROUP_ALIASES.get(value, value))
        if group == "manifest":
            from scripts.manager.manifest_registry import main as manifest_main
            manifest_main(["status"])
            continue
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
        elif stage == "p4" and action == "inventory":
            module.run(["inventory"])
        elif action in module.SPEC.actions:
            module.run(["plan", "--for-action", action])
        elif action:
            print("Unsupported action; no operation executed.")


def interactive() -> int:
    """Delegate all P1–P8 operator navigation to the complete TTY console."""
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
        lifecycle_route = (len(args) >= 3 and args[0] == "model"
                           and args[1] in ("flash-next", "27b", "orcarouter")
                           and args[2] in ("lifecycle", "recipe-diff"))
        if not lifecycle_route and not (len(args) >= 2 and args[:2] in
                                       (["model", "choose"], ["model", "list"],
                                        ["operations", "resources"],
                                        ["operations", "measurements"],
                                        ["operations", "generic"])):
            args = _resolve_stage(args)
    except ValueError as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}))
        return 2
    if not args:
        if sys.stdin.isatty() and not as_json:
            return interactive()
        args = ["list"]
    if len(args) >= 2 and args[:2] == ["operations", "generic"]:
        from scripts.manager.generic_operations import main as generic_main
        return generic_main(args[2:] + (["--json"] if as_json else []))
    if (dry_run and len(args) >= 3 and
            args[:3] == ["operations", "measurements", "benchmark-execute"]):
        print(json.dumps({"status": "BLOCKED", "issues": ["DRY_RUN_INFERENCE_CONFLICT"],
                          "inference_executed": False, "service_mutated": False}))
        return 3
    if len(args) >= 2 and args[:2] == ["operations", "measurements"]:
        from scripts.manager.model_measurements import main as measurements_main
        return measurements_main(args[2:] + (["--json"] if as_json else []))
    if len(args) >= 2 and args[:2] == ["operations", "resources"]:
        from scripts.manager.resource_diagnostics import main as resources_main
        return resources_main(args[2:] + (["--json"] if as_json else []))
    if len(args) >= 2 and args[:2] == ["p5", "trial"]:
        if dry_run and any(action in ("prepare", "execute") for action in args[2:]):
            print(json.dumps({"status": "BLOCKED",
                              "issues": ["P5_TRIAL_DRY_RUN_MUTATION_BLOCKED"]}))
            return 3
        from scripts.manager.p5_live_trial import main as p5_live_main
        return p5_live_main(args[2:] + (["--json"] if as_json else []))
    if args[0] == "manifest":
        from scripts.manager.manifest_registry import main as manifest_main
        return manifest_main(args[1:] + (["--json"] if as_json else [])
                             + (["--dry-run"] if dry_run else []))
    if args[0] == "evidence":
        from scripts.manager.evidence_catalog import main as evidence_main
        return evidence_main(args[1:])
    if args[0] in ("help", "--help", "-h"):
        print(USAGE)
        return 0
    if lifecycle_route:
        # Explicit read-only generic lifecycle route. Never pass --execute to a
        # legacy stage handler or turn a candidate SHA into execution approval.
        model = args[1]
        tail = args[2:]
        if tail[0] == "recipe-diff":
            action, options = "status", tail[1:]
        else:
            action = tail[1] if len(tail) >= 2 else "status"
            options = tail[2:] if len(tail) >= 2 else []
        cache_source = None
        if options.count("--cache-source") == 1:
            at = options.index("--cache-source")
            if at + 1 < len(options):
                cache_source = options[at + 1]
                del options[at:at + 2]
        valid_cache_source = (cache_source is None or (
            isinstance(cache_source, str) and cache_source.startswith("/")
            and not any(ord(ch) < 32 for ch in cache_source)))
        if options not in ([], ["--plan"]) or not valid_cache_source:
            print(json.dumps({
                "status": "BLOCKED", "executed": False,
                "approval_accepted": False, "plan_id": None,
                "issues": ["LIFECYCLE_CLI_READ_ONLY_NO_EXECUTE_OR_APPROVAL"],
            }, sort_keys=True))
            return 3
        from scripts.manager.recipe_drift import plan
        doc = plan(model, action, cache_source=cache_source) if cache_source else plan(model, action)
        if dry_run:
            doc["dry_run"] = True
        if as_json:
            print(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            print("Model lifecycle (read-only): " + doc["status"])
            print("  Model: " + model + " | action: " + action)
            print("  Decision: " + str(doc.get("decision", "BLOCKED")))
            for change in doc.get("diff", []):
                print("  Changed " + change["field"] + ":")
                print("    desired=" + str(change["desired"]))
                print("    observed=" + str(change["observed"]))
            for issue in doc.get("issues", []):
                print("  Blocker: " + issue)
            for note in doc.get("advisories", []):
                print("  Note: " + note)
            print("  No Docker/GPU/API mutation authorized.")
        return 0 if doc["status"] != "BLOCKED" else 3
    if len(args) >= 2 and args[:2] == ["model", "list"]:
        if args[2:] != ["--installed"]:
            print(json.dumps({"status": "BLOCKED", "executed": False,
                              "issues": ["ONLY_MODEL_LIST_INSTALLED_READ_ONLY_SUPPORTED"]}))
            return 2
        from scripts.manager.installed_models import installed_models
        try:
            document = installed_models()
        except (OSError, RuntimeError, ValueError) as exc:
            document = {"status": "BLOCKED", "executed": False,
                        "issues": ["INSTALLED_MODELS_UNAVAILABLE:" + type(exc).__name__]}
        if dry_run:
            document["dry_run"] = True
        if as_json:
            print(json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True))
        else:
            if document["status"] == "BLOCKED":
                print("Model inventory unavailable: " + ", ".join(document["issues"]))
            else:
                print("Installed models — read-only cache / recipe inventory")
                for entry in document["models"]:
                    active = " [ACTIVE API VERIFIED]" if entry["active_api_identity_verified"] else ""
                    print("  " + entry["model"] + ": " + entry["source_state"] + active)
                    for snap in entry["cache_snapshots"][:4]:
                        print("     " + snap["snapshot"] + " (" + snap["state"] + ")")
                    ple = entry.get("ple_asset")
                    if ple:
                        print("     PLE " + ple["asset_id"] + ": " +
                              ple.get("source_state", ple["status"]) +
                              " (GPU mmap " + ple["runtime_mmap_status"] + ")")
                    view = entry.get("legacy_recipe_view")
                    if view and view["directory_present"]:
                        print("     legacy recipe view: " + view["path"])
                for other in document["other_cached_repos"]:
                    print("  [unregistered] " + other["repo_id"] +
                          ": snapshot observed, unqualified")
        return 0 if document["status"] == "READ_ONLY_INVENTORY" else 3
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
