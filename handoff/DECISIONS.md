## D-035 — 2026-11-06 — Operator's conditional P3-A permission is NOT satisfied while P1 work remains

Operator instruction: "Flash-Next에서 추가로 해야하는거 있나요? P1 에서 안한거 있는지 점검 후 없다면 27B 전환을 승인합니다." This is **conditional**, not blanket downtime/P3-A permission. Based on retained actual DGX P1 history, verify=PASS (baseline/extended completion, chat, tools, vision), benchmark=PASS (3 bounded requests), but actual numerical P1 TTFT/latency/tokens-per-second measurements have **not been supplied**; historic doctor and inventory-plan rc=3 stdout/stderr are still missing; post-P3-B P1 rerun is by definition NOT_RUN. **Therefore the condition is NOT MET and P3-A is NOT AUTHORIZED to execute.** Keep live Flash-Next, all assets and :8000 unchanged. D-034 still requires actual post-B P1 functional/numeric evidence before C. No automatic stage progression.

Source code review identified an independent logic error: `scripts.manager.inventory.main` returns rc=3 when `qwen38-flash` and its listening :8000 already exist even if `inspect_host.status=PASS` and `errors=[]`. Historical rc=3 might reflect an expected collision but cannot be asserted without original JSON. `p3_p1_evidence_gate.py` previously required rc=0 for both doctor and inventory, an incompatible success gate with the active source after B. Source corrected to accept **only rc=3 with both full parsed inventory documents proving that exact active Flash image/container owns :8000, no read errors, correct launch-preview target and consistent collision flags**, plus still-required reviewed disposition, timestamps, new functional and measured benchmark receipts. No actual P1 completion or operator permission is implied by CPU CI.

---

## D-034 — 2026-11-06 — P2 stops; P3 separately entered; Flash-Next P1 remediation then final 27B (OVERRIDES D-033)

User explicitly specifies: **P2 completion MUST NOT automatically enter P3**. P3 must first verify 27B as the source state, then **27B → Flash-Next** transition. Only after that succeeds, **address P1 deficiencies and rebenchmark Flash-Next** using actual measured evidence. Then **Flash-Next → 27B** transition and verification; final expected active model is **27B**. Because P2 currently restores original Flash-Next, 27B must be made active through its own approved gate before the requested 27B→Flash-Next verification. Do not imply this preliminary activation is automatic. Independent plan/approval/restore on each transition; pause at each phase, no auto chaining. Old P3 two temporary roundtrips conflict with this order and are retired/fail-closed. New read-only `sequence --plan` is not a persistent switch executor, never issues an execution plan or starts GPU. D-033 is explicitly superseded. No new live downtime authorized.

---

## D-033 — 2026-11-06 — P3 acceptance starts with two temporary verified roundtrips, not permanent switch

P3 first acceptance instrument is **exactly two** sequential Flash-Next → temporary NVIDIA 27B → original Flash-Next cycles using the existing proven one-shot recovery executor. It is **blocked absent actual P2 benchmark receipt** `BENCH_PASS_RESTORED_VERIFIED` and additionally requires **new P3-specific plan ID plus explicit downtime acknowledgment**. After every cycle, recheck actual original container identity, running state and Manifest-based API served ID; on first failure never begin another cycle. Reporting P3 temporary-roundtrip PASS must **not** be called persistent production model-switch readiness. Persistent switch, failure injection and recoverability remain later independent work. No service, image or model change authorized by source-level readiness.

## D-032 — 2026-11-06 — P2 benchmark must reuse the proven exact-identity restoration path

The actual 27B DGX smoke `PASS_RESTORED` means do not repeat source import probes. Add bounded 3-request/64-token **benchmark-specific** approval that cannot reuse the first smoke trial's plan ID. Reuse the original one-shot target launch, exclusive GPU container policy, preserved original identity and mandatory original restore; capture client metrics, not generated text, and local 0600 evidence including fresh Manifest/API check after restore. Mark client TTFT, decode/prefill **proxies** separately from engine speed, and memory point sample distinctly from peak. Any result absent real measured data or independent return-to-Flash proof is not benchmark PASS. Disruptive execution still needs fresh exact plan and new typed downtime approval; no user "continue" instruction by itself grants a service interruption.

---

## D-031 — 2026-11-06 — Wizard must use Manifest-led live service status as primary operator interface

