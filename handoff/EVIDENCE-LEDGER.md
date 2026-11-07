## E-20261107-27B-OPENWEBUI-AUTO-TOOL-BLOCKED — real operator observation

Direct actual DGX `/v1/chat/completions` with `chat_template_kwargs.enable_thinking=false`: matching `model=qwen3.8-27b`, `message.content="DGX_OK"`, `reasoning=null`, `finish_reason=stop`, `completion_tokens=4`, vLLM `0.32.0-bfe01fe9`. This confirms strict visible-output formatting for **one no-tool request** and no longer implies unconditional reasoning leakage. Separately, real Open WebUI 27B question failed with exact `"auto" tool choice requires --enable-auto-tool-choice and --tool-call-parser to be set`. Neither WebUI settings nor current Docker Cmd were supplied, so root cause is **strongly supported by source 27B launcher flags omission, not fully observed in container**. No changes to running 27B or Open WebUI settings by assistant. Investigate using `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`; do not infer Native Tool Calling PASS.

---

## E-20261107-27B-CURL-SMOKE-REAL-DGX-PASS — received original operator terminal output

Actual DGX operator ran direct localhost `curl` for `/health`, `/v1/models`, and `/v1/chat/completions`, followed by fast-forward from `df3ec01` to `05c1968` and `bash scripts/temporary/operational-27b-curl-smoke.sh`. No Docker mutation or model switch. Direct /v1/models sole ID `qwen3.8-27b`, NVIDIA model root revision `482ca0f3832238542f8f5295dde86b5f22711d80`, `max_model_len=8192`. Direct chat model `qwen3.8-27b`, finish `stop`, 26 completion tokens, `system_fingerprint=vllm-0.32.0-bfe01fe9`; success included `DGX_OK` but also reasoning-like text and literal `</think>` in `message.content` while `message.reasoning` null. Updated smoke printed `HEALTH_PASS`, `IDENTITY_PASS`, `INFERENCE_PASS`, `27B_CURL_SMOKE_PASS`. **REAL DGX generation PASS; EXACT OUTPUT FORMATTING NOT PASS.** Console text is the evidentiary source, not a fabricated private JSON receipt; raw private logs, request IDs and output are not published in repo.

New source-only separate formatting classifier and Fake-CPU tests distinguish `INFERENCE_PASS` from `FORMAT_DEVIATION`; no real DGX rerun of that new script has been claimed. Source CI must be checked at the final new HEAD. P3 general operating switch still `NOT_RUN`.

---

## E-20261107-27B-CURL-SMOKE-SOURCE — inference-specific proof gate

User correctly distinguished `LIVE_SERVICE_VERIFIED` (current API identity) from actual `/v1/chat/completions` functional inference. New bounded, localhost-only `scripts/temporary/operational-27b-curl-smoke.sh` and offline CPU tests `tests/test_operational_curl_smoke_cpu.py` ensure 27B health, exclusive served model identity and one user-visible response are separately checked. Wizard read-only preview provides exact command. Source CI to be checked at latest commit. **Real DGX inference smoke NOT_RUN / output not yet supplied.** Do not conflate script/test creation, old benchmark evidence or PREVIEW READY with fresh model functional acceptance; running 27B and preserved Flash assets remain untouched.

---

## 2026-11-07 — Source-only ordinary operating switch development evidence (NOT a new GPU trial)

GitHub source changes: independent read-only switch preview and new unexposed guarded transaction source, Fake-DGX CPU unit tests, CLI/TTY preview, separated readiness dashboard, and CPU workflow changes. Track \`scripts/manager/operational_switch.py\`, \`scripts/manager/operational_executor.py\`, \`tests/test_operational_switch_cpu.py\`, \`tests/test_operational_executor_cpu.py\` and \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`. Latest CPU run should be verified on GitHub at its actual HEAD; historical CI was 565/565 before these new suites. These are CI/source evidence **only**, not actual DGX. No new physical DGX probe, stop, start, API inference, benchmark, service switch or actual rollback occurred.

Historical independently user-provided P3-C success remains unchanged: 2026-11-07 10:19:39 KST, \`PASS\` with live 27B \`qwen3.8-27b\` on :8000. One-off P3-A/B/C receipts are immutable input evidence only. General operational switch, new rollback, menu execute and P7 release are NOT DGX qualified. Private source receipts and logs remain unmodified and absent from Git. No new release execution approvals were given.

---

## E-20261107-P3-C-FINAL-REAL-DGX-PASS — USER-APPROVED 27B REMAINS ACTIVE

**First actual successfully executed P3-C stage-C evidence from user DGX console, 2026-11-07 10:19:39 KST**: source branch was fast-forward pulled (reported 11 files changed 396 insertions), and operator ran `bash scripts/temporary/p3-stage-c-operator.sh --execute` on real DGX. Read-only preflight `status=READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL`, `issues=[]`, original Flash observed `qwen3.8-flash-next`, original 27B target preserved, after-B P1 Verify/Benchmark/diagnostics hash gate PASS, original P2 27B benchmark SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. C fresh plan SHA `cb88d3be38a4fe1fd965a57aee402c76d53d746fe1cac76640d5b0a4fb6293ad`, expires 2026-11-07 10:20 KST, no rollover (`plan_refreshed=false/refresh_probes=0`). Operator independently typed all three valid current approvals (C-only SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`). Core Wizard executed and returned `{status:PASS,stage:c,executed:true,live_verified:true,active_model:27b}`, exit code zero. Wrapper independently checked final service, observed `post_switch_status=LIVE_SERVICE_VERIFIED` and `post_switch_observed_model=27b`, canonical original `stage-c.json`; final wrapper `status=P3_C_PASS_FINAL_27B_ACTIVE`, `issues=[]`, `approval_accepted=true`, `execution_dispatched=true`, `executed=true`.

Original canonical receipt path: `/home/inlc/.local/state/blazux-wizard/p3/stage-c.json`. Private project report: `/home/inlc/Workspace/llm/blazux-orcarouter/reports/transitions/flash-next--to--27b/p3-c-operator-20261107T011939Z-5f26a6ff25a2.json`. User source original Flash CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`; target 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`. Shared Docker image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137` not model identity on its own. Canonical receipt and reports are PRIVATE on DGX and must never be published raw to Git. **NVIDIA 27B stays running on port 8000; original Flash remains preserved for potential independently approved return.**

**Critical distinction for next sessions:** P1/P2 Verify/Benchmark actual DGX and P3-A/B/C switching backend CLI accepted and evidence-verified. The current interactive `./wizard.sh` menu in `wizard/console.py` only displays P3 stage `--plan` and NEVER executes or guides the transfer. Actual P3-C was executed with `scripts/temporary/p3-stage-c-operator.sh` delegating to canonical `./wizard.sh switch flash-next-27b stage-c --execute`. This proves engine and operator wrapper, **not final user-friendly Wizard UI or routine reversible switch UX**. Preserve completed P3 receipts; don't rerun the one-off P3 acceptance sequence or inadvertently stop 27B. UX phase requires explicit design, separate implementation, fake-CPU tests and independent DGX validation.

---

## 2026-11-07 — TWO REAL P3-C PLAN-EXPIRY BLOCKS; SOURCE-ONLY ROLLOVER REPAIR

Actual DGX operator `bash scripts/temporary/p3-stage-c-operator.sh --execute` emitted two private unique receipts: `reports/transitions/flash-next--to--27b/p3-c-operator-20261107T010814Z-dd8b2073f8cc.json` at 10:08:14 KST and `p3-c-operator-20261107T010930Z-62cf3383e227.json` at 10:09:30 KST. Both show **status=BLOCKED**, `issues=["P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS"]`, `approval_accepted=false`, `executed=false`, `execution_dispatched=false`, source served `qwen3.8-flash-next`, original pinned Flash image/CID `90f39a4d...`, preserved 27B CID `6d9ede09...`, post-B P1 `PASS`, P2 digest `80f109db...`. Canonical SHA `30b2b29bb715e2393b65152ea8d1da2db61956d631efce2248aee2e9690610de` expiry 2026-11-07 **10:10:00 KST**, leaving 106s then 30s (<120s required). These are valid pre-approval safe blocks; no GPU/service mutation or P3-C completion.

Tracked source-only repair in `scripts/temporary/p3_stage_c_operator.py`: `--execute` with **TTY and fully READY initial stage-C provenance only** now runs bounded <=150s **read-only** re-observation across expiring window until a NEW different, still qualified SHA is available with >=120s remaining. Service/target/evidence/Git changes, unexpected before-boundary plan ID changes, non-rotating plans, Ctrl+C, timeout must block without dispatch. Only *new* exact SHA and independent two literals can authorize the unchanged canonical Stage C Wizard. `--plan` unchanged, no automatic consent or activation. New fake DGX virtual-time and full post-refresh C-dispatch tests under `tests/test_p3_stage_c_operator_cpu.py`. Source CI is distinct from **ACTUAL DGX** execution; current P3-C NOT_RUN. Original unmodified stage-A/B receipts and service containers preserved. See [runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## 2026-11-07 — REAL DGX ORIGINAL-TO-GIT BENCHMARK ROUND-TRIP VERIFIED

**New actual DGX operator result (not simulated CPU testing):** After Git fast-forward pull of the benchmark publication implementation, `bash scripts/temporary/verify-published-benchmarks.sh` returned **two `status=VERIFIED` records, each `issues=[]` and `executed=false`**, followed by `Published Flash-Next and NVIDIA 27B summaries match private DGX source receipts.`

- Flash-Next published `benchmarks/published/qwen3.8-flash-next/f506db4c76430674.json`: `VERIFIED`, source original raw SHA256 `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db`.
- NVIDIA 27B published `benchmarks/published/qwen3.8-27b/80f109dbd7c97460.json`: `VERIFIED`, source original raw SHA256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`.

This **closes the previously pending operator DGX source-byte/public-summary reproduction check**. The two allowlisted public JSON summaries exactly match what the validated exporter computes from the original private DGX receipts; no new benchmark, service mutation, stage-C dispatch, Git upload of original private telemetry, or port switch is asserted. This does **not** provide a fresh live model status check or authorize a Stage-C stop. P3-C remains NOT_RUN based on most recent run (cancelled due leading '[' in approval). Next optionally run the latest tracked `bash scripts/temporary/p3-stage-c-operator.sh --plan` for fresh current live gate; separate explicit Flash downtime consent remains mandatory for `--execute`.

---

## 2026-11-07 — PUBLIC/GIT BENCHMARK SUMMARY RECORDS + C APPROVAL CANCEL

