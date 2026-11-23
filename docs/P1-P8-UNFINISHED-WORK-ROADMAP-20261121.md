# P1–P8 미완료 작업 및 종료 게이트 — DGX Spark

**기준:** 2026-11-21 KST · 검토한 feature HEAD `3be4080008eb74511d27ee3153da0d80cc09971c` · 대상 PR #1 `feature/recipe-wizard-handoff` (기록상 Draft/Open/Unmerged; 재개 시 재조회). 이 문서는 **앞으로 무엇을 끝내야 하는지**에 대한 실행 기준이다. 기존 날짜별 계획·실측·인수인계는 삭제하지 않고 증거 원본으로 유지한다. 문서 작성은 CPU/GPU/CI 검증이나 운영 승인에 해당하지 않는다.

> **핵심:** P3의 성공적인 일회성 전환과 P5의 MTP0 개발 trial은 완료된 범위 안에서만 유효하다. **Orcarouter MTP2 실기 구동은 아직 하지 않았고**, P1/P2 Wizard end-to-end, P3에서 P8로 넘긴 Flash 재설치, P5 기능·성능, P6 실전환, P7 실연동, P8 실복구도 끝나지 않았다. P7 증거 서명 설계를 먼저 진행한다는 이유로 이 작업들을 완료 처리하지 않는다.

## 1. 판정 규칙과 불변 조건

- 각 작업은 `SOURCE`, `CPU`, `CI`, `DGX_READ_ONLY`, `DGX_LIVE`, `OPERATING_ACCEPTANCE`를 **각각** 판정한다. `PASS`에는 대상 SHA, 실행 주체, 명령/조건, 원본 receipt, 종료 코드와 승인 범위를 묶는다. `NOT_RUN`, `BLOCKED`, `DEFERRED_CONDITIONAL`, `HISTORIC_SCOPED_PASS`는 서로 다르다.
- **이관 ≠ 완료:** P3-E/F의 운영 미완료는 P8-R0/R1/R2에 남아 있다. **MTP0 ≠ MTP2:** P5 v3 trial API·텍스트와 제한된 visible TTFC 측정은 MTP2 loader·품질·성능 증거가 아니다. **Fake-DGX ≠ 실복구:** 수치·출처·인증도 별도 게이트다.
- vLLM **0.32.0**, SGLang 금지, `ONE_ACTIVE_MODEL_ONLY`, host `:8000/v1`. Flash/27B/Orcarouter의 이미지·원본 checkpoint·donor·PLE·HF cache·기존 운영 Journal 및 OpenWebUI/Ollama/Portainer를 보존한다. 현재 실제 활성 모델·포트 소유권은 과거 receipt에서 추정하지 말고 운영 직전 새로 확인한다.
- 새 승인 없이는 GPU 추론·MTP2 overlay 생성·이미지 빌드·Docker start/stop·모델 전환·재설치·삭제·privileged procfs·운영 Journal 기록·장애 주입·CI dispatch/설정 변경·main 수정·PR merge를 실행하지 않는다. 이 문서는 위 행위의 승인이 아니다.

## 2. 미완료 작업 장부 — 단계별로 닫는다

