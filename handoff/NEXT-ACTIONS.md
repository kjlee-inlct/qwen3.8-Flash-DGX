## 2026-11-12 — Measurement workspace handoff (SOURCE ONLY; DGX test deferred)

Model-independent, extensible measurement workspace added on top of branch baseline `df9829cf815527f3b931aed6f5d608972c094641`. It integrates the existing P5 resource snapshot (all host/cgroup/GPU/NVMe/PSI/Swap telemetry) with read-only exact-container runtime launch/profile inspection and non-secret parsed model-load/KV log metrics. New `operations measurements {catalog,inventory,history,benchmark-plan,benchmark-execute}` route; the model-selected TTY shows current memory and runtime settings, with refresh and local opt-in measurement history. This is **source code, not a newly measured value**; runtime log labels are not full host memory or PLE RSS. Benchmark requires exact `I_ACCEPT_ACTIVE_MODEL_INFERENCE`, active API/Docker identity, bounded 1..256K requested context calibration, and never runs automatically from menu. Data are stored only with `--save` as private 0600 JSON outside the P6 operating Journal. No Docker start/stop, model switch, checkpoint/cache deletion, GPU/governor/cgroup change, service release or PR merge. Existing Orcarouter v3 remains DEVELOPMENT_TRIAL, :8000, ONE_ACTIVE_MODEL_ONLY, vLLM 0.32, no SGLang. **No DGX measurement or API workload occurred in this GitHub-only change; CI must be confirmed on the final commit.**

Use [current measurement contract](../docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md) for commands, metric semantics, limitations and later operator test checklist. Do not misreport source implementation or future opt-in benchmark results as YSLAB-equivalent production measurements.

---

## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-10 (P5-D/P6-E evidence and Journal v2 safety)

**Historical 2026-11-09 baseline CI (superseded):** code+workflow HEAD `29c28e4750adabbd421dcda64a432127d3f45659`, GitHub Push run [42553107135](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42553107135) and PR run [42553114059](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42553114059) both **SUCCESS**. Newly added CPU checks explicitly included: P5 session 8, P6/P8 extended transition 8, P7 reconciliation 6, Wizard TTY 1 = **23 added tests PASS**. Original 24 synthetic cases preserved, 66 extended synthetic cases PASS as expected. **CI does not validate real Docker/GPU/inference/recovery**. Subsequent documentation-only commits may advance branch HEAD; always query the live branch/PR on restart.

**2026-11-10 read-only source CI supersession:** HEAD `6fbba09bbb240d5359968f9e59ab50011eb4b300`; [Push CI 42742988471](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42742988471) and [PR CI 42742994801](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42742994801) SUCCESS. P5-D model/API/container/role/port evidence binding and P6-E hostile Journal v2 input now fail closed. New CPU fixtures PASS in CI. P5-D real DGX capture, P6-E operating migration, real benchmark and live rollback remain NOT VERIFIED. This is the most recently completed source CI at the time of this text.

**Current P5 trial:** adapter `qwen4exp-qsa62318-lmhead-v032-v3` resolved `lm_head.weight_scale`. Orcarouter v3 remains DEVELOPMENT_TRIAL, not production. The newer 10:15 KST operator-provided *idle-only* telemetry and P5–P8 source-only implementation/acceptance supersession immediately below do not authorize any actual DGX service change.

[Model-independent P5–P8 source/acceptance contract](../docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md) · [Full document audit](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md)

---

### 2026-11-10 P5-D / P6-E read-only provenance and V2 journal proposal

P5-D/P6-E SOURCE CI VERIFIED: implementation commit `61effbd25a856a1736bb01098f2f87742b0248e0` (initial failed only because document inventory excluded new runbook); inventory correction commit `c697c7474550e1703f4f68daf857582e66292eec` passed **9/9 new CPU tests**, full Push [42739085075](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42739085075) and PR [42739090964](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42739090964) both **SUCCESS**. DGX P5-D command has **NOT** been run; P6-E migration is source-only, not a production write.

- **Operator-supplied actual DGX P5-C evidence**: `observation-capture --model orcarouter --json` reported `SOURCE_OBSERVATIONS_CORRELATED_NOT_LIVE_ACCEPTANCE`, zero issues, `DEVELOPMENT_TRIAL`, live trial `qwen38-orcarouter-qsa62318-lmhead-v3`, full Docker ID starting `9c49950015a8`, served ID `qwen3.8-flash-next-orca-uncensored-bf16`. This is a historical user-reported observation, not a new GitHub-side host check. P6-D `BLOCKED_LIVE_EXECUTOR_NOT_QUALIFIED` was expected with absent evidence.
- **P5-D** `scripts/manager/process_ownership.py`: exact read-only sequential `docker inspect`, `docker top`, `ss -H -ltnp` and `nvidia-smi --query-compute-apps=pid` (6s argv-bound probes). `./wizard.sh operations generic ownership-capture --model orcarouter --json`. Crosscheck source P5-C Docker full ID to independently repeated inspect, container init/host process PIDs, host listener PID and GPU compute PID subsets. **Always** leave `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false` because Docker NAT/GB10 GPU query may be unsupported and a host PID list alone does NOT authenticate port forwarding or GPU kernel exclusivity. On unsupported/missing data return BLOCKED_PARTIAL_PROCESS_EVIDENCE, not success; even consistent sets are not release.
- **P6-E** `scripts/manager/generic_journal_v2.py`: model-registry-based schema-v2 hash event proposal with separate source/target full Docker IDs, canonical role required, prior-v2 chain, optional V1 anchor, policy and nonce/approval requirements, strict audit on in-memory **untrusted** draft. `./wizard.sh operations generic journal-v2-preview --from-model orcarouter --to-model 27b --json` always reports BLOCKED (exit 3). Legacy V1 journal 2-model scope unchanged; no migration, no file writes, no auto-resume. Clean, empty and dirty V1 summaries have separate migration preview handling; none authorizes conversion. Detailed runbook: `docs/P5-D-P6-E-READ-ONLY-PROVENANCE-JOURNAL-V2-20261110.md`.
- New `tests/test_p5d_p6e_cpu.py` integrated in GitHub Actions; source commit CI must be checked separately before claiming PASS. No actual DGX probe performed in this source change. All past tests preserved. PR #1 Draft/Open/Unmerged. No service stop/start, inference, cleanup, GPU governor/cgroup change, model download/delete, live Journal mutation or merge. vLLM 0.32, SGLang disallowed, ONE_ACTIVE_MODEL_ONLY, API :8000.


### 2026-11-10 P5-C + P6-D source-only observation / operating gate

CI verified on source commit `37f3a1b8417a777206fea63965e6fcd7acef0ada`: Push [42720683321](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42720683321) SUCCESS and PR [42720691856](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42720691856) SUCCESS. All 9 new P5-C/P6-D CPU tests PASS. No actual DGX observation or operating transition occurred; the source code is not production qualified.

- **P5-C** `scripts/manager/observation_binding.py`: reconcile one existing `service_status.inspect_live_status` observation with one `resource_diagnostics.snapshot` observation. Explicit Orcarouter v3 DEVELOPMENT_TRIAL vs CANONICAL roles; cross-check registered checkpoint, served ID, container name/image and Docker full ID obtained from resource probe. `observation-review --model orcarouter --service-evidence /absolute/service.json --resource-evidence /absolute/resource.json --json` consumes untrusted JSON only; `observation-capture --model orcarouter --json` performs exactly one sequential **read-only** service and resource probe (Docker inspect, system sensors and GET /health,/v1/models), with **no inference**. Neither path proves port-PID or GPU exclusivity, source Docker-ID continuity across simultaneous probes, PLE residency, loaded benchmark, or release; never promote a Trial.
- **P6-D** `scripts/manager/generic_operating_gate.py`: `operating-gate-review --from-model orcarouter --to-model 27b --json` returns **BLOCKED** with explicit missing live executor, independent approval/authentication, cross-process durable nonce, atomic live-state and journal fencing. Even forged fully consistent JSON is never accepted as permission. The historical on-disk journal remains **2-model scoped**, Orcarouter schema unsupported; no new write to `service_journal.py`, no model start/stop/restore. `--review-now-utc` is untrusted source consistency clock input, not approval.
- New CPU module `tests/test_p5c_p6d_contract_cpu.py` and GitHub Actions workflow gate; source tests and CI outcome must be independently verified on the new commit. Previous P5 synthetic 21, P6 fake-disk 48, P8 extended 66, original 24 remain.
- No actual DGX service mutation, benchmark, model/cache/PLE deletion, GPU settings or PR merge. vLLM 0.32, no SGLang, ONE_ACTIVE_MODEL_ONLY, host 8000, Orcarouter v3 DEVELOPMENT_TRIAL untouched. PR #1 Draft/Open/Unmerged. Next: independent atomic Docker-ID/port PID/GPU process probes, separately approved operating journal schema upgrade, live P5 benchmark and P8 acceptance.


### 2026-11-09 P6-B/C SOURCE-ONLY: separate Docker identities and private fake-disk contract

- P6-B `scripts/manager/transition_safety.py` + `mock_transaction_pipeline.py`: each in-memory event has **distinct** `source_container_id`/`target_container_id`, plus `active_container_id` and `port_owner_container_id`. The legacy `docker_id` field is retained as synthetic SOURCE ID only. The audit blocks ID collisions, drift, mismatched phase/active ID, forged port owner, inconsistent phase, or unresolved transition. These are deterministic test IDs, **NOT** Orcarouter v3's live Docker ID.
- P6-C `scripts/manager/mock_persistent_contract.py`: **TEST TEMP FILES ONLY** under fresh `blazux-p6-fake-*` private directory, `fake-events.jsonl` / `fake-state.json`; O_EXCL, 0600, fsync(log/snapshot), os.replace, read-only audit, planned log-vs-snapshot interruption, symlink/tamper/dirty rejection. Synthetic bounded-clock lease ties model pair + two IDs + plan + nonce and detects expiry, drift and replay, **NOT** a real/operator approval or durable operating journal.
- CLI: `./wizard.sh operations generic fake-disk-matrix --summary-only --json` tests all 3 registered models / 6 directed pairs × 8 scenarios = **48 fake cases**. `fake-disk-contract --from-model orcarouter --to-model 27b --json` runs one ephemeral filesystem contract. Both avoid Docker/GPU/inference, model switch or any production journal path. Original 24/66 Fake-DGX scenarios and legacy service_journal/operational_audit are unchanged. Dedicated `tests/test_mock_persistent_contract_cpu.py` added to GitHub Actions; CI on source commit `4369bb10b33a3a7ca33347857d16055dc63b389a` independently confirmed: Push [42567344677](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42567344677) SUCCESS, PR [42567348419](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42567348419) SUCCESS; 11 new P6-B/C tests PASS, 48 synthetic disk scenarios PASS.
- **Not released**: no real cross-process authorization, authenticated observation, long-running lock, crash-safe persistent nonce across machines, operating journal migration, real Docker backend, automatic restore, performance qualification or P7/P8 live acceptance. Host :8000; ONE_ACTIVE_MODEL_ONLY; vLLM 0.32; no SGLang; Orcarouter v3 DEVELOPMENT_TRIAL untouched; PR #1 Draft/Open/Unmerged; retain all HF/PLE/assets.


### 2026-11-09 P5-B / P6-A in-memory pipeline source addition (no DGX mutation)

- **P5-B** `scripts/manager/mock_benchmark_session.py`: an exact synthetic, model-registry-driven coordination fixture produces bound session/profile hashes, mock before/after resource samples, an enclosed mock 3-request workload window, and reuses `session_review` to catch sample loss, Docker ID drift, API identity drift, clock drift, request failure and OOM. `./wizard.sh operations generic session-mock --model orcarouter --json`; `session-matrix --summary-only --json` = 3 models × 7 fixture scenarios (21). ALL synthetic numbers are invented fixture values, NOT actual benchmarks or resource measurements.
- **P6-A** `scripts/manager/mock_transaction_pipeline.py`: bridges the existing exact `InMemoryBackend` transition trace to an indexed, SHA256 hash-linked **in-memory** journal. Audit checks event chain, phase order, source/target/port, Docker ID continuity, owner/exclusivity and terminal safety; `pipeline-mock --from-model orcarouter --to-model 27b --json`. This does NOT call `service_journal.append_transition`, never fsyncs disk, accepts no downtime approval, and provides NO live executor/rollback or resume authorization.
- Added dedicated CPU test files `tests/test_mock_benchmark_session_cpu.py` and `tests/test_mock_transaction_pipeline_cpu.py` to the recipe-manifest GitHub Actions workflow. Existing 24/66 matrices and old CLI preserved. Source CI results must be verified for the **new commit**, not inferred from old runs.
- Last operator DGX read-only evidence remains Orcarouter v3 `LIVE_P5_TRIAL_API_VERIFIED` / `DEVELOPMENT_TRIAL`, port 8000, API ID `qwen3.8-flash-next-orca-uncensored-bf16`, `production_released=false`; single managed model, but GPU exclusivity and host-port process ownership NOT verified. **No live service action authorized.**
- **NEXT**: independently measured loaded inference + synchronized resource session, trial-vs-canonical Docker ID binding, PLE-specific RSS; approved real transaction adapter, durable journal reconciliation, strict plan TTL/replay fencing, source restoration, P7 real probes and P8 operator-approved fault trials. Preserve vLLM 0.32.0, no SGLang, ONE_ACTIVE_MODEL_ONLY, host 8000, Draft PR #1 and every model/cache/image/PLE asset.



## CURRENT SUPERSESSION — 2026-11-09 10:15 KST P5–P8 generic source and operator evidence

