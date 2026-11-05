## E-20261106-P2-DGX-STATIC — exact pinned 27B CPU source proof from operator

Operator supplied actual DGX outputs (2026-11-06 KST):
1. Exact `nvidia/Qwen3.8-27B-NVFP4` revision `482ca0f3832238542f8f5295dde86b5f22711d80` source found. Quantization audit `MIXED_PRECISION`, `producer=modelopt`, `layer_algorithms={"FP8":208,"NVFP4":193}`, `layer_count=401`, `issues=[]`, `mixed_fp8_nvfp4_metadata=true`, `runtime_qualified=false`.
2. `./scripts/temporary/p2-27b-image-audit.sh --plan`: `CPU_ONLY_PROBE_PLAN`, local image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, no GPU/network/port mutation.
3. `--execute-cpu-only`: `SOURCE_SURFACES_PRESENT_UNQUALIFIED`, image registry Qwen3.5 true, Qwen3.5 class true, ModelOpt FP8/NVFP4/mixed algorithm literals true, mixed config classes true; all three Python source modules parsed. `executed_gpu=false`, `gpu_verified=false`, `runtime_qualified=false`, `launch_authorized=false`.
4. User reported git pull 13 changed files, no service stop/restart, and old Flash-Next status `observed_model=flash-next`, `:8000` listening from live preflight. Full 27B runtime remains `BLOCKED` as designed.

**SOURCE CI:** GitHub commit `ae4490d66d9c1b9306435165a9821253ee6f38d7`, Actions run `42110115101`: SUCCESS **315/315 CPU tests PASS**. Added dedicated non-executable 27B launch argv and API identity/baseline checks, not a GPU run. Initial `234a8e4a` CI had one failing *test-only placeholder assertion*, fixed by `ae4490d6`; latest success supersedes the first failure.

---

## E-20261106-P2-QUANT-SOURCE-CI — Pinned ModelOpt audit unit tests

GitHub `cd63f25f0bf7282ea06dbb13c3499798394322b0`, Actions `42065472163` — **303/303 CPU tests PASS**, all 15 test batches and deliberately unqualified candidate-recipe check SUCCESS. The added P2 audit uses `hf_quant_config.json` in exact NVIDIA immutable snapshot and reports layer algorithm counts; malformed/oversize/unknown algorithms fail closed. Neither the new quantization fields nor static image source checks have been run on DGX yet; GPU/27B loader/bench/API/transition and recovery **NOT_RUN**. The previous DGX `status --inspect-runtime` result remains a **config-only** observation, not a per-layer audit.

---

## E-20261106-P2-READONLY — DGX real NVIDIA 27B qualification observation

- Operator ran `git pull --ff-only origin feature/recipe-wizard-handoff`: fast-forward `e99914c..edf0968`, checkout clean as reported.
- Real DGX `./wizard.sh model 27b status --inspect-runtime --json`: source candidate **present** at full SHA `482ca0f3832238542f8f5295dde86b5f22711d80`, architecture `Qwen3_5ForConditionalGeneration`, model type `qwen3_5`, quant method `modelopt`, context 262144, vision config yes, host aarch64; Docker image `qwen38-flash-dgx:v0.32` image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, Linux/ARM64, `qwen38.base=v0.32`, `repo_digests=[]`.
- Observed original Flash-Next active on host port 8000; NVIDIA download container no longer running. No GPU residency validation (`gpu_verified=false`), actual loader/model start/27B API/benchmark/rollback `NOT_RUN`.
- Read-only preflight correctly BLOCKED: `VLLM032_27B_LOADER_NOT_QUALIFIED`, `MODEL_OPT_MIXED_NVFP4_FP8_GPU_NOT_QUALIFIED`, `IMAGE_DIGEST_NOT_PINNED_IN_VALIDATED_RECIPE`, `GPU_MEMORY_AND_CONTEXT_PROFILE_UNVERIFIED`, `27B_START_AND_FLASH_NEXT_ROLLBACK_NOT_VERIFIED`, `ACTIVE_MODEL_REQUIRES_SEPARATE_TRANSITION_APPROVAL`.
- Public vLLM 0.32.0 supported models list `Qwen3_5ForConditionalGeneration` and versioned ModelOpt code provides NVFP4+FP8 mixed config. **Public upstream != local patched image**: image static audit developed but actual DGX execution of image source probe still `NOT_RUN`. See https://docs.vllm.ai/en/v0.32.0/models/supported_models/ and https://docs.vllm.ai/en/v0.32.0/api/vllm/model_executor/layers/quantization/modelopt/ .
- **CI on `acf5d64a37929811af9e2da33fa1b30de5e38cb0`: SUCCESS, 294/294 CPU tests PASS.** No GPU/API/inference actions performed by GitHub development.

