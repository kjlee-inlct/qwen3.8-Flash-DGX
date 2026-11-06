#!/usr/bin/env bash
# D-016 tracked operator stage A wrapper; NO implicit execution.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec python3 -m scripts.temporary.p3_stage_a_operator "$@"
