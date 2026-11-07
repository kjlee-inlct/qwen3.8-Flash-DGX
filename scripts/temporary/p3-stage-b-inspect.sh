#!/usr/bin/env bash
# D-016 tracked P3-B read-only source / target preflight. NO execution mode.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec python3 -m scripts.temporary.p3_stage_b_inspect "$@"
