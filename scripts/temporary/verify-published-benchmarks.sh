#!/usr/bin/env bash
# Read-only cross-check of Git-published metrics against ORIGINAL private DGX receipts.
# No GPU, Docker, API, Git add/commit/push or benchmark re-execution.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

python3 -m scripts.manager.benchmark_publication \
  --model flash-next \
  --source "$HOME/.local/state/blazux-wizard/p1/20261106T233031Z-66af25d31aab.json" \
  --verify-published

python3 -m scripts.manager.benchmark_publication \
  --model 27b \
  --source "$HOME/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json" \
  --verify-published

echo "Published Flash-Next and NVIDIA 27B summaries match private DGX source receipts."
