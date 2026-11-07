## 2026-11-08 — P3-D latest current PID proof and P3-E/F source follow-up

Operator's latest DGX read-only `--sudo-ss` P3-D/E/F/G output: **P3-D READ_ONLY_PASS**, independently attributed docker-proxy IPv4 PID `2560693` and IPv6 PID `2560708`, GPU PID `2560905`, no detected GPU ownership conflict. **P3-E DRAFT_REVIEW_REQUIRED** despite `cmd_normalized=true` using `FLASH_FP8HYBRID_READ_ONLY_V1`, `cmd_normalization_error=null`, draft-field `issues=[]`, because canonical reinstall remains unqualified. **P3-F 153/153 DGX-local CPU PASS**. P3-G preview in this particular runner does not invalidate previously completed real bidirectional G. `blocked_stages=[]` with total `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` is expected.

GitHub source: [03cbe4c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/03cbe4cc45a750322c4f99616c85f1061f7b2288), [2b44ccc](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/2b44ccc0237fa34742e28608ad089cb3ca90fe55), and [8e8fcec](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/8e8fcec5acb280e01445a2bd773fc9f4ecedf2f6). Source-only CI [42390619936](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42390619936): **870/870 PASS, 39 groups**, including 5 new Flash host asset tests. **No acceptance promotion**: P3-D latest READ_ONLY_PASS on real DGX, P3-E still source draft/no canonical reinstall, P3-F local 153 CPU test PASS but production executor blocked; P3-G prior independent real both-direction transfer PASS/CLOSED. P8 deliberate fault/recovery and final go-live NOT_RUN. The new host asset command has not yet been run on DGX and must not mark E as qualified from CI alone.

---

## Source-only addendum — 2026-11-08 (P3-E/F hardening)

