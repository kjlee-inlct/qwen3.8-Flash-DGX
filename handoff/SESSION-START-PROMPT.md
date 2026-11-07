## 2026-11-07 — P3-A–G EVIDENCE AUDIT / P3-G CLOSED; P8 OWNS FAULT & FINAL RELEASE

**New canonical audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md` and `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`. Stage results: **P3-A/B/C** original immutable one-off real DGX PASS/CLOSED (A Flash→27B, B 27B→Flash, C Flash→27B); **D** real read-only GPU+IPv4/IPv6 host :8000 PID ownership PASS from operator `--sudo-ss` run (pre-latest switch); **E** Flash source `-fp8hybrid` prepared view and versioned draft-field match, but **canonical Flash reinstall recipe UNQUALIFIED** (`DRAFT_REVIEW_REQUIRED`, `launch_allowed=false`); **F** six Fake-DGX/CPU suites **144/144 local PASS**, but `PRODUCTION_LIFECYCLE_RELEASED=false` and generic live install/reinstall not accepted; **G** actual independent 27B→Flash→27B TTY-approved ordinary two-way transfers **REAL PASS/CLOSED** with two receipts, API identities, final 27B `diff=[]`, journal VERIFIED/COMMITTED 28 events, last actual active `qwen38-27b` on port 8000. **P3-A–G aggregate = PARTIAL (E open, F source only)** despite G closed. The user explicitly moved intentional failure injection, automatic restore and final operational/UX/production signoff to **P8** (NEW, NOT_RUN, not authorized to execute). P7 is integration only. Preserve old receipts, model assets and `ONE_ACTIVE_MODEL_ONLY`; no P3 A/B/C/G replays or fault injection to perform this audit. Latest P8-source registration CI [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS 856/856 CPU tests 38 groups (source evidence only). Basic post-switch service manager `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are **NOT PROBED** by that command, not conflicts; do not overclaim fresh D audit. The single-script D–G read-only runner prints G preview even after separate real G PASS by design.

**NEXT SESSION:** Do not rerun P3 A/B/C/G. Their actual DGX evidence is already in audit/report. Current 27B, :8000, recipe diff=[], committed journal. Work remaining: P3-E Flash reinstall-ready canonical recipe and true qualification, P3-F generic lifecycle production gating, optional P4 then P5/P6/P7; P8 exclusively owns controlled fault/automatic restoration and full operating release. P8 CLI is read-only BLOCKED and not permission to inject failure. Use `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`, `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md` and `docs/P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md` before acting.

---

## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

