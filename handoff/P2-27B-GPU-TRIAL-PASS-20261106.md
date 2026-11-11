# P2: NVIDIA Qwen3.8-27B real DGX GPU trial PASS_RESTORED

Source: **actual operator-provided DGX terminal output**, 2026-11-06 (KST; UTC evidence filename is 20261105T230229Z).

```json
{
  "evidence": "/home/inlc/.local/state/blazux-wizard/p2/20261105T230229Z-a4fc14cf8079.json",
  "executed": true,
  "inference_ok": true,
  "restoration": {"issues": [], "status": "RESTORED"},
  "status": "PASS_RESTORED",
  "target_api_ready": true,
  "target_log": "/home/inlc/.local/state/blazux-wizard/p2/20261105T230229Z-a4fc14cf8079.target.log",
  "trial": "PASS"
}
```

The operator explicitly approved an experimental one-shot outage of Flash-Next and ran the pinned **NVIDIA Qwen3.8-27B-NVFP4** using the local vLLM 0.32 image and ModelOpt `modelopt_mixed`. Initial profile: 8192 context, 1 sequence, 0.70 GPU memory fraction, eager mode, no MTP or PLE. The 27B model API became ready and a bounded text inference completed. The trial then returned to the **same preserved original Flash-Next container** and verified the original API `qwen3.8-flash-next` with `/health` and `/v1/models`. This establishes first actual GPU startup/inference and the normal successful restore path, not merely CPU imports.

**Limits:** private local JSON/log paths were provided in stdout, not read or copied; no measured TTFT, prefill/decode tok/s, memory peak, vision, tool calls, MTP, long context or sustained workload. Exceptional rollback (daemon failure, SIGKILL, power loss) and permanent repeated switching remain unverified. Old handoff notes saying GPU NOT_RUN are historical, superseded by the actual successful operator test.

## Preferred read-only operating-state verification: manifest-driven Wizard

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
```

Updated `status` combines *fresh* Docker/socket manifest observation, policy `runtimes/service-policy.json` (one active managed model, :8000) and bounded HTTP `/health` + `/v1/models` matching the expected model ID from the manifest. Expected **post-trial Flash-Next** outcome: `status=LIVE_SERVICE_VERIFIED`, `observed_model=flash-next`, `expected_served_id=qwen3.8-flash-next`, all `checks=true`, `issues=[]`, `operations_enabled=false`. This is **not yet observed on DGX using the new implementation**. It is read-only; it does not prove earlier rollback provenance, GPU exclusivity outside managed containers or performance.

Standalone diagnostics remain `./wizard.sh service manager inventory --json` (manifest observation only), `./wizard.sh service manager health --json` (HTTP status), and `./wizard.sh service manager logs --json` (bounded, potentially private logs). Do not replace these with raw ad hoc `docker ps`/`curl` as primary operator workflow.

**Next stage:** implement P2 Qwen3.8-27B benchmark and functional-test suite in an independently approved, bounded stop→27B→restore trial; collect TTFT, prefill/decode throughput, memory and safe functional probes. Preserve production Flash-Next on :8000. Any fresh GPU transition requires a fresh exact current plan and explicit downtime authorization. Draft PR #1 stays unmerged.
