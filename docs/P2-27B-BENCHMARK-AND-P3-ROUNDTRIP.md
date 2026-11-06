> **SUPERSEDED P3 PROCEDURE (2026-11-06):** The user changed the required P3 order. P2 must **STOP** after actual bench/Flash-Next restore; it must NOT auto-enter P3. Separately enter P3, establish 27B active, verify **27B → Flash-Next**, then resolve P1 deficiencies and rebenchmark Flash-Next, then finish **Flash-Next → 27B** with 27B active. The old two-roundtrip commands below are **RETIRED/BLOCKED**. Follow [P3-MANUAL-TRANSITION-SEQUENCE-20261106.md](P3-MANUAL-TRANSITION-SEQUENCE-20261106.md). P2 benchmark instructions below are still applicable.

# P2 27B bounded GPU benchmark, followed by P3 two-cycle roundtrip acceptance

Date: 2026-11-06. Branch: `feature/recipe-wizard-handoff`. **SOURCE READY/CPU CI**, GPU benchmark and repeated P3 trials **NOT RUN**.

## Confirmed DGX starting point

- Existing production: NVIDIA Flash-Next on unchanged `:8000/v1`; actual manifest-led `./wizard.sh service manager status --json` previously returned `LIVE_SERVICE_VERIFIED`, served ID `qwen3.8-flash-next`, same immutable image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`.
- Pinned NVIDIA Qwen3.8-27B-NVFP4 checkpoint revision `482ca0f3832238542f8f5295dde86b5f22711d80` present, 3/3 indexed shards.
- The **first real GPU one-shot trial** already achieved `PASS_RESTORED`: 27B API ready, bounded inference PASS, original Flash-Next restored. It was NOT a timed benchmark or repeated permanent-switch test.

## P2 benchmark (primary next action)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh model 27b benchmark --plan --json
```

The **plan-only** command is safe: reads pinned source, exact image and running source facts, Docker GPU-container inventory and :8000 API; does NOT stop/launch inference. Expected success status is `READY_TO_REQUEST_TRIAL_APPROVAL` with a **distinct 64-hex benchmark plan ID**, separate from the original one-shot `--trial-plan`. Any `BLOCKED` or unexpected issue forbids execution. Plan expires in the existing 10-minute window. `./scripts/serve_27b.sh --bench-plan` is a compatibility alias; prefer Wizard.

**Actual execution, only in an explicitly approved Flash-Next downtime window:** the dedicated `./wizard.sh model 27b benchmark --execute --approve-plan "$BENCH_ID" --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME --json` route uses `scripts/manager/p2_27b_benchmark.py` with **the existing exact-identity, exclusive-GPU, lock-protected one-shot `p2_27b_gpu_trial.execute` executor**. It stops the original `qwen38-flash` (without removing it), starts the pinned 27B transient `qwen38-27b`, checks exact 27B API, performs **3 sequential SSE requests with at most 64 generated tokens each**, then stops/removes only the labeled transient and restarts the original Flash-Next. A fresh manifest + API check must confirm original `qwen3.8-flash-next`.

The benchmark records per-request client-measured latency, TTFT (first streamed content *or reasoning*), completion and prompt token counts when reported, end-to-end tokens/sec, **decode tokens/sec proxy** and prompt-ingestion/sec proxy; p50/p95 summaries, a before/after best-effort `nvidia-smi` memory sample (may be unavailable for unified-memory GB10), and success/failure. Prompts are static embedded diagnostics; only their SHA256, not generated text, is recorded. **True internal prefill throughput, decode kernel throughput, GPU memory peak, vision, tool-call performance and large contexts are NOT measured by this first 3-request profile**; the proxy metrics must never be misrepresented as engine metrics. Request time ceiling 180 seconds with socket timeout and SSE bounds; one active model, no MTP/PLE. On any failure the existing executor attempts original restore; SIGKILL, host OOM/power or Docker failure can defeat automatic recovery.

The base trial JSON and target log remain operator-private in `~/.local/state/blazux-wizard/p2`. The new `*.benchmark.json` stores measured metrics and final restore verification in the same protected directory, mode 0600. A successful run must report **`BENCH_PASS_RESTORED_VERIFIED`**, `benchmark.status=PASS`, `restoration.status=RESTORED`, and `post_restore_wizard_status.status=LIVE_SERVICE_VERIFIED` with `flash-next`. If the benchmark or return-to-original check is incomplete, do not call P2 complete.

## P3 two-cycle temporary roundtrip (AFTER P2 actual benchmark PASS)

```bash
./wizard.sh switch flash-next-27b roundtrip --plan --json
```

This starts **read-only**. P3 plan **must be BLOCKED** with `P2_BENCHMARK_RECEIPT_NOT_FOUND` or `P2_BENCHMARK_NOT_QUALIFIED` until the actual latest private `*.benchmark.json` is valid and reports the exact P2 success described above. An original one-shot `PASS_RESTORED` by itself is **not enough**. The P3 exact plan ID binds the current Flash-Next container/image/API preflight, benchmark receipt digest and exactly **2** cycles. It cannot reuse the P2 ID.

Once separately approved (not authorized by this document), `./wizard.sh switch flash-next-27b roundtrip --execute --approve-plan "$P3_PLAN_ID" --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME --json` performs **two** successive Flash-Next → temporary 27B → restored original Flash-Next cycles, each with exact fresh preflight and per-cycle original container ID + `/health`/`/v1/models` Wizard verification. If any cycle fails or cannot prove original recovery, **do not run the next cycle**. Report private `p3-roundtrips-*.json`, statuses `P3_TEMPORARY_ROUNDTRIP_PASS` or `P3_INCOMPLETE_OR_BLOCKED`. This is a bounded two-cycle *reversion trial*, **NOT** implementation or qualification of permanent model switching; the production-service handover and fault injection remain separate P3 acceptance goals.

## Boundaries and evidence

- No automatic benchmark, P3 trial or live service mutation by installing/updating the code, displaying the Wizard or running `--plan`.
- No source model deletion, model re-download, image rebuild, HF cache changes, proxy/gateway modifications, MTP, YaRN or Orcarouter work.
- Preserve current live source, one GPU model and port :8000. Never merge Draft PR #1 merely because source code and CPU tests pass.
- **Source/CPU CI does not establish DGX performance**. Operator must supply reviewed actual P2 output/metric evidence; record it in the handoff before subsequent P3 maintenance execution.
