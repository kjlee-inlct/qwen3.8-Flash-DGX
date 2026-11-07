## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

**P3-G actual downtime authorized, execution NOT YET observed.** Read `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`. Existing `scripts/temporary/operational-switch-acceptance.sh` provides one-switch real TTY trial, separate four exact operator acknowledgements and new SHA per direction. No auto-chain; no P3 A/B/C replay, no Flash reinstall or production enable. First trial target flash-next (current model 27B), inspect evidence, then separately target 27b. Evidence currently D read-only pass, E draft-only match, F local 144 PASS, G preview PASS.

---

## 2026-11-07 — THIRD ACTUAL DGX P3-D READ-ONLY PASS; P3-E FP8-HYBRID SOURCE DRAFT

**Actual operator evidence:** Third DGX batch after fast-forward to `1b785c6`: normal `--run` reported D no visible socket PIDs but E `DRAFT_REVIEW_REQUIRED`, F local **136/136 CPU PASS**, G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`. Operator then explicitly ran `sudo -v` followed by `--run --sudo-ss`: **P3-D READ_ONLY_PASS**, both IPv4+IPv6 :8000 `docker-proxy` PIDs (2051487,2051502) independently attributed to canonical active 27B; GPU compute PID 2051842 verified. Overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`, `blocked_stages=[]`, `acceptance_complete=false`; no service mutation or real G transfer. **P3-E** pinned NVIDIA `fc694b54fb0174e0913e6adf86691ef85a4ead47-fp8hybrid` derivative prepared/view files verified; canonical reinstall recipe NOT registered. Legacy Flash cache writable; source metadata and vLLM flags preserved. Evidence `docs/P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md`.

**NEW SOURCE P3-E DRAFT (UNRELEASED):** `recipes/qwen38-flash-next.runtime.draft.json` is `launch_allowed=false`, `register_as_runtime_recipe=false`, not linked into service-policy, no Flash install adapter/executor. `scripts/manager/flash_recipe_review.py` checks versioned pinned Flash 500K/Yarn/MTP2/native tools/image/env/template/mount *documented fields only*, returns `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` or explicit field differences. `P3-E.source_draft_field_review` added to single-script report. P3-E stays DRAFT_REVIEW_REQUIRED; direct live DGX comparison of new code still **NOT_RUN**. CI [42373758262](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42373758262) **854/854 CPU/Fake-DGX PASS / 38 groups**, source only. Full runbook `docs/P3-E-FLASH-FP8HYBRID-SOURCE-DRAFT-20261107.md`.

**Next:** read-only `--run --sudo-ss` batch to inspect E draft comparison, then review remaining host env/mount/image provenance. Separate operator-approved real Flash install and G switch/rollback acceptance required; `PRODUCTION_EXECUTION_RELEASED=False` remains. P3-A/B/C closed, 27B unchanged, P4 optional, P5/P6/P7 queued.

---

## 2026-11-07 — SECOND ACTUAL DGX D–G BATCH + PINNED FP8 HYBRID / HIDDEN SOCKET PIDS

