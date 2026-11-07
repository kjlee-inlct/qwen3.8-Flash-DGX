"""P7 service/proxy/gateway integration, NOT final P8 operating signoff."""
from ..common import Stage, run as run_stage

SPEC = Stage(
    "p7", "Integrated service / proxy / gateway qualification",
    ("inventory", "service", "proxy", "gateway", "storage", "audit", "integration"),
    ("P1-P6 qualified and P4 storage disposition documented",
     "service/proxy/gateway/storage integration design",
     "integrated component checks and source/CI gates",
     "final fault/restore and release signoff explicitly moved to P8"),
)

def run(argv, *, as_json=False, dry_run=False):
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
