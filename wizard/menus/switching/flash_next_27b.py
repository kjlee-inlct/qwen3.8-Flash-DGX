"""P3 explicit operator-entry plan; legacy two-cycle runner is retired."""
from __future__ import annotations

import json
from ..common import Stage, run as run_stage

SPEC = Stage(
    "p3", "Flash-Next and 27B switching",
    ("inspect", "switch", "rollback", "verify", "sequence"),
    ("Actual P2 DGX benchmark PASS and fresh service status",
     "Separate P3 operator entry, scoped approval for each switch",
     "27B->Flash-Next success, P1 remediation+benchmark, final 27B verification"),
    ("flash-next", "27b"),
    (("flash-next", "27b"), ("27b", "flash-next")),
)


def run(argv, *, as_json=False, dry_run=False):
    args = list(argv)
    if args[:2] == ["operational", "acceptance"]:
        from scripts.manager.operational_acceptance import main as acceptance_main
        return acceptance_main(args[2:])
    if args[:2] == ["operational", "guided"]:
        from scripts.manager.operational_wizard import main as guided_main
        return guided_main(args[2:])
    if args and args[0] == "operational":
        from scripts.manager.operational_switch import main
        return main(args[1:])
    if args and args[0] in ("stage-a", "stage-b", "stage-c"):
        # Persistent switching is a distinct P3 executor. The individual
        # stage must receive its own exact-plan approval; never chain stages.
        from scripts.manager.p3_persistent_switch import main
        return main([args[0][-1], *args[1:]])
    if args == ["sequence", "--plan"]:
        from scripts.manager.p3_transition_sequence import main
        return main(["plan"])
    if args and args[0] == "sequence":
        print(json.dumps({
            "status": "BLOCKED", "stage": "p3", "executed": False,
            "operations_enabled": False, "plan_id": None,
            "issues": ["P3_SEQUENCE_IS_READ_ONLY",
                       "P3_SEPARATE_OPERATOR_ENTRY_AND_SWITCH_BACKEND_REQUIRED"]}))
        return 3
    if args and args[0] == "roundtrip":
        # Fail closed even for old cached approved IDs or direct CLI calls.
        from scripts.manager.p3_27b_roundtrip import make_plan
        print(json.dumps(make_plan(), indent=2, sort_keys=True))
        return 3
    return run_stage(SPEC, args, as_json=as_json, dry_run=dry_run)
