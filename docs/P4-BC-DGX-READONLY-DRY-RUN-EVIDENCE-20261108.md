# P4-B/C — Actual DGX Spark read-only one-shot dry-run evidence (2026-11-08)

## Evidence provenance and limits

- Source: operator-supplied terminal excerpt (attached paste `붙여넣은 텍스트(1)(20261107-190824).txt`, 285 lines), received 2026-11-08 KST, following the one-shot script recommendation `bash scripts/temporary/p4-bc-dry-run.sh --json`.
- Excerpt includes creation notices for `docs/P4-BC-ONE-SHOT-DRY-RUN-20261108.md`, `scripts/manager/p4_bc_dry_run.py`, `scripts/temporary/p4-bc-dry-run.sh`, `tests/test_p4_bc_dry_run_cpu.py` and P4-A evidence, followed by 13 Fake-DGX unit tests and P4-B+C JSON.
- The excerpt does **not** independently display `git rev-parse HEAD` or a complete raw P4-A snapshot. The actual P4-B/C JSON and observed assets below are attributable to the operator-reported DGX run, not GitHub CPU CI. Do not claim a new exact operator checkout SHA from this excerpt.
- The separate source-only GitHub Actions run [42404211649](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42404211649) succeeded on source HEAD `66c7e5b`; that is distinct from this operator-side DGX observation.

## One-shot results: PASS within read-only scope

| Scope | Operator output | Interpretation |
|---|---|---|
| Fake-DGX CPU regressions | `Ran 13 tests ... OK` | 13/13 PASS before host read-only stage |
| Referenced P4-A inventory | `inventory_status=READ_ONLY_INVENTORY_COMPLETE` | Current source collector reported complete |
| P4-B review | `READ_ONLY_REVIEW_COMPLETE`, `issues=[]` | Redacted resource classification succeeded |
| P4-C rehearsal | `DRY_RUN_COMPLETE_RELEASE_GATED`, `issues=[]` | Pure transaction rehearsal succeeded, live gate still closed |
| Combined dry-run | `READ_ONLY_DRY_RUN_PASS` | Read-only integrated acceptance for current snapshot |
| Final flags | `executed=false`, `operations_enabled=false`, `live_deletion_approved=false`, `production_released=false` | No deletion/service mutation or operational release approved |

## P4-B resources (9 reviewed records, **0 deletion approvals**)

The JSON includes **9 review records**, not 9 delete candidates. Breakdown: **2 managed container records** (`27b` running, `flash-next` stopped); **3 HF model-repository records** (`root-1:27b`, `root-1:flash-next`, `root-2:orcarouter`); **4 Docker category display estimates** (Images, Containers, Local Volumes, Build Cache). All entries set `selected_for_deletion=false`, `eligible_for_deletion_now=false`, `reference_ownership_verified=false`, `safe_reclaimable_bytes=null` and `would_execute=false`.

| Resource key | Classification | Observed allocated bytes, if given |
|---|---|---:|
| `container:27b` | `PRESERVE_ACTIVE_MODEL` | — |
| `container:flash-next` | `PRESERVE_P8_FLASH_REINSTALL_REFERENCE` | — |
| `root-1:27b` | `PRESERVE_ACTIVE_MODEL` | 21,932,584,960 |
| `root-1:flash-next` | `PRESERVE_P8_FLASH_REINSTALL_REFERENCE` | 75,967,504,384 |
| `root-2:orcarouter` | `PRESERVE_P5_ORCAROUTER_SOURCE` | 177,686,446,080 |
| Docker category estimates (4) | `NOT_AN_EXACT_RESOURCE_TARGET` | Docker display only |

Docker report displays: Images 28.74GB / 0B reclaimable; Containers 416.7MB / 182.7MB (43%) reclaimable; Local Volumes 34.16kB / 0B reclaimable; Build Cache 7.364MB / 2.088MB reclaimable. These provider display figures **are not verified safe recovery or permission to delete**. No cross-root additive capacity or actual freed-space amount is established.

Observed review fingerprint (read-only **not an approval or plan ID**): `f6ee99301983f4439048c29c1032e5f6a6a58a3138430c17030120201ed2feb1`. The same fingerprint appears in P4-C. Both `plan_id=null` and `approval_accepted=false`.

## P4-C transaction rehearsal: 2 PASS, 2 deferred, 1 not released, 1 not executed

| Step | Reported result | Acceptance boundary |
|---|---|---|
| `verify_current_p4_a_snapshot` | `PASS` | Read-only snapshot accepted by source contract |
| `enumerate_model_container_docker_references` | `PASS` | Bounded resource **record enumeration** succeeded; not verified hardlink/layer ownership |
| `verify_hardlink_shared_layers_and_rollback_references` | `DEFERRED_P5_OR_P8` | Full dependency/reference audit **not executed** |
| `fresh_exact_id_recheck_and_tty_approval` | `DEFERRED_P5_OR_P8` | No live-resource identification/TTY approval |
| `release_live_cleanup_adapter` | `NOT_RELEASED` | Production deletion adapter absent/gated |
| `delete_and_verify_api_gpu_port_disk` | `NOT_EXECUTED` | No real delete or post-delete verification |

`reviewed_resources=9`, `selected_resources=0`; all 9 `simulated_operations[].would_execute=false`. `live_execution_released=false`, `docker_mutation_performed=false`, `hf_mutation_performed=false`, `reclaimable_bytes_verified=false`, `safe_reclaimable_bytes=null`, `operations_enabled=false`, `executed=false`, `production_released=false`.

## Five unresolved reference gaps (reported verbatim)

1. `HF_SNAPSHOT_BLOB_SYMLINK_HARDLINK_GRAPH_NOT_AUDITED`
2. `CACHE_ROOT_MOUNT_DEVICE_ID_NOT_AUDITED`
3. `FLASH_FP8_DERIVATIVE_P8_REFERENCE_NOT_AUDITED`
4. `DOCKER_IMAGE_VOLUME_LAYER_OWNERSHIP_NOT_AUDITED`
5. `HISTORICAL_RECEIPTS_AND_REINSTALL_ROLLBACK_NOT_AUDITED`

These are anticipated **deferred safeguards**, not new failures of the read-only dry-run. They explicitly prevent any claim of approved deletion candidates or known-safe reclaimable bytes.

## Verdict and next boundary

**P4-B/C one-shot REAL DGX READ-ONLY DRY-RUN: PASS / COMPLETE in its source+observation scope. P4-C actual deletion: NOT RUN / NOT IMPLEMENTED AS LIVE ADAPTER / NOT RELEASED.** This PASS must not be promoted to end-to-end destructive cleanup acceptance. Actual removal remains deferred to a separate explicitly authorized **P5 operational issue** or **P8 final operations acceptance**, requiring exact identities, dependency and rollback audits, fresh approval, a newly qualified mutation adapter and postchecks. Do not stop 27B, delete stopped Flash, touch Orcarouter cache, replay P3 acceptance, trigger P5/P8 or merge Draft PR #1 on this evidence.