After real one-shot Qwen3.8-27B GPU `PASS_RESTORED`, the user chose **Manifest-based Wizard** instead of manual `docker ps` + `curl` for verifying original Flash-Next recovery and future switching. Keep a **single** `./wizard.sh service manager status --json` command with fresh actual Docker/socket observation + declared `runtimes/service-policy.json` expectations + localhost `/health` and `/v1/models` exact model ID. Return `LIVE_SERVICE_VERIFIED` or fail closed `BLOCKED`, never infer operation authority or API identity from a stale manifest. Preserve `inventory`, `health`, `logs` for diagnostics. Do not conflate current API verification with prior trial provenance, GPU exclusivity, permanent switch readiness, memory/latency measurements or user authorization to stop production. No Docker or GPU mutation from any status command.

---

## D-029 — 2026-11-06 — Permit FIRST 27B GPU trial only via exact-approved, bounded, restoring experiment

A real DGX CPU-only ModelOpt registration pass justifies trying GPU startup instead of further speculative CPU checks. This is **not** permission to interrupt the running Flash-Next without operator acknowledgment. Implement 27B **experimental one-shot** guarded CLI, with default read-only planning and exact full SHA plan ID + typed interruption acknowledgment. A trial deliberately stops original `qwen38-flash` and must try restoring the **existing same original container** regardless of target launch success. No parallel GPU models, permanent model transition, cache deletion, image rebuild/pull, or reuse of Flash-Next PLE/MTP options. Protect on unknown Docker target/GPU status; if recovery cannot be verified, show failure and require operator intervention. Original service may be disrupted temporarily and power/daemon failure can defeat auto-recovery.

Keep NVIDIA `nvidia/Qwen3.8-27B-NVFP4` ModelOpt FP8/NVFP4 separate from community Unsloth compressed-tensors examples; checkpoint's internal `Qwen3_5ForConditionalGeneration` is *only a loader identifier*, not the model product name. Start with ctx8192/one sequence/0.70 GPU/eager, no MTP/YaRN; qualify kernels/API first, optimize later.

---

## D-028 — 2026-11-06 — Verify ModelOpt mixed name through public registry, not instance method

The installed vLLM 0.32 `ModelOptMixedPrecisionConfig.get_name(self)` is an **instance** method. The initial CPU-only audit's class-level zero-argument call yielded a self-binding TypeError unrelated to model compatibility. Correct strategy: import `vllm.model_executor.layers.quantization`, call `get_quantization_config("modelopt_mixed")` (no config or model instantiation), and verify identity to the imported `ModelOptMixedPrecisionConfig`. Preserve fail-closed checks and exact raw DGX evidence. No method-call issue may be treated as GPU kernel/load failure; no source-only/CPU result can authorize GPU transition.

---

## D-027 — 2026-11-06 — Opt-in CPU loader import is distinct from GPU runtime acceptance

After actual DGX read-only `serve_27b.sh --status/--plan` success, separately check installed Python imports of vLLM Qwen3.5 and `ModelOptMixedPrecisionConfig`, plus the declared quantization name `modelopt_mixed`, in a bounded **operator-opted-in CPU-only runc container**. Do not mount model cache, publish ports, request GPUs, start the vLLM engine, call inference or modify the original Flash-Next process. The wrapper must default to `--plan`. Import failure in this restricted environment is ambiguous; even a clean import/class/name result does not qualify GB10 GPU kernels, checkpoint loading, memory fit, API, benchmarks or rollback. GPU/start/transition requires separately scoped approval.

---

## D-026 — 2026-11-06 — Serving scripts split per model, preserve legacy call path

Choose model-specific serving entrypoints: `scripts/serve_flash-next.sh` contains original Flash-Next PLE/MTP/QSA implementation; `scripts/serve_27b.sh` is an independent NVIDIA ModelOpt entrypoint (initially plan/status only); `scripts/serve.sh` remains default-compatible Flash-Next dispatcher with optional explicit `27b` selection. `./flash serve` retains existing Flash-Next behavior and tests. Do not inherit Flash-Next-only PLE/MTP/hybrid settings into 27B and never allow 27B to start/switch without separately approved, exact-plan executor with tested old-service restore. `serve.sh` with no args is **not** a harmless preview: it keeps legacy Flash-Next start behavior. Prefer explicit `scripts/serve_27b.sh --plan` for P2 read-only evidence.

---

## D-025 — 2026-11-06 — P2 27B dedicated initial-run preview without implicit transition