---

## E-20261106-P2-DOWNLOAD — NVIDIA pinned download PASS (operator DGX evidence)

- Command: `./wizard.sh model 27b download --guided`; approval ID `e7d3ee776b65c3c5e3395fbeff5d0d739ef432028c030df8d604578412570c49`.
- `Fetching 19 files: 100%` (19/19); process exit 0; final `status=PASS`, `executed=true`, `scope=DGX_NETWORK_DISK`, `checkpoint_status=SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, `issues=[]`.
- Repo/revision: `nvidia/Qwen3.8-27B-NVFP4` / `482ca0f3832238542f8f5295dde86b5f22711d80`.
- Evidence: `/home/inlc/.local/state/blazux-wizard/p2/evidence/20261105T150433Z-bd8cf46ef5.json`.
- Independent weight-shard cryptographic rehash **NOT_RUN**; loader/GB10/GPU/API/benchmark/rollback **NOT_RUN**. `gpu_verified=false`.
- GitHub-only new preflight/test code: **SOURCE implemented; CI pending final HEAD**. No DGX source update or GPU operations by this coding session. This record supersedes older transfer 84% observations.

---## 2026-11-06 — Complete Wizard SOURCE; actual runtime remains gated

- GitHub SOURCE: `wizard/console.py` full three-level operator UI; `wizard/workflow.py` consistent P1/P2/P5 model action catalog; `wizard/roadmap.py` release evidence view; `scripts/manager/service_logs.py` bounded read-only log tail. Existing `scripts/manager/p1_wizard.py` and `scripts/manager/p2_27b_download.py` preserved. Added test suites `test_wizard_workflow_cpu.py`, `test_wizard_roadmap_cpu.py`, `test_service_logs_cpu.py`; no real Docker/GPU/network operations executed from GitHub code edits.
- A CPU regression exposed a bypass where P1 guarded start dispatch ignored its own capability BLOCKED result. Fixed by requiring `GUARDED_P1` and preventing P1 quickstart when 27B/Orcarouter is active; latest CI must show PASS before releasing source.
- Last DGX runtime evidence remains operator-reported NVIDIA 27B download started at `Fetching 19 files: 84%`, NOT_VERIFIED complete. No P2 NVFP4 loader, GPU acceptance, P3/P6 switch, P4 deletion, Orcarouter runtime or P7 release PASS evidence exists in this turn.

## 2026-11-05 — Service health and transition preview CPU evidence

- SOURCE: local :8000 GET-only health/model-ID observer, with no inference POST, no Docker mutation, fixed request/size/time bounds; source-only stop-old → port release → new start → API verify → rollback preview, always BLOCKED without verified executor.
- CPU mock tests cover correct served model ID, ID mismatch, bad or oversized response, unqualified Orcarouter, unknown service, stop-before-start and rollback invariants, and no hidden GPU/Docker actions.
- Actual DGX service health action, 27B model start/switch and rollback: **NOT_RUN**. Source CI status must be confirmed at final HEAD. Last real DGX transfer evidence still only `Fetching 19 files: 84%`.

## 2026-11-05 — First DGX NVIDIA 27B transfer and unified Wizard source

- **Actual DGX operator terminal:** `./wizard.sh model 27b download --guided` with exact approved plan id `e7d3ee776b65c3c5e3395fbeff5d0d739ef432028c030df8d604578412570c49`, `Fetching 19 files: 84% (16/19)`. Scope DGX NETWORK/DISK, actual transfer **STARTED**; completion, source checksum/index audit and outcome evidence **NOT_OBSERVED**. Existing `qwen38-flash` still Up with external host :8000 at initial plan.
- GitHub SOURCE: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`, `wizard/quickstart.py`, three-choice root TTY menu, live `download_running` manifest, unqualified Orcarouter policy, new CPU test matrix and legacy CLI compatibility. This is **SOURCE/CI evidence only**, no DGX UI update or GPU execution.
- Final HEAD CI must be checked after all documentation and tests. Old P1 bounded verify/benchmark PASS remains historical and does not imply 27B qualification.

## 2026-11-05 — Guided NVIDIA download refusal evidence and correction

