## 2026-11-21 KST — P7 16/16 CPU PASS confirmed (supersedes earlier NOT_RUN at tested SHA)
- **Tested checkout HEAD:** `c36b2bf9124b1237606d2d1d138929bfd138485c` after fast-forward, operator transcript `Ran 16 tests in 0.006s / OK`, `P7_CPU_RC=0`. GitHub PR #1 direct read at intake was Draft/Open/Unmerged, base main, HEAD identical to that SHA. Direct test blob `d2eb49469e2b1407e8e571e33a087dc444795f3f`. Newly added 3 methods for cross-session/nonce, missing capture root/collector and false authentication assumption all reported `ok`. This is **operator-reported CPU-only evidence, not GitHub Actions**.
- **Previous NOT_RUN retained as historical context:** P7 source/test commits `9e09e6df`/`9e8f578b`; source-only captures remain editable. `capture_provenance_authenticated=false`, `replay_prevention_verified=false`, all real/operations/production permissions false. Exact tested SHA PR-associated runs 0 and commit statuses 0; **CI_UNVERIFIED**. Clean worktree: `git status --short` produced no visible changes in supplied transcript, without independently attested filesystem provenance.
- **Other suites not re-run at this SHA:** Wizard prior 126/126 RC0 at `a4bd913`, Manifest prior 77/77 RC0 at `dcf73332` (Cleanup 12 subset), P6-E 37/37 RC0 at `4c86b799`. Next run **Wizard+Manifest broader CPU-only** on the then-current checkout, capturing exact HEAD/status/counts/RCs. Following design target is a verifiable P7 collector/trust issuer, signed canonical receipt, durable nonce replay ledger and independently bound service identity; do not treat matching labels as proof.
- **No approved operating release:** P5-D PLE/NAT BLOCKED, P6-E operating Journal/nonce BLOCKED, P7 independent origin PENDING, P8 actual recovery BLOCKED, Production BLOCKED. No DGX service mutation, sudo, Docker, GPU inference, cache cleanup, Actions dispatch, main write or PR merge.

## 2026-11-21 KST — P7 cross-session capture identity update (new session handoff)
- Baseline read-only PR head **`feee718bce461bffb14c27940843b469a1ac536a`**, PR #1 Draft/Open/Unmerged, base main. Re-read latest head on every new session; do not assume this SHA still current.
- Existing `integration_contract.py` verified to contain registered model/served ID, container/upstream 64-hex equality, :8000, strict numeric, timezone/future skew, duplicate probe-ID and storage path checks. Missing boundary: different capture sessions/nonces could be collaged into one apparently consistent *source-only* document. Baseline behavior inferred by direct source inspection; **baseline repro not executed**.
- Feature source commit **`9e09e6df2ed156c065e839bc7602a726a95f6887`** binds root `capture_session_id`/`capture_nonce` to four component entries; each requires nonblank `collector_id`. Test commit **`9e8f578bc12cfe448a10abd3ce11a371b735d2f7`** updates fixtures and adds three positive/negative regressions: **16 expected P7 CPU methods; NOT_RUN** (no full repo CPU runner accessible in assistant environment), RC unavailable. Legacy evidence files lacking capture metadata are intentionally BLOCKED. No runtime action taken.
- New flags `capture_provenance_authenticated=false`, `replay_prevention_verified=false`; all existing live/operations/release flags remain false. **Any JSON author can copy consistent capture values**, so source consistency cannot authenticate collector, command/session issue, Docker/process origin, replay or operating authority. Future authenticated read-only collectors and durable nonce ledger remain PENDING and require separate approved design/observations.
- Historical CPU receipts remain separate: P6-E 37/37 RC0 at `4c86b799`; P7 13/13 RC0 at `77fe76a8`; Wizard 126/126 RC0 at `a4bd913`; Manifest 77/77 RC0 (Cleanup 12 subset) at `dcf73332`. No transfer to this commit or documentation-only HEAD. GitHub CI still requires exact-SHA run ID; **CI_UNVERIFIED** until confirmed.
- Next operator: checkout actual feature head on clean tree; run P7 16 methods, Wizard/Manifest regressions with exact SHA and RC, validate CLI behavior under new schema, then review origin-verifiable signed/attested collector trust and durable nonce replay fences. No Docker/GPU/serving, procfs permissions, CI dispatch, operating journal, main writes or PR merge. P5-D live PLE/NAT, P6-E real Journal/Nonce, P7 live authenticated capture, P8 recovery and release remain BLOCKED/NOT_ACCEPTED.

## 2026-11-21 KST — 새 세션 최종 인수인계 (문서 커밋 전 HEAD 4c28ee8778a4837a0b7f4452a0195af460acd038)
- GitHub feature branch HEAD를 직접 대조해 `4c28ee8778a4837a0b7f4452a0195af460acd038`와 identical 확인. 문서 변경으로 최종 HEAD는 달라지므로 시작 시 반드시 다시 조회.
- **CPU 검증은 각각 다른 SHA:** P6-E 37/37 RC0 at `4c86b799`; P7 13/13 RC0 at `77fe76a8`; Wizard 126/126 RC0 at `a4bd913`; Cleanup 12/12 RC0 및 Manifest 77/77 RC0 (서브셋 중복 계산 금지) at `dcf73332`. 실제 CI는 최신 exact-SHA 검증되지 않았으며 doc-only HEAD는 CPU PASS가 아님.
- Next action: P7 independent/authenticated observation provenance boundary, model/service identity binding and fail-closed source-only tests; no runtime modifications or unapproved CI.

