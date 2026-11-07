#!/usr/bin/env bash
# ONE-TIME 27B recipe promotion. Read-only by default; live migration only
# after exact NEW plan and TWO distinct operator TTY acknowledgements.
# The normal Wizard P3-C stage and the old P2 trial MUST NOT be re-run.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

usage() {
  cat <<'HELP'
Canonical 27B Native Tools recipe migration:
  bash scripts/temporary/p2-27b-native-recipe-migrate.sh --plan
    Read-only Docker/receipt/API/recipe preflight. No service changes.

  bash scripts/temporary/p2-27b-native-recipe-migrate.sh --execute
    DOWNTIME: requires TTY, fresh plan SHA, downtime + container deletion
    acknowledgements. Stop original qwen38-27b, rename backup, RECREATE
    canonical qwen38-27b from pinned Native Tools recipe. Verify normal
    chat + structured tool_calls + streaming, benchmark 3 requests with
    TTFT/throughput, promote a NEW latest-benchmark pointer. ONLY AFTER
    full pass, remove the verified stopped OLD BACKUP DOCKER CONTAINER.
    Docker images, model files, old benchmarks and P3 receipts persist.
    On precommit failure, attempt original-container rollback; a host or
    Docker crash may prevent automatic restoration. Never blindly retry.

  bash scripts/temporary/p2-27b-native-recipe-migrate.sh --help
HELP
}

case "${1:---plan}" in
  --help|-h|help)
    [[ $# -eq 1 ]] || { echo "Unexpected arguments" >&2; exit 2; }
    usage
    ;;
  --plan)
    [[ $# -le 1 ]] || { echo "Plan does not accept approval flags" >&2; exit 2; }
    exec python3 -m scripts.manager.p2_27b_recipe_migration plan
    ;;
  --execute)
    [[ $# -eq 1 ]] || { echo "Execute accepts no command-line approval flags" >&2; exit 2; }
    [[ -t 0 && -t 1 ]] || { echo "BLOCKED: real interactive DGX TTY required" >&2; exit 3; }
    exec python3 -m scripts.manager.p2_27b_recipe_migration execute
    ;;
  *)
    echo "Unsupported 27B migration action: ${1}" >&2
    usage >&2
    exit 2
    ;;
esac
