## 2026-11-07 — P3-C OPERATOR PLAN WINDOW ROLLOVER FIX IS SOURCE-ONLY

Actual DGX `--execute` twice near 10:10 KST canonical 10-minute plan expiration (10:08:14, 10:09:30 KST) returned `BLOCKED` solely due `P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS`, with `approval_accepted=false/executed=false/execution_dispatched=false`. No Stage C transition, GPU operation or downtime. Active model observed remained original Flash-Next; preserved NVIDIA 27B target unchanged, original P1/P2 evidence PASS. Canonical plan window end `2026-11-07 10:10:00 KST`; old SHA `30b2b29bb715e2393b65152ea8d1da2db61956d631efce2248aee2e9690610de` has expired and cannot be reused.

Updated **only** the tracked `scripts/temporary/p3_stage_c_operator.py` flow: near expiry, wait a bounded <=150 seconds for a **different fully READY read-only canonical plan** with >=120 seconds left; if source/API/P1/P2/container/provenance changes, SHA rotates unexpectedly before boundary, time limit/TTY/interrupt fails, or git becomes dirty, BLOCK before dispatch. Once freshly READY, it requests fresh exact current SHA, separate Flash downtime ack and separate final-C ack; then still repeats plan/live check and uses unchanged canonical switch guard. `--plan` unchanged. New virtual-clock CPU tests; docs `docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md`. Source+CI cannot claim actual DGX Stage C execution. No auto approval, no model deletion, no PR merge. P3-C still NOT_EXECUTED pending actual operator command.

---

## 2026-11-07 — PUBLIC BENCHMARK REPORTS VERIFIED AGAINST ORIGINAL REAL DGX PRIVATE RECEIPTS