| ID / 단계 | 지금까지 확보한 범위 | **남은 작업 / 종료 증거** | 분류 |
| --- | --- | --- | --- |
| W0 / upstream fork gap | 현재 fork는 Blazux `b0aa8b7` (2026-11-02)에서 분기; upstream `01731a1` (2026-11-15) 직접 조회 | upstream 0.33 기반 이미지·MTP 프로필·prefix cache workaround·보안 수정 등 변경을 **기능별 목록/적용 여부/위험/테스트**로 감사. 포크의 vLLM 0.32 P5 Orcarouter 전용 patch/ABI와 27B/Flash Wizard의 호환성을 각각 검증. 원본 원격을 merge/rebase하거나 GPU에 자동 적용하지 않음 | 별도 source 감사/버전 업그레이드 결정 필요 |
| W1 / P1 Flash | 실제 DGX의 과거 Flash 백엔드·API·Tools/Vision·제한 벤치 PASS | 통합 **Wizard**를 통한 pinned prepare/serve/verify/benchmark/evidence 및 실패·재시작·reinstall UX를 별도 검증. 종전 `flash`/백엔드 성공만으로 Wizard e2e 종료 금지. 안전한 기존 증거로 충족 가능한 세부 항목은 먼저 식별하고, 신규 실기 항목은 승인 후 수행 | 미완료 Wizard 범위; 과거 백엔드 PASS 보존 |
| W2 / P2 27B | pinned 27B GPU/API, Native Tools **canonical recipe 실기 migration COMMITTED + 새 3회 bounded 벤치 PASS** 및 상태/운영 Journal 재확인 (운영자 제공 receipt) | 이미 완료된 canonical migration을 다시 요구하지 않음. 남은 **모델 우선 Wizard e2e**, OpenWebUI Native 실제 UI/agent end-to-end, 새 canonical Docker ID에 대한 기존 P3 반복 전환 lineage 호환/원본 복구·응답 품질을 별도 판정. 과거 1회성 variant 시험과 현재 canonical을 혼동 금지 | canonical native-tools 부분 완료; Wizard/연동/lineage OPEN |
| W3 / P3→P8-R0/R1/R2 | P3 A/B/C/G의 역사적 **실제** Flash↔27B 성공 전환, D 당시 read-only PASS; E host-asset metadata, F CPU handoff | canonical Flash **실행 가능한 recipe/image/cache·env·security provenance**를 확정하고, 별도 승인된 실제 재설치·API/Tools/Vision·benchmark·idempotence·Journal·원본 복귀를 실증. P3 A/B/C/G를 재실행하거나 P8로 옮긴 일을 완료로 기록하지 말 것 | P3 성공 전환 CLOSED; 재설치/범용 lifecycle OPEN |
| W4 / P4 Storage | A 용량 인벤토리와 B/C 삭제 없는 실제 DGX dry-run PASS | 실제 삭제는 **필수 선행 작업이 아님**. 공간 부족 등 명시적 필요 시에만 정확한 대상·공유 참조·복구 계획·별도 승인 후 추진; 없으면 `DEFERRED_CONDITIONAL` | 조건부 보류, PASS/삭제 승인 아님 |
| W5a / P5 MTP0 baseline | Orcarouter v3 MTP0 `DEVELOPMENT_TRIAL` API/텍스트 PASS; 1K/4K/7K 비사고 visible TTFC/TPS 1회 측정, reasoning-only 시험 별도 | 원본 측정의 workload·`finish_reason=length`·리소스 한계 명시. MTP0의 긴 context, 동시성, 장기 안정성·정확한 응답, 실제 모델별 리소스/품질 baseline을 별도 수용; 기존 일회성 승인은 재사용 금지 | 부분 실측/운영 미승격 |
| **W5b / P5 MTP2** | pinned donor **31 BF16 tensors / 3 shards**의 과거 메타데이터·SHA 감사와 `mtp2` **후보** recipe; 현재 v3 adapter는 `MTP0_ONLY` | overlay 생성 권한·불변성/지문·vLLM 0.32 adapter/MTP loader·lm_head/QSA/CUDA graph 호환성, MTP2 프로필/served ID·실제 GPU load·speculative 동작·Chat/SSE/오류 및 동일 조건 MTP0 대비 TTFT/TPS·메모리·품질을 각각 검증. **현재 실제 MTP2 trial·benchmark = NOT_RUN**; YSLAB 수치는 우리 측정치 아님 | **최우선 누락 실기 패키지**, 별도 승인 필요 |
| W5c / P5 기능·출시 | P5 후보 runtime은 source 등록, MTP0 trial만 관측 | Orcarouter Native Tools/tool-result·OpenWebUI, reasoning/streaming, Vision은 지원 범위를 먼저 확정해 지원 시 실측, 16K 이상 긴 context/동시성·실부하 안정성, 메모리 정책 임계값, 원래 정의된 first-token logprob `1e-4` gate의 비교 가능 baseline/판정. canonical `qwen38-orcarouter` 승격은 이들과 별도의 변경/원복 승인 | 미검증/일부 기능 지원 여부 확인 필요 |
| W5d / P5-D provenance | Docker/API/PID 부분 상관; 비승격 `/proc/PID/smaps`·FD **3/3 EACCES**; 실제 PLE RSS/PSS 미관측 | 권한/도구 선행조건을 먼저 좁게 정의해 **별도 승인**을 구한다. 그 뒤 PLE 파일별 RSS/PSS·inode↔PID·실제 NAT/:8000 경로·GPU 배타 소유를 각각 검증. 동일 권한 재시도 금지; RC3는 서비스 장애나 RSS=0이 아님 | 권한/증거 차단 |
| W6 / P6 실제 Orcarouter↔27B | 사전검사, Fake-DGX 전환, P6-E in-memory Journal/Fake nonce의 CPU 결과 | 독립 승인·consume-once 영속 nonce/Journal v2·충돌/크래시 복구·실제 executor·원본 보존을 먼저 수용. 이어서 **두 방향 각각** Wizard 승인형 실전환, served ID/:8000/GPU 단일 소유, 실패 시 관측 가능한 복귀·Journal/receipt를 확인. P5 trial의 중단/재시작을 P6 전환 PASS로 대체 금지 | 실전환 NOT_RUN, 운영 ledger BLOCKED |
| W7 / P7 통합 | source JSON 구조 일치·session/nonce/collector 레이블 검사, 해당 SHA CPU 16/16 | 실제 신뢰 가능한 issuer/collector·검증·replay fence를 설계하고, **실제 독립** Service/Proxy/Gateway/Storage/OpenWebUI 경로·upstream·API ID·Wizard UX를 관측. 서명된 자기 주장도 물리적 관측의 증거가 아님 | source 계약만 PASS; 실연동 OPEN |
| W8 / P8 복구·최종 | 24/66/48 등 서로 다른 Fake-DGX matrix | R0 Flash desired-state/recipe, R1 승인형 재설치, R2 기능·복귀, **R3 별도 승인된 실제 장애 주입/자동 원복**, 오작동 시 중단/수동 복구 및 최종 Wizard 수용. 과거 P3 성공 전환이나 Fake 복구로 R3를 닫지 말 것 | 실복구·운영 Go/No-Go BLOCKED |

