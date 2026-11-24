#!/usr/bin/env bash
# One-off live DGX operating-switch acceptance, NOT a production release.
# Default is READ-ONLY. --execute needs a real TTY and FOUR exact operator
# inputs. No automatic P3 replays, auto-restoration after PASS, or file cleanup.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"
exec "$ROOT/wizard.sh" switch flash-next-27b operational acceptance "$@"
