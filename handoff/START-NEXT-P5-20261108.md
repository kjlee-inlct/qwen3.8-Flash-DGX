## 2026-11-08 — P5 source implementation and acceptance update (not GPU released)

P5 source was committed to the existing feature branch and Draft PR #1 as [33adec1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/33adec182e97a8eac0d5584bdf73f1448bdd84f2), with [GitHub Actions 42429745463](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463) **SUCCESS** including the new 20/20 CPU/Fake-DGX tests and `--cpu-only --json` PASS. Additional detailed per-case JSON and profile inspection enhancements require independent follow-up CI.

Implemented source: `recipes/qwen38-orcarouter.runtime.json` (pinned, **unqualified**, launch forbidden), imported YSLAB safetensors/manifest/BF16 PLE audit and immutable MTP overlay code under `scripts/p5_vendor`, donor 3-shard SHA256 / 31 BF16 name audit when local files exist, distinct MTP0/MTP2 candidate recipes, Wizard `p5` and `model orcarouter-flash-next` routes, `scripts/temporary/p5-one-shot-acceptance.sh`. The vendor overlay builder is **not** executable via CLI and no HF asset changes were authorized. Prior Blazux BF16 PLE source markers pass static inspection only; compressed-tensors and MTP2 runtime ABI/quantized lm_head/CUDA graph compatibility in actual vLLM 0.32 remain unqualified.

No DGX command/active-state reread or GPU/API/benchmark/rollback was performed in this session. All live P5 stages are NOT_RUN, `--gpu-trial` permanently BLOCKED until a separate operator approval and verified image/rollback implementation. Preserve 27B and :8000/ONE_ACTIVE_MODEL_ONLY, other models/caches, P3 historical receipts, no P4 deletion/P6 switch/P8 tests or Draft PR merge. New source/runbook: `docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md`.

---

# New Conversation Starter — Blazux DGX Spark / vLLM 0.32 / P5 Orcarouter BF16PLE Integration

이전 대화의 Blazux / NVIDIA DGX Spark / vLLM 0.32 기반 모델 레시피·Wizard·서비스 관리 프로젝트를 **P5부터 이어서 실제 개발**해주세요.

**이번 대화의 최우선 목표:** YSLAB-ai의 `Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark` 참고 구현을 **현재 Blazux vLLM 0.32.0 기반**에 통합하여 `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4`의 `compressed-tensors + BF16 PLE mmap + 선택적 31/31 BF16 MTP2`를 기존 매니페스트·레시피·Wizard·서비스·벤치·증거 관리 방식으로 설치·실행·검증 가능하게 만드세요.

**상태 요약이나 작업 계획으로만 끝내지 마세요.** GitHub 연결 도구를 사용해 소스·레시피·테스트·문서까지 한 번에 최대한 구현하고, 단일 임시 스크립트에서 CPU/Fake-DGX와 DGX 읽기 전용/승인된 GPU 단계의 결과를 **자동 판정하는 체계**를 완성하세요. 단, 코드 완성과 GPU 실제 시험은 별개입니다. 운영자 승인 없는 GPU 기동, 기존 27B 중단, :8000 전환, 데이터 삭제는 하지 않습니다.

## 1. 저장소·브랜치·운영 환경

| 항목 | 기준 |
|---|---|
| 개발 저장소 | https://github.com/kjlee-inlct/qwen3.8-Flash-DGX |
| 주 작업 브랜치 | `feature/recipe-wizard-handoff` |
| 시작 전 확인할 마지막 알려진 HEAD | `ac88693196a8b2b5efc95f091dc88531d6951037` — 새 세션에서 반드시 재조회 |
| PR | [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) Open / Draft / Unmerged, **기존 PR을 유지** |
| 최근 확인한 CI | [42405103774](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42405103774) SUCCESS; P4까지 **902/902 CPU/Fake-DGX PASS, 41 그룹** |
| 병렬 과거 설계 브랜치 | `feature/orcarouter-bf16-adapter@620598c30cfe3521af99a935caf0baf5b83556d8` — 참고용, 무단 머지 금지 |
| upstream | https://github.com/blazux/qwen3.8-Flash-DGX |
| YSLAB 참고 저장소 | https://github.com/YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark |
| 참고 소스 SHA | `9492b78c6bc04638587b42f2ffeb0680b0fcb3ef` — 새 세션에서 최신 재조회 |
| DGX 작업 경로 | `~/Workspace/llm/blazux-orcarouter` |
| 장비/OS | NVIDIA DGX Spark GB10 / Ubuntu ARM64 |
| 엔진 | **Blazux vLLM 0.32.0** — SGLang 금지 |
| Wizard/API | `./wizard.sh`, `/v1`, **호스트 포트 8000** |
| 서비스 정책 | `ONE_ACTIVE_MODEL_ONLY`, 이전 모델 중지→새 모델 기동, 동일 GPU 동시 상주 금지 |

