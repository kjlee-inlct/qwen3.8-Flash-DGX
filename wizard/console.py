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
    print("  Recommended: " + ("Open model actions / diagnostics" if doc["next_action"] == "none" else str(doc["next_action"])))
    for step in doc["selection"].get("steps", []):
        print("   - " + ("review model" if step["action"] == "review_p1" else step["action"]) + ": " + step["state"]
              + " — " + step["reason"])
    preview = doc["selection"].get("transition_preview")
    if preview:
        print("  Transition: BLOCKED pending source/target qualification and recovery")
    print("  Use All model actions for verification, benchmark and guarded lifecycle operations.")


def _actions_menu(model: str) -> None:
    actions = list(MODEL_ACTIONS[model])
    while True:
        doc = model_workflow(model)
        print("\n" + doc["title"] + " — actions (0 back)")
        for i, cap in enumerate(doc["actions"], 1):
            # Internal rollout identifiers belong in plans, not operator menus.
            display = ("APPROVAL_REQUIRED" if cap["status"] == "GUARDED_P1"
                       else cap["status"])
            print(f" {i:2}. {cap['action']:<11} [{display}]")
        action = _choice(_input("Action (0 back): "), actions)
        if action is None:
            return
        if not action:
            print("Unknown action; nothing executed.")
            continue
        capability = next(cap for cap in doc["actions"] if cap["action"] == action)
        if capability["status"] == "GUARDED_P1" and model == "flash-next":
            # The operator already chose the action above: do not ask for it
            # again inside the legacy P1 submenu. Execution stays in the
            # existing exact-plan/rechecked-backend approval boundary.
            if _input("Review current NVIDIA Flash-Next " + action
                      + " plan for approval? [y/N]: ") != "y":
                print("Cancelled.")
                continue
            from wizard.menus.models import flash_next
            flash_next.run(["guided", "--for-action", action])
        elif capability["status"] == "APPROVAL_REQUIRED":
            print("Operation uses a separate exact-plan approval Wizard.")
            if _input("Open its guarded Wizard? [y/N]: ") != "y":
                print("Cancelled.")
                continue
            invoke_model_action(model, action, workflow=doc, guided=True)
        else:
            invoke_model_action(model, action, workflow=doc)




def _history_menu(model: str) -> None:
    """Read-only history from local project and immutable legacy receipts.

    No /health, inference, Docker or GPU calls. Results are summaries; the
    model ID is resolved from the service-policy manifest by the catalog.
    """
    from scripts.manager.evidence_catalog import history
    categories = {"1": "all", "2": "verify", "3": "benchmark",
                  "4": "transition", "5": "trial", "6": "diagnostics"}
    while True:
        print("\nPast model results (read-only, 0 back)")
        print(" 1. All records")
        print(" 2. Verify")
        print(" 3. Benchmark")
        print(" 4. Model transitions")
        print(" 5. GPU trials")
        print(" 6. Diagnostics")
        picked = _input("History (0 back): ")
        if picked in (None, "0"):
            return
        if picked not in categories:
            print("Unknown category; nothing executed.")
            continue
        try:
            doc = history(model=model, kind=categories[picked], limit=20)
        except (OSError, ValueError, TypeError) as exc:
            print("History unavailable: " + type(exc).__name__)
            continue
        if doc["status"] != "READ_ONLY_HISTORY":
            print("History blocked: " + ", ".join(doc.get("issues") or []))
            continue
        print("\nModel: " + doc["model"] + " | " + doc["category"]
              + " | " + str(doc["count"]) + " unique records")
        for rec in doc["records"]:
            print(" - " + rec["timestamp_utc"] + " | "
                  + rec["category"] + " | " + rec["status"])
            summary = rec.get("summary") or {}
            if rec["category"] == "verify":
                print("   baseline=" + str(summary.get("baseline_status"))
                      + ", extended=" + str(summary.get("extended_status")))
                for name, status in summary.get("probes", {}).items():
                    print("   " + name + "=" + str(status))
            if rec["category"] == "benchmark":
                for key, caption, unit in (
                    ("mean_tokens_per_sec", "Mean throughput", "tokens/sec"),
                    ("mean_e2e_tokens_per_sec", "Mean E2E throughput", "tokens/sec"),
                    ("mean_decode_tokens_per_sec_proxy", "Decode proxy", "tokens/sec"),
                    ("ttft_p50_sec", "TTFT p50", "sec"),
                    ("ttft_p95_sec", "TTFT p95", "sec"),
                    ("latency_p50_sec", "Latency p50", "sec"),
                    ("latency_p95_sec", "Latency p95", "sec"),
                ):
                    if summary.get(key) is not None:
                        print("   " + caption + ": " + str(summary[key]) + " " + unit)
            if rec["category"] == "transition":
                print("   " + str(summary.get("from_model")) + " -> "
                      + str(summary.get("to_model"))
                      + "; live verified=" + str(summary.get("live_verified")))
            print("   Evidence: " + rec["path"])
        if doc.get("issues"):
            print("Note: " + str(len(doc["issues"]))
                  + " unreadable/untrusted file(s) not displayed. No files changed.")