User explicitly suggested keeping measured benchmark results in Git. Source branch now tracks sanitized `benchmarks/published/qwen3.8-flash-next/f506db4c76430674.json` and `benchmarks/published/qwen3.8-27b/80f109dbd7c97460.json`, with historical ACTUAL DGX numerical values supplied in user logs and original immutable raw record SHA256 hashes. Flash: 2026-11-06T23:30:31Z, P1 post-B 3 x64 tokens concurrency1, mean 37.9527 tokens/s, TTFT p50/p95 1.384594/1.779602 s, E2E latency p50/p95 1.724560/1.813754 s, 192 output tokens; source raw SHA256 `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db`. 27B: 2026-11-06T04:26:42Z, actual bounded `BENCH_PASS_RESTORED_VERIFIED`, mean E2E 7.9002 tokens/s vs decode proxy 11.1801 (not measured vLLM engine decode throughput); TTFT p50/p95 0.179349/28.977990 s, latency p50/p95 5.818283/34.609889 s, source raw SHA256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`.

Published JSON contains ONLY model/revision/runtime, profile, numeric metrics, receipt SHA, status and limitations; no original raw file or private paths/plan ID/prompt/output/logs were committed. `scripts/manager/benchmark_publication.py`, `tests/test_benchmark_publication_cpu.py`, `scripts/temporary/verify-published-benchmarks.sh` added. **Initial reports transcribed from actual operator output; source-bytes round-trip verification has not yet run on operator DGX**. Read-only one-command verifier must return two VERIFIED events before claiming machine-reconciled publication. Source CI is CPU fixture/provenance validation only.

Actual latest user P3-C `--execute` entered SHA with an extra initial `[`. Wrapper output `status=CANCELLED`, `executed=false`, `execution_dispatched=false`, `approval_accepted=false`. Flash was still observed active; no C service change. New C plan needed for any future intentional switch.

---

## 2026-11-07 — OPERATOR ACTUAL STAGE-C READ-ONLY READY; SOURCE-ONLY C WRAPPER

New operator DGX text `붙여넣은 텍스트(1)(6).txt`: clean fast-forward from `ebebd60` to `20907793795f43b3999d4a6470cbbf766ea87385`; `./wizard.sh evidence list --model 27b --kind benchmark` found ONE original 27B benchmark `20261106T042642Z-0cacd3f29370.benchmark.json`, `mean_e2e_tokens_per_sec=7.9002`, `mean_decode_tokens_per_sec_proxy=11.1801`, `ttft_p50_sec=0.179349`, `status=BENCH_PASS_RESTORED_VERIFIED`. `./wizard.sh evidence migrate --plan` READY with 14 COPY candidates and SHA `44753008...`, but the guided approval prompt received literal `COPY`, so output `CANCELLED/executed=false/copied=0`. Original P1/P2/P3 files unmodified and no import completed.

Actual `./wizard.sh switch flash-next-27b stage-c --plan --json` returned **READY_TO_REQUEST_TRANSITION_APPROVAL**, `issues=[]`, `p1_evidence.status=PASS` (Verify `b5bab417...`, Benchmark `f506db4c...`, diagnostics `38227eee...`), original active Flash container CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, preserved 27B target `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`, source and target images `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, P2 receipt SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, `executed=false/approval_accepted=false`. Historical C SHA `d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7` is short-lived and **never authorizes reuse**. No actual C execution or GPU port transfer.

New **source only** `scripts/temporary/p3_stage_c_operator.py`, `scripts/temporary/p3-stage-c-operator.sh`, `tests/test_p3_stage_c_operator_cpu.py` control canonical Wizard, require three separate fresh manual confirmations for actual --execute and verify both live 27B and canonical stage-C receipt afterward. No actual DGX wrapper execution or C service mutation yet. Original read-only plan is real, source CI is not actual C. [Runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## 2026-11-07 — CPU SOURCE EVIDENCE: model history + copy-only consolidation

Historical actual DGX `blazux-wizard.zip` remains unchanged and is detailed in the earlier operator evidence entry (P3-A/B PASS, post-B P1 Verify/Benchmark PASS, stage-B receipts, original rc3 diagnostics). Added **source only** `scripts/manager/evidence_catalog.py`, `tests/test_evidence_catalog_cpu.py`, Wizard `evidence` route and console model option 4 plus Advanced copy option 8. Catalog reads original private JSON and project-local reports, including `p2/*.benchmark.json` real-shaped E2E/proxy stats and stage A/B transitions. Copy importer rehashes current plan and writes digest-named append-only 0600 copies without ever moving P2/P3 state/locks/journal. Its fake CPU tests do **not** prove any real DGX import or Stage-C readiness. See [contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md).

P3-C remains NOT_RUN, NOT_AUTHORIZED; latest source CI and fresh operator `stage-c --plan --json` must be examined. P1 original receipts and source proof are untouched.

---

## 2026-11-07 — NEW ORIGINAL OPERATOR DGX ZIP / POST-B REAL P1 RECEIPTS

New user-provided `blazux-wizard.zip`, **not source CI**:
- Canonical P3-B `blazux-wizard/p3/stage-b.json`: `PASS/executed=true/live_verified=true`; completed `2026-11-06T22:31:24Z`; Flash-Next restored.
- Read-only diagnostic `blazux-wizard/p3/p1-diagnostics-20261106T231959Z-8de8d9f283d8.json`: PASS, expected own Flash container name/port rc3.
- Latest read-only diagnostic `blazux-wizard/p3/p1-diagnostics-20261106T232509Z-42cd3f5e323f.json`: PASS, expected own Flash container name/port rc3.
- **Actual GPU Verify** `blazux-wizard/p1/20261106T232627Z-82b4aebbdd13.json`: `PASS`, baseline/extended `PASS`, all four probes `PASS`, explicit SHA `dbc86cd43d631ca012e1439c03d7ed7197429aae1e314fc04ee0782ccf20b020`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`.
- **Actual GPU Benchmark** `blazux-wizard/p1/20261106T233031Z-66af25d31aab.json`: `PASS`, separate explicit SHA `72f18943a69b04dad0b082bb1da4e12cac62e12017eeb6170a5fdebbc1a7882f`, 3 samples, 64 tokens each, concurrency 1, seed 1234. TTFT p50/p95 1.384594/1.779602 sec, latency p50/p95 1.724560/1.813754 sec, mean 37.9527 tokens/sec, 192 output tokens.
- The uploaded ZIP's `blazux-p1-reports/` and `blazux-p3-reports/` trees are *separate older operator reports*. The new project-local P1 evidence location contains **no claim of existing DGX files yet**: code-only default newly introduced in GitHub and unverified on real operator runtime.

New evidence layout and dual-read gate documented in [contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md). Historical records remain append-only. P3-C NOT_AUTHORIZED and NOT_RUN.

---

## E-20261107-P3-B-REAL-PASS-POST-B-READONLY-P1-AND-SOURCE-FIX

**OPERATOR-SUPPLIED ACTUAL DGX EVIDENCE (not assistant-observed live Docker):** P3-B canonical `/home/inlc/.local/state/blazux-wizard/p3/stage-b.json` with `stage=b,status=PASS,executed=true,live_verified=true,active_model=flash-next`; wrapper report `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T223124Z-14861d75.json` shows `P3_B_PASS_FLASH_NEXT_ACTIVE`, exit 0, `issues=[]`, independent post-switch `LIVE_SERVICE_VERIFIED` and `qwen3.8-flash-next`. Prefix `p3-a-operator-` is a WRAPPER naming error, not a failed B execution. Old wrapper `approval_accepted=false` is stale bookkeeping despite explicit separate terminal triple input and successful Wizard. Do not rewrite this historic private receipt.

**ACTUAL POST-B READ-ONLY P1 PREFLIGHT:** `/home/inlc/blazux-p1-reports/20261106T224010Z-d2095867/result.json` reports correct API served ID, clean branch, plan Verify+Benchmark READY, original/Hybrid READY, indexed 11 weight shards, source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`. Doctor/inventory each return 3; their latest raw JSON disposition is NOT PROVEN from supplied summary alone. Verify/Benchmark actions intentionally `BLOCKED/inspection_only` = NOT_RUN. This is not functional regression or performance PASS.

**SOURCE-ONLY IMPLEMENTATION:** fixes in tracked P3-A/B operator source and fake DGX tests; new `p1-post-b-audit.sh` uses existing inspect-only P1 checks, compares both raw rc3 JSON to exact running Flash source image, persists new 0600 immutable `p1-diagnostics-<UTC>-*.json` and never grants GPU or P3-C permission. P3-C gate picks latest attempt and blocks stale/invalid numeric/revision evidence. CI success for initial audited source `ea1a4ca1629acfd519fbfa839b615f45dd91c86e`; subsequent hardening must be evaluated at its own commit. Actual DGX run of new script **NOT_RUN**.

---

## E-20261106-P3-B-REAL-DGX-READ-ONLY-READY-B-NOT-AUTHORIZED

DGX operator pasted actual `bash scripts/temporary/p3-stage-b-inspect.sh` output at branch HEAD `e5d4171d07838e565510b1127f4a0b27dcd8423f`: `status=READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`, `operations_enabled=false`, `approval_accepted=false`, `current_model=27b`, `current_model_ids=["qwen3.8-27b"]`. Actual IDs: running 27B `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`, original preserved Flash `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Docker runtime image digest for both is `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; distinct served API/identity is needed, image digest alone does not differentiate models. Verified original P3-A plan hash `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`, P2 receipt SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. B inspection plan `7af40f009dd67975c77b98c03183833dd4997e16f9c9443bd11ea880f6d8162c` expiration `1793955000` (2026-11-06 17:50:00 KST), not valid later or as implicit operator authorization. Private receipt `/home/inlc/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`.

**Source-only change:** previous B core approval field erroneously named Flash downtime while B actually shuts down 27B; now distinct B-specific `I_ACCEPT_27B_DOWNTIME` + `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`. New default read-only B operator wrapper can execute only after separate real TTY triple confirmations with a fresh B SHA and updated core guard. Fake-DGX [PR 42190159738](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) **489/489 CPU PASS** across 22 groups on source `59046c4e17a5094f2c80a84025a763c2a767edcb`. Actual P3-B GPU transition **NOT_RUN**, no authorization. Preserve live 27B and source images/containers; stage-B source code is neither DGX qualification nor user permission.

---

## E-20261106-P3-A-REAL-DGX-COMMITTED-27B-ACTIVE

**Actual user-provided live DGX log** (not a CPU test): `feature/recipe-wizard-handoff` at HEAD `a3945bdc5cfec467478978c47b3a27bdafee84bd`; tracked `scripts/temporary/p3-stage-a-operator.sh --execute` output an initial plan READY with `issues=[]`, verified Flash source image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, P1 pre-A review `PRE_A_P1_REVIEW_READY`, P2 SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, `plan_id=b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`, expiry epoch `1793951400` (2026-11-06 16:50:00 KST), preserved Flash ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. All three exact manual confirmations typed independently. Result `execute_command_exit_code=0`, `executed=true`, `wizard_result.status=PASS`, `wizard_result.stage=a`, `wizard_result.live_verified=true`, `wizard_result.active_model=27b`; wrapper independently `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `status=P3_A_PASS_27B_ACTIVE`, `issues=[]`. Real stage A Wizard receipt `/home/inlc/.local/state/blazux-wizard/p3/stage-a.json`; local operator report `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. Original may remain stopped and preserved by design, but its post-A detailed Docker state has not yet been supplied; only independently qualify preservation from actual stage-B preflight.

**NEXT PHASE B NOT EXECUTED OR APPROVED.** A is the only approved completed live stage; B returns to Flash-Next, then new P1 functional/numeric evidence after B, then C to 27B final with separate approval. D-016 source-only B inspection `scripts/temporary/p3-stage-b-inspect.sh` compares actual A receipt to fresh service/API and canonical B read-only plan, validates original Flash immutable ID and 27B model/image provenance, writes private 0600 summary. It has no execute CLI, no GPU calls or Docker changes. Its CPU CI (fake fixtures) cannot replace actual DGX evidence and gives no B authorization. Preserve all images, checkpoints and stopped source container.

---

## E-20261106-P3-A-STALE-PLAN-REFUSAL-EXACT-PROMPT-FIX

**Actual operator DGX transcript:** HEAD `be6f3f9e6d757cc11c6299024900b637c7ca239d`, `scripts/temporary/p3-stage-a-operator.sh --execute`. Real preflight `status=READY_TO_REQUEST_OPERATOR_INPUT`, `issues=[]`, original source image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, P1 pre-A PASS report `p1-pre-a-20261106T065104Z-aaed31b2.json`, P2 receipt hash `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. Plan SHA `94b4dedae21eb72b12443029257931e123e33404c32898d9ae2bad52954c064f`, expires `1793950200` = 2026-11-06 **16:30:00 KST**. Operator **correctly** typed exact three strings: plan SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_P3_ENTRY`. Wizard rejected `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT` with `executed=false`, `approval_accepted=false`. Existing wrapper misleadingly surfaced `OPERATOR_REVIEW_REQUIRED`, but no actual stage A Docker service change occurred. Evidence `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T073049Z-4dc8be1b.json` (07:30:49Z=16:30:49 KST). Expiration highly consistent, not asserted as sole proven reason without fresh plan comparison.

**Source fix** at `fb34ce0ce985824cecd9c63159bf6f1eed408279`: show every exact typed literal adjacent to prompt, KST expiry and seconds left; guard <120s remaining before human confirmation; after acknowledgments replan read-only and refuse expired/changed SHA before canonical Wizard; nested stale refusal `executed=false` becomes `BLOCKED`. No automatic silent reapproval, no retry. Fake-DGX CPU tests 459/459 PASS ([push 42181851452](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181851452), [PR 42181858236](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236)); latest DGX code rerun NOT_RUN. D-016 operator workflow and D-037 scoped conditional approval unchanged; B/C and post-B P1 still separately gated.

---

## E-20261106-P1-PRE-A-ACTUAL-DGX-PASS-AND-P3-A-CONDITIONAL-ENTRY

User-provided DGX terminal transcript for source HEAD `834f823a76556a37a982e3dbf7f243db3edad6df` after tracked P1 pre-A wrapper rerun: `status=PRE_A_P1_REVIEW_READY`, `issues=[]`, `current_model=flash-next`, immutable image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; `current_rc3` and `historical_rc3` both `EXPECTED_ACTIVE_FLASH_COLLISION` (`check_count=2`); `p1_verify=PASS`; `p1_benchmark=PASS`, `sample_count=3`, TTFT P50/P95 1.398707/1.751198s, latency P50/P95 1.687357/1.780142s, mean 38.2968 tokens/s, total 192 completion tokens. Read-only local evidence `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`, `observed_at_utc=2026-11-06T06:51:04.065299+00:00`, no issues. Actual P3-A `executed=false`, `operations_enabled=false`, `p3_a_execution_authorized=false` **in the P1 receipt** because it was a read-only reconciliation, not actual stage-A approval/execution or API switch. Historical gaps have been reviewed successfully for **PRE-A only**.

D-037: operator's prior conditional P3-A intent is now eligible after P1 initial clearance, but actual P3-A remains a separate real live DGX event with a *fresh* short-lived plan ID, exact typed operator downtime and P3-entry confirmations, and service recovery risk. Newly tracked operator wrapper `p3-stage-a-operator.sh` requires private P1 PASS receipt, currently verified Flash, P2 receipt hash, current plan, interactive triple confirmations, canonical Wizard execute and independent 27B API identity; defaults to read-only plan, cannot chain B. Both models' checkpoint/images and original stopped source must survive. User has **not provided actual P3-A execution output** and therefore A/B/C statuses remain NOT_RUN. No GitHub activity here touches GPU service, Docker, port or cache.

---

## E-20261106-P1-PRE-A-REAL-DGX-PARSER-BUG-439-CPU-FIX

**Operator-supplied actual DGX output**, branch `feature/recipe-wizard-handoff` HEAD `3a59419305b31266f034fe4cbec2b384bb91d1f4`: tracked temporary P1 pre-A audit wrote `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T064009Z-70e9cef9.json`, returned `BLOCKED` with exactly `P1_ASSET_AUDIT_NOT_READY` and `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. `current_rc3` and `historical_rc3` each `EXPECTED_ACTIVE_FLASH_COLLISION` (`check_count=2`); P1 Verify PASS; benchmark PASS, 3 samples, 192 output tokens, TTFT P50/P95=1.398707/1.751198s, latency P50/P95=1.687357/1.780142s, mean 38.2968 tokens/s. Current model flash-next, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. Zero authorization, no P3 service mutation.

**Source-verified bug, not observed asset corruption**: persisted source report `p1_post_download.session` stores full cache diagnosis within `checks.cache_diagnosis.stdout`; console printing synthesizes `cache_diagnosis` only for the short terminal summary. Pre-A audit incorrectly accessed the nonexistent persisted top-level key and reported the missing revision as mismatch. Now uses original cache diagnosis summary helper to parse actual saved raw stdout, with revision validity/mismatch separately classified. Real-shaped fake-DGX regression checks no top-level diagnostic, raw stdout PASS, malformed/missing source blocked, actual changed SHA blocked. [Push 42176219970](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176219970), [PR 42176224898](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898), **439/439 CPU PASS on code `9adc9ab282a91c02e959dcb5c62f98527b556391`**. No claim of DGX reevaluation PASS yet. D-016 pending operator pull and single script rerun, preserve original service.

---

## E-20261106-D016-P1-PRE-A-WRAPPER-435-CPU-CI — no DGX run

Followed user-reaffirmed D-016 temporary script GitHub-first rule: tracked `scripts/temporary/p1-pre-a-readiness.sh` plus Python module, CPU fake DGX tests, workflow shell syntax validation, operating/runbook updates. One read-only wrapper reconciles **two** actual local P1 report files (2026-11-05 earlier and 2026-11-06 new), exact original private P1 verify+bench receipts, numerical TTFT/latency/tokens/s and samples, same source image, P1 plan readiness, and fresh Wizard service manager API/manifest. Separate `doctor`/`inventory-plan` outputs must each be actual parsed `rc=3` with expected active Flash owned-container image and port collision, `status=PASS` and `errors=[]`. Missing data/foreign image/unknown model/changed revision fails closed. Actual live execution remains `NOT_RUN`, no service change or GPU inference, no P3 automatic authorization.

**Another correctness issue fixed:** `p1_wizard.verify_api` obtains `identity = require_model(...)`, which returns `{"health":"PASS","models":["qwen3.8-flash-next"]}` on success, NOT `{"status":"PASS"}`. Initial pre-A and existing `p3_p1_evidence_gate` erroneously checked nonexistent `identity.status`; both now check actual health and served model list. New real-shaped positive tests and wrong-ID negatives added, no checks weakened. Intermediate CI failures before updating old fake fixtures are preserved; latest code SHA `75d22ce4303736ee84563a0f388a978379e4f228` [push run 42173798547](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173798547) and [PR run 42173805888](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) SUCCESS **435/435 CPU tests in 19 groups**. Cannot claim actual historical rc3 cause resolved until the operator runs the GitHub-pushed wrapper and shares JSON.

---

## E-20261106-P1-INSPECT-AND-NUMERICAL-RECEIPT — operator-provided direct facts, raw rc3 not yet seen

Operator's actual DGX latest `bash scripts/temporary/p1-post-download.sh --inspect-only` report at `/home/inlc/blazux-p1-reports/20261106T060941Z-e71a159c/result.json` has clean branch/head/tracked changes, no active setup process, API model IDs exactly `qwen3.8-flash-next`, HTTP health/models rc=0, GPU command=0, source+hybrid READY, `source_issues=[]` and `hybrid_issues=[]`, no incomplete blobs. Checkpoint revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`; source+Hybrid each report 11 indexed shards with compatible external symlinks. Verify and benchmark `plans.*.ready=true`; `actions.verify` and `actions.benchmark` `status=BLOCKED`, `reason=inspection_only` correctly mean **no new inference/benchmark was attempted**, not failure of historical P1 PASS. Both doctor and inventory_plan rc=3, but the pasted short report does not include raw stdout, so precise historical rc3 cause cannot be decided.

Separate operator P1 original Wizard benchmark receipt `~/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`: `status=PASS`, `benchmark.status=PASS`, `sample_count=3`, `total_completion_tokens=192`; actual numerical TTFT P50 1.398707 s/P95 1.751198 s; E2E latency P50 1.687357 s/P95 1.780142 s; average measured completion throughput 38.2968 tokens/s. These are **NVIDIA Flash-Next P1**, NOT 27B P2 metrics and not the required post-P3-B P1 benchmark. Distinguish source of these from client proxy prefill/decode metrics in P2. Historical 2026-11-05 P1 `verify=PASS`, baseline+extended and text/chat/tools/vision PASS unchanged. Actual rc3 raw cause remains unresolved pending tracked wrapper. No new GPU work or model switch performed from the user's read-only script.

---

## E-20261106-P1-OUTSTANDING-CONDITIONAL-APPROVAL-AND-RC3-RECONCILIATION — source checked, no DGX mutation

Actual P1 history recorded at E-20261105-16: NVIDIA Flash-Next source and Hybrid READY, 11/11 indexed shards; operator-supplied `verify=PASS` baseline+extended, completion/chat/tools/vision PASS; bounded `benchmark=PASS`; local receipt names `20261105T113119Z-eca4ec724ede.json` (verify) and `20261105T113125Z-586b2b46d93e.json` (benchmark). No TTFT/latency/token/sec numbers supplied in current conversation or ledger; previous `doctor=3`, `inventory_plan=3` had no accompanying JSON, so exact historical failure cause UNKNOWN. Post-B P1 receipts cannot exist before P3-A/B and remain NOT_RUN.

Operator's approval condition specifically requires **no unfinished P1 work before Flash→27B**; that condition is not fulfilled by current proof, so P3-A NOT AUTHORIZED and no actual service transition performed. The currently running Flash service identity `LIVE_SERVICE_VERIFIED` is not P1 benchmark proof.

Found exact **source semantics** of rc3: `scripts/manager/inventory.py` returns code 3 when collision_free=false due to an already present named container and occupied host port (even when `status=PASS` and `errors=[]`). Historic rc3 could be this, but no retrospective proof is invented. Fixed `p3_p1_evidence_gate.py` to require raw parsed doctor + inventory documents showing expected active same-image `qwen38-flash`/published :8000 collision with no inventory errors, instead of impossible rc=0; plus existing reviewed written disposition and actual post-B P1 receipts. **CPU-only tests** on `26a69507983dbcb2a7ab4c569f9d8baa6162e25c`: [push 42172119698](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172119698) and [PR 42172127412](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172127412) SUCCESS, **418/418 tests** in 19 groups. One intermediate source-only commit `f1dfc37` had red CI from old fixture; addressed by implementing real-shaped raw evidence fixture and five negative tests. No host container or model mutated.

---

## E-20261106-P3-SEQUENCE-STATUS-RECOVERY-SAFETY-CI — source-only continued, no GPU operations

After real DGX stage-A `READY_TO_REQUEST_TRANSITION_APPROVAL` with `issues=[]` (operator logs below), corrected misleading global sequence wording: staged source adapters exist, but `sequence --plan` remains permanently read-only and `BLOCKED` pending separate P3 entry. Changed P3 restore logic to recheck unexpected GPU-enabled Docker containers before restarting original service after a failure; fail closed as `RESTORE_FOREIGN_GPU_CONSUMER` / `RECOVERY_FAILED`. Added CPU fake-Docker normal/foreign-GPU recovery tests. **Does not establish host GPU process exclusivity.** Read-only P3 readiness remains a different evidence class from runtime operational PASS.

**Verified SOURCE HEAD `02bf94c1628828ce22fa338dd5a8e5a0955f9179`:** [push GitHub Actions 42170050031](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170050031) SUCCESS and [Draft PR Actions 42170056860](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860) SUCCESS, 413 CPU tests over 19 suites. Previous interim `d82122f` failed because simulated `docker ps` output incorrectly contained literal backslash-n rather than newline; corrected without weakening assertions. Actual DGX P3 execute remains **NOT_RUN**, no `:8000` downtime, no additional GPU model start, no file/cache deletion, no PR merge.

---

## E-20261106-P3-A-ACTUAL-DGX-READ-ONLY-READY — operator-provided JSON, no service mutation

2026-11-06 DGX operator read-only observation: current Flash-Next `qwen38-flash` on :8000/v1, `LIVE_SERVICE_VERIFIED`, served ID `qwen3.8-flash-next`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, exact container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Manifest/API check array 8/8 true, `issues=[]`, `executed=false`; **GPU exclusivity and process ownership remain unverified**, and current identity is not historical rollback proof. `sequence --plan`: `status=BLOCKED` with only `P3_SEPARATE_OPERATOR_ENTRY_REQUIRED` by D-034 (expected), with successful local P2 receipt SHA-256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, evidence path `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`. `stage-a --plan`: `status=READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, source `flash-next`, target `27b`, `plan_id=79be6bf05cb02306ec9155ade317e06c457238de427417ebab8946e35449247a`, expiry epoch `1793943600` (2026-11-06 14:40 KST), target image equal to preserved local Docker image ID, expected target container ID null (not yet created), `executed=false` and `operations_enabled=false`. **This was a plan only, not scoped downtime approval or P3 entry**; plan IDs must be regenerated when stale and must never be reused across stages. No GPU/Docker/service mutation was performed by these read-only queries.

**Interpretation:** P2 receipt was found and accepted by the read-only sequence planner. The P3-A plan's readiness says source/target preliminary guard conditions are satisfied; it does not certify actual GPU exclusivity, service interruption permission, persistence or rollback. The P3 global sequence remains BLOCKED until separately approved entry, and actual P3 A/B/C remain NOT_RUN. The local plan expiry is not a reusable authorization token. No user authorization to stop `qwen38-flash` is recorded.

---

## E-20261106-P3-PERSISTENT-SOURCE-CI — source and CPU only, no DGX P3 operation

New P3 standalone stages in `scripts/manager/p3_persistent_switch.py`, `p3_p1_evidence_gate.py` and Wizard menu. Durable approval boundary: P2 benchmark evidence does not automatically open P3; A requires a separate explicit operator-entry acknowledgment and exact current A plan; B, C each need new stage-specific plans and downtime approvals. A/B/C mock Docker implementations have been tested; label and ID tampering fails closed; successful C remains on 27B. Post-B fresh P1 numerical/functional receipts and rc=3 diagnostics required; absent data remains BLOCKED, no invented TTFT/throughput values.

**GitHub Actions, actual code HEAD `27728045907a1f2111dc4b8340fbea2cc365ff1d`:** [push run 42168518712](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168518712) SUCCESS and [Draft PR run 42168524464](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168524464) SUCCESS. Logs report 411 passing CPU unittest cases across 19 test groups. Earlier intermediate red CI steps were genuine syntax/new-mock issues and were fixed, not hidden. They are not runtime GPU test outcomes.

**P3 DGX actual:** A/B/C `NOT_RUN`; actual service state last provided after P2 was Flash-Next `LIVE_SERVICE_VERIFIED`. No updated DGX direct observation after source/doc commits. **P1 post-B remedy/verify/rebenchmark actual:** `NOT_RUN`; doctor/inventory-plan historical return code 3 reason still UNKNOWN. No model start/stop, Docker system cleanup, port change, cache mutation or PR merge occurred from code work.

---

## E-20261106-P2-DGX-BENCH-PASS-RESTORED — actual operator-provided DGX stdout, private files not independently fetched

Result: `status=BENCH_PASS_RESTORED_VERIFIED`, `trial=PASS`, `executed=true`, `target_api_ready=true`, `inference_ok=true`, `benchmark.status=PASS`, `restoration.status=RESTORED`, `restoration.issues=[]`, post-restore Wizard `LIVE_SERVICE_VERIFIED` with `observed_model=flash-next`, `expected_served_id=qwen3.8-flash-next`, `issues=[]`. NVIDIA `nvidia/Qwen3.8-27B-NVFP4` revision `482ca0f3832238542f8f5295dde86b5f22711d80`, exact served ID `qwen3.8-27b`, image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. This overrides plan-only `P2_BENCHMARK_RECEIPT_NOT_FOUND` entries from earlier in the day, which remain historical.

**Observed measured benchmark (3/3 successes, stream=true, concurrency=1, seed=1234, max_tokens=64):**

| Request | TTFT (s) | E2E (s) | Completion tokens | Client decode proxy (tok/s) |
|---|---:|---:|---:|---:|
| #0 | 32.177839 | 37.808956 | 64 | 11.1878 |
| #1 | 0.179349 | 5.818283 | 64 | 11.1723 |
| #2 | 0.178962 | 5.813945 | 64 | 11.1802 |

Aggregate TTFT P50=0.179349s, P95=28.977990s; latency P50=5.818283s, P95=34.609889s; mean E2E=7.9002 tok/s, mean client decode proxy=11.1801 tok/s, mean client prompt-ingest proxy=246.2744 tok/s. Do not conflate client proxies with vLLM engine metrics; first-request latency cause not yet established. GPU memory `UNAVAILABLE`; GPU peak and actual engine prefill/decode metrics `NOT_MEASURED`. Three small text requests do NOT prove broader feature/load readiness.

Paths on the operator's DGX (not accessible through GitHub, exact file contents independently unverified):
- `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`
- `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.json`
- `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.target.log`

**Disposition:** P2 approved limited scope COMPLETE and STOP. P3 persistent switching is **NOT_RUN / NOT_QUALIFIED**. D-034 demands separate operator entry/transition approvals and P1 corrective/remeasurement evidence before final 27B. No GPU/service mutation from this documentation update.

---

## E-20261106-P3-REORDERED-SOURCE-ONLY — user instruction, code/CI evidence; no new DGX runtime data

**Operator's new instruction:** Do not automatically enter P3 after P2; when P3 successfully switches **27B→Flash-Next**, resolve P1 shortcomings and benchmark Flash-Next before switching **Flash-Next→27B**. Since previous P2 design restores Flash-Next, P3 must separately and explicitly establish 27B as the source model for the requested 27B→Flash-Next test. Final intended active service after P3 is **27B** (not Flash-Next).

**Source-only changes:** retired `scripts/manager/p3_27b_roundtrip.py` previously executable two-cycle path (its `main`, `make_plan`, `execute` now always return `BLOCKED`); introduced read-only `scripts/manager/p3_transition_sequence.py` + Wizard `switch flash-next-27b sequence --plan --json` with `plan_id=null` and no auto progression. Read-only new sequence encodes per-stage explicit approvals and prerequisite P1 remediation/rebenchmark. CPU tests verify no receipt, successful receipt still requires manual entry, phase order, wrong model/API BLOCKED, and legacy direct execution prevented.

**Verification:** GitHub Actions [run 42163187058](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42163187058) **SUCCESS, 395/395 CPU tests, 19 test suites**, on code HEAD `f195e8bcc48333b5d40147c8b66e6c412c949818`. Subsequent docs-only commits do not constitute DGX runtime validation. No new actual P2 benchmark/P3 transition was performed. Previous actual DGX P2 `--plan` was only `READY_TO_REQUEST_TRIAL_APPROVAL`; no measured bench result supplied. Draft PR stays unmerged.

---

## E-20261106-DGX-P2-BENCH-PLAN-READY-P3-PLAN-BLOCKED — actual operator stdout

**P2 read-only plan evidence:** `action=Qwen3.8-27B-bounded-benchmark-and-original-restore`, `status=READY_TO_REQUEST_TRIAL_APPROVAL`, `issues=[]`, `executed=false`, `gpu_verified=false`, `image_id=sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, `source_container_id=90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, `plan_id=2f76c3b03865b6a15a5c2fe8f316231f532fbf8b7fe178ffd00db8383edc3399` (expired 2026-11-06 **12:20 KST**), benchmark `requests=3`, `max_tokens=64`, `concurrency=1`, `seed=1234`, `stream=true`. This is a **read-only plan**; no actual GPU benchmark result or performance numbers.

**P3 read-only prerequisite evidence:** `action=P3-two-temporary-roundtrips-with-original-restore`, `status=BLOCKED`, `plan_id=null`, `issues=["P2_BENCHMARK_RECEIPT_NOT_FOUND"]`, `executed=false`, `cycles=2`. Expected fail-closed behavior until a successful real P2 `BENCH_PASS_RESTORED_VERIFIED` private evidence file exists.

Do not call P2 bench PASS, repeat P3 plans as a workaround, reuse expired P2 plan, or interpret these logs as operator approval to interrupt Flash-Next.

---

## E-20261106-P2-BENCH-P3-ROUNDTRIP-SOURCE — no new DGX GPU execution

**Source on `feature/recipe-wizard-handoff` only:** new P2 distinct-hash benchmark plan and 3 sequential SSE timing requests; original one-shot stop/restore executor reused, protected local metric evidence, post-restore Wizard status; new P3 exactly two temporary roundtrips conditional on real P2 benchmark success. CPU fake-backend tests verify approval separation, invalid and stale approval fail-closed, no HTTP/GPU from plans, SSE bounds, recording measured TTFT/e2e vs proxies, and source ID/API restore checks. **Do not record any actual performance numbers until real DGX execution.**

**Existing real DGX evidence remains separate:** first 27B GPU one-shot API/inference `PASS_RESTORED` and actual Flash-Next `LIVE_SERVICE_VERIFIED`. Neither is a timed benchmark nor a two-cycle result. P3 plan is deliberately BLOCKED until `*.benchmark.json` produced by the newly approved real benchmark. Source CPU CI does not qualify either GPU runtime command, persistent P3 switch, GPU peak memory or true engine prefill throughput.

---

## E-20261106-ACTUAL-DGX-MODEL-INVENTORY — Orcarouter original and BF16/MTP recipe still exist

**Actual operator JSON:** `./wizard.sh model list --installed --json` => `status=READ_ONLY_INVENTORY`, two cache roots checked, three registered sources observed, `other_cached_repos_truncated=false`, `service_status=LIVE_SERVICE_VERIFIED`, active `flash-next`, `executed=false`. Model revisions/shards/metadata/missing shards:
- `nvidia/Qwen3.8-Flash-Next-NVFP4` `fc694b54fb0174e0913e6adf86691ef85a4ead47`: **11**, missing **0**, `source_files_present=true`, active + API verified.
- `nvidia/Qwen3.8-27B-NVFP4` `482ca0f3832238542f8f5295dde86b5f22711d80`: **3**, missing **0**, `source_files_present=true`, inactive.
- `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` `3a3b63161c0745390e5270179af42e46efc70799`: **17**, missing **0**, `source_files_present=true`, inactive; original legacy HF cache `/home/inlc/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`; recipe view directory `/home/inlc/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2` has `directory_present=true`. This **directly confirms preservation, not runtime functionality**.

Also **4 unregistered cache snapshots**: `maurienne-ai/Qwen3.8-27B-DFlash2-NVFP4-RTNcal`, `RadixArk/Qwen3.8-27B-NVFP4`, `dealignai/Qwen3.8-Flash-Next-ABLITERATED-NVFP4`, `RadixArk/Qwen3.8-Flash-Next-NVFP4`. These were only discovered by revision listing; **index/shards not validated** for unregistered cache entries. Unknown locations beyond the two configured roots were not searched.

**Evidence boundary:** source inventory and current Flash-Next API confirmed, no GPU operations performed here. Orcarouter BF16 PLE/MTP recipe contents not audited and no Orcarouter runtime qualification yet. No cleanup/re-download.

---

## 2026-11-06 — Read-only installed model inventory, including protected legacy Orcarouter

An earlier example `./wizard.sh model list --installed --json` was suggested **before implementation** and gave `{"status":"BLOCKED","error":"choose a valid submenu item for model"}` when the operator tried it. That error was a **missing Wizard route**, NOT evidence that any model was deleted.

This command is now implemented and tested:
```bash
./wizard.sh model list --installed --json
```

Canonical config `runtimes/model-discovery.json` lists known Hugging Face caches (`~/.cache/huggingface`, `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`, and `HF_CACHE`/`HF_HOME` overrides). It maps registered service models to their source repo identifiers **without changing `runtimes/service-policy.json` or granting launch permission**. Includes protected original Orcarouter source `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4`, revision `3a3b63161c0745390e5270179af42e46efc70799` and original BF16/MTP recipe view `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2`. The previous project originally reported ~180GB `hf-cache`, ~5GB `recipe-views`; this was historical storage evidence and has **not been rechecked today**.

Read-only inventory validates selected snapshot's bounded weight index and existence of every indexed nonempty shard (following HF symlinks), tokenizer and config. It reports exact cache/revision and source state. A recipe view alone yields `RECIPE_VIEW_ONLY_SOURCE_UNVERIFIED`; missing weights yield `SNAPSHOT_INCOMPLETE_OR_UNVERIFIED`; found complete indexed weights yield `SOURCE_FILES_PRESENT_UNQUALIFIED`. Unknown caches beyond configured roots are **not** conclusively absent; limited other cached repos are reported as `UNREGISTERED_CACHE_SNAPSHOT_OBSERVED`. Active API identity comes from the manifest-led live service inspector. All these are observational; no model is moved, deleted, downloaded, registered as ready, started, restored, or switched.

The new command has **not yet run on the real DGX**. After clean Git fast-forward, operator executes one read-only Wizard command and provides JSON. Any Orcarouter result must be reconciled with current disk evidence before asserting continued asset availability or runtime compatibility. Original service `qwen38-flash` remains untouched. Existing P2 first GPU trial `PASS_RESTORED` and `LIVE_SERVICE_VERIFIED` are separate, already reported facts.

---

## E-20261106-P2-ACTUAL-GPU-TRIAL-PASS-AND-WIZARD-STATUS-SOURCE

**Real operator DGX terminal**: `./scripts/serve_27b.sh --trial-execute --approve-plan "$PLAN_ID" --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME` reported `{"executed":true,"target_api_ready":true,"inference_ok":true,"trial":"PASS","restoration":{"status":"RESTORED","issues":[]},"status":"PASS_RESTORED"}`. Private local evidence `/home/inlc/.local/state/blazux-wizard/p2/20261105T230229Z-a4fc14cf8079.json` and associated `.target.log`; only stdout was supplied, file contents not inspected. Supports **real GPU Qwen3.8-27B load/API/small generation and normal-path original Flash-Next return**, not comprehensive GPU benchmark or emergency recovery testing.

**Source-only follow-up**: user requested **Manifest-based Wizard** rather than standalone `docker ps` and `curl`. Added new `scripts/manager/service_status.py`; `./wizard.sh service manager status --json` now composes a single fresh Manifest observation with a bounded API health check using exactly the same snapshot. It compares actual managed container/model/port, `runtimes/service-policy.json` expected served model ID and `/v1/models` response. Returns `LIVE_SERVICE_VERIFIED` only if the recorded checks all pass; otherwise `BLOCKED` with issues. `inventory` and `health` remain separate diagnostics. **No actual DGX run of the newly combined Wizard status yet.** `gpu_exclusivity_verified=false`, `previous_trial_provenance_verified=false` expressly separate current status from historical trial receipt.

---

## E-20261106-P2-CPU-REGISTRY-PASS-AND-GPU-TRIAL-SOURCE

**Actual user-supplied DGX:** refreshed isolated CPU `./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only` reported **all 9 checks true**, including `qwen3_5_module_imported`, `qwen3_5_class_present`, `modelopt_module_imported`, `modelopt_nvfp4_class_present`, `quant_registry_factory_present`, `modelopt_mixed_registry_class_matches`, `modelopt_mixed_cli_name`. `observed_quantization_name=modelopt_mixed`, `issues=[]`, `status=IMPORT_AND_REGISTRY_PRESENT_UNQUALIFIED`, `gpu_verified=false`, `launch_authorized=false`. Actual Qwen3.8 checkpoint continues to declare internal `Qwen3_5ForConditionalGeneration`.

**Source only:** Implemented opt-in exact-approved, single-GPU 27B trial and strong original-container restoration. Source commit `ea28b0c0ddbe085782617cc1445c2fcaf613f2a4`; [GitHub Actions run 42124595787](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42124595787) **SUCCESS 354/354 CPU tests, 16 suites**. No real DGX GPU model load, inference, stop/start, or recovery has been run yet. This capability must not be described as tested rollback.

**External comparative sources** (not direct proof of this pinned image):
- `https://github.com/MiaAI-Lab/Qwen3.8-27B-DGX-Spark-RTX-6000`: Unsloth compressed-tensors, separate from NVIDIA ModelOpt `nvidia/Qwen3.8-27B-NVFP4`.
- `https://forums.developer.nvidia.com/t/qwen3-8-27b-nvfp4-on-a-single-dgx-spark-up-to-1m-context-vllm-mtp-measurements/380244/17`: GB10 NVFP4-specific community kernel caveats, MTP after basic start.
- `https://github.com/eugr/spark-vllm-docker`: supports NVIDIA checkpoint and DGX Spark-specific images; adopt only after checking exact format/recipe.
- `https://build.nvidia.com/spark/vllm/intermediate`: official Spark guide includes NVIDIA 27B, alternative NVIDIA vLLM image as potential contingency.

---

## E-20261106-P2-CPU-IMPORT-DGX — observed import PASS, name-probe false negative

Operator DGX `git pull --ff-only` fast-forward `99dde4c..9db92f7`. Image inspected `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. `./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only` yielded **five PASS** checks (Qwen3.5 module and model class, ModelOpt module, ModelOpt MixedPrecision config class, NVFP4 config class). `modelopt_mixed_cli_name=false` and `MODEL_OPT_NAME_LOOKUP_FAILED:TypeError` were due to audit code calling instance method `get_name(self)` as a classmethod. Output `status=BLOCKED`, `runtime_qualified=false`, `executed_gpu=false`. Incidental restricted-container warning `vllm._C ModuleNotFoundError` and CUDA runtime missing; not proof of production loader failure. **No GPU run or source Flash-Next stop.**

Follow-up code `0a14f189c4dae61827298fde46f3148d316f8c72` changes check to vLLM public `get_quantization_config("modelopt_mixed")` registry/class identity. CI run `42121160545` **SUCCESS 336/336 CPU tests**. This **corrected registry probe has not yet been executed on DGX**; record its actual JSON when provided.

---

## E-20261106-P2-DGX-SERVE-SPLIT — actual DGX status and startup preview after file separation

User-supplied DGX stdout: `git pull --ff-only origin feature/recipe-wizard-handoff` advanced `b1c9b2e..c44aa72` and then `c44aa72..99dde4c`. After split, `./scripts/serve_27b.sh --status` yielded `action=runtime-preflight`, immutable NVIDIA revision `482ca0f3832238542f8f5295dde86b5f22711d80`, ModelOpt FP8 208/NVFP4 193, 401 total, image id `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, ARM64/v0.32, `status=BLOCKED`, `runtime_qualified=false`, six explicit unresolved gates. `./scripts/serve_27b.sh --plan` returned `action=start-preview`, `observed_source.api_identity_confirmed=true`, original `qwen38-flash` with the **same image ID** as 27B candidate, 27B proposed `modelopt_mixed` / 8192 / seqs1 / 0.70/eager; `status=BLOCKED`, `operations_enabled=false`, `plan_id=null`, `executed=false`. This proves the split routing and live source identity; not GPU import/launch or benchmark.

**New source CI, not yet DGX evidence:** commit `834c750fc966f73c885fcfc5d81d054a60ae419e`, Actions `42112730764` SUCCESS **333/333** CPU tests including eight CPU import audit unit tests. The import tool was NOT_RUN on the operator DGX at evidence capture time.

---

## E-20261106-SERVE-SPLIT-CI — dedicated model serve entrypoints

GitHub source branch `feature/recipe-wizard-handoff`, commit `67a54afc615e51f207f12238e8473200c62a1aad`, Actions run `42111216055` **SUCCESS 325/325 CPU tests, 16 suites**, including 10 new `tests/test_serve_split_cpu.py` tests. Modified `flash` to invoke copied original `scripts/serve_flash-next.sh`, preserving P1 options, legacy `scripts/serve.sh` as a thin dispatcher, and source-only `scripts/serve_27b.sh` with no Docker run/stop. Existing `tests/test_flash_launch.py` continued PASS with synthetic Docker. No actual DGX process or GPU service execution occurred as part of this source edit. Latest real DGX 27B pinned ModelOpt metadata and image static source proof are in earlier E-20261106 entries.

---

## E-20261106-P2-DGX-STATIC — exact pinned 27B CPU source proof from operator

Operator supplied actual DGX outputs (2026-11-06 KST):
1. Exact `nvidia/Qwen3.8-27B-NVFP4` revision `482ca0f3832238542f8f5295dde86b5f22711d80` source found. Quantization audit `MIXED_PRECISION`, `producer=modelopt`, `layer_algorithms={"FP8":208,"NVFP4":193}`, `layer_count=401`, `issues=[]`, `mixed_fp8_nvfp4_metadata=true`, `runtime_qualified=false`.
2. `./scripts/temporary/p2-27b-image-audit.sh --plan`: `CPU_ONLY_PROBE_PLAN`, local image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, no GPU/network/port mutation.
3. `--execute-cpu-only`: `SOURCE_SURFACES_PRESENT_UNQUALIFIED`, image registry Qwen3.5 true, Qwen3.5 class true, ModelOpt FP8/NVFP4/mixed algorithm literals true, mixed config classes true; all three Python source modules parsed. `executed_gpu=false`, `gpu_verified=false`, `runtime_qualified=false`, `launch_authorized=false`.
4. User reported git pull 13 changed files, no service stop/restart, and old Flash-Next status `observed_model=flash-next`, `:8000` listening from live preflight. Full 27B runtime remains `BLOCKED` as designed.

**SOURCE CI:** GitHub commit `ae4490d66d9c1b9306435165a9821253ee6f38d7`, Actions run `42110115101`: SUCCESS **315/315 CPU tests PASS**. Added dedicated non-executable 27B launch argv and API identity/baseline checks, not a GPU run. Initial `234a8e4a` CI had one failing *test-only placeholder assertion*, fixed by `ae4490d6`; latest success supersedes the first failure.

---

## E-20261106-P2-QUANT-SOURCE-CI — Pinned ModelOpt audit unit tests

GitHub `cd63f25f0bf7282ea06dbb13c3499798394322b0`, Actions `42065472163` — **303/303 CPU tests PASS**, all 15 test batches and deliberately unqualified candidate-recipe check SUCCESS. The added P2 audit uses `hf_quant_config.json` in exact NVIDIA immutable snapshot and reports layer algorithm counts; malformed/oversize/unknown algorithms fail closed. Neither the new quantization fields nor static image source checks have been run on DGX yet; GPU/27B loader/bench/API/transition and recovery **NOT_RUN**. The previous DGX `status --inspect-runtime` result remains a **config-only** observation, not a per-layer audit.

---

## E-20261106-P2-READONLY — DGX real NVIDIA 27B qualification observation

- Operator ran `git pull --ff-only origin feature/recipe-wizard-handoff`: fast-forward `e99914c..edf0968`, checkout clean as reported.
- Real DGX `./wizard.sh model 27b status --inspect-runtime --json`: source candidate **present** at full SHA `482ca0f3832238542f8f5295dde86b5f22711d80`, architecture `Qwen3_5ForConditionalGeneration`, model type `qwen3_5`, quant method `modelopt`, context 262144, vision config yes, host aarch64; Docker image `qwen38-flash-dgx:v0.32` image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, Linux/ARM64, `qwen38.base=v0.32`, `repo_digests=[]`.
- Observed original Flash-Next active on host port 8000; NVIDIA download container no longer running. No GPU residency validation (`gpu_verified=false`), actual loader/model start/27B API/benchmark/rollback `NOT_RUN`.
- Read-only preflight correctly BLOCKED: `VLLM032_27B_LOADER_NOT_QUALIFIED`, `MODEL_OPT_MIXED_NVFP4_FP8_GPU_NOT_QUALIFIED`, `IMAGE_DIGEST_NOT_PINNED_IN_VALIDATED_RECIPE`, `GPU_MEMORY_AND_CONTEXT_PROFILE_UNVERIFIED`, `27B_START_AND_FLASH_NEXT_ROLLBACK_NOT_VERIFIED`, `ACTIVE_MODEL_REQUIRES_SEPARATE_TRANSITION_APPROVAL`.
- Public vLLM 0.32.0 supported models list `Qwen3_5ForConditionalGeneration` and versioned ModelOpt code provides NVFP4+FP8 mixed config. **Public upstream != local patched image**: image static audit developed but actual DGX execution of image source probe still `NOT_RUN`. See https://docs.vllm.ai/en/v0.32.0/models/supported_models/ and https://docs.vllm.ai/en/v0.32.0/api/vllm/model_executor/layers/quantization/modelopt/ .
- **CI on `acf5d64a37929811af9e2da33fa1b30de5e38cb0`: SUCCESS, 294/294 CPU tests PASS.** No GPU/API/inference actions performed by GitHub development.

---

## E-20261106-P2-DOWNLOAD — NVIDIA pinned download PASS (operator DGX evidence)

- Command: `./wizard.sh model 27b download --guided`; approval ID `e7d3ee776b65c3c5e3395fbeff5d0d739ef432028c030df8d604578412570c49`.
- `Fetching 19 files: 100%` (19/19); process exit 0; final `status=PASS`, `executed=true`, `scope=DGX_NETWORK_DISK`, `checkpoint_status=SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, `issues=[]`.
- Repo/revision: `nvidia/Qwen3.8-27B-NVFP4` / `482ca0f3832238542f8f5295dde86b5f22711d80`.
- Evidence: `/home/inlc/.local/state/blazux-wizard/p2/evidence/20261105T150433Z-bd8cf46ef5.json`.
- Independent weight-shard cryptographic rehash **NOT_RUN**; loader/GB10/GPU/API/benchmark/rollback **NOT_RUN**. `gpu_verified=false`.
- GitHub-only new preflight/test code: **SOURCE implemented; CI pending final HEAD**. No DGX source update or GPU operations by this coding session. This record supersedes older transfer 84% observations.

---## 2026-11-06 — Complete Wizard SOURCE; actual runtime remains gated

- GitHub SOURCE: `wizard/console.py` full three-level operator UI; `wizard/workflow.py` consistent P1/P2/P5 model action catalog; `wizard/roadmap.py` release evidence view; `scripts/manager/service_logs.py` bounded read-only log tail. Existing `scripts/manager/p1_wizard.py` and `scripts/manager/p2_27b_download.py` preserved. Added test suites `test_wizard_workflow_cpu.py`, `test_wizard_roadmap_cpu.py`, `test_service_logs_cpu.py`; no real Docker/GPU/network operations executed from GitHub code edits.
- A CPU regression exposed a bypass where P1 guarded start dispatch ignored its own capability BLOCKED result. Fixed by requiring `GUARDED_P1` and preventing P1 quickstart when 27B/Orcarouter is active; latest CI must show PASS before releasing source.
- Last DGX runtime evidence remains operator-reported NVIDIA 27B download started at `Fetching 19 files: 84%`, NOT_VERIFIED complete. No P2 NVFP4 loader, GPU acceptance, P3/P6 switch, P4 deletion, Orcarouter runtime or P7 release PASS evidence exists in this turn.

## 2026-11-05 — Service health and transition preview CPU evidence

- SOURCE: local :8000 GET-only health/model-ID observer, with no inference POST, no Docker mutation, fixed request/size/time bounds; source-only stop-old → port release → new start → API verify → rollback preview, always BLOCKED without verified executor.
- CPU mock tests cover correct served model ID, ID mismatch, bad or oversized response, unqualified Orcarouter, unknown service, stop-before-start and rollback invariants, and no hidden GPU/Docker actions.
- Actual DGX service health action, 27B model start/switch and rollback: **NOT_RUN**. Source CI status must be confirmed at final HEAD. Last real DGX transfer evidence still only `Fetching 19 files: 84%`.

## 2026-11-05 — First DGX NVIDIA 27B transfer and unified Wizard source

- **Actual DGX operator terminal:** `./wizard.sh model 27b download --guided` with exact approved plan id `e7d3ee776b65c3c5e3395fbeff5d0d739ef432028c030df8d604578412570c49`, `Fetching 19 files: 84% (16/19)`. Scope DGX NETWORK/DISK, actual transfer **STARTED**; completion, source checksum/index audit and outcome evidence **NOT_OBSERVED**. Existing `qwen38-flash` still Up with external host :8000 at initial plan.
- GitHub SOURCE: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`, `wizard/quickstart.py`, three-choice root TTY menu, live `download_running` manifest, unqualified Orcarouter policy, new CPU test matrix and legacy CLI compatibility. This is **SOURCE/CI evidence only**, no DGX UI update or GPU execution.
- Final HEAD CI must be checked after all documentation and tests. Old P1 bounded verify/benchmark PASS remains historical and does not imply 27B qualification.

## 2026-11-05 — Guided NVIDIA download refusal evidence and correction

- Actual DGX console: operator supplied the full Wizard-computed plan ID `b190c936072038bc55c14c62dd2f9a63e3ddbf5c2e1ebbf0d1710551a7ec21ce`. Wizard returned `status=BLOCKED`, `executed=false`, `issues=[PREFLIGHT_CHANGED_REPLAN_REQUIRED]`. There is **no actual NVIDIA download execution evidence**.
- GitHub source analysis: live preflight hashed mutable `free_inodes`, free GiB floor and human Docker status. The lock/state directory is created between plan generation and the second preflight, so drift can arise without a meaningful safety change.
- SOURCE remedy: stable `_approval_facts` fingerprint; retain dynamic safety gates and ten-minute approval period; add regression tests. CPU/CI PASS verdict must be checked at final HEAD. DGX second attempt `NOT_RUN`.

## 2026-11-05 — NVIDIA 27B pinned acquisition SOURCE and single-model policy

- Authoritative public checkpoint: `nvidia/Qwen3.8-27B-NVFP4`, immutable `482ca0f3832238542f8f5295dde86b5f22711d80`, 3 indexed safetensors shards (~21.9GB): https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/482ca0f3832238542f8f5295dde86b5f22711d80 .
- Prior actual DGX user-provided inventory (before current code): `NO_PINNED_LOCAL_SNAPSHOT` for NVIDIA 27B. No evidence of downloaded NVIDIA checkpoint or running 27B service yet.
- New GitHub SOURCE: guarded no-GPU, no-port Wizard download, pinned-without-refs scanner, single-model service policy, read-only observed manifest and transition journal primitives. Actual DGX download/GPU/API 27B/start-stop-switch: **NOT_RUN**. The runtime approval boundary remains independent of download approval.
- Latest CPU CI should be checked against final commit before claiming PASS.

## 2026-11-05 — NVIDIA P2 cache and service-menu evidence

- DGX user console: `nvidia/Qwen3.8-27B-NVFP4`, `refs.main=null`, `local_revision=null`, `indexed_shard_count=0`, `incomplete_blob_files=0`, `source_files_present=false`, `issues=[NO_PINNED_LOCAL_SNAPSHOT]`. Scope: read-only `~/.cache/huggingface` only; actual download NOT_RUN.
- New GitHub SOURCE: Wizard `service manager` module and `model 27b plan --for-action download` fail-closed action. CI verdict requires latest-HEAD check. No DGX service, download, GPU, benchmark execution.

## 2026-11-05 — P2 model selection and provenance split

**DGX observation (historical, not NVIDIA):** user-supplied Wizard read-only inventory for `RadixArk/Qwen3.8-27B-NVFP4` at revision `52d1adc5f38aa5ebf099c29ed7025ba34cfbb854`; 3/3 indexed shards, 0 incomplete transfers, `issues=[]`. **Current chosen P2 model:** `nvidia/Qwen3.8-27B-NVFP4`; NVIDIA cache inspection, immutable SHA, vLLM 0.32 GPU operation and benchmark remain NOT_RUN. Public NVIDIA model card lists vLLM on GB300 TP4, not a qualification of this single Spark GB10. https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4

## 2026-11-05 P2 — config audit SOURCE evidence

- GitHub-connected source patch: `scripts/manager/p2_27b_inventory.py`, `tests/test_p2_27b_inventory_cpu.py` on `feature/recipe-wizard-handoff`.
- Evidence level: **SOURCE committed**. CI at new HEAD requires separate run confirmation; no local DGX, GPU, Docker, network download or model service test was executed.
- Previous P1 operator report remains valid with its original dated scope. No P2 runtime qualification inferred from candidate checkpoint metadata.

# Evidence ledger — observed facts and test reports

## E-20261105-16 — P1 baseline, advanced tests, and bounded GPU bench PASS

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

## E-20261105-17 — 27B source-only cache discovery

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

**Source/CPU**: code/testing/CI in this branch, independent of DGX GPU acceptance. No 27B GPU benchmark, install, live switch, or production rollout observed.


Use an append-only entry for every meaningful result. Never substitute README claims or previous chats for locally reproduced tests.

## Entry template

| Field | Value |
|---|---|
| ID / KST | `E-YYYYMMDD-NN` / timestamp |
| Model / recipe / revision | full id + immutable revision |
| Git HEAD / branch | exact actual SHA and branch |
| Runtime image / host | immutable digest, vLLM version, GPU/driver/OS |
| Scope | SOURCE / CPU / CI / GPU / API / SWITCH / RELEASE |
| Exact invocation | command/environment; redact secrets |
| Inputs | test names, prompt/seed hashes, dataset scope |
| Result | PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE |
| Artifacts | paths/URLs/digests |
| Limits | scope, caveats, unresolved mismatches |

## E-20261104-01 — source-only planning baseline

- **Scope:** SOURCE / GitHub metadata and public source inspection, **not** GPU.
- **Repo:** `kjlee-inlct/qwen3.8-Flash-DGX`.
- **Source commit:** `blazux/qwen3.8-Flash-DGX@b0aa8b77604139557169387b2fa8386355d8b651`; user fork main same at branch creation.
- **Source observations:** `flash` and `profiles` cover NVIDIA and RadixArk Flash-Next; `scripts/serve.sh` removes container matching `NAME`; `feature/orcarouter-bf16-adapter` already holds a design doc; aphex3k 27B recipe uses SGLang, **not** local vLLM 0.32 proof.
- **Result:** `PASS_SOURCE_INSPECTION` for cited facts; `NOT_RUN` for CPU tests, CI, DGX runtime/benchmark.
- **Artifacts:** [Blazux source](https://github.com/blazux/qwen3.8-Flash-DGX/tree/b0aa8b77604139557169387b2fa8386355d8b651), [Orcarouter parallel branch design](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/blob/feature/orcarouter-bf16-adapter/docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md), [27B external reference](https://github.com/aphex3k/Qwen3.8-27B-on-DGX-Spark).
- **Limits:** No current disk, container, memory or actual 27B vLLM evidence.

## E-20261104-02 — new planning branch and documentation

- **Scope:** GitHub SOURCE / documentation-only.
- **Branch base:** `feature/recipe-wizard-handoff` created from `b0aa8b77604139557169387b2fa8386355d8b651`.
- **Result:** `PASS_SOURCE/GITHUB`: 10-file commit `76cd8dae16b0f34e47c353b56b6e9dbcc5fcde25` confirmed by branch readback and compare with `main`; draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) opened against `main`, unmerged. `NO_CHECKS_REPORTED` for that original commit (0 check-runs, 0 PR workflow runs). **No CPU, CI, GPU or service tests run.** This entry does not qualify any runtime.
- **Artifacts:** `docs/MODEL-RECIPE-WIZARD-PLAN.md`, `docs/MANIFEST-CONTRACTS.md`, `handoff/*`.
- **Limits:** Manifest examples, wizard commands and state machines are designs, not implemented software.

## E-20261104-03 — N1 isolated CPU source contract check

- **Scope:** SOURCE/CPU (2026-11-04 KST). Executed in a separate CPU container, **not DGX**. Previous fork HEAD read: feature/recipe-wizard-handoff@07b0e3d49b387ecc29c00e3f5338e4e7065bcc27; new commit must be verified independently.
- **Tools:** Python 3, PyYAML 6.0.3, jsonschema 4.26.0; no vLLM/CUDA/Docker.
- **Exact commands:** python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -q => **15 PASS**; python3 -m scripts.manager.manifest validate recipes/qwen38-27b.candidate.yaml => expected **FAIL**, exit 2, 6 invalid/unverified fields; same command with tests/fixtures/recipe-valid.synthetic.yaml => schema **PASS**, exit 0, launch_authorized=false.
- **Artifacts:** schemas/recipe.schema.json; scripts/manager/manifest.py; recipes/qwen38-27b.candidate.yaml; tests/test_manager_manifest_cpu.py; tests/fixtures/recipe-valid.synthetic.yaml.
- **Limits:** synthetic a/b/c-character SHA values are fake fixture data; schema PASS is not repository existence/image runtime compatibility evidence. CI awaits new PR SHA observation. GPU/API/SWITCH/RELEASE NOT_RUN. No current DGX state observed.

## E-20261105-01 — Flash-Next 8000 default/N2 inventory source implementation

- **Scope:** SOURCE/CPU TEST CODE. Old fork HEAD was `bf453aea425c0d9136d67ac003a4f296a0a96885`; GitHub commit/CI outcome must be re-read after updating branch.
- **Change:** default Blazux NVIDIA Flash-Next, hybrid/YaRN/MTP2, exposed :8000/v1, served `qwen3.8-flash-next`; refactored unsafe implicit Docker container replacement into fail-on-name-exists. Removed outdated schema hard-coding of port 8000 and historic Orcarouter name.
- **Added read-only inspections:** `python3 -m scripts.manager.inventory doctor --dry-run` and `plan --dry-run` via Wizard. Commands collect local Docker/ss/disk/HF cache metadata; never execute model/Docker mutation.
- **New tests:** `tests/test_manager_inventory_cpu.py` (10 synthetic scenarios), `tests/test_flash_launch.py` (+4 cases), `tests/test_manager_manifest_cpu.py` updated old port expectations. GitHub CPU workflow expanded; **CI_NOT_YET_OBSERVED** in this source entry.
- **DGX:** user reports old services removed, **NOT_INDEPENDENTLY_VERIFIED**. No model/download/GPU/API/bench, no new runtime measured; required source/model image revisions still to be pinned for release.

## E-20261105-02 — CI failure and corrective script mode

- **Scope:** CI, commit `7e8f4a109a04c130a5dba0d73e3ece0881d85478`.
- **Observed:** GitHub Actions jobs [push failure](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41947918546/job/126984612955) and [PR run](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41947924748/job/126984632242) reported manifest **15/15 PASS**, N2 Inventory **10/10 PASS** and launch **4 FAIL/13**. Exact failures: `test_capable_dflash_launch`, `test_default_options_remain_empty`, `test_default_port_8000_and_next_flash_model_id`, `test_docker_options_reach_docker_not_vllm`; shell exit 126.
- **Root cause:** GitHub tree update accidentally wrote executable shell paths `flash` and `scripts/serve.sh` as `100644`. Root Git tree confirmed incorrect modes; not a demonstrated model/runtime bug. Correction restores `100755`; actual CI rerun must be independently checked. No failure history removed.
- **DGX:** NOT_RUN, no status observed.

## E-20261105-03 — Confirmed Wizard-first P1–P7 roadmap (decision, not test)

- **Scope:** USER_DECISION / DOCUMENTATION. The user reconfirmed sequential Wizard execution for all milestones. Evidence is the user request; not runtime testing.
- **Last independently verified source CI:** `feature/recipe-wizard-handoff@017319a5394155797bcb7e5c933ccef35080d669`; [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41948116286/job/126985272415) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41948122438/job/126985292140) **SUCCESS** (15 manifest + 10 inventory + 13 launch + 1 script modes = 39/39 tests each). Historical `7e8f4a1` four test failures remain recorded in E-20261105-02.
- **Current deliverable:** documentation-only alignment, no new source-test execution; CI for resulting documentation HEAD to be read back. **GPU/API/BENCH/SWITCH/RELEASE = NOT_RUN**; live DGX and :8000 occupancy **NOT_OBSERVED**.
- **Boundary:** Roadmap confirmation does not itself approve GPU loading or model/cache deletion. P4 is conditional with exact approval; `SKIPPED_NOT_NEEDED` permitted.

## E-20261105-05 — DGX terminal log supplied by operator

- **Source/scope:** user-attached terminal output, 2026-11-05; `USER_SUPPLIED_DGX_LOG`, **not direct SSH observation**. `wizard/00-doctor.sh`, `wizard/10-plan.sh` reported `collision_free=true`, host :8000 unoccupied, no `qwen38-flash` container, 580,134,281,216 bytes free. OpenWebUI and Portainer were still running. `./flash doctor default` showed aarch64 GB10, unified memory 121 GiB total /117 GiB available, Docker 29.6.2.
- `./flash setup default` image build **FINISHED**, `qwen38-flash-dgx:v0.32` image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, then resumed download for `nvidia/Qwen3.8-Flash-Next-NVFP4`; last output **9/25 (36%)**. **No proof** download/hybrid/serve/API/bench complete.
- The shell already received `./flash serve default`, `./flash wait`, `./flash test` sequentially after setup. These may run without any additional assistant action once setup finishes. Do not start a second `setup`, `serve`, change the active worktree, or remove any assets.
- Observation is time-bounded; fresh current status remains required.

## E-20261105-06 — P1 Wizard code + CPU mock suite

- **Scope:** SOURCE (GitHub commit `c625a49276272e90d19ab6367f580a0230754890`), CI verified: 2/2 SUCCESS, 80/80 CPU tests each. Added `p1_assets.py` fail-closed snapshot/index and symlink audit, `p1_wizard.py` live plan/approval/action runner, `p1_bench.py` SSE benchmark, `wizard/p1.sh` shell entry, and `tests/test_p1_*_cpu.py` fake backends. Extended GitHub workflow: 41 new P1 CPU tests and 39 baseline CPU tests PASSED in each of two jobs; [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41959325678/job/127021656282) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41959334560/job/127021682353).
- **Limit:** No DGX Wizard operation performed by assistant; no new GPU/API/benchmark results claimed. Plans require complete assets, live image identity, container/port checks and fresh exact approval, and cannot automatically download/clean up/switch.

