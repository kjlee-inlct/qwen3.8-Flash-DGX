# 2026-11-07 — REAL DGX canonical NVIDIA 27B Native Tools migration and fresh benchmark v2 PASS

## Executive evidence verdict

**ACTUAL operator-provided DGX stdout** (not CI or an invented measurement): second independently approved execution of `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --execute` returned `status=COMMITTED`, `issues=[]`, `executed=true`, `native_tools_pass=true`, `benchmark_pass=true`, `benchmark_promoted=true`, `backup_container_deleted=true`. The active canonical container is again named `qwen38-27b`, but is a **NEW Docker container** with the tool-enabled recipe flags. Served API stays `qwen3.8-27b` on host port `8000`; the original backed-up old canonical container was deleted **only after all tests PASS**. Model image, pinned checkpoint, cache, stopped old Native Tools V1 one-shot variant and historical evidence are preserved per design.

**P2 Native Tools canonical recipe migration + bounded benchmark v2 acceptance = REAL DGX PASS.** This closes the attempted recipe-promotion subgate. It does **not** independently qualify the Open WebUI Native UI/agent end-to-end, reasoning/response-quality completion, main interactive Wizard production release or recurring Flash↔27B switch after the canonical container's ID changed.

## Chronology

1. Operator performed a fast-forward `519866d..f90375a` on `feature/recipe-wizard-handoff`, then independently observed the original `qwen38-27b` on :8000 and `LIVE_SERVICE_VERIFIED/issues=[]`.
2. First migration had been `FAIL_RESTORED` due to v1 benchmark predicate, not failed Native Tool Calling. Read-only `--audit-failure` inspected the original Docker identity and the immutable earlier event hash chain. Result: `PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY`, issues empty, original Docker ID matched history. Operator entered a separate exact prior-SHA reconciliation; `RECONCILIATION_RECORDED` confirmed. **Old attempt and reconciliation files are private and retained.**
3. New read-only `--plan`: `READY_FOR_CANONICAL_27B_NATIVE_RECIPE_MIGRATION`, `issues=[]`; recipe SHA pinned and **benchmark version** `p2-27b-native-tools-canonical-benchmark-v2`, sequential 3 requests, max 128 tokens, seed 1234, temperature 0, stream include_usage and `chat_template_kwargs.enable_thinking=false`.
4. Operator issued a NEW manual 64hex plan approval, separate API downtime acknowledgement, and independent successful-benchmark-only backup-container-deletion acknowledgement in a real TTY. Result: **COMMITTED**. Plan was consumed; **never replay the old or new plan SHA**. New active Docker container ID prefix `00094794475a`; old canonical ID prefix `6d9ede0904c2` now historical.
5. `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --status` independently returned `LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED`, `issues=[]`, `latest_benchmark_verified=true`, `backup_container_deleted=true`, `native_tools_qualified_by_one_shot=true`.
6. Independent `./wizard.sh service manager status --json` returned `LIVE_SERVICE_VERIFIED` / `API_IDENTITY_CONFIRMED`, observed sole managed model `27b`, served ID `qwen3.8-27b`, published :8000, `issues=[]`. `python3 -m scripts.manager.operational_audit --json` returned `VERIFIED`, phase `COMMITTED`, event_count **14**, `issues=[]`, unchanged last hash prefix `ece2b07f40d9`.

## Actual NEW benchmark v2 — from DGX live result

All three bounded synthetic SSE Chat Completions: `status=PASS`, `stream_complete=true`, `usage_reported=true`, `content_observed=true`, `reasoning_observed=false`, `failure_reasons=[]`. These measurements are **not** engine-side GPU throughput or quality/semantic grading.

| Benchmark metric | Observed |
| --- | ---: |
| model | `qwen3.8-27b` |
| profile | `p2-27b-native-tools-canonical-benchmark-v2` |
| requests / concurrency / seed | 3 / 1 / 1234 |
| max completion tokens | 128 |
| thinking mode | explicit `enable_thinking=false` (benchmark requests only) |
| mean client end-to-end throughput | **10.9570 tokens/s** |
| mean client decode throughput PROXY | **11.0918 tokens/s** |
| mean prompt/TTFT ingest PROXY | 124.2336 tokens/s |
| client TTFT p50 / p95 | **0.165412 s** / **0.192569 s** |
| end-to-end latency p50 / p95 | **11.597904 s** / **11.623362 s** |
| observed completion token counts | 128, 38, 128 |
| terminal finish reasons | `length`, `stop`, `length` |
| sampled GPU peak | **NOT MEASURED** (`null`) |
| engine prefill throughput | **NOT MEASURED** (`null`) |

**Caveat:** the first and third outputs reached the chosen 128-token cap (`finish_reason=length`), so this proves SSE completion, nonempty data and valid reported token usage/TTFT, but **not fully completed natural-language answers**. The middle request ended with `stop`. These strict protocol checks are the agreed acceptance gate; conversational completeness and Open WebUI Native E2E remain separate. The earlier 64-token v1 benchmark is a **different workload**; do not claim a 10.957/previous-value percentage improvement or benchmark comparability.

## Current Docker inventory after successful promotion

Operator `docker ps -a` list:

- `qwen38-27b`: running (new Native Tools canonical 27B container).
- `qwen38-27b-failed-6d9ede0904c2`: stopped (retained FIRST failure's native candidate for forensic review).
- `qwen38-27b-native-tools-v1`: stopped (retained first one-shot proven variant).
- `qwen38-flash`: stopped preserved Flash fallback.
- `open-webui`: healthy, and `portainer`: running.
- `qwen38-27b-pre-native-6d9ede0904c2`: **no longer listed**, consistent with `backup_container_deleted=true`.

**P3-C:** historical one-time Flash-Next → original NVIDIA 27B final Stage-C on 2026-11-07 at 10:19:39 KST was REAL PASS and already CLOSED. Its old immutable container ID references now describe retired history, NOT the new current canonical Docker ID. **Do not rewrite the P3-C receipts or rerun P3-C.** Ordinary recurring Flash↔27B switch code that insists on the old ID must fail closed pending an explicit current-lineage update.

## P8 decision and remaining work

User specified: defer P2/P3-related 27B Native Tools canonical rollout to P8 **only if second live trial fails**. It did not. **P8 conditional migration ticket INACTIVE / NOT ACTIVATED**. New work on Open WebUI Native E2E, ordinary Wizard runtime identity and release gates can be tracked as their own future acceptance items; they are **not proof that the canonical migration failed**. Keep `ONE_ACTIVE_MODEL_ONLY`, `:8000`, vLLM 0.32.0, original pinned NVIDIA checkpoint + all HF cache/model files/images, preserved private P2/P3/operating receipts and historical benchmark output.

**Evidence scope:** all statements above are derived from operator-pasted DGX terminal output; this public Git commit does not contain private raw attempt/event/result JSON or full approval SHA. No later DGX experiment has been performed by a GitHub commit.
