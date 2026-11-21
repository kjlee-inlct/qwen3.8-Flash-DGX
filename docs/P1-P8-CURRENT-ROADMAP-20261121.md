# Blazux DGX Spark — P1–P8 current execution roadmap
**기준일:** 2026-11-21 KST · **기준 GitHub HEAD:** `629eedede29987b346313d855aa9cbb14226873b` (문서 생성 이전)  
**대상:** `kjlee-inlct/qwen3.8-Flash-DGX`, `feature/recipe-wizard-handoff`, PR #1 **Draft/Open/Unmerged**, base `main`  
**성격:** 실행 우선순위와 수용 게이트의 최신 진입점. 아래 SHA는 *테스트 실행 대상 SHA*이며 향후 문서 전용 커밋 SHA와 구분한다. GitHub 최신 HEAD·운영 상태·CI는 매 세션 재확인한다.

> **한 문장 결론:** 현재 범위의 source-only CPU 회귀는 확인했지만 **P5-D 실제 PLE/NAT, P6-E 운영 Journal/Replay, P7 독립 출처 인증, P8 실제 복구, Production은 수용되지 않았다.** 다음 개발은 P7 출처/증거 신뢰 기반과 P6-E 영속 Replay 계약을 CPU/Fake-DGX에서 먼저 구축한다. 운영시험 및 CI 트리거는 별도 승인 게이트다.

## 1. 정확한 검증 기준선 — 새 HEAD의 CI로 오인하지 않기

| 대상 | 운영자 제공 확인 결과 | 정확한 테스트 SHA | 증거 한계 |
| --- | --- | --- | --- |
| Wizard 선택 CPU | **126/126 OK, RC0**, 60.398 s | `8e4eb923f8d1bd45ab63c08dabb7b5dd5c5a724c` | CPU-only, 실제 DGX 운영 수용 아님 |
| Manifest 선택 CPU | **77/77 OK, RC0**, 0.160 s | `8e4eb923f8d1bd45ab63c08dabb7b5dd5c5a724c` | 같은 SHA, Cleanup 12는 기존 77에 포함 |
| P7 capture-session/upstream CPU | **16/16 OK, RC0**, 0.006 s | `c36b2bf9124b1237606d2d1d138929bfd138485c` | 주장된 JSON 구조 일치만 검증 |
| P6-E Journal/Fake Nonce CPU | **22/22 + 15/15 = 37/37, 각각 RC0** | `4c86b7990ea865a31bb78a346ca92867ed5e9e83` | Fake/CPU 계약, 실제 영속 운용 아님 |
| P5-D 선택 CPU 및 권한 진단 | 과거 선택 CPU PASS; 비승격 procfs **EACCES** | 과거 SHA별 Evidence Ledger 참조 | PLE RSS/PSS·inode↔PID·NAT 소유권 미수용 |
| P5 실측 | 과거 MTP0 visible TTFC 1K/4K/7K 3/3 **측정 완료**, reasoning-only 1K/4K 별도 | 원본 receipt 및 [P5 acceptance](P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md) 참조 | 선택 부하의 측정이지 loaded/production 품질 아님 |

**주의:** Wizard 126 + Manifest 77 = **서로 다른 선택 패턴의 CPU 203개**가 **동일 SHA**에서 PASS한 것이다. P7 16개와 P6-E 37개를 이 SHA의 전체 회귀 숫자에 합치거나 소급 승격하지 않는다. `c36b2bf`→`8e4eb923` 구간에는 문서 전용 커밋만 있었지만 **P7은 이전 테스트 SHA에 귀속**한다.

**GitHub CI:** `8e4eb923` 및 마지막 문서 HEAD `629eeded` 확인 시 PR-associated workflow runs 0, Check Runs 0, Commit Statuses 0. **CI_UNVERIFIED**, 원인 미확정. 이후 문서 커밋은 CI 성공을 뜻하지 않는다. 정상 커밋/푸시 이벤트와의 차이를 조사하는 실험, 수동 dispatch, workflow/settings 변경, main 쓰기는 승인 전 금지.

## 2. 프로젝트 상태 — 개발 완료와 운영 수용을 분리

