#!/usr/bin/env bash
# P3-D/E/F/G ONE command, READ-ONLY source/DGX acceptance draft.
# This wrapper intentionally has no --execute, sudo, docker mutation or
# approvals; a real transition/fault-injection test is separate.
set -euo pipefail
cd "$(dirname "$0")/../.."
exec python3 -m scripts.manager.p3_dg_acceptance "$@"