## E-20261105-07 — Modular P1–P7 Wizard CLI source/CI

- **GitHub SOURCE commit:** `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`, branch `feature/recipe-wizard-handoff`; [CI push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961358317/job/127028222400) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961362251/job/127028234413), both **SUCCESS**. Per job: 15 manifest + 10 inventory + 13 legacy Flash + 1 shell mode + 41 P1 + 21 routing = **101/101 CPU PASS**.
- **Contract:** `./wizard.sh list --json`; `./wizard.sh p1 status --json`; `./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json`; `./wizard.sh --stage p3 --action switch ... --json`. P2–P7 are **INTERFACE_ONLY / runtime NOT_RUN / operations_enabled=false**; execute/approval arguments return BLOCKED. P1 delegates to existing approval-protected core.
- **Follow-up:** P1 JSON-guided handling improvement and 2 tests submitted in a separate commit; verify updated CI independently. **No assistant DGX command, GPU/API/BENCH, switch, cache cleanup or Docker operation**. Prior operator-supplied download and queued commands not interrupted.

## E-20261105-08 — Final modular Wizard CLI source CI

- **Source/docs HEAD tested:** `feature/recipe-wizard-handoff@43f5131b63b7e3f20cde0c409b3ddd672ddb349b`. Two GitHub Actions `manifest` checks completed **SUCCESS**: [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961837000/job/127029761586) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961842431/job/127029780582).
- **Observed CI logs per job:** 15 manifest PASS + 10 Inventory PASS + 13 legacy Flash PASS + 1 executable mode PASS + 41 P1 CPU PASS + 23 Wizard router PASS = **103/103 CPU tests**. P1 guided mode in JSON returns BLOCKED without prompting and normal TTY path remains supported. Unsupported stages and fake approvals are blocked.
- **Runtime boundaries:** all code tests are GitHub-hosted CPU-only mocks; **DGX Wizard GPU/API/BENCH/SWITCH/RELEASE NOT_RUN**, no new images/weights served and no cleanup. P2–P7 are non-executable planning interfaces. Previous user-supplied DGX image-build/download log is time bounded and not superseded by CI results.

