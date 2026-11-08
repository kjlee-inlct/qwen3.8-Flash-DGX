# P5 Orcarouter — Recipe-first MTP0 GPU trial (2026-11-08)

## Decision

P5 Orcarouter is a **manifest-led model and recipe** on the existing single DGX Spark/GB10 **Blazux vLLM 0.32.0** engine. Do not automatically patch upstream or Blazux `model.py` / `mtp.py` to accommodate a model. Run the pinned MTP0 model from its registered recipe and collect real GPU loader evidence. Only an observed, specific runtime incompatibility may justify proposing a separately versioned adapter later.

This change supersedes the earlier *P5-specific candidate image build* approach. The latest actual DGX log on 2026-11-08 demonstrated that `Dockerfile.p5.candidate` advanced past the local-image reference and PLE hook but failed during source patching: `MTP loader return: expected one vLLM0.32 anchor, got 2`. This is a **patch implementation failure**, not evidence the Orcarouter model cannot be served by existing vLLM 0.32, and not evidence that the patch is needed at MTP0. **Neither 27B nor the GPU were stopped/started**; the plan was BLOCKED with no approval ID.

The P5 candidate Dockerfile and legacy source patch script are preserved for reference, **but are not in the active MTP0 `prepare`/`plan`/`execute` path**. Never run the retired Dockerfile as part of this trial.

## Immutable recipe

- `recipes/qwen38-orcarouter.runtime.json` is authoritative for model repo and pinned revision, served model identity, BF16 PLE reference, MTP0 versus MTP2, context, concurrency, GPU memory settings, KV dtype, native tool/reasoning parsers, environment, and explicit experimental no-restore policy.
- `runtimes/ple-assets.json` schema 2 independently describes the actual BF16 table (128 tensors, width 160, 320001536 total rows, no scale, 102400491520 mmap bytes). Future FP8/FP16/other PLE formats use their own validated manifests rather than inheriting BF16 behavior.
- `runtimes/ple-loader-profiles.json` remains **unqualified** on real GPU until the experiment demonstrates an actual load and inference. Source metadata PASS does not prove CUDA, mmap, TP1 or tools qualification.
- `runtimes/service-policy.json` retains `ONE_ACTIVE_MODEL_ONLY`, port 8000, stop-old-before-start-new. Only the separately declared P5 MTP0 **development trial** has the user-requested no-auto-restore exception.

## Actual P5 CLI behavior

`./wizard.sh p5 trial prepare --json` (**read-only preflight**)
: Validates pinned manifests and BF16 PLE metadata; confirms live 27B container's full image ID, OS and arm64, verifies the Blazux vLLM 0.32 image provenance, and runs a **GPU-free, network-isolated, ephemeral CPU container** reading its installed vLLM version, BF16 PLE mmap implementation, Qwen4Exp hook and Python source syntax. No new Docker image is built or tagged, no vLLM file is changed, and 27B remains running. A successful capability check does **not** establish Orcarouter model loading support.

`./wizard.sh p5 trial plan --json` (**read-only plan**)
: Re-evaluates source, CPU ABI, other active GPU containers, port and exact pinned recipe; binds original 27B container ID and the **same existing Blazux image ID** as the MTP0 runtime image into an expiring approval hash. Plan includes `image_built:false`, `source_patched:false`. Do not execute if plan is BLOCKED or `plan_id:null`.

`./wizard.sh p5 trial execute --approve-plan <SHA64> --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json` (**real GPU**)
: Revalidates exact plan, stops `qwen38-27b` without removing it, checks 8000 free and no remaining GPU compute processes, starts `qwen38-orcarouter` using the existing Blazux image **by immutable ID**, read-only pinned Orcarouter snapshot, recipe-derived BF16 mmap env and MTP0 configuration, waits for exact `/v1/models` alias and a bounded chat completion. Success keeps the Orcarouter trial running. Failure leaves 27B stopped, **does not restore**, preserves original images, checkpoint, donor, cache, target container and logs, and records a private receipt. This is not production promotion.

`./wizard.sh p5 trial status --json` (**read-only observation**)
: Inspects target container and possible API ID. Status alone does not confer real GPU qualification.

### Recommended commands on DGX

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh manifest validate --json

./wizard.sh p5 trial prepare --json | tee /tmp/p5-mtp0-prepare.json
./wizard.sh p5 trial plan --json | tee /tmp/p5-mtp0-gpu-trial-plan.json
```

Before any GPU operation, independently confirm `prepare.status=="PASS"`, `prepare.image_built==false`, `plan.status=="READY_TO_APPROVE"`, `plan.issues==[]`, `plan.details.runtime_image_id==plan.details.source.image_id`, `plan.details.strategy=="RECIPE_FIRST_EXISTING_VLLM032_IMAGE"`, `plan.plan_id` is a 64-digit lowercase SHA and the current 27B is healthy. **No P5-specific build should occur.** The CPU preflight executes an ephemeral CPU Docker container with `--rm` but never uses GPU or changes the image.

```bash
bash <<'BASH'
set -euo pipefail
PLAN_ID=$(python3 - <<'PY'
import json, re
prep=json.load(open("/tmp/p5-mtp0-prepare.json"))
p=json.load(open("/tmp/p5-mtp0-gpu-trial-plan.json"))
assert prep["status"]=="PASS", prep
assert prep["image_built"] is False and prep["source_patched"] is False
assert p["status"]=="READY_TO_APPROVE" and p["issues"]==[], p
assert p["details"]["strategy"]=="RECIPE_FIRST_EXISTING_VLLM032_IMAGE"
assert p["details"]["runtime_image_id"]==p["details"]["source"]["image_id"]
assert re.fullmatch(r"[0-9a-f]{64}", p["plan_id"])
print(p["plan_id"])
PY
)
./wizard.sh p5 trial execute \
  --approve-plan "$PLAN_ID" \
  --ack-downtime I_ACCEPT_P5_NO_ROLLBACK \
  --json | tee /tmp/p5-mtp0-gpu-result.json
BASH
```

If the result is `FAIL_NO_ROLLBACK`, do not restart 27B automatically. Capture:

```bash
./wizard.sh p5 trial status --json
docker ps -a --filter name=qwen38-orcarouter
docker logs --tail 250 qwen38-orcarouter
ls -lah ~/.local/state/blazux-wizard/p5-live-trial/
```

## Pass criteria and next iterations

The first GPU trial only proves a pinned MTP0 start, BF16 PLE mmap and one bounded API chat. **Tool-calling, vision, extended context, throughput, memory behavior and MTP2** need separate tests and evidence. Native MTP2 overlay and 31 BF16 donor tensors are not deployed by MTP0.

If load fails due to a real quantized LM head or compressed-tensors incompatibility, capture full error signature before building any code adapter. A future adapter must be a separate versioned, opt-in engine compatibility plugin, never a silent rewrite to the canonical vLLM 0.32 image and never an unexplained global patch introduced by the model recipe.
