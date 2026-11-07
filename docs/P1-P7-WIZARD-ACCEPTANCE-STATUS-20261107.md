## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

**P3-G updated acceptance row:** Forward real 27B→Flash PASS; reverse Flash→27B NOT_RUN; controlled failure/rollback NOT_RUN; UX/production release not qualified. P3-D read-only GPU/port source audit PASS before switch, P3-E source candidate match but reinstall unqualified, P3-F 144 local CPU PASS; keep evidence distinctions. P4 optional and P5/P6/P7 unchanged.

---

## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

**Stage G:** D read-only PASS; E candidate documented fields match (reinstall unqualified); F CPU 144/144 PASS; G read-only PREVIEW PASS. Newly authorized *maintenance downtime scope* permits separate one-off live operating acceptance steps, **NOT performed**. G real forward, reverse, failure-restore and UX acceptance remain NOT_RUN until operator logs real receipts. P4 conditional, P5/6/7 unchanged.

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

## 2026-11-07 — OFFICIAL P3 EXTENSION: STAGES D, E, F, G (SOURCE DRAFT)

**Approved stage numbering:** P3-A/B/C historical one-off transfers are **REAL PASS/CLOSED and immutable**. The formerly unnamed four common Wizard operating-function tasks are now officially **P3-D** (GPU exclusivity and :8000 PID audit), **P3-E** (Flash-Next canonical runtime/reinstall recipe qualification), **P3-F** (general recipe lifecycle, restart/reinstall/rollback/immutable journal/CPU acceptance), and **P3-G** (real DGX bidirectional operating transfers, safe fault/restore and Wizard UX final acceptance). There is **no P3-H** in the current plan. This expansion does not reopen or replay A/B/C.

**One command draft runner:** `bash scripts/temporary/p3-d-g-acceptance.sh --run` performs D/E/G *read-only* DGX probes plus F CPU/Fake-DGX regression; `--cpu-only` runs source regressions without GPU/Docker/API, `--plan` is inert. `--strict` returns nonzero while real D-G acceptance is incomplete. **No Docker mutation, no benchmark, no installation/reinstall, and no real P3-G switch/rollback**. A successful source run does NOT mean D-G are complete or production released. `P3-E` without a separately qualified Flash reinstall recipe must remain DRAFT_REVIEW_REQUIRED. Full contract: `docs/P3-D-G-UNIFIED-WIZARD-DRAFT-ACCEPTANCE-20261107.md`. Current real DGX preexisting baseline: canonical 27B `diff=[]`, source-current-ID Flash operational preview `READY_FOR_OPERATOR_REVIEW_ONLY`, `LIVE_SERVICE_VERIFIED`; not evidence of D hardware ownership or G live transfers after canonical 27B recreation.

**P4/P5/P6/P7 remain unchanged**: P4 optional Flash removal/recovery (may be NOT_APPLICABLE), P5 Orcarouter serving+bench, P6 Orcarouter↔27B switches, P7 full integrated system release. P3-D-G complete acceptance is a predecessor to selecting P4 disposition, but optional P4 is not a forced deletion stage.

---

## SUPERSEDING VERIFIED STATE — 2026-11-07, AFTER DGX REAL ACCEPTANCE

**LATEST FACTS override older diagnostic/HTTP-400/source-only text further down.** The initial NVIDIA 27B API HTTP 400 and absent native parser flags were RESOLVED via a user-approved RECREATION of the canonical `qwen38-27b` from pinned `recipes/qwen38-27b.runtime.json` (vLLM 0.32.0, modelopt_mixed, port 8000, `qwen3_coder` / `qwen3` / exact NVIDIA Jinja). Actual DGX native `tool_calls`, tool result continuation, streaming, normal chat, benchmark v2 **PASS** (3/3, mean client E2E 10.957 tok/s, p50 TTFT 0.165412 s), and Open WebUI Native **user-confirmed PASS**. Original old container's verified stopped backup was deleted after full success; new canonical `qwen38-27b` is operational. P3-C one-off already REAL PASS/CLOSED; old P3 Docker IDs are historical, not current execution identity.

