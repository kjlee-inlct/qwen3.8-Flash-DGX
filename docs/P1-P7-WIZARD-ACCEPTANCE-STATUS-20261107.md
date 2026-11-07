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