User ran `bash scripts/temporary/verify-published-benchmarks.sh` on actual DGX after pulling branch changes. Both Flash `f506db4c76430674.json` and NVIDIA 27B `80f109dbd7c97460.json` returned `status=VERIFIED/issues=[]/executed=false`, with raw original SHA256 values respectively `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db` and `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. Thus the previously pending REAL-DGX private-to-public benchmark reproducibility check **is complete** (not merely mock CI). Published summaries are now source-reconciled, not unverified manual transcriptions. They remain narrow 3-request benchmarks using distinct Flash E2E and 27B E2E/decode-proxy definitions.

No GPU inference or service transition was performed by this check. **P3-C remains NOT_RUN, NOT_AUTHORIZED for live Flash downtime**; the previous actual `--execute` was CANCELLED prior to dispatch. Read-only benchmark verification does not re-prove current API readiness. For next actual step run `bash scripts/temporary/p3-stage-c-operator.sh --plan` with latest code for a fresh live check, and require independent exact current plan SHA/downtime/target acknowledgments before any `--execute`. No A/B repetition or P1 retest. PR remains Draft, unmerged.

---

## 2026-11-07 — GIT-PUBLISHED METRIC-ONLY BENCHMARKS / C CANCELLED BEFORE DISPATCH

Original operator evidence contains actual DGX Flash-Next post-P3-B benchmark PASS (mean 37.9527 tok/s, TTFT p50/p95 1.384594/1.779602 s, latency p50/p95 1.724560/1.813754 s, 3x64-token requests, concurrency1) and actual NVIDIA 27B bounded bench `BENCH_PASS_RESTORED_VERIFIED` (mean E2E 7.9002 tok/s, mean decode proxy 11.1801 tok/s, TTFT p50/p95 0.179349/28.977990 s, latency p50/p95 5.818283/34.609889 s, 3 requests). Published **sanitized** copies of this metric metadata only to tracked `benchmarks/published/`, with original private SHA256 digests and pinned model revisions; raw JSON evidence, plan IDs, host paths and logs stay LOCAL and `/reports/` remains Git-ignored. `scripts/manager/benchmark_publication.py` + CPU tests allow future original-private → public allowlist export. One-command cross-check `bash scripts/temporary/verify-published-benchmarks.sh` is READ ONLY; DGX original-file verification pending operator execution. These values are from user logs, not new benchmark invocations; 27B E2E vs decode proxy are not the same metric.

Actual P3-C operator `--plan` READY and P1 gate PASS. User's P3-C `--execute` submitted `[56a30...` instead of exact `56a30...` (the leading `[` is only prompt decoration), got **CANCELLED**, `approval_accepted=false/executed=false/execution_dispatched=false`. No Docker stop/start or Stage-C receipt. P3-C remains NOT_RUN; no automatic retries. Reissue new plan SHA and separate downtime/final C confirmations only at operator's direction.

---

## 2026-11-07 — NEW STAGE-C WRAPPER READY IN SOURCE; DGX C PLAN READY, NO SWITCH YET

Operator DGX independently ran `./wizard.sh switch flash-next-27b stage-c --plan --json`: **READY_TO_REQUEST_TRANSITION_APPROVAL / issues=[] / executed=false / approval_accepted=false**, POST-B P1 verify+benchmark+rc3 diagnostics gate PASS with SHA256 hashes, P2 trial benchmark receipt hash unchanged, original running Flash CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5` and stopped preserved 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`, shared image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. Old short-window SHA `d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7` expired by design and must never be reused. Optional P2/P3 evidence import prompt received literal `COPY` instead of SHA: `CANCELLED/copied=0/executed=false`; no P2/P3 records copied or migrated.

NEW GitHub source: `scripts/temporary/p3_stage_c_operator.py`, `scripts/temporary/p3-stage-c-operator.sh`, fake-DGX `tests/test_p3_stage_c_operator_cpu.py` provide a tracked D-016 Stage C operator. Default `--plan` checks original immutable A/B receipts, pinned P2, P1 post-B PASS evidence and live Flash without service mutation. `--execute` would require a **new** exact current C SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C` manually typed in TTY, then fresh preflight and canonical Wizard recheck. Third literal is wrapper-only; core C uses null `--enter-p3`. C pass additionally requires live 27B API and canonical `stage-c.json` proof. Per-model direction report under `reports/transitions/flash-next--to--27b/`, no changes to original state/journal/locks. Source CI is not actual DGX C execution; **P3-C NOT_AUTHORIZED/NOT_EXECUTED**. No PR merge. Runbook: [C operator](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## 2026-11-07 — HISTORICAL EVIDENCE VIEW AND GUARDED P2/P3 COPY ADDED (SOURCE ONLY)

Latest source adds a **read-only model-indexed history** for original Flash Verify/Benchmark, 27B GPU trials/benchmarks, stage A/B model transitions, diagnostics and optional operator reports. The service-policy manifest supplies human-facing model IDs; the UI hides internal P-codes. It distinguishes Flash-Next direct throughput from 27B E2E and decode-proxy throughput. History reads both old `~/.local/state/blazux-wizard/p1,p2,p3` and new ignored repo `reports/`, deduplicates byte-identical SHA256, and sorts by UTC event time. CPU-only synthetic fixtures test this.

Stage 1 copy-only consolidation: `./wizard.sh evidence migrate --plan` / `--guided` or main Wizard `3 Advanced → 8` generates and revalidates a digest-bound fresh copy plan, requires the literal full SHA in prompt, writes private 0600 append-only files under `reports/models/<served-id>`, `reports/transitions/<direction>`, `reports/diagnostics/<served-id>`; no source deletion. P2/P3 original state/journal/locks and original trial/transition evidence remain authoritative; no change to their live writers or restore mechanics. Stage 2 native writer mirrors and stage 3 full state relocation are **not implemented**, by design until later real-DGX review. Source approval tests are not evidence of a DGX import.

**P3-C next:** Actual operator-provided P3-B and post-B P1 PASS; fresh stage-C read-only plan on DGX NOT_RUN. Request `./wizard.sh switch flash-next-27b stage-c --plan --json` after source CI+ff-only update, then evaluate its exact live source/target/receipt gates. C downtime NOT_AUTHORIZED and no switch performed. See [migration document](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md) and [next actions](NEXT-ACTIONS.md).

---

## 2026-11-07 — OPERATOR POST-B P1 ACTUAL PASS / MODEL-CENTERED WIZARD UX SOURCE UPDATE

The operator supplied `blazux-wizard.zip`, confirming DGX **P1 Verify PASS** (baseline/extended + text/chat/tools/vision, UTC 2026-11-06T23:26:27Z) and **P1 Benchmark PASS** (UTC 23:30:31Z, 3 requests, 64 tokens, concurrency 1, seed 1234; 37.9527 tokens/sec; TTFT p50 1.384594 s, p95 1.779602 s; latency p50 1.724560 s, p95 1.813754 s). Both have distinct typed exact plan IDs and immutable old-path receipts under `~/.local/state/blazux-wizard/p1`. P3-B stage-B canonical state PASS, existing original NVIDIA Flash-Next serving :8000 and post-B read-only diagnostics PASS with expected own name/port collision rc3. **P3-C NOT_AUTHORIZED/NOT_RUN**; no automatic phase transition. Original historical receipts must never be rewritten.

Source branch now changes Flash interactive UX to one chosen action, P3-style `Type exactly [SHA]` with the current SHA visible, and Verify/Benchmark metrics on screen. New Flash evidence writes into Git-ignored project `reports/models/qwen3.8-flash-next`; P3 evidence gate reads this and the legacy path without allowing old PASS to mask newer failed attempts. All operational changes were source-only GitHub edits; **no further GPU/runtime/transition/merge took place**. Review [operator UX/evidence contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md), confirm current HEAD and CI, then a clean operator fast-forward pull before using the updated Wizard. Do not rerun real GPU checks without separate operator authorization.

---

## 2026-11-07 — CPU SOURCE VALIDATION CHECKPOINT

GitHub source+documentation as of commit `67ff9cc2e4ece0c89c911513673f7d5d55c98fa4`: **501/501 CPU PASS, 23 test groups** ([Actions run 42310408411](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42310408411)). Draft PR #1 reviewed with COMMENT (review ID `5808289782`), remains OPEN/DRAFT/UNMERGED. This validates only source/CPU regressions, not new real DGX post-B P1 or C. Newest handoff-only commit SHA/CI must be checked live at next session. D-016 next: clean fast-forward pull then exactly one `bash scripts/temporary/p1-post-b-audit.sh`; no unapproved GPU call, model switch or cache cleanup.

---

## 2026-11-07 — LATEST AUTHORITATIVE STAGE: P3-B ACTUAL DGX PASS; Flash-Next ACTIVE

**This section supersedes older `P3-B NOT_RUN` / `27B ACTIVE` sections below.** Actual DGX outputs supplied by the operator, NOT inferred from CPU CI:

- P2 27B initial GPU benchmark/restoration: **PASS / COMPLETE**, do not repeat.
- P3-A Flash-Next → 27B: **ACTUAL_DGX_PASS** (`stage-a.json`, `P3_A_PASS_27B_ACTIVE`).
- P3-B 27B → original Flash-Next: **ACTUAL_DGX_PASS**, `stage-b.json`, `P3_B_PASS_FLASH_NEXT_ACTIVE`, `executed=true`, `wizard_result.status=PASS`, `wizard_result.live_verified=true`, `issues=[]`, `post_switch_status=LIVE_SERVICE_VERIFIED`.
- Last operator-verified model: **flash-next**; API served ID **`qwen3.8-flash-next`**, port **8000**. New live runtime observation during this GitHub source-only work: **NOT_PERFORMED**.
- Original Flash CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. P3-A-created 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`. Runtime image shared `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; identical image does NOT imply identical served model.
- Actual B operator report `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T223124Z-14861d75.json` (historically misnamed); canonical `/home/inlc/.local/state/blazux-wizard/p3/stage-b.json`. Historical `approval_accepted=false` in old operator report is a wrapper bookkeeping error, not evidence of missing core execution consent. Do not modify old evidence.
- P1 POST-B READ-ONLY PREFLIGHT: **PASS**: `/home/inlc/blazux-p1-reports/20261106T224010Z-d2095867/result.json`, API ID correct, branch+clean+plan checks READY, source/Hybrid ready. `actions.verify/benchmark=BLOCKED` with `reason=inspection_only` means **NOT_RUN**, not failed.
- P1 POST-B Verify: **NOT_RUN**; Benchmark: **NOT_RUN**. Post-B raw doctor/inventory `rc=3` disposition: **NOT_YET_QUALIFIED** (prior pre-A expected collision is not new post-B evidence).
- P3-C: **NOT_RUN, NOT_AUTHORIZED**, ineligible until separately approved actual new P1 Verify, numeric Benchmark, valid post-B diagnostics.

**Current source work:** stage-B filename/approval-state fixes and append-only `scripts/temporary/p1-post-b-audit.sh` with fake-DGX tests and latest-evidence P3-C gate. No GPU/service mutation or PR merge. D-016: commit/CI first, then operator fast-forward pulls and runs ONE tracked read-only audit, stops on BLOCKED, and separately approves any later GPU action.

---

## 2026-11-06 — P3-B separate downtime permission GRANTED; actual DGX transition pending

Operator explicitly replied **"승인"** when asked the unambiguous scoped question "P3-B(현재 NVIDIA 27B 중단 → 원본 Flash-Next 복귀)를 승인하시겠습니까?" following real DGX `READY_FOR_SEPARATE_P3_B_APPROVAL` (`issues=[]`, saved `~/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`). **P3-B entry permission now granted** for this one stage only; does not authorize another action. No new actual B DGX output exists: **P3-B NOT_RUN**, 27B last verified running. Tracked GitHub `scripts/temporary/p3-stage-b-operator.sh --execute` is ready, CPU [489/489 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) with exact stage-B-only `I_ACCEPT_27B_DOWNTIME` + `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`, fresh full current plan SHA and typed three-step terminal confirmation. Do not pre-fill approvals or use expired B inspection plan SHA. D-016: agent commits docs; operator fast-forward pulls and runs one tracked wrapper. Wizard must verify live source/target containers and restore on failure when possible; return `P3_B_PASS_FLASH_NEXT_ACTIVE` and independently verified `qwen3.8-flash-next` before any P1 work. No automatic post-B P1 or C, no PR merge/cleanup.

---

## 2026-11-06 — Real DGX P3-B INSPECT PASS, 27B still LIVE, separately approved stage B NOT_RUN

Operator ran D-016 tracked `scripts/temporary/p3-stage-b-inspect.sh` after pulling HEAD `e5d4171d07838e565510b1127f4a0b27dcd8423f`. ACTUAL DGX result `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`, `operations_enabled=false`, `approval_accepted=false`, saved to `/home/inlc/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. API current model `27b`, ID `qwen3.8-27b`; running 27B container ID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`; preserved original Flash ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`; both share runtime image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. P2 benchmark evidence hash unchanged. Canonical B stage plan generated with no issues (`7af40f009dd67975c77b98c03183833dd4997e16f9c9443bd11ea880f6d8162c`, expires 17:50 KST Nov 6); this SHA is inspection-only and must not be reused after expiry.

**Actual staged state:** P1 initial PASS / P2 trial+bench PASS / **P3-A DGX PASS (27B ACTIVE)** / **P3-B read-only inspect PASS, NO B execution or B permission** / post-B P1 verify+numerics NOT_RUN / C NOT_RUN. User's log is not an additional downtime approval. No assistant-side GPU/Docker mutation was performed.

Source work after receipt: fixed wrong all-stage Flash downtime ACK in core: B now has exact `I_ACCEPT_27B_DOWNTIME` + independent `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`; A/C retain original ACK contracts. Added `scripts/temporary/p3-stage-b-operator.sh` default read-only and explicit `--execute` protected by three typed B-specific exact approvals, active source/API and A receipt safeguards, plan expiry/rotation guard, independent returned Flash API, private 0600 evidence, no auto P1/C. Fake DGX CI [489/489 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) on source `59046c4e17a5094f2c80a84025a763c2a767edcb`; actual updated B operator DGX NOT_RUN. Do not instruct `--execute` until separate B user approval; 27B kept live. Draft PR #1 open/unmerged, no cache/image cleanup.

---

## 2026-11-06 — P3-A actual DGX PASS: NVIDIA 27B LIVE; stop before B, B source inspector CPU-tested

User actually executed `bash scripts/temporary/p3-stage-a-operator.sh --execute` after a fast-forward pull to Git HEAD `a3945bdc5cfec467478978c47b3a27bdafee84bd` and typed the current plan hash `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`, Flash downtime ACK and separate P3 entry ACK. The Wizard returned `stage=a,status=PASS,executed=true,live_verified=true` and durable `~/.local/state/blazux-wizard/p3/stage-a.json`. The tracked wrapper independently observed `post_switch_observed_model=27b`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `status=P3_A_PASS_27B_ACTIVE`, `issues=[]` and exit code 0. Private evidence `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. As of actual user report, **27B active**, original Flash original image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137` and original container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5` are stage-A identity anchors; independently inspect still-preserved/stopped status before B. P2 receipt hash remains `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`.

**Stage ledger:** P1 initial pre-A evidence PASS / P2 GPU smoke+benchmark PASS / **P3-A ACTUAL PASS** / **P3-B NOT_RUN, NOT AUTHORIZED** / P1 post-B verify+measured benchmark NOT_RUN / P3-C NOT_RUN. P3-A being successful doesn't justify any subsequent downtime or automatic GPU workload. Existing stage-B canonical Wizard backend has independent exact plan/ack requirement; plan generation alone does not approve execute. To support the upcoming separate decision, added source-only D-016 `scripts/temporary/p3-stage-b-inspect.sh` and Python module with NO execute mode; it compares actual private A receipt, 27B live Manifest/API ID, stopped preserved Flash container ID/image and newly generated stage-B plan, writes local 0600 summary. It cannot run B. CPU mock-DGX cases validate false-identity/stale plans/no execute. Actual DGX B inspection is NOT_RUN pending operator pull. The original P3-A source test and latest source changes are GitHub/CI only; no change was made on the currently running 27B by assistant. Do not merge Draft PR, clean HF caches, or schedule background GPU activity.

---

## 2026-11-06 — Actual P3-A triple-ack attempt BLOCKED, zero Docker mutation; fixed approval UX and short plan boundary

User ran `bash scripts/temporary/p3-stage-a-operator.sh --execute` after fast-forward pull to HEAD `be6f3f9e6d757cc11c6299024900b637c7ca239d`. Real P1 proof `PRE_A_P1_REVIEW_READY`, live Flash `LIVE_SERVICE_VERIFIED`, P2 receipt hash `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, P3-A plan `94b4dedae21eb72b12443029257931e123e33404c32898d9ae2bad52954c064f`. Operator independently typed plan ID, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, and `I_SEPARATELY_AUTHORIZE_P3_ENTRY` correctly. Wizard returned `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT`, `approval_accepted=false`, `executed=false`, no stage transition. Local report `~/blazux-p3-reports/p3-a-operator-20261106T073049Z-4dc8be1b.json` has `status=OPERATOR_REVIEW_REQUIRED` **from old wrapper**, even though nested Wizard result was `BLOCKED` and no operation occurred. P3-A/B/C actual service transitions remain **NOT_RUN**; original Flash service was verified before the attempt. No proof of failure to restore: there was no stop/start.

**Stale plan root evidence:** plan `expires_at_epoch_seconds=1793950200` = **2026-11-06 16:30:00 KST**. Receipt is named at **2026-11-06 16:30:49 KST** (07:30:49Z). The 10-minute plan window expired before the final report; this strongly explains stale-plan refusal (the exact nested fresh-plan difference was not included in operator output). Do not reuse the old hash.

Operator requested exact typed strings to be displayed **in the terminal**, not generic prompts. Source updated `scripts/temporary/p3_stage_a_operator.py`: prints actual current plan full SHA and both exact literal acknowledgements beside each prompt, with KST expiry and seconds remaining. `--execute` refuses initiating prompts when fewer than 120 seconds remain; after all typed acknowledgments refreshes the stage-A read-only plan and blocks without invoking execution if SHA changed or expired. A stale Wizard refusal with `executed=false` reports `BLOCKED` rather than misleading recovery warning. Never auto replace a SHA, auto-retry, or auto-enter B/C. Fake DGX tests include all three strings, short window, rotated SHA, stale refusal. [Code push CI 42181851452](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181851452) and [PR CI 42181858236](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236) **SUCCESS 459/459 CPU, 20 groups** on code SHA `fb34ce0ce985824cecd9c63159bf6f1eed408279`. Actual DGX with updated wrapper **NOT_RUN** yet. D-016 GitHub→fast-forward pull→one wrapper; fresh triple-ack required if operator opts into a subsequent real P3-A attempt. Preserve original Flash containers/images/cache and Draft PR.

---

## 2026-11-06 — Actual DGX P1 PRE-A PASS, conditional 27B entry now eligible; guarded P3-A wrapper SOURCE only

Actual DGX `git pull` then `bash scripts/temporary/p1-pre-a-readiness.sh` on source HEAD `834f823a76556a37a982e3dbf7f243db3edad6df` wrote `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`: `status=PRE_A_P1_REVIEW_READY`, **`issues=[]`**, both current/historical `rc3=EXPECTED_ACTIVE_FLASH_COLLISION` (2 checks each), P1 Verify PASS, P1 numerical benchmark PASS with 3 requests, 192 completion tokens; TTFT P50/P95 1.398707/1.751198s, latency P50/P95 1.687357/1.780142s, mean throughput 38.2968 tokens/s. Current Flash-Next service image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137` verified. Earlier P1 numeric gaps, rc3 ambiguity and temporary cached-diagnosis parser issue are **closed for pre-A assessment**; post-B P1 full reverify+remeasurement remains NOT_RUN and required later.

User's original P3-A scope was **if P1 initial gaps all resolved, approve 27B transition**. D-037 records that the condition is now satisfied. The local `p3_a_execution_authorized=false` field simply means the **read-only P1 evidence command** never authorizes/executes service changes; live stage A still requires a new plan and independently typed exact ID / downtime / P3 entry confirmations. No actual P3-A/B/C has run; current model remains Flash-Next.

Source added `scripts/temporary/p3-stage-a-operator.sh` + `p3_stage_a_operator.py`, covered by fake-DGX CPU tests `tests/test_p3_stage_a_operator_cpu.py` and Actions workflow. Default is plan-only; `--execute` requires interactive three independent typed confirmations, verifies same Flash image and complete P2 receipt provenance and freshness, delegates live transition ONLY to canonical Wizard stage-A executor, then independently rechecks actual served `qwen3.8-27b` API/model/container/image. On failure show `OPERATOR_REVIEW_REQUIRED` and do not retry or auto-B; rollback by core executor is best-effort and can fail. No host-GPU exclusivity or live P3 recovery qualification is implied by source/CPU CI. D-016 GitHub push→CI→DGX pull→one wrapper remains mandatory. Draft PR #1 stays unmerged.

---

## 2026-11-06 — DGX pre-A P1 evidence showed *two parser-induced blockers*; source fix 439 CPU PASS, DGX rerun pending

DGX operator ran tracked `scripts/temporary/p1-pre-a-readiness.sh` from HEAD `3a59419305b31266f034fe4cbec2b384bb91d1f4`. Real local saved receipt `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T064009Z-70e9cef9.json` reported `status=BLOCKED` only on `P1_ASSET_AUDIT_NOT_READY` and `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. **Other actual checks passed:** historic and current doctor/inventory rc=3 independently confirmed `EXPECTED_ACTIVE_FLASH_COLLISION` 2/2 each, P1 functional `p1_verify.status=PASS`, numerical `p1_benchmark.status=PASS` (3 samples, latency P50 1.687357s, TTFT P50 1.398707s, mean throughput 38.2968 tokens/s), live model flash-next, expected preserved image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. `operations_enabled=false`, `p3_a_execution_authorized=false`, no P3 execute.

Source root cause verified from original `scripts.temporary.p1_post_download.session`: private persisted `result.json` retains `checks.cache_diagnosis.stdout` JSON but **does not store a top-level `cache_diagnosis` key**; that top-level key is printed only in the console summary. `p1_pre_a_readiness.assessment` previously read `current["cache_diagnosis"]["wizard_audit"]`, always missing for genuine saved files, then falsely labeled missing revision as `DRIFT`. Fixed to reuse canonical `p1_post_download.cache_diagnosis_summary(current["checks"])` to read stored data and distinguish `P1_CURRENT_CHECKPOINT_REVISION_UNAVAILABLE` from actual `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. Test fixture changed to exact real `checks.cache_diagnosis.stdout` structure; additional positive, corrupt/missing, and true-drift CPU regressions added. **Source commit `9adc9ab282a91c02e959dcb5c62f98527b556391`: [push CI 42176219970](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176219970) and [PR CI 42176224898](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898) SUCCESS, 439/439 CPU tests across 19 groups**. Source proof only, **no DGX rerun yet**. D-016: operator fast-forward pulls, invokes same tracked wrapper once, returns `issues` and `status`; do not run P3-A or disrupt Flash automatically. Original conditional entry approval is not independently validated until real re-evaluation.

---

## 2026-11-06 — GitHub-first D-016 P1 audit delivered, 435/435 CPU PASS; operator DGX step pending

New tracked wrapper `scripts/temporary/p1-pre-a-readiness.sh` is committed with CPU fake-DGX tests, runbook, private evidence output and no GPU/service operations. Pre-A initial P1 numeric evidence *already supplied* (2026-11-05 original benchmark): TTFT P50/P95 1.398707/1.751198 s; latency P50/P95 1.687357/1.780142 s; mean 38.2968 tokens/s from 192 tokens across 3 requests. P1 source+Hybrid READY and basic/extended Verify PASS; 2026-11-06 inspection `actions.*=BLOCKED/inspection_only` is intentionally non-executed, not regression. Only historical/current raw `doctor=3` /`inventory_plan=3` cause remains unreviewed from supplied **summary**, plus D-034's mandatory post-B P1 rebenchmark later.

Discovered and corrected impossible P1 identity receipt check: actual P1 Wizard identity result has `health=PASS` and `models` with served ID, not `identity.status=PASS`. This was fixed in both initial read-only wrapper and P3 final C P1 gate, test fixtures made real-shaped, wrong-ID negatives added. GitHub push [42173798547](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173798547) and PR [42173805888](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) on source commit `75d22ce4303736ee84563a0f388a978379e4f228` SUCCESS, **435/435 CPU PASS, 19 groups**. No actual DGX pre-A wrapper run yet, P3-A/B/C NOT_RUN, no automatic P3 authorization. After fast-forward pull, operator invokes **one** `bash scripts/temporary/p1-pre-a-readiness.sh` and supplies its small JSON result; do not paste custom terminal Python snippets.

---

## 2026-11-06 — P1 initial numerics now REAL; D-016 tracked pre-A evidence wrapper developed (DGX NOT_RUN)

Operator-reported genuine P1 benchmark JSON `20261105T113125Z-586b2b46d93e.json` status PASS: **TTFT P50 1.398707 s / P95 1.751198 s; latency P50 1.687357 s / P95 1.780142 s; mean 38.2968 tokens/sec; 3 samples, total 192 tokens**. This supersedes prior "metrics not supplied" only. Flash-Next inspect-only report `20261106T060941Z-e71a159c/result.json` returned clean branch, source/Hybrid ready and no incomplete blobs; 11/11 indexed shards present/resolvable (some compatible external symlinks), original source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, API `qwen3.8-flash-next`, plans verify/benchmark READY, no active setup process. `actions.verify/benchmark` show `BLOCKED/inspection_only` because operator selected read-only mode; **not** GPU verify/benchmark failure. Historical P1 functional verify PASS is retained. Current/historic doctor/inventory-plan return 3 cause still **not independently established from raw JSON** (pasted report summary only contains rc), so do not accept P3-A conditional approval yet.

D-016 temporary script rule was re-read. Added a tracked `scripts/temporary/p1-pre-a-readiness.sh` and Python entry, with CPU fake-DGX tests; it reads old + current private P1 reports, original P1 verify+benchmark receipts and fresh Wizard service manager status, writing a concise local 0600 evidence record; **never switches service, starts GPU inference, performs git pull or auto-generates an approval**. Next operator action after CI: clean DGX `git pull --ff-only`, then run this **single wrapper**, return its small JSON. `PRE_A_P1_REVIEW_READY` would mean initial pre-A evidence acceptable for reviewing conditional P3 entry, **not** automatic Flash downtime or post-B evidence. P3-A/B/C remain NOT_RUN, original Flash active.

---

## 2026-11-06 — Conditional P3-A consent NOT MET: P1 missing metrics/rc3 evidence; 418/418 CPU PASS for guard correction

User requested P1 remaining-work inspection before any P3-A Flash→27B interruption and explicitly granted **conditional** approval only if no P1 work remains. Latest recorded P1 actual DGX on 2026-11-05 has `verify=PASS`, baseline+extended `PASS`, default_completion/chat/tools/vision `PASS`, `benchmark=PASS`, Flash image/source/Hybrid ready; **P1 numeric TTFT/latency/throughput values have never been shared or independently reviewed, doctor and inventory-plan rc=3 raw reasons unexamined, and required post-B P1 rerun NOT_RUN**. Condition is not met. P3-A NOT_RUN, no new service-change approval; original Flash service retained.

Source audit shows both `wizard/00-doctor.sh` and `wizard/10-plan.sh` delegate to `scripts.manager.inventory`; its CLI returns 3 when `collision_free=false`. When the expected `qwen38-flash` is already running on :8000, collision is expected even if inventory's `status=PASS` and `errors=[]`. Previous post-B P1 gate required both return codes zero, contradictory to active source service. Corrected to accept only raw-proven exact owned active Flash collision (both rc3, parsed doctor+inventory JSON with no inventory errors, correct image/name/API port/launch preview), not merely any rc3; genuine read errors or foreign containers fail closed. **Historic raw rc3 cause still UNKNOWN**, so it remains open. New post-B actual P1 verify/benchmark/diagnosis receipt requirement unchanged.

Source commit `26a69507983dbcb2a7ab4c569f9d8baa6162e25c`: [push 42172119698](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172119698) and [Draft PR 42172127412](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172127412) **SUCCESS**, 418/418 CPU tests over 19 groups. Actual DGX P3 A/B/C NOT_RUN, stage-A previous plan IDs must not be reused after expiry; Draft PR remains unmerged.

---

## 2026-11-06 — P3 read-only plan UX and recovery collision guard corrected (413 CPU PASS)

With actual DGX P3-A read-only READY evidence preserved below, SOURCE-only development continued without service interruption. Global `sequence --plan` now distinguishes staged switch code implemented from actual DGX qualification: `persistent_switch_source_implemented=true`, `persistent_switch_dgx_qualified=false`, and independent stage A/B/C read-only commands while retaining `status=BLOCKED`, no `plan_id` and `operations_enabled=false`. This corrects stale "no persistent switch executor" notice, without authorizing P3 entry or live execution.

The P3 recovery function now performs another Docker GPU-consumer inventory after stopping/removing the failed target and **before restarting the original model**. Unexpected GPU-enabled Docker consumer => `RECOVERY_FAILED` with `RESTORE_FOREIGN_GPU_CONSUMER`; original is not restarted onto another GPU service. CPU tests cover refusal and normal recovery. Host-level GPU processes outside inspected Docker inventory are not fully qualified; neither this patch nor `gpu_exclusivity_verified=false` implies global GPU exclusivity.

**Actual CI on source commit `02bf94c1628828ce22fa338dd5a8e5a0955f9179`:** [push 42170050031](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170050031) and [PR 42170056860](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860) SUCCESS; **413/413 CPU tests, 19 test groups**, no failures. Intermediate fixture serialization failure on commit `d82122f` was corrected; no production GPU calls occurred. P3-A/B/C actual transitions and P1 post-B benchmark remain NOT_RUN. Draft PR still unmerged.

---

## 2026-11-06 — New real DGX P3-A read-only readiness; Flash-Next still active (no P3 execution)

2026-11-06 DGX operator read-only observation: current Flash-Next `qwen38-flash` on :8000/v1, `LIVE_SERVICE_VERIFIED`, served ID `qwen3.8-flash-next`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, exact container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Manifest/API check array 8/8 true, `issues=[]`, `executed=false`; **GPU exclusivity and process ownership remain unverified**, and current identity is not historical rollback proof. `sequence --plan`: `status=BLOCKED` with only `P3_SEPARATE_OPERATOR_ENTRY_REQUIRED` by D-034 (expected), with successful local P2 receipt SHA-256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, evidence path `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`. `stage-a --plan`: `status=READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, source `flash-next`, target `27b`, `plan_id=79be6bf05cb02306ec9155ade317e06c457238de427417ebab8946e35449247a`, expiry epoch `1793943600` (2026-11-06 14:40 KST), target image equal to preserved local Docker image ID, expected target container ID null (not yet created), `executed=false` and `operations_enabled=false`. **This was a plan only, not scoped downtime approval or P3 entry**; plan IDs must be regenerated when stale and must never be reused across stages. No GPU/Docker/service mutation was performed by these read-only queries.

**Current stage:** P2 closed; P3-A `PLAN_READY` but **P3 entry / actual stage execution NOT APPROVED and NOT_RUN**. Only the independent first-stage request for operational approval is eligible for review. Preserve `qwen38-flash`, both model snapshots, Docker image and :8000. Do not auto-run B, P1 remedial benchmark or C. Last provided actual DGX service state remains Flash-Next.

---

## 2026-11-06 — P3 staged persistent switching SOURCE implemented; CPU CI 411/411 PASS; DGX P3 NOT_RUN

Existing D-034 remains binding: P2 actual limited NVIDIA 27B benchmark `BENCH_PASS_RESTORED_VERIFIED` and original Flash-Next `LIVE_SERVICE_VERIFIED` were recorded below; P2 is CLOSED. No P3 live service change has been authorized or executed.

New **source-only** P3 stage-specific adapter `scripts/manager/p3_persistent_switch.py` and Wizard `switch flash-next-27b stage-a/stage-b/stage-c --plan`: A Flash→27B; B 27B→Flash; C final Flash→27B. Each stage has live Docker/Manifest/API identity checks, target ID/label preservation, independent short-lived plan SHA, explicit downtime acknowledgment, stage A separate P3 entry acknowledgment, stop-before-start, port :8000 release, single-GPU Docker guard, private receipt and append-only service journal. Success leaves target model active and never auto-advances. Failure attempts exact source container recovery; recovery-failed journal blocks automatic replay. Older `roundtrip` remains RETIRED/BLOCKED; global `sequence --plan` remains non-executable.

New `scripts/manager/p3_p1_evidence_gate.py` blocks C until local P1 `verify` and `benchmark` PASS receipts are *newer* than stage B, include actual functional and numerical TTFT/latency/tokens/sec proof tied to original Flash-Next image, and actual reviewed resolution of historical `doctor/inventory-plan` rc=3. No fabricated P1 benchmark or rc=3 cause; **P1 REMEDIATION NOT_RUN / NO POST-B EVIDENCE**.

CI after code/Wizard changes: [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168518712) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168524464) **SUCCESS, 411/411 CPU tests, 19 groups** at code HEAD `27728045907a1f2111dc4b8340fbea2cc365ff1d`. CPU simulations include A/B/C successful transitions, target identity change rejection, failure recovery, explicit approvals and P1 acceptance gate; no actual DGX GPU, API switch or downtime. Some intermediate development commits had red CI (syntax and test doubles); these were corrected and preserved in Actions history. CI PASS does not certify production safety.

Read [P3 source operation contract](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md) before read-only planning. Next runtime step requires independent operator approval, actual current DGX preflight and fallback arrangement; P3 stage A/B/C status remains **NOT_RUN/NOT_QUALIFIED** and Draft PR stays unmerged.

---

## 2026-11-06 — Actual DGX P2 benchmark PASS (operator-supplied, supersedes earlier plan-only status)

**P2 COMPLETED within the approved bounded trial scope.** Operator-provided DGX execution output, not independent access to the private report bytes: `BENCH_PASS_RESTORED_VERIFIED`, executed=true, target API ready=true, inference=true, benchmark 3/3 streaming requests (64 max output tokens, concurrency=1, seed=1234), original Flash-Next `RESTORED` without issues, and fresh Wizard post-restore `LIVE_SERVICE_VERIFIED` for `qwen3.8-flash-next`. Original Docker image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. This **supersedes older sections below saying P2 benchmark NOT_RUN**; do not repeat P2/download/build.

Actual client metrics supplied: TTFT P50=0.179349s, P95=28.977990s; E2E latency P50=5.818283s, P95=34.609889s; mean E2E throughput=7.9002 tok/s; mean **client decode proxy**=11.1801 tok/s; mean **prompt-ingest proxy**=246.2744 tok/s. Per-request TTFT 32.177839/0.179349/0.178962s; latency 37.808956/5.818283/5.813945s, each 64 completion tokens. First-request cold overhead hypothesis is NOT confirmed. GPU memory/peak unavailable, engine decode/prefill throughput unmeasured, no extended concurrency/vision/tools acceptance for 27B.

DGX private evidence paths: `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`, `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.json`, `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.target.log`. These are operator-reported paths, not contents independently read by GitHub tools. Source revision `482ca0f3832238542f8f5295dde86b5f22711d80`.

**P2 STAGE CLOSED. P3 NOT STARTED** and not authorized for live changes. D-034 manual order: independent approval Flash-Next→27B (A), independent 27B→Flash-Next (B), resolve P1 doctor/inventory-plan rc=3 and functional/TTFT/tokens/sec evidence on Flash-Next, then independent final Flash-Next→27B (C); expected final 27B active. Old `roundtrip` executor is retired. Source-only P3 engineering is permissible but no GPU/service mutation, no auto progression, no PR merge.

---

## 2026-11-06 — REVISED P3 MANUAL sequence; P2 must STOP, never auto enter P3

User decision D-034 supersedes previous P3 two-cycle roundtrip. **P2 benchmark still NOT RUN** on DGX; previous latest actual DGX only `--plan READY_TO_REQUEST_TRIAL_APPROVAL` with `issues=[]`, and prior first GPU smoke `PASS_RESTORED` plus Flash-Next `LIVE_SERVICE_VERIFIED`. No change to live model. After separately approved actual P2 measured PASS, **terminate P2 workflow** and wait for explicit P3 instruction and a new separate scoped approval.

P3 revised order: explicit operator P3 entry; because P2 leaves Flash-Next running, separately approve **Flash-Next → 27B** to establish 27B source; verify **27B → Flash-Next**; address outstanding P1 issues/redo functional probes and actual benchmark on verified Flash-Next; only then approve **Flash-Next → 27B** and verify 27B as final active model. No phase auto-chaining. P1 pending: historic `doctor`/`inventory-plan` rc=3 causes unresolved, actual numeric TTFT/throughput metrics not supplied (despite earlier P1 smoke and bounded bench PASS). No P1 metrics invented.

Source changes: old `scripts/manager/p3_27b_roundtrip.py` plan/execute now **permanently BLOCKED**; Wizard `roundtrip` route retired. New `./wizard.sh switch flash-next-27b sequence --plan --json` provides read-only manual-entry plan and **never** an executable ID; new persistent P3 service-switch executor not yet implemented/qualified. This change is policy/source-only and does not alter P2's measured benchmark/restore executor. See `docs/P3-MANUAL-TRANSITION-SEQUENCE-20261106.md`.

---

## 2026-11-06 — Actual DGX P2 benchmark READ-ONLY plan READY; P3 prerequisite BLOCKED as designed

Operator ran `./wizard.sh model 27b benchmark --plan --json` on the actual DGX and received `status=READY_TO_REQUEST_TRIAL_APPROVAL`, `issues=[]`, `executed=false`, `gpu_verified=false`, benchmark profile `p2-27b-api-benchmark-v1` (3 requests, 64 max tokens, seed 1234, concurrency 1, model `qwen3.8-27b`, stream). Verified source exact Docker ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`; original image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. The plan ID `2f76c3b03865b6a15a5c2fe8f316231f532fbf8b7fe178ffd00db8383edc3399` expired **2026-11-06 12:20 KST** (epoch 1793935200), and MUST NOT be reused for execution. **This was read-only readiness, not actual P2 GPU benchmark PASS**.

Operator also ran `./wizard.sh switch flash-next-27b roundtrip --plan --json`: `status=BLOCKED`, `issues=["P2_BENCHMARK_RECEIPT_NOT_FOUND"]`, `plan_id=null`, `executed=false`, `cycles=2`. This is the **correct** P3 prerequisite guard; P3 cannot begin until actual approved P2 benchmark returns `BENCH_PASS_RESTORED_VERIFIED` and a private `*.benchmark.json` receipt exists.

**Next**: operator authorizes a fresh Flash-Next service downtime separately. During that maintenance window, regenerate the **new** P2 benchmark plan ID using the read-only Wizard, then explicitly execute with fresh `--approve-plan` and `--ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME`. Any nonempty issues/blocker prevents execution. An approved P2 run interrupts :8000 and must attempt original Flash-Next restoration. Read its actual metrics + evidence and independently verify restored model before any P3 plan/execute. Preserve original Flash-Next until authorized; no GPU test was performed merely by these two plan queries.

---

## 2026-11-06 — P2 bounded GPU benchmark and P3 gated two-cycle trial implemented in SOURCE; DGX NOT RUN

**Priority corrected:** stop feature drift into model inventory/Orcarouter; original target is **P2 27B benchmark, then P3 Flash-Next ↔ 27B verification**. Existing real DGX P2 first-launch `PASS_RESTORED` and latest live `LIVE_SERVICE_VERIFIED` remain valid. P2 timed benchmark **NOT_RUN**; P3 repeated roundtrip **NOT_RUN**; permanent production switch remains unimplemented.

Added `scripts/manager/p2_27b_benchmark.py`, Wizard `./wizard.sh model 27b benchmark --plan --json` and exact-scoped `--execute` route. P2 benchmark plans have a **different ID** from one-shot smoke. Execute reuses the real proven `p2_27b_gpu_trial.execute` original-container lock/restore; measures 3 bounded streaming text prompts, client TTFT/latency, e2e throughput and separate explicitly labeled prefill/decode **proxies** (not engine metrics), best-effort point GPU memory samples (not peak). Actual 27B text benchmark measures yet **not available**. Local private JSON `*.benchmark.json` records final result and fresh Wizard post-restore API identity.

Added `scripts/manager/p3_27b_roundtrip.py` and Wizard `./wizard.sh switch flash-next-27b roundtrip --plan --json`. It **fails closed until a real latest P2 benchmark receipt reports `BENCH_PASS_RESTORED_VERIFIED`**. Its optional separately approved `--execute` reuses the guarded trial executor exactly twice, requiring the original Flash-Next container ID and API service state to be verified after **every** cycle, aborting on failure. This is **two temporary forward-and-return cycles**, NOT a persistent model-switch implementation and NOT automatically qualified without actual DGX evidence. No GPU/service changed by source-only development.

Canonical new instructions: [P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md](../docs/P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md). The next DGX action is **read-only P2 benchmark --plan** after clean fast-forward; use no GPU execute until new explicit downtime approval.

---

## 2026-11-06 — ACTUAL DGX installed-model inventory PASS; legacy Orcarouter confirmed preserved

Operator executed **`./wizard.sh model list --installed --json`** on DGX after pulling the new Wizard. Actual result `status=READ_ONLY_INVENTORY`, `scope=CONFIGURED_CACHE_ROOTS_ONLY`, `service_status=LIVE_SERVICE_VERIFIED`, `active_model_observed=flash-next`, `active_api_identity_verified=true`, `executed=false`, `operations_enabled=false`, `other_cached_repos_truncated=false`, `service_issues=[]`.

The scanner checked `/home/inlc/.cache/huggingface` and `/home/inlc/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`. Registered original NVIDIA Flash-Next revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` has **11/11** indexed nonempty shards and `source_files_present=true` in the default cache; it is also the **only observed active/verified API model**. Registered NVIDIA Qwen3.8-27B revision `482ca0f3832238542f8f5295dde86b5f22711d80` has **3/3** indexed shards and `source_files_present=true` in the default cache, but is not currently serving. Previous actual 27B one-shot GPU trial separately returned `PASS_RESTORED`; scanner's individual `runtime_qualified=false` only means source inventory does not requalify GPU runtime.

**Crucial newly observed fact:** The original `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` revision `3a3b63161c0745390e5270179af42e46efc70799` is **still present** in the legacy `yslab-qwen38-bf16ple-dgx-spark/hf-cache`: **17/17** nonempty indexed shards, tokenizer/config/index true, `issues=[]`, `source_files_present=true`. Its existing `recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2` directory is **also present**. Therefore the source/recipe directory is **not deleted**, and redownload must not be performed merely because Orcarouter is inactive. **NOT** yet established: recipe file completeness/identity, BF16 PLE/MTP build/runtime compatibility, reinstallation feasibility, API functionality or benchmarks. Orcarouter remains inactive and runtime-unqualified.

Four **unregistered snapshot sightings only**, not verified full checkpoints: `maurienne-ai/Qwen3.8-27B-DFlash2-NVFP4-RTNcal` rev `bd7a934213c47a9e7ef69eef36bb3325f47fd1f1`; `RadixArk/Qwen3.8-27B-NVFP4` rev `52d1adc5f38aa5ebf099c29ed7025ba34cfbb854`; `dealignai/Qwen3.8-Flash-Next-ABLITERATED-NVFP4` rev `be794b990578ef3031eccf9f28e675a289a09ee9`; `RadixArk/Qwen3.8-Flash-Next-NVFP4` rev `7b719225242aacd3dbd3f9407468c2ee9a9d2594`. Do **not** automatically register, switch to or delete any of these.

This is actual DGX source-preservation and current-service evidence, **not** permission to move/delete files, switch models, benchmark GPU, or modify the operational Flash-Next container. It supersedes prior `NOT_YET_RUN` references to the installed-model CLI below.

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

## 2026-11-06 — ACTUAL P2 27B GPU PASS_RESTORED; manifest-led Wizard service status is canonical

**Latest actual DGX operator JSON:** one-shot NVIDIA Qwen3.8-27B GPU trial `executed=true`, `target_api_ready=true`, `inference_ok=true`, `trial=PASS`, `restoration={"status":"RESTORED","issues":[]}`, overall `status=PASS_RESTORED`. First real GPU load, bounded inference and normal successful original Flash-Next restoration now confirmed. Original private DGX evidence `/home/inlc/.local/state/blazux-wizard/p2/20261105T230229Z-a4fc14cf8079.json` and `.target.log` exist according to operator stdout; contents **not independently inspected**. Historical older NOT_RUN sections below are superseded by this result; this does not verify full benchmark, MTP, large contexts, tools/vision, permanent switching or failure-mode rollback.

**Service verification decision:** user prefers manifest-based Wizard over manual `docker ps`/`curl`. Implemented `./wizard.sh service manager status --json` to combine `runtimes/service-policy.json`, read-only fresh container/port Manifest and localhost `/health` + `/v1/models` exact expected served model ID in a **single** status response. New `scripts/manager/service_status.py` (source only) status `LIVE_SERVICE_VERIFIED` iff checks all pass, otherwise `BLOCKED` and explicit issues. `inventory`, `health`, `logs` retain individual read-only diagnostic commands. Status does not assert historical rollback provenance or GPU exclusivity outside managed models. **New unified-status command has NOT_RUN on actual DGX**; do not call it PASS until operator executes it.

Next: operator fast-forwards clean branch, runs `./wizard.sh service manager status --json`, expects `flash-next` and `qwen3.8-flash-next` with all checks true. Source code/CI stage and GPU run stage stay distinct. Keep Draft PR #1 unmerged; no further Flash-Next stop/27B restart without fresh explicit approval. Detailed run receipt: [P2-27B-GPU-TRIAL-PASS-20261106.md](P2-27B-GPU-TRIAL-PASS-20261106.md).

---

## 2026-11-06 — Qwen3.8-27B CPU registration PASS; explicit one-shot GPU trial prepared (NOT RUN)

Operator DGX returned **all nine import/registry checks true**, `issues: []`, `status: IMPORT_AND_REGISTRY_PRESENT_UNQUALIFIED`, `modelopt_mixed_cli_name: true`, `schema_version: 2`. These are real restricted CPU-only imports for installed Qwen3.8-27B checkpoint's internal `Qwen3_5ForConditionalGeneration` loader and vLLM ModelOpt mixed precision registry. They do **not** prove CUDA kernels or GPU model load. `nvidia/Qwen3.8-27B-NVFP4` remains the target model; `qwen3_5` is **only** the checkpoint's internal architecture key.

User requested moving to actual GPU startup rather than more source-only gates and provided comparative external references (MiaAI-Lab, NVIDIA DGX forum, eugr/spark-vllm-docker). Key distinction: MiaAI-Lab runs `unsloth/Qwen3.8-27B-NVFP4` with compressed-tensors; operator's pinned `nvidia/Qwen3.8-27B-NVFP4` uses ModelOpt MIXED FP8/NVFP4, so do NOT copy `--quantization compressed-tensors` or alternate images/quantization defaults. eugr supports NVIDIA checkpoint; GB10 community references require architecture-specific NVFP4 kernels, but do not prove this exact local vLLM 0.32 image.

New `scripts/manager/p2_27b_gpu_trial.py` and `scripts/serve_27b.sh --trial-plan` / `--trial-execute` implement **one-shot experimental GPU load and mandatory return to Flash-Next**, not a permanent model switch. Default/read-only plan checks pinned checkpoint, image, current source API identity, exact original container ID and restart policy, host :8000, target name available, no competing GPU-enabled Docker container. The **only** execute path requires the full SHA256 plan ID plus explicit typed `I_ACCEPT_FLASH_NEXT_DOWNTIME` acknowledgment within the approval time window and revalidates live state under local lock. On execution: stop existing `qwen38-flash` (never remove), launch NVIDIA ModelOpt 27B with 8k ctx/one seq/0.70 eager (no PLE/MTP), wait exact API ID, run one bounded inference, save local bounded trial logs, stop/rm ONLY own labeled trial container, docker start ORIGINAL Flash-Next and verify :8000 original served ID. If rollback cannot be proven, report `RECOVERY_FAILED` (manual recovery required); SIGKILL/power loss/Docker faults are not guaranteed to recover. **No DGX GPU trial has run yet.**

Source branch HEAD before handoff docs `ea28b0c0ddbe085782617cc1445c2fcaf613f2a4`; CI run `42124595787` **SUCCESS 354/354 CPU tests, 16 suites**. Draft PR #1 remains unmerged; original operational GPU service untouched by source work.

---

## 2026-11-06 — Actual DGX 27B Python import succeeded; ModelOpt name audit false negative fixed

**Real operator DGX** on branch HEAD `9db92f7` executed `./scripts/temporary/p2-27b-loader-import-audit.sh --plan` (correct local image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, no GPU/ports/weights/changes) and explicit `--execute-cpu-only` in restricted `runc`. The container reported `qwen3_5_module_imported=true`, `qwen3_5_class_present=true`, `modelopt_module_imported=true`, `modelopt_mixed_class_present=true`, `modelopt_nvfp4_class_present=true`. **All actual imports/class surfaces passed.** However `modelopt_mixed_cli_name=false` and `MODEL_OPT_NAME_LOOKUP_FAILED:TypeError` were caused by **our checker** incorrectly calling `ModelOptMixedPrecisionConfig.get_name()` on the class. The installed vLLM 0.32 has an instance method `get_name(self)`, not a static/classmethod. CPU container also printed nonfatal `vllm._C ModuleNotFoundError` and `No CUDA runtime is found` warnings; they do not establish GPU incompatibility or launch success. **No GPU, weights or inference were run.**

Fixed in source commit `0a14f189c4dae61827298fde46f3148d316f8c72`: now obtain `get_quantization_config("modelopt_mixed")` from the vLLM public quant registry and verify class identity against the imported `ModelOptMixedPrecisionConfig`; no instance construction or mis-bound `get_name(self)` call. Three additional tests plus regression for instance-method signature, wrong registry, exceptions; GitHub Actions run `42121160545` **SUCCESS 336/336 tests (16 suites)**. **Updated checker has NOT_RUN on real DGX yet**; actual quant-registry result remains pending, 27B GPU/launch and Flash-Next recovery remain unverified/blocked.

---

## 2026-11-06 — Real DGX after model-specific serve split; CPU-only Python loader import probe prepared

**Actual operator DGX evidence (new):** clean source pull `b1c9b2e..c44aa72`, then `c44aa72..99dde4c` (split `serve.sh` entrypoints into Flash-Next/27B). Operator ran `./wizard.sh model 27b plan --for-action start --launch-preview --json` before the split, then `./scripts/serve_27b.sh --status` and `--plan` **after the split**; both paths returned the expected read-only JSON, no errors. Latest `--status`: exact pinned NVIDIA 27B source/architecture ModelOpt FP8 208 + NVFP4 193, image ARM64 v0.32, `runtime_qualified=false`, six remaining GPU/start/rollback issues. Latest `--plan`: `observed_source.api_identity_confirmed=true`, source container `qwen38-flash`, original source image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, **identical to candidate 27B local image ID**; target `command_preview` includes pinned snapshot `482ca0f3832238542f8f5295dde86b5f22711d80`, `modelopt_mixed`, context 8192, max seqs 1, mem fraction 0.70, eager. Status `BLOCKED`, `executed=false`, `plan_id=null`, `operations_enabled=false`. Original Flash-Next API remains observed and identity-confirmed on :8000. This is **not** 27B GPU/loader/bench/rollback proof.

**New source-only follow-up:** `scripts/manager/p2_27b_loader_import_audit.py` and `scripts/temporary/p2-27b-loader-import-audit.sh` for isolated CPU-only actual installed module imports and `ModelOptMixedPrecisionConfig.get_name() == modelopt_mixed`. Default `--plan` only inspects Docker image; explicit `--execute-cpu-only` uses ephemeral restricted runc/no GPU/network/cache/ports. The new import probe **has not been run on real DGX**. Source commit `834c750fc966f73c885fcfc5d81d054a60ae419e` CI `42112730764` **SUCCESS 333/333 CPU tests**. Even import PASS cannot authorize 27B GPU start.

---

## 2026-11-06 — Model-specific serve entrypoints separated (Flash-Next behavior preserved)

Operator requested model-specific serving files rather than maintaining Flash-Next and 27B launch details in one `serve.sh`.

**Implemented**: the original full Flash-Next implementation lives at `scripts/serve_flash-next.sh` (same configuration/modes/guards and default behavior). `flash` directly calls this file. `scripts/serve.sh` is now a thin backward-compatible dispatcher: no args -> Flash-Next, explicit `flash-next` -> Flash-Next, `27b --plan` (or `--model 27b --plan`) -> `scripts/serve_27b.sh` with source-only preview. `scripts/serve_27b.sh` owns the P2 model-specific entrypoint but **only supports read-only plan/status**; direct GPU --execute/start/switch remains blocked until a verified separate approved runtime transaction. The Flash-Next runner refuses an attempted NVIDIA 27B checkpoint override, so PLE/MTP presets never silently reach 27B.

**CI:** source commit `67a54afc615e51f207f12238e8473200c62a1aad` GitHub Actions run `42111216055` SUCCESS, **325/325 CPU tests PASS** across 16 suites. Original Flash-Next live DGX service was not modified in this development step; no 27B GPU run, service stop/switch or rollback performed. New documentation commit CI to be verified.

---

## 2026-11-06 — DGX pinned 27B quant + image AST PASS; dedicated launch *preview* added

**New actual operator DGX evidence supersedes old checklists:**
- `./wizard.sh model 27b status --inspect-runtime --json` confirmed exact pinned source `482ca0f3832238542f8f5295dde86b5f22711d80`; `quantization_audit.status=PINNED_METADATA_PARSED_UNQUALIFIED`, `producer=modelopt`, `quant_algo=MIXED_PRECISION`, **FP8=208, NVFP4=193, 401 total**, `issues=[]`, CPU metadata only.
- `./scripts/temporary/p2-27b-image-audit.sh --plan` returned immutable local image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, no execution.
- Operator explicitly ran `--execute-cpu-only`: `SOURCE_SURFACES_PRESENT_UNQUALIFIED`, **four of four checks true**: 27B model registry architecture, `Qwen3_5ForConditionalGeneration` class, ModelOpt NVFP4/FP8 mixed algorithms and mixed config classes. Actual installed image source locations: `vllm/model_executor/models/registry.py`, `.../models/qwen3_5.py`, `.../layers/quantization/modelopt.py`. This test ran one CPU-only runc audit container; GPU `false`, launch authority `false`.
- Flash-Next remains observed on port 8000. **27B GPU loading, GPU kernels, API, benchmarks and rollback remain NOT_RUN**. Source PASS does not close those gates.

**New P2 implementation:** `scripts/manager/p2_27b_launch_preview.py` and `./wizard.sh model 27b plan --for-action start --launch-preview --json` implement an entirely read-only 27B-specific candidate argv and live-source API identity preview; **never execute** the candidate `docker run` argv. Initial **unvalidated** settings: `modelopt_mixed`, 8192 context, 1 sequence, 0.70 memory fraction, eager, PLE/MTP disabled. Source commit `ae4490d66d9c1b9306435165a9821253ee6f38d7`, GitHub Actions run `42110115101` **SUCCESS 315/315 CPU tests**. The new docs commit requires its own CI verification.

---

## 2026-11-06 — Exact pinned ModelOpt mixed-precision metadata audit added to Wizard

On the previous real DGX read-only preflight, source is pinned and configuration reports `quant_method=modelopt`, but **layer distribution has not yet been observed**. New SOURCE `scripts/manager/p2_27b_quant_audit.py` now parses only `hf_quant_config.json` in the immutable NVIDIA 27B snapshot, rejects oversized/malformed/unexpected algorithms, reports `MIXED_PRECISION`, exact per-algorithm counts, and adds `quantization_audit` to the existing `status --inspect-runtime` JSON. It does not inspect weights or approve runtime execution. Actual DGX run of this updated command remains **NOT_RUN**.

**Latest source/CI:** `cd63f25f0bf7282ea06dbb13c3499798394322b0` — GitHub Actions run `42065472163` **SUCCESS, 303/303 CPU tests PASS**, including nine additional quantization unit tests. Existing single active model and Flash-Next :8000 unchanged. Further documentation commit requires final HEAD CI verification.

---

## 2026-11-06 — DGX P2 runtime metadata verified; installed-image source audit developed

**New actual operator DGX evidence (2026-11-06 KST):** after clean fast-forward from `e99914c` to `edf0968`, `./wizard.sh model 27b status --inspect-runtime --json` returned `source_files_present=true`, `source_checkpoint_status=SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, pinned revision `482ca0f3832238542f8f5295dde86b5f22711d80`; `Qwen3_5ForConditionalGeneration`, `qwen3_5`, `modelopt`, context 262144, vision config present; host `aarch64`, Docker image ARM64/Linux with base label `v0.32`, local image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. Flash-Next observed running and port 8000 listening; download no longer running. `repo_digests=[]`, `gpu_verified=false`, `runtime_qualified=false`; `status=BLOCKED` with six unresolved runtime/transition gates. This is read-only host evidence, not 27B GPU support proof.

**Source work:** added `scripts/manager/p2_27b_image_audit.py` and `scripts/temporary/p2-27b-image-audit.sh`. Default `--plan` only reads local image ID; explicit `--execute-cpu-only` creates a short-lived, isolated runc container with no GPU, network, port, cache or service changes and AST-parses installed vLLM registry/Qwen3.5/ModelOpt source. Even `SOURCE_SURFACES_PRESENT_UNQUALIFIED` is not a 27B load PASS. GitHub Actions on source commit `acf5d64` PASS, **294/294 CPU tests**, invalid recipe still blocked. New documentation commit needs CI confirmation.

---

## 2026-11-06 — P2 NVIDIA 27B download PASS confirmed; read-only runtime qualification added

**Operator DGX evidence (2026-11-05 KST):** approved `./wizard.sh model 27b download --guided` completed **19/19** files, return code **0**. NVIDIA repo `nvidia/Qwen3.8-27B-NVFP4`, immutable revision `482ca0f3832238542f8f5295dde86b5f22711d80`, checkpoint result `SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, `issues=[]`, `gpu_verified=false`, runtime `NOT_RUN`, evidence `/home/inlc/.local/state/blazux-wizard/p2/evidence/20261105T150433Z-bd8cf46ef5.json`. This **supersedes** older 84%-in-progress and NOT_RUN download notes below; do not redownload without new corruption evidence.

**Current GitHub SOURCE addition:** `scripts/manager/p2_27b_qualification.py` and `./wizard.sh model 27b status --inspect-runtime --json` expose bounded, read-only pinned snapshot/config, modelopt architecture, host ARM64, exact Docker image metadata and actual service inventory, while retaining explicit blockers for unproven vLLM 0.32 loader, mixed NVFP4/FP8 GPU kernels, immutable recipe digest, memory/context and rollback. CPU regression cases added. **Neither a matching image tag nor downloaded files grant startup approval.** The existing Flash-Next on host :8000 remains protected; no GPU start, switch, cleanup or DGX command was run by the source session. Latest GitHub CI verdict requires post-commit check.

---## 2026-11-06 — full P1–P7 Wizard source implemented; P2–P7 adapters to debug

**Operator instruction D-021:** create the entire Wizard now, even if parts cannot yet execute; as actual P2 onward develops, debug/qualify individual backend adapters. Completed GitHub SOURCE:
- `wizard/console.py`: simple 3-choice primary TTY, per-model Continue + all ten actions, service status/health/bounded logs/start/stop/restart/rollback/proxy/gateway, advanced P3/P4/P6/P7 with explicit switch pair and guarded legacy menu.
- `wizard/workflow.py`: unified three-model action matrix, read-only machine `workflow MODEL --json` and `--for-action ACTION`; existing P1 guarded backend and P2 approved exact-revision downloader reused. Fixed a real P1 UX safety issue: never offer/invoke P1 guided start while another managed model is active or the inventory is unknown.
- `wizard/roadmap.py`: seven-stage P1–P7 evidence-scoped acceptance overview, CLI `roadmap --json`. No source-only result counts as GPU/benchmark PASS.
- `scripts/manager/service_logs.py`: bounded, opt-in read-only tail for exactly observed managed service; no Docker mutation, no automatic log upload.
- Added focused CPU regression suites and CI for full console/P1–P7 workflow, P7 dashboard and log limits. Docs/CLI/decisions updated. GitHub PR #1 remains Draft until DGX verification.

**DGX actual state:** user last supplied proof that the exact-revision 27B download began (`Fetching 19 files: 84%`). No later completion, evidence receipt, pinned shard audit, 27B vLLM-0.32 ARM64 start, API bench, P3/P6 switch or recovery have been observed; **do not claim these PASS**. The existing Flash-Next `:8000` deployment and download are untouched by this source-only work. User should not pull/interrupt until the active download exits. SOURCE/CPU CI verdict requires latest HEAD readback.

## 2026-11-05 — Batch A plus read-only service health/switch preview complete in SOURCE

Model-first Wizard UI, legacy-compatible selection CLI and in-flight 27B detection implemented. Additional GitHub SOURCE: bounded localhost `/health`+`/v1/models` API identity probe exposed via `./wizard.sh service manager health --json`, and fail-closed `service_transition_preview.py` attached to model selection if an alternate running model is observed. Preview specifies stop-old → port 8000 free → start-target → verify identity → journal commit and rollback, but **always BLOCKED/plan_id=null** until vLLM 0.32 target runtime, original recovery and approved executor are qualified. Existing P1 runner and 27B guarded downloader remain unchanged. Final CI still requires HEAD check; source-only API/preview tests do not constitute actual DGX execution.

DGX transfer: user reported `Fetching 19 files: 84%` after successful download plan approval. Started only; **no completion or integrity evidence yet**. Do not ask operator to pull new commits or disrupt active download. Existing Flash-Next :8000 remains protected.

## 2026-11-05 — model-first Wizard SOURCE implemented during user-owned 27B download (current)

**Operator DGX evidence:** on branch `feature/recipe-wizard-handoff`, `./wizard.sh model 27b download --guided` accepted a new full plan ID `e7d3ee776b65c3c5e3395fbeff5d0d739ef432028c030df8d604578412570c49` and printed `Fetching 19 files: 84% (16/19)`. This **establishes actual download started**; no process completion, receipt audit/evidence path, 27B vLLM-0.32 startup, GPU benchmark or switching results were supplied. Host preflight observed Flash-Next container `qwen38-flash` Up, bound `:8000`, approx 322 GiB free before download. **Do not recommend `git pull` or interfere with the operator's running download until it completes.**

Operator accepted **D-020 model-first primary UI**: `./wizard.sh` → 1 Select/run model, 2 Service, 3 Advanced, 0 Exit. The TTY selection and `./wizard.sh select 27b --json` share read-only `wizard/quickstart.py` planner. Model choices Flash-Next, NVIDIA 27B, Orcarouter. `service_manifest.py` now observes `qwen38-27b-dl` to suppress duplicate transfers. `runtimes/service-policy.json` registers Orcarouter as an **unqualified placeholder only**. Existing `p1_wizard.py` + P1 API/bench and P2 approved downloader untouched; old CLI aliases remain supported. UI never stops/starts a service by selection, and runtime transition is still BLOCKED until qualified. Definitive plan: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`. GitHub CPU CI verification pending final HEAD; no DGX execution from this coding session.

## 2026-11-05 — P2 guided approval false-positive fixed (source)

Actual DGX operator log: the exact 64-character plan ID `b190c936072038bc55c14c62dd2f9a63e3ddbf5c2e1ebbf0d1710551a7ec21ce` was entered at `./wizard.sh model 27b download --guided`, but execution returned `executed=false` and `PREFLIGHT_CHANGED_REPLAN_REQUIRED`. This **does not** establish that download started. Root cause in source: mutable `free_inodes` (changed by creating the lock/state folder), exact free GiB and Docker human uptime were included in SHA256 fingerprint and changed between approval and locked revalidation. Fixed to hash stable safety-critical identity while still rechecking all capacity/inode/collision conditions after lock. CPU regressions include real directory/lock, uptime/inode/disk drift, changed image and running-state authorization, and low disk fail-closed behavior. Current actual DGX download still `NOT_RUN`; operator must `git pull --ff-only` and use the **new** plan ID from `download --guided`. P1 active service untouched.

## 2026-11-05 — P2 pinned download ready in SOURCE; one-model API policy (supersedes earlier notes)

**Latest user decision:** one active GPU model per DGX; Flash-Next and NVIDIA 27B share host `:8000/v1`. A 27B GPU start requires approved Flash-Next stop → port release → 27B start → verified API → rollback on failure. **No live stop/start/switch is authorized or performed.** Committed `runtimes/service-policy.json` and live read-only `scripts/manager/service_manifest.py`; append-only, atomic, generation-checked `scripts/manager/service_journal.py` is source-only pending qualified executor. `service manager inventory` reports Docker observations with API/GPU verification explicitly false.

**P2 actual download status: NOT_RUN.** NVIDIA 27B was absent from operator-observed `~/.cache/huggingface` at previous HEAD. Official full SHA `482ca0f3832238542f8f5295dde86b5f22711d80` verified from Hugging Face listing. New `scripts/manager/p2_27b_download.py` is a Wizard-backed, exact-plan-approved, no-GPU/no-port download path. Plan requires image ID, >=35GiB free, inode/cache/name/process checks; CLI `./wizard.sh model 27b plan --for-action download --json`, interactive approval `./wizard.sh model 27b download --guided`. The source recipe remains invalid pending vLLM 0.32 loader/image digest qualification. CPU/CI results must be quoted only for the final checked HEAD; no DGX download or benchmark claims. Pinned snapshot audit no longer requires `refs/main`.

## P2 DGX NVIDIA cache absent; Wizard service menu source implementation (2026-11-05)

User-supplied DGX `./wizard.sh model 27b status --inspect-cache --json` after `git pull` to `3f4ef68` returned NVIDIA `nvidia/Qwen3.8-27B-NVFP4` `local_revision=null`, `source_files_present=false`, `indexed_shard_count=0`, `incomplete_blob_files=0`, `issues=[NO_PINNED_LOCAL_SNAPSHOT]`. The earlier RadixArk snapshot does not satisfy this NVIDIA checkpoint. No download has run. New Wizard top-level **service management** menu has a separate guarded `svc` handler; P7 operations remain integrated release acceptance, and 27B gains `download` planning. Both remain source-only/blocked for mutations; they cannot restart/stop the Flash-Next service or launch GPU. See `docs/P2-27B-WIZARD-OPERATIONS.md`.

## P2 operator decision — NVIDIA 27B replaces RadixArk candidate (2026-11-05)

**Current target is `nvidia/Qwen3.8-27B-NVFP4`** per operator instruction. Public NVIDIA model card establishes checkpoint listing and vLLM multi-GPU GB300 example, **not** vLLM 0.32 single-GB10 qualification. Previously supplied DGX read-only inspection returned RadixArk revision `52d1adc5f38aa5ebf099c29ed7025ba34cfbb854`, 3/3 indexed shards, 0 incomplete transfers, zero issues, and a parsed ModelOpt config; this is **historical RadixArk evidence only** and cannot establish NVIDIA cache presence. The Wizard now inspects the `models--nvidia--Qwen3.8-27B-NVFP4` cache and retains fail-closed runtime status. No P2 model download, GPU start, service cutover or cache deletion approved or performed.

## P2 source progress — 2026-11-05 (new session)

GitHub-linked source changes add a bounded, read-only 27B `config.json` inspector to `scripts/manager/p2_27b_inventory.py`: records reported model architecture, model type, quantization method, context length and presence of vision configuration without inferring vLLM 0.32, GPU fit or runtime acceptance. Invalid/oversize JSON is explicitly rejected from `source_files_present`. CPU regression fixtures cover valid, invalid and oversized model config. **SOURCE changes committed; CI must be checked at latest HEAD. DGX/GPU tests NOT_RUN.** No installation, model download, Docker or API changes authorized.

# Current state — active snapshot

## Newest confirmed DGX evidence: P1 API/GPU PASS; P2 source-only (2026-11-05)

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.


## Most recent 2026-11-05 update — baseline vs optional Wizard probes

**Latest operator DGX result (2026-11-05):** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` summary from `--auto-gpu` at `805f8e3e`: source checkpoint and Hybrid are both READY, `source_issues=[]`, `hybrid_issues=[]`, 11 indexed source and Hybrid shards resolved, `api_model_ids=["qwen3.8-flash-next"]`, verify and benchmark plans each READY, yet **verify action returned FAIL** and benchmark BLOCKED by verification gate. Original console suppressed the Wizard's failure evidence location because it parsed the JSON outcome only on returncode 0, even though Wizard writes evidence for returncode 2. This is an actual attempted API/GPU verification with FAIL outcome, not evidence of a broken default Blazux model. Exact failing subprobe/error still unconfirmed until raw report is examined.

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

**SOURCE/CI validation (not DGX):** `391a2844f4c8549e282eae3e266806c89801ad1a`, GitHub push and PR checks 2/2 SUCCESS, each 15 manifest + 10 inventory + 13 launcher + 1 mode + 102 P1 + 32 router = **173/173 CPU tests PASS**. Real DGX execution against this fix has NOT_RUN; prior verify FAIL remains unresolved until this new code runs.


**Snapshot written:** 2026-11-05 (KST) · **Status:** `WIZARD_P1_P7_ROUTER_SOURCE_IMPLEMENTED / P1_GPU_NOT_VERIFIED` · **Implementation:** Flash-Next default port 8000, N2 read-only Inventory and Wizard doctor/plan; **GPU:** `VERIFY_ATTEMPTED_FAIL`; new source fix `NOT_RUN_ON_DGX`.

## Latest DGX checkpoint update and P1 diagnostic blocker (2026-11-05)

**DGX operator update, 2026-11-05:** The operator explicitly confirms the NVIDIA Flash-Next download has finished. Their submitted terminal output after `git pull` to `dea7c5aa183da770b6b467288f2f6eedf8e94946` shows `bash scripts/temporary/p1-post-download.sh` produced report `/home/inlc/blazux-p1-reports/20261105T052545Z-1e6ec592/result.json`; current branch and clean tracked worktree checks PASS; no setup process found in the process scan. HTTP `/health` and `/v1/models` command exit codes are 0 **but actual served model ID was not included in the console summary**. Wizard doctor and inventory plan returned exit code 3; both P1 verify/benchmark plans BLOCKED: `checkpoint_downloading_or_incomplete`, `hybrid_not_prepared_or_incomplete`; no Wizard GPU/bench requests executed. The `checkpoint_downloading_or_incomplete` string is a **generic validation failure**, not proof that the download continues. The apparent mismatch needs read-only evidence before any setup, repair, download, switch or deletion.

**Diagnosis implementation validation:** SOURCE/CPU CI verified at `4c0041dd230e2abe22ba8379aca74068933ecece`: GitHub push and PR both SUCCESS, each **138/138 CPU tests PASS** (15 manifest + 10 inventory + 13 launcher + 1 executable-mode + 67 P1 + 32 Wizard router). The earlier `eb759ad` source attempt failed its tests because the optional new diagnostic key was absent from an old fake fixture; fixed in `4c0041d` without changing runtime assets. Real DGX evidence still pending.

**New read-only diagnosis:** `scripts/temporary/p1_cache_diagnosis.py` is called from `p1-post-download.sh`. It records `refs/main`, `refs/master`, actual snapshot and Hybrid file issues, remaining `.incomplete` names count and strict P1 Wizard audit. Source/CI evidence is separate; it cannot claim the weights actually need downloading. No automatic repair. Next action is operator `git pull --ff-only` and a single `bash scripts/temporary/p1-post-download.sh --inspect-only`; review `cache_diagnosis` and `checks.models.stdout` before planning any GPU test.

## Latest root-cause split: Blazux default support vs Wizard regression

**2026-11-05 P1 regression analysis:** NVIDIA's default `nvidia/Qwen3.8-Flash-Next-NVFP4` is supported by Blazux. The official `fc694b5` snapshot distributes `model.safetensors.index.json` (~31.3 MB) and `tokenizer.json` (~12.8 MB). Our new P1 audit erroneously rejected an otherwise-valid index above 16 MiB; code changed to a bounded 64 MiB maximum. **However the operator's specific issues** `model.safetensors.index.json` and `tokenizer.json` arise at the initial `_good_file` stage, *before* parsing/size checks. Thus the artificial size cap does not by itself explain the reported failures. The Hybrid marker exists, but Hybrid `tokenizer.json` also fails. Do not conflate claimed download completion with all snapshot symlinks resolving correctly; investigate metadata file existence, symlink resolution, size and repository containment first.

**Mitigation:** source commit `66c6c448c1922f958886fa4696c403a4b6227685` passes 145/145 CPU tests/job in 2/2 GitHub CI checks; **DGX field-level metadata evidence still pending**. Next operator use is a single `scripts/temporary/p1-post-download.sh --inspect-only` after Git Pull. No active model/container/cache mutation.

## 2026-11-05 — Blazux metadata-symlink parity / P1 GPU approval update

**Operator DGX facts (2026-11-05):** The latest post-download diagnostic returned `api_model_ids=["qwen3.8-flash-next"]`, `refs/main=fc694b54fb0174e0913e6adf86691ef85a4ead47`, 0 incomplete HF blobs, a source index and tokenizer that are **existing nonempty symlinks whose targets resolve outside the model repository**, and a Hybrid tokenizer with the same layout. The Hybrid index is a normal 31,907,813-byte file and the `.prepared` marker exists. These observations show the previous `TARGET_OUTSIDE_REPOSITORY` reason is a **new P1 checker policy stricter than Blazux's original `os.path.exists`-based policy**; they do not establish that any metadata is missing. Previous plans were blocked before actual GPU verification or benchmark. The user explicitly allows non-disruptive GPU compute tests to run without separate per-step approvals, provided the actual target service is confirmed. The presence of an API response means some server is listening; do NOT assume there are literally no processes running or stop/replace any service.

**Implementation:** P1 asset audit now accepts existing nonempty external metadata symlinks for just `model.safetensors.index.json` and `tokenizer.json`; referenced weight shards still cannot escape the model repository. Diagnostic reports `p1_metadata_link_compatible` and target size. The one-command temporary runner gets `--auto-gpu` for verify → benchmark, *with exact fresh Wizard plan IDs passed internally and independently rechecked*. No model lifecycle actions added. **SOURCE/CI verification:** commit `0063b0e004902408f980c155076c098d49d4569e`, 2/2 GitHub Actions SUCCESS, **155/155 CPU tests PASS in each job** (15 manifest + 10 inventory + 13 launcher + 1 mode + 84 P1 + 32 router). **Actual host GPU/API tests remain NOT_RUN** pending operator's new bundle output.

## Confirmed user goal — Wizard-first, P1 through P7

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

**Current P1 exit gate:** Wizard handles preflight → pinned recipe/image/checkpoint verification → explicit plan/approval → setup/prepare → model serve → /v1/models + reasoning/tool/vision smoke → reproducible benchmark (throughput, TTFT, peak resource, seed/config) → evidence export → safe failure/recovery. No GPU/benchmark exit claim is permitted before real DGX measurements.

**CI readback:** At `017319a5394155797bcb7e5c933ccef35080d669`, two GitHub Actions `manifest` jobs succeeded, 39/39 CPU tests per job (15 manifest + 10 inventory + 13 launch + 1 executable-mode). This is **CI PASS only**, not P1 acceptance. Actual HEAD must still be fetched per session.

## Repository/branch tracking

| Item | Last verified state |
|---|---|
| New fork | `kjlee-inlct/qwen3.8-Flash-DGX` |
| Upstream `main` baseline | `b0aa8b77604139557169387b2fa8386355d8b651` |
| Fork `main` baseline at branch creation | `b0aa8b77604139557169387b2fa8386355d8b651` |
| **Active work branch** | `feature/recipe-wizard-handoff` — created from fork `main` |
| Parallel Orcarouter branch | `feature/orcarouter-bf16-adapter@620598c30cfe3521af99a935caf0baf5b83556d8` (as last checked) |
| Parallel Orcarouter design | `docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md` on the parallel branch |
| Old Preview repository | `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark`; frozen preservation, historic `feature/blazux-phase6-runtime-gates@2e6a5794b0fe282ae4bf6f4852acd919fea6d55a` |
| New branch exact HEAD | **Read actual GitHub branch HEAD**. Do not embed a file's own eventual HEAD as authoritative; the branch commit changes when this file changes |
| Draft PR | [#1 — recipe wizard roadmap and handoff](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) against `main`; open, not merged |
| PR CI | New 2026-11-05 implementation commit 7e8f4a1: manifest 15/15 PASS, Inventory 10/10 PASS; **4 launcher tests FAIL (exit 126)** because executable mode lost. Follow-up commit restores script modes and adds regression; **recheck HEAD CI**. Prior verified HEAD `017319a` has two successful CI jobs (39/39 CPU tests each); live HEAD check required each session. |

## Operational environment — protect; verify fresh

**User report 2026-11-05:** prior operating services have all been deleted; requests Blazux default NVIDIA Flash-Next on the **same external :8000/v1 API port**. This is a user-reported change, not yet independently observed with current DGX Docker/ss/df commands. Historical prior-session values (not rechecked):
- Container `qwen38-flash-orca-uncensored-bf16-mtp`.
- Container ID `3fc5a3d5be1d52595602287acd87895220219bad050484251ac0408a163ffc45`.
- Original image ID `sha256:b0984c4b724b6f8c0745acb654994e1bd3a6c50b75c2c76078f1bfd6b395f39a`.
- OpenAI-compatible `:8000/v1`, model ID `qwen3.8-flash-next-orca-uncensored-bf16-mtp`, existing external clients.
- Legacy workspace `~/Workspace/llm/blazux-phase6-gates`, target new workspace `~/Workspace/llm/blazux-orcarouter`.

**Actual current running/stopped status, capacity, local Docker images, model snapshots and ports: `NOT_OBSERVED_THIS_SESSION`.** No stop/delete/launch performed by this development session. Do not infer that port 8000 or container name is free just because previous services were reported deleted.

**Target default service source configuration:** `MODEL=nvidia/Qwen3.8-Flash-Next-NVFP4`, `MODE=hybrid`, `MTP=2`, `YARN=1`, `CTX=500000`, `NAME=qwen38-flash`, `PORT=8000`, served model `qwen3.8-flash-next`, Docker internal 8000. This is desired/source state, **not a running API**. Existing Orcarouter model ID is not an alias for this different checkpoint.

**P1 checkpoint download (2026-11-05 11:46 KST, USER_REPORTED):** `nvidia/Qwen3.8-Flash-Next-NVFP4` is **DOWNLOAD_IN_PROGRESS** on the user's machine. This is **not** independently observed on DGX and has no verified completion percent, downloaded bytes, checkpoint revision, sha256, download command or cache path. **DOWNLOAD_COMPLETED=NOT_VERIFIED**, **HYBRID_PREPARED=NOT_VERIFIED**, **SERVICE/API/BENCH=NOT_RUN**. This session has not started, stopped, retried, removed or modified the download. Do not run a second download, `./flash setup default` (could download/build and mutate cache), hybrid preparation, model launch or cleanup while a write may still be in progress. Continue with P1 Wizard implementation and mock CPU tests independently of download, and inspect completed snapshot/index/shards after the user reports completion.

## New evidence and P1 Wizard source batch

**2026-11-05 operator-provided DGX terminal log (not directly observed through an SSH tool):** GB10/aarch64, Docker 29.6.2, 121 GiB unified memory (117 GiB available then); read-only Wizard Inventory showed no host :8000 collision and no `qwen38-flash` container, and initially 580,134,281,216 bytes free. The existing OpenWebUI and Portainer containers were running; preserve both. `./flash setup default` finished building `qwen38-flash-dgx:v0.32` (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`). The final log line showed **model download 9/25 = 36%**, NOT completed weights/Hybrid. The user's shell also entered `./flash serve default`, `./flash wait`, `./flash test` after setup, so these may run automatically after download/preparation. Do not compete with, modify or restart this running operator setup chain. Port availability and download progress can change after the log timestamp.

**New P1 SOURCE implementation at `c625a49276272e90d19ab6367f580a0230754890`:** `wizard/p1.sh`, `scripts/manager/p1_assets.py`, `p1_wizard.py`, `p1_bench.py`, new CPU tests and CI coverage. Wizard supports read-only inventory/snapshot/image proof, deterministic plan SHA, explicit per-action approval, guarded Hybrid prepare/start/wait, API health/model/text/tool/vision probes, bounded SSE benchmark and JSON evidence. **SOURCE IMPLEMENTED, CPU CI 2/2 PASS (80/80 per job), DGX Wizard/API/bench NOT_RUN.** It never automatically runs `setup`, downloads, deletes containers or caches or switches services.

## P1–P7 unified Wizard architecture (2026-11-05)

- User requested **build the entire Wizard navigation/CLI framework up front**, then incrementally connect and debug real P1–P7 model/runtime adapters. One stage file per menu: `wizard/menus/models/`, `switching/`, `storage/`, and `operations/`, shared `wizard/menus/common.py`, dispatcher `wizard/main.py`, executable root `./wizard.sh`, legacy `wizard/p1.sh`.
- `./wizard.sh` offers the interactive stage menu. The same handlers support direct noninteractive CLI, `--stage`, `--action`, `--json`, `--dry-run`, `--execute`, `--approve-plan`. The P1 adapter reuses `p1_wizard.py` and current exact-plan approval. P2–P7 have typed source-only status/plan interfaces; **execution remains hard-BLOCKED** until each model adapter, recipe, GPU evidence and rollback gate is actually implemented.
- Initial modular source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`: 2 GitHub CI checks SUCCESS, **101/101 CPU tests per job** (80 previous + 21 router tests). Follow-up full source/docs commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b`: GitHub CI **2/2 SUCCESS**, **103/103 CPU tests per job** (15 manifest, 10 inventory, 13 launch, 1 script mode, 41 P1, 23 Wizard router). No actual DGX actions performed by this batch.
- `./wizard.sh p1 status --json` and `./wizard.sh p1 plan --for-action verify --json` are read-only. `./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json` returns BLOCKED until P3 qualifies. No model switching or deletion feature was secretly enabled.
- **Current DGX source-of-evidence remains** the prior user-supplied log: image built, Flash-Next download 36% last observed, queued original setup/serve/wait/test; current live service still unverified. Do not update the live worktree while that shell chain may be running. See `docs/WIZARD-CLI-CONTRACT.md`.

## Descriptive Wizard menus, grouped by capability

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

**Source evidence:** `571e1c204d76bcb66b9e02cb1315ac775013a130` refactor, GitHub Actions push/PR **2/2 SUCCESS**, **112/112 CPU tests per job** (15 manifest + 10 inventory + 13 Flash launch + 1 script mode + 41 P1 + 32 router). No real DGX model operations performed or authorized by this rename.

## Temporary one-command DGX P1 handoff workflow (D-016)

- New `scripts/temporary/` is the canonical place for **single-invocation, short-lived, Git-committed operator bundles**. `p1-post-download.sh` dispatches `p1_post_download.py` with source-safe diagnostics → explicit independent Wizard verify/benchmark approvals → JSON evidence collection. `--inspect-only` is safe and can run unattended; on a TTY, each real action requires the full current 64-character plan hash. Script never calls `./flash setup`, downloads, starts/stops a service, removes images/cache, changes the active worktree or performs `git pull`.
- Operator must complete the **already entered** original `setup/serve/wait/test` shell chain **before** Git Pull; do not infer from the old 9/25 download log that current operations have finished. Operator local entrypoint: `git pull --ff-only origin feature/recipe-wizard-handoff`, then `bash scripts/temporary/p1-post-download.sh` (interactive) or `... --inspect-only`. Non-TTY with no explicit plan hashes executes only inspection. Logs stored with restricted permissions under `~/blazux-p1-reports/`, outside Git/HF cache. Wizard-generated evidence remains under `~/.local/state/blazux-wizard/p1/`.
- This code is **SOURCE+CPU CI verified at `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b` (2/2 jobs SUCCESS, 131/131 tests/job); actual DGX/API/GPU/bench still NOT_RUN pending operator evidence**. 27B/Orcarouter runtime phases remain gated; P2–P7 are not executable. See `scripts/temporary/README.md` and `handoff/OPERATING-RULES.md#r1d--git-tracked-temporary-script-batches-for-user-operated-dgx-d-016`.

## Stage matrix

| Stage | Source/plan | CPU/CI | DGX/GPU | Release |
|---|---|---|---|---|
| P0 inventory + recipe/wizard architecture | `N1 schema + N2 inventory + default 8000 SOURCE_IMPLEMENTED`; N3 doctor/plan partial | N1 15 + N2 10 CPU PASS at 7e8f4a1; launch 4 FAIL from permissions; **CI_RECHECK_REQUIRED** after mode fix | `NOT_RUN` | `NOT_APPLICABLE` |
| P1 Flash-Next **Wizard** implementation + DGX bench | `WIZARD_SOURCE_IMPLEMENTED / CI_VERIFY_REQUIRED` | Existing 39/39 previous PASS, new P1 CPU suite 41/41 PASS; total 80/80 CPU tests PASS per CI job (2 successes) | `IMAGE_BUILD_USER_LOG_PASS`, download last seen 36%; **Wizard GPU/API/BENCH NOT_RUN** | `BLOCKED` |
| P2 27B **Wizard** implementation + DGX bench | `PLANNED/COMPAT_UNKNOWN` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P3 Flash-Next ↔ 27B **Wizard** switching/rollback | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P4 Flash-Next **Wizard** optional removal, only if capacity requires | `PLAN_ONLY/EXACT_APPROVAL_REQUIRED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P5 Orcarouter-Flash-Next **Wizard** implement + DGX bench | `PARALLEL_DESIGN_ONLY` | `NOT_RUN_THIS_FORK` | `NOT_RUN` | `BLOCKED` |
| P6 Orcarouter ↔ 27B **Wizard** switching/rollback | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |
| P7 **Wizard**/service/proxy/gateway/storage operations acceptance | `PLANNED` | `NOT_RUN` | `NOT_RUN` | `BLOCKED` |

**Outstanding historic release blocker:** same-checkpoint strict max logprob delta `<=1e-4` not satisfied in old Preview baseline, therefore do not claim Orcarouter numerical qualification.

## Current deliverables

- `docs/MODEL-RECIPE-WIZARD-PLAN.md` — stage roadmap and architecture.
- `docs/MANIFEST-CONTRACTS.md` — manifest schema intent, switch/rollback/deletion gates.
- `handoff/*` — persistent entrypoint, rules, decisions, evidence, action list and starter prompt.
- N1 SOURCE IMPLEMENTED: schema, bounded YAML validator, intentionally invalid 27B candidate, synthetic fixture, 15 CPU tests, new GitHub Actions CPU workflow. See schemas/recipe.schema.json, scripts/manager/manifest.py, recipes/, tests/test_manager_manifest_cpu.py.
- Default Blazux `flash` + `profiles/default.env` + `scripts/serve.sh` now target host port 8000 and refuse implicit Docker name replacement. The built-in model is NVIDIA Flash-Next. This path requires image/model assets and explicit operational go-ahead on DGX.
- `scripts/manager/inventory.py` and `wizard/00-doctor.sh`/`10-plan.sh` provide read-only Docker/ss/disk/cache inspection. N3 is partial (no interactive or execute path).
- No pinned, launchable **manifest**; no service controller, proxy/gateway or 27B runtime adapter. Synthetic recipe SHA values are fake fixture data.

## Blockers / approvals

- Need fresh read-only DGX inventory **execution** before operational choices; the code now exists, but DGX observations do not.
- Need vLLM 0.32 source check for Qwen3.8-27B architecture, quantized `lm_head`, GDN, tokenizer and speculative support. SGLang is excluded.
- User requested implementation for Flash-Next on port 8000; no local GPU/model loading was performed and no command was executed against DGX. Obtain scoped operator confirmation and preflight evidence before actually running setup/serve; explicit deletion approval remains required for P4.
- Need plan for sufficient free disk. Do not delete existing images/cache or checkpoint automatically.

## Immediate dependencies and next safest actions

1. Verify new GitHub Actions CPU checks on `c625a492…`, remedy any failures and preserve failure evidence.
2. Let operator's existing `./flash setup default` download/Hybrid preparation and queued `serve/wait/test` commands finish **without restarting or changing the worktree mid-run**. Once done, use `bash wizard/p1.sh status`; if container is already running, do not rerun `start`.
3. Obtain fresh Wizard `plan --for-action verify`, explicit action approval, run Wizard API text/tool/vision verify; then separately plan/approve a bounded 3-request benchmark and save local JSON evidence. Do not claim P1 PASS until real DGX data proves it. P2 remains next after P1.

## Immediate next actions

1. **P1 Wizard end-to-end implementation first:** add guided/noninteractive `prepare/serve/verify/benchmark/evidence` flow, approvals, idempotent state + fail-closed plan with mock CPU tests. Existing `doctor/plan` are only partial; no launch without gated operator action.
2. Read-only DGX `wizard/00-doctor.sh` and `./flash doctor default`; establish current port 8000 availability, checkpoint/image provenance, HF cache mounts and disk capacity. No claims of service running until observed.
3. After scope-specific operational go-ahead and rollback plan, execute **P1 via Wizard** on DGX, collect actual API/benchmark evidence, then advance to P2 (27B Wizard), not directly to Orcarouter.

See [NEXT-ACTIONS.md](NEXT-ACTIONS.md), [EVIDENCE-LEDGER.md](EVIDENCE-LEDGER.md) and [../docs/MODEL-RECIPE-WIZARD-PLAN.md](../docs/MODEL-RECIPE-WIZARD-PLAN.md).