**RESUME P3-G WITH LIVE FLASH-NEXT**: Actual guarded 27B→Flash-Next one-off PASS and receipt exists at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json` (operator-provided path). API status LIVE_SERVICE_VERIFIED for qwen3.8-flash-next port 8000; journal VERIFIED/COMMITTED event_count21. Never restart forward trial or assume old 27B is live. **NEXT:** new independent Flash→27B read-only acceptance plan, then operator real TTY with 4 exact current prompts and new SHA; postcheck. Reverse/failure recovery NOT_RUN. Do not replay P3-A/B/C, force delete/recreate model or mark G fully released. See `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`.

---

## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

**P3-G downtime permission granted by user in conversation**, but real 27B→Flash and reverse have NOT occurred as of this handoff. Latest DGX read-only D-G: D verified GPU/:8000 process ownership, E preserved FP8hybrid source-draft all documented fields match (`MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED`), F 144/144 local CPU tests, G preview pass; `P3_DG_EXIT=0` only for read-only. Need real operator interactive `scripts/temporary/operational-switch-acceptance.sh --target flash-next --plan --json` → `--target flash-next --execute`; require four fresh exact TTY approvals, avoid automatic transfer, inspect receipt and journal before reverse. P3-G plan/test instructions in `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`. P3-A/B/C closed. No production release or image/cache deletion.

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

## 2026-11-07 — FIRST DGX D-G RUN: D/E BLOCKERS; FIXED SOURCE AWAITING READ-ONLY RETEST

First actual DGX unified `--run`: D BLOCKED `HOST_PORT_8000_LISTENER_NOT_UNAMBIGUOUS` despite `gpu_process_exclusivity_verified=true`, E BLOCKED Flash parser + unqualified canonical Flash reinstall recipe, F local 119/119 CPU PASS, G verified operating journal/current-IDs PREVIEW PASS. Subsequent GitHub SOURCE fixes support dual-stack IPv4/IPv6 sockets, exact Docker proxy /proc-to-container-IP provenance, legacy Flash raw command inventory and writable mount review. CI 42371091647 **838/838 CPU PASS, 37 groups**. Actual DGX rerun not yet seen; do not call D/E real PASS or G real switch PASS. Next on clean DGX: `bash scripts/temporary/p3-d-g-acceptance.sh --run --report /tmp/p3-d-g-readonly-v2-$(date +%Y%m%dT%H%M%S).json`. Read `docs/P3-D-G-FIRST-DGX-DIAGNOSTIC-FIXES-20261107.md`. Do not replay P3 A/B/C or mutate current 27B.

---

## 2026-11-07 — NEW OFFICIAL P3-D/E/F/G AND SINGLE-SCRIPT DRAFT

User explicitly mapped four general Wizard operating tasks to P3-D/E/F/G, following permanently CLOSED P3-A/B/C. New one-command local runner: `bash scripts/temporary/p3-d-g-acceptance.sh --run --report /tmp/unique-p3-dg.json` after fast-forwarding `feature/recipe-wizard-handoff`. Implements D Docker/ss/nvidia-smi/proc read-only ownership, E Flash preserved Docker candidate and missing qualified recipe gate, F automatic CPU/Fake-DGX suites, G read-only switch/journal readiness; distinct verdicts and `acceptance_complete=false`. The batch must NOT call Docker mutation, automatically approve a downtime SHA, execute P3-A/B/C again, or claim real G PASS. Read `docs/P3-D-G-UNIFIED-WIZARD-DRAFT-ACCEPTANCE-20261107.md`. P4 optional Flash removal, P5 Orcarouter, P6 Orcarouter↔27B, P7 integration; keep existing PR #1 Draft and unmerged.

---

## 2026-11-07 — LATEST OPERATOR READ-ONLY DGX PREVIEW PASS ON SOURCE 4189a79

A second operator DGX read-only run after source `4189a79` verified canonical 27B `diff=[]`, `advisories=[]` with explicit HF source; `switch flash-next-27b operational --target flash-next --plan --json` now returns `READY_FOR_OPERATOR_REVIEW_ONLY`, `issues=[]`, `current_ids_from_live_docker=true`, source lineage `CANONICAL_RECIPE`, target lineage `HISTORICAL_P3_INSTANCE`. API remains `LIVE_SERVICE_VERIFIED`. **No actual DGX mutation/transfer**, no GPU process exclusivity or process-level port ownership verified, and no production switch gate unlocked. Evidence and next priorities: `docs/WIZARD-27B-OPERATIONAL-PREVIEW-DGX-PASS-20261107.md`, `handoff/NEXT-ACTIONS.md`. Last SOURCE CI 814/814 CPU Fake-DGX PASS run 42367665200; PR #1 still Draft. Do not re-run P3 A/B/C or assume approval from preview fingerprint.

---

## 2026-11-07 — LATEST UPDATE: READ-ONLY DGX MATCHED AND CURRENT-ID SWITCH SOURCE READY

Actual user DGX read-only Wizard after 5456eae: 27B canonical `diff=[]`, `LIVE_SERVICE_VERIFIED`, observed host cache `/home/inlc/.cache/huggingface`, no reboot/switch/recreate. New source uses fresh current Docker IDs in ordinary switch, validates canonical 27B settings, keeps P3 A/B/C receipts immutable, and adds optional `--cache-source` READ-ONLY comparison. GitHub source CI 42367665200: **814/814 PASS**, 36 suites. No real operating switch or release. Read `docs/WIZARD-27B-LIVE-DRIFT-CURRENT-ID-20261107.md` first; next DGX commands are READ-ONLY `model 27b recipe-diff --cache-source /home/inlc/.cache/huggingface --json` and `switch flash-next-27b operational --target flash-next --plan --json`. Old generic lifecycle baseline status below is historical; keep source vs real PASS boundaries. The existing PR #1 remains Draft, do not merge.

---

## 2026-11-07 — UPDATE TO CURRENT NEW CONVERSATION STARTER: SOURCE IMPLEMENTATION ALREADY COMMITTED

The generic 27B recipe diff, read-only Wizard lifecycle interface and gated lifecycle/rollback transaction scaffold now exist in scripts/manager/recipe_drift.py and scripts/manager/model_lifecycle.py. New CPU/Fake-DGX tests are included in GitHub workflow; latest confirmed run 42355750124 **799/799 PASS in 36 groups**. This is NOT actual DGX lifecycle qualification; both generic lifecycle and ordinary production switch gates remain False. Before starting a new session, inspect live GitHub HEAD, PR #1, CI and docs/WIZARD-LIFECYCLE-SOURCE-IMPLEMENTATION-20261107.md. Highest priorities: current DGX read-only recipe comparison, preserve exact 27B recipe SHA, upgrade old P3 live-ID assumptions, qualified Flash recipe, backup cleanup and benchmark publication, separate DGX acceptance. Do not redo already real-PASS P2-FINAL/P3-C or infer these are re-opened. Older starter text below represents the prior implementation handoff.

---

# CURRENT NEW CONVERSATION STARTER — 2026-11-07 (canonical, supersedes older P2-FINAL starter)

**Copy the complete prompt immediately below.** The history following the separator is archived context and must NOT override newer DGX evidence or the user-approved model uninstall/reinstall policy. Standalone source: [START-NEXT-WIZARD-LIFECYCLE-20261107.md](START-NEXT-WIZARD-LIFECYCLE-20261107.md).

---

# New Conversation Starter — Blazux DGX Spark / Wizard 레시피 차이 감지·모델 수명주기 통합

이전 대화에서 이어서 **실제 소스 개발과 GitHub 커밋**을 진행해주세요. 이 프롬프트는 새로운 대화에서 독립적으로 사용하기 위한 최신 인수인계입니다. 단순히 계획만 작성하지 말고, GitHub 연결 도구로 최신 상태를 조사하고 소스·테스트·문서 구현 및 기존 브랜치 커밋까지 수행하세요. 실제 DGX 서비스 변경은 별도 운영자 승인 없이 하지 마세요.

## 1. 저장소 / 운영 환경 / 절대 원칙

- GitHub: https://github.com/kjlee-inlct/qwen3.8-Flash-DGX
- Branch: feature/recipe-wizard-handoff
- Existing PR: #1 Open / Draft / Unmerged. 유지; 사전 승인 없이 새 PR 생성/머지 금지.
- Parallel branch: feature/orcarouter-bf16-adapter; upstream: https://github.com/blazux/qwen3.8-Flash-DGX
- Real DGX directory: ~/Workspace/llm/blazux-orcarouter
- Device: NVIDIA DGX Spark / GB10 / Ubuntu ARM64.
- API: OpenAI-compatible :8000/v1. 모델 하나만 활성(ONE_ACTIVE_MODEL_ONLY).
- Engine: **vLLM 0.32.0 고정**, SGLang 사용하지 않음.
- 사용자 인터페이스: ./wizard.sh
- GitHub 최신 HEAD는 새 대화 시작 즉시 조회. 참고로 문서 감사 전 HEAD는 9ec7420b74369e7a76785577dc543f9dafb8897d였고 이후 문서 커밋이 추가됨.
- 최신 확인된 소스-only GitHub CI: run 42352654468 SUCCESS, **757/757 CPU 테스트, 34개 그룹**. CPU CI는 실제 GPU/서비스 시험이 아님.
- 새 대화 시작 시 GitHub 연결 도구로 **실제 최신 HEAD/PR/CI/변경 내역**을 조회한 뒤 판단하라.

## 2. 읽어야 할 영구 문서

1. handoff/README.md
2. handoff/CURRENT-STATE.md
3. handoff/OPERATING-RULES.md
4. handoff/NEXT-ACTIONS.md
5. handoff/EVIDENCE-LEDGER.md
6. handoff/DECISIONS.md
7. handoff/CHANGELOG.md
8. handoff/SESSION-START-PROMPT.md
9. docs/HANDOFF-DOCUMENT-AUDIT-20261107.md
10. docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md
11. docs/P2-27B-CANONICAL-NATIVE-RECIPE-LIVE-PASS-20261107.md
12. docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md
13. docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md
14. docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md
15. docs/MODEL-RECIPE-WIZARD-PLAN.md
16. docs/UNIFIED-MODEL-WIZARD-DESIGN.md
17. docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md
18. docs/MANIFEST-CONTRACTS.md
19. docs/WIZARD-CLI-CONTRACT.md
20. docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md
21. recipes/README.md
22. scripts/temporary/README.md
23. benchmarks/published/README.md

이전 문서가 과거 HTTP 400, P2-FINAL NOT_RUN, 기존 컨테이너 절대 삭제 금지 등을 말해도 **2026-11-07 최신 실측 및 사용자 결정이 우선**이다. 과거 로그는 역사적 증거로 보존하되 최신 상태와 혼동하지 말 것. 위 필수 문서 25개와 두 벤치마크 디렉터리 존재 여부는 감사함. 각 내용의 완전성/상호 정합성은 새 세션에서도 확인할 것.

## 3. 실제 DGX에서 이미 완료된 시험 — 재실행하지 말 것

**P1 Flash-Next**: NVIDIA Qwen3.8-Flash-Next-NVFP4 revision fc694b54fb0174e0913e6adf86691ef85a4ead47. 실제 API 기능·Chat·Completions·Tool·Vision·Verify·Benchmark PASS. P3-B 이후 재검증 및 공개 메트릭 존재.

**P2 원본 27B**: NVIDIA Qwen3.8-27B-NVFP4 revision 482ca0f3832238542f8f5295dde86b5f22711d80; ModelOpt modelopt_mixed, vLLM 0.32.0, 초기 GPU trial, chat/API, 기존 3회 벤치마크, 원복 PASS.

**P3-A/B/C**: Flash→27B, 27B→Flash, Flash→27B 각각 REAL DGX PASS. **P3-C 일회성 Stage-C 완료/보존**; stage-c.json 등 기존 증거/영수증 삭제·수정·재실행 금지. 과거 일반 운영 양방향 백엔드 실측도 PASS했으나, 이후 27B 정식 컨테이너 **ID가 새로 변경**되었음. 옛 P3 영수증 ID를 현재 Docker ID로 취급하지 말 것. 반복 가능한 일반 Wizard 정식 전환 릴리스와 실제 메뉴/강제오류 복구 시험은 별도 미완료.

**P2-FINAL Native Tools**: 과거 기존 27B에서 --enable-auto-tool-choice 및 parser 누락으로 HTTP 400이 발생했으나 **이미 해결됨**. 정식 기본 레시피 recipes/qwen38-27b.runtime.json에 --chat-template (NVIDIA pinned Jinja), --enable-auto-tool-choice, --tool-call-parser qwen3_coder, --reasoning-parser qwen3를 반영하고, 원본 27B를 새 컨테이너로 실제 재생성함. 정상 Chat, 구조화된 tool_calls, Tool Result 연속 처리, SSE streaming 모두 실측 PASS. 벤치마크 v2: 3/3 PASS, client mean E2E **10.9570 tok/s**, decode proxy **11.0918 tok/s**, TTFT P50 **0.165412 s**, latency P50 **11.597904 s**. 128토큰 상한 때문에 2개 요청 finish_reason=length였으므로 응답 완결성 전체 PASS라고 확대 해석하지 말 것. **Open WebUI Native 실제 동작도 사용자가 확인 완료.** 최신 벤치마크 포인터 갱신, 예전 원본 27B 백업 컨테이너는 검증 뒤 삭제. 신규 27B 컨테이너 ID 00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a.

**Wizard manifest cleanup**: 다음 중지된 두 테스트 컨테이너를 정확한 name/ID/labels/영수증 검증, 별도 SHA·TTY 승인으로 REAL DGX 삭제 완료.
- qwen38-27b-failed-6d9ede0904c2
- qwen38-27b-native-tools-v1
실제 cleanup --execute 및 독립 cleanup --status 모두 MANIFEST_RETIRED_CONTAINERS_CLEANED, issues=[], remaining=[], live 27B preserved. 완료 receipt: result-39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5.json (private DGX). 이 두 컨테이너를 재삭제하거나 실패한 과거 플랜 SHA를 재사용하지 마라. service manager cleanup --plan은 최신 GitHub 소스에서 ALREADY_CLEANED로 no-op이어야 한다.

**현재 마지막 DGX 실제 상태**: qwen38-27b Up, qwen38-flash Exited, open-webui healthy, portainer Up. 활성 API qwen3.8-27b, port 8000, service manager status LIVE_SERVICE_VERIFIED/issues=[]. ordinary operational_audit VERIFIED/COMMITTED/14 events (마지막 알려진 hash ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e). gpu_exclusivity_verified=false/port_process_ownership_verified=false는 **그 읽기 전용 상태 명령에서 추가 증명하지 않은 항목**이지 충돌이 관측됐다는 뜻이 아님. 현재 상태는 새 증거로 다시 확인해야 하며 임의로 단정하지 말 것.

## 4. 최신 사용자 결정과 우선 개발 목표

**이제 P2 Native Tool Calling HTTP-400 수정이 아니라 Wizard의 통합 모델 관리 기능 개발을 시작한다.**

메인 목표: 모든 모델에 대해 **레시피 변경에 따른 실제 컨테이너 차이를 비교하고**, Wizard에서 start/restart/switch/install/reinstall/remove를 실행할 때 다음 정책을 적용.

1. 각 모델의 desired recipe, installed/active runtime, 실제 Docker inspect, 매니페스트, GPU/port/served model ID, 최신 시험·벤치마크 수용 상태를 명확히 보여줘라.
2. 현재 Docker Config.Cmd / image digest / model checkpoint revision / readonly HF cache mount / Env / port 8000 / GPU request / parser / quantization / GPU memory / context / labels와 정식 **versioned recipe**를 정규화해 비교하라. 의미 있는 차이만 drift로 판정하고 사용자가 어떤 설정이 달라졌는지 보여줘라.
3. **동일 레시피:** 기존 컨테이너를 안전하게 재사용할 수 있다면 불필요한 재생성 금지. **레시피 drift:** 단순 docker restart로 옵션이 반영된 것처럼 표현하지 말고 중단 → 기존 컨테이너 롤백용 rename → 정확한 recipe로 같은 정식 이름 재생성 → API·일반 Chat·해당 모델의 Tool/SSE·필요 시 새 Benchmark → PASS 후 최신 운영 기준 갱신 → 명시적 허용 시 백업 컨테이너 삭제. 실패 시 원본 복구·불확실 상태 차단.
4. 서비스가 없으면 설치, 있으면 재시작 또는 변경 비교, 삭제됐으면 동일 레시피로 재설치 가능해야 함. **qwen38-27b와 qwen38-flash를 전역 삭제 불가 모델로 하드코딩하지 말라**. 단, 실제 실행 시 현재 활성 서비스 다운타임·GPU/port 소유권·재설치 절차와 정확한 대상 승인 필수.
5. 일반 모델 삭제/재설치와 과거 두 테스트 컨테이너를 정리한 **일회성 retirement batch**를 구분. 삭제 이력은 매니페스트·영수증에 보존하되 이미 완료된 작업을 pending으로 다시 표시하지 말라.
6. 과거 P3-A/B/C 영수증은 불변의 역사적 증거. 새 27B Docker ID로 업데이트하면서 **옛 영수증을 덮어쓰거나 재활용하지 말라**. 현 상태 판단은 새 Docker inspect + 서비스 매니페스트 + 새로운 실행 저널·증거에 근거해야 한다.
7. 기존 일반 모델 전환의 production flag **PRODUCTION_EXECUTION_RELEASED=False**는 정식 실제 DGX 수용 전 해제하지 말라. 한 대에서 동시에 GPU 모델은 하나만, 포트는 8000 고정.
8. 27B 정식 runtime recipe는 현재 성공한 벤치마크 포인터가 **레시피 전체 SHA에 바인딩**되어 있으므로, 보기 좋게 필드만 수정해도 drift가 된다. 수정하려면 새 버전/해시/검증·증거 갱신 경로를 계획하라. Flash-Next도 실제 실측에 대응하는 정식 실행 레시피가 없으면 먼저 검증 가능한 레시피를 만들라. Orcarouter는 검증 전 서비스 기동 금지.

## 5. 반드시 검토할 실제 코드

- wizard/main.py, wizard/console.py, wizard/menus/operations/service.py
- scripts/manager/service_manifest.py, scripts/manager/service_status.py
- scripts/manager/operational_wizard.py, scripts/manager/operational_switch.py
- scripts/manager/operational_executor.py, scripts/manager/operational_acceptance.py, scripts/manager/operational_audit.py
- scripts/manager/p2_27b_recipe_migration.py, scripts/manager/manifest_cleanup.py
- scripts/manager/p2_27b_benchmark.py, scripts/manager/p2_27b_tool_calling.py, scripts/manager/p2_27b_tool_streaming.py
- recipes/qwen38-27b.runtime.json, runtimes/service-policy.json, runtimes/model-discovery.json
- tests/test_manifest_cleanup_cpu.py 및 관련 Wizard/서비스 회귀 테스트
- .github/workflows/recipe-manifest-cpu.yml

기존 코드를 읽기 전에 함수명·상태값·CLI가 있을 것으로 추정하지 말고 실제 파일을 조회하라.

## 6. 수행 우선순위와 수용 기준

**P0 — 실제 상태 감사:** 최신 GitHub HEAD/PR/CI, 영구 문서와 source, 새로운 DGX 로그가 있다면 최신 실측 증거를 검증. 무엇이 소스-only/실기 PASS/NOT_RUN/NOT_RELEASED인지 명시.

**P1 — 범용 recipe diff + manifest:** 모델별 desired/observed/installed/active/retired 식별, versioned recipe SHA, 실제 container identity와 과거 P3 ID 분리. 읽기 전용 CLI 및 UX 구현.

**P2 — 범용 Wizard lifecycle 구현:** install, remove, reinstall, restart, switch, same-name recreate; match=no-op, drift=plan+approval, stop-before-start, rollback, benchmark qualification and one-active-model policy. 코드·테스트·문서 직접 커밋.

**P3 — 독립 검증:** CPU/Fake-DGX 사례: 동일 recipe/no-op, drift in parser, image, mount, revision, env, host port, GPU request; container missing/stopped/running, fresh/expired SHA, TTY approval, cancellation, port conflict, foreign GPU, crash/stop/start fail, api/model mismatch, benchmark failure, rollback PASS/FAIL, private receipt corruption, cleanup repeat no-op, previous ID retention, menu regression. GitHub CI 결과와 테스트 개수 확인.

**P4 — 실제 DGX 수용:** 안전한 읽기 전용 계획을 Git에서 추적할 수 있는 스크립트로 전달. 실장비에서 컨테이너 stop/recreate/remove/benchmark는 반드시 **별도 운영자 승인**을 요청하는 실행 경로를 사용. 새로운 실행 영수증과 사후 Docker/API 상태를 확보한 뒤에만 LIVE PASS 판정.

**이후 단계:** 원래 P4 저장공간 정리, P5 Orcarouter BF16 PLE 구동·Benchmark, P6 Orcarouter↔27B 전환, P7 서비스/프록시/게이트웨이 통합 운영. 사용자의 "두 번째 27B Native Tools 레시피 시도 실패 시 P8 이관" 조건은 두 번째 실제 시도가 **성공**해 활성화되지 않았음. P8을 현재 미완료로 오해하지 말라.

## 7. GitHub, 문서, 실기 안전 운영 규칙

- GitHub connector를 통해 작업 브랜치 HEAD·PR #1·CI·파일을 먼저 확인하고, 직접 파일 생성/수정/커밋 및 필요 시 Draft PR 검토 내용을 갱신한다. 기존 브랜치/PR 유지. PR merge나 새 PR은 사용자의 별도 승인 필요.
- 핸드오프 문서 CURRENT-STATE, OPERATING-RULES, NEXT-ACTIONS, EVIDENCE-LEDGER, DECISIONS, CHANGELOG, SESSION-START-PROMPT와 해당 docs/tests/scripts/manifest를 진행에 따라 갱신한다. 누락된 계약 문서가 있으면 새로 만든다.
- 이전 성공한 P1/P2/P3 실측을 근거 없이 반복하지 않는다. 단, **새로운 레시피나 새 컨테이너**의 별도 수용 시험은 필요할 수 있다.
- 원본 HF checkpoint/cache, pinned Docker 이미지, old historical P3 and original benchmark receipts, active Open WebUI/Portainer, normal API :8000을 의도 없이 변경하지 않는다. 이것은 **아예 모델 컨테이너 삭제가 금지**된다는 뜻이 아님: 승인된 모델 수명주기 제거/재설치는 지원해야 한다.
- Docker prune, git reset --hard, git clean -fd, model image/cache 삭제, 무승인 모델 중단·전환, obsolete 계획 SHA 재사용, 승인 문자열 자동 입력, CPU PASS를 DGX PASS라 주장, 승인 없는 PRODUCTION_EXECUTION_RELEASED 변경은 금지.
- 실제 DGX 로컬 작업은 작업 트리를 확인한 다음 git pull --ff-only origin feature/recipe-wizard-handoff. 가능한 한 임시 CLI 코드를 복사·붙여넣기하도록 하지 말고 Git 추적 가능한 Wizard/스크립트로 제공.
- 불확실한 상태에서는 먼저 읽기 전용 감사; 실패 시 동일 mutation blind retry 금지. 과거 완료된 두 테스트 컨테이너 정리 CLI execute는 재실행하지 말 것.

## 8. 다음 대화에서 요구하는 보고 형식

1. WHAT CHANGED — 실제 구현/수정한 파일, 기능, 아직 미지원
2. GITHUB — 최신 HEAD, 브랜치, PR Draft 상태, CI/테스트 건수, 커밋
3. CURRENT REAL DGX — 마지막 사용자 실측 서비스/모델/포트/컨테이너와 증거
4. RECIPE/MANIFEST DRIFT — 비교 로직, 설치·재설치/삭제 지원, Docker ID 이력 분리
5. SAFETY / TEST — no-op, 승인, 롤백, 벤치마크, Docker/GPU 독점, 장애 시 차단
6. STAGE STATUS — P1·P2·P2-FINAL·P3-C 이미 PASS, 일반 Wizard production UX 미릴리스, P4~P7, P8 조건부 비활성
7. NEXT ACTIONS — 즉시 수행할 코드 작업, DGX 읽기 전용 점검, 별도 실기 승인 필요 부분

**이번 새 대화의 첫 작업:** GitHub에서 실제 최신 HEAD/PR/CI와 위 필수 문서를 확인한 뒤, `docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md`를 기준으로 **Wizard 범용 모델 레시피 차이 감지 및 설치·삭제·재설치·재생성 관리 기능** 개발을 직접 시작하고, 테스트·문서·커밋을 진행하세요. P2 Native Tool Calling HTTP 400은 이미 해결됐으며 P3-C는 완료 상태이므로 과거 작업부터 재시도하지 마세요.


---

# ARCHIVED OLDER SESSION PROMPTS — HISTORICAL REFERENCE ONLY

## LATEST REAL DGX — 2026-11-07 Wizard manifest cleanup actually executed and VERIFIED: two historical test containers REMOVED

**Operator-provided real DGX terminal stdout** after fast-forward to `9518f25e614367ab0ebbb725d7568e5c6bf177ed`: `./wizard.sh service manager inventory --json` listed original canonical `qwen38-27b` active on :8000 and two retired stopped containers. `./wizard.sh service manager cleanup --plan` returned `READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL`, `issues=[]`, target_count=2, plan `39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5`, active container full ID `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`. User then supplied exact fresh SHA and both TTY approvals to `./wizard.sh service manager cleanup --execute`, which returned **`MANIFEST_RETIRED_CONTAINERS_CLEANED`**, `executed=true`, `issues=[]`, `remaining=[]`, `preserved_original_model_service=true`, `preserved_images_and_caches=true`. Exact removed names and Docker IDs:
- `qwen38-27b-failed-6d9ede0904c2` → `44920f80610c5787f7d72064269be175d18150fe68d5a2fe846499129fc596bc`.
- `qwen38-27b-native-tools-v1` → `d42a15e2f7959829eeb616d748522193999441c9f418ec5dcae98931dfe5da56`.

**INDEPENDENT POSTCHECK PASS:** `./wizard.sh service manager cleanup --status` → `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, `remaining=[]`, `active_service_preserved=true`, private immutable receipt `result-39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5.json`. `./wizard.sh service manager status --json` → `LIVE_SERVICE_VERIFIED`, `API_IDENTITY_CONFIRMED`, `issues=[]`, served model ID `qwen3.8-27b`, port 8000. `docker ps -a` lists ONLY running `qwen38-27b`, stopped `qwen38-flash`, running `open-webui` (healthy) and `portainer`. The status tool's `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are untested scopes, not observed conflicts. No separate file-by-file HF checksum check done; cleanup code only removed stopped Docker containers.