참고 YSLAB의 Dockerfile은 `vllm/vllm-openai:qwen38-flash-next@sha256:fc120ece...` 및 레이블 상 `0.1.dev20073+g8e685d198` 기반이고 기본 포트는 18300입니다. **이를 Blazux vLLM 0.32.0 이미지/ABI 및 포트 8000 대신 사용하지 마세요.** 구형 패치의 함수·클래스·CUDA Graph hook을 기계적으로 이식하지 말고 현재 소스와 비교해야 합니다.

## 2. 먼저 GitHub에서 반드시 실제로 읽을 문서

### 핵심 핸드오프 8종

1. `handoff/README.md`
2. `handoff/CURRENT-STATE.md`
3. `handoff/OPERATING-RULES.md`
4. `handoff/NEXT-ACTIONS.md`
5. `handoff/EVIDENCE-LEDGER.md`
6. `handoff/DECISIONS.md`
7. `handoff/CHANGELOG.md`
8. `handoff/SESSION-START-PROMPT.md`

### P5의 신규 최우선 문서

- `handoff/START-NEXT-P5-20261108.md` (이 프롬프트)
- `docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md` (세부 구현·승인·자동 판정 계약)
- `docs/HANDOFF-DOCUMENT-AUDIT-P5-20261108.md` (파일 존재와 이전 내용 최신화 감사)
- `docs/MODEL-RECIPE-WIZARD-PLAN.md`
- `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`
- `docs/WIZARD-CLI-CONTRACT.md`
- `docs/MANIFEST-CONTRACTS.md`
- `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`

### 실제 DGX P3/P4 폐쇄 증거와 P8 인계

- `docs/P4-A-DGX-READONLY-CAPACITY-EVIDENCE-20261108.md`
- `docs/P4-BC-DGX-READONLY-DRY-RUN-EVIDENCE-20261108.md`
- `docs/P4-BC-ONE-SHOT-DRY-RUN-20261108.md`
- `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`
- `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`
- `docs/P3-E-TO-P8-FLASH-REINSTALL-HANDOFF-20261108.md`
- `docs/P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md`
- `runtimes/service-policy.json`
- `runtimes/model-discovery.json`
- `recipes/qwen38-27b.runtime.json`
- `recipes/qwen38-flash-next.runtime.draft.json`
- `recipes/README.md`

### 반드시 검토할 참고 구현

- `YSLAB-ai/...@9492b78`: `README.md`, `compatibility.json`, `docs/HOW-IT-WORKS.md`, `docs/COMPATIBILITY.md`, `Dockerfile`, `src/vllm_ple_mmap.py`, `src/patch_qwen4_exp_{config,quantized_lm_head,mtp_load_guard,mtp_compressed_ignore}.py`, `src/patch_parallel_lm_head_linear_attrs.py`, `src/recipe/{manifest,download,audit,hybrid,mtp,runtime,safetensors,cli}.py`, `tests/` 및 `results/orcarouter/`.
- 별도 브랜치 `feature/orcarouter-bf16-adapter`의 `docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md`. 과거 설계와 현재 실측이 충돌하면 **최신 실제 DGX 관측→확정 결정/최신 수용→현재 HEAD 코드/매니페스트→이전 소스설계** 순으로 판단하고, 불확실성을 명시합니다.

## 3. 이전 작업의 완료/미완료 사실

