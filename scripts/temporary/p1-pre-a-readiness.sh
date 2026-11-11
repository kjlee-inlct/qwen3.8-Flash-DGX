#!/usr/bin/env bash
# D-016: tracked operator script. Read-only DGX/P1 inspection and local evidence.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec python3 -m scripts.temporary.p1_pre_a_readiness "$@"
