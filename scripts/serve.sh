#!/usr/bin/env bash
# Compatibility dispatcher: default Flash-Next; 27B requires explicit selection.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

usage() {
  cat <<'HELP'
Blazux model-specific serving entry points:
  scripts/serve.sh                       Backward compatible Flash-Next
  scripts/serve.sh flash-next            Explicit Flash-Next
  scripts/serve.sh --model flash-next    Explicit Flash-Next
  scripts/serve.sh 27b --plan            Read-only NVIDIA 27B launch preview
  scripts/serve.sh --model 27b --plan    Read-only NVIDIA 27B launch preview

  scripts/serve_flash-next.sh            Original guarded Flash-Next launcher
  scripts/serve_27b.sh --plan            27B preview only, no start/stop/GPU
No automatic service switch or approved 27B GPU start is implemented.
HELP
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  usage
  exit 0
fi

model="flash-next"
if [[ "${1:-}" == "--model" ]]; then
  if [[ $# -lt 2 ]]; then
    echo "ERROR: --model requires flash-next or 27b" >&2
    exit 2
  fi
  model="$2"
  shift 2
elif [[ "${1:-}" == "flash-next" || "${1:-}" == "27b" ]]; then
  model="$1"
  shift
fi

case "$model" in
  flash-next)
    if [[ $# -ne 0 ]]; then
      echo "ERROR: Flash-Next options use environment variables, not positional flags" >&2
      exit 2
    fi
    exec "$HERE/serve_flash-next.sh"
    ;;
  27b)
    exec "$HERE/serve_27b.sh" "$@"
    ;;
  *)
    echo "ERROR: unsupported model '$model'" >&2
    exit 2
    ;;
esac
