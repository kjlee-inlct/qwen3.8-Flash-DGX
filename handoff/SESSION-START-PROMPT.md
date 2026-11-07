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