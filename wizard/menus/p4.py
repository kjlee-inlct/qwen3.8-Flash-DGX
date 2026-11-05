"""P4 conditional Flash-Next storage stage; no mutation adapter."""
from .common import Stage, run as run_stage

SPEC = Stage(
    "p4", "Flash-Next conditional storage planning",
    ("inspect", "candidates", "retire", "restore"),
    ("P3 actual DGX switch PASS", "verified capacity pressure",
     "canonical paths and snapshot reference check", "separate scoped approval"),
    ("flash-next",),
)

def run(argv, *, as_json=False, dry_run=False):
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
