## 2026-11-07 — CURRENT P3-C HANDOFF (SUPERSEDES OLDER "P1 NOT_RUN"/"B PENDING")

User completed actual P3-A and P3-B transitions, original Flash-Next remains live on :8000. Post-B P1 Verify and numeric 3-request Benchmark PASS, original doctor/inventory own-port collision diagnosed as benign. Actual DGX `./wizard.sh switch flash-next-27b stage-c --plan --json` is `READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, `p1_evidence.status=PASS`, `executed=false`, original Flash CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, preserved 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`. Its short-lived plan SHA must not be reused. Optional `evidence migrate --guided` received literal `COPY` and returned `CANCELLED/copied=0`; import optional, independent of C.

Per D-016, new GitHub-tracked `scripts/temporary/p3-stage-c-operator.sh` and Python `p3_stage_c_operator.py` invoke canonical C Wizard after separate live approval; default `--plan` non-disruptive. `--execute` requires TTY + independent EXACT new SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`, then fresh plan/API recheck. Third literal is wrapper-only; core C expects no `--enter-p3`. Final C success requires independently verified 27B :8000 API + immutable old-root stage-c receipt and leaves 27B serving. Preserve Flash/27B models and original P2/P3 canonical state. CPU tests/fake DGX + CI required; no actual new C switch or PR merge. See `docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md`.

Next operator: confirm latest GitHub HEAD and CI, clean `git pull --ff-only origin feature/recipe-wizard-handoff`, run ONLY `bash scripts/temporary/p3-stage-c-operator.sh --plan`; if READY/empty issues, separately secure explicit user Flash downtime authorization before `--execute`. Do not auto-run or blindly repeat C on failure.

---

## 2026-11-07 — Latest handoff override (read before historical prompt below)

**Current stage:** P2 complete; P3-A actual DGX PASS; **P3-B actual DGX PASS** with original Flash-Next restored and served `qwen3.8-flash-next` on port 8000. The previous "P3-B NOT_RUN / 27B ACTIVE" headings below are historical. Canonical B receipt `~/.local/state/blazux-wizard/p3/stage-b.json`; wrapper old report misnamed `~/blazux-p3-reports/p3-a-operator-20261106T223124Z-14861d75.json`. P1 post-B inspect-only readiness PASS `~/blazux-p1-reports/20261106T224010Z-d2095867/result.json`. P1 Verify/Benchmark after B NOT_RUN and doctor/inventory post-B raw cause needs a new independent audit. P3-C NOT_RUN/NOT_AUTHORIZED.

**New D-016 tracked source action:** `bash scripts/temporary/p1-post-b-audit.sh` is always read-only. It creates an immutable private post-B `p1-diagnostics-*.json` from canonical inspect-only + raw doctor/inventory JSON after verifying B receipt and Flash API. Run only after latest GitHub CI passes and DGX fast-forward pull. Fail closed on mismatch; do not execute GPU verify, benchmark, P3-C, A/B replay, Docker cleanup or PR merge. Independent action approvals required later. Recheck current HEAD/PR/CI before changes; branch `feature/recipe-wizard-handoff`, Draft PR #1 remains unmerged. See `handoff/CURRENT-STATE.md`, D-042/D-043, and `handoff/NEXT-ACTIONS.md`. All previous content below is history unless consistent with this override.

---

> **SUPERSEDING 2026-11-06 HANDOFF (read this first):** P2 NVIDIA 27B actual DGX benchmark **BENCH_PASS_RESTORED_VERIFIED** and Flash-Next recovery **LIVE_SERVICE_VERIFIED**; no further P2 GPU/download/build work. Stage P3 governed by D-034: separately approved Flash→27B (A) → separately approved 27B→Flash (B) → P1 rc=3 gap closure, functional re-verify and real measured Flash benchmark → separately approved final Flash→27B (C). Source P3 manual switch executor and P1 evidence gate are added, with CPU tests; P3 actual GPU service changes **NOT_RUN/NOT_QUALIFIED**. The older P1/P2/P3 roadmap below is historical where conflicting. Use [CURRENT-STATE](CURRENT-STATE.md), [DECISIONS](DECISIONS.md), [P3 source runbook](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md) and latest GitHub HEAD/CI. PR #1 Draft/unmerged; no GPU change, cleanup or merge without separate authorization.

# New conversation starter — copy as a single prompt

아래 저장소의 **레시피/Wizard/서비스 관리 개발**을 이전 작업에서 이어서 수행해주세요.

**저장소:** https://github.com/kjlee-inlct/qwen3.8-Flash-DGX  
**현재 작업 브랜치:** `feature/recipe-wizard-handoff`  
**별도 병렬 브랜치:** `feature/orcarouter-bf16-adapter`  
**upstream:** https://github.com/blazux/qwen3.8-Flash-DGX

## 반드시 먼저 확인할 파일

1. `handoff/README.md`
2. `handoff/CURRENT-STATE.md`
3. `handoff/OPERATING-RULES.md`
4. `handoff/NEXT-ACTIONS.md`
5. `handoff/EVIDENCE-LEDGER.md`
6. `handoff/DECISIONS.md`
7. `docs/MODEL-RECIPE-WIZARD-PLAN.md`
8. `docs/MANIFEST-CONTRACTS.md`

GitHub 연결 도구를 이용하여 해당 브랜치의 **실제 HEAD, 열린 PR, 변경 파일, CI**를 조회하고, 문서의 마지막 상태와 대조하세요. 이전 대화의 추정이나 과거 SHA를 현재 상태로 간주하지 마세요.

## 작업 목표

Blazux/vLLM 0.32 기반에서 (1) Flash-Next 구동/벤치, (2) 27B 구동/벤치, (3) 양방향 전환, (4) **별도 승인된** Flash-Next 체크포인트 정리, (5) Orcarouter BF16 PLE/MTP2 구동/벤치, (6) Orcarouter↔27B 전환을 재현 가능한 **모델 레시피 + manifest + Wizard + 서비스/프록시/게이트웨이/Docker/저장공간 관리** 체계로 구현합니다. **SGLang 사용 금지**. 모델 별 구현과 실제 실행 검증을 혼동하지 마세요.

## 최신 확정 개발 순서 — **Wizard 필수** (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

P1은 `doctor/plan`까지만 소스 구현되었으며 설치·기동·API 검증·벤치마크·증거 저장까지의 end-to-end Wizard는 미완성입니다. **다음 시작 작업은 이를 완성하는 것**입니다. P2~P7은 앞 단계 DGX 검증·용량·승인 조건을 지키며 순서대로 진행합니다. 포트 `8000/v1` 유지 목표, 모델별 served ID 관리, vLLM 0.32만 허용합니다.

## Wizard 개발 구조 (2026-11-05 추가 확정)

**Wizard architecture decision (2026-11-05):** Implement all P1–P7 **menu/CLI modules first** and then integrate/debug actual runtime in P1→P7 order. Root operator entry is `./wizard.sh`; `wizard/menus/models/`, `switching/`, `storage/`, and `operations/` own per-menu behavior, with `wizard/main.py` and `wizard/menus/common.py` for routing and safe source contracts. Scripts accept explicit stage/action arguments and emit JSON and stable exit codes for operator-mediated DGX tests. Only P1 calls the existing guarded backend today; P2–P7 are SOURCE-ONLY plans and must never execute merely because a menu exists. No SGLang; vLLM 0.32 only.

사용자 DGX는 Shell에서 Wizard 인자를 직접 실행하고 JSON 결과를 복사해 전달할 수 있으므로, **대화형과 비대화형 기능이 동일**해야 합니다. `./wizard.sh list --json`, `./wizard.sh p1 status --json`, `./wizard.sh p1 plan --for-action verify --json`부터 사용하세요. 미완성 P2~P7에서는 실행 대신 `BLOCKED`가 정상입니다. 현재 사용자의 `./flash setup default` 다운로드 및 이미 입력된 `serve/wait/test` 순서를 건드리지 마세요. 설치/기동/전환/제거는 단계별 인가와 실제 DGX 검증이 필요합니다.

## 최신 Wizard 기능군별 구조 — D-015 (2026-11-05)

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

다음 대화에서는 `./wizard.sh model flash-next status --json`, `./wizard.sh switch flash-next-27b ...` 형태를 우선 사용하고, P1~P7은 구버전 호환 별칭으로만 취급합니다. 서브모듈 변경 시 기능군 폴더와 테스트를 같이 수정하세요. 새 구조는 GitHub CI 통과만 확인되었으며, 실제 DGX Wizard 벤치는 아직 미수행입니다.

## 임시 DGX 스크립트 운영 규칙 — D-016/R1D

긴 명령 블록을 반복해서 보내는 대신, `scripts/temporary/`에 목적별 단일 임시 실행 스크립트와 CPU 모의 테스트/README를 생성하고 GitHub에 커밋하여 CI 및 handoff를 갱신합니다. 사용자는 기존 DGX 다운로드/기동 셸 체인이 모두 끝난 뒤 `git pull --ff-only`하고 스크립트 하나를 실행합니다. 스크립트는 ① 읽기 전용 환경 점검 → ② 최신 Wizard plan ID별 별도 승인된 검증·벤치 → ③ 결과 JSON/증거 경로 수집을 묶습니다. 승인이나 준비가 없으면 BLOCKED를 보고하고 GPU를 실행하지 않습니다. 서버/캐시 중단·삭제, 재다운로드, Git 자동 갱신, 로그 자동 업로드를 하지 않습니다. 스크립트 정리는 증거 영구 기록 후 별도 PR/커밋으로만 수행합니다. 상세 규칙은 `handoff/OPERATING-RULES.md` R1D, `scripts/temporary/README.md` 및 결정 D-016을 읽으세요.

## 2026-11-05 — D-017, Blazux 기본 Flash-Next 호환과 GPU 허용

사용자가 제공한 DGX 결과에서 `qwen3.8-flash-next` API ID를 확인했고, 원본 index/tokenizer와 Hybrid tokenizer는 실재하는 **외부 경로 심볼릭 링크**로서 새로운 Wizard가 과도하게 차단했습니다. Blazux 기본 `os.path.exists` 동작과 일치하도록 메타데이터 두 파일만 기존 링크를 허용하고 weight shard 탈출은 금지합니다. 사용자는 **기존 서비스 중단 없는 bounded P1 GPU/API 검증·벤치**를 별도의 plan-hash 입력 없이 허용했습니다. 최신 단일 스크립트 `bash scripts/temporary/p1-post-download.sh --auto-gpu`는 현재 plan ID를 내부에서 받아 Wizard에 재검증시킵니다. 원본 Docker 컨테이너 재기동/삭제, 모델 다운로드, Hybrid 재생성, P2–P7 전환은 별도 허가가 필요합니다. 사용자의 '서비스 없음' 설명과 실제 API 응답을 구분하여, 활성 모델 서버/포트를 보호해야 합니다.

## 진행 규칙

`handoff/OPERATING-RULES.md`를 필수 규칙으로 적용하세요. 과거 Orcarouter 컨테이너와 API `:8000/v1`은 사용자가 서비스 삭제를 보고한 **역사적 환경**입니다. 이를 현재 실행 중으로 추정하지 말고, DGX의 실제 컨테이너/포트/이미지/캐시를 읽기 전용으로 새로 확인하세요. 새 NVIDIA Flash-Next 기본 목표 API는 `:8000/v1`이지만 현재 포트 점유는 미확인입니다. 기존 공유 이미지/모델 파일/HF 캐시/기타 컨테이너와 클라이언트는 확인 없이 변경하지 마세요. 정비창/모델 기동/GPU 사용/전환/삭제는 구체적 범위와 원복계획을 먼저 수립하고 별도 승인을 받아야 합니다. 문서상 P4가 있다고 해서 삭제 허가가 난 것은 아닙니다.

안전한 범위에서는 질문 턴을 최소화하도록 소스 분석→구현→CPU 테스트→문서→GitHub 커밋/PR 검토를 가능한 한 묶어서 진행하세요. 기존 코드가 있으면 재사용하고 필요 시 scripts/tests/docs를 신규 생성하세요. 매 완료 단계에서 `handoff/CURRENT-STATE.md`, `NEXT-ACTIONS.md`, `CHANGELOG.md`를 갱신하고, 시험/결정이 바뀐 경우 각각 `EVIDENCE-LEDGER.md`/`DECISIONS.md`도 갱신하세요.

**출력:** 실제 작업 결과, 최신 브랜치/HEAD/PR/CI, PASS/FAIL/NOT_RUN을 구분한 검증, 현재 DGX 관측값과 과거 정보를 구별, 미완료·차단·승인 사항, 다음 1~3개 실행 작업을 간결하게 제시하세요. 완료되지 않은 작업은 완료로 표현하지 마세요.

**시작할 작업:** `handoff/NEXT-ACTIONS.md`의 첫 번째 안전한 미완료 항목부터 실행하세요. 새 대화에서 이 프롬프트가 뒤늦게 사용되면 실제 GitHub와 handoff 상태를 우선하세요.
