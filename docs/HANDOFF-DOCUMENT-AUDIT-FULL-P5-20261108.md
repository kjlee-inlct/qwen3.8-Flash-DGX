## 2026-11-09 latest P5–P8 incremental document/path audit

**GitHub source snapshot at `5acf0b11f753615b6fba69c3d754b56d6289f325`:** recursive tree 524 entries, 482 blobs, `truncated=false`; 170 document-like files under the frozen extension/LICENSE selection. Historical enumerated 169 document paths and this audit file remain present; 2 added files since prior baseline are Python source/test (`scripts/manager/p6_p8_fakedgx.py` and `tests/test_p6_p8_fakedgx_cpu.py`), not additional documentation paths. This recheck establishes paths and selected links, not a deep content review of every document. The frozen 169-item inventory and all old approval/failure receipts are preserved below.

**Superseding evidence (operator at 2026-11-09 00:55 KST):** Orcarouter v3 MTP0 text `PASS_LIVE_INFERENCE`, service `LIVE_P5_TRIAL_API_VERIFIED`, trial only. Host MemAvailable 30.18 GiB, swap used 1.31 GiB (Orcarouter cgroup 0), Docker 7.157 GiB vs cgroup current 25.54 GiB with inactive_file 18.38 GiB, PSI 0 and OOM 0 in idle measurement. Earlier 00:43 KST and P5 v2 records remain historical. P6 source Fake-DGX + P8 synthetic matrix (`21aa6c9`) and cgroup identity-safe delta (`5acf0b1`) have Push/PR CI SUCCESS; no new real DGX execution or P6/P8 release. [P5 technical](P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md) · [P8 acceptance](P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md).

---

# Full GitHub document inventory and P5 state-consistency audit — 2026-11-08

## Incremental full-tree/document completeness recheck — 2026-11-08 P5 v3 live inference

**Repository observation at `e352a9351ed3660fb595320ea1ff0f51e347d20b`:** recursive Git tree had **520 entries, 478 blobs**, with `truncated=false`. Recomputed the exact previously defined document-like inventory criterion from `tests/test_p5_document_integrity_cpu.py`: `.md/.mdx/.rst/.adoc/.json/.yaml/.yml/.toml/.txt` and extensionless `LICENSE/NOTICE`. Result: **170 document-like blobs** (86 Markdown, 33 JSON, 40 TXT, 3 YAML, 1 YML, 7 LICENSE/NOTICE). The **169 paths** enumerated in this document's historical original list all still exist; the **only additional path** is this audit file itself. **Missing paths: 0; unlisted document-like paths: 0** (after accounting for this file). No new text/document filenames require inventory inclusion in the original frozen 169-item baseline. This is a path-level inventory and selected current-content consistency review; it is **not** a claim to re-read all 170 large document contents deeply at this recheck.

**Significant content supersessions found:** historical P5 v2/QSA-only runbooks and old `handoff/SESSION-START-PROMPT.md` top originally still described unverified GPU loading, despite later actual DGX evidence. They are preserved as historical records, but the authoritative 2026-11-08 v3 PASS section was inserted at the beginning of canonical handoff documents (including `START-NEXT-P5-20261108.md`), and a new current starter has been made the first section of `handoff/SESSION-START-PROMPT.md`. The source path `docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md` retains its historical name but begins with a current override. Do not infer status from the old filename.

**LATEST ACTUAL DGX EVIDENCE from operator transcript (not CI):** `qwen38-orcarouter-qsa62318-lmhead-v3` image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4` active at :8000, ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`. Wizard `service manager status` **`LIVE_P5_TRIAL_API_VERIFIED`**; `p5 trial verify` **`PASS_LIVE_INFERENCE`**, content `READY`. `p5 trial cleanup-execute` **`PASS`**, deleted exactly three failed exited(1) old P5 test containers (name-original, QSA-only, LM-head-v2) after archiving local private logs, preserving current v3, images and caches. **Not production released**, MTP2, tools, vision, actual memory/CPU pressure and benchmark not verified.

**Reference implementation check at YSLAB pinned public HEAD `9492b78c6bc04638587b42f2ffeb0680b0fcb3ef`:** `src/recipe/runtime.py` enforces `MIN_MEM_AVAILABLE_BYTES=100 * 1024**3` before start (can be overridden only via its explicit unsafe mechanism), profile `gpu_memory=0.80`, `VLLM_PLE_MMAP=1`, `VLLM_PLE_MMAP_WORKERS=32`, `VLLM_PLE_MMAP_PREWARM=0`; `benchmarks/stability.py` records `MemAvailable` and swap use during opt-in stability runs. No source-level CPU frequency/governor cap, cgroup hard-memory limit, PSI-based daemon or automatic host-memory pressure protector was found in the inspected reference scripts. These YSLAB profile measurements are **external context only**, not Blazux vLLM0.32 qualification. Current Blazux P5 MTP0 uses `gpu_memory_utilization=0.7`, 16 mmap gather workers, 8192 model context, one concurrent sequence; capacity not measured in supplied GPU logs. Next design: read-only baseline and recipe-owned safety gates BEFORE any intrusive throttling/limits.

