# P4-A — Wizard capacity and state inventory (read-only, 2026-11-08)

## Decision / stage separation

Operator requested **P4-A capacity and current-asset state reconnaissance BEFORE deciding whether anything should be deleted**. This supersedes the earlier P4 no-start instruction **only for P4-A read-only implementation and observation**. **P4-B disposal candidates and P4-C retirement execution are NOT_STARTED/NOT_APPROVED.** This is not an implicit instruction to delete Flash, containers, Docker images, HF blobs, derivative views, or historical evidence.

P3 source closeout (actual DGX, supplied by operator on 2026-11-08):
- Flash pinned FP8-hybrid view and command observed; `flash_host_assets` status `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`, `issues=[]`; 299,845 weight-map entries, **11 index-referenced shards** totaling **129,771,270,410 apparent bytes**, metadata and template SHA-256 recorded in the terminal evidence.
- Large model shard bytes are **NOT** cryptographically verified; `verified_model_revision=false`. Referenced shard size total **IS NOT** allocated disk usage or recoverable space.
- Current DGX P3-F **168/168 PASS across 7 CPU suites**, production lifecycle flag `false`; active 27B API :8000 `LIVE_SERVICE_VERIFIED`, 8/8 checks. That status command did not independently re-check GPU PID/socket owner; prior P3-D read-only provenance PASS remains historical.
- P3-E/F source & read-only evidence may be handed to P8; actual canonical reinstall, production lifecycle, fault/automatic restore and final signoff remain P8-owned and NOT_RUN/NOT_RELEASED.

## P4-A Wizard UX

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh storage flash-next inventory --json
# Compatible stage alias:
./wizard.sh p4 inventory --json
```

In the interactive Wizard: **Advanced / recipes / storage → Storage / selective cleanup → inventory**. This action is read-only, has no plan ID, and cannot accept `--execute` or `--approve-plan`. Existing `retire`, `restore`, `candidates` and other mutation-style operations retain the blocked stage interface.

P4-A reports, without raw host paths or secrets:
- Verified currently served model identity from existing live API / manifest check, active 27B/container status, managed container presence/run status, total foreign containers, GPU-container and port-8000 owner counts. API identity is not equivalent to standalone PID proof.
- Docker's `system df` per-category **display estimates** (Images, Containers, Local Volumes, Build Cache; total/active counts, size/reclaimable), NOT approved safe-delete quantities and NOT an account of shared image-layer dependencies.
- Each configured or manifest-linked HF cache root: actual filesystem total/free byte counts, **allocated bytes from no-follow GNU `du`**, and presence/allocated bytes of known Flash/27B/Orcarouter model repository directories. Redacted root indices and source categories only; no host mount paths or private filenames in output.
- The output is **not additive** across cache-root / nested model directories / shared layers and hardlinks, and does not establish the bytes recoverable after any deletion. Other models, shared blobs, derived checkpoint symlinks, P8 reinstall baseline and protected receipts remain a reference/deletion review blocker.
- Partial/failed Docker or storage observation is explicitly `READ_ONLY_INVENTORY_PARTIAL` and cannot authorize disposition.

## P4-A source and runtime boundary

- Read-only probes: existing `recipe_drift.collect_docker()` (Docker `ps -a` and `inspect`), `service_status.inspect_live_status()` (local API health), `docker system df --format '{{json .}}'`, filesystem `shutil.disk_usage`, GNU `du -s -B1 -- <known root>`. No shell interpolation; subprocess command allowlist. The latter may take time on large caches, and has a bounded timeout. No `rm`, `stop`, `start`, `prune`, `volume` cleanup, image deletion, cache write or model download.
- Unknown Docker storage configurations or inaccessible cache roots remain **unavailable** in the report; do not extrapolate or synthesize capacities. Provider-reported reclaimable amounts can include shared assets and must not be directly approved.
- P4-A always sets `reclaimable_bytes_verified=false`, `operations_enabled=false`, `executed=false`, `removal_plan_id=null`, `production_released=false`, and explicitly preserves Flash as an existing P8 reference candidate pending a separate user decision.
- GitHub CPU/Fake-DGX tests prove interface safety only; **actual DGX P4-A capacity inventory must still be run** and reviewed.

## P4-B and P4-C prerequisites (not implemented/approved)

Only **after** reading the user's P4-A DGX report: map model-repository snapshot/blob ownership, Docker container/image layer use, derived Flash FP8-hybrid symlink and checkpoint references, P8 reinstall/rollback needs, actual disk pressure, and uncertainty in shared-layer reclaim estimates. Propose keep/optional cleanup alternatives and quantified *upper bounds/uncertainty*, not a decision or executable removal script. A separate new request/approval would be needed to design P4-B; eventual removal P4-C requires a fresh, exact plan, resource identities, explicit TTY approval, tested rollback where possible and verified postchecks. User has **not** approved either B or C.

## 2026-11-08 source safety clarification — incomplete inventory is partial

The inventory must observe **all four** Docker `system df` categories (Images, Containers, Local Volumes, Build Cache) to report `OBSERVED_DOCKER_ESTIMATES`; a missing category leaves partial display rows and reports `DOCKER_CAPACITY_CATEGORIES_INCOMPLETE`. This is not permission to infer unreported bytes are zero. The single GPU-container and host-port-8000 owner must **match the API-verified active managed model**, not merely belong to the set of known model containers; mismatch is `READ_ONLY_INVENTORY_PARTIAL`. These guards are source/Fake-DGX acceptance only. No live P4-A DGX capacity result or deletion authorization is established by this update.
