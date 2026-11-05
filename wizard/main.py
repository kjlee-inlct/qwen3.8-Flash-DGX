"""Single operator entrypoint. P1 delegates to its tested core; P2-P7 fail closed."""
from __future__ import annotations

import json
import sys
from wizard.menus import HANDLERS


USAGE = """Blazux Wizard v1 (source-first, vLLM 0.32)
  ./wizard.sh                    interactive stage menu (TTY)
  ./wizard.sh list --json        machine-readable capability inventory
  ./wizard.sh p1 status --json
  ./wizard.sh p1 plan --for-action verify --json
  ./wizard.sh p1 verify --execute --approve-plan <current-full-plan-id>
  ./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json
  ./wizard.sh --stage p1 --action status --json

P1 has executable actions only after its existing exact-plan approval and
local preflight. P2-P7 have status/plan interfaces only: execution BLOCKED.
"""


def catalog() -> dict:
    stages = []
    for key, module in HANDLERS.items():
        if key == "p1":
            stages.append({
                "stage": key, "title": "NVIDIA Flash-Next",
                "implementation": "P1_SOURCE_READY_NEEDS_DGX_VALIDATION",
                "runtime": "NOT_VERIFIED", "interface": "status/plan/execute",
                "operations_require_live_plan_approval": True,
            })
        else:
            spec = module.SPEC
            stages.append({
                "stage": key, "title": spec.title,
                "implementation": "INTERFACE_ONLY",
                "runtime": "NOT_RUN", "interface": "status/plan",
                "operations_require_live_plan_approval": True,
                "actions": list(spec.actions),
            })
    return {"schema_version": 1, "engine": "vllm-0.32",
            "api_host_port": 8000, "stages": stages}


def interactive() -> int:
    print("Blazux Wizard — P1..P7, 0 exits")
    while True:
        for item in catalog()["stages"]:
            print("  " + item["stage"] + ": " + item["title"])
        try:
            selected = input("Stage (p1-p7, 0): ").strip().lower()
        except EOFError:
            return 0
        if selected == "0":
            return 0
        if selected not in HANDLERS:
            print("Unknown stage.")
            continue
        if selected == "p1":
            HANDLERS[selected].run(["guided"])
            continue
        module = HANDLERS[selected]
        module.run(["status"])
        print("Available actions: " + ", ".join(module.SPEC.actions))
        try:
            action = input("Action for read-only plan (Enter to return): ").strip()
        except EOFError:
            return 0
        if action in module.SPEC.actions:
            module.run(["plan", "--for-action", action])
        elif action:
            print("Unsupported action; nothing executed.")


def _normalized(argv: list[str]) -> list[str]:
    """Support compact --stage P3 --action switch syntax for remote operators."""
    result = list(argv)
    if "--stage" in result:
        index = result.index("--stage")
        if index + 1 >= len(result):
            raise ValueError("--stage needs p1-p7")
        value = result[index + 1]
        del result[index:index + 2]
        if result and result[0] in HANDLERS:
            raise ValueError("do not specify stage twice")
        result.insert(0, value)
    if "--action" in result:
        index = result.index("--action")
        if index + 1 >= len(result):
            raise ValueError("--action needs an action")
        value = result[index + 1]
        del result[index:index + 2]
        if len(result) >= 2 and not result[1].startswith("--"):
            raise ValueError("do not specify command twice")
        result.insert(1, value)
    return result


def main(argv: list[str] | None = None) -> int:
    raw = list(sys.argv[1:] if argv is None else argv)
    as_json, dry_run = "--json" in raw, "--dry-run" in raw
    args = [value for value in raw if value not in ("--json", "--dry-run")]
    if dry_run and "--execute" in args:
        if as_json:
            print(json.dumps({"status": "BLOCKED",
                              "issues": ["DRY_RUN_EXECUTION_CONFLICT"],
                              "executed": False}))
        else:
            print("BLOCKED: --dry-run and --execute cannot be combined")
        return 3
    try:
        args = _normalized(args)
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
    if args[0] in ("list", "catalog"):
        doc = catalog()
        if as_json:
            print(json.dumps(doc, indent=2, ensure_ascii=False, sort_keys=True))
        else:
            for item in doc["stages"]:
                print(f"{item['stage'].upper():>3}: {item['title']} [{item['implementation']}]")
        return 0
    if args[0] not in HANDLERS:
        print("Unknown stage. Run './wizard.sh list' or './wizard.sh help'.")
        return 2
    handler = HANDLERS[args[0]]
    return handler.run(args[1:], as_json=as_json, dry_run=dry_run)


if __name__ == "__main__":
    raise SystemExit(main())
