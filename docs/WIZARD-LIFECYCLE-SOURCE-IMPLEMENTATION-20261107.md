# 2026-11-07 — Generic Wizard recipe drift and model lifecycle source implementation

**Scope:** SOURCE-ONLY, CPU/Fake-DGX validated. NOT a DGX live lifecycle release or approval to stop a live service. Prior P2-FINAL Native Tools, P3-C CLOSED, and manifest cleanup remain historical successes.

## Implemented

- scripts/manager/recipe_drift.py: read-only normalized desired-vs-live Docker inspection for 27B. This checks immutable canonical recipe SHA, local pinned image ID, exact checkpoint/revision path, served API model ID, Config.Cmd flags, GPU access, host port :8000, IPC, shared memory, /hf bind RO status, HF_HOME/HF_HUB_OFFLINE, and stable recipe label. Dynamic migration labels are not treated as recipe drift; CURRENT container IDs are identity-bound to each read-only plan, never the old P3 IDs.
- Explicit host cache source checking is supported only when a trusted path is supplied. The existing committed 27B recipe does not pin a host source; absence of this check creates advisory HOST_HF_CACHE_SOURCE_NOT_PINNED_IN_RECIPE. A missing-container install must not guess the cache root.
- Plans distinguish missing, stopped, running, no-op, install, start existing, restart existing, stop, remove, and recreate. Semantic command drift triggers recreate rather than unsafe restart. Live Docker-name, GPU and Docker port-binding observations block known conflicts. Process-level external socket ownership requires further DGX acceptance.
- CLI: ./wizard.sh model 27b recipe-diff --json ; ./wizard.sh model 27b lifecycle restart --plan --json ; ./wizard.sh model 27b lifecycle reinstall --plan --json ; ./wizard.sh model 27b lifecycle remove --plan --json . These are READ-ONLY. Approval and --execute are rejected.
- Interactive Wizard model menu adds option 7 Recipe diff / container lifecycle review. Original numbered menu choices are preserved.
- scripts/manager/model_lifecycle.py: guarded SOURCE-ONLY transaction scaffold with an injected Fake-DGX backend for tests. Concrete Docker adapter reuses the single qualified canonical 27B launch generator; setup includes separate exact fresh SHA/TTY/downtime/removal approval checks, private locks, write-once attempt/events/results, stop-before-start, rollback backup renaming, container-only remove/recreate, API/chat/structured-tool/SSE verification and bounded benchmark pass check. On failure, source restoration is attempted; unrecoverable failures return RECOVERY_UNCERTAIN. Successful recreation retains the backup; separate approval is needed before cleanup.
- PRODUCTION_LIFECYCLE_RELEASED=False is hardcoded; the normal Wizard cannot dispatch this transaction and no CLI flag overrides the gate. No actual DGX GPU, Docker or API mutation was executed.
- New CPU suites: tests/test_recipe_drift_cpu.py and tests/test_model_lifecycle_cpu.py. Included in recipe-manifest-cpu workflow. Run 42355750124: 799/799 PASS across 36 test groups. This CI does not verify real DGX runtime.

## Safety and remaining work

1. Run current DGX READ-ONLY recipe diff and inspect Docker Config.Cmd, full image ID, /hf bind path and RO, network port, GPU requests and API ID. Correct any discovered false-positive normalizations before approving a lifecycle trial.
2. Pin and verify a qualified Flash-Next runtime recipe, separate from 27B parser settings. Orcarouter must remain P5-unqualified. There is no blanket prohibition on container deletion; actual removal without a qualified reinstall plan remains blocked.
3. Current source transaction checks a fresh 27B benchmark for pass, but does not publish/promote a new latest benchmark pointer or clean up successful rollback backups. Add separate explicit cleanup approval and atomic benchmark publication with immutable old receipts preserved.
4. operational_switch.py and operational_executor.py still compare some live Docker identities against old P3-A/B/C stage IDs. Refactor to live observed current IDs and distinct historical provenance, before generic production switch release.
5. Complete independent DGX operator-approved real menu, happy-path, failure injection, rollback and recovery acceptance. Do not relax PRODUCTION_EXECUTION_RELEASED or PRODUCTION_LIFECYCLE_RELEASED before that.
6. Secure write-ahead journal and crash consistency for the generalized executor need further hardening and on-device testing. Never blind-retry RECOVERY_UNCERTAIN.

## Read-only DGX commands after clean fast-forward

  ./wizard.sh model 27b recipe-diff --json
  ./wizard.sh model 27b lifecycle restart --plan --json
  ./wizard.sh model 27b lifecycle reinstall --plan --json
  ./wizard.sh service manager status --json

Preserve the qualified recipes/qwen38-27b.runtime.json byte-for-byte and historic P3/benchmark receipts. Keep active 27B on :8000, qwen38-flash stopped, Open WebUI/Portainer unaffected. Do not rerun P3-A/B/C, use consumed SHA, purge Docker/images/HF cache, or dispatch generalized --execute. Real service downtime requires separate operator approval.

## Stage truth

P1 / P2 / P2-FINAL Native Tools / Open WebUI Native / P3-A/B/C (C CLOSED) / exact manifest retire-cleanup: historical real PASS/DONE. Generic lifecycle: SOURCE-ONLY 799/799 CI PASS; REAL DGX NOT_RUN, PRODUCTION NOT_RELEASED. P4-P7 follow-up. P8 condition inactive.
