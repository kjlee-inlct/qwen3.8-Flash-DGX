## 2026-11-06 — REAL Qwen3.8-27B GPU PASS_RESTORED and unified Manifest-led Wizard status

Operator supplied actual DGX `--trial-execute` result: `executed=true`, `target_api_ready=true`, `inference_ok=true`, `trial=PASS`, `restoration.status=RESTORED`, `issues=[]`, `status=PASS_RESTORED`. This supersedes earlier source-only `NOT_RUN` statements. User requested canonical Manifest-based Wizard read-only status rather than ad hoc Docker/curl. Implemented `scripts/manager/service_status.py` and unified `./wizard.sh service manager status --json`; added CPU fake-backend tests and updated routing. Kept old `inventory`, `health`, `logs` non-mutating. Combined status NOT_RUN on real DGX until operator invocation; no further actual GPU model or service changes made during this source update. See `handoff/P2-27B-GPU-TRIAL-PASS-20261106.md`.

---

## 2026-11-06 — Qwen3.8-27B experimental GPU trial (explicit approval, restore original)

After actual DGX 9/9 CPU import/ModelOpt registry PASS, implemented `scripts/manager/p2_27b_gpu_trial.py` with exact 64-character fresh plan approval, downtime acknowledgment, bounded initial 27B launch (NVIDIA ModelOpt mixed, no MTP), health/model ID + tiny generation test, private logs and exact original Flash-Next `:8000` container restoration. Added `--trial-plan`/`--trial-execute` to dedicated `serve_27b.sh`. Unknown Docker state or competing GPU container blocks start/restoration; trial never removes original. CPU regression CI `ea28b0c0` 354/354 PASS. **Actual 27B GPU trial and rollback NOT_RUN yet**. Compared MiaAI-Lab/Unsloth, NVIDIA forum GB10 recipe, eugr and NVIDIA guide; checkpoint formats not interchangeable.

---

## 2026-11-06 — Resolve 27B CPU import check false-negative

Observed the operator's actual isolated CPU import with Qwen3.5 and ModelOpt classes all present, but TypeError when our test incorrectly invoked vLLM `ModelOptMixedPrecisionConfig.get_name()` without `self`. Replaced with public vLLM quantization factory lookup under `modelopt_mixed` and exact returned class identity, without constructing quant config or model. Added 3 extra CPU tests plus instance-method regression; CI `0a14f189` **336/336 PASS**. Test must be re-run on DGX; runtime/launch still blocked.

---

## 2026-11-06 — Post-split DGX accepted read-only 27B entrypoint; new opt-in CPU import probe

Reconciled real DGX fast-forward and actual `serve_27b.sh --status/--plan` JSON, including verified original Flash-Next API identity and identical original/target local vLLM 0.32 image IDs. Added isolated `scripts/manager/p2_27b_loader_import_audit.py`, `scripts/temporary/p2-27b-loader-import-audit.sh`, and 8 CPU tests. It imports installed vLLM Qwen3.5 and ModelOpt class and verifies `get_name()=modelopt_mixed` under restricted CPU runc (opt-in; not run on DGX yet); no inference/weights/GPU/cache/network/ports. Source CI `834c750` **333/333 PASS**; 27B GPU/service stop/start/switch remains blocked.

---

## 2026-11-06 — Separate dedicated Flash-Next/27B server entrypoints

Moved existing Flash-Next launch implementation into executable `scripts/serve_flash-next.sh` and routed `./flash serve` directly to it. Replaced `scripts/serve.sh` with compatible default Flash-Next dispatcher and explicit 27B selection; added executable `scripts/serve_27b.sh` exposing only `--plan`/`--status` (read-only) while GPU start/switch remains blocked. Added 10 CPU regressions, executable-mode checks and CI workflow coverage for both new files. Source CI `67a54afc`: 325/325 PASS. No inference service changes, commits/merges to main or 27B GPU launch.

---

## 2026-11-06 — Operator DGX 27B source PASS and separate blocked launch-preview