# 새 세션 실행 프롬프트 — Blazux DGX Spark / P7 independent provenance (2026-11-21)

이전 Blazux DGX Spark GB10 / vLLM 0.32.0 / P1–P8 개발을 이어서 수행해주세요. **단순 계획이나 요약으로 끝내지 말고**, GitHub 연결 도구로 최신 소스/문서를 확인한 뒤 허용된 **source-only 범위에서** 실제 결함 재현 → 최소 구현 → 부정 조건 CPU 테스트 추가 → 가능한 검증 → feature 브랜치 커밋 → 최신 SHA/CI 조회 → 영구 문서 갱신까지 진행하세요. 기존 구현을 중복 개발하지 마세요. 새로운 오류가 없다면 임의 코드 변경 대신 근거 있는 테스트/문서 개선을 수행하세요.

## 저장소와 진입점
- Development: https://github.com/kjlee-inlct/qwen3.8-Flash-DGX
- Upstream: https://github.com/blazux/qwen3.8-Flash-DGX
- Branch: `feature/recipe-wizard-handoff`; PR #1: https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1 (기록상 Draft/Open/Unmerged, base main; **현재 상태 재조회**)
- 작업 전 확인한 HEAD: `4c28ee8778a4837a0b7f4452a0195af460acd038`. **인수인계 문서 커밋 후 SHA는 바뀌므로 이것을 현재 HEAD로 단정하지 마세요.**
- 최우선 문서: `handoff/SESSION-HANDOFF-P7-20261120.md`, `handoff/SESSION-START-PROMPT.md`, `handoff/EVIDENCE-LEDGER.md`, `handoff/NEXT-ACTIONS.md`, `handoff/DECISIONS.md`, `docs/P1-P8-EXECUTION-ROADMAP-20261119.md`, `docs/P7-PROBE-ID-INDEPENDENCE-CONTRACT-20261120.md`, `docs/WIZARD-CLI-CONTRACT.md`.
- Source: `scripts/manager/integration_contract.py`, `scripts/manager/generic_operations.py`, `scripts/manager/manifest_cleanup.py`, `tests/test_integration_contract_cpu.py`, `tests/test_manifest_cleanup_cpu.py`, `wizard/main.py`, 서비스/모델 Manifest.

## 마지막으로 확정한 CPU 증거 — SHA별로 분리
- P6-E Fake Journal/Nonce: `4c86b7990ea865a31bb78a346ca92867ed5e9e83`에서 Journal **22/22 RC0** + Fake Nonce **15/15 RC0** = **37/37** (운영자 로그, CI 아님).
- P7 upstream/service identity source consistency: `77fe76a839d85930533536ec2db5af3c1f4c7293`에서 **13/13 RC0 (0.005s)**. Proxy/Gateway `upstream_container_id`가 Service `container_id`와 동일한 유효 64-hex여야 한다. Numeric type, timestamp +120s, normalized duplicate `probe_id`, model/served ID, fixed :8000도 기존 구현됨. **편집 가능한 JSON 필드는 독립 인증이 아님**.
- Wizard CPU: `a4bd913267f688129477415fd7d15c6842122acb`에서 **126/126 RC0 (61.070s)** (운영자 로그).
- Manifest cleanup 이전 오류: `a4bd913...`에서 **76건 중 2 ERROR, RC1** (`manifest_cleanup.py`의 지역 `status`가 전역 함수 `status()`를 shadow); 소스 수정 `84352446dfcdafd9002a16f05b67fc0300318aa1`, 테스트 추가 `6a76c425a7b4916c8fcec9d0c98cfb124d361200`; 신규 테스트에 double-backslash SyntaxError가 발생한 뒤 `9f891f85eac8fd595c74a824b4f9efe20938ddd4`에서 수정.
- **최신 Manifest 검증 완료**: `dcf73332e8ffc8d729b9cbf4b35d08c52643421b`에서 Python AST **2/2 OK**, Cleanup **12/12 RC0 (0.003s)**, full Manifest **77/77 RC0 (0.141s)**. **12개는 77개에 포함되므로 중복 합산 금지**. `git status --short` 출력은 별도로 표시되지 않아 clean-tree 확인은 미완료. 해당 SHA의 GitHub PR-filtered Actions runs 0, commit statuses 0; **CI_UNVERIFIED**.
- 그 이후 documentation-only HEAD `4c28ee8778a4837a0b7f4452a0195af460acd038`는 **새 CPU PASS가 아님**. 서로 다른 SHA에서의 Wizard/P7/Manifest 결과를 하나의 최신 HEAD 전체 테스트 PASS로 합치지 마세요.

## P5–P8 운영 수용 게이트 (변경 없음)
- P5-D: 이전 SHA들에서 source CPU PASS. 실제 PLE RSS/PSS, inode/PID와 Docker NAT/kernel port owner는 **BLOCKED**, 비승격 procfs EACCES/UID 차이. 같은 권한으로 반복 실측하지 마세요. RC3은 증거 부족이지 서비스 장애 단정이 아님.
- P6-E: Fake Journal v2/Nonce fence CPU 37/37 PASS; **실제 operating Journal, durable replay prevention, operator approval identity는 BLOCKED**.
- P7: source-only model/service/upstream binding CPU PASS; **독립적으로 인증된 service/Proxy/Gateway/Storage 관측은 PENDING/NOT_ACCEPTED**. `SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED`를 live PASS로 승격 금지.
- P8: 실제 restart/rollback/restore 수용 **BLOCKED**. Production Release **BLOCKED**. GitHub CI 최신 exact-SHA **UNVERIFIED**; 신규 run이 없다는 사실만으로 원인을 단정하지 마세요.

