## ACTUAL DGX POST-EXECUTION UPDATE — 2026-11-07

**COMPLETED:** The operator approved this exact batch and actually removed both previously stopped test containers on DGX. Wizard `cleanup --execute` returned `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, `deleted[]` exactly the two registered names, `remaining=[]`, `preserved_original_model_service=true`. An independent `cleanup --status` also returned `MANIFEST_RETIRED_CONTAINERS_CLEANED` with receipt `result-39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5.json`; API service status was `LIVE_SERVICE_VERIFIED`, `qwen3.8-27b` on :8000, `issues=[]`. `docker ps -a` now lists only running `qwen38-27b`, stopped `qwen38-flash`, Open WebUI and Portainer. **Do not run the one-time cleanup procedure below again.** It is preserved for historical reproducibility only.

The current Git-tracked manifest stores the completed batch with exact consumed SHA and deleted Docker IDs; this is an **audit history**, not a pending cleanup queue. Runtime `./wizard.sh service manager cleanup --status` remains the authoritative read-only check. A repeated `cleanup --plan` returns **`ALREADY_CLEANED`** when the exact private receipt, active API and Docker absence match; it cannot create another executable plan. If they disagree, it returns BLOCKED rather than trusting Git history. See [actual DGX cleanup evidence](WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md).

---

# Wizard manifest container cleanup — 2026-11-07

## Operator-selected scope, NOT a global model deletion ban

Both **canonical `qwen38-27b` and preserved `qwen38-flash` are removable and reinstallable Docker services**. This is explicitly recorded in `runtimes/service-policy.json` under the models' `container_lifecycle`. Their temporary existence is not a reason to declare them immutable or permanently protected.

**Qualification boundary:** The Wizard has NOT yet implemented a general, repeatable managed-model uninstall/reinstall/recreate workflow. Setting `removable=true` and `reinstallable=true` expresses the policy and expected future capability; it does **not** silently enable those Docker actions. Flash's old install/recipe integration still needs verification. Removing an active service, if explicitly requested later, must first present its downtime, target selection and restore/reinstallation recipe. Historical P3 evidence and measured benchmark raw records stay meaningful as history even if a particular Docker container is deleted and recreated.

This **specific cleanup action** only retires the following two **stopped historical test containers** whose model recipe has already been promoted, and only after the operator explicitly approves:

1. `qwen38-27b-failed-6d9ede0904c2` — first canonical migration's failed-benchmark native-tools container (actual previous executor `FAIL_RESTORED`).
2. `qwen38-27b-native-tools-v1` — original experimental, subsequently stopped one-shot tool-enabled variant (actual previous executor `PASS_RESTORED`).

These are **not model definitions**; they are retired Docker container instances. **This batch is not an uninstall of NVIDIA 27B or Flash-Next.** The two targets are registered with exact name, image ID, pinned trial/container lineage, labels and immutable receipt path in `runtimes/service-policy.json` → `retired_containers.targets`.

## Read-only phase after Git Pull

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff

./wizard.sh service manager inventory --json
./wizard.sh service manager cleanup --plan
```

Require `status=READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL`, `issues=[]`, `target_count=2`, `targets[]` exactly the two intended names and both `running=false`. The bounded plan verifies current canonical 27B recipe+new benchmark receipt+API, preserved Flash state, live Docker IDs, exact labels, same pinned vLLM image and read-only HF mounts, and each candidate's original local immutable trial/migration evidence. No inference or Docker mutation in `--plan`.

A blocked plan is a **hard stop**: inspect the returned issues and actual live state; do not bypass identity checks with `docker rm -f` or invent missing lineage. This applies only to the present batch, not model uninstall rights.

## Separately approved Wizard cleanup

From a **real terminal**, after reviewing a successful plan:

```bash
./wizard.sh service manager cleanup --execute
```

Or open `./wizard.sh` → **Service health / status / logs** → **cleanup**. The operator enters a **new** full 64-character SHA printed by the interactive command, then independently confirms:

- `I_APPROVE_MANIFEST_TWO_STOPPED_CONTAINERS_ONLY`
- `I_CONFIRM_ACTIVE_27B_AND_ALL_MODEL_EVIDENCE_PRESERVED`

A fresh SHA and both exact strings are mandatory; execution repeats all identity checks under existing ordinary-switch/recipe/trial private file locks. It runs **only** `docker rm <two-exact-stopped-container-names>`, never `docker stop`, `docker rmi`, model deletion, a checkpoint download, cache deletion, volume cleanup or historical receipt editing. Each candidate is re-checked immediately before removal. If one removal fails or current identity changes, the batch stops and preserves the immutable attempt and result record for manual reconciliation; there is no silent second attempt. A container deletion itself is irreversible, although the model can be recreated from the recipe.

A fully completed result is `status=MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, two entries in `deleted[]`, and `preserved_original_model_service=true`. The private proof is written under `~/.local/state/blazux-wizard/manifest-container-cleanup/`, not by rewriting immutable prior P3/P2 logs.

## Postcheck

```bash
./wizard.sh service manager cleanup --status
./wizard.sh service manager status --json
./wizard.sh service manager inventory --json
docker ps -a --format 'table {{.Names}}\t{{.Status}}'
```

Status `MANIFEST_RETIRED_CONTAINERS_CLEANED` requires both targets absent, one signed-off result in local private receipts, and the live canonical 27B independent status still verified. The desired-state manifest retains retirement provenance as history; physical Docker observation plus private receipt establishes the **actual** cleanup completion. The manifest does not magically remove Docker containers during a Git Pull.

**As-of source commit:** User had confirmed canonical 27B Native Tools migration benchmark v2 PASS and Open WebUI Native success, but the new two-container Wizard cleanup command **has not been run on actual DGX**. GitHub source tests are not live cleanup proof.
