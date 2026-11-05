"""P7 integrated system acceptance interfaces."""
from ..common import Stage, run as run_stage

SPEC = Stage(
    "p7", "Integrated system operations",
    ("inventory", "service", "proxy", "gateway", "storage", "audit", "acceptance"),
    ("P1-P6 qualified and P4 storage decision recorded",
     "service/proxy/gateway/storage design", "CI and numerical release gates",
     "operator signoff and rollback runbook"),
)

def run(argv, *, as_json=False, dry_run=False):
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
