## P6-B / P6-C — distinct fake container IDs and temp-file Journal acceptance (2026-11-09)

All claims below are **CPU/Fake-DGX source contracts only**; no DGX, Docker, GPU, inference, live port release, real switch, production-approved journal, or operator approval.

- `transition_safety.InMemoryBackend` binds two different synthetic SHA-256 container IDs; `mock_transaction_pipeline` exports each model's ID and the currently active/host-port-owner container ID per phase. Audit enforces exact phase-owner-ID correspondence, hash, sequence, single model and :8000. The legacy `docker_id` key retains its SOURCE-only meaning for existing consumers, not current active container identity.
- `mock_persistent_contract.py` tests OS-level O_EXCL, 0600 file permissions, log fsync, atomic snapshot rename+fsync, orphaned log, forged snapshot, unresolved phase, duplicate write, fake TTL expiry, ticket identity drift and replay. **Only auto-deleted private temporary directories** are created. This is an exercise of the write/read contract, *not* authorization or verified production durability; existing `service_journal.py` and `operational_audit.py` still apply to their historical, separately qualified operating domain and are not modified.
- New commands: `./wizard.sh operations generic fake-disk-contract --from-model orcarouter --to-model 27b --json`; `./wizard.sh operations generic fake-disk-contract --from-model 27b --to-model flash-next --mock-disk-scenario interrupted-snapshot --json`; `./wizard.sh operations generic fake-disk-matrix --summary-only --json`. Three models = 6 directed pairs × 8 scenarios = 48. Existing P5 21, P8 extended 66, legacy 24 cases remain separate.
- Acceptance: SOURCE IMPLEMENTED / 4369bb1 Push+PR CI SUCCESS (new P6-B/C 11 tests PASS, fake disk 48 PASS); docs-only changes are not live acceptance; REAL DGX runtime/provenance/loaded benchmark, real approval, durable operating rollback, P7 independent proxy/gateway and P8 live fault/release **NOT RUN**. Do not remove or rename the operating Orcarouter v3 container or change governor/cgroup/port 8000.

---

## P5-B / P6-A MOCK coordination and journal extension — 2026-11-09

**Source and CPU/Fake-DGX only; no live DGX mutation or promotion.** New `mock_benchmark_session.py` implements model-independent P5 synthetic timeline coordination (pre-sample → mock benchmark → post-sample) and feeds the existing `benchmark_session.session_review`. Mock metrics, API observation flags, timestamps and Docker IDs are synthetic test fixtures, not current performance values. New `mock_transaction_pipeline.py` connects the exact in-memory P6 executor trace to indexed hash-linked in-memory events with a fail-closed journal audit; the hash chain does not establish origin, fsync durability, true approval, live status, or the ability to restart a model. Existing persistent `service_journal.py` remains untouched and does not yet implement Orcarouter live transaction support.

Commands (all source-only):
```bash
./wizard.sh operations generic session-mock --model orcarouter --json
./wizard.sh operations generic session-mock --model 27b --mock-fault oom --json
./wizard.sh operations generic session-matrix --summary-only --json
./wizard.sh operations generic pipeline-mock --from-model orcarouter --to-model 27b --json
./wizard.sh operations generic pipeline-mock --from-model 27b --to-model flash-next --extended-fault target-api --json
```

P5 fixture has 7 faults including normal, missing sample, container/API drift, clock drift, request error, OOM. The extended P8 baseline continues separately with 11 faults × 6 pairs = 66 Fake-DGX cases. All tests must remain explicit in GitHub Actions. Operational P5 Session Plan still correctly BLOCKS unapproved real workload; actual live benchmark/resource capture, persistent journal, real P6 executor, Proxy/Gateway, live P8 recovery and final release remain unverified.

---

## 2026-11-09 10:15 KST source-contract supersession (operator DGX idle-only)

Operator's newest read-only Orcarouter v3 receipt: `/home/inlc/.local/state/blazux-wizard/resource-diagnostics/20261109T011520343025Z.json`, **5 samples / 44.27 s**; min MemAvailable ~30.16 GiB, last ~30.18 GiB, host MemTotal ~121.63 GiB; cgroup memory.current ~25.25 GiB, peak ~37.02 GiB; host swap used ~1.31 GiB, cgroup swap 0; memory PSI avg10=0%, OOM/OOMKill/major fault/file refault interval delta 0, swap in/out 0; CPU busy 0.19%, GPU 0% and 33°C, system peak 33.8°C, Docker identity unchanged. **Idle-only**: not loaded inference, PLE RSS, TTFT/TPS, or safe startup threshold verification. Keep OBSERVE_ONLY and startup_gate_enabled=false.