Recorded actual exact pinned ModelOpt layer counts FP8 208 + NVFP4 193, and installed image source 4/4 checks true from CPU-only runc. Added `scripts/manager/p2_27b_launch_preview.py` + 12 CPU tests and `--launch-preview` Wizard CLI, returning proposed explicit `modelopt_mixed` vLLM argv and source/API fingerprints. This is not approval/execution, includes immutable pinned revision, prohibits Flash-Next PLE/MTP inheritance, and keeps transition/rollback/GPU gates closed. CI `ae4490d6` 315/315 PASS. No DGX GPU or inference service mutation performed.

---

## 2026-11-06 — Immutable NVIDIA ModelOpt mixed precision audit in P2 runtime preflight

Added `scripts/manager/p2_27b_quant_audit.py` + nine CPU regressions. Existing Wizard runtime-preflight now reads bounded exact-pin `hf_quant_config.json`, reports producer/quantization mode/layer counts and blocks unexpected or unparseable mixes while preserving all prior image/host/runtime gates. GitHub source commit `cd63f25`: CI 303/303 PASS; no model, GPU, Docker service, download or cache mutations performed.

---

## 2026-11-06 — Audit installed vLLM 0.32 image source using CPU-only runc

Based on the new DGX preflight result, authored `scripts/manager/p2_27b_image_audit.py`, `scripts/temporary/p2-27b-image-audit.sh` and 8 CPU regressions to audit the exact local image's registered Qwen3.5 model class and ModelOpt NVFP4/FP8 source without importing vLLM/CUDA. The wrapper defaults to plan-only and requires an explicit CPU-only run flag; image ID pinned and Docker isolated with runc, no GPU or network. SOURCE commit `acf5d64` CI 294/294 PASS. Actual operator CPU-only image probe, GPU/27B service/bench and rollback NOT_RUN.

---

## 2026-11-06 — P2 download completion evidence and guarded runtime preflight

Reconciled operator's actual NVIDIA 27B 19/19 exit-0 download with stale handoff. Added read-only `p2_27b_qualification.py` for pinned source/config, host ARM64, Docker image/platform/label and current service observation, plus `model 27b status --inspect-runtime` command and isolated CPU regressions. Kept the candidate recipe intentionally invalid, GPU start/switch blocked, and Flash-Next service unchanged. NVIDIA 27B `SOURCE_FILES_PRESENT_PINNED_CANDIDATE` does not establish loader, GPU/API, benchmark, or rollback qualification. CI needs validation at new HEAD.

---## 2026-11-06 — Complete P1–P7 Wizard console and lifecycle source (D-021)

Added `wizard/console.py` (three primary screens, model Continue/all actions, full service and advanced P3/P4/P6/P7 plans), `wizard/workflow.py` (P1/P2/P5 action slots for inspect/download/prepare/start/wait/verify/benchmark/switch/rollback/recipe), `wizard/roadmap.py` (all seven release gates), and `scripts/manager/service_logs.py` (bounded opt-in read-only service logs). Wired CLI `workflow` and `roadmap`, extended service `logs` route and CPU CI tests; preserved original P1 guarded engine and P2 approved downloader. Corrected P1 shortcut routing so another active GPU model or unknown service observation cannot enter P1 guided startup. All new P2–P7 mutation adapters remain blocked until runtime/recovery qualification. No DGX operations performed.

## 2026-11-05 — Read-only local API health and stop-before-start/rollback preview

Added `scripts/manager/service_health.py` (fixed loopback :8000 GET /health and /v1/models, bounded response and timeout, served-ID match) and `scripts/manager/service_transition_preview.py` (fail-closed atomic handover preview and explicit recovery). Wired health into existing service CLI and simple root Service choice; attached transition preview to model selection when other model observed. Extended CPU unit tests and CI. No actual service/DGX/API/GPU calls in this development session. Download is user-owned and in progress per last evidence; not verified complete.

## 2026-11-05 — Model-first Wizard UI and read-only automatic lifecycle planner (D-020)

Created `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`; changed `wizard/main.py` TTY root to 3 choices and introduced machine `select MODEL --json` / `model choose MODEL --json`. Added `wizard/quickstart.py`: safe consolidated download/monitor/P1-guided/switch-blocked plans from actual service + pinned checkpoint observations. Updated live `service_manifest.py` to classify in-flight `qwen38-27b-dl` without triggering new downloads; added unqualified Orcarouter service policy entry. Preserved old stage CLI and Flash-Next P1 backend. Added new CPU regression suite and refreshed canonical docs/CI/DECISIONS. User-owned NVIDIA 27B download started; receipt and runtime **not verified**. No service/API/GPU or DGX worktree actions performed in this coding session.

