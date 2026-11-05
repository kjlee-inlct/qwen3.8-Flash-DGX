#!/usr/bin/env bash
# P2 official NVIDIA Qwen3.8-27B-NVFP4 on DGX Spark — PLAN-ONLY.
# The immutable NVIDIA checkpoint uses ModelOpt MIXED_PRECISION NVFP4/FP8.
# No inference, GPU model launch, service mutation, or model switch is authorized.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODE="${1:---plan}"
if [[ "$MODE" == "--trial-execute" ]]; then
  shift
  exec python3 -m scripts.manager.p2_27b_gpu_trial execute "$@"
fi

usage() {
  cat <<'HELP'
NVIDIA 27B dedicated entrypoint:
  scripts/serve_27b.sh --plan       Read-only pinned launch/source/live-API preview
  scripts/serve_27b.sh --status     Read-only immutable snapshot/runtime audit
  scripts/serve_27b.sh --trial-plan       Read-only exact GPU trial approval plan
  scripts/serve_27b.sh --trial-execute --approve-plan SHA64 --ack-downtime ACK
  scripts/serve_27b.sh --help       Show usage
The 27B execute mode is blocked pending independent vLLM/GPU qualification,
exact approval, and verified Flash-Next service rollback.
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
  --trial-plan)
    exec python3 -m scripts.manager.p2_27b_gpu_trial plan
    ;;
  --status|status)
    exec "$ROOT/wizard.sh" model 27b status --inspect-runtime --json
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
