## 2026-11-09 current P5 v2 supersession — historical adapter now replaced by v3 runtime observation

[Current P5 audit](HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) · [Active P5 technical record](P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md)

Historical `qwen4exp-qsa62318-lmhead-v032-v2` and its failed GPU trial remain unchanged below; the **latest actual operator DGX observation** is v3 adapter `qwen4exp-qsa62318-lmhead-v032-v3` with corrected `lm_head.weight_scale`, container `qwen38-orcarouter-qsa62318-lmhead-v3`, :8000 API `qwen3.8-flash-next-orca-uncensored-bf16`, `LIVE_P5_TRIAL_API_VERIFIED` and MTP0 text `PASS_LIVE_INFERENCE` (READY). Only `DEVELOPMENT_TRIAL`; do not promote canonical `qwen38-orcarouter` without a separately approved lifecycle.

**2026-11-09 00:54–00:55 KST resource evidence (idle-only):** MemAvailable 30.18 GiB/121.63 GiB total, host swap 1.31 GiB, Orcarouter swap 0 GiB; Docker usage 7.157 GiB versus cgroup memory.current 25.54 GiB and peak 37.02 GiB, inactive_file 18.38 GiB, anon 4.58 GiB; memory PSI avg10 0, OOM/OOMKill 0, swap I/O, major fault and file-refault deltas 0; CPU busy ~0.18% over 45s, performance governor, CPU split 2808/3900 MHz, system ~34.7 C/GPU ~33 C. Inactive file cache largely accounts for memory reporting differences, NOT proof of PLE RSS/memory leak. P5 recipe remains OBSERVE_ONLY, startup gate disabled and BLOCKED_UNCALIBRATED expected. No arbitrary YSLAB 100 GiB, CPU governor, clock or hard memory limit.

**Current acceptance:** P5 MTP0 text/API and idle telemetry observed; P5 Tools, Vision, MTP2, under-load benchmarks, long stability and canonical promotion NOT_QUALIFIED. P6 read-only Orcarouter↔27B preflight and source-only two-way in-memory Fake-DGX matrix implemented at `21aa6c9`; P5 same-container cgroup fault/oom deltas implemented at `5acf0b1`, both Push/PR CI SUCCESS. Actual P6 switching remains NOT_RUN. P7 Wizard source route present; Proxy/Gateway/OpenWebUI integration acceptance still NOT_RUN. P8 Fake-DGX faults are NOT real automatic recovery; real injection/signoff NOT_RUN/NOT_RELEASED. Preserve vLLM 0.32.0, no SGLang, ONE_ACTIVE_MODEL_ONLY and port 8000; no service mutation, no PR merge.

**Wizard read-only / simulation routes:** `./wizard.sh switch orcarouter-27b preflight --to-model 27b --json`, `./wizard.sh switch orcarouter-27b simulate --from-model orcarouter --to-model 27b --json`, `./wizard.sh operations recovery-acceptance fault-matrix --fake-dgx --json`. None can perform a real switch or release.

[Full documentation audit](HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) · [P5 technical record](P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md)

---

## 2026-11-08 current P5 v2 supersession (document-wide audit)

The complete [document inventory and consistency audit](HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) and [current **P5 QSA+LM-head v2** DGX trial runbook](P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md) supersede earlier P5 source-only / GPU NOT_RUN descriptions and older QSA-only commands. Latest actual DGX **QSA-only** trial failed after 15/17 safetensors shards with missing `lm_head.weight_scale`; the candidate v2 source/CPU CI passed but **v2 GPU load is not proven**. Current v2 adapter is `qwen4exp-qsa62318-lmhead-v032-v2` and its **new** target is `qwen38-orcarouter-qsa62318-lmhead`. Actual current :8000 service state remains unobserved since that failed trial. Previous 27B and failed candidate images/containers are preserved. Never copy the earlier QSA-only `execute` commands without revalidation. vLLM=0.32.0, one active model, :8000; P6/P8 live operations and PR #1 merge remain out of scope. Older sections below remain historical.

---

## 2026-11-08 — P5 source implementation and acceptance update (not GPU released)