- Actual DGX console: operator supplied the full Wizard-computed plan ID `b190c936072038bc55c14c62dd2f9a63e3ddbf5c2e1ebbf0d1710551a7ec21ce`. Wizard returned `status=BLOCKED`, `executed=false`, `issues=[PREFLIGHT_CHANGED_REPLAN_REQUIRED]`. There is **no actual NVIDIA download execution evidence**.
- GitHub source analysis: live preflight hashed mutable `free_inodes`, free GiB floor and human Docker status. The lock/state directory is created between plan generation and the second preflight, so drift can arise without a meaningful safety change.
- SOURCE remedy: stable `_approval_facts` fingerprint; retain dynamic safety gates and ten-minute approval period; add regression tests. CPU/CI PASS verdict must be checked at final HEAD. DGX second attempt `NOT_RUN`.

## 2026-11-05 — NVIDIA 27B pinned acquisition SOURCE and single-model policy

- Authoritative public checkpoint: `nvidia/Qwen3.8-27B-NVFP4`, immutable `482ca0f3832238542f8f5295dde86b5f22711d80`, 3 indexed safetensors shards (~21.9GB): https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/482ca0f3832238542f8f5295dde86b5f22711d80 .
- Prior actual DGX user-provided inventory (before current code): `NO_PINNED_LOCAL_SNAPSHOT` for NVIDIA 27B. No evidence of downloaded NVIDIA checkpoint or running 27B service yet.
- New GitHub SOURCE: guarded no-GPU, no-port Wizard download, pinned-without-refs scanner, single-model service policy, read-only observed manifest and transition journal primitives. Actual DGX download/GPU/API 27B/start-stop-switch: **NOT_RUN**. The runtime approval boundary remains independent of download approval.
- Latest CPU CI should be checked against final commit before claiming PASS.

## 2026-11-05 — NVIDIA P2 cache and service-menu evidence

- DGX user console: `nvidia/Qwen3.8-27B-NVFP4`, `refs.main=null`, `local_revision=null`, `indexed_shard_count=0`, `incomplete_blob_files=0`, `source_files_present=false`, `issues=[NO_PINNED_LOCAL_SNAPSHOT]`. Scope: read-only `~/.cache/huggingface` only; actual download NOT_RUN.
- New GitHub SOURCE: Wizard `service manager` module and `model 27b plan --for-action download` fail-closed action. CI verdict requires latest-HEAD check. No DGX service, download, GPU, benchmark execution.

## 2026-11-05 — P2 model selection and provenance split

**DGX observation (historical, not NVIDIA):** user-supplied Wizard read-only inventory for `RadixArk/Qwen3.8-27B-NVFP4` at revision `52d1adc5f38aa5ebf099c29ed7025ba34cfbb854`; 3/3 indexed shards, 0 incomplete transfers, `issues=[]`. **Current chosen P2 model:** `nvidia/Qwen3.8-27B-NVFP4`; NVIDIA cache inspection, immutable SHA, vLLM 0.32 GPU operation and benchmark remain NOT_RUN. Public NVIDIA model card lists vLLM on GB300 TP4, not a qualification of this single Spark GB10. https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4

## 2026-11-05 P2 — config audit SOURCE evidence

- GitHub-connected source patch: `scripts/manager/p2_27b_inventory.py`, `tests/test_p2_27b_inventory_cpu.py` on `feature/recipe-wizard-handoff`.
- Evidence level: **SOURCE committed**. CI at new HEAD requires separate run confirmation; no local DGX, GPU, Docker, network download or model service test was executed.
- Previous P1 operator report remains valid with its original dated scope. No P2 runtime qualification inferred from candidate checkpoint metadata.

# Evidence ledger — observed facts and test reports

## E-20261105-16 — P1 baseline, advanced tests, and bounded GPU bench PASS

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

## E-20261105-17 — 27B source-only cache discovery

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

**Source/CPU**: code/testing/CI in this branch, independent of DGX GPU acceptance. No 27B GPU benchmark, install, live switch, or production rollout observed.


Use an append-only entry for every meaningful result. Never substitute README claims or previous chats for locally reproduced tests.

## Entry template

| Field | Value |
|---|---|
| ID / KST | `E-YYYYMMDD-NN` / timestamp |
| Model / recipe / revision | full id + immutable revision |
| Git HEAD / branch | exact actual SHA and branch |
| Runtime image / host | immutable digest, vLLM version, GPU/driver/OS |
| Scope | SOURCE / CPU / CI / GPU / API / SWITCH / RELEASE |
| Exact invocation | command/environment; redact secrets |
| Inputs | test names, prompt/seed hashes, dataset scope |
| Result | PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE |
| Artifacts | paths/URLs/digests |
| Limits | scope, caveats, unresolved mismatches |