| 단계 | 확보한 범위 | 남은 수용 기준 | 현재 상태 |
| --- | --- | --- | --- |
| **P1–P4** | Flash-Next/27B 역사적 범위의 실증, 승인형 전환·스토리지 인벤토리·dry run | 새 모델/일반화된 재설치·삭제·실복구는 별도 승인 | **과거 범위 한정 수용** |
| **P5-C / P5 측정** | Orcarouter 개발용 runtime/API 및 선택 SSE TTFT/TPS/visible TTFC, 리소스 샘플 | 조건부 측정 완성도, MTP2/Tools/Vision, loaded profile, 실서비스 적격성 | **부분 실측/미승격** |
| **P5-D** | read-only 진단 코드·CPU 보강, 이전 Docker/API/PID 부분 상관 | PLE 파일별 실제 RSS/PSS·inode↔PID, 독립 GPU/port 8000 NAT 경로, 증거 권한 | **BLOCKED_PERMISSION/PROVENANCE** |
| **P6-E** | Fake Journal v2, Fake durable nonce/replay 및 실패 경로 CPU 37/37 | 인증된 발급/승인 주체, crash-consistent 실제 영속 Journal/Nonce, 운영자 승인 결합 | **SOURCE/FAKE PASS · LIVE BLOCKED** |
| **P7** | model/served/container/upstream/port/time/probe ID + capture-session/nonce 일치, CPU 16/16 | 위변조 불가능한 신뢰 출처와 서비스↔Proxy↔Gateway↔Storage 실제 독립 관측 | **STRUCTURAL CPU PASS · AUTH PENDING** |
| **P8** | Fake-DGX 24/66/48 등 구분된 fault/disk simulation 집합, 안전한 fail-closed 계약 | 승인형 실제 실패 주입·원상 복구·Journal/서비스 재검증·최종 운영 서명 | **REAL BLOCKED** |
| **Production** | 아직 승인 없음 | 모든 선행 게이트·정확한 SHA CI·운영 결정 | **BLOCKED** |

**P5-D 차단 이유:** 비승격 계정과 프로세스 UID/권한 불일치, `/proc/PID/smaps`/FD 읽기 EACCES 3/3, namespace·PLE↔PID·kernel NAT 소유권을 확증하지 못함. `RC3` = 증거 불충분 / 비승격 경계, **서비스 장애나 RSS=0이 아님**. 동일 권한으로 무의미한 재시도 금지.

## 3. 신규 실행 순서 — 증거 의존 관계 중심

```text
G0  정확한 SHA/CPU/CI 증거 규약 ────────────────────────────┐
  │                                                         │
  ├── G1  P7 trusted issuer / collector provenance (CPU/Fake)│
  │       ├─ G1a Session/Nonce 발급 주체 및 신뢰 키 계약       │
  │       ├─ G1b canonical signed evidence + detached verify │
  │       └─ G1c 실제 원천 인증과 서명된 JSON의 차이 분리      │
  │                       │                                 │
  ├── G2  P6-E durable replay / Journal v2 (CPU/Fake)        │
  │       ├─ 단회 nonce consume, crash/rollback/동시성        │
  │       └─ 원자성/재시작/손상/부분 기록 부정 테스트         │
  │                       │                                 │
  └───────────── G3  P7 end-to-end evidence composition ────┤
                          │                                 │
                    승인 필요 경계                           │
                    ├─ G4 P7 실제 read-only 출처/endpoint 실증│
                    ├─ G5 P5-D 특권/도구 선행조건 해결 후 실측│
                    └─ G6 P6-E 실제 ledger/operation 승인    │
                          └─────────┬───────────────────────┘
                                    │
                       G7 P8 승인형 fault/restore
                                    │
                       G8 최종 CI + Operator Go/No-Go
```

G0의 **CI 정상 동작 원인 규명**은 G1–G3 source-only 개발과 병행 가능한 독립 추적이다. 반면 **CI PASS는 최종 Merge/Release의 필수 조건**이다. G4/G5/G6는 단일 선형 순서가 아니라 각각 별도 승인/증거를 요구하는 병렬 수용 게이트다. P8로 넘기기 전 반드시 모두 충족한다.

### G0 — 증거/CI 기준선 (source/read-only)
- 실행: exact `git rev-parse HEAD`, `git status --short`, 선택한 패턴별 test count/RC를 원본 transcript와 영구 ledger에 기록한다. GitHub runs/checks/status를 **각 정확한 SHA**에서 조회한다.
- 병렬 이슈: 최신 커밋 Actions 미실행 원인을 **read-only로** 분리 조사한다. 현재 원인 불명; `GITHUB_TOKEN` suppression이나 default-branch workflow 부재를 검증 없이 원인으로 단정하지 않는다.
- **완료 조건:** 정확한 SHA에 연결된 독립 CI Run ID + 성공/실패 결과가 있어야 `CI_VERIFIED`. 운영자 CPU PASS만으로 충족되지 않음.

