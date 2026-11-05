#!/usr/bin/env bash
# P1 Flash-Next Wizard; defaults to guided confirmation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ "$#" -eq 0 ]; then
  exec python3 -m scripts.manager.p1_wizard guided
fi
exec python3 -m scripts.manager.p1_wizard "$@"
