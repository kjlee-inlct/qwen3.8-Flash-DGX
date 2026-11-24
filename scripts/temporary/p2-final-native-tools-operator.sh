#!/usr/bin/env bash
# P2-FINAL one-shot NVIDIA 27B Native Tools validation. NEVER a production
# service-switch command. --plan is read-only (Docker inspect/API + CPU Jinja).
# --execute requires a NEW interactive approval and temporarily interrupts
# :8000; the guarded Python executor then restores the ORIGINAL 27B.
# Failure after SIGKILL/host reboot/Docker/OOM may require manual reconciliation.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

usage() {
  cat <<'HELP'
P2-FINAL Native Tools V1 (one-shot DGX test; original qwen38-27b restored):
  bash scripts/temporary/p2-final-native-tools-operator.sh --plan
      Read-only exact plan, pinned Jinja CPU check and service/receipt audit.
      Does not stop/start Docker containers or run GPU inference.

  bash scripts/temporary/p2-final-native-tools-operator.sh --execute
      Requires interactive TTY, fresh 64-char plan SHA typed by operator,
      I_ACCEPT_P2_FINAL_NATIVE_TOOLS_DOWNTIME,
      I_APPROVE_DISTINCT_27B_NATIVE_TOOLS_V1.
      Stops original 27B, starts separately named native-tools V1 on :8000,
      probes structured tool_calls and SSE, then restores original 27B
      even after a PASS. Does not delete original container or HF cache.
      There WILL be API downtime; power/host/Docker/OOM failure may prevent
      automated restoration. No unattended retries.

  bash scripts/temporary/p2-final-native-tools-operator.sh --help
HELP
}

case "${1:---plan}" in
  --help|-h|help)
    [[ $# -eq 1 ]] || { echo "ERROR: unexpected extra arguments" >&2; exit 2; }
    usage
    ;;
  --plan)
    [[ $# -le 1 ]] || { echo "ERROR: --plan takes no arguments" >&2; exit 2; }
    exec python3 -m scripts.manager.p2_27b_tool_live_trial plan
    ;;
  --execute)
    [[ $# -eq 1 ]] || { echo "ERROR: --execute takes no arguments; independent TTY approval only" >&2; exit 2; }
    [[ -t 0 && -t 1 ]] || { echo "BLOCKED: independent approval requires a real interactive TTY" >&2; exit 3; }
    exec python3 -m scripts.manager.p2_27b_tool_live_trial execute
    ;;
  *)
    echo "ERROR: unsupported Native Tools V1 operator action '${1}'" >&2
    usage >&2
    exit 2
    ;;
esac