- P1 NVIDIA Flash-Next (`nvidia/Qwen3.8-Flash-Next-NVFP4@fc694b54fb0174e0913e6adf86691ef85a4ead47`) 구동·Chat·Tool/Vision·Verify/Bench 증거 보존.
- P2 NVIDIA 27B (`nvidia/Qwen3.8-27B-NVFP4@482ca0f3832238542f8f5295dde86b5f22711d80`) canonical native tools/Open WebUI/benchmark 완료. 현재 마지막 실제 DGX 관측은 `qwen38-27b`, API `qwen3.8-27b`, 포트 8000.
- P3-A/B/C/G 실기 PASS/CLOSED, 재시험 금지. P3-E/F의 Flash 재설치 및 범용 lifecycle 수용은 P8로 인계됐음. P3-G를 되돌려 미완료로 취급하지 말 것.
- P4-A 실제 DGX `READ_ONLY_INVENTORY_COMPLETE`; 보고된 디스크 여유 **324,880,961,536 bytes** (그 시점), 두 HF 캐시 루트는 동일 파일시스템으로 여유 공간 합산 금지.
- P4-B/C 실제 통합 DGX **`READ_ONLY_DRY_RUN_PASS`**; 로컬 Fake-DGX 13/13, P4-B 검토 기록 9개·선택 삭제 0개, P4-C 2 PASS/2 DEFERRED/1 NOT_RELEASED/1 NOT_EXECUTED, `executed=false`, `live_deletion_approved=false`. 실제 삭제 어댑터 부재/미승격.
- P5는 **아직 구현/실측 전**: `wizard/menus/models/orcarouter_flash_next.py`는 인터페이스 수준, `runtimes/service-policy.json` Orcarouter는 placeholder (`checkpoint=null`, `served_id=null`, `qualification=NOT_VERIFIED`). 정식 P5 런타임 레시피/원샷 판정 스크립트 미구현. P6 실제 Orcarouter↔27B 일반 전환은 P5 다음 별도 단계.
- P8의 장애 주입/자동 복구/최종 프로덕션 수용은 **NOT_RUN / NOT_RELEASED**. 실측이 없는 항목을 PASS/구동 가능으로 표시하지 마세요.
- 27B / Flash / Orcarouter HF 캐시, Open WebUI, Portainer, 모든 역사적 영수증 보존. 오래된 2026-11-08 P4-A용 starter 문구는 역사적 상태이며 현재 지시가 아닙니다.

## 4. P5 대상 모델과 구현 전제

- Orcarouter 원본: `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799` — gated HF 접근·토큰/약관 선행, 토큰 출력 금지. 기존 보존된 캐시의 실제 revision·파일 완전성은 검증 필요.
- 원본은 **compressed-tensors + direct BF16 PLE**, 기존 NVIDIA/RadixArk ModelOpt hybrid와 다름. PLE 128텐서/320001536행/width160/BF16/약95.37GiB NVMe mmap, 로컬 무결성 및 weight map 검사.
- 원본에는 MTP 가중치가 없음. MTP2 별도 준비 시 `RadixArk/Qwen3.8-Flash-Next-NVFP4@7b719225242aacd3dbd3f9407468c2ee9a9d2594`의 **31 BF16 MTP tensors / 3 pinned donor shards**를 파일명·sha256·크기·dtype·shape·architecture/load-count로 fail-closed 검증하고 원본 불변인 로컬 overlay/view로 구현.
- **MTP=0 기초 경로와 MTP=2 경로를 한 번에 소스 구현하되 분리 검증**. NVIDIA/RadixArk 기존 실행 경로와 default recipe를 건드리지 않음.
- YSLAB 검증 프로파일: PIECEWISE CUDA graphs/BF16 KV/262144 native context/8 max seq/gpu utilization 0.80/PLE prewarm OFF/MTP2. 이는 원본 실측 참고이며 Blazux 0.32 환경에서 별도 실제 적격성·메모리 측정 필요.
- 기존 Orcarouter 운영 호환 모델 ID 후보: `qwen3.8-flash-next-orca-uncensored-bf16-mtp`. 27B `qwen3.8-27b`, NVIDIA `qwen3.8-flash-next`와 명확하게 분리. 실제 제공 ID는 매니페스트에 명시하고 검증.
- 원본 YSLAB 측 MTP2 44.23 tok/s 등 수치는 **외부 참고 결과**이지 본 프로젝트 실측이나 자동 성능 합격 기준이 아님. 과거 strict first-token logprob pairwise abs `1e-4` release gate는 명시적 검증 없이는 해제 금지.

## 5. 이번 새 대화에서 최대한 일괄 구현할 항목

