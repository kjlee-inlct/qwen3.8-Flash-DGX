#!/usr/bin/env bash
# Read-only isolated CPU import probe; no GPU inference/model cache, port or network.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/scripts/manager/p2_27b_loader_import_audit.py"
IMAGE="qwen38-flash-dgx:v0.32"
MODE="--plan"
if [[ $# -eq 1 ]]; then MODE="$1"; fi
if [[ $# -gt 1 || ("$MODE" != "--plan" && "$MODE" != "--execute-cpu-only") ]]; then
  echo "Usage: $0 [--plan|--execute-cpu-only]" >&2; exit 2
fi
IMAGE_ID="$(docker image inspect "$IMAGE" --format '{{.Id}}')" || exit 3
if [[ ! "$IMAGE_ID" =~ ^sha256:[0-9a-f]{64}$ ]]; then
  echo "Missing or invalid immutable Docker image ID" >&2; exit 3
fi
if [[ "$MODE" == "--plan" ]]; then
  printf '{"status":"CPU_ONLY_IMPORT_PROBE_PLAN","image_id":"%s","gpu":false,"network":false,"model_mount":false,"host_port":null,"executed":false,"changes_live_service":false}\n' "$IMAGE_ID"
  exit 0
fi
# User opts in to ONE transient CPU-only container; no model mount or published port.
exec docker run --rm --pull never --runtime runc --network none \
  --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 128 --memory 2g --cpus 2 \
  --tmpfs /tmp:rw,nosuid,nodev,size=128m \
  --user "$(id -u):$(id -g)" -e PYTHONDONTWRITEBYTECODE=1 \
  -e HF_HUB_OFFLINE=1 -e TRANSFORMERS_OFFLINE=1 \
  --mount "type=bind,source=$SCRIPT,target=/opt/p2_27b_loader_import_audit.py,readonly" \
  --entrypoint python3 "$IMAGE_ID" -I /opt/p2_27b_loader_import_audit.py
