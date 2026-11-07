# P4-B + P4-C — combined dry-run and deferred deletion contract (2026-11-08)

## Operator direction and current scope

Implement P4-B asset/reference candidate assessment and P4-C cleanup transaction rehearsal together. Verify both through **one dry-run shell script**. Do not actually remove files, model assets, Docker containers/images/volumes or build cache now. Future live cleanup belongs to a **separately authorized P5 operational problem** or **P8 final acceptance**.

**Production deletion adapter is intentionally absent and not released.** This is a complete **review + dry-run source implementation**, not a live deletion implementation or acceptance claim. Do not interpret a review fingerprint or CI PASS as a deletion authorization.

## Actual prior P4-A evidence

- [Actual DGX P4-A capacity report](P4-A-DGX-READONLY-CAPACITY-EVIDENCE-20261108.md), run at source checkout `a29cd6e`.
- P4-A `READ_ONLY_INVENTORY_COMPLETE`, `issues=[]`, `active_api_verified=true`; 27B running at :8000, stopped Flash container preserved, Orcarouter model cache observed, one GPU model.
- Disk total 982,819,848,192 bytes; free 324,880,961,536 bytes (~33.06%). Both cache roots reported identical filesystem total/free; do not add the totals. 11 FP8 Hybrid referenced shards with apparent size 129,771,270,410 bytes are not actual reclaimable space.
- Docker reclaimable output (182.7MB containers, 2.088MB build cache) is only a display estimate and not a safe deletion amount.

## One-shot operator-side DGX dry-run (no deletion)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p4-bc-dry-run.sh --json
```

The script runs 13 Fake-DGX CPU regression tests (stderr), then takes one fresh read-only P4-A inventory using Docker ps/inspect, local API health, `docker system df`, `du` and disk_usage. P4-B and P4-C are pure transforms of that one observation. JSON is written to stdout; the script exports `PYTHONDONTWRITEBYTECODE=1`. No Docker/HF mutation, GPU model switch or journal deletion is triggered.

## Supported Wizard/CI paths

```bash
./wizard.sh storage flash-next dry-run --json
./wizard.sh p4 candidates --dry-run --json
./wizard.sh p4 retire --dry-run --json
bash scripts/temporary/p4-bc-dry-run.sh --fixture-only
```

The first command covers both stages in one P4-A read-only probe. `candidates --dry-run` reviews only P4-B; `retire --dry-run` rehearses only P4-C. Legacy `p4 candidates` and `p4 retire` **without explicit dry-run** still fail closed. All `--execute` and `--approve-plan` attempts are rejected **before host inspection**; a plan ID is never issued.

## P4-B review semantics

- Validate a **fresh complete P4-A** snapshot, service/API observation and all four Docker capacity categories. Missing model, cache size, active owner or provider estimate fails closed.
- Redacted resource observations only: managed container presence/run state, model-repository allocations by numbered cache root, and Docker category display estimates. Never output host paths, secrets, foreign container names or unregistered repo IDs.
- 27B is `PRESERVE_ACTIVE_MODEL`; stopped Flash is `PRESERVE_P8_FLASH_REINSTALL_REFERENCE`; Orcarouter is `PRESERVE_P5_ORCAROUTER_SOURCE`. Other unscoped Docker category estimates are **not exact targets**.
- No candidate is delete-eligible and no actual reclaimable byte quantity is verified. `candidate_count` is a count of **reviewed resource records**, not delete permissions.
- Unresolved safeguards: shared HF snapshots/blobs/symlinks/hardlinks, filesystem aliases and device IDs, Docker shared layers, FP8 derived checkpoint and P8 reinstall/rollback/evidence dependencies.

## P4-C rehearsal semantics

- Build a fail-closed in-memory transaction with steps for P4-A snapshot check, reference enumeration, link/rollback analysis, exact fresh identities, approval, live adapter release and API/GPU/port/disk postchecks.
- Return `DRY_RUN_COMPLETE_RELEASE_GATED` only for a complete P4-B review. All 9 observed sample resources in Fake-DGX have `would_execute=false`, `selected_resources=0`, `safe_reclaimable_bytes=null`.
- `P4_C_LIVE_EXECUTION_RELEASED=False` and **no live deletion adapter exists**. No `rm`, `prune`, HF deletion, stopping/restarting a model, or automatic P5/P8 transition is available through this implementation.

## Required future P5/P8 execution work (not authorized now)

1. New operator instruction identifying a real P5 storage/operation issue or a P8 acceptance need, with exact resource selection.
2. Independent live inventory of resource IDs, Docker image/share references, cache roots, snapshot/blob/hardlink graph and P8 recovery dependencies. Never infer exact bytes reclaimed from `du` or `docker system df` alone.
3. Separate exact plan, fresh TTY confirmation, rollback/resume and postchecks, source tests and real DGX acceptance before enabling any live deletion adapter.
4. Preserve vLLM 0.32, `ONE_ACTIVE_MODEL_ONLY`, API :8000, Open WebUI/Portainer, active 27B, historical P3 receipts and unqualified Flash P8 reinstall references unless independently authorized.

## Validation status

- Initial P4-B/C source commits `4129418` and `1c68962`, existing Draft PR #1 remains open/unmerged.
- GitHub Actions runs [42403828742](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42403828742) and [42403824687](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42403824687) SUCCESS: **902/902 CPU/Fake-DGX PASS in 41 groups**, including 13 P4-B/C tests.
- The new combined script has not yet been run on the actual DGX. Its real host result is still **PENDING**, distinct from the older P4-A PASS.
