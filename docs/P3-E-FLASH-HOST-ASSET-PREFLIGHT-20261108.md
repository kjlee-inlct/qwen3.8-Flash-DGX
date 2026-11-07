## 2026-11-08 — Real DGX index within file-size cap; weight-map structure/count unknown

Real DGX output confirmed `index_file_size_bytes_observed=31907813` (~30.43 MiB), below `index_file_size_limit_bytes=134217728` (128 MiB). Thus the separate bounded reader successfully reached JSON parsing. It then returned `PARSE_SHARD_INDEX:FLASH_SHARD_INDEX_UNQUALIFIED`, before shard checks.

The original bundled validation `not isinstance(weight_map, dict) or not 0 < len(weight_map) <= 100000` could not distinguish malformed/missing or empty `weight_map` from an otherwise valid but greater-than-100,000-entry map. **Do not claim the tensor count is known from this log.** Source-only follow-up emits safe `index_weight_map_structure`, `index_weight_map_entry_count_observed` and `index_weight_map_entry_limit`, with distinct `FLASH_WEIGHT_MAP_MISSING_OR_WRONG_TYPE`, `FLASH_WEIGHT_MAP_EMPTY`, and `FLASH_WEIGHT_MAP_ENTRY_LIMIT_EXCEEDED` errors.

This does not raise the 100,000-entry policy. The operator should run the same **read-only** command after pulling the branch and report the redacted entry count. Then the actual model profile and bounded-parser memory risk can be reviewed before changing limits. No model files, HF cache, Docker services, P3-G historical state or production release gates are changed.

---

## 2026-11-08 — Actual DGX BLOCKED reason identified: shard index exceeds generic 8 MiB cap

The follow-up actual DGX `python3 -m scripts.manager.flash_host_assets --json` returned:

- `failed_stage=READ_SHARD_INDEX`, `failure_reason_code=FILE_EXCEEDS_BOUNDED_READ`.
- `pinned_command_identity_matched=true`, `prepared_view_path_observed=true`.
- `indexed_shard_count=0`, `metadata_sha256={}`, `template_sha256=null`: **verification not reached**, not proof of missing or corrupt weights.
- No Docker or GPU mutation. Flash canonical reinstall remains **NOT QUALIFIED**, `launch_allowed=false`.

Root cause for THIS diagnostic is the source tool applying the 8 MiB general small-metadata limit to `model.safetensors.index.json`. The index's actual size was not measured in the previous result, so there is no basis to say it is within 128 MiB yet.

**Corrective source approach:** retain the 8 MiB cap for `config.json` and `tokenizer_config.json`, and 256 KiB for template, but apply a separate hard **128 MiB** read cap for the shard index only. Bound the file read itself (`read(limit+1)`) to close stat/read growth races, retain JSON structural and shard-count/path checks, and report nonsecret `index_file_size_bytes_observed` and `index_file_size_limit_bytes`. No unbounded reads, uncapped JSON, shard content reads, launch promotion, or silent limit bypass.

