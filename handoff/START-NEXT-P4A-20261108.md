# New conversation starter — Blazux DGX Spark / Wizard P4-A capacity and asset survey

Continue the existing Blazux model-recipe/Wizard/service management project. **The immediate assignment is P4-A read-only capacity and current-state inventory on the real DGX Spark, NOT any cleanup action.** Do not stop at a high-level plan: inspect GitHub, read current docs and code, analyze real operator results when provided, fix source-only issues, test, commit to existing branch, and update handoff. Never execute a live DGX mutation without separately explicit operator approval.

## GitHub and environment
- Repo: https://github.com/kjlee-inlct/qwen3.8-Flash-DGX
- Branch: `feature/recipe-wizard-handoff`; existing PR #1 **Open/Draft/Unmerged**; parallel branch `feature/orcarouter-bf16-adapter`; upstream `blazux/qwen3.8-Flash-DGX`.
- **Pre-handoff HEAD:** `99ee6b83266c824bc32bf5c8431cfe1c2e5f9fff` (new handoff/audit docs may advance this); [GitHub Actions run 42395478976](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42395478976) **SUCCESS, 887/887 CPU/Fake-DGX PASS across 40 groups**. Re-fetch actual latest HEAD/PR/CI before edits; don't assume these values remain current.
- DGX path `~/Workspace/llm/blazux-orcarouter`; NVIDIA DGX Spark GB10, Ubuntu ARM64, vLLM **0.32.0** (not SGLang); `./wizard.sh`; OpenAI-compatible `:8000/v1`; strict `ONE_ACTIVE_MODEL_ONLY`.

