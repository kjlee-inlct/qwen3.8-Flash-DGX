# NVIDIA Flash-Next — port 8000 safe deployment runbook

**Source and CPU CI pass, GPU Wizard unqualified.** 2026-11-05 user-supplied DGX log: vLLM 0.32 Docker image build finished; model download 9/25 files (36%) at last visible line. OpenWebUI and Portainer remained running; port 8000 was free at the earlier scan. The operator entered flash setup, serve, wait and test sequentially, so subsequent commands may run without assistant action. Do not modify the worktree, restart the process, repeat setup, or replace an already running container before the original chain ends. These are time-bounded facts, not proof of full download or API readiness.

## Intended fork defaults

- Engine: pinned vLLM v0.32.0 family (the repo Dockerfile starts from `vllm/vllm-openai:v0.32.0`).
- Default model repository: `nvidia/Qwen3.8-Flash-Next-NVFP4`. This is **not** the earlier Orcarouter compressed-tensors checkpoint.
- `./flash serve default` resolves profile `MODE=hybrid`, `YARN=1`, `CTX=500000`, `MTP=2`; NVIDIA Flash-Next weights need a prepared hybrid snapshot.
- Public API host port `8000`; Docker internal port `8000`; API base `http://<DGX-HOST>:8000/v1`.
- Container: `qwen38-flash`; `/v1/models` should expose `qwen3.8-flash-next` only when actually up.
- Blazux bare `./flash serve`, `./flash doctor default`, `./flash wait`, `./flash test`, `./flash status` use the fork port default. External clients must update the old Orcarouter ID if hard-coded.

## Read-only preflight (no setup, no GPU)

Run only on the intended DGX after checking out this branch and reviewing its diff:

```bash
git status --short --branch
git log -1 --format='%H %cs %s'
python3 -m pip show PyYAML jsonschema
bash wizard/00-doctor.sh
bash wizard/10-plan.sh
./flash doctor default
docker ps -a --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}'
ss -ltn '( sport = :8000 )'
df -h
```

The Wizard commands are **read-only** and print `launch_authorized=false`. Their collision gate fails if name/port 8000 is occupied, or if Docker/ss cannot be inspected. Confirm with the operator that the old service and its client requirements are actually gone; do not assume this from prior conversation alone.

## Prepare and serve — **separately gated, NOT RUN**

Only after checking free space, image provenance, exact checkpoint snapshot, backup/rollback, and getting a scope-specific operational go-ahead:

```bash
# Deliberate operator commands, never executed by source-only Wizard.
./flash setup default      # CAN download ~124 GiB and build/modify local image/cache
./flash doctor default     # Re-check after setup
./flash serve default      # STARTS GPU; refuses an existing container with the same name
./flash wait               # checks :8000 for service readiness
./flash test               # API/quality smoke test on the live model
curl -fsS http://127.0.0.1:8000/v1/models
```

**If `qwen38-flash` already exists, `serve.sh` stops without removing/restarting it.** Do not run `docker rm -f` as a remedy without separately verifying identity and getting approval. Container image can have a mutable local tag; record exact image ID/digest, checkpoint full revision, model config, command, wall clock, GPU memory, API ID, test results and logs before promoting to production. Running a moving `refs/main` is not yet an immutable, qualified release.

## P1 Wizard after existing operator process finishes

Read [P1 Wizard operations](P1-WIZARD-OPERATIONS.md). Use read-only bash wizard/p1.sh status and bash wizard/p1.sh plan --for-action verify. If the model is already serving, do not use start: adopt its existing container and verify/benchmark with a fresh explicit plan approval.

## Recovery and limitations

- If `setup` cannot fit disk, stop; do **not** delete the HF cache, models, Docker images or fallback assets.
- If startup fails, capture `docker ps -a`, `docker logs --tail 100 qwen38-flash` (redact secrets), `ss`, `df`; leave the failed container for explicit inspection.
- Restore any previous service only from an operator-approved, actually verified snapshot/recipe, not an assumed historical Orcarouter container.
- No proxy, alias compatibility layer, model-switch/rollback execution or GPU performance qualification is implemented by this change. Those are later work.