P5 source was committed to the existing feature branch and Draft PR #1 as [33adec1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/33adec182e97a8eac0d5584bdf73f1448bdd84f2), with [GitHub Actions 42429745463](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463) **SUCCESS** including the new 20/20 CPU/Fake-DGX tests and `--cpu-only --json` PASS. Additional detailed per-case JSON and profile inspection enhancements require independent follow-up CI.

Implemented source: `recipes/qwen38-orcarouter.runtime.json` (pinned, **unqualified**, launch forbidden), imported YSLAB safetensors/manifest/BF16 PLE audit and immutable MTP overlay code under `scripts/p5_vendor`, donor 3-shard SHA256 / 31 BF16 name audit when local files exist, distinct MTP0/MTP2 candidate recipes, Wizard `p5` and `model orcarouter-flash-next` routes, `scripts/temporary/p5-one-shot-acceptance.sh`. The vendor overlay builder is **not** executable via CLI and no HF asset changes were authorized. Prior Blazux BF16 PLE source markers pass static inspection only; compressed-tensors and MTP2 runtime ABI/quantized lm_head/CUDA graph compatibility in actual vLLM 0.32 remain unqualified.

No DGX command/active-state reread or GPU/API/benchmark/rollback was performed in this session. All live P5 stages are NOT_RUN, `--gpu-trial` permanently BLOCKED until a separate operator approval and verified image/rollback implementation. Preserve 27B and :8000/ONE_ACTIVE_MODEL_ONLY, other models/caches, P3 historical receipts, no P4 deletion/P6 switch/P8 tests or Draft PR merge. New source/runbook: `docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md`.

---

## 2026-11-08 — P5 next-session planning clarified (NO P5 implementation yet)

Operator's confirmed next stage: **P5 Orcarouter Uncensored NVFP4 with direct BF16 PLE / optional 31-tensor BF16 MTP overlay, adapted to Blazux vLLM 0.32 on one DGX Spark**. YSLAB repo is a source reference (vLLM custom 0.1.dev image, default port 18300), not a replacement for the Blazux engine/Wizard/port :8000. New plan `docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md`, audit `docs/HANDOFF-DOCUMENT-AUDIT-P5-20261108.md`, next-chat prompt `handoff/START-NEXT-P5-20261108.md`. Proposed deliverable is one coherent source implementation with a single temporary staged automatic judge; **P5 source implementation and real DGX model/API/benchmark NOT_RUN** at this documentation-only checkpoint. Prior P4-B/C actual DGX read-only PASS/CLOSED stands, real deletion deferred to new P5 incident or P8 consent. P6 actual Orcarouter↔27B switch and P8 release NOT_RUN. P3 closed tests remain closed; do not infer YSLAB benchmark is our runtime measurement.

---

## 2026-11-08 — P4-B/C REAL DGX combined dry-run PASS (source + observation only)

Operator-provided actual DGX terminal: 13 local Fake-DGX tests PASS; `inventory_status=READ_ONLY_INVENTORY_COMPLETE`; `candidate_review.status=READ_ONLY_REVIEW_COMPLETE` / 9 reviewed resources (2 managed containers, 3 HF repos, 4 Docker categories), zero deletion candidates selected; `cleanup_rehearsal.status=DRY_RUN_COMPLETE_RELEASE_GATED` with 2 PASS, 2 DEFERRED_P5_OR_P8, 1 NOT_RELEASED, 1 NOT_EXECUTED; overall `READ_ONLY_DRY_RUN_PASS`. Source CI 902/902 in 41 groups is **independent source-only evidence**. **P4-B/C dry-run acceptance PASS/CLOSED; actual cleanup NOT_RUN, no production release or adapter.** No active model switch, no deletion, no verified reclaimable bytes or approved plan. Detailed [DGX evidence](P4-BC-DGX-READONLY-DRY-RUN-EVIDENCE-20261108.md). P5 actual work and P8 real fault/restore/final acceptance remain not run and require independent authorization.

---

## 2026-11-08 — P4-B/C read-only source implementation and one-shot dry-run