**SOURCE/HANDOFF UPDATE (AFTER this real run):** `docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md` contains complete actual-evidence breakdown. `runtimes/service-policy.json.retired_containers.completion` now records consumed plan, exact removed Docker IDs, verified active ID and immutable result pointer; historical target descriptions remain in place **for provenance, not as a pending deletion queue**. `scripts/manager/manifest_cleanup.py` now requires exact Git-tracked completed metadata + matching local 0600 immutable receipt + actual Docker target absence + current canonical API health before reporting DONE. Its `--plan` returns **`ALREADY_CLEANED` without a new approval SHA** when this is all verified; any mismatch blocks, never blindly deletes. The new source did not mutate DGX. Completion is authoritative only when live Docker/receipt agrees, not because Git says so.

**USER POLICY CLARIFICATION:** `qwen38-27b` and `qwen38-flash` are VALID removable/reinstallable managed model services, not globally protected from user-approved uninstall. This one-off cleanup never deleted either. General Wizard uninstall/reinstall, recipe-diff-aware restart/recreation and 27B↔Flash current-ID-aware switching remain NOT_IMPLEMENTED/NOT_RELEASED even though canonical 27B Native Tools real DGX migration + benchmark v2 and Open WebUI Native passed. P3-C historical real PASS closed; P8 conditional ticket inactive. Keep vLLM 0.32, one GPU model active, API port 8000, pinned checkpoint/cache, original P3/benchmark receipts and Draft PR #1 unmerged.

**No further DGX action necessary for retired-container cleanup.** If operator wants a read-only check after pulling this new source: `./wizard.sh service manager cleanup --status`; repeated `--plan` should report `ALREADY_CLEANED` (exit code 3, non-action; use status for success). **Do not run `--execute` again**.

---

## LATEST — 2026-11-07: Wizard manifest-owned retirement of two stopped test containers; canonical models ARE removable/reinstallable

**NEW USER CLARIFICATION (higher-priority than older blanket language):** Do NOT impose a permanent deletion prohibition on `qwen38-27b` or `qwen38-flash`. Both are **operator-removable and reinstallable** Docker model services, as managed model lifecycle policy now records in `runtimes/service-policy.json` `models.*.container_lifecycle`. A future general uninstall/reinstall or recipe-diff-aware recreate command requires its own scoped approval, downtime and qualified reinstall recipe; merely setting lifecycle policy does NOT mean that general Wizard executor has been implemented. For the current user-requested batch, **only** two named stopped historical DGX test containers are selected: `qwen38-27b-failed-6d9ede0904c2` and `qwen38-27b-native-tools-v1`. This is operation-specific scoping, **NOT a global ban on deleting other models**.

**Source committed, real DGX execution NOT RUN:** `runtimes/service-policy.json.retired_containers.targets` now registers exact names, original test provenance labels/known IDs, observed vLLM image, immutable local receipt paths, and cleanup lifecycle policy. `scripts/manager/manifest_cleanup.py` implements read-only `plan` (matches live canonical 27B Native Tools promoted recipe/benchmark, exact stopped target IDs, labels, read-only HF cache, result/evidence history, no foreign GPU owners), fresh exact SHA + two independent TTY approvals, and deletion of **only these two stopped Docker containers** through `docker rm`; no images, checkpoint files, HF cache, historical P3 receipts, or benchmarks deleted. A private immutable attempt/result receipt blocks blind partial-retry. Post `status` requires actual target absence plus live canonical service verification. Routed through **`./wizard.sh service manager cleanup --plan` / `--execute` / `--status`** and interactive Wizard → service menu → cleanup. `scripts/manager/service_manifest.py` read-only inventory now exposes `managed_container_lifecycle`, `retired_container_inventory`, manifest names, distinguishing desired policy from Docker observed state. Existing numeric service-menu shortcuts are preserved. Testing is source-only Fake-DGX, not real removal.

**Actual before-state:** user supplied second live canonical recipe migration `COMMITTED` all Native Tools/SSE, three-request benchmark v2 PASS (mean E2E 10.957 tok/s; TTFT P50 0.165412s), new container `qwen38-27b` and independent `LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED`, `LIVE_SERVICE_VERIFIED`, old backup container deleted. User separately confirmed **Open WebUI Native success**. Stopped forensic containers remain present until operator executes new cleanup plan; also stopped `qwen38-flash`. Keep stopped Flash as currently unselected; it remains deletable separately by a future appropriately scoped lifecycle action. P3-C historical PASS/closed, normal Wizard repeatable switch/reinstall recipe-diff code remains distinct unfinished work; old P3 IDs must not be recycled as live authority. P8 conditional migration ticket remains INACTIVE because second canonical recipe migration succeeded.