Once operator-supplied 27B pinned source metadata (FP8 208/NVFP4 193) and installed vLLM 0.32 source registry/ModelOpt AST checks pass, develop a **separate 27B runner** instead of reusing Flash-Next `scripts/serve.sh` (PLE/MTP/QSA defaults). The new `model 27b plan --for-action start --launch-preview` returns a **non-executable, unapproved** argv with exact local image ID, pinned snapshot path, `modelopt_mixed`, conservative *unvalidated* 8192 context/1 sequence/0.70 GPU memory/eager. Preview inspects original Flash-Next container image and localhost API identity but never calls Docker run/stop. No `plan_id`, no `--execute` override, no `operations_enabled`. A registry digest/validated recipe, GPU memory/kernels, exact source recovery and separate stop-before-start approval are still required. A preview command displayed in JSON must **never be copied to the shell**.

---

## D-024 — 2026-11-06 — Quantization source audit is a distinct release gate

Verify the local immutable NVIDIA 27B `hf_quant_config.json` rather than assuming the main-branch model card reflects downloaded revision. Require a bounded read-only `MIXED_PRECISION` description with layer-level FP8 and NVFP4 for source shape audit. Missing/invalid/unrecognized metadata blocks further qualification; valid metadata is still **not** proof of ModelOpt GPU kernel support, image import, memory capacity, runtime functionality or service transfer approval. No GPU launch and no implicit cleanup.

---

## D-023 — 2026-11-06 — Installed image source audit before P2 GPU runtime

Use a **separately invoked, explicitly CPU-only, isolated Docker runc image-source audit** to inspect patched vLLM 0.32 model registration/Qwen3.5 classes and ModelOpt NVFP4/FP8 before building/enabling a 27B launcher. A local image ID is not a registry digest, source symbols are not executed kernel proof, and neither gives service start authorization. The default operation is `--plan`; `--execute-cpu-only` uses no network, GPU or published ports, temporarily creates one runc container and removes it upon exit, and never touches Flash-Next. GPU start/old-service stop/transition and cache deletion remain separately gated.

---

## D-022 — 2026-11-06 — P2 download is evidence, not 27B runtime approval

Operator-supplied immutable NVIDIA 27B download PASS (19/19; exit 0; pinned source candidate) supersedes stale in-progress entries. Preserve exactly one active GPU inference model and host port 8000; never re-download without missing/corrupt evidence. Approve adding a **read-only** runtime preflight interface without enabling a GPU start, implicit service switch or recipe validity. The existing Flash-Next-specific serve script and hybrid/MTP defaults must not be repurposed as a validated 27B launcher. Actual 27B vLLM 0.32 loader, ModelOpt NVFP4/FP8, memory, image digest and safe rollback remain independent gates; P2 GPU service requires separate explicit authorization.

---# Decision record — accepted constraints vs proposals

Record what has been **decided** and what still needs approval. Proposals in docs are not automatically accepted implementations.

| ID | Date | Decision | Status / boundary |
|---|---|---|---|
| D-001 | 2026-11-04 | Use **Blazux vLLM 0.32 only**, no SGLang engine; aphex3k is tuning/benchmark reference | DECIDED |
| D-002 | 2026-11-04 | Keep NVIDIA/RadixArk existing Blazux capability while adding Orcarouter and 27B via model-specific opt-in recipes | DECIDED as target architecture; NOT_IMPLEMENTED |
| D-003 | 2026-11-04 | Create new `feature/recipe-wizard-handoff` branch from fork `main`; preserve `feature/orcarouter-bf16-adapter` separately | DECIDED / branch created |
| D-004 | 2026-11-04 | P0→P7 order: Flash-Next benchmark, 27B benchmark, switch test, **conditional Flash-Next cleanup**, Orcarouter benchmark, switch test, release gate | DECIDED as roadmap; all GPU work gated |
| D-005 | 2026-11-04 | Manage model as recipes, manifests, bounded wizard steps, service/proxy/gateway, Docker and storage inventory | DECIDED as design target; NOT_IMPLEMENTED |
| D-006 | 2026-11-04 | Preserve current original Orcarouter container, its API clients, data/image; explicit scoped approval before stateful GPU ops, restart or deletion | DECIDED / hard safety rule |
| D-007 | 2026-11-04 | Model deletion may be necessary due to storage; approve **exact candidate plan**, not automatic stage advancement | DECIDED / no deletion authorized |
| D-008 | 2026-11-04 | Single large active GPU model by default; stable gateway later, not at the expense of operating port `:8000` | DESIGN ASSUMPTION pending capacity/operations tests |
| D-009 | 2026-11-04 | Existing numerical strict `1e-4` Orcarouter release gate remains unresolved; no implied release PASS | DECIDED / release block |

