# P5 handoff completeness + source compatibility audit — 2026-11-08

## Purpose and provenance

Before starting P5 in a **new** conversation, verify that all core handoff and historical acceptance evidence remain in GitHub and that the YSLAB reference is not mistakenly treated as the Blazux runtime. This audit covers **file presence and selected source content**, not line-by-line validation of every historical document or proof of full DGX model integrity. The P5 implementation is not being performed in this handoff-only session.

- Current fork: `kjlee-inlct/qwen3.8-Flash-DGX` branch `feature/recipe-wizard-handoff`, **pre-handoff HEAD** `ac88693196a8b2b5efc95f091dc88531d6951037`; tree `ebb8b191ba80c9523359c377aef88b75a4dfbe9c`, 467 entries total, untruncated. GitHub PR #1 `Open/Draft/Unmerged`. Latest pre-handoff Actions run [42405103774](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42405103774) `completed/success`; source tests previously 902/902 in 41 groups. New documentation commits will advance HEAD; always re-query.
- External YSLAB `YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark` main `9492b78c6bc04638587b42f2ffeb0680b0fcb3ef`, tree `5cd0a90f9968a6aa5d5ac06bef90912d33a5494f`, 87 entries, untruncated, read-only accessible.
- Existing parallel Orcarouter branch `feature/orcarouter-bf16-adapter@620598c30cfe3521af99a935caf0baf5b83556d8` with `docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md`, **not merged**, design-only historic evidence.

## Actual Git tree existence audit

**All 34/34 previously required files still exist (no missing files):**

| Group | Expected | Present | Missing |
|---|---:|---:|---:|
| Standard handoff documents: README, CURRENT-STATE, OPERATING-RULES, NEXT-ACTIONS, EVIDENCE-LEDGER, DECISIONS, CHANGELOG, SESSION-START-PROMPT | 8 | 8 | 0 |
| P3 and P1–P8 acceptance evidence documents as enumerated by `docs/HANDOFF-DOCUMENT-AUDIT-20261108.md` | 8 | 8 | 0 |
| P4-A plan `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md` | 1 | 1 | 0 |
| P8 plans (fault recovery + 27B recipe defer) | 2 | 2 | 0 |
| Design / historic audit/transition docs | 8 | 8 | 0 |
| Runtime/model discovery / recipe / temporary-scripts / benchmark readmes | 7 | 7 | 0 |
| **Total** | **34** | **34** | **0** |

Additionally the latest P4 source/evidence group has **7/7 existing**: `docs/P4-A-DGX-READONLY-CAPACITY-EVIDENCE-20261108.md`, `docs/P4-BC-ONE-SHOT-DRY-RUN-20261108.md`, `docs/P4-BC-DGX-READONLY-DRY-RUN-EVIDENCE-20261108.md`, `scripts/manager/p4_a_inventory.py`, `scripts/manager/p4_bc_dry_run.py`, `scripts/temporary/p4-bc-dry-run.sh`, and `tests/test_p4_bc_dry_run_cpu.py`.

**Missing P5 implementation artifacts are deliberate future work, not lost records**: `recipes/qwen38-orcarouter.runtime.json` is not yet a canonical file; `scripts/temporary/p5-one-shot-acceptance.sh` and P5 unit/Fake-DGX test suites do not exist; `wizard/menus/models/orcarouter_flash_next.py` currently only defines a blocked source-only interface; `runtimes/service-policy.json.models.orcarouter` is a placeholder with `checkpoint=null`, `served_id=null`, `qualification=NOT_VERIFIED`. Do not report this as implementation PASS.

To close this **documentation-only** gap, create `docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md`, `handoff/START-NEXT-P5-20261108.md`, and this P5 audit. Update top of existing handoff without deleting historical snapshot/receipts. A new actual P5 DGX acceptance evidence file must not be created and marked PASS before real output exists.

## External reference verification and incompatible defaults