**근거:** [27B canonical Native Tools 실기 PASS](P2-27B-CANONICAL-NATIVE-RECIPE-LIVE-PASS-20261107.md), [원래 모델/Wizard 단계 계약](MODEL-RECIPE-WIZARD-PLAN.md), [P2 canonical recipe 미실행 기록](P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md), [P3→P8 이관](P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md), [P5 MTP2 설계와 출고 게이트](P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md), [현재 P5 recipe의 `MTP0_ONLY`/`mtp2` 후보](../recipes/qwen38-orcarouter.runtime.json), [P5–P8 공통 계약](P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md), [P8 실복구 계약](P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md). 작업별 원본과 최신 상태는 [Evidence Ledger](../handoff/EVIDENCE-LEDGER.md)에서 SHA 단위로 대조한다.

## 3. 실제 실행 순서 — 건너뛴 항목을 다시 드러내기

```text
T0  미완료 목록/기준선 동결: 현재 HEAD·recipe·서비스 읽기 전용 확인, 기존 receipt 대조
 ├─ U0  upstream 0.32→0.33 변경 감사·취사선택 (읽기 전용/CPU, 런타임 전환 아님)
 ├─ T1  P1/P2 Wizard 및 canonical 27B 미완료를 CPU/증거로 분리
 ├─ T2  P3-E/F → P8-R0 Flash 재설치 설계/리허설 (실제 R1/R2는 별도 승인)
 ├─ T3  P5 MTP2 source·donor·overlay·이미지·원복 경로 사전검증
 │     └─ 승인된 독립 MTP2 GPU trial → MTP0와 동일 조건 비교 → P5 기능/수치/안정성 판정
 ├─ T4  P5-D 권한 선행조건 및 측정 설계; P6-E 영속 승인/Journal; P7 출처 인증 (병렬 source 작업)
 └─ T5  P5 수용 증거 + P6 안전한 실전환 두 방향 + P7 실제 통합 증거
          └─ T6 P8-R1/R2/R3 승인형 재설치·실복구·최종 Wizard Go/No-Go
                    └─ T7 exact-SHA CI / 별도 운영·PR merge 승인
```