## E-20261104-01 — source-only planning baseline

- **Scope:** SOURCE / GitHub metadata and public source inspection, **not** GPU.
- **Repo:** `kjlee-inlct/qwen3.8-Flash-DGX`.
- **Source commit:** `blazux/qwen3.8-Flash-DGX@b0aa8b77604139557169387b2fa8386355d8b651`; user fork main same at branch creation.
- **Source observations:** `flash` and `profiles` cover NVIDIA and RadixArk Flash-Next; `scripts/serve.sh` removes container matching `NAME`; `feature/orcarouter-bf16-adapter` already holds a design doc; aphex3k 27B recipe uses SGLang, **not** local vLLM 0.32 proof.
- **Result:** `PASS_SOURCE_INSPECTION` for cited facts; `NOT_RUN` for CPU tests, CI, DGX runtime/benchmark.
- **Artifacts:** [Blazux source](https://github.com/blazux/qwen3.8-Flash-DGX/tree/b0aa8b77604139557169387b2fa8386355d8b651), [Orcarouter parallel branch design](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/blob/feature/orcarouter-bf16-adapter/docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md), [27B external reference](https://github.com/aphex3k/Qwen3.8-27B-on-DGX-Spark).
- **Limits:** No current disk, container, memory or actual 27B vLLM evidence.

## E-20261104-02 — new planning branch and documentation

- **Scope:** GitHub SOURCE / documentation-only.
- **Branch base:** `feature/recipe-wizard-handoff` created from `b0aa8b77604139557169387b2fa8386355d8b651`.
- **Result:** `PASS_SOURCE/GITHUB`: 10-file commit `76cd8dae16b0f34e47c353b56b6e9dbcc5fcde25` confirmed by branch readback and compare with `main`; draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) opened against `main`, unmerged. `NO_CHECKS_REPORTED` for that original commit (0 check-runs, 0 PR workflow runs). **No CPU, CI, GPU or service tests run.** This entry does not qualify any runtime.
- **Artifacts:** `docs/MODEL-RECIPE-WIZARD-PLAN.md`, `docs/MANIFEST-CONTRACTS.md`, `handoff/*`.
- **Limits:** Manifest examples, wizard commands and state machines are designs, not implemented software.

## E-20261104-03 — N1 isolated CPU source contract check

- **Scope:** SOURCE/CPU (2026-11-04 KST). Executed in a separate CPU container, **not DGX**. Previous fork HEAD read: feature/recipe-wizard-handoff@07b0e3d49b387ecc29c00e3f5338e4e7065bcc27; new commit must be verified independently.
- **Tools:** Python 3, PyYAML 6.0.3, jsonschema 4.26.0; no vLLM/CUDA/Docker.
- **Exact commands:** python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -q => **15 PASS**; python3 -m scripts.manager.manifest validate recipes/qwen38-27b.candidate.yaml => expected **FAIL**, exit 2, 6 invalid/unverified fields; same command with tests/fixtures/recipe-valid.synthetic.yaml => schema **PASS**, exit 0, launch_authorized=false.
- **Artifacts:** schemas/recipe.schema.json; scripts/manager/manifest.py; recipes/qwen38-27b.candidate.yaml; tests/test_manager_manifest_cpu.py; tests/fixtures/recipe-valid.synthetic.yaml.
- **Limits:** synthetic a/b/c-character SHA values are fake fixture data; schema PASS is not repository existence/image runtime compatibility evidence. CI awaits new PR SHA observation. GPU/API/SWITCH/RELEASE NOT_RUN. No current DGX state observed.

## E-20261105-01 — Flash-Next 8000 default/N2 inventory source implementation

- **Scope:** SOURCE/CPU TEST CODE. Old fork HEAD was `bf453aea425c0d9136d67ac003a4f296a0a96885`; GitHub commit/CI outcome must be re-read after updating branch.
- **Change:** default Blazux NVIDIA Flash-Next, hybrid/YaRN/MTP2, exposed :8000/v1, served `qwen3.8-flash-next`; refactored unsafe implicit Docker container replacement into fail-on-name-exists. Removed outdated schema hard-coding of port 8000 and historic Orcarouter name.
- **Added read-only inspections:** `python3 -m scripts.manager.inventory doctor --dry-run` and `plan --dry-run` via Wizard. Commands collect local Docker/ss/disk/HF cache metadata; never execute model/Docker mutation.
- **New tests:** `tests/test_manager_inventory_cpu.py` (10 synthetic scenarios), `tests/test_flash_launch.py` (+4 cases), `tests/test_manager_manifest_cpu.py` updated old port expectations. GitHub CPU workflow expanded; **CI_NOT_YET_OBSERVED** in this source entry.
- **DGX:** user reports old services removed, **NOT_INDEPENDENTLY_VERIFIED**. No model/download/GPU/API/bench, no new runtime measured; required source/model image revisions still to be pinned for release.

