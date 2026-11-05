"""Operator-focused TTY console for all P1–P7 Wizard capabilities.

One selected model → one recommended step. All model lifecycle actions are
exposed for testing; unimplemented P2–P7 operations fail closed. No implicit
Docker/GPU/API mutation is performed by entering menus.
"""
from __future__ import annotations

from wizard.quickstart import MODEL_CHOICES
from wizard.workflow import MODEL_ACTIONS, model_workflow, invoke_model_action


def _input(prompt: str) -> str | None:
    try:
        return input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        return None


def _choice(value: str | None, keys: list[str]) -> str | None:
    if value is None or value == "0":
        return None
    if value.isdecimal() and 1 <= int(value) <= len(keys):
        return keys[int(value) - 1]
    return value if value in keys else ""


def _display_workflow(doc: dict) -> None:
    print("\n" + doc["title"] + " | state: " + str(doc["status"]))
    print("  Active observed: " + str(doc["observed_model"] or "none/unknown"))
    print("  API port: :8000/v1 | model identity verification is separate")
    print("  Recommended: " + str(doc["next_action"]))
    for step in doc["selection"].get("steps", []):
        print("   - " + step["action"] + ": " + step["state"]
              + " — " + step["reason"])
    preview = doc["selection"].get("transition_preview")
    if preview:
        print("  Transition: BLOCKED pending source/target qualification and recovery")
    print("  Full action menu exists for prepare/start/wait/verify/bench/restore.")


def _actions_menu(model: str) -> None:
    actions = list(MODEL_ACTIONS[model])
    while True:
        doc = model_workflow(model)
        print("\n" + doc["title"] + " — actions (0 back)")
        for i, cap in enumerate(doc["actions"], 1):
            print(f" {i:2}. {cap['action']:<11} [{cap['status']}]")
        action = _choice(_input("Action (0 back): "), actions)
        if action is None:
            return
        if not action:
            print("Unknown action; nothing executed.")
            continue
        capability = next(cap for cap in doc["actions"] if cap["action"] == action)
        if capability["status"] in ("GUARDED_P1", "APPROVAL_REQUIRED"):
            print("Operation uses the existing separate, exact-plan approval Wizard.")
            if _input("Open its guarded Wizard? [y/N]: ") != "y":
                print("Cancelled.")
                continue
            invoke_model_action(model, action, workflow=doc, guided=True)
        else:
            invoke_model_action(model, action, workflow=doc)


def _model_screen(model: str) -> None:
    while True:
        doc = model_workflow(model)
        _display_workflow(doc)
        print("  1. Continue recommended step")
        print("  2. All model actions / diagnostics")
        print("  3. Refresh observed state")
        print("  0. Back")
        selected = _input("Choice (0 back): ")
        if selected in (None, "0"):
            return
        if selected == "1":
            next_action = doc["next_action"]
            if next_action in ("download", "open_p1_guided"):
                from wizard.quickstart import interactive_select
                interactive_select(model)
            elif next_action == "monitor_download":
                print("27B download already running. Do not start a second transfer.")
            elif next_action == "none":
                print("Model container is already observed; verify service health separately.")
            else:
                print("BLOCKED: missing runtime qualification or service transition approval.")
                if doc["selection"].get("transition_preview"):
                    for issue in doc["selection"]["transition_preview"]["issues"]:
                        print("  - " + issue)
        elif selected == "2":
            _actions_menu(model)
        elif selected == "3":
            continue
        else:
            print("Unknown option; nothing executed.")


def _model_selector() -> None:
    names = list(MODEL_CHOICES)
    print("\nSelect a model (0 back)")
    for i, name in enumerate(names, 1):
        print(f" {i}. {MODEL_CHOICES[name]['title']}")
    selection = _choice(_input("Model: "), names)
    if selection is None:
        return
    if not selection:
        print("Unknown model; nothing executed.")
        return
    _model_screen(selection)


