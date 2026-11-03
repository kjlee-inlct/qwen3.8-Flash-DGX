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

## 진행 규칙

`handoff/OPERATING-RULES.md`를 필수 규칙으로 적용하세요. 기존 DGX Orcarouter Docker 컨테이너, 이미지, API `:8000/v1`, 모델 파일, HF cache 및 연결 클라이언트를 건드리지 마세요. 정비창/모델 기동/GPU 사용/전환/삭제는 구체적 범위와 원복계획을 먼저 수립하고 별도 승인을 받아야 합니다. 문서상 P4가 있다고 해서 삭제 허가가 난 것은 아닙니다.

안전한 범위에서는 질문 턴을 최소화하도록 소스 분석→구현→CPU 테스트→문서→GitHub 커밋/PR 검토를 가능한 한 묶어서 진행하세요. 기존 코드가 있으면 재사용하고 필요 시 scripts/tests/docs를 신규 생성하세요. 매 완료 단계에서 `handoff/CURRENT-STATE.md`, `NEXT-ACTIONS.md`, `CHANGELOG.md`를 갱신하고, 시험/결정이 바뀐 경우 각각 `EVIDENCE-LEDGER.md`/`DECISIONS.md`도 갱신하세요.

**출력:** 실제 작업 결과, 최신 브랜치/HEAD/PR/CI, PASS/FAIL/NOT_RUN을 구분한 검증, 현재 DGX 관측값과 과거 정보를 구별, 미완료·차단·승인 사항, 다음 1~3개 실행 작업을 간결하게 제시하세요. 완료되지 않은 작업은 완료로 표현하지 마세요.

**시작할 작업:** `handoff/NEXT-ACTIONS.md`의 첫 번째 안전한 미완료 항목부터 실행하세요. 새 대화에서 이 프롬프트가 뒤늦게 사용되면 실제 GitHub와 handoff 상태를 우선하세요.
