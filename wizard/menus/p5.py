"""P5 Orcarouter-Flash-Next source-only menu adapter."""
from .common import Stage, run as run_stage

SPEC = Stage(
    "p5", "Orcarouter Flash-Next",
    ("doctor", "recipe", "prepare", "start", "verify", "benchmark"),
    ("P1-P3 acceptance", "P4 storage decision",
     "Orcarouter BF16 PLE pinned adapter and 31/31 MTP audit",
     "numeric reproducibility qualification"),
    ("orcarouter",),
)

def run(argv, *, as_json=False, dry_run=False):
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