## E-20261105-09 — Domain-grouped Wizard refactor and compatibility CI

- **Source commit:** `571e1c204d76bcb66b9e02cb1315ac775013a130` on `feature/recipe-wizard-handoff`. GitHub Actions [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41967161260/job/127046714703) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41967169194/job/127046737309) both **SUCCESS**.
- **CPU test logs per job:** 15 manifest + 10 inventory + 13 legacy Flash + 1 permission + 41 P1 + 32 grouped CLI router = **112/112 PASS**. Newly verified: grouped catalog, four domain categories, P1/P2/P5 model routes, P3/P6 switch routes, legacy stage aliases, no-TTY/JSON safety and fail-closed future stages.
- **Boundaries:** `SOURCE/CI PASS` only. **DGX GPU/API/BENCH/SWITCH/CLEANUP/RELEASE=NOT_RUN** for this refactor; current live download/port status not re-probed, no user-owned shell process modified. P2–P7 are `INTERFACE_ONLY` and execution is blocked.

## E-20261105-10 — Temporary P1 operator bundle source/CI boundary

- **Scope:** SOURCE/CPU/CI pending exact new commit; `scripts/temporary/p1-post-download.sh` shell wrapper, `p1_post_download.py` Python coordinator, `scripts/temporary/README.md`, `tests/test_p1_temporary_cpu.py`; CI workflow extended with fake backend tests and shell/executable mode checks.
- **Safety design:** only read-only diagnostics by default; per-action plan hash validated through current P1 Wizard; terminal consent separate for verify and benchmark, no benchmark without verify PASS, process/branch/dirty-tree guards; JSON report outside Git and model cache with 0600 permissions, no automatic model mutation.
- **Evidence outstanding:** new GitHub Actions results and actual DGX operator log. User's prior download/setup chain must be confirmed finished **before** using the wrapper. No assistant-executed DGX/GPU/API/benchmark, no service changes or cache deletion; `DGX=NOT_RUN` until operator returns evidence.

