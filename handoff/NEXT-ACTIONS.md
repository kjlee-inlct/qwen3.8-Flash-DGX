## 2026-11-06 — Re-run corrected 27B registry name audit (minimal next DGX step)

- [x] Initial DGX isolated CPU import passed module/class presence (five checks). `modelopt_mixed` check initially reported TypeError due to incorrect class-level call to `get_name(self)`; not evidence the model cannot run.
- [x] Correct `p2_27b_loader_import_audit.py` to use public `get_quantization_config("modelopt_mixed")` registry/class-identity resolution without instantiating a quant config; source CI `0a14f189`, 336/336 PASS.
- [ ] Clean fast-forward DGX to latest `feature/recipe-wizard-handoff`, execute `./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only` and capture full JSON. Expected keys `quant_registry_module_imported`, `quant_registry_factory_present`, `modelopt_mixed_registry_class_matches`, `modelopt_mixed_cli_name`. A future PASS is a CPU import/registry PASS only, **not** GPU qualification. If registry wrong, investigate actual installed image rather than guessing flags.
- [ ] Confirm true runtime CUDA/C++ extension and loader in an **independently approved** GPU plan before service stop/27B model load; preserve the live original Flash-Next and single :8000 service.
- [ ] Keep Draft PR #1, no merge, no start/switch, no manual execution of `command_preview`.

---

## 2026-11-06 — Next controlled 27B loader import evidence after successful DGX serve split

- [x] DGX ran both dedicated entrypoint `./scripts/serve_27b.sh --status` and `--plan` after fast-forward to `99dde4c`; correct read-only outputs, no 27B start or service modification. Existing Flash-Next `qwen38-flash` API identity **confirmed**, original image ID equals candidate 27B local image ID, and ModelOpt source mix is 208 FP8 + 193 NVFP4.
- [x] Implement isolated CPU-only import probe `p2-27b-loader-import-audit.sh` and 8 unit regressions; source `834c750` CI 333/333 PASS.
- [ ] DGX: after clean `git status -sb` and `git pull --ff-only origin feature/recipe-wizard-handoff`, execute `./scripts/temporary/p2-27b-loader-import-audit.sh --plan`. Optional separately opted-in CPU container `--execute-cpu-only` may test installed vLLM Qwen3.5 and ModelOpt import/class/name with 2GiB/2CPU/no network/GPU/cache/ports. Report structured JSON only. A restricted CPU sandbox import failure is **not** a GPU incompatibility verdict.
- [ ] Reconcile actual ModelOpt name/import facts with candidate `--quantization modelopt_mixed`; verify 27B image provenance, vLLM real loader and GB10 kernels, memory/context and original Flash-Next restore before any approved GPU transition. Keep P2 startup, service stop/switch and rollback blocked until scoped approval.
- [ ] Keep Draft PR #1 unmerged. Do not execute `command_preview` by hand; no duplicate active inference models.

---

## 2026-11-06 — Model-specific serving scripts delivered

- [x] Split legacy `scripts/serve.sh` into default-compatible dispatcher + `scripts/serve_flash-next.sh` (existing executable) + `scripts/serve_27b.sh` (read-only plan/status). `./flash serve` explicitly uses Flash-Next file.
- [x] Preserve old startup behavior/test fixtures and add 10 new CPU tests covering permissions, shell syntax, dispatcher, direct Flash-Next invocation, NVIDIA 27B environment override rejection and absence of a 27B start bypass. CI `67a54afc`: 325/325 PASS.
- [ ] After clean `git pull --ff-only`, operator may run **only read-only 27B** `./scripts/serve_27b.sh --plan` or `--status`; this returns `status=BLOCKED` even when metadata/source PASS. Avoid running `scripts/serve.sh` or `./flash serve` without realizing those default to an actual Flash-Next start, and **do not manually run the returned command_preview**.
- [ ] Review actual P2 source image provenance, ModelOpt vLLM/GPU import/weight load, 27B memory/context, original Flash-Next recovery/rollback, approved DGX transition scope; only then implement a guarded executable `serve_27b.sh` backend with complete start/wait/verify/benchmark and safe recovery.
- [ ] Preserve single active GPU model and `:8000/v1`. Keep PR #1 Draft until evidence/approval gates pass.

---

## 2026-11-06 — P2 dedicated 27B launch preview; GPU acceptance still blocked

