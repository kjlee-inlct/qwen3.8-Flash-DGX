# P3-D–G second DGX read-only observation: hidden socket PIDs, Flash fp8hybrid

**Date:** 2026-11-07 KST. Operator-provided terminal JSON after pulling the preceding D/E diagnostic fixes. The batch made **no Docker/API/GPU mutation**. Current real service was canonical NVIDIA 27B at :8000; historic P3-A/B/C remain completed and immutable.

## Second actual DGX `--run` observations

| Stage | Exact returned status | New evidence / interpretation |
| --- | --- | --- |
| P3-D | `BLOCKED`; `issues=["HOST_PORT_PROCESS_PID_UNAVAILABLE"]` | Docker reports sole managed GPU container and host 8000 owner `qwen38-27b`. NVIDIA compute PID `2051842` has `gpu_process_exclusivity_verified=true`. `ss -H -ltnp sport = :8000` returned two actual `LISTEN` rows, `0.0.0.0:8000` and `[::]:8000`, with **no `users:(...pid=...)` data**; `ss_returncode=0`; `observed_port_pids=[]`. The socket exists, but process ownership is NOT established in unprivileged `ss` evidence. This is not proof that port 8000 belongs to another application. |
| P3-E | `BLOCKED`; `FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED`, `FLASH_CHECKPOINT_REVISION_UNVERIFIED` | Preserved Flash exact Docker ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; observed `Config.Entrypoint=["vllm","serve"]`, `Config.Cmd` checkpoint is `.../snapshots/fc694b54fb0174e0913e6adf86691ef85a4ead47-fp8hybrid`. The source pinned 40-hex HF revision is `fc694b54fb0174e0913e6adf86691ef85a4ead47`; `-fp8hybrid` denotes a locally prepared **derived view**, not a different HF source revision. Observed `--max-model-len 500000`, `--max-num-seqs 8`, `--gpu-memory-utilization 0.80`, `--speculative-config {"method":"mtp","num_speculative_tokens":2,"max_model_len":500000}`. HF mount is bind `/home/inlc/.cache/huggingface:/hf`, `read_only=false`. Model ID `qwen3.8-flash-next`, port 8000, GPU all, offline env present. Canonical reinstall recipe still NOT qualified; raw argv is not equivalent to a promoted recipe. |
| P3-F | `SOURCE_CPU_PASS_NOT_RELEASED`; `issues=[]` | Actual DGX local CPU suites: 28 + 17 + 21 + 38 + 24 = **128 / 128 PASS**. Production lifecycle remains unreleased. |
| P3-G | `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`; `issues=[]` | Live ID aware source `27b/CANONICAL_RECIPE` → preserved `flash-next/HISTORICAL_P3_INSTANCE`, operating journal `VERIFIED/COMMITTED`. No execution, no rollback fault injection. |

Overall `status=BLOCKED`, `blocked_stages=["P3-D","P3-E"]`, `acceptance_complete=false`, `P3_DG_EXIT=3`. Historical one-off transfer receipts are distinct from current recurrent switch acceptance.

## Root causes and source-only corrections

1. **P3-D:** The initial one-listener bug was fixed in the prior patch and the new observation correctly displays two listeners. However, the `ss` PID fields are missing under the operator's current privilege level. It would be incorrect to mark `port_process_ownership_verified=true` from Docker bindings or healthy API alone. New optional **`--sudo-ss`** on the single-entry runner explicitly permits only `sudo -n ss -H -ltnp sport = :8000` when the normal `ss` output lacks PIDs. It refuses changed IPv4/IPv6 local socket sets and only accepts real process attribution by cgroup or Docker proxy /proc + exact network-port mapping. `sudo` is NEVER called in default `--run`, `--plan` or `--cpu-only`; `sudo -n` never prompts and a privilege issue remains a BLOCKED diagnostic rather than silently escalating. No model mutation occurs.
2. **P3-E:** The existing `scripts/serve_flash-next.sh` selects a prepared `-fp8hybrid` snapshot from the pinned original source. `scripts/prepare-hybrid.sh` creates `.prepared` in that derived directory after conversion. The P3-E observer now recognizes exactly the committed pinned NVIDIA Flash 40-hex source plus **`-fp8hybrid`**, reporting separately `source_revision`, `checkpoint_variant=LOCAL_PREPARED_FP8HYBRID`, and `hybrid_preparation_verified`. Read-only checks require `.prepared`, `config.json`, `tokenizer.json`, `tokenizer_config.json` and `model.safetensors.index.json` to exist in that exact source-derived view. Missing preparation evidence or any other revision still BLOCKS. **This merely validates observed source lineage**, not file integrity or serving correctness and NEVER automatically promotes a reinstall recipe.
3. **P3-E remaining gate:** Even if the prepared Hybrid view matches, **`canonical_recipe_registered=false`** remains factual until a separately reviewed/versioned Flash lifecycle recipe and end-to-end real reinstall/recovery acceptance exist. At best, this read-only stage should return `DRAFT_REVIEW_REQUIRED`. Existing writable host HF cache and legacy vLLM arguments remain explicit review advisories, not permission to recreate the preserved model.
4. **P3-F/G:** Code and old P3 receipts unchanged. P3-G cannot become actual PASS from this audit; it still requires separately authorized real roundtrip and controlled failure/recovery verification.

## Source-only verification

GitHub Actions [42371861344](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371861344): **SUCCESS, 846 / 846 CPU/Fake-DGX tests across 37 reported groups** on source commit `7f9a0266d0fe591ab8435f89a8d97b71b61c739f`. New regression fixtures simulate derived pinned `-fp8hybrid` with/without `.prepared`, wrong revisions, unprivileged `ss` with hidden PIDs, explicit noninteractive privileged `ss`, and listener-set mismatch.

This is **not** an actual rerun on DGX of the newest source.

## Next single command on DGX (read-only)

Pull the branch after confirming `git status --short` is clean:

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff

# Try normal, non-elevated dry-run diagnostics:
bash scripts/temporary/p3-d-g-acceptance.sh --run \
  --report /tmp/p3-d-g-v3-$(date +%Y%m%dT%H%M%S).json
```

If D remains `HOST_PORT_PROCESS_PID_UNAVAILABLE`, an operator **may explicitly choose** to run the same non-mutating batch with privileged socket introspection (no full root execution of the Wizard):

```bash
# Optional, operator-initiated privilege validation, may prompt once for sudo credentials:
sudo -v &&
bash scripts/temporary/p3-d-g-acceptance.sh --run --sudo-ss \
  --report /tmp/p3-d-g-v3-sudo-ss-$(date +%Y%m%dT%H%M%S).json
```

`--sudo-ss` uses only `sudo -n ss` and will never request credentials itself. No `--execute`, Docker restart/stop/rm, checkpoint rewrite, model download, P3-A/B/C replay or production release.

Review the new JSON: D `observed_port_listener_rows`, `observed_port_pids`, `port_pid_attribution`, `sudo_ss_requested`, E `source_revision`, `checkpoint_variant`, `hybrid_preparation_verified`, `issues`, `advisories`. If E view is intact, the correct non-final status is still **`DRAFT_REVIEW_REQUIRED`**. F source pass and G preview pass should remain separate from eventual real DGX acceptance.
