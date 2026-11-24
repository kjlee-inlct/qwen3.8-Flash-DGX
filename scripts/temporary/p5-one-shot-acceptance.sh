#!/usr/bin/env bash
# P5 source/CPU/host-read-only acceptance; GPU trial is permanently gated pending ABI qualification.
set -euo pipefail
cd "$(dirname "$0")/../.."
export PYTHONDONTWRITEBYTECODE=1
exec python3 -B -m scripts.manager.p5_orcarouter "$@"