## 다음 작업 우선순위
1. 최신 HEAD/PR/관련 소스 및 계약을 GitHub connector로 직접 재확인. `integration_reconcile`가 주장된 단일 Docker ID/served ID만 신뢰하고 있는 한계와 **독립 수집 출처의 인증 경계**를 분석. 소스 문서 구조 검증과 실제 provenance를 엄격히 분리.
2. 독립 Probe provenance를 설계할 때 **capture/collector identity, command provenance, time/nonce/session, model/service/container binding, evidence authenticity, replay/forgery**, origin/source isolation을 검사하되, 증명되지 않은 신뢰를 부여하지 말 것. Source-only fixture 속 필드만 추가해서 'authenticated' 또는 실제 실행 PASS라 주장하지 말 것. 기존 duplicate probe ID, strict numerics, time skew, 64hex upstream container binding을 재구현하지 말 것.
3. 재현 가능한 fail-open 결함이 있을 경우 최소 코드 수정 + 긍정/부정 CPU 사례. Wizard/Manifest/P7 기존 안전 계약의 회귀 영향도 확인. 실행 가능 환경이 없다면 `NOT_RUN` 표기하고 **실제 코드 미실행**을 숨기지 말 것; 실행 로그가 필요한 경우 한 번에 실행 가능한 CPU-only 명령 제공.
4. GitHub feature 브랜치에만 커밋, 새 HEAD/blob 재확인, exact-SHA Actions/check 상태 읽기 전용 조회. 없으면 `CI_UNVERIFIED` 유지. Evidence Ledger, Next Actions, Decisions, 이 문서, 관련 P7 계약을 영구 갱신하고 필요시 PR 설명을 정합화하되 PR Draft/Open/Unmerged 상태 유지.
5. **운영자 명시 승인 없는 작업 금지**: 모델 전환/다운로드/삭제, Docker/GPU/inference/benchmark, 실행 중 서비스/Portainer restart, 운영 Journal/Nonce 기록·수정·삭제, sudo/ptrace/procfs 권한 승격, firewall/NAT 변경, HF cache cleanup, CI dispatch/rerun/합성 trigger 시험, main 수정, PR merge. `ONE_ACTIVE_MODEL_ONLY`, API :8000, vLLM **0.32.0 고정**, SGLang 금지, OpenWebUI와 Ollama :11434 유지.

## 완료 보고 방식
마지막에는 **실제 수정한 코드/테스트/문서와 커밋**, **실제 실행된 테스트 SHA·건수·RC**, **CI Run ID 또는 UNVERIFIED**, **독립 운영 수용 미달 조건**, **다음 실행 작업**을 분리하고 URL 링크를 남기세요. 단순 분석/계획만으로 완료 처리하지 말고 승인된 source-only 개발을 진행하세요.


---

## 2026-11-21 KST — Manifest operator CPU 77/77 PASS (exact source SHA)
- DGX operator at `dcf73332e8ffc8d729b9cbf4b35d08c52643421b`: Python syntax `ast.parse` **2/2 OK**, Cleanup **12/12 OK / CLEANUP_CPU_RC=0 / 0.003s**, full Manifest **77/77 OK / MANIFEST_CPU_RC=0 / 0.141s**. Cleanup 12 are included in Manifest 77, not additive. GitHub compare confirmed the tested HEAD matched feature branch before this documentation update. `git status --short` output not separately shown; clean worktree not independently verified.
- Source path shadowing fix `84352446` and test backslash repair `9f891f85` now have operator-reported exact-SHA CPU results; previous `CPU_NOT_RUN` entries describe history and are superseded **at `dcf73332e8ffc8d729b9cbf4b35d08c52643421b` only**. Wizard 126/126 at `a4bd913`, P7 13/13 at `77fe76a8`, and P6-E 37/37 at `4c86b799` remain separate receipts.
- Read-only GitHub PR-filtered Actions runs 0, commit statuses 0 for tested SHA, CI_UNVERIFIED. The next documentation-only SHA receives no automatic CPU PASS. Next: inspect P7 independently captured provenance boundary and model/service binding architecture; keep all operating acceptance gates blocked and PR Draft/Open/Unmerged.

## 2026-11-21 KST — Manifest cleanup test syntax repair; CPU retry pending
- Previous operator at `6a0bf716ed1e0e89d096760632528ec3288b5617`: cleanup `Ran 1 test` import error `CLEANUP_CPU_RC=1`; manifest discovery `Ran 66 tests` import error `MANIFEST_CPU_RC=1`. Both caused by double backslash after `with patch.object(...)` at `tests/test_manifest_cleanup_cpu.py:195`, not evidence of a runtime/Docker fault.
- Fixed **only** the test file in GitHub commit `9f891f85eac8fd595c74a824b4f9efe20938ddd4`: single Python continuation backslash. CPU **NOT_RUN** after this repair; re-run targeted expected 12 and manifest expected 77 tests at latest actual HEAD. Document-only commits following this line are not CPU PASS.
- Preserve earlier Wizard 126/126 at `a4bd913`, P7 13/13 at `77fe76a8` as earlier-SHA results. CI remains unverified, no real cleanup, DGX Docker/GPU/Journal or release authorized.

