"""P3 bidirectional Flash-Next and 27B switch plan interface."""
from ..common import Stage, run as run_stage

SPEC = Stage(
    "p3", "Flash-Next and 27B switching",
    ("inspect", "switch", "rollback", "verify"),
    ("P1 and P2 actual DGX benchmark PASS", "Stable API 8000",
     "Tested rollback plan and target readiness"),
    ("flash-next", "27b"),
    (("flash-next", "27b"), ("27b", "flash-next")),
)

def run(argv, *, as_json=False, dry_run=False):
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
