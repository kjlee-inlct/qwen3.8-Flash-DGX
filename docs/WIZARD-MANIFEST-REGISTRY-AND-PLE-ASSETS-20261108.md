# Shared Wizard Manifest Registry and Managed PLE Assets — 2026-11-08

## Decision and ownership

The Wizard manifest is a **shared foundation**, not an Orcarouter-only status JSON. The canonical index is `runtimes/manifest-registry.json`; the pure, fail-closed controller is `scripts/manager/manifest_registry.py`. It currently indexes six versioned manifest contracts:

| Registry key | Canonical document | Ownership |
| --- | --- | --- |
| `service_policy` | `runtimes/service-policy.json` | Desired single-GPU-model lifecycle and :8000 service identities |
| `model_discovery` | `runtimes/model-discovery.json` | Read-only pinned caches, managed model registration and optional legacy views |
| `ple_assets` | `runtimes/ple-assets.json` | Immutable source PLE asset identity, geometry, cache protection and verification scope |
| `orcarouter_recipe` | `recipes/qwen38-orcarouter.runtime.json` | Unreleased compressed-tensors vLLM0.32 candidate, MTP0/MTP2, donor checkpoint |
| `27b_recipe` | `recipes/qwen38-27b.runtime.json` | Canonical tested Native Tools 27B recipe; **untouched** |
| `yslab_compatibility` | `scripts/p5_vendor/compatibility.json` | Pinned third-party BF16PLE/donor technical reference |

All readers use the shared bounded, strict version-1 JSON loader: no duplicate keys, NaN/Infinity, symlink manifest paths, unknown registry paths, oversized files or mutable path injection. The registry cross-validator checks model-repo/pinned-revision alignment, service API and single-model policy, 27B canonical identity, P5 unreleased flags, PLE asset IDs and exact source geometry, 31-donor/three-shard identity and vendor reference metadata. **Cross-reference drift makes validation FAIL**, not a fresh execution approval.

`runtimes/ple-assets.json` registers `orcarouter-bf16-ple` with revision `3a3b63161c0745390e5270179af42e46efc70799`, direct BF16 PLE 128 shards/320001536 rows/width160/102400491520 bytes, and consumers `mtp0`/`mtp2`. It has independent immutable-source lifecycle and forbids implicit deletion. The same ID appears in P5 recipe, model-discovery and service-policy; hard-coded implicit PLE ownership has been removed from new inspection routes. Donor MTP remains pinned to `RadixArk/Qwen3.8-Flash-Next-NVFP4@7b719225242aacd3dbd3f9407468c2ee9a9d2594` in P5 recipe/YSLAB reference and is cross-validated.

## The three distinct truths

1. **Declarative manifest integrity**: `./wizard.sh manifest status --json` or `./wizard.sh manifest validate --json` returns `status=PASS` **only for this source graph**, with each file and the cross-reference check reported. `runtime_qualified=false`, `source_snapshot_verified=false`, `gpu_verified=false`. Manifest changes alone cannot authorize start.
2. **Observed local asset integrity**: `./wizard.sh model list --installed --json` returns a per-model `ple_asset` including registration, expected geometry, pinned source, `metadata_verified`, `source_state` and `runtime_mmap_status=NOT_RUN`. `./wizard.sh p5 status --json`, `./wizard.sh p5 doctor --json` and P5 `--read-only` use the same canonical PLE inspection function. Actual pinned safetensors header/weight-map audit may return PASS while GPU runtime remains NOT_RUN. No checkpoint full-file SHA claim is made for PLE.
3. **Live service truth**: `./wizard.sh service manager status --json` reports the *current* Docker/API identity and adds `manifest_integrity` and `registered_ple_assets` as separate fields. A service at :8000 is not evidence that dormant Orcarouter PLE is loaded into its GPU. Live identity is never overridden by a stale Git manifest.

## Safe commands and acceptance

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh manifest validate --json
./wizard.sh manifest status --json
./wizard.sh model list --installed --json
./wizard.sh p5 status --json
./wizard.sh p5 doctor --read-only --json
./wizard.sh service manager status --json
bash scripts/temporary/p5-one-shot-acceptance.sh --cpu-only --json
bash scripts/temporary/p5-one-shot-acceptance.sh --read-only --json
```

These interfaces do not mutate Docker/GPU/HF assets, do not auto-generate overlays, and do not stop the active 27B. The local asset audit reads safetensors **metadata** and may perform considerable filesystem I/O; `--read-only` additionally hashes the three pinned MTP donor shards. No token contents should be logged. Manifest validation does not perform host checks.

CPU/Fake-DGX regression tests: `tests/test_manifest_registry_cpu.py` exercises registry and reference drift, malformed JSON, unsupported paths, CLI read-only guarantees. `tests/test_p5_ple_manifest_cpu.py` covers PLE source identity, geometry, inventory and Wizard status, synthetic absent/malformed snapshots and no false GPU promotion. Existing tests and P1–P4 features remain on the CI matrix. CI is authoritative for source acceptance and must be rechecked after each commit.

## DGX read-only evidence supplied by operator

The 2026-11-08 operator console recorded `8f8ad0c2868d3f124f247d42ee47f63824852694` **before this manifest refactor**, with `qwen38-27b` on :8000 serving `qwen3.8-27b` (`LIVE_SERVICE_VERIFIED`). P5 `--read-only` reported pinned BF16 PLE **128 tensors, 320001536 rows, width160 PASS** (checkpoint full SHA not claimed), RadixArk donor **31 BF16 tensors / 3 pinned shards, SHA256 verified PASS**, and preservation of live 27B PASS. Source CPU **29/29 PASS**. These are historical operator observations, not newly generated receipts by this refactor. **This new registry/Wizard layout must be checked on DGX after safe fast-forward**; actual Orcarouter GPU/MTP2/Tools/bench/restore still NOT_RUN.

## Explicitly remaining gaps

The registry exposes desired-state consistency, not deployment completeness: Flash-Next canonical reinstall recipe integration is not qualified, Orcarouter image digest/ABI and GPU launch are not qualified. P5 `launch_allowed=false`, active Orcarouter served ID remains null and the `--gpu-trial` executor is deliberately blocked. P6 generic switching and P8 injected recovery remain separately gated; no historical P3 replay, P4 actual deletion, container/Image/HF cleanup, 27B interruption or PR merge. Any manifest expansion must add a versioned contract and a cross-reference test, never silently elevate `SOURCE_FILES_PRESENT` to `RUNNING_VERIFIED`.