## 2026-11-20 KST — Wizard PASS / Manifest two-error remediation (CPU pending)
- Operator at `a4bd913267f688129477415fd7d15c6842122acb`: **Wizard 126/126 OK RC0 (61.070s)**, **Manifest 76 tests, 2 ERROR RC1 (0.147s)**. Both completed-cleanup tests reached `make_plan()` and raised `UnboundLocalError`: local `status = active_status()` shadows module read-only `status()` in earlier completion branch. No claim of all-Wizard/Manifest PASS at this SHA.
- Feature source correction `84352446dfcdafd9002a16f05b67fc0300318aa1`, test `6a76c425a7b4916c8fcec9d0c98cfb124d361200`: rename only the local to `active_report`, preserve completion drift fail-closed semantics; add targeted no-Docker completed-manifest regression. Manifest CPU expected **77 methods**, **NOT_RUN for new SHA**. Next operator: run selected `test_manifest_cleanup_cpu.py`, then full `test_*manifest*cpu.py` with exact SHA + RC and clean status. Wizard 126/126 historical at `a4bd913` does not transfer to newer HEAD.
- P7 source-only 13/13 PASS at `77fe76a8` remains separate. All live operating gates and CI release remain blocked/unverified. This document update creates no CPU pass.

## 2026-11-20 KST — operator P7 13/13 CPU validation receipt
- Latest **tested** SHA: `77fe76a839d85930533536ec2db5af3c1f4c7293`. Operator transcript: `Ran 13 tests in 0.005s`, `OK`, `P7_CPU_RC=0`, with preceding `git pull` reporting `7 files changed, 84 insertions(+)`. GitHub direct comparison: branch HEAD **identical** at time of verification. Clean worktree not shown; keep **UNVERIFIED**.
- This supersedes earlier **CPU NOT_RUN** for the specific upstream-identity source change only **at tested SHA**. Previous 11/11 result at `73fe7c84` and P6-E 37/37 at `4c86b799` are separate prior receipts.
- Exact tested SHA: PR-filtered workflow runs 0, commit status entries 0; **CI_UNVERIFIED**, not CI PASS. Newly created documentation commits have later HEADs but inherit no CPU evidence. Next source-only priority: broad Wizard/Manifest CPU regression, then independently sourced P7 probe architecture review. P5-D actual PLE/NAT, P6-E operating Journal/Nonce, P7 independent live capture, P8 actual recovery and production remain unqualified. No live DGX/CI dispatch/main/merge changes.

## Follow-up 2026-11-20 KST — P7 upstream service identity binding implemented, CPU pending
- GitHub source commit `bbc32e710d500b7d8029594a682097561e5b588e`, tests commit `34aad3f6a3b855491c155ed50af059291f5890f1`. New required proxy/gateway `upstream_container_id` equals valid service `container_id`. Missing, malformed or mismatched IDs fail source-only closed. Existing served ID, :8000, 120s, registry and probe-id contracts remain.
- Updated P7 test fixtures and added two negative methods: **13 expected, NOT_RUN for this source**. Operator historical 11/11 RC0 at `73fe7c84...` is a separate earlier-SHA result. The docs-only commit of this section is not a CPU/CI PASS. No independent live Docker identity is authenticated by editable JSON.
- Next operator run: `git pull --ff-only; git rev-parse HEAD; git status --short; python3 -B -m unittest discover -s tests -p 'test_integration_contract_cpu.py' -v; printf 'P7_CPU_RC=%s\\n' "$?"`. Then broaden Wizard/Manifest regression; keep operational gates and CI actions restricted.

## Follow-up 2026-11-20 KST — P7 CPU receipt attached to exact source SHA
- Operator terminal: `73fe7c841762adbaf5135261d8dba96c27591060`; `Ran 11 tests in 0.004s / OK`; `P7_CPU_RC=0` for `tests/test_integration_contract_cpu.py`. GitHub comparison confirmed feature HEAD identical to that SHA **before this documentation commit**. Classification: **OPERATOR_REPORTED_P7_CPU_11_OF_11_PASS_RC0_AT_73FE7C / CLEAN_TREE_UNVERIFIED / CI_UNVERIFIED**.
- Earlier header saying `CPU NOT_RUN` records the **prior session's state**, now superseded **only for that exact tested SHA**. This documentation update carries no new test execution. P7 actual independent source authentication remains PENDING, P5-D live PLE/NAT and P6-E live Journal/Nonce and P8 restore remain BLOCKED; Production remains BLOCKED.
- Next focus: cross-component model/service identity binding; independent provenance authentication boundary; wider Wizard/manifest CPU regression. No unapproved DGX operations, CI dispatch, main write or PR merge.

