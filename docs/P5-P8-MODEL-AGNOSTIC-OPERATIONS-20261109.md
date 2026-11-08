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
