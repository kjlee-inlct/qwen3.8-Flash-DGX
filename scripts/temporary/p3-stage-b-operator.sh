#!/usr/bin/env bash
# Tracked D-016 stage B operator interface: default plan is read-only.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec python3 -m scripts.temporary.p3_stage_b_operator "$@"