**New operator next actions (no automatic Docker mutation on Git pull):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager inventory --json
./wizard.sh service manager cleanup --plan
```
Require exact two stopped target names, `READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL`, `issues=[]`. Only then separate TTY `./wizard.sh service manager cleanup --execute` with new SHA and `I_APPROVE_MANIFEST_TWO_STOPPED_CONTAINERS_ONLY` / `I_CONFIRM_ACTIVE_27B_AND_ALL_MODEL_EVIDENCE_PRESERVED`. Finally `./wizard.sh service manager cleanup --status`, `./wizard.sh service manager status --json`, `docker ps -a`. No claim of deletion until actual DGX stdout. If BLOCKED, inspect source provenance rather than bypassing.

Permanent runbook: `docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-20261107.md`. User specifically rejects a hard-coded “canonical 27B and Flash can never be deleted” policy. Keep global uninstall ability possible; current cleanup's exact two-target allowlist is intentionally scoped.

---

## 2026-11-07 — Immediate DGX v2 RETRY authorized as next operator action; P8 contingency and P3-C closure boundary

User instruction: **Proceed to second REAL DGX canonical NVIDIA 27B Native Tools recipe migration test immediately after Git Pull and guarded read-only recovery audit**. User expressly does not require waiting for Fake-DGX CI. This is NOT permission to bypass existing irreversible attempt markers or TTY approval. Previously consumed first migration plan **01702fa1b0901a0dce7517ccbaee133fc253058a1c07abe63bc00c42bec52a15** returned REAL `FAIL_RESTORED`, `native_tools_pass=true`, `benchmark_pass=false`, and `original_restored=true`; independent current Docker/API postcheck has not been furnished. No second DGX run result exists yet.

External GitHub source comparison: [MiaAI-Lab start.sh](https://github.com/MiaAI-Lab/Qwen3.8-27B-DGX-Spark-RTX-6000/blob/main/start.sh) and [styles01 27B recipe](https://github.com/styles01/sparkrun-recipes/blob/main/recipes/qwen-38-27b.yaml) use **different unsloth checkpoint, compressed-tensors, patched/nightly image, sometimes MTP and FP8 KV**. These are **NOT** substituted for our proven pinned NVIDIA nv-community `nvidia/Qwen3.8-27B-NVFP4` / vLLM 0.32.0 `modelopt_mixed` container. `qwen3_coder` / `qwen3` / explicit per-request non-thinking mode are supported by both and already real-DGX tool/SSE tested. Additional [CloudRift vLLM 0.32.0 NVFP4](https://github.com/cloudrift-ai/emmy/blob/main/recipes/Qwen3.8-27B-NVFP4/RESULTS.md) supports parser/benchmark separation but is RTX5090, not GB10. Detailed analysis: `docs/P2-27B-EXTERNAL-RECIPE-RESEARCH-20261107.md`.

**NEW v2 source-only request profile:** `recipes/qwen38-27b.runtime.json` pins `benchmark.version=p2-27b-native-tools-canonical-benchmark-v2`, 3 sequential SSE requests, output cap **128 tokens**, `chat_template_kwargs={"enable_thinking": false}`, temperature 0 and seed 1234, with no literal informal `/no_think` suffix, preserving historical benchmark v1 and production thinking capability. The migration executor verifies benchmark-v2 version, prompt settings, samples and throughput before replacement/promotion; stores complete per-sample diagnostics BEFORE any fail-restore. No claims of successful v2 throughput until actual DGX stdout.

**IMMEDIATE DGX workflow:** `git pull --ff-only origin feature/recipe-wizard-handoff` → current service status/ordinary journal → `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --audit-failure`; require `PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY` and no issues; then manual TTY `--reconcile` (exact old failed SHA + phrase), `--plan` (new SHA, v2 benchmark profile, no issues), and only under NEW downtime and backup-deletion acknowledgements `--execute`. `--status` plus service status after test. If the audit is blocked, STOP; no manual bypass, deletion, old P3-C replay or uncontrolled third execution. GitHub CI is not a prerequisite per the user, but source itself is not a real DGX test.

**Explicit contingency:** IF the second **executed** DGX migration FAILS again, move remaining P2/P3-related canonical Native Tools recipe+benchmark rollout to **P8**, do not continue repeated P2/P3 tests now. Keep P1/P2 original baseline and P3-A/B/C historical real PASS immutable. **P3-C historical Stage-C was already completed at 2026-11-07 10:19:39 KST with `P3_C_PASS_FINAL_27B_ACTIVE`**. Finalize/ARCHIVE this stage without rerunning it; unrelated interactive Wizard production release stays OFF. Conditional tracker: `docs/P8-27B-NATIVE-RECIPE-DEFER-IF-V2-FAIL-20261107.md` is **INACTIVE/PENDING** until actual second result; DO NOT falsely mark P8 active before new output. If second FULL `COMMITTED` with benchmark and backup cleanup PASS, keep P8 inactive. Any `RECOVERY_FAILED` requires physical recovery first, regardless of backlog.

---

## 2026-11-07 — REAL DGX canonical Native Tools migration 1st attempt FAIL_RESTORED; BENCHMARK diagnostic and reconciliation fix

**Most recent actual DGX operator output:** TTY-approved `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --execute` consumed fresh plan `01702fa1b0901a0dce7517ccbaee133fc253058a1c07abe63bc00c42bec52a15`. JSON returned `status=FAIL_RESTORED`, `executed=true`, `native_tools_pass=true`, `benchmark_pass=false`, `benchmark_promoted=false`, `backup_container_deleted=false`, `original_restored=true`, `issues=["MIGRATION_ERROR_NEW_CANONICAL_BENCHMARK_NOT_QUALIFIED"]`. **Actual service independently checked AFTER this failure: NOT YET provided.** This is a real DGX Native Tools pass followed by an unsuccessful new 3-sample performance acceptance test and attempted original restore, **NOT a successful canonical migration**. Do not delete containers/cache/benchmark receipts or re-run the used SHA.

**Root-cause evidence boundary:** In the initial migration code, `p2_27b_benchmark.measure()` returned a structured measurement dictionary, then the caller rejected its acceptance criteria. The caller discarded `samples` and `metrics` before writing the immutable failure report. Therefore the actual failed sample or reason **cannot be reconstructed from the provided output**; not evidence of GPU/model inference failure. The benchmark also used legacy `/no_think` prompt text rather than explicit `chat_template_kwargs={"enable_thinking":False}` which the **successful Native Tools probe uses**. This is a plausible cause but NOT established. Avoid falsely claiming actual latency/TPS.

**Source remediation:** `scripts/manager/p2_27b_benchmark.py` now accepts opt-in pinned nonthinking kwargs while preserving historical defaults and captures per-sample `usage_reported`, `content_observed`, `reasoning_observed`, `stream_finish_reason`, exact failure reason codes, TTFT, tokens and sampled metrics (no generated text). `scripts/manager/p2_27b_recipe_migration.py` opts in to explicit `enable_thinking=false` and writes private immutable `benchmark-observed-<NEW SHA>.json` plus a `BENCHMARK_MEASURED` journal event **before** checking pass/rolling back. Result now includes `benchmark_diagnostics` even on `FAIL_RESTORED`. A `finish_reason=length` at the intended 64-token benchmark cap is recorded, **not automatically deemed a failure**. Do not loosen actual benchmark eligibility for missing usage, TTFT, SSE completion or generated tokens.

**Safe subsequent run protection:** Existing `attempt-<oldSHA>.json` remains immutable; source does NOT silently bypass it. Added `--audit-failure` read-only verification of exact one prior failed result, seven-event hash chain ending RESTORED, original P3 container ID running+API ready, stopped/owned failed candidate, Flash/variant stopped, original ordinary journal clean and no promoted benchmark. If and ONLY IF audit returns `PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY` / issues empty, operator may separately run interactive `--reconcile` and type exact prior used SHA plus `I_REVIEWED_27B_BENCHMARK_FAILURE_AND_RESTORED_SERVICE`; this writes **only a private reconciliation receipt**, never touches Docker. Then `--plan` issues **new distinct SHA** bound to prior reconciliation (also checks fresh current identity, recipe, cache and P3 lineage), and `--execute` STILL requires new TTY SHA, downtime and backup-deletion consent for any second attempt. Previously failed new container is **preserved**; new failed-container name is unique per NEW plan. Two unverified failures or state/evidence drift remain BLOCKED. **No next DGX attempt has been observed.**

**DGX Pull/read-only instructions (NO service mutation):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
docker ps -a --filter name=qwen38-27b --format 'table {{.Names}}\t{{.Status}}'
bash scripts/temporary/p2-27b-native-recipe-migrate.sh --audit-failure
```
If audit is BLOCKED, inspect actual Docker and private `~/.local/state/blazux-wizard/27b-recipe-migration/` rather than clearing markers. Only after reviewing evidence can operator choose interactive `--reconcile`, then `--plan`, then separately authorized live `--execute`. Any new migration result must be grounded in real DGX output; GitHub source-only CI is not DGX acceptance. Preserve original 27B model, HF cache, vLLM image, original P3 A/B/C and 14-event ordinary journal. Main Wizard production flag remains OFF; Draft PR #1 not merged.

---

## LATEST 2026-11-07 — User selects SINGLE canonical 27B recipe replacement (not variant switching); benchmark then delete verified old backup ONLY after PASS

Supersedes previous proposed persistent `qwen38-27b`↔`qwen38-27b-native-tools-v1` service-switch feature: user clarified to change **original 27B recipe**, stop existing service, **recreate the same canonical `qwen38-27b` name** with already DGX-proven native-tool flags, run NEW bounded benchmark, **replace latest active benchmark result**, then **remove the exact old backup Docker container only when every test PASSES**. Old benchmark evidence, model images, checkpoint cache and P3 A/B/C records must NOT be deleted/re-written. The separate unqualified persistent-switch prototype was removed from branch (not deployed). Native Tools 1-shot real DGX `PASS_RESTORED` remains prior proof and trial variant `qwen38-27b-native-tools-v1` remains stopped; its 9 chained events and receipt preserved.

**New Git source (NOT YET RUN on DGX):** `recipes/qwen38-27b.runtime.json` (single pinned 27B canonical source, vLLM 0.32.0, exact local image `sha256:9479fc92...`, revision `482ca0f...`, Jinja SHA `c3cf9e34...`, native-parser flags), desired `runtimes/service-policy.json` registration, `scripts/manager/p2_27b_recipe_migration.py` (read-only plan, independent exact-TTY execution, backup rename, canonical recreation, ordinary chat/structured tools/stream/SSE 3-sample fresh benchmark, private immutable receipts, atomic latest benchmark pointer, remove verified stopped old container only after all PASS, restore pre-change on precommit failure), and `scripts/temporary/p2-27b-native-recipe-migrate.sh` (`--plan`, `--execute`, `--status`). Permanent runbook: [docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md). **Per user request, do NOT block Git Pull on Fake-DGX CI**, but no source change alone authorizes downtime. User runs `git pull --ff-only` and `--plan` first; `--execute` still needs new independently accepted SHA + downtime acknowledgement + explicit verified-backup-deletion acknowledgement. Pull does not mutate Docker.

**CAUTION:** Original P3 receipts pin the PRE-MIGRATION 27B Docker ID. When user explicitly approves deletion after successful promotion, that old ID becomes historic, NOT active. Existing generic operating Flash↔27B code must remain fail-closed until later lineage-aware revision; ordinary service status sees canonical `qwen38-27b` by name but doesn't check tool flags, thus use new `--status` check to verify post migration actual flags / benchmark. Do NOT rewrite historical P3 receipts or indiscriminately delete caches or Docker images. Model stays `qwen3.8-27b` at `:8000`, ONE_ACTIVE_MODEL_ONLY, no SGLang.

**Current real DGX:** user most recently showed `qwen38-27b-native-tools-v1` `Exited (0)`, original `qwen38-27b` operating, 9 one-shot events, and validated `PASS_RESTORED`. **Canonical recipe migration, its new benchmark, backup cleanup, and new `--status` PASS are NOT_RUN.** The new action runs real Docker only on operator-approved TTY, not via connector or Fake-DGX. If `--plan` BLOCKED or execute reports `FAIL_RESTORED`, `RECOVERY_FAILED`, `COMMITTED_CLEANUP_PENDING`, stop and reconcile; never retry blindly.

---

## LATEST REAL DGX — 2026-11-07 P2-FINAL native tool_calls + streaming PASS_RESTORED

**Actual operator-provided DGX run, not CPU simulation:** fresh TTY-approved `scripts/temporary/p2-final-native-tools-operator.sh --execute` completed with `status=PASS_RESTORED`, `trial=PASS`, `structured_tool_call=true`, `tool_result_continuation=true`, `streamed_tool_call=true`, `structured_probe_status=LOCAL_STRUCTURED_TOOL_CYCLE_PASS`, `stream_probe_status=LOCAL_STREAMED_TOOL_CALL_PASS`, `issues=[]`, `original_restored=true` / `restoration.status=RESTORED`. Operator then independently verified original `qwen38-27b` serving sole API ID `qwen3.8-27b` at `:8000`, `LIVE_SERVICE_VERIFIED`, `issues=[]`. Ordinary operating journal still `VERIFIED`/`COMMITTED`, **14 events**, `issues=[]`, last event hash `ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e`. Docker running list contains original 27B, Open WebUI (healthy), Portainer; no second running model shown.