**단순 계획 금지: 리포지토리의 실제 모듈을 변경하고 테스트를 완성한 후 GitHub 커밋·CI·Draft PR 갱신까지 실행하세요.**

1. 소스/런타임 차이 맵: YSLAB vLLM 개발 빌드와 Blazux vLLM 0.32의 `Qwen4Exp` 아키텍처·quantized lm_head·compressed-tensors·MTP/PLE·CUDA graph splitting_ops를 함수·형식 단위 비교하고 누락/충돌을 문서화.
2. **Orcarouter opt-in 정식 레시피/매니페스트**: pinned 원본/도너/revision, 모델 ID, 정식 이미지/빌드 provenance, 모드별 파라미터, 캐시 뷰/리비전, `runtimes/service-policy.json`, discovery, recipe drift 및 Wizard 선택 UI 연계. 모델별 stop/recreate/remove는 별도 정확 승인과 실측 후 처리.
3. **BF16 PLE direct mmap**: vLLM 0.32 로더 경로에 checkpont-conditional 적용, 128 tensors 검증, zero-scale BF16, 메모리 경계, 샤드/safetensors 인덱스 변조 감지, page-cache/prewarm 정책, safe fail-closed.
4. **BF16 MTP overlay**: RadixArk 세 shard의 hash/type/name/shape 감사, 31/31 로드 guard, deterministic local view, MTP OFF baseline과 MTP2 qualified profile 분리. 원본 checkpoint는 수정/삭제/이동 금지.
5. **Wizard 전체 P5 단계**: doctor→recipe→prepare→start→verify→benchmark→증거/히스토리; 기본 `./wizard.sh`, `model orcarouter-flash-next`, `p5` alias, 설치·상태·레시피 drift·캐시 재사용·이상 발생 시 안전 거부 UX.
6. **단일 임시 자동 판정**: `scripts/temporary/p5-one-shot-acceptance.sh`, manager와 JSON/종료코드; `--plan`, `--cpu-only`, `--read-only`는 모두 운영 안전, GPU trial은 `--gpu-trial` 별도 입력/명시 승인. 단계별 PASS/BLOCKED/NOT_RUN/INCONCLUSIVE, 증거경로·issue·모델/리비전/이미지·지표, 마지막 집계 PASS/FAIL 명시.
7. **한 번에 많은 CPU/Fake-DGX 회귀**: 레시피 스키마, SHA/token redaction, 31 MTP 누락·변조·extra mismatch, PLE 형식/행 수/메모리 map, stale cache/symlink traversal, Docker 포트 8000 / 단일 모델, 안전한 resource ownership/승인·TTL·rollback, 복수 모델/foreign container, 레거시 P1-P4 비회귀.
8. **성능/기능 기준**: 실제 동의된 GPU trial에서 MTP0→MTP2 순으로 load, API `/v1/models`, Chat/Completions, reasoning, native tools roundtrip 및 tool-result continuation, SSE streaming, Open WebUI, benchmark TTFT/tokens/sec/e2e/latency/메모리/긴 문맥/안정성, Vision은 런타임 지원 시에만. 엄격한 수치 기준이 있다면 동등한 baseline/source/probe 없이 PASS 하지 말 것.
9. **DGX 안전 운영**: 실제 GPU trial은 기존 `27b` 중단이 필요하므로 정확한 plan_id, 유효기간, TTY 확인과 downtime acknowledgment, 원본 확인·복구·API 재검증. DGX 실측 자료를 제공받기 전 GitHub CI에서 GPU를 실측한 것처럼 표현하지 말 것. P6 일반 양방향 switch 또는 P8 장애 자동 복구는 실행 금지.
10. **문서 유지**: 코드/테스트/설계·매니페스트/CI/핸드오프/EVIDENCE-LEDGER/DECISIONS/NEXT-ACTIONS/CHANGELOG/기존 Draft PR #1을 그때그때 갱신하고 로그 및 외부 벤치마크 출처를 분리. 별도 PR 생성·머지/최종 출시 금지.