New common **source-only** implementation:
- **P5**: `scripts/manager/benchmark_session.py` and read-only resource snapshot monotonic clock. `./wizard.sh operations generic session-plan --model 27b --json` is BLOCKED and creates no workload. `session-review --model 27b --session-resource-evidence /absolute/resource.json --session-benchmark-evidence /absolute/benchmark.json --json` checks session ID, profile hash, registry checkpoint/served ID/Docker ID, UTC and monotonic bracket, API identity flags, request/error arithmetic, TTFT/TPS, OOM. Matching data only produce `SOURCE_SESSION_CORRELATED_NOT_LIVE_ACCEPTANCE`, **never real benchmark PASS**. Existing idle `resources observe` does not yet capture an approved workload or a unified bound session.
- **P6/P8**: `scripts/manager/transition_safety.py` accepts only an exact in-memory backend; `operations generic transaction-simulate --from-model 27b --to-model flash-next --extended-fault port-release --json` and `operations generic extended-fault-matrix --summary-only --json`. Eleven fault types × six directed pairs = **66 synthetic cases** with the current three-model registry; includes port-release, source-stop, container drift, journal write failure, approval expiry, state drift, replay, target start/API and restore failures. Original common 24-case matrix retained without changing output. No live executor, fresh approval engine, persistent journal or real recovery was implemented or released by this change.
- **P7**: `scripts/manager/integration_contract.py`, `operations generic integration-reconcile --model 27b --component-evidence /absolute/components.json --json`. Compares model-bound service/API/container, Proxy/Gateway upstream and storage observations with time/identity invariants. A user-authored `status: PASS` is not trusted; even internally consistent supplied JSON is `SOURCE_COMPONENT_FIELDS_CONSISTENT_NOT_LIVE_VERIFIED`, never actual Proxy/Gateway PASS. TTY common model submenu now shows P5 session planning, extended P8 matrix, strict P7 reconciliation.

Acceptance remains separated: SOURCE IMPLEMENTED / CPU+Fake-DGX CI vs REAL DGX OBSERVED idle / real BENCHMARK VERIFIED / real SWITCH VERIFIED / real RECOVERY VERIFIED / PRODUCTION RELEASED. The latter four remain **NOT RUN / NOT RELEASED**. Preserve Orcarouter v3 DEVELOPMENT_TRIAL, OpenWebUI/Portainer, all models/images/HF/PLE files, vLLM 0.32.0, no SGLang, ONE_ACTIVE_MODEL_ONLY, port 8000, and Draft/Open/Unmerged PR #1. Actual DGX workload, model switch, CPU/cgroup policy or fault injection requires a separate explicit operator approval. Historical source and DGX evidence remain below.

---

# P5–P8 범용 Wizard 운영 기능 (2026-11-09)

**공통 기능은 모델 독립, 런타임 어댑터는 모델별.** P5 리소스 보호·벤치 증거, P6 모델 전환, P7 서비스/프록시/게이트웨이/스토리지 통합과 Wizard UX, P8 장애 원복 및 최종 운영 수용은 하나의 checkpoint와 무관하게 모든 매니페스트 등록 모델에 적용한다. Quantization·PLE·MTP·Tools·Vision·vLLM loader 등은 모델별 adapter/recipe의 책임이다.

## 불변식

- DGX Spark GB10, Blazux vLLM **0.32.0**, **SGLang 금지**.
- **ONE_ACTIVE_MODEL_ONLY**, host **:8000/v1**, source stop → port release → target start → API served ID 검증.
- Git service-policy는 원하는 구성, 실제 Docker/API/GPU 상태는 별도 실측 증거로 확인.
- Generic 소스 검증, Fake-DGX PASS 및 문서 PASS는 실제 전환이나 실기 자동복구 승인에 사용 금지.
- 실기 서비스 중단/변경, 이미지·모델·HF 캐시 삭제, CPU clock·governor/cgroup 제한, P8 fault injection 및 PR merge는 별도 정확한 승인 필수.

## 구현 현황

| Phase | 공통 구현 (model-agnostic) | 별도 실기 수용 또는 모델별 어댑터 |
|---|---|---|
| P5 | 모든 등록 모델을 `--model`로 선택하여 read-only resource snapshot/observe/preflight 수행; container-ID 연속성, OOM/PSI/Swap/NVMe interval, 모델 바인딩 TTFT/TPS 근거 검증 | 동시 추론 부하 벤치마크의 자동 계측, PLE residency, 메모리·CPU 운영 임계값 검증 |
| P6 | 모델 레지스트리 자동 발견, 모든 서로 다른 source/target pair 사전검사, stop-before-start·포트·단일 모델 Fake-DGX 불변식 | 검증/승인된 실제 모델 전환 executor와 DGX 양방향 확인 |
| P7 | 공통 CLI/TTY 메뉴와 service/proxy/gateway/storage 네 요소의 모델 바인딩 증거 스키마 | 실제 프록시·게이트웨이 상태 측정과 운영 수용 |
| P8 | 각 pair의 정상·target-start 오류·API ID mismatch·restore-source 실패를 모두 인메모리 시험 | 실제 장애 주입, 자동 원복, 최종 release signoff |

## 소스

- 공통 엔진: `scripts/manager/generic_operations.py`
- CPU 검증: `tests/test_generic_operations_cpu.py`, `tests/test_generic_console_cpu.py`
- 모델 선택 리소스 관측: `scripts/manager/resource_diagnostics.py`
- 기존 P6/P8 two-model alias: `scripts/manager/p6_p8_fakedgx.py`
- 공통 라우트/UX: `wizard/main.py`, `wizard/console.py`

