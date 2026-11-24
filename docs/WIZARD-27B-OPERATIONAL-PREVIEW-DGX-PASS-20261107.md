# 2026-11-07 — DGX Read-Only Acceptance: Canonical 27B and Flash-Next Switch Preview

## Evidence provenance and limitations

Operator ran the read-only Wizard commands on DGX Spark **after** fast-forwarding `feature/recipe-wizard-handoff` from `5456eae` to `4189a79` (commit `4189a7946dd68fd460b79735efbb1b64547757d3`). The results were pasted in the conversation on 2026-11-07. The inspection did **not** execute a model switch, Docker stop/start, reinstall, removal, restart, benchmark, GPU process audit, or port ownership check.

Three commands (in order):

```bash
./wizard.sh model 27b recipe-diff --cache-source /home/inlc/.cache/huggingface --json
./wizard.sh switch flash-next-27b operational --target flash-next --plan --json
./wizard.sh service manager status --json
```

## 1. Canonical 27B desired-versus-observed

- `action=MODEL_RECIPE_LIFECYCLE`, `status=READ_ONLY_STATUS`, `decision=OBSERVE_ONLY`, `issues=[]`, `diff=[]`, `advisories=[]`.
- `container_name=qwen38-27b`, `container_id=00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`, `installed=true`, `running=true`, `active_model=27b`.
- `served_id=qwen3.8-27b`; image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; model revision `482ca0f3832238542f8f5295dde86b5f22711d80`; recipe SHA256 `301c9c7980690b97e357db5fb57090fc82c507ab9c1116c8e154739e360bbbbb`.
- Explicit requested host cache source `/home/inlc/.cache/huggingface` matches observed Docker host mount to `/hf` read-only. `HF_HOME=/hf`, `HF_HUB_OFFLINE=1`, model command, tool parser (`qwen3_coder`), reasoning parser (`qwen3`), chat template, GPU, IPC, shm and port all match the canonical desired runtime.
- `operations_enabled=false`, `production_released=false`, `executed=false`, `approval_accepted=false`.

The prior unpinned HF host-source advisory is gone when the operator provides an explicit source path; this does **not** alter or pin the canonical recipe.

## 2. Actual read-only recurrent operating transfer preview

- `action=OPERATING_MODEL_SWITCH_PREVIEW`, `status=READY_FOR_OPERATOR_REVIEW_ONLY`, `issues=[]`, `current_ids_from_live_docker=true`.
- `source_model=27b`, `source_lineage=CANONICAL_RECIPE`, source Docker ID `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`.
- `source_recipe_sha256=301c9c7980690b97e357db5fb57090fc82c507ab9c1116c8e154739e360bbbbb`.
- `target_model=flash-next`, `target_lineage=HISTORICAL_P3_INSTANCE`, target Docker ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, target served ID `qwen3.8-flash-next`; target recipe SHA is `null` (qualified canonical Flash recipe not yet available).
- `historical_acceptance=LOCAL_P3_A_B_C_RECEIPTS_VERIFIED`; historical `p3_a_plan_id=b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`.
- The 27B/Flash image IDs both equal `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`. This alone is not a recipe conflict: both preserved containers can use the same image while serving different checkpoints/command lines. The qualified Flash provenance and preserved Docker ID are the current gate.
- `operations_enabled=false`, `execution_supported=false`, `approval_accepted=false`, `executed=false`.
- The read-only preview's expiring `plan_id` is **not an execution approval** and must not be replayed after its window. No attempt was made to use it to trigger a switch.

**Interpretation:** The earlier stale-P3-Docker-ID obstacle is resolved in actual DGX preflight for the currently running canonical 27B. Both source and target model lineages are recognized without rewriting P3-A/B/C receipts. This is NOT actual end-to-end failover/rollback qualification.

## 3. Current manifest/API status

- `status=LIVE_SERVICE_VERIFIED`; `api_health_status=API_IDENTITY_CONFIRMED`; `expected_served_id=qwen3.8-27b`, observed IDs `[qwen3.8-27b]`.
- All eight `checks` fields true: managed active model and manifest, published :8000, API HTTP/identity, listening port, served ID, manifest observation, one managed running model.
- `issues=[]`, `executed=false`.
- `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` are **scopes not verified by this status probe**, not affirmative negative findings. `manifest_status=OBSERVED_UNQUALIFIED` does not supersede the qualified historical P3 receipts or imply production switch acceptance.
- `operations_enabled=false`.

## Acceptance classification and safe next work

| Scope | Classification |
|---|---|
| Canonical 27B normalized runtime desired/observed equality, including explicit HF source | **Actual DGX read-only PASS** |
| 27B current Docker ID vs immutable historic P3-ID separation | **Actual DGX read-only PASS** |
| Canonical 27B -> preserved historic Flash target preview | **Actual DGX read-only PASS** |
| P3 immutable historical provenance check | **Actual DGX read-only PASS** |
| 27B API identity and manifest status | **Actual DGX read-only PASS** |
| Source-only Fake-DGX executor, rollback and recurrent switch tests | **CPU CI PASS**, not real DGX |
| GPU process exclusivity, process-level host port ownership | **NOT VERIFIED** |
| Live 27B -> Flash and Flash -> 27B transitions, fail/rollback paths | **NOT EXECUTED** |
| Qualification of canonical Flash runtime reinstall recipe | **PENDING** |
| General switch/lifecycle production release | **GATED / NOT AUTHORIZED** |

Source-only tests last demonstrated `814/814` in 36 groups, GitHub Actions run [42367665200](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42367665200). This document-only commit requires no new code qualification and changes no service, cache, image, recipe or P3 receipt.

**Next engineering priority:** Prepare a fully read-only GPU/port ownership audit and qualify the existing Flash runtime recipe from *observed current* Docker metadata, with tests first. Do not infer that a planning SHA authorizes execution; live model switching requires a separately approved operator maintenance window and independent released executor.
