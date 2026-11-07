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