| Issue | YSLAB pinned reference | Blazux P5 requirement |
|---|---|---|
| Runtime | Dockerfile base `vllm/vllm-openai:qwen38-flash-next@sha256:fc120ece...`; label `ai.yslab.vllm.version=0.1.dev20073+g8e685d198` | **vLLM 0.32.0**, actual ABI/import audit, no standalone YSLAB runtime as production |
| Host port | YSLAB `RuntimeOptions.port=18300`, bind `127.0.0.1` | stable **:8000/v1**, unique owner; no implicit container start |
| Model | `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799` | pinned new Orcarouter opt-in target, preservation of NVIDIA 27B/Flash |
| Quantization/PLE | compressed-tensors, direct BF16 95.37GiB PLE, 128 tensors / 320001536 rows / width160 | inspect vLLM 0.32 Qwen4Exp mapping and use BF16 mmap, no NVIDIA ModelOpt hybrid assumption |
| MTP | 31 BF16 source tensors from `RadixArk/Qwen3.8-Flash-Next-NVFP4@7b719225242aacd3dbd3f9407468c2ee9a9d2594` | source shard hash/name/dtype/shape/architecture + 31/31 load guard, MTP OFF baseline then MTP=2 |
| Runtime profile | PIECEWISE, BF16 KV, `max_model_len=262144`, 8 sequences, GPU memory 0.80, PLE prewarm OFF | transfer only after compatibility/memory evidence and explicit approved trial |
| Evidence | YSLAB reports Orcarouter MTP2 44.23 tok/s versus MTP0 27.26 tok/s | reference-only measured numbers; do not claim Blazux P5 benchmark PASS |
| Auth | HF gated model requires browser approval/read token | do not expose token in logs, check small metadata first, skip download when pinned cached files qualify |

Check the following YSLAB source for correctness, not automatic compatibility: `compatibility.json`, `src/recipe/{runtime,manifest,mtp,download,audit,safetensors}.py`, `src/vllm_ple_mmap.py`, `src/patch_qwen4_exp_*.py`, `Dockerfile`, `docs/COMPATIBILITY.md`. The previous parallel Blazux design branch already notes Qwen3_8FlashNext vs Qwen4Exp class/loader and patch boundary differences; do not cherry-pick blindly. License/NOTICE and gated model terms must be respected; never redistribute weights/tokens.

## Fresh current acceptance boundary

- Actual P3-A/B/C/G operator-approved PASS/CLOSED; P3-E/F source + Flash asset audit handed to P8 for real reinstall/lifecycle. No historical P3 switches replay.
- Actual P4-A DGX capacity inventory PASS. P4-B/C **real read-only dry-run PASS** (13/13 Fake-DGX locally, 9 reviewed resource records / 0 delete selections, P4-C 2 PASS/2 deferred/1 not released/1 not executed). This is **not** real deletion authorization.
- Active model in latest actual operator evidence: 27B, API model ID `qwen3.8-27b`, port 8000. P4 cache storage observations do not imply P5 full checkpoint/overlay integrity.
- P5 not run or source-implemented on current branch; P6 switching and P8 final fault/recovery/release not run. P5 implementation will begin only in the **next** conversation, with separate exact approval for any GPU downtime or actual storage cleanup.

## Resolved handoff instructions

- Source-of-truth order: latest operator DGX data and exact logs → confirmed decisions/acceptance → current actual GitHub HEAD code/manifest → older historical design. Older `docs/HANDOFF-DOCUMENT-AUDIT-20261108.md` describes P4-A NOT_RUN and is intentionally a time-stamped old audit; **this new audit supersedes its current-stage summary**.
- Next session should build the **P5 code + CPU/Fake-DGX + integrated one-shot judge together**, not split into many micro-phases, and keep source PASS separate from real DGX GPU acceptance.
- P5 live execution requires strict one-active-model/port 8000 exclusivity, original 27B preservation and separate operator approval. P4 real deletion only for a separately approved capacity/operational issue or P8 acceptance, never automatic. Open WebUI, Portainer, HF caches, historical receipts and PR Draft status remain intact.
