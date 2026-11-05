"""P1 stage menu delegates to the existing guarded Flash-Next backend."""
import json
import sys
from scripts.manager import p1_wizard


def run(argv, *, as_json=False, dry_run=False):
    args = list(argv)
    if dry_run and "--execute" in args:
        print(json.dumps({"stage": "p1", "status": "BLOCKED",
                          "issues": ["DRY_RUN_EXECUTION_CONFLICT"],
                          "executed": False}))
        return 3
    if not args:
        args = ["status"] if as_json or not sys.stdin.isatty() else ["guided"]
    if as_json and args[0] == "guided":
        print(json.dumps({"stage": "p1", "status": "BLOCKED",
                          "issues": ["INTERACTIVE_MODE_REQUIRES_TTY"],
                          "executed": False}))
        return 3
    return p1_wizard.main(args)
