## Additional executable safety guards (source update)

- The candidate image's Docker label `blazux.p5.base_image` must equal the precise live 27B source **image digest** recorded in the approved plan. Merely having a P5-looking tag is insufficient.
- After stopping 27B and releasing port 8000, **GPU compute-process inventory** must be empty via `nvidia-smi --query-compute-apps=pid --format=csv,noheader`; an unknown or unsupported result blocks the target start and leaves 27B stopped. This prevents starting a second GPU model while stale/non-Docker CUDA processes are running.
- `./wizard.sh p5 trial status` reports API identity as an observation rather than marking a fresh independent GPU qualification. The execution receipt is the bounded live inference evidence.
- Failure reports `FAIL_NO_ROLLBACK` and a private local receipt; no automatic 27B restart. Keep all images, cache and container logs for diagnosis.

---

# P5 — Real DGX Orcarouter MTP0 one-shot GPU trial (NO automatic restore), 2026-11-08

## Scope and authorization

Operator explicitly confirms this is an idle **development** use of DGX Spark. Downtime of the existing 27B serving on port 8000 is permitted and **failure does not require 27B restoration**. A failed target is left as-is for investigation; the original 27B container is left **stopped, not deleted**, and no automatic rollback, auto-restart, cache deletion, image removal or P3/P6/P8 action occurs. This exception is limited to this P5 MTP0 *trial* and does not change the default service transition rollback policy. Successful MTP0 GPU trial is not production release.

Current known DGX log from operator: HEAD `30577b1`, 7-document manifest PASS; Orcarouter pinned PLE BF16 (128 tensors, 320001536 rows, width160) source metadata PASS; pinned donor MTP BF16 31 exact tensors and three SHA-verified shards PASS; P5 Fake-DGX 57/57 PASS; existing 27B active `qwen38-27b`, served `qwen3.8-27b` on 8000, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. **None** of these results is an actual P5 GPU success. The live state must be re-observed before use.

## New execution path

`./wizard.sh p5 trial` is a separately scoped temporary development entry, distinct from `./wizard.sh p5 start`, the conventional recipe release, and historical P3. The executable module is `scripts/manager/p5_live_trial.py`. It supports **MTP0 only**; MTP2 requires a verified derived overlay and a different plan.

1. `prepare` performs pinned manifest/PLE metadata checks and builds `Dockerfile.p5.candidate` using the **current running 27B Docker image by immutable ID** as base. It preserves existing 27B service during the image build. The P5 candidate ensures the Blazux BF16-capable PLE mmap hook exists and applies isolated vLLM 0.32 source patches; any missing architecture/patch anchor fails the build. The candidate image remains experimental and is not reused from YSLAB's unrelated vLLM dev snapshot.
2. `plan` confirms the current **27B container** image ID, full container ID, real API model identity, model cache and BF16 PLE header, the new candidate image label/digest, exclusive running GPU containers, absence of any existing `qwen38-orcarouter` target, and ownership of :8000. Plan SHA256 binds identities and expires at the next 15-minute boundary. No Docker mutation occurs.
3. `execute` requires matching `--approve-plan` plus exact `--ack-downtime I_ACCEPT_P5_NO_ROLLBACK`. It rechecks the plan and source immediately; then stops only the exact verified 27B service, verifies :8000 free and no other GPU Docker container, starts **one** `qwen38-orcarouter` with PLE mmap from the pinned *read-only* cache and `VLLM_P5_ORCAROUTER=1`, and waits for exact `/v1/models` model ID and a bounded chat completion. The first trial uses `--enforce-eager` to avoid unqualified PIECEWISE graph capture, conservative 8192 context, one sequence, GPU 0.70, MTP0, BF16 KV, automatic tool parser enabled. Graph and MTP2 optimization will be evaluated later.
4. On success, report `PASS_GPU_TRIAL` and keep the Orcarouter service active on 8000. This means one bounded chat passed, **not** full tools, MTP2, vision, benchmark, or production acceptance.
5. On failure, report `FAIL_NO_ROLLBACK`. **27B remains stopped**. The failed P5 Docker container, local image, checkpoint, donor, recipes, and logs are retained. A private append-only result file is written under `~/.local/state/blazux-wizard/p5-live-trial/`. Never automatically start the old container, remove the new one, or clear the cache.

## Exact operator commands

Run on the **real DGX**, in the local checkout, not on the GitHub runner:

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh manifest validate --json
./wizard.sh p5 trial prepare --json
./wizard.sh p5 trial plan --json | tee /tmp/p5-mtp0-gpu-trial-plan.json
```

Stop and inspect the plan. Only when `status=READY_TO_APPROVE`, `issues=[]`, source container `qwen38-27b` is actually the running model and the target digest is pinned:

```bash
PLAN_ID=$(python3 - <<'PY'
import json, re
d=json.load(open('/tmp/p5-mtp0-gpu-trial-plan.json'))
assert d['status']=='READY_TO_APPROVE' and not d['issues'], d
assert d['operation']=='P5_MTP0_STOP_27B_START_ORCAROUTER_NO_ROLLBACK'
assert re.fullmatch(r'[0-9a-f]{64}',d['plan_id'])
print(d['plan_id'])
PY
)
./wizard.sh p5 trial execute \
  --approve-plan "$PLAN_ID" \
  --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json
./wizard.sh p5 trial status --json
./wizard.sh service manager status --json
```

If the terminal reports `FAIL_NO_ROLLBACK`:

```bash
docker ps -a --filter name=qwen38-orcarouter
docker logs --tail 180 qwen38-orcarouter
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
ls -lah ~/.local/state/blazux-wizard/p5-live-trial/
```

No reboot, auto restore or removal implied. Do not run the `--execute` command again using a stale plan, and do not manually start a second GPU model on :8000.

## First acceptance gates

- Build image is arm64 vLLM **0.32.0**, original source patch anchor audit PASS, BF16 PLE mmap hook present.
- Pinned snapshot remains immutable with correct source metadata (no fabricated full checkpoint SHA proof).
- Exactly one model active; `qwen38-27b` stopped before `qwen38-orcarouter` starts.
- Runtime logs confirm actual PLE mmap rather than allocating the entire 95GiB table in GPU/unified memory, without hangs at TP=1.
- API model identity exactly `qwen3.8-flash-next-orca-uncensored-bf16`; bounded Chat Completion PASS.
- Then separately test tool parser/native tool call, streaming, reasoning, short context benchmark and longer context; *later* MTP2 derivative overlay from pinned 31 BF16 tensors, with separate qualification.
- If GPU trial fails, mark actual cause and reproduce with a new bounded plan; never forge `runtime_qualified` from registry metadata.

## Further work

This new execution path is **experimental, opt-in and no-rollback** by explicit user instruction, not a generic switch engine. The normal service manifest's `failed_new_model_rollback_to_old=true` default still applies to future production switches. User approval for downtime does not prove a GPU load was run; only real DGX output can establish that.
