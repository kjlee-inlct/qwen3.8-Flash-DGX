#!/usr/bin/env bash
# Non-disruptive 27B curl smoke: localhost health, served identity, one chat reply.
# This sends a small inference request; it NEVER starts/stops Docker or switches models.
set -euo pipefail

if [[ $# -ne 0 ]]; then
  echo "Usage: bash scripts/temporary/operational-27b-curl-smoke.sh (no arguments)" >&2
  exit 2
fi
command -v curl >/dev/null 2>&1 || { echo "BLOCKED: curl unavailable" >&2; exit 3; }
command -v python3 >/dev/null 2>&1 || { echo "BLOCKED: python3 unavailable" >&2; exit 3; }
BASE="http://127.0.0.1:8000"
MODEL="qwen3.8-27b"

echo "27B live inference smoke; localhost :8000; no service changes"
health="$(curl --silent --show-error --connect-timeout 3 --max-time 10 --output /dev/null --write-out '%{http_code}' "$BASE/health")"
if [[ "$health" != "200" ]]; then
  echo "FAIL: /health returned HTTP $health" >&2
  exit 3
fi
echo "HEALTH_PASS HTTP 200"

models="$(curl --silent --show-error --fail-with-body --connect-timeout 3 --max-time 10 --max-filesize 2097152 "$BASE/v1/models")"
printf '%s\n' "$models" | python3 -c '
import json, sys
try:
    doc = json.load(sys.stdin)
    entries = doc["data"]
    ids = [row["id"] for row in entries]
    if ids != ["qwen3.8-27b"]:
        raise ValueError("expected only qwen3.8-27b; observed " + repr(ids))
except (ValueError, KeyError, TypeError) as exc:
    sys.exit("FAIL: /v1/models identity: " + str(exc))
print("IDENTITY_PASS qwen3.8-27b (only served model)")
'

payload='{"model":"qwen3.8-27b","messages":[{"role":"user","content":"Reply with exactly DGX_OK."}],"max_tokens":256,"temperature":0,"stream":false}'
response="$(curl --silent --show-error --fail-with-body --connect-timeout 3 --max-time 180 --max-filesize 2097152 \
  --header "Content-Type: application/json" --data-binary "$payload" "$BASE/v1/chat/completions")"
printf '%s\n' "$response" | python3 -c '
import json, sys
try:
    doc = json.load(sys.stdin)
    if doc.get("model") != "qwen3.8-27b":
        raise ValueError("completion model identity mismatch")
    choices = doc["choices"]
    if not isinstance(choices, list) or not choices:
        raise ValueError("no completion choices")
    first = choices[0]
    content = first["message"]["content"]
    if not isinstance(content, str) or not content.strip():
        raise ValueError("empty user-visible response")
    finish = first.get("finish_reason")
except (ValueError, KeyError, TypeError, IndexError) as exc:
    sys.exit("FAIL: 27B inference: " + str(exc))
print("INFERENCE_PASS model=qwen3.8-27b finish_reason="
      + str(finish) + " content_preview=" + repr(content[:160]))
'
echo "27B_CURL_SMOKE_PASS health + identity + real text generation"