**Hand-off priority order:** (1) actual P5 resource measurement and CPU/GPU/system safety requirements; (2) artifact ownership/versioned recipe, operational naming and operator-approved canonical `qwen38-orcarouter` promotion; (3) P5 MTP2, native tools, vision, benchmark; (4) P8 stays deferred. `ONE_ACTIVE_MODEL_ONLY`, :8000, vLLM0.32.0, no SGLang, P3/P4/P8 live replay forbidden, PR #1 Draft/Open/Unmerged. New conversations must verify current GitHub HEAD/CI again and never reuse historical plan IDs.

---



**2026-11-08 incremental complete-tree recheck (P5 checkpoint gate):** The updated branch tree was retrieved with `recursive=1`, `truncated=false`: **515 tree entries, 473 blobs**, of which **170 are document-like** by the same extension + LICENSE/NOTICE rule. The 170 are the original 169 enumerated items plus this audit itself; no new document-like filenames were introduced. The 4 new Python-only files are `scripts/manager/p5_lm_head_checkpoint_audit.py`, `scripts/manager/p5_checkpoint_preflight.py`, `tests/test_p5_lm_head_checkpoint_audit_cpu.py`, and `tests/test_p5_checkpoint_preflight_cpu.py`. The original 169-item file list below remains an inventory baseline and is not rewritten to include itself. Source/API/GPU states are not inferred from this code-tree inventory. Latest v2 Runbook and eight canonical handoff files were updated to point to the new read-only preflight; historical GPU failure receipts remain intact.

**Scope and method:** recursive Git tree `1494a714ef1034d69471d2e16df0ad491b6695fb` on branch `feature/recipe-wizard-handoff`, `truncated=false`. The **initial** tree at `9e7cd1b9cb18` contained 466 files and **168 document-like items**, all reviewed: 84 Markdown/markup, 77 JSON/YAML/TXT/CI/evidence (six segments each), plus **7 extensionless LICENSE/NOTICE files**. After adding the new v2 Runbook, the enumeration snapshot at `1494a714ef10` contains **467 files and 169 document-like items** (85 Markdown, including the newly authored Runbook, 77 structured/text items and 7 legal/attribution notices). This audit file was itself created after that snapshot. Each item's contents were fetched from its Git blob and inspected for subject, provenance and current-versus-historical status. Programmatic enumeration is a completeness claim for these extensions **and the seven identified extensionless notices**, **not** proof of deep semantic correctness of every historical log entry. No DGX/network service state was changed by the audit. No document is treated as live GPU evidence.

## Audit conclusion and documents that had been missed

