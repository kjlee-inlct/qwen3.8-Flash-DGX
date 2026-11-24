#!/usr/bin/env bash
# P2 source surface audit: explicit CPU-only sandbox; no GPU, network, API or live-service mutation.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
SCRIPT="$ROOT/scripts/manager/p2_27b_image_audit.py"
IMAGE="qwen38-flash-dgx:v0.32"
MODE="--plan"
if [[ $# -gt 1 ]]; then echo "Usage: $0 [--plan|--execute-cpu-only]" >&2; exit 2; fi
if [[ $# -eq 1 ]]; then MODE="$1"; fi
if [[ "$MODE" != "--plan" && "$MODE" != "--execute-cpu-only" ]]; then
  echo "Invalid audit mode" >&2; exit 2
fi
IMAGE_ID="$(docker image inspect "$IMAGE" --format '{{.Id}}')" || exit 3
if [[ ! "$IMAGE_ID" =~ ^sha256:[0-9a-f]{64}$ ]]; then
  echo "Missing or invalid immutable Docker image ID" >&2; exit 3
fi
if [[ "$MODE" == "--plan" ]]; then
  printf '{"status":"CPU_ONLY_PROBE_PLAN","image_id":"%s","gpu":false,"network":false,"host_port":null,"executed":false,"changes_live_service":false}\n' "$IMAGE_ID"
  exit 0
fi
# Explicitly override NVIDIA default runtime; use no --gpus, --privileged or published ports.
exec docker run --rm --pull never --runtime runc --network none \
  --read-only --cap-drop ALL --security-opt no-new-privileges \
  --pids-limit 64 --memory 512m --cpus 1 \
  --user "$(id -u):$(id -g)" -e PYTHONDONTWRITEBYTECODE=1 \
  --mount "type=bind,source=$SCRIPT,target=/opt/p2_27b_image_audit.py,readonly" \
  --entrypoint python3 "$IMAGE_ID" -I /opt/p2_27b_image_audit.py
