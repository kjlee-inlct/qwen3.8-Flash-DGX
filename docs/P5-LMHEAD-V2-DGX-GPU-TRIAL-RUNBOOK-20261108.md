# P5 Orcarouter vLLM 0.32.0 — current DGX MTP0 trial, QSA + LM-head v2

**2026-11-08 current superseding instructions.** Earlier sections of `docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md` that refer to the QSA-only adapter/container are historical. Use **this** runbook for the next P5 experiment; never reuse an old plan ID.

## New read-only checkpoint gate — 2026-11-08

**Run this before `p5 trial prepare`.** The checkpoint was not independently readable from this GitHub session (gated HF source); the latest GPU failure must not be promoted to PASS based on external model cards.

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
git rev-parse HEAD

python3 -m scripts.manager.p5_checkpoint_preflight --json \
  | tee /tmp/p5-lmhead-checkpoint-preflight.json
```

This single CPU-only, no-Docker/no-GPU/no-network judge runs manifest validation, the pinned `config.json` and `model.safetensors.index.json` audit, bounded safetensors **header-only** reads for `lm_head.weight` and `lm_head.weight_scale`, and `test_p5_*_cpu.py` regressions. It does **not** read weight payloads or change a cache. It returns `PASS_SOURCE_ONLY` only when its checks pass; even this means **no GPU registration, MTP0 inference or PLE mmap qualification**. `BLOCKED` (exit 3) forbids image preparation and approval planning.

The `p5 trial prepare` and `p5 trial plan` metadata gate now invokes the same pinned head audit; plan/execute cannot bypass it. Specifically, a checkpoint containing a FP8 scale but listing LM-head in `quantization_config.ignore`, lacking an explicit head-target FP8 group, or having inconsistent indexed safetensors headers is **BLOCKED**. Generic `Linear` targets alone do not establish matching for `ParallelLMHead` in vLLM 0.32. The audit is intentionally fail-closed and may require further engine ABI work even on a metadata PASS. Do **not** edit or rewrite checkpoint weights/config to force a pass.

If this tool returns a blocking code, share the redacted JSON fields `checkpoint.lm_head`, `checkpoint.issues` and `cpu_tests` for source analysis. No approval or GPU run should be attempted until the mismatch is resolved in a new isolated, versioned adapter.

## Evidence boundary and latest observed failure

- **Actual operator-provided DGX, checkout `247d31de79da9fda3b2dcea41d7c96141d5a766b`**: QSA #62318 derived image built and MTP0 GPU trial launched. The initial QKV/indexer quantization exception no longer blocked constructor creation; safetensors shard progress reached 15/17 before a *new* `ValueError: There is no module or parameter named 'lm_head.weight_scale' in Qwen4ExpForCausalLM`. Available LM-head params: only `lm_head.weight`. Trial receipt: `~/.local/state/blazux-wizard/p5-live-trial/trial-20261108T054106528164Z.json`, `FAIL_NO_ROLLBACK`, `gpu_verified=false`, `ORCAROUTER_CONTAINER_EXITED`. This confirms **neither GPU load nor inference success**, and does not prove BF16 PLE mmap activation.
- Container `qwen38-orcarouter-qsa62318` exited(1), original failed `qwen38-orcarouter` exited(1), original `qwen38-27b` exited(0); last observed :8000 unserved. This is *last reported observation*, not current live inventory. Never silently restart 27B or remove the preserved containers.
- **GitHub source candidate v2**: `src/p5_qsa_quant_backport_v032.py` remains the #62318 / Blazux FP8-hybrid QSA fix; `src/p5_lm_head_quant_backport_v032.py` additionally injects `quant_config=self.quant_config` into the vLLM 0.32.0 Qwen4Exp LM-head constructor in a **new, isolated image**. vLLM 0.32's ParallelLMHead already has relevant linear metadata, so do not apply the YSLAB *older-development-image* metadata patch globally. The new source fix is **CPU/CI validated, not yet DGX-build/GPU qualified**.
- **Quantization warning:** constructor wiring alone does **not** guarantee that `lm_head.weight_scale` is registered. The pinned checkpoint's actual `quantization_config` targets, `ignore` list and weight keys must be inspected. If `lm_head` is ignored while a scale tensor exists, treat as a **blocked format/loader mismatch**; do not silently remove an ignore entry, rename/discard a scale tensor, or assume a legacy recipe solves it. A forum-posted configuration is external evidence, not proof of this pinned snapshot.

## Immutable recipe and image identity

| Field | Current P5 v2 candidate |
| --- | --- |
| Branch | `feature/recipe-wizard-handoff`, fetch fresh HEAD |
| Engine | Blazux vLLM **0.32.0**, no SGLang |
| Candidate adapter | `qwen4exp-qsa62318-lmhead-v032-v2` |
| Candidate Dockerfile | `Dockerfile.p5.qsa62318-lmhead` |
| Candidate image tag | `blazux-p5-orcarouter:qsa62318-lmhead-v032` |
| Candidate container | `qwen38-orcarouter-qsa62318-lmhead` |
| Old QSA-only candidate | `qwen38-orcarouter-qsa62318` — PRESERVE |
| Base image | exact SHA256 ID from existing `qwen38-27b` container; unchanged |
| Checkpoint | `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799` |
| Serving | host `:8000/v1`, `ONE_ACTIVE_MODEL_ONLY`, MTP0 |
| Recovery | development **no automatic restoration** on trial failure |
| Release | false; MTP2, Tools, Vision, benchmarks, P6 switch, P8 fault tests unqualified |

## Operator sequence

First update the checkout and run CPU/read-only checks. The following `prepare` builds and labels an **offline derived image** if absent; it is NOT read-only, but it does not launch a GPU model or change the canonical Blazux source image. Do not run it if image building is no longer permitted.

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
git rev-parse HEAD

./wizard.sh manifest validate --json
python3 -m unittest discover -s tests -p 'test_p5_*_cpu.py' -v
./wizard.sh p5 trial status --json

./wizard.sh p5 trial prepare --json | tee /tmp/p5-lmhead-v2-prepare.json
./wizard.sh p5 trial plan --json | tee /tmp/p5-lmhead-v2-plan.json
```

