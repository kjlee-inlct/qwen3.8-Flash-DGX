from scripts.manager import p1_wizard

def run(argv, *, as_json=False, dry_run=False):
    return p1_wizard.main(argv or ["status"])
