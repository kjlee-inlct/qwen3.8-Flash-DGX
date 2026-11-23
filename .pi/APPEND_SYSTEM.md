# blazux-orcarouter 프로젝트 작업 지침

## 응답 및 조사

- 한국어를 기본 언어로 사용한다. 명령어, 식별자, 경로, 오류 메시지, 데이터시트·upstream 원문 용어는 원문을 유지한다.
- 작업 전 다음을 확인한다: `git status --short --branch`, 현재 HEAD, remotes, 관련 README/로드맵/핸드오프, 변경 대상의 기존 구현과 테스트.
- 현재 사실, 문서상 주장, 계산 추정, 미검증 가설을 구분한다. 실제 실행하지 않은 테스트·CI·DGX 관측·운영 수용을 PASS로 쓰지 않는다.
- 문서 작업은 역사적 evidence를 덮어쓰지 않는다. 서로 다른 SHA의 테스트 결과를 합산하거나 최신 HEAD로 소급하지 않는다.

## 프로젝트 불변 조건

- 대상 브랜치: `feature/recipe-wizard-handoff`; `main`은 변경하지 않는다.
- PR #1은 별도 지시 없이는 Draft/Open/Unmerged로 유지한다. PR merge, force push, rebase/reset은 하지 않는다.
- 기본 런타임 계약: vLLM `0.32.0`, SGLang 금지, `ONE_ACTIVE_MODEL_ONLY`, host API `:8000/v1`.
- 별도 명시 승인이 없으면 다음을 실행하지 않는다: Docker/GPU/inference/benchmark, 서비스 stop/start/restart, model switch/reinstall/download/delete, HF cache·PLE·image cleanup, operating Journal/nonce 변경, sudo/ptrace/procfs 권한 승격, firewall/NAT/sysctl 변경, GitHub Actions dispatch/rerun/trigger 실험, `main` 변경, PR merge.
- upstream 변경은 자동 merge/rebase하지 않는다. 먼저 merge-base 기반으로 감사하고, 0.32 유지·선택 backport·별도 후보 검증을 분리한다. vLLM 0.33 upstream 결과를 이 fork의 Orcarouter/MTP2 수용 결과로 간주하지 않는다.

## 검증 및 문서화

- CPU/source-only, GitHub Actions CI, DGX read-only, DGX live, operating acceptance를 별도 증거 유형으로 기록한다.
- 테스트 결과에는 정확한 source SHA, 명령/패턴, 테스트 수, RC, clean-tree 여부와 CI Run ID를 가능한 범위에서 기록한다. CI run/check/status가 없으면 `CI_UNVERIFIED`로 유지한다.
- P1–P8의 정식 실행 진입점은 `docs/P1-P8-UNFINISHED-WORK-ROADMAP-20261121.md`이다. 기존 날짜별 로드맵·`handoff/` 문서는 역사적 증거로 보존한다.
- `MTP0 != MTP2`, `SOURCE/CPU PASS != DGX PASS`, `Fake-DGX != live recovery`, `이관 != 완료`를 상태 판정에 적용한다.
- 변경 시 관련 `handoff/CURRENT-STATE.md`, `handoff/NEXT-ACTIONS.md`, `handoff/EVIDENCE-LEDGER.md`, `handoff/DECISIONS.md`의 갱신 필요성을 확인한다. 원본 operator receipt와 private 경로·secret은 커밋하지 않는다.
- 기존 테스트를 삭제·완화하지 않는다. 문서 링크, manifest inventory, 관련 CPU 회귀를 먼저 실행하고 실패 원인을 해결하거나 명확히 보고한다.

## 커밋 메시지 규칙

- Conventional Commits 형식: `<type>(<scope>): <imperative summary>`.
- 허용 type: `feat`, `fix`, `test`, `docs`, `refactor`, `build`, `chore`. 문서·인수인계는 보통 `docs`, 테스트만은 `test`, 동작 결함은 `fix`, 새 기능은 `feat`를 사용한다.
- scope는 변경 영역을 소문자 단일 토큰으로 우선 사용한다: `p7`, `p6-e`, `p5d`, `manifest`, `handoff`, `roadmap`, `wizard`, `ci`. 기존 기록에 대문자 scope가 있어도 신규 메시지는 소문자를 우선한다.
- summary는 영어 imperative, 짧고 구체적으로 작성하며 마침표를 붙이지 않는다. 예: `docs(roadmap): restore unfinished P1-P8 gates`.
- 한 커밋에는 하나의 논리적 목적만 담는다. 코드/테스트/필수 문서는 함께 커밋할 수 있지만 unrelated cleanup은 분리한다.
- 커밋 전에 `git diff --check`와 관련 CPU 테스트를 실행한다. 커밋 후 `git rev-parse HEAD`, `git status --short --branch`, 원격 HEAD를 재확인한다.
- push는 현재 feature 브랜치에만 한다. push 전 원격 HEAD가 예상한 값인지 확인하고, 강제 push는 하지 않는다.

## 기본 작업 보고 형식

1. 요구사항과 현재 증거
2. 변경 파일 및 이유
3. 실행한 검사: 명령, count, RC, SHA, CI 상태
4. 미검증·차단 항목 및 운영 승인 경계
5. 커밋·원격 반영 상태