## E-20261105-11 — P1 temporary operator bundle CPU CI accepted

- **Code HEAD:** `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b`, `feature/recipe-wizard-handoff`. GitHub Actions [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970955588/job/127058833280) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970960007/job/127058848658), both **SUCCESS**: 131 unique CPU tests each (15 manifest, 10 inventory, 13 launch, 1 script mode, 60 P1 including 19 temporary tests, 32 router).
- **Tested behaviors (mock DGX):** safe read-only inspection; no setup/Git reset/Docker rm; independent live Wizard plan approval; blocked/dirty/wrong-branch/active-setup refusal; mid-run race prevention; benchmark only after verify PASS; restricted JSON artifact outside Git/HF cache.
- **Real DGX:** `NOT_RUN_BY_ASSISTANT`. No GPU/API/benchmark results, operator's queued `flash setup/serve/wait/test` completion still not observed and must be confirmed before `git pull`/wrapper.

## E-20261105-12 — DGX operator report: checkpoint download finished, Wizard blocked

- **Source:** user-provided DGX terminal output and operator clarification, 2026-11-05. **Evidence scope:** USER-REPORTED download complete; console wrapper evidence for `git pull` and `bash scripts/temporary/p1-post-download.sh`; not assistant SSH and not complete raw `result.json`.
- **Git/host:** `feature/recipe-wizard-handoff@dea7c5aa183da770b6b467288f2f6eedf8e94946` fast-forward; working tree clean; no relevant active setup process detected. Result path `/home/inlc/blazux-p1-reports/20261105T052545Z-1e6ec592/result.json`.
- **Read-only command statuses:** doctor=3, inventory_plan=3, HTTP health=0, HTTP models=0, GPU command=0, Docker command=0. Response contents and model ID were not pasted. P1 verify and benchmark `status=BLOCKED`, issues `checkpoint_downloading_or_incomplete` and `hybrid_not_prepared_or_incomplete`; no Wizard actions executed.
- **Interpretation:** generic P1 source/Hybrid audit failure; not evidence of ongoing download. Could be refs-main-only handling, stale incomplete blobs, missing Hybrid marker/files or a different configured cache/mount; no cause selected without new diagnostic facts. New `p1_cache_diagnosis.py` provides read-only facts from actual snapshot and strict audit. SOURCE/CPU CI verified at `4c0041dd230e2abe22ba8379aca74068933ecece`: GitHub push and PR both SUCCESS, each **138/138 CPU tests PASS** (15 manifest + 10 inventory + 13 launcher + 1 executable-mode + 67 P1 + 32 Wizard router). The earlier `eb759ad` source attempt failed its tests because the optional new diagnostic key was absent from an old fake fixture; fixed in `4c0041d` without changing runtime assets. Real DGX evidence still pending.
- **P1 GPU/API/benchmark:** Wizard verification and benchmark `NOT_RUN`; observed curl GET is an API reachability test, not a workload benchmark or complete model identity verification.