Wizard manifest cleanup then actually removed the two *stopped historical test containers*, `qwen38-27b-failed-6d9ede0904c2` and `qwen38-27b-native-tools-v1`. Live `cleanup --execute` and independent `cleanup --status` returned `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, both absent, active canonical 27B preserved; `service manager status --json` returned `LIVE_SERVICE_VERIFIED` with API `qwen3.8-27b` at :8000. The recorded cleanup was completed, NOT a pending removal. `qwen38-flash` remains stopped; Open WebUI and Portainer remain running.

**Next work is NOT P2 native-tool HTTP-400 troubleshooting.** It is general Wizard model lifecycle / recipe diff-aware install, removal, reinstallation and same-name recreation, current-Docker-ID-aware model switching and independent production release acceptance. Canonical 27B and Flash are removable/reinstallable upon independently approved actions; no global deletion ban. Such generic lifecycle functionality and the post-container-ID-change operating switch are **NOT YET RELEASED OR REAL-DGX QUALIFIED**. Keep `PRODUCTION_EXECUTION_RELEASED=False`; one active GPU model and port 8000; preserve historical journal/receipts/images/model files unless explicitly scoped.

Details: [27B real PASS](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-LIVE-PASS-20261107.md), [actual cleanup PASS](../docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md), [new Wizard lifecycle scope](../docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md). Do NOT edit the canonical recipe JSON cosmetically without a versioned/requalified migration: its exact SHA is bound into the current latest benchmark pointer.

---

## LATEST REAL DGX — 2026-11-07 P2-FINAL native tool_calls + streaming PASS_RESTORED

**Actual operator-provided DGX run, not CPU simulation:** fresh TTY-approved `scripts/temporary/p2-final-native-tools-operator.sh --execute` completed with `status=PASS_RESTORED`, `trial=PASS`, `structured_tool_call=true`, `tool_result_continuation=true`, `streamed_tool_call=true`, `structured_probe_status=LOCAL_STRUCTURED_TOOL_CYCLE_PASS`, `stream_probe_status=LOCAL_STREAMED_TOOL_CALL_PASS`, `issues=[]`, `original_restored=true` / `restoration.status=RESTORED`. Operator then independently verified original `qwen38-27b` serving sole API ID `qwen3.8-27b` at `:8000`, `LIVE_SERVICE_VERIFIED`, `issues=[]`. Ordinary operating journal still `VERIFIED`/`COMMITTED`, **14 events**, `issues=[]`, last event hash `ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e`. Docker running list contains original 27B, Open WebUI (healthy), Portainer; no second running model shown.

**Qualification update:** The actual bounded 27B Native Tools `tool_choice=auto` + synthetic tool-result continuation + SSE + original restoration **subgate is now REAL PASS**. Earlier “not run” / original API HTTP-400 historical entries below remain chronological evidence, **not current milestone status**. This run does NOT verify real Open WebUI Native end-to-end, production Wizard native-tools switching, crash/forced-error rollback, comprehensive generated reasoning leakage, physical GPU process exclusivity or host port process ownership. The ordinary status fields `manifest_status=OBSERVED_UNQUALIFIED`, `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `operations_enabled=false` remain unqualified scopes rather than observed conflicts. Do not declare complete P2-FINAL production acceptance; ordinary Wizard `PRODUCTION_EXECUTION_RELEASED=False`, old P3-C immutable, original containers/images/HF cache retained, vLLM 0.32, port 8000, ONE_ACTIVE_MODEL_ONLY. **No repeat trial with the same SHA**; private attempt marker blocks blind repetition.

**Evidence detail and remaining acceptance gates:** [docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md](P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md). Next: private one-shot evidence/stopped variant inventory audit (read-only); design safe long-lived variant-aware service identity and production rollout (separately approved); live Open WebUI Native application end-to-end only during an independently approved maintenance period. No new service downtime authorized by this report.

---

## LATEST DGX — 2026-11-07 full ordinary bidirectional postcheck PASS; P2-FINAL tool auto still blocked

The operating acceptance 27B→Flash and reverse Flash→27B had both independently returned live `PASS`. New post-reverse REAL DGX `service manager status --json` confirms last active `27b`, `LIVE_SERVICE_VERIFIED`, exact sole API served ID `qwen3.8-27b`, port 8000, no issues. Independent `operational_audit --json` confirms `VERIFIED/COMMITTED`, **14** events, `issues=[]`. Ordinary operating backend's actual bidirectional transfer and postcheck therefore **PASS**. Real forced failure/restore and main interactive Wizard production switch release are still **NOT_QUALIFIED** (`PRODUCTION_EXECUTION_RELEASED=False`).