Actual operator DGX batch (**read-only; no model changes**) after previous source fixes: **P3-D BLOCKED** because `ss` showed BOTH IPv4 0.0.0.0:8000 and IPv6 [::]:8000 LISTEN but no process PID; Docker reported only running `qwen38-27b` as GPU/8000 port owner, NVIDIA compute PID 2051842 verified to active 27B. **P3-E BLOCKED** because the observed preserved Flash checkpoint was pinned NVIDIA source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` plus **`-fp8hybrid` local prepared variant**, not a different HF revision; canonical Flash reinstall recipe still unqualified. Flash /hf mount observed writable and legacy argv preserved. **P3-F PASS 128/128 actual local CPU tests. P3-G preview PASS**, current Docker ID and VERIFIED/COMMITTED journal; actual transfer/rollback NOT executed. Overall exit=3, acceptance_complete=false.

Subsequent SOURCE fix: E now recognizes only exact pinned NVIDIA source revision plus `-fp8hybrid` prepared view and verifies `.prepared`/essential files read-only; no recipe promotion. D now permits ONLY operator-selected `--sudo-ss` to run `sudo -n ss` (no prompt; no sudo by default) and independently reverify unchanged socket set and PID provenance. Unknown PID always BLOCKED. CPU CI [42371861344](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371861344) **846/846 PASS / 37 groups**, SOURCE-ONLY, actual DGX rerun pending. Full evidence `docs/P3-D-G-SECOND-DGX-PID-HYBRID-DIAGNOSTIC-20261107.md`. No P3-A/B/C replay, no production switch release.

---

## 2026-11-07 — CURRENT P3-A-G TRACKING

The user adopted **P3-D/E/F/G** as formal continuation of historical P3-A/B/C (all already passed, no replay). Read `docs/P3-D-G-UNIFIED-WIZARD-DRAFT-ACCEPTANCE-20261107.md` first for each gate and local `bash scripts/temporary/p3-d-g-acceptance.sh --run` automatic CPU + read-only DGX judge. D unknown process visibility is BLOCKED rather than invented PASS; E Flash canonical recipe unqualified until reviewed, F CPU-only does not release executor, G preview does not execute a real switch or rollback. P4 remains optional, then P5/6/7 as before.

---

## 2026-11-07 — LATEST DGX ACTUAL READ-ONLY ACCEPTANCE: CURRENT-ID SWITCH PREVIEW PASS

Read `docs/WIZARD-27B-OPERATIONAL-PREVIEW-DGX-PASS-20261107.md` for the second operator DGX read-only report after pulling 4189a79: canonical 27B `diff=[]`, `advisories=[]`; ordinary 27B -> preserved Flash-Next switch preflight `READY_FOR_OPERATOR_REVIEW_ONLY`, `issues=[]`, current IDs and source/target lineage validated; service `LIVE_SERVICE_VERIFIED`. **This is a PREVIEW PASS only**, not GPU exclusivity or port ownership and not actual model switch/rollback acceptance. Code CI 814/814 PASS. Never treat a preview plan hash as execution approval.

---

## 2026-11-07 — LATEST DGX READ-ONLY evidence and current-ID-aware switch code

Operator's actual DGX post-pull Wizard: 27B `diff=[]`, `issues=[]`, API `LIVE_SERVICE_VERIFIED`, container ID `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`; cache host `/home/inlc/.cache/huggingface` mounted `/hf:ro`. New source fixes ordinary switch stale P3 Docker ID assumptions, with qualified canonical 27B provenance and explicit optional read-only host cache comparison. CI 42367665200 SUCCESS: 814/814 CPU/Fake-DGX tests (36 groups), no actual DGX mutation. Start with `docs/WIZARD-27B-LIVE-DRIFT-CURRENT-ID-20261107.md`, `handoff/CURRENT-STATE.md` and `handoff/NEXT-ACTIONS.md`. Production release gates unchanged False; historical P2/P3/cleanup real evidence preserved.

---

## 2026-11-07 — LATEST SOURCE-ONLY Wizard lifecycle implementation

New generic 27B recipe drift comparator, read-only Wizard lifecycle CLI and interactive menu option 7, and guarded container-only lifecycle/rollback scaffold were implemented on feature/recipe-wizard-handoff. GitHub Actions CI 42355750124: **799/799 CPU/Fake-DGX PASS (36 groups)**. No DGX service mutation was authorized or performed; production dispatch remains hard-blocked. Read docs/WIZARD-LIFECYCLE-SOURCE-IMPLEMENTATION-20261107.md and newest entries in CURRENT-STATE.md / NEXT-ACTIONS.md for source-vs-real status and remaining blockers. The previously recorded canonical live 27B and P3-C evidence below remains historical, not a fresh live probe.

---

## 2026-11-07 — HANDOFF DOCUMENT AUDIT / NEXT CONVERSATION READY

The user starts the next development phase in a separate conversation. **Audit verified all 8 handoff docs, 12 implementation docs and 5 recipe/manifest/benchmark indices exist (25/25), plus both published benchmark collection directories and current source/evidence files.** The pre-audit HEAD `9ec7420b74369e7a76785577dc543f9dafb8897d` had GitHub Actions run `42352654468` SUCCESS, **757/757 CPU tests in 34 groups**. This CI is source-only. New documentation commits advance HEAD; inspect GitHub afresh.

A new **complete standalone** prompt is in `handoff/START-NEXT-WIZARD-LIFECYCLE-20261107.md` and prominently at the top of `handoff/SESSION-START-PROMPT.md`; older prompts below are ARCHIVED / superseded. Missing-document/staleness audit: `docs/HANDOFF-DOCUMENT-AUDIT-20261107.md`. Next implementation contract: `docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md`.

**Latest actual DGX:** canonical NVIDIA 27B native-tool recipe, 3/3 benchmark v2, Open WebUI Native user-confirmed PASS, two old diagnostic containers removed via verified Wizard manifest cleanup; original `qwen38-27b` runs at :8000 with served `qwen3.8-27b`, Flash container stopped, Open WebUI/Portainer running. P3-C historical PASS/CLOSED, P8 conditional migration ticket INACTIVE. Do not restart the old P2 Tool HTTP-400 diagnosis; it was resolved. Old original 27B Docker container IDs recorded in P3 stage receipts remain HISTORICAL. `PRODUCTION_EXECUTION_RELEASED=False` for main Wizard generic switch; post-ID-change real guided switch/recovery acceptance still open.

**Next target:** general Wizard lifecycle/recipe-diff detection at install/start/restart/switch, scoped container remove/reinstall/recreate with fresh approval, new runtime receipt and rollback. No global deletion prohibition on canonical 27B or Flash. No live DGX mutation is authorized by this documentation step. The canonical `recipes/qwen38-27b.runtime.json` file's exact SHA is tied to current approved benchmark pointer: do NOT silently edit this file to fix text/metadata. Preserve old P3/bench receipts, images/caches, vLLM 0.32, one GPU model, port 8000, Draft PR #1.

---

## SUPERSEDING VERIFIED STATE — 2026-11-07, AFTER DGX REAL ACCEPTANCE

**LATEST FACTS override older diagnostic/HTTP-400/source-only text further down.** The initial NVIDIA 27B API HTTP 400 and absent native parser flags were RESOLVED via a user-approved RECREATION of the canonical `qwen38-27b` from pinned `recipes/qwen38-27b.runtime.json` (vLLM 0.32.0, modelopt_mixed, port 8000, `qwen3_coder` / `qwen3` / exact NVIDIA Jinja). Actual DGX native `tool_calls`, tool result continuation, streaming, normal chat, benchmark v2 **PASS** (3/3, mean client E2E 10.957 tok/s, p50 TTFT 0.165412 s), and Open WebUI Native **user-confirmed PASS**. Original old container's verified stopped backup was deleted after full success; new canonical `qwen38-27b` is operational. P3-C one-off already REAL PASS/CLOSED; old P3 Docker IDs are historical, not current execution identity.

Wizard manifest cleanup then actually removed the two *stopped historical test containers*, `qwen38-27b-failed-6d9ede0904c2` and `qwen38-27b-native-tools-v1`. Live `cleanup --execute` and independent `cleanup --status` returned `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, both absent, active canonical 27B preserved; `service manager status --json` returned `LIVE_SERVICE_VERIFIED` with API `qwen3.8-27b` at :8000. The recorded cleanup was completed, NOT a pending removal. `qwen38-flash` remains stopped; Open WebUI and Portainer remain running.