## E-20261105-02 — CI failure and corrective script mode

- **Scope:** CI, commit `7e8f4a109a04c130a5dba0d73e3ece0881d85478`.
- **Observed:** GitHub Actions jobs [push failure](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41947918546/job/126984612955) and [PR run](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41947924748/job/126984632242) reported manifest **15/15 PASS**, N2 Inventory **10/10 PASS** and launch **4 FAIL/13**. Exact failures: `test_capable_dflash_launch`, `test_default_options_remain_empty`, `test_default_port_8000_and_next_flash_model_id`, `test_docker_options_reach_docker_not_vllm`; shell exit 126.
- **Root cause:** GitHub tree update accidentally wrote executable shell paths `flash` and `scripts/serve.sh` as `100644`. Root Git tree confirmed incorrect modes; not a demonstrated model/runtime bug. Correction restores `100755`; actual CI rerun must be independently checked. No failure history removed.
- **DGX:** NOT_RUN, no status observed.

## E-20261105-03 — Confirmed Wizard-first P1–P7 roadmap (decision, not test)

- **Scope:** USER_DECISION / DOCUMENTATION. The user reconfirmed sequential Wizard execution for all milestones. Evidence is the user request; not runtime testing.
- **Last independently verified source CI:** `feature/recipe-wizard-handoff@017319a5394155797bcb7e5c933ccef35080d669`; [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41948116286/job/126985272415) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41948122438/job/126985292140) **SUCCESS** (15 manifest + 10 inventory + 13 launch + 1 script modes = 39/39 tests each). Historical `7e8f4a1` four test failures remain recorded in E-20261105-02.
- **Current deliverable:** documentation-only alignment, no new source-test execution; CI for resulting documentation HEAD to be read back. **GPU/API/BENCH/SWITCH/RELEASE = NOT_RUN**; live DGX and :8000 occupancy **NOT_OBSERVED**.
- **Boundary:** Roadmap confirmation does not itself approve GPU loading or model/cache deletion. P4 is conditional with exact approval; `SKIPPED_NOT_NEEDED` permitted.

## E-20261105-05 — DGX terminal log supplied by operator

- **Source/scope:** user-attached terminal output, 2026-11-05; `USER_SUPPLIED_DGX_LOG`, **not direct SSH observation**. `wizard/00-doctor.sh`, `wizard/10-plan.sh` reported `collision_free=true`, host :8000 unoccupied, no `qwen38-flash` container, 580,134,281,216 bytes free. OpenWebUI and Portainer were still running. `./flash doctor default` showed aarch64 GB10, unified memory 121 GiB total /117 GiB available, Docker 29.6.2.
- `./flash setup default` image build **FINISHED**, `qwen38-flash-dgx:v0.32` image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, then resumed download for `nvidia/Qwen3.8-Flash-Next-NVFP4`; last output **9/25 (36%)**. **No proof** download/hybrid/serve/API/bench complete.
- The shell already received `./flash serve default`, `./flash wait`, `./flash test` sequentially after setup. These may run without any additional assistant action once setup finishes. Do not start a second `setup`, `serve`, change the active worktree, or remove any assets.
- Observation is time-bounded; fresh current status remains required.

## E-20261105-06 — P1 Wizard code + CPU mock suite

- **Scope:** SOURCE (GitHub commit `c625a49276272e90d19ab6367f580a0230754890`), CI verified: 2/2 SUCCESS, 80/80 CPU tests each. Added `p1_assets.py` fail-closed snapshot/index and symlink audit, `p1_wizard.py` live plan/approval/action runner, `p1_bench.py` SSE benchmark, `wizard/p1.sh` shell entry, and `tests/test_p1_*_cpu.py` fake backends. Extended GitHub workflow: 41 new P1 CPU tests and 39 baseline CPU tests PASSED in each of two jobs; [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41959325678/job/127021656282) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41959334560/job/127021682353).
- **Limit:** No DGX Wizard operation performed by assistant; no new GPU/API/benchmark results claimed. Plans require complete assets, live image identity, container/port checks and fresh exact approval, and cannot automatically download/clean up/switch.

