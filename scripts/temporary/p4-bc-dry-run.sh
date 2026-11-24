#!/usr/bin/env bash
# One-command P4-B + P4-C: Fake-DGX CPU checks, then one DGX read-only probe.
# Absolutely no sudo, Docker rm/prune, cache deletion or service interruption.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONDONTWRITEBYTECODE=1

arg="--json"
if [ "$#" -gt 1 ]; then
  echo "Usage: bash scripts/temporary/p4-bc-dry-run.sh [--json|--fixture-only]" >&2
  exit 2
fi
if [ "$#" -eq 1 ]; then
  arg="$1"
fi

case "$arg" in
  --fixture-only)
    exec python3 -m unittest discover -s tests -p 'test_p4_bc_dry_run_cpu.py' -v
    ;;
  --json)
    python3 -m unittest discover -s tests -p 'test_p4_bc_dry_run_cpu.py' -v >&2
    exec python3 -m scripts.manager.p4_bc_dry_run --json
    ;;
  *)
    echo "Only --json or --fixture-only allowed; live cleanup is P5/P8 gated." >&2
    exit 2
    ;;
esac