**Next read-only DGX step after updating GitHub branch:**

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
python3 -m scripts.manager.flash_host_assets --json
```

If the dedicated 128 MiB limit or a later stage still blocks, capture `failed_stage`, `failure_reason_code` and the numeric index size/limit; do **not** raise limits again blindly. Even a clean result remains only `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`, not an approved reinstall or P8 acceptance.

---

## 2026-11-08 — First real DGX invocation BLOCKED; refine failure classification

Operator ran `python3 -m scripts.manager.flash_host_assets --json` after the source landed. It returned `FLASH_HOST_ASSET_PREFLIGHT:ValueError`, zero indexed shards, empty metadata hashes, `legacy_hf_bind_writable=true`, and `verified_model_revision=true`. **That does not identify the failing asset.** The original implementation set the last boolean after validating a pinned command/cache mount, *before* checking the prepared files; thus it was misleading as content verification. This is a preflight failure only, not evidence of a broken or unusable model. No service change occurred.

The next source patch:
- Adds `failed_stage` and `failure_reason_code` with allowlisted stage/reason tokens, **never raw errors or host paths**, to distinguish index size, invalid/missing index, prepared marker, dangling shards, tokenizer and chat template failures.
- Adds separate `pinned_command_identity_matched` and `prepared_view_path_observed` observation booleans. `verified_model_revision=false` remains conservative until actual trusted source byte provenance is established; simply matching a directory name or metadata digests does not prove that.
- Preserves read-only inspection, no automatic cache repair, no unapproved Docker mutation and `launch_allowed=false`.

**Next read-only diagnostic after updating code**: `python3 -m scripts.manager.flash_host_assets --json`. Copy only allowlisted JSON. If blocked, use `failed_stage` and `failure_reason_code` to identify the precise branch; do not relax the metadata caps or alter HF assets speculatively.

---

## Verified source test evidence — 2026-11-08

GitHub source: [03cbe4c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/03cbe4cc45a750322c4f99616c85f1061f7b2288), [2b44ccc](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/2b44ccc0237fa34742e28608ad089cb3ca90fe55), and [8e8fcec](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/8e8fcec5acb280e01445a2bd773fc9f4ecedf2f6). Source-only CI [42390619936](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42390619936): **870/870 PASS, 39 groups**, including 5 new Flash host asset tests. Existing DGX 153/153 local CPU execution was **before** this new five-test file; a new DGX-local run is not yet reported. Bounded host utility remains read-only and unqualified for launch.

---

# P3-E Flash host asset evidence — source-only implementation (2026-11-08)

## Latest operator result before this addition

- **P3-D READ_ONLY_PASS** on DGX via explicitly opted-in `--sudo-ss`. Verified IPv4 docker-proxy PID 2560693 and IPv6 PID 2560708, both `QUALIFIED_DOCKER_PROXY`; GPU compute PID 2560905, independent GPU exclusivity true.
- **P3-E DRAFT_REVIEW_REQUIRED**. Actual Flash FP8-hybrid vLLM argv successfully normalized using `FLASH_FP8HYBRID_READ_ONLY_V1`, `cmd_normalized=true`, `cmd_normalization_error=null`, documented-field comparison issues empty. Still `canonical_recipe_registered=false`, host asset/content provenance unqualified, legacy writable /hf mount.
- **P3-F 153/153 DGX-local CPU PASS**. P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN` in this draft runner, while original operator-approved real two-way transfer remains historically PASS/CLOSED. Overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`; `blocked_stages=[]` does not equal real reinstall acceptance.

## New source-only host asset preflight

Run after fetching the latest code, **without service interruption**:

```bash
python3 -m scripts.manager.flash_host_assets --json
```

It calls only read-only `docker inspect` against the preserved `qwen38-flash`, then observes the exact NVIDIA pinned `-fp8hybrid` view within the existing /hf bind. It rejects missing or out-of-cache checkpoint assets, malformed/path-traversing `model.safetensors.index.json`, unknown launch flags, unsafe mount shapes and absent template. It hashes bounded small metadata and the mounted template; it checks existence and file size of index-referenced shard files without reading or hashing large model weights.

The structured output is **allowlisted**. It never emits raw Docker Config/HostConfig, environment values, mount source paths, template contents, secrets, or arbitrary file contents. Some SHA-256 digests are included as evidence fingerprints. A fully observed host asset inventory still deliberately returns `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`, `launch_allowed=false`, `full_docker_runtime_reinstall_qualified=false`; these hashes do **not** establish fresh container creation, security/network equivalence, checkpoint integrity or GPU runtime compatibility.

## Outstanding P3-E/P3-F release gates

- Separate audit of inherited vs runtime environment, complete Docker network/security/restart configuration, image origin vs local image ID, and cache/template ownership and lifecycle; explicit desired spec with immutable hashes and versioned recipe registration.
- Source-only Fake-DGX recreate/restore plans and tests, then **independent** scoped operator approval for any real Flash container creation, API downtime or fallback. Do not make a release decision from this preflight alone.
- `ONE_ACTIVE_MODEL_ONLY`, :8000, vLLM 0.32 and no SGLang. Existing 27B canonical recipe and original P3 receipts remain untouched. P3-G real PASS stays CLOSED. P8 alone owns intentional fault injection, automatic recovery hardware validation, and final operations/release acceptance.