## 6. 단일 자동 판정 스크립트의 목표 사용 예시 (현재는 아직 없음)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p5-one-shot-acceptance.sh --plan --json
bash scripts/temporary/p5-one-shot-acceptance.sh --cpu-only --json
bash scripts/temporary/p5-one-shot-acceptance.sh --read-only --json
# --gpu-trial / --execute는 생성된 정확 plan과 사용자 별도 운영 승인 이후만.
```

**한 번에 코드를 구현한다는 것은 승인 없이 GPU를 실행한다는 뜻이 아닙니다.** 진행 가능한 소스 작업은 연속 처리하되, `:8000` 기존 27B를 내리거나 다운로드·체크포인트/overlay 쓰기·서비스 중단·모델 전환·실제 GPU 벤치 등 실제 상태 변경은 각 단계의 승인 계약을 준수합니다. 안전하게 검증할 방법이 없다면 명확히 `BLOCKED`로 남기고 다음 진행을 위한 정확한 명령만 보고하세요.

## 7. 반드시 보존할 운영 규칙

- 현재 모델 한 개만 GPU에서 실행, host port `8000` 단일 소유. SGLang 사용 금지, vLLM 0.32.0 유지. WebUI와 Portainer 서비스·사용자 데이터 유지.
- P4-B/C에서 검토한 9 자산은 삭제 대상 9개가 **아니라** 리뷰 기록 9개; 선택 삭제 0개. P4-C 실제 삭제 미구현/미승인. P5 진행 중 **실제 디스크 부족 문제가 발생했을 때만** 별도의 보존·공유 레이어·참조 그래프 감사와 운영자 별도 승인 하에 향후 정리 고려; 자동 Docker prune/HF 삭제 절대 금지.
- 원본 HF snapshots / derived views / images / historical reports / migration receipts 보존. 이미 설치된 cache가 존재해도 무결성/정확 revision을 검증하기 전 재사용을 PASS하지 말고, 중복 다운로드도 하지 않음.
- 운영자 승인 문자열·plan_id를 자동 생성/입력해서 통과시키지 않음. GPU trial / stop old / rollback은 각각 기존 Wizard 경계와 연결해야 함.
- P3-A/B/C/G 재실행 금지. P6 및 P8 실제 재설치/장애주입/자동복구/최종 릴리스는 별도 단계. 기존 Draft PR은 유지하고 무단 머지 금지.
- 실패나 `INCONCLUSIVE` 시 결과를 PASS로 위장하지 않고 정확한 코드/런타임/환경 원인, reproducible receipt와 next step을 남길 것.

## 8. 권장 진행 순서

**Step 1:** GitHub 연결 도구로 최신 branch HEAD, PR #1, CI, 변경파일, 참조 YSLAB HEAD와 병렬 adapter 브랜치를 확인.

**Step 2:** 위 핸드오프 8종·P5 두 문서·P4/P8 판정·매니페스트, `wizard/menus/models/orcarouter_flash_next.py`, `scripts/manager/`, `src/`, `profiles/`를 검토. 필요하면 git tree로 추가 관련 경로 탐색.

**Step 3:** P5 코드·정식 recipe·PLE/MTP adapter·Wizard route·원샷 자동 판정·Fake-DGX 및 회귀 테스트를 가능한 범위에서 **한 작업 묶음으로 구현**. 임시 스크립트가 CPU/Fake-DGX를 연속 수행, 자동 PASS/FAIL, 읽기 전용 DGX 검사와 승인 필요 GPU 단계를 분리하도록 함.

**Step 4:** GitHub CI를 확인하고 실패한 테스트를 직접 고친 뒤 최신 HEAD를 반영. 모델 assets/cache/원본 Docker 비파괴 현장 검사 프롬프트와 필요한 별도 GPU 승인을 문서화.

**Step 5:** `WHAT CHANGED`, `GITHUB HEAD/PR/CI`, `SOURCE & CPU AUTO-JUDGE`, `DGX READ-ONLY`, `MTP0/MTP2`, `RUNTIME/API/BENCH`, `RECOVERY/SAFETY`, `REMAINING BLOCKERS`, `NEXT ACTIONS`로 최종 보고. 완료·미실행·차단 구분.

## 마지막 지시

**P5의 구현과 테스트 자동화까지 한 번에 최대한 완료해 주세요.** 이전 P1–P4 검증은 그대로 보존하고 재작업하지 마세요. 현재 활성 27B를 임의 중단하거나 YSLAB 개발 이미지/포트 18300을 새 운영 기준으로 바꾸지 마세요. 새 대화에서 GitHub 소스 구현을 직접 수행하고, 자동 판정과 증거가 있는 범위만 완료 처리하세요.