## 2026-11-20 KST — P7 strict numeric types and future timestamps (SOURCE-ONLY, CPU NOT_RUN)
- Source commit `dcbe9e63f5103e75472c64fdfb801bdcfeef8831`; tests commit `5ec3a81a5cde065819812323c2283a993748f452`. `integration_contract.py` now requires exact JSON integer types for root `api_port`, service `port/http_status`, and proxy/gateway `upstream_port/http_status` (rejecting float, bool, string lookalikes); future component observations beyond UTC current time +120 seconds fail with `*_OBSERVATION_TIME_IN_FUTURE`. Existing 120-second inter-component window and time-zone-aware ISO parsing remain.
- Three methods added to `test_integration_contract_cpu.py`: negative numeric combinations (root/service/proxy/gateway), all-future zero-spread rejection, and historical UTC+09:00 positive regression. Expected module method count **11**. Existing normalized duplicate probe-ID handling reused.
- **Execution receipt: CPU NOT_RUN**, because complete repository checkout/runner was unavailable in this session; no assertion of 11/11 PASS, no overall suite PASS. GitHub read-only at test SHA `5ec3a81a...` found associated PR-filtered workflow runs **0** and commit statuses **0**; full check-run verification remains outstanding; **CI_UNVERIFIED**. This documentation commit creates no additional CPU/CI evidence.
- Next operator CPU-only check on clean checkout: `git rev-parse HEAD; git status --short; python3 -B -m unittest discover -s tests -p 'test_integration_contract_cpu.py' -v; printf 'P7_CPU_RC=%s\\n' "$?"`. Report exact source SHA, test count, RC, clean-tree state. Do not combine a later docs HEAD with prior source test evidence.
- P7 source `SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED` is never independent authenticated provenance. P5-D real PLE/NAT, P6-E operating Journal/nonce, P7 live probes, P8 recovery and production release remain **BLOCKED/NOT_ACCEPTED**; no DGX/CI dispatch/model/permissions/main/merge changes were authorized.

# Blazux DGX Spark — P7 재개용 정식 세션 인수인계 및 실행 프롬프트 (2026-11-20 KST)

> **새 세션의 가장 우선되는 참조 문서.** 기준 GitHub PR #1 HEAD: `f70a2a6b5652806e0867f8eb7d63b561f292f676` (작성 직전 직접 조회; 이 문서를 커밋하면 HEAD가 바뀜). 개발 branch `feature/recipe-wizard-handoff`, base `main`, **Draft / Open / Unmerged**. 먼저 최신 PR HEAD를 재조회하고 본 문서·관련 소스와 비교하라. 문서 커밋을 새 SHA의 CPU/CI PASS로 해석하지 않는다.

## 0. 이번 세션의 목표 (실행 우선)

**P7 Proxy/Gateway/Storage 독립 증거 계약의 source-only/Fake-DGX 개선**을 이어서 수행한다. 단순 분석이나 계획서로 끝내지 말 것. GitHub 도구로 실제 최신 파일을 조사하고, 이미 구현된 경로를 재사용하며, 명확한 결함을 찾을 경우 **좁은 코드 수정 → 부정 조건 CPU 테스트 추가 → 실행 가능한 범위의 실제 검증(실행 못 했다면 NOT_RUN 표기) → feature 브랜치 커밋 → SHA/PR/Actions 재조회 → 이 문서 및 영구 인수인계 갱신**까지 진행한다. **승인 없는 실운영 검증, 작업 재시작, CI 임의 트리거, PR 머지는 절대 하지 않는다.**

## 1. Repository 및 운영 환경

| 항목 | 값 |
|---|---|
| Development | https://github.com/kjlee-inlct/qwen3.8-Flash-DGX |
| Upstream | https://github.com/blazux/qwen3.8-Flash-DGX |
| Feature branch | `feature/recipe-wizard-handoff` |
| PR | https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1 — Draft/Open/Unmerged, base main |
| 문서 작업 전 HEAD | `f70a2a6b5652806e0867f8eb7d63b561f292f676` — **latest 여부는 다음 세션에서 재확인** |
| DGX operator workspace | `~/Workspace/llm/blazux-orcarouter` |
| Hardware/OS | NVIDIA DGX Spark GB10 / Ubuntu ARM64 |
| Runtime policy | vLLM **0.32.0 고정**, **SGLang 금지**, `ONE_ACTIVE_MODEL_ONLY`, OpenAI-compatible API 포트 **8000** |
| 기존 연동 | OpenWebUI 유지, Ollama :11434 유지, HF 캐시 보호 |
| 최근 기록상 개발 trial | `qwen38-orcarouter-qsa62318-lmhead-v3` / served API ID `qwen3.8-flash-next-orca-uncensored-bf16`; **현재 실시간 상태로 추정하지 말 것** |

Manifest registry에 등록된 모델을 범용 지원하되 임의 모델 전환 또는 컨테이너 승격은 금지한다. 과거 운영 trial 컨테이너와 canonical container는 같은 개념이 아니며, source `served_id` 문자열이 실제 API 응답을 인증하지 않는다.

## 2. 2026-11-20 최신 확정 CPU 증거와 서로 다른 SHA의 분리

| Evidence source SHA | 근거/검증 | 판정·한계 |
|---|---|---|
| `7c11d0d1a0921ef7b0f4134bd3d3c0d8ac4e5795` | 운영자 제공 P5-D/Manifest/Wizard 선택 CPU **138/138 PASS** | 당시 SHA 기준 선언/코드 PASS; 운영 PLE/NAT 미검증 |
| `fd338efa549a8c3bb54e65e5e033d2334d9e96e1` | P5-D 읽기 전용 프로세스 감사: `smaps` **3/3 EACCES(13)**, FD/root 및 namespace 귀속 불충분, `BLOCKED_PARTIAL_PROVENANCE / RC3` | 실운영 RSS/PSS·inode·NAT ownership **BLOCKED**. RC3는 서비스 장애가 아님 |
| `045947fccd33952ef4911c908ffb480d62b3d82b` | P5-D permission CPU **7/7 PASS**, 운영자 비승격 preflight `BLOCKED_PERMISSION_PREFLIGHT/RC3` | UID 1001 observer vs UID 0 process; 불필요한 재실행 금지 |
| `f0e48a5a43824468618aa494ad03cc06f09c10c7` | 운영자 P6-E CPU **14+20=34/34 OK** | 당시에만 유효, RC/clean status 기록 없음 |
| `25bf012a4a76d30508743d751d5693aaff33b943` | 운영자 P6-E CPU **15+20=35/35 OK**. Journal RC0, Nonce RC 미출력 | 당시에만 유효 |
| **`4c86b7990ea865a31bb78a346ca92867ed5e9e83`** | **운영자 제공 P6-E Journal 22/22 OK (0.018 s, RC0) + Fake Nonce 15/15 OK (0.075 s, RC0) = 합계 37/37 PASS**; GitHub 테스트 메서드 수 직접 대조 | **현재 가장 최근 검증된 P6-E source SHA**, `git status --short` 미제공, CI/실운영 인증 아님 |
| `f70a2a6b5652806e0867f8eb7d63b561f292f676` | GitHub 문서 전용 커밋; 위 37/37 CPU 증거를 영구 기록 | 새 소스 테스트를 실행한 SHA가 **아님** |