**P2-FINAL Open WebUI Native Tool Calling remains outstanding**: actual preserved 27B Docker `Config.Cmd` lacks `--enable-auto-tool-choice`, `--tool-call-parser`, `--reasoning-parser`; source opt-in flag preview is correct but not deployed. Local structured `tool_choice=auto` probe returned `BLOCKED/LOCAL_API_HTTP_ERROR_400`; live structured call, continuation, streaming, thinking separation and WebUI Native UI **NOT PASS**. Prior P2 pinned GPU trial/benchmark PASS and P3-C original one-off PASS remain immutable and complete. Keep original assets and port 8000.

---

## LATEST — P2-FINAL Tool Calling scope; P3-C already CLOSED; ordinary switch both-way backend PASS

Confirmed current model in user's newest supplied ordinary acceptance result is `27b` after actual **Flash→27B** ordinary trial `PASS`, distinct from original **P3-C** historical one-off Flash→27B `PASS`. Earlier new ordinary 27B→Flash also REAL PASS and separately post-checked. Independent status/audit AFTER most recent reverse is still missing. `./wizard.sh` main menu remains **release-gated**, so a two-way one-off operator trial is NOT proof of normal everyday menu execution UX.

P2 earlier pinned 27B download/loader/runtime trial/benchmark/Flash restore is REAL PASS. User added **last P2 acceptance item**: official vLLM **Qwen3.8-27B** Native Tool Calling on pinned NVIDIA variant, using `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`. Source opt-in profile and benign localhost structured tool-cycle probe implemented, existing original 27B startup untouched. **P2-FINAL live tool activation, streaming, reasoning, Open WebUI Native and preserved-container-safe migration NOT YET VERIFIED**. Thus do not mark newly expanded P2 acceptance all PASS. Historical **P3-C original real PASS stays CLOSED/IMMUTABLE** and requires no further Stage-C execution. See `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.

---

## New actual DGX verification — 2026-11-07: post-ordinary 27B→Flash status and journal PASS

**First real ordinary 27B→Flash PASS** now additionally confirmed via independently issued read-only DGX commands: Flash is sole active `qwen3.8-flash-next` `LIVE_SERVICE_VERIFIED`, `issues=[]` on :8000, and independent operating journal chain audit `VERIFIED` / terminal `COMMITTED` / 7 events, `issues=[]`. Reverse ordinary **Flash→27B is still NOT_RUN**: its preflight is `READY_FOR_SEPARATE_TRIAL_APPROVAL`, issues none, with an ephemeral plan SHA and 276 seconds remaining **at capture only**. No reverse action or failure-recovery injection has been performed. Production guided switch menu remains gate-locked; old P3 A/B/C are historical. No incorrect assumption that the read-only service's `gpu_exclusivity_verified=false` equates to a live GPU conflict.

---

## LATEST 2026-11-07 ACTUAL ordinary switch acceptance: 27B → Flash-Next PASS (first direction only)

Operator real DGX after source `4054eb2` ran the newly tracked `operational-switch-acceptance.sh --target flash-next --execute` under a fresh read-only plan and four exact, manually typed trial/SHA/downtime/target approvals. Source API before transfer was `LIVE_SERVICE_VERIFIED` for sole `qwen3.8-27b`, operating journal initially `EMPTY`, current plan `READY_FOR_SEPARATE_TRIAL_APPROVAL`, issues `[]`. The NEW independent ordinary-switch backend returned `Live transition result: PASS`, `Observed model: flash-next`, and private immutable completion receipt. **This is first real DGX ordinary 27B→Flash acceptance**, independent of historic P3-B.

**Acceptance scope:** historical P3-A/B/C actual PASS unchanged; new ordinary operating **27B→Flash PASS**, **Flash→27B NOT_RUN**, real failure/restore injection **NOT_RUN**, normal `./wizard.sh` everyday model-switch menu still `PRODUCTION_EXECUTION_RELEASED=False` and **NOT_RELEASED**. Execution backend's PASS covers its bounded chat and committed journal checks; source report does not substitute for separately supplied post-execution `service manager status` and `operational_audit` output. **The latest observed active model is FLASH-NEXT**, not 27B. No automatic reverse. Next read-only: current service/status, journal integrity, and fresh `--target 27b --plan --json`; reverse execution requires new explicit operator downtime approval and four new inputs. Tool Calling and other phases remain postponed.

---

## 2026-11-07 — General P3 operating Wizard SOURCE acceptance candidate (not real DGX release)

**P3 one-off historical real DGX A/B/C PASS unchanged.** Subsequent real DGX 27B curl text generation and one no-thinking exact response PASS; real recurring 27B ↔ Flash operating switch and rollback **NOT_RUN**. New GitHub source fully connects the *existing* `./wizard.sh` main menu (option 4) and model menu (option 6) to independent ordinary-switch guided review; CLI `operational guided` has read-only default, and production `--execute` remains source release-gated. The operating backend now has domain-separated execution SHA and three human consent fields, immutable journal audit with crash divergence rejection, bounded target Chat Completions after health/model identity, no-downtime cancellation, best-effort rollback and failure reporting.

A separate one-time operator acceptance route `operational acceptance --target ... --plan|--execute` and a tracked shell wrapper are implemented. `--execute` needs four fresh exact human TTY approvals and independently checked current plan, which provides a way to perform **one** physical acceptance only if the operator separately approves 27B/Flash API downtime. It is NOT itself real hardware proof and does NOT release the normal operating Wizard. Read `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`.

Open WebUI 27B tool parser and recipe integration are intentionally **DEFERRED**. P4/P5/P6/P7 are unchanged. Original P3 immutable receipts and 27B active :8000 are preserved; no merge or deletion.

---

## Latest DGX proof — current 27B functional text-generation PASS (2026-11-07)

User-supplied DGX actual `curl` probe and tracked script both verified localhost `:8000/health`, sole served model `qwen3.8-27b` and actual Chat Completions with the matching model ID. Tracked script returned `27B_CURL_SMOKE_PASS`. This strengthens **current P2/27B serving functional health** (not a new benchmark); P3 A/B/C historical completion is unchanged. Direct reply `finish_reason=stop` with 26 generated tokens; however `message.content` contained reasoning-like text and literal `</think>` before `DGX_OK`, so strict exact-format compliance is **not PASS**. New classifier source-only, pending actual DGX rerun; **general operating switch, user-friendly approval, recovery and P7 release remain NOT ACCEPTED**. No model transfers or restarts authorized.

---

## 2026-11-07 SOURCE UPDATE — ordinary model-switch preview and independent guarded backend

The original actual-DGX P1/P2/P3-A/B/C PASS results below remain valid and immutable; the last operator observation is still NVIDIA 27B on :8000 (\`qwen3.8-27b\`). A **new source-only** ordinary switch preview is available from \`./wizard.sh\` model selection and CLI \`./wizard.sh switch flash-next-27b operational --target flash-next --plan --json\`; \`operational_executor.py\` implements independent protected transaction SOURCE but **is not exposed for live execute**. Fake-DGX CPU CI validates source paths only. P3 operating-switch readiness = **SOURCE_PRESENT / CPU_SIMULATION_PASS / REAL_DGX_NOT_RUN / INTERACTIVE_EXECUTE_NOT_ACCEPTED**. The dashboard now separates strictly readable private P3 historical receipts, local model history, current API health, general operating readiness and UX acceptance. P4/P5/P6/P7 remain as shown below; do not upgrade release or operations qualification solely from source CI.

See \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`. Private P3 A/B/C receipts remain historical; never re-run stage A/B/C, stop NVIDIA 27B without new approval, delete caches, or merge Draft PR #1.