| D-010 | 2026-11-04 | Implement N1 recipe with YAML + JSON Schema Draft 2020-12, CPU PyYAML/jsonschema verifier, required full pinned source/model SHA and Docker image digest, vLLM 0.32 only, and no launch/deletion approval bypass. 27B candidate stays invalid. | DECIDED / SOURCE_ONLY; not runtime authorization |

| D-011 | 2026-11-05 | User reports old services removed and asks Blazux default NVIDIA Flash-Next to occupy previous host API `:8000/v1`; model ID uses Blazux `qwen3.8-flash-next` (not the old Orcarouter identifier); keep vLLM 0.32 default profile and no SGLang. Remove static ban on 8000 and historic container name, replacing with live Docker/socket collision check. Never implicitly rm -f a container. | DECIDED / SOURCE_CHANGE; actual host deployment NOT_OBSERVED/NOT_RUN, supersedes D-006 and D-008 **only for presumed presence and reserved port**, not for protection of any actual resources |

| D-012 | 2026-11-05 | **User reaffirmed Wizard-first sequential P1–P7 delivery:** P1 Flash-Next implement+benchmark via Wizard → P2 27B implement+benchmark via Wizard → P3 bidirectional Flash-Next/27B switch via Wizard → P4 optional Flash-Next cleanup if disk constrained, via Wizard and exact approval → P5 Orcarouter-Flash-Next implement+benchmark via Wizard → P6 Orcarouter/27B switch via Wizard → P7 integrated operation. All steps must be Wizard-operable; CLI is underlying execution only; source CI ≠ DGX bench PASS. Preserve :8000/v1 external endpoint where feasible; vLLM 0.32 only, no SGLang. | DECIDED / ROADMAP LOCK; supersedes any task ordering that bypasses Wizard or promotes Orcarouter before P1–P3 verification; no GPU/deletion permission implied |

| D-013 | 2026-11-05 | While operator-owned `./flash setup default` is downloading, implement P1 Wizard source only; do not run competing download/prepare/start. Wizard must verify complete shards and image label, detect active setup, refuse Docker/name/port conflicts, use a fresh exact SHA-256 plan approval, keep benchmark bounded and record JSON evidence. Source CI ≠ DGX qualification. | DECIDED / SOURCE_IMPLEMENTED, GPU/delete not implicitly approved |

| D-014 | 2026-11-05 | User requested full P1–P7 **Wizard interface scaffold up front**, separately debug model-specific P1–P7 execution later. Use modular `wizard/menus/pN.py` files, shared router/contracts and both interactive `./wizard.sh` and headless `--stage/--action/--json` CLI. P1 retains existing approval/preflight implementation; P2–P7 default to read-only status/plan with no operational adapter/approval acceptance. Keep P1→P7 acceptance order unchanged. | DECIDED / SOURCE_IMPLEMENTED; GPU, switch, cleanup, gateway NOT_AUTHORIZED by scaffolding |

| D-015 | 2026-11-05 | **Supersedes D-014's numbered source-file layout:** classify Wizard by capability. Top-level Model management (P1/P2/P5), Model switching (P3/P6), Storage (P4), Operations (P7); descriptive submodules under `wizard/menus/models/`, `switching/`, `storage/`, `operations/`. Keep P identifiers and direct `./wizard.sh pN ...` / `--stage pN` as compatibility aliases. Group+item CLI and nested interactive menu use same handlers and guards. | DECIDED / SOURCE+CI PASS; DGX runtime NOT_RUN, P2–P7 execution BLOCKED |

| D-016 | 2026-11-05 | For repeatable user-mediated DGX workflows, develop **one Git-tracked temporary script per bounded milestone** in `scripts/temporary/`, accompanied by a CPU-only fake test, README lifecycle and handoff. User workflow is GitHub commit/CI → finish existing operator setup/serve tasks → `git pull --ff-only` → invoke one wrapper for preflight → separately approved Wizard verify/benchmark → evidence summary. Default read-only; no script-level auto-git-update, implicit operational approval, cache deletion, service disruption or secret log uploads. Temporary wrappers must be retired only by a reviewed commit after evidence is recorded; shared logic belongs in permanent Wizard modules. | DECIDED / SOURCE+CPU CI VERIFIED; DGX/GPU NOT_RUN |

