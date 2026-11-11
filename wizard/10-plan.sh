#!/usr/bin/env bash
# CPU/read-only plan. A valid plan is not approval to start or delete.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec python3 -m scripts.manager.inventory plan --dry-run "$@"
