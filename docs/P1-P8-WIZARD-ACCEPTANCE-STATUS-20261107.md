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