## 2026-11-05 — Fix P2 guided download falsely expiring under its own lock

After a user entered the correct plan ID, the second preflight rejected the request because raw inode counts, floor free GiB and Docker uptime were hashed. Created `_approval_facts` containing stable model/revision/cache/image/host running-state/port occupancy plus time window. Retained all live minimum-disk, inode, transfer and Docker checks on revalidation. Added mock CPU tests reproducing the change while state lock is created and guarding safety-relevant image/state drift. No DGX download or service mutation was performed by this change.

## 2026-11-05 — P2 pinned NVIDIA downloader and single active model manifest foundations

Operator confirmed one active GPU model per DGX Spark, both NVIDIA Flash-Next and 27B on host port 8000. Added `runtimes/service-policy.json`, `service_manifest.py`, `service_journal.py`; service menu read-only inventory uses actual Docker/socket. Added exact-revision `p2_27b_download.py` Wizard download plans with live revalidation/lock/approval and bounded evidence, no GPU/port/service effects. Added interactive `download --guided`, CPU regressions and pinned snapshot recognition without refs/main. Source and CI separate from actual DGX download/GPU/switch. No service interrupted.

## 2026-11-05 — Service management UI and NVIDIA 27B download planning

Added independent `service manager` Wizard menu/CLI (source-only) while retaining `operations system` for P7. Added `download` action to NVIDIA 27B planning, default BLOCKED. CPU router tests cover menu/catalog and refusal of unapproved mutation. Documented NVIDIA DGX `NO_PINNED_LOCAL_SNAPSHOT`; no download, restart, Docker/GPU work run.

## 2026-11-05 — P2 model choice changed to NVIDIA

Operator selected `nvidia/Qwen3.8-27B-NVFP4` instead of RadixArk. Switched read-only Wizard cache inventory, fixture cache path, invalid candidate recipe and current documentation. Preserved RadixArk 3/3-shard DGX result as historical evidence; NVIDIA local presence and DGX/GPU acceptance NOT_RUN. No runtime mutation or download.

## 2026-11-05 — P2 bounded config metadata audit

Added read-only `config.json` model facts (architecture, model type, quantization, context, vision marker) to 27B Wizard inventory. Source inspection remains unqualified for vLLM 0.32 and never authorizes runtime mutations; malformed and >1MiB config are explicitly not source-ready. Added CPU fixtures. GitHub CI results must be recorded separately; no DGX command executed in this session.

# Handoff changelog (append-only)

## 2026-11-05 — H-018 — Observed P1 GPU PASS; begin P2 source-only read inventory

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

- Distinguish high-level benchmark PASS from performance metric thresholds; operational doctor/inventory-plan exits remain 3, no P1 service lifecycle exit asserted. P2 candidate remains invalid/unpinned, operations blocked. No DGX action by assistant.


## 2026-11-05 — H-017 — Default Blazux baseline separated from optional Wizard probes