**Next work is NOT P2 native-tool HTTP-400 troubleshooting.** It is general Wizard model lifecycle / recipe diff-aware install, removal, reinstallation and same-name recreation, current-Docker-ID-aware model switching and independent production release acceptance. Canonical 27B and Flash are removable/reinstallable upon independently approved actions; no global deletion ban. Such generic lifecycle functionality and the post-container-ID-change operating switch are **NOT YET RELEASED OR REAL-DGX QUALIFIED**. Keep `PRODUCTION_EXECUTION_RELEASED=False`; one active GPU model and port 8000; preserve historical journal/receipts/images/model files unless explicitly scoped.

Details: [27B real PASS](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-LIVE-PASS-20261107.md), [actual cleanup PASS](../docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md), [new Wizard lifecycle scope](../docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md). Do NOT edit the canonical recipe JSON cosmetically without a versioned/requalified migration: its exact SHA is bound into the current latest benchmark pointer.

---

## START HERE — 2026-11-07 LATEST: P2 Tool Calling HTTP 400 CONFIRMED; ordinary switch real bidirectional PASS

**Latest operator's real DGX at source HEAD `09c6780`**: fresh source fast-forward completed; **NVIDIA 27B is ACTIVE** on `:8000/v1` (`qwen38-27b`, `qwen3.8-27b`, `LIVE_SERVICE_VERIFIED`, `issues=[]`). The *independent ordinary operating journal* is `VERIFIED/COMMITTED`, **14 events**, `issues=[]`. This corroborates BOTH real ordinary operating switch directions `27B→Flash` and `Flash→27B` PASS. Historical P3-A/B/C and P3-C final PASS remain **CLOSED**; never rerun them. **Normal main Wizard execution remains gated** (`PRODUCTION_EXECUTION_RELEASED=False`); actual production menu acceptance and real forced-failure recovery are distinct and still outstanding.