## E-20261105-13 — Default NVIDIA index cap regression fixed, actual missing files unresolved

- **Model release fact:** NVIDIA `nvidia/Qwen3.8-Flash-Next-NVFP4` revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` includes `model.safetensors.index.json` (~31.3 MB) and `tokenizer.json` (~12.8 MB). Source: https://huggingface.co/nvidia/Qwen3.8-Flash-Next-NVFP4/tree/main
- **Source bug:** Python strict index parser refused >16MiB (incompatible with official file), though the operator's **observed filenames** were initially rejected before this parser. Source change now permits ≤64MiB while retaining bounds; diagnostic returns exact file/symlink/size status, not merely `checkpoint_downloading_or_incomplete`.
- **GitHub evidence:** code/test commit `66c6c448c1922f958886fa4696c403a4b6227685`, push job https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41976231273/job/127075608240 and PR job https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41976236273/job/127075624614 — both **SUCCESS**, per job 15 + 10 + 13 + 1 + 74 + 32 = 145 CPU tests PASS.
- **Operator DGX prior evidence:** source files `model.safetensors.index.json`, `tokenizer.json` failed `_good_file` metadata validation; Hybrid `tokenizer.json` failed with `.prepared` present. HF blob incomplete-count=0, refs/main valid. Exact failure mode (missing vs dangling symlink vs zero-size) NOT YET OBSERVED. No actual P1 Wizard GPU/API workload BENCH acceptance.
- **Next**: `git pull --ff-only` then one read-only temporary wrapper; review exact file metadata and served API ID. No guessed setup/download/prepare, and no modifying current services.

## E-20261105-14 — DGX confirms externally linked Flash-Next metadata

- **Operator-supplied output:** `/home/inlc/blazux-p1-reports/20261105T055849Z-084c3609/result.json` summary after `git pull` to `4708fe9ef396404d823ca385cde013b67e4d098a`. `api_model_ids=["qwen3.8-flash-next"]`; full snapshot revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`; incomplete blob count 0. Original model index + tokenizer and Hybrid tokenizer: `TARGET_OUTSIDE_REPOSITORY`, `symlink=true`, successful target resolution; Hybrid index `PRESENT_NONEMPTY`, `size_bytes=31907813`; Hybrid marker present.
- **Interpretation:** Existing Blazux-compatible shared metadata link layout was over-rejected by the new P1 file containment check. This alone does not prove that every model tensor is valid or any GPU workload passed. The API served ID indicates there is an API service listening despite the user's description of no existing services.
- **Test authorization:** user approves bounded, non-disruptive GPU inference/benchmark without manual per-action hash entry. Implement `--auto-gpu` as a scoped script option; still validate each current Wizard plan ID and fail closed on changed preflight or failed P1 verification. No service lifecycle or cache changes authorized.
- **Source/CPU CI evidence:** `0063b0e004902408f980c155076c098d49d4569e`, GitHub push and PR jobs **SUCCESS**, 155 CPU PASS each (15 manifest, 10 inventory, 13 launch, 1 script mode, 84 P1, 32 router). [Push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978150843/job/127081754127), [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978155433/job/127081768853).
- **Next DGX scope:** after code pull, single `bash scripts/temporary/p1-post-download.sh --auto-gpu` call. Actual GPU/API/benchmark statuses remain `NOT_RUN` for the new version until operator evidence.