위 값은 서로 다른 시점/커밋의 근거이다. 합산해서 단일 HEAD의 전체 CPU PASS로 취급하지 않는다. 이후 **이번 인수인계 문서 커밋**도 문서-only 변경이며 신규 CPU 수용 근거가 아니다.

GitHub REST read-only 재조회에서 37/37 원본 SHA와 문서 작업 전 HEAD 각각의 Actions runs **0**, Check runs **0**, Commit status **0**. **GitHub CI = UNVERIFIED**, Actions 자동 트리거 미발생 원인 미확정. 과거 성공 run, `GITHUB_TOKEN`/GitHub App 가설 등으로 원인을 단정하지 않는다. CI dispatch/워크플로 수정/트리거 재시험은 별도 명시 승인 전까지 보류.

## 3. 이미 구현된 P6-E와 P7 코드 — 중복 구현 방지

### P6-E — CPU 검증 기록은 완료, 운영 수용은 미완료

- `scripts/manager/mock_nonce_fence_v2.py`: 0700로 제한된 임시 `blazux-p6e-fake-*` 디렉터리의 Fake nonce marker. `O_EXCL`, `O_NOFOLLOW`, 0600 소유/모드/링크 검증, JSON 타입 엄격 비교, duplicate keys 및 비정상 상수 거부, `fsync` 후 inode/path 검증, 동일 inode·동일 길이 byte 변조 readback 거부. 불확실한 marker 삭제/재사용 없음. **실제 운영 nonce 장부 아님**.
- `scripts/manager/generic_journal_v2.py`: V2 in-memory event/hash/phase audit, V1 migration preview, untrusted restart snapshot 리뷰. V1 전이 규칙을 V2에 재사용할 때 발생하는 **종결(COMMITTED/RESTORED/CANCELLED/RECOVERY_FAILED) 이후 동일 plan/nonce 재진입** 및 **FAILED → OBSERVED** 차단. **FAILED → ROLLBACK_STARTING**은 정상 경로로 유지. 영속 operating Journal/replay ledger, operator approval, live restart 모두 아직 BLOCKED.
- `tests/test_p5d_p6e_cpu.py`: **22** methods, `tests/test_mock_nonce_fence_v2_cpu.py`: **15** methods, 합 37은 `4c86b7990ea865a31bb78a346ca92867ed5e9e83`에서 실제 운영자가 **RC0**로 검증.
- 세부: `docs/P6-E-JOURNAL-V2-ATTEMPT-BOUNDARY-20261120.md`, `docs/P6-E-FAKE-NONCE-POST-FSYNC-CONTENT-READBACK-20261120.md`, `handoff/EVIDENCE-LEDGER.md`.

### P7 — 다음 우선순위

- `scripts/manager/integration_contract.py`: `integration_reconcile(model, evidence, config=None)`, `service/proxy/gateway/storage`의 source-only 구조적 일관성 검토. registered model의 canonical container, served ID, checkpoint/recipe, :8000, single-active-model, 시각 120초 범위 등을 검사.
- 동일한 `probe_id`를 두 component가 공유하거나 공백만 달리 재사용하는 경우 양측 `NOT_OBSERVED` 및 `*_PROBE_ID_REUSED_ACROSS_COMPONENTS`으로 차단하는 구현은 **이미 있음**. 이를 다시 만들지 말 것. 고유 `probe_id`와 `probe_mode='DIRECT_OBSERVATION'`도 사용자가 쓴 JSON 문자열에 불과해 독립 검증을 인증하지 않는다.
- `tests/test_integration_contract_cpu.py`: 현재 GitHub 소스에서 **8 unittest methods**. 기존 P7 patch 당시 **독립 fixture 8/8 PASS + stubbed registry 7/7 PASS**, **실제 전체 Wizard CLI/full source suite/Actions CI는 미확인**. 37/37 P6-E 검증은 이 P7 module을 포함하지 않는다.
- `wizard.main`의 `operations generic integration-reconcile --model <name> --component-evidence <file> --json` 명령은 source 문서 평가에 한정한다. source `SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED`는 **운영 PASS가 아님**, 실제 gateway/API/storage 인증 아님.
- 참조: `docs/P7-PROBE-ID-INDEPENDENCE-CONTRACT-20261120.md`, `docs/WIZARD-CLI-CONTRACT.md`, `docs/P1-P8-EXECUTION-ROADMAP-20261119.md`.
- **후속 코드 리뷰 후보**: status/port를 비교할 때 Python 숫자 `8000 == 8000.0` 등 유형 차이가 source-only 일관성을 부당하게 통과시키는지 확인; ISO timestamp가 시간대-aware만 요구하고 미래 날짜/증거 생성 시각의 fresh upper-bound를 검증하지 않는지 검토; root/component 모델 및 시계 skew, 추출된 경로의 진위, `http_status` 유형, 공통 identity binding, 중복 capture ID 처리를 검증. **실제 새 결함인지 재현부터 확인하고 기존 단위 테스트와 구현 중복은 피할 것.** 어느 경우든 origin spoofing을 source 필드 몇 개만으로 인증할 수 없다.

