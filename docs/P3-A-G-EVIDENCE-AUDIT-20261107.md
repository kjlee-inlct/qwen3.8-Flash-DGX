# P3-A through P3-G — evidence-led acceptance audit (2026-11-07)

**Audit scope:** review the actual operator-provided DGX logs, the immutable historical A/B/C receipt contract and source/CPU evidence at branch `feature/recipe-wizard-handoff`. This is **not** a new DGX runtime run and does **not** replay P3 A/B/C, create/stop containers, write journal events, modify models or bypass approval. **P8 owns controlled fault injection, real automatic source restoration and final production operating signoff** per the operator's latest phase decision. The original P3-G successful transfer acceptance is not retroactively invalidated by that migration.

## Stage-by-stage classification

| Stage | Acceptance definition under current user decisions | Actual evidence and output | Audit verdict |
| --- | --- | --- | --- |
| **P3-A** | First `flash-next → 27b` one-off, independently authorized | Historical private A receipt in `p3_persistent_switch`; the A/B/C receipt validator returned `LOCAL_P3_A_B_C_RECEIPTS_VERIFIED`, with executed/pinned-lineage/chronology checks; operator's original real A PASS | **REAL PASS / CLOSED (historical)** |
| **P3-B** | `27b → flash-next` one-off, remeasure/verify Flash | Original real B PASS and Flash-Next post-B API/benchmark evidence; its private B receipt shares the immutable A lineage and passed the A/B/C validator | **REAL PASS / CLOSED (historical)** |
| **P3-C** | Final original `flash-next → 27b` return | Original operator P3-C `status=PASS/stage=c/executed=true/live_verified=true`, final `P3_C_PASS_FINAL_27B_ACTIVE` and served ID `qwen3.8-27b` at :8000 | **REAL PASS / CLOSED (historical)** |
| **P3-D** | Independent one-model GPU process and host :8000 PID ownership diagnostic | On the DGX, `--run --sudo-ss` `READ_ONLY_PASS`, `issues=[]`: compute PID 2051842 and two `docker-proxy` PIDs 2051487 and 2051502 matched the managed 27B GPU/container/host port. This evidence is **before** the later bidirectional run; basic post-reverse service manager does not audit GPU/PIDs | **REAL DGX READ_ONLY_PASS**, scoped to the measured run |
| **P3-E** | Preserved Flash FP8-hybrid runtime lineage and canonical reinstall-ready versioned recipe | Original NVIDIA source SHA `fc694b54fb0174e0913e6adf86691ef85a4ead47` with `-fp8hybrid` derived view had `hybrid_preparation_verified=true`. `source_draft_field_review.status=MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED`, `issues=[]`, draft SHA `2511a952eb6b2f5bfd4355b3d2f5469c3e624284c05e113aca63bee792f3e2a1`; `canonical_recipe_registered=false`, `FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED` | **Observed draft field match PASS; canonical reinstall acceptance OPEN** (`DRAFT_REVIEW_REQUIRED`) |
| **P3-F** | Shared Wizard lifecycle/switch/journal CPU/Fake-DGX regression safety; production authority separately gated | Latest operator local six CPU suites: 28+17+21+38+32+8 = **144/144 PASS**, zero test issues, `SOURCE_CPU_PASS_NOT_RELEASED`, `PRODUCTION_LIFECYCLE_RELEASED=false` | **CPU SOURCE PASS**; live general lifecycle install/reinstall/recreate not production-qualified |
| **P3-G** | Real ordinary bidirectional 27B↔Flash-Next transitions with separate TTY approvals, post-switch API/manifest and committed journal | First real `27b→flash-next` SHA `365099fe…a3654` **PASS**, live Flash API `qwen3.8-flash-next`, journal VERIFIED/COMMITTED, 21 events. Second real `flash-next→27b` SHA `a909a147…84ed8b` **PASS**, live 27B API `qwen3.8-27b`, journal VERIFIED/COMMITTED, 28 events, 27B `recipe-diff=[]`, issues=[] | **REAL BIDIRECTIONAL PASS / CLOSED** by the now-narrowed P3-G scope |

### P3 aggregate interpretation

**Do NOT claim `P3-A~G ALL FULL PASS`.** A, B, C, D, G have applicable real DGX PASS evidence; F **source-only CPU** PASS is valid within its declared scope; **E canonical reinstall qualification is still OPEN**. Consequently, the **P3-A–G aggregate is PARTIALLY COMPLETE**, with the one unresolved functional qualification specifically in E (plus operational lifecycle deployment authority outside F's CPU evidence). This is not an excuse to rerun closed A/B/C/G trials.

**P3-G successful bidirectional acceptance is CLOSED.** Any older document saying P3-G still requires fault injection, automatic rollback from an induced failure or final operator signoff is a historical superseded definition; these requirements now belong exclusively to P8. Their lack of real results does **not** change the already observed two-way switching PASS.

## Current actual DGX baseline and evidence boundaries

Latest actual operator reverse trial returned:
- active container `qwen38-27b`, served API `qwen3.8-27b`, port 8000, `LIVE_SERVICE_VERIFIED`, eight status checks true, issues=[].
- operational journal `VERIFIED/COMMITTED`, **28 events**, issues=[], last hash `213670149ca6ef36eabda3fe2d5b6f13ac7ec5851f12b535373a84af46efc311`.
- canonical 27B recipe `diff=[]`, `issues=[]`; `HOST_HF_CACHE_SOURCE_NOT_PINNED_IN_RECIPE` is a nonblocking host-specific bind-path advisory.
- Basic service status `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are explicitly **not measured in that query**. Do not falsely report collision or a new post-reverse P3-D GPU/PID PASS. The earlier independent D evidence remains valid for that earlier run.

Private immutable historic A/B/C and operating acceptance files are on the operator's local DGX, not accessible to the GitHub connector. Their exact bytes were **not** re-read during this GitHub audit. Historic A/B/C are supported by the verified validator output and the original operator's actual logs, not invented current file contents.

## Source / Wizard caveat found in review

The command `bash scripts/temporary/p3-d-g-acceptance.sh --run` is **deliberately read-only**. Its P3-G subsection returns `PREVIEW_PASS_REAL_SWITCH_NOT_RUN` and its `acceptance_complete=false` regardless of previously completed real standalone P3-G acceptance. That is a **scope distinction**, not a regression of the real two-way transfer. The source-runner's P3-F result covers CPU tests only. Never promote P3-E or P3-F from that result into production without their own planned qualifications.

The `wizard/roadmap.py` status dashboard is also a conservative source/current-host survey, **not** a signed audit of two distinct P3-G execution receipts. It must not advertise runtime PASS just by reading static user-facing docs. The new P8 menu and roadmap are nonmutating source interfaces.

## CI and phase boundary

GitHub Actions run [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) **SUCCESS**, **856/856 CPU tests across 38 reported groups**, including new P8 source-only router/roadmap checks. This is a source/CI proof only, not DGX P8 hardware readiness. All phases use vLLM 0.32, host port 8000, `ONE_ACTIVE_MODEL_ONLY`, and preserve model assets by default.

**Remaining roadmap:** complete/review Flash-Next canonical reinstall-ready recipe in P3-E (if qualifying full P3), keep F source gates intact, optionally record P4 `NOT_APPLICABLE`, then P5 Orcarouter, P6 Orcarouter↔27B, P7 integration, **P8 controlled fault recovery and final operational release**. No new downtime or fault test is authorized by this audit.