def _service_menu() -> None:
    from wizard.menus.operations import service as manager
    actions = ["status", "health", "logs", "start", "stop",
               "restart", "rollback", "proxy", "gateway"]
    while True:
        print("\nService management: active inference model on :8000/v1")
        for i, name in enumerate(actions, 1):
            indicator = "read only" if name in ("status", "health", "logs") else "guarded"
            print(f" {i}. {name:<8} [{indicator}]")
        selected = _choice(_input("Action (0 back): "), actions)
        if selected is None:
            return
        if not selected:
            print("Unknown option.")
            continue
        manager.run([selected])


def _advanced_menu() -> None:
    """P3/P4/P5/P6/P7 are discoverable, even before their GPU adapters exist."""
    from wizard.menus.switching import flash_next_27b, orcarouter_27b
    from wizard.menus.storage import flash_next_cleanup
    from wizard.menus.operations import system
    rows = [
        ("Switch Flash-Next ↔ 27B (P3)", flash_next_27b),
        ("Storage / selective cleanup (P4)", flash_next_cleanup),
        ("Switch Orcarouter ↔ 27B (P6)", orcarouter_27b),
        ("System acceptance / proxy / gateway (P7)", system),
    ]
    while True:
        print("\nAdvanced management (0 back)")
        print(" 1. Model lifecycle actions (P1/P2/P5)")
        for i, row in enumerate(rows, 2):
            print(f" {i}. {row[0]}")
        print(" 6. Legacy group / stage tools")
        selected = _input("Choice (0 back): ")
        if selected in (None, "0"):
            return
        if selected == "1":
            _model_selector()
            continue
        if selected == "6":
            from wizard.main import _advanced_menu as legacy_advanced
            legacy_advanced()
            continue
        if selected not in ("2", "3", "4", "5"):
            print("Unknown option.")
            continue
        mod = rows[int(selected) - 2][1]
        _stage_actions(mod)


def _stage_actions(module) -> None:
    spec = module.SPEC
    actions = list(spec.actions)
    while True:
        print("\n" + spec.title + " (0 back)")
        for i, action in enumerate(actions, 1):
            print(f" {i}. {action}")
        selected = _choice(_input("Plan action (0 back): "), actions)
        if selected is None:
            return
        if not selected:
            print("Unknown option.")
            continue
        args = ["plan", "--for-action", selected]
        if spec.key in ("p3", "p6") and selected in ("switch", "rollback"):
            # Explicit pair selection from the known stage contract.
            pairs = list(spec.transitions)
            for i, pair in enumerate(pairs, 1):
                print(f" {i}. {pair[0]} -> {pair[1]}")
            pair_selected = _choice(_input("Direction (0 cancel): "),
                                    [str(i) for i in range(1, len(pairs)+1)])
            if pair_selected is None:
                continue
            if not pair_selected or not pair_selected.isdecimal():
                print("Invalid direction.")
                continue
            src, dst = pairs[int(pair_selected)-1]
            args.extend(["--from-model", src, "--to-model", dst])
        if spec.key == "p4" and selected in ("retire", "restore"):
            args.extend(["--target", "flash-next"])
        module.run(args)


def run() -> int:
    from scripts.manager.service_manifest import inspect_service
    print("Blazux Wizard — one GPU model / port 8000")
    while True:
        try:
            observed = inspect_service()
        except (OSError, RuntimeError, ValueError):
            observed = {"status": "BLOCKED", "observed_model": None,
                        "download_running": False}
        active = (observed.get("observed_model")
                  if observed.get("status") == "OBSERVED_UNQUALIFIED" else None)
        print("\nActive observed: " + (active or "unknown / none")
              + " | API :8000/v1 (verify identity separately)")
        if observed.get("download_running"):
            print("NVIDIA 27B: download container RUNNING; completion unverified")
        print("  1. Select / run model")
        print("  2. Service health / status / logs")
        print("  3. Advanced / recipes / storage")
        print("  0. Exit")
        selected = _input("Select (0 exit): ")
        if selected in (None, "0"):
            return 0
        if selected == "1":
            _model_selector()
        elif selected == "2":
            _service_menu()
        elif selected == "3":
            _advanced_menu()
        else:
            print("Unknown option; nothing executed.")
