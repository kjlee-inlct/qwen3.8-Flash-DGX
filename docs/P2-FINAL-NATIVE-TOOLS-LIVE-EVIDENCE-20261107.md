# 2026-11-07 — REAL DGX P2-FINAL 27B Native Tools one-shot trial PASS_RESTORED

## Provenance and scope

- Evidence source: operator-supplied actual DGX terminal stdout in this conversation; not an independent remote read of the machine. Keep full private trial event files on DGX, not copied into Git.
- Entry: `bash scripts/temporary/p2-final-native-tools-operator.sh --execute`, which invokes `scripts.manager.p2_27b_tool_live_trial` in a real interactive TTY after **fresh exact plan SHA and TWO independent downtime/target acknowledgements**. The source SHA at delivery was `a41d86aeadbd761d17ccf13fc5a76df0d9db687b`. User entered the presented SHA and both acknowledgements; expired SHA is **not** reusable.
- Environment: NVIDIA `Qwen3.8-27B-NVFP4` pinned snapshot revision `482ca0f3832238542f8f5295dde86b5f22711d80`; installed vLLM `0.32.0` with registered `qwen3_coder` / `qwen3`; prior independently observed CPU Jinja 5/5 render PASS, SHA-256 `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`.
- Intended trial design: temporarily stop **original preserved** `qwen38-27b`, start separate `qwen38-27b-native-tools-v1` on the SAME :8000 using exact local pinned image, bounded `tool_choice=auto` structured/continuation/SSE probes, then stop variant and restore original `qwen38-27b` even on pass. No deletion or P3 replay. The output confirms normal restore path; no fault injection was performed.

## Actual one-shot executor result

```json
{
  "action": "P2_FINAL_NATIVE_TOOLS_ONESHOT",
  "executed": true,
  "issues": [],
  "original_restored": true,
  "restoration": {"issues": [], "status": "RESTORED"},
  "schema_version": 1,
  "status": "PASS_RESTORED",
  "stream_probe_issues": [],
  "stream_probe_status": "LOCAL_STREAMED_TOOL_CALL_PASS",
  "streamed_tool_call": true,
  "structured_probe_issues": [],
  "structured_probe_status": "LOCAL_STRUCTURED_TOOL_CYCLE_PASS",
  "structured_tool_call": true,
  "tool_result_continuation": true,
  "trial": "PASS"
}
```

**PASS for actual bounded native inference structured tool calls, tool-result continuation, streamed tool calls, and one-shot original restoration.** The tool is synthetic; no real external function or application-side tool execution was tested. Detailed individual argument/ID values and generated model responses are not in the supplied stdout; the bounded probe verified them internally, and the output only reports its status. Full model-side reasoning separation across all OpenWebUI formats remains unqualified.

## Independent operator postcheck after restore

```text
./wizard.sh service manager status --json
  status: LIVE_SERVICE_VERIFIED
  active_container.name: qwen38-27b
  active_container.image_id:
    sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137
  host_port: 8000
  observed_model_ids: ["qwen3.8-27b"]
  api_health_status: API_IDENTITY_CONFIRMED
  issues: []
  manifest_status: OBSERVED_UNQUALIFIED
  gpu_exclusivity_verified: false
  port_process_ownership_verified: false
  operations_enabled: false

python3 -m scripts.manager.operational_audit --json
  status: VERIFIED
  phase: COMMITTED
  event_count: 14
  last_event_hash: ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e
  issues: []

docker ps
  qwen38-27b: Up 3 minutes
  open-webui: Up 2 weeks (healthy)
  portainer: Up 2 weeks
```

**Interpretations:** the ordinary service manifest and API identify restored original 27B and the older independent operating-switch journal remains VERIFIED/COMMITTED at 14 events. Neither `gpu_exclusivity_verified=false` nor `port_process_ownership_verified=false` proves an actual conflict; those scopes are *unverified* by that read-only status route. The running-container list shows no other running model, but does **not** prove that the stopped variant remains present (`docker ps -a` would be needed). The private one-shot trial attempt/event/result files are distinct from the ordinary journal; do not infer their full hash chain from the ordinary audit alone.

## P2-FINAL status after this evidence

**CLOSED, ACTUAL DGX PASS:**
- exact vLLM parser registration and pinned tokenizer/Jinja CPU render compatibility;
- bounded native `tool_choice=auto` structured `tool_calls`;
- synthetic tool-result continuation;
- streamed native structured tools probe;
- one-shot source-stop, separate variant start, one-original-model restore;
- independent read-only original API and ordinary operating-journal postcheck.

**STILL OPEN — do not promote to production or claim P2-FINAL all-pass:**
- Live **Open WebUI Native** application/tool UI end-to-end in a separately approved maintenance session (original 27B is currently serving *without* native tool flags, so current UI cannot validate this variant);
- long-lived variant-aware service policy/manifest, guided Wizard user-facing switching, independent rollback acceptance/fault injection and permanent variant promotion;
- detailed reasoning-content separation across nontrivial generated outputs beyond the bounded probes;
- independently verify private one-shot event/receipt integrity and the stopped trial variant identity, plus GPU process/host-port owner observations if required.

**Never** rerun old P3-C or reuse the one-shot SHA. Existing one-shot `attempt-*.json` blocks another trial pending manual reconciliation and a new source-reviewed workflow. Keep `PRODUCTION_EXECUTION_RELEASED=False` until separately accepted; maintain ONE_ACTIVE_MODEL_ONLY, API :8000, vLLM 0.32 and original model/cache preservation.