## Mandatory document audit before changing code
- All 8 standard `handoff/` files: `README.md`, `CURRENT-STATE.md`, `OPERATING-RULES.md`, `NEXT-ACTIONS.md`, `EVIDENCE-LEDGER.md`, `DECISIONS.md`, `CHANGELOG.md`, `SESSION-START-PROMPT.md`.
- Current P4-A: `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md`.
- P3 closed source handoff: `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`, `docs/P3-E-TO-P8-FLASH-REINSTALL-HANDOFF-20261108.md`, `docs/P3-E-FLASH-HOST-ASSET-PREFLIGHT-20261108.md`, `docs/P3-E-F-DGX-READONLY-20261108.md`, `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.
- Acceptance and real DGX transfer: `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`, `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`, `docs/P3-G-LIVE-BIDIRECTIONAL-SWITCH-PASS-20261107.md`.
- P8 boundaries: `docs/P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md`.
- Designs and manifest contracts: `docs/MODEL-RECIPE-WIZARD-PLAN.md`, `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`, `docs/WIZARD-CLI-CONTRACT.md`, `docs/MANIFEST-CONTRACTS.md`, `runtimes/service-policy.json`, `runtimes/model-discovery.json`, `recipes/qwen38-27b.runtime.json`, `recipes/qwen38-flash-next.runtime.draft.json`.
- Current document audit: `docs/HANDOFF-DOCUMENT-AUDIT-20261108.md`. Old 20261107 document audits and older sections are history, not current directives.

## Fixed completed/migrated results — never replay
- P1 NVIDIA Flash-Next and P2 NVIDIA 27B historical actual DGX API/verify/benchmark; native tool calling for 27B including Open WebUI user confirmation accepted.
- **P3-A/B/C/G REAL PASS/CLOSED**, historical separate operator-approved transfers; never replay or reuse old SHA approvals.
- P3-D independent :8000 IPv4/IPv6 docker-proxy/GPU PID read-only PASS only at the measured time.
- **P3-E source/metadata DGX handoff COMPLETE**: Flash FP8 hybrid pinned `fc694b54fb0174e0913e6adf86691ef85a4ead47`, 31,907,813-byte index with 299,845 `weight_map` entries, 11 referenced shards with apparent size sum 129,771,270,410 bytes; metadata/template fingerprints; `issues=[]`, status `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`. Large shards not cryptographically hashed; no actual fresh canonical reinstall proven.
- **P3-F current local 7-suite 168/168 CPU PASS**. `PRODUCTION_LIFECYCLE_RELEASED=False`, generic live install/recreate/recovery not released. Source CI ≠ real DGX runtime.
- Last real service observation: NVIDIA 27B `qwen38-27b`, served `qwen3.8-27b` on host 8000, `LIVE_SERVICE_VERIFIED` (8/8). That status does not independently recheck GPU/PID ownership.
- **P8 owns** remaining canonical Flash recipe/real reinstall, generic lifecycle production acceptance, forced failures/automatic source restoration and final Wizard operating signoff; **NOT_RUN/NOT_RELEASED**. Do not initiate P8 tests.

## P4-A precise task
- P4-A is **READ-ONLY**. First inspect existing `scripts/manager/p4_a_inventory.py`, `wizard/menus/storage/flash_next_cleanup.py`, `wizard/main.py`, `wizard/console.py`, `wizard/roadmap.py`, `scripts/manager/installed_models.py`, `scripts/manager/recipe_drift.py`, `scripts/manager/service_status.py`, `runtimes/model-discovery.json`, `tests/test_p4_a_inventory_cpu.py`, `tests/test_wizard_router_cpu.py`, and `.github/workflows/recipe-manifest-cpu.yml`. Preserve existing Wizard UX and CLI aliases.
- Use `./wizard.sh storage flash-next inventory --json` or `./wizard.sh p4 inventory --json` after safe `git status --short` and `git pull --ff-only`. These are the **next operator-side read-only commands**; the actual P4-A DGX inventory has **NOT YET BEEN PROVIDED**. Never claim real capacity values from the source tests.
- Inspect current 27B/Flash/Orcarouter container presence/activity, Docker image/container/volume/build cache categories (`docker system df` display estimates), HF cache and per-model repository **allocated** bytes, filesystem total/free bytes, mounted `/hf` references and historical receipts.
- Separate **apparent model shard size** and per-directory allocated bytes from **actually reclaimable** capacity. Model snapshots, shared layers, symlinks, hardlinks and nested cache directories may overlap; never add these as independent savings. The old Flash shard stat total 129,771,270,410 bytes is **not** verified freeable space.
- Report clear preservation needs for active 27B, P8 Flash reinstall/rollback baseline, Orcarouter, HF model blobs/image layers, template, journals and receipts. Missing/partial observation must be a warning and not a deletion decision.
- If P4-A observer fails, update **read-only code only**, add Fake-DGX tests, run source CI and update the existing branch/PR and handoff. Report evidence vs inference and numeric uncertainty.
- P4-B optional cleanup candidate evaluation and P4-C execution remain **NOT_STARTED / NOT_APPROVED**. Require a separate user's explicit scope decision before doing either. There is NO authorization to delete containers, images or model files, nor to run Docker stop/start/prune/rename, switch services or create a removal approval SHA.

## Operating rules
One active GPU model, vLLM 0.32, no SGLang, :8000. Preserve original 27B canonical recipe bytes and historic receipts, caches, Flash prepared FP8 hybrid view and snapshots. Keep Open WebUI/Portainer running. No `git reset --hard`, `git clean -fd`, unapproved DGX service changes, new PR/merge, P3 A/B/C/G replay, P8 fault injection or accidental production gate enablement. Source-only CI is not real DGX acceptance.

## Expected next session output
1. **WHAT CHANGED:** audited source/docs and safe P4-A improvements or no modifications.
2. **GITHUB:** actual latest HEAD, PR state, commit(s), CI groups/tests/status.
3. **TEST RESULTS:** separate source CPU/Fake-DGX from operator-provided real P4-A DGX observations.
4. **P3 / P8:** P3 source/metadata/CPU completed; production reinstall/fault/release still pending P8.
5. **P4-A CAPACITY:** per-model/cache/container allocated sizes, filesystem free, Docker reported reclaimable estimates and limitations.
6. **RECOMMENDATION:** preserve / possibly review / unknown with reasoning, **not** removal execution.
7. **SAFETY:** unchanged source, port/GPU exclusivity boundary, approvals, immutable receipts and release gates.
8. **NEXT ACTIONS:** further read-only checks or a separate request for P4-B if warranted; do not perform P4-C.

**Start by checking GitHub latest HEAD/PR/CI, mandatory documents, and actual P4-A source. Then request or analyze the real DGX P4-A JSON, and implement/document only justified safe corrections.**
