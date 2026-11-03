# Blazux 모델 지원 현황과 Orcarouter 추가 설계

- 작성 기준: 2026-11-04 (Asia/Seoul)
- 개발 저장소: `kjlee-inlct/qwen3.8-Flash-DGX`
- 개발 브랜치: `feature/orcarouter-bf16-adapter`
- Blazux 원본 기준: `blazux/qwen3.8-Flash-DGX@b0aa8b77604139557169387b2fa8386355d8b651` (vLLM 0.32.0)
- 기존 Preview 기준: `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark@2e6a5794b0fe282ae4bf6f4852acd919fea6d55a`
- YSLAB-ai 참고 기준: `YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark@9492b78c6bc04638587b42f2ffeb0680b0fcb3ef`
- 상태: **SOURCE-REVIEW / DESIGN ONLY**. 신규 Fork의 Orcarouter 런타임·CPU·GPU 검증은 아직 수행하지 않았다.

## 1. 지금 Blazux에서 사용 가능한 체크포인트·모드 (질문 2)

| 체크포인트/범주 | upstream 근거 | 모델 실행 상태/제약 |
| --- | --- | --- |
| `nvidia/Qwen3.8-Flash-Next-NVFP4` | 기본 `MODEL`, 공식 ModelOpt mixed-precision NVFP4 export | **기본 지원, upstream GX10 실측**. 기본 `default` 프로파일은 `MODE=hybrid`, MTP2, YaRN. `published`는 `MODE=nvfp4` |
| `RadixArk/Qwen3.8-Flash-Next-NVFP4` | README에서 두 번째 공식 지원 레시피로 명시 | **지원, upstream GX10 실측**. `MODEL=`로 선택. `hybrid-mtp`는 RadixArk 전용으로 Inferact에서 NVFP4 MTP 전문가를 가져와 구성 |
| 같은 ModelOpt 가중치 형식의 일부 파생 체크포인트 | README가 Jiunsong, drowzeys 사례를 언급 | **형식상 호환 가능**; 각 파생 모델의 실제 v0.32 실행·품질을 일괄 보증하지 않음 |
| `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` | README가 `compressed-tensors` 파생 모델로 명시 | **인식된 별도 양자화 형식이나 Blazux 런타임 검증은 없음**. 본 개발의 추가 대상. `MODE=hybrid` 변환 대상 아님 |
| `lychee888/…-FP8PLE` | README issue #23에서 압축 텐서 파생형식 및 PLE mmap 예상 경로 설명 | **가능성만 기록, upstream에서 실제 기동 미검증** |
| `Inferact/Qwen3.8-Flash-Next-NVFP4` | Blazux `hybrid-mtp`의 일부 MTP 전문가 **공여** 체크포인트 | 현재 Blazux에서 **독립 타깃 모델의 검증된 지원으로 표시하지 않음**. YSLAB BF16 레시피의 별도 target 지원과 구분 |
| `incoai/Qwen3.8-Flash-Next-DFlash2` | `dflash` 프로파일 | **별도의 타깃 모델이 아닌 0.6B speculative draft 모델**. 기존 NVIDIA/RadixArk 타깃에 선택적으로 사용 |

`MODE=nvfp4`와 `MODE=hybrid`는 *동일 타깃 체크포인트의 가중치 레이아웃/실행 모드*이지 서로 다른 언어모델이 아니다. `published`, `default`, `speed`, `context`, `context-1m`, `native`, `dflash`는 실행 프로파일이다. 모델 목록은 Hugging Face의 모든 Qwen 변종을 뜻하지 않는다.

주요 구현: `flash` → `profiles/*.env` → `scripts/serve.sh`에서 `MODEL`, `MODE`, `MTP`, `SERVED_MODEL_NAME`, `PORT`, `NAME` 등을 선택한다. Blazux 기본 target은 NVIDIA이고 `MODEL=RadixArk/Qwen3.8-Flash-Next-NVFP4`로 전환할 수 있다. 소스상 `flash`는 `config.json`의 `quantization_config`도 인식하고, 압축 텐서 체크포인트의 `hybrid` 변환을 회피하도록 안내한다.