## E-20261105-07 — Modular P1–P7 Wizard CLI source/CI

- **GitHub SOURCE commit:** `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`, branch `feature/recipe-wizard-handoff`; [CI push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961358317/job/127028222400) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961362251/job/127028234413), both **SUCCESS**. Per job: 15 manifest + 10 inventory + 13 legacy Flash + 1 shell mode + 41 P1 + 21 routing = **101/101 CPU PASS**.
- **Contract:** `./wizard.sh list --json`; `./wizard.sh p1 status --json`; `./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json`; `./wizard.sh --stage p3 --action switch ... --json`. P2–P7 are **INTERFACE_ONLY / runtime NOT_RUN / operations_enabled=false**; execute/approval arguments return BLOCKED. P1 delegates to existing approval-protected core.
- **Follow-up:** P1 JSON-guided handling improvement and 2 tests submitted in a separate commit; verify updated CI independently. **No assistant DGX command, GPU/API/BENCH, switch, cache cleanup or Docker operation**. Prior operator-supplied download and queued commands not interrupted.

## E-20261105-08 — Final modular Wizard CLI source CI

- **Source/docs HEAD tested:** `feature/recipe-wizard-handoff@43f5131b63b7e3f20cde0c409b3ddd672ddb349b`. Two GitHub Actions `manifest` checks completed **SUCCESS**: [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961837000/job/127029761586) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961842431/job/127029780582).
- **Observed CI logs per job:** 15 manifest PASS + 10 Inventory PASS + 13 legacy Flash PASS + 1 executable mode PASS + 41 P1 CPU PASS + 23 Wizard router PASS = **103/103 CPU tests**. P1 guided mode in JSON returns BLOCKED without prompting and normal TTY path remains supported. Unsupported stages and fake approvals are blocked.
- **Runtime boundaries:** all code tests are GitHub-hosted CPU-only mocks; **DGX Wizard GPU/API/BENCH/SWITCH/RELEASE NOT_RUN**, no new images/weights served and no cleanup. P2–P7 are non-executable planning interfaces. Previous user-supplied DGX image-build/download log is time bounded and not superseded by CI results.

## E-20261105-09 — Domain-grouped Wizard refactor and compatibility CI

- **Source commit:** `571e1c204d76bcb66b9e02cb1315ac775013a130` on `feature/recipe-wizard-handoff`. GitHub Actions [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41967161260/job/127046714703) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41967169194/job/127046737309) both **SUCCESS**.
- **CPU test logs per job:** 15 manifest + 10 inventory + 13 legacy Flash + 1 permission + 41 P1 + 32 grouped CLI router = **112/112 PASS**. Newly verified: grouped catalog, four domain categories, P1/P2/P5 model routes, P3/P6 switch routes, legacy stage aliases, no-TTY/JSON safety and fail-closed future stages.
- **Boundaries:** `SOURCE/CI PASS` only. **DGX GPU/API/BENCH/SWITCH/CLEANUP/RELEASE=NOT_RUN** for this refactor; current live download/port status not re-probed, no user-owned shell process modified. P2–P7 are `INTERFACE_ONLY` and execution is blocked.

## E-20261105-10 — Temporary P1 operator bundle source/CI boundary

- **Scope:** SOURCE/CPU/CI pending exact new commit; `scripts/temporary/p1-post-download.sh` shell wrapper, `p1_post_download.py` Python coordinator, `scripts/temporary/README.md`, `tests/test_p1_temporary_cpu.py`; CI workflow extended with fake backend tests and shell/executable mode checks.
- **Safety design:** only read-only diagnostics by default; per-action plan hash validated through current P1 Wizard; terminal consent separate for verify and benchmark, no benchmark without verify PASS, process/branch/dirty-tree guards; JSON report outside Git and model cache with 0600 permissions, no automatic model mutation.
- **Evidence outstanding:** new GitHub Actions results and actual DGX operator log. User's prior download/setup chain must be confirmed finished **before** using the wrapper. No assistant-executed DGX/GPU/API/benchmark, no service changes or cache deletion; `DGX=NOT_RUN` until operator returns evidence.

## E-20261105-11 — P1 temporary operator bundle CPU CI accepted