## 사용법 (모두 read-only / in-memory)

`./wizard.sh operations generic catalog --json`

`./wizard.sh operations generic preflight --from-model 27b --to-model orcarouter --json`

`./wizard.sh operations generic simulate --from-model flash-next --to-model 27b --fault target-api --json`

`./wizard.sh operations generic fault-matrix --json`

`./wizard.sh operations resources observe --model 27b --samples 3 --interval 5 --json --save`

`./wizard.sh operations generic resource-review --model 27b --resource-evidence /absolute/resource.json --benchmark-evidence /absolute/benchmark.json --json`

`./wizard.sh operations generic integration --model 27b --component-evidence /absolute/components.json --json`

Resource-review는 증거의 `model`/`snapshots`/`interval_summary`와 benchmark의 `model`/`ttft_seconds`/`tokens_per_second`를 비교한다. P7 component JSON은 `service`, `proxy`, `gateway`, `storage`가 각자 `status:"PASS"`, 동일한 `model`, 비어 있지 않은 `evidence_id`를 요구한다. 파일은 1 MiB 이하의 absolute non-symlink JSON object로 한정된다. **구조적 완전성만으로 실기 통합 성능이나 파일 출처를 인증하지 않는다.**

현재 등록 모델: Flash-Next/27B/Orcarouter의 **6개 방향 × 4개 fault = 24 case**. 테스트로 네 번째 모델을 추가하면 **12방향 × 4 = 48 case**가 자동 생성된다. `restore-source`의 `FAIL_FAKE_RECOVERY`는 기대된 실패 상태로, 매트릭스 통과가 실제 복구 성공을 뜻하지 않는다. 기존 Orcarouter↔27B alias는 호환성을 위해 **8 case**를 유지한다. Canonical 등록이 안 된 모델은 P6 preflight가 무조건 막힌다.

## 최신 DGX 운영자 증거 (2026-11-09 07:18 KST)

첨부 로그의 v3 trial 컨테이너와 API :8000/served ID 정상 유지, 44.266초 동안 5번 측정에서 동일 Docker ID, 최소 MemAvailable 약 **30.16 GiB**, host SwapUsed 약 1.31 GiB, 컨테이너 Swap 0, memory PSI avg10 0, OOM/OOM kill·major fault/file refault 구간 증가 0, host CPU busy 0.2%. 이는 **유휴 리소스** 관측이고 새 MTP2/Tools/Vision 또는 loaded PLE 성능 수용이 아니다. P6 `BLOCKED` 및 P8 레거시 8 case `PASS_FAKE_DGX_EXPECTED_OUTCOMES`가 설계대로 확인되었다. 코드 수정은 해당 live v3·Docker/CPU 제한을 변경하지 않는다.

## 미완료

실기 benchmark 동시 계측·장기 압박 테스트, PLE 실거주량, 별도 승인형 범용 실기 executor, 프록시/게이트웨이 실측 프로브, 실제 P8 fault/restore 및 최종 운영 수용. PR #1은 Draft/Open/Unmerged로 유지한다. 실제 모델 고유 Loader/PLE 어댑터는 계속 별도 검증한다.

## 2026-11-09 09:23 KST 운영자 제공 신규 DGX 증거

Git HEAD `e8d6c2a505e5023c1cbfaaba0ef723238125aa5e` fast-forward 완료. 3개 모델 카탈로그 PASS, 6방향×4종 Fake-DGX 총 24건 `PASS_FAKE_DGX_EXPECTED_OUTCOMES` (정상 6, 복구 12, 의도된 복구 실패 6), Orcarouter→27B preflight `BLOCKED` (7개 검증·승격 게이트 미완료). 실제 전환·장애 주입·복구 없음.

P5 Orcarouter 5회/44.268초 read-only interval: 동일 Docker ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, API :8000에 살아있는 v3의 메모리 cgroup 25.25 GiB, 전체 121.63 GiB, 최소 MemAvailable 30.13 GiB, cgroup Swap 0, host Swap 1.31 GiB, PSI memory 0, OOM/kill/major fault/refault 구간 증가 0, 호스트 swap in/out 0, CPU busy 0.2%. GPU 34°C, 시스템 최고 35.7°C; GPU utilization 0%, read-only idle measurement. `ple_specific_residency_status=NOT_OBSERVED`, `process_smaps_rollup_status=NOT_OBSERVED`, 운영 임계값 `UNCALIBRATED`. 증거 파일: `~/.local/state/blazux-wizard/resource-diagnostics/20261109T002330768366Z.json` (DGX 내부, GitHub에 업로드하지 않음).

대용량 상세 출력이 있는 공통 도구에 명시적 `--summary-only` 추가: `./wizard.sh operations generic fault-matrix --summary-only --json`, `./wizard.sh operations resources observe --model orcarouter --samples 5 --interval 10 --summary-only --save --json`. 전자는 모든 시나리오를 평가한 후 집계만 출력하고, 후자는 모든 snapshot을 원본 그대로 private evidence JSON에 보존한 후 stdout만 축약한다. **요약은 증거 원본 또는 실제 실기 운영 수용의 대체물이 아님.**