**근거:** [Blazux README — Checkpoints](https://github.com/blazux/qwen3.8-Flash-DGX/blob/b0aa8b77604139557169387b2fa8386355d8b651/README.md#checkpoints-nvidias-nvfp4-default-and-radixarks), [flash](https://github.com/blazux/qwen3.8-Flash-DGX/blob/b0aa8b77604139557169387b2fa8386355d8b651/flash), [serve.sh](https://github.com/blazux/qwen3.8-Flash-DGX/blob/b0aa8b77604139557169387b2fa8386355d8b651/scripts/serve.sh), [profiles](https://github.com/blazux/qwen3.8-Flash-DGX/tree/b0aa8b77604139557169387b2fa8386355d8b651/profiles).

## 2. 기존 모델은 유지하면서 Orcarouter를 추가하는 구조 (질문 3)

**설계 원칙:** upstream의 NVIDIA/RadixArk 프로파일·ModelOpt 로더·MTP·PLE·QSA는 그대로 둔다. Orcarouter 추가는 **별도의 opt-in 체크포인트/어댑터/프로파일**로 구현한다. 기본값과 기존 checkpoint 동작을 변경하지 않는다.

```text
Blazux upstream vLLM 0.32.0 + 기존 최적화
├── nvidia / default,published,...      [기존 그대로]
├── RadixArk / hybrid,context,...       [기존 그대로]
└── Orcarouter / dedicated profile      [신규, 기본 OFF]
    ├── orcarouter 원본 NVFP4 + compressed-tensors checkpoint
    ├── BF16 PLE mmap (95.37 GiB, 128 shards, scale-free)
    ├── MTP OFF target-only compatibility [첫 검증 목표]
    └── 검증된 BF16 MTP 31-tensor overlay / MTP=2 [최종 목표]
```

### 2.1 체크포인트와 이름 분리

- Orcarouter 원본: `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799` (접근 승인·토큰 필요). **원본 checkpoint는 수정 금지**.
- PLE 기대 구조: `128` tensors, `320001536` rows, width `160`, `BF16`, layer `1`, 총 약 `95.37 GiB`. `VLLM_PLE_MMAP` 경로 사용. 별도 FP8 변환 금지.
- MTP2는 원본 Orcarouter checkpoint에 존재하지 않는 **31개 BF16 텐서**를 가져오는 별도 준비된 overlay가 필요하다. 소스는 `RadixArk/Qwen3.8-Flash-Next-NVFP4@7b719225242aacd3dbd3f9407468c2ee9a9d2594`; 3개 donor shard의 해시/이름/Shape/dtype/count 확인을 유지한다. MTP OFF baseline과 MTP2 경로를 혼동하지 않는다.
- 모델 ID는 target별로 분리: 기본 Blazux `qwen3.8-flash-next`는 변경하지 않는다. Orcarouter 운영 호환 ID `qwen3.8-flash-next-orca-uncensored-bf16-mtp`는 새로운 프로파일에서만 사용한다. `SERVED_MODEL_NAME`은 API 표시 이름이지 가중치 선택 키가 아니다.
- 추가된 target 설정은 **보존된 checkpoint/PLE/HF cache를 읽기 전용으로 참조**하는 격리 stage에서만 준비한다. 원본 Hugging Face snapshot 내부 index와 safetensors를 덮어쓰지 않는다.

### 2.2 코드/ABI에 필요한 실제 확인

1. **Config / architecture**: Preview의 `Qwen3_8FlashNext` vs v0.32의 `Qwen4Exp` 모델 등록, text config, Loader, quantization path, checkpoint weight names/shapes. `compressed-tensors`의 FP8 dense+NVFP4 routed experts, 별도의 quantized `lm_head`까지 검사.
2. **BF16 PLE**: Blazux `src/vllm_ple_mmap.py`는 이미 `BF16`/`F16`을 지원하며 동일한 `layers.<idx>.ple.ple_embedding.ngram_embedding.shard_N.weight` 이름 패턴을 사용한다. 그러나 v0.32의 `Qwen4ExpNGramEmbedding`, `compute_ngram_ids`, `ple_mmap_lookup_ids`, `forward`/CUDA graph 경계는 Preview의 생성자·`forward_impl` 패치와 다르다. 128개 shard 완전성·dtype·row count·hash/shape/scale-free와 forward parity를 **별도 adapter/test에서 입증**한다.
3. **MTP**: v0.32 `Qwen4ExpMTP`에 Preview BF16 31-tensor overlay를 단순 복사하지 않는다. `compressed-tensors` ignore-path remap, MTP layer naming, load guard, shared target head, draft/target vocab, speculative acceptance 및 aux-output를 실제 소스로 매핑한다. **MTP OFF를 먼저**, 이후 `MTP=2` 검증. Reduced 65,536 vocabulary/DFlash2는 초기 Orcarouter 이식에 적용하지 않는다.
4. **API**: Chat/Responses, tool roundtrip, reasoning/streaming/finish reason과 외부 모델 ID를 후보에서 별도 시험한다. NVIDIA/RadixArk 동작을 보존하도록 변경의 조건 분기를 체크포인트 전용으로 제한한다.
5. **메모리**: 단일 DGX Spark 128GB 통합 메모리에서 2개 대형 타깃 모델을 **동시에 GPU 상주하지 않는다**. PLE는 file-backed mmap으로 남기되 모델 weights, KV, OS/page cache, draft의 여유는 GPU 정비창 승인 후 실제 측정한다.

**참고 구현:** [YSLAB-ai README](https://github.com/YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark/blob/9492b78c6bc04638587b42f2ffeb0680b0fcb3ef/README.md), [manifest](https://github.com/YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark/blob/9492b78c6bc04638587b42f2ffeb0680b0fcb3ef/compatibility.json), [MTP guard](https://github.com/YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark/blob/9492b78c6bc04638587b42f2ffeb0680b0fcb3ef/src/patch_qwen4_exp_mtp_load_guard.py), [compressed-tensors MTP remap](https://github.com/YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark/blob/9492b78c6bc04638587b42f2ffeb0680b0fcb3ef/src/patch_qwen4_exp_mtp_compressed_ignore.py), [quantized head patch](https://github.com/YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark/blob/9492b78c6bc04638587b42f2ffeb0680b0fcb3ef/src/patch_qwen4_exp_quantized_lm_head.py). 모두 **구형 Preview vLLM 전용**이므로 v0.32에 기계적으로 적용하지 않는다.

### 2.3 다중 모델을 '보존'하는 것과 '동시 서비스'는 다름

- **지원 코드 보존**: NVIDIA/RadixArk 프로파일과 기능/테스트는 삭제하지 않는다. Orcarouter를 opt-in 경로로만 추가한다.
- **체크포인트 보존**: 디스크/HF cache의 각 모델을 개별 revision으로 관리한다. 재선택을 위해 재다운로드/재변환하지 않는 것을 목표로 한다.
- **선택적 실행**: 모델 전환은 계획된 별도 운영 절차로 수행한다. 서로 다른 `NAME`, `PORT`, 이미지 태그, 로컬 stage를 쓰더라도 **단일 GPU 메모리가 공유**되므로 중복 대형 모델 기동을 자동 실행해서는 안 된다.
- **향후 API 선택**: 기존 클라이언트의 `:8000/v1`와 Orcarouter 모델 ID를 보존하려면 검증 완료 후 고정 포트의 API 프록시 또는 승인된 단일 active model cutover로 전환한다. 프록시는 요청을 라우팅할 뿐 물리적인 두 모델의 동시 상주를 가능하게 하지는 않는다.
- **위험한 launcher 주의**: upstream `scripts/serve.sh`는 `docker rm -f "$NAME"` 후 `docker run`한다. 운영 컨테이너 이름 `qwen38-flash-orca-uncensored-bf16-mtp`을 새 후보의 `NAME`으로 사용하지 않는다. 새로운 `./flash serve`, `./flash setup`은 **승인 전 실행 금지**.

### 2.4 단계별 구현·검증

| 단계 | 실제 목표 | 통과 기준 |
| --- | --- | --- |
| A: 소스+메타데이터 | 압축 텐서 checkpoint Config/Loader/shape, BF16 PLE, MTP weight name 매핑 | 차단점을 정확히 열거하고 GO/NO-GO 판단; 운영/가중치 불변 |
| B: 최소 opt-in adapter | `profiles/orcarouter.env`와 필요 시 `src/*` adapter, checkpoint 전용 경로, 테스트 | NVIDIA/RadixArk 기본 분기 불변, 가짜 CPU fixture 기반 핵심 매핑 검증 |
| C: MTP OFF 타깃 | 원본 Orcarouter checkpoint와 BF16 PLE mmap가 v0.32에 적재 가능하도록 조정 | 초기 설계 수준의 source/CPU PASS와 **향후 승인된 GPU 런타임 PASS 분리** |
| D: MTP2 overlay | 31-tensor 독립 stage 및 정확한 BF16 load/acceptance 경로 | MTP2가 실제 후보에서 검증; NVIDIA/RadixArk 회귀 |
| E: API/성능/운영 | 별도 GPU 승인 후 one-model window, 복구·모니터링, 컷오버 | Chat/Responses/Tools/Stream/메모리/수치 기준, 기존 same-ID 서비스 복구 |
| P3 | reduced draft vocab, DFlash2, 500k/1m, 고급 메모리/수치 원인 분석 | 별도 일정. 기존 strict `1e-4` Release Gate는 계속 차단 조건 |

## 3. 기존 운영 서비스 보호

기존 개발 저장소 `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark`는 **동결·보존**하고, 신규 기능 개발은 이 Fork에서만 한다. 운영 원본은 사용자가 실제 DGX에서 변경했는지 확인하기 전까지 아래 고정 자산으로 취급한다.

- 운영 컨테이너: `qwen38-flash-orca-uncensored-bf16-mtp`
- 고정 Container ID: `3fc5a3d5be1d52595602287acd87895220219bad050484251ac0408a163ffc45`
- 고정 이미지 SHA256: `sha256:b0984c4b724b6f8c0745acb654994e1bd3a6c50b75c2c76078f1bfd6b395f39a`
- API `:8000/v1`, 기존 외부 클라이언트, 기존 모델 ID 유지
- DGX 기존 checkout `~/Workspace/llm/blazux-phase6-gates` 보존; 신규 `~/Workspace/llm/blazux-orcarouter` 사용
- 원본 컨테이너 stop/rm/recreate/exec, 이미지·체크포인트·HF cache·PLE·Compile cache 변경, 새 GPU 모델 구동/성능부하, 운영 cutover는 **별도 승인 전 금지**
- strict first-token logprob pairwise absolute `1e-4` release 기준은 해결/면제된 것이 아니다. 기능 구현 완료, CPU 검증, GPU 검증, 출시 승인을 별개 상태로 기록한다.

**결론:** Blazux upstream이 검증한 NVIDIA/RadixArk 경로를 보존한 채, Orcarouter는 `compressed-tensors + BF16 PLE mmap + optional BF16 MTP2` 전용 호환 경로로 추가한다. 현재는 **BLOCKED_NEEDS_EXACT_EVIDENCE**, 기존 Blazux 모델을 삭제하거나 이전 Preview 서비스를 중단할 이유는 없다.