- **Code HEAD:** `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b`, `feature/recipe-wizard-handoff`. GitHub Actions [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970955588/job/127058833280) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970960007/job/127058848658), both **SUCCESS**: 131 unique CPU tests each (15 manifest, 10 inventory, 13 launch, 1 script mode, 60 P1 including 19 temporary tests, 32 router).
- **Tested behaviors (mock DGX):** safe read-only inspection; no setup/Git reset/Docker rm; independent live Wizard plan approval; blocked/dirty/wrong-branch/active-setup refusal; mid-run race prevention; benchmark only after verify PASS; restricted JSON artifact outside Git/HF cache.
- **Real DGX:** `NOT_RUN_BY_ASSISTANT`. No GPU/API/benchmark results, operator's queued `flash setup/serve/wait/test` completion still not observed and must be confirmed before `git pull`/wrapper.

## E-20261105-12 — DGX operator report: checkpoint download finished, Wizard blocked

- **Source:** user-provided DGX terminal output and operator clarification, 2026-11-05. **Evidence scope:** USER-REPORTED download complete; console wrapper evidence for `git pull` and `bash scripts/temporary/p1-post-download.sh`; not assistant SSH and not complete raw `result.json`.
- **Git/host:** `feature/recipe-wizard-handoff@dea7c5aa183da770b6b467288f2f6eedf8e94946` fast-forward; working tree clean; no relevant active setup process detected. Result path `/home/inlc/blazux-p1-reports/20261105T052545Z-1e6ec592/result.json`.
- **Read-only command statuses:** doctor=3, inventory_plan=3, HTTP health=0, HTTP models=0, GPU command=0, Docker command=0. Response contents and model ID were not pasted. P1 verify and benchmark `status=BLOCKED`, issues `checkpoint_downloading_or_incomplete` and `hybrid_not_prepared_or_incomplete`; no Wizard actions executed.
- **Interpretation:** generic P1 source/Hybrid audit failure; not evidence of ongoing download. Could be refs-main-only handling, stale incomplete blobs, missing Hybrid marker/files or a different configured cache/mount; no cause selected without new diagnostic facts. New `p1_cache_diagnosis.py` provides read-only facts from actual snapshot and strict audit. SOURCE/CPU CI verified at `4c0041dd230e2abe22ba8379aca74068933ecece`: GitHub push and PR both SUCCESS, each **138/138 CPU tests PASS** (15 manifest + 10 inventory + 13 launcher + 1 executable-mode + 67 P1 + 32 Wizard router). The earlier `eb759ad` source attempt failed its tests because the optional new diagnostic key was absent from an old fake fixture; fixed in `4c0041d` without changing runtime assets. Real DGX evidence still pending.
- **P1 GPU/API/benchmark:** Wizard verification and benchmark `NOT_RUN`; observed curl GET is an API reachability test, not a workload benchmark or complete model identity verification.

## E-20261105-13 — Default NVIDIA index cap regression fixed, actual missing files unresolved

- **Model release fact:** NVIDIA `nvidia/Qwen3.8-Flash-Next-NVFP4` revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` includes `model.safetensors.index.json` (~31.3 MB) and `tokenizer.json` (~12.8 MB). Source: https://huggingface.co/nvidia/Qwen3.8-Flash-Next-NVFP4/tree/main
- **Source bug:** Python strict index parser refused >16MiB (incompatible with official file), though the operator's **observed filenames** were initially rejected before this parser. Source change now permits ≤64MiB while retaining bounds; diagnostic returns exact file/symlink/size status, not merely `checkpoint_downloading_or_incomplete`.
- **GitHub evidence:** code/test commit `66c6c448c1922f958886fa4696c403a4b6227685`, push job https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41976231273/job/127075608240 and PR job https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41976236273/job/127075624614 — both **SUCCESS**, per job 15 + 10 + 13 + 1 + 74 + 32 = 145 CPU tests PASS.
- **Operator DGX prior evidence:** source files `model.safetensors.index.json`, `tokenizer.json` failed `_good_file` metadata validation; Hybrid `tokenizer.json` failed with `.prepared` present. HF blob incomplete-count=0, refs/main valid. Exact failure mode (missing vs dangling symlink vs zero-size) NOT YET OBSERVED. No actual P1 Wizard GPU/API workload BENCH acceptance.
- **Next**: `git pull --ff-only` then one read-only temporary wrapper; review exact file metadata and served API ID. No guessed setup/download/prepare, and no modifying current services.

## E-20261105-14 — DGX confirms externally linked Flash-Next metadata

- **Operator-supplied output:** `/home/inlc/blazux-p1-reports/20261105T055849Z-084c3609/result.json` summary after `git pull` to `4708fe9ef396404d823ca385cde013b67e4d098a`. `api_model_ids=["qwen3.8-flash-next"]`; full snapshot revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`; incomplete blob count 0. Original model index + tokenizer and Hybrid tokenizer: `TARGET_OUTSIDE_REPOSITORY`, `symlink=true`, successful target resolution; Hybrid index `PRESENT_NONEMPTY`, `size_bytes=31907813`; Hybrid marker present.
- **Interpretation:** Existing Blazux-compatible shared metadata link layout was over-rejected by the new P1 file containment check. This alone does not prove that every model tensor is valid or any GPU workload passed. The API served ID indicates there is an API service listening despite the user's description of no existing services.
- **Test authorization:** user approves bounded, non-disruptive GPU inference/benchmark without manual per-action hash entry. Implement `--auto-gpu` as a scoped script option; still validate each current Wizard plan ID and fail closed on changed preflight or failed P1 verification. No service lifecycle or cache changes authorized.
- **Source/CPU CI evidence:** `0063b0e004902408f980c155076c098d49d4569e`, GitHub push and PR jobs **SUCCESS**, 155 CPU PASS each (15 manifest, 10 inventory, 13 launch, 1 script mode, 84 P1, 32 router). [Push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978150843/job/127081754127), [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978155433/job/127081768853).
- **Next DGX scope:** after code pull, single `bash scripts/temporary/p1-post-download.sh --auto-gpu` call. Actual GPU/API/benchmark statuses remain `NOT_RUN` for the new version until operator evidence.


