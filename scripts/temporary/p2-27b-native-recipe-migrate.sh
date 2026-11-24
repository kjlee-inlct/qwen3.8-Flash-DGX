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

  bash scripts/temporary/p2-27b-native-recipe-migrate.sh --audit-failure
    Read-only check of failed benchmark migration's immutable event chain,
    original Docker ID/API, stopped failed candidate and unchanged journal.

  bash scripts/temporary/p2-27b-native-recipe-migrate.sh --reconcile
    Separately review the already-verified FAIL_RESTORED outcome in a TTY.
    Writes an immutable PRIVATE reconciliation receipt, NOT a Docker action.
    Only this enables a NEW SHA and separate downtime approval for a retry.

  bash scripts/temporary/p2-27b-native-recipe-migrate.sh --status
    Read-only post-migration canonical Docker/API and fresh benchmark audit.

  bash scripts/temporary/p2-27b-native-recipe-migrate.sh --execute
    DOWNTIME: requires TTY, fresh plan SHA, downtime + container deletion
    acknowledgements. Stop original qwen38-27b, rename backup, RECREATE
    canonical qwen38-27b from pinned Native Tools recipe. Verify normal
    chat + structured tool_calls + streaming, benchmark 3 requests
    (v2: 128-token cap, enable_thinking=false ONLY for benchmark) with
    measured TTFT/throughput, promote a NEW latest-benchmark pointer.
    ONLY AFTER
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
  --audit-failure)
    [[ $# -eq 1 ]] || { echo "Audit does not accept arguments" >&2; exit 2; }
    exec python3 -m scripts.manager.p2_27b_recipe_migration audit-failure
    ;;
  --reconcile)
    [[ $# -eq 1 ]] || { echo "Reconcile accepts no command-line approvals" >&2; exit 2; }
    [[ -t 0 && -t 1 ]] || { echo "BLOCKED: operator TTY required for reconciliation" >&2; exit 3; }
    exec python3 -m scripts.manager.p2_27b_recipe_migration reconcile
    ;;
  --status)
    [[ $# -eq 1 ]] || { echo "Status does not accept arguments" >&2; exit 2; }
    exec python3 -m scripts.manager.p2_27b_recipe_migration status
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
