#!/usr/bin/env bash
# Compatibility shim to the central Wizard router.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [ "$#" -eq 0 ]; then
  exec python3 -m wizard p1 guided
fi
exec python3 -m wizard p1 "$@"