---

# Blazux P1–P7 인수인계 기준 현황 — 2026-11-07

> **범위:** 실제 DGX에서 증거가 확인된 백엔드 수행 결과와, `./wizard.sh` 대화형 운영 UX의 완성도를 **독립적으로** 기록한다. 이 문서는 최신 실장비 실시간 점검 명령의 대용이 아니다. 모든 과거 기록의 `NOT_RUN` 표시보다 `handoff/EVIDENCE-LEDGER.md`의 최신 시간순 실측 증거가 우선한다. 단계별 원본 테스트 영수증은 로컬에 보존하고 Git에는 공개 허용된 벤치마크 요약만 저장한다.

## 1. 최신 실제 DGX 기준

- **2026-11-07 10:19:39 KST**: P3-C 최종 Flash-Next → NVIDIA 27B 실행 **PASS**. 원본 canonical Wizard C `status=PASS/stage=c/executed=true/live_verified=true/active_model=27b`. 운영자 wrapper `status=P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `issues=[]`. 최종 served model ID `qwen3.8-27b` / API 포트 8000.
- P1 NVIDIA Flash-Next 실제 API Verify(Completion/Chat/Tools/Vision) 및 bounded Benchmark **PASS**. P3-B 후의 P1 재검증·Benchmark·diagnostics **PASS**. Flash-Next 공개 allowlist 벤치: 평균 **37.9527 tokens/sec**.
- P2 `nvidia/Qwen3.8-27B-NVFP4` pinned revision `482ca0f3832238542f8f5295dde86b5f22711d80`: 19파일 다운로드/런타임 trial/API/3요청 bounded Benchmark, 원본 Flash 복구 확인 `BENCH_PASS_RESTORED_VERIFIED`. 27B 공개 allowlist 벤치: **7.9002 client E2E tokens/sec**, **11.1801 client decode proxy tokens/sec**. 서로 다른 측정 지표를 공정한 모델 간 성능 순위로 직접 비교하지 않는다.
- P3-A 실제 Flash→27B PASS, P3-B 실제 27B→Flash PASS, **P3-C 실제 Flash→27B PASS**. **일회성 P3-A/B/C 재실행 금지**; 현재 마지막 관측 상태는 27B ACTIVE이며 그 상태를 보존해야 한다.
- 독립 실장비 검증: `bash scripts/temporary/verify-published-benchmarks.sh`는 Git 공개 요약 2개 모두 `VERIFIED/issues=[]/executed=false`로 원본 private JSON과 일치함을 확인했다. 벤치 결과는 `benchmarks/published/` 참조.
- GitHub 작업: `feature/recipe-wizard-handoff`, Draft PR #1 미병합. 최근 CI 565/565 CPU PASS(26그룹), run 42323857383. **매 새 세션에서 HEAD·PR·CI를 반드시 실시간으로 다시 조회한다.**

## 2. 단계별 구현/검증 분리표

| 단계 | 기술 범위 | 실제 DGX 백엔드 | 통합 Wizard 운영 UX | 비고/다음 개발 |
|---|---|---|---|---|
| P1 | NVIDIA Flash-Next recipe·prepare·start·API Verify·Benchmark | **PASS** (지정된 시나리오) | **부분**, 설치~실행~결과까지 메뉴 전체 통합 수용 미검증 | P1 기존 guarded backend 보존 |
| P2 | NVIDIA 27B pinned download·loader·trial·API·Benchmark·원본 복구 | **PASS** (bounded) | **부분**, 모델 선택부터 전체 흐름 수용 미검증 | 27B 현재 활성, 불필요한 재다운로드 금지 |
| P3 | Flash↔27B 실제 A/B/C 순차 전환 | **A/B/C 실제 PASS** | **미검증**: `wizard/console.py` stage 메뉴는 현재 `--plan`만 호출 | 반복 가능한 일반 전환 엔진 및 모델 중심 메뉴 연동 필요; one-off P3 영수증 재사용 금지 |
| P4 | Flash-Next 선택적 제거 및 복구 | **NOT_RUN**, 조건부 | 계획/메뉴 interface만 | 저장공간 여유라면 NOT_APPLICABLE 결정; 별도 삭제 승인 없이 원본 보존 |
| P5 | Orcarouter Flash-Next pinned BF16 PLE/vLLM 0.32 구동·벤치 | **NOT_RUN** | 메뉴/interface only | 별도 `feature/orcarouter-bf16-adapter` 연구 검토 후 런타임 적격성/벤치 |
| P6 | Orcarouter↔27B 전환·실패 복구 | **NOT_RUN** | interface only | P5 실제 검증 후 구현·양방향 수용 시험 |
| P7 | 모델/레시피/서비스/프록시/게이트웨이/저장/릴리스 | **NOT_RELEASE_QUALIFIED** | 상태·health·logs 일부 지원; 실행/통합 미완성 | release·복구·수치 게이트·운영자가 승인한 end-to-end 수용 |

**경고:** 백엔드 특정 시나리오 PASS와 설치/운영 UX 전체 수용 PASS는 같은 의미가 아니다. P3 stage-A/B/C는 별도로 승인된 **일회성 단계 수용**이며 일반 운영의 지속 가능한 Flash↔27B 양방향 반복 전환은 아직 구현·실장비 검증되지 않았다.

## 3. Wizard 구현상 확인된 불일치 / 보완

- `wizard/console.py::_stage_actions`: 현재 P3 `stage-a`, `stage-b`, `stage-c`를 선택하면 `module.run([selected, "--plan"])`만 수행하고 **실제 실행은 시작하지 않음**. 실제 C 성공은 `scripts/temporary/p3-stage-c-operator.sh --execute` → canonical `./wizard.sh switch flash-next-27b stage-c --execute` backend 경로. 이것이 사용성 개선의 가장 큰 공백이다.
- `wizard/roadmap.py::readiness_report`: P1–P7의 상태 문자열이 보수적 정적으로 정의되어 P3에 `SWITCH_EXECUTOR_NOT_QUALIFIED`를 계속 표시할 수 있다. 이는 **실제 P3 증거가 틀렸다는 의미가 아니라 대시보드가 증거 기반 최신화되어 있지 않다는 뜻**이다. 원본 receipt를 검증하고 UI/CLI 백엔드·운영 수용·현재 서비스 상태를 별개로 보여주도록 개선한다. 증거 누락 시 성공을 추정하거나 정적 PASS를 하드코딩하지 않는다.
- `docs/MODEL-RECIPE-WIZARD-PLAN.md` 등 과거 운영 계획에는 P2/P3 NOT_RUN 등의 **시점별 과거 사실**이 기록돼 있다. 역사적 계획과 증거는 삭제하지 말고, 최신 headnote로 superseded 상태만 명확히 한다.
- 현재 모델 선택 중심 UX 설계는 `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`, `docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md`에서 확인한다.

## 4. 다음 개발 우선순위 — 서비스 변경 없이 소스 우선

1. **통합 Wizard 운영 UX**: 메인 화면에서 실제 서비스 ID/설치 모델/최신 모델별 Verify·벤치/복구 위험을 보여주고, **모델 선택 → 전환 준비 확인 → 명시적 downtime 승인 → canonical backend 실행 → 실제 API 확인/복구**를 몇 개의 단계로 연결한다. SHA/계획 만료 정책은 백엔드에서 보존하되 중복 조작을 최소화한다. 자동 승인은 금지한다.
2. **반복 가능한 일반 모델 전환**: P3-A/B/C 일회성 acceptance 루틴을 재사용하지 말고 기존 canonical 서비스 전환의 lock/journal/stop-before-start/rollback 원칙을 보존하면서 운영용 실행 계약을 설계한다. 첫 구현은 read-only plan 및 fake-DGX CPU 테스트; 실제 27B 중단은 새 독립 승인 필요.
3. **대시보드/증거**: 실제 P1~P3 수용 증거 기반 status, 최근 API 관측과 과거 수용 기록의 분리, Benchmark metric definition 보존, `reports/` private 0600 append-only, public `benchmarks/published/` allowlist 규칙.
4. **P4 판단 → P5 → P6 → P7**: 원본 Flash 및 27B HF 캐시/컨테이너/이미지 보존; P4는 필요 없으면 NOT_APPLICABLE; Orcarouter vLLM 0.32 자산·런타임·벤치·전환 후 proxy/gateway 운영 통합.
5. **영구 핸드오프 및 CI**: 기존 `feature/recipe-wizard-handoff` Draft PR #1 유지. 테스트 추가, CI 확인, 코드 변경 시 `handoff/{CURRENT-STATE,NEXT-ACTIONS,EVIDENCE-LEDGER,DECISIONS,CHANGELOG,SESSION-START-PROMPT}.md`의 최신 섹션 정합성을 유지. 명시적 승인 없는 PR 머지·GPU 동작·다운타임·데이터 삭제 금지.

## 5. 운영 불변식과 근거 링크

- DGX Spark GB10 / Ubuntu ARM64; vLLM **0.32**; **SGLang 미사용**; **ONE_ACTIVE_MODEL_ONLY**; OpenAI 호환 API **:8000/v1** 고정.
- `./wizard.sh`가 사용자 대상 통합 인터페이스이며, 기존 Python/Shell은 검증된 실행 백엔드로 유지한다.
- `handoff/CURRENT-STATE.md` / `handoff/EVIDENCE-LEDGER.md`: 최신 실제 DGX 경과와 영수증.
- `handoff/OPERATING-RULES.md` / `handoff/DECISIONS.md`: D-016, D-056 등 변경·승인 경계.
- `handoff/NEXT-ACTIONS.md` / `handoff/SESSION-START-PROMPT.md`: 다음 대화 소스 작업.
- `docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md`: 완료된 stage C 운영 이력(복사하여 재실행하는 절차가 아님).
- `benchmarks/published/README.md`: 2개 실제 DGX 원본 SHA 대조를 완료한 공개 가능 수치 요약.