P4-B candidate/reference review + P4-C deletion transaction rehearsal are available from `./wizard.sh storage flash-next dry-run --json` and `bash scripts/temporary/p4-bc-dry-run.sh --json`. 13 Fake-DGX tests integrated into CI: [42403828742](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42403828742) **SUCCESS 902/902 CPU/Fake-DGX across 41 groups**. No new actual DGX P4-B/C result yet. Previous actual P4-A PASS remains established. No live deletion adapter exists (`P4_C_LIVE_EXECUTION_RELEASED=False`); P5 operational issue or P8 acceptance requires separate authorization and an exact-resource adapter/test before real cleanup. Never infer safe reclaim bytes. Reference: `docs/P4-BC-ONE-SHOT-DRY-RUN-20261108.md`.

---
## 2026-11-08 — P4-A actual DGX capacity inventory: READ_ONLY PASS / COMPLETE

Operator ran `./wizard.sh storage flash-next inventory --json` at checkout `a29cd6e`: `READ_ONLY_INVENTORY_COMPLETE`, `issues=[]`, `active_api_verified=true`, 27B active, stopped Flash preserved, Orcarouter model cache present without a container, one GPU and one port-8000 owner, all four Docker capacity categories. File-system total **982,819,848,192 bytes**, free **324,880,961,536 bytes** (~**33.06% free**); both HF cache roots returned the *same* filesystem total/free, so never add those values. Root allocated bytes **267,995,971,584** and **192,507,006,976**; known model-repository allocated sizes: Flash **75,967,504,384**, 27B **21,932,584,960**, Orcarouter **177,686,446,080**. Docker displayed reclaimable: containers **182.7MB**, build cache **2.088MB**, images/volumes **0B**; **not** verified safe reclaimable bytes. See `docs/P4-A-DGX-READONLY-CAPACITY-EVIDENCE-20261108.md` for bounded source, units, and non-additivity caveats. No deletion or service mutation; **P4-B/C NOT_STARTED/NOT_APPROVED**, **P8 NOT_RUN/NOT_RELEASED**. Do not repeat P3-A/B/C/G.

---

## 2026-11-08 — Actual DGX P3-E/F read-only closeout complete; P4-A inventory NEXT

**Observed on actual DGX after fast-forward to `0421b46`:** P3-E `flash_host_assets` status `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`, issues=[], 31,907,813-byte index, 299,845 weight-map entries (400,000 cap), **11 shards** total apparent size **129,771,270,410 bytes**, metadata hashes and mounted template SHA-256 observed. Checkpoint weights not hashed (`large_shard_hashes_verified=false`), pinned published revision bytes not independently verified (`verified_model_revision=false`), reinstall not qualified. P3-F real DGX **168/168 CPU PASS (7 suites)**, `PRODUCTION_LIFECYCLE_RELEASED=false`. Current `qwen38-27b` API `qwen3.8-27b`, host :8000, 8/8 service checks true and `LIVE_SERVICE_VERIFIED`; service-status command does not independently validate GPU/PID ownership. All commands read-only and no service mutation.

**P3 disposition:** A/B/C/G historical actual operator-approved PASS/CLOSED; D independent read-only PASS historically; E source/host-asset metadata handoff COMPLETED but **not** real reinstall; F source/CPU handoff COMPLETED but **not** production lifecycle. **P8 remains owner** of full Flash recipe/install validation, actual reinstall/rollback, deliberately induced failure/automatic recovery and final release (all real work NOT_RUN). No replay, no automatic source launch.

**New operator instruction supersedes prior P4 hold ONLY for read-only P4-A:** implement capacity and current-state inventory via Wizard *before* considering any deletion. P4-B candidates and P4-C cleanup remain not started and unauthorized. Read `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md`. P4-A is SOURCE IMPLEMENTED, DGX CAPACITY OBSERVATION NOT_RUN. Latest P4-A CPU/Fake-DGX CI [42395243458](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42395243458): **887/887 PASS, 40 groups**; no real disk capacities have been measured by the new Wizard in the conversation.

---