## E-20261105-15 — DGX P1 assets pass, Wizard's combined verify fails

- **Raw-report path:** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` (operator-owned); only console summary supplied.
- **Facts:** snapshot `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, 11/11 listed shards resolved in source+Hybrid, API model ID `qwen3.8-flash-next`, verify+benchmark plans READY, **verify=FAIL, benchmark=BLOCKED verification_not_passed**. These are verified user-supplied runtime outcomes. No benchmark inference was executed.
- **Known source defect:** original temporary runner only parsed Wizard JSON result on rc=0; Wizard returns rc=2 with evidence even on FAIL, hence console `evidence:null` does not demonstrate no evidence. Original combined `_chat_probe` demanded 48 token text, tools required and tiny vision; one failure throws and masks others. Exact original error is UNKNOWN without reading the saved raw result; do not call this a model failure.
- **SOURCE/CI corrective commit:** `391a2844f4c8549e282eae3e266806c89801ad1a`, [push CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42015135913/job/127203693134), [PR CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42015144016/job/127203722486); 2/2 SUCCESS, 173 CPU tests/job. Separates default completions/chat baseline from optional tools/vision and retains nonzero Wizard evidence; actual DGX post-fix GPU validation NOT_RUN.
- **Next:** inspect stored evidence for original failure, then single auto-GPU wrapper on new code. Do not alter operating service, HF data, Hybrid, or gateway.

