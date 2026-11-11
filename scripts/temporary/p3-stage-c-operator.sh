#!/usr/bin/env bash
# Tracked operator interface for final Flash-Next -> preserved NVIDIA 27B.
# Default --plan is non-disruptive. --execute is separately operator-approved.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec python3 -m scripts.temporary.p3_stage_c_operator "$@"
