"""P3 bidirectional Flash-Next and 27B switch plan interface."""
from ..common import Stage, run as run_stage

SPEC = Stage(
    "p3", "Flash-Next and 27B switching",
    ("inspect", "switch", "rollback", "verify", "roundtrip"),
    ("P1 and P2 actual DGX benchmark PASS", "Stable API 8000",
     "Tested rollback plan and target readiness"),
    ("flash-next", "27b"),
    (("flash-next", "27b"), ("27b", "flash-next")),
)

def run(argv, *, as_json=False, dry_run=False):
    args = list(argv)
    # Explicit opt-in P3 acceptance path. Plain "verify"/"switch" stay
    # blocked. Only fresh P2 benchmark receipt + exact approval enables
    # two temporary roundtrips; never a persistent model switch.
    if len(args) >= 2 and args[0] == "roundtrip" and args[1] in ("--plan", "--execute"):
        import json
        from scripts.manager import p3_27b_roundtrip
        if dry_run and args[1] == "--execute":
            print(json.dumps({"status": "BLOCKED", "executed": False,
                              "issues": ["DRY_RUN_EXECUTION_CONFLICT"]}))
            return 3
        if args[1] == "--plan" and args[2:]:
            print(json.dumps({"status": "BLOCKED", "executed": False,
                              "issues": ["P3_PLAN_CANNOT_ACCEPT_APPROVAL"]}))
            return 2
        return p3_27b_roundtrip.main([
            "plan" if args[1] == "--plan" else "execute", *args[2:]])
    return run_stage(SPEC, args, as_json=as_json, dry_run=dry_run)