- [x] Actual pinned DGX quant audit: modelopt `MIXED_PRECISION`, FP8 **208**, NVFP4 **193**, total **401**, no metadata issues.
- [x] Actual installed image AST audit: **4/4 checks true**, `SOURCE_SURFACES_PRESENT_UNQUALIFIED`; no GPU model load or kernels tested.
- [x] Build dedicated 27B **start-preview** with exact snapshot SHA, local image ID, `modelopt_mixed`, conservative initial GPU settings, no Flash-Next-specific PLE/MTP, source container image and local API identity audit. Source-only `ae4490d6` CI **315/315 PASS**. Does not enable `start --execute`.
- [ ] After clean fast-forward, run `./wizard.sh model 27b plan --for-action start --launch-preview --json` on DGX. This reads local Docker and `/health` plus `/v1/models` on existing `127.0.0.1:8000`, not a GPU model inference request; compare returned original container image and served API ID. Report `issues` and `observed_source`. **Do not run `command_preview`**.
- [ ] Verify runtime vLLM 0.32 CLI `modelopt_mixed`, quant loader import/GPU kernels, VRAM/context 8192/SSM dtype, image provenance/pinned-recipe acceptance, verified Flash-Next recovery before enabling an executable P2 transaction. Keep per-action source identity and explicit approval ID, revalidate immediately before any future stop/start.
- [ ] Only with separately approved DGX GPU/port 8000 maintenance window: stop old, verify port and GPU freed, start isolated 27B, wait, test exact API ID/text/tools/vision + bounded benchmark and restore on failure. Keep PR #1 Draft until those tests pass.

---

## 2026-11-06 — P2 CPU-source qualification next operator evidence

- [x] Add immutable-source ModelOpt layer-algorithm auditor and integrate `quantization_audit` in Wizard; CI `cd63f25` 303/303 CPU PASS.
- [ ] With checkout clean, `git pull --ff-only origin feature/recipe-wizard-handoff`, then rerun `./wizard.sh model 27b status --inspect-runtime --json` and review `quantization_audit` actual pinned local values; do not load model or stop Flash-Next.
- [ ] Inspect local image source with `./scripts/temporary/p2-27b-image-audit.sh --plan`, then explicit `--execute-cpu-only` for isolated runc source AST checks (CPU-only temporary container). Return JSON without secrets; this is NOT GPU model loading.
- [ ] Reconcile ModelOpt per-layer algorithm set against actual installed vLLM registry/loader. Only then design/qualify 27B-specific pinned launcher, image ID vs registry digest, memory/context profile and start/wait/verify/benchmark; no reuse of Flash-Next PLE/MTP defaults.
- [ ] Operational GPU/start/switch/rollback requires separate scoped approval and verified original Flash-Next recovery assets. Keep PR #1 Draft.

---

## 2026-11-06 — Actual image source audit for 27B next

- [x] Operator DGX actual `status --inspect-runtime` confirms NVIDIA pinned 27B source, correct architecture/modelopt/context, ARM64/Linux v0.32 local image ID and protected live Flash-Next.
- [x] Add bounded installed-image source AST auditor and explicit no-GPU/no-network temporary Docker wrapper, plus eight CPU unit tests. `acf5d64` CI: 294/294 PASS.
- [ ] **DGX read-only follow-up:** after `git status -sb` and clean `git pull --ff-only`, run `./scripts/temporary/p2-27b-image-audit.sh --plan`; review, then `./scripts/temporary/p2-27b-image-audit.sh --execute-cpu-only`. This transient runc container does not use GPU, host port or inference service. Return JSON, especially registry/modelopt checks and blocker messages.
- [ ] Audit exact `hf_quant_config.json`, mixed FP8/NVFP4 per-layer support and pinned snapshot tokenizer, verify executable image registry and real memory budget; do not confuse static source presence with GPU loading.
- [ ] Finish isolated 27B launcher/recipe and bounded P2 lifecycle executor with immutable image identification, transaction approval and full original Flash-Next restore. Actual 27B start and `:8000` switchover require a *separate* explicit user-approved transition window; until then no operation may touch inference service/GPU.
- [ ] Run GPU/model/API/benchmark/rollback acceptance only with approved DGX plan. PR #1 stays Draft.

---

## 2026-11-06 — NVIDIA 27B source downloaded; runtime qualification pending