**Qualification update:** The actual bounded 27B Native Tools `tool_choice=auto` + synthetic tool-result continuation + SSE + original restoration **subgate is now REAL PASS**. Earlier “not run” / original API HTTP-400 historical entries below remain chronological evidence, **not current milestone status**. This run does NOT verify real Open WebUI Native end-to-end, production Wizard native-tools switching, crash/forced-error rollback, comprehensive generated reasoning leakage, physical GPU process exclusivity or host port process ownership. The ordinary status fields `manifest_status=OBSERVED_UNQUALIFIED`, `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `operations_enabled=false` remain unqualified scopes rather than observed conflicts. Do not declare complete P2-FINAL production acceptance; ordinary Wizard `PRODUCTION_EXECUTION_RELEASED=False`, old P3-C immutable, original containers/images/HF cache retained, vLLM 0.32, port 8000, ONE_ACTIVE_MODEL_ONLY. **No repeat trial with the same SHA**; private attempt marker blocks blind repetition.

**Evidence detail and remaining acceptance gates:** [docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md](../docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md). Next: private one-shot evidence/stopped variant inventory audit (read-only); design safe long-lived variant-aware service identity and production rollout (separately approved); live Open WebUI Native application end-to-end only during an independently approved maintenance period. No new service downtime authorized by this report.

---

## 2026-11-07 — User-authorized P2-FINAL Native Tools one-shot DGX trial SOURCE delivered; RUN NOT YET

**Actual real DGX prerequisites confirmed by operator:** vLLM 0.32.0 has registered `qwen3_coder` and `qwen3`; pinned NVIDIA revision `482ca0f3832238542f8f5295dde86b5f22711d80` Jinja SHA256 `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041` rendered all five CPU synthetic cases successfully on DGX: tool_prompt, tool_result, non_tool_prompt, no_thinking, thinking_prompt. Result `CPU_TEMPLATE_RENDER_VALIDATED_ONLY`, issues empty. User then requested to **proceed with actual server native `tool_calls` testing** and explicitly directed delivery of a **temporary committed script** for DGX `git pull`. No new live result yet.

**Implemented source-only + Fake-DGX PASS:** tracked `scripts/temporary/p2-final-native-tools-operator.sh` dispatches to `scripts.manager.p2_27b_tool_live_trial` with `--plan` (default, read-only) or `--execute` (TTY only). The new one-shot executor is **separate** from historical P3 and ordinary Wizard and uses fresh 64hex SHA plus two independent per-target downtime acknowledgements, operating and trial locks, independent private immutable attempt marker + phased event files, preserved original P3 lineage/image/port 8000, exact pinned NVIDIA tool-enabled argv, stop original `qwen38-27b` BEFORE creating uniquely named `qwen38-27b-native-tools-v1`, bounded structured `tool_choice=auto`, tool-result continuation and streaming probes, then **ALWAYS attempt to stop variant and restore/verify original 27B even after PASS**. One-shot variant remains stopped/preserved, original P3/operational receipts remain untouched. An interrupted/previous trial is blocked pending manual reconciliation. It does not set `PRODUCTION_EXECUTION_RELEASED` or enable normal Wizard variant switching; no service manifest migration. A host power failure, SIGKILL, OOM, Docker problem may defeat recovery and requires manual reconciliation. Do not claim live GPU acceptance from CI.

**Fake-DGX CI:** [Recipe manifest CPU run 42343502949](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42343502949) succeeded after fixing the empty `docker ps` fake fixture (the failed run 42343432619 was a fixture-only issue). New shell-wrapper tests also passed in [run 42343608738](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42343608738). These checks run NO real Docker/GPU. **No actual trial or downtime was executed** by source commit.

**Next operator steps on DGX:** `git status -sb`, `git pull --ff-only origin feature/recipe-wizard-handoff`, `bash scripts/temporary/p2-final-native-tools-operator.sh --plan`. Require `READY_FOR_INDEPENDENT_NATIVE_TOOLS_TRIAL_APPROVAL`, issues empty, original 27B currently live, original restoration required. Then the user may choose to run `bash scripts/temporary/p2-final-native-tools-operator.sh --execute` in a real TTY during a separately accepted maintenance interruption, type the new SHA printed during execute and exact two independent strings `I_ACCEPT_P2_FINAL_NATIVE_TOOLS_DOWNTIME` and `I_APPROVE_DISTINCT_27B_NATIVE_TOOLS_V1`. The result may be PASS_RESTORED / PARTIAL_RESTORED / FAIL_RESTORED / RECOVERY_FAILED; even PASS_RESTORED only validates trial probes and original restoration, not Open WebUI Native/ongoing service switch. After trial independently inspect `./wizard.sh service manager status --json` and `python3 -m scripts.manager.operational_audit --json`. **NEVER blindly retry or delete original containers/caches/receipts**; older P3 stages remain immutable, port 8000 and ONE_ACTIVE_MODEL_ONLY always enforced.

**Permanent runbook:** `docs/P2-FINAL-NATIVE-TOOLS-ONE-SHOT-OPERATOR-20261107.md`. PR #1 remains Draft/open/unmerged. Main Wizard production switch release remains OFF.

---

## 2026-11-07 — Actual DGX parser registry PASS; pinned NVIDIA Jinja solution / CPU-only experiment (NOT LIVE ACCEPTED)

The DGX operator ran a **non-mutating import audit inside existing `qwen38-27b`** and reported `vllm_version=0.32.0`, tool parser `qwen3_coder` = `vllm.tool_parsers.qwen3_engine_tool_parser.Qwen3EngineToolParser`, reasoning parser `qwen3` = `vllm.parser.engine.adapters.Qwen3ParserReasoningAdapter`, all **FOUND**. The pinned snapshot's `tokenizer_config.json` exists but its inline `chat_template` is `null`. This is **not** evidence of an absent effective template.

**Root-cause hypothesis and concrete fix candidate:** The **same exact pinned NVIDIA revision** `482ca0f3832238542f8f5295dde86b5f22711d80` contains a *separate* `chat_template.jinja` (8.95 kB), with Qwen XML `<tool_call><function=...><parameter=...>` prompting, `<tool_response>` continuation and `enable_thinking=false`. This was independently checked at [NVIDIA pinned revision](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/482ca0f3832238542f8f5295dde86b5f22711d80) and [pinned Jinja source](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/blob/482ca0f3832238542f8f5295dde86b5f22711d80/chat_template.jinja). [vLLM 0.32 Online Serving documentation](https://docs.vllm.ai/en/v0.32.0/serving/online_serving/) explicitly supports `--chat-template path/to/file.jinja`. The `qwen3_coder` and `qwen3` flags match the [upstream Qwen3.8 recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-27B.yaml) and the DGX import audit.

The distinct **source-only candidate** `qwen38-27b-native-tools-v1` now appends `--chat-template /hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/482ca0f3832238542f8f5295dde86b5f22711d80/chat_template.jinja` before official opt-in parser flags. Original `qwen38-27b` `Config.Cmd`, `_candidate_argv(...,tool_calling=False)`, source image, all containers, API :8000 and every historical P2/P3 receipt remain unchanged. **Do not run the inert command** or launch a second GPU process.

**Next non-disruptive DGX experiment (after clean git pull):**

```bash
bash scripts/serve_27b.sh --tools-template-audit
```

Runs **one bounded 90s** `docker exec -i` Python `-B` in the existing original container with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `CUDA_VISIBLE_DEVICES=-1` and `PYTHONDONTWRITEBYTECODE=1`; no model weights, inference API, Docker lifecycle, host port or cache write. Reads pinned Jinja and reports its SHA, tokenizer auto-detection and whether synthetic tool-choice, no-thinking, non-tool chat and tool-result continuation prompts render with local Transformers `AutoTokenizer`. It **does not** contact another model, show prompt bodies, or make external tool calls. `CPU_TEMPLATE_RENDER_VALIDATED_ONLY` is **not P2-FINAL PASS**. If missing file/unsupported tokenizer/render fails, report the diagnostic and fix with a **pinned, provenance-preserving** source change; no floating updates, SGLang or replacement tokenizer downloads.

Outstanding: actual pinned template file on operator DGX not yet independently shown; runtime tokenizer/Jinja compatibility not yet tested; variant service integration, crash-safe journal/rollback and *new distinct downtime consent* not implemented; actual native tool calling, streaming, reasoning isolation and Open WebUI Native not qualified. Main Wizard `PRODUCTION_EXECUTION_RELEASED=False`, PR #1 remains Draft/unmerged, old P3-C PASS immutable.

---

## 2026-11-07 — P2-FINAL Fake-DGX cutover state-machine simulation added; 722 CPU PASS

Added `scripts/manager/p2_27b_tool_cutover_simulation.py` and `tests/test_p2_27b_tool_cutover_simulation_cpu.py`: a deliberately **Fake-DGX-only**, injected-adapter transaction state machine covering strict variant/source/fallback identity, domain-separated expiring simulated approval, two acknowledgements, lock/prior-journal refusal, stop original→port free→no GPU overlap→start separate variant→check tools/API→preserve original, and failure rollback/uncertainty. Its results are named `SIMULATED_*`, `executed_on_real_dgx=false`; there is NO live Docker adapter, CLI execute route, persistent journal, or production release flag. Simulated approvals must NEVER be treated as real operator consent.

Source code SHA `fe4e6b01c98c9244787a5bb8e034ca81d88bba08` passed GitHub Actions [42339247960](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42339247960): **722/722 offline CPU tests PASS, 34 groups**. This supersedes the earlier 706-test source validation. No DGX service, current original 27B Docker config, HF cache or immutable P3-C was changed. **P2-FINAL Native Tool Calling remains NOT_QUALIFIED** pending parser/image audit, real variant-aware executor/journal/rollback implementation, independent downtime consent, actual structured/streaming/reasoning/WebUI tests. Main Wizard release remains OFF.

---

## 2026-11-07 — SOURCE CI independently VERIFIED for protected Native Tools V1

GitHub Actions [Recipe manifest CPU run 42339037935](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42339037935) **SUCCESS** at exact source SHA `695e4b1f6a10825324d66b01695cda6b0ffeb02d`: **706/706 offline CPU tests in 34 groups PASS**, including the new protected identity, ModelOpt, streaming and malformed-request regressions; both intentionally unqualified candidate YAML recipes were confirmed non-launchable. This CI establishes SOURCE/Fake-DGX correctness only, not DGX parser availability, Tool Calling WebUI or a tested service rollback. Original 27B runtime and ordinary journal were not touched. The subsequent handoff-only update does not alter verified runtime code or CI workflow.

---

> **2026-11-07 later source-only update:** P2-FINAL now has `p2_27b_tool_variant.py` (new protected `qwen38-27b-native-tools-v1`), intentionally invalid `recipes/qwen38-27b-native-tools-v1.candidate.yaml`, `--tools-variant-plan` read-only preflight, and `--tools-stream-probe` SSE inference probe with CPU tests. Consult `docs/P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md`. No new actual DGX run, no parser validation, no cutover executor, no production release; P2-FINAL remains OPEN. Original NVIDIA 27B at :8000 and old HTTP 400 are last operator observations. Historical P3-C remains closed. Re-check HEAD/CI/PR at the start of the new session; do NOT replay P3 or use a candidate argv as executable approval.

---

# New Conversation Starter — Blazux P2-FINAL Native Tool Calling, DGX Spark / Wizard 안전 전환 개발

아래 저장소의 **Blazux / vLLM 0.32 기반 DGX Spark 모델 레시피·Wizard·서비스 관리 개발**을 이전 작업에서 이어서 직접 수행해주세요. 이 프롬프트는 새 대화에서 독립적으로 사용되는 핸드오프입니다. 반드시 먼저 GitHub 연결 도구로 HEAD/PR/CI와 최신 영구 문서/소스를 조회하고, 이후 코드를 구현·테스트·커밋·Draft PR 검토·문서 업데이트까지 처리하세요. 계획만 작성하고 중단하지 마세요. **실제 DGX GPU/서비스 변경은 별도의 운영자 승인 없이는 절대 실행하지 마세요.**

## 1. 저장소와 고정 운영 정책

- Repository: https://github.com/kjlee-inlct/qwen3.8-Flash-DGX
- Branch: `feature/recipe-wizard-handoff`, Draft PR #1 **Open / Unmerged**, 새 브랜치/PR 및 머지 임의 수행 금지
- Parallel `feature/orcarouter-bf16-adapter`, upstream https://github.com/blazux/qwen3.8-Flash-DGX
- Real DGX source: `~/Workspace/llm/blazux-orcarouter`; NVIDIA DGX Spark GB10 / Ubuntu ARM64, Docker
- Inference: **vLLM 0.32 only; no SGLang**. API remains `:8000/v1`, served ID `qwen3.8-27b` or `qwen3.8-flash-next`. **ONE_ACTIVE_MODEL_ONLY**.
- Main UX: `./wizard.sh`, preserve Portainer/Open WebUI, pinned containers, images, model snapshot/HF caches and private receipts.
- Last verified source-code HEAD (before newest documentation-only updates): `09c6780f52104de14fd3510c528a7a79c3d467dd`. [GitHub Actions 42337337910](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42337337910): **SUCCESS, 680/680 offline CPU tests, 34 groups**. **Do not assume this is current Git HEAD**: refresh PR #1's head SHA, latest CI and any newer doc commits.

## 2. Mandatory permanent handoff and contracts

Read these files **in order**, prioritizing the latest dated top sections over historical records:
1. `handoff/README.md`
2. `handoff/CURRENT-STATE.md`
3. `handoff/OPERATING-RULES.md`
4. `handoff/NEXT-ACTIONS.md`
5. `handoff/EVIDENCE-LEDGER.md`
6. `handoff/DECISIONS.md` (especially D-016, D-056, D-057, D-058 and newer decisions)
7. `handoff/CHANGELOG.md`
8. `handoff/SESSION-START-PROMPT.md`

Then inspect `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`, `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`, `docs/P2-27B-WIZARD-OPERATIONS.md`, `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md`, `docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md`, `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`, `docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md`, `docs/MODEL-RECIPE-WIZARD-PLAN.md`, `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`, `docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md`, `docs/WIZARD-CLI-CONTRACT.md`, `docs/MANIFEST-CONTRACTS.md`, `runtimes/service-policy.json`, `runtimes/model-discovery.json`, `recipes/README.md`, `scripts/temporary/README.md`, `benchmarks/published/README.md`, and the published Flash/27B sanitized reports. **All these named files and benchmark reports existed in the branch at the 2026-11-07 audit.**

Important code: `scripts/manager/p2_27b_launch_preview.py`, `scripts/manager/p2_27b_tool_calling.py`, `scripts/manager/p2_27b_gpu_trial.py`, `scripts/manager/operational_{switch,executor,wizard,acceptance,audit,probe}.py`, `scripts/serve_27b.sh`, `wizard/{console,main,roadmap}.py`, `wizard/menus/switching/flash_next_27b.py`, `tests/test_p2_27b_tool_calling_cpu.py`, `tests/test_operational_*_cpu.py`, and `.github/workflows/recipe-manifest-cpu.yml`.

## 3. Proven actual DGX history — do not redo accomplished work

**P1 Flash-Next**: `nvidia/Qwen3.8-Flash-Next-NVFP4`, revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`. Real API/Completion/Chat/Tool/Vision Verify PASS; benchmark and post-P3-B re-verify/benchmark PASS. Post-B reported average 37.9527 tok/s (different metric from 27B).