**Latest operator DGX result (2026-11-05):** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` summary from `--auto-gpu` at `805f8e3e`: source checkpoint and Hybrid are both READY, `source_issues=[]`, `hybrid_issues=[]`, 11 indexed source and Hybrid shards resolved, `api_model_ids=["qwen3.8-flash-next"]`, verify and benchmark plans each READY, yet **verify action returned FAIL** and benchmark BLOCKED by verification gate. Original console suppressed the Wizard's failure evidence location because it parsed the JSON outcome only on returncode 0, even though Wizard writes evidence for returncode 2. This is an actual attempted API/GPU verification with FAIL outcome, not evidence of a broken default Blazux model. Exact failing subprobe/error still unconfirmed until raw report is examined.

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

**SOURCE/CI validation (not DGX):** `391a2844f4c8549e282eae3e266806c89801ad1a`, GitHub push and PR checks 2/2 SUCCESS, each 15 manifest + 10 inventory + 13 launcher + 1 mode + 102 P1 + 32 router = **173/173 CPU tests PASS**. Real DGX execution against this fix has NOT_RUN; prior verify FAIL remains unresolved until this new code runs.


## 2026-11-05 — H-016 — Preserve default Blazux shared-metadata layout and preauthorize bounded P1 GPU tests

- Operator's latest actual DGX report showed expected API model ID `qwen3.8-flash-next`; original index/tokenizer and Hybrid tokenizer are symlinks resolving to existing files **outside** the model repo. 31,907,813-byte Hybrid index and `.prepared` exist, incomplete blob count=0. Older P1 checker falsely treated these metadata links as missing. This is a P1 source compatibility defect; no evidence that the full checkpoint needs re-downloading.
- New asset verifier accepts only nonempty **metadata** symlinks (`model.safetensors.index.json`, `tokenizer.json`) across the model-repo boundary; weight shards remain root-pinned, JSON index still parsed with 64MiB cap. Source/Hybrid symlink, dangling link and escaped shard regression fixtures added. Diagnostic records compatibility flag and target size without copying model files.
- User explicitly authorized GPU compute for non-disruptive P1 testing without per-action typed consent. Added `--auto-gpu` to the existing temporary wrapper. It checks expected served ID and health, takes current verify and benchmark hash IDs, invokes the original Wizard's same second-preflight protection, and never touches lifecycle/cache. P1 verify must PASS before bounded bench.
- This is source-only implementation; do not claim actual P1 GPU PASS until new DGX operator evidence. D-017, R1E added to permanent rules; P2–P7 and destructive actions remain separately blocked.
- **CI/source confirmation:** commit `0063b0e004902408f980c155076c098d49d4569e`, [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978150843/job/127081754127) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978155433/job/127081768853), both **SUCCESS**. Each job ran 15 + 10 + 13 + 1 + 84 + 32 = **155/155 CPU tests PASS**. No actual DGX GPU/API/benchmark result has been observed for the fixed Wizard yet.


## 2026-11-05 — H-015 — P1 metadata audit bug corrected and file-level diagnosis added

- Blazux default NVIDIA checkpoint remains supported. NVIDIA Hugging Face `fc694b5` index is 31.3 MB; our P1 Python audit invented a 16 MiB JSON size ceiling, causing a false rejection for *otherwise valid indexes*. Changed to a bounded 64 MiB cap; added realistic >16MiB and still-over-limit regression tests. This is our new code defect, not an upstream Blazux limitation.
- The actual DGX `source_issues=[model.safetensors.index.json, tokenizer.json]` are from the **earlier `_good_file` predicate** and therefore do not prove that this size gate caused the user's failure. New read-only diagnostics now identify file absent/dangling symlink/empty/outside repo, size, source vs Hybrid, and report parsed API model IDs.
- `66c6c448c1922f958886fa4696c403a4b6227685` source commit CI 2/2 **SUCCESS**, 145/145 CPU tests per job. No GPU/bench re-run, download/repair or service change by assistant; real DGX file evidence still required.


## 2026-11-05 — H-014 — Download completed (operator report), P1 audit disagreement

- Operator confirms NVIDIA Flash-Next download finished. First actual DGX wrapper run on branch `dea7c5a`: Git clean, process scan no active setup, `/health` and `/v1/models` exit code 0; Doctor/inventory plan exit 3; Wizard verify/bench both BLOCKED on generic checkpoint incomplete and Hybrid unready. No Wizard GPU/benchmark calls made.
- Root cause **unknown**: P1 audit currently reads `refs/main` only, whereas `./flash` accepts `refs/master` or an alternate snapshot; it also treats any remaining `.incomplete` blob as blocking even when indexed files are present. A full copy of the raw report has not been supplied; do not assert either explanation as proven.
- Added read-only `scripts/temporary/p1_cache_diagnosis.py`, wired into the one-command wrapper, plus CPU fixtures. First CI run failed due an optional diagnostic missing in the pre-existing report fixture; follow-up makes the field optional and adds tests. GitHub CI fix commit `4c0041dd230e2abe22ba8379aca74068933ecece` 2/2 SUCCESS, 138/138 CPU PASS per job. No DGX changes executed by assistant.


## 2026-11-05 — H-013 — Temporary operator bundle safety and final CPU CI

- Fix commit `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b` checks an operator-owned setup/serve process again just before test execution, blocks report output under HF cache, adds two CPU regressions, and removes duplicated CI invocation (temporary test suite is included under `test_p1_*_cpu.py`).
- GitHub Actions **2/2 SUCCESS**, each with 15 manifest + 10 inventory + 13 Flash launch + 1 executable-mode + 60 P1 (41 earlier and 19 temporary) + 32 Wizard router = **131/131 unique CPU tests PASS**. [Push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970955588/job/127058833280), [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970960007/job/127058848658).
- This is SOURCE/CI evidence, not a DGX runtime observation. Download, model service, GPU benchmarks and existing user processes were untouched by the assistant.

## 2026-11-05 — H-012 — Git-first temporary operator script rule and first P1 bundle

- User requested grouping post-download steps 1–3 into one script, committed in GitHub so the DGX operator only needs a Git Pull and single script invocation, with a separate temporary scripts directory. Follow-up explicitly requested that this **become a permanent documented project rule**.
- Added D-016 and OPERATING-RULES R1D: use `scripts/temporary/` for scoped tested throwaway wrappers; source commit + CPU checks → operator's own `git pull --ff-only` after preexisting processes finish → one wrapper for inspect → individually approved Wizard verify/bench → structured evidence. No implicit setup/download/stop/start/cleanup, no logs in Git/HF cache, no secret upload, no self-removal.
- Staged `scripts/temporary/p1-post-download.sh`, `p1_post_download.py`, README and mocked `tests/test_p1_temporary_cpu.py`; CI workflow and executable-bit test extended. **Runtime DGX operations NOT_RUN** in this GitHub-only session; result/CI to be verified at exact new HEAD.


## 2026-11-05 — H-011 — Rename numbered Wizard stages into capability groups

- User clarified that model P1/P2/P5 belong to one **Model management** menu with descriptive model submodules; P3/P6 belong to one **Model switching** menu with transition submodules; P4 storage and P7 operations are separate domains.
- Source commit `571e1c204d76bcb66b9e02cb1315ac775013a130`: move `wizard/menus/p1.py`–`p7.py` to `models/flash_next.py`, `models/qwen_27b.py`, `models/orcarouter_flash_next.py`, `switching/flash_next_27b.py`, `switching/orcarouter_27b.py`, `storage/flash_next_cleanup.py`, `operations/system.py`; update grouped two-level menu, CLI router, flat compatibility alias registry, 32 router CPU tests.
- **CI 2/2 SUCCESS**, 112/112 CPU tests per job; historical P1–P7 CLI flags and `wizard/p1.sh` remain compatible. No assistant DGX Docker, GPU, checkpoint/download, model switching or cleanup operation. Source-only P2–P7 still blocked.
- Active docs updated; D-015 supersedes D-014 numbered filename architecture, while original roadmap order P1→P7 remains unchanged.


## 2026-11-05 — H-010 — P1 JSON-mode hardening and final CPU CI

- Follow-up commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b` hardened P1: no guided prompt in `--json` mode, verified guided default for TTY, added two router regression tests, committed modular CLI contract/handoff.
- GitHub Actions push and PR `manifest` jobs both **SUCCESS**; per job 15 manifest + 10 inventory + 13 Flash launcher + 1 script mode + 41 P1 + 23 Wizard router = **103/103 CPU PASS**. [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961837000/job/127029761586); [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961842431/job/127029780582).
- No actual DGX Wizard GPU/API/benchmark operations, model switching, cleanup or gateway changes occurred. P2–P7 menu skeleton SOURCE_ONLY and execution BLOCKED. Original user download/setup/serve chain not interrupted.



