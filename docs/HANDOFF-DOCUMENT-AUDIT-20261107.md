# 2026-11-07 — Hand-off document completeness and staleness audit

## Verified GitHub state at start of audit

- Repository: `kjlee-inlct/qwen3.8-Flash-DGX`, branch `feature/recipe-wizard-handoff`.
- PR #1: Open, Draft, unmerged. Preserve existing branch/PR; do not create or merge another without separate user direction.
- Pre-audit confirmed HEAD: `9ec7420b74369e7a76785577dc543f9dafb8897d`. Later audit-only docs edits advance HEAD; new session MUST re-fetch.
- GitHub Actions source-only workflow for that commit: run `42352654468`, `SUCCESS`. Decoded job log showed **757/757 unit tests** across **34 Python unittest groups**, all completed successfully. This is NOT GPU or real DGX validation.
- Actual operator DGX: canonical 27B Native Tools + benchmark-v2 + Open WebUI Native confirmed; two stopped old test containers cleaned via Wizard, separate postcheck PASS, current `qwen38-27b` API `qwen3.8-27b` at :8000. See linked real-evidence docs.

## Verified existing required file list (25/25)

**Eight handoff entry points (all exist):**
`handoff/README.md`,
`handoff/CURRENT-STATE.md`,
`handoff/OPERATING-RULES.md`,
`handoff/NEXT-ACTIONS.md`,
`handoff/EVIDENCE-LEDGER.md`,
`handoff/DECISIONS.md`,
`handoff/CHANGELOG.md`,
`handoff/SESSION-START-PROMPT.md`.

**Twelve implementation/acceptance docs (all exist):**
`docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`,
`docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`,
`docs/P2-27B-WIZARD-OPERATIONS.md`,
`docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md`,
`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md`,
`docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`,
`docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md`,
`docs/MODEL-RECIPE-WIZARD-PLAN.md`,
`docs/UNIFIED-MODEL-WIZARD-DESIGN.md`,
`docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md`,
`docs/WIZARD-CLI-CONTRACT.md`,
`docs/MANIFEST-CONTRACTS.md`.

**Five manifest, recipe and benchmark index files (all exist):**
`runtimes/service-policy.json`,
`runtimes/model-discovery.json`,
`recipes/README.md`,
`scripts/temporary/README.md`,
`benchmarks/published/README.md`.

**Both published benchmark collection directories exist**, as GitHub returned explicit "path points to a directory" for `benchmarks/published/qwen3.8-flash-next/` and `benchmarks/published/qwen3.8-27b/`. This confirms directory existence, **not an exhaustive audit of file contents within them**.

**Additional current-evidence files verified to exist:**
`docs/P2-27B-CANONICAL-NATIVE-RECIPE-LIVE-PASS-20261107.md`,
`docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md`,
`docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-20261107.md`,
`docs/P8-27B-NATIVE-RECIPE-DEFER-IF-V2-FAIL-20261107.md`,
`recipes/qwen38-27b.runtime.json`,
`scripts/manager/p2_27b_recipe_migration.py`,
`scripts/manager/manifest_cleanup.py`,
`scripts/manager/operational_wizard.py`,
`scripts/manager/operational_switch.py`,
`wizard/console.py`,
`wizard/menus/operations/service.py`,
`tests/test_manifest_cleanup_cpu.py`,
`.github/workflows/recipe-manifest-cpu.yml`.

## Staleness findings and remedy

- The historical starting prompt (provided by the user) was written **before the real canonical 27B Native Tools adoption and real cleanup**. Its HTTP-400 error, "do not recreate old 27B" restrictions and next P2-FINAL focus are no longer current.
- `handoff/README.md`, `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`, `docs/P2-27B-WIZARD-OPERATIONS.md`, `docs/MANIFEST-CONTRACTS.md`, and `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md` had stale-looking first headers; **a clearly marked current-priority superseding section was prepended**, keeping historical failure records intact.
- New permanent scope: `docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md` explicitly defines next session's unfinished generic Wizard recipe diff/install/remove/reinstall/recreate/current-ID-aware switch, approval, resilience and CI plan.
- The canonical recipe JSON's exact byte SHA is referenced by live promoted benchmark/migration evidence: do **not** alter `recipes/qwen38-27b.runtime.json` simply to freshen cosmetic qualification metadata. Use new pinned version/migration if changing any recipe value.
- Completed one-time retired-container batch remains historical manifest evidence; the Wizard should not issue new deletion approval for it. User **does not** prohibit removal/reinstallation of canonical 27B or Flash by future correctly scoped Wizard lifecycle commands.
- The latest `handoff/SESSION-START-PROMPT.md` begins with a complete CURRENT next-conversation prompt; any earlier starter text remains archived as history and MUST NOT supersede it.

## Known NOT-YET accepted items (not missing documents)

- Generic Wizard model install/remove/reinstall; recipe-diff detection at every start/restart/switch; versioned safe recreate; live current-Docker-ID authority decoupled from historical P3 receipt IDs.
- Updated real DGX guided/interactive Wizard production model-switch tests after canonical 27B ID replacement, independent fault-injection/rollback qualification and production release flag.
- P4 storage cleanup, P5 Orcarouter BF16 PLE model, P6 Orcarouter↔27B, P7 service/proxy/gateway; conditional P8 migration failure ticket remains INACTIVE.
- Existing Flash-Next precise reinstall recipe and full generic production operator workflow remain subject to review. Do not fabricate or enable missing behavior.