**Latest DGX observation supplied by operator (not executed by this GitHub session):** Orcarouter v3 `qwen38-orcarouter-qsa62318-lmhead-v3`, unchanged Docker ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`. Private read-only receipt `/home/inlc/.local/state/blazux-wizard/resource-diagnostics/20261109T011520343025Z.json`: **5 IDLE samples / 44.27 seconds**, host MemTotal 121.63 GiB / min MemAvailable 30.16 GiB / last 30.18 GiB; cgroup memory.current 25.25 GiB / peak 37.02 GiB; host swap used 1.31 GiB vs cgroup swap zero; memory PSI avg10 zero, OOM/OOMKill/major fault/file refault and swap-I/O interval deltas zero; CPU busy 0.19%, GPU utilization zero/33°C, host maximum temperature 33.8°C. This is **IDLE ONLY** and resource policy remains `OBSERVE_ONLY` / `UNCALIBRATED` / `startup_gate_enabled=false`. Not PLE RSS, loaded TTFT/TPS, safe memory threshold, loaded stability or production proof. Raw receipt is retained on DGX only.

**Latest source changes (GitHub, no DGX service mutation):** P5 `benchmark_session.py` adds model-agnostic source-only `session-plan` and `session-review`; identity bound to registry checkpoint/served ID/Docker ID, session/workload hash, UTC/monotonic clocks, request/TTFT/TPS/error metrics and OOM. `resource_diagnostics.snapshot` adds `monotonic_ns`, but independent API identity and a coordinated real benchmark sampler/workload **are not yet implemented**. P6/P8 `transition_safety.py` adds exact **in-memory-only** backend and **66 extended synthetic tests** (3 registered models × 6 directed pairs × 11 fault types). Original generic **24 Fake-DGX cases** and old aliases remain unchanged. P7 `integration_contract.py` adds strict source-only four-component reconciliation; claimed `status: PASS` does not verify real Proxy/Gateway. Common CLI and TTY now expose these functions. CPU/Fake-DGX CI is source validation, never runtime acceptance.

**Pending:** real approved P5 loaded session and PLE-specific memory measurement, P6 generic live Docker executor and one-time approval/journal integration, P7 independent Proxy/Gateway/OpenWebUI probes, P8 real fault/recovery/Go-No-Go. Orcarouter v3 is still `DEVELOPMENT_TRIAL`; P6 Orcarouter→27B live preflight remains BLOCKED. Preserve vLLM 0.32.0, no SGLang, ONE_ACTIVE_MODEL_ONLY, host :8000, live v3, OpenWebUI/Portainer, Flash-Next/27B checkpoints, caches and PLE, all history and Draft/Open/Unmerged PR #1. No service/model/CPU/cgroup/image/cache mutation or PR merge authorized.

Read-only commands: `./wizard.sh operations generic session-plan --model orcarouter --json`; `./wizard.sh operations generic extended-fault-matrix --summary-only --json`; `./wizard.sh operations generic integration-reconcile --model 27b --component-evidence /absolute/components.json --json`. A session review requires both separately captured matching resource/benchmark receipt files; no workload is generated by these commands. [Current generic spec](../docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md).

---

## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-09 09:23 KST (model-agnostic DGX read-only validation)

**Operator-provided DGX evidence (not this GitHub session's new GPU test):** checkout `e8d6c2a` fast-forward PASS. Three registered models (`flash-next`, `27b`, `orcarouter`); common 6 directed pairs × 4 Fake-DGX scenarios = 24 expected outcomes PASS (6 simulated switches, 12 simulated successful restores, 6 deliberately failed restores). P6 Orcarouter→27B preflight `BLOCKED` with seven real-runtime release/integrity blockers. No live model switch, outage, fault injection, or real recovery.

**Latest P5 read-only interval, 09:22–09:23 KST:** 5 observations / 44.268 seconds, running `qwen38-orcarouter-qsa62318-lmhead-v3`, Docker ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, stable :8000. Minimum MemAvailable ~30.13 GiB, cgroup memory.current ~25.25 GiB, host SwapUsed ~1.31 GiB but cgroup Swap 0, memory PSI 0, interval OOM/OOMKill/major fault/refault and host swap I/O increases 0; CPU busy ~0.2%, GPU 0% and 34°C, host maximum 35.7°C. **Idle-only**: no loaded benchmark, PLE RSS or production qualification. CPU/memory policy remains `OBSERVE_ONLY`/`UNCALIBRATED`. Private full evidence at `~/.local/state/blazux-wizard/resource-diagnostics/20261109T002330768366Z.json` stays on DGX.

**Implementation follow-up:** common `--summary-only` for full-matrix Fake-DGX and bounded resource observations retains unaltered full private JSON when `--save` is used. Adapter `qwen4exp-qsa62318-lmhead-v032-v3` resolved historical `lm_head.weight_scale`; current Orcarouter remains a `DEVELOPMENT_TRIAL`. vLLM 0.32.0, no SGLang, ONE_ACTIVE_MODEL_ONLY, :8000. No new approval, container stop/rename, limit changes or PR merge. [Generic P5–P8 specification](../docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md) · [Evidence ledger](EVIDENCE-LEDGER.md).

---

## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-09 00:55 KST (v3 MTP0 + P6/P8 source)

**Actual operator DGX record, not a new session runtime test:** Orcarouter `qwen38-orcarouter-qsa62318-lmhead-v3` on :8000, API `qwen3.8-flash-next-orca-uncensored-bf16`; `LIVE_P5_TRIAL_API_VERIFIED` and `PASS_LIVE_INFERENCE` (READY). Adapter `qwen4exp-qsa62318-lmhead-v032-v3` resolves `lm_head.weight_scale`. Still `DEVELOPMENT_TRIAL`, not production. Failed-candidate cleanup is already complete; no repeat.

**Latest 00:54–00:55 KST idle telemetry:** total RAM 121.63 GiB; MemAvailable 30.18 GiB; host SwapUsed 1.31 GiB, Orcarouter cgroup Swap 0; Docker MemUsage 7.157 GiB vs cgroup memory.current 25.54 GiB, peak 37.02 GiB, inactive_file 18.38 GiB, anon 4.58 GiB; memory PSI avg10 0, OOM/OOMKill 0, no interval swap I/O, major faults or file refaults; host busy ~0.18% over 45 seconds, performance governor, 10 cores at 2808 MHz plus 10 at 3900 MHz, system up to ~34.7 C, GPU ~33 C. The Docker/cgroup difference largely matches inactive file cache; neither memory leak nor PLE resident bytes is established. This is **idle-only** evidence; loaded performance/stability remains unqualified. Old 00:43 observation retained below. Resource policy remains `OBSERVE_ONLY` with disabled startup gate; `BLOCKED_UNCALIBRATED` is expected. Do not apply YSLAB 100 GiB startup threshold, CPU cap or cgroup limits.

**Source update:** P6 read-only Orcarouter↔27B checks, both-direction in-memory Fake-DGX switch and P8 synthetic fault matrix (`21aa6c9`), plus same-container-ID cgroup interval fault/OOM safeguards (`5acf0b1`); both GitHub push/PR CI SUCCESS. Actual P5 MTP2, Tools, Vision, benchmarks, canonical lifecycle, P6 live switch, P7 Proxy/Gateway, P8 real fault/restore and release remain unqualified. Keep live v3, models, caches, images, OpenWebUI/Portainer; vLLM 0.32.0, no SGLang, one active model and port 8000. No unauthorized Docker/GPU mutation or PR merge.

[Current technical record](../docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md) · [Full documentation audit](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md)

**P5~P8 범용 기능 (2026-11-09):** 등록 모델 전체에 공통인 리소스/벤치 증거(P5), 전환 사전검사(P6), 통합 UX 및 서비스·프록시·게이트웨이 근거(P7), Fake-DGX 장애 매트릭스(P8)를 분리 구현했다. 07:18 KST DGX 유휴 관측과 소스 CI를 실기 전환/복구 승인으로 간주하지 않는다. [범용 기능 계약](../docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md).

---

## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-08 (Orcarouter v3 MTP0 live inference PASS)

**LATEST DGX RESOURCE EVIDENCE (2026-11-09 00:43 KST, operator log):** v3 running, 30.18 GiB MemAvailable / 121.63 GiB total, swap used 1.31 GiB, memory PSI avg10=0; Docker 7.157 GiB versus cgroup 25.54 GiB (cache split NOT YET MEASURED), peak 37.02 GiB, cgroup OOM=0. GPU memory N/A is expected on GB10 UMA. 13-second idle observation only, NOT loaded stability acceptance; preflight BLOCKED_UNCALIBRATED is expected. **Do not apply memory cap or 100 GiB admission gate.** New source-only cgroup memory.stat/Swap churn diagnostics must receive fresh DGX read-only evidence. [P5 technical record](../docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md).


**NEW SOURCE-ONLY RESOURCE DIAGNOSTICS — 2026-11-08:** `./wizard.sh operations resources snapshot --json`, `observe --samples 3 --interval 5 --json`, `preflight --json` implemented with CPU/Fake-DGX CI; declared `OBSERVE_ONLY` P5 recipe policy. No DGX measurements obtained in this source session, no live service changes or resource limits applied. Preflight is NOT wired to launch, returns `BLOCKED_UNCALIBRATED` without approved threshold. Optional `--save` creates private 0600 JSON evidence. See [P5 adoption notes](../docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md), keep trial v3 and port 8000 untouched.


**This section supersedes older v2-only instructions below, which remain historical.** Read [full 170-document inventory and supersession audit](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) and [active P5 live runbook](../docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md). The model is `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` (revision `3a3b63161c0745390e5270179af42e46efc70799`), Blazux **vLLM 0.32.0**, no SGLang, single active model, port **8000**. The exact v3 adapter is `qwen4exp-qsa62318-lmhead-v032-v3`, resolving the QSA #62318 / quantized `lm_head.weight_scale` loading failure via checkpoint-target prefix `lm_head`.

**LATEST ACTUAL DGX EVIDENCE, 2026-11-08 ~23:30 KST (operator attached transcript):**
- `./wizard.sh service manager status --json`: `LIVE_P5_TRIAL_API_VERIFIED`, `issues=[]`, `runtime_role=DEVELOPMENT_TRIAL`, `production_released=false`; actual image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`, active Docker `qwen38-orcarouter-qsa62318-lmhead-v3` (ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`), host 8000; API model ID `qwen3.8-flash-next-orca-uncensored-bf16`. Do not stop/rename active v3 just because it is a temporary candidate.
- `./wizard.sh p5 trial verify --json`: **`PASS_LIVE_INFERENCE`**, `inference_verified=true`, chat reply `READY`, no service mutation. This is **actual MTP0 text-inference evidence**, not proof of MTP2, native Tools, Vision, sustained pressure tolerance or performance benchmarking.
- Explicitly approved `p5 trial cleanup-execute`: **`PASS`**, three exited(1) failed test containers deleted: `qwen38-orcarouter`, `qwen38-orcarouter-qsa62318`, `qwen38-orcarouter-qsa62318-lmhead`. Their log files and private receipts retained in `~/.local/state/blazux-wizard/p5-live-trial/cleanup/`; images and checkpoint/HF assets retained; running v3 protected. This cleanup is **already complete**; do not replay it or treat canonical `qwen38-orcarouter` as currently running.
- **Final service naming:** display `Orcarouter Flash-Next`, canonical container `qwen38-orcarouter` once separately approved/promoted; v1/v2/v3 are development trial identities, not long-term operational names. No production promotion yet.
- **Resource capacity now the highest unmeasured concern:** memory quantity, `MemAvailable`, swap, page-cache/PLE residency, PSI, cgroup usage, CPU clock/temperature/power, service stability have **NOT been measured** in provided log. The pinned YSLAB reference (`9492b78c6bc04638587b42f2ffeb0680b0fcb3ef`) uses a pre-launch `MemAvailable >= 100 GiB` gate, `--gpu-memory-utilization 0.80`, PLE mmap file-backed, `VLLM_PLE_MMAP_PREWARM=0`, 32 gather workers, and a stability probe recording MemAvailable + swap; **no CPU-frequency cap or cgroup/PSI hard protection identified**. Current Blazux trial uses GPU utilization 0.70, 16 gather workers, context 8192 / one sequence. Do not import the 0.80/32/262144 profile as validated Blazux settings. Prioritize non-mutating telemetry and safety design; CPU clocks, governors, system-wide memory settings and Docker hard limits require separate validation/approval.
- **Next:** bounded read-only capacity snapshot (DGX CPU/GPU/RAM/Swap/PSI/cgroup, file-backed PLE), optional non-disruptive observation under real workload, then policy design and CPU/fake-DGX tests; only later approved controlled constraints, benchmark, P5 MTP2/tools/vision and canonical lifecycle promotion. P8 owns failure recovery/production acceptance.
- Existing PR #1 remains Draft/Open/Unmerged. DGX evidence has **not** been independently executed from GitHub. Preserve 27B/Flash images, HF cache, live v3, OpenWebUI/Portainer; no past P3/P4/P8 live replay, no auto stop/prune/merge. **GitHub baseline at evidence capture:** `e352a9351ed3660fb595320ea1ff0f51e347d20b`, CI push/PR PASS; verify newer HEAD in every new session.

---

## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-08 (QSA #62318 + LM-head v2)

**Latest 2026-11-08 DGX observation and P5 lifecycle fix:** current adapter `qwen4exp-qsa62318-lmhead-v032-v3` targets `lm_head.weight_scale` registration. v3 `qwen38-orcarouter-qsa62318-lmhead-v3` is **RUNNING** and publishes `:8000`. Actual GET `/v1/models` returned `qwen3.8-flash-next-orca-uncensored-bf16`. Port 8000 belongs to the live v3 Docker proxy, NOT orphaned 27B; **do not stop it**. Chat inference and production release are still unverified; next direct command is `./wizard.sh p5 trial verify --json`. Existing service-manager status was BLOCKED solely because it did not enumerate P5 trial name and production served_id remained null. Source now reports the P5 runtime separately as `LIVE_P5_TRIAL_API_VERIFIED` when Docker+HTTP identity pass, `runtime_role=DEVELOPMENT_TRIAL`; not canonical production. Stable eventual canonical container **`qwen38-orcarouter`** (Orcarouter Flash-Next), trial `v1/v2/v3` names only temporary. No automatic promotion. New `./wizard.sh p5 trial cleanup-plan --json` and `cleanup-execute --approve-plan <fresh 64hex> --ack-cleanup I_APPROVE_P5_FAILED_TRIAL_CONTAINERS_ONLY --json` provide exact allowlisted exited-failed-only cleanup with mode-0600 local log preservation and live v3 identity rechecks; no cleanup has been executed here. Do NOT delete running v3 or use unrelated 27B cleanup. Read first section of [active P5 runbook](../docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md). Preserve HF cache/models. PR #1 stays Draft/unmerged.

**Read these before following historical commands:** [complete 168-item initial document review (169 including the new v2 runbook; audit file added afterward)](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) and [current P5 v2 DGX Runbook](../docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md). (For links from `docs/`, the authoritative paths are `docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md` and `docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md`.) These supersede old QSA-only trial commands, old P4/P5 starter prompts and earlier claims that P5 was never attempted.

**Latest actual operator-provided DGX evidence:** checkout `247d31d`, previous QSA-only container `qwen38-orcarouter-qsa62318` exited(1) after loading reached **15/17 safetensors shards**; hard failure `lm_head.weight_scale` not registered on `Qwen4ExpForCausalLM`. Receipt `~/.local/state/blazux-wizard/p5-live-trial/trial-20261108T054106528164Z.json`: `FAIL_NO_ROLLBACK`, `gpu_verified=false`. Original `qwen38-27b` exited(0); :8000 was unserved **then**. This is not a new live check.

**Current GitHub candidate:** isolated composite adapter `qwen4exp-qsa62318-lmhead-v032-v2`, image `blazux-p5-orcarouter:qsa62318-lmhead-v032`, target `qwen38-orcarouter-qsa62318-lmhead`, `Dockerfile.p5.qsa62318-lmhead`. Previous QSA-only candidate and logs are preserved; canonical vLLM **0.32.0** base unchanged. Source/CPU CI for code commit `9e7cd1b` passed ([push 42473176346](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42473176346), [PR 42473180100](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42473180100)); **actual v2 image build, GPU mmap/inference, MTP2, benchmarks and production release are NOT VERIFIED**. `lm_head` quantization config vs checkpoint scale must be independently checked; a constructor source edit alone is not GPU proof.

**LATEST 2026-11-08 DGX GPU log supersedes the v2 heading above:** v2 image `sha256:3e0afbb4...` started, loaded **15/17** shards and applied BF16 PLE mmap, then exited(1), `OOMKilled=false`, SAME `lm_head.weight_scale` unregistered. Exact trace recorded in operator log and receipt `~/.local/state/blazux-wizard/p5-live-trial/trial-20261108T132744209946Z.json`. vLLM 0.32.0 nested-prefix mismatch identified: config group targets `lm_head` while v2 passed `maybe_prefix(prefix,"lm_head")` (nested language_model prefix), so compressed-tensors did not register FP8 scale. **NEW ACTUAL NEXT TASK is v3 GPU trial, not document/CPU preflight:** clean pull, `./wizard.sh p5 trial prepare --json`, `./wizard.sh p5 trial plan --json`, operator explicitly approves NEW exact plan with `I_ACCEPT_P5_NO_ROLLBACK`. v3 scoped `qwen4exp-qsa62318-lmhead-v032-v3`, `Dockerfile.p5.qsa62318-lmhead-v3`, image `blazux-p5-orcarouter:qsa62318-lmhead-v3-v032`, target `qwen38-orcarouter-qsa62318-lmhead-v3`. No original vLLM or checkpoint mutation; old failed containers retained. **No v3 GPU pass yet.** Details: [v3 first section of active runbook](../docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md).

**Still binding:** `ONE_ACTIVE_MODEL_ONLY`, host `:8000/v1`, no SGLang, no checkpoint/HF/cache/old-container deletion, no P3 replay, P4 live deletion, P6 general switch, P8 faults or PR #1 merge. P5 is an explicitly approved *development no-auto-rollback trial only*; regular service switch rollback behavior has not been changed. Treat all older sections below as timestamped historical evidence.

---

## 2026-11-08 — Operator priority: Orcarouter live start

User objective is to **run `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` on DGX (vLLM 0.32.0, port 8000)**, NOT to continue validating document-inventory checks. Actual DGX `a7e2ed7` checkpoint metadata PASS (LM-head FP8+BF16 scale, `group_0`, not ignored); 119 local CPU tests had exactly one **documentation inventory equality** AssertionError, unrelated to model startup, while matching GitHub CI tests passed. Source change `44093c2`: one-shot P5 preflight now defaults to manifest/checkpoint only; full CPU tests only `--with-tests`. Direct next action: clean `git pull --ff-only`, run `./wizard.sh p5 trial prepare --json` to build the isolated derived vLLM 0.32 image, then `./wizard.sh p5 trial plan --json`; operator inspects current source :8000 and fresh plan and explicitly approves `./wizard.sh p5 trial execute --approve-plan <FRESH_PLAN_ID> --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json`. Target `PASS_GPU_TRIAL` is actual Orcarouter /v1/models + chat reply, not CI. No automatic restoration; preserve assets and previous failed containers; no unapproved GPU execution. Updated runbook `docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md` has direct steps. Keep PR #1 Draft/Unmerged.


## 2026-11-08 — REAL DGX pinned LM-head metadata PASS; P5 CPU suite BLOCKED (117 executed, exit 1)

Operator fast-forwarded to `596a6839cd34117f234fd28d80c0412857994326` and ran the non-mutating `python3 -m scripts.manager.p5_checkpoint_preflight --json`. **Real pinned checkpoint metadata PASS**: `ignore_lm_head=false`, explicit matched quant group `group_0`; `lm_head.weight` F8_E4M3 shape `[248320,2560]` in `model-00017-of-00017.safetensors`; `lm_head.weight_scale` BF16 shape `[248320,1]` in `model-00016-of-00017.safetensors`. Manifest PASS; checkpoint issues empty. This rules against simple LM-head ignore/no-quant-target hypotheses **for this snapshot**; does NOT prove engine quant-method resolution, actual registered parameter or GPU correctness (`weight_registration_verified=false`, `gpu_verified=false`).

The same real DGX preflight returned **`status=BLOCKED`**, `cpu_tests.count=117` (number **executed, not passed**), `cpu_tests.exit_code=1`, `issues=["P5_PREFLIGHT_CPU_TESTS_FAILED"]`. The original one-shot script suppressed the unittest failure lines, so the exact failing case remains **UNKNOWN**, not an observed checkpoint defect. Previous GitHub Actions 117/117 CPU result at the same source HEAD and the DGX local nonzero exit are distinct evidence; do not override one with the other.

Remediation commits following this observation update `scripts/manager/p5_checkpoint_preflight.py` to record **only bounded test IDs, failure counts and exception class names** in JSON (no raw paths, model prompts, cache content, or tracebacks); CPU execution is pinned to repository ROOT. Additional safe-output tests were added. **Operator next:** after new CI and `git pull --ff-only`, repeat exactly `python3 -m scripts.manager.p5_checkpoint_preflight --json` and return `cpu_tests.failing_test_ids`, `reported_failure_counts`, `exception_types`, `issues`. Do not attempt `p5 trial prepare/plan/execute` while preflight is BLOCKED. A later source PASS is not GPU acceptance. Keep original checkpoint, images, cache, services, old trial receipts, Draft PR and all operating constraints.



## 2026-11-08 — P5 pinned LM-head checkpoint preflight (NEW SOURCE, NOT GPU QUALIFIED)

- In addition to the current v2 QSA + LM-head adapter, `scripts/manager/p5_lm_head_checkpoint_audit.py` now audits the **actual local pinned HF snapshot** read-only: `config.json` quantization groups/ignore, safetensors index keys, and bounded `lm_head.weight` / `lm_head.weight_scale` headers (shape/dtype/shard). This source work does not confirm any current DGX observation; the exact gated Orcarouter snapshot could not be read through GitHub/public-web access in this session.
- **Root mechanism verified in upstream vLLM 0.32:** `ParallelLMHead` gets its quant method via `resolve_quant_method`; compressed-tensors checks `ignore` before selecting matching targets/schemes, and handles `ParallelLMHead` separately from `LinearBase`. Adding `quant_config=self.quant_config` alone does not guarantee `weight_scale` registration. If a scale exists but head is ignored or no explicit head FP8 target matches, the audit blocks; checkpoint/config is never silently rewritten.
- `scripts/manager/p5_live_trial.py` now requires a clean pinned LM-head metadata audit inside `prepare` and `plan`. `scripts/manager/p5_checkpoint_preflight.py` provides a no-Docker, no-GPU, no-network one-shot report containing manifest + checkpoint + all P5 CPU regressions. Operator-safe call after clean fast-forward: `python3 -m scripts.manager.p5_checkpoint_preflight --json`. `PASS_SOURCE_ONLY` is **not** GPU qualification. `BLOCKED` forbids preparation/planning pending source investigation.
- Added CPU/Fake-DGX regressions for FP8 group matching, ignore-scale conflict, missing scale, header/path limits, and judge safety. Latest CI must be inspected separately; original GPU evidence remains `FAIL_NO_ROLLBACK` at old QSA-only HEAD, v2 GPU build/inference **NOT VERIFIED**, `gpu_verified=false`. BF16 PLE GPU mmap, MTP0, MTP2, Tools, Vision, Bench and release are **NOT QUALIFIED**.
- Full technical sequence in [the current v2 Runbook](../docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md), with [the exhaustive historical document audit](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md). Preserve vLLM 0.32.0, port 8000, ONE_ACTIVE_MODEL_ONLY, all historical receipts/failed containers/cache, PR #1 Draft/unmerged. No unapproved DGX GPU execution, Docker mutation, P3/P4/P6/P8 work or production release.


## 2026-11-08 DGX P5 scoped QSA #62318 image-build follow-up: Blazux hybrid QSA ABI

Actual DGX after HEAD `136a969`: `manifest validate PASS`; `p5 trial prepare` BLOCKED while building `Dockerfile.p5.qsa62318` at step 4/4: `P5_QSA62318_QSA_FUSE_GUARD_ANCHOR_COUNT_0`. No candidate image built, no `plan` or `execute` reached due to shell `set -euo pipefail`. Existing `qwen38-27b` remains EXITED(0) and old failed `qwen38-orcarouter` EXITED(1). New `qwen38-orcarouter-qsa62318` absent, port 8000 unserved, **no new GPU trial occurred**. This is a source-anchor mismatch during isolated build; NOT evidence of a new GPU model incompatibility.

Verified canonical repo `Dockerfile` lines 49–52 already rewrite the *original upstream* QSA `self.fuse_indexer_projection = vllm_config.lora_config is None` to `self.fuse_indexer_projection = (vllm_config.lora_config is None and not _fp8_hybrid_separate_qsa(quant_config, prefix))`. They also redirect the **qkv_proj keyword** to `_fp8_hybrid_excluded(quant_config)`, but leave the positional `model.without_modelopt_fp4(quant_config)` in `Qwen4ExpQSAQKVIndexerLinear`. Initial scoped upstream fix #62318 wrongly expected the unmodified guard and failed closed (correctly).

Implementation correction: `src/p5_qsa_quant_backport_v032.py` now supports exactly two anchored, AST-checked source ABIs: pristine upstream vLLM v0.32.0 and the *real installed Blazux hybrid QSA* modification. The Blazux variant computes `fused_quant_config = _fp8_hybrid_excluded(quant_config)`, retains `not _fp8_hybrid_separate_qsa(quant_config, prefix)` and adds official `type(qkv_proj.quant_method) is type(indexer.index_qk_proj.quant_method)` safeguard before fused wrapper construction. The original 3-way `packed_modules_mapping["qkv_proj"]` correction remains. Mixed/unknown/duplicate anchors must block. **No edits to canonical Blazux image, original 27B container, HF cache, or GPU.** Only separate P5 derived image gets changes.

The image CPU ABI probe additionally requires both upstream method-match and original Blazux hybrid veto to survive; new CPU regression tests cover exact Dockerfile sed declaration, Blazux fixture, idempotence, unknown hybrid source failure and isolated build. Re-run `./wizard.sh p5 trial prepare --json` *first* after new HEAD; only if PASS, `plan --json`; only if READY and fresh approved SHA, then GPU test. Previous failed container/logs retained, no auto rollback, API port 8000 and single-model invariants. The prior actual GPU QKV mismatch is **not yet re-verified with fixed image**; MTP0 GPU remains UNQUALIFIED.

---

## 2026-11-08 P5 actual DGX GPU trial: quantized QKV / BF16 QSA indexer, upstream fix #62318

**User-observed runtime (file `20261108-043721`):** HEAD `f9c6cef`; P5 MTP0 plan `READY_TO_APPROVE`, approved execute `executed=true,target_started=true,source_stopped=true,gpu_verified=false,status=FAIL_NO_ROLLBACK` (receipt `~/.local/state/blazux-wizard/p5-live-trial/trial-20261108T043550955560Z.json`). Container `qwen38-orcarouter` exited(1); `qwen38-27b` exited(0); :8000 no API. Exact EngineCore failure during QSA projection construction **before weight load**: `ValueError: Found different quantization schemes for the shards of language_model.model.layers.3.self_attn.qkv_proj` at compressed-tensors `should_ignore_layer`. BF16 PLE metadata probe previously passed, **but real GPU mmap and model inference are NOT VERIFIED**.

**Public root-cause verification:** vLLM [issue #62308](https://github.com/vllm-project/vllm/issues/62308) documents the EXACT error in Qwen3.8 Flash-Next vLLM 0.32.0; merged upstream PR [#62318](https://github.com/vllm-project/vllm/pull/62318), commit `fe833b1`, Oct 27 2026. `Qwen4ExpForCausalLM.packed_modules_mapping["qkv_proj"]` incorrectly includes BF16 `indexer.index_qk_proj` even when Q/K/V are quantized. Official fix maps Q/K/V only and fuses indexer only if its quant method matches; changing checkpoint `ignore` list is **not** a valid repair (actual weight formats differ). `--enable-lora` does not bypass. vLLM remains **0.32.0** and SGLang unused.

**Implementation direction and policy:** User instructed recipe-first. This is an actual **upstream engine regression**, not a recipe parameter typo. Preserve canonical Blazux/27B/Flash image unchanged. The P5 MTP0 recipe alone selects an **isolated, minimal, version-pinned upstream #62318 backport** from `src/p5_qsa_quant_backport_v032.py` via `Dockerfile.p5.qsa62318`; source changes only in a derived, independently tagged and identity-checked candidate image. No automatic global vLLM source rewrite, no model checkpoint modification or HF-cache edit. Future generic patches prohibited. Model recipe binds adapter ID, provenance, target name and MTP0 only; release still unqualified.

**Operational fix for idle after failure:** source `qwen38-27b` may be running OR **cleanly stopped (ExitCode 0)**, with port and GPU exclusivity checks. Do not restart 27B just to switch again. Preserve existing failed `qwen38-orcarouter` container and its log. The new adapter trial uses separate `qwen38-orcarouter-qsa62318` name. `prepare` builds offline in isolation with original SHA-pinned Docker base; it does not stop/restart any model or use GPU. `plan` binds exact original+candidate IDs and immutable git HEAD into expiring approval. `execute` must have exact approval + `I_ACCEPT_P5_NO_ROLLBACK`; no auto restore and no deletion, ever. **No actual DGX post-fix trial has run.** If CPU fake tests pass, don't promote GPU status.

Latest permanent runbook: `docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md`.
Next: pull latest branch, manifest validate, `./wizard.sh p5 trial prepare --json` then `plan --json`; if PASS/READY, run fresh hash-approved trial only under previously accepted development downtime. Collect model/container logs and API output, runbook specifies commands and safety. PR remains DRAFT, DO NOT MERGE. P8 recovery/fault acceptance deferred, MTP2 unqualified.

---

## 2026-11-08 P5 MTP0 strategy correction: recipe-first, no vLLM 0.32 patch build

After the actual DGX `./wizard.sh p5 trial prepare` failed with `MTP loader return: expected one vLLM0.32 anchor, got 2` during **P5-specific image source patching**, user explicitly redirected P5 toward **recipe-managed model/runtime configuration**, not upstream source patches. This is accepted.

P5 MTP0 now uses `recipes/qwen38-orcarouter.runtime.json` as the single source for pinned checkpoint, actual BF16 PLE, served ID, `dtype=bfloat16`, context/seqs/memory, MTP depth 0, KV cache, read-only cache, PLE mmap environment, native-tool profile and experiment policy. `./wizard.sh p5 trial prepare` performs only read-only manifest/P5 header checks and a short **GPU-free CPU probe** in the currently running 27B Blazux vLLM 0.32 image, checking engine version, source PLE mmap hook, BF16 and source syntax. It **never builds or tags a Docker image or modifies model.py/mtp.py**. `plan` binds that same immutable verified image ID and asserts a valid SHA plan; `execute` stops the old 27B only with explicit approval and launches Orcarouter MTP0 from existing Blazux image with **no automatic rollback on failure**, preserving all image/cache sources. Historical P5 `Dockerfile.p5.candidate` and `src/p5_patch_qwen4exp_v032.py` remain archived source candidates **NOT called** by the trial. No MTP2 MTP donor overlay is used. Experimental qualification remains **NOT_RUN**, even if the CPU image preflight passes.

The previous real DGX run at HEAD `0071cb2` failed at Docker build step 6 due to patch anchor duplication; `plan` stayed BLOCKED and 27B was never stopped. The new recipe-first code has **not yet been executed on real DGX**. First re-run `./wizard.sh p5 trial prepare --json` and `./wizard.sh p5 trial plan --json` on the updated branch; **do not attempt live execute on a BLOCKED plan**. Any actual Orcarouter model-load error (e.g. quantized lm_head) must be logged and specifically diagnosed before introducing a separate, versioned, opt-in adapter.

Updated runbook: `docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md`.

---

## 2026-11-08 P5 DGX failed image-build observation and correction

**Actual DGX operator log** (`20261108-030535`) after pulling HEAD `1367a86`: `manifest validate --json` PASS, PLE BF16 metadata true. `./wizard.sh p5 trial prepare --json` failed **BEFORE any GPU execution or 27B stop**: BuildKit parsed `FROM sha256:9479fc92...` as `docker.io/library/sha256:<...>` and tried an unauthorized registry lookup. `prepare.status=BLOCKED, P5_CANDIDATE_IMAGE_BUILD_FAILED`. Subsequently `plan.status=BLOCKED`, `candidate_image_id=null`, `issues=["DOCKER_INSPECT_FAILED"]`, `plan_id=null`. The user command substitution raised AssertionError; a separately submitted `execute` without a valid plan was correctly blocked (`EXACT_PLAN_AND_NO_ROLLBACK_ACK_REQUIRED`), `executed=false`, `source_stopped=false`, `target_started=false`. Real DGX `service manager status` continued to show healthy `qwen38-27b` at :8000 and `/v1/models` returned only `qwen3.8-27b`. No Orcarouter container exists.

**Fix:** Local Docker image ID `sha256:<64>` is **not** an acceptable standalone Dockerfile `FROM` repository reference; automatically derive an immutable-source-ID-specific local tag `blazux-p5-source:v032-<64hex>` using `docker tag` only if absent, never overwrite an alias pointing to any other image, verify its inspected image ID equals original. Build from the verified local tag with `docker build --pull=false --network=none`, pass a *separate* original full immutable image ID `P5_QUALIFIED_BASE_IMAGE_ID` to the image provenance label `blazux.p5.base_image`, and validate that label after build and again at plan. No GPU, cache, container stop/restart, image removal or remote pull needed in `prepare`. Add CPU/Fake-DGX tests for alias creation, alias collision, daemon failure, build arguments and negative provenance. Corrected DGX trial still **NOT_RUN** until operator retries.

[Details and runbook](../docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md). **Next operator commands:** pull latest `feature/recipe-wizard-handoff`, run manifest validate; run `./wizard.sh p5 trial prepare --json` and `./wizard.sh p5 trial plan --json`. A failed plan must **never** be used in `execute`; avoid chaining a failed shell `PLAN_ID=$(...)` followed by an independently executing test. Only proceed with actual GPU if plan `READY_TO_APPROVE` and approval token is valid, using previously granted *development* downtime and no-restore acknowledgment.

---

## 2026-11-08 — P5 Orcarouter real GPU MTP0 no-auto-restore live-trial path

**Developer DGX, explicitly operator-authorized interruption**: The currently active 27B is **not** required for service, and failure **does not require restoration**. Latest source commit `599ff47` added `scripts/manager/p5_live_trial.py`, `./wizard.sh p5 trial {prepare,plan,execute,status}`, P5 candidate image build with inherited pinned vLLM0.32 source and BF16 PLE mmap, isolated MTP0 start on :8000, model+image+GPU/live API identity revalidation, short-expiring SHA256 exact plan and explicit `I_ACCEPT_P5_NO_ROLLBACK` acknowledgment. On failure leave 27B stopped and preserve the failed target/container/logs/images/HF files and write a private receipt. The standard production transition rollback policy is unchanged; only the **scoped P5 MTP0 development trial** is no-restore. MTP2 is NOT included.

[New detailed runbook](../docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md); [CI #42438845913 SUCCESS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42438845913): 67 P5 CPU/Fake-DGX tests PASS. **This GitHub session has NOT operated the real DGX.** New code must be pulled to actual DGX. Operator execution: `./wizard.sh manifest validate --json`, `./wizard.sh p5 trial prepare --json`, `./wizard.sh p5 trial plan --json`, then separately `./wizard.sh p5 trial execute --approve-plan HASH --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json`. Confirm exact current source, image, remaining GPU containers and plan ID before dispatch. If target fails, gather `docker logs --tail 180 qwen38-orcarouter` and private receipt; no automatic 27B start. No P3 replay, P4 prune, P6 live transition, P8 fault injection, PR merge or source file deletion.

---

## 2026-11-08 — Latest P5 PLE v2 / GPU-permitted development DGX

Source HEAD `d395368` [CI #42436269922 SUCCESS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42436269922). The Wizard's **seven-document** shared registry now includes `runtimes/ple-assets.json` schema v2 and `runtimes/ple-loader-profiles.json`. The PLE asset format is **independent** of model-body quantization, MTP donor and KV cache. BF16 remains pinned for Orcarouter, while FP8/F16/F32 and other explicitly modeled encodings can be registered as *unqualified* future assets. Source loader 0.32.0 GB10 remains NOT_RUN; no GPU release. The model switch preview requires no hot reuse of PLE mmap, independent PLE loader/scale/TP1 worker checks, GPU allocation and port 8000 release, preserved old assets and exact rollback.

The operator explicitly allowed downtime of current development DGX 27B and GPU use. Do not claim a production deployment or that this GitHub-only session touched the live machine. P5 `--gpu-trial` remains blocked until a pinned real vLLM0.32/ARM64 image/loader, rollback and exact guarded plan are qualified. User-provided pre-refactor DGX evidence had PLE 128/128 BF16 PASS, MTP donor 31/31 BF16 and 3 pinned SHA PASS, 27B live on 8000. Latest new schema has not been run on DGX. Separate external research: [dolf3131 lane pinned 45e3d477](https://github.com/dolf3131/dgx-spark-llm-serving/tree/45e3d47771577dabab0998e9013e85dd0915ae4f) and [NVIDIA DGX Spark forum](https://forums.developer.nvidia.com/t/nvidia-official-qwen3-8-flash-next-checkpoint-for-single-dgx-spark/385994) inform FP8 PLE global BF16 scale, TP1 offload worker, independent quantization and B12X compatibility; no external image/patch was adopted.

Read `docs/P5-PLE-FORMAT-AND-DGX-SPARK-REFERENCE-ADOPTION-20261108.md`. Next DGX **read-only**: `./wizard.sh manifest validate --json`, `./wizard.sh model list --installed --json`, `./wizard.sh p5 doctor --read-only --json`, `./wizard.sh service manager status --json`. No P3 historical replay, P4 deletion, P6 transition, P8 faults, auto cleanup, loss of HF caches/images/receipts or Draft PR merge.

---

## 2026-11-08 — NEXT after manifest registry CPU PASS

After clean DGX fast-forward to the latest branch HEAD, **read-only** run `./wizard.sh manifest validate --json`, `./wizard.sh model list --installed --json`, `./wizard.sh select orcarouter --json`, `./wizard.sh p5 status --json`, `./wizard.sh p5 doctor --read-only --json`, and `./wizard.sh service manager status --json`. Verify manifest graph integrity and actual pinned BF16 PLE 128/128 independently from the 31/31 BF16 MTP donor and live 27B API on :8000. Keep metadata PASS vs mmap GPU NOT_RUN. Source commit `a17b361` [CI #42433160630 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42433160630) (996 executed CPU test cases over 44 invocations, duplicates included); confirm follow-up selector/docs CI separately.

Before any overlay generation obtain separate asset-write approval; before any GPU trial/27B stop require a separately qualified vLLM 0.32 ARM64 image, exact rollback/expiry/TTY consent. The P5 GPU trial remains blocked. Preserve all source caches, P3 historical tests, P4 deletion dry-run policy, P6 separate switching, P8 final fault/recovery and unmerged Draft PR #1. Reference `docs/WIZARD-MANIFEST-REGISTRY-AND-PLE-ASSETS-20261108.md`.

---

## 2026-11-08 — P5 vLLM 0.32 opt-in ABI candidate (source only, not built)

After first source CI PASS, compared actual upstream `vllm-project/vllm@v0.32.0` Qwen4Exp Python sources. `vllm/models/qwen4_exp/nvidia/model.py` blob `2fb056bde43cfa5b0d9f0e15545e4ca3a2782c98`, `mtp.py` blob `32e95faa0dc882150a3b7dd9809641651fb2ff4e`, and `vocab_parallel_embedding.py` blob `92e65c839dbf40fa3b983e57e2364eb7cbf52654`. Official v0.32 model.py and mtp.py each have precisely one candidate ParallelLMHead prefix anchor; MTP draft config and load-weights return anchors each appear once. Importantly v0.32 `CompressedTensorsConfig.ignore` exists independently of `ignored_layers`/`exclude_modules` and the upstream draft converter does not explicitly remap `ignore`.

New **source-only** `src/p5_patch_qwen4exp_v032.py` provides fail-closed, idempotent candidate source transformations: opt-in `ParallelLMHead(quant_config=...)`, remap `CompressedTensorsConfig.ignore`, and exact 31-name BF16 MTP loader guard (not len-only). The pin names are cross-checked against vendor YSLAB MTP manifest. `Dockerfile.p5.candidate` requires an explicitly supplied **qualified immutable base** from Blazux 0.32; it contains no YSLAB development Docker base, no default `VLLM_P5_ORCAROUTER` opt-in, and **has not been built**. The Python patch `--apply` requires `P5_EXPLICIT_IMAGE_BUILD=1` and a vLLM 0.32.0 installed package. Additional CPU tests prove marker/AST/idempotence, tamper refusal, 31 exact names, version gate and no source writes without explicit build opt-in. P5 one-shot static audit now detects the source candidate. This is NOT evidence that installed DGX vLLM/ABI, GPU, quantized lm_head, runtime MTP2 or any benchmark works.

This candidate is deliberately not integrated into `Dockerfile` or production start. Strict `launch_allowed=false`, `register_as_runtime_recipe=false`, no image digest, no GPU execution or Docker mutation. `--gpu-trial` remains BLOCKED; image build, overlay asset creation and 27B downtime each require separate explicit operator approval and rollback gate. Maintain P3/P4/P6/P8 restrictions and keep Draft PR #1 unmerged. Confirm follow-up commit's CI before claiming the new tests passed.

---

## 2026-11-08 — NEXT: P5 DGX read-only source qualification, then separately approved runtime work

Source commit `33adec1` [Actions 42429745463 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463). P5 Wizard, pinned source recipe and one-shot are implemented but **not released for actual GPU**. After a clean fast-forward on DGX, inspect `git rev-parse HEAD` and `./wizard.sh service manager status --json`; execute only `bash scripts/temporary/p5-one-shot-acceptance.sh --plan --json`, `--cpu-only --json`, and **`--read-only --json`**. The final mode reads local pinned caches and verifies SHA256 of up to three large donor shards without altering assets, so schedule its disk I/O appropriately.

Then independently inspect Blazux vLLM 0.32 ARM64 loader ABI, checkpoint compressed-tensors/quantized lm_head, MTP 31/31 guard, PIECEWISE graph splitting and CUDA kernels. Before invoking vendor MTP-overlay view builder, obtain separate asset-write approval. GPU trial (first MTP0, then MTP2) needs fresh exact TTY downtime consent, approved 27B restoration sequence and benchmark/test plan; the current `--gpu-trial` is deliberately BLOCKED. Preserve the strict `1e-4` logprob gate, :8000, ONE_ACTIVE_MODEL_ONLY, 27B, all HF assets. P3 historical tests, P4 deletion, P6 switch and P8 fault/recovery are not to be repeated or initiated. Draft PR #1 remains unmerged.

---

## 2026-11-08 — Next conversation: P5 implementation + one-shot automatic adjudication

User explicitly selected P5 next: integrate **YSLAB Orcarouter BF16PLE / MTP** reference on **Blazux vLLM 0.32** (NOT YSLAB's vLLM 0.1.dev image or standalone port 18300). Work in existing `feature/recipe-wizard-handoff`, Draft PR #1, review parallel design branch but do not merge it blindly. New mandatory starter: `handoff/START-NEXT-P5-20261108.md`; full implementation contract `docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md`; audit `docs/HANDOFF-DOCUMENT-AUDIT-P5-20261108.md`.

**Develop all together:** pinned Orcarouter/PLE/MTP compatibility and exact recipe/service manifest; vLLM 0.32 adapter; deterministic 31 BF16 MTP donor overlay; MTP OFF baseline and MTP2; Wizard doctor/prepare/start/verify/benchmark; CPU/Fake-DGX tests; `scripts/temporary/p5-one-shot-acceptance.sh` source/read-only/GPU-stage auto-judge and isolated JSON receipts. Code implementation and CI can proceed; real GPU execution, 27B shutdown, download/cache changes and port cutover require **new exact operator approval**. Do not auto-start P6/P8 or remove P4 assets.

**Previous P4 is closed only for actual DGX read-only dry-run** (13/13 CPU, 9 reviewed / 0 selected; no deletion), so no new P4 cleanup run. P5 source/CPU/GPU evidence will have separate statuses. Do not claim current P5 code, runtime or benchmark as PASS before actually implemented and measured. Older P4-A/P4-B/C NEXT sections below are superseded by this new top entry.

---

## 2026-11-08 — P4-B/C one-shot REAL DGX dry-run accepted; no cleanup now

The operator's combined report is **READ_ONLY_DRY_RUN_PASS**, 13/13 Fake-DGX PASS, P4-B review 9 assets / selected 0, P4-C `DRY_RUN_COMPLETE_RELEASE_GATED` with 2 PASS / 2 DEFERRED / 1 NOT_RELEASED / 1 NOT_EXECUTED and no mutation or approval. Record the result as **P4-B/C READ-ONLY DRY-RUN COMPLETE**, not real cleanup acceptance. Evidence: `docs/P4-BC-DGX-READONLY-DRY-RUN-EVIDENCE-20261108.md`.

**NEXT:** Do not perform additional P4 deletion attempts, prune, switch 27B, run P5/P8 automatically or merge PR. Actual deletion adapter is absent and cannot be introduced until a new operator request for a real P5 problem or P8 acceptance with exact resource/link/rollback safety, fresh approval and verification. P4-B/C source/real-dry-run handoff may be closed. Older 'run P4-B/C dry-run next' instructions below are superseded.

---

## 2026-11-08 — NEXT: one-shot P4-B/C dry-run on actual DGX, no deletion

Source/CPU P4-B and P4-C rehearsal implemented; run after clean `git status --short` and `git pull --ff-only origin feature/recipe-wizard-handoff`: `bash scripts/temporary/p4-bc-dry-run.sh --json`. The script runs 13 Fake-DGX CPU tests then performs one **read-only P4-A** collection, pure P4-B review and pure P4-C transaction rehearsal. Return JSON, preserving distinction between CPU CI and real DGX run. No `--execute`, sudo, cache mutation, Docker prune, model stop or automatic P5/P8. Actual deletion is separately authorized only if P5 needs it or in P8. See `docs/P4-BC-ONE-SHOT-DRY-RUN-20261108.md`.

---
## 2026-11-08 — P4-A operator real DGX inventory collected; pause before P4-B

P4-A is now **actual DGX READ_ONLY_INVENTORY_COMPLETE / issues=[]**, not merely source ready. Evidence and exact bytes: `docs/P4-A-DGX-READONLY-CAPACITY-EVIDENCE-20261108.md`. Current model 27B API verified, Flash stopped/present, Orcarouter source present, ~324.88 GB (33.06%) filesystem free. Docker reclaimable 182.7 MB containers and 2.088 MB build-cache are **display estimates only** and no verified safe reclaim. Preserve caches, Docker images, stopped Flash, 27B, Orcarouter, receipts, Open WebUI and Portainer. **Do not begin P4-B review/candidate work or P4-C deletion without another operator instruction**. P8 real install/fault/release remains separate. GitHub branch source checkout for the real inventory was `a29cd6e` (889/889 source tests verified on preceding CI); later documentation-only commits do not retroactively change observed DGX runtime.

---

## 2026-11-08 — P4-A next: actual DGX read-only inventory, revised completeness safeguards

P4-A source now treats incomplete Docker capacity categories and GPU/port owners inconsistent with the API-verified active model as **partial evidence**, not a clean inventory. Review the actual operator-side `./wizard.sh storage flash-next inventory --json` output after a safe fast-forward. Confirm all four Docker categories and host cache allocated/free bytes; do not infer reclaimable disk capacity or perform cleanup. P4-B/C and P8 remain separately gated. Source CI must be checked after the latest commit; actual DGX P4-A has not been reported.

---

## 2026-11-08 — Current next-session checkpoint: P4-A read-only inventory

Latest current branch audit and new conversation starter:
- `docs/HANDOFF-DOCUMENT-AUDIT-20261108.md` (all 34 required core documents/recipes present; previous dated audits are historical).
- `handoff/START-NEXT-P4A-20261108.md` (current comprehensive copy/paste starter).
P3 E/F source, metadata and CPU handoff complete; P4-A **source implemented**, actual DGX inventory pending; P4-B/C unauthorized; P8 real reinstall/recovery/final operating signoff pending. Latest pre-audit GitHub state: branch `99ee6b8`, 887/887 CPU PASS / 40 groups, PR #1 Draft/Open/Unmerged. Re-fetch after any doc commit.

---

## NEXT — ONLY P4-A READ-ONLY CAPACITY/STATE INVENTORY, NO DELETION

P3-E and P3-F DGX verification have completed in their **source/metadata/CPU handoff scope**, NOT runtime reinstall or production lifecycle release. Actual: E 11 indexed shards / 129,771,270,410 apparent bytes / metadata-template hashes / issues=[], F 168/168 CPU PASS in 7 suites, 27B API 8/8. See `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`.

**Operator now authorizes P4-A observation as the next stage before any disposition decision; previous P4 hold remains valid for all mutation and P4-B/C work.** Source-only Wizard command `./wizard.sh storage flash-next inventory --json` (alias `./wizard.sh p4 inventory --json`) reports Docker capacity *estimates*, configured HF cache/repository allocated bytes, filesystem free/total, model/container activity and uncertainty. No raw paths/secrets, no deletion plan or approval. Actual DGX P4-A command has NOT_RUN. See `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md`.

After inspecting actual P4-A output, decide *whether* any cleanup is useful, accounting for shared image layers, symlinked checkpoint views, P8 rollback/reinstall asset requirements. Do not begin P4-B candidate deletion work or P4-C cleanup until another explicit operator decision. Preserve vLLM 0.32, single GPU model, :8000, 27B currently live, P3 receipts, HF assets, P8 release locks and Draft PR #1.

---

## IMMEDIATE — FINISH P3; HOLD P4 (2026-11-08)

The operator explicitly prohibited starting P4. P4 source module/test/CI were reverted in [1110681](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/1110681f451bc72470454bbbee1e1d79d6406a1d). **P4 NOT_STARTED/OPERATOR_HOLD**. Read `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`.

**Two remaining P3 read-only confirmations**: run `python3 -m scripts.manager.flash_host_assets --json` after pulling the new 400,000-key source to check real shard metadata/template; run `python3 -m scripts.manager.p3_dg_acceptance --cpu-only` to record latest 7-suite P3-F local CPU count/production release lock. No GPU/model stop, Docker mutation or fault injection. Save redacted results as evidence.

**P8, not P3:** canonical Flash runtime/reinstall qualification, independently authorized real install/recreate/rollback, general lifecycle production adapter, fault/automatic restore and final release. Historical P3-G remains real PASS/CLOSED. P4 cannot start without another explicit instruction; don't merge PR #1.

---

## 2026-11-08 — P3-E actual DGX 30.43 MiB index parsed, weight_map condition under investigation

**Operator read-only evidence:** `python3 -m scripts.manager.flash_host_assets --json` on DGX observed `model.safetensors.index.json` size **31,907,813 bytes (~30.43 MiB)**, below the 128 MiB cap (134,217,728 bytes). The tool reached `PARSE_SHARD_INDEX` and returned `FLASH_SHARD_INDEX_UNQUALIFIED`. Source code combined three cases into one: a missing/non-dict `weight_map`, an empty map, or a map with **more than 100,000 entries**. No count was in that output; **cause within these three cases not yet resolved**. `indexed_shard_count=0` means no shard enumeration, not model damage or missing shards. Pinned command and prepared `-fp8hybrid` view observed; last actual active service remains 27B :8000.

**New source-only diagnosis:** [135f75c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/135f75c8cc652ed63b8508d10fcf5f079dff24ef) adds redacted `index_weight_map_structure` (OBJECT or MISSING_OR_WRONG_TYPE), `index_weight_map_entry_count_observed`, `index_weight_map_entry_limit` and three distinct bounded errors. **100,000 count cap unchanged** until a real count and intended NVFP4/ModelOpt profile are evidenced; no automatic relaxing, downloading, cache modification or Docker operations. GitHub Actions [42392277467](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42392277467) **878/878 CPU/Fake-DGX PASS, 39 groups**, 2 new tests. No hardware run of this new code yet.

**Next DGX read-only action:** `git pull --ff-only origin feature/recipe-wizard-handoff` then `python3 -m scripts.manager.flash_host_assets --json`; evaluate `index_weight_map_entry_count_observed`, `index_weight_map_structure`, `failure_reason_code`. If entry count is above limit, review bounded parser memory and stable ModelOpt index before targeted policy change. Do not assume 31MB index is corrupt or change HF cache. Flash canonical reinstall remains `false`, launch disabled, generic lifecycle unreleased, historical real P3-G PASS/CLOSED, P8 deliberate fault/auto-recovery/final acceptance NOT_RUN.

---

## 2026-11-08 — Actual DGX Flash shard-index cap identified; bounded source fix

**Actual DGX read-only result:** `python3 -m scripts.manager.flash_host_assets --json` returned `BLOCKED`, `failed_stage=READ_SHARD_INDEX`, `failure_reason_code=FILE_EXCEEDS_BOUNDED_READ`. The pinned command identity and `-fp8hybrid` prepared view matched; no model shard contents were examined because `model.safetensors.index.json` exceeded the generic 8 MiB metadata cap. **Actual index byte size is still unknown** and zero recorded shards means unchecked, not missing/corrupt. No DGX GPU or Docker mutation, 27B service remains the last observed active :8000.

**GitHub SOURCE fix:** [56d39e4](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/56d39e4acb5d4e69777372283fe5f8839a16fc7c) uses separate **128 MiB hard cap for index only**, 8 MiB config/tokenizer_config cap, 256 KiB template cap; files are bounded at read time (`read(limit+1)`) to prevent stat/read growth bypass. Adds sanitized numeric `index_file_size_bytes_observed`/`index_file_size_limit_bytes`. Tests cover >8 MiB valid JSON and exceeding index cap. GitHub Actions [42391564016](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391564016) **SUCCESS 876/876 CPU/Fake-DGX, 39 groups** (874 previous + 2 new). This is *not* new DGX asset or GPU validation.

**Next read-only operator step:** `git pull --ff-only origin feature/recipe-wizard-handoff` followed by `python3 -m scripts.manager.flash_host_assets --json`. Observe numeric index size and full staged status. If blocked again, investigate actual `failed_stage` and `failure_reason_code` before altering limits or files. Do **not** change HF caches, start/stop/reinstall/switch models, or inject failures without new explicit consent. Flash canonical reinstall NOT QUALIFIED; P3-F lifecycle release OFF, P3-G real bidirectional PASS historically CLOSED, P8 NOT_RUN.

---

## 2026-11-08 — Latest blocked Flash host assets after real DGX read-only trial

- First actual DGX `flash_host_assets --json` returned a generic `ValueError` after pinned command/env/cache validation; shard count 0 and metadata hashes empty mean **unverified**, not necessarily absent. Prior `verified_model_revision=true` was misleading.
- [Source-only diagnostic fix 9beb1d3](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/9beb1d3f73675ac4a22daedfc2167b380742305c) tracks explicit sanitized failure stage/reason and separates pinned command from host prepared file evidence; `verified_model_revision=false` is conservative absent trusted hash/source validation.
- [Actions 42391221418](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391221418): **874/874 CPU/Fake-DGX PASS, 39 groups**, no hardware operations.
- **Next** retrieve redacted actual failure using `python3 -m scripts.manager.flash_host_assets --json` after Git pull. **Do not** patch cache, regenerate model, adjust caps, or reinstall on a guessed diagnosis.

---

## 2026-11-08 — P3-E host asset inventory next, no service mutation

Operator's latest DGX read-only `--sudo-ss` P3-D/E/F/G output: **P3-D READ_ONLY_PASS**, independently attributed docker-proxy IPv4 PID `2560693` and IPv6 PID `2560708`, GPU PID `2560905`, no detected GPU ownership conflict. **P3-E DRAFT_REVIEW_REQUIRED** despite `cmd_normalized=true` using `FLASH_FP8HYBRID_READ_ONLY_V1`, `cmd_normalization_error=null`, draft-field `issues=[]`, because canonical reinstall remains unqualified. **P3-F 153/153 DGX-local CPU PASS**. P3-G preview in this particular runner does not invalidate previously completed real bidirectional G. `blocked_stages=[]` with total `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` is expected.

GitHub source: [03cbe4c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/03cbe4cc45a750322c4f99616c85f1061f7b2288), [2b44ccc](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/2b44ccc0237fa34742e28608ad089cb3ca90fe55), and [8e8fcec](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/8e8fcec5acb280e01445a2bd773fc9f4ecedf2f6). Source-only CI [42390619936](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42390619936): **870/870 PASS, 39 groups**, including 5 new Flash host asset tests.

1. On DGX after `git pull --ff-only origin feature/recipe-wizard-handoff`, run only `python3 -m scripts.manager.flash_host_assets --json` and review its allowlisted output. This command reads existing `qwen38-flash` Docker inspect plus bounded local host metadata and template; no service change. Treat an incomplete/blocked result as evidence to investigate, not permission to recreate.
2. Distinguish actual local image ID from registry digest, verify complete Docker security/network/restart fields, inherited versus runtime Env (37 additional keys in last observation), and pinned template file hash before drafting an unregistered Flash reinstall target. Do not upload raw Env, Config, HostConfig or host paths.
3. Add CPU/Fake-DGX desired-vs-observed negative tests, bounded recreating/stopping failure-state proof, and backup/journal semantics. Preserve 27B recipe SHA and prior P3 receipts.
4. Seek a separate exact-plan operator approval for any real Flash installation, port-8000 service interruption or container re-creation. P8 remains for deliberate fault injection and final operational/release acceptance, not P3-G.

**No P3 A/B/C/G replay.** Keep vLLM 0.32, no SGLang, ONE_ACTIVE_MODEL_ONLY and fixed :8000.

---

## 2026-11-08 — Flash command parser CI confirmation

The 3-test follow-up source commit [bb4d64e](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/bb4d64e02e0d73d6406e6e0d7c593ec86ba4c954) passed GitHub Actions [42388253469](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42388253469): **865/865 CPU/Fake-DGX tests in 38 groups, SOURCE-ONLY**. The operator's 150/150 DGX-local CPU result predates these 3 source tests; new DGX-local CPU execution has not yet been observed. P3-D privileged PID check remains optional explicit operator step; E remains reinstall-unqualified, F unreleased, G historically real PASS/CLOSED, P8 NOT_RUN.

---

## 2026-11-08 — DGX operator read-only P3-D/E/F/G follow-up

**Operator evidence:** `docs/P3-E-F-DGX-READONLY-20261108.md`. At DGX local read-only snapshot, 27B API at :8000 is `LIVE_SERVICE_VERIFIED` with 8/8 checks true. P3-D remains `BLOCKED` only because unprivileged `ss` exposed no port listener PID (`sudo_ss_requested=false`); not a measured GPU conflict. P3-E full Flash draft-field match `issues=[]`, but reinstall unqualified with 37 extra environment keys and zero extra mounts; 27B-only command normalization reported Flash `-cc` tokens as unexpected positionals. P3-F new code ran **150/150 CPU tests PASS on operator DGX**; P3-G is only preview in this run, while prior real two-way G is CLOSED. The source follow-up introduces strict read-only Flash FP8-hybrid argv normalization, no service operations or release gate changes. Historical P3-G, P8 boundaries and Source/DGX classifications remain intact.

---

## 2026-11-08 — Immediate P3-E/F continuation

Source change: [d68106a](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d68106a24c4c6071acff7a4d98d74e04c6ecbfe1). Actual GitHub Actions [42386939625](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42386939625): **862/862 PASS in 38 CPU/Fake-DGX groups** (856 baseline + 6 new). This is **SOURCE-ONLY**; no fresh DGX test or service change. Full scope: `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

1. **P3-E read-only DGX inventory:** reobserve full Flash Config/HostConfig/Env/Mounts/command, sanitize secrets and host paths, validate prepared `-fp8hybrid` view, mount file digests, local image origin and exact parser/MTP/Yarn runtime settings. Do **not** generate a launchable recipe from only documented fields.
2. **P3-E source candidate:** version canonical Flash desired-state contract separately from legacy source draft; add strict CPU/Fake-DGX normalization/negative tests for actual host config, cache source, template bytes, port, GPU, IPC/SHM, image and native tools. Keep unregistered/non-executable until independent qualification.
3. **P3-F source expansion:** test partial journal failures, unknown port/GPU owners, stale approval, failed candidate reconciliation and idempotent recovery. Never auto-retry uncertain state.
4. **CI and evidence:** ensure new source tests stay green, record HEAD and run, never label CI a real DGX test.
5. **Operator-only downstream:** propose bounded Flash reinstall/restore acceptance plan with fresh SHA, exact affected resources, downtime and stop conditions. Obtain distinct approval before modifying any DGX model/container. P8 handles intentional fault injection/final release; do not replay P3 A/B/C/G.

**Current safety gates:** no `PRODUCTION_LIFECYCLE_RELEASED`, no Flash canonical qualification, no P8 execution approval.

---

## 2026-11-07 — P3-A–G EVIDENCE AUDIT / P3-G CLOSED; P8 OWNS FAULT & FINAL RELEASE

**New canonical audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md` and `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`. Stage results: **P3-A/B/C** original immutable one-off real DGX PASS/CLOSED (A Flash→27B, B 27B→Flash, C Flash→27B); **D** real read-only GPU+IPv4/IPv6 host :8000 PID ownership PASS from operator `--sudo-ss` run (pre-latest switch); **E** Flash source `-fp8hybrid` prepared view and versioned draft-field match, but **canonical Flash reinstall recipe UNQUALIFIED** (`DRAFT_REVIEW_REQUIRED`, `launch_allowed=false`); **F** six Fake-DGX/CPU suites **144/144 local PASS**, but `PRODUCTION_LIFECYCLE_RELEASED=false` and generic live install/reinstall not accepted; **G** actual independent 27B→Flash→27B TTY-approved ordinary two-way transfers **REAL PASS/CLOSED** with two receipts, API identities, final 27B `diff=[]`, journal VERIFIED/COMMITTED 28 events, last actual active `qwen38-27b` on port 8000. **P3-A–G aggregate = PARTIAL (E open, F source only)** despite G closed. The user explicitly moved intentional failure injection, automatic restore and final operational/UX/production signoff to **P8** (NEW, NOT_RUN, not authorized to execute). P7 is integration only. Preserve old receipts, model assets and `ONE_ACTIVE_MODEL_ONLY`; no P3 A/B/C/G replays or fault injection to perform this audit. Latest P8-source registration CI [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS 856/856 CPU tests 38 groups (source evidence only). Basic post-switch service manager `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are **NOT PROBED** by that command, not conflicts; do not overclaim fresh D audit. The single-script D–G read-only runner prints G preview even after separate real G PASS by design.

**PRIORITY:** (1) P3-E audit/qualify installable canonical NVIDIA Flash FP8-hybrid recipe without silently recreating preserved Docker; design Fake-DGX path first; explicit DGX downtime separate. (2) P3-F distinguish CPU/source regression PASS from actual generic lifecycle operations release. (3) Continue optional P4 disposition → P5 Orcarouter runtime → P6 Orcarouter/27B transfer → P7 service/proxy/gateway integration. (4) P8 design bounded deliberate failures and source restoration, test source first, then request a **new explicit** maintenance/fault approval, finally operational UX/release signoff. P3-G real two-way done; no replay. Verify latest source CI before any new code acceptance.

---

## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

**NEXT (operator TTY, already permitted downtime scope but fresh four inputs REQUIRED):** Verify clean branch and `git pull --ff-only origin feature/recipe-wizard-handoff`; `./wizard.sh service manager status --json`; `python3 -m scripts.manager.operational_audit --json`; then read-only `bash scripts/temporary/operational-switch-acceptance.sh --target 27b --plan --json`. Only if `READY_FOR_SEPARATE_TRIAL_APPROVAL`, source `flash-next`, target `27b`, issues=[], run in a real terminal `bash scripts/temporary/operational-switch-acceptance.sh --target 27b --execute`. Approval values are `I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL`, the **new exact SHA displayed**, `I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME`, `I_APPROVE_27B_AS_ACTIVE_MODEL`. Postcheck `./wizard.sh service manager status --json` and `python3 -m scripts.manager.operational_audit --json`. If any error or restore/unknown identity state, STOP; no blind retries or auto-chain. **Do not execute from GitHub tools or a non-TTY call.** Full `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`.

---

## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

**IMMEDIATE NEXT OPERATOR STEP (REAL DOWNTIME PERMITTED):** On a clean checkout, `git pull --ff-only origin feature/recipe-wizard-handoff`, then `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --plan --json`. Only if `READY_FOR_SEPARATE_TRIAL_APPROVAL`, directly run in a real terminal: `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute`. Four explicit inputs printed by Wizard: `I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL`, **fresh displayed execution plan SHA**, `I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME`, `I_APPROVE_FLASH_NEXT_AS_ACTIVE_MODEL`. After PASS, run `./wizard.sh service manager status --json` and `python3 -m scripts.manager.operational_audit --json`. **STOP and share output** before second direction; on failure do not auto-retry. Only after verified PASS and fresh reverse read-only plan use `--target 27b --execute` with a NEW four-input approval (last `I_APPROVE_27B_AS_ACTIVE_MODEL`). See `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md` for full gates and evidence.

---

## 2026-11-07 — THIRD ACTUAL DGX P3-D READ-ONLY PASS; P3-E FP8-HYBRID SOURCE DRAFT

**Actual operator evidence:** Third DGX batch after fast-forward to `1b785c6`: normal `--run` reported D no visible socket PIDs but E `DRAFT_REVIEW_REQUIRED`, F local **136/136 CPU PASS**, G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`. Operator then explicitly ran `sudo -v` followed by `--run --sudo-ss`: **P3-D READ_ONLY_PASS**, both IPv4+IPv6 :8000 `docker-proxy` PIDs (2051487,2051502) independently attributed to canonical active 27B; GPU compute PID 2051842 verified. Overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`, `blocked_stages=[]`, `acceptance_complete=false`; no service mutation or real G transfer. **P3-E** pinned NVIDIA `fc694b54fb0174e0913e6adf86691ef85a4ead47-fp8hybrid` derivative prepared/view files verified; canonical reinstall recipe NOT registered. Legacy Flash cache writable; source metadata and vLLM flags preserved. Evidence `docs/P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md`.

**NEW SOURCE P3-E DRAFT (UNRELEASED):** `recipes/qwen38-flash-next.runtime.draft.json` is `launch_allowed=false`, `register_as_runtime_recipe=false`, not linked into service-policy, no Flash install adapter/executor. `scripts/manager/flash_recipe_review.py` checks versioned pinned Flash 500K/Yarn/MTP2/native tools/image/env/template/mount *documented fields only*, returns `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` or explicit field differences. `P3-E.source_draft_field_review` added to single-script report. P3-E stays DRAFT_REVIEW_REQUIRED; direct live DGX comparison of new code still **NOT_RUN**. CI [42373758262](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42373758262) **854/854 CPU/Fake-DGX PASS / 38 groups**, source only. Full runbook `docs/P3-E-FLASH-FP8HYBRID-SOURCE-DRAFT-20261107.md`.

**Next:** read-only `--run --sudo-ss` batch to inspect E draft comparison, then review remaining host env/mount/image provenance. Separate operator-approved real Flash install and G switch/rollback acceptance required; `PRODUCTION_EXECUTION_RELEASED=False` remains. P3-A/B/C closed, 27B unchanged, P4 optional, P5/P6/P7 queued.

---

After clean `git pull --ff-only origin feature/recipe-wizard-handoff`, use the one command **`sudo -v && bash scripts/temporary/p3-d-g-acceptance.sh --run --sudo-ss --report /tmp/p3-d-g-e-draft-$(date +%Y%m%dT%H%M%S).json`**. Check `stages.P3-E.source_draft_field_review.status/issues/draft_recipe_sha256`. If D remains unchanged, it already has actual DGX PASS evidence. E can match draft fields but still must NOT be marked reinstall-qualified. No unattended real switching or downtime.

## 2026-11-07 — SECOND ACTUAL DGX D–G BATCH + PINNED FP8 HYBRID / HIDDEN SOCKET PIDS

Actual operator DGX batch (**read-only; no model changes**) after previous source fixes: **P3-D BLOCKED** because `ss` showed BOTH IPv4 0.0.0.0:8000 and IPv6 [::]:8000 LISTEN but no process PID; Docker reported only running `qwen38-27b` as GPU/8000 port owner, NVIDIA compute PID 2051842 verified to active 27B. **P3-E BLOCKED** because the observed preserved Flash checkpoint was pinned NVIDIA source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` plus **`-fp8hybrid` local prepared variant**, not a different HF revision; canonical Flash reinstall recipe still unqualified. Flash /hf mount observed writable and legacy argv preserved. **P3-F PASS 128/128 actual local CPU tests. P3-G preview PASS**, current Docker ID and VERIFIED/COMMITTED journal; actual transfer/rollback NOT executed. Overall exit=3, acceptance_complete=false.

Subsequent SOURCE fix: E now recognizes only exact pinned NVIDIA source revision plus `-fp8hybrid` prepared view and verifies `.prepared`/essential files read-only; no recipe promotion. D now permits ONLY operator-selected `--sudo-ss` to run `sudo -n ss` (no prompt; no sudo by default) and independently reverify unchanged socket set and PID provenance. Unknown PID always BLOCKED. CPU CI [42371861344](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371861344) **846/846 PASS / 37 groups**, SOURCE-ONLY, actual DGX rerun pending. Full evidence `docs/P3-D-G-SECOND-DGX-PID-HYBRID-DIAGNOSTIC-20261107.md`. No P3-A/B/C replay, no production switch release.

NEXT read-only DGX retest after `git status --short` and clean `git pull --ff-only origin feature/recipe-wizard-handoff`: `bash scripts/temporary/p3-d-g-acceptance.sh --run --report /tmp/p3-d-g-v3-$(date +%Y%m%dT%H%M%S).json`. If D still hides socket PIDs and operator explicitly consents to privileged read-only socket diagnostics, run `sudo -v` THEN (nonroot) `bash scripts/temporary/p3-d-g-acceptance.sh --run --sudo-ss --report /tmp/p3-d-g-v3-sudo-ss-$(date +%Y%m%dT%H%M%S).json`. **Do not invoke the whole Wizard as sudo.** E expected DRAFT_REVIEW_REQUIRED only if actual prepared derivative assets are present. No real G switch.


---

## 2026-11-07 — NEXT OPERATOR ACTION: READ-ONLY D/E DIAGNOSTIC RETEST

The first actual DGX P3-D~G unified batch was run. F 119/119 CPU PASS and G current-ID/journal PREVIEW PASS. D host socket attribution and E Flash parser blocked (NOT demonstrated hardware/service failure). New source safely repairs dual-stack host PID recognition, Docker proxy attribution, and legacy Flash candidate collection; CI 42371091647 **838/838 PASS**.

On a clean DGX checkout:
```bash
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p3-d-g-acceptance.sh --run --report /tmp/p3-d-g-readonly-v2-$(date +%Y%m%dT%H%M%S).json
```
Examine D `observed_port_listener_rows`, `port_pid_attribution`, `ss_returncode`, E `observed_candidate.raw_cmd` / `cmd_normalization_error` / `advisories`; do not claim D PASS without actual attribution. E is expected to remain DRAFT_REVIEW_REQUIRED until a separate reviewed/reinstall-qualified Flash recipe; do not force G real switch/rollback from the automatic batch. Historical A/B/C and canonical 27B SHA untouched. Detailed `docs/P3-D-G-FIRST-DGX-DIAGNOSTIC-FIXES-20261107.md`.

---

## 2026-11-07 — P3-D/E/F/G ONE-COMMAND DRAFT ACCEPTANCE: NEXT DGX STEP

**Source completion evidence:** P3-D~G unified draft implementation code HEAD `efb0dda` was tested by GitHub Actions **42369840239 SUCCESS, 829/829 tests / 37 groups**. The user still needs to run the ONE non-mutating DGX batch; no actual D/E/F/G real acceptance evidence is claimed.


**Stage labels are now P3-D/E/F/G** after completed P3-A/B/C. Run ONE read-only acceptance batch on DGX after clean pull:

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p3-d-g-acceptance.sh --plan
bash scripts/temporary/p3-d-g-acceptance.sh --run --report /tmp/p3-d-g-readonly-$(date +%Y%m%dT%H%M%S).json
```

Collect the full JSON/exit status and classify D (GPU/port process attribution), E (Flash observed candidate/qualified recipe missing), F (CPU suite), G (current-ID switch and journal preview). Expect `E.DRAFT_REVIEW_REQUIRED` until a reviewed Flash recipe exists and `G.PREVIEW_PASS_REAL_SWITCH_NOT_RUN` even if all read-only prechecks pass; neither means final acceptance. Do not use `--execute`, do not replay P3 A/B/C, do not stop 27B or promote Flash recipe without new scoped operator approval. Next SOURCE priorities after first DGX output: close D environment-specific visibility gaps; qualify Flash E; complete F executor/rollback/crash semantics; conduct separately approved real G trial. P4 optional deletion decision and P5/P6/P7 follow.

Full runbook: `docs/P3-D-G-UNIFIED-WIZARD-DRAFT-ACCEPTANCE-20261107.md`.

---

## 2026-11-07 — DGX READ-ONLY CURRENT-ID SWITCH PREVIEW NOW PASS; NEXT GATES

**The earlier read-only DGX step is COMPLETE** on source `4189a79`: canonical 27B matches including explicit HF source; operating switch preview 27B -> Flash-Next has `status=READY_FOR_OPERATOR_REVIEW_ONLY`, `issues=[]`, `source_lineage=CANONICAL_RECIPE`, `target_lineage=HISTORICAL_P3_INSTANCE`, current Docker IDs sourced from live inspect; service manager remains `LIVE_SERVICE_VERIFIED`. Details in `docs/WIZARD-27B-OPERATIONAL-PREVIEW-DGX-PASS-20261107.md`. Do **not** repeat this read-only test absent drift.

**Remaining work in priority order:** (1) source-only independent GPU process/host port ownership read-only audit; (2) qualify canonical Flash runtime recipe (do not reinterpret the P3 Flash historical instance as a reinstall-verified recipe); (3) strengthen generic executor crash/rollback journal and independent benchmark pointer/backup cleanup; (4) CPU/Fake-DGX tests and CI; (5) real DGX switch/rollback acceptance in separately authorized maintenance window; (6) only then consider releasing production operations. Service policy ONE_ACTIVE_MODEL_ONLY, vLLM 0.32 and :8000 remain unchanged. No Docker mutation/cleanup or P3 replay authorized.

---

## 2026-11-07 — NEXT: VERIFY CURRENT-ID-AWARE SWITCH PREVIEW ON DGX (READ ONLY)

Current operator DGX observation already confirms **canonical 27B `diff=[]`, API LIVE_SERVICE_VERIFIED**, exact actual host HF source `/home/inlc/.cache/huggingface`, and no need to recreate active 27B. Later source code updated ordinary switch preview/executor to accept fresh current canonical 27B ID, retaining old P3 receipts only as history; 814/814 CPU/Fake-DGX tests PASS, CI 42367665200.

Next operator safe checks after clean git fast-forward:
`./wizard.sh model 27b recipe-diff --cache-source /home/inlc/.cache/huggingface --json`
`./wizard.sh switch flash-next-27b operational --target flash-next --plan --json`
`./wizard.sh service manager status --json`.

Investigate any new PREVIEW blockers without overriding. Do not perform `--execute`. Remaining engineering: qualified Flash-Next runtime recipe and host source policy, immutable benchmark pointer promotion, verified backup retirement, robust crash consistency/rollback, independent GPU exclusivity/port process ownership, real DGX maintenance acceptance and user-facing lifecycle release. Historical P2-FINAL/P3-C remain complete and must not replay. No new SHA approval was given here. See `docs/WIZARD-27B-LIVE-DRIFT-CURRENT-ID-20261107.md`.

---

## 2026-11-07 — ACTIVE NEXT ACTIONS after Wizard SOURCE implementation (CI 799/799 PASS)

1. Pull the latest feature/recipe-wizard-handoff commit with a clean fast-forward on DGX. Run READ-ONLY ./wizard.sh model 27b recipe-diff --json and ./wizard.sh service manager status --json; inspect false-positive differences against current 27B actual Docker Cmd, mount RO/source, GPU, ports, API. No execute.
2. Pin/verify trusted host HF cache location and qualified Flash-Next recipe before generic model uninstall/reinstall release. Do not edit the existing qualified 27B recipe SHA casually.
3. Replace stale P3 receipt Docker IDs used by operational_switch.py / operational_executor.py live checks with fresh observed IDs while preserving historical receipt integrity.
4. Complete source-level private journal/crash guarantees, independent verified backup cleanup and atomic benchmark latest-pointer promotion; test idempotence, interrupted writes, uncertain rollback. Existing generic lifecycle execution remains hard-gated False.
5. Separate DGX operator authorization and real UX, fault/rollback, one-active-model, :8000 and 27B tool/benchmark acceptance before production gates change. P4-P7 remain later; P2-FINAL and P3-C stay PASS/CLOSED.

Implementation scope and caveats: docs/WIZARD-LIFECYCLE-SOURCE-IMPLEMENTATION-20261107.md. New GitHub CI run 42355750124, **799 CPU/Fake-DGX PASS in 36 groups**. This is NOT actual DGX live qualification.

---

## 2026-11-07 — HANDOFF DOCUMENT AUDIT / NEXT CONVERSATION READY

The user starts the next development phase in a separate conversation. **Audit verified all 8 handoff docs, 12 implementation docs and 5 recipe/manifest/benchmark indices exist (25/25), plus both published benchmark collection directories and current source/evidence files.** The pre-audit HEAD `9ec7420b74369e7a76785577dc543f9dafb8897d` had GitHub Actions run `42352654468` SUCCESS, **757/757 CPU tests in 34 groups**. This CI is source-only. New documentation commits advance HEAD; inspect GitHub afresh.

A new **complete standalone** prompt is in `handoff/START-NEXT-WIZARD-LIFECYCLE-20261107.md` and prominently at the top of `handoff/SESSION-START-PROMPT.md`; older prompts below are ARCHIVED / superseded. Missing-document/staleness audit: `docs/HANDOFF-DOCUMENT-AUDIT-20261107.md`. Next implementation contract: `docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md`.

**Latest actual DGX:** canonical NVIDIA 27B native-tool recipe, 3/3 benchmark v2, Open WebUI Native user-confirmed PASS, two old diagnostic containers removed via verified Wizard manifest cleanup; original `qwen38-27b` runs at :8000 with served `qwen3.8-27b`, Flash container stopped, Open WebUI/Portainer running. P3-C historical PASS/CLOSED, P8 conditional migration ticket INACTIVE. Do not restart the old P2 Tool HTTP-400 diagnosis; it was resolved. Old original 27B Docker container IDs recorded in P3 stage receipts remain HISTORICAL. `PRODUCTION_EXECUTION_RELEASED=False` for main Wizard generic switch; post-ID-change real guided switch/recovery acceptance still open.

**Next target:** general Wizard lifecycle/recipe-diff detection at install/start/restart/switch, scoped container remove/reinstall/recreate with fresh approval, new runtime receipt and rollback. No global deletion prohibition on canonical 27B or Flash. No live DGX mutation is authorized by this documentation step. The canonical `recipes/qwen38-27b.runtime.json` file's exact SHA is tied to current approved benchmark pointer: do NOT silently edit this file to fix text/metadata. Preserve old P3/bench receipts, images/caches, vLLM 0.32, one GPU model, port 8000, Draft PR #1.

---

## LATEST REAL DGX — 2026-11-07 Wizard manifest cleanup actually executed and VERIFIED: two historical test containers REMOVED

**Operator-provided real DGX terminal stdout** after fast-forward to `9518f25e614367ab0ebbb725d7568e5c6bf177ed`: `./wizard.sh service manager inventory --json` listed original canonical `qwen38-27b` active on :8000 and two retired stopped containers. `./wizard.sh service manager cleanup --plan` returned `READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL`, `issues=[]`, target_count=2, plan `39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5`, active container full ID `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`. User then supplied exact fresh SHA and both TTY approvals to `./wizard.sh service manager cleanup --execute`, which returned **`MANIFEST_RETIRED_CONTAINERS_CLEANED`**, `executed=true`, `issues=[]`, `remaining=[]`, `preserved_original_model_service=true`, `preserved_images_and_caches=true`. Exact removed names and Docker IDs:
- `qwen38-27b-failed-6d9ede0904c2` → `44920f80610c5787f7d72064269be175d18150fe68d5a2fe846499129fc596bc`.
- `qwen38-27b-native-tools-v1` → `d42a15e2f7959829eeb616d748522193999441c9f418ec5dcae98931dfe5da56`.

**INDEPENDENT POSTCHECK PASS:** `./wizard.sh service manager cleanup --status` → `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, `remaining=[]`, `active_service_preserved=true`, private immutable receipt `result-39f38df37561bbfdffbe0ecce12566a7f3d0d51cd8c5b90190c506e68e28bbd5.json`. `./wizard.sh service manager status --json` → `LIVE_SERVICE_VERIFIED`, `API_IDENTITY_CONFIRMED`, `issues=[]`, served model ID `qwen3.8-27b`, port 8000. `docker ps -a` lists ONLY running `qwen38-27b`, stopped `qwen38-flash`, running `open-webui` (healthy) and `portainer`. The status tool's `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are untested scopes, not observed conflicts. No separate file-by-file HF checksum check done; cleanup code only removed stopped Docker containers.

**SOURCE/HANDOFF UPDATE (AFTER this real run):** `docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md` contains complete actual-evidence breakdown. `runtimes/service-policy.json.retired_containers.completion` now records consumed plan, exact removed Docker IDs, verified active ID and immutable result pointer; historical target descriptions remain in place **for provenance, not as a pending deletion queue**. `scripts/manager/manifest_cleanup.py` now requires exact Git-tracked completed metadata + matching local 0600 immutable receipt + actual Docker target absence + current canonical API health before reporting DONE. Its `--plan` returns **`ALREADY_CLEANED` without a new approval SHA** when this is all verified; any mismatch blocks, never blindly deletes. The new source did not mutate DGX. Completion is authoritative only when live Docker/receipt agrees, not because Git says so.

**USER POLICY CLARIFICATION:** `qwen38-27b` and `qwen38-flash` are VALID removable/reinstallable managed model services, not globally protected from user-approved uninstall. This one-off cleanup never deleted either. General Wizard uninstall/reinstall, recipe-diff-aware restart/recreation and 27B↔Flash current-ID-aware switching remain NOT_IMPLEMENTED/NOT_RELEASED even though canonical 27B Native Tools real DGX migration + benchmark v2 and Open WebUI Native passed. P3-C historical real PASS closed; P8 conditional ticket inactive. Keep vLLM 0.32, one GPU model active, API port 8000, pinned checkpoint/cache, original P3/benchmark receipts and Draft PR #1 unmerged.

**No further DGX action necessary for retired-container cleanup.** If operator wants a read-only check after pulling this new source: `./wizard.sh service manager cleanup --status`; repeated `--plan` should report `ALREADY_CLEANED` (exit code 3, non-action; use status for success). **Do not run `--execute` again**.

---

## LATEST — 2026-11-07: Wizard manifest-owned retirement of two stopped test containers; canonical models ARE removable/reinstallable

**NEW USER CLARIFICATION (higher-priority than older blanket language):** Do NOT impose a permanent deletion prohibition on `qwen38-27b` or `qwen38-flash`. Both are **operator-removable and reinstallable** Docker model services, as managed model lifecycle policy now records in `runtimes/service-policy.json` `models.*.container_lifecycle`. A future general uninstall/reinstall or recipe-diff-aware recreate command requires its own scoped approval, downtime and qualified reinstall recipe; merely setting lifecycle policy does NOT mean that general Wizard executor has been implemented. For the current user-requested batch, **only** two named stopped historical DGX test containers are selected: `qwen38-27b-failed-6d9ede0904c2` and `qwen38-27b-native-tools-v1`. This is operation-specific scoping, **NOT a global ban on deleting other models**.

**Source committed, real DGX execution NOT RUN:** `runtimes/service-policy.json.retired_containers.targets` now registers exact names, original test provenance labels/known IDs, observed vLLM image, immutable local receipt paths, and cleanup lifecycle policy. `scripts/manager/manifest_cleanup.py` implements read-only `plan` (matches live canonical 27B Native Tools promoted recipe/benchmark, exact stopped target IDs, labels, read-only HF cache, result/evidence history, no foreign GPU owners), fresh exact SHA + two independent TTY approvals, and deletion of **only these two stopped Docker containers** through `docker rm`; no images, checkpoint files, HF cache, historical P3 receipts, or benchmarks deleted. A private immutable attempt/result receipt blocks blind partial-retry. Post `status` requires actual target absence plus live canonical service verification. Routed through **`./wizard.sh service manager cleanup --plan` / `--execute` / `--status`** and interactive Wizard → service menu → cleanup. `scripts/manager/service_manifest.py` read-only inventory now exposes `managed_container_lifecycle`, `retired_container_inventory`, manifest names, distinguishing desired policy from Docker observed state. Existing numeric service-menu shortcuts are preserved. Testing is source-only Fake-DGX, not real removal.

**Actual before-state:** user supplied second live canonical recipe migration `COMMITTED` all Native Tools/SSE, three-request benchmark v2 PASS (mean E2E 10.957 tok/s; TTFT P50 0.165412s), new container `qwen38-27b` and independent `LIVE_CANONICAL_27B_NATIVE_TOOLS_VERIFIED`, `LIVE_SERVICE_VERIFIED`, old backup container deleted. User separately confirmed **Open WebUI Native success**. Stopped forensic containers remain present until operator executes new cleanup plan; also stopped `qwen38-flash`. Keep stopped Flash as currently unselected; it remains deletable separately by a future appropriately scoped lifecycle action. P3-C historical PASS/closed, normal Wizard repeatable switch/reinstall recipe-diff code remains distinct unfinished work; old P3 IDs must not be recycled as live authority. P8 conditional migration ticket remains INACTIVE because second canonical recipe migration succeeded.

**New operator next actions (no automatic Docker mutation on Git pull):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager inventory --json
./wizard.sh service manager cleanup --plan
```
Require exact two stopped target names, `READY_FOR_MANIFEST_RETIRED_CONTAINER_CLEANUP_APPROVAL`, `issues=[]`. Only then separate TTY `./wizard.sh service manager cleanup --execute` with new SHA and `I_APPROVE_MANIFEST_TWO_STOPPED_CONTAINERS_ONLY` / `I_CONFIRM_ACTIVE_27B_AND_ALL_MODEL_EVIDENCE_PRESERVED`. Finally `./wizard.sh service manager cleanup --status`, `./wizard.sh service manager status --json`, `docker ps -a`. No claim of deletion until actual DGX stdout. If BLOCKED, inspect source provenance rather than bypassing.

Permanent runbook: `docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-20261107.md`. User specifically rejects a hard-coded “canonical 27B and Flash can never be deleted” policy. Keep global uninstall ability possible; current cleanup's exact two-target allowlist is intentionally scoped.

---

## 2026-11-07 — Immediate DGX v2 RETRY authorized as next operator action; P8 contingency and P3-C closure boundary

User instruction: **Proceed to second REAL DGX canonical NVIDIA 27B Native Tools recipe migration test immediately after Git Pull and guarded read-only recovery audit**. User expressly does not require waiting for Fake-DGX CI. This is NOT permission to bypass existing irreversible attempt markers or TTY approval. Previously consumed first migration plan **01702fa1b0901a0dce7517ccbaee133fc253058a1c07abe63bc00c42bec52a15** returned REAL `FAIL_RESTORED`, `native_tools_pass=true`, `benchmark_pass=false`, and `original_restored=true`; independent current Docker/API postcheck has not been furnished. No second DGX run result exists yet.

External GitHub source comparison: [MiaAI-Lab start.sh](https://github.com/MiaAI-Lab/Qwen3.8-27B-DGX-Spark-RTX-6000/blob/main/start.sh) and [styles01 27B recipe](https://github.com/styles01/sparkrun-recipes/blob/main/recipes/qwen-38-27b.yaml) use **different unsloth checkpoint, compressed-tensors, patched/nightly image, sometimes MTP and FP8 KV**. These are **NOT** substituted for our proven pinned NVIDIA nv-community `nvidia/Qwen3.8-27B-NVFP4` / vLLM 0.32.0 `modelopt_mixed` container. `qwen3_coder` / `qwen3` / explicit per-request non-thinking mode are supported by both and already real-DGX tool/SSE tested. Additional [CloudRift vLLM 0.32.0 NVFP4](https://github.com/cloudrift-ai/emmy/blob/main/recipes/Qwen3.8-27B-NVFP4/RESULTS.md) supports parser/benchmark separation but is RTX5090, not GB10. Detailed analysis: `docs/P2-27B-EXTERNAL-RECIPE-RESEARCH-20261107.md`.

**NEW v2 source-only request profile:** `recipes/qwen38-27b.runtime.json` pins `benchmark.version=p2-27b-native-tools-canonical-benchmark-v2`, 3 sequential SSE requests, output cap **128 tokens**, `chat_template_kwargs={"enable_thinking": false}`, temperature 0 and seed 1234, with no literal informal `/no_think` suffix, preserving historical benchmark v1 and production thinking capability. The migration executor verifies benchmark-v2 version, prompt settings, samples and throughput before replacement/promotion; stores complete per-sample diagnostics BEFORE any fail-restore. No claims of successful v2 throughput until actual DGX stdout.

**IMMEDIATE DGX workflow:** `git pull --ff-only origin feature/recipe-wizard-handoff` → current service status/ordinary journal → `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --audit-failure`; require `PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY` and no issues; then manual TTY `--reconcile` (exact old failed SHA + phrase), `--plan` (new SHA, v2 benchmark profile, no issues), and only under NEW downtime and backup-deletion acknowledgements `--execute`. `--status` plus service status after test. If the audit is blocked, STOP; no manual bypass, deletion, old P3-C replay or uncontrolled third execution. GitHub CI is not a prerequisite per the user, but source itself is not a real DGX test.

**Explicit contingency:** IF the second **executed** DGX migration FAILS again, move remaining P2/P3-related canonical Native Tools recipe+benchmark rollout to **P8**, do not continue repeated P2/P3 tests now. Keep P1/P2 original baseline and P3-A/B/C historical real PASS immutable. **P3-C historical Stage-C was already completed at 2026-11-07 10:19:39 KST with `P3_C_PASS_FINAL_27B_ACTIVE`**. Finalize/ARCHIVE this stage without rerunning it; unrelated interactive Wizard production release stays OFF. Conditional tracker: `docs/P8-27B-NATIVE-RECIPE-DEFER-IF-V2-FAIL-20261107.md` is **INACTIVE/PENDING** until actual second result; DO NOT falsely mark P8 active before new output. If second FULL `COMMITTED` with benchmark and backup cleanup PASS, keep P8 inactive. Any `RECOVERY_FAILED` requires physical recovery first, regardless of backlog.

---

## 2026-11-07 — REAL DGX canonical Native Tools migration 1st attempt FAIL_RESTORED; BENCHMARK diagnostic and reconciliation fix

**Most recent actual DGX operator output:** TTY-approved `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --execute` consumed fresh plan `01702fa1b0901a0dce7517ccbaee133fc253058a1c07abe63bc00c42bec52a15`. JSON returned `status=FAIL_RESTORED`, `executed=true`, `native_tools_pass=true`, `benchmark_pass=false`, `benchmark_promoted=false`, `backup_container_deleted=false`, `original_restored=true`, `issues=["MIGRATION_ERROR_NEW_CANONICAL_BENCHMARK_NOT_QUALIFIED"]`. **Actual service independently checked AFTER this failure: NOT YET provided.** This is a real DGX Native Tools pass followed by an unsuccessful new 3-sample performance acceptance test and attempted original restore, **NOT a successful canonical migration**. Do not delete containers/cache/benchmark receipts or re-run the used SHA.

**Root-cause evidence boundary:** In the initial migration code, `p2_27b_benchmark.measure()` returned a structured measurement dictionary, then the caller rejected its acceptance criteria. The caller discarded `samples` and `metrics` before writing the immutable failure report. Therefore the actual failed sample or reason **cannot be reconstructed from the provided output**; not evidence of GPU/model inference failure. The benchmark also used legacy `/no_think` prompt text rather than explicit `chat_template_kwargs={"enable_thinking":False}` which the **successful Native Tools probe uses**. This is a plausible cause but NOT established. Avoid falsely claiming actual latency/TPS.

**Source remediation:** `scripts/manager/p2_27b_benchmark.py` now accepts opt-in pinned nonthinking kwargs while preserving historical defaults and captures per-sample `usage_reported`, `content_observed`, `reasoning_observed`, `stream_finish_reason`, exact failure reason codes, TTFT, tokens and sampled metrics (no generated text). `scripts/manager/p2_27b_recipe_migration.py` opts in to explicit `enable_thinking=false` and writes private immutable `benchmark-observed-<NEW SHA>.json` plus a `BENCHMARK_MEASURED` journal event **before** checking pass/rolling back. Result now includes `benchmark_diagnostics` even on `FAIL_RESTORED`. A `finish_reason=length` at the intended 64-token benchmark cap is recorded, **not automatically deemed a failure**. Do not loosen actual benchmark eligibility for missing usage, TTFT, SSE completion or generated tokens.

**Safe subsequent run protection:** Existing `attempt-<oldSHA>.json` remains immutable; source does NOT silently bypass it. Added `--audit-failure` read-only verification of exact one prior failed result, seven-event hash chain ending RESTORED, original P3 container ID running+API ready, stopped/owned failed candidate, Flash/variant stopped, original ordinary journal clean and no promoted benchmark. If and ONLY IF audit returns `PRIOR_BENCH_FAIL_ROLLBACK_VERIFIED_READ_ONLY` / issues empty, operator may separately run interactive `--reconcile` and type exact prior used SHA plus `I_REVIEWED_27B_BENCHMARK_FAILURE_AND_RESTORED_SERVICE`; this writes **only a private reconciliation receipt**, never touches Docker. Then `--plan` issues **new distinct SHA** bound to prior reconciliation (also checks fresh current identity, recipe, cache and P3 lineage), and `--execute` STILL requires new TTY SHA, downtime and backup-deletion consent for any second attempt. Previously failed new container is **preserved**; new failed-container name is unique per NEW plan. Two unverified failures or state/evidence drift remain BLOCKED. **No next DGX attempt has been observed.**

**DGX Pull/read-only instructions (NO service mutation):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
docker ps -a --filter name=qwen38-27b --format 'table {{.Names}}\t{{.Status}}'
bash scripts/temporary/p2-27b-native-recipe-migrate.sh --audit-failure
```
If audit is BLOCKED, inspect actual Docker and private `~/.local/state/blazux-wizard/27b-recipe-migration/` rather than clearing markers. Only after reviewing evidence can operator choose interactive `--reconcile`, then `--plan`, then separately authorized live `--execute`. Any new migration result must be grounded in real DGX output; GitHub source-only CI is not DGX acceptance. Preserve original 27B model, HF cache, vLLM image, original P3 A/B/C and 14-event ordinary journal. Main Wizard production flag remains OFF; Draft PR #1 not merged.

---

## LATEST 2026-11-07 — User selects SINGLE canonical 27B recipe replacement (not variant switching); benchmark then delete verified old backup ONLY after PASS

Supersedes previous proposed persistent `qwen38-27b`↔`qwen38-27b-native-tools-v1` service-switch feature: user clarified to change **original 27B recipe**, stop existing service, **recreate the same canonical `qwen38-27b` name** with already DGX-proven native-tool flags, run NEW bounded benchmark, **replace latest active benchmark result**, then **remove the exact old backup Docker container only when every test PASSES**. Old benchmark evidence, model images, checkpoint cache and P3 A/B/C records must NOT be deleted/re-written. The separate unqualified persistent-switch prototype was removed from branch (not deployed). Native Tools 1-shot real DGX `PASS_RESTORED` remains prior proof and trial variant `qwen38-27b-native-tools-v1` remains stopped; its 9 chained events and receipt preserved.

**New Git source (NOT YET RUN on DGX):** `recipes/qwen38-27b.runtime.json` (single pinned 27B canonical source, vLLM 0.32.0, exact local image `sha256:9479fc92...`, revision `482ca0f...`, Jinja SHA `c3cf9e34...`, native-parser flags), desired `runtimes/service-policy.json` registration, `scripts/manager/p2_27b_recipe_migration.py` (read-only plan, independent exact-TTY execution, backup rename, canonical recreation, ordinary chat/structured tools/stream/SSE 3-sample fresh benchmark, private immutable receipts, atomic latest benchmark pointer, remove verified stopped old container only after all PASS, restore pre-change on precommit failure), and `scripts/temporary/p2-27b-native-recipe-migrate.sh` (`--plan`, `--execute`, `--status`). Permanent runbook: [docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md). **Per user request, do NOT block Git Pull on Fake-DGX CI**, but no source change alone authorizes downtime. User runs `git pull --ff-only` and `--plan` first; `--execute` still needs new independently accepted SHA + downtime acknowledgement + explicit verified-backup-deletion acknowledgement. Pull does not mutate Docker.

**CAUTION:** Original P3 receipts pin the PRE-MIGRATION 27B Docker ID. When user explicitly approves deletion after successful promotion, that old ID becomes historic, NOT active. Existing generic operating Flash↔27B code must remain fail-closed until later lineage-aware revision; ordinary service status sees canonical `qwen38-27b` by name but doesn't check tool flags, thus use new `--status` check to verify post migration actual flags / benchmark. Do NOT rewrite historical P3 receipts or indiscriminately delete caches or Docker images. Model stays `qwen3.8-27b` at `:8000`, ONE_ACTIVE_MODEL_ONLY, no SGLang.

**Current real DGX:** user most recently showed `qwen38-27b-native-tools-v1` `Exited (0)`, original `qwen38-27b` operating, 9 one-shot events, and validated `PASS_RESTORED`. **Canonical recipe migration, its new benchmark, backup cleanup, and new `--status` PASS are NOT_RUN.** The new action runs real Docker only on operator-approved TTY, not via connector or Fake-DGX. If `--plan` BLOCKED or execute reports `FAIL_RESTORED`, `RECOVERY_FAILED`, `COMMITTED_CLEANUP_PENDING`, stop and reconcile; never retry blindly.

---

## LATEST REAL DGX — 2026-11-07 P2-FINAL native tool_calls + streaming PASS_RESTORED

**Actual operator-provided DGX run, not CPU simulation:** fresh TTY-approved `scripts/temporary/p2-final-native-tools-operator.sh --execute` completed with `status=PASS_RESTORED`, `trial=PASS`, `structured_tool_call=true`, `tool_result_continuation=true`, `streamed_tool_call=true`, `structured_probe_status=LOCAL_STRUCTURED_TOOL_CYCLE_PASS`, `stream_probe_status=LOCAL_STREAMED_TOOL_CALL_PASS`, `issues=[]`, `original_restored=true` / `restoration.status=RESTORED`. Operator then independently verified original `qwen38-27b` serving sole API ID `qwen3.8-27b` at `:8000`, `LIVE_SERVICE_VERIFIED`, `issues=[]`. Ordinary operating journal still `VERIFIED`/`COMMITTED`, **14 events**, `issues=[]`, last event hash `ece2b07f40d972761565b95c3c9b99552876079783af4e4aa4e2db5053a5724e`. Docker running list contains original 27B, Open WebUI (healthy), Portainer; no second running model shown.

**Qualification update:** The actual bounded 27B Native Tools `tool_choice=auto` + synthetic tool-result continuation + SSE + original restoration **subgate is now REAL PASS**. Earlier “not run” / original API HTTP-400 historical entries below remain chronological evidence, **not current milestone status**. This run does NOT verify real Open WebUI Native end-to-end, production Wizard native-tools switching, crash/forced-error rollback, comprehensive generated reasoning leakage, physical GPU process exclusivity or host port process ownership. The ordinary status fields `manifest_status=OBSERVED_UNQUALIFIED`, `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `operations_enabled=false` remain unqualified scopes rather than observed conflicts. Do not declare complete P2-FINAL production acceptance; ordinary Wizard `PRODUCTION_EXECUTION_RELEASED=False`, old P3-C immutable, original containers/images/HF cache retained, vLLM 0.32, port 8000, ONE_ACTIVE_MODEL_ONLY. **No repeat trial with the same SHA**; private attempt marker blocks blind repetition.

**Evidence detail and remaining acceptance gates:** [docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md](../docs/P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md). Next: private one-shot evidence/stopped variant inventory audit (read-only); design safe long-lived variant-aware service identity and production rollout (separately approved); live Open WebUI Native application end-to-end only during an independently approved maintenance period. No new service downtime authorized by this report.

---

## 2026-11-07 — User-authorized P2-FINAL Native Tools one-shot DGX trial SOURCE delivered; RUN NOT YET

**Actual real DGX prerequisites confirmed by operator:** vLLM 0.32.0 has registered `qwen3_coder` and `qwen3`; pinned NVIDIA revision `482ca0f3832238542f8f5295dde86b5f22711d80` Jinja SHA256 `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041` rendered all five CPU synthetic cases successfully on DGX: tool_prompt, tool_result, non_tool_prompt, no_thinking, thinking_prompt. Result `CPU_TEMPLATE_RENDER_VALIDATED_ONLY`, issues empty. User then requested to **proceed with actual server native `tool_calls` testing** and explicitly directed delivery of a **temporary committed script** for DGX `git pull`. No new live result yet.

**Implemented source-only + Fake-DGX PASS:** tracked `scripts/temporary/p2-final-native-tools-operator.sh` dispatches to `scripts.manager.p2_27b_tool_live_trial` with `--plan` (default, read-only) or `--execute` (TTY only). The new one-shot executor is **separate** from historical P3 and ordinary Wizard and uses fresh 64hex SHA plus two independent per-target downtime acknowledgements, operating and trial locks, independent private immutable attempt marker + phased event files, preserved original P3 lineage/image/port 8000, exact pinned NVIDIA tool-enabled argv, stop original `qwen38-27b` BEFORE creating uniquely named `qwen38-27b-native-tools-v1`, bounded structured `tool_choice=auto`, tool-result continuation and streaming probes, then **ALWAYS attempt to stop variant and restore/verify original 27B even after PASS**. One-shot variant remains stopped/preserved, original P3/operational receipts remain untouched. An interrupted/previous trial is blocked pending manual reconciliation. It does not set `PRODUCTION_EXECUTION_RELEASED` or enable normal Wizard variant switching; no service manifest migration. A host power failure, SIGKILL, OOM, Docker problem may defeat recovery and requires manual reconciliation. Do not claim live GPU acceptance from CI.

**Fake-DGX CI:** [Recipe manifest CPU run 42343502949](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42343502949) succeeded after fixing the empty `docker ps` fake fixture (the failed run 42343432619 was a fixture-only issue). New shell-wrapper tests also passed in [run 42343608738](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42343608738). These checks run NO real Docker/GPU. **No actual trial or downtime was executed** by source commit.

**Next operator steps on DGX:** `git status -sb`, `git pull --ff-only origin feature/recipe-wizard-handoff`, `bash scripts/temporary/p2-final-native-tools-operator.sh --plan`. Require `READY_FOR_INDEPENDENT_NATIVE_TOOLS_TRIAL_APPROVAL`, issues empty, original 27B currently live, original restoration required. Then the user may choose to run `bash scripts/temporary/p2-final-native-tools-operator.sh --execute` in a real TTY during a separately accepted maintenance interruption, type the new SHA printed during execute and exact two independent strings `I_ACCEPT_P2_FINAL_NATIVE_TOOLS_DOWNTIME` and `I_APPROVE_DISTINCT_27B_NATIVE_TOOLS_V1`. The result may be PASS_RESTORED / PARTIAL_RESTORED / FAIL_RESTORED / RECOVERY_FAILED; even PASS_RESTORED only validates trial probes and original restoration, not Open WebUI Native/ongoing service switch. After trial independently inspect `./wizard.sh service manager status --json` and `python3 -m scripts.manager.operational_audit --json`. **NEVER blindly retry or delete original containers/caches/receipts**; older P3 stages remain immutable, port 8000 and ONE_ACTIVE_MODEL_ONLY always enforced.

**Permanent runbook:** `docs/P2-FINAL-NATIVE-TOOLS-ONE-SHOT-OPERATOR-20261107.md`. PR #1 remains Draft/open/unmerged. Main Wizard production switch release remains OFF.

---

## 2026-11-07 — REAL DGX NVIDIA 27B pinned-template CPU rendering PASS (P2-FINAL subgate CLOSED)

Operator fast-forwarded `1295f30..a137e27` and ran `bash scripts/serve_27b.sh --tools-template-audit` on the actual DGX Spark. Actual **operator-provided** JSON (do not confuse with GitHub CI) reported `status=CPU_TEMPLATE_RENDER_VALIDATED_ONLY`, `issues=[]`, all five markers **TRUE**: `tool_prompt_rendered`, `tool_result_rendered`, `non_tool_prompt_rendered`, `no_thinking_rendered`, `thinking_prompt_rendered`. `tokenizer_auto_template_present=true`, local Transformers `5.19.0`, expected and observed SHA-256 exactly `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`, pinned NVIDIA `chat_template.jinja` revision `482ca0f3832238542f8f5295dde86b5f22711d80`. Prior real DGX registry import audit independently confirmed vLLM `0.32.0`, tool `qwen3_coder` and reasoning `qwen3` registered.

**Evidence boundary:** This closes the **CPU parser-registry presence + pinned tokenizer/Jinja prompt-render** subgates, not actual `--enable-auto-tool-choice` serving, structured tool_calls, streaming, reasoning separation in generated API output or Open WebUI Native, and not production cutover acceptance. Original `qwen38-27b` remains the most recently observed active model, original `qwen38-flash` preserved, API :8000, `ONE_ACTIVE_MODEL_ONLY`, HF cache, original Docker IDs and old P2/P3/P3-C plus ordinary-switch receipts/journal untouched. This last test reported `docker_state_mutated=false`, `gpu_inference_executed=false`, `execution_enabled=false`, `approval_accepted=false`, `plan_id=null`.

**Next development:** Implement and Fake-DGX-test distinct **variant-aware service inventory/identity policy, crash-safe independent journal/rollback and separate operator approval** before any live Native Tools cutover. Keep original service manifest semantics and `PRODUCTION_EXECUTION_RELEASED=False` until explicitly reviewed. The existing Fake-DGX simulation is NOT a real executor. No operator downtime consent is given by this CPU PASS; DO NOT run the inert Docker candidate, manually stop the original or replay P3. Draft PR #1 remains open/unmerged.

---

## 2026-11-07 — Real DGX pinned Qwen3.8 Jinja: 3/4 render checks TRUE; no-thinking predicate FIXED in source

After fast-forward on the real DGX, the non-mutating `bash scripts/serve_27b.sh --tools-template-audit` returned `BLOCKED` with only `TEMPLATE_RENDER_FAILED_NO_THINKING_RENDERED` and aggregate `CPU_TEMPLATE_NOT_VALIDATED`. **All actual positive render observations:** `tool_prompt_rendered=true`, `tool_result_rendered=true`, `non_tool_prompt_rendered=true`, `template_present=true`, `tokenizer_auto_template_present=true`, `transformers_version=5.19.0`, pinned NVIDIA template SHA-256 `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`. Exact revision remains `482ca0f3832238542f8f5295dde86b5f22711d80`. Execution flags `docker_state_mutated=false`, `gpu_inference_executed=false`, `execution_enabled=false`.

**Root cause: source diagnostic false negative, not an observed parser, tokenizer or Jinja failure.** The prior test mistakenly asserted that `enable_thinking=false` means no literal `<think>` tags in the **rendered prompt**. The actual [official Qwen3.8-27B model Jinja template](https://huggingface.co/Qwen/Qwen3.8-27B/blob/main/chat_template.jinja) intentionally pre-fills a *closed, empty* thinking region `<|im_start|>assistant\\n<think>\\n\\n</think>\\n\\n` in non-thinking mode. In thinking-enabled mode it opens `<|im_start|>assistant\\n<think>\\n`. This is prompt formatting, **not model-generated reasoning or a leak**. No modification to the original NVIDIA Jinja is warranted.

**Source remediation:** fixed `p2_27b_tool_template_audit.py` to check both exact suffixes (reported as `no_thinking_rendered`, `thinking_prompt_rendered`), and pin the actual observed NVIDIA template SHA-256; a hash mismatch blocks. Added CPU regressions for both correct prompt suffix contracts and failure cases, SHA content pin, syntax compile, and safe Docker failure details. `--tools-template-audit` remains CPU-only and read-only in the original `qwen38-27b`; it does not launch the source-only `qwen38-27b-native-tools-v1` variant. Original P2/P3-C/ordinary-switch receipts, original Docker identity, GPU service port 8000, HF cache, and Flash fallback are not changed. This is **not live Native Tool Calling acceptance**. The real corrected audit has **NOT_RUN** until operator fast-forwards and runs it. Protected variant executor, journal, approval and rollback gates remain unimplemented; P2-FINAL NOT_QUALIFIED; main Wizard production OFF, PR #1 Draft/unmerged.

**Next non-disruptive operator experiment only after CI success:** `git pull --ff-only origin feature/recipe-wizard-handoff`, then `bash scripts/serve_27b.sh --tools-template-audit`. Expect five true fields including `thinking_prompt_rendered`, `no_thinking_rendered`, and `status=CPU_TEMPLATE_RENDER_VALIDATED_ONLY` provided the pinned runtime template is identical; actual output must still be checked before claiming PASS. Do not `docker run` candidate or execute `--tools-stream-probe` against the unqualified original.

---

## 2026-11-07 — DGX pinned Jinja CPU experiment: initial BLOCKED due embedded diagnostic Python syntax; corrected source + CI regression

Operator fast-forwarded to `7343cdf` and ran `bash scripts/serve_27b.sh --tools-template-audit` on real DGX. Actual output: `status=BLOCKED`, `docker_exec_returncode=1`, `issues=["DOCKER_EXEC_CPU_PROBE_NONZERO_EXIT"]`, `docker_state_mutated=false`, `gpu_inference_executed=false`, `execution_enabled=false`. Prior implementation suppressed captured `stderr`, so initial output did not disclose the root cause. **Do NOT classify this as vLLM, model, GPU, tokenizer or Jinja incompatibility.**

Source investigation identified a Python `SyntaxError` in the multiline `CPU_PROBE` injected by `scripts/manager/p2_27b_tool_template_audit.py`: the synthetic assistant tool-cycle message had a missing closing `}` after `tool_calls`. A new CPU regression `ast.parse(mod.CPU_PROBE)`/ `compile` reproduced `SyntaxError: closing parenthesis ']' does not match opening parenthesis '{' on line 78` in Actions run [42341080267](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42341080267) (expected failure during remediation), preventing silent re-release. The tool definitions and synthetic assistant tool-cycle are now rewritten with explicit balanced nesting. The source also corrects the no-thinking condition: `enable_thinking=false` must not be assumed to render literal `<think>\n\n</think>`. Structured inner JSON error details, bounded redacted last stderr line and injection process return code are now surfaced for genuine runtime errors; no raw traceback or private prompt bodies are published to Git.

**Next operator command ONLY after new green CPU CI and clean fast-forward:**

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/serve_27b.sh --tools-template-audit
```