### G1 — P7 신뢰된 관측 출처 기반 (다음 source-only 우선순위)
- **구현 순서:** (a) 위협 모델과 trust boundary/키 수명주기·발급자·취소/만료 정책, (b) trusted issuer가 모델·서비스·유효기간·수집 목적에 묶인 Session/Nonce challenge 발급, (c) collector의 canonical payload 서명/검증, (d) 검증 결과에 인증 상태와 출처 신뢰 수준을 분리 표기.
- **반드시 포함할 필드:** schema/version, issuer/collector key ID, source tree SHA, session ID, nonce, issued/observed/expiry time, probe ID, model ID, canonical container ID, served ID, :8000 endpoint, upstream identity, storage checkpoint/recipe digest, payload digest 및 signature. 비밀 키·토큰·실사용 credential을 evidence로 수집/커밋하지 않는다.
- **신뢰 경계:** 서명 검증은 **키 소유 증명**이지 Docker/프로세스/커널 관측의 참임을 자동 증명하지 않는다. trusted collector의 배포·실행 출처와 외부에서 관찰되는 identity를 별도로 검증해야 한다. 기존 `integration_reconcile`의 **untrusted JSON 경로는 절대로 live verified로 승격하지 않는다**.
- **CPU/Fake-DGX 부정 시험:** payload 변조, 서명 위조, 잘못된 키, 교체된 collector/session, 여러 시점 JSON 콜라주, time skew, 잘못된 Docker/served/storage digest, legacy unsigned, 키 회전/폐기.
- **완료 조건:** 독립 verifier가 부정 케이스를 fail-closed로 분류하고, 어떤 fake evidence에서도 `real_dgx_verified/operations_enabled/production_released=true`를 설정하지 않음. **실제 출처 인증 수용은 G4**.

### G2 — P6-E 영속 Nonce/Journal v2 (G1과 공통 신뢰 설계)
- **구현:** G1 issuer/session authority와 충돌하지 않는 nonce 수명주기; consume-once + 다중 프로세스 배타성, atomic write/fsync + restart readback, tamper/부분 기록/rollback 검출, Journal v2 hash-chain/attempt boundary/approval identity 결합.
- **검증:** two-process contention, same nonce replay, process crash before/after commit, partial file, directory fsync failure, stale lock, restart, bad previous hash, same-plan terminal restart → **CPU/Fake-DGX fail-closed**.
- **완료 조건:** Fake/CPU 계약을 재현 가능하게 검증하고 운영 경로와 별도의 fixture만 사용. `real_operation_authorized=false` 유지. **운영 Journal migration, persistent approval storage, 실제 restart는 별도 G6 승인/실증 전 금지**.

### G3 — P7 end-to-end 증거 결합 (CPU/Fake-DGX)
- 서비스, Proxy, Gateway, Storage의 증거를 **같은 발급 세션/nonce, 신뢰 주체, 시간창, 실제 상관관계**에 묶되 각 구성 요소의 독립성을 검증한다. 기존 64-hex container ID equality, probe ID uniqueness, 120초 window, 정수 타입, `:8000`, ONE_ACTIVE_MODEL_ONLY를 재구현하지 않고 재사용한다.
- CLI/Wizard는 **STRUCTURALLY_CONSISTENT / AUTHENTICATED_RECEIPT / LIVE_INDEPENDENTLY_VERIFIED**를 구분한다. 다만 실제 실행이 없는 Fake-DGX에서 LIVE로 승격하는 로직은 만들지 않는다.
- **완료 조건:** source-only P7 부정 테스트 + Wizard/Manifest CPU 회귀 + 증거 스키마/운영 전제 문서 커밋. 새 코드 SHA에 새로운 실행 receipt 필요.

### G4–G6 — 실제 DGX 증거/승인 (각각 별도 gate)
- **G4 P7 live:** 승인된 범위의 read-only collectors로 서비스/Proxy/Gateway/Storage/OpenWebUI API와 실제 container/upstream continuity를 *독립적으로* 관측. 신뢰된 서명만 있고 실제 수집이 없는 경우 불합격.
- **G5 P5-D live:** `/proc` EACCES/UID·namespace 장벽의 권한/도구 선행조건을 먼저 설계·승인. 다음 실측은 bounded one-turn read-only 기준, PLE mapping RSS/PSS·inode↔PID와 실제 NAT/port owner를 각각 검증. 단순 `smaps` 불가 시 `NOT_OBSERVED`로 유지; 동일 권한 반복 금지. P5 기존 TTFC 측정은 별도 성공 기록으로 유지.
- **G6 P6-E live:** durable Journal/Nonce, 승인 발급자, replay/atomicity, 정확한 service ownership과 승인된 executor 경계 검증. Fake-DGX 성공만으로 운영 restart/rollback 권한 부여 금지.
- **완료 조건:** 독립 실행 주체/승인자, 범위·시간·대상 SHA·개인정보/비밀 비노출, 정확한 원본 receipt 및 RC를 남기고 각각 별도 수용 결정.