- **바로 다음 source-only 작업:** W0 upstream 변경 감사와 W1/W2/W3/W5b의 현행 구현·원본 receipt 대조를 병행한다. 특히 `MTP0_ONLY` adapter와 `mtp2` 후보 사이의 실제 누락을 명세/부정 조건 CPU 시험으로 고정한다. P7 신뢰 설계와 P6-E 영속성은 **병렬**로 진행할 수 있지만 P5 MTP2·Wizard·Flash 재설치를 지워 버리는 새로운 메인 로드맵으로 삼지 않는다.
- **MTP2 실기 전 별도 결정:** 파생 overlay/이미지 쓰기, 디스크·메모리 headroom, 현재 :8000 모델 서비스 중단/복귀 조건, 1회성 시험 범위·타임아웃·실패 시 수동 복구 및 증거 보존. `mtp2` 후보의 `qualification=NOT_RUN`, `launch_allowed=false`를 계획만으로 변경하지 않는다. GPU trial 결과가 나오기 전에는 MTP2 수용 시점을 예측하지 않는다.
- **조건부 분기:** W4 삭제는 용량이 충분하면 건너뛰고, W5c Vision은 해당 checkpoint/런타임의 실제 지원 여부를 조사해 지원 항목만 실기 수용한다. 수치 `1e-4` 기준을 충족하지 못하거나 동일 조건 비교가 불가능하면 `FAIL/INCONCLUSIVE`로 기록하고 정책 변경은 별도 결정한다. 승인 없이 게이트를 낮추지 않는다.
- **병렬 개발과 선행조건 구분:** P6-E/P7의 소스 보강은 P5 시험 승인 대기 중에도 가능하다. **그러나** P6 실전환은 P5 target/source의 준비·안전 복귀와 실제 Journal 승인에, P8 최종 운영 수용은 해당 모델 기능·P6·P7·실복구 증거에 의존한다. P3에서 이관한 Flash 재설치는 P8 최종 판정 이전에 별도로 실행/판정한다.

### U0 — fork 이후 upstream 변경 감사 (현재 운용 버전 교체와 별개)