**P2 existing GPU portion**: `nvidia/Qwen3.8-27B-NVFP4`, pinned revision `482ca0f3832238542f8f5295dde86b5f22711d80`; 19 files downloaded; `modelopt_mixed` ModelOpt NVFP4/FP8, runtime GPU trial/API PASS, 3/3 bounded benchmark and source restoration PASS. 27B reported 7.9002 client E2E tok/s and 11.1801 decode proxy tok/s. Internal loader `Qwen3_5ForConditionalGeneration` DOES NOT rename the installed Qwen3.8 checkpoint/API.

**Historical P3 A/B/C**: `stage-a` Flash→27B PASS, `stage-b` 27B→Flash PASS, post-B P1 benchmark/verify PASS, `stage-c` Flash→27B PASS with private immutable receipt `~/.local/state/blazux-wizard/p3/stage-c.json`. **Original one-off P3-C is FINAL, CLOSED, IMMUTABLE. NEVER rerun P3-A/B/C, change old receipts or treat them as routine-switch execution.**

**New ordinary operational switching** is a distinct backend. Real DGX operator executed two independent four-approval trials: 27B→Flash **PASS** (original private receipt `completed-72e0941f…json`) and Flash→27B **PASS** (private receipt `completed-a811068f…json`). Separate actual postchecks show latest active `qwen38-27b` on :8000 with sole `qwen3.8-27b` / `LIVE_SERVICE_VERIFIED` / `issues=[]` and independent operating journal `VERIFIED`, phase `COMMITTED`, **14 events**, `issues=[]`, hash `ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e`. Thus both ordinary directions plus postchecks are REAL PASS. **The normal interactive `./wizard.sh` execution menu remains `PRODUCTION_EXECUTION_RELEASED=False` and is NOT fully accepted/released**; actual intentional fault/recovery testing is NOT_RUN. Do NOT flip this gate from source/CPU or one-off trial results alone.

## 4. NEWEST operator-provided P2-FINAL evidence (2026-11-07)

Operator fast-forwarded local source from `4054eb2` to `09c6780`, with clean Git status and no destructive action. **Last observed live model: NVIDIA 27B**, service `LIVE_SERVICE_VERIFIED` at port 8000, correct sole `qwen3.8-27b`. Operating journal `VERIFIED/COMMITTED/14`.

Direct `docker inspect qwen38-27b --format '{{json .Config.Cmd}}'` shows pinned `/hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/482ca0f3832238542f8f5295dde86b5f22711d80`, `--served-model-name qwen3.8-27b`, `--quantization modelopt_mixed`, `--dtype bfloat16`, `--max-model-len 8192`, `--max-num-seqs 1`, `--gpu-memory-utilization 0.70`, `--enforce-eager`. **The original running Docker Cmd DOES NOT include** `--enable-auto-tool-choice`, `--tool-call-parser`, or `--reasoning-parser`.

The new `bash scripts/serve_27b.sh --tools-profile` displays source candidate flags:

```bash
--enable-auto-tool-choice \
--tool-call-parser qwen3_coder \
--reasoning-parser qwen3
```

Its status is `SOURCE_PROFILE_ONLY_DGX_NOT_QUALIFIED`; `production_enabled=false`, no Docker recreation or migration. The benign bounded localhost `bash scripts/serve_27b.sh --tools-probe` returned **`BLOCKED`, `issues=["LOCAL_API_HTTP_ERROR_400"]`, `structured_tool_call=false`, `tool_result_continuation=false`, `reasoning_separation=false`**. HTTP response body is not yet captured: do not fabricate it. Prior Open WebUI Native request had auto tool-choice parser error. Combined evidence confirms missing startup switches and current tool-auto incompatibility, NOT that the model itself cannot call tools. Source-only profile does not retrofit an immutable Docker container.

## 5. Primary next development — P2 FINAL Tool Calling properly qualified

P2 existing download/GPU/benchmark remains PASS; **add formal Native Tool Calling as P2's LAST unfinished acceptance gate**, and only close it after actual DGX & Open WebUI evidence. Official vLLM 0.32 Qwen3.8-27B recipe candidate:
`--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`.

1. Inspect repo's real architecture, launcher, recipes, manifest, pinned Docker image, available parser/serving args and existing safe service manager. Confirm exact Qwen3.8 27B parser/chat-template compatibility; don't silently assume Qwen3.5 model ID or reuse Flash PLE/MTP config.
2. Design **separate, named and versioned tool-enabled 27B recipe/runtime variant** rather than modifying/deleting `qwen38-27b`. Original 27B container ID/image/labels/P3 provenance are protected by the current normal-switch preflight. Explicitly design how separate variant fits manifest/service status/port :8000, protected fallback, lock/journal, one GPU model, cutover and rollback. Any need to modify existing container identities must be proposed and reviewed; no implicit collision, remove, force-recreate or `docker run` on port 8000.
3. Implement source-only candidate plan, new exact authorization contract and proper CPU/Fake-DGX failure cases: invalid parser, wrong container/image ID, collision, timeout, GPU exclusivity, stale/expired plan, refusal/cancellation, partial start, failed health, source restore, journal tampering, no double running model. Do not expose unapproved execute path.
4. Design/test bounded real Tool Calling acceptance: `tool_choice=auto`, structured `tool_calls` name/ID/JSON arguments, actual tool result continuation (benign local test function, no external side effects), no-tool chat, streaming tool-call chunks, reasoning separation, Open WebUI **Native Tools** functional integration. Distinguish HTTP 200 from successful structured tool semantics. Keep private evidence private.
5. GitHub commit source/tests/docs, confirm CI and include manual, explicitly approved DGX trial instructions. **Obtain new operator downtime approval before ANY live service stop/start/recreate/migration, even if a plan is READY.** The existing user message authorizes documentation/source planning, NOT new downtime.
6. Only after real Native tool cycle + streaming + Open WebUI + restore proof passes, mark `P2-FINAL=PASS`. Do not reopen historical P3-C.

Secondary milestone: finish and qualify normal main Wizard guided production execute (currently source gate OFF) and real failure/recovery, separately from P2 tool integration. Keep P4 conditional cleanup, P5 Orcarouter, P6 Orcarouter↔27B, P7 proxy/gateway for later.

## 6. Development workflow and immutable rules

Follow D-016 and latest Operating Rules: read code/docs, implement necessary changes directly through GitHub connector, add/adjust CPU tests, run/check CI, commit to SAME feature branch, comment on existing Draft PR #1 and update handoff records. Never present a theoretical plan as delivered code. For DGX actions supply tracked `scripts/temporary/` read-only scripts and runbooks, not lengthy unreviewed commands; operator can `git pull --ff-only origin feature/recipe-wizard-handoff` when clean.

**Do not**: re-run P3 A/B/C or finished P1/P2 benchmarks; erase/update original receipts; delete HF cache, models, original Flash/27B containers or Docker images; `docker system prune`, `git reset --hard`, `git clean -fd`; alter API port 8000; use SGLang; run 2 GPU inference models; auto-type approvals; turn on normal operating `PRODUCTION_EXECUTION_RELEASED` without distinct qualification; merge PR #1 without explicit authorization; upload secrets/private raw receipts or sensitive traces. A future newly approved tool-enabled variant may require service downtime but this prompt gives **NO SUCH APPROVAL**.

At each meaningful development milestone update `handoff/CURRENT-STATE.md`, `NEXT-ACTIONS.md`, `EVIDENCE-LEDGER.md`, `DECISIONS.md`, `CHANGELOG.md`, `SESSION-START-PROMPT.md`, related `docs/` and tests/CI. Preserve historical content and prepend correctly dated superseding headnotes when older states are now stale.

## 7. Required report

Clearly separate: **WHAT CHANGED** (concrete implementation), **GITHUB** (actual latest HEAD, branch, PR, CI), **TESTS** (CPU vs real DGX), **P2-FINAL TOOL CALLING** (current 400/flags, root cause, variant/migration/acceptance), **WIZARD** (two real direction PASS vs main menu still locked), **DGX STATE** (last user-observed 27B :8000; preserve assets), **BLOCKERS / NEXT ACTIONS** (source-only next step vs separately approved physical cutover). Do not claim true DGX status after the last operator log, new model restart, parser/live tool success, or production release without new evidence.

**Start now:** inspect newest GitHub HEAD/PR/CI, the handoff files and source paths, identify the minimal safe P2-FINAL separate 27B tool-enabled variant/migration design, implement/test/commit what can be done without altering the real DGX, and update permanent handoff. Do not ask again for details already established above.

---

## Previous handoff snapshots below (historical; superseded where inconsistent)

## NEWEST — 2026-11-07: P2 final Tool Calling added / historical P3-C CLOSED

Priority selected by operator: original P2 pinned NVIDIA Qwen3.8-27B GPU download/loader/trial/benchmark historically PASS; **add Native Tool Calling on vLLM 0.32 (auto parser `qwen3_coder` / reasoning `qwen3`) as P2 last acceptance gate**, without renaming the model to Qwen3.5. Source-only opt-in profile `_candidate_argv(..., tool_calling=True)`, `scripts/manager/p2_27b_tool_calling.py`, and `scripts/serve_27b.sh --tools-profile|--tools-probe` now exist; source Fake-DGX tests cover profile and benign 2-turn tool-call. This does NOT retrofit original Docker startup flags or qualify current tool-native Open WebUI; operator must independently approve a separate preserved-container-safe variant migration and real GPU tool tests. Original **P3-C A/B/C were ALREADY REAL PASS and are now FINAL/CLOSED**, never replay. Separate new recurring operating 27B→Flash and Flash→27B trials both REAL PASS from operator, newest observed active 27B, but independent reverse postcheck still missing; normal `./wizard.sh` main menu production hard gate remains OFF. Initial safe DGX observations `service manager status --json`, `operational_audit --json`, `docker inspect qwen38-27b --format '{{json .Config.Cmd}}'`, then `scripts/serve_27b.sh --tools-profile|--tools-probe`; no Docker stop/restart. Read `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`. Keep Draft PR #1 unmerged, model caches/receipts preserved, port 8000, ONE_ACTIVE_MODEL_ONLY.

---

## NEWEST ACTUAL DGX READ-ONLY postcheck — 2026-11-07, after ordinary 27B→Flash PASS

