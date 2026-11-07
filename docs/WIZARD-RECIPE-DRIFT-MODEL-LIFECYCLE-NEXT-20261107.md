# Next-session scope — Recipe-diff-aware Wizard model lifecycle

**Status as of 2026-11-07:** FUTURE WORK / NOT IMPLEMENTED / NO REAL DGX LIFECYCLE ACCEPTANCE. This is a design and acceptance handoff, not a new request to stop any service.

## Verified starting point

Actual DGX canonical NVIDIA 27B Native Tools recipe migration **COMMITTED** with structured tools, continued tool-result chat, SSE, normal chat, benchmark v2 PASS (mean client E2E 10.957 tok/s, TTFT p50 0.165412 s, three requests), old original backup deleted after PASS. User independently confirmed Open WebUI Native. The Wizard then **actually deleted** the two stopped test containers `qwen38-27b-failed-6d9ede0904c2` and `qwen38-27b-native-tools-v1`, with independent `cleanup --status=MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`. Canonical `qwen38-27b` remains running at :8000, `qwen38-flash` remains stopped, Open WebUI and Portainer remain running. Historical P3-A/B/C receipts and ordinary 14-event journal remain historical; do not rewrite them.

Canonical recipe: `recipes/qwen38-27b.runtime.json`; manifest: `runtimes/service-policy.json`. **IMPORTANT:** recipe SHA is embedded in the promoted benchmark latest pointer and immutable migration receipt; modifying that JSON (even non-runtime metadata) without a new qualification/reconciliation path will cause the existing current-recipe status check to report drift. Treat edits as a managed, versioned new recipe revision, not in-place cosmetic formatting.

## Problem and desired behavior

Today the specific 27B canonical Native Tools migration and the two-target historical cleanup were implemented in purpose-built guarded scripts. The generic Wizard model lifecycle still does not consistently compare desired recipe vs actual Docker `Config.Cmd`, environment, image digest, HF mount, port, model revision, container ID and previous qualified runtime; does not reliably offer install/remove/reinstall/recreate on a per-model basis; and may compare live Docker identities against **retired P3 stage container IDs**. `PRODUCTION_EXECUTION_RELEASED=False` for generalized production model switching is a separate release gate.

The user's desired normal behavior:

- Selected model page displays **installed / running / stopped / missing / drifted / qualified / unqualified**, plus recipe revision, current Docker container ID/image, served API ID, :8000 ownership and latest benchmark evidence.
- On **start/restart/switch**, inventory the live Docker state and compare a normalized, pinned desired recipe to actual container create parameters. **If equal:** do not recreate, use existing stopped container when compatible; **if unequal:** present meaningful field-by-field diff and a **plan to recreate**, not a blind restart, with user confirmation and downtime estimate only when grounded.
- Stop current GPU model before starting a different model. For same-model recreation: stop old; rename to rollback backup; create a new container with canonical name using pinned recipe; verify Docker identity, API model ID, chat and required tool capabilities; optionally run a new benchmark and promote latest pointer only after PASS; then delete selected backup only with explicit user approval. Retain images/HF cache and raw immutable benchmark/P3 evidence.
- Users can independently **remove and reinstall** canonical 27B or Flash-Next containers; there is **no blanket permanent deletion prohibition**. Removal of an active service requires scoped downtime confirmation and a known reinstall/rollback plan; absent or unqualified install recipes must block automatic reinstallation rather than invent configurations. An explicit whole-model uninstall must not be conflated with stopped test-container retirement.
- Track source, installed, desired, active, preserved backup, failed-candidate, and retired instance records in separate manifest/receipt scopes. Distinguish **Git desired state** from **live observed state**, and **immutable historical receipts** from current container identity. Cleanup a completed retirement only as a read-only **ALREADY_CLEANED** check.
- One active model policy (`ONE_ACTIVE_MODEL_ONLY`), fixed :8000, vLLM 0.32 only; no SGLang. Keep OpenWebUI and Portainer running; no `docker system prune`, destructive cache cleanup, guessing container IDs, stale SHA replay, or unsigned mutation.

## Expected implementation steps (GitHub directly)

1. Audit exact repo HEAD, open Draft PR #1, latest source-only CI, latest DGX receipt pointers, and actual modules `wizard/console.py`, `wizard/menus/operations/service.py`, `scripts/manager/service_manifest.py`, `scripts/manager/service_status.py`, `scripts/manager/operational_wizard.py`, `scripts/manager/operational_switch.py`, `scripts/manager/operational_executor.py`, `scripts/manager/p2_27b_recipe_migration.py`, `scripts/manager/manifest_cleanup.py`, `runtimes/service-policy.json`.
2. Define an independent schema + normalization/diff contract: compare pinned image digest, exact HF revision/cache mount and flags, model/API identity, host :8000, GPU request, start command, env and labels, policy/recipe SHA; explicitly separate irrelevant Docker metadata from meaningful serving drift. Do not mismatch a currently healthy canonical 27B simply because old P3 stage IDs are retired.
3. Implement read-only `model status` / `recipe diff` / lifecycle `--plan --json`; add guided Wizard UX with explicitly displayed changes. Use immutable plan SHA, expiration, fresh revalidation, distinct TTY approval and local lock/journal before destructive operations.
4. Add scoped, idempotent install, stop, remove, reinstall and same-model recreate, then integrate recipe-diff checks into generic restart and model switch; retain production release gate until an independently approved DGX real menu/rollback acceptance. For Flash: first pin a **qualified actual Flash-Next runtime recipe**; do not copy 27B parser flags or assume same Docker argv. Keep Orcarouter placeholder inactive until its separate P5 verification.
5. Verification: CPU/Fake-DGX tests for match/no-op, diff-to-recreate, no model installed, stale/retired stage IDs, Port 8000 conflict, GPU exclusive stop-before-start, changed image/revision/mount/flags, cancel/stale-plan, crashed Docker, incomplete/failed new model, rollback and uncertain recovery, prior immutable records, cleanup idempotency and menu numeric shortcut compatibility.
6. CI tests + documentation, then report exactly what is SOURCE-ONLY versus REAL DGX. Commit in `feature/recipe-wizard-handoff`, retain PR #1 Draft/unmerged; no separate PR/merge without user approval. Real DGX container recreation/benchmark/rollback requires independent operator approval and evidence.

## Stage status boundaries

- P1 Flash-Next and original P2 27B bounded trial: historical real PASS.
- P2-FINAL canonical 27B Native Tools + benchmark v2 + OpenWebUI Native: real PASS.
- P3-A/B/C historical one-off stages: real PASS, **C CLOSED**. Do not replay. Historical ordinary 27B↔Flash both-direction backend trials passed BEFORE canonical container ID change; do not silently treat them as post-change production qualification.
- Wizard two-container exact manifest cleanup: real DONE. `cleanup --status` remains read-only status.
- P8 conditional deferral of failing second canonical recipe migration: **INACTIVE** since actual second run PASSED.
- Generic repeatable Wizard lifecycle, recipe-diff-aware recreate, current-ID-aware switch, deliberate fault-injection recovery, main menu production release: NOT YET QUALIFIED.
- P4 storage, P5 Orcarouter, P6 Orcarouter↔27B, P7 proxy/gateway remain separately scoped future work.