## 2026-11-05 — H-009 — Build P1–P7 Wizard menu/router before operational phases

- User requests complete up-front Wizard **architecture** and per-stage/menu source modules rather than one monolithic file; direct CLI/JSON automation in addition to guided menu for user-mediated DGX operations.
- Added root executable `wizard.sh`, `wizard/main.py`, `wizard/menus/{common,p1,p2,p3,p4,p5,p6,p7}.py`; existing `wizard/p1.sh` retained as compatibility shim. P1 reuses existing guarded source workflow, P2–P7 status/plan interfaces explicitly `BLOCKED` for execution pending pinned recipes/source/runtime/rollback acceptance.
- First source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`, two GitHub Actions SUCCESS, **101 CPU tests per job** (21 new routing tests and 80 previous).
- Follow-up source hardens P1 JSON mode and adds two regression tests; verify final branch CI before release claim.
- No DGX Docker/GPU/service interaction, model download or deletion by assistant. User-supplied previous download/queued setup chain preserved. Actual P1–P7 runtime acceptance remains incomplete.


## 2026-11-05 — H-008 — P1 Wizard code batch and operator build/download evidence

- Operator-provided DGX log: Docker image `qwen38-flash-dgx:v0.32` built (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`), port :8000 free at earlier read-only scan, model download 9/25 = 36% in last visible line. OpenWebUI/Portainer kept running. Shell has queued `serve/wait/test` after `./flash setup default`.
- Added `scripts/manager/p1_assets.py` (read-only shard/index/cache/image integrity), `p1_wizard.py` (guarded actions, approval plan hashes, API smoke, immutable JSON evidence), `p1_bench.py` (bounded streaming TTFT/latency/tokens), `wizard/p1.sh` (guided and noninteractive), isolated mock CPU tests and GitHub Actions coverage.
- First source commit `c625a49276272e90d19ab6367f580a0230754890` applied; two GitHub Actions runs SUCCESS with 80/80 CPU tests each (41 new P1 + 39 baseline). No assistant-executed Docker, HF cache, GPU or API action. P1 runtime remains `NOT_RUN`. Do not start a duplicate download or interfere with existing operator setup.