## E-20261105-15 — DGX P1 assets pass, Wizard's combined verify fails

- **Raw-report path:** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` (operator-owned); only console summary supplied.
- **Facts:** snapshot `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, 11/11 listed shards resolved in source+Hybrid, API model ID `qwen3.8-flash-next`, verify+benchmark plans READY, **verify=FAIL, benchmark=BLOCKED verification_not_passed**. These are verified user-supplied runtime outcomes. No benchmark inference was executed.
- **Known source defect:** original temporary runner only parsed Wizard JSON result on rc=0; Wizard returns rc=2 with evidence even on FAIL, hence console `evidence:null` does not demonstrate no evidence. Original combined `_chat_probe` demanded 48 token text, tools required and tiny vision; one failure throws and masks others. Exact original error is UNKNOWN without reading the saved raw result; do not call this a model failure.
- **SOURCE/CI corrective commit:** `391a2844f4c8549e282eae3e266806c89801ad1a`, [push CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42015135913/job/127203693134), [PR CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42015144016/job/127203722486); 2/2 SUCCESS, 173 CPU tests/job. Separates default completions/chat baseline from optional tools/vision and retains nonzero Wizard evidence; actual DGX post-fix GPU validation NOT_RUN.
- **Next:** inspect stored evidence for original failure, then single auto-GPU wrapper on new code. Do not alter operating service, HF data, Hybrid, or gateway.

## Historic evidence not transferred

## E-20261105-04 — User-reported Flash-Next download still in progress

- **Time/subject:** 2026-11-05 11:46 KST, `nvidia/Qwen3.8-Flash-Next-NVFP4`.
- **Evidence:** user said checkpoint was **still downloading**. Classification: `USER_REPORTED / DOWNLOAD_IN_PROGRESS`, not a DGX/filesystem observation and **not** a checksum or completion proof.
- **Unknown:** actual download process, command, bytes, completion percentage, snapshot revision, local cache path and storage headroom.
- **Verification:** `DOWNLOAD_COMPLETE=NOT_VERIFIED`; `HYBRID_PREPARED=NOT_VERIFIED`; `GPU/API/BENCH=NOT_RUN`. No upload/download/cache/operational operation by the assistant.
- **Next safe action:** build P1 Wizard flows and download-in-progress fail-closed tests from synthetic data; after reported completion, verify snapshot and all weight shards read-only before preparation/serve, avoiding concurrent writes.


Old Preview/YSLAB projects reported Orcarouter BF16 PLE/MTP results; those are **reference evidence only**, not proof of the new vLLM 0.32 fork. Historical Preview strict same-token logprob `1e-4` release blocker remains unresolved. DGX status is unobserved this session.

## Update policy

Append new measured entries, never replace failures. When rerunning a test, give it a new ID and reference prior entry. If an entry proves wrong, add an explicit correction with link; do not rewrite history. Publish non-sensitive artifact locations and keep credentials/private data out.
