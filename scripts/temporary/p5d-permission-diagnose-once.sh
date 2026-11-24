#!/usr/bin/env bash
# Single approved P5-D non-elevated diagnosis; no sudo, Docker exec or inference.
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
[[ "$(git branch --show-current)" == "feature/recipe-wizard-handoff" ]] || {
  echo 'P5D_WRONG_BRANCH'; exit 3;
}
[[ -z "$(git status --porcelain)" ]] || {
  echo 'P5D_DIRTY_SOURCE'; exit 3;
}
printf 'P5D_SOURCE_SHA=%s\n' "$(git rev-parse HEAD)"
python3 -B -m unittest discover -s tests -p 'test_p5d_permission_preflight_cpu.py' -v
printf 'P5D_PERMISSION_CPU_RC=0\n'
python3 -B -m wizard manifest validate --json
python3 -B -m wizard operations generic p5d-source-binding-review --model orcarouter --json
set +e
python3 -B -m wizard operations generic p5d-permission-preflight --model orcarouter --json
rc=$?
set -e
printf 'P5D_PERMISSION_PREFLIGHT_RC=%s\n' "$rc"
if [[ "$rc" -eq 0 ]]; then
  echo 'P5D_READONLY_AUDIT_START=PERMISSION_SAMPLED_NOT_ATTESTED'
  set +e
  python3 -B -m scripts.manager.p5d_live_audit --save --json
  audit_rc=$?
  set -e
  printf 'P5D_READONLY_AUDIT_RC=%s\n' "$audit_rc"
else
  echo 'P5D_FULL_AUDIT_SKIPPED=PROCFS_OR_IDENTITY_BLOCKED'
  echo 'P5D_LIVE_ACCEPTANCE=BLOCKED_NOT_SERVICE_OUTAGE'
fi
test -z "$(git status --porcelain)" || {
  echo 'P5D_SOURCE_DIRTY_AFTER'; exit 3;
}
printf 'P5D_SOURCE_SHA_AFTER=%s\n' "$(git rev-parse HEAD)"
echo 'P5D_NO_PRODUCTION_RELEASE'