The operator independently reran `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, `observed_model=flash-next`, sole `qwen3.8-flash-next`, active `qwen38-flash`, port 8000, issues `[]`. `python3 -m scripts.manager.operational_audit --json`: `VERIFIED`, `COMMITTED`, 7 journal events, issues `[]`; confirms the completed transaction's journal/snapshot/receipt linkage. `operational-switch-acceptance.sh --target 27b --plan --json`: read-only `READY_FOR_SEPARATE_TRIAL_APPROVAL`, `source=flash-next`, `target=27b`, issues `[]`, executed/approval false, original plan 276s remaining at that observation. **Do not reuse an expired plan SHA.** First physical ordinary transfer 27B→Flash PASS; real reverse Flash→27B **NOT_RUN**, forced recovery tests **NOT_RUN**; production normal menu `PRODUCTION_EXECUTION_RELEASED=False`. Latest live model is Flash-Next. Preserve P3 historical receipts and all models, caches, port 8000; no automatic reverse or PR merge. After a separate user-approved downtime scope, independently planned live `--target 27b --execute` requires four fresh exact TTY approvals.

---

## NEWEST DGX checkpoint — 2026-11-07 first ordinary Wizard acceptance 27B→Flash PASS

This supersedes earlier handoff passages that said ordinary transfer NOT_RUN or 27B currently ACTIVE. On source `4054eb2`, actual DGX operator ran read-only current 27B service verification and empty independent operating journal, obtained a fresh `READY_FOR_SEPARATE_TRIAL_APPROVAL` plan with no issues and >180s, then manually approved all four required trial/SHA/downtime/target strings at the NEW `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute`. Report: **`Live transition result: PASS`, `Observed model: flash-next`** and local private immutable `completed-72e0941f…json`. This was the independent recurring operating backend, NOT a replay of P3-A/B/C. Its PASS is actual live switching + API/model/chat verification and committed receipt/audit, but independent after-action status/audit console output has not yet been shared.

**Next safe work:** the new last observed model is **Flash-Next**; query `./wizard.sh service manager status --json`, `python3 -m scripts.manager.operational_audit --json`, `bash scripts/temporary/operational-switch-acceptance.sh --target 27b --plan --json` (ALL read only). A separately scoped Flash downtime approval is REQUIRED for an actual reverse `--target 27b --execute` with a fresh plan and four independent TTY inputs. Do not use prior SHA, turn on ordinary production execution gate, merge PR #1, rerun P3 stages or clean caches. Real ordinary reverse and failure/rollback trial remain NOT_RUN. Tool Calling deferred; vLLM 0.32, single GPU model, :8000 unchanged.

---

## LATEST HANDOFF 2026-11-07 — Operating Wizard source implementation complete candidate; real acceptance requires new consent

Current task is **existing Blazux `./wizard.sh` ordinary Flash-Next ↔ NVIDIA 27B switching UX to execution backend**, NOT Open WebUI 27B Tool Calling (deferred). Current GitHub feature branch `feature/recipe-wizard-handoff`, Draft PR #1, no merge. Source code now includes: main Wizard option 4 / model option 6; release-gated guided normal switching; read-only preview and domain-separated execution SHA; independent locked executor with stop-before-start, private append-only journal + strict crash-divergence audit, target /health + served ID + bounded chat verification, best-effort original restore and explicit uncertain failure; one-off physically accepted trial entry via `scripts/temporary/operational-switch-acceptance.sh --target flash-next --plan|--execute` (four fresh TTY approvals on live execute). Source Fake-DGX CI must be refreshed at latest HEAD. `PRODUCTION_EXECUTION_RELEASED=False` until independently approved ACTUAL DGX both directions and recovery scenarios pass. Latest real DGX from user: original pinned 27B ACTIVE :8000, local curl completions PASS, no source-induced service mutation. Do not replay historical P3 A/B/C, repeat P1/P2 benchmarks, alter API port, delete model/cache or merge PR without permission.

**Next safe step**: review fresh GitHub HEAD/CI, then on operator DGX fast-forward pull and run *read-only* `./wizard.sh service manager status --json`, `python3 -m scripts.manager.operational_audit --json`, `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --plan --json`. For ACTUAL switch, independently scoped 27B downtime consent and four fresh typed inputs are mandatory, with separate reverse-direction authorization; see `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`. No actual ordinary operating test evidence has been supplied yet. Any `RECOVERY_FAILED`/uncertain status forbids blind retry.

---

## LATEST ACTUAL DGX checkpoint — 2026-11-07, operator 27B curl PASS (supersedes prior NOT_RUN)

After P3-C and the routine-switch read-only preflight, the actual DGX operator directly checked `:8000/health`, sole `/v1/models` ID `qwen3.8-27b` and actual `/v1/chat/completions` on NVIDIA pinned 27B under vLLM 0.32.0. Also fast-forward pulled Git source `05c1968` and ran `bash scripts/temporary/operational-27b-curl-smoke.sh`: **HEALTH_PASS, IDENTITY_PASS, INFERENCE_PASS, 27B_CURL_SMOKE_PASS**. This closes prior *current functional text-generation* uncertainty without any service switch or restart. **Distinct anomaly:** completion `content` carried reasoning-like text, `</think>` then `DGX_OK`, with `reasoning=null`, so strict exact-answer format failed. New source-only classifier with `FORMAT_DEVIATION` and fake CPU tests pending final CI; no live DGX rerun of this updated classifier. Active 27B remains untouched, historical P3-A/B/C receipts preserved, ordinary repeatable switching/rollback and integrated UX **still NOT DGX qualified**. Next: investigate chat template vs reasoning parser read-only, harden transaction source and obtain new separate scoped operator consent before any actual model transfer. Do not merge PR #1.

---

## 2026-11-07 — NEW SESSION HEADNOTE: operational switch source implementation, unexposed and unqualified

After P3-C actual DGX PASS, an ordinary operating switch **read-only preview** and **isolated guarded executor source** have been added to the existing feature branch. Read \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`, \`scripts/manager/operational_switch.py\`, \`scripts/manager/operational_executor.py\`, and the Fake-DGX suites. The latter source is **NOT invoked by Wizard CLI or TTY** and has not switched any actual DGX model. Do not claim repeated operating switch UX acceptance or release. First refresh GitHub HEAD/PR/CI and fix any CPU regressions, then review guarded transaction/rollback design; only after separate user authorization may live DGX acceptance be planned. Keep NVIDIA 27B running at :8000, retain all original assets, do not re-run historical P3 stages/benchmarks and do not merge Draft PR #1. This headnote supersedes older "executor not yet written" statements only at the SOURCE level; live qualification remains pending.

---

# New Conversation Starter — Blazux P1~P3 실제 DGX PASS 이후 통합 Wizard UX 및 일반 운영 모델 전환 개발

다음 GitHub 저장소의 **Blazux / vLLM 0.32 기반 DGX Spark 통합 모델 레시피·Wizard·서비스/프록시/게이트웨이 관리** 작업을 이전 대화에서 이어서 진행해주세요.

**이번 작업의 출발점은 P3-C 완료 이후입니다. P3-A/B/C 또는 P1/P2 벤치마크를 다시 시작하지 마세요.** 최우선 목표는 이미 검증된 백엔드 실행 엔진을, 일반 사용자가 쉽게 조작할 수 있는 **모델 중심 `./wizard.sh` 통합 UX**에 연결하고 상태·승인·실패 복구를 일관되게 만드는 것입니다. P4~P7 계획은 이어서 관리하되, 실장비 운영 상태를 바꾸는 작업은 새 별도 승인이 필요합니다.

이 요청은 단순 의견이나 계획서 작성 요청이 아닙니다. **GitHub 연결 도구로 실제 HEAD/PR/CI 및 기존 코드·문서 확인 → 갭 분석 → 필요 코드·CPU 회귀 테스트·영구 문서 구현/수정 → 기존 브랜치에 커밋 → CI 확인 → Draft PR 리뷰**까지 가능한 범위에서 직접 수행하세요. 실제 DGX 컴퓨터에 직접 접근할 수 없다면 접근한 것처럼 표현하지 말고, GitHub에 추적 가능한 실행 스크립트를 먼저 준비한 뒤 운영자가 명시적으로 승인한 경우에만 DGX 실행 절차를 제시하세요. 알 수 없는 실측·검증 결과를 추측하지 마세요.

## 1. 저장소 및 실행 정책

| 항목 | 사실/운영 규칙 |
|---|---|
| GitHub | https://github.com/kjlee-inlct/qwen3.8-Flash-DGX |
| 작업 브랜치 | `feature/recipe-wizard-handoff` |
| PR | #1, Draft/Open/Unmerged — 명시적 허가 전 머지 금지 |
| 병렬 Orcarouter 브랜치 | `feature/orcarouter-bf16-adapter` — 독립 코드 감사를 거치기 전 무단 합치지 않음 |
| Upstream | https://github.com/blazux/qwen3.8-Flash-DGX |
| 실제 DGX 작업 디렉터리 | `~/Workspace/llm/blazux-orcarouter` |
| 하드웨어/OS | NVIDIA DGX Spark (GB10), Ubuntu ARM64 |
| 추론 엔진 | Blazux 기반 **vLLM 0.32** 고정; **SGLang 사용 금지** |
| 외부 API | `:8000/v1` 고정, 이전 주소를 불필요하게 변경하지 않음 |
| 런타임 | **ONE_ACTIVE_MODEL_ONLY**; API용 GPU 모델 동시 실행 금지 |
| 주 사용자 인터페이스 | **`./wizard.sh`** — P1~P7 내부 식별자를 숨기고 모델 선택 중심으로 구성 |
| 자산 보존 | 기존 Flash-Next·NVIDIA 27B 컨테이너, Docker 이미지, Hugging Face cache/체크포인트 및 모든 원본 evidence 유지 |

**신규 대화 시작 시 반드시 GitHub connector로 최신 HEAD, PR #1, CI run을 다시 조회하세요.** 직전 알려진 코드/문서 기준은 2026-11-07; 기존 CI run **42323857383**에서 **565/565 CPU 테스트 PASS(26개 그룹)**. 이후 문서 커밋이 추가됐으므로 특정 HEAD를 고정된 최신 값으로 간주하지 마세요. CPU CI는 실장비 GPU/API 시험을 대체하지 않습니다.

## 2. 반드시 읽고 정합성을 점검할 파일

**우선 읽을 핸드오프**
1. `handoff/README.md`
2. `handoff/CURRENT-STATE.md` — 최신 2026-11-07 P3-C 실제 성공 섹션이 먼저
3. `handoff/OPERATING-RULES.md`
4. `handoff/NEXT-ACTIONS.md`
5. `handoff/EVIDENCE-LEDGER.md`
6. `handoff/DECISIONS.md` — 특히 **D-016, D-056**
7. `handoff/CHANGELOG.md`
8. `handoff/SESSION-START-PROMPT.md` — 이 프롬프트 최신판

**설계·계약·현재 진행도**
- `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md` — 실제 DGX 백엔드 PASS와 메뉴 UX 수용 상태 구분
- `docs/MODEL-RECIPE-WIZARD-PLAN.md` — 원래 P1→P7 순서 및 Wizard-first 승인 계약
- `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`
- `docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md`
- `docs/WIZARD-CLI-CONTRACT.md`
- `docs/MANIFEST-CONTRACTS.md`
- `docs/P1-WIZARD-OPERATIONS.md`, `docs/P2-27B-WIZARD-OPERATIONS.md`
- `docs/P3-MANUAL-TRANSITION-SEQUENCE-20261106.md`
- `docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md`
- `docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md` — 과거 완료된 전환 기록; 현재 재실행 안내로 취급 금지
- `docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md`
- `runtimes/service-policy.json`, `runtimes/model-discovery.json`
- `recipes/README.md`, `scripts/temporary/README.md`
- `benchmarks/published/README.md` 및 해당 2개 모델 benchmark JSON

**관련 코드/테스트**
- `wizard.sh`, `wizard/main.py`, `wizard/console.py`, `wizard/quickstart.py`, `wizard/workflow.py`, `wizard/roadmap.py`
- `wizard/menus/models/{flash_next,qwen_27b,orcarouter_flash_next}.py`
- `wizard/menus/switching/{flash_next_27b,orcarouter_27b}.py`
- `wizard/menus/operations/{service,system}.py`, `wizard/menus/storage/flash_next_cleanup.py`
- `scripts/manager/{p1_wizard,p2_27b_benchmark,p3_persistent_switch,service_status,service_journal,service_manifest}.py`
- `scripts/manager/benchmark_publication.py`; `scripts/temporary/p3_stage_c_operator.py`
- 해당 `tests/test_*_cpu.py`와 `.github/workflows/recipe-manifest-cpu.yml`

일부 옛 문서에는 P2/P3 `NOT_RUN`, 'Flash-Next ACTIVE', 'P3-C pending' 등이 남아 있습니다. **새로운 실제 증거와 최신 날짜가 있는 핸드오프 섹션이 우선**입니다. 과거 기록을 삭제/소급 수정해 증거를 없애지 말고 최신 섹션 또는 headnote로 superseded 관계를 표현하세요.

## 3. 최신 실제 DGX 확인 결과 — 절대 역행 금지

2026-11-07 KST에 **P3-C 최종 Flash-Next→NVIDIA 27B 전환이 실제로 성공했습니다.** 이후 해당 서비스가 변경됐다는 새로운 사용자 실측 증거는 없습니다.

- P1 `nvidia/Qwen3.8-Flash-Next-NVFP4` revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`: vLLM 0.32 구동/API Completion·Chat·Tools·Vision Verify PASS, bounded benchmark PASS. P3-B 이후 **재 Verify PASS, 3회 실측 Benchmark PASS, 진단 PASS**; 이전 예제의 `POST-B P1 NOT_RUN` 상태는 완전히 과거 정보입니다.
- P2 `nvidia/Qwen3.8-27B-NVFP4` revision `482ca0f3832238542f8f5295dde86b5f22711d80`: pinned 19파일 다운로드, 실제 DGX GPU launch/trial/API PASS, 3회 streaming bounded Benchmark `BENCH_PASS_RESTORED_VERIFIED`, 당시 원본 Flash 서비스 복원 확인. 다시 다운로드하거나 초기 benchmark를 반복하지 마세요.
- P3-A Flash→27B **ACTUAL DGX PASS**; canonical `stage-a.json`.
- P3-B 27B→Flash **ACTUAL DGX PASS**; canonical `stage-b.json`. 당시 운영자 보조 보고서가 P3-A 파일명으로 잘못 저장된 과거 metadata 문제는 실제 성공을 무효화하지 않으며, 원본 파일 불변성을 지켜야 합니다.
- P3-B 후 P1 functional Verify/Benchmark/doctor/inventory rc3의 새 진단 증거가 **PASS**이고 원본 SHA가 P3-C 게이트로 검증됐습니다. `doctor/inventory rc3`는 예상된 원본 Flash 자체 이름/포트 점유로 증거 기반 판정됐으며 이를 현재 장애라고 다시 표시하지 마세요.
- P3-C Flash→27B **ACTUAL DGX PASS**. 별도 현재 SHA·`I_ACCEPT_FLASH_NEXT_DOWNTIME`·`I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C` 세 가지 TTY 수동 승인을 받은 뒤, 기존 Wizard canonical backend `./wizard.sh switch flash-next-27b stage-c --execute`가 성공: `wizard_result.status=PASS`, `executed=true`, `live_verified=true`, `active_model=27b`. Wrapper 최종 `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `issues=[]`. 원본 canonical 기록 `~/.local/state/blazux-wizard/p3/stage-c.json`, 보조 operator report `reports/transitions/flash-next--to--27b/p3-c-operator-20261107T011939Z-5f26a6ff25a2.json`. **이 시점 최종 모델은 `qwen3.8-27b` / 포트 8000. 성공 직후 자동 Flash 복귀 없음.** wrapper의 `current_model=flash-next`는 **전환 전 상태**이고 `post_switch_observed_model=27b`가 최종 상태입니다.
- 원본 Flash CID는 `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, 기존 보존된 27B CID는 `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`. Docker image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`는 공유 가능하므로 **모델 identity 자체로 판단 금지**. 새 세션에서 service 현황 재확인이 필요하다면 읽기 전용 `./wizard.sh service manager status --json`을 사용하고 직접 관측 전에는 '마지막 확인'이라고 표현할 것.
- Git-public allowlist benchmark: Flash `37.9527 mean tokens/sec`, original receipt SHA `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db`; 27B `7.9002 client E2E tokens/sec` 및 `11.1801 client decode proxy tokens/sec`, original SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`. 두 공개 요약은 실제 DGX 원본 private JSON과 `bash scripts/temporary/verify-published-benchmarks.sh`로 **2/2 VERIFIED**. 서로 다른 지표·3요청 제한 시험을 공정한 모델 성능 순위로 오도 금지.

