#!/usr/bin/env bash
# Blazux P1-P7 Wizard: one interactive and automation-compatible entrypoint.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
exec python3 -m wizard "$@"