| D-017 | 2026-11-05 | User confirmed Blazux default NVIDIA Flash-Next must remain compatible and authorized **bounded non-disruptive P1 GPU/API verify+benchmark without separate interactive plan-hash typing**. Correct new P1 checker false positives for existing shared metadata cross-repository symlinks (`tokenizer.json`, `model.safetensors.index.json`), retaining strict shard checks and bounded JSON index. Use `scripts/temporary/p1-post-download.sh --auto-gpu`, deriving live action-specific plan IDs and letting the Wizard revalidate each one. No change to permissions for service start/stop, setup/download, Hybrid repair, cache deletion, model switches or gateway. API model ID shows some server is active; preserve it. | DECIDED / SOURCE+CI PASS at 0063b0e (2/2 jobs, 155 tests/job); DGX GPU verdict PENDING |

| D-018 | 2026-11-05 | Preserve native Blazux default Flash-Next acceptance in Wizard: mandatory /v1/completions + standard chat baseline, separate tool/vision probes, mark partial advanced failures without blocking bounded baseline benchmark, retain nonzero-rc Wizard evidence, keep model/server untouched. Original DGX verify failure still needs evidence to identify precise cause. | DECIDED / SOURCE+CI PASS 391a2844 / DGX RECHECK PENDING |

## D-019 — Single active GPU model, fixed API :8000 and manifest-first orchestration (2026-11-05)

**DECIDED by operator:** At any given time DGX Spark hosts **one active GPU inference model**. Both NVIDIA Flash-Next and NVIDIA Qwen3.8-27B must expose the same host API `:8000/v1` when active. **27B start requires Flash-Next stop, port release, identity verification and approved rollback**; never run both GPU models or bind a second external port as an implicit workaround. Conversely, 27B → Flash-Next requires the same ordered stop/start/verify/restore discipline. Download is a separate **network/disk-only** operation allowed while Flash-Next serves (no GPU use, service stop, host port binding or API cutover). Maintain a versioned committed desired policy `runtimes/service-policy.json` and a live observed manifest from Docker/socket inventory; historical manifest records are evidence, not proof of current reality. State transitions must be lock-protected, auditable, checkpoint/image-preserving and explicitly plan-approved. Approval for download does **not** approve service stop, GPU startup or model switch. **SOURCE implemented / DGX transition NOT_RUN**, P3 acceptance remains separate.

## D-020 — Model-first consolidated Wizard (accepted 2026-11-05)

Operator approved `./wizard.sh` with only **1 Select/run model, 2 Service, 3 Advanced, 0 Exit** and model choices **Flash-Next / NVIDIA 27B / Orcarouter**. Wizard detects missing assets, in-flight download, active model and runtime readiness to propose the minimum required steps. It may invite checkpoint-only download through the existing P2 exact-plan gate. **Service switching (stop current model → free host :8000 → start new → API identity verification → rollback) remains separately gated and NOT_IMPLEMENTED/NOT_RUN.** Retain old Flash-Next P1 backend and all CLI names; this supersedes D-015 only for the interactive primary menu, not its stable internal category routes. Git desired policy/actual observation/event journal remain distinct. Per operator terminal, pinned NVIDIA 27B download **started** (`Fetching 19 files: 84%`); completion not evidenced. Full design: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`.

## D-021 — Full P1–P7 Wizard source-first delivery (operator accepted 2026-11-06)

Operator instructed **finish the entire Wizard interface now**, even if P2–P7 execution is not yet enabled; qualify and debug real adapters progressively as P2 onward develops. This explicitly approves full menus/action plans/status/roadmap and backend interface wiring in GitHub, **not** Docker/GPU/runtime/service mutation. Root menu remains model-first (D-020), all model actions are available for planning. Implement `wizard/console.py`, `wizard/workflow.py`, `wizard/roadmap.py`, bounded service log viewer and tests. Preserve original P1 `p1_wizard.py`, exact-approval P2 pinned downloader, all P1–P7 CLI aliases, one active GPU model, stable host `:8000/v1`, and separately scoped approval before any stop/start/switch/recovery. No in-flight 27B download disturbance. SOURCE complete does not imply runtime/gateway/recovery PASS; Draft PR remains open until qualifying DGX evidence.

### Design choices not yet finalized

- Remaining runtime/service/inventory contract fields and wizard flags. The source-only N1 recipe schema has been implemented.
- Whether 27B NVFP4/BF16-head vLLM 0.32 support can use stock backend or requires an opt-in patch; exact checkpoint and draft engine mode.
- Proxy/gateway implementation and host port layout; any port or model alias changes require operational approval.
- GPU benchmark thresholds, allowable downtimes, retention policies and available disk capacity.
- Integration strategy and merge ordering of Orcarouter adapter and this management branch.

### When creating a decision

Add a dated ID, why, alternatives, evidence, affected files/branches, rollback if relevant and approval boundary. If reversing a decision, append a superseding ID; never silently overwrite.