Source change: [d68106a](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d68106a24c4c6071acff7a4d98d74e04c6ecbfe1). Actual GitHub Actions [42386939625](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42386939625): **862/862 PASS in 38 CPU/Fake-DGX groups** (856 baseline + 6 new). This is **SOURCE-ONLY**; no fresh DGX test or service change. Full scope: `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

Acceptance milestones **unchanged**: P3-E `DRAFT_REVIEW_REQUIRED`, no qualified Flash canonical reinstall; P3-F `SOURCE_CPU_PASS_NOT_RELEASED`, generic lifecycle execution blocked; P3-G `REAL BIDIRECTIONAL PASS / CLOSED` from original operator DGX receipts; P8 `NOT_RUN / NOT_RELEASED`. No new DGX runtime/rollback/benchmark measurement or production release.

---

## 2026-11-07 — AUDITED P3-A–G; G CLOSED, FAILURE/FINAL RELEASE REASSIGNED TO P8

**Latest acceptance audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`. Historical **A/B/C REAL PASS/CLOSED** (Flash→27B, 27B→Flash, Flash→27B; immutable original receipts); **D REAL READ_ONLY_PASS** for single GPU and independently attributed IPv4/IPv6 host :8000 process ownership (measured before most recent roundtrip); **E DRAFT_REVIEW_REQUIRED** despite confirmed NVIDIA Flash `-fp8hybrid` source variant and source-draft documented-field match because **canonical reinstall-qualified Flash recipe is NOT registered or real tested**; **F 144/144 local Fake-DGX/CPU PASS** with production lifecycle release still OFF; **G REAL BIDIRECTIONAL PASS/CLOSED**, two separately authorized 27B→Flash→27B live transfers, current last observed 27B API `qwen3.8-27b`, `diff=[]`, journal `VERIFIED/COMMITTED` 28 events. **P3-A~G aggregate is NOT fully complete because E remains OPEN and F is only source-qualified.** Don't replay A/B/C/G. The operator reclassified deliberate fault injection, automatic source restoration and final production/UX signoff exclusively as **P8**, which is `NOT_RUN/NOT_RELEASED` and does not block G's closed successful-transfer scope. P7 remains component integration only. Source-only CI after P8 registration: [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS, **856/856 CPU tests / 38 groups**; that does not evidence new DGX runtime results.

P3-E remains the sole currently open *canonical reinstall qualification* among A-G; P3-F CPU suite accepted as source-only scope but generic lifecycle remains locked pending distinct operational authorization. P8 final Go/No-Go and recovery must not be backfilled from G.

---

# P1–P8 Wizard acceptance status — canonical milestone scope (2026-11-07)

> This document supersedes phase **scope** and status headings in the older historical `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md`; it does **not** alter immutable execution receipts or rewrite historical evidence. All live statuses below reflect the last **operator-provided** DGX output, not a new probe from GitHub.

## Scope and current status

| Phase | Acceptance objective | Current evidence classification |
| --- | --- | --- |
| P1 | NVIDIA Flash-Next source/runtime/API/benchmark | Prior real DGX P1 checks passed; refer to prior immutable records |
| P2 | NVIDIA 27B pinned download/start/API/native tool calling/benchmark | Prior real DGX P2 checks passed; canonical 27B recipe SHA preserved |
| P3-A/B/C | Original one-off stage sequence; exact receipts | **REAL PASS / CLOSED** |
| P3-D | Exclusive GPU process and host port-8000 PID provenance | **READ_ONLY_PASS** on real DGX with explicitly opted-in `sudo -n ss` |
| P3-E | Flash runtime provenance, canonical reinstall-ready recipe | **DRAFT_REVIEW_REQUIRED**: pinned `-fp8hybrid` snapshot and documented draft fields matched, but canonical reinstall unqualified |
| P3-F | Generic lifecycle operations' CPU/Fake-DGX source gates | **SOURCE_CPU_PASS_NOT_RELEASED**; last supplied local batch 144/144 PASS |
| **P3-G** | **Real 27B↔Flash-Next successful independent bidirectional operating transfers, API/journal and canonical recipe postchecks** | **REAL PASS / CLOSED** — two separate DGX TTY-authorized switches and reverse 27B `diff=[]` |
| P4 | Optional Flash storage cleanup/reinstall disposition | Optional; NOT_APPLICABLE may be chosen if no need for deletion |
| P5 | Orcarouter deployment/API/bench | PENDING |
| P6 | Orcarouter↔27B real transfer | PENDING |
| **P7** | **Service/proxy/gateway integration and numerical/CI qualification** | PENDING; **does not include final signoff** |
| **P8** | **Deliberate controlled fault injection, automatic source restoration real verification, final operating UX/security/production release signoff** | **NOT_RUN / NOT_RELEASED** |

## Real P3-G bidirectional evidence

1. `27b → flash-next`: independent execution SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`, operator `PASS`, Flash served API `qwen3.8-flash-next`, journal `VERIFIED/COMMITTED`, 21 events.
2. `flash-next → 27b`: independent execution SHA `a909a1470760613b3d8e1f588dada06a41205ceac7e07c5ff464eac01884ed8b`, operator `PASS`, 27B served API `qwen3.8-27b`, journal `VERIFIED/COMMITTED`, 28 events. 27B canonical recipe diff `[]`, issues `[]`. Source: `docs/P3-G-LIVE-BIDIRECTIONAL-SWITCH-PASS-20261107.md`.

**Current last-observed running model**: NVIDIA 27B, host port 8000; one managed model according to manifest-led service check. The `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` of the basic status command mean that command doesn't independently audit those properties, not that collisions were observed.

**P3-G completion is limited to successful two-way transfers**, not claim of fault-tolerance under injected failure. P3-E Flash reinstall recipe qualification, P3-F general lifecycle/production dispatch and P8 release remain independently pending. No forced error, deletion, image/cache purge or irreversible service change is authorized by phase renumbering.

## P8 safety contract

P8-A fault matrix and live bounds; P8-B Fake-DGX recovery/journal and negative tests; P8-C independently approved DGX bounded failure and verified **automatic source restoration**; P8-D full Wizard final integrated operations/UX/security and go-live signoff. Details `docs/P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md`.

A successful *source-only* P8 plan or Fake-DGX tests **cannot** mark P8-C or P8-D PASS, cannot set `production_released=true`, and cannot dispatch Docker/GPU fault injection. The new Wizard P8 menu is deliberately `INTERFACE_ONLY / BLOCKED`.

## Handoff rule

Future work on P4–P7 may proceed without reopening P3-G. P8 remains the dedicated safety/end-to-end acceptance milestone. Preserve old DGX switch receipts, preserve model files/HF cache and vLLM 0.32/API 8000/ONE_ACTIVE_MODEL_ONLY rules; do not use SGLang. PR #1 stays Draft/unmerged until a separate release decision.