### G7 — P8 실제 장애 복구와 최종 수용
- 기존 P8-R0~R3 구분 보존: **R0** desired-state/drift/복구 계획 source-only → **R1** 별도 승인된 bounded reinstall/switch 준비 → **R2** API/Tools/Vision/benchmark/Journal 및 source 복귀 검증 → **R3** 별도로 승인된 실패 주입·자동 원복·장애 후 검증.
- 실패 주입은 보존된 원본 모델/캐시/서비스, 승인 다운타임, rollback 계획, actual restore observation을 전제로 한다. 24/66/48 synthetic 시나리오 수는 **서로 다른 행렬**이며 실제 복구 완료가 아님.
- **완료 조건:** 운영자 승인에 따른 실제 대상 모델의 start/fault/restore/API/Journal/port/GPU evidence와 Go/No-Go 서명. 미충족 시 `P8_BLOCKED`.

### G8 — Release/PR 최종 게이트
- `exact SHA CPU/Fake-DGX PASS` + `independent Actions CI PASS` + `P5-D evidence qualified` + `P6-E live Journal/replay accepted` + `P7 independently authenticated live probes accepted` + `P8 real recovery accepted` + `operator release approval` 전부 필요.
- 하나라도 빠지면 `PRODUCTION_BLOCKED`, PR #1은 Draft/Open/Unmerged로 유지. Merge를 CI 실행을 위한 임시 실험으로 사용하지 않는다.

## 4. 당장 수행할 수 있는 다음 개발 턴

1. **G1 설계:** 기존 `integration_contract.py`, Journal v2, Fake Nonce 코드와 스키마에 중복 없는 trust/issuer/verifier 경계를 정의하고 위협 모델을 테스트로 고정한다.
2. **G1 source-only 최소 구현:** 운영 credential을 쓰지 않는 단위 fixture로 서명 검증/오염 거부/키 오류 케이스 작성 후 Fake-DGX 실행. 운영 경로는 항상 non-authorizing.
3. **G2 저장 계약:** G1 nonce 발급과 P6-E 소비자/Journal 간 데이터 계약을 문서화하고 crash/replay negative tests 확대. 기존 37/37 테스트를 변경 없이 보존하거나 해당 새 SHA에서 재실행한다.
4. **G3 연결/회귀:** P7 16-case, Wizard 126-case, Manifest 77-case 등의 새 SHA 선택 회귀를 실제 실행하여 RC 및 Test SHA 기록. 원본 `docs/handoff`만 수정한 SHA는 새 CPU 실행이 아니다.
5. **G0 병행:** GitHub Actions 정확한 SHA CI 누락 원인을 read-only로 계속 조사. workflow dispatch/trigger 실험은 별도 승인 전 금지.

## 5. 변경 불가 안전 조건과 증거 출처

- DGX Spark GB10, **vLLM 0.32.0 유지**, **SGLang 금지**, **ONE_ACTIVE_MODEL_ONLY**, 기존 OpenAI-compatible `:8000/v1`, OpenWebUI·Ollama·Portainer 연결·모델 HF 캐시 보존.
- 새로운 승인 없는 `sudo/ptrace`·procfs 권한 승격, Docker stop/start/restart, GPU inference, benchmark 재실행, 실제 model switch, operating Journal 기록/삭제/마이그레이션, cache/PLE 삭제, CPU/전력 조절, CI manual dispatch/trigger, GitHub Actions 설정 변경, `main` 커밋/PR 머지 **금지**.
- **권위 있는 증거 원본:** [Evidence Ledger](../handoff/EVIDENCE-LEDGER.md), [Next Actions](../handoff/NEXT-ACTIONS.md), [P7 handoff](../handoff/SESSION-HANDOFF-P7-20261120.md), [역사적 상세 로드맵](P1-P8-EXECUTION-ROADMAP-20261119.md), [P5-D 진단](P5-D-ONE-TURN-PERMISSION-DIAGNOSIS-20261120.md), [P8 수용](P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md).
- **현시점 판정:** `SOURCE_CPU_SCOPED_PASS / CI_UNVERIFIED / P5D_LIVE_BLOCKED / P6E_LIVE_BLOCKED / P7_AUTH_PENDING / P8_REAL_BLOCKED / PRODUCTION_BLOCKED`. 새 운영 관측 없이 이를 자동 갱신하지 않는다.