2026-11-21 읽기 전용 `git fetch upstream main` 기준: fork 공통 조상 `b0aa8b77604139557169387b2fa8386355d8b651`, upstream/main `01731a10c93dfab07ec6fabf6a30cde7f4bfc25d` (2026-11-15). upstream 고유 커밋 **36개**, 관련 diff 115 files (merge-base→upstream), fork 고유 커밋 1472개라는 Git 비교 결과다. 이 숫자는 **우리 포크에 미적용된 독립 기능 36개**라는 의미가 아니다. `upstream/main`은 [vLLM 0.33 기반](https://github.com/blazux/qwen3.8-Flash-DGX/blob/01731a10c93dfab07ec6fabf6a30cde7f4bfc25d/docs/VLLM-033.md) Dockerfile과 `mtp-fast`(NVIDIA Flash, MTP3), opt-in [prefix-cache workaround](https://github.com/blazux/qwen3.8-Flash-DGX/blob/01731a10c93dfab07ec6fabf6a30cde7f4bfc25d/docs/PREFIX-CACHE-WORKAROUND.md), `--api-key` 출력 redaction, 벤치 fixture/검증을 포함한다. upstream의 0.33 Flash MTP3는 **우리 Orcarouter BF16 MTP2와 다른 모델·프로필**이다. benchmark 수치와 prefix workaround의 관측 한계를 upstream 문서 그대로 유지하며 우리 하드웨어 수용으로 소급하지 않는다.

1. `merge-base` 기준으로 Dockerfile, patch/serve/flash/profile, 테스트, security fix, 모델별 recipe와 문서의 **변경 유형별 차이**를 기록하고, 우리 포크가 이미 동등하게 반영했는지 확인한다. upstream 보안 관련 redaction은 우선 검토하되 기능 변경을 무조건 가져오지 않는다.
2. **결정 분기:** (a) vLLM 0.32 유지 + 특정 수정만 독립 backport, (b) 별도 후보 브랜치/이미지에서 0.33 검증, (c) 불필요/위험한 변경 보류. 기준은 GB10 ARM64 ABI, BF16 PLE mmap, QSA/lm_head, Orcarouter 31-tensor MTP2, NVIDIA Flash/27B tools/vision/prefix-cache, 기존 Wizard·:8000/한 모델 운영 계약과 복구 가능성이다. 자동 `git merge upstream/main`/Docker 이미지 교체 금지.
3. 선택된 변경마다 pinned upstream SHA·fork 적용 SHA·부정/회귀 CPU, 독립 이미지 빌드/로더 smoke(별도 승인), P1/P2/P5 회귀·동등 workload/수치·원본 복구 증거를 수집한다. **업그레이드 Go/No-Go는 별도 결정**이며 그 전까지 운용 버전은 vLLM 0.32.0 고정. MTP2 최초 수용을 무조건 upstream 0.33 도입 이후로 미루지 않는다.

## 4. 현재 검증 증거와 다음 판정에 필요한 영수증

| 영수증 | 확인된 사실 | 아직 주장할 수 없는 것 |
| --- | --- | --- |
| P5 visible one-shot (DGX source `bc0a9ea…`) | MTP0, request-local `enable_thinking=false` 1K/4K/7K 3/3의 visible TTFT=TTFC 및 TPS 관측 | MTP2 성능, 완결 답변, 장기 안정성, production |
| P6-E CPU (`4c86b799…`) | Journal 22/22 + Fake Nonce 15/15, 운영자 제공 RC0 | 실제 운영 승인/영속 replay/복구 |
| P7 CPU (`c36b2bf…`) | integration contract 16/16, 운영자 제공 RC0 | 서명/실제 독립 관측 및 사용 권한 |
| Wizard/Manifest CPU (`8e4eb923…`) | 126/126 + 77/77, 운영자 제공 각각 RC0 | P1/P2/P5 Wizard 실기 e2e, GitHub CI |
| Actions 최신 | 과거 특정 SHA 이후 신규 성공 run 미확인; 원인 미확정 | 현 HEAD CI PASS. 문서만 push해도 CI가 반드시 뜬다는 보장 |

새 trial/수용 항목에는 **검증 대상 Git SHA**, 매니페스트/이미지/체크포인트 digest, 기존·후속 Docker full ID 및 모델 ID, :8000 상태, MTP0/2 프로필, workload/토큰/반복 수, 초(s) 단위 TTFT/TTFC·tokens/s, 리소스·오류·타임아웃, 원본 receipt 경로/해시, 판정자와 별도 승인 식별자를 포함한다. 미측정 항목은 0으로 채우지 않는다. 실기 전 read-only 확인 역시 허용된 권한과 범위에서만 수행한다.

## 5. 종료 규칙 / 다음 문서 갱신

**완료 선언 금지 조건:** W0의 upstream 변경 취사선택/버전 유지 결정, W1/W2 Wizard 경로, W3 Flash 재설치, **W5b MTP2**, W5c 모델 기능·수치, W5d PLE/NAT, W6 양방향 실전환, W7 독립 실연동, W8 자동 원복 중 하나라도 요구 범위에서 미수용이면 `P1–P8_COMPLETE=false`, `PRODUCTION_RELEASED=false`. 조건부 W4만 필요성과 별도 승인 없을 때 `DEFERRED_CONDITIONAL`로 남길 수 있다. 지원되지 않는 기능은 근거와 사용자 결정으로 범위를 확정한다.

CI는 각 **최종 코드 SHA**의 실제 Actions Run ID와 결과가 있어야 PASS다. 원인을 알 수 없는 CI no-run은 `CI_UNVERIFIED`이며 PR merge로 우회하지 않는다. 마지막에는 운영자가 증거·위험·복구 계획을 검토하고 Go/No-Go와 PR merge를 **각각 별도로 승인**한다.

이 문서가 현재 작업 목록의 **정식 진입점**이다. [기존 2026-11-21 G0–G8 계획](P1-P8-CURRENT-ROADMAP-20261121.md)은 P5-D/P6-E/P7 증거 신뢰 설계의 세부 보조 계획으로 보존하고, [2026-11-19 실행 기록](P1-P8-EXECUTION-ROADMAP-20261119.md)은 역사적 근거로 보존한다. 이후 단계별 receipt가 생길 때는 해당 작업 ID·정확한 SHA·승인·종료 조건을 먼저 갱신하고, 승인되지 않은 새 실행을 다음 작업으로 쓰지 않는다.
