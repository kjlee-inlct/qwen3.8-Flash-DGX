#!/usr/bin/env bash
# D-016: POST-B read-only source, API, and doctor/inventory evidence.
set -euo pipefail
cd "$(dirname "$0")/../.."
exec python3 -m scripts.temporary.p1_post_b_audit --inspect-only "$@"
