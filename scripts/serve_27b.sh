#!/usr/bin/env bash
# P2 official NVIDIA Qwen3.8-27B-NVFP4 on DGX Spark — guarded trial/benchmark.
# The immutable NVIDIA checkpoint uses ModelOpt MIXED_PRECISION NVFP4/FP8.
# Execution requires a fresh exact-plan approval and downtime acknowledgement.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:---plan}"
if [[ "$MODE" == "--bench-execute" ]]; then
  shift
  cd "$ROOT"
  exec python3 -m scripts.manager.p2_27b_benchmark execute "$@"
fi
if [[ "$MODE" == "--trial-execute" ]]; then
  shift
  cd "$ROOT"
  exec python3 -m scripts.manager.p2_27b_gpu_trial execute "$@"
fi

usage() {
  cat <<'HELP'
NVIDIA 27B dedicated entrypoint:
  scripts/serve_27b.sh --plan       Read-only pinned launch/source/live-API preview
  scripts/serve_27b.sh --status     Read-only immutable snapshot/runtime audit
  scripts/serve_27b.sh --tools-profile   Read-only official 27B vLLM tool/reasoning flags
  scripts/serve_27b.sh --tools-variant-plan Read-only protected tools-V1 identity/port/GPU inspection (NO execution)\n  scripts/serve_27b.sh --tools-stream-probe   Bounded local SSE native-tool probe (no Docker changes)\n  scripts/serve_27b.sh --tools-probe     Bounded LOCAL inference tool-call/continuation probe (no Docker change)
  scripts/serve_27b.sh --bench-plan       Read-only P2 27B benchmark plan\n  scripts/serve_27b.sh --bench-execute --approve-plan SHA64 --ack-downtime ACK\n  scripts/serve_27b.sh --trial-plan       Read-only exact GPU trial approval plan
  scripts/serve_27b.sh --trial-execute --approve-plan SHA64 --ack-downtime ACK
  scripts/serve_27b.sh --help       Show usage
27B trial and benchmark need distinct exact-plan approvals and downtime acknowledgement.
Never execute the returned JSON command_preview manually.
HELP
}
if [[ $# -gt 1 ]]; then
  echo "ERROR: 27B runner expects one read-only option" >&2
  exit 2
fi
case "$MODE" in
  --help|-h|help) usage ;;
  --plan|plan)
    exec "$ROOT/wizard.sh" model 27b plan --for-action start --launch-preview --json
    ;;
  --bench-plan)
    cd "$ROOT"
    exec python3 -m scripts.manager.p2_27b_benchmark plan
    ;;
  --trial-plan)
    cd "$ROOT"
    exec python3 -m scripts.manager.p2_27b_gpu_trial plan
    ;;
  --status|status)
    exec "$ROOT/wizard.sh" model 27b status --inspect-runtime --json
    ;;
  --tools-profile)
    cd "$ROOT"
    exec python3 -m scripts.manager.p2_27b_tool_calling profile --json
    ;;
  --tools-variant-plan)
    cd "$ROOT"
    exec python3 -m scripts.manager.p2_27b_tool_variant
    ;;
  --tools-stream-probe)
    cd "$ROOT"
    exec python3 -m scripts.manager.p2_27b_tool_streaming --json
    ;;
  --tools-probe)
    cd "$ROOT"
    exec python3 -m scripts.manager.p2_27b_tool_calling probe --json
    ;;
  --execute|--start|start|--switch|switch)
    echo "BLOCKED: 27B GPU operations need a separately approved runtime and rollback executor" >&2
    exit 3
    ;;
  *)
    echo "ERROR: unsupported 27B action '$MODE'" >&2
    exit 2
    ;;
esac
