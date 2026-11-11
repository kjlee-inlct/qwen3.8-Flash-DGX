## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-12 P5-D actual DGX result

**Verified source identity:** operator-run Orcarouter v3 `qwen38-orcarouter-qsa62318-lmhead-v3` (adapter `qwen4exp-qsa62318-lmhead-v032-v3`, previous `lm_head.weight_scale` fix), API :8000, DEVELOPMENT_TRIAL. **This is an operator-provided receipt, not a new GPU/API test by GitHub.**

Operational invariant: a generic Wizard exit 3 for `OBSERVED_PID_SETS_CONSISTENT_NOT_AUTHORIZED` or `BLOCKED_PARTIAL_PROCESS_EVIDENCE` **is not a service-down signal**. Record exact issues and unsupported PID probes; independently verify Docker container and localhost API before outage claims. Host PID `ss` limitations may be Docker NAT/docker-proxy, permissions, or environment—cause **unproven**. Do not restart service, change network privileges, switch models, run inference, or promote/release on this result. P5-D completeness waits until P8, P6-E source work can advance.

[Actual P5-D evidence and PID-limitations runbook](../docs/P5-D-P6-E-READ-ONLY-PROVENANCE-JOURNAL-V2-20261110.md) · [P5–P8 operating scope](../docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md)

**Safety boundary:** ONE_ACTIVE_MODEL_ONLY; vLLM 0.32.0; no SGLang, startup/shutdown, inference, port/cgroup/governor change, journal migration, auto-recovery or PR merge. Draft PR #1 unchanged. See the runbook for exact PID evidence and historical timestamp.

---

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

## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-08 (v3 live PASS, safe resource work next)

**LATEST DGX RESOURCE EVIDENCE (2026-11-09 00:43 KST, operator log):** v3 running, 30.18 GiB MemAvailable / 121.63 GiB total, swap used 1.31 GiB, memory PSI avg10=0; Docker 7.157 GiB versus cgroup 25.54 GiB (cache split NOT YET MEASURED), peak 37.02 GiB, cgroup OOM=0. GPU memory N/A is expected on GB10 UMA. 13-second idle observation only, NOT loaded stability acceptance; preflight BLOCKED_UNCALIBRATED is expected. **Do not apply memory cap or 100 GiB admission gate.** New source-only cgroup memory.stat/Swap churn diagnostics must receive fresh DGX read-only evidence. [P5 technical record](../docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md).


**NEW SOURCE-ONLY RESOURCE DIAGNOSTICS — 2026-11-08:** `./wizard.sh operations resources snapshot --json`, `observe --samples 3 --interval 5 --json`, `preflight --json` implemented with CPU/Fake-DGX CI; declared `OBSERVE_ONLY` P5 recipe policy. No DGX measurements obtained in this source session, no live service changes or resource limits applied. Preflight is NOT wired to launch, returns `BLOCKED_UNCALIBRATED` without approved threshold. Optional `--save` creates private 0600 JSON evidence. See [P5 adoption notes](../docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md), keep trial v3 and port 8000 untouched.


Read [complete document audit](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) and [active P5 runbook](../docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md), as well as [latest CURRENT-STATE](CURRENT-STATE.md) and [EVIDENCE-LEDGER](EVIDENCE-LEDGER.md). All pre-v3 procedures below are historical, not the current run instructions.

**Latest actual operator evidence:** adapter `qwen4exp-qsa62318-lmhead-v032-v3` fixes `lm_head.weight_scale`; `./wizard.sh p5 trial verify --json` returned **`PASS_LIVE_INFERENCE`** with `READY`. `./wizard.sh service manager status --json` returned **`LIVE_P5_TRIAL_API_VERIFIED`**, model ID `qwen3.8-flash-next-orca-uncensored-bf16`, v3 trial container `qwen38-orcarouter-qsa62318-lmhead-v3` running on :8000. Operator-approved failed-trial cleanup **completed PASS**: exited old candidates `qwen38-orcarouter`, `qwen38-orcarouter-qsa62318`, `qwen38-orcarouter-qsa62318-lmhead` deleted after logging to `~/.local/state/blazux-wizard/p5-live-trial/cleanup/`. Do **not** repeat deletion or stop running v3. Old images/checkpoints/caches preserved. Actual CPU/GPU memory pressure and CPU clocks have **not** been measured; test service is not production released.

**Current highest priority:** read-only DGX capacity/performance safety baseline first (MemAvailable, MemTotal, swap, page cache, PSI, cgroup memory, PLE NVMe I/O, CPU frequencies, thermal/power). YSLAB pinned commit `9492b78c6bc04638587b42f2ffeb0680b0fcb3ef` offers a pre-launch 100 GiB MemAvailable gate, mmap PLE/no prewarm, 0.80 GPU memory profile, 32 gather workers and MemAvailable/swap stability probe, **not an identified CPU frequency cap or automatic memory-pressure protection**. Current Blazux MTP0 is 0.70 GPU utilization, 16 workers, 8192-token context, 1 sequence; do not copy reference defaults without Blazux-vLLM0.32 evaluation. Any CPU clock/governor/system memory/Docker limit change needs separate operator approval. After non-disruptive verification, implement recipe-owned resource policy, then explicitly approved canonical `qwen38-orcarouter` (Orcarouter Flash-Next) lifecycle promotion and separate MTP2/Tools/Vision/Benchmark. P8 fault recovery remains deferred. Fixed vLLM 0.32.0, no SGLang, ONE_ACTIVE_MODEL_ONLY, port 8000. Draft PR #1 Open/Unmerged.

---

## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-08 (QSA #62318 + LM-head v2)

**Read these before following historical commands:** [complete 168-item initial document review (169 including the new v2 runbook; audit file added afterward)](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) and [current P5 v2 DGX Runbook](../docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md). (For links from `docs/`, the authoritative paths are `docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md` and `docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md`.) These supersede old QSA-only trial commands, old P4/P5 starter prompts and earlier claims that P5 was never attempted.

**Latest actual operator-provided DGX evidence:** checkout `247d31d`, previous QSA-only container `qwen38-orcarouter-qsa62318` exited(1) after loading reached **15/17 safetensors shards**; hard failure `lm_head.weight_scale` not registered on `Qwen4ExpForCausalLM`. Receipt `~/.local/state/blazux-wizard/p5-live-trial/trial-20261108T054106528164Z.json`: `FAIL_NO_ROLLBACK`, `gpu_verified=false`. Original `qwen38-27b` exited(0); :8000 was unserved **then**. This is not a new live check.

**Current GitHub candidate:** isolated composite adapter `qwen4exp-qsa62318-lmhead-v032-v2`, image `blazux-p5-orcarouter:qsa62318-lmhead-v032`, target `qwen38-orcarouter-qsa62318-lmhead`, `Dockerfile.p5.qsa62318-lmhead`. Previous QSA-only candidate and logs are preserved; canonical vLLM **0.32.0** base unchanged. Source/CPU CI for code commit `9e7cd1b` passed ([push 42473176346](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42473176346), [PR 42473180100](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42473180100)); **actual v2 image build, GPU mmap/inference, MTP2, benchmarks and production release are NOT VERIFIED**. `lm_head` quantization config vs checkpoint scale must be independently checked; a constructor source edit alone is not GPU proof.

**Still binding:** `ONE_ACTIVE_MODEL_ONLY`, host `:8000/v1`, no SGLang, no checkpoint/HF/cache/old-container deletion, no P3 replay, P4 live deletion, P6 general switch, P8 faults or PR #1 merge. P5 is an explicitly approved *development no-auto-rollback trial only*; regular service switch rollback behavior has not been changed. Treat all older sections below as timestamped historical evidence.

---


## 2026-11-08 — P5 pinned LM-head checkpoint preflight (NEW SOURCE, NOT GPU QUALIFIED)