## Historic evidence not transferred

## E-20261105-04 — User-reported Flash-Next download still in progress

- **Time/subject:** 2026-11-05 11:46 KST, `nvidia/Qwen3.8-Flash-Next-NVFP4`.
- **Evidence:** user said checkpoint was **still downloading**. Classification: `USER_REPORTED / DOWNLOAD_IN_PROGRESS`, not a DGX/filesystem observation and **not** a checksum or completion proof.
- **Unknown:** actual download process, command, bytes, completion percentage, snapshot revision, local cache path and storage headroom.
- **Verification:** `DOWNLOAD_COMPLETE=NOT_VERIFIED`; `HYBRID_PREPARED=NOT_VERIFIED`; `GPU/API/BENCH=NOT_RUN`. No upload/download/cache/operational operation by the assistant.
- **Next safe action:** build P1 Wizard flows and download-in-progress fail-closed tests from synthetic data; after reported completion, verify snapshot and all weight shards read-only before preparation/serve, avoiding concurrent writes.


Old Preview/YSLAB projects reported Orcarouter BF16 PLE/MTP results; those are **reference evidence only**, not proof of the new vLLM 0.32 fork. Historical Preview strict same-token logprob `1e-4` release blocker remains unresolved. DGX status is unobserved this session.

## Update policy

Append new measured entries, never replace failures. When rerunning a test, give it a new ID and reference prior entry. If an entry proves wrong, add an explicit correction with link; do not rewrite history. Publish non-sensitive artifact locations and keep credentials/private data out.
