"""P2 vLLM 27B adapter registration."""
from .common import Stage, run as run_stage
SPEC = Stage("p2","27B",("doctor","recipe","prepare","start","verify","benchmark"),("P1 GPU benchmark PASS","27B vLLM 0.32 compatibility verified","immutable checkpoint revision"),("27b",))
def run(argv, *, as_json=False, dry_run=False):
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
