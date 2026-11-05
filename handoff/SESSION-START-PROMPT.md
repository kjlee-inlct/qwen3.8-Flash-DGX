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

## 진행 규칙

`handoff/OPERATING-RULES.md`를 필수 규칙으로 적용하세요. 과거 Orcarouter 컨테이너와 API `:8000/v1`은 사용자가 서비스 삭제를 보고한 **역사적 환경**입니다. 이를 현재 실행 중으로 추정하지 말고, DGX의 실제 컨테이너/포트/이미지/캐시를 읽기 전용으로 새로 확인하세요. 새 NVIDIA Flash-Next 기본 목표 API는 `:8000/v1`이지만 현재 포트 점유는 미확인입니다. 기존 공유 이미지/모델 파일/HF 캐시/기타 컨테이너와 클라이언트는 확인 없이 변경하지 마세요. 정비창/모델 기동/GPU 사용/전환/삭제는 구체적 범위와 원복계획을 먼저 수립하고 별도 승인을 받아야 합니다. 문서상 P4가 있다고 해서 삭제 허가가 난 것은 아닙니다.

안전한 범위에서는 질문 턴을 최소화하도록 소스 분석→구현→CPU 테스트→문서→GitHub 커밋/PR 검토를 가능한 한 묶어서 진행하세요. 기존 코드가 있으면 재사용하고 필요 시 scripts/tests/docs를 신규 생성하세요. 매 완료 단계에서 `handoff/CURRENT-STATE.md`, `NEXT-ACTIONS.md`, `CHANGELOG.md`를 갱신하고, 시험/결정이 바뀐 경우 각각 `EVIDENCE-LEDGER.md`/`DECISIONS.md`도 갱신하세요.

**출력:** 실제 작업 결과, 최신 브랜치/HEAD/PR/CI, PASS/FAIL/NOT_RUN을 구분한 검증, 현재 DGX 관측값과 과거 정보를 구별, 미완료·차단·승인 사항, 다음 1~3개 실행 작업을 간결하게 제시하세요. 완료되지 않은 작업은 완료로 표현하지 마세요.

**시작할 작업:** `handoff/NEXT-ACTIONS.md`의 첫 번째 안전한 미완료 항목부터 실행하세요. 새 대화에서 이 프롬프트가 뒤늦게 사용되면 실제 GitHub와 handoff 상태를 우선하세요.