Stop if manifest, CPU tests, prepare, or plan are not PASS/READY. Confirm **all** of: `prepare.status == PASS`, `plan.status == READY_TO_APPROVE`, `plan.issues == []`, `plan.details.adapter == qwen4exp-qsa62318-lmhead-v032-v2`, original base image digest matches, new candidate digest differs, source identity matches, port/GPU exclusivity gates pass and plan SHA/expiry is fresh. Source may be running 27B or previously exited(0); a running unknown model or an occupied idle :8000 is a hard block.

Inspect the *actual pinned* config and weight map **read-only** before another GPU attempt. Never edit the HF snapshot:

```bash
python3 - <<'PY'
import json
from scripts.manager.p5_live_trial import SNAPSHOT
cfg = json.loads((SNAPSHOT / 'config.json').read_text())
q = cfg.get('quantization_config', {})
ignore = q.get('ignore', [])
groups = q.get('config_groups', {})
print({
  'ignore_lm_head': 'lm_head' in ignore,
  'lm_head_target_groups': [
    key for key, group in groups.items()
    if any('lm_head' in str(target) for target in group.get('targets', []))
  ],
  'quant_format': q.get('format'),
})
PY
```

**Do not equate the above diagnostic with approval or CPU proof that a scale is loadable.** If it reveals an unresolved target/ignore mismatch, stop; first identify the actual LM-head tensor shape/dtype/scheme and source loader path. Do not approve GPU trial merely because `prepare` and `plan` pass.

Only after successful checks and the operator's explicit decision to use the development DGX, obtain a **fresh** plan and approve the exact transaction using the existing Wizard interface:

```bash
./wizard.sh p5 trial plan --json
# Then, only with a VERIFIED fresh 64-hex plan ID:
./wizard.sh p5 trial execute --approve-plan <FRESH_64_HEX_PLAN_ID> \
  --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json
```

This intentionally can leave port 8000 unserved on failure. It never authorizes deleting containers/cache, merging PR #1, P3 replay, P4 live deletion, P6 generic switches or P8 fault/recovery.

## Evidence and acceptance

After a trial, record `git rev-parse HEAD`, `./wizard.sh p5 trial status --json`, `docker ps -a --filter 'name=qwen38-'`, `docker logs --tail 1000 qwen38-orcarouter-qsa62318-lmhead`, the private P5 trial receipt, `/v1/models` and inference result if serving. Avoid tokens or other secrets in Git. `PASS_GPU_TRIAL` requires actual started model + confirmed API identity + bounded Chat response; it does NOT establish MTP2, benchmark, Tool or production release.

## Source-of-truth priority

Actual **latest** DGX report > committed current recipe/manifest/Wizard code > current top-of-file handoff and this runbook > historical P5/P4 starter examples and external YSLAB/forum work. Never promote an old `NOT_RUN` statement into current truth when a later failed trial exists; never misreport a failed GPU attempt as a pass.
