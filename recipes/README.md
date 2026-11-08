## 2026-11-08 — Shared Wizard manifest registry and managed Orcarouter PLE

**Implemented (source/CPU):** `runtimes/manifest-registry.json` is the Wizard's canonical shared registry for service policy, model discovery, the canonical 27B recipe, the Orcarouter source-only recipe, YSLAB compatibility and a **new first-class PLE asset registry** `runtimes/ple-assets.json`. `scripts/manager/manifest_registry.py` centralizes bounded strict JSON loading, duplicate-key/non-finite/symlink rejection and all model/recipe/PLE/donor/service cross-reference checks; `./wizard.sh manifest status --json` and `./wizard.sh manifest validate --json` are read-only and do not check the GPU. PLE asset `orcarouter-bf16-ple` is now referenced by the P5 recipe, service policy and model discovery; canonical `scripts/manager/ple_assets.py` performs local pinned header/weight-map checks and reports metadata status independent of GPU. Wizard P5 status/doctor, model installed list, service status and model-first selector expose the asset appropriately. These interfaces **never authorize deletion/overlay, Docker mutation or runtime activation**.

[Source commit a17b3618](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/a17b3618fab98aa5b849359d464c0d7698fae4a0) passed [Actions #42433160630](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42433160630), including 996 executed CPU test cases across 44 unittest invocations (duplicates included), manifest registry contract/drift and new PLE asset mocks. Final model-first selector/documentation follow-up requires independent CI. Read detailed decisions and commands in `docs/WIZARD-MANIFEST-REGISTRY-AND-PLE-ASSETS-20261108.md`.

**Actual DGX evidence:** the operator's supplied previous-HEAD console output showed `qwen38-27b` serving `qwen3.8-27b` on :8000, Orcarouter pinned BF16 PLE 128/128 header/shape PASS, MTP 31/31 donor tensors and all 3 donor SHA256 PASS; GPU Orcarouter not started. This observation predates the manifest code and does not verify its new DGX integration. The P5 GPU loader/overlay/bench/rollback and P8 release remain NOT_RUN. Preserve 27B, :8000/ONE_ACTIVE_MODEL_ONLY, all HF assets and historical receipts; P3 replay/P4 delete/P6 switch/P8 fault/PR merge remain unauthorized.

---

## 2026-11-08 — P5 vLLM 0.32 source patch candidate; image not built

Verified the official `vllm-project/vllm@v0.32.0` Qwen4Exp `model.py` and `mtp.py` static anchors (one occurrence each). v0.32 `CompressedTensorsConfig.ignore` is separate from `ignored_layers` and `exclude_modules`, requiring a scoped remap for donor MTP BF16 bypass.

`src/p5_patch_qwen4exp_v032.py` is the **P5-only optional source patch** for quantized LM head, compressed-tensors ignore remap, and strict 31/31 native BF16 MTP name/dtype guard. Other models are unaffected when `VLLM_P5_ORCAROUTER` is unset. The source candidate requires exactly installed vLLM 0.32.0 and fail-closed anchor matching. `Dockerfile.p5.candidate` has no fixed base; its required `P5_QUALIFIED_BASE_IMAGE` must be provided only after independently verified Blazux v0.32 image pin and explicit image-build permission. `P5_EXPLICIT_IMAGE_BUILD=1` permits source patching *inside that isolated candidate image build only*; **no image has been built or loaded**. `tests/test_p5_vllm032_patch_cpu.py` validates pure-source patch behavior without Docker/GPU. Actual ARM64 ABI, GPU model load, MTP0/MTP2 API, OpenWebUI and benchmark remain **NOT_RUN**.

This is not permission to run `docker build`, generate a multi-GB BF16 MTP overlay, interrupt the active 27B on :8000 or merge Draft PR #1. Existing standalone source-only one-shot `--gpu-trial` stays BLOCKED. Await final CI for this addition before reporting test PASS.

---

## 2026-11-08 — P5 source implementation and acceptance update (not GPU released)

P5 source was committed to the existing feature branch and Draft PR #1 as [33adec1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/33adec182e97a8eac0d5584bdf73f1448bdd84f2), with [GitHub Actions 42429745463](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463) **SUCCESS** including the new 20/20 CPU/Fake-DGX tests and `--cpu-only --json` PASS. Additional detailed per-case JSON and profile inspection enhancements require independent follow-up CI.

Implemented source: `recipes/qwen38-orcarouter.runtime.json` (pinned, **unqualified**, launch forbidden), imported YSLAB safetensors/manifest/BF16 PLE audit and immutable MTP overlay code under `scripts/p5_vendor`, donor 3-shard SHA256 / 31 BF16 name audit when local files exist, distinct MTP0/MTP2 candidate recipes, Wizard `p5` and `model orcarouter-flash-next` routes, `scripts/temporary/p5-one-shot-acceptance.sh`. The vendor overlay builder is **not** executable via CLI and no HF asset changes were authorized. Prior Blazux BF16 PLE source markers pass static inspection only; compressed-tensors and MTP2 runtime ABI/quantized lm_head/CUDA graph compatibility in actual vLLM 0.32 remain unqualified.

No DGX command/active-state reread or GPU/API/benchmark/rollback was performed in this session. All live P5 stages are NOT_RUN, `--gpu-trial` permanently BLOCKED until a separate operator approval and verified image/rollback implementation. Preserve 27B and :8000/ONE_ACTIVE_MODEL_ONLY, other models/caches, P3 historical receipts, no P4 deletion/P6 switch/P8 tests or Draft PR merge. New source/runbook: `docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md`.

---

## 2026-11-07 — Canonical 27B Native Tools runtime recipe (supersedes separate variant switch design)

The user chose **one canonical `qwen38-27b` container**, not persistent original-vs-native two-container switching. New `recipes/qwen38-27b.runtime.json` pins the ACTUALLY DGX-verified `qwen3_coder`, `qwen3`, NVIDIA Jinja, exact vLLM image and :8000 launch profile. Desired `runtimes/service-policy.json` now references this canonical recipe; it does NOT mean existing Docker `Config.Cmd` was changed.

The separate `recipes/qwen38-27b-native-tools-v1.candidate.yaml` remains a historical incomplete trial candidate, **not the production recipe**. The existing `recipes/qwen38-27b.candidate.yaml` remains intentionally invalid/historical; neither should be launched. One-shot native tool inference was REAL DGX PASS, but canonical migration is **NOT_RUN** until explicit fresh operator TTY approval.

Use `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --plan` first, then `--execute` only after downtime and verified-old-container-deletion acknowledgement; successful migration validates normal chat/tools/SSE, completes a fresh 3-request benchmark, atomically replaces **only the latest active benchmark pointer** and deletes ONLY verified stopped old backup Docker container. Existing benchmark receipts, P3 A/B/C receipts, images and HF caches survive. `--status` is a separate read-only post migration audit. See [canonical runtime migration runbook](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md).

---

## 2026-11-07 — P2-FINAL Native Tools V1 separate candidate (NOT LAUNCHABLE)

`recipes/qwen38-27b-native-tools-v1.candidate.yaml` declares a distinct container name `qwen38-27b-native-tools-v1` using the same pinned NVIDIA 27B and :8000 **only after** stopping the original. This second YAML is deliberately schema-INCOMPLETE (unverified exact image/source), source-only and NOT in the live service manifest. Never use `docker run` from a preview. Use `bash scripts/serve_27b.sh --tools-variant-plan` for fail-closed read-only inspection (expected exit code 3); see `docs/P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md`. Original `qwen38-27b`, P3 receipts, Flash and HF caches remain protected. A source recipe cannot grant downtime consent.

---

# Recipe registry (P0/N1: source schema only)

Recipes are YAML checked against schemas/recipe.schema.json by
scripts/manager/manifest.py. This branch does not provide a model loader,
wizard switch action, or permission to modify the running service.

The 27B candidate qwen38-27b.candidate.yaml is deliberately invalid until
actual source/pins/PLE are verified. Synthetic test SHA values under
tests/fixtures are placeholders, not a model or image. Validity of a recipe
means structural checks only; it does NOT prove checkpoint provenance,
model support, operational safety, or permission to launch.

Install CPU-only requirements-manager.txt, then run:

    python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -v
    python3 -m scripts.manager.manifest validate recipes/qwen38-27b.candidate.yaml

Candidate exit status MUST be 2 (FAIL). Even exit 0 cannot authorize
Docker actions, model downloads, GPU use or deletion.
The former static Orcarouter name/8000 bans were removed on 2026-11-05 after user reported removal. N2 inventory now checks actual Docker container names and socket listeners; source format PASS is never permission to launch.

## P2 27B local cache discovery (source-only; no download)

`nvidia/Qwen3.8-27B-NVFP4` is the currently selected candidate checkpoint ID. The prior RadixArk DGX inspection is historical and is not NVIDIA cache evidence. Its published
model files are not proof of pinned vLLM-0.32 support or local availability.
To inspect *existing* files and symlinks without Docker, sockets, model download
or GPU calls, run:

```bash
./wizard.sh model 27b status --inspect-cache --json
```

The JSON `inspection` reports refs/main/master, indexed shard file existence,
quantization metadata presence and incomplete transfer counts. A
`SOURCE_FILES_PRESENT_UNPINNED` result is deliberately **not** P2 READY.
The candidate recipe still fails schema validation until exact source SHA,
model revision, architecture support, image SHA256 digest and runtime
compatibility have actual evidence. All `prepare`, `start`, `verify`,
`benchmark` actions remain BLOCKED.

## NVIDIA 27B pinned acquisition (updated 2026-11-05)

The P2 selected repository is `nvidia/Qwen3.8-27B-NVFP4`. Its immutable source revision is `482ca0f3832238542f8f5295dde86b5f22711d80`, as verified on the official Hugging Face tree. The candidate recipe pins this revision and desired `:8000` port, but **remains intentionally INVALID** until source runtime SHA, image digest, architecture/quantization loader, PLE/MTP and DGX API validation are reviewed. `nvidia/Qwen3.8-Flash-Next-NVFP4` uses the same host API port when active; both cannot run concurrently. Pinned source download is separate and can run while Flash-Next serves.

Read-only plan: `./wizard.sh model 27b plan --for-action download --json`. Guided operator approval: `./wizard.sh model 27b download --guided` (must type fresh full plan ID). Both are backed by the same Wizard download implementation. SOURCE and CPU verification are not actual DGX download/GPU readiness. Consult `docs/P2-27B-WIZARD-OPERATIONS.md` and `runtimes/service-policy.json`.