This is a CPU-only read-only `docker exec` into **existing** `qwen38-27b`, with no service lifecycle changes or actual GPU inference. Successful synthetic rendering is not native tool inference, parser+template end-to-end qualification, rollback acceptance or downtime consent. Even if a tokenizer/Jinja render issue is identified after syntax repair, investigate the reported error without installing packages or switching models. Preserve source/Flash original containers/images, API :8000, pinned HF cache, all P2/P3/P3-C receipts/journal. P2-FINAL remains OPEN and Wizard production flag remains OFF; PR #1 stays Draft/unmerged.

---

## 2026-11-07 — Actual DGX parser registry PASS; pinned NVIDIA Jinja solution / CPU-only experiment (NOT LIVE ACCEPTED)

The DGX operator ran a **non-mutating import audit inside existing `qwen38-27b`** and reported `vllm_version=0.32.0`, tool parser `qwen3_coder` = `vllm.tool_parsers.qwen3_engine_tool_parser.Qwen3EngineToolParser`, reasoning parser `qwen3` = `vllm.parser.engine.adapters.Qwen3ParserReasoningAdapter`, all **FOUND**. The pinned snapshot's `tokenizer_config.json` exists but its inline `chat_template` is `null`. This is **not** evidence of an absent effective template.

**Root-cause hypothesis and concrete fix candidate:** The **same exact pinned NVIDIA revision** `482ca0f3832238542f8f5295dde86b5f22711d80` contains a *separate* `chat_template.jinja` (8.95 kB), with Qwen XML `<tool_call><function=...><parameter=...>` prompting, `<tool_response>` continuation and `enable_thinking=false`. This was independently checked at [NVIDIA pinned revision](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/tree/482ca0f3832238542f8f5295dde86b5f22711d80) and [pinned Jinja source](https://huggingface.co/nvidia/Qwen3.8-27B-NVFP4/blob/482ca0f3832238542f8f5295dde86b5f22711d80/chat_template.jinja). [vLLM 0.32 Online Serving documentation](https://docs.vllm.ai/en/v0.32.0/serving/online_serving/) explicitly supports `--chat-template path/to/file.jinja`. The `qwen3_coder` and `qwen3` flags match the [upstream Qwen3.8 recipe](https://github.com/vllm-project/recipes/blob/main/models/Qwen/Qwen3.8-27B.yaml) and the DGX import audit.

The distinct **source-only candidate** `qwen38-27b-native-tools-v1` now appends `--chat-template /hf/hub/models--nvidia--Qwen3.8-27B-NVFP4/snapshots/482ca0f3832238542f8f5295dde86b5f22711d80/chat_template.jinja` before official opt-in parser flags. Original `qwen38-27b` `Config.Cmd`, `_candidate_argv(...,tool_calling=False)`, source image, all containers, API :8000 and every historical P2/P3 receipt remain unchanged. **Do not run the inert command** or launch a second GPU process.

**Next non-disruptive DGX experiment (after clean git pull):**

```bash
bash scripts/serve_27b.sh --tools-template-audit
```

Runs **one bounded 90s** `docker exec -i` Python `-B` in the existing original container with `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`, `CUDA_VISIBLE_DEVICES=-1` and `PYTHONDONTWRITEBYTECODE=1`; no model weights, inference API, Docker lifecycle, host port or cache write. Reads pinned Jinja and reports its SHA, tokenizer auto-detection and whether synthetic tool-choice, no-thinking, non-tool chat and tool-result continuation prompts render with local Transformers `AutoTokenizer`. It **does not** contact another model, show prompt bodies, or make external tool calls. `CPU_TEMPLATE_RENDER_VALIDATED_ONLY` is **not P2-FINAL PASS**. If missing file/unsupported tokenizer/render fails, report the diagnostic and fix with a **pinned, provenance-preserving** source change; no floating updates, SGLang or replacement tokenizer downloads.

Outstanding: actual pinned template file on operator DGX not yet independently shown; runtime tokenizer/Jinja compatibility not yet tested; variant service integration, crash-safe journal/rollback and *new distinct downtime consent* not implemented; actual native tool calling, streaming, reasoning isolation and Open WebUI Native not qualified. Main Wizard `PRODUCTION_EXECUTION_RELEASED=False`, PR #1 remains Draft/unmerged, old P3-C PASS immutable.

---

## 2026-11-07 — P2-FINAL Fake-DGX cutover state-machine simulation added; 722 CPU PASS

Added `scripts/manager/p2_27b_tool_cutover_simulation.py` and `tests/test_p2_27b_tool_cutover_simulation_cpu.py`: a deliberately **Fake-DGX-only**, injected-adapter transaction state machine covering strict variant/source/fallback identity, domain-separated expiring simulated approval, two acknowledgements, lock/prior-journal refusal, stop original→port free→no GPU overlap→start separate variant→check tools/API→preserve original, and failure rollback/uncertainty. Its results are named `SIMULATED_*`, `executed_on_real_dgx=false`; there is NO live Docker adapter, CLI execute route, persistent journal, or production release flag. Simulated approvals must NEVER be treated as real operator consent.

Source code SHA `fe4e6b01c98c9244787a5bb8e034ca81d88bba08` passed GitHub Actions [42339247960](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42339247960): **722/722 offline CPU tests PASS, 34 groups**. This supersedes the earlier 706-test source validation. No DGX service, current original 27B Docker config, HF cache or immutable P3-C was changed. **P2-FINAL Native Tool Calling remains NOT_QUALIFIED** pending parser/image audit, real variant-aware executor/journal/rollback implementation, independent downtime consent, actual structured/streaming/reasoning/WebUI tests. Main Wizard release remains OFF.

---

## 2026-11-07 — SOURCE CI independently VERIFIED for protected Native Tools V1

GitHub Actions [Recipe manifest CPU run 42339037935](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42339037935) **SUCCESS** at exact source SHA `695e4b1f6a10825324d66b01695cda6b0ffeb02d`: **706/706 offline CPU tests in 34 groups PASS**, including the new protected identity, ModelOpt, streaming and malformed-request regressions; both intentionally unqualified candidate YAML recipes were confirmed non-launchable. This CI establishes SOURCE/Fake-DGX correctness only, not DGX parser availability, Tool Calling WebUI or a tested service rollback. Original 27B runtime and ordinary journal were not touched. The subsequent handoff-only update does not alter verified runtime code or CI workflow.

---

## LATEST NEXT ACTIONS 2026-11-07 — after source-only protected 27B Native Tools V1

1. **CI and source review:** confirm latest feature branch CI for `p2_27b_tool_variant.py`, `p2_27b_tool_streaming.py`, new test suites, intentionally invalid V1 YAML and shell CLI. GitHub CPU PASS is not DGX qualification.
2. **Read-only DGX audit (optional operator run):** after clean `git pull --ff-only`, use `--tools-profile` and `--tools-variant-plan` (exit 3 by design). Preserve original 27B/Flash and existing port 8000. Do not invoke SSE probe repeatedly against original HTTP-400 container.
3. **Develop missing executor safely:** validate exact pinned vLLM 0.32 parser/tokenizer; design variant-aware service-policy/manifest, domain-separated expiring execution plan, TTY approvals, stop-old→free :8000→start distinct variant→verify native tools, locked journal, rollback and ambiguous crash-denial. Add Fake-DGX launch/restore/failure and concurrent-service regression tests. **No live execution authorization**.
4. **Later separate real approval:** only after source/CI safety and independent downtime consent, qualify DGX auto Tool Calling + continuation + streaming + reasoning + non-tool chat, Open WebUI Native, original restore and independent final journal. Then decide P2-FINAL PASS. Keep `PRODUCTION_EXECUTION_RELEASED=False` until its own Wizard menu and fault recovery qualifications.
5. Historical P3-C must never be repeated, original image/container/cache/receipts never removed, no auto approval, no PR merge. P4–P7 retain their separate ordering.

Contract: `docs/P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md`.

---

## LATEST NEXT ACTIONS — 2026-11-07: P2-FINAL real HTTP 400, protected tool-enabled variant design required

**P0 — Record closure/evidence, no operation:** newest user-provided `LIVE_SERVICE_VERIFIED` current 27B, journal `VERIFIED/COMMITTED` with **14** events; both real ordinary 27B→Flash and Flash→27B PASS and independently post-checked. Historical P3-C remains FINAL/CLOSED, never re-run. Normal main Wizard is NOT production released and real fault injection/recovery not accepted. Reconfirm current status before any action.

**P1 — P2 last Tool Calling gap:** verified preserved `qwen38-27b` `Config.Cmd` lacks `--enable-auto-tool-choice`, `--tool-call-parser` and `--reasoning-parser`; source opt-in profile has intended `qwen3_coder` / `qwen3`; actual bounded local probe `BLOCKED/LOCAL_API_HTTP_ERROR_400`. **Do not retry repeatedly or pretend Tool Calling works.** Plan separate named, immutable 27B tool-enabled recipe/profile variant on vLLM 0.32, with image/parser support inspection, pinned model & original protected containers, formal single-model :8000 cutover, rollback and private evidence paths. Do NOT reuse the P2 first-boot trial, P3 stage C, or casually recreate `qwen38-27b` (ordinary switching pins its ID/provenance).
 
**P2 — Implement & qualify on source:** profile variant (non-default); safe migration plan and separate authorization/executor contract; offline CPU Fake-DGX tests for parser flags and name/port/image/candidate identity, approval expiry, no parallel GPU, failed launch/rollback, tool `auto`/structured JSON/continuation, streaming chunks, thinking separation, Open WebUI Native expectations. New source/tests/docs commit to existing feature branch, CI green. Obtain actual DGX user approval **before** any stopping, starting, recreating or replacing inference containers, benchmark rerun or Open WebUI service modification.

**P3 — Actual P2-final acceptance only after new consent:** bounded live tool-enabled runtime / Open WebUI Native tools accepted and original model assets retained, evidence for streaming and tool cycle. Only then consider P2-FINAL closed; original P2 and P3-C historic receipts untouched. Normal `./wizard.sh` release gate stays false pending its own menu UX and real failure-recovery acceptance. P4/P5/P6/P7 are deferred.

See `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`, `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`, `docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md`.

---

## NEXT after user P2/P3-C closure decision — 2026-11-07

1. **P3-C historical real DONE/CLOSED**: original Flash→27B one-off actual P3-A/B/C accepted, no additional Stage-C run or receipt editing. Separately, new ordinary 27B→Flash and Flash→27B operators reported PASS; reverse final independent status/audit must still be observed. Last reported active is now 27B.
2. **P2-final Native Tool Calling is the only appended P2 acceptance gate** (prior P2 GPU/benchmark/restore PASS retained). Source vLLM 0.32 Qwen3.8-27B profile `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3` is opt-in, never automatically retrofits original 27B container. See `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.
3. DGX no-downtime read-only + small inference checks: `./wizard.sh service manager status --json`; `python3 -m scripts.manager.operational_audit --json`; `docker inspect qwen38-27b --format '{{json .Config.Cmd}}' | python3 -m json.tool`; `bash scripts/serve_27b.sh --tools-profile`; `bash scripts/serve_27b.sh --tools-probe`. The probe intentionally returns BLOCKED if auto-parser is absent; no need to retry/restart. New source requires clean fast-forward and CPU CI first.
4. Before actual P2-FINAL remediation, design a **distinct pinned tool-enabled 27B recipe/service variant**; do not recreate/delete historical `qwen38-27b`. Qualify parser on vLLM 0.32, tool_call, tool-result continuation, **streaming**, non-tool inference, reasoning separation, Open WebUI Native. Requires independently approved outage/restore risk and a separately reviewed rollback plan. Do not disturb active 27B or port 8000 while creating read-only profile.
5. **Normal everyday Wizard main menu release still OFF**; Fake-DGX CPU and actual trial-only dual direction PASS do NOT alone qualify main TTY menu or failure recovery. No forced recovery test, P3 replay, P4 cleanup, Orcarouter changes or PR merge without independent approval.

---

## LATEST NEXT — 2026-11-07: first ordinary switch + independent postcheck PASS; reverse source READY only

- [x] Actual DGX ordinary `27b→flash-next`: operator's `PASS` and private receipt plus **separate after-action** `LIVE_SERVICE_VERIFIED` for sole `qwen3.8-flash-next`, `operational_audit=VERIFIED/COMMITTED/7 events`.
- [x] Reverse `flash-next→27b` **READ-ONLY** preflight: `READY_FOR_SEPARATE_TRIAL_APPROVAL`, `issues=[]` (the recorded 276s remaining and SHA expired/rotate according to time; never assume still valid).
- [ ] **Real reverse execution NOT_RUN.** Need new, separately scoped Flash-Next API downtime authorization, fresh `--target 27b --plan --json` and (only when approved) human `--target 27b --execute` with FOUR *new* exact TTY inputs; do not auto-fill, pipe, or reuse first direction's SHA. Successful reverse leaves 27B active, no auto-return.
- [ ] Separately authorize and qualify real error/restore behavior before normal production switch release. `PRODUCTION_EXECUTION_RELEASED=False` continues to protect normal `./wizard.sh` main/model menus; P3 A/B/C remain historical, not to rerun.
- [ ] Preserve private operating/P3 receipts, model containers/image/caches, Portainer/Open WebUI and port 8000. Keep 27B Tool Calling deferred and PR #1 unmerged until independently assessed.

**Next exact safe command (read-only)**: `bash scripts/temporary/operational-switch-acceptance.sh --target 27b --plan --json`, followed by separate operator consideration of the trial. No automatic action authorized merely by this log.

---

## NEXT after REAL DGX ordinary 27B → Flash-Next PASS — 2026-11-07

1. **Record current active model as FLASH-NEXT**: the new actual single-switch `operational acceptance --target flash-next --execute` returned `PASS` and `Observed model: flash-next`. Prior next-actions saying this first direction has NOT_RUN are superseded. P3 A/B/C receipts and operations journal are distinct; do NOT replay P3 stages.
2. **Immediate safe read-only post-check on DGX:** `./wizard.sh service manager status --json`; `python3 -m scripts.manager.operational_audit --json`; `bash scripts/temporary/operational-switch-acceptance.sh --target 27b --plan --json`. Check `LIVE_SERVICE_VERIFIED` with only Flash ID `qwen3.8-flash-next`, journal `VERIFIED` / terminal `COMMITTED`, next fresh plan source `flash-next`→target `27b`, no issues. If output disagrees, stop; no destructive action.
3. **Separate consent still required for reverse direction:** a new operator-approved Flash-Next downtime window and fresh four exact human TTY approvals are needed before `--target 27b --execute`. First plan hash/approval **cannot** be reused. Success would leave 27B active; no automatic toggle or repetition. Do not run merely on instruction to review status.
4. After actual bidirectional trials, verify independently supplied journal/receipt status and still assess real rollback/failure behavior under separately approved conditions. Do not trigger intentional failure on the live DGX without a dedicated controlled test plan.
5. Keep `PRODUCTION_EXECUTION_RELEASED=False` and Draft PR #1 unmerged until acceptance evidence and safety review meet the ordinary menu release gates. Keep Open WebUI Tool Calling, recipe modifications, P4/P5/P6/P7 deferred.

---

## LATEST TOP PRIORITY — Ordinary Wizard source finished; independently approved DGX acceptance is next

1. Verify latest GitHub commit and **green source CPU CI** (Fake-DGX only). `./wizard.sh` main option **4**, model option **6**, `operational guided --target flash-next|27b`, and one-off acceptance `operational acceptance --target ... --plan|--execute` are new and source-wired. Production release gate is intentionally false.
2. Next safe DGX operator step is **READ ONLY**, after clean fast-forward source pull: `./wizard.sh service manager status --json`, `python3 -m scripts.manager.operational_audit --json`, then `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --plan --json`. No stop, GPU start, benchmark or P3 replay in these commands.
3. To complete ACTUAL hardware acceptance, obtain a fresh, independently scoped **27B downtime/possible restore failure** approval. Only then can the DGX human voluntarily run the tracked `--execute` (four independent exact TTY approvals). PASS leaves Flash active. Flash→27B requires **another separate new operator approval**, plan and physical trial. Stop immediately on `RECOVERY_FAILED` / committed uncertainty, no blind retries or state deletion.
4. On supplied actual DGX outputs, review private evidence vs current journal, target chat, post-switch identity and rollback. Only AFTER both real directions and recovery behaviors are independently qualified can the reviewed normal production release gate be enabled. Do not infer DGX acceptance from CI or one-off P3 receipts.
5. Keep **Open WebUI 27B Tool Calling and recipe parser updates deferred**. Later P4 conditional cleanup, P5 Orcarouter, P6 Orcarouter↔27B, P7 proxy/gateway are separate phases. Preserve active 27B, original Flash fallback, HF cache, port 8000, all historical evidence and Draft PR #1.

Primary runbook: `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`.

---

## TOP PRIORITY 2026-11-07 — Resume normal model switching Wizard UX, DEFER Tool Calling

1. Complete GitHub CPU CI for newly wired guided path `wizard/console.py` option 6 / `operational guided --target` / `operational_wizard.py` / `operational_executor.py`. Resolve any regressions before user source pull. Preserve Draft PR #1.
2. Continue executor recovery-hardening source + Fake-DGX failure-injection and journal tests. Keep `PRODUCTION_EXECUTION_RELEASED=False` until independent real DGX acceptance; release flag is **not** a user-configurable toggle.
3. Make guided operator review concise: current/target, port :8000, protected container and model identity, plan expiry, interruption warning, exact independent SHA, target-specific downtime consent, PASS/restored/uncertain outcomes. Current CLI `operational guided --target` and console menu are **REVIEW ONLY**.
4. After all code/recovery gates, separately review a **new downtime approval** and conduct independently approved real DGX ordinary 27B→Flash and Flash→27B trials and failure recovery; never replay historical P3 A/B/C or auto-switch.
5. Only after P3 general recurring switch acceptance, revisit P4 conditional cleanup, P5 Orcarouter, P6 and P7. **Open WebUI 27B Tool Calling and recipe parser configuration intentionally postponed**, despite prior diagnosis.

---

## 2026-11-07 — Current WebUI-vLLM 27B integration issue

- [x] Real DGX 27B default chat/inference PASS; with `chat_template_kwargs.enable_thinking=false`, direct strict `DGX_OK` **PASS**. Distinguish formatting from actual generation.
- [ ] On Open WebUI 27B model only, disable Builtin Tools and attached/chat Tools; retest plain text chat. **Real WebUI outcome NOT_RUN** as of evidence received.
- [ ] Optionally `docker inspect qwen38-27b --format '{{json .Config.Cmd}}' | python3 -m json.tool` (read-only). Real live arguments not yet observed.
- [ ] Source-only test per-model tool parser configuration using pinned vLLM 0.32 and NVIDIA 27B chat template; no parser assumption. Any new native tool-capable container requires a separately approved downtime/rollback plan, not restart of existing preserved container. Full Open WebUI tools and general operating switch NOT_QUALIFIED.
- [ ] Preserve active 27B, Flash fallback assets, historical P3 A/B/C, API port 8000 and Draft PR #1 unmerged. See `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`.

---

## 2026-11-07 — Follow-up after actual DGX 27B curl PASS

- [x] Real DGX 27B health, sole API model ID and actual chat completion **PASS** from operator console. `/v1/models=qwen3.8-27b`, completion model matches, stop finish, vLLM 0.32.0, original source at `05c1968`. Previous `curl smoke NOT_RUN` note is superseded.
- [ ] Investigate **response formatting only**, separately: `content` contains reasoning-like text and `</think>` before `DGX_OK`, `reasoning=null`. Optional non-disruptive per-request `chat_template_kwargs.enable_thinking=false` experiment after reviewing actual Qwen/launcher compatibility. Never edit the live 27B runtime or restart blindly. Updated `FORMAT_DEVIATION` classifier is SOURCE+CPU until independently run on actual DGX.
- [ ] Source-only general switch executable release gates: recovery/crash testing, non-reusable scoped operator consent, integrated Wizard UX and independent approved DGX bidirectional/rollback acceptance. **NOT YET AUTHORIZED**. Do not replay P3 A/B/C or automatically switch models, delete caches, or merge Draft PR.

---

## 2026-11-07 current immediate operator read-only / inference task

- [ ] On *real DGX*, while NVIDIA 27B is still active, pull source only and run `bash scripts/temporary/operational-27b-curl-smoke.sh`. Supply output (health, served ID, completion). It makes **one bounded localhost GPU inference** but does NOT switch/stop/start containers. `LIVE_SERVICE_VERIFIED` alone is not inference proof. Do not claim actual pass before output.
- [ ] Review source-only CPU CI for the new fake-curl tests and Wizard hint. Do not authorize general switch execution from a smoke result.
- [ ] Continue source hardening of the separately guarded general operating switch, crash-recovery fail-closed behavior and guided UX, with **real DGX switching NOT_RUN**. P3-A/B/C are complete and must never be replayed. Draft PR #1 remains unmerged.

---

## 2026-11-07 — NEXT after source-only operating switch implementation

The new ordinary switch PREVIEW and independent guarded executor SOURCE are implemented on the existing branch. **No Wizard execute route and no actual DGX operation were enabled.** Next: (1) confirm the new Fake-DGX executor and preflight CI passes including stop→start, exact identity, rollback success/fail and retry denial; (2) review the new execution contract and identify state machine/lock/recovery limitations; (3) implement a real user-friendly guided review/approval flow only after safety gates and CPU tests qualify, keeping live execution disabled until separately authorized DGX maintenance; (4) run operator-initiated read-only \`./wizard.sh switch flash-next-27b operational --target flash-next --plan --json\` optionally after safe fast-forward pull; (5) request a separately scoped consent before ANY live 27B downtime or repeated switch test. P4 remains conditional, P5 Orcarouter source audit after UX, P6 after P5 GPU qualification, P7 after service/proxy/gateway integration. Do not reuse one-off P3 stage receipts as authorization.

Read latest design: \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`. Retain original 27B active :8000, entire original HF cache, containers/images, original immutable P3 receipts and journals. Draft PR #1 must remain Draft/unmerged.

---

## 2026-11-07 — P3-C SUCCESS; STOP REPEATING P3 STAGES, NEXT WIZARD USABILITY PHASE

**P3-C is now DONE on actual DGX, not just preflight!** Operator's real `--execute` used a newly approved C SHA and both distinct explicit downtime/activation strings; canonical Wizard returned PASS and `active_model=27b`; wrapper `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `issues=[]`, original immutable `stage-c.json` verified. Private report `reports/transitions/flash-next--to--27b/p3-c-operator-20261107T011939Z-5f26a6ff25a2.json`. Flash assets/containers preserved. DO NOT RE-RUN A/B/C, P1/P2 benches, restore Flash, prune models, or change port 8000 as part of this handoff. Preserve running 27B for operational use. Real P1+P2+P3 backend qualification is COMPLETE for the specified bounded scenarios; generic recurring switch and interactive menu acceptance are NOT.

**Next source work only (requires separate scoped UX plan before changing live services):** deliver model-centric, ease-of-use main `./wizard.sh` menu, not exposing internal P1/P2/P3 as default. Recommended interaction: observe and verify current live model; show installed qualified alternative and historical Verify/Benchmark, preview specific exact transition and any clients that will lose service; show clear final confirmation with exact plan/approval value as needed; under the hood invoke the same canonical guarded backend/lock/journal/restore; then independently show FINAL active API/port; private receipts append-only and model-indexed. No silent approval, no automatic target start, no model cache cleanup, no plan SHA reuse. Design robust expiring-plan refresh pre-approval. Add CPU fake-DGX tests for menu navigation/approval/cancellation/post-switch/recovery; actual 27B→Flash and Flash→27B ordinary operating transition must be separately approved and demonstrated only later.

**Architectural status:** P1 interactive guided actions and backend Verify/Benchmark ran real DGX; P2 bounded trial/benchmark and original restore ran; P3-A/B/C original Wizard CLI engine ran; but `wizard/console.py::_stage_actions` currently calls `module.run([selected, "--plan"])` and prints "Execution NOT initiated". Therefore the main UX cannot yet execute a stage and P3 C success does not prove regular model selection-to-switch. Original CLI can start/stop the existing services under approvals; don't conflate it with a user-friendly menu.

Use read-only `./wizard.sh service manager status --json` only if an additional independent live check is wanted. Actual user already supplied post-switch successful independent API status and canonical C receipt. Draft PR #1 still unmerged. After source docs commit, ask operator to ff-pull only when needed; no model operations implied by Git updates.

---

## 2026-11-07 — STAGE-C TIME WINDOW HANDLING: NEXT OPERATOR ACTION

After latest source CI PASS and a clean `git pull --ff-only origin feature/recipe-wizard-handoff`, the operator can run `bash scripts/temporary/p3-stage-c-operator.sh --execute` on actual DGX **only if explicit live Flash-Next downtime consent remains in force**. Current user explicitly authorized Flash-Next stop and final NVIDIA 27B switch earlier. The two attempted `--execute` commands at 10:08:14 and 10:09:30 KST were safely BLOCKED by <=120s remaining; **no dispatch occurred**. Keep original Flash :8000 active until canonical C actually succeeds.

The wrapper now handles the edge of the canonical 10-minute window: if current plan has >=120s remaining, show exact three TTY prompts; if shorter, perform only read-only status + Stage C plan rechecks, bounded <=150 seconds, for a NEW DIFFERENT SHA with >=120s left. No sleep/refresh in `--plan`; no previous SHA, approvals or old C plan are reused. New plan requires unchanged original A/B receipt lineage, pinned preserved 27B, P2 SHA and post-B P1 PASS. Then user must independently type the new full 64-char SHA without brackets and the exact `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Original canonical Wizard rechecks again under its lock; success requires actual 27B API and canonical immutable C receipt. If any BLOCKED/CANCELLED/UNCERTAIN status, HALT and review report, never skip gate or force retries. No PR merge/prune/P1 reruns.

[Updated operator runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md). Both Git-published benchmark summaries are ALREADY VERIFIED against original DGX receipts; no repeat bench needed.

---

## 2026-11-07 — NEXT: STAGE-C FRESH READ-ONLY PLAN; BENCHMARK PUBLICATION ALREADY VERIFIED

**Completed by operator on actual DGX:** `bash scripts/temporary/verify-published-benchmarks.sh` checked private Flash and NVIDIA 27B original JSONs against two Git-tracked metric-only public summaries: both `VERIFIED`, `issues=[]`, `executed=false`; original SHA256s match expected. No need to repeat publication verification or run GPU benchmarks without new reason. Git `benchmarks/published/` entries are now actual source-reconciled and private originals remain local.

**Next operation, non-disruptive:**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p3-stage-c-operator.sh --plan
```
Require `status=READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL`, empty issues, active Flash-Next expected model and original preserved 27B target, P1 post-B evidence PASS, fresh plan SHA and expiry. This must be rechecked because the benchmark verifier does not query current live service.

**DO NOT auto-execute Stage C.** When operator separately and explicitly approves stopping the live Flash API on :8000, `bash scripts/temporary/p3-stage-c-operator.sh --execute` prompts for 3 independently typed literals: NEW SHA **with no brackets**, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, and `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Any stale/changed plan or issue blocks; canonical Wizard alone owns Docker and rollback; final success requires actual live 27B identity and immutable C receipt. Prior C attempt was cancelled before dispatch; no C state or running model change was established by this new benchmark verification log. Do not merge PR #1, delete caches/models/containers, reuse old SHA, or perform unattended downtime.

---

## 2026-11-07 — APPROVAL PROMPT FIX AFTER REAL BRACKETED INPUT

New C operator `confirm()` now displays `Paste exactly <current 64-char SHA> (no brackets; Enter cancels):`, with explicit warning against `[` or `]`. The real previous `[<sha>` submission safely returned CANCELLED/dispatched=false and is NOT a switch. When operator *separately* decides to stop Flash-Next, use a NEW fresh plan, then type only the 64 hex chars and both exact independent acknowledgements; no auto approval. This UX change does not change canonical C, service status or model files. Verify original Git-tracked benchmark summaries first with read-only `bash scripts/temporary/verify-published-benchmarks.sh`.

---

## 2026-11-07 — NEXT: VERIFY PUBLISHED BENCHMARK SUMMARIES READ-ONLY, THEN SEPARATELY APPROVED C

1. Confirm latest GitHub branch and CI, then on operator DGX `git pull --ff-only origin feature/recipe-wizard-handoff`. **Do not** restart GPU containers, merge PR or edit/copy original benchmark receipts.
2. Validate both Git-published metric-only summaries against exact original local JSON with `bash scripts/temporary/verify-published-benchmarks.sh`. Expected TWO `VERIFIED` JSON records and final confirmation. If mismatch, STOP and compare allowlisted fields; do not overwrite source or hide discrepancy. This check is read-only and independent of P3-C.
3. For future bench publications: `python3 -m scripts.manager.benchmark_publication --model <flash-next|27b> --source <private-original-json> --plan`, then operator-review summary (no paths/keys/requests/responses), use hash-approved `--write --approve-sha256 <actual source SHA>` to create **local** untracked Git-ready record, manually review before Git add/commit/push. Never auto-publish private evidence.
4. P3-C prior `--execute` was CANCELLED **before dispatch** because typed SHA included a leading bracket; current observed model Flash-Next, Stage-C NOT_RUN. At separate explicit operator decision, re-run `bash scripts/temporary/p3-stage-c-operator.sh --plan` for fresh status then `--execute` only if accepting live Flash downtime and independently typing the full new SHA **without brackets**, `I_ACCEPT_FLASH_NEXT_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Expired old SHA must never be reused. Do not run Stage A/B or P1 benchmarks again.

Documentation and sanitized entries: `benchmarks/published/README.md`. Original telemetry still stored locally in `~/.local/state/blazux-wizard/`. No model deletion, no automatic Git commit of new future runs, no P3-C execution in source work.

---

## 2026-11-07 — NEXT OPERATOR: FAST-FORWARD PULL + TRACKED STAGE-C PLAN, THEN SEPARATE ACTUAL DOWNTIME CONSENT

Operator has already shown **canonical** `./wizard.sh switch flash-next-27b stage-c --plan --json` READY/issues=[]/P1 gate PASS on actual DGX. Do NOT demand another P1 benchmark/diagnostic, repeat A/B or optional `evidence migrate`. The optional import was cancelled via input `COPY` and copied **0** files; Stage C does not depend on it.

1. Check latest GitHub source HEAD, PR #1 Draft/Unmerged, CPU tests SUCCESS and fast-forward pull in clean `~/Workspace/llm/blazux-orcarouter`.
2. Run exactly **`bash scripts/temporary/p3-stage-c-operator.sh --plan`**. This is the tracked P3-C wrapper's default read-only live preflight. It never stops services. Confirm `READY_FOR_SEPARATE_P3_C_OPERATOR_APPROVAL`, `issues=[]`, source current Flash, target original preserved 27B, P1 evidence PASS, `executed=false` and report path.
3. **STOP for separate operator consent to actually stop the live Flash-Next API on port 8000.** Only if the human explicitly approves C downtime, run `bash scripts/temporary/p3-stage-c-operator.sh --execute`. Three new terminal inputs are mandatory: fresh 64 SHA printed in the new plan prompt, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Must be typed manually, never scripted/auto-piped. A/B or historic C SHA invalid. Expiry/changed live service blocks before core.
4. Wrapper invokes canonical Wizard stage C with exact SHA + downtime ack (NO `--enter-p3` since canonical C requires null), which exclusively owns Docker, original Flash preservation and rollback. Stage C succeeds only if canonical `stage-c.json` and independent 27B live API on :8000 both verified, yielding `P3_C_PASS_FINAL_27B_ACTIVE`. No switch-back after success.
5. If BLOCKED/OPERATOR_REVIEW_REQUIRED/RECOVERY_FAILED, **STOP**, collect appended operator report and original P3 journal/status; no blind retry, no deleting attempt markers/locks/old containers. Do not merge Draft PR, prune caches or start extra models.

[Stage-C controller runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md). Latest real source observations are **read-only only**; C service transfer itself has not yet run.

---

## 2026-11-07 — NEXT DGX OPERATOR READ-ONLY HISTORY AND P3-C PLAN (NO TRANSITION)

1. Confirm latest branch HEAD / GitHub CPU CI; `git pull --ff-only origin feature/recipe-wizard-handoff`. Do not merge PR #1, delete models, or restart/stop any service.
2. In `./wizard.sh` select NVIDIA Flash-Next or NVIDIA 27B → option **4 Past Verify / Benchmark / transitions**, read-only. Or `./wizard.sh evidence list --model flash-next --kind benchmark` and `--model 27b --kind benchmark`. Validate original 2026-11-06 metrics and both A/B transitions visible without GPU activity.
3. Optional separate evidence COPY step: `./wizard.sh evidence migrate --plan` first; if READY with no issues, `./wizard.sh evidence migrate --guided` and type current literal SHA. This copies only JSON report snapshots into Git-ignored project `reports/`, no legacy state/lock/journal relocation. Operator approval is separate; do NOT preapprove the copy.
4. **P3-C NOW THE NEXT POTENTIAL GPU OPERATION** (not dependent on doing optional copy): on same updated DGX run `./wizard.sh switch flash-next-27b stage-c --plan --json` **ONLY**. Report `status`, `issues`, `p1_evidence.status`, `source_model`, `target_model` and current observed IDs. If BLOCKED, STOP. If READY with current exact SHA and valid P1 gate, require a separately scoped decision/Flash-Next downtime approval before building/running C guided operator procedure. P3-C has **not** been authorized or executed.
5. Only after independently approved C may original Flash be stopped and original preserved 27B started on :8000 with actual API identity verification; preserve all HF assets, Flash image and rollback container. No automatic restore on successful final 27B.
   
Source contract: [model history/migration](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md). Actual post-B P1 Verify+Benchmark already PASS; do not repeat inference merely because history or copy code changed. P2/P3 future writer redirection and control-state relocation require separate design/test and are **not** part of this source PR.

---

## 2026-11-07 — CURRENT: P1 VERIFY + BENCHMARK ACTUAL PASS; UX CI + OPERATOR RECHECK

Supersedes previous "P1 POST-B audit then Verify/Benchmark NOT_RUN" instructions. The operator provided immutable actual DGX evidence: original Flash-Next still active and served on :8000, two post-B diagnostics PASS for expected original-own-port rc3; Verify baseline/extended + all probes PASS and separately approved 3-request Benchmark PASS with **37.9527 tok/s, TTFT p50/p95 1.384594/1.779602 sec, latency p50/p95 1.724560/1.813754 sec**. Both original receipts reside under OLD `~/.local/state/blazux-wizard/p1/` and MUST NOT be moved, overwritten or deleted. Source updated to show P3-style exact SHA prompts, remove duplicate action entry, display numeric metrics, use new Git-ignored project-local `reports/models/qwen3.8-flash-next/` for **future** evidence, and dual-read old/new for P3-C evidence qualification.

**Next:** confirm fresh GitHub HEAD + BOTH CI checks (including new operator-UX tests) and Draft PR #1, then operator may `git pull --ff-only origin feature/recipe-wizard-handoff` and inspect the new Wizard UX. No additional real Verify/Benchmark inference is implied by an interface change; an actual re-run would require fresh distinct operator approvals. P3-C downtime/transition remains **separately NOT_AUTHORIZED**, even if the evidence prerequisite checker is now PASS. Never merge PR, clean models or restart/switch services automatically. See [UX/evidence contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

## 2026-11-07 — READY FOR OPERATOR READ-ONLY CHECK (SOURCE CI PASS)

The targeted source audit and P3-B operator metadata fix are implemented; latest source-tested `67ff9cc2e4ece0c89c911513673f7d5d55c98fa4` passed [GitHub CPU CI 42310408411](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42310408411): **501/501 PASS / 23 groups**. PR #1 has a review COMMENT (ID `5808289782`) and remains Draft/Unmerged. No new GPU/DGX execution. After checking the latest HEAD/CI and a clean DGX fast-forward pull, the ONE authorized next read-only action is `bash scripts/temporary/p1-post-b-audit.sh`. PASS with raw own Flash collision evidence is diagnostic readiness only; subsequent P1 Verify and Benchmark need individual approvals. P3-C NOT_AUTHORIZED.

---

## 2026-11-07 — POST-B P1 READ-ONLY AUDIT NEXT; P3-B ACTUAL PASS (supersedes old B execution TODO)

**Completed in actual operator DGX output:** P3-B stage B `P3_B_PASS_FLASH_NEXT_ACTIVE`, canonical `stage-b.json`, original Flash restored and served `qwen3.8-flash-next`, post-B `p1-post-download.sh --inspect-only` preflight PASS/Verify+Benchmark plans READY. P3-A/B must NOT be repeated. Old P3-B operator report was misnamed `p3-a-operator-20261106T223124Z-14861d75.json`; preserve as original evidence.

**Next operator step only AFTER new GitHub CPU CI PASS** (D-016): clean branch and `git pull --ff-only origin feature/recipe-wizard-handoff` in `~/Workspace/llm/blazux-orcarouter`, then run exactly **`bash scripts/temporary/p1-post-b-audit.sh`**. This is source/API/read-only preflight and doctor/inventory RAW rc3 diagnosis: NO GPU inference, benchmark, Docker start/stop or P3-C. New private `~/.local/state/blazux-wizard/p3/p1-diagnostics-<UTC>-<nonce>.json` is append-only, `0600`; existing evidence never overwritten.

**Expected:** `status=PASS`, `issues=[]`, `doctor_exit_code=3`, `inventory_plan_exit_code=3`, `post_b_verify=NOT_RUN`, `post_b_benchmark=NOT_RUN`, `p3_c_authorized=false`. If `BLOCKED`, retain report and stop; do not infer benign collision from exit 3 alone, repeat P3 stages or auto-enter GPU tests. Historical successful P1 numeric results cannot substitute for new post-B samples.

**After successful new diagnostics:** independently propose/obtain new action-specific P1 Verify plan ID and operator approval; after actual successful Verify, separately approve new numeric P1 Benchmark (at least 3 samples, `requests=3,max_tokens=64,seed=1234,concurrency=1` when supported). Only with verified immutable post-B receipts, metrics, timestamps, same Flash revision/image and fresh evidence gate PASS is P3-C eligible for **its own explicit downtime approval**. Do not supply P3-C execute commands earlier.

---

## 2026-11-06 — User approved ONE P3-B shutdown/return; execute only with fresh exact interactive B gates

- [x] Operator separately answered **"승인"** to explicitly scoped P3-B **NVIDIA 27B downtime → preserved Flash-Next restoration** question after actual B-read-only PASS; D-041 records this approval. Original P3-A approval alone was not used.
- [x] Latest tracked P3-B execution wrapper `scripts/temporary/p3-stage-b-operator.sh` is source and CPU CI PASS (489 tests), current branch HEAD at permission check `2f914242ae98ef678477386e1a26b1d6668d717e`. Distinct B exact ACKs required: `I_ACCEPT_27B_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_P3_STAGE_B` and a freshly generated full B plan SHA. CI does not prove any live runtime execution.
- [ ] Operator DGX `git pull --ff-only origin feature/recipe-wizard-handoff`, then **one** `bash scripts/temporary/p3-stage-b-operator.sh --execute`; read current source=27b, target=flash-next and exact immutable container/image. Type all three currently displayed strings, do not reuse expired 17:50 inspection SHA. Port :8000 will experience downtime; on BLOCKED/RECOVERY_FAILED/OPERATOR_REVIEW_REQUIRED stop and report evidence, never retry blindly.
- [ ] After actual `P3_B_PASS_FLASH_NEXT_ACTIVE` and `LIVE_SERVICE_VERIFIED` for `qwen3.8-flash-next`, stop at B. D-034 requires **new post-B P1 Verify + measured Benchmark + rc3 diagnosis** under independent action-specific approval and evidence, then independently authorize C final 27B; no hidden chain.

---

## 2026-11-06 — P3-B DGX preflight PASS; require explicit NEW permission before any live 27B shutdown

- [x] Actual DGX tracked B inspector HEAD `e5d4171`: `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, active API `qwen3.8-27b`, source CID `6d9ede...`, preserved original Flash CID `90f39...`, actual A/P2 provenance complete. Evidence `~/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. `executed=false`, `approval_accepted=false`, no 27B interruption. Old inspection-only plan `7af40f...` expired Nov 6 17:50 KST and must not be reused.
- [x] Stage-B source guard formerly demanded `I_ACCEPT_FLASH_NEXT_DOWNTIME`, semantically wrong for **27B stop**. Updated canonical Wizard core to `I_ACCEPT_27B_DOWNTIME` + independently typed `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`; A/C contracts unchanged. **Source change, no execution.**
- [x] D-016 GitHub tracked `scripts/temporary/p3-stage-b-operator.sh` / Python and CPU fake-DGX tests: default read-only; `--execute` only after separate user scope permission, checks current live 27B + exact A receipts + immutable original Flash + short-lived B plan, separately asks current full SHA, new 27B downtime and B-entry strings; refuses expiry/changed plan before calling guarded Wizard, verifies returned Flash API, records private evidence and NEVER auto-runs P1/C. [489/489 CPU CI PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) on source `59046c4e17a5094f2c80a84025a763c2a767edcb`.
- [ ] Obtain **user's explicit P3-B 27B→Flash-Next downtime approval**. The B inspector PASS and P3-A typed approvals are **not** this approval. Until then leave 27B service live; no `--execute` and no spontaneous P1 test.
- [ ] Only if separately authorized, D-016 fast-forward pull after CI followed by `bash scripts/temporary/p3-stage-b-operator.sh --execute` with user independently typing current printed full B SHA, `I_ACCEPT_27B_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`. Don't replay old B inspection SHA. Report `P3_B_PASS_FLASH_NEXT_ACTIVE` and original preserved Flash container restored; on BLOCKED/RECOVERY_FAILED STOP, do not retry. Never auto-start stage C.
- [ ] D-034 after B PASS: collect fresh functional P1 verify+measured benchmark with individual plans/approvals and rc3 diagnosis after B, then independently approve C final 27B. Preserve original image/cache/containers, API :8000 and unmerged Draft PR.

---

## 2026-11-06 — P3-A completed on actual DGX; prepare B read-only, require fresh B authorization

- [x] **REAL P3-A SUCCESS:** user ran `p3-stage-a-operator.sh --execute` with a new exact plan SHA `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4` and both individually typed ACKs; Wizard `PASS/executed=true/live_verified=true`, wrapper `P3_A_PASS_27B_ACTIVE` with `issues=[]`, after-switch `LIVE_SERVICE_VERIFIED` and `27b`. Evidence `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json` plus `~/.local/state/blazux-wizard/p3/stage-a.json`. Supersedes prior failed/expired SHA refusal history. No P3-B runtime action.
- [x] Build a D-016 GitHub-tracked **read-only** stage-B inspector `scripts/temporary/p3-stage-b-inspect.sh`, Python, fake-DGX tests, CI. It checks actual successful immutable stage-A receipt, active 27B API, new canonical B-stage plan and preserved original Flash container ID/image with P2 provenance; **no execute mode**.
- [ ] After GitHub-tested source push, DGX user fast-forward pulls and runs **only `bash scripts/temporary/p3-stage-b-inspect.sh`** to collect actual `READY_FOR_SEPARATE_P3_B_APPROVAL` / `BLOCKED` with issues and private evidence. Inspection never stops 27B or starts Flash; keep 27B LIVE.
- [ ] **Separate operator B approval** required after inspecting evidence: no `stage-b --execute` from A approval, no reusing A plan SHA, no automatic downtime. B is 27B→Flash-Next and needs its own fresh plan, independent typed downtime approval, original Flash container preservation and target API verification.
- [ ] Only **after** B PASS, run actual new P1 full functional Verify and numerical Benchmark with explicit individual P1 plans/approvals, plus reviewed rc3 diagnostic evidence newer than B before contemplating P3-C. C final 27B active likewise independently approved. Preserve Draft PR unmerged, checkpoints, original Docker objects and public :8000/v1 contract.

---

## 2026-11-06 — P3-A exact-input UX fixed; previous approved input refused as stale, no transition

- [x] Operator had typed **all three correct** P3-A strings. Wizard returned `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT`, `executed=false`, `approval_accepted=false`; former wrapper displayed ambiguous `OPERATOR_REVIEW_REQUIRED`. Plan expiration `1793950200` was **16:30:00 KST**; report time `16:30:49 KST`. No P3-A Docker stop/start, Flash→27B NOT_RUN. Preserve original Flash.
- [x] Fix tracked `scripts/temporary/p3-stage-a-operator.sh`: terminal prompts now print exact current plan SHA and **both exact ACK strings**, 10-minute plan expiry KST and remaining seconds; stop when <120s remain for input, replan read-only after three typed confirmations and block changed/expired SHA. A Wizard reject with `executed=false` is `BLOCKED`, never false recovery warning. No auto retry/plan swap.
- [x] Fake-DGX tests for old failure, exact prompt literals, short plan window and after-typing SHA change. [Source CI 459/459 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236) on code `fb34ce0ce985824cecd9c63159bf6f1eed408279`.
- [ ] D-016 only: operator DGX clean fast-forward pull then rerun **one** `bash scripts/temporary/p3-stage-a-operator.sh --execute` if still explicitly choosing P3-A downtime. Read actual **NEW** plan SHA printed at prompt; DO NOT reuse the old SHA. Enter three independent typed current literals; cancel on unfamiliar model/image or plan expiry. If `P3_A_NOT_ENOUGH_TIME_FOR_MANUAL_CONFIRMATIONS` then rerun wrapper in a later fresh plan window; do not auto-cycle.
- [ ] Only `P3_A_PASS_27B_ACTIVE` plus independent live model ID and stage A receipt qualifies actual A completion. On `BLOCKED`, `CANCELLED`, `OPERATOR_REVIEW_REQUIRED`, `RECOVERY_FAILED`, STOP and review evidence. D-034 B, post-B P1 rebenchmark, C independently approved and NOT_RUN. No automatic merge/cleanup.

---

## 2026-11-06 — P1 PRE-A proof complete; next P3-A only via D-016 interactive exact-gate wrapper

- [x] Actual operator-reported P1 audit source HEAD `834f823`: `PRE_A_P1_REVIEW_READY`, `issues=[]`, both historical/current expected own-Flash :8000 rc3 collisions, functional Verify PASS, numerical benchmark 3/3 PASS (38.2968 tokens/s, TTFT/latency included), original model/image still active. Evidence: `~/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`. No need to repeat initial P1 GPU benchmark.
- [x] Original operator **conditional** approval (P1 initial work resolved ⇒ 27B transition) is now eligible for **P3-A only**; no blanket GPU/Docker authorization from P1 read-only status itself. D-037 supersedes earlier pre-A hold. P3-A/B/C are not yet executed.
- [x] Add tracked `scripts/temporary/p3-stage-a-operator.sh` and Python helper with default `--plan`, independent `--execute` TTY exact fresh SHA plan, downtime and entry strings, fake-DGX tests, Actions CI and docs; preserves original image/container, does not auto-run B/C.
- [ ] **Only after latest GitHub CPU CI PASS and fast-forward pull**, DGX operator runs `bash scripts/temporary/p3-stage-a-operator.sh --execute` if choosing real P3-A downtime. Review fresh printed `source_model=flash-next`, `target_model=27b`, exact source image/container, immutable P2 receipt; type full fresh plan ID, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_P3_ENTRY` at three prompts. The Wizard rechecks its plan immediately before actual stop/start; any changed state/expired plan cancels without action. This interrupts port :8000 and GPU and may fail to restore on host/Docker outage; P3 source-only pass not a production qualification.
- [ ] Check return `P3_A_PASS_27B_ACTIVE` only with independent manifest/API served `qwen3.8-27b` and local stage-A receipt. On `BLOCKED`, `CANCELLED` or `OPERATOR_REVIEW_REQUIRED`, stop; DO NOT auto retry or run B/C. Report concise summary and evidence path.
- [ ] D-034 next: B 27B→Flash-Next needs separate actual scoped approval; fresh post-B P1 functional+TTFT/tokens/sec benchmark and rc3 reviewed `p1-diagnostics.json`; only then C new separate approval to 27B final active. Keep Draft PR unmerged and don't clean caches.

---

## 2026-11-06 — Fix verified source-report schema error; DGX only reruns tracked P1 audit

- [x] Real DGX first P1 pre-A audit HEAD `3a594193` returned `BLOCKED` **only** for `P1_ASSET_AUDIT_NOT_READY` / `P1_RECEIPT_CHECKPOINT_REVISION_DRIFT`. All historic/current expected active Flash collision checks, original Verify and 3-sample numerical benchmark, current API ID/image were confirmed; no P3 runtime mutation.
- [x] Root cause in source: `p1_post_download.session` persists raw `checks.cache_diagnosis.stdout`, while console-only short summary prints top-level `cache_diagnosis`. New pre-A script read the wrong place and falsely labeled missing SHA as real `DRIFT`.
- [x] Reuse canonical `cache_diagnosis_summary` to parse real persisted raw JSON; report missing revision as `P1_CURRENT_CHECKPOINT_REVISION_UNAVAILABLE` and actual mismatch only if both concrete SHA values exist. Update tests to match actual report schema and prove malformed/changed/checks fail closed. [Code CI 439/439 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898) on `9adc9ab282a91c02e959dcb5c62f98527b556391`.
- [ ] **Operator DGX:** use D-016: `git pull --ff-only origin feature/recipe-wizard-handoff`, then **single** `bash scripts/temporary/p1-pre-a-readiness.sh`. Provide compact JSON `status`, `issues`, `p1_verify`, `p1_benchmark`, `historical_rc3`, `current_rc3`; script has no GPU inference or live-model mutation.
- [ ] If real `PRE_A_P1_REVIEW_READY` and `issues=[]`, review the operator's earlier conditional P3-A approval and refresh exact stage A plan; **do not execute stage A automatically or reuse expired plan**. Independently check downtime boundary and GPU/process ownership. D-034 post-B P1 retest and separately approved B/C remain mandatory. Keep Draft PR unmerged.

---

## 2026-11-06 — One tracked DGX wrapper after GitHub push/CI (D-016)

- [x] Original P1 numerical benchmark 3/3 PASS evidence supplied, including TTFT/latency/throughput, and 2026-11-06 inspect-only source/Hybrid/API READY; no pre-A rerun of P1 inference needed just to obtain metrics.
- [x] New `scripts/temporary/p1-pre-a-readiness.sh`, Python implementation, fake-DGX tests, workflow shell syntax and docs pushed under `feature/recipe-wizard-handoff`; [source CPU CI 435/435 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) at `75d22ce4303736ee84563a0f388a978379e4f228`.
- [x] Fix P3-C evidence gate and pre-A audit using REAL `identity.health` and `identity.models` output, not nonexistent `identity.status`; historical doctor rc3 raw checks still required and NOT assumed.
- [ ] **DGX operator only after GitHub fast-forward pull**: `bash scripts/temporary/p1-pre-a-readiness.sh` once; review printed `status`, `issues`, `historical_rc3`, `current_rc3`, `p1_verify`, `p1_benchmark` and `evidence_file`. The wrapper reads original P1 local reports and receipts; it does no GPU, inference, Docker lifecycle or model transitions. Do not repeat pasted Python snippets.
- [ ] Only if actual DGX evidence is `PRE_A_P1_REVIEW_READY` with empty issues, consider the operator's conditional pre-A approval and fresh stage A plan / scoped downtime, **without automatic execution**. A blocked result needs targeted diagnosis. Do not claim that pre-A implies production qualification or P3-C readiness.
- [ ] D-034: stage B independently approved, post-B P1 full functional and actual measured rebenchmark plus reviewed historical collision disposition, then independent C to 27B. Keep original service, :8000 and source preserved until authorized.
- [ ] Draft PR #1 stays Open/Unmerged. No auto PR merge or cache cleanup.

---

## 2026-11-06 — Use tracked temporary wrapper, not pasted DGX code (P1 pre-A reconciliation)

- [x] Actual P1 initial benchmark values shared: 3 samples / 192 tokens; latency P50=1.687357s/P95=1.780142s, TTFT P50=1.398707s/P95=1.751198s, mean 38.2968 tokens/sec; no repeat GPU benchmark needed just to obtain these numbers.
- [x] Actual P1 `--inspect-only` report shows source+Hybrid READY, API `qwen3.8-flash-next`, no active transfer, clean Git branch, both verify/benchmark plans READY; `actions.*.status=BLOCKED` because inspection-only is expected and **does not revoke earlier verify/benchmark PASS**.
- [x] Reaffirm D-016: temporary DGX logic goes through tracked `scripts/temporary/p1-pre-a-readiness.sh` → GitHub commit/CPU CI → operator `git pull --ff-only` → one wrapper execution → local private JSON evidence → reviewed handoff. No ad hoc pasted shell/Python code; script never does git pull, GPU tests, Docker mutation or model switch.
- [ ] Operator runs `bash scripts/temporary/p1-pre-a-readiness.sh` **after** CI and clean fast-forward pull. It reconciles historic 2026-11-05 and latest current 2026-11-06 doctor/inventory raw stdout, verifies current Flash image+API and original P1 functional/numeric receipts. If past/current reports are missing, use a new separately approved/read-only inspection report, not fabricated evidence. Return the small JSON.
- [ ] Check whether raw historical doctor/inventory rc3 was only expected own `qwen38-flash` / :8000 occupancy with `status=PASS`, `errors=[]`. If not, diagnose actual read failure and keep P3-A blocked. If pre-A baseline accepted, re-evaluate the operator's **conditional** P3-A downtime approval with a newly generated short-lived plan. No automatic stage execute.
- [ ] Post-B P1 functional verification, **numeric** full benchmark and reviewed diagnostic `p1-diagnostics.json` are still required by D-034 before final stage C. No initial P1 result substitutes for actual post-B proof.
- [ ] Draft PR #1 stays unmerged, Flash-Next host :8000 unchanged, no GPU/daemon mutation and no cleanup.

---

## 2026-11-06 — Conditional switch approval NOT MET; finish read-only P1 evidence review first

- [x] Check actual P1 historical evidence before P3-A: 2026-11-05 `verify=PASS` for baseline+extended completion/chat/tools/vision; `benchmark=PASS` bounded, original Flash source/Hybrid ready.
- [ ] Review actual prior local P1 benchmark JSON under `~/.local/state/blazux-wizard/p1/` and capture numerical TTFT, latency and usage-backed tokens/sec; historical summary had no numbers. **Do not rerun GPU benchmark merely to invent missing evidence.**
- [ ] Inspect actual read-only `doctor`/ `inventory-plan` JSON and earlier raw report, distinguish benign active `qwen38-flash`/port :8000 collision from Docker/socket/disk/cache observation failures. Exit 3 alone is not a fault diagnosis nor proof of benign collision. `bash scripts/temporary/p1-post-download.sh --inspect-only` captures these checks without GPU inference or service mutation; review output before any change.
- [x] Fix incompatible `P3-C` source gate that required both raw launch preflights to exit zero while the original model is already running. Only accept both rc3 under exact raw parsed/no-error same Flash-Next source-image and port ownership conditions. New negative tests forbid missing JSON, errors, wrong image/port or rc0 shortcut. [CI 418/418 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172127412).
- [ ] Treat operator's "**if no P1 outstanding, approve 27B**" as condition **currently NOT met**, NOT authorization for P3-A `--execute` or Flash downtime. No model change, PR merge, or auto progression.
- [ ] Preserve D-034 separate P3 stage A, B, post-B P1 verify/numerical rebenchmark, C order. Any P1 check now cannot replace genuine post-B receipts. Require fresh explicit authorization and current exact P3-A plan after a reviewed safe boundary.
- [ ] Preserve Draft PR, checkpoint/image/container, and :8000; no auto GPU benchmark or file cleanup.

---

## 2026-11-06 — Source hardening/CPU 413 PASS; P3-A runtime requires new explicit approval

- [x] Operator-supplied real DGX `sequence --plan` P2 receipt and P3-A read-only plan READY recorded below, including exact 14:40 KST expiry; **NOT_EXECUTED**.
- [x] Correct stale `sequence --plan` wording: staged source exists but actual DGX switch not qualified. Keep source implemented vs DGX acceptance explicit.
- [x] Add recovery-time foreign GPU-enabled Docker consumer guard (stop/restore collision fails closed) and focused CPU fake-Docker tests.
- [x] CPU 413/413 SUCCESS on tested source commit `02bf94c1628828ce22fa338dd5a8e5a0955f9179`: [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170050031), [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860).
- [ ] **No runtime P3-A action without explicit separately scoped operator downtime approval.** When such approval arrives, regenerate exact unexpired `stage-a --plan` and independently review source/target, :8000 ownership, GPU consumers, recovery readiness; old `79be6bf...` token expires 14:40 KST, never reuse it.
- [ ] After any separately authorized actual A run, verify independent live `qwen3.8-27b` API and complete A receipt before considering B. Stages B and C independently approved; P1 remediation/rebenchmark after verified B remains mandatory.
- [ ] Keep Draft PR unmerged; no unattended DGX operation, host Docker change, source cleanup or port service interruption.

---

## 2026-11-06 — Actual P3-A DGX read-only plan READY; next gate requires explicit downtime approval

- [x] Operator supplied real `./wizard.sh service manager status --json`: Flash-Next `LIVE_SERVICE_VERIFIED` on :8000, exact API ID `qwen3.8-flash-next`, `issues=[]`; **no mutation** and GPU/process exclusivity not independently qualified.
- [x] Operator supplied real `./wizard.sh switch flash-next-27b sequence --plan --json`: P2 successful private receipt SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9` observed, P3 separate-entry `BLOCKED` expected, not a failure.
- [x] Operator supplied real `./wizard.sh switch flash-next-27b stage-a --plan --json`: `READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, source exact ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, plan `79be6bf05cb02306ec9155ade317e06c457238de427417ebab8946e35449247a` expires 2026-11-06 **14:40 KST**. **Do not reuse this plan after expiry.**
- [ ] Request **separate explicit P3-A maintenance-window / downtime authorization**. Only then regenerate a fresh stage-A `--plan` on the actual DGX, independently review exact source/target IDs, foreign GPU consumers, current port ownership, fallback, and approval ID. No generic `continue` counts as authorization.
- [ ] Only after scoped explicit authorization execute stage A and independently verify `qwen3.8-27b` ACTIVE using fresh Manifest/API and stage-A local journal. Pause after A; stage B needs a *new* approval. P1 post-B remediation and final C remain blocked until preceding receipts exist.
- [ ] Do not merge Draft PR, touch model/cache, auto-advance P3 or restart the current service as a side effect of GitHub/docs/source activity.

---

## 2026-11-06 — P3 SOURCE/CPU gates ready; hold at operational approval boundary

- [x] P2 completed and recorded as `BENCH_PASS_RESTORED_VERIFIED`, original Flash-Next restored/verified. Do not run again.
- [x] D-034 source stages A/B/C implemented in `p3_persistent_switch.py`, read-only plans visible in Wizard CLI/TTY; source container restore and journal protections with fake Docker tests.
- [x] Post-B P1 `verify`, measured `benchmark` and historical rc=3 diagnostic proof gate implemented; **no actual P1 remedial evidence yet**, so final C is appropriately ineligible.
- [x] Source CI PASS 411/411 on `27728045907a1f2111dc4b8340fbea2cc365ff1d` ([PR run](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168524464)). Follow-up documentation commits are not additional GPU proof.
- [ ] Evaluate real P3 stage-A read-only `./wizard.sh switch flash-next-27b stage-a --plan --json` on DGX after non-destructive `git status -sb` and `git pull --ff-only`. Collect exact live source, pinned image/target, candidate plan and issue array.
- [ ] **NEW explicit approval needed** before executing A (Flash→27B) during a maintenance window. Separately confirm API ID and observed source/target IDs; do not chain B.
- [ ] Plan and separately approve B (27B→Flash); only after verified B obtain historical doctor/inventory-plan rc=3 root cause records, re-run P1 functional and numerical benchmark with fresh P1 approvals. Keep diagnostic status BLOCKED until reviewed.
- [ ] Only after P1 actual evidence verified, plan and separately approve C (Flash→27B). Verify 27B actually active; preserve Flash-Next and other model source assets.
- [ ] Before considering production release, perform controlled DGX fault-injection checks and validate actual rollback, port/GPU exclusivity and persistence after Docker restart. CI mock success is not enough.
- [ ] Keep PR #1 Draft/unmerged pending explicit merge request and production review. No Orcarouter/cleanup scope.

---

## 2026-11-06 — UPDATED NEXT ACTIONS: P2 COMPLETE; SOURCE-ONLY P3 engineering

- [x] P2 27B bounded **actual DGX** GPU/API/streaming benchmark: `BENCH_PASS_RESTORED_VERIFIED`, 3/3; original Flash-Next `RESTORED` and `LIVE_SERVICE_VERIFIED` (operator-supplied JSON). See EVIDENCE-LEDGER. **Do not rerun P2.**
- [x] P2 STOP boundary enforced; D-034 supersedes old D-033 two-roundtrip plan.
- [ ] Read latest GitHub HEAD/CI and existing manager code. Implement safe **separate P3 staged persistent switching** with per-stage current-state plan, exact scoped approval, fresh observed Docker/API/GPU source, target image/checkpoint/recipe, stop-before-start, port 8000, source-ID preservation, failure restore, append-only evidence and duplicate/stale block. CPU fake-backend tests BEFORE attempting any DGX execution.
- [ ] Integrate P3 phase evidence and **P1 remedial functional + actual rebenchmark evidence gate** into final stage C. Historical P1 doctor/inventory-plan rc=3 remains unexplained and P1 numeric metrics still unprovided; do not assume PASS. Retain existing P1 executor.
- [ ] Commit safe source/tests/docs into existing Draft PR #1, review CI. Keep PR unmerged.
- [ ] **Separate operational approval required** for each P3 transition A/B/C; no `--execute` on live DGX under this documentation/engineering instruction. A must verify 27B live, B Flash-Next live; after P1 remediation/rebench accepted, C must finish on 27B.
- [ ] Preserve original Docker images/containers, both pinned checkpoints, Orcarouter assets and :8000 external API. No deletion, redownload, image rebuild or parallel GPU models.

Earlier P2 checklist blocks below are historical and **superseded** by this completed result; never treat their unchecked P2 benchmark item as a current next action.

---

## 2026-11-06 — P2 then STOP; separate P3 entry; remediate/rebench P1 before final 27B

- [ ] **P2 first**: operator separately approves a new Flash-Next downtime plan; execute actual bounded NVIDIA 27B benchmark, record measured client TTFT/latency/decode/ingest proxies and restored original Flash-Next `LIVE_SERVICE_VERIFIED`; **STOP at P2 regardless of PASS**. No auto P3 plan or execute.
- [ ] Wait for explicit P3 entry authorization. Do not recycle the P2 benchmark plan ID; require fresh live Manifest/API and separate transition plan + approval.
- [ ] In P3, since P2 restores Flash-Next, separately activate 27B and verify `qwen3.8-27b` to establish the source for the next test.
- [ ] Separately switch **27B → Flash-Next**, verify `qwen3.8-flash-next` and preserve original container/rollback evidence.
- [ ] While Flash-Next is active resolve outstanding P1 `doctor/inventory-plan` nonzero reasons, repeat functional probes and **measure real P1 TTFT/latency/tokens/sec** with saved benchmark evidence. If not satisfied, block final transition.
- [ ] With P1 PASS, separately approve and perform final **Flash-Next → 27B**; verify API `qwen3.8-27b` and preserve safe rollback resources, record P3 outcome. **Final target 27B active**, not automatic Flash-Next restore.
- [x] Source-only: retire old P3 two-roundtrip executor, expose new read-only `sequence --plan`; persistent P3 switching executor **NOT IMPLEMENTED**, no new GPU actions.
- [ ] Retain existing Flash-Next API, original images and both caches; keep Draft PR unmerged. No Orcarouter/extra model scope.

---

## 2026-11-06 — Actual DGX P2 plan READY / P3 correctly BLOCKED; next is specifically approved P2 measured run

- [x] Actual DGX read-only `./wizard.sh model 27b benchmark --plan --json` returned `READY_TO_REQUEST_TRIAL_APPROVAL`, `issues=[]`, `executed=false`, correct model/image/source. Returned ID `2f76c3b03865b6a15a5c2fe8f316231f532fbf8b7fe178ffd00db8383edc3399` **expires 2026-11-06 12:20 KST** and must be regenerated.
- [x] Actual DGX read-only `./wizard.sh switch flash-next-27b roundtrip --plan --json` returned `BLOCKED`, `P2_BENCHMARK_RECEIPT_NOT_FOUND`; this is intended until a real P2 benchmark success receipt exists.
- [ ] After separately authorizing a Flash-Next :8000 downtime, create a **fresh** P2 benchmark `./wizard.sh model 27b benchmark --plan --json` and review `status=READY_TO_REQUEST_TRIAL_APPROVAL`, `issues=[]`, exact plan ID. During approved window execute via Wizard with fresh full ID and `I_ACCEPT_FLASH_NEXT_DOWNTIME`. Confirm `BENCH_PASS_RESTORED_VERIFIED`, actual TTFT/throughput proxy metrics, private benchmark evidence and Wizard Flash-Next restore identity before moving on. Any startup/restore failure => do not start P3.
- [ ] ONLY THEN generate the P3 two-cycle roundtrip plan; require separate explicit downtime approval and validated fresh P3 plan. No automatic P3 switching or model re-download.
- [ ] Keep original Flash-Next container, HTTP :8000, PR Draft and model caches untouched by preparatory plan queries.

---

## 2026-11-06 — REFOCUS on P2 actual benchmark and P3 repeated temporary roundtrip

- [x] First actual DGX NVIDIA 27B GPU text smoke and return-to-original `PASS_RESTORED`, plus independent manifest-led Flash-Next `LIVE_SERVICE_VERIFIED`.
- [x] **Source implementation** P2 exact-approved bounded benchmark, 3 sequential 64-token SSE prompts, client TTFT/latency/proxy throughput and point-memory sampling with private evidence, then same-original restore + Wizard check. Distinct approval from first smoke trial.
- [x] **Source implementation** P3 conditional two-cycle temporary roundtrip plan/executor, blocked absent successful current P2 `*.benchmark.json`; each cycle uses same original-recovery protections; two-cycle run does not qualify permanent switching.
- [ ] DGX **read-only**: `git status -sb` and `git pull --ff-only origin feature/recipe-wizard-handoff`; `./wizard.sh model 27b benchmark --plan --json`. Record status/plan parameters/issues. If BLOCKED, debug before requesting downtime; no repeated source-only import checks.
- [ ] When explicitly approved, run real P2 benchmark during maintenance with exact live plan and typed downtime acknowledgment. Share measured JSON/status; confirm `BENCH_PASS_RESTORED_VERIFIED`, metrics, original API, source ID and real `*.benchmark.json`. **No approval inferred from this handoff.**
- [ ] **Only after P2 DGX benchmark PASS**, read-only `./wizard.sh switch flash-next-27b roundtrip --plan --json`. Then separately obtain full P3 two-cycle downtime approval and test both cycles; record original-container and API identity after each.
- [ ] Full permanent Flash-Next ↔ 27B service switch, extended performance/profiles, abnormal-path fault recovery and rollback remain independently gated. Orcarouter work remains for P5, not current scope.
- [ ] Keep Draft PR #1 unmerged, original Flash-Next container and API :8000 intact until scoped actual test.

---

## 2026-11-06 — After real installed model inventory: preserve Orcarouter, advance P2 benchmarks

- [x] DGX ran `./wizard.sh model list --installed --json` and returned `READ_ONLY_INVENTORY`, `executed=false`; source snapshots Flash-Next **11/11**, NVIDIA 27B **3/3**, Orcarouter **17/17** with zero missing indexed shards.
- [x] **Actual legacy Orcarouter assets are preserved** at previous YSLAB HF cache revision `3a3b63161c0745390e5270179af42e46efc70799`; matching historical `orca-uncensored-bf16-mtp/ee5b6b553f1226d2` recipe directory observed. **No model removal or redownload needed** for source discovery; no GPU/recipe qualification yet.
- [x] Current Flash-Next API confirmed by manifest-led live status (`LIVE_SERVICE_VERIFIED`); 27B remains inactive after prior `PASS_RESTORED` first GPU trial.
- [ ] **Read-only future Orcarouter qualification:** inspect legacy recipe directory's exact manifests, referenced files, symlinks and model provenance without moving/modifying legacy files; distinguish original NVFP4 cache versus BF16 PLE recipe view and avoid claiming ready based on directory presence.
- [ ] Continue **P2 27B benchmark** in a separately approved, bounded GPU maintenance window with strict stop→test→restore; measure TTFT, prefill/decode tokens/s, memory and functional behavior. Never silently restart 27B based on file availability.
- [ ] P3 repeated Flash-Next ↔ 27B transition, P5 Orcarouter run/benchmark and P6 Orcarouter ↔ 27B transitions remain separately gated. Keep production service, legacy model caches, and 4 unregistered snapshots untouched.

---

## 2026-11-06 — Read-only installed model inventory, including protected legacy Orcarouter

An earlier example `./wizard.sh model list --installed --json` was suggested **before implementation** and gave `{"status":"BLOCKED","error":"choose a valid submenu item for model"}` when the operator tried it. That error was a **missing Wizard route**, NOT evidence that any model was deleted.

This command is now implemented and tested:
```bash
./wizard.sh model list --installed --json
```

Canonical config `runtimes/model-discovery.json` lists known Hugging Face caches (`~/.cache/huggingface`, `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/hf-cache`, and `HF_CACHE`/`HF_HOME` overrides). It maps registered service models to their source repo identifiers **without changing `runtimes/service-policy.json` or granting launch permission**. Includes protected original Orcarouter source `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4`, revision `3a3b63161c0745390e5270179af42e46efc70799` and original BF16/MTP recipe view `~/Workspace/llm/yslab-qwen38-bf16ple-dgx-spark/recipe-views/orca-uncensored-bf16-mtp/ee5b6b553f1226d2`. The previous project originally reported ~180GB `hf-cache`, ~5GB `recipe-views`; this was historical storage evidence and has **not been rechecked today**.

Read-only inventory validates selected snapshot's bounded weight index and existence of every indexed nonempty shard (following HF symlinks), tokenizer and config. It reports exact cache/revision and source state. A recipe view alone yields `RECIPE_VIEW_ONLY_SOURCE_UNVERIFIED`; missing weights yield `SNAPSHOT_INCOMPLETE_OR_UNVERIFIED`; found complete indexed weights yield `SOURCE_FILES_PRESENT_UNQUALIFIED`. Unknown caches beyond configured roots are **not** conclusively absent; limited other cached repos are reported as `UNREGISTERED_CACHE_SNAPSHOT_OBSERVED`. Active API identity comes from the manifest-led live service inspector. All these are observational; no model is moved, deleted, downloaded, registered as ready, started, restored, or switched.

The new command has **not yet run on the real DGX**. After clean Git fast-forward, operator executes one read-only Wizard command and provides JSON. Any Orcarouter result must be reconciled with current disk evidence before asserting continued asset availability or runtime compatibility. Original service `qwen38-flash` remains untouched. Existing P2 first GPU trial `PASS_RESTORED` and `LIVE_SERVICE_VERIFIED` are separate, already reported facts.

---

## 2026-11-06 — After real GPU PASS_RESTORED: check live status ONLY through Manifest Wizard

- [x] Real DGX NVIDIA Qwen3.8-27B ModelOpt GPU startup, API ready and one bounded inference **PASS**. Normal-path original Flash-Next return `RESTORED`, issues=[]; overall `PASS_RESTORED`. Private evidence file `/home/inlc/.local/state/blazux-wizard/p2/20261105T230229Z-a4fc14cf8079.json` (not read independently). Never confuse normal restore with exceptional rollback tests.
- [x] Create unified read-only Manifest + API Wizard service status. `./wizard.sh service manager status --json` combines actual Docker/socket, `runtimes/service-policy.json`, expected exact `/v1/models` served ID, and `/health`. Keep `inventory`, `health` and `logs` distinct diagnostics; all read-only, no activation.
- [ ] Operator on DGX: `git status -sb`, `git pull --ff-only origin feature/recipe-wizard-handoff`, `./wizard.sh service manager status --json`. Confirm `status=LIVE_SERVICE_VERIFIED`, `observed_model=flash-next`, `expected_served_id=qwen3.8-flash-next`, all `checks` true and `issues=[]`. If BLOCKED, provide JSON and investigate, never silently bypass. No raw Docker/curl as main user workflow.
- [ ] Design P2 functional and timed benchmark probes that run **while Qwen3.8-27B is temporarily serving**, capturing real TTFT, prefill/decode tokens/sec, peak memory and short/mid context behavior. Keep one-model GPU policy and mandatory original Flash-Next restore; require **new** explicit interruption approval for another GPU trial.
- [ ] Then qualify repeated Flash-Next ↔ 27B permanent switching, transition journal + rollback, and separately Orcarouter. No unstated production model switch or PR merge.
- [ ] Record new status command's actual DGX JSON and benchmark results in evidence ledger/hand-off as separate fresh observations.

---

## 2026-11-06 — One-shot actual NVIDIA 27B trial next; explicit operator outage approval required

- [x] DGX CPU-only Qwen3.8 internal Qwen3_5 loader/ModelOpt registry checks **9/9 true, issues=[]**, `modelopt_mixed` registered. No GPU/weights tested.
- [x] Deliver exact-approved **temporary** 27B GPU trial with original Flash-Next rollback. 354/354 CPU regression tests PASS at source commit `ea28b0c0`. No model switch or running service change yet.
- [ ] Operator updates clean branch then runs `./scripts/serve_27b.sh --trial-plan` (read-only). Verify `status=READY_TO_REQUEST_TRIAL_APPROVAL`, original container ID and local pinned image identity, other GPU containers absent. If `BLOCKED`, investigate and **do not bypass**.
- [ ] **Only during approved maintenance interruption**, operator may opt into `./scripts/serve_27b.sh --trial-execute --approve-plan FULL_64_HEX_SHA --ack-downtime I_ACCEPT_FLASH_NEXT_DOWNTIME`. This directly interrupts live Flash-Next :8000 and can cause an outage if rollback fails. No approval implied by CPU PASS, user preference to try soon, or earlier download permission. Keep terminal attached; do not use `nohup` or background execution. The exact plan expires within 10 minutes.
- [ ] Record local trial JSON and bounded target log paths (no raw logs uploaded automatically). Distinguish trial API PASS, inference PASS, restored Flash-Next API PASS. If `RECOVERY_FAILED`, **do not start old while new GPU container may still run**; manually inspect Docker and GPU ownership.
- [ ] Based on first GPU error, adjust ModelOpt/GB10 kernel image separately if needed; do not introduce Unsloth compressed-tensors flags into official NVIDIA ModelOpt checkpoint. Future MTP, long context and production switching remain distinct follow-ups.

---

## 2026-11-06 — Re-run corrected 27B registry name audit (minimal next DGX step)

- [x] Initial DGX isolated CPU import passed module/class presence (five checks). `modelopt_mixed` check initially reported TypeError due to incorrect class-level call to `get_name(self)`; not evidence the model cannot run.
- [x] Correct `p2_27b_loader_import_audit.py` to use public `get_quantization_config("modelopt_mixed")` registry/class-identity resolution without instantiating a quant config; source CI `0a14f189`, 336/336 PASS.
- [ ] Clean fast-forward DGX to latest `feature/recipe-wizard-handoff`, execute `./scripts/temporary/p2-27b-loader-import-audit.sh --execute-cpu-only` and capture full JSON. Expected keys `quant_registry_module_imported`, `quant_registry_factory_present`, `modelopt_mixed_registry_class_matches`, `modelopt_mixed_cli_name`. A future PASS is a CPU import/registry PASS only, **not** GPU qualification. If registry wrong, investigate actual installed image rather than guessing flags.
- [ ] Confirm true runtime CUDA/C++ extension and loader in an **independently approved** GPU plan before service stop/27B model load; preserve the live original Flash-Next and single :8000 service.
- [ ] Keep Draft PR #1, no merge, no start/switch, no manual execution of `command_preview`.

---

## 2026-11-06 — Next controlled 27B loader import evidence after successful DGX serve split

- [x] DGX ran both dedicated entrypoint `./scripts/serve_27b.sh --status` and `--plan` after fast-forward to `99dde4c`; correct read-only outputs, no 27B start or service modification. Existing Flash-Next `qwen38-flash` API identity **confirmed**, original image ID equals candidate 27B local image ID, and ModelOpt source mix is 208 FP8 + 193 NVFP4.
- [x] Implement isolated CPU-only import probe `p2-27b-loader-import-audit.sh` and 8 unit regressions; source `834c750` CI 333/333 PASS.
- [ ] DGX: after clean `git status -sb` and `git pull --ff-only origin feature/recipe-wizard-handoff`, execute `./scripts/temporary/p2-27b-loader-import-audit.sh --plan`. Optional separately opted-in CPU container `--execute-cpu-only` may test installed vLLM Qwen3.5 and ModelOpt import/class/name with 2GiB/2CPU/no network/GPU/cache/ports. Report structured JSON only. A restricted CPU sandbox import failure is **not** a GPU incompatibility verdict.
- [ ] Reconcile actual ModelOpt name/import facts with candidate `--quantization modelopt_mixed`; verify 27B image provenance, vLLM real loader and GB10 kernels, memory/context and original Flash-Next restore before any approved GPU transition. Keep P2 startup, service stop/switch and rollback blocked until scoped approval.
- [ ] Keep Draft PR #1 unmerged. Do not execute `command_preview` by hand; no duplicate active inference models.

---

## 2026-11-06 — Model-specific serving scripts delivered

- [x] Split legacy `scripts/serve.sh` into default-compatible dispatcher + `scripts/serve_flash-next.sh` (existing executable) + `scripts/serve_27b.sh` (read-only plan/status). `./flash serve` explicitly uses Flash-Next file.
- [x] Preserve old startup behavior/test fixtures and add 10 new CPU tests covering permissions, shell syntax, dispatcher, direct Flash-Next invocation, NVIDIA 27B environment override rejection and absence of a 27B start bypass. CI `67a54afc`: 325/325 PASS.
- [ ] After clean `git pull --ff-only`, operator may run **only read-only 27B** `./scripts/serve_27b.sh --plan` or `--status`; this returns `status=BLOCKED` even when metadata/source PASS. Avoid running `scripts/serve.sh` or `./flash serve` without realizing those default to an actual Flash-Next start, and **do not manually run the returned command_preview**.
- [ ] Review actual P2 source image provenance, ModelOpt vLLM/GPU import/weight load, 27B memory/context, original Flash-Next recovery/rollback, approved DGX transition scope; only then implement a guarded executable `serve_27b.sh` backend with complete start/wait/verify/benchmark and safe recovery.
- [ ] Preserve single active GPU model and `:8000/v1`. Keep PR #1 Draft until evidence/approval gates pass.

---

## 2026-11-06 — P2 dedicated 27B launch preview; GPU acceptance still blocked

- [x] Actual pinned DGX quant audit: modelopt `MIXED_PRECISION`, FP8 **208**, NVFP4 **193**, total **401**, no metadata issues.
- [x] Actual installed image AST audit: **4/4 checks true**, `SOURCE_SURFACES_PRESENT_UNQUALIFIED`; no GPU model load or kernels tested.
- [x] Build dedicated 27B **start-preview** with exact snapshot SHA, local image ID, `modelopt_mixed`, conservative initial GPU settings, no Flash-Next-specific PLE/MTP, source container image and local API identity audit. Source-only `ae4490d6` CI **315/315 PASS**. Does not enable `start --execute`.
- [ ] After clean fast-forward, run `./wizard.sh model 27b plan --for-action start --launch-preview --json` on DGX. This reads local Docker and `/health` plus `/v1/models` on existing `127.0.0.1:8000`, not a GPU model inference request; compare returned original container image and served API ID. Report `issues` and `observed_source`. **Do not run `command_preview`**.
- [ ] Verify runtime vLLM 0.32 CLI `modelopt_mixed`, quant loader import/GPU kernels, VRAM/context 8192/SSM dtype, image provenance/pinned-recipe acceptance, verified Flash-Next recovery before enabling an executable P2 transaction. Keep per-action source identity and explicit approval ID, revalidate immediately before any future stop/start.
- [ ] Only with separately approved DGX GPU/port 8000 maintenance window: stop old, verify port and GPU freed, start isolated 27B, wait, test exact API ID/text/tools/vision + bounded benchmark and restore on failure. Keep PR #1 Draft until those tests pass.

---

## 2026-11-06 — P2 CPU-source qualification next operator evidence

- [x] Add immutable-source ModelOpt layer-algorithm auditor and integrate `quantization_audit` in Wizard; CI `cd63f25` 303/303 CPU PASS.
- [ ] With checkout clean, `git pull --ff-only origin feature/recipe-wizard-handoff`, then rerun `./wizard.sh model 27b status --inspect-runtime --json` and review `quantization_audit` actual pinned local values; do not load model or stop Flash-Next.
- [ ] Inspect local image source with `./scripts/temporary/p2-27b-image-audit.sh --plan`, then explicit `--execute-cpu-only` for isolated runc source AST checks (CPU-only temporary container). Return JSON without secrets; this is NOT GPU model loading.
- [ ] Reconcile ModelOpt per-layer algorithm set against actual installed vLLM registry/loader. Only then design/qualify 27B-specific pinned launcher, image ID vs registry digest, memory/context profile and start/wait/verify/benchmark; no reuse of Flash-Next PLE/MTP defaults.
- [ ] Operational GPU/start/switch/rollback requires separate scoped approval and verified original Flash-Next recovery assets. Keep PR #1 Draft.

---

## 2026-11-06 — Actual image source audit for 27B next

- [x] Operator DGX actual `status --inspect-runtime` confirms NVIDIA pinned 27B source, correct architecture/modelopt/context, ARM64/Linux v0.32 local image ID and protected live Flash-Next.
- [x] Add bounded installed-image source AST auditor and explicit no-GPU/no-network temporary Docker wrapper, plus eight CPU unit tests. `acf5d64` CI: 294/294 PASS.
- [ ] **DGX read-only follow-up:** after `git status -sb` and clean `git pull --ff-only`, run `./scripts/temporary/p2-27b-image-audit.sh --plan`; review, then `./scripts/temporary/p2-27b-image-audit.sh --execute-cpu-only`. This transient runc container does not use GPU, host port or inference service. Return JSON, especially registry/modelopt checks and blocker messages.
- [ ] Audit exact `hf_quant_config.json`, mixed FP8/NVFP4 per-layer support and pinned snapshot tokenizer, verify executable image registry and real memory budget; do not confuse static source presence with GPU loading.
- [ ] Finish isolated 27B launcher/recipe and bounded P2 lifecycle executor with immutable image identification, transaction approval and full original Flash-Next restore. Actual 27B start and `:8000` switchover require a *separate* explicit user-approved transition window; until then no operation may touch inference service/GPU.
- [ ] Run GPU/model/API/benchmark/rollback acceptance only with approved DGX plan. PR #1 stays Draft.

---

## 2026-11-06 — NVIDIA 27B source downloaded; runtime qualification pending

- [x] Record user-provided DGX NVIDIA pinned download 19/19, exit 0, `SOURCE_FILES_PRESENT_PINNED_CANDIDATE`, with exact evidence path; prior transfer-in-progress checklist is historical.
- [x] Implement source-only read-only `status --inspect-runtime` audit of exact source revision, model config, Docker image/platform/label and current service, with CPU fault tests. No GPU allocation, service stop or auto approval.
- [ ] After clean `git pull --ff-only` (download has completed), operator may run `./wizard.sh model 27b status --inspect-runtime --json` and return sanitized JSON, to ground actual cache/config/image/service assertions. Do not launch 27B.
- [ ] Inspect exact pinned config / hf_quant_config and vLLM 0.32 model registry+ModelOpt loader in image, ARM64 support, memory budget and validated image digest. Complete a 27B-specific non-Flash serve recipe and guarded start/wait/verify/benchmark adapter.
- [ ] Obtain a separate exact plan approval before any Flash-Next stop, 27B GPU start or P3 cutover. Preserve and verify rollback source, health and `:8000` API identity.
- [ ] After source CPU/CI, verify actual runtime in approved DGX window, including failures, latency/TTFT/TPS, model identity and rollback. Keep PR #1 Draft until end-to-end acceptance.

---## 2026-11-06 — full Wizard SOURCE / incremental P2–P7 debug

- [x] Build complete model-first TTY menu and machine workflow/roadmap, expose all ten model lifecycle actions for Flash-Next/NVIDIA 27B/Orcarouter.
- [x] Build service menu for status/health/bounded logs and guarded start/stop/restart/rollback/proxy/gateway; P3/P4/P6/P7 advanced plan actions and readiness dashboard are accessible.
- [x] Preserve P1 exact approval and 27B pinned downloader; block P1 guided when another inference model is active or service inventory unknown; add regression.
- [x] Add no-Docker/no-GPU CPU matrix to GitHub CI and update docs/decisions/handoff. Check final HEAD test counts and Draft PR #1 status.
- [ ] While operator-owned 27B download remains active, leave DGX checkout, qwen38-27b-dl, source image/cache and Flash-Next :8000 untouched; **do not ask git pull while downloading**. On completion, obtain exact return code/evidence, then review `./wizard.sh model 27b status --inspect-cache --expected-revision 482ca0f3832238542f8f5295dde86b5f22711d80 --json`.
- [ ] Begin real P2 runtime adapter qualification on source/CPU (vLLM 0.32 single GB10 ARM64, ModelOpt NVFP4, image digest, PLE/MTP) before any live GPU trial; model conversion/stop/switch requires separate approval.
- [ ] Implement/start fault-injected service transaction and symmetric rollback when approved; P3 bidirectional proof, P4 optional no-deletion default, Orcarouter adapter from reviewed parallel branch, P6 switch, P7 acceptance. Keep shared host API 8000.

## 2026-11-05 — after model-first Batch A/source-only B

- [x] Implement root model selection, read-only lifecycle plans and in-flight download suppression, preserving P1 and existing CLI.
- [x] Add bounded GET-only service health/model identity observer and preview-only atomic stop/port-free/start/verify/rollback order.
- [x] Add mock CPU tests and workflow coverage for model cases, API failures and transition gates.
- [ ] At completion of **operator-owned** NVIDIA download, collect return code, `~/.local/state/blazux-wizard/p2/evidence/*.json` path and exact pinned cache inspection before calling P2 downloaded; do not touch current DGX worktree during transfer.
- [ ] Next source batch: validate NVIDIA 27B vLLM 0.32 ARM64/GB10 loader+image, build start/wait/verify/bench adapter and real manifest-based service handover with scoped approval and recovery; do not enable live switching from preview alone.
- [ ] On user-approved DGX validation window after receipt, verify model start/rollback and 27B API/bench; keep Flash-Next model weights/image intact.

## 2026-11-05 — model-first unified Wizard source continuation

- [x] Record accepted D-020 UX design and source/acceptance gates; retain Flash-Next P1 backend.
- [x] Implement root 3-choice menu and read-only `select MODEL --json`; model plans for active, missing, in-flight, source-only, unknown and Orcarouter cases. Show only the relevant downloader or existing P1 guided backend behind explicit separate prompts.
- [x] Expose `qwen38-27b-dl` live container state in observed service manifest; suppress second download; add Orcarouter registry placeholder with no launch permission.
- [x] Add CPU regression matrix and GitHub CI job; preserve all legacy P1–P7 command routes and destructive refusal behavior.
- [ ] **Operator-owned DGX transfer still in progress at last evidence (`16/19` files).** Do not pull updates, restart Flash-Next, interrupt/alter download or run a second transfer. After download exits, collect Wizard receipt/evidence first and only then update DGX checkout.
- [ ] Batch B: actual /v1/models + GPU observation, bounded health/logs, immutable recipe/runtime qualification, and source-only stop→free :8000→start→verify→rollback transition plans with fault injection tests.
- [ ] Batch C: separately approve a live DGX service handover window; validate 27B vLLM 0.32 image/loader/ARM64 before any GPU start. Keep Orcarouter separate branch unmodified.

## P2 download approval unblock (2026-11-05)

- [x] Diagnose user-reported exact approval rejected by mutable preflight fingerprint; fix hash scope to stable safety fields. All storage/Docker/inode preconditions still rerun under download lock.
- [x] CPU regressions for lock inode creation, uptime/free-space drift, actual approved execution, low disk rejection, and service/image identity change requiring reapproval.
- [ ] Check final-HEAD GitHub Actions and PR. On DGX operator's next run: `git pull --ff-only origin feature/recipe-wizard-handoff`, then `./wizard.sh model 27b download --guided` and input the **new** full plan ID. Never reuse pre-fix ID `b190c936...`. Report evidence path / any new blockers.
- [ ] Actual NVIDIA 27B full checkpoint receipt and verification remains `NOT_RUN` until the operator reports results; single model at host `:8000` policy unchanged.

## P2 immediate operator download and parallel source development (2026-11-05)

- [x] Confirm NVIDIA exact model revision `482ca0f3832238542f8f5295dde86b5f22711d80` from authoritative source and add immutable SHA to invalid (not runtime-qualified) recipe.
- [x] Implement guarded Wizard `download --guided` and `download --execute --approve-plan` with no GPU and no API/Docker service mutation; add mock CPU tests and pinned-without-refs audit.
- [x] Commit one-GPU-model/host `:8000` service policy, read-only live manifest and generation-checked transition journal primitives.
- [ ] After latest CI PASS, **operator**: `git pull --ff-only`, then `./wizard.sh model 27b download --guided`. If plan BLOCKED (capacity/image/cache/name/transfer), return the exact issues; do not force the download or delete Flash-Next. Download is **NOT_RUN** until actual DGX evidence is returned.
- [ ] While 27B downloads, implement tested service-switch executor (stop Flash-Next, verify port release, start 27B at :8000, API verify and rollback); preserve original Flash-Next and require separately approved live transition.
- [ ] Qualify vLLM 0.32 ModelOpt loader and single GB10/ARM64 compatibility, then Wizard wait/verify/benchmark and P2 runtime acceptance.

## P2 NVIDIA acquisition and service-manager follow-up (2026-11-05)

- [x] User DGX read-only NVIDIA status: `NO_PINNED_LOCAL_SNAPSHOT`, 0 indexed shards, no local revision in inspected cache. Historical RadixArk evidence retained separately.
- [x] Add Wizard top-level Service management menu and 27B `download` planning action; all stateful actions remain fail-closed.
- [ ] Implement live read-only service/port/inode/disk/download-container inventory, immutable NVIDIA source pin and exact SHA256 plan with freshness and explicit approval.
- [ ] Implement and CPU-test guarded resumable 27B download (without `flash setup`, active model replacement or deletion); then schedule/approve actual DGX download separately.
- [ ] Qualify vLLM 0.32 single GB10 runtime and implement start/wait/verify/bench + rollback as a distinct action from downloading.

## P2 NVIDIA target selection (2026-11-05)

- [x] Replace P2 active model ID and local HF cache directory with `nvidia/Qwen3.8-27B-NVFP4`; retain RadixArk DGX result as historical evidence only.
- [ ] After Git pull, operator runs read-only `./wizard.sh model 27b status --inspect-cache --json` for **NVIDIA cache**, not the previously inspected RadixArk checkpoint.
- [ ] Verify NVIDIA immutable full SHA and actual local source files; qualify pinned vLLM 0.32 runtime/image and single GB10 memory before any download/start. No reuse of RadixArk revision.

## P2 source qualification update — 2026-11-05

- [x] Add bounded config fact discovery (architecture, model type, quant method, context and vision metadata), strictly **unqualified** for vLLM/GB10, with malformed/oversized config regressions.
- [ ] Check current CI after implementation and inspect real DGX read-only `./wizard.sh model 27b status --inspect-cache --json` output; never infer actual model availability from test fixtures.
- [ ] Source-check immutable model revision and vLLM 0.32 loader/GB10 support, then implement guarded 27B recipe planning and runtime steps without allowing unapproved download/start/replacement.

# Next actions — ordered work queue

## Current transition: P1 bounded GPU tests PASS → P2 27B inventory/qualification

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

- [x] P1: actual Wizard baseline, chat, tools, vision and bounded bench PASS.
- [ ] P1: obtain benchmark evidence metrics (TTFT, latency, tok/s) from the already existing operator file; review `doctor`/`inventory_plan` issues and confirm Wizard-driven install/start if required by full P1 lifecycle.
- [x] P2: source-only, fail-closed read-only HF cache inventory in Wizard; unit tests/CI required before DGX operator command.
- [ ] P2: operator runs `./wizard.sh model 27b status --inspect-cache --json` (no downloads, GPU, Docker or API changes).
- [ ] P2: source-verify pinned immutable 27B revision, image digest, vLLM 0.32/model architecture, memory/disk and baseline API expectations before changing placeholder recipe. Candidate stays deliberately invalid until verified.
- [ ] P2: guarded prepare/start/verify/benchmark **not yet implemented**; do not authorize service swap merely because P1 passed.



## 2026-11-05 — Restore default Blazux P1 acceptance semantics

**Latest operator DGX result (2026-11-05):** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` summary from `--auto-gpu` at `805f8e3e`: source checkpoint and Hybrid are both READY, `source_issues=[]`, `hybrid_issues=[]`, 11 indexed source and Hybrid shards resolved, `api_model_ids=["qwen3.8-flash-next"]`, verify and benchmark plans each READY, yet **verify action returned FAIL** and benchmark BLOCKED by verification gate. Original console suppressed the Wizard's failure evidence location because it parsed the JSON outcome only on returncode 0, even though Wizard writes evidence for returncode 2. This is an actual attempted API/GPU verification with FAIL outcome, not evidence of a broken default Blazux model. Exact failing subprobe/error still unconfirmed until raw report is examined.

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

**SOURCE/CI validation (not DGX):** `391a2844f4c8549e282eae3e266806c89801ad1a`, GitHub push and PR checks 2/2 SUCCESS, each 15 manifest + 10 inventory + 13 launcher + 1 mode + 102 P1 + 32 router = **173/173 CPU tests PASS**. Real DGX execution against this fix has NOT_RUN; prior verify FAIL remains unresolved until this new code runs.

- [x] Source: split standard /v1/completions + chat baseline from optional tool/vision probes, preserve exact per-probe failure classes and HTTP status without raw outputs, retain Wizard evidence on rc=2; let baseline PASS through to the short benchmark even if optional probes are PARTIAL.
- [x] CI/source unit and fake DGX regressions: 2/2 SUCCESS, 173 CPU tests per job.
- [ ] Operator can FIRST read the **existing** `20261105T103738Z-c4eb4031/result.json` at `actions.verify.command.stdout/stderr` to identify the original failure without re-running GPU work. Be careful of raw output before sharing.
- [ ] Only after that, `git pull --ff-only origin feature/recipe-wizard-handoff` and one `bash scripts/temporary/p1-post-download.sh --auto-gpu` to obtain per-subprobe baseline/extended status, actual evidence URI, benchmark metrics if baseline passes.
- [ ] Treat default P1 baseline and full extra feature acceptance as distinct gates; do not claim P1 complete if tools/vision or benchmark remain PARTIAL. Never restart servers or re-download assets as a response to a Wizard probe failure.


> Updated 2026-11-05 KST. **Draft PR [#1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) open, unmerged; current source CI at `43f5131` 2/2 SUCCESS (103 CPU tests/job).** Status terms are scoped. Tasks are not achieved merely because listed in a plan.

## 2026-11-05 — Completed download reported; P1 validation disagreement

**DGX operator update, 2026-11-05:** The operator explicitly confirms the NVIDIA Flash-Next download has finished. Their submitted terminal output after `git pull` to `dea7c5aa183da770b6b467288f2f6eedf8e94946` shows `bash scripts/temporary/p1-post-download.sh` produced report `/home/inlc/blazux-p1-reports/20261105T052545Z-1e6ec592/result.json`; current branch and clean tracked worktree checks PASS; no setup process found in the process scan. HTTP `/health` and `/v1/models` command exit codes are 0 **but actual served model ID was not included in the console summary**. Wizard doctor and inventory plan returned exit code 3; both P1 verify/benchmark plans BLOCKED: `checkpoint_downloading_or_incomplete`, `hybrid_not_prepared_or_incomplete`; no Wizard GPU/bench requests executed. The `checkpoint_downloading_or_incomplete` string is a **generic validation failure**, not proof that the download continues. The apparent mismatch needs read-only evidence before any setup, repair, download, switch or deletion.

- [x] SOURCE/CPU CI 2/2 SUCCESS, 138/138 tests each at `4c0041d`; previous fixture incompatibility fixed. Commit read-only `scripts/temporary/p1_cache_diagnosis.py` and invoke it from the existing one-command temporary P1 script; add synthetic tests, including master-ref fallback diagnostic and completed shards with leftover incomplete blob names. The current main-only Wizard check is deliberately left fail-closed pending evidence.
- [ ] Operator should `git pull --ff-only`, run `bash scripts/temporary/p1-post-download.sh --inspect-only` once and return the report's `cache_diagnosis` and actual `checks.models.stdout`; no `setup`, `prepare`, `serve` or automated benchmark until the discrepancy is understood.
- [ ] If diagnostics prove an auditor mismatch, fix the *specific* source predicate with CPU fixtures and rerun CI; otherwise identify genuinely missing Hybrid preparation without any competing download. Confirm the expected API model ID and actual image identity before Wizard verify/bench.

## Latest P1 checkpoint investigation — file-level facts required

**2026-11-05 P1 regression analysis:** NVIDIA's default `nvidia/Qwen3.8-Flash-Next-NVFP4` is supported by Blazux. The official `fc694b5` snapshot distributes `model.safetensors.index.json` (~31.3 MB) and `tokenizer.json` (~12.8 MB). Our new P1 audit erroneously rejected an otherwise-valid index above 16 MiB; code changed to a bounded 64 MiB maximum. **However the operator's specific issues** `model.safetensors.index.json` and `tokenizer.json` arise at the initial `_good_file` stage, *before* parsing/size checks. Thus the artificial size cap does not by itself explain the reported failures. The Hybrid marker exists, but Hybrid `tokenizer.json` also fails. Do not conflate claimed download completion with all snapshot symlinks resolving correctly; investigate metadata file existence, symlink resolution, size and repository containment first.

- [x] Fix 16MiB index-size bug, retaining 64MiB safety cap, with 17MiB-valid and >64MiB-rejected regression tests.
- [x] Expand `scripts/temporary/p1_cache_diagnosis.py` to return for each affected source/Hybrid metadata file: missing vs dangling HF symlink vs outside repo vs zero bytes vs valid, file size, and whether it exceeds the obsolete 16MiB cap. Add fixture tests for each class.
- [x] Existing single-command wrapper now reports API `/v1/models` **model IDs**, plus a distinct inspection-only vs Wizard-not-ready reason. No GPU, cache, model or Docker mutation from those source changes.
- [x] **Source/CI accepted:** `66c6c448c1922f958886fa4696c403a4b6227685`, GitHub Actions 2/2 SUCCESS, each 145/145 CPU tests PASS (15 manifest + 10 Inventory + 13 launcher + 1 executable mode + 74 P1 tests + 32 Wizard router). This is NOT DGX runtime acceptance.
- [ ] On DGX after operator's existing shell command chain finishes, `git pull --ff-only` then `bash scripts/temporary/p1-post-download.sh --inspect-only`; return **`cache_diagnosis.snapshots[*].source_metadata/hybrid_metadata`**, `api_model_ids`, and new evidence path. Only then decide if missing metadata should be repaired from its exact official revision and whether Hybrid snapshot needs a non-destructive repair. **Never re-download the 124GiB checkpoint or run `setup` as a guessed fix.**

## D-017 — Resolve false P1 audit block and exercise existing GPU service

**Operator DGX facts (2026-11-05):** The latest post-download diagnostic returned `api_model_ids=["qwen3.8-flash-next"]`, `refs/main=fc694b54fb0174e0913e6adf86691ef85a4ead47`, 0 incomplete HF blobs, a source index and tokenizer that are **existing nonempty symlinks whose targets resolve outside the model repository**, and a Hybrid tokenizer with the same layout. The Hybrid index is a normal 31,907,813-byte file and the `.prepared` marker exists. These observations show the previous `TARGET_OUTSIDE_REPOSITORY` reason is a **new P1 checker policy stricter than Blazux's original `os.path.exists`-based policy**; they do not establish that any metadata is missing. Previous plans were blocked before actual GPU verification or benchmark. The user explicitly allows non-disruptive GPU compute tests to run without separate per-step approvals, provided the actual target service is confirmed. The presence of an API response means some server is listening; do NOT assume there are literally no processes running or stop/replace any service.

- [x] Restore compatibility for confirmed existing metadata symlinks without weakening shard containment; add synthetic source/Hybrid and dangling/shard escape regressions.
- [x] Add scoped `--auto-gpu` to the existing one-command temporary runner. The operator may exercise the GPU without typing any plan-hash approvals. Still require actual model identity, current successful Wizard plan + double-checked plan ID, and verify PASS before benchmark. It never starts/stops a container, repairs Hybrid, changes model, or downloads anything.
- [x] GitHub SOURCE/CPU CI verified at `0063b0e004902408f980c155076c098d49d4569e`: push and PR jobs both SUCCESS, 155/155 CPU tests per job. No GPU PASS claim until operator results.
- [ ] Operator: `git pull --ff-only`, then `bash scripts/temporary/p1-post-download.sh --auto-gpu`. Return `~/blazux-p1-reports/.../result.json` summary including `plans`, `actions`, `api_model_ids` and new `cache_diagnosis`. If still BLOCKED, diagnose *new explicit issues*; no blind `./flash setup` or cache purge.

## CONFIRMED IMPLEMENTATION ORDER — Wizard is the mandatory operator entrypoint

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

P1 **not yet complete**: current Wizard only supports read-only `00-doctor.sh` / `10-plan.sh`. Next coding milestone is Wizard-driven Flash-Next prepare/build/launch/health/bench/artifacts with no implicit mutation and mock CPU tests. **P2 only after P1 DGX benchmark evidence**; P3 only after both model baselines; P4 optional and separate exact deletion consent; P5 Orcarouter follows P4 decision (skipped if not needed). Keep external `:8000/v1` stable across switches and record actual served model ID. One large GPU model active at a time. Do not use SGLang.

## 2026-11-05 large P1 code batch / current operator action

**2026-11-05 operator-provided DGX terminal log (not directly observed through an SSH tool):** GB10/aarch64, Docker 29.6.2, 121 GiB unified memory (117 GiB available then); read-only Wizard Inventory showed no host :8000 collision and no `qwen38-flash` container, and initially 580,134,281,216 bytes free. The existing OpenWebUI and Portainer containers were running; preserve both. `./flash setup default` finished building `qwen38-flash-dgx:v0.32` (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`). The final log line showed **model download 9/25 = 36%**, NOT completed weights/Hybrid. The user's shell also entered `./flash serve default`, `./flash wait`, `./flash test` after setup, so these may run automatically after download/preparation. Do not compete with, modify or restart this running operator setup chain. Port availability and download progress can change after the log timestamp.

- **Source committed:** P1 Wizard `wizard/p1.sh` interactive/noninteractive mode plus pinned snapshot/image audits, plan-hash gate, guarded Hybrid preparation/start/wait, API verification and bounded sequential SSE benchmark with local JSON evidence. `tests/test_p1_*_cpu.py` added; CI at c625a49 verified 2/2 SUCCESS, 80/80 tests per job; DGX Wizard/API/bench NOT_RUN.
- **Immediate next:** fix new CPU/CI failures if any, no active DGX work. The operator's `./flash setup default` is already downloading and has queued later `serve/wait/test`. When it ends, inspect Wizard status and adopt any existing running service. Do not rerun setup or delete the cache.
- **Exit gate still unchecked:** Real P1 Wizard execution and DGX API/benchmark PASS (including tool/vision) and rollback verification. Source-only CI does not close P1.

## New implementation contract — modular Wizard before P1–P7 live testing

**User decision (2026-11-05):** Build the **whole Wizard menu/CLI skeleton first**. Keep each P-stage in a separate `wizard/menus/pN.py`, shared CLI/router/guards in common modules, and retain a **single root `./wizard.sh`** for both guided use and direct `--stage/--action` scripting. Use stable machine-readable JSON/exit codes so the operator can run commands on DGX and return output for analysis. Do not confuse source-only menu registration with an implemented service, validated 27B model, switch, cleanup or gateway.

- [x] **W0 — Modular menu and headless CLI routing (SOURCE/CI).** P1 delegates to existing tested P1 flow; P2–P7 have per-stage status/plan interfaces and fail-closed execution. Source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe` produced 2/2 CI success, 101/101 tests/job. Follow-up source/docs commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b` GitHub CI verified **2/2 SUCCESS, 103/103 CPU tests each**, including P1 JSON guided guard.
- [ ] **W1 — Complete shared execution service and model adapters.** Add stage-specific schema/recipes/provenance checks, guarded prepare/start/verify/bench/rollback controllers as phases qualify; do not enable unverified P2–P7 operations. Exercise P1 against the actual DGX **only after the current setup and queued commands finish**, with per-action approval.
- [ ] **W2 — Real Wizard baseline acceptance.** P1 measured API and benchmark, rollback and evidence; then implement and validate P2, P3, optional P4, P5, P6, P7 in the previously locked order. P4 is conditionally skipped if capacity is sufficient.

**Direct CLI examples:** `./wizard.sh list --json`; `./wizard.sh p1 status --json`; `./wizard.sh --stage p3 --action switch --from-model flash-next --to-model 27b --json` (BLOCKED by design). Detailed contract: `docs/WIZARD-CLI-CONTRACT.md`.

## UI organization decision — domain-based menus (D-015)

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

- [x] Rename source `wizard/menus/p1.py`–`p7.py` into descriptive submodules under models/switching/storage/operations; update routing, legacy aliases, two-level interactive navigation, JSON catalog and direct CLI, plus CPU regressions. **SOURCE+CI 112/112 PASS/job twice** at `571e1c2`.
- [ ] Next model-specific implementation remains P1 actual DGX Wizard API/benchmark/rollback, then P2/P3/conditional P4/P5/P6/P7 in the existing runtime acceptance sequence. **File/menu grouping does not change stage acceptance order.**

## D-016 — User-run single-script temporary batch

- [x] Design and stage `scripts/temporary/p1-post-download.sh`, `p1_post_download.py`, source-only test `tests/test_p1_temporary_cpu.py`, README and CI. One script collects P1 diagnostic status, uses the existing Wizard for separate explicit verify/benchmark plans, and writes a consolidated report. Never runs a competing `setup`, automatic `serve` or cleanup.
- [x] New runner GitHub CPU CI VERIFIED at `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b`: both jobs SUCCESS; each ran 131 unique CPU tests. CPU CI is not DGX qualification.
- [ ] Once the operator-owned original setup/serve/wait/test process **fully ends**, operator runs `git pull --ff-only` and the one temporary wrapper. Start with `--inspect-only` if the live model state is uncertain; then use interactive TTY for independent current plan hashes if readiness is confirmed. Return reviewed `result.json` path/results; never upload secrets automatically.
- [ ] Review real P1 API/bench data (and any BLOCKED status) and update evidence/next actions before advancing. Temporary script is retired only by a later reviewed commit, not by running itself.

**Permanent rules:** `handoff/OPERATING-RULES.md` R1D and `scripts/temporary/README.md`; decision D-016.

## NOW — P0, read-only/source-safe

**P1 ASSET STATE (USER_REPORTED 2026-11-05 11:46 KST):** `nvidia/Qwen3.8-Flash-Next-NVFP4` downloading **IN_PROGRESS**. Do **not** auto-download, re-download, build over shared cache, run `setup`/hybrid preparation, or launch the model while it may be incomplete. First safe work: implement full P1 Wizard orchestration using synthetic CPU fixtures; the Wizard must detect `DOWNLOADING/INCOMPLETE` vs `READY` and block serve/bench until checkpoint revision, shards and cache integrity are confirmed. On next user-reported completion, read-only verify exact snapshot and local resources before progressing. Actual DGX state, percent, completion and revision remain **NOT_OBSERVED**.


**CI regression note:** First N2+port commit `7e8f4a1` had four launch FAIL due to permission `100644` (exit 126), despite 15 schema and 10 inventory tests PASS. Script executable bits repaired in follow-up commit; check actual new HEAD CI before claiming all PASS.

**2026-11-05 priority revision (user request):** legacy services reported deleted; restore external `:8000/v1` with Blazux *NVIDIA Flash-Next* `default` profile, not Orcarouter. SOURCE changes to `flash`, `scripts/serve.sh`, `profiles/default.env` and manifest rules; N2 read-only inventory and deterministic plan implemented. **DGX state unobserved**. No setup, serve, GPU, download or cleanup done.


**N1 completed SOURCE/CPU only (2026-11-04):** JSON Schema Draft 2020-12, safe YAML loader, bounded guards and 15 isolated CPU tests PASS. 27B candidate intentionally FAIL (exit 2); synthetic valid fixture is not deployable. New PR CI requires GitHub readback at the actual commit SHA. No DGX/GPU/API execution.


- [x] **N1 — Make manifest schema machine-checkable.** Add `recipes/` and `schemas/` proposals implemented with validated, explicit repo revision, digest and immutable targets; a sample 27B placeholder must fail closed. CPU tests cover malformed manifest and unsupported engine.
- [x] **N2 — Implement read-only storage/Docker inventory.** Gather capacity and model references without changing caches, engines or services. Detect protected live service name/image/mount/port and disallow unsafe paths/names. Add `--dry-run` and deterministic plan output.
- [ ] **N3/P1 FIRST — P1 Wizard SOURCE implemented; verify CI and actual DGX API/benchmark before completion.** `wizard/00-doctor.sh` and `10-plan.sh` are read-only partial foundations. Add shared Python manager, interactive and noninteractive wrappers, exact pin/asset/disk/port validation, prepare/start/wait/API verify, benchmark and reproducible evidence export, gated approvals, rollback/failed-launch guard, deterministic dry-run, mock CPU tests. **No GPU readiness claim until actual Wizard execution on DGX**.
- [ ] **N4 — vLLM 0.32 27B source feasibility audit.** Determine exact architecture mapping, NVFP4 quantized output head, vision input, GDN, kernel/sm_121 constraints, context, MTP OFF baseline and DFlash2 scope. Record precise pinning and file/line evidence; **do not copy SGLang launcher**.
- [ ] **N5 — Integrate existing Orcarouter feature deliberately.** Review `feature/orcarouter-bf16-adapter` docs/commits, resolve against manifest contract, then merge/cherry-pick only after explicit integration/test plan. Preserve PLE/MTP count/dtype guards.

## THEN — ordered Wizard milestone gates (DGX operation requires scope-specific approval)

- [ ] P1 **Wizard** Flash-Next installation → preparation → start → API checks → pinned benchmark → artifact/evidence export. Requires DGX PASS for exit.
- [ ] P2 **Wizard** 27B feasibility source/CPU GO → install/start → API/benchmark/evidence on DGX. Requires DGX PASS for exit.
- [ ] P3 **Wizard** Flash-Next ↔ 27B repeated bidirectional switch on stable :8000, readiness check, rollback and failure injection.

## AFTER — independently gated

- [ ] P4 **Wizard** optional Flash-Next checkpoint cleanup **only if space is insufficient**; after P3 verified, dry-run exact paths/shared reference check, preserve fallback + get explicit exact approval. **Otherwise SKIP without treating it as a failed stage.**
- [ ] P5 **Wizard** Orcarouter-Flash-Next direct BF16 PLE MTP OFF → verified 31/31 BF16 overlay MTP2, install/start/API/benchmark/evidence.
- [ ] P6 **Wizard** Orcarouter ↔ 27B repeated bidirectional switch and rollback with stable :8000 and validated model IDs.
- [ ] P7 **Wizard** integrated operational acceptance: service/proxy/gateway/storage, retention, CI, numerical reproducibility, release gates, runbooks and rollback.

## Required action output format

Each completed N-step must report: file+commit SHA, `PASS/FAIL/NOT_RUN` with source/CPU/CI/GPU scope, exact commands, side effects, relevant evidence path and next blocker. Update `CURRENT-STATE.md`, `CHANGELOG.md`, and tests ledger. If blocked, retain task unchecked and add precise reason.

## Current exclusions

Current **source-only development**: no operational GPU usage; no `./flash setup` or `./flash serve` run on DGX; no image pull/build/download; no Docker stop/rm; no deletion; no SGLang. User-requested source default now targets :8000; actual port occupancy and service deployment remain unverified and require separate preflight.


## 2026-11-08 P5 resource diagnostics implementation (SOURCE ONLY; no DGX measurement)

- New non-mutating `./wizard.sh operations resources snapshot --json`, `observe --samples 3 --interval 5 --json`, and `preflight --json`. Only passive /proc, /sys, nvidia-smi query, Docker ps/inspect/stats and git rev-parse are invoked; no inference, system tuning, model restart, Docker cleanup, or GPU mutation.
- Host MemAvailable/page-cache/swap, memory/cpu/io PSI, CPU cpufreq/governors, thermal, nvidia-smi metrics where supported, Docker exact candidate identity, cgroup v2 memory, process smaps_rollup (NOT PLE-specific), NVMe cumulative counters are reported. Missing permissions/sensors => UNSUPPORTED/NOT_OBSERVED, never a fabricated zero.
- Recipe resource policy is OBSERVE_ONLY; proposed startup threshold and pressure limits are null until DGX data is measured and policy approved. Preflight returns BLOCKED_UNCALIBRATED when no approved threshold; it is not wired into live startup and does NOT grant launch approval.
- `--save` opt-in writes a 0600 evidence JSON under `~/.local/state/blazux-wizard/resource-diagnostics/`. Default snapshot is write-free. These are SOURCE-only changes pending real DGX data and CI.
- YSLAB pinned 9492b78 applies a static 100-GiB pre-launch MemAvailable check and mmap/no-prewarm; it does not establish approved thresholds for this vLLM 0.32.0 Orcarouter deployment. P8 recovery and operator-authorized hard resource controls remain excluded.