## 2026-11-05 — H-007 — User reports NVIDIA Flash-Next checkpoint download in progress

- At 11:46 KST user reports `nvidia/Qwen3.8-Flash-Next-NVFP4` download is **still running**. This is USER_REPORTED, not independently inspected on DGX. Completion percentage, cache path, revision and storage remaining unknown.
- Recorded `DOWNLOAD_IN_PROGRESS` in CURRENT-STATE, priority guard in NEXT-ACTIONS and E-20261105-04 in evidence ledger. `DOWNLOAD_COMPLETE`, `HYBRID_READY`, GPU, API and benchmarks remain **NOT_VERIFIED / NOT_RUN**.
- Do not launch a competing download, `./flash setup default` or hybrid preparation while it may modify active weights/cache. P1 Wizard code and synthetic CPU tests can proceed while assets download.
- GitHub documentation change only: no Docker, image, download, cache or GPU operations performed by this session.

## 2026-11-05 — H-006 — Confirm all P1–P7 stages must be Wizard-driven

- User explicitly confirmed exact sequential target: Wizard Flash-Next install/run/bench → Wizard 27B install/run/bench → Wizard Flash-Next ↔ 27B switching → optional approved Flash-Next cleanup if storage insufficient → Wizard Orcarouter-Flash-Next install/run/bench → Wizard Orcarouter ↔ 27B switching → integrated Wizard operations release.
- Clarified `P4=SKIPPED_NOT_NEEDED` when disk allows; no automatic deletion. External port :8000 is the desired stable API entrypoint; actual DGX occupancy and activation remain NOT_OBSERVED.
- Promoted the sequence into `handoff/README.md`, `OPERATING-RULES.md`, `NEXT-ACTIONS.md`, `CURRENT-STATE.md`, `DECISIONS.md`, `SESSION-START-PROMPT.md` and master plan. First unfinished implementation remains **P1 Wizard end-to-end**, not merely manual `flash serve`.
- Documentation-only GitHub commit; no DGX, GPU, Docker operations, benchmark, deletion or model switch. Previously verified code HEAD `017319a`: 39/39 CPU tests in each of two successful GitHub Actions runs; recheck new commit checks separately.

## 2026-11-05 — H-005 — Restore executable bits and record CI failure

