# Manifest contracts, service orchestration and storage safety

**State: DESIGN CONTRACT ONLY.** No manifests, wizard executables, gateway, or new runtime have been implemented by this documentation commit.

## A. Five concerns with different ownership

| Type | Source of truth | Key fields | Version policy |
|---|---|---|---|
| Recipe | Git `recipes/*.yaml` | `recipe_id`, model repo/revision, tokenizer, architecture, quantization, PLE, MTP, stage dependencies, compatible runtime IDs, checks | Versioned, reviewed, no tokens |
| Runtime | Git `runtimes/*.yaml` or bounded recipe reference | vLLM version, Docker image **digest**, architecture `linux/arm64`, host/GPU/env/CLI flags, mounts, limits | Versioned; no floating `latest` for qualified release |
| Service | Git desired state + local runtime state | served name vs model repo, container identity, port, API compatibility, gateway routing, health and rollback policy | Desired config versioned; actual process state read from DGX |
| Storage inventory | Local, generated, timestamped | checkpoint snapshot SHA, canonical path, inode/symlink/blobs, bytes, ownership, consumers, protection flags | Regenerate before stateful action; never assume Git knows free space |
| Benchmark/evidence | Immutable measured artifact + Git pointers | source/recipe/weights/image digests, host specs, exact commands, seeds, request hashes, results, logs, status | Append-only, link to `handoff/EVIDENCE-LEDGER.md` |

Secrets, HF read tokens, API keys and host-private raw paths are **never** committed.

## B. Proposed minimal recipe YAML (illustrative, NOT executable)

```yaml
schema_version: 1
recipe_id: qwen38-27b-nvfp4
engine: vllm
runtime_ref: vllm032-gb10
model:
  repo_id: RadixArk/Qwen3.8-27B-NVFP4
  revision: REPLACE_WITH_VERIFIED_FULL_SHA
  tokenizer_repo_id: null
  architecture: UNVERIFIED_27B_VLLM032
  quantization: nvfp4
  ple: UNVERIFIED_FOR_27B  # verify architecture-specific PLE; do not reuse Flash-Next BF16 PLE
  mtp: {enabled: false}
service:
  served_model_name: qwen3.8-27b
  port: null  # assigned by manager; not the protected live :8000 port
  container_name: null
checks:
  require_exact_revision: true
  require_ready_health: true
  allow_launch_without_gpu_approval: false
lifecycle:
  protected: false
  allow_delete_without_approval: false
```

Never fill placeholders by inference. Use validated checkpoint metadata and fail closed if `model.architecture`, quant method, tensor names, module mappings or revisions differ from validated assumptions. Flash-Next and Orcarouter require their own `PLE/MTP` specifications.

## C. Safety-first commands and state machine (proposed)

```text
inventory / plan / doctor / verify-source       READ_ONLY
prepare --dry-run                               READ_ONLY
prepare --execute --approval-id ...             RESOURCE_MUTATION
serve --dry-run                                 READ_ONLY
switch --dry-run --to RECIPE                    READ_ONLY
switch --execute --approval-id ...              GPU_SERVICE_MUTATION
retire --dry-run --recipe RECIPE                READ_ONLY
retire --execute --approval-id ...              DESTRUCTIVE_MUTATION
rollback --dry-run                              READ_ONLY
rollback --execute --approval-id ...            GPU_SERVICE_MUTATION
```

Use unique `plan_id`, `approval_id`, snapshot generation, expected active model/port/image, expected candidates and lock; approval binds to **exact plan digest and resource IDs**, expires after state changes. A source conversation saying “do the roadmap” is not an unconditional approval for any of those mutations.

```text
IDLE -> PLAN -> PRECHECK -> APPROVAL -> QUIESCE -> STOP_OLD
-> START_NEW -> READY_CHECK -> API_SMOKE -> COMMIT
                             \-> FAILED -> ROLLBACK -> VERIFY_OLD
```

Before `STOP_OLD`, guarantee the source recipe, rollback image, checkpoint, port and snapshot remain intact. A rollback that depends on deleted files is invalid. For a single GPU box, the gateway must queue/reject requests with a clear 503/Retry-After during cutover rather than silently misrouting; avoid misleading `/v1/models` listing if the model is not actually active.

At every transition write an append-only local transition log (no credentials). Restart after interruption must reconcile actual Docker/port state, **never** trust an outdated state.json alone. Prevent two overlapping switches with a lock.

## D. Disk deletion policy and required inventory

1. Snapshot existing protected live Docker container, image digest, mounts and current HF cache. Collect `df`, `du`, `docker system df` and resolved paths **read-only**.
2. Build a concrete candidate list with resolved parent/canonical paths and content hashes where feasible, expected reclaimed bytes **conservatively** estimated. Different snapshots may share blobs.
3. Deny deletion if a path is under a protected root, referenced by a runtime/recipe/rollback/donor overlay, bound into a running container, not owned by the manager, or has unresolved symlink/shared-blob references.
4. Show **exact file list**, checkpoint revision, byte count, consequences, redownload/recovery method. Explicit approval must identify the specific deletion plan; default is dry-run.
5. Remove only audited targets in bounded batches; log before/after free space, digests for surviving manifests, and rollback metadata. Never automatically run `docker system prune -a`, `docker image prune` or entire HF cache deletion.
6. Preserve recipe, original validation records, manifests, error traces (redacted), benchmark data and Git history even if model weights are removed.

**Space bottleneck before P2:** do not skip P3 to remove P1 checkpoint. Ask for targeted storage expansion, alternative download staging, or user-approved deletion plan with a still-recoverable fallback; otherwise mark `BLOCKED_CAPACITY`.

## E. Acceptance protocol

- CPU/CI: parse schema, select recipe, error-path guards, path canonicalization, symlink/refgraph logic, safe container name/port rules, dry-run idempotence, state-machine/recovery fault injection; no Docker/GPU for unit tests.
- GPU window: memory guard, one active model, startup, 27B architecture viability, PLE, MTP OFF then on, API routes, repeated switching, failover, and measured latency/throughput/quality. Pin benchmark seeds and prompts; redact secrets.
- Release: `PASS` requires reproducible artifacts and gate matrix, not only an API 200. A status is one of `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE` with explicit scope.

See [master plan](MODEL-RECIPE-WIZARD-PLAN.md) and [current handoff](../handoff/CURRENT-STATE.md).
