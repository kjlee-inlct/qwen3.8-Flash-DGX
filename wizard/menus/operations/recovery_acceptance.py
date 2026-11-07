"""P8 fault recovery and final operational acceptance: source-only safety gate.

No fault injection, Docker commands, API mutations or production release.
Execution remains unavailable until independently designed and approved.
"""
from ..common import Stage, run as run_stage

SPEC = Stage(
    "p8", "Fault recovery and final operational acceptance",
    ("preflight", "fault-matrix", "recovery", "audit", "ux", "signoff"),
    (
        "P3-G real bidirectional switching accepted independently",
        "P5/P6 Orcarouter runtime and transfer evidence independently accepted",
        "P7 service/proxy/gateway integration evidence available",
        "Source/Fake-DGX bounded failure matrix and rollback journal checks",
        "Dedicated explicit DGX fault-injection and downtime approval",
        "Independent live restore, API identity, one-model GPU ownership, :8000 and UX proof",
        "Reviewed final production release decision; never inferred from CPU-only or read-only PASS",
    ),
)


def run(argv, *, as_json=False, dry_run=False):
    """The common source-only adapter always denies execution."""
    return run_stage(SPEC, argv, as_json=as_json, dry_run=dry_run)