## 2026-11-08 — P3 CLOSEOUT ONLY; P4 operator hold; P8 owns live reinstall and recovery

**Operator decision:** Do not start P4. Earlier P4 module/test/workflow code was reverted ([1110681](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/1110681f451bc72470454bbbee1e1d79d6406a1d), [CI 42393129150](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42393129150) SUCCESS). **P4 = NOT_STARTED / OPERATOR_HOLD**. No P4 inventories/cleanup/source implementations.

**P3-E:** Flash FP8 hybrid command/source draft and 299,845-key weight-map observed at DGX; source cap now 400,000 with 128 MiB byte cap and all path/shard safeguards retained ([1a05eb2](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/1a05eb2dfacda960527ba94da544e5f545d8793f), [CI 42392758148](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42392758148) **880/880 CPU PASS, 39 groups**). P3 closeout still needs a current **read-only DGX host-asset rerun** for index/shards/template evidence. Not qualified for canonical reinstall.

**P3-F:** Source Fake-DGX lifecycle/rollback tests pass, `PRODUCTION_LIFECYCLE_RELEASED=False`. P3 closeout asks **read-only `p3_dg_acceptance --cpu-only` 7-suite** local result; last DGX six-suite PASS was 153/153 before added host-asset suite. Actual generic Docker install/recreate/rollback production release is transferred to P8, not declared done. P3-A/B/C/G real PASS/CLOSED, D READ_ONLY_PASS; no replay.

**P8:** Full canonical Flash runtime/env/image/security spec, explicit-approval fresh reinstall, API/benchmark/idempotence/journal, controlled failure/automatic recovery and final Wizard go-live after integration gates. P8 real fault/release NOT_RUN. **Detailed closeout checklist**: `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`.

---

## 2026-11-08 — P3-E actual DGX 30.43 MiB index parsed, weight_map condition under investigation

**Operator read-only evidence:** `python3 -m scripts.manager.flash_host_assets --json` on DGX observed `model.safetensors.index.json` size **31,907,813 bytes (~30.43 MiB)**, below the 128 MiB cap (134,217,728 bytes). The tool reached `PARSE_SHARD_INDEX` and returned `FLASH_SHARD_INDEX_UNQUALIFIED`. Source code combined three cases into one: a missing/non-dict `weight_map`, an empty map, or a map with **more than 100,000 entries**. No count was in that output; **cause within these three cases not yet resolved**. `indexed_shard_count=0` means no shard enumeration, not model damage or missing shards. Pinned command and prepared `-fp8hybrid` view observed; last actual active service remains 27B :8000.

**New source-only diagnosis:** [135f75c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/135f75c8cc652ed63b8508d10fcf5f079dff24ef) adds redacted `index_weight_map_structure` (OBJECT or MISSING_OR_WRONG_TYPE), `index_weight_map_entry_count_observed`, `index_weight_map_entry_limit` and three distinct bounded errors. **100,000 count cap unchanged** until a real count and intended NVFP4/ModelOpt profile are evidenced; no automatic relaxing, downloading, cache modification or Docker operations. GitHub Actions [42392277467](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42392277467) **878/878 CPU/Fake-DGX PASS, 39 groups**, 2 new tests. No hardware run of this new code yet.

**Next DGX read-only action:** `git pull --ff-only origin feature/recipe-wizard-handoff` then `python3 -m scripts.manager.flash_host_assets --json`; evaluate `index_weight_map_entry_count_observed`, `index_weight_map_structure`, `failure_reason_code`. If entry count is above limit, review bounded parser memory and stable ModelOpt index before targeted policy change. Do not assume 31MB index is corrupt or change HF cache. Flash canonical reinstall remains `false`, launch disabled, generic lifecycle unreleased, historical real P3-G PASS/CLOSED, P8 deliberate fault/auto-recovery/final acceptance NOT_RUN.

---

## 2026-11-08 — Actual DGX Flash shard-index cap identified; bounded source fix