- Commit `7e8f4a109a04c130a5dba0d73e3ece0881d85478` had a real **CI FAIL**: manifest 15/15 PASS; inventory 10/10 PASS; shell launcher 9/13 PASS and 4/13 FAIL, exit 126 because `flash`/`scripts/serve.sh` lost executable permissions in GitHub tree update.
- Restored executable mode `100755` for both scripts; added a CPU regression test asserting launch scripts are executable and `bash -n` workflow checks. Rerun CI on new HEAD; preserve failed evidence instead of rewriting.
- No DGX, Docker runtime, GPU, API port or model state changed.

## 2026-11-05 — H-004 — Flash-Next on legacy :8000 and source-safe inventory

- User reports previous operating services deleted; current Docker/ports/images/weights on DGX **NOT OBSERVED**. Do not treat past Orcarouter container or model ID as current deployment state.
- Updated `flash`, `profiles/default.env`, `scripts/serve.sh` so NVIDIA Flash-Next default profile exposes host port 8000 and served name `qwen3.8-flash-next`. The upstream profile continues Hybrid+YaRN+MTP2; no SGLang.
- Replaced implicit `docker rm -f "$NAME"` with refusal to replace any existing exact Docker container name. No automatic removal on failed launch.
- Removed historical hard-coded 8000/name manifest bans. Added `scripts/manager/inventory.py` (read-only Docker/ss/disk/cache/mount reconciliation), Wizard `00-doctor.sh`/`10-plan.sh` wrappers, deterministic synthetic CPU tests, CI workflow coverage.
- This commit is SOURCE-only; tests CI verification to follow actual commit. No DGX GPU, cache mutations, download, Docker actions or API benchmark. Updated rules, decisions, contracts and runbook.

## 2026-11-04 — H-003 — N1 source-only manifest validation

- Added YAML recipe JSON Schema Draft 2020-12, CPU-only validator, pinned SHA/digest constraints, historical protected name/port denial, no approval bypass.
- Added deliberately invalid 27B candidate, synthetic fixture, 15 isolated CPU tests and new GitHub Actions CPU workflow. No Docker, GPU, actual DGX or model/cache/port changes.
- Ran: python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -q -> **15/15 PASS**; 27B candidate -> expected FAIL (exit 2); synthetic fixture -> schema PASS (exit 0) with launch_authorized=false.
- Updated CURRENT-STATE, NEXT-ACTIONS, EVIDENCE-LEDGER, DECISIONS and planning contracts. Draft PR #1 still requires CI readback and review; N2 and all operational testing remain outstanding.

## 2026-11-04 — H-002 — Documentation committed and draft PR opened

- Verified the new planning branch was 1 commit ahead of `main`, 10 tracked doc files, all under `docs/` and `handoff/`.
- Commit `76cd8dae16b0f34e47c353b56b6e9dbcc5fcde25` created the initial document set.
- Opened [Draft PR #1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1); no merge. At original commit check, GitHub showed 0 check-runs/0 PR workflow runs; **not CI PASS**.
- Corrected illustrative 27B recipe to keep PLE semantics `UNVERIFIED_FOR_27B` rather than assuming no PLE; still no runtime/CPU tests.
- Updated live handoff state, next actions and evidence. All work was GitHub-only.

## 2026-11-04 — H-001 — Recipe/Wizard migration planning initialized

- Confirmed user preference: **vLLM 0.32 only**, no SGLang, one large target at a time by default.
- Created planning branch `feature/recipe-wizard-handoff` from fork `main@b0aa8b77604139557169387b2fa8386355d8b651`.
- Preserved parallel `feature/orcarouter-bf16-adapter` design branch.
- Defined P0→P7 roadmap, manifest separation, wizard steps, protected runtime boundaries, gated checkpoint deletion and switch/rollback semantics.
- Added a standard entrypoint, living current state, evidence ledger, decisions, next tasks and new-conversation prompt under `handoff/`.
- **Tests:** documentation/source review only. No new CPU/CI/GPU/benchmark runs; no Docker, HF weights, model or service changes.
- PR/CI state should be read from GitHub; do not infer a merge.

## Future entry template

`YYYY-MM-DD — H-NNN — Subject`: exact changes, files, branch/commit, PR, test outcomes, external effects, remaining blockers. Newer entries should be placed **above** older entries while preserving them.