- In addition to the current v2 QSA + LM-head adapter, `scripts/manager/p5_lm_head_checkpoint_audit.py` now audits the **actual local pinned HF snapshot** read-only: `config.json` quantization groups/ignore, safetensors index keys, and bounded `lm_head.weight` / `lm_head.weight_scale` headers (shape/dtype/shard). This source work does not confirm any current DGX observation; the exact gated Orcarouter snapshot could not be read through GitHub/public-web access in this session.
- **Root mechanism verified in upstream vLLM 0.32:** `ParallelLMHead` gets its quant method via `resolve_quant_method`; compressed-tensors checks `ignore` before selecting matching targets/schemes, and handles `ParallelLMHead` separately from `LinearBase`. Adding `quant_config=self.quant_config` alone does not guarantee `weight_scale` registration. If a scale exists but head is ignored or no explicit head FP8 target matches, the audit blocks; checkpoint/config is never silently rewritten.
- `scripts/manager/p5_live_trial.py` now requires a clean pinned LM-head metadata audit inside `prepare` and `plan`. `scripts/manager/p5_checkpoint_preflight.py` provides a no-Docker, no-GPU, no-network one-shot report containing manifest + checkpoint + all P5 CPU regressions. Operator-safe call after clean fast-forward: `python3 -m scripts.manager.p5_checkpoint_preflight --json`. `PASS_SOURCE_ONLY` is **not** GPU qualification. `BLOCKED` forbids preparation/planning pending source investigation.
- Added CPU/Fake-DGX regressions for FP8 group matching, ignore-scale conflict, missing scale, header/path limits, and judge safety. Latest CI must be inspected separately; original GPU evidence remains `FAIL_NO_ROLLBACK` at old QSA-only HEAD, v2 GPU build/inference **NOT VERIFIED**, `gpu_verified=false`. BF16 PLE GPU mmap, MTP0, MTP2, Tools, Vision, Bench and release are **NOT QUALIFIED**.
- Full technical sequence in [the current v2 Runbook](../docs/P5-LMHEAD-V2-DGX-GPU-TRIAL-RUNBOOK-20261108.md), with [the exhaustive historical document audit](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md). Preserve vLLM 0.32.0, port 8000, ONE_ACTIVE_MODEL_ONLY, all historical receipts/failed containers/cache, PR #1 Draft/unmerged. No unapproved DGX GPU execution, Docker mutation, P3/P4/P6/P8 work or production release.


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

## 2026-11-08 P5 source-only update: format-generic PLE, external DGX Spark evidence

