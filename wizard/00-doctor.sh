#!/usr/bin/env bash
# CPU/read-only check. No service modifications.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
exec python3 -m scripts.manager.inventory doctor --dry-run "$@"
