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
