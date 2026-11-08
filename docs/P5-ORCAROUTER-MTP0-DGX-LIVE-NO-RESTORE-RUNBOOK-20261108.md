## 2026-11-08 DGX P5 scoped QSA #62318 image-build follow-up: Blazux hybrid QSA ABI

Actual DGX after HEAD `136a969`: `manifest validate PASS`; `p5 trial prepare` BLOCKED while building `Dockerfile.p5.qsa62318` at step 4/4: `P5_QSA62318_QSA_FUSE_GUARD_ANCHOR_COUNT_0`. No candidate image built, no `plan` or `execute` reached due to shell `set -euo pipefail`. Existing `qwen38-27b` remains EXITED(0) and old failed `qwen38-orcarouter` EXITED(1). New `qwen38-orcarouter-qsa62318` absent, port 8000 unserved, **no new GPU trial occurred**. This is a source-anchor mismatch during isolated build; NOT evidence of a new GPU model incompatibility.

Verified canonical repo `Dockerfile` lines 49–52 already rewrite the *original upstream* QSA `self.fuse_indexer_projection = vllm_config.lora_config is None` to `self.fuse_indexer_projection = (vllm_config.lora_config is None and not _fp8_hybrid_separate_qsa(quant_config, prefix))`. They also redirect the **qkv_proj keyword** to `_fp8_hybrid_excluded(quant_config)`, but leave the positional `model.without_modelopt_fp4(quant_config)` in `Qwen4ExpQSAQKVIndexerLinear`. Initial scoped upstream fix #62318 wrongly expected the unmodified guard and failed closed (correctly).

Implementation correction: `src/p5_qsa_quant_backport_v032.py` now supports exactly two anchored, AST-checked source ABIs: pristine upstream vLLM v0.32.0 and the *real installed Blazux hybrid QSA* modification. The Blazux variant computes `fused_quant_config = _fp8_hybrid_excluded(quant_config)`, retains `not _fp8_hybrid_separate_qsa(quant_config, prefix)` and adds official `type(qkv_proj.quant_method) is type(indexer.index_qk_proj.quant_method)` safeguard before fused wrapper construction. The original 3-way `packed_modules_mapping["qkv_proj"]` correction remains. Mixed/unknown/duplicate anchors must block. **No edits to canonical Blazux image, original 27B container, HF cache, or GPU.** Only separate P5 derived image gets changes.

The image CPU ABI probe additionally requires both upstream method-match and original Blazux hybrid veto to survive; new CPU regression tests cover exact Dockerfile sed declaration, Blazux fixture, idempotence, unknown hybrid source failure and isolated build. Re-run `./wizard.sh p5 trial prepare --json` *first* after new HEAD; only if PASS, `plan --json`; only if READY and fresh approved SHA, then GPU test. Previous failed container/logs retained, no auto rollback, API port 8000 and single-model invariants. The prior actual GPU QKV mismatch is **not yet re-verified with fixed image**; MTP0 GPU remains UNQUALIFIED.

---

# P5 Orcarouter MTP0 DGX trial — upstream QSA #62318 compatibility adapter
## Evidence: actual GPU fail-no-rollback (2026-11-08)

User-supplied DGX file: 붙여넣은 텍스트(1)(20261108-043721).txt.
Observed SHA f9c6cef; P5 recipe-first prepare PASS on existing Blazux vLLM 0.32 image `sha256:9479fc92...`, model snapshot `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799`, BF16 PLE mmap capability true. P5 plan `READY_TO_APPROVE`; approved execute `executed=true`, `target_started=true`, `source_stopped=true`, `gpu_verified=false`, `status=FAIL_NO_ROLLBACK`, `issues=["ORCAROUTER_CONTAINER_EXITED"]`. Receipt `~/.local/state/blazux-wizard/p5-live-trial/trial-20261108T043550955560Z.json`; original failed target container `1af5ef18a296...=qwen38-orcarouter` EXITED(1); original 27B `00094794475a...=qwen38-27b` EXITED(0); no API on port 8000. **Do not claim successful GPU model-load.**

