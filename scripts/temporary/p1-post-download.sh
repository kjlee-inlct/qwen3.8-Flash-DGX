#!/usr/bin/env bash
# Temporary P1 post-download operator bundle. Run after original setup chain ends.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec python3 -m scripts.temporary.p1_post_download "$@"