**중요:** 이것은 P1~P3 **지정된 백엔드 기능/시험**의 DGX 수용입니다. 대화형 `./wizard.sh` 메뉴에서 P3 모델 전환을 실행하는 UX는 아직 수용되지 않았습니다. 실제 P3-C는 *tracked 임시 script → canonical Wizard CLI backend* 경로를 거쳤습니다. `wizard/console.py::_stage_actions()`는 현재 P3 stage 선택 시 `module.run([selected, "--plan"])`만 호출하며, 일반 모델 선택→반복 운영 전환은 아직 연결되어 있지 않습니다. P3 일회성 수행 영수증을 일반 운영 전환에 재사용하지 마세요.

## 4. P1~P7 전체 현황 — 두 종류의 완료 기준을 혼동 금지

| 단계 | 목표 | 실제 DGX 백엔드 | Wizard 운영 UX / 남은 일 |
|---|---|---|---|
| P1 | Flash-Next 설치/구동/Verify/Benchmark | **PASS** | 설치→사용→이력 등 전체 메뉴 통합 시험 미완료 |
| P2 | NVIDIA 27B pinned 설치/구동/Benchmark | **PASS** | 사용자 메뉴에서 설치·구동·상태·결과 전체 흐름 시험 미완료 |
| P3 | Flash↔27B 영구 전환 | **A/B/C PASS** | **일반 반복 전환 엔진과 통합 Wizard 메뉴 실행·취소·복구 UI 미완료** |
| P4 | Flash-Next 선택적 삭제/복구 | 조건부 **NOT_RUN** | 저장공간 필요 여부 판단, 정확한 삭제 대상과 별도 승인이 없으면 N/A |
| P5 | Orcarouter Flash-Next pinned adapter/serve/benchmark | **NOT_RUN** | `feature/orcarouter-bf16-adapter` 감사를 거쳐 vLLM 0.32 런타임 구현·실측 |
| P6 | Orcarouter↔27B 반복 전환·복구 | **NOT_RUN** | P5 PASS 후 실행 엔진 및 운영 UI, 양방향 복구 |
| P7 | 서비스·프록시·게이트웨이·릴리스 | **NOT_RELEASE_QUALIFIED** | 상태/health/logs 일부만 제공; 완전한 운영·복구·수치·배포 검증 필요 |

`wizard/roadmap.py`은 지금도 P3 상태를 정적 `SWITCH_EXECUTOR_NOT_QUALIFIED`라고 표시할 수 있습니다. 이는 **실제 수용 증거가 아닌 오래된 대시보드 분류**입니다. 고정 PASS로 바꾸는 편법 대신, 실제 영수증 검증 + 현재 live state + GUI UX 수용 상태를 구분하는 evidence-based dashboard로 개선하세요.

## 5. 이번 새 대화에서 실제로 수행할 작업 — Wizard-first UX 개발

**우선순위 1: 기존 흐름과 문제 재현**
- 최신 `wizard/console.py` / `wizard/workflow.py` / `wizard/quickstart.py` / `wizard/roadmap.py`의 실제 메뉴 동작·다중 프롬프트·중복 action 선택·stale SHA·blocker 표기 확인.
- 각 모델의 설치/검증/실행 가능 여부를 **실제 evidence 경계**로 분류. `docker Up`/저장소에 checkpoint 존재만으로 API qualified를 표시하지 않음.
- P3 CLI guarded executor와 현재 일반 Wizard 메뉴 연결 지점을 정확히 파악. **P3 A/B/C는 one-off라 재실행하지 말고, 일반 반복 전환에 별도 상태 계약이 필요한지 먼저 설계.**

**우선순위 2: UX 설계 및 실장비 변경 없는 구현**
- 기본 사용자 흐름은 `./wizard.sh` → **현재 활성 모델 및 API :8000 표시** → **모델 선택** → 현재 설치/recipe/Verify/Benchmark/전환 가능성 표시 → **한 번의 전환 요청** → 의미 있는 downtime 경고 → **신규 action-bound 현재 SHA/별도 수동 승인** → canonical guarded 실행기 → 모델 ID/API 최종 검증/원복 결과 표시.
- 보통 사용자는 내부 P1~P7 단계나 긴 shell 명령을 알 필요가 없게 하고, **안전 확인은 줄이지 말고 조작만 줄인다.**
- Flash↔27B 반복적인 운영 전환 기능은 P3 stage-A/B/C 완료 영수증에 의존해 다시 수행하는 방식이 아닌 **별도 모델 전환 계약**으로 설계. single-active :8000, 원본 컨테이너/HF caches 유지, docker stop-before-start, 상태 journal/lock, fail-closed, rollback, timeout, target model ID 확인 조건 유지.
- 상태 화면에 **과거 acceptance PASS**, **현재 live API**, **실행 가능한 전환**, **UI 통합 검증 상태**를 각각 표시. `wizard/roadmap.py`의 정적/역사적 status 오류도 개선.
- 필요하면 `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`와 새 UX 계약서를 갱신하되 기존 `./wizard.sh` CLI/JSON 호환, P1/P2/P3 API 동작·영수증·이름을 깨뜨리지 않음.

**우선순위 3: Fake-DGX CPU 회귀·문서·GitHub**
- 소스 테스트: Flash ACTIVE/27B ACTIVE/없는 모델/설치되었지만 미검증/unknown service, 성공·취소·오입력·만료/변경된 SHA, downtime 미동의, target startup fail, rollback success/fail, receipt mismatch, API model ID mismatch, 포트 8000 충돌, one-active 준수, 메뉴 navigation/키보드 동작/긴 원문 출력 축약, 기존 CLI 호환.
- 이미 존재하는 테스트를 삭제/완화하지 말고 커밋별 CI 검증. 실장비 검증 결과와 CPU fake-DGX 결과를 구분.
- 핸드오프/설계/변경 기록 업데이트, PR #1에 구체적 리뷰 코멘트. **PR 머지는 요청하지 않으면 절대 금지**.
- 신규 DGX 운영 점검은 먼저 **GitHub에 추적되는 `scripts/temporary/` 스크립트**로 구현하고 CPU 테스트/CI 후 사용자가 `git pull --ff-only origin feature/recipe-wizard-handoff`로 받는 방식(D-016). 동작 기본값 read-only. 기존 P1~P3 성공 시험은 무의미하게 반복하지 않는다.

**후속:** P4 저장용량 결정(불필요하면 `NOT_APPLICABLE`) → P5 Orcarouter adapter/실장비 benchmark → P6 Orcarouter↔27B 일반 전환 → P7 proxy/gateway/service/logging/릴리스 검증. 작업 전 기존 병렬 Orcarouter 브랜치 내용 검토. 미검증 모델을 활성화하지 말고, P5용 설계/테스트 코드가 실제로 DGX에서 돌았다고 주장하지 않는다.

## 6. 승인·데이터 보호·실행 금지 조건

- **현재 마지막 실측된 27B 서비스 ACTIVE**; 새 UX 소스 개발을 위해 이를 중단·복구·전환하거나 P3-C를 다시 호출하지 않음.
- 실제 DGX GPU 추론·벤치마크는 작업별 신규 동의 필요. 실제 서비스 stop/start/restart/model switch/rollback/삭제는 별도 명시적 downtime/작업 범위 승인 필수. 소스 구현·GitHub CI는 서비스 운영 승인과 별개.
- **기존 P3-A/B/C 전체 재실행 금지**, expired plan SHA 재사용 금지, 승인 문자열 자동 입력 금지, 타 단계의 승인 재활용 금지. 실패 발생 시 무조건 재시도하지 말고 receipt와 상태를 진단한다.
- 단일 모델, vLLM 0.32, API :8000, NVIDIA 원본 및 Orcarouter cache `~/.cache/huggingface`, `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`, `recipe-views`, Docker 컨테이너/이미지/HF snapshots/manifest/journal/attempt markers/0600 JSON 영수증 보존.
- `docker system prune`, `git reset --hard`, `git clean -fd`, HF 캐시 무단 삭제/재다운로드, 로그/프롬프트/토큰/승인 키/원본 private JSON의 Git 업로드 금지.
- Git-public `benchmarks/published/`는 정확히 allowlisted 메트릭과 원본 SHA만 보관. raw private 보고서 변경, 기존 Git 보고서 overwrite, 지표를 섞은 미검증 비교 금지.
- OpenWebUI/Portainer와 기존 API 클라이언트 영향은 반드시 전환 계획에 표시. 실제 시간·최종 모델·관측 점수는 새 DGX 로그 없이는 추측하지 않음.
- 중요한 상태와 결정은 `handoff/`에 **다음 새 대화에서도 복구할 수 있게** append-only/최신 섹션 우선 구조로 기록하고, 과거 모순은 superseded를 명확히 한다.

## 7. 첫 번째 행동 및 응답 형식

1. GitHub 연결 도구로 최신 branch HEAD / Draft PR #1 / CI / 주요 실행 파일과 핸드오프를 직접 조회. 새로운 브랜치·PR을 불필요하게 생성하지 않음.
2. `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md`와 현재 소스를 대조하여 **이미 검증된 P1/P2/P3 백엔드**와 **아직 미완성 Wizard UX**의 갭을 구체적으로 기록.
3. **P3-A/B/C 재실행 없이** 통합 메뉴·운영 전환 실행 계약·사용성 개선 설계와 가능한 소스/모의 CPU 테스트를 GitHub에서 직접 구현하고 CI까지 검증.
4. 작업 결과를 `WHAT CHANGED`, `GITHUB HEAD/PR/CI`, `FAKE-CPU TEST RESULTS`, `ACTUAL DGX KNOWN STATE`, `UX ACCEPTANCE / BLOCKERS`, `FILES/DOCS`, `NEXT SAFE OPERATOR ACTION`으로 구분해 보고.
5. 실제 live 서비스 변경이 필요한 검증 단계에 도달하면 **그 작업 범위와 다운타임 영향을 설명한 뒤 명시적 승인을 받아야 한다**. 승인이 없는 상태에서는 코드/문서/CPU-only까지 완료하고, 필요하면 단일 read-only 추적 스크립트만 제시.

**이번 대화에서 완료할 핵심 목표: 일반 운영자가 메뉴에서 모델을 선택해 쉽게 상태·벤치·전환을 관리할 수 있도록 Wizard를 개발하고, 안전성을 후퇴시키지 않는 CPU 회귀/CI/인수인계까지 진행. 실제 27B 서비스는 유지.**