**P2-FINAL tool support remains OPEN**: operator directly inspected preserved `qwen38-27b` Docker `Config.Cmd`, which has `modelopt_mixed`/BF16/context 8192, **NO `--enable-auto-tool-choice`, `--tool-call-parser`, or `--reasoning-parser`**. `serve_27b.sh --tools-profile` displays correct opt-in source flags `qwen3_coder` + `qwen3`; `serve_27b.sh --tools-probe` returns **`BLOCKED/LOCAL_API_HTTP_ERROR_400`**, structured tool cycle **NOT PASS**. Git source change does not retrofit existing container. Do not guess the exact HTTP 400 body, or claim migration/Parser/Open WebUI Native PASS. Next task is **safe separate tool-enabled model recipe/variant and rollback design**, with vLLM 0.32, one active model and `:8000` unchanged. Any actual runtime mutation requires new operator downtime consent. Original containers/images/HF caches and private receipts preserved. Draft PR #1 stays unmerged.

Read **[current state](CURRENT-STATE.md)**, **[next actions](NEXT-ACTIONS.md)**, **[evidence ledger](EVIDENCE-LEDGER.md)**, **[new conversation starter](SESSION-START-PROMPT.md)**, and **[P2-FINAL acceptance](../docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md)** before older snapshots. Earlier lines below (P3-C NOT_RUN, Flash active, first direction outstanding) are historical, NOT current. Latest branch SHA/CI should always be queried from GitHub.

---

## 2026-11-07 — START HERE: P3-C 실제 DGX PASS, NVIDIA 27B ACTIVE, 이제 Wizard UX 개발

**가장 최신 확정 상태:** P1 Flash-Next Verify/Benchmark와 P3-B 후 P1 재검증/진단, P2 NVIDIA 27B trial/benchmark, P3-A/B/C 실제 양방향 stage 순차 실행이 전부 PASS. 최종 `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_observed_model=27b`, `post_switch_status=LIVE_SERVICE_VERIFIED` at port 8000. **원본 모델/컨테이너/HF 캐시 보존; P3-A/B/C 재실행 금지.** Git 공개 모델별 benchmark 원본 대조는 2/2 VERIFIED. 이 아래 오래된 `P3-C NOT_RUN`, `Flash active`, `benchmark comparison pending` 문구는 당시 이력이며 **현재 상태가 아님**.

**새 대화는 [최신 시작 프롬프트](SESSION-START-PROMPT.md)에서 시작하세요.** [P1–P7 실제 백엔드/UX 별도 검증 표](../docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md)를 우선 참고. 대화형 `./wizard.sh`의 P3 메뉴는 계획 조회만 하므로, **다음 개발은 통합 Wizard 운영 UX + 반복 가능한 일반 Flash↔27B 전환**, 실제 27B 라이브 서비스 운영은 별도 명시적 승인 전 변경 금지. Draft PR #1은 미병합이며 GitHub HEAD/CI는 새 세션에서 다시 조회.

---

## 2026-11-07 — MODEL BENCHMARK RESULTS NOW IN GIT AS SANITIZED SUMMARIES

