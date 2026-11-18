#!/usr/bin/env bash
# P5-D READ-ONLY one-turn operator audit; no inference, Docker writes or sudo.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT"

HEAD="$(git rev-parse HEAD)"
[[ "$HEAD" =~ ^[0-9a-f]{40}$ ]] || { echo "P5D_BAD_GIT_HEAD"; exit 3; }
[[ -z "$(git status --porcelain)" ]] || { echo "P5D_BLOCKED_DIRTY_SOURCE"; exit 3; }
printf 'P5D_SOURCE_HEAD=%s\n' "$HEAD"
printf 'P5D_EXPLICIT_SCOPE=READ_ONLY_NO_SUDO_NO_GPU_INFERENCE\n'

python3 -B -m unittest discover -s tests -p 'test_p5d_live_audit_cpu.py' -v
printf 'P5D_LIVE_AUDIT_CPU_RC=0\n'
python3 -B -m unittest discover -s tests -p 'test_p5_readonly_attribution_cpu.py' -v
printf 'P5D_ATTRIBUTION_CPU_RC=0\n'
python3 -B -m unittest discover -s tests -p 'test_p5d_p6e_cpu.py' -v
printf 'P5D_P6E_CPU_RC=0\n'

./wizard.sh service manager status --json | python3 -c '
import json,sys
s=json.load(sys.stdin)
ok=(s.get("status")=="LIVE_P5_TRIAL_API_VERIFIED"
    and s.get("observed_model")=="orcarouter"
    and s.get("runtime_role")=="DEVELOPMENT_TRIAL"
    and s.get("host_port")==8000
    and s.get("expected_served_id")=="qwen3.8-flash-next-orca-uncensored-bf16"
    and s.get("issues")==[]
    and (s.get("active_container") or {}).get("name")==
        "qwen38-orcarouter-qsa62318-lmhead-v3")
print("P5D_SERVICE_PREFLIGHT_PASS" if ok else "P5D_SERVICE_PREFLIGHT_BLOCKED")
sys.exit(0 if ok else 3)
'

set +e
python3 -B -m scripts.manager.p5d_live_audit --save --json
rc=$?
set -e
printf 'P5D_READONLY_AUDIT_RC=%s\n' "$rc"
printf 'P5D_READONLY_AUDIT_DONE (RC3=EVIDENCE_UNQUALIFIED_NOT_SERVICE_OUTAGE)\n'
printf 'P5D_SOURCE_HEAD_AFTER=%s\n' "$(git rev-parse HEAD)"
test -z "$(git status --porcelain)" || {
  echo "P5D_POST_SOURCE_TREE_DIRTY"; exit 3;
}