**Actual DGX read-only result:** `python3 -m scripts.manager.flash_host_assets --json` returned `BLOCKED`, `failed_stage=READ_SHARD_INDEX`, `failure_reason_code=FILE_EXCEEDS_BOUNDED_READ`. The pinned command identity and `-fp8hybrid` prepared view matched; no model shard contents were examined because `model.safetensors.index.json` exceeded the generic 8 MiB metadata cap. **Actual index byte size is still unknown** and zero recorded shards means unchecked, not missing/corrupt. No DGX GPU or Docker mutation, 27B service remains the last observed active :8000.

**GitHub SOURCE fix:** [56d39e4](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/56d39e4acb5d4e69777372283fe5f8839a16fc7c) uses separate **128 MiB hard cap for index only**, 8 MiB config/tokenizer_config cap, 256 KiB template cap; files are bounded at read time (`read(limit+1)`) to prevent stat/read growth bypass. Adds sanitized numeric `index_file_size_bytes_observed`/`index_file_size_limit_bytes`. Tests cover >8 MiB valid JSON and exceeding index cap. GitHub Actions [42391564016](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391564016) **SUCCESS 876/876 CPU/Fake-DGX, 39 groups** (874 previous + 2 new). This is *not* new DGX asset or GPU validation.

**Next read-only operator step:** `git pull --ff-only origin feature/recipe-wizard-handoff` followed by `python3 -m scripts.manager.flash_host_assets --json`. Observe numeric index size and full staged status. If blocked again, investigate actual `failed_stage` and `failure_reason_code` before altering limits or files. Do **not** change HF caches, start/stop/reinstall/switch models, or inject failures without new explicit consent. Flash canonical reinstall NOT QUALIFIED; P3-F lifecycle release OFF, P3-G real bidirectional PASS historically CLOSED, P8 NOT_RUN.

---

## 2026-11-08 — P3-E real DGX Flash host asset preflight blocked; diagnostic patch/source CI

**Actual operator DGX evidence, no Docker mutation:** `python3 -m scripts.manager.flash_host_assets --json` returned `status=BLOCKED`, issue `FLASH_HOST_ASSET_PREFLIGHT:ValueError`, `legacy_hf_bind_writable=true`, `indexed_shard_count=0`, `metadata_sha256={}`, `template_sha256=null`, `verified_model_revision=true`. This only establishes that the **old observer** advanced past pinned command/env/cache bind, then raised a ValueError during an unidentified local-file validation step. Neither zero shards nor `verified_model_revision=true` proves a missing model or verified revision bytes. **No user-provided evidence of broken inference or failed reinstall.**

**Source fix, not live DGX proof:** [9beb1d3](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/9beb1d3f73675ac4a22daedfc2167b380742305c) adds allowlisted `failed_stage`, `failure_reason_code`, `pinned_command_identity_matched`, `prepared_view_path_observed`, and stops falsely setting `verified_model_revision=true` from a directory name alone. Private exception messages/path/env values are never emitted. Tests cover metadata cap, malformed index, empty/missing/escaped marker, secret exception redaction. GitHub Actions [42391221418](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391221418) **SUCCESS: 874/874 CPU/Fake-DGX tests across 39 groups** (previous 870 + 4). Real DGX did not run this patch yet.

**Next safe operator command:** `git pull --ff-only origin feature/recipe-wizard-handoff`; then `python3 -m scripts.manager.flash_host_assets --json`. Inspect only redacted `failed_stage` and `failure_reason_code`. No cache repairs, container recreation, GPU activity or permissions escalation should follow from this result without separate evidence/approval. Flash canonical reinstall remains unqualified, lifecycle release disabled, historic P3-G real PASS/CLOSED and P8 NOT_RUN; preserve 27B at :8000.

---

## 2026-11-08 — P3-D latest current PID proof and P3-E/F source follow-up

Operator's latest DGX read-only `--sudo-ss` P3-D/E/F/G output: **P3-D READ_ONLY_PASS**, independently attributed docker-proxy IPv4 PID `2560693` and IPv6 PID `2560708`, GPU PID `2560905`, no detected GPU ownership conflict. **P3-E DRAFT_REVIEW_REQUIRED** despite `cmd_normalized=true` using `FLASH_FP8HYBRID_READ_ONLY_V1`, `cmd_normalization_error=null`, draft-field `issues=[]`, because canonical reinstall remains unqualified. **P3-F 153/153 DGX-local CPU PASS**. P3-G preview in this particular runner does not invalidate previously completed real bidirectional G. `blocked_stages=[]` with total `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` is expected.

