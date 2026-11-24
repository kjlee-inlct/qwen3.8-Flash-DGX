"""P6 Orcarouter/27B bidirectional switch plan interface."""
from ..common import Stage, run as run_stage

SPEC = Stage(
    "p6", "Orcarouter and 27B switching",
    ("inspect", "switch", "rollback", "verify"),
    ("P2 and P5 actual DGX benchmark PASS",
     "stable port 8000 and model ID mapping", "two-way rollback evidence"),
    ("orcarouter", "27b"),
    (("orcarouter", "27b"), ("27b", "orcarouter")),
)

def run(argv, *, as_json=False, dry_run=False):
    args = list(argv)
    if args and args[0] in ("preflight", "simulate"):
        from scripts.manager.p6_p8_fakedgx import main
        return main(args + (["--json"] if as_json else []))
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