## 4. P5–P8 및 릴리스 게이트

| Stage | 현 시점 판정 |
|---|---|
| P5-D Manifest/Wizard source CPU | 과거 SHA에서 PASS; 새 HEAD의 전체 테스트는 별도 검증 |
| **P5-D 실제 PLE RSS/PSS·inode·PID 및 Docker NAT 커널 소유권** | **BLOCKED** — non-privileged `/proc/PID/smaps`, `fd`, `root` 접근 불가, UID mismatch. 반복 조사 금지 |
| P5 실부하 Benchmark/session | 전면 운영 수용 아님; 별도 명시 승인 필요 |
| **P6-E Fake-Journal/Nonce CPU** | **37/37 OK, RC0 at `4c86b7990ea8`** |
| **P6-E 실제 operating Journal v2·Nonce/Replay/승인 인증** | **BLOCKED** — CPU fixture/hash consistency는 운영 권한 아님 |
| **P7 Proxy/Gateway/Storage 실독립 관측·증빙** | **PENDING/NOT ACCEPTED** — source-only 계약 보강 가능 |
| **P8 실제 장애·재시작·원상복구** | **BLOCKED**; Fake-DGX 통과는 실제 복구 인증이 아님 |
| GitHub Actions 최신 exact-SHA CI | **UNVERIFIED** |
| PR #1 merge / Production Release | **BLOCKED** — PR Draft/Open/Unmerged 유지 |

`0` 관측 RSS/PSS와 `UNREADABLE`/permission-denied는 다르다. `RC3`는 증거 부족이지 서비스 장애 판정이 아니다. Docker port declaration 일치만으로 kernel NAT·프로세스 포트 귀속을 증명하지 않는다.

## 5. 절대 변경하지 않을 운영 범위

- **명시적 새 운영자 승인 없이 금지**: 실제 모델 전환/다운로드/삭제, Docker/GPU/inference/벤치마크, 서비스 재시작, Portainer 변경, 운영 Journal/nonce ledger 읽기·쓰기, P8 실복구, sudo, ptrace, sysctl, firewall/NAT, procfs 권한 승격, HF 캐시 cleanup, :8000/OpenWebUI/Ollama 영향 작업.
- **명시 승인 전 GitHub CI 수동 dispatch/rerun, Actions settings/workflow permissions 변경 또는 합성 trigger 비교 시험 금지.**
- `main` 쓰기와 PR #1 merge 금지; feature 브랜치에만 필요 최소 변경을 커밋. 강제 push 금지, 선행 HEAD 검사 후 `expected_sha`로 fast-forward 업데이트.
- GitHub 코드 수정과 DGX 실운영은 별개 승인 범주이다. 터미널에 제시하는 CPU-only 명령은 실제 Docker/모델 파일/Journal을 건드리지 않는 것으로 검증할 것.
- 모델 일반화 지향; hardcoded `27b`/`flash-next` 전제 회피. 한 시점에 활성 LLM은 하나; vLLM 0.32.0, SGLang 금지.

## 6. 새 세션 즉시 수행 순서

1. GitHub connector로 PR #1 **최신 HEAD**와 base/main, Draft/Open/Unmerged 상태 확인. 역사적 `f70a2a6b5652806e0867f8eb7d63b561f292f676`을 현재 HEAD라고 단정하지 말 것.
2. 우선 `handoff/SESSION-HANDOFF-P7-20261120.md`와 `handoff/EVIDENCE-LEDGER.md`, `handoff/NEXT-ACTIONS.md`, `handoff/DECISIONS.md`, 로드맵 및 P7 코드·테스트를 최신 HEAD에서 읽는다. 기존 메서드/테스트·Wizard·Manifest 구현을 열람하고 patch 중복을 방지.
3. P7 source-only fail-closed 누락을 **재현 가능한 단 하나 이상의 구체적 사례**로 먼저 확인. 확인된 결함만 최소 수정, 정상 플로우·등록된 3개 모델/미래 모델·120초 창·포트 8000 보호. 유저 작성 `PASS`와 사실상 독립 관측의 차이는 보존.
4. CPU/Fake-DGX **부정 조건 테스트**와 정상 회귀 추가. 실행 환경이 있으면 Git 원본과 일치하는 코드로 실제 실행하고 결과 SHA/건수/RC 기록. 도구에 runner가 없으면 명시적으로 **NOT_RUN**; 격리 mirroring/stub은 실제 전체 저장소 PASS로 서술 금지. 필요 시 CPU-only operator 실행 명령 1회 제시하고 로그를 받고 계속.
5. Source patch → GitHub commit (feature branch) → PR HEAD/변경파일 blob 재조회 → **해당 SHA** GitHub Actions Run ID, Check Run 조회. 0개면 `CI_UNVERIFIED` 그대로. prior CPU PASS를 신규 SHA에 이관하지 말 것.
6. `handoff/EVIDENCE-LEDGER.md`, `handoff/NEXT-ACTIONS.md`, `handoff/DECISIONS.md`, 이 세션 인수인계와 적절한 `docs/P7-...` 문서에 SHA·확정 결과·미수용 게이트·다음 행동을 영구 기록. 필요 시 PR 설명은 맞춤 갱신하되 PR 자체는 Draft/Open/Unmerged 유지.
7. 작업 결과를 사용자에게 **무엇을 실제 구현·커밋·검증했는지** / **미검증 무엇인지** / **운영 승인 경계**로 분리 보고. 막힌 것은 실제 원인, 재현에 필요한 최소 권한/테스트만 제시.