def _switch_preview(model: str) -> None:
    """Review one ordinary switch candidate; never launch the P3 one-off stages."""
    if model not in ("flash-next", "27b"):
        print("General switching for this model is not runtime-qualified.")
        return
    from scripts.manager.operational_switch import make_plan
    doc = make_plan(model)
    print("\nOrdinary model switch — read-only candidate")
    print("  Current: " + str(doc.get("source_model") or "unverified"))
    print("  Requested: " + model + " | API stays :8000/v1")
    print("  Status: " + doc["status"])
    if doc.get("plan_id"):
        print("  Candidate fingerprint (NOT an executable approval): " + doc["plan_id"])
    for issue in doc.get("issues", []):
        print("  Blocker: " + issue)
    if (doc.get("source_model") == "27b"
            and doc.get("current_live_status") == "LIVE_SERVICE_VERIFIED"):
        print("  API identity alone does NOT prove 27B text generation.")
        print("  Optional live 27B curl smoke (one inference, no model switch):")
        print("    bash scripts/temporary/operational-27b-curl-smoke.sh")
        print("  Smoke is not invoked by this read-only preview.")
    print("  No service stopped or started. Historical P3 A/B/C are not rerun.")
    print("  Actual operating execution remains blocked until the independent")
    print("  guarded executor, recovery tests and operator downtime approval qualify.")


def _switch_guided(model: str) -> None:
    """Model-first, release-gated review; never replay P3 acceptance stages."""
    if model not in ("flash-next", "27b"):
        print("General switching for this model is not runtime-qualified.")
        return
    from scripts.manager.operational_wizard import guided
    guided(model)


def _model_screen(model: str) -> None:
    while True:
        doc = model_workflow(model)
        _display_workflow(doc)
        print("  1. Continue recommended step")
        print("  2. All model actions / diagnostics")
        print("  3. Refresh observed state")
        print("  4. Past Verify / Benchmark / transitions (read only)")
        print("  5. Review ordinary model switch (read only)")
        print("  6. Guided operating switch (release gated)")
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
            elif model == "27b" and doc["status"] == "SOURCE_PRESENT_UNQUALIFIED":
                print("Pinned source found; running read-only 27B runtime preflight.")
                invoke_model_action(model, "inspect", workflow=doc)
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
        elif selected == "4":
            _history_menu(model)
        elif selected == "5":
            _switch_preview(model)
        elif selected == "6":
            _switch_guided(model)
        else:
            print("Unknown option; nothing executed.")


def _model_selector() -> None:
    names = list(MODEL_CHOICES)
    print("\nSelect a model (0 back)")
    for i, name in enumerate(names, 1):
        print(f" {i}. {MODEL_CHOICES[name]['title']}")
    print(f" {len(names) + 1}. Installed models (read only / legacy caches)")
    typed = _input("Model: ")
    if typed in (str(len(names) + 1), "installed", "list"):
        from wizard.main import main as cli_main
        cli_main(["model", "list", "--installed"])
        return
    selection = _choice(typed, names)
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
        ("Switch Flash-Next ↔ 27B", flash_next_27b),
        ("Storage / selective cleanup", flash_next_cleanup),
        ("Switch Orcarouter ↔ 27B", orcarouter_27b),
        ("System acceptance / proxy / gateway", system),
    ]
    while True:
        print("\nAdvanced management (0 back)")
        print(" 1. Model lifecycle actions")
        for i, row in enumerate(rows, 2):
            print(f" {i}. {row[0]}")
        print(" 6. Legacy group / stage tools")
        print(" 7. Readiness dashboard")
        print(" 8. Copy historical reports into project (guarded, originals retained)")
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
        if selected == "7":
            from wizard.roadmap import run_cli
            run_cli()
            continue
        if selected == "8":
            from scripts.manager.evidence_catalog import main as evidence_main
            print("Copy-only legacy evidence import. No old record, lock, or "
                  "service journal will be moved or removed.")
            if _input("Review exact copy plan? [y/N]: ") == "y":
                evidence_main(["migrate", "--guided"])
            continue
        if selected not in ("2", "3", "4", "5"):
            print("Unknown option.")
            continue
        mod = rows[int(selected) - 2][1]
        _stage_actions(mod)


def _stage_actions(module) -> None:
    spec = module.SPEC
    actions = list(spec.actions)
    if spec.key == "p3":
        # One-off P3 A/B/C acceptance is complete. Keep CLI compatibility,
        # but do not invite operators to replay those stages from a menu.
        actions.append("ordinary-switch-preview")
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
        if spec.key == "p3" and selected == "ordinary-switch-preview":
            direction = _choice(_input("Review target: 1 Flash-Next / 2 NVIDIA 27B (0 back): "),
                                ["flash-next", "27b"])
            if direction in ("flash-next", "27b"):
                _switch_preview(direction)
            elif direction is not None:
                print("Unknown target; nothing executed.")
            continue
        if spec.key == "p3" and selected in ("sequence", "stage-a", "stage-b", "stage-c"):
            # Read-only P3 planning only. Each actual service transfer requires
            # its own separately reviewed plan ID and downtime acknowledgment.
            module.run([selected, "--plan"])
            if selected.startswith("stage-"):
                print("Execution NOT initiated. Review plan and request independent downtime approval.")
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