- [x] Record user-provided DGX NVIDIA pinned download 19/19, exit 0, `SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, with exact evidence path; prior transfer-in-progress checklist is historical.
- [x] Implement source-only read-only `status --inspect-runtime` audit of exact source revision, model config, Docker image/platform/label and current service, with CPU fault tests. No GPU allocation, service stop or auto approval.
- [ ] After clean `git pull --ff-only` (download has completed), operator may run `./wizard.sh model 27b status --inspect-runtime --json` and return sanitized JSON, to ground actual cache/config/image/service assertions. Do not launch 27B.
- [ ] Inspect exact pinned config / hf_quant_config and vLLM 0.32 model registry+ModelOpt loader in image, ARM64 support, memory budget and validated image digest. Complete a 27B-specific non-Flash serve recipe and guarded start/wait/verify/benchmark adapter.
- [ ] Obtain a separate exact plan approval before any Flash-Next stop, 27B GPU start or P3 cutover. Preserve and verify rollback source, health and `:8000` API identity.
- [ ] After source CPU/CI, verify actual runtime in approved DGX window, including failures, latency/TTFT/TPS, model identity and rollback. Keep PR #1 Draft until end-to-end acceptance.

---## 2026-11-06 — full Wizard SOURCE / incremental P2–P7 debug

- [x] Build complete model-first TTY menu and machine workflow/roadmap, expose all ten model lifecycle actions for Flash-Next/NVIDIA 27B/Orcarouter.
- [x] Build service menu for status/health/bounded logs and guarded start/stop/restart/rollback/proxy/gateway; P3/P4/P6/P7 advanced plan actions and readiness dashboard are accessible.
- [x] Preserve P1 exact approval and 27B pinned downloader; block P1 guided when another inference model is active or service inventory unknown; add regression.
- [x] Add no-Docker/no-GPU CPU matrix to GitHub CI and update docs/decisions/handoff. Check final HEAD test counts and Draft PR #1 status.
- [ ] While operator-owned 27B download remains active, leave DGX checkout, qwen38-27b-dl, source image/cache and Flash-Next :8000 untouched; **do not ask git pull while downloading**. On completion, obtain exact return code/evidence, then review `./wizard.sh model 27b status --inspect-cache --expected-revision 482ca0f3832238542f8f5295dde86b5f22711d80 --json`.
- [ ] Begin real P2 runtime adapter qualification on source/CPU (vLLM 0.32 single GB10 ARM64, ModelOpt NVFP4, image digest, PLE/MTP) before any live GPU trial; model conversion/stop/switch requires separate approval.
- [ ] Implement/start fault-injected service transaction and symmetric rollback when approved; P3 bidirectional proof, P4 optional no-deletion default, Orcarouter adapter from reviewed parallel branch, P6 switch, P7 acceptance. Keep shared host API 8000.

## 2026-11-05 — after model-first Batch A/source-only B

- [x] Implement root model selection, read-only lifecycle plans and in-flight download suppression, preserving P1 and existing CLI.
- [x] Add bounded GET-only service health/model identity observer and preview-only atomic stop/port-free/start/verify/rollback order.
- [x] Add mock CPU tests and workflow coverage for model cases, API failures and transition gates.
- [ ] At completion of **operator-owned** NVIDIA download, collect return code, `~/.local/state/blazux-wizard/p2/evidence/*.json` path and exact pinned cache inspection before calling P2 downloaded; do not touch current DGX worktree during transfer.
- [ ] Next source batch: validate NVIDIA 27B vLLM 0.32 ARM64/GB10 loader+image, build start/wait/verify/bench adapter and real manifest-based service handover with scoped approval and recovery; do not enable live switching from preview alone.
- [ ] On user-approved DGX validation window after receipt, verify model start/rollback and 27B API/bench; keep Flash-Next model weights/image intact.

## 2026-11-05 — model-first unified Wizard source continuation

- [x] Record accepted D-020 UX design and source/acceptance gates; retain Flash-Next P1 backend.
- [x] Implement root 3-choice menu and read-only `select MODEL --json`; model plans for active, missing, in-flight, source-only, unknown and Orcarouter cases. Show only the relevant downloader or existing P1 guided backend behind explicit separate prompts.
- [x] Expose `qwen38-27b-dl` live container state in observed service manifest; suppress second download; add Orcarouter registry placeholder with no launch permission.
- [x] Add CPU regression matrix and GitHub CI job; preserve all legacy P1–P7 command routes and destructive refusal behavior.
- [ ] **Operator-owned DGX transfer still in progress at last evidence (`16/19` files).** Do not pull updates, restart Flash-Next, interrupt/alter download or run a second transfer. After download exits, collect Wizard receipt/evidence first and only then update DGX checkout.
- [ ] Batch B: actual /v1/models + GPU observation, bounded health/logs, immutable recipe/runtime qualification, and source-only stop→free :8000→start→verify→rollback transition plans with fault injection tests.
- [ ] Batch C: separately approve a live DGX service handover window; validate 27B vLLM 0.32 image/loader/ARM64 before any GPU start. Keep Orcarouter separate branch unmodified.

## P2 download approval unblock (2026-11-05)

- [x] Diagnose user-reported exact approval rejected by mutable preflight fingerprint; fix hash scope to stable safety fields. All storage/Docker/inode preconditions still rerun under download lock.
- [x] CPU regressions for lock inode creation, uptime/free-space drift, actual approved execution, low disk rejection, and service/image identity change requiring reapproval.
- [ ] Check final-HEAD GitHub Actions and PR. On DGX operator's next run: `git pull --ff-only origin feature/recipe-wizard-handoff`, then `./wizard.sh model 27b download --guided` and input the **new** full plan ID. Never reuse pre-fix ID `b190c936...`. Report evidence path / any new blockers.
- [ ] Actual NVIDIA 27B full checkpoint receipt and verification remains `NOT_RUN` until the operator reports results; single model at host `:8000` policy unchanged.

## P2 immediate operator download and parallel source development (2026-11-05)

- [x] Confirm NVIDIA exact model revision `482ca0f3832238542f8f5295dde86b5f22711d80` from authoritative source and add immutable SHA to invalid (not runtime-qualified) recipe.
- [x] Implement guarded Wizard `download --guided` and `download --execute --approve-plan` with no GPU and no API/Docker service mutation; add mock CPU tests and pinned-without-refs audit.
- [x] Commit one-GPU-model/host `:8000` service policy, read-only live manifest and generation-checked transition journal primitives.
- [ ] After latest CI PASS, **operator**: `git pull --ff-only`, then `./wizard.sh model 27b download --guided`. If plan BLOCKED (capacity/image/cache/name/transfer), return the exact issues; do not force the download or delete Flash-Next. Download is **NOT_RUN** until actual DGX evidence is returned.
- [ ] While 27B downloads, implement tested service-switch executor (stop Flash-Next, verify port release, start 27B at :8000, API verify and rollback); preserve original Flash-Next and require separately approved live transition.
- [ ] Qualify vLLM 0.32 ModelOpt loader and single GB10/ARM64 compatibility, then Wizard wait/verify/benchmark and P2 runtime acceptance.

## P2 NVIDIA acquisition and service-manager follow-up (2026-11-05)

- [x] User DGX read-only NVIDIA status: `NO_PINNED_LOCAL_SNAPSHOT`, 0 indexed shards, no local revision in inspected cache. Historical RadixArk evidence retained separately.
- [x] Add Wizard top-level Service management menu and 27B `download` planning action; all stateful actions remain fail-closed.
- [ ] Implement live read-only service/port/inode/disk/download-container inventory, immutable NVIDIA source pin and exact SHA256 plan with freshness and explicit approval.
- [ ] Implement and CPU-test guarded resumable 27B download (without `flash setup`, active model replacement or deletion); then schedule/approve actual DGX download separately.
- [ ] Qualify vLLM 0.32 single GB10 runtime and implement start/wait/verify/bench + rollback as a distinct action from downloading.

## P2 NVIDIA target selection (2026-11-05)

- [x] Replace P2 active model ID and local HF cache directory with `nvidia/Qwen3.8-27B-NVFP4`; retain RadixArk DGX result as historical evidence only.
- [ ] After Git pull, operator runs read-only `./wizard.sh model 27b status --inspect-cache --json` for **NVIDIA cache**, not the previously inspected RadixArk checkpoint.
- [ ] Verify NVIDIA immutable full SHA and actual local source files; qualify pinned vLLM 0.32 runtime/image and single GB10 memory before any download/start. No reuse of RadixArk revision.

## P2 source qualification update — 2026-11-05

- [x] Add bounded config fact discovery (architecture, model type, quant method, context and vision metadata), strictly **unqualified** for vLLM/GB10, with malformed/oversized config regressions.
- [ ] Check current CI after implementation and inspect real DGX read-only `./wizard.sh model 27b status --inspect-cache --json` output; never infer actual model availability from test fixtures.
- [ ] Source-check immutable model revision and vLLM 0.32 loader/GB10 support, then implement guarded 27B recipe planning and runtime steps without allowing unapproved download/start/replacement.

# Next actions — ordered work queue

## Current transition: P1 bounded GPU tests PASS → P2 27B inventory/qualification

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

- [x] P1: actual Wizard baseline, chat, tools, vision and bounded bench PASS.
- [ ] P1: obtain benchmark evidence metrics (TTFT, latency, tok/s) from the already existing operator file; review `doctor`/`inventory_plan` issues and confirm Wizard-driven install/start if required by full P1 lifecycle.
- [x] P2: source-only, fail-closed read-only HF cache inventory in Wizard; unit tests/CI required before DGX operator command.
- [ ] P2: operator runs `./wizard.sh model 27b status --inspect-cache --json` (no downloads, GPU, Docker or API changes).
- [ ] P2: source-verify pinned immutable 27B revision, image digest, vLLM 0.32/model architecture, memory/disk and baseline API expectations before changing placeholder recipe. Candidate stays deliberately invalid until verified.
- [ ] P2: guarded prepare/start/verify/benchmark **not yet implemented**; do not authorize service swap merely because P1 passed.



## 2026-11-05 — Restore default Blazux P1 acceptance semantics

**Latest operator DGX result (2026-11-05):** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` summary from `--auto-gpu` at `805f8e3e`: source checkpoint and Hybrid are both READY, `source_issues=[]`, `hybrid_issues=[]`, 11 indexed source and Hybrid shards resolved, `api_model_ids=["qwen3.8-flash-next"]`, verify and benchmark plans each READY, yet **verify action returned FAIL** and benchmark BLOCKED by verification gate. Original console suppressed the Wizard's failure evidence location because it parsed the JSON outcome only on returncode 0, even though Wizard writes evidence for returncode 2. This is an actual attempted API/GPU verification with FAIL outcome, not evidence of a broken default Blazux model. Exact failing subprobe/error still unconfirmed until raw report is examined.

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

**SOURCE/CI validation (not DGX):** `391a2844f4c8549e282eae3e266806c89801ad1a`, GitHub push and PR checks 2/2 SUCCESS, each 15 manifest + 10 inventory + 13 launcher + 1 mode + 102 P1 + 32 router = **173/173 CPU tests PASS**. Real DGX execution against this fix has NOT_RUN; prior verify FAIL remains unresolved until this new code runs.

- [x] Source: split standard /v1/completions + chat baseline from optional tool/vision probes, preserve exact per-probe failure classes and HTTP status without raw outputs, retain Wizard evidence on rc=2; let baseline PASS through to the short benchmark even if optional probes are PARTIAL.
- [x] CI/source unit and fake DGX regressions: 2/2 SUCCESS, 173 CPU tests per job.
- [ ] Operator can FIRST read the **existing** `20261105T103738Z-c4eb4031/result.json` at `actions.verify.command.stdout/stderr` to identify the original failure without re-running GPU work. Be careful of raw output before sharing.
- [ ] Only after that, `git pull --ff-only origin feature/recipe-wizard-handoff` and one `bash scripts/temporary/p1-post-download.sh --auto-gpu` to obtain per-subprobe baseline/extended status, actual evidence URI, benchmark metrics if baseline passes.
- [ ] Treat default P1 baseline and full extra feature acceptance as distinct gates; do not claim P1 complete if tools/vision or benchmark remain PARTIAL. Never restart servers or re-download assets as a response to a Wizard probe failure.


> Updated 2026-11-05 KST. **Draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) open, unmerged; current source CI at `43f5131` 2/2 SUCCESS (103 CPU tests/job).** Status terms are scoped. Tasks are not achieved merely because listed in a plan.

## 2026-11-05 — Completed download reported; P1 validation disagreement

**DGX operator update, 2026-11-05:** The operator explicitly confirms the NVIDIA Flash-Next download has finished. Their submitted terminal output after `git pull` to `dea7c5aa183da770b6b467288f2f6eedf8e94946` shows `bash scripts/temporary/p1-post-download.sh` produced report `/home/inlc/blazux-p1-reports/20261105T052545Z-1e6ec592/result.json`; current branch and clean tracked worktree checks PASS; no setup process found in the process scan. HTTP `/health` and `/v1/models` command exit codes are 0 **but actual served model ID was not included in the console summary**. Wizard doctor and inventory plan returned exit code 3; both P1 verify/benchmark plans BLOCKED: `checkpoint_downloading_or_incomplete`, `hybrid_not_prepared_or_incomplete`; no Wizard GPU/bench requests executed. The `checkpoint_downloading_or_incomplete` string is a **generic validation failure**, not proof that the download continues. The apparent mismatch needs read-only evidence before any setup, repair, download, switch or deletion.

- [x] SOURCE/CPU CI 2/2 SUCCESS, 138/138 tests each at `4c0041d`; previous fixture incompatibility fixed. Commit read-only `scripts/temporary/p1_cache_diagnosis.py` and invoke it from the existing one-command temporary P1 script; add synthetic tests, including master-ref fallback diagnostic and completed shards with leftover incomplete blob names. The current main-only Wizard check is deliberately left fail-closed pending evidence.
- [ ] Operator should `git pull --ff-only`, run `bash scripts/temporary/p1-post-download.sh --inspect-only` once and return the report's `cache_diagnosis` and actual `checks.models.stdout`; no `setup`, `prepare`, `serve` or automated benchmark until the discrepancy is understood.
- [ ] If diagnostics prove an auditor mismatch, fix the *specific* source predicate with CPU fixtures and rerun CI; otherwise identify genuinely missing Hybrid preparation without any competing download. Confirm the expected API model ID and actual image identity before Wizard verify/bench.

## Latest P1 checkpoint investigation — file-level facts required

**2026-11-05 P1 regression analysis:** NVIDIA's default `nvidia/Qwen3.8-Flash-Next-NVFP4` is supported by Blazux. The official `fc694b5` snapshot distributes `model.safetensors.index.json` (~31.3 MB) and `tokenizer.json` (~12.8 MB). Our new P1 audit erroneously rejected an otherwise-valid index above 16 MiB; code changed to a bounded 64 MiB maximum. **However the operator's specific issues** `model.safetensors.index.json` and `tokenizer.json` arise at the initial `_good_file` stage, *before* parsing/size checks. Thus the artificial size cap does not by itself explain the reported failures. The Hybrid marker exists, but Hybrid `tokenizer.json` also fails. Do not conflate claimed download completion with all snapshot symlinks resolving correctly; investigate metadata file existence, symlink resolution, size and repository containment first.

- [x] Fix 16MiB index-size bug, retaining 64MiB safety cap, with 17MiB-valid and >64MiB-rejected regression tests.
- [x] Expand `scripts/temporary/p1_cache_diagnosis.py` to return for each affected source/Hybrid metadata file: missing vs dangling HF symlink vs outside repo vs zero bytes vs valid, file size, and whether it exceeds the obsolete 16MiB cap. Add fixture tests for each class.
- [x] Existing single-command wrapper now reports API `/v1/models` **model IDs**, plus a distinct inspection-only vs Wizard-not-ready reason. No GPU, cache, model or Docker mutation from those source changes.
- [x] **Source/CI accepted:** `66c6c448c1922f958886fa4696c403a4b6227685`, GitHub Actions 2/2 SUCCESS, each 145/145 CPU tests PASS (15 manifest + 10 Inventory + 13 launcher + 1 executable mode + 74 P1 tests + 32 Wizard router). This is NOT DGX runtime acceptance.
- [ ] On DGX after operator's existing shell command chain finishes, `git pull --ff-only` then `bash scripts/temporary/p1-post-download.sh --inspect-only`; return **`cache_diagnosis.snapshots[*].source_metadata/hybrid_metadata`**, `api_model_ids`, and new evidence path. Only then decide if missing metadata should be repaired from its exact official revision and whether Hybrid snapshot needs a non-destructive repair. **Never re-download the 124GiB checkpoint or run `setup` as a guessed fix.**

## D-017 — Resolve false P1 audit block and exercise existing GPU service

**Operator DGX facts (2026-11-05):** The latest post-download diagnostic returned `api_model_ids=["qwen3.8-flash-next"]`, `refs/main=fc694b54fb0174e0913e6adf86691ef85a4ead47`, 0 incomplete HF blobs, a source index and tokenizer that are **existing nonempty symlinks whose targets resolve outside the model repository**, and a Hybrid tokenizer with the same layout. The Hybrid index is a normal 31,907,813-byte file and the `.prepared` marker exists. These observations show the previous `TARGET_OUTSIDE_REPOSITORY` reason is a **new P1 checker policy stricter than Blazux's original `os.path.exists`-based policy**; they do not establish that any metadata is missing. Previous plans were blocked before actual GPU verification or benchmark. The user explicitly allows non-disruptive GPU compute tests to run without separate per-step approvals, provided the actual target service is confirmed. The presence of an API response means some server is listening; do NOT assume there are literally no processes running or stop/replace any service.

- [x] Restore compatibility for confirmed existing metadata symlinks without weakening shard containment; add synthetic source/Hybrid and dangling/shard escape regressions.
- [x] Add scoped `--auto-gpu` to the existing one-command temporary runner. The operator may exercise the GPU without typing any plan-hash approvals. Still require actual model identity, current successful Wizard plan + double-checked plan ID, and verify PASS before benchmark. It never starts/stops a container, repairs Hybrid, changes model, or downloads anything.
- [x] GitHub SOURCE/CPU CI verified at `0063b0e004902408f980c155076c098d49d4569e`: push and PR jobs both SUCCESS, 155/155 CPU tests per job. No GPU PASS claim until operator results.
- [ ] Operator: `git pull --ff-only`, then `bash scripts/temporary/p1-post-download.sh --auto-gpu`. Return `~/blazux-p1-reports/.../result.json` summary including `plans`, `actions`, `api_model_ids` and new `cache_diagnosis`. If still BLOCKED, diagnose *new explicit issues*; no blind `./flash setup` or cache purge.

## CONFIRMED IMPLEMENTATION ORDER — Wizard is the mandatory operator entrypoint

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

P1 **not yet complete**: current Wizard only supports read-only `00-doctor.sh` / `10-plan.sh`. Next coding milestone is Wizard-driven Flash-Next prepare/build/launch/health/bench/artifacts with no implicit mutation and mock CPU tests. **P2 only after P1 DGX benchmark evidence**; P3 only after both model baselines; P4 optional and separate exact deletion consent; P5 Orcarouter follows P4 decision (skipped if not needed). Keep external `:8000/v1` stable across switches and record actual served model ID. One large GPU model active at a time. Do not use SGLang.

## 2026-11-05 large P1 code batch / current operator action

**2026-11-05 operator-provided DGX terminal log (not directly observed through an SSH tool):** GB10/aarch64, Docker 29.6.2, 121 GiB unified memory (117 GiB available then); read-only Wizard Inventory showed no host :8000 collision and no `qwen38-flash` container, and initially 580,134,281,216 bytes free. The existing OpenWebUI and Portainer containers were running; preserve both. `./flash setup default` finished building `qwen38-flash-dgx:v0.32` (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`). The final log line showed **model download 9/25 = 36%**, NOT completed weights/Hybrid. The user's shell also entered `./flash serve default`, `./flash wait`, `./flash test` after setup, so these may run automatically after download/preparation. Do not compete with, modify or restart this running operator setup chain. Port availability and download progress can change after the log timestamp.

- **Source committed:** P1 Wizard `wizard/p1.sh` interactive/noninteractive mode plus pinned snapshot/image audits, plan-hash gate, guarded Hybrid preparation/start/wait, API verification and bounded sequential SSE benchmark with local JSON evidence. `tests/test_p1_*_cpu.py` added; CI at c625a49 verified 2/2 SUCCESS, 80/80 tests per job; DGX Wizard/API/bench NOT_RUN.
- **Immediate next:** fix new CPU/CI failures if any, no active DGX work. The operator's `./flash setup default` is already downloading and has queued later `serve/wait/test`. When it ends, inspect Wizard status and adopt any existing running service. Do not rerun setup or delete the cache.
- **Exit gate still unchecked:** Real P1 Wizard execution and DGX API/benchmark PASS (including tool/vision) and rollback verification. Source-only CI does not close P1.

## New implementation contract — modular Wizard before P1–P7 live testing

**User decision (2026-11-05):** Build the **whole Wizard menu/CLI skeleton first**. Keep each P-stage in a separate `wizard/menus/pN.py`, shared CLI/router/guards in common modules, and retain a **single root `./wizard.sh`** for both guided use and direct `--stage/--action` scripting. Use stable machine-readable JSON/exit codes so the operator can run commands on DGX and return output for analysis. Do not confuse source-only menu registration with an implemented service, validated 27B model, switch, cleanup or gateway.

- [x] **W0 — Modular menu and headless CLI routing (SOURCE/CI).** P1 delegates to existing tested P1 flow; P2–P7 have per-stage status/plan interfaces and fail-closed execution. Source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe` produced 2/2 CI success, 101/101 tests/job. Follow-up source/docs commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b` GitHub CI verified **2/2 SUCCESS, 103/103 CPU tests each**, including P1 JSON guided guard.
- [ ] **W1 — Complete shared execution service and model adapters.** Add stage-specific schema/recipes/provenance checks, guarded prepare/start/verify/bench/rollback controllers as phases qualify; do not enable unverified P2–P7 operations. Exercise P1 against the actual DGX **only after the current setup and queued commands finish**, with per-action approval.
- [ ] **W2 — Real Wizard baseline acceptance.** P1 measured API and benchmark, rollback and evidence; then implement and validate P2, P3, optional P4, P5, P6, P7 in the previously locked order. P4 is conditionally skipped if capacity is sufficient.

**Direct CLI examples:** `./wizard.sh list --json`; `./wizard.sh p1 status --json`; `./wizard.sh --stage p3 --action switch --from-model flash-next --to-model 27b --json` (BLOCKED by design). Detailed contract: `docs/WIZARD-CLI-CONTRACT.md`.

## UI organization decision — domain-based menus (D-015)

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

- [x] Rename source `wizard/menus/p1.py`–`p7.py` into descriptive submodules under models/switching/storage/operations; update routing, legacy aliases, two-level interactive navigation, JSON catalog and direct CLI, plus CPU regressions. **SOURCE+CI 112/112 PASS/job twice** at `571e1c2`.
- [ ] Next model-specific implementation remains P1 actual DGX Wizard API/benchmark/rollback, then P2/P3/conditional P4/P5/P6/P7 in the existing runtime acceptance sequence. **File/menu grouping does not change stage acceptance order.**

## D-016 — User-run single-script temporary batch

- [x] Design and stage `scripts/temporary/p1-post-download.sh`, `p1_post_download.py`, source-only test `tests/test_p1_temporary_cpu.py`, README and CI. One script collects P1 diagnostic status, uses the existing Wizard for separate explicit verify/benchmark plans, and writes a consolidated report. Never runs a competing `setup`, automatic `serve` or cleanup.
- [x] New runner GitHub CPU CI VERIFIED at `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b`: both jobs SUCCESS; each ran 131 unique CPU tests. CPU CI is not DGX qualification.
- [ ] Once the operator-owned original setup/serve/wait/test process **fully ends**, operator runs `git pull --ff-only` and the one temporary wrapper. Start with `--inspect-only` if the live model state is uncertain; then use interactive TTY for independent current plan hashes if readiness is confirmed. Return reviewed `result.json` path/results; never upload secrets automatically.
- [ ] Review real P1 API/bench data (and any BLOCKED status) and update evidence/next actions before advancing. Temporary script is retired only by a later reviewed commit, not by running itself.

**Permanent rules:** `handoff/OPERATING-RULES.md` R1D and `scripts/temporary/README.md`; decision D-016.

## NOW — P0, read-only/source-safe

**P1 ASSET STATE (USER_REPORTED 2026-11-05 11:46 KST):** `nvidia/Qwen3.8-Flash-Next-NVFP4` downloading **IN_PROGRESS**. Do **not** auto-download, re-download, build over shared cache, run `setup`/hybrid preparation, or launch the model while it may be incomplete. First safe work: implement full P1 Wizard orchestration using synthetic CPU fixtures; the Wizard must detect `DOWNLOADING/INCOMPLETE` vs `READY` and block serve/bench until checkpoint revision, shards and cache integrity are confirmed. On next user-reported completion, read-only verify exact snapshot and local resources before progressing. Actual DGX state, percent, completion and revision remain **NOT_OBSERVED**.


**CI regression note:** First N2+port commit `7e8f4a1` had four launch FAIL due to permission `100644` (exit 126), despite 15 schema and 10 inventory tests PASS. Script executable bits repaired in follow-up commit; check actual new HEAD CI before claiming all PASS.

**2026-11-05 priority revision (user request):** legacy services reported deleted; restore external `:8000/v1` with Blazux *NVIDIA Flash-Next* `default` profile, not Orcarouter. SOURCE changes to `flash`, `scripts/serve.sh`, `profiles/default.env` and manifest rules; N2 read-only inventory and deterministic plan implemented. **DGX state unobserved**. No setup, serve, GPU, download or cleanup done.


**N1 completed SOURCE/CPU only (2026-11-04):** JSON Schema Draft 2020-12, safe YAML loader, bounded guards and 15 isolated CPU tests PASS. 27B candidate intentionally FAIL (exit 2); synthetic valid fixture is not deployable. New PR CI requires GitHub readback at the actual commit SHA. No DGX/GPU/API execution.


- [x] **N1 — Make manifest schema machine-checkable.** Add `recipes/` and `schemas/` proposals implemented with validated, explicit repo revision, digest and immutable targets; a sample 27B placeholder must fail closed. CPU tests cover malformed manifest and unsupported engine.
- [x] **N2 — Implement read-only storage/Docker inventory.** Gather capacity and model references without changing caches, engines or services. Detect protected live service name/image/mount/port and disallow unsafe paths/names. Add `--dry-run` and deterministic plan output.
- [ ] **N3/P1 FIRST — P1 Wizard SOURCE implemented; verify CI and actual DGX API/benchmark before completion.** `wizard/00-doctor.sh` and `10-plan.sh` are read-only partial foundations. Add shared Python manager, interactive and noninteractive wrappers, exact pin/asset/disk/port validation, prepare/start/wait/API verify, benchmark and reproducible evidence export, gated approvals, rollback/failed-launch guard, deterministic dry-run, mock CPU tests. **No GPU readiness claim until actual Wizard execution on DGX**.
- [ ] **N4 — vLLM 0.32 27B source feasibility audit.** Determine exact architecture mapping, NVFP4 quantized output head, vision input, GDN, kernel/sm_121 constraints, context, MTP OFF baseline and DFlash2 scope. Record precise pinning and file/line evidence; **do not copy SGLang launcher**.
- [ ] **N5 — Integrate existing Orcarouter feature deliberately.** Review `feature/orcarouter-bf16-adapter` docs/commits, resolve against manifest contract, then merge/cherry-pick only after explicit integration/test plan. Preserve PLE/MTP count/dtype guards.

## THEN — ordered Wizard milestone gates (DGX operation requires scope-specific approval)

- [ ] P1 **Wizard** Flash-Next installation → preparation → start → API checks → pinned benchmark → artifact/evidence export. Requires DGX PASS for exit.
- [ ] P2 **Wizard** 27B feasibility source/CPU GO → install/start → API/benchmark/evidence on DGX. Requires DGX PASS for exit.
- [ ] P3 **Wizard** Flash-Next ↔ 27B repeated bidirectional switch on stable :8000, readiness check, rollback and failure injection.

## AFTER — independently gated

- [ ] P4 **Wizard** optional Flash-Next checkpoint cleanup **only if space is insufficient**; after P3 verified, dry-run exact paths/shared reference check, preserve fallback + get explicit exact approval. **Otherwise SKIP without treating it as a failed stage.**
- [ ] P5 **Wizard** Orcarouter-Flash-Next direct BF16 PLE MTP OFF → verified 31/31 BF16 overlay MTP2, install/start/API/benchmark/evidence.
- [ ] P6 **Wizard** Orcarouter ↔ 27B repeated bidirectional switch and rollback with stable :8000 and validated model IDs.
- [ ] P7 **Wizard** integrated operational acceptance: service/proxy/gateway/storage, retention, CI, numerical reproducibility, release gates, runbooks and rollback.

## Required action output format

Each completed N-step must report: file+commit SHA, `PASS/FAIL/NOT_RUN` with source/CPU/CI/GPU scope, exact commands, side effects, relevant evidence path and next blocker. Update `CURRENT-STATE.md`, `CHANGELOG.md`, and tests ledger. If blocked, retain task unchecked and add precise reason.

## Current exclusions

Current **source-only development**: no operational GPU usage; no `./flash setup` or `./flash serve` run on DGX; no image pull/build/download; no Docker stop/rm; no deletion; no SGLang. User-requested source default now targets :8000; actual port occupancy and service deployment remain unverified and require separate preflight.