GitHub source: [03cbe4c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/03cbe4cc45a750322c4f99616c85f1061f7b2288), [2b44ccc](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/2b44ccc0237fa34742e28608ad089cb3ca90fe55), and [8e8fcec](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/8e8fcec5acb280e01445a2bd773fc9f4ecedf2f6). Source-only CI [42390619936](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42390619936): **870/870 PASS, 39 groups**, including 5 new Flash host asset tests. **No acceptance promotion**: P3-D latest READ_ONLY_PASS on real DGX, P3-E still source draft/no canonical reinstall, P3-F local 153 CPU test PASS but production executor blocked; P3-G prior independent real both-direction transfer PASS/CLOSED. P8 deliberate fault/recovery and final go-live NOT_RUN. The new host asset command has not yet been run on DGX and must not mark E as qualified from CI alone.

---

## Source-only addendum — 2026-11-08 (P3-E/F hardening)

Source change: [d68106a](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d68106a24c4c6071acff7a4d98d74e04c6ecbfe1). Actual GitHub Actions [42386939625](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42386939625): **862/862 PASS in 38 CPU/Fake-DGX groups** (856 baseline + 6 new). This is **SOURCE-ONLY**; no fresh DGX test or service change. Full scope: `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

Acceptance milestones **unchanged**: P3-E `DRAFT_REVIEW_REQUIRED`, no qualified Flash canonical reinstall; P3-F `SOURCE_CPU_PASS_NOT_RELEASED`, generic lifecycle execution blocked; P3-G `REAL BIDIRECTIONAL PASS / CLOSED` from original operator DGX receipts; P8 `NOT_RUN / NOT_RELEASED`. No new DGX runtime/rollback/benchmark measurement or production release.

---

## 2026-11-07 — AUDITED P3-A–G; G CLOSED, FAILURE/FINAL RELEASE REASSIGNED TO P8

**Latest acceptance audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`. Historical **A/B/C REAL PASS/CLOSED** (Flash→27B, 27B→Flash, Flash→27B; immutable original receipts); **D REAL READ_ONLY_PASS** for single GPU and independently attributed IPv4/IPv6 host :8000 process ownership (measured before most recent roundtrip); **E DRAFT_REVIEW_REQUIRED** despite confirmed NVIDIA Flash `-fp8hybrid` source variant and source-draft documented-field match because **canonical reinstall-qualified Flash recipe is NOT registered or real tested**; **F 144/144 local Fake-DGX/CPU PASS** with production lifecycle release still OFF; **G REAL BIDIRECTIONAL PASS/CLOSED**, two separately authorized 27B→Flash→27B live transfers, current last observed 27B API `qwen3.8-27b`, `diff=[]`, journal `VERIFIED/COMMITTED` 28 events. **P3-A~G aggregate is NOT fully complete because E remains OPEN and F is only source-qualified.** Don't replay A/B/C/G. The operator reclassified deliberate fault injection, automatic source restoration and final production/UX signoff exclusively as **P8**, which is `NOT_RUN/NOT_RELEASED` and does not block G's closed successful-transfer scope. P7 remains component integration only. Source-only CI after P8 registration: [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS, **856/856 CPU tests / 38 groups**; that does not evidence new DGX runtime results.

P3-E remains the sole currently open *canonical reinstall qualification* among A-G; P3-F CPU suite accepted as source-only scope but generic lifecycle remains locked pending distinct operational authorization. P8 final Go/No-Go and recovery must not be backfilled from G.

---

# P1–P8 Wizard acceptance status — canonical milestone scope (2026-11-07)

> This document supersedes phase **scope** and status headings in the older historical `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md`; it does **not** alter immutable execution receipts or rewrite historical evidence. All live statuses below reflect the last **operator-provided** DGX output, not a new probe from GitHub.

## Scope and current status

| Phase | Acceptance objective | Current evidence classification |
| --- | --- | --- |
| P1 | NVIDIA Flash-Next source/runtime/API/benchmark | Prior real DGX P1 checks passed; refer to prior immutable records |
| P2 | NVIDIA 27B pinned download/start/API/native tool calling/benchmark | Prior real DGX P2 checks passed; canonical 27B recipe SHA preserved |
| P3-A/B/C | Original one-off stage sequence; exact receipts | **REAL PASS / CLOSED** |
| P3-D | Exclusive GPU process and host port-8000 PID provenance | **READ_ONLY_PASS** on real DGX with explicitly opted-in `sudo -n ss` |
| P3-E | Flash runtime provenance, canonical reinstall-ready recipe | **DRAFT_REVIEW_REQUIRED**: pinned `-fp8hybrid` snapshot and documented draft fields matched, but canonical reinstall unqualified |
| P3-F | Generic lifecycle operations' CPU/Fake-DGX source gates | **SOURCE_CPU_PASS_NOT_RELEASED**; last supplied local batch 144/144 PASS |
| **P3-G** | **Real 27B↔Flash-Next successful independent bidirectional operating transfers, API/journal and canonical recipe postchecks** | **REAL PASS / CLOSED** — two separate DGX TTY-authorized switches and reverse 27B `diff=[]` |
| P4 | Optional Flash storage cleanup/reinstall disposition | Optional; NOT_APPLICABLE may be chosen if no need for deletion |
| P5 | Orcarouter deployment/API/bench | PENDING |
| P6 | Orcarouter↔27B real transfer | PENDING |
| **P7** | **Service/proxy/gateway integration and numerical/CI qualification** | PENDING; **does not include final signoff** |
| **P8** | **Deliberate controlled fault injection, automatic source restoration real verification, final operating UX/security/production release signoff** | **NOT_RUN / NOT_RELEASED** |

## Real P3-G bidirectional evidence

1. `27b → flash-next`: independent execution SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`, operator `PASS`, Flash served API `qwen3.8-flash-next`, journal `VERIFIED/COMMITTED`, 21 events.
2. `flash-next → 27b`: independent execution SHA `a909a1470760613b3d8e1f588dada06a41205ceac7e07c5ff464eac01884ed8b`, operator `PASS`, 27B served API `qwen3.8-27b`, journal `VERIFIED/COMMITTED`, 28 events. 27B canonical recipe diff `[]`, issues `[]`. Source: `docs/P3-G-LIVE-BIDIRECTIONAL-SWITCH-PASS-20261107.md`.

**Current last-observed running model**: NVIDIA 27B, host port 8000; one managed model according to manifest-led service check. The `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` of the basic status command mean that command doesn't independently audit those properties, not that collisions were observed.

**P3-G completion is limited to successful two-way transfers**, not claim of fault-tolerance under injected failure. P3-E Flash reinstall recipe qualification, P3-F general lifecycle/production dispatch and P8 release remain independently pending. No forced error, deletion, image/cache purge or irreversible service change is authorized by phase renumbering.

## P8 safety contract

P8-A fault matrix and live bounds; P8-B Fake-DGX recovery/journal and negative tests; P8-C independently approved DGX bounded failure and verified **automatic source restoration**; P8-D full Wizard final integrated operations/UX/security and go-live signoff. Details `docs/P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md`.

A successful *source-only* P8 plan or Fake-DGX tests **cannot** mark P8-C or P8-D PASS, cannot set `production_released=true`, and cannot dispatch Docker/GPU fault injection. The new Wizard P8 menu is deliberately `INTERFACE_ONLY / BLOCKED`.

## Handoff rule

Future work on P4–P7 may proceed without reopening P3-G. P8 remains the dedicated safety/end-to-end acceptance milestone. Preserve old DGX switch receipts, preserve model files/HF cache and vLLM 0.32/API 8000/ONE_ACTIVE_MODEL_ONLY rules; do not use SGLang. PR #1 stays Draft/unmerged until a separate release decision.