1. **P5 runtime failure supersedes earlier 27B-live and Orcarouter NOT_RUN statements.** Operator-supplied DGX `247d31d` evidence shows successful QSA-only image build, then `FAIL_NO_ROLLBACK` after partial 17-shard loading (`lm_head.weight_scale` unregistered), 27B exited(0), both Orcarouter trial containers exited(1), host port 8000 unserved *at that observation*. Keep original private receipt; newer live state must be measured, not invented.
2. **Old Runbook is unsafe to reuse verbatim.** `docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md` points to QSA-only adapter `qwen4exp-qsa-62318-v032-v1`, target `qwen38-orcarouter-qsa62318`, and prior test commands. Superseded for future testing by **`docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md`**. Historical content preserved.
3. **Primary handoff is append-only but newest heading was behind the last real GPU evidence.** `handoff/{README,CURRENT-STATE,NEXT-ACTIONS,EVIDENCE-LEDGER,DECISIONS,CHANGELOG,OPERATING-RULES,SESSION-START-PROMPT}.md` and `handoff/START-NEXT-P5-20261108.md` need an explicit v2 authoritative pointer at the top; no rewriting/removing earlier evidence.
4. **Avoid old conversation starters.** `handoff/START-NEXT-P4A-20261108.md` and `handoff/START-NEXT-WIZARD-LIFECYCLE-20261107.md` are historical, not instructions to repeat P3/P4. `handoff/START-NEXT-P5-20261108.md` describes an earlier P5 baseline and is now overlaid by this audit and v2 runbook.
5. **Read-only capability is not GPU qualification.** `runtimes/ple-assets.json` schema v2 retains 128 BF16 PLE, with independent source/format. `runtimes/ple-loader-profiles.json` now binds the scoped v2 adapter but deliberately keeps `cuda_loader_verified=false`, `mmap_gpu_verified=false`, `autostart_released=false`. Neither model metadata nor CPU image ABI probes prove that `lm_head.weight_scale` matches a registered quantization scheme. Do not change `quantization_config.ignore` or truncate scales merely because an external forum post has a recipe.
6. **Source implementation changes are intentionally isolated.** `recipes/qwen38-orcarouter.runtime.json`, `scripts/manager/manifest_registry.py`, `scripts/manager/p5_live_trial.py`, `Dockerfile.p5.qsa62318-lmhead`, `src/p5_lm_head_quant_backport_v032.py`, `tests/test_p5_lm_head_quant_backport_cpu.py` hold the current candidate. Canonical vLLM=0.32.0; SGLang forbidden; API :8000, one model active. QSA-only image and both failed containers preserved. No checkpoint, HF-cache or 27B original image modification.
7. **Historic documents and fixtures remain historic.** 2026-10 vLLM-031/032 validation, historical P1/P2/P3/P4 evidence, previous PR/CI notes and `tests/vllm032/validation/` fixtures are not claims about current P5. Do not edit historical raw evidence to force consistency.
8. **License/NOTICE completeness:** The extensionless root/vendor/test-bundle license/attribution files were separately discovered and read after the first extension-based pass; all seven are recorded below. No source license was changed.
9. **CI/PR:** source update HEAD `9e7cd1b9cb189122cbbf319c4b274a2fa4072dd7` completed two successful GitHub Actions runs: [push #42473176346](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42473176346) and [PR #42473180100](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42473180100). These are CPU/source validations only. PR #1 stays Draft/Open/unmerged. Additional documentation commits need their own CI confirmation.

## Decisions

- **Current runtime guide:** `docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md`; exact approval token and `I_ACCEPT_P5_NO_ROLLBACK` are required for execution. `prepare` may build an isolated image; it is not read-only.
- **Current record ledger:** `handoff/EVIDENCE-LEDGER.md` newest dated entry; distinguish latest operator DGX observations from GitHub CI and external articles. If a future DGX log supersedes these, add a new entry, do not erase old history.
- **P3/P4/P8:** P3-A/B/C/G historical pass; P4-A/B/C read-only scope complete, no cleanup approved; P8 owns fault/automatic recovery/final release, NOT_RUN. P5 MTP2/Tools/Vision/bench/general P6 switch remain not qualified.
- **Reference authority:** actual newest operator DGX output, then versioned recipe/manifest/source+current runbook, then older handoff sections and original P1–P4 stories. Never let a later GitHub CPU-only test overwrite an actual GPU failure.

## Complete enumerated review inventory

The paths below are exhaustive for the audited text/document-like extensions **plus extensionless LICENSE/NOTICE** at the pre-audit tree. Counts include raw test evidence fixtures so no file is silently excluded; this is not a claim that log fixtures constitute procedural documentation.

### Markdown / markup (85, including the newly added v2 Runbook)

- `README.md`
- `benchmarks/published/README.md`
- `docs/FLASH-NEXT-8000-OPERATIONS.md`
- `docs/HANDOFF-DOCUMENT-AUDIT-20261107.md`
- `docs/HANDOFF-DOCUMENT-AUDIT-20261108.md`
- `docs/HANDOFF-DOCUMENT-AUDIT-P5-20261108.md`
- `docs/HISTORY.md`
- `docs/HOW-IT-WORKS.md`
- `docs/MANIFEST-CONTRACTS.md`
- `docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md`
- `docs/MODEL-RECIPE-WIZARD-PLAN.md`
- `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`
- `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`
- `docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md`
- `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md`
- `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`
- `docs/P1-WIZARD-OPERATIONS.md`
- `docs/P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md`
- `docs/P2-27B-CANONICAL-NATIVE-RECIPE-LIVE-PASS-20261107.md`
- `docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md`
- `docs/P2-27B-EXTERNAL-RECIPE-RESEARCH-20261107.md`
- `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`
- `docs/P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md`
- `docs/P2-27B-WIZARD-OPERATIONS.md`
- `docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md`
- `docs/P2-FINAL-NATIVE-TOOLS-ONE-SHOT-OPERATOR-20261107.md`
- `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`
- `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`
- `docs/P3-D-G-FIRST-DGX-DIAGNOSTIC-FIXES-20261107.md`
- `docs/P3-D-G-SECOND-DGX-PID-HYBRID-DIAGNOSTIC-20261107.md`
- `docs/P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md`
- `docs/P3-D-G-UNIFIED-WIZARD-DRAFT-ACCEPTANCE-20261107.md`
- `docs/P3-E-F-DGX-READONLY-20261108.md`
- `docs/P3-E-F-SOURCE-HARDENING-20261108.md`
- `docs/P3-E-FLASH-FP8HYBRID-SOURCE-DRAFT-20261107.md`
- `docs/P3-E-FLASH-HOST-ASSET-PREFLIGHT-20261108.md`
- `docs/P3-E-TO-P8-FLASH-REINSTALL-HANDOFF-20261108.md`
- `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`
- `docs/P3-G-LIVE-BIDIRECTIONAL-SWITCH-PASS-20261107.md`
- `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`
- `docs/P3-MANUAL-TRANSITION-SEQUENCE-20261106.md`
- `docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md`
- `docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md`
- `docs/P4-A-DGX-READONLY-CAPACITY-EVIDENCE-20261108.md`
- `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md`
- `docs/P4-BC-DGX-READONLY-DRY-RUN-EVIDENCE-20261108.md`
- `docs/P4-BC-ONE-SHOT-DRY-RUN-20261108.md`
- `docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md`
- `docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md`
- `docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md`
- `docs/P5-PLE-FORMAT-AND-DGX-SPARK-REFERENCE-ADOPTION-20261108.md`
- `docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md`
- `docs/P8-27B-NATIVE-RECIPE-DEFER-IF-V2-FAIL-20261107.md`
- `docs/P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md`
- `docs/SAFE-OUTPUT.md`
- `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`
- `docs/VLLM-031.md`
- `docs/VLLM-032.md`
- `docs/WIZARD-27B-LIVE-DRIFT-CURRENT-ID-20261107.md`
- `docs/WIZARD-27B-OPERATIONAL-PREVIEW-DGX-PASS-20261107.md`
- `docs/WIZARD-CLI-CONTRACT.md`
- `docs/WIZARD-LIFECYCLE-SOURCE-IMPLEMENTATION-20261107.md`
- `docs/WIZARD-MANIFEST-REGISTRY-AND-PLE-ASSETS-20261108.md`
- `docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-20261107.md`
- `docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md`
- `docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md`
- `docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md`
- `handoff/CHANGELOG.md`
- `handoff/CURRENT-STATE.md`
- `handoff/DECISIONS.md`
- `handoff/EVIDENCE-LEDGER.md`
- `handoff/NEXT-ACTIONS.md`
- `handoff/OPERATING-RULES.md`
- `handoff/P2-27B-GPU-TRIAL-PASS-20261106.md`
- `handoff/README.md`
- `handoff/SESSION-START-PROMPT.md`
- `handoff/START-NEXT-P4A-20261108.md`
- `handoff/START-NEXT-P5-20261108.md`
- `handoff/START-NEXT-WIZARD-LIFECYCLE-20261107.md`
- `recipes/README.md`
- `scripts/p5_vendor/README.md`
- `scripts/temporary/README.md`
- `tests/issue31_safe_output/README.md`
- `tests/issue31_schema_arguments/README.md`
- `tests/vllm032/README.md`

### JSON / YAML / TOML / TXT / CI / captured test output (77)

- `.github/workflows/recipe-manifest-cpu.yml`
- `benchmarks/published/qwen3.8-27b/80f109dbd7c97460.json`
- `benchmarks/published/qwen3.8-flash-next/f506db4c76430674.json`
- `recipes/qwen38-27b-native-tools-v1.candidate.yaml`
- `recipes/qwen38-27b.candidate.yaml`
- `recipes/qwen38-27b.runtime.json`
- `recipes/qwen38-flash-next.runtime.draft.json`
- `recipes/qwen38-orcarouter.runtime.json`
- `requirements-manager.txt`
- `runtimes/manifest-registry.json`
- `runtimes/model-discovery.json`
- `runtimes/ple-assets.json`
- `runtimes/ple-loader-profiles.json`
- `runtimes/service-policy.json`
- `schemas/recipe.schema.json`
- `scripts/p5_vendor/compatibility.json`
- `tests/fixtures/recipe-valid.synthetic.yaml`
- `tests/issue31_safe_output/PORT-MANIFEST.json`
- `tests/issue31_safe_output/SOURCE.json`
- `tests/issue31_schema_arguments/PORT-MANIFEST.json`
- `tests/issue31_schema_arguments/SOURCE.json`
- `tests/issue31_schema_arguments/VALIDATION.json`
- `tests/vllm032/MROPE-MANIFEST.json`
- `tests/vllm032/PORT-MANIFEST.json`
- `tests/vllm032/validation/VALIDATION.json`
- `tests/vllm032/validation/cpu/hybrid-dispatch.txt`
- `tests/vllm032/validation/cpu/hybrid.txt`
- `tests/vllm032/validation/cpu/mtp.txt`
- `tests/vllm032/validation/cpu/parser-baseline.txt`
- `tests/vllm032/validation/cpu/parser-engine.txt`
- `tests/vllm032/validation/cpu/ple-constructor.txt`
- `tests/vllm032/validation/cpu/ple.txt`
- `tests/vllm032/validation/cpu/prefilter.txt`
- `tests/vllm032/validation/cpu/responses.txt`
- `tests/vllm032/validation/cpu/safe.json`
- `tests/vllm032/validation/cpu/safe.txt`
- `tests/vllm032/validation/cpu/schema.json`
- `tests/vllm032/validation/cpu/schema.txt`
- `tests/vllm032/validation/cpu/summary.txt`
- `tests/vllm032/validation/cpu/topk.txt`
- `tests/vllm032/validation/issue60-20261022/VALIDATION.json`
- `tests/vllm032/validation/issue60-20261022/baseline-mrope-qa.txt`
- `tests/vllm032/validation/issue60-20261022/candidate-build.txt`
- `tests/vllm032/validation/issue60-20261022/candidate-mrope-qa.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/hybrid-dispatch.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/hybrid-qsa.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/mrope-window.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/mtp-aux.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/ple-constructor.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/responses.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/safe-output.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/schema.txt`
- `tests/vllm032/validation/issue60-20261022/cpu/summary.json`
- `tests/vllm032/validation/issue60-20261022/gpu/baseline.json`
- `tests/vllm032/validation/issue60-20261022/gpu/candidate.json`
- `tests/vllm032/validation/issue60-20261022/runtime-comparison.json`
- `tests/vllm032/validation/issue60-20261022/upstream-floor-comparison.json`
- `tests/vllm032/validation/live-default/smoke.txt`
- `tests/vllm032/validation/live-default/startup-summary.txt`
- `tests/vllm032/validation/live-default/summary.json`
- `tests/vllm032/validation/live-fp8/long-context.json`
- `tests/vllm032/validation/live-fp8/perf.txt`
- `tests/vllm032/validation/live-fp8/protocol.json`
- `tests/vllm032/validation/live-fp8/smoke.txt`
- `tests/vllm032/validation/qwen-v031-perf-clean.txt`
- `tests/vllm032/validation/qwen-v031-prefill-fresh.txt`
- `tests/vllm032/validation/restoration.json`
- `tests/vllm032/validation/review-20261022/build.txt`
- `tests/vllm032/validation/review-20261022/hybrid-dispatch.txt`
- `tests/vllm032/validation/review-20261022/hybrid-qsa.txt`
- `tests/vllm032/validation/review-20261022/memory-build.txt`
- `tests/vllm032/validation/review-20261022/mtp-aux.txt`
- `tests/vllm032/validation/review-20261022/ple-constructor.txt`
- `tests/vllm032/validation/review-20261022/responses.txt`
- `tests/vllm032/validation/review-20261022/safe-output.txt`
- `tests/vllm032/validation/review-20261022/schema.txt`
- `tests/vllm032/validation/review-20261022/summary.json`

### Extensionless license and attribution documents (7)

- `LICENSE`
- `scripts/p5_vendor/LICENSE`
- `scripts/p5_vendor/NOTICE`
- `tests/issue31_safe_output/LICENSE`
- `tests/issue31_safe_output/NOTICE`
- `tests/issue31_schema_arguments/LICENSE`
- `tests/issue31_schema_arguments/NOTICE`

**Content checked:** root/vendor Apache-2.0 text and YSLAB attribution notice, plus the historical vLLM issue #31 source-bundle LICENSE and NOTICE files. Preserve these originals and their pinned source/provenance; do not rewrite them as current P5 runtime approvals.

## Exclusions and limits

The remaining 298 repository files are source/code, shell scripts, Dockerfiles, Git metadata, binary/test assets or other extensions and were **not** counted as document-like inventory. The P5 source/manifest/CI files noted above were separately inspected for cross-consistency, but this is not a line-by-line code audit of all 467 files in the enumeration snapshot. The user's actual DGX filesystem, Docker daemon, runtime GPU state and local private receipts are not connected to this GitHub audit. Do not assert current Docker/API availability or claim a GPU PASS from this audit.