Current code HEAD `d395368`; [CI #42436269922 SUCCESS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42436269922). PLE asset manifest schema v2; seven-document shared registry adds separate loader/ABI capability profile (Blazux vLLM0.32 GB10 remains NOT_QUALIFIED). BF16 Orcarouter remains pinned, but model-dependent FP8 and other formats, per-table BF16 scalar scales, independent memory placement and MTP controls are represented. Switching preview requires old PLE mmap and GPU release, :8000 free, image/loader ABI requalification, PLE format compatibility and rollback. See `docs/P5-PLE-FORMAT-AND-DGX-SPARK-REFERENCE-ADOPTION-20261108.md` and external [dolf3131 pinned 45e3d477](https://github.com/dolf3131/dgx-spark-llm-serving/tree/45e3d47771577dabab0998e9013e85dd0915ae4f), [NVIDIA DGX Spark forum](https://forums.developer.nvidia.com/t/nvidia-official-qwen3-8-flash-next-checkpoint-for-single-dgx-spark/385994). External B12X images, unmerged patches and floating tags are NOT compatible substitutes for vLLM0.32 without validation.

The operator permits development DGX 27B downtime and GPU use now. Do not treat this as completed GPU load or release: the user-provided pre-refactor log showed PLE BF16 128 PASS, MTP donor 31/3-hash PASS, active 27B served at :8000; this session only used GitHub, no live DGX operations. P5 GPU execution still explicitly disabled until pinned loader/rollback readiness; keep one active GPU model, port 8000, old cache/models/images/journals, Draft PR unmerged. Next safe commands: `./wizard.sh manifest validate --json`, `./wizard.sh model list --installed --json`, `./wizard.sh p5 doctor --read-only --json`, `./wizard.sh service manager status --json`. Never replay P3, execute P4 deletion or P8 fault tests without their individual gating.

---

## 2026-11-08 — Wizard shared manifest registry / Orcarouter BF16 PLE asset (READ-ONLY)

Implemented `runtimes/manifest-registry.json` and shared `scripts/manager/manifest_registry.py`: schema-1 strict bounded JSON, duplicate/nonfinite/symlink rejection, cross-checks for service-policy, model-discovery, canonical 27B recipe, unqualified Orcarouter recipe, pinned YSLAB compatibility and new `runtimes/ple-assets.json` PLE asset. PLE ID `orcarouter-bf16-ple` is referenced consistently in P5 recipe, service policy, model discovery. Common `scripts/manager/ple_assets.py` validates pinned 128 BF16 table headers, 320001536 rows and width160; its metadata PASS is **not** mmap/GPU PASS.

Wizard `manifest status|validate --json`, `model list --installed --json`, `p5 status/doctor --json`, `service manager status --json` and model-first selector expose manifest/PLE registration and independent observed state. No hidden asset movement, image build, start/stop, deletion or model switch. Initial code commit [a17b3618](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/a17b3618fab98aa5b849359d464c0d7698fae4a0) passed [CI #42433160630](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42433160630): 996 executed CPU test cases across 44 invocations (duplicates included). Follow-up model-selector/docs requires CI separately.

2026-11-08 operator-provided DGX `8f8ad0c` evidence: 27B `LIVE_SERVICE_VERIFIED` at :8000, Orcarouter PLE 128 BF16 tensors PASS, MTP donor 31 tensors and three pinned SHA256 PASS; the **new registry code was not run on DGX**. Actual Orcarouter runtime/MTP2/API/benchmark/restore NOT_RUN, release false. Preserve 27B, all HF caches and receipts, :8000/ONE_ACTIVE_MODEL_ONLY, OpenWebUI/Portainer. No P3 replay, P4 deletion, P6 transition, P8 fault/recovery or Draft PR merge. Architecture and commands: `docs/WIZARD-MANIFEST-REGISTRY-AND-PLE-ASSETS-20261108.md`.

---

## 2026-11-08 — P5 SOURCE implementation and CPU/Fake-DGX acceptance

The P5 source batch was committed as [33adec1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/33adec182e97a8eac0d5584bdf73f1448bdd84f2); [GitHub Actions 42429745463](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463) **SUCCESS**, including 20/20 P5 CPU tests and integrated one-shot `--cpu-only --json` PASS. It implements the pinned P5 candidate recipe, imported licensed YSLAB metadata/immutable-overlay source tools, direct BF16 PLE and three-donor/31 BF16 MTP audits, separate MTP0/MTP2 candidate profiles, Wizard stage and safety gates, `scripts/temporary/p5-one-shot-acceptance.sh`. A subsequent source enhancement adds detailed per-case CPU JSON and profile preview and must pass its own CI.

**Not runtime-qualified:** actual Blazux vLLM 0.32 CUDA/quantized-lm-head/compressed-tensors/MTP loader ABI, on-DGX PLE and donor audits, overlay generation, GPU model loading, native Tools, streaming, benchmarks, strict numerical parity and 27B restoration are **NOT_RUN**. Vendor overlay *code* included but no CLI execution/asset write approved. The recipe has `launch_allowed=false`, `register_as_runtime_recipe=false`, unknown runtime image ID. `--gpu-trial` always BLOCKED, no execution approval generated. Preserve existing 27B at :8000, single-model service, HF caches, other images, WebUI, Portainer; do not replay P3, delete P4 assets, start P6/P8 or merge Draft PR #1. Actual DGX is not connected to this session. Read-only runbook: `docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md`.

---

## 2026-11-08 — P5 reference integration scope and safety authorization

P5 source implementation is authorized for the NEXT conversation: adapt YSLAB BF16PLE and Orcarouter MTP mechanics into Blazux vLLM 0.32 **without** replacing its base image/control plane, changing :8000, or violating `ONE_ACTIVE_MODEL_ONLY`. No SGLang. Preserve NVIDIA/RadixArk/27B existing defaults. Gated HF auth must never appear in logs; pinned sources/derived views must remain immutable with explicit revisions and hashes. Distinguish MTP OFF and MTP2, and keep numeric strict `1e-4` release gate unresolved until real comparable evidence.

**Allowed source work:** code, recipe/manifest, CPU/Fake-DGX, bounded read-only inspection, dry-run/plan, CI, docs and Draft PR body updates. **Separately approved operations only:** download or writing large HF/derived assets, Docker image build if it mutates actual DGX, starting/stopping 27B/Orcarouter, GPU trial and benchmark, changing :8000 owner, any P4 deletion or invasive recovery. No automatic approval token, no Docker prune, no P3 replay, no P6/P8 real execution, no PR merge. The one-shot script must never escalate read-only mode into GPU or deletion without a fresh exact plan/TTY downtime approval.

Next handoff: `handoff/START-NEXT-P5-20261108.md`. This **does not** retroactively grant a live P5 trial; old P4 prohibition below is superseded only for P5 development.

---

## 2026-11-08 — P4-B/C source-only scope; no live cleanup

Only P4-B reference/candidate **review** and P4-C **in-memory transaction rehearsal** have been authorized. Review fingerprints are not execution approvals. `P4_C_LIVE_EXECUTION_RELEASED=False`, and no production deletion adapter exists. The separate operator must establish an actual P5 operational issue or P8 acceptance need, exact resource identities, model/cache/blob/dependency audit, rollback, fresh TTY approval, runtime acceptance and postchecks before a future live cleanup adapter may be introduced. Never run Docker/HF/volume prune, delete stopped Flash reference or active 27B, alter the API service, automatically start P5/P8, or merge the Draft PR. Older P4-B/C NOT_STARTED markers are history for the **source development** scope only.

---
## R1AC — 2026-11-08 — P4-A read-only inventory authorized; no cleanup inferred

P4-A may inspect Docker container/API inventory, `docker system df`, configured/mounted HF caches and known model repository directory allocated sizes/free space with bounded no-shell read-only commands. Redact host paths, env and private resources. Report Docker reclaimable as unverified estimates and avoid adding model repo + parent cache totals. Model storage sizes are not verified safe-reclaimable bytes; P8 real Flash reinstall/rollback may require those cached assets. **No P4-B candidate decisions, P4-C execute/approval, Docker stop/start/rm, image/prune, cache writes or model switch** without later explicit user instruction and fresh per-action consent. P3 E/F source-level closeout is complete, but P8 production acceptance remains pending.

---

## R1AB — 2026-11-08 — P4 no-start instruction and P3/P8 scope boundary

No P4 source code, inventories, cleanups or container/storage activities without fresh explicit user authorization. P3-E is source draft and bounded read-only host evidence; P3-F is CPU/Fake-DGX source proof with production lock. P8 exclusively owns independently approved real Flash reinstall, lifecycle release, injected fault/automatic recovery and final signoff. Preserve vLLM 0.32, one active GPU model, :8000, HF caches, 27B canonical recipe and historical P3 receipts. `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`.

---

## 2026-11-08 — P3-E real DGX Flash host asset preflight blocked; diagnostic patch/source CI

**Actual operator DGX evidence, no Docker mutation:** `python3 -m scripts.manager.flash_host_assets --json` returned `status=BLOCKED`, issue `FLASH_HOST_ASSET_PREFLIGHT:ValueError`, `legacy_hf_bind_writable=true`, `indexed_shard_count=0`, `metadata_sha256={}`, `template_sha256=null`, `verified_model_revision=true`. This only establishes that the **old observer** advanced past pinned command/env/cache bind, then raised a ValueError during an unidentified local-file validation step. Neither zero shards nor `verified_model_revision=true` proves a missing model or verified revision bytes. **No user-provided evidence of broken inference or failed reinstall.**

**Source fix, not live DGX proof:** [9beb1d3](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/9beb1d3f73675ac4a22daedfc2167b380742305c) adds allowlisted `failed_stage`, `failure_reason_code`, `pinned_command_identity_matched`, `prepared_view_path_observed`, and stops falsely setting `verified_model_revision=true` from a directory name alone. Private exception messages/path/env values are never emitted. Tests cover metadata cap, malformed index, empty/missing/escaped marker, secret exception redaction. GitHub Actions [42391221418](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391221418) **SUCCESS: 874/874 CPU/Fake-DGX tests across 39 groups** (previous 870 + 4). Real DGX did not run this patch yet.

**Next safe operator command:** `git pull --ff-only origin feature/recipe-wizard-handoff`; then `python3 -m scripts.manager.flash_host_assets --json`. Inspect only redacted `failed_stage` and `failure_reason_code`. No cache repairs, container recreation, GPU activity or permissions escalation should follow from this result without separate evidence/approval. Flash canonical reinstall remains unqualified, lifecycle release disabled, historic P3-G real PASS/CLOSED and P8 NOT_RUN; preserve 27B at :8000.

---

## R1AA — 2026-11-08 — P3-E bounded Flash host inventory is observation, never authorization

`python3 -m scripts.manager.flash_host_assets --json` is **read-only** and must not invoke Docker create/stop/start/rm, model downloads or HF cache writes. A complete local metadata/template SHA-256 and indexed-shard presence check do not verify large-weight integrity, full Config/HostConfig/Env semantics, Docker registry provenance, restart/network/security policy or new container GPU execution. Never print or commit raw environment values, host paths, template contents or private Docker inspect payloads. A failing asset check is not a reason for automatic repair or retry. All model changes need a distinct fresh SHA, explicit TTY approval and recoverability review. P8 fault/automatic restore remains independently gated.

---

## R1Z — 2026-11-07 — Fake-DGX stop/start/rollback simulation NEVER authorizes runtime

`p2_27b_tool_cutover_simulation.py` is an isolated pure-injected simulation with NO production adapter or executable Wizard command. Its SHA and acknowledgements are intentionally domain-separated **simulation-only** and must never be accepted by any real DGX executor. It models failure/restoration paths for CPU tests, not actual journal integrity or validated Docker behavior. GitHub 722 CPU PASS on `fe4e6b01` is SOURCE ONLY; actual native tools and safe live rollback remain unqualified. Continue preserving original NVIDIA 27B, Flash, caches/receipts, single-model :8000, vLLM 0.32, no SGLang, no P3 replay, no release-gate flip.

---

## R1Y — 2026-11-07 — Native Tools V1 source-only candidate is not deployment consent

The new distinct `qwen38-27b-native-tools-v1` source candidate uses the same pinned NVIDIA 27B and served ID but a different container name; never reuse or remove preserved `qwen38-27b`. Read-only `--tools-variant-plan` returns exit code 3 intentionally, even on a clean preflight; its fingerprint and argv are NOT executable approvals. New `--tools-stream-probe` makes bounded local inference, not Docker changes, and cannot by itself qualify Open WebUI. Candidate YAML is schema-incomplete and not registered as production. Independent parser+tokenizer qualification, variant-aware service-policy, real stop/start rollback executor, explicit new TTY downtime consent, Fake-DGX faults and actual DGX native tool checks are still REQUIRED. No source changes auto-authorize Docker, port, service, P3 replay, receipt modification, or Wizard release. Historical P3-C is immutable; keep :8000, ONE_ACTIVE_MODEL_ONLY, vLLM 0.32, no SGLang.

---

## R1X — 2026-11-07 — Source-safe P2 FINAL Tool Calling next; no implicit restart/migration

Previous operating-rule headnotes saying 27B Tool Calling is deferred are now superseded **only in priority** by D-058 and the newest DGX evidence: P2-FINAL is the next source development goal; **not** pre-approved real runtime modification. Current preserved `qwen38-27b` is serving normally at :8000, but its actual Config.Cmd omits auto-tool/parser/reasoning switches; the local tool probe returns HTTP 400. Design a **separate pinned tool-enabled 27B variant** preserving both original NVIDIA/Flash Docker container IDs, image/cache and P2/P3/operating receipts, with independently reviewed rollback and ONE_ACTIVE_MODEL_ONLY/port 8000. Avoid in-place removal/recreation, forced Docker restart or approval string automation. P3-C historical PASS is final and never rerun. New ordinary operating backend both physical directions and independent postchecks PASS, but live normal Wizard main menu still `PRODUCTION_EXECUTION_RELEASED=False` and fault-injection restore is NOT qualified. Source-only development and GitHub CI are allowed; actual inference/proxy/service changes require separately scoped operator consent. Keep vLLM 0.32, no SGLang, Draft PR unmerged.

---

## R1W — 2026-11-07 — New ordinary operating switch source complete candidate; real DGX release distinct

Binding priorities: model-centered `./wizard.sh` everyday Flash-Next↔NVIDIA 27B switching, independent preflight, exact scoped approval, stop-before-start, verified API+bounded chat, evidence and safe best-effort rollback. Defer 27B Tool Calling / Open WebUI and Orcarouter until separately requested. Keep P3 A/B/C immutable as historical provenance; never reuse their plan IDs or repeat one-off stages. New source-only normal UX is production `PRODUCTION_EXECUTION_RELEASED=False`, while a dedicated one-switch DGX acceptance route offers `--plan` by default and separately approved `--execute` with four manually typed TTY inputs; no unattended `--execute --json`, env approval overrides, forced plan reuse or automatic reverse switch. Do NOT treat generic source-development permission as consent for current 27B downtime. Actual user controls trial separately under `docs/OPERATING-SWITCH-DGX-ACCEPTANCE-RUNBOOK-20261107.md`; any unverified journal, model identity or rollback blocks subsequent switching. Original vLLM 0.32, single GPU model, API port 8000, active 27B, preserved Flash, HF cache, P3 private receipts, Draft PR unmerged remain binding.

---

## R1V — 2026-11-07 — P3 최종 PASS 이후 일반 운영 UX 개발, one-off 전환 재실행 금지

실제 DGX P3-A/B/C 전환이 모두 실행/검증되었고 최종 활성 모델은 **NVIDIA 27B :8000**. 원본 Flash 컨테이너/이미지/HF cache 및 27B 자산, 기존 canonical P3 journal/receipt/attempt marker를 그대로 보존한다. 아래 과거의 'P3-C 준비·별도 승인·NOT_RUN'은 **당시 승인 경계 기록**이지 완료된 Stage C를 다시 실행하라는 지시가 아니다. P1/P2/POST-B/P3 재시험·Flash 복귀·27B 중단은 새 작업 목적 및 신규 승인 없이는 금지.

`./wizard.sh` 메인 UI의 stage 선택은 `--plan`만 호출하므로 **P1~P3의 CLI/backend 검증 PASS와 최종 사용자 Wizard UX PASS를 혼동하지 않는다**. 다음 소스 목표는 모델 선택→신규 scoped 승인→일반 반복 전환→API 확인을 사용성 좋게 연결하는 것. 완성 전에는 P3 one-off `stage-a/b/c`를 일반 운영 전환에 전용하지 않는다. 대시보드는 actual canonical 증거, 실시간 API, 운영/UX 인수증을 구별해야 하며 정적 PASS 또는 정적 NOT_QUALIFIED로 실제 증거를 대체하지 않는다.

최신 [P1–P7 acceptance snapshot](../docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md), [new conversation starter](SESSION-START-PROMPT.md). 모든 변경은 기존 브랜치와 Draft PR #1에 코드/CPU 테스트 후 CI/문서 동기화. 실제 GPU/서비스 downtime/cleanup은 새 별도 승인. Docker 이미지/컨테이너/모델 파일/cache 증거 삭제 및 무단 머지 금지.

---

## R1U — 2026-11-07 — P3-C APPROVAL PLAN TIME WINDOW ROTATION IS READ-ONLY UNTIL NEW THREE MANUAL ACKS

The canonical Stage C SHA expires at the next 10-minute UTC bucket. Previous user attempts near the window end were BLOCKED/pre-dispatch, not a failure of model health. The temporary `--execute` wrapper MAY wait at most 150 seconds using only `service manager status --json` and canonical `stage-c --plan --json` to obtain a NEW, DISTINCT, fully qualified SHA with >=120s before expiry; `--plan` remains immediate and read-only. This wait is strictly pre-authorization; it MUST NOT execute the switch, rotate a previously typed SHA, script or pipe approval strings, auto-approve downtime, or run new benchmarks. If the source Flash API/model/images/27B CID/P1 or P2 evidence/Git state change, or SHA changes ahead of its expected time boundary, or wait times out/interrupted, fail closed and preserve service.

After read-only rollover, old plan and any prior approval are discarded; prompt a fresh exact SHA (no brackets) plus exact independent `I_ACCEPT_FLASH_NEXT_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. After typing, re-observe and require matching typed plan; canonical Wizard must re-check independently under original lock and own recovery logic. On success keep 27B running on port 8000 and preserve original Flash container/image/HF cache. Do not update canonical P3 approval schema or bypass attempt markers. Source/CPU CI is distinct from actual DGX service proof.

---

## R1T — 2026-11-07 — Git BENCHMARK RESULTS MUST BE ALLOWLISTED, NOT RAW

Model-based operator benchmark publications belong under **Git-tracked** `benchmarks/published/<served-model-id>/<original-sha256-prefix>.json` and index `benchmarks/published/README.md`. Source raw JSON under original `~/.local/state/blazux-wizard` or ignored `reports/` stays immutable, PRIVATE and never committed. Published fields only: stable model ID/repository/revision, explicit runtime, report timestamp, original raw SHA256 digest, exact bounded profile, benchmark and actual service-restoration outcome, allowlisted numeric throughput/TTFT/latency, and interpretative measurement limitations. NEVER publish original prompt/output, cache/log host filesystem paths, network/API endpoints, container IDs, plan IDs, user tokens, approval acknowledgments, keys, configuration secrets, memory telemetry, or complete raw execution JSON. Never confuse 27B client E2E throughput with decode proxy or standardized head-to-head model comparisons.

Future export is user-reviewed, one original private receipt at a time: `python3 -m scripts.manager.benchmark_publication --model ... --source ... --plan`; `--write` requires explicitly matching current original source SHA256 and does not stage/commit/push. Existing published summary can only be verified or blocked on mismatch, never overwritten. Read-only original-file verification is `bash scripts/temporary/verify-published-benchmarks.sh`. CI tests exercise whitelisting and privacy; CI cannot validate original DGX receipt bytes not in Git. Any discovered mismatch blocks claiming full machine verification until reconciled.

P3-C executed **NO** service transition in recent user log: exact SHA was typed with leading `[`, returned CANCELLED/executed=false/dispatched=false; plan readiness PASS does not grant downtime. Preserve current Flash-Next and explicit C approval policy.

---

## R1S — 2026-11-07 — P3-C TRANSITION REQUIRES TRACKED OPERATOR + THREE NEW TTY ACKS

Original D-016 agreement: agent may commit tracked operator-only scripts, tests, permanent docs and source CI on existing `feature/recipe-wizard-handoff`; **actual DGX source changes require clean fast-forward pull by operator**. No agent-initiated Docker stop/start/GPU benchmark, no PR merge. Latest DGX canonical C `--plan` showed READY/issues=[]/P1 evidence PASS, original Flash/27B identities unchanged. That is **NOT** authorization for actual Flash downtime. Historical C SHA `d5f200ff...` expires in the original plan window. Optional `evidence migrate --guided` was CANCELLED/copied=0 by typing `COPY`; it is NOT a C prerequisite and never authorizes it.

New `scripts/temporary/p3-stage-c-operator.sh` defaults `--plan` (read-only), creates unique 0600 Git-ignored project report, leaves original P3 stage receipts, lock, journal and model files unchanged. `--execute` is exclusively operator-initiated after separate consent, requires a real TTY and manually input **CURRENT** exact stage-C SHA + **`I_ACCEPT_FLASH_NEXT_DOWNTIME`** + **`I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`**. The controller checks A/B original receipts, current Flash live identity, preserved exact 27B container, P2 receipt SHA and P1 post-B Verify/Benchmark/diagnostics SHA; refuses expired/rotated plan. It only dispatches canonical Wizard stage-C. Core C expects **no** `--enter-p3` (null) while the wrapper independently requires the third C-specific input. Stage-C success additionally requires immutable `stage-c.json` and live 27B `:8000/v1` identity, preserving original Flash for rollback. Any ambiguous result is NOT success and forbids blind retry. No automatic P3 post-success stage or Flash switch-back. See [operator runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## R1R — 2026-11-07 — READ-ONLY HISTORY + EXPLICIT P2/P3 COPY, P3-C SEPARATE AUTHORIZATION

The model history command and integrated Wizard menu are READ ONLY: no CUDA, inference, health check, service or Docker commands. Scan private bounded JSON records from declared legacy and new report directories; dedup by immutable SHA256 and report unreadable/untrusted files. Model names come from `runtimes/service-policy.json` not internal rollout stage numbers. 27B throughput reports separate E2E and decode proxy; do not compare it unqualified with Flash direct throughput.

Import is a separately approved COPY-ONLY operation, not service migration: `./wizard.sh evidence migrate --plan` then optional `--guided` requiring current full plan_id. Plans are rehashed immediately before execution. Use O_EXCL, 0600 immutable JSON and private 0700 project directories. Do NOT copy mutable P2/P3 locks/journal/state/attempt markers or .target.log, do NOT delete originals, and do NOT silently switch the canonical P2/P3 paths. Any partial/invalid/mismatched copy BLOCKS review, never overwrite. Imported files are Git-ignored local artifacts, not synchronized backups. Phase-2 native P2/P3 report mirrors and phase-3 active state relocation are postponed pending independent design/recovery qualification.

Original actual P3-B + post-B P1 Verify/Benchmark evidence remains valid as previously supplied. P3-C currently NOT_AUTHORIZED, NOT_RUN. Next operator action is fresh `./wizard.sh switch flash-next-27b stage-c --plan --json` (read-only), after source CI+clean pull; only if all gates READY and the operator separately approves Flash downtime can stage-C execute through the canonical guarded switch. Never infer live approval from prior test results or historical stage A/B plan IDs. See [contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md).

---

## R1Q — 2026-11-07 — Model-centric UX change; actual post-B P1 PASS and private evidence continuity

Operator ZIP contains actual POST-B P1 Verify PASS (baseline/extended plus all four functional probes) and 3-request numeric Benchmark PASS, distinct fresh action SHA approvals; the latest earlier read-only doctor/inventory rc=3 diagnosis PASS for the original Flash own-name/own-port collision. These facts supersede old P1 NOT_RUN entries. They **do not** grant P3-C downtime authorization. Keep Flash-Next service API :8000 active, ONE_ACTIVE_MODEL_ONLY, vLLM 0.32, SGLang unused.

Roll out UX source only after CPU CI and a clean DGX fast-forward pull; no hidden inference re-runs, service transitions, cleanup, or PR merge. Operator-facing Wizard menus show model/action instead of P1/P2/P3 and repeat exact current SHA in the approval prompt, retaining rechecked action-specific approval. Future P1 JSON receipts write append-only, 0600 into ignored `<repo>/reports/models/qwen3.8-flash-next`; historical `~/.local/state/blazux-wizard/p1` never moves or gets overwritten. P3-C gate checks both roots and latest finish timestamps including failures. P2/P3 state and locks must **not** be naively relocated; their readers require a separate staged migration and CPU/fake-DGX tests. See [contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

## R1P — 2026-11-07 — P3-B ACTUAL PASS; POST-B P1 is the only current work

Supersedes historical R1O/R1N "B pending, 27B active" positions: real DGX operator returned `P3_B_PASS_FLASH_NEXT_ACTIVE`, executed/live verified by canonical stage-B and a separate Flash API check. Flash-Next is the latest verified active model, API `:8000/v1`. P3-A/B **must not be repeated**. Do not retroactively edit the historically misnamed old P3-B report or infer failure from its stale `approval_accepted=false` field.

D-016: GitHub source + Fake DGX CPU tests + CI + tracked docs first, then clean DGX fast-forward pull and **one** read-only `bash scripts/temporary/p1-post-b-audit.sh`. This script never requests or accepts `--execute`/GPU approvals; it checks current stage-B receipt and Flash API, existing P1 plan readiness, raw doctor/inventory rc=3 cause, and exact original image/revision. Append-only private 0600 evidence only; failures BLOCKED and no automatic retry/transition. No cache/model/container cleanups, no change to vLLM 0.32, port 8000 or ONE_ACTIVE_MODEL_ONLY.

Even a diagnostic PASS only qualifies **P1 POST-B diagnostics**, NOT new P1 Verify/Benchmark or P3-C. Each live API inference step requires a newly scoped approval and current action-bound SHA; P3-C separately requires explicit downtime approval and all real post-B evidence. Draft PR #1 remains Open/Draft/Unmerged until user authorizes merge.

---

## R1O — 2026-11-06 — P3-B read-only READY, 27B remains ACTIVE until newly scoped B approval (LATEST)

Actual DGX read-only B inspection (17:41:56 KST) reported `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, active API ID `qwen3.8-27b`, immutable 27B running container and original preserved Flash container identities; `executed=false`. **Do not treat READY as permission to stop the live 27B service.** B's operator approval must be separately given, with an unexpired fresh SHA and **correctly named shutdown target**: `I_ACCEPT_27B_DOWNTIME` plus independent `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`; neither P3-A's SHA nor `I_ACCEPT_FLASH_NEXT_DOWNTIME` is valid for B. Record the change under D-040.

D-016 remains binding: agent prepares `scripts/temporary/p3-stage-b-operator.sh` + Python, fake-DGX tests and permanent handoff on GitHub, confirms CI and PR, then operator fast-forward pulls. `--plan` is read-only and safe; **`--execute` is not authorized by this source work** and must NOT be asked of DGX operator until a separate explicit B downtime approval is obtained. If authorized, wrapper requires exact printed live SHA, 27B downtime and B-entry literals, fresh preflight/replan, and stops after B; no automatic post-B P1 or C. Canonical Wizard owns Docker mutation with best-effort rollback. No GPU-service changes from source-only GitHub work, preserve active 27B, old Flash container/image, P2 assets, API :8000 and Draft PR unmerged. Stale B inspect SHA expired 2026-11-06 17:50 KST, NEVER reuse for execution.

---

## R1N — 2026-11-06 — Actual P3-A PASS means 27B is ACTIVE; mandatory STOP before separate P3-B authorization (LATEST)

Operator reported real `P3_A_PASS_27B_ACTIVE` and `LIVE_SERVICE_VERIFIED` after `stage-a --execute` with exact newly generated SHA and downtime+entry acknowledgments, stored `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`, Wizard immutable receipt `~/.local/state/blazux-wizard/p3/stage-a.json`. This supersedes R1M's "A not run" state. **P3-A PASS (actual runtime)** is distinct from GitHub source CI success. Keep the active 27B service untouched until user explicitly approves B; sharing A's PASS is not a second-stage approval. No automatic B, P1 after B, or C, no hidden GPU tests, no cache/image cleanup, no Draft PR merge. Original Flash image/container must be preserved.

Per D-016, agent may push a **read-only** B preparation wrapper `scripts/temporary/p3-stage-b-inspect.sh`, fake-DGX CPU tests, docs; DGX user pulls fast-forward and runs the single read-only wrapper to ground 27B API and preserved Flash IDs. No `--execute` is supported by the inspector. A fresh B exact plan, source ID, stopped preserved Flash ID and separate operator downtime acknowledgment must still be reviewed before any future dedicated B execution procedure; old A SHA and A permission never apply to B. Follow D-039 and D-034's later post-B P1 rebenchmark then separately approved final C.

---

## R1M — 2026-11-06 — P1 PRE-A now PASS; scoped conditional P3-A entry must be freshly and interactively authorized (LATEST)

Actual DGX P1 report `~/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json` returns `PRE_A_P1_REVIEW_READY`, `issues=[]`, same verified Flash source/image, P1 functional PASS, 3-request numeric benchmark PASS and exact own-container historical/current rc3 resolution. Initial P1 backlog in older R1K/R1L is **superseded for pre-A only**. User's explicit condition "P1에 추가로 하지 않은 것이 없다면 27B 전환 승인" is met for **P3-A stage only**, not B/C and not permission for an automated model interruption. Read-only P1 receipt's `p3_a_execution_authorized=false` is intentional and does not reflect a failed P1 audit.

D-016 remains mandatory: GitHub-tracked `scripts/temporary/p3-stage-a-operator.sh`, CPU tests and docs are pushed/tested before DGX fast-forward pull. The wrapper DEFAULTS to `--plan`, does not git pull or mutate Docker under a plan; `--execute` requires an actual TTY, current unexpired action-bound SHA plan and three separately typed operator inputs (full plan SHA, Flash downtime ack, independent P3-entry ack). Only then canonical Wizard executes stage A with exact source stop, target start, live ID check and best-effort source restore. Successful A **leaves 27B active**; NEVER auto-execute B or C or P1 after B. Fault injection, host PID GPU exclusivity and host/daemon recovery unqualified; unexpected runtime result requires operator intervention, never auto retry. Preserve images/containers/model caches and :8000 contract; Draft PR #1 stays unmerged without explicit release approval. Binding decision D-037.

---

## R1L — 2026-11-06 — D-016 temporary GitHub→DGX workflow reaffirmed; P1 numerics supplied (LATEST)

**Operator corrected process:** never substitute pasted complex DGX Python/shell snippets for tracked temporary scripts. For every new operator-side P1/P2/P3 diagnostic: create/modify one coherent `scripts/temporary` wrapper plus CPU fake-runtime tests and docs; **push branch `feature/recipe-wizard-handoff` to GitHub, verify CI/PR, then tell DGX operator to `git pull --ff-only` and run the one tracked wrapper**. Wrapper must not git pull, switch model or perform unapproved GPU/service changes; write private evidence outside Git/HF. This is D-016 and `scripts/temporary/README.md`, not a new discretionary preference. User provided actual P1 inspect output and actual benchmark metrics; record the results and avoid rerunning GPU work solely to obtain figures.

**P1 latest evidence:** 2026-11-06 read-only report `/home/inlc/blazux-p1-reports/20261106T060941Z-e71a159c/result.json`: source+Hybrid READY, source/hybrid issues=[], index 11/11 compatible, source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, API model ID `qwen3.8-flash-next`, branch/clean/health checks PASS. `--inspect-only` action verify/benchmark reported `BLOCKED/inspection_only` **by design**, not a P1 failure. Both `doctor=3`, `inventory_plan=3` still require **actual raw JSON** analysis; current summary supplies only exit codes. Historical P1 2026-11-05 BENCH PASS receipt was read by operator: 3 samples / 192 completion tokens, TTFT P50/P95 1.398707/1.751198 s, latency P50/P95 1.687357/1.780142 s, mean 38.2968 tokens/sec. This supersedes earlier "no P1 numeric metrics supplied" claims. Prior functional verify PASS remains recorded. Per conditional approval D-035, with rc3 exact-cause still unexamined **P3-A is not authorized**; use tracked `p1-pre-a-readiness.sh` for evidence reconciliation, do not mutate Flash-Next. A pre-A baseline PASS does not cancel D-034 mandatory post-B P1 verification/rebenchmark and independent P3 stage approvals.

---

## R1K — 2026-11-06 — P2 STOP boundary / manually entered revised P3 sequence (LATEST OVERRIDES old R1H/J and D-033)

- **P2 bench PASS must not auto-start P3.** End P2 with actual metrics evidence + original Flash-Next `LIVE_SERVICE_VERIFIED`; wait for explicit operator request and new scoped approval before P3 planning/execution. A general instruction to "continue" is not downtime approval.
- **P3 order is immutable unless user changes it:** after P2 restored Flash-Next, separately activate 27B and verify; switch **27B → Flash-Next** with approval and verify; **while Flash-Next runs resolve outstanding P1 verification/measurement issues, then rebenchmark P1 and preserve actual numeric evidence**; finally switch **Flash-Next → 27B** with a new scoped approval and verify **27B active** as intended final service. Every transition is an independent guard/rollback unit, no automatic chaining or hidden start/stop.
- P1 initial backlog: historical `doctor=3` and `inventory_plan=3` issues not explained; earlier P1 verify and bounded benchmark PASS but **actual TTFT/latency/tokens/sec measurements not supplied**. Retest existing functional probes and collect measured benchmark evidence after verified 27B→Flash-Next transition. Block final 27B switch until P1 evidence accepted.
- Existing P3 two-roundtrip `roundtrip --execute` and direct legacy module execution are **RETIRED/BLOCKED** because they always restore Flash-Next and conflict with final 27B goal. Canonical source-only read-only plan: `./wizard.sh switch flash-next-27b sequence --plan --json`; `plan_id=null`, `operations_enabled=false`. No real persistent switch executor approved yet.
- Continue single active GPU model on :8000, stable public API, preserved original containers/images/checkpoints, fresh actual Manifest and API served ID, exact scoped approval and mandatory rollback. No P2/P3 automatic handoff, no cache cleanup, no Orcarouter work and no Draft PR merge as side effect.
- Binding document: `docs/P3-MANUAL-TRANSITION-SEQUENCE-20261106.md`. Older D-033 and `docs/P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md` are historical/superseded on P3 ordering; do not use their P3 execute instructions.

---

## R1J — Full Wizard source first, P2–P7 qualify later (2026-11-06)

- D-021 operator direction: finish **all user-facing model / service / advanced / P1–P7 lifecycle menu pathways now**, while execution adapters for P2–P7 remain deliberately blocked until independently qualified. Source-level completeness, CPU CI and DGX acceptance must be tracked as three different statuses.
- `wizard/console.py` implements model-first operator UX; `wizard/workflow.py` owns action capability matrix; `wizard/roadmap.py` reports P1–P7 evidence-scoped status. Don't remove P1 action-specific approval runner or P2 approved revision downloader, and do not accept any new `--execute` bypass from generic UI.
- For model actions `inspect/download/prepare/start/wait/verify/benchmark/switch/rollback/recipe`, display `BLOCKED` with exact reason when adapter not qualified. Do not silently start models via generic `flash serve` or auto-stop Flash-Next.
- Service log view is opt-in, bounded, targets only observed managed model and is potentially sensitive; no automatic upload or logging of its contents to GitHub.
- Keep in-flight NVIDIA 27B download and active Flash-Next/API untouched. After operator-owned transfer finishes, reconcile pinned source and new GitHub Wizard code; only then plan P2 GPU validation and P3 recovery window.

## R1I — Model-first root Wizard UX (operator accepted 2026-11-05)

- Current canonical UI: **Select/run model, Service, Advanced** (plus Exit). Model choices Flash-Next / NVIDIA 27B / Orcarouter. Do not make the operator navigate P1–P7 for ordinary operations.
- The same read-only decision planner serves root TTY selection and `./wizard.sh select MODEL --json`. It must suppress duplicate downloads while `qwen38-27b-dl` is running; no automatic start, stop, rollback or model conversion from merely selecting a model.
- Preserve `scripts/manager/p1_wizard.py` and its existing exact action-specific approvals and DGX evidence. Reuse `p2_27b_download.py`, do not restart its existing active download. Keep old CLI aliases stable.
- Desired Git manifest, observed live Docker/socket (with API/GPU verification separated), and event journal are distinct layers. No stale manifest may authorize a service change. The download's approval scope is **checkpoint-only**, never a transition.
- During an ongoing DGX download, GitHub source/CI/docs work is allowed, but do not ask the user to `git pull`, `docker stop`, start another download or touch live `:8000` without carefully coordinating with completion; preserve user-owned in-flight container and mount.
- Source acceptance does not imply 27B GPU, vLLM 0.32 runtime, model switch or recovery PASS. Implementation plan: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`.

## R1H — One model per DGX, one external API port (operator-confirmed 2026-11-05)

- `runtimes/service-policy.json` is the reviewed desired-state policy. Exactly **one active GPU inference model** may run. Both NVIDIA Flash-Next and NVIDIA 27B must use host `:8000/v1` when active; no dual loading or permanent secondary port.
- A service transition from Flash-Next to 27B requires: validated pinned 27B files/image → fresh live service+GPU+API identity manifest → exact approval and rollback resources → stop Flash-Next → verify port 8000 free → start 27B → verify served ID and bounded API health → commit; on failed startup restore Flash-Next and record recovery outcome. Reverse direction has symmetric gates.
- The model **download only** may overlap Flash-Next inference because it uses disk/network, without GPU, host port binding, service stop or API change. Download plan approval cannot authorize a transition, start, stop, rollback, cleanup or GPU use.
- Stored manifests and journals document desired/previous state, but **actual Docker/socket/API/GPU evidence wins**. Incomplete or contradictory observations block transitions; no success inferred from a stale manifest. The current implementation provides read-only live manifest and an approved downloader, **not** a qualified runtime switch executor.
- Never run a 27B start through generic `flash serve` that overwrites/stops Flash-Next. Treat P3 as independent service handover acceptance and P2 first runtime as separately approved action.

# Project operating rules (must follow in every conversation)

## R1G — P1 live evidence and P2 guarded progression (2026-11-05)

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

- Do not conflate `benchmark=PASS` with a specific throughput target or full Wizard lifecycle qualification.
- Stage P2 begins with **read-only Wizard inventory** and source/CPU validation; retain actual `flash-next` server, caches, model recipes and storage unmodified.
- No guessing immutable 27B SHA or vLLM compatibility from public release marketing; do not auto-download 27B or switch models based only on source inventory.



> Applies to `kjlee-inlct/qwen3.8-Flash-DGX` development, planning, deployment and handoff.

## R1 — Repo, branch and concurrent work

- Canonical new fork `kjlee-inlct/qwen3.8-Flash-DGX`; upstream `blazux/qwen3.8-Flash-DGX`. Preserve upstream behavior and periodically verify pinned upstream SHA before integration.
- Mainline `main` remains a stable base. Plan/handoff work: `feature/recipe-wizard-handoff`. Parallel Orcarouter adaptation: `feature/orcarouter-bf16-adapter`. Do not merge/cherry-pick either automatically without reading diff, resolving conflicts and checking regressions.
- Legacy `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark` and YSLAB references are **read-only historical sources**, not the new implementation base. Never silently replace new fork code with old vLLM patches.
- One coherent topic per branch; meaningful commits, draft PRs for unvalidated work, CI/readback. Record PR and Git SHA. No unverified claim of merge.

## R1A — User-confirmed sequential Wizard delivery contract (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

- Do not advance a milestone merely because source/CPU CI succeeded: require actual **Wizard-driven DGX** installation, API/benchmark and evidence for P1/P2/P5; switch and restore verification for P3/P6.
- Existing `flash`, scripts and Python manager are allowed as **subprocess engines** invoked by the Wizard, not as substitutes for a complete Wizard entrypoint. Both interactive and batch/noninteractive operations should share validation, plans, gates and evidence. Wizard should reject implicit destructive defaults.
- Keep external host API `:8000/v1` where feasible and consistently manage served-model IDs. No simultaneous assumption that two heavy models fit GPU memory. Any change to external clients/port/gateway requires explicit operator review.
- P4 is conditional: if sufficient space exists, record **SKIPPED_NOT_NEEDED** rather than delete weights. If required, enforce exact-path dry-run and explicit separate approval, verified safe fallback, no shared-cache blob deletion and rollback plan. Preserve source, recipes, tests, logs and evidence.

## R1B — Modular Wizard and user-mediated command execution

**Wizard architecture decision (2026-11-05):** Implement all P1–P7 **menu/CLI modules first** and then integrate/debug actual runtime in P1→P7 order. Root operator entry is `./wizard.sh`; `wizard/menus/models/`, `switching/`, `storage/`, and `operations/` own per-menu behavior, with `wizard/main.py` and `wizard/menus/common.py` for routing and safe source contracts. Scripts accept explicit stage/action arguments and emit JSON and stable exit codes for operator-mediated DGX tests. Only P1 calls the existing guarded backend today; P2–P7 are SOURCE-ONLY plans and must never execute merely because a menu exists. No SGLang; vLLM 0.32 only.

- All P-stage menus use one root `./wizard.sh` entrypoint; direct command syntax and interactive choices must share the same stage implementation. Never build separate secret execution paths for headless runs.
- Default to read-only status/plan with machine-readable JSON; use exit 0 for successful inspection, exit 3 for blocked plans, and nonzero for failures. A plan printed with BLOCKED is evidence of **refusal**, not approval. P1 execution retains its fresh full `plan_id` gate. Do not allow `--dry-run` with `--execute`.
- The adapter for P2, P3, P4, P5, P6, P7 must remain `INTERFACE_ONLY` and `executed=false` until separate pinned, tested implementation, source/CPU/CI and real DGX acceptance prove each operation. In particular P4 may be skipped and never deletes anything without its own exact-path approval; P3/P6 do not switch any live services until qualification.
- Do not update the active DGX worktree while the user-owned `./flash setup default` or its queued `serve/wait/test` commands may still be running. The last supplied log showed download at 9/25 (36%), image build PASS; current state must be rechecked after completion.

## R1C — Functional categories override numbered module filenames

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

- Do not create a new numbered `wizard/menus/pN.py` module. Extend only the appropriate descriptive category module. The numeric P-stage IDs are metadata/legacy CLI aliases; never reintroduce numbered filenames as the primary architecture.
- Root `./wizard.sh` defaults to two-level group/selection navigation and supports noninteractive `./wizard.sh model flash-next status --json` or `./wizard.sh switch flash-next-27b plan --for-action switch --from-model flash-next --to-model 27b --json`. Legacy `./wizard.sh p1 ...`, `--stage p3` and `wizard/p1.sh` remain supported.
- P2–P7 remain `INTERFACE_ONLY` with no operational permissions, regardless of menu naming or presence; no resumed download, Docker changes, cache cleanup or model switch from this refactor.

## R1D — Git-tracked temporary script batches for user-operated DGX (D-016)

**Default for multi-command DGX checks/tests:** Do not repeatedly paste a long ad-hoc shell transcript. Implement one **descriptively named, tested, version-controlled temporary wrapper** in `scripts/temporary/`. GitHub-first changes (script + CPU fake-backend tests + docs) must be committed on the active branch, CI checked and recorded in handoff. The operator then **finishes any existing processes**, runs `git switch` / `git pull --ff-only`, and invokes **one script**; the script itself must not automatically pull, reset/clean the worktree, install/upgrade packages, or mutate in-use services.

- **Required pipeline:** (1) **preflight/inventory + safe diagnostics**, (2) **Wizard-mediated, explicit per-operation approval + bounded verification/benchmark** only when ready, (3) **report/evidence export**. Missing readiness, wrong branch, dirty tracked files, active setup or missing approval must fail closed; still export an honest BLOCKED result.
- **Approval:** Source/CPU checks are read-only and may run unattended. **Except the user-authorized, non-disruptive P1 auto-GPU procedure in R1E**, real API/GPU operations require an exact currently valid action-specific Wizard `plan_id`, independent consent for *verify* and *benchmark*, a second Wizard preflight, and benchmark only after verification PASS. R1E still mandates action-specific current IDs and a second preflight but permits the script to supply them without separate typed consent. In interactive shells ask for that full hash; in headless mode never auto-consent and accept only explicitly supplied exact identifiers. Never hide consent inside `--yes` or a global preapproval.
- **Evidence:** Use date-stamped folders under a user-owned location **outside** Git/HF cache, restricted to the operator, containing raw command return codes and structured JSON plus Wizard evidence paths; print the result path. The user may selectively share reviewed logs with the assistant. Do not commit/upload live logs, model data, API credentials or proprietary prompts to GitHub automatically.
- **Temporary lifecycle:** Each script needs a one-line purpose, run preconditions, exact commands, side effects, safety boundary, owner/stage, test path and disposal condition in `scripts/temporary/README.md`. Keep the wrapper until the results have been analyzed and recorded; then archive/remove by a separate reviewable Git commit. Never have the script self-delete or purge broad folders. Leave stable implementations in `wizard/` or `scripts/manager/`, not permanently hidden in `scripts/temporary/`.
- **Non-authorized actions:** No automatic `setup`/download, Docker stop/remove/recreate, HF cache cleanup, image prune, model switching, gateway changes, `git reset --hard` or `git clean -fd`. These need an independent scoped plan and explicit operational permission when/if requested. Existing OpenWebUI/Portainer and the user's prior queued `flash setup/serve/wait/test` must be preserved.

**First implementation:** `scripts/temporary/p1-post-download.sh` with `p1_post_download.py`, CPU tests `tests/test_p1_temporary_cpu.py`, and the canonical instructions `scripts/temporary/README.md`. Run only **after the original setup/serve/wait/test shell chain ends**. `--inspect-only` is non-executing; default TTY interactive prompts for separate current verify/benchmark hashes. This is not authorization to perform live DGX operations from the assistant.

## R1E — Default Blazux compatibility and scoped P1 GPU test authorization (D-017)

**Operator DGX facts (2026-11-05):** The latest post-download diagnostic returned `api_model_ids=["qwen3.8-flash-next"]`, `refs/main=fc694b54fb0174e0913e6adf86691ef85a4ead47`, 0 incomplete HF blobs, a source index and tokenizer that are **existing nonempty symlinks whose targets resolve outside the model repository**, and a Hybrid tokenizer with the same layout. The Hybrid index is a normal 31,907,813-byte file and the `.prepared` marker exists. These observations show the previous `TARGET_OUTSIDE_REPOSITORY` reason is a **new P1 checker policy stricter than Blazux's original `os.path.exists`-based policy**; they do not establish that any metadata is missing. Previous plans were blocked before actual GPU verification or benchmark. The user explicitly allows non-disruptive GPU compute tests to run without separate per-step approvals, provided the actual target service is confirmed. The presence of an API response means some server is listening; do NOT assume there are literally no processes running or stop/replace any service.

- **Default-first compatibility:** For default `nvidia/Qwen3.8-Flash-Next-NVFP4`, match supported Blazux source/snapshot/Hybrid metadata conventions. The earlier P1 strict audit wrongly treated **existing metadata-only cross-repository symlinks** (`tokenizer.json` and `model.safetensors.index.json`) as missing. Accept these two names when the target resolves to an existing nonempty regular file; fully parse and validate the bounded index JSON and referenced shards. Keep arbitrary external **weight shard** symlinks blocked. The new P1 64MiB index-size guard remains; do not disable it or silently bypass missing files.
- **Operator-granted P1 GPU scope:** On the DGX, user authorizes **non-disruptive** GPU inference/API verification and a bounded benchmark **without typing a plan hash or approving each subtest again**. Run via `bash scripts/temporary/p1-post-download.sh --auto-gpu` after `git pull --ff-only`; script obtains the *current* distinct verify and benchmark plan IDs itself and submits them to the existing Wizard's second revalidation. It still blocks on wrong branch, dirty worktree, missing/wrong served model ID, active setup/download, failed or changing asset audits, failed verification, and port/image/container mismatch.
- This authorization is **not** permission to stop/restart/replace containers, modify the listening API, run setup/download, regenerate Hybrid assets, delete model/cache files, switch to 27B/Orcarouter, change proxy/gateway, or run heavy unbounded load. Do not treat the statement that no prior service is operating as evidence no current model process exists; `/v1/models` returned `qwen3.8-flash-next` and must be respected.
- **Default script behavior unchanged:** `--inspect-only` remains strictly read-only; without `--auto-gpu`, the script continues to request individual manual hashes or blocks non-TTY. Auto GPU is opt-in at script invocation, only for P1 verify (text/tool/vision) then 3 bounded SSE requests by default. CPU CI does not prove DGX performance.

## R1F — Preserve native Blazux baseline; never gate it on Wizard-only probes (2026-11-05)

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

- Distinguish **native model baseline** (Blazux coherence /v1/completions and ordinary chat) from **optional feature probes** (strict tool invocation, synthetic image). A partial optional failure is NOT a failure of default Blazux. Record `baseline_status`, `extended_status`, named `probes`, and `status=PARTIAL` where appropriate.
- Never hide a Wizard failure on nonzero returncode: parse its bounded JSON stdout regardless of returncode, preserve evidence path and sanitized probe errors. Do not mistake `evidence:null` in a wrapper summary for absent stored Wizard evidence.
- Baseline PASS may enable already-authorized bounded P1 benchmark even if extras fail; baseline FAIL may not. Full P1 acceptance is still pending until required extended features and benchmark meet their own exit criteria.
- Never correct a Wizard-specific test mismatch by re-downloading 124GiB weights, regenerating Hybrid or changing a live API without separate concrete evidence and scoped authorization.

## R2 — Live operations, authorization boundaries

- **Superseded observed-operational assumption (2026-11-05):** user reports all previous operating services deleted. The old Orcarouter container `qwen38-flash-orca-uncensored-bf16-mtp` and old `:8000/v1` are **historical**, no longer presumed active or statically reserved. Still perform fresh read-only Docker/socket/volume inspection on DGX; a user report does not prove the port and name are free. Preserve any actually existing unrelated containers, image assets, weights, HF cache, integrations or mounted storage.
- Do not stop/kill/exec/remove/replace/retag/rebind/reconfigure any **observed existing container**, or mutate shared cache/models, without separately scoped approval. Refuse a name conflict: no implicit docker rm -f. Do not treat deletion of old services as authorization to remove other resources.
- This fork removes the implicit `docker rm -f "$NAME"` from `scripts/serve.sh`, replacing it with an exact-name collision refusal; still verify collision checks and race behavior before approving operational launch. Existing upstream scripts in other worktrees may retain the destructive behavior.
- Current user request authorizes **implementing** new Blazux default source/config for port 8000. Do not infer approval for GPU/model loading, Docker image replacement, gateway cutover, service stop, model/cache deletion or other disruptive resource actions. Before deployment obtain actual DGX preflight/port/image evidence and a scoped operation/rollback agreement.
- Read-only GitHub/source/test inspection and local CPU-only tests are allowed. DGX read-only inspections should be scoped and recorded, avoiding sensitive output.
- **vLLM 0.32 only** for all three model recipes. No SGLang integration.

## R3 — Destructive cleanup is separate

- Stage P4 `retire Flash-Next` means cleanup *candidate*, not advance permission to delete.
- Require specific cleanup plan ID, confirmed inventory, exact paths/digests, size estimates, disjoint protected roots, no running/bound/shared references, rollback capacity and explicit approval.
- Default `dry-run`; never `rm -rf` a whole workspace/Hub cache, `docker system prune -a` or delete unknown blobs/images.
- Keep recipe, config, benchmark, logs, source and provenance even after checkpoint deletion. Prevent cleanup of the last validated fallback.

## R4 — Verification and assertions

- Status vocabulary: `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`. Each status must carry **scope** `SOURCE/CPU/CI/GPU/API/SWITCH/RELEASE`.
- A source audit `PASS` is **not** GPU runtime `PASS`; upstream/other-author benchmarks are not local benchmarks; default branch compatibility does not imply 27B compatibility.
- Record full model repository revision, image digest, Git HEAD, recipe SHA, runtime config, host resources, command, seeds, comparison method, observed output, log/artifact location and timestamp for every claimed result.
- Orcarouter strict same-checkpoint logprob max absolute delta `1e-4` previously failed in Preview. Carry forward as `RELEASE_BLOCKED` until proven otherwise or a separately reviewed gate decision is recorded. Avoid comparing logprobs across different checkpoints.
- Test failures must be recorded, not concealed, renamed or marked `PASS` for task completion.

## R5 — Efficient development and update rules

- Prefer a meaningful **batch of related changes per conversation**: inspect → implement → write tests → run CPU checks → docs → commit → PR/verify.
- If needed, add or update scripts, manifests, tests and docs, rather than leaving long transient manual commands as the implementation.
- Keep `README.md` external references intact; cite aphex3k only for transferable tuning and benchmark methodology. No SGLang runtime.
- Every state-changing session ends with updated `handoff/CURRENT-STATE.md`, `handoff/NEXT-ACTIONS.md`, and `handoff/CHANGELOG.md`. If there are new tests, update `EVIDENCE-LEDGER.md`; if new policies, update `DECISIONS.md`.
- On a new chat, read handoff first, verify against GitHub and real runtime evidence, proceed directly with the next safe actions. If no tool/action is available, record `BLOCKED` honestly; do not fabricate execution.
- No secrets, personal tokens or private host-only strings in GitHub markdown, logs or PRs.

## R6 — Exit report format

Every meaningful handoff update must include: `WHAT CHANGED`; `SOURCE BRANCH + ACTUAL SHA`; `PR + CI`; `TESTS (PASS/FAIL/NOT_RUN by scope)`; `DGX STATE (observed vs historical)`; `BLOCKERS/APPROVAL`; `NEXT 1–3 ACTIONS`; `FILES UPDATED`. Unknown values must say unknown.