Exact root cause observed in Docker logs (two copies of stack):
```
vllm/model_executor/layers/quantization/compressed_tensors/utils.py:66
ValueError: Found different quantization schemes for the shards of
language_model.model.layers.3.self_attn.qkv_proj. vLLM requires all to use the same scheme.
```
Failure is at Qwen4Exp QSA `QKVParallelLinear` construction **before model weight loading**, not proof that BF16 PLE mmap or an MTP donor is broken. External verification yielded exact vLLM regression [#62308](https://github.com/vllm-project/vllm/issues/62308) introduced by upstream #59533 in vLLM v0.32.0, fixed upstream in merged [#62318](https://github.com/vllm-project/vllm/pull/62318) on 2026-10-27, commit `fe833b1`: `packed_modules_mapping["qkv_proj"]` wrongly included `indexer.index_qk_proj` and the QSA indexer was fused even when its BF16 quant method differed from quantized q/k/v. Upstream explicitly notes that modifying the checkpoint `ignore` list or enabling LoRA does NOT fix it: the fourth shard is injected by vLLM's class mapping, not the checkpoint.

## Decision: recipe-first with strictly scoped upstream compatibility adapter

Neither changing `quantization_config.ignore` nor generic CLI flags is justified; that would mismatch actual packed checkpoint weights. The canonical Blazux vLLM0.32 / Flash-Next / 27B image is **not patched**. Instead the Orcarouter **P5 MTP0 trial recipe** explicitly pins the *upstream merged* fix and a separate isolated derived image. This is a versioned, narrow engine compatibility backport, not a silent model recipe override or globally applied vLLM source rewrite.

- Recipe: `recipes/qwen38-orcarouter.runtime.json`, `trial.adapter=qwen4exp-qsa-62318-v032-v1`, `trial.container_name=qwen38-orcarouter-qsa62318`, `trial.image_tag=blazux-p5-orcarouter:qsa62318-v032`. Only `mtp0`; no 31-tensor MTP2 donor deployed.
- Adapter: `src/p5_qsa_quant_backport_v032.py`, strict exact upstream v0.32 Python anchor validation on `vllm/models/qwen4_exp/nvidia/model.py` and `qsa.py`, AST parse, explicit isolated-build opt-in. Other vLLM files unchanged. Both source files are changed only **inside** a new derived image. Original 27B image ID is preserved and used as SHA-bound Docker base. `Dockerfile.p5.qsa62318` labels adapter ID, original immutable source image ID, vLLM 0.32.0, non-production.
- Candidate image build: `./wizard.sh p5 trial prepare --json` checks pinned PLE/header, original 27B image even if **already stopped**, a CPU-only original image ABI audit, creates an image-ID-derived local tag **only if missing**, builds offline (`--pull=false --network=none`), validates image provenance/label and CPU-only upstream-fix hook in derived candidate. Does not stop/restart 27B, delete images, mutate HF cache, or load model on GPU.
- Plan: `./wizard.sh p5 trial plan --json` verifies original 27B running **or cleanly exited(0)** with no port 8000 listener in the idle case, exact derived image ID and original base digest, CPU adapter capabilities, no other active GPU containers/processes, target container name unoccupied, and expiry-bound SHA-256 approval. **The old failed `qwen38-orcarouter` container is preserved.**
- Execute: `./wizard.sh p5 trial execute --approve-plan <fresh64hex> --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json`. Full recipe argv validated **before** interrupting anything. If old 27B running, stop it first; if already stopped, do not restart just to stop. Recheck port / GPU process absence; launch **new** `qwen38-orcarouter-qsa62318` using the exact derived image digest on port 8000; bounded API / chat readiness. Failure: NO AUTO RESTORE, no model/image pruning. Keep both old and new failed containers for diagnosis. No automatic production release/merge/rollback qualification.
- `./wizard.sh p5 trial status --json` observes **new** `qwen38-orcarouter-qsa62318`; general service-manager status may remain OBSERVED_UNQUALIFIED because this is an isolated trial name.

### DGX commands (do not use old/f9c6cef plan token)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh manifest validate --json

./wizard.sh p5 trial prepare --json | tee /tmp/p5-qsa62318-prepare.json
./wizard.sh p5 trial plan --json | tee /tmp/p5-qsa62318-plan.json
```

Confirm `prepare.status=PASS`, `prepare.original_engine_patched=false`, `prepare.base_image_id=sha256:9479...`, `plan.status=READY_TO_APPROVE`, `plan.issues=[]`, `plan.details.adapter=qwen4exp-qsa-62318-v032-v1`, `plan.details.runtime_image_id != plan.details.source.image_id`, `plan.details.source.state=IDLE_27B_STOPPED_AFTER_P5`, plan ID lowercase 64 hex, and exact current HEAD.

The old `qwen38-orcarouter` container is NOT reused or deleted. If `prepare` fails, **stop** before GPU trial; inspect bounded build log and adjust only if actual vLLM source ABI differs. If plan BLOCKED, no GPU trial. Fresh plan before execute.

```bash
bash <<'BASH'
set -euo pipefail
./wizard.sh p5 trial plan --json | tee /tmp/p5-qsa62318-plan.json
PLAN_ID=$(python3 - <<'PY'
import json, re, subprocess, time
prep=json.load(open('/tmp/p5-qsa62318-prepare.json'))
p=json.load(open('/tmp/p5-qsa62318-plan.json'))
assert prep['status']=='PASS',prep
assert prep['original_engine_patched'] is False
assert p['status']=='READY_TO_APPROVE' and p['issues']==[],p
assert p['details']['adapter']=='qwen4exp-qsa-62318-v032-v1'
assert p['details']['source']['image_id']==prep['base_image_id']
assert p['details']['runtime_image_id']==prep['image_id']
assert p['details']['runtime_image_id']!=p['details']['source']['image_id']
assert p['details']['git_head']==subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
assert p['expires_at_epoch_seconds']>time.time()+30
assert re.fullmatch(r'[0-9a-f]{64}',p['plan_id'])
print(p['plan_id'])
PY
)
./wizard.sh p5 trial execute --approve-plan "$PLAN_ID" \
  --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json | tee /tmp/p5-qsa62318-result.json
BASH
```

If trial fails, collect `./wizard.sh p5 trial status --json`, `docker logs --tail 250 qwen38-orcarouter-qsa62318`, `docker inspect qwen38-orcarouter-qsa62318`, and API status. Do not restart the source automatically. Only successful actual model-load and bounded inference can mark `PASS_GPU_TRIAL`. MTP2, long-context, native tools, vision, benchmarking, and general production promotion remain unqualified.
