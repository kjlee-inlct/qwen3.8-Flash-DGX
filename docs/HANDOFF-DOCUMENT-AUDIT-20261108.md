# Hand-off completeness and staleness audit — 2026-11-08 (P4-A next)

## Scope and live GitHub evidence

Inspected the **actual Git tree** of `feature/recipe-wizard-handoff`, not older hand-off text. **Pre-audit GitHub HEAD** `99ee6b83266c824bc32bf5c8431cfe1c2e5f9fff`; PR #1 **Open / Draft / Unmerged**. Workflow [42395478976](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42395478976) **SUCCESS**; decoded job logs show **887/887 CPU/Fake-DGX tests, 40 groups**. This CI is **source-only**, not a live P4-A DGX storage measurement. This documentation audit may advance branch HEAD; re-fetch GitHub state in the new session.

Git tree count: 459 paths, 54 under `docs/`, 10 under `handoff/`, complete nontruncated tree.

## Required document presence audit — no missing files

- **8/8 standard handoff**: `handoff/{README,CURRENT-STATE,OPERATING-RULES,NEXT-ACTIONS,EVIDENCE-LEDGER,DECISIONS,CHANGELOG,SESSION-START-PROMPT}.md`.
- **8/8 core/current P3 acceptance**: `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`, `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`, `docs/P3-G-LIVE-BIDIRECTIONAL-SWITCH-PASS-20261107.md`, `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`, `docs/P3-E-TO-P8-FLASH-REINSTALL-HANDOFF-20261108.md`, `docs/P3-E-FLASH-HOST-ASSET-PREFLIGHT-20261108.md`, `docs/P3-E-F-DGX-READONLY-20261108.md`, `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.
- **1/1 latest P4-A**: `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md`.
- **2/2 P8**: `docs/P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md`, `docs/P8-27B-NATIVE-RECIPE-DEFER-IF-V2-FAIL-20261107.md`.
- **8/8 further design/historical handoff**: `docs/MODEL-RECIPE-WIZARD-PLAN.md`, `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`, `docs/WIZARD-CLI-CONTRACT.md`, `docs/MANIFEST-CONTRACTS.md`, `docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md`, `docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md`, `docs/HANDOFF-DOCUMENT-AUDIT-20261107.md`, `handoff/START-NEXT-WIZARD-LIFECYCLE-20261107.md`.
- **7/7 recipe/manifest/supporting README**: `runtimes/service-policy.json`, `runtimes/model-discovery.json`, `recipes/qwen38-27b.runtime.json`, `recipes/qwen38-flash-next.runtime.draft.json`, `recipes/README.md`, `scripts/temporary/README.md`, `benchmarks/published/README.md`.

This audit establishes **file presence only**, not exhaustive line-by-line consistency of every historic document. Older files still contain obsolete snapshot instructions by design; do not edit original real DGX receipts or erase historical information.

## Actual current evidence classification (operator DGX vs source)

- P3-A/B/C and P3-G real operator-approved transfers **PASS / CLOSED**. P3-D independently read-only GPU/socket PID ownership PASS **at its measured time**, not continuously.
- **P3-E source/asset handoff complete**: Flash pinned NVIDIA source + `-fp8hybrid` observed, read-only asset report `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`, `issues=[]`, 31,907,813-byte index, 299,845 weight-map entries, 11 referenced shard files apparent size sum 129,771,270,410 bytes. Metadata/chat-template SHA-256 observed; large shards **not** hashed, genuine revision bytes **not** verified. Not a new canonical Flash reinstall.
- **P3-F source/CPU handoff complete**: actual DGX 7 suite **168/168 CPU PASS**; generic lifecycle `PRODUCTION_LIFECYCLE_RELEASED=False`. These results do not prove live reinstall or automated restoration.
- Last provided actual service observation: `qwen38-27b`, API `qwen3.8-27b`, :8000, 8/8 manifest/API checks true, `LIVE_SERVICE_VERIFIED`; basic status probe does not re-verify GPU PID/port process owner.
- **P4-A SOURCE READY / REAL DGX INVENTORY NOT_RUN**: `./wizard.sh storage flash-next inventory --json` (alias `./wizard.sh p4 inventory --json`) performs read-only capacity/state inspection. It reports Docker category estimates, HF configured and managed bind cache allocated sizes and free/total filesystem, active service/container. No deletions, no actual DGX capacity values yet.
- **P4-B and P4-C NOT_STARTED/NOT_APPROVED**; no candidate cleanup decision. Docker `reclaimable` estimates and HF snapshot/shard apparent sizes must not be treated as actually recoverable bytes.
- P8 owns canonical Flash reinstall qualification/actual independently authorized install/rollback, lifecycle production adapter, controlled fault/automatic source restoration, final Wizard operating signoff. P8 actual fault trial **NOT_RUN**, production release **false**.

## Stale/superseded guidance

The old pasted/example starter (“P3-E/F development next”, old HEAD `669743f...`, CI 856, 38 groups, local P3-F 144, and P4 held without exception) is **historical**, not current next-action guidance. `docs/HANDOFF-DOCUMENT-AUDIT-20261107.md` also cites an earlier 757-test snapshot; preserve it as a dated audit and use this file for 2026-11-08 state.

The `handoff/` records use prepend-only chronology; some **lower** historical sections say `P4 NOT_STARTED` or `P3-E/F open`. Those passages are superseded by the **newest top** sections, the newest user's P4-A-only decision and this audit. Do not reorder/delete history merely to normalize those old status strings.

## Next session safe execution plan

1. Re-fetch GitHub branch HEAD, existing Draft PR #1, latest CI and actual file paths; read the eight handoff files and latest P3/P4-A/P8 docs.
2. On DGX, request/read the result of **only** `./wizard.sh storage flash-next inventory --json`, after non-destructive `git status --short` and `git pull --ff-only`; never overwrite local edits or infer that the command was already run.
3. Review Docker's display `Reclaimable` as **unverified**, filesystem actual allocated/free sizes separately; identify duplicate/shared image layers, cache symlinks/hardlinks, prepared Flash FP8 hybrid view, active 27B, P8 restore dependencies, and missing measurement coverage.
4. If P4-A is partial/blocked, fix the **read-only observer** and add CPU/Fake-DGX negative tests and CI; do not infer missing assets or dispatch cleanup.
5. Produce a sourced **P4-A state/capacity report** and `KEEP / REVIEW_NEEDED / NOT_PROVEN` recommendations; only propose P4-B scope if the user separately authorizes it. P4-C removal is **not authorized**.
6. Update existing branch and Draft PR when the new P4-A evidence warrants code/docs changes, preserve vLLM 0.32, port :8000, `ONE_ACTIVE_MODEL_ONLY`, caches, 27B recipe/receipts and P8 release lock. No SGLang, no P3-A/B/C/G rerun, no new PR/merge.

See the separate new-conversation prompt `handoff/START-NEXT-P4A-20261108.md`.