## 7. 필독 영구 참조 (모두 최신 feature ref로 다시 조회)

- `handoff/SESSION-HANDOFF-P7-20261120.md` (이 문서; 가장 우선되는 세션 진입점)
- `handoff/SESSION-START-PROMPT.md`, `handoff/EVIDENCE-LEDGER.md`, `handoff/NEXT-ACTIONS.md`, `handoff/DECISIONS.md`
- `handoff/SESSION-HANDOFF-P5D-20261120.md` (P5-D procfs/permissions 역사적 세부)
- `docs/P1-P8-EXECUTION-ROADMAP-20261119.md`
- `docs/P7-PROBE-ID-INDEPENDENCE-CONTRACT-20261120.md`, `docs/WIZARD-CLI-CONTRACT.md`
- `docs/P6-E-JOURNAL-V2-ATTEMPT-BOUNDARY-20261120.md`
- `docs/GITHUB-ACTIONS-OPERATOR-PUSH-COMPARISON-20261120.md`
- `docs/P5-D-PROCFS-PERMISSION-BLOCKER-20261120.md`
- Source: `scripts/manager/integration_contract.py`, `tests/test_integration_contract_cpu.py`, `scripts/manager/generic_journal_v2.py`, `scripts/manager/mock_nonce_fence_v2.py`, `wizard/main.py`, `runtimes/manifest-registry.json`.

## 8. 새 대화 붙여넣기용 작업 지시문

```text
이전 Blazux DGX Spark / vLLM 0.32.0 / P5–P8 개발을 그대로 이어주세요.

GitHub: https://github.com/kjlee-inlct/qwen3.8-Flash-DGX
Branch: feature/recipe-wizard-handoff
PR #1: Draft/Open/Unmerged, base main
가장 최신 기준 문서: handoff/SESSION-HANDOFF-P7-20261120.md
이전 문서 작업 시작 HEAD: f70a2a6b5652806e0867f8eb7d63b561f292f676 (현재 HEAD라고 가정하지 말고 GitHub에서 다시 확인할 것)

우선 GitHub 연결 도구로 최신 PR HEAD, 위 인수인계 문서, Evidence Ledger, Next Actions, Decisions, 로드맵, scripts/manager/integration_contract.py 및 tests/test_integration_contract_cpu.py의 최신 파일을 실제 확인하세요.

확정된 CPU 증거: 운영자 제공 소스 SHA 4c86b7990ea865a31bb78a346ca92867ed5e9e83에서 P6-E Journal 22/22 OK/RC0 + Fake Nonce 15/15 OK/RC0 = 37/37 PASS. 이후 문서 커밋은 새 CPU 통과가 아닙니다. 최신 CI는 해당 SHA에서 runs/checks/statuses 0/0/0, UNVERIFIED입니다.
실제 P5-D PLE RSS/PSS/inode/PID·kernel NAT 소유권은 /proc EACCES/권한 경계 때문에 BLOCKED. P6-E 실운영 Journal/nonce/replay/approval과 P7 실독립 Proxy/Gateway/Storage, P8 실제 복구, Production Release도 미수용입니다.

이번 진행 목표는 P7 source-only/Fake-DGX 계약 보강입니다. 이미 구현된 duplicate probe_id/whitespace 검증을 중복 구현하지 마세요. 먼저 최신 코드/테스트로 결함을 입증한 뒤 필요한 최소 소스 수정, 부정 조건 CPU 회귀, 실제 가능한 테스트 실행, feature 브랜치 GitHub 커밋, 새 SHA의 CI 확인, 영구 문서 갱신까지 수행하세요. 테스트를 실제 실행하지 않았다면 NOT_RUN이라고 쓰고, 이전 SHA의 PASS를 새 SHA에 승격하지 마세요.

새로운 명시 승인 없이 sudo/ptrace, Docker/GPU/모델 전환·실부하, 서비스 restart, 운영 Journal 기록/삭제, procfs 권한 승격, CI manual dispatch/trigger 실험, main 수정 또는 PR 머지는 금지합니다. vLLM 0.32.0/SGLang 금지, ONE_ACTIVE_MODEL_ONLY, API :8000 및 기존 OpenWebUI/Ollama를 유지하세요. P5-D EACCES를 반복 확인하지 마세요.

단순 계획서로 끝내지 말고 실제 GitHub 구현 가능한 범위를 한 세션에서 수행한 다음 테스트/CI/운영 수용 여부와 정확한 SHA를 구분해 보고하세요.
```

> **마지막 주의:** 이 문서는 작성 당시 증거와 안전 경계를 정리한 **문서 전용 인수인계**이다. PR HEAD, 운영 환경, 최신 CI, 모델 service 여부는 새 세션에서 반드시 독립 재검증한다.