User requested storing benchmark results in Git. Current branch now tracks real operator-reported metric-only summaries at `benchmarks/published/qwen3.8-flash-next/f506db4c76430674.json` (post-B Flash mean 37.9527 tok/s; original private JSON SHA `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db`) and `benchmarks/published/qwen3.8-27b/80f109dbd7c97460.json` (27B E2E 7.9002 tok/s; decode proxy 11.1801; original SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`). These came from the user's actual DGX logs, not fresh GPU measurement. No private raw JSON, prompts, paths, tokens/approvals, container IDs or logs committed. `scripts/manager/benchmark_publication.py` is a guarded allowlist exporter (read-only plan/verify; explicit hash-approved local write; NO auto Git add/commit/push). `bash scripts/temporary/verify-published-benchmarks.sh` cross-checks Git summaries against original DGX receipts WITHOUT service changes. **Source CPU tests pass; real original-byte cross-check is pending operator pull/run.** See `benchmarks/published/README.md`.

User also tried Stage-C `--execute`, but typed a leading `[` with the SHA; wrapper returned **CANCELLED/executed=false/execution_dispatched=false/approval_accepted=false**. Flash-Next stayed the observed live source; **P3-C NOT_RUN**. Future C approvals require NEW current 64-hex SHA without the displayed brackets, then two distinct exact downtime/final-C literal inputs. Never reuse historical plan ID or infer authorization. Current Draft PR #1 unmerged; the agent only committed source/sanitized measurement summaries.

---

## 2026-11-07 — STAGE-C CANONICAL READ-ONLY READY; TRACKED C OPERATOR SOURCE IMPLEMENTED

The latest **actual operator DGX** command `./wizard.sh switch flash-next-27b stage-c --plan --json` returned **READY_TO_REQUEST_TRANSITION_APPROVAL**, `issues=[]`, `p1_evidence.status=PASS`, correct active original `flash-next` and preserved target `27b` CIDs/images, with `executed=false`. This is a real read-only plan, **not** C downtime permission. The old C plan SHA `d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7` had a short expiry and is NEVER reused. User also entered `COPY` at optional evidence import's exact-plan prompt; result **CANCELLED/copied=0**, unrelated to C.

To honor original D-016 operation model, source-tracked `scripts/temporary/p3-stage-c-operator.sh` and Python controller provide default `--plan` (non-disruptive) and separately approved `--execute` (human TTY, fresh C-only SHA, exact Flash downtime and independent final-C confirmation; canonical Wizard alone changes Docker). 27B final API and original canonical `stage-c.json` checked again; new operator report is private ignored project `reports/transitions/flash-next--to--27b/`, immutable P3 operational state remains in original local state directory. CPU fake-DGX tests in `tests/test_p3_stage_c_operator_cpu.py`. After current GitHub HEAD CI success and clean DGX fast-forward pull, request **`bash scripts/temporary/p3-stage-c-operator.sh --plan` first**. The actual `--execute` requires a NEW separate operator decision to interrupt Flash. No automatic execution, model deletion, migration, PR merge, or P3-A/B repetition. [Operator C runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## 2026-11-07 — NEXT: MODEL HISTORY + P2/P3 COPY-ONLY CONSOLIDATION; P3-C READ-ONLY PLAN

User asked to add per-model past Verify/Benchmark/history in the main Wizard and phase in project-local P2/P3 evidence. Implemented read-only catalog `scripts/manager/evidence_catalog.py`, integrated `Select model → 4 Past results` and `Advanced → 8 Exact-approved report COPY`; machine CLI `./wizard.sh evidence list --model flash-next --kind benchmark`, `./wizard.sh evidence migrate --plan|--guided`. P1/P2/P3 old source receipts, runtime locks/journal remain unchanged; project reports ignored by Git. New copy uses fresh 64-char approval, revalidation, 0600 O_EXCL, 0700 directories, hash dedup; P3-C safety-critical evidence gate still reads canonical state. See [migration contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md).

Actual DGX ZIP still grounds P3-A/B PASS and POST-B P1 Verify+Benchmark PASS; last observed Flash-Next active :8000. **P3-C is the next eligible operating stage, but is NOT_AUTHORIZED/NOT_RUN and its *new live preflight* has NOT yet been supplied.** Once latest GitHub code/CPU CI passes and user clean-pulls, request ONLY `./wizard.sh switch flash-next-27b stage-c --plan --json`. If `READY_TO_REQUEST_TRANSITION_APPROVAL` with `issues=[]` and P1 gate PASS, separately seek actual Flash downtime authorization. Do not automatically execute C, repeat A/B, clean caches or merge Draft PR #1. Older messages claiming POST-B P1 NOT_RUN superseded.

---

## 2026-11-07 — CURRENT operator state: Post-B Flash Verify + Benchmark REAL PASS, UX source fixes

The operator supplied a ZIP containing actual Flash-Next GPU Verify and Benchmark executed after successful P3-B. Both PASS with distinct explicit SHA approvals; measured 3-request mean 37.9527 tokens/sec, TTFT p50 1.384594 sec, latency p50 1.724560 sec. Last known actual API served `qwen3.8-flash-next` on :8000. Older statements that POST-B P1 is NOT_RUN are superseded. `P3-C` is still NOT_AUTHORIZED; no model switch/restart/repeat inferred.

The open Draft PR #1 working branch includes a model-centric interactive UX change: operator sees the exact approval SHA, avoids the duplicate action selection, sees Verify and Benchmark metrics, and stores future P1 receipts under Git-ignored project `reports/models/qwen3.8-flash-next`. Historical receipts stay immutable; gate reads both legacy and project paths. Source CI includes new approval/UI and mixed-path tests. **Never confuse CPU CI success with actual DGX UX rerun.** See [current state](CURRENT-STATE.md), [next actions](NEXT-ACTIONS.md), [evidence ledger](EVIDENCE-LEDGER.md), [operating decisions](DECISIONS.md), [UX/evidence contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

## 2026-11-07 — CURRENT: P3-A/B actual DGX PASS; Flash-Next restored; POST-B P1 pending

**Supersedes all older headings below that say "P3-B NOT_RUN" or "27B ACTIVE".** Operator-provided actual DGX P3-B output: `P3_B_PASS_FLASH_NEXT_ACTIVE`, `executed=true`, `wizard_result.status=PASS`, `live_verified=true`, `post_switch_status=LIVE_SERVICE_VERIFIED`, and original served ID `qwen3.8-flash-next`. The immutable Wizard receipt is `~/.local/state/blazux-wizard/p3/stage-b.json`. The old B operator report was **misnamed** `~/blazux-p3-reports/p3-a-operator-20261106T223124Z-14861d75.json` due to imported A persistence; do not delete or rename it. Source fix now uses B-specific filenames and reports independent manual consent and execution dispatch.

POST-B P1 `p1-post-download.sh --inspect-only` on actual DGX was READY/PASS **for source, API and Verify/Benchmark plans only** (report `~/blazux-p1-reports/20261106T224010Z-d2095867/result.json`). Verify execution, Benchmark execution and full post-B doctor/inventory raw diagnosis are **NOT_RUN/NOT_YET_QUALIFIED**. The read-only D-016 `bash scripts/temporary/p1-post-b-audit.sh` was implemented and CPU-tested; DGX run still pending. P3-C NOT_RUN/NOT_AUTHORIZED. Preserve port 8000, single active GPU model, original containers/image/cache and Draft PR #1.

---

> **2026-11-06 LATEST REAL P3-B INSPECTION: READY, 27B ACTIVE, B NOT APPROVED.** User ran tracked stage-B read-only inspector after P3-A. Result `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`, live API `qwen3.8-27b`, original Flash preserved identity. `~/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. Core B gate now uses **`I_ACCEPT_27B_DOWNTIME`** (not old Flash ACK) and independently **`I_SEPARATELY_AUTHORIZE_P3_STAGE_B`**. New D-016 `scripts/temporary/p3-stage-b-operator.sh` defaults read-only, with a separately approved `--execute` route only after user explicitly consents to new 27B downtime. **Do not treat inspection PASS as B approval.** P3-B actual transition NOT_RUN, post-B P1 and C NOT_RUN. Keep 27B LIVE, preserve models/containers, no Draft PR merge. See [D-040](DECISIONS.md), [next actions](NEXT-ACTIONS.md), [stage B operator runbook](../scripts/temporary/README.md).

> **LATEST 2026-11-06 — REAL P3-A PASS; NVIDIA 27B ACTIVE, STOP BEFORE B.** Operator executed `p3-stage-a-operator.sh --execute` on DGX, actual Wizard `stage=a,status=PASS,executed=true,live_verified=true`, independently verified Manifest/API `27b`, final wrapper `P3_A_PASS_27B_ACTIVE`, `issues=[]`; operator report `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json` and immutable Wizard receipt `~/.local/state/blazux-wizard/p3/stage-a.json`. Previous older paragraphs claiming A NOT_RUN are **historical**, superseded here. **P3-B (27B→Flash-Next) is NOT approved/executed**, nor are post-B P1 rebenchmark and C. New D-016 `scripts/temporary/p3-stage-b-inspect.sh` is **read-only only** and needs GitHub source CI then DGX pull; no B executor or GPU start/stop through it. See [state](CURRENT-STATE.md), [decision D-039](DECISIONS.md) and [runbook](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md). No auto B, cache deletion or PR merge.

> **NEW P1 PRE-A CLEARANCE + P3-A OPERATOR BOUNDARY (2026-11-06):** operator's actual DGX `scripts/temporary/p1-pre-a-readiness.sh` output at `20261106T065104Z` was `PRE_A_P1_REVIEW_READY`, `issues=[]`: source + P1 functional and measured benchmark PASS, historical/current rc3 proved own active Flash collision. User's earlier conditional approval is eligible **only for P3-A**. A dedicated GitHub-tracked D-016 `scripts/temporary/p3-stage-a-operator.sh` is now the operator interface: `--plan` read-only, `--execute` TTY with full current plan hash and individually typed downtime and P3-entry acknowledgments, one stage only with independent 27B API recheck. **Actual P3-A/B/C NOT_RUN**. Preserve all original assets, don't auto-chain or merge Draft PR. See [current state](CURRENT-STATE.md), [D-037](DECISIONS.md), [P3 runbook](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md).

> **LATEST actual P2 / staged P3 source (2026-11-06):** User-supplied DGX bounded NVIDIA 27B streaming benchmark 3/3 PASS, overall `BENCH_PASS_RESTORED_VERIFIED`, original Flash-Next `RESTORED` and fresh Wizard `LIVE_SERVICE_VERIFIED`; P2 **COMPLETED/STOP**. Earlier paragraphs below claiming P2 benchmark NOT_RUN are historical. P3 D-034 stage A/B/C source executor and P1 measured evidence gate now exist and have CPU CI tests, **but actual P3 switch still NOT_RUN/NOT_QUALIFIED and must not run without separate stage-specific downtime approvals**. New runbook: [docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md). Do not interpret this source update as permission to interrupt :8000, start GPU models or merge PR #1.

> **LATEST P2/P3 OPERATOR RULE (2026-11-06):** P2 actual 27B benchmark must finish and **STOP**; NEVER auto-enter P3. P3 requires a fresh explicit operator decision, separate approved establishment of active 27B, **27B→Flash-Next** verification, **P1 deficiencies addressed + actual Flash-Next rebenchmark**, and finally a separately approved **Flash-Next→27B** transition with **27B active as final state**. The former P3 `roundtrip` plan/execute is **RETIRED and BLOCKED**. Source-only new read-only command `./wizard.sh switch flash-next-27b sequence --plan --json` does not execute any transition; persistent switch backend still missing. See [binding P3 sequence](../docs/P3-MANUAL-TRANSITION-SEQUENCE-20261106.md), [operating rules](OPERATING-RULES.md), [newest current state](CURRENT-STATE.md) and [D-034](DECISIONS.md). Previous roundtrip procedures below are superseded. No GPU/service mutation has been performed for this rule change.

> **2026-11-06 LATEST ACTUAL GPU EVIDENCE:** NVIDIA Qwen3.8-27B startup/API/small text inference on DGX **PASS** and original Flash-Next normal-path restore **RESTORED**, zero issues (`PASS_RESTORED`). This supersedes historical `NOT_RUN` notes below; benchmark and repeat switching not yet qualified. **Live status now uses Manifest + API via `./wizard.sh service manager status --json`**, no separate raw Docker/curl commands. See [real P2 GPU evidence and Wizard workflow](P2-27B-GPU-TRIAL-PASS-20261106.md). No further service interruption authorized by this report.

> **2026-11-06 P2 superseding update:** Operator completed the NVIDIA 27B exact-revision download (19/19, exit 0, \`SOURCE_FILES_PRESENT_PINNED_CANDIDATE\`; GPU \`NOT_RUN\`). New read-only qualification: \`./wizard.sh model 27b status --inspect-runtime --json\`. Older 84% transfer comments below are historical, not current. No service switch/27B start is authorized. See \`CURRENT-STATE.md\`, \`EVIDENCE-LEDGER.md\`.

> **2026-11-06 full Wizard SOURCE handoff (D-021):** `./wizard.sh` now runs complete operator console `wizard/console.py`: 1 model → recommended next / all lifecycle actions, 2 service status/health/logs and guarded start/stop/restart/rollback/proxy/gateway, 3 advanced P3/P4/P6/P7 + readiness dashboard. `./wizard.sh workflow 27b --json`, `./wizard.sh workflow 27b --for-action start --json`, and `./wizard.sh roadmap --json` expose machine-readable plans. P1 and P2 execution backends **unchanged**, P2–P7 real runtime/switch/cleanup still **BLOCKED**. Full spec: [../docs/UNIFIED-MODEL-WIZARD-DESIGN.md](../docs/UNIFIED-MODEL-WIZARD-DESIGN.md). User's DGX 27B transfer started but no completion receipt yet; avoid pull while it runs.

# Handoff index — START HERE

> **2026-11-05 current Wizard UI decision (D-020):** `./wizard.sh` now presents **1 Select/run model, 2 Service, 3 Advanced, 0 Exit**. `./wizard.sh select 27b --json` produces a read-only consolidated lifecycle plan. Old P1–P7, model/switch/storage/operations/service commands remain supported, and the P1 guarded backend is retained verbatim. Approved design: [../docs/UNIFIED-MODEL-WIZARD-DESIGN.md](../docs/UNIFIED-MODEL-WIZARD-DESIGN.md). DGX user-reported pinned NVIDIA 27B download **started** (`Fetching 19 files: 84%`); receipt, runtime and switching **NOT_VERIFIED**. No DGX commands from source work; do not change the worktree under an active download.



**Canonical starting point for every new ChatGPT, human or agent work session on this fork.** These files live on the **new planning branch** `feature/recipe-wizard-handoff` until merged. Do not assume they are on `main`.

## Confirmed delivery order (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

## Wizard CLI first-class entrypoint

**Wizard architecture decision (2026-11-05):** Implement all P1–P7 **menu/CLI modules first** and then integrate/debug actual runtime in P1→P7 order. Root operator entry is `./wizard.sh`; `wizard/menus/models/`, `switching/`, `storage/`, and `operations/` own per-menu behavior, with `wizard/main.py` and `wizard/menus/common.py` for routing and safe source contracts. Scripts accept explicit stage/action arguments and emit JSON and stable exit codes for operator-mediated DGX tests. Only P1 calls the existing guarded backend today; P2–P7 are SOURCE-ONLY plans and must never execute merely because a menu exists. No SGLang; vLLM 0.32 only.

CLI reference: [../docs/WIZARD-CLI-CONTRACT.md](../docs/WIZARD-CLI-CONTRACT.md). Current stage readiness: [CURRENT-STATE.md](CURRENT-STATE.md).

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

### User-operated DGX temporary command bundles (D-016/R1D)

Prefer a **Git-committed, CI-tested, single-entry temporary script** in `scripts/temporary/` over pasting many shell commands. The operator completes any previous setup, then `git pull --ff-only`, runs one wrapper, and returns reviewed JSON evidence. See [OPERATING-RULES.md](OPERATING-RULES.md) R1D and [scripts/temporary/README.md](../scripts/temporary/README.md). Initial P1 bundle: source/CI PASS 131/131 tests/job ×2 at `b9f9a1b`, actual DGX execution NOT_RUN.

## Read order (mandatory)

1. **[CURRENT-STATE.md](CURRENT-STATE.md)** — latest known project, branch/HEAD, active stage, blockers and verification status.
2. **[OPERATING-RULES.md](OPERATING-RULES.md)** — do-not-touch boundary, evidence standards, update obligations.
3. **[NEXT-ACTIONS.md](NEXT-ACTIONS.md)** — tasks in priority order and exit conditions.
4. **[DECISIONS.md](DECISIONS.md)** — fixed decisions vs proposals.
5. **[EVIDENCE-LEDGER.md](EVIDENCE-LEDGER.md)** — what was actually tested, source vs DGX.
6. **[CHANGELOG.md](CHANGELOG.md)** — append-only significant updates.
7. **[../docs/MODEL-RECIPE-WIZARD-PLAN.md](../docs/MODEL-RECIPE-WIZARD-PLAN.md)** and **[../docs/MANIFEST-CONTRACTS.md](../docs/MANIFEST-CONTRACTS.md)** — scope, staging, interfaces and cleanup contract.

Use [SESSION-START-PROMPT.md](SESSION-START-PROMPT.md) for a new conversation. Do not paste full context repeatedly if GitHub can be read.

## Source-of-truth hierarchy

1. Fresh **read-only actual DGX evidence** and verified GitHub refs/CI (for runtime/git facts).
2. `CURRENT-STATE.md` and `EVIDENCE-LEDGER.md` (for previously observed facts; preserve timestamps).
3. Reviewed committed plan, contracts and decisions.
4. Legacy Preview/YSLAB documents and earlier chat summaries (historical context, **not** proof of this fork).
5. Assumptions must be labelled `UNVERIFIED`; no upgrade to PASS without evidence.

When refs disagree, do not silently merge/overwrite: record the discrepancy, refresh with tools and fix source documents in the same PR.

## Handoff closing checklist

On any session that changes GitHub, documents, tests, requirements or verified state:
- commit implementation and documentation, or record precisely why they cannot be committed;
- update `CURRENT-STATE.md` and `NEXT-ACTIONS.md` **in the same change set**; update ledger/decisions/changelog if affected;
- refresh actual branch, commit, PR and CI status using GitHub tool; never write a self-referential “this file contains its own HEAD” claim;
- include exact commands, what ran, test results, artifact/log links, what did **not** run, next safe action;
- open or update PR as appropriate; **do not merge merely because documentation exists**;
- end with a short handoff summary linking these files.

`CURRENT-STATE.md` is a **living snapshot**, not a history. Put the history in `CHANGELOG.md` and evidence in `EVIDENCE-LEDGER.md`. No secrets or credentials in these files. File and branch names are stable interfaces for future sessions.
