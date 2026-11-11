## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-12 P5-D actual DGX result

**Verified source identity:** operator-run Orcarouter v3 `qwen38-orcarouter-qsa62318-lmhead-v3` (adapter `qwen4exp-qsa62318-lmhead-v032-v3`, previous `lm_head.weight_scale` fix), API :8000, DEVELOPMENT_TRIAL. **This is an operator-provided receipt, not a new GPU/API test by GitHub.**

2026-11-12 DOC-ONLY: captured operator DGX P5-D ownership evidence (`BLOCKED_PARTIAL_PROCESS_EVIDENCE`, missing :8000 PID; Docker and GPU PID subsets consistent), confirmed no evidence of service failure, recorded P5-C/API healthy observations and separate read-only KV inventory, and moved remaining measurement completeness to P8. Preserved historical source/CI entries; no model/Docker/API mutation or production release. Continue with P6-E.

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

## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-09 00:55 KST (v3 real PASS, P6/P8 source)

Latest **operator-observed** P5 Orcarouter container `qwen38-orcarouter-qsa62318-lmhead-v3`, API `qwen3.8-flash-next-orca-uncensored-bf16`, port 8000, service `LIVE_P5_TRIAL_API_VERIFIED`, MTP0 chat `PASS_LIVE_INFERENCE` (READY). Adapter `qwen4exp-qsa62318-lmhead-v032-v3` corrected `lm_head.weight_scale`, but runtime remains `DEVELOPMENT_TRIAL` / not production. Preserve v3, previous failed-container cleanup history and all HF/checkpoint/images.

Latest 00:54–00:55 KST idle-only evidence: host MemTotal 121.63 GiB, MemAvailable 30.18 GiB, SwapUsed 1.31 GiB (Orcarouter cgroup swap 0); Docker memory 7.157 GiB vs cgroup current 25.54 GiB, peak 37.02 GiB, inactive_file 18.38 GiB, anon 4.58 GiB; PSI memory avg10 0, OOM/OOMKill 0, zero observed page/swap/refault churn; CPU busy ~0.18% for 45s at governor performance, 10 CPUs 2808 MHz / 10 CPUs 3900 MHz; temperatures up to ~34.7 C system, ~33 C GPU. Inactive cache accounts for much of Docker/cgroup gap, NOT proof of leak or PLE residency. Earlier 00:43 KST data are historical below. Startup policy is OBSERVE_ONLY, no active gate, BLOCKED_UNCALIBRATED is expected; never copy YSLAB 100 GiB or apply CPU/cgroup restrictions without approval.

GitHub source `21aa6c9` implements P6 non-authorizing live preflight, two-direction synthetic switch and P8 Fake-DGX fault matrix; `5acf0b1` requires same Docker identity for cgroup OOM/fault deltas. Push/PR CI for both source commits succeeded. Actual DGX P5 Tools/Vision/MTP2/benchmark/canonical promotion, P6 switch, P7 Proxy/Gateway and P8 fault/restore/release are NOT accepted. Fixed vLLM 0.32.0, no SGLang, ONE_ACTIVE_MODEL_ONLY, :8000; no authorized service mutation and PR #1 remains Draft/Unmerged.

[Full document audit](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md) · [P5 resource and engine details](../docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md)

**P5~P8 범용 기능 (2026-11-09):** 모든 등록 모델에 공통인 리소스/벤치 근거(P5), 전환 검증(P6), Wizard UX·서비스 통합 증거(P7), Fake-DGX 복구 매트릭스(P8)를 구현했다. 모델별 엔진·로더·PLE·MTP는 별도 어댑터이며, source PASS는 운영 승격/복구 승인이 아니다. 07:18 KST 제공된 DGX idle 관측에서 v3/API 8000 유지 확인. [범용 운영 명세](../docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md).

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

## 2026-11-08 — P5 real DGX one-shot MTP0 trial (no restore)

Operator permitted stopping development 27B and specifically waived automatic 27B restoration if Orcarouter fails. Newly implemented `./wizard.sh p5 trial prepare|plan|execute|status` with built, isolated Blazux vLLM 0.32 candidate, BF16 PLE mmap, immutable base image/source pins, :8000 and one active GPU model, explicit exact plan approval `I_ACCEPT_P5_NO_ROLLBACK`, preserved HF caches/images/old stopped container and private evidence. Execution re-checks actual 27B served ID, source/candidate image digests, :8000 release and NVIDIA compute process inventory. The default production service transition rollback remains unchanged. MTP2, Native Tools and benchmark still require separate GPU qualification.

**Real DGX P5 not yet executed by this GitHub session.** User's latest DGX log: new PLE schema+manifests PASS, Orcarouter PLE BF16 metadata PASS, donor 31 BF16 SHA PASS, 57 CPU tests PASS; 27B still serving. The new GPU trial code first had 67 P5 CI CPU tests PASS; the latest extra source/image/GPU guard CI must be checked after commit. Runbook: `docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md`. No auto restoration, source deletion, P3 replay, P4 prune, P6 switch, P8 faults, or PR merge.

---

## P5 follow-up 2026-11-08: PLE schema v2 and cross-engine reference discipline

The operator allows development DGX service downtime and GPU experiments. Shared Wizard `runtimes/ple-assets.json` now schema v2 (model-specific dtype/scale/placement; Orcarouter pinned BF16 unchanged), `runtimes/ple-loader-profiles.json` is in the common registry as seventh manifest, and `scripts/manager/ple_format.py` plus transition preview require independent source mapping/GPU release and rollback during switches. External DGX references dolf3131 (pinned 45e3d477) and NVIDIA October FP4-Local forum provide **research only**; no alternative container/image adopted, and Blazux vLLM0.32 remains mandatory.

[Source commit d395368](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d395368645b04ebc4d2367f33314ea07fb68ff1b) / [CI #42436269922 SUCCESS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42436269922). GPU P5 remains NOT_RUN; this GitHub session did not stop 27B despite downtime permission. Exact new docs `docs/P5-PLE-FORMAT-AND-DGX-SPARK-REFERENCE-ADOPTION-20261108.md`; check current HEAD/PR/CI. Read-only DGX validation is next; no deletion, unapproved GPU executor, P3 replay or Draft PR merge.

---

## 2026-11-08 — Shared Wizard manifest refactor and first-class BF16 PLE registry

`a17b361`: canonical `runtimes/manifest-registry.json`, `runtimes/ple-assets.json`, shared strict loader and cross-reference validator `scripts/manager/manifest_registry.py`, read-only metadata-backed PLE controller `scripts/manager/ple_assets.py`, registration links in service/discovery/Orcarouter recipe, Wizard manifest status/validate command, model list, P5 status/doctor and service status integration. Added 14+ dedicated manifest-registry tests and 11 PLE asset integration tests, plus existing P1–P4 regression. [CI #42433160630 SUCCESS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42433160630), 996 executed CPU cases over 44 invocations (repeats included). Follow-up model-first selector display and documentation require their own CI.

Operator-provided DGX pre-refactor log: pinned PLE headers 128/128 PASS, RadixArk MTP 31 BF16/3 pinned hash PASS, active 27B :8000 LIVE_SERVICE_VERIFIED; no fresh on-DGX validation of new registry or GPU run. P5 runtime and benchmark remain NOT_RUN/NOT_RELEASED. No model/cache/image/container mutation, no Draft PR merge.

---

## 2026-11-08 — P5 vLLM 0.32 opt-in ABI candidate (source only, not built)

After first source CI PASS, compared actual upstream `vllm-project/vllm@v0.32.0` Qwen4Exp Python sources. `vllm/models/qwen4_exp/nvidia/model.py` blob `2fb056bde43cfa5b0d9f0e15545e4ca3a2782c98`, `mtp.py` blob `32e95faa0dc882150a3b7dd9809641651fb2ff4e`, and `vocab_parallel_embedding.py` blob `92e65c839dbf40fa3b983e57e2364eb7cbf52654`. Official v0.32 model.py and mtp.py each have precisely one candidate ParallelLMHead prefix anchor; MTP draft config and load-weights return anchors each appear once. Importantly v0.32 `CompressedTensorsConfig.ignore` exists independently of `ignored_layers`/`exclude_modules` and the upstream draft converter does not explicitly remap `ignore`.

New **source-only** `src/p5_patch_qwen4exp_v032.py` provides fail-closed, idempotent candidate source transformations: opt-in `ParallelLMHead(quant_config=...)`, remap `CompressedTensorsConfig.ignore`, and exact 31-name BF16 MTP loader guard (not len-only). The pin names are cross-checked against vendor YSLAB MTP manifest. `Dockerfile.p5.candidate` requires an explicitly supplied **qualified immutable base** from Blazux 0.32; it contains no YSLAB development Docker base, no default `VLLM_P5_ORCAROUTER` opt-in, and **has not been built**. The Python patch `--apply` requires `P5_EXPLICIT_IMAGE_BUILD=1` and a vLLM 0.32.0 installed package. Additional CPU tests prove marker/AST/idempotence, tamper refusal, 31 exact names, version gate and no source writes without explicit build opt-in. P5 one-shot static audit now detects the source candidate. This is NOT evidence that installed DGX vLLM/ABI, GPU, quantized lm_head, runtime MTP2 or any benchmark works.

This candidate is deliberately not integrated into `Dockerfile` or production start. Strict `launch_allowed=false`, `register_as_runtime_recipe=false`, no image digest, no GPU execution or Docker mutation. `--gpu-trial` remains BLOCKED; image build, overlay asset creation and 27B downtime each require separate explicit operator approval and rollback gate. Maintain P3/P4/P6/P8 restrictions and keep Draft PR #1 unmerged. Confirm follow-up commit's CI before claiming the new tests passed.

---

## 2026-11-08 — P5 Orcarouter BF16PLE source-only integration and CI

- Source commit [33adec1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/33adec182e97a8eac0d5584bdf73f1448bdd84f2) introduces pinned unqualified Orcarouter recipe, licensed YSLAB audit/overlay source in `scripts/p5_vendor`, PLE/MTP donor verification, MTP0/MTP2 candidate profiles, Wizard P5 source commands, one-shot `--plan`/`--cpu-only`/`--read-only`/`--gpu-trial` (blocked), and 20 CPU tests. [GitHub Actions 42429745463](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463) SUCCESS; new 20/20 P5 CPU and one-shot CPU PASS.
- Follow-up improvement: detailed per-test-case JSON and source profile preview for Wizard, subject to new CI recheck.
- **No on-DGX observation this session**, no GPU loader/MTP0/MTP2 API/bench, no derived overlay write, no 27B interruption. Runtime release remains false, P6/P8 NOT_RUN, P4 cleanup not approved, Draft PR #1 unmerged. See `docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md`.

---

## 2026-11-08 — Prepare next P5 implementation conversation (documentation only)

Verified GitHub branch `feature/recipe-wizard-handoff` pre-audit HEAD `ac88693196a8b2b5efc95f091dc88531d6951037`, Draft PR #1 Open/Unmerged and Actions SUCCESS. Confirmed core 34/34 historical handoff/design/manifest files plus 7/7 P4 evidence/source assets exist. Inspected external YSLAB BF16PLE code at `9492b78c6bc04638587b42f2ffeb0680b0fcb3ef` and historical parallel Orcarouter adapter design branch. Created P5 design (`docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md`), P5 document audit (`docs/HANDOFF-DOCUMENT-AUDIT-P5-20261108.md`) and full next-session prompt (`handoff/START-NEXT-P5-20261108.md`); primary handoff pointers and D-068 updated. No P5 code/GPU operation/deletion, no PR merge. Planned P5 runtime recipe and one-shot acceptance script remain to be implemented next session.

---

## 2026-11-08 — P4-B/C operator DGX combined read-only dry-run PASS

Operator submitted `bash scripts/temporary/p4-bc-dry-run.sh --json` output: **13/13 local Fake-DGX tests PASS**, P4-A inventory complete; P4-B `READ_ONLY_REVIEW_COMPLETE` (9 resource records, zero selected), P4-C `DRY_RUN_COMPLETE_RELEASE_GATED` (2 PASS, 2 DEFERRED, 1 NOT_RELEASED, 1 NOT_EXECUTED), combined `READ_ONLY_DRY_RUN_PASS`, issues empty. All would_execute false and no live operation/approval. Real cleanup deferred to future independently approved P5 issue or P8; actual live adapter absent. `docs/P4-BC-DGX-READONLY-DRY-RUN-EVIDENCE-20261108.md` is the source-grounded receipt; source-only GitHub CI remains separate. Existing PR #1 stays Draft/Open/Unmerged.

---

## 2026-11-08 — P4-B/C read-only source implementation and one-shot dry-run

P4-B candidate/reference review + P4-C deletion transaction rehearsal are available from `./wizard.sh storage flash-next dry-run --json` and `bash scripts/temporary/p4-bc-dry-run.sh --json`. 13 Fake-DGX tests integrated into CI: [42403828742](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42403828742) **SUCCESS 902/902 CPU/Fake-DGX across 41 groups**. No new actual DGX P4-B/C result yet. Previous actual P4-A PASS remains established. No live deletion adapter exists (`P4_C_LIVE_EXECUTION_RELEASED=False`); P5 operational issue or P8 acceptance requires separate authorization and an exact-resource adapter/test before real cleanup. Never infer safe reclaim bytes. Reference: `docs/P4-BC-ONE-SHOT-DRY-RUN-20261108.md`.

---
## 2026-11-08 — P4-A actual DGX capacity inventory: READ_ONLY PASS / COMPLETE

Operator ran `./wizard.sh storage flash-next inventory --json` at checkout `a29cd6e`: `READ_ONLY_INVENTORY_COMPLETE`, `issues=[]`, `active_api_verified=true`, 27B active, stopped Flash preserved, Orcarouter model cache present without a container, one GPU and one port-8000 owner, all four Docker capacity categories. File-system total **982,819,848,192 bytes**, free **324,880,961,536 bytes** (~**33.06% free**); both HF cache roots returned the *same* filesystem total/free, so never add those values. Root allocated bytes **267,995,971,584** and **192,507,006,976**; known model-repository allocated sizes: Flash **75,967,504,384**, 27B **21,932,584,960**, Orcarouter **177,686,446,080**. Docker displayed reclaimable: containers **182.7MB**, build cache **2.088MB**, images/volumes **0B**; **not** verified safe reclaimable bytes. See `docs/P4-A-DGX-READONLY-CAPACITY-EVIDENCE-20261108.md` for bounded source, units, and non-additivity caveats. No deletion or service mutation; **P4-B/C NOT_STARTED/NOT_APPROVED**, **P8 NOT_RUN/NOT_RELEASED**. Do not repeat P3-A/B/C/G.

---

## 2026-11-08 — P4-A source guard: Docker category completeness and live owner matching

The read-only inventory now fails closed to partial when any Docker `system df` category is missing or when the single reported GPU/host-port-8000 owner is another managed container rather than the API-verified active model. Added Fake-DGX regression cases for both. No GPU, Docker, HF, recipe, or service mutations; no P4-B/C authorization. CI and real DGX capacity remain separate evidence.

---

## 2026-11-08 — Actual DGX P3-E/F read-only closeout complete; P4-A inventory NEXT

**Observed on actual DGX after fast-forward to `0421b46`:** P3-E `flash_host_assets` status `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`, issues=[], 31,907,813-byte index, 299,845 weight-map entries (400,000 cap), **11 shards** total apparent size **129,771,270,410 bytes**, metadata hashes and mounted template SHA-256 observed. Checkpoint weights not hashed (`large_shard_hashes_verified=false`), pinned published revision bytes not independently verified (`verified_model_revision=false`), reinstall not qualified. P3-F real DGX **168/168 CPU PASS (7 suites)**, `PRODUCTION_LIFECYCLE_RELEASED=false`. Current `qwen38-27b` API `qwen3.8-27b`, host :8000, 8/8 service checks true and `LIVE_SERVICE_VERIFIED`; service-status command does not independently validate GPU/PID ownership. All commands read-only and no service mutation.

**P3 disposition:** A/B/C/G historical actual operator-approved PASS/CLOSED; D independent read-only PASS historically; E source/host-asset metadata handoff COMPLETED but **not** real reinstall; F source/CPU handoff COMPLETED but **not** production lifecycle. **P8 remains owner** of full Flash recipe/install validation, actual reinstall/rollback, deliberately induced failure/automatic recovery and final release (all real work NOT_RUN). No replay, no automatic source launch.

**New operator instruction supersedes prior P4 hold ONLY for read-only P4-A:** implement capacity and current-state inventory via Wizard *before* considering any deletion. P4-B candidates and P4-C cleanup remain not started and unauthorized. Read `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md`. P4-A is SOURCE IMPLEMENTED, DGX CAPACITY OBSERVATION NOT_RUN. Latest P4-A CPU/Fake-DGX CI [42395243458](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42395243458): **887/887 PASS, 40 groups**; no real disk capacities have been measured by the new Wizard in the conversation.

---

## 2026-11-08 — P3 CLOSEOUT ONLY; P4 operator hold; P8 owns live reinstall and recovery

**Operator decision:** Do not start P4. Earlier P4 module/test/workflow code was reverted ([1110681](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/1110681f451bc72470454bbbee1e1d79d6406a1d), [CI 42393129150](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42393129150) SUCCESS). **P4 = NOT_STARTED / OPERATOR_HOLD**. No P4 inventories/cleanup/source implementations.

**P3-E:** Flash FP8 hybrid command/source draft and 299,845-key weight-map observed at DGX; source cap now 400,000 with 128 MiB byte cap and all path/shard safeguards retained ([1a05eb2](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/1a05eb2dfacda960527ba94da544e5f545d8793f), [CI 42392758148](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42392758148) **880/880 CPU PASS, 39 groups**). P3 closeout still needs a current **read-only DGX host-asset rerun** for index/shards/template evidence. Not qualified for canonical reinstall.

**P3-F:** Source Fake-DGX lifecycle/rollback tests pass, `PRODUCTION_LIFECYCLE_RELEASED=False`. P3 closeout asks **read-only `p3_dg_acceptance --cpu-only` 7-suite** local result; last DGX six-suite PASS was 153/153 before added host-asset suite. Actual generic Docker install/recreate/rollback production release is transferred to P8, not declared done. P3-A/B/C/G real PASS/CLOSED, D READ_ONLY_PASS; no replay.

**P8:** Full canonical Flash runtime/env/image/security spec, explicit-approval fresh reinstall, API/benchmark/idempotence/journal, controlled failure/automatic recovery and final Wizard go-live after integration gates. P8 real fault/release NOT_RUN. **Detailed closeout checklist**: `docs/P3-CLOSEOUT-AND-P8-HANDOFF-20261108.md`.

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

## 2026-11-08 — P3-E real DGX Flash host asset preflight blocked; diagnostic patch/source CI

**Actual operator DGX evidence, no Docker mutation:** `python3 -m scripts.manager.flash_host_assets --json` returned `status=BLOCKED`, issue `FLASH_HOST_ASSET_PREFLIGHT:ValueError`, `legacy_hf_bind_writable=true`, `indexed_shard_count=0`, `metadata_sha256={}`, `template_sha256=null`, `verified_model_revision=true`. This only establishes that the **old observer** advanced past pinned command/env/cache bind, then raised a ValueError during an unidentified local-file validation step. Neither zero shards nor `verified_model_revision=true` proves a missing model or verified revision bytes. **No user-provided evidence of broken inference or failed reinstall.**

**Source fix, not live DGX proof:** [9beb1d3](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/9beb1d3f73675ac4a22daedfc2167b380742305c) adds allowlisted `failed_stage`, `failure_reason_code`, `pinned_command_identity_matched`, `prepared_view_path_observed`, and stops falsely setting `verified_model_revision=true` from a directory name alone. Private exception messages/path/env values are never emitted. Tests cover metadata cap, malformed index, empty/missing/escaped marker, secret exception redaction. GitHub Actions [42391221418](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42391221418) **SUCCESS: 874/874 CPU/Fake-DGX tests across 39 groups** (previous 870 + 4). Real DGX did not run this patch yet.

**Next safe operator command:** `git pull --ff-only origin feature/recipe-wizard-handoff`; then `python3 -m scripts.manager.flash_host_assets --json`. Inspect only redacted `failed_stage` and `failure_reason_code`. No cache repairs, container recreation, GPU activity or permissions escalation should follow from this result without separate evidence/approval. Flash canonical reinstall remains unqualified, lifecycle release disabled, historic P3-G real PASS/CLOSED and P8 NOT_RUN; preserve 27B at :8000.

---

## 2026-11-08 — Operator DGX read-only P3-D PASS + P3-E asset evidence source

Operator's latest DGX read-only `--sudo-ss` P3-D/E/F/G output: **P3-D READ_ONLY_PASS**, independently attributed docker-proxy IPv4 PID `2560693` and IPv6 PID `2560708`, GPU PID `2560905`, no detected GPU ownership conflict. **P3-E DRAFT_REVIEW_REQUIRED** despite `cmd_normalized=true` using `FLASH_FP8HYBRID_READ_ONLY_V1`, `cmd_normalization_error=null`, draft-field `issues=[]`, because canonical reinstall remains unqualified. **P3-F 153/153 DGX-local CPU PASS**. P3-G preview in this particular runner does not invalidate previously completed real bidirectional G. `blocked_stages=[]` with total `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` is expected.

GitHub source: [03cbe4c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/03cbe4cc45a750322c4f99616c85f1061f7b2288), [2b44ccc](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/2b44ccc0237fa34742e28608ad089cb3ca90fe55), and [8e8fcec](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/8e8fcec5acb280e01445a2bd773fc9f4ecedf2f6). Source-only CI [42390619936](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42390619936): **870/870 PASS, 39 groups**, including 5 new Flash host asset tests. Added `scripts/manager/flash_host_assets.py`, `tests/test_flash_host_assets_cpu.py`, and `docs/P3-E-FLASH-HOST-ASSET-PREFLIGHT-20261108.md`. Fixed source-only parser test coverage, empty `.prepared` sentinel handling, and registered 5 new tests in CI + P3-F suite. Did **not** change `recipes/qwen38-27b.runtime.json`, enable Flash canonical install, switch services or run P8 fault injection.

---

## 2026-11-08 — Flash command parser CI confirmation

The 3-test follow-up source commit [bb4d64e](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/bb4d64e02e0d73d6406e6e0d7c593ec86ba4c954) passed GitHub Actions [42388253469](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42388253469): **865/865 CPU/Fake-DGX tests in 38 groups, SOURCE-ONLY**. The operator's 150/150 DGX-local CPU result predates these 3 source tests; new DGX-local CPU execution has not yet been observed. P3-D privileged PID check remains optional explicit operator step; E remains reinstall-unqualified, F unreleased, G historically real PASS/CLOSED, P8 NOT_RUN.

---

## 2026-11-08 — DGX operator read-only P3-D/E/F/G follow-up

**Operator evidence:** `docs/P3-E-F-DGX-READONLY-20261108.md`. At DGX local read-only snapshot, 27B API at :8000 is `LIVE_SERVICE_VERIFIED` with 8/8 checks true. P3-D remains `BLOCKED` only because unprivileged `ss` exposed no port listener PID (`sudo_ss_requested=false`); not a measured GPU conflict. P3-E full Flash draft-field match `issues=[]`, but reinstall unqualified with 37 extra environment keys and zero extra mounts; 27B-only command normalization reported Flash `-cc` tokens as unexpected positionals. P3-F new code ran **150/150 CPU tests PASS on operator DGX**; P3-G is only preview in this run, while prior real two-way G is CLOSED. The source follow-up introduces strict read-only Flash FP8-hybrid argv normalization, no service operations or release gate changes. Historical P3-G, P8 boundaries and Source/DGX classifications remain intact.

---

## 2026-11-08 — P3-E/F source-hardening (no DGX mutation)

Source change: [d68106a](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d68106a24c4c6071acff7a4d98d74e04c6ecbfe1). Actual GitHub Actions [42386939625](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42386939625): **862/862 PASS in 38 CPU/Fake-DGX groups** (856 baseline + 6 new). This is **SOURCE-ONLY**; no fresh DGX test or service change. Full scope: `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

- `scripts/manager/model_lifecycle.py`: stop-intent reconciliation, conditional restart, truthful no-prior-service failure verdict and journal phase.
- `scripts/manager/flash_recipe_review.py`: non-secret coverage accounting, template mount source validation, no full reinstall auto-qualification.
- `recipes/qwen38-flash-next.runtime.draft.json`: replace obsolete G bidirectional blocker with outstanding P8 acceptance.
- `tests/test_model_lifecycle_cpu.py` and `tests/test_flash_recipe_draft_cpu.py`: 6 added regressions.
- New detailed report: `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

Still blocked: Flash canonical reinstall, production lifecycle executor, and P8 real fault/restore/UX/release. Historical G real PASS retained.

---

## 2026-11-07 — P3-A–G EVIDENCE AUDIT / P3-G CLOSED; P8 OWNS FAULT & FINAL RELEASE

**New canonical audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md` and `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`. Stage results: **P3-A/B/C** original immutable one-off real DGX PASS/CLOSED (A Flash→27B, B 27B→Flash, C Flash→27B); **D** real read-only GPU+IPv4/IPv6 host :8000 PID ownership PASS from operator `--sudo-ss` run (pre-latest switch); **E** Flash source `-fp8hybrid` prepared view and versioned draft-field match, but **canonical Flash reinstall recipe UNQUALIFIED** (`DRAFT_REVIEW_REQUIRED`, `launch_allowed=false`); **F** six Fake-DGX/CPU suites **144/144 local PASS**, but `PRODUCTION_LIFECYCLE_RELEASED=false` and generic live install/reinstall not accepted; **G** actual independent 27B→Flash→27B TTY-approved ordinary two-way transfers **REAL PASS/CLOSED** with two receipts, API identities, final 27B `diff=[]`, journal VERIFIED/COMMITTED 28 events, last actual active `qwen38-27b` on port 8000. **P3-A–G aggregate = PARTIAL (E open, F source only)** despite G closed. The user explicitly moved intentional failure injection, automatic restore and final operational/UX/production signoff to **P8** (NEW, NOT_RUN, not authorized to execute). P7 is integration only. Preserve old receipts, model assets and `ONE_ACTIVE_MODEL_ONLY`; no P3 A/B/C/G replays or fault injection to perform this audit. Latest P8-source registration CI [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS 856/856 CPU tests 38 groups (source evidence only). Basic post-switch service manager `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are **NOT PROBED** by that command, not conflicts; do not overclaim fresh D audit. The single-script D–G read-only runner prints G preview even after separate real G PASS by design.

Added a read-only evidence audit of P3-A through G; registered P8 source-only recovery/final acceptance module, separated P7 integration vs P8 final signoff and retained P7 acceptance CLI compatibility. Updated roadmap to P1–P8. Real G both directions accepted, F local CPU pass, E Flash canonical reinstall still open. No DGX runtime/container action from these source/document updates.

---

## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

Recorded P3-G first live operating switch 27B→Flash PASS with fresh 4-input TTY approval, private receipt SHA, postcheck LIVE_SERVICE_VERIFIED on qwen3.8-flash-next :8000 and journal VERIFIED COMMITTED / event_count21. Corrected future plans to current active Flash; reverse and fault injection NOT_RUN. Added `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`.

---

## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

Recorded P3-G explicit user downtime authorization for one-off real DGX operating acceptance, preserved existing live independent 4-input TTY approval; new `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md` step-by-step two separate approved transfers and halt-on-failure. Latest actual D–G preflight D READ_ONLY_PASS, E draft field match only, F 144/144 CPU PASS, G preview PASS. Actual forward/reverse/fault-restoration NOT_RUN and model still last observed 27B.

---

## 2026-11-07 — THIRD ACTUAL DGX P3-D READ-ONLY PASS; P3-E FP8-HYBRID SOURCE DRAFT

**Actual operator evidence:** Third DGX batch after fast-forward to `1b785c6`: normal `--run` reported D no visible socket PIDs but E `DRAFT_REVIEW_REQUIRED`, F local **136/136 CPU PASS**, G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`. Operator then explicitly ran `sudo -v` followed by `--run --sudo-ss`: **P3-D READ_ONLY_PASS**, both IPv4+IPv6 :8000 `docker-proxy` PIDs (2051487,2051502) independently attributed to canonical active 27B; GPU compute PID 2051842 verified. Overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`, `blocked_stages=[]`, `acceptance_complete=false`; no service mutation or real G transfer. **P3-E** pinned NVIDIA `fc694b54fb0174e0913e6adf86691ef85a4ead47-fp8hybrid` derivative prepared/view files verified; canonical reinstall recipe NOT registered. Legacy Flash cache writable; source metadata and vLLM flags preserved. Evidence `docs/P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md`.

**NEW SOURCE P3-E DRAFT (UNRELEASED):** `recipes/qwen38-flash-next.runtime.draft.json` is `launch_allowed=false`, `register_as_runtime_recipe=false`, not linked into service-policy, no Flash install adapter/executor. `scripts/manager/flash_recipe_review.py` checks versioned pinned Flash 500K/Yarn/MTP2/native tools/image/env/template/mount *documented fields only*, returns `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` or explicit field differences. `P3-E.source_draft_field_review` added to single-script report. P3-E stays DRAFT_REVIEW_REQUIRED; direct live DGX comparison of new code still **NOT_RUN**. CI [42373758262](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42373758262) **854/854 CPU/Fake-DGX PASS / 38 groups**, source only. Full runbook `docs/P3-E-FLASH-FP8HYBRID-SOURCE-DRAFT-20261107.md`.

**Next:** read-only `--run --sudo-ss` batch to inspect E draft comparison, then review remaining host env/mount/image provenance. Separate operator-approved real Flash install and G switch/rollback acceptance required; `PRODUCTION_EXECUTION_RELEASED=False` remains. P3-A/B/C closed, 27B unchanged, P4 optional, P5/P6/P7 queued.

---

## 2026-11-07 — SECOND ACTUAL DGX D–G BATCH + PINNED FP8 HYBRID / HIDDEN SOCKET PIDS

Actual operator DGX batch (**read-only; no model changes**) after previous source fixes: **P3-D BLOCKED** because `ss` showed BOTH IPv4 0.0.0.0:8000 and IPv6 [::]:8000 LISTEN but no process PID; Docker reported only running `qwen38-27b` as GPU/8000 port owner, NVIDIA compute PID 2051842 verified to active 27B. **P3-E BLOCKED** because the observed preserved Flash checkpoint was pinned NVIDIA source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47` plus **`-fp8hybrid` local prepared variant**, not a different HF revision; canonical Flash reinstall recipe still unqualified. Flash /hf mount observed writable and legacy argv preserved. **P3-F PASS 128/128 actual local CPU tests. P3-G preview PASS**, current Docker ID and VERIFIED/COMMITTED journal; actual transfer/rollback NOT executed. Overall exit=3, acceptance_complete=false.

Subsequent SOURCE fix: E now recognizes only exact pinned NVIDIA source revision plus `-fp8hybrid` prepared view and verifies `.prepared`/essential files read-only; no recipe promotion. D now permits ONLY operator-selected `--sudo-ss` to run `sudo -n ss` (no prompt; no sudo by default) and independently reverify unchanged socket set and PID provenance. Unknown PID always BLOCKED. CPU CI [42371861344](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371861344) **846/846 PASS / 37 groups**, SOURCE-ONLY, actual DGX rerun pending. Full evidence `docs/P3-D-G-SECOND-DGX-PID-HYBRID-DIAGNOSTIC-20261107.md`. No P3-A/B/C replay, no production switch release.

---

## 2026-11-07 — P3-D/E first actual DGX diagnostics repaired in source, 838/838 CI PASS

User's first read-only D-G DGX runner: D port `ss` single-listener assumption BLOCKED, E Flash legacy `Config.Cmd` canonical-27B parser BLOCKED, F 119/119 CPU PASS, G current-ID and journal PREVIEW PASS; no real switch. Corrected dual-stack socket proof, strict Docker proxy `/proc`/Docker-IP attribution and legacy Flash raw argv/mount capture. Canonical Flash reinstall recipe remains unqualified and production release gates remain locked. Source GitHub Actions 42371091647 SUCCESS 838/838 tests. Full evidence: `docs/P3-D-G-FIRST-DGX-DIAGNOSTIC-FIXES-20261107.md`.

---

## 2026-11-07 — P3-D/E/F/G phase expansion and unified draft source entry point

Committed new common Wizard milestone map (D GPU/port ownership, E Flash recipe, F generic lifecycle, G actual DGX roundtrip/restore/UX) and non-mutating one-command `scripts/temporary/p3-d-g-acceptance.sh` with Python stage orchestrator, Fake-DGX regressions, CI and detailed acceptance contract. Real D-G runner has NOT yet executed on DGX; no service mutation was authorized. Historical A/B/C remain closed. Draft verdicts cannot claim full P3-G acceptance.

---

## 2026-11-07 — LIVE DGX CURRENT-ID ORDINARY SWITCH PREVIEW PASSED READ-ONLY

On actual DGX after operator pulled 4189a79, 27B recipe drift including pinned explicit host cache source yielded no drift/advisories, 27B -> Flash-Next `operational --plan` yielded `READY_FOR_OPERATOR_REVIEW_ONLY`, zero issues, correct current Docker IDs and source CANONICAL_RECIPE / target HISTORICAL_P3_INSTANCE, and manager status `LIVE_SERVICE_VERIFIED`. No model changes were made. Full report: `docs/WIZARD-27B-OPERATIONAL-PREVIEW-DGX-PASS-20261107.md`. Source CI baseline remains 814/814 PASS. Release gates remain disabled.

---

## 2026-11-07 — 27B DGX read-only recipe comparison PASS; current-ID operating switch code source-only

Operator reported `qwen38-27b` LIVE_SERVICE_VERIFIED, image/revision/options matching canonical recipe, `diff=[]`, `issues=[]`, HF bind source `/home/inlc/.cache/huggingface`, restart preview RESTART_EXISTING and explicit reinstall preview RECREATE, no executed change. Source updated `operational_switch.py` and `operational_executor.py` to bind the current container ID and distinguish 27B canonical recipe from historical P3 instance. Read-only CLI now accepts `--cache-source /absolute/path`. Source CI 42367665200 SUCCESS **814/814 tests, 36 groups**; no DGX switch or production release. See `docs/WIZARD-27B-LIVE-DRIFT-CURRENT-ID-20261107.md`.

---

## 2026-11-07 — SOURCE implementation of generic recipe drift and model lifecycle (NOT a new DGX mutation)

GitHub CI 42355750124 SUCCESS: **799/799 CPU/Fake-DGX tests**, 36 groups. Added scripts/manager/recipe_drift.py, scripts/manager/model_lifecycle.py, tests/test_recipe_drift_cpu.py, tests/test_model_lifecycle_cpu.py; extended Wizard CLI router, model menu option 7, CI workflow; documented in docs/WIZARD-LIFECYCLE-SOURCE-IMPLEMENTATION-20261107.md. Production lifecycle executor remains source-only and unreleased; no Docker/API/GPU change. Earlier live P2/P3/cleanup outcomes remain immutable historical evidence; latest actual operator state was canonical 27B running on :8000.

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

## 2026-11-07 — P2-FINAL protected Native Tools V1 SOURCE implementation (no DGX operations)

Created distinct `qwen38-27b-native-tools-v1` source candidate and deliberately unqualified pinned recipe; implemented read-only source/original/fallback/port/GPU inspection with no execute, plus strict SSE auto tool-call parsing with bounded data/time and HTTP/error guard. New offline regressions cover original immutability, variant collisions, other GPU users, source image/port/cache drift, malformed/truncated streaming/JSON and model mismatch. Extended `scripts/serve_27b.sh` CLI. Documented isolated cutover, independent approval, journal and rollback contract as **future implementation gates**; do not confuse SOURCE/CPU with actual DGX acceptance. Existing P3-C, original 27B/Flash, cache, operating journal and normal Wizard production gate untouched. P2-FINAL remains OPEN.

---

## 2026-11-07 — Latest DGX operational reverse postcheck VERIFIED; P2-FINAL Tool Calling HTTP 400 confirmed

Operator fast-forwarded to `09c6780`; verified real running `qwen38-27b`, `:8000` `LIVE_SERVICE_VERIFIED`, sole `qwen3.8-27b`, `issues=[]`; independent operating journal `VERIFIED/COMMITTED`, 14 events. Direct Docker `Config.Cmd` confirms absence of all tool-auto/parser/reasoning flags from preserved 27B, while source opt-in tool profile displays expected candidate flags. Real bounded local `--tools-probe` returns `BLOCKED/LOCAL_API_HTTP_ERROR_400` with no structured call/continuation; no destructive or lifecycle actions. This **closes the earlier reverse-postcheck gap** while keeping **P2-FINAL Native Tool Calling NOT_QUALIFIED**. Original P3-C historic PASS unchanged, normal main Wizard production gate OFF. New task: protected tool-enabled 27B variant and separately approved transition/rollback design; Open WebUI Native and streaming tests pending.

---

## 2026-11-07 — P2 final tool-calling opt-in source / P3-C completed-history freeze

Per operator ordering, created dedicated final P2 item for 27B Native Tool Calling. Verified official Qwen3.8-27B vLLM flags `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`; implemented opt-in candidate argv flag (legacy P2 launch remains unchanged), source-only profile and bounded localhost structured auto tool-call/continuation probe (no real tool execution, no Docker mutation), plus 27B dedicated entrypoint flags and Fake-DGX regression suite. Historical P2 GPU/benchmark passed and P3-C Stage A/B/C passed on DGX unchanged; appended P2 Tool Calling requires real parser/migration/Open WebUI tests before full P2 closure. Last actual ordinary reverse Flash→27B trial PASS, independent final status/audit still not supplied. Production main Wizard remains release gated; no P3-C rerun, no asset deletion or PR merge.

---

## 2026-11-07 — Independent post-switch Flash service and journal VERIFIED; reverse 27B plan ready

Operator subsequently read live DGX service: `flash-next` ACTIVE / `LIVE_SERVICE_VERIFIED`, sole `qwen3.8-flash-next` on :8000, `issues=[]`; operating journal `VERIFIED`, `COMMITTED`, 7 events, no issues. Separate read-only ordinary reverse plan `flash-next→27b` `READY_FOR_SEPARATE_TRIAL_APPROVAL`, issues none, **not executed**. First 27B→Flash physically accepted switch is now corroborated by independent read-only after-checks. Reverse still needs fresh explicit downtime consent and manual exact approvals. No new model transfer/cleanup or PR merge in this documentation update.

---

## 2026-11-07 — First REAL DGX normal Wizard switch PASS: NVIDIA 27B → Flash-Next

Operator supplied terminal showing source fast-forward to `4054eb2`, current 27B API `LIVE_SERVICE_VERIFIED`, independent operating journal `EMPTY`, exact fresh operating acceptance plan ready, and four human TTY approvals. The tracked new `operational-switch-acceptance.sh --target flash-next --execute` returned `Live transition result: PASS`, `Observed model: flash-next`, and new immutable private completion receipt. This proves first **ordinary** backend physical transfer, not one-off P3 replay. The independently verified source CI remains 671/671 CPU Fake-DGX. No reverse action, real rollback trial, production menu release, model deletion, Tool Calling recipe work or PR merge. The current last observed model is now Flash-Next, superseding prior 27B-active claims.

---

## 2026-11-07 — End-to-end source implementation of ordinary model-switch Wizard, independently gated DGX trial

Implemented existing `./wizard.sh` model-first main entry and target selector; separate guided review and eventual three-input production action flow, source gate still OFF; strict domain-separated execution SHA vs preview; trial-only `operational acceptance` CLI with four exact TTY acknowledgments and tracked wrapper; extra expiry/TTY/JSON cancel gates. Hardened new operating executor's pre-stop cancellation (no downtime on stale source), foreign-GPU post-start check, bounded target chat inference, terminal immutable receipt and journal audit before PASS. New read-only `operational_audit` checks event-log hash chain vs snapshot and missing committed receipt to fail closed after crash. Added multi-direction Fake-DGX acceptance, rollback, mismatch, expiry, noninteractive cancellation and journal corruption CPU tests, workflow wiring, main menu, roadmap and runbook. No ACTUAL DGX operating switch or recovery was attempted; no active 27B changes, model cleanup, P3 replay or Draft PR merge. Deferred Open WebUI Tool Calling.

---

## 2026-11-07 — Restore Wizard ordinary operating switch priority; release-gated UX/backend link (SOURCE)

Created `scripts/manager/operational_wizard.py` for target-first switch review, source-safe independent authorization fingerprint, three exact approvals and fake-only backend dispatch. Wired into existing `./wizard.sh` interactive model option 6 and grouped CLI `switch flash-next-27b operational guided --target ...`. Updated existing independent executor to reject preview-only SHA; Fake-DGX unit/integration tests and CI workflow. Production gate false, no real Docker/GPU switch; P3 immutable historical stages untouched. WebUI Tool Calling and 27B recipe support **deferred** per operator correction, not current focus.

---

## 2026-11-07 — WebUI native tools mismatch; 27B no-thinking exact output PASS

Real operator direct 27B curl with per-request `enable_thinking=false` returned exactly `DGX_OK` (4 tokens), while Open WebUI emitted vLLM tool-choice auto configuration error. Read-only Git source review identified missing `--enable-auto-tool-choice` / `--tool-call-parser` in 27B candidate launcher, unlike Flash; actual current Docker command still not observed. Added `docs/OPENWEBUI-27B-TOOL-CALLING-20261107.md`, recommended WebUI Builtin Tools-off workaround and separate future startup-profile/parser qualification gate. No source executor changes, DGX restarts, model switch, deletion or PR merge.

---

## 2026-11-07 — Real DGX 27B curl verification PASS, formatting anomaly isolated

User supplied successful actual localhost /health, single /v1/models identity and two chat-completion probes (direct raw request and tracked shell smoke); tracked script emitted `27B_CURL_SMOKE_PASS`. Recorded actual active 27B pinned NVIDIA revision, vLLM 0.32.0 and 26-token direct reply. Reply contains reasoning-like prose and literal `</think>` in `content` despite `reasoning=null`: distinguish healthy inference from failed exact-format compliance, no speculative server-side repair. Follow-up `FORMAT_PASS` / `FORMAT_DEVIATION` classifier and offline fake-curl tests source-only. Maintained Draft PR, 27B state, Flash preservation and unqualified general operating switch.

---

## 2026-11-07 — Separate current 27B curl inference smoke from identity-only switch preview (source only)

Added one-command non-disruptive localhost `curl` 27B smoke with explicit /health, /v1/models and one bounded /v1/chat/completions verification; Fake-CPU failure modes and CI; Wizard ordinary-switch hint; operating switch UX doc and permanent handoff updates. Does **not** enable ordinary switch dispatch, perform real DGX curl, repeat P3 A/B/C or alter Docker/GPU service state. Await operator's actual 27B smoke output.

---

## 2026-11-07 — Ordinary model-switch preview, source-only transaction and Fake-DGX tests

- Added \`scripts/manager/operational_switch.py\`: strict independent read-only candidate (historical P3 provenance, fresh API, pinned Docker identity, foreign GPU and journal blockers), rotating non-executable fingerprint.
- Added \`scripts/manager/operational_executor.py\`: guarded backend source for independent exact plan and two acknowledgments, separate lock/journal/attempts, stop-before-start, port/model identity, post-switch verification and best-effort restoration. **Not routed to any CLI or TTY execute; not DGX qualified.**
- Updated model-first TTY \`wizard/console.py\` and P3 switching adapter to display an ordinary read-only switch preview without recommending replay of one-off stages.
- Updated \`wizard/roadmap.py\` to separate local historical P1/P2/P3 evidence, current API, general switching, interactive UX and release qualification.
- Added fake-DGX preview/transaction tests \`test_operational_switch_cpu.py\` and \`test_operational_executor_cpu.py\`; enrolled in \`.github/workflows/recipe-manifest-cpu.yml\`.
- Created \`docs/OPERATING-SWITCH-UX-CONTRACT-20261107.md\`. Actual DGX 27B remains untouched, assets and P3 receipts preserved; Draft PR #1 still open/unmerged.

---

## 2026-11-07 — P3-C 실제 최종 PASS, 새로운 P1–P7 수용 현황 및 대화 시작 프롬프트 최신화

실제 DGX 운영자가 새로운 P3-C 계획/3개 독립 승인으로 전환했고, canonical Wizard가 `status=PASS/stage=c/executed=true/live_verified=true/active_model=27b`를 반환했다. wrapper `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, `issues=[]`; 원본 `stage-c.json` 증거 보존. 이 결과는 10분 경계에서 승인 부족으로 BLOCKED되었던 과거 시도를 supersede하며, **현재 마지막 관측 모델은 NVIDIA 27B ACTIVE :8000**. 최신 Git 모델별 벤치 2개도 actual DGX private source와 VERIFIED.

모든 핵심 doc 경로를 재조회하여 필수 핸드오프/마스터 플랜/운영 계약/Manifest/벤치/단계별 P3 runbook의 **파일 미존재 없음**을 확인. 다만 기존 `handoff/SESSION-START-PROMPT.md`, `README.md`, `CHANGELOG.md` 및 일부 이전 계획의 첫 문단이 과거 P3-C NOT_RUN으로 시작하는 문서 최신화 누락을 발견. 새 시작 프롬프트를 P3-C 완료 이후 UX 작업 기준으로 갱신하고, `docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md`를 추가하여 실제 DGX P1-P3 백엔드 PASS와 일반 Wizard 메뉴 UX 수용 미완료를 분리했다. 원본 증거·GitHub Draft PR·활성 27B 서비스는 변경하지 않았다. `wizard/roadmap.py` P3 정적 상태와 `wizard/console.py` P3 plan-only 메뉴는 **다음 소스 개발의 확인된 갭**, 이번 문서 작업에서는 실행 코드 변경 없음.

---

## 2026-11-07 — Fixed P3-C 10-minute plan-boundary operator refusal, source only

Actual operator runs at 10:08:14 and 10:09:30 KST, both ending in `P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS` with `executed=false/execution_dispatched=false`, revealed the canonical expiring plan window UX issue while Flash remained active. No real Stage-C transition occurred. New `scripts/temporary/p3_stage_c_operator.py` bounded 150s **read-only** refreshes stage-C plan and live Flash source until a NEW, fully provenance-qualified SHA with >=120s remains; rejects early unexpected SHA change, foreign current model, missing P1/P2 evidence, dirty Git, timeout/interrupt. Old plan and approvals never reused. Still requires three fresh exact manual inputs and independently calls unchanged canonical guarded Wizard. `--plan` stays immediate/non-mutating. Added fake DGX virtual-clock and newly authorized SHA execution regression tests. Operator pulls latest branch after CI and can run `bash scripts/temporary/p3-stage-c-operator.sh --execute` under existing explicit operator Flash downtime consent. No model deletion, no PR merge, no GPU activity in source changes.

---

## 2026-11-07 — Git-public benchmark snapshots, source-only exporter and post-C cancellation evidence

Published **two** model-named, Git-tracked, metric-only benchmark JSON files in `benchmarks/published/` with original receipt SHA256 and standardized metadata. Original user-observed Flash-Next post-B throughput 37.9527 tokens/s, and 27B trial-with-Flash-restore E2E 7.9002 tokens/s / decode proxy 11.1801 tokens/s; both 3 sequential requests max64 tokens. Numeric source values are grounded in supplied operator logs, not newly run models or normalized performance comparisons. Original private `~/.local/state/blazux-wizard` JSON, `reports/`, host paths, approval IDs, prompt/output and Docker logs remain Git-ignored/unpublished. Added allowlist-safe deterministic `scripts/manager/benchmark_publication.py` with `--plan`, `--verify-published`, exact original-SHA-gated `--write` and 12 fake-CPU tests, and read-only `scripts/temporary/verify-published-benchmarks.sh` checking published results against original DGX receipts. `--write` never stages/commits/pushes. Actual DGX original-to-public verifier NOT_RUN yet; request operator pull and run.

P3-C previous `--execute` output `CANCELLED` before dispatch because SHA was typed with leading `[`. No model transition occurred in that attempt. New C SHA and separate explicit live downtime confirmation required if proceeding. PR #1 Draft/unmerged.

---

## 2026-11-07 — Final P3-C tracked operator, actual C read-only plan READY

User's latest actual DGX dump shows C canonical `--plan` status READY/no issues/P1 post-B evidence PASS with original Flash active and preserved 27B offline; optional P2/P3 historical evidence import was CANCELLED/copied=0 (typed `COPY`, not SHA). No service changes. Added D-016 `scripts/temporary/p3_stage_c_operator.py` and `scripts/temporary/p3-stage-c-operator.sh`: default read-only plan, new P3-C-specific three exact TTY confirmations, action-bound fresh replan, canonical Wizard only for `--execute`, final 27B `:8000/v1` and immutable `stage-c.json` checks, Git-ignored private report `reports/transitions/flash-next--to--27b` and fail-closed recovery uncertainty. Added isolated fake-DGX `tests/test_p3_stage_c_operator_cpu.py` + GitHub workflow. Success intentionally leaves 27B active; original Flash model/image/container preserved. Actual C still NOT_RUN/NOT_AUTHORIZED; separate human downtime consent remains mandatory. [Operator instructions](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md). No PR merge.

---

## 2026-11-07 — Wizard model history and P2/P3 non-destructive consolidation

New `scripts/manager/evidence_catalog.py` reads model-centric historical Verify/Benchmark, 27B GPU trial/benchmark, P3 stage transitions and Flash diagnostics from existing private `~/.local/state/blazux-wizard` paths and new project `reports/`. Main Wizard adds model option **4** for categorized read-only history, Advanced option **8** to request a guarded copy-only import; CLI `./wizard.sh evidence list --model ... --kind ...` and `evidence migrate --plan|--guided`. Current SHA is repeated in guided approval prompt like P3. Copies use 0600 O_EXCL, 0700 directories, byte-identical SHA256 dedup, and legacy P2/P3 live state/journal/locks/attempt markers remain canonical/unmoved. P3 stage-B historically misnamed operator report classified by stage content, not filename. Additional CPU-only fake evidence tests, no CUDA/Docker inference performed. See [contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md). P3-C next step is **read-only** `./wizard.sh switch flash-next-27b stage-c --plan --json`, NOT a user-approved switch. Draft PR unmerged.

---

## 2026-11-07 — Model-centered Wizard / post-B real GPU receipts / evidence path contract

User's original DGX ZIP shows Flash-Next post-B Verify baseline+extended PASS and separate bounded Benchmark PASS (mean 37.9527 tokens/s, TTFT P50 1.384594 s). Distinct exactly approved original receipts remain in `~/.local/state/blazux-wizard/p1`; latest P1 diagnostic rc3 issue disposition PASS and P3-B stage-B PASS are immutable. Code updated for exact P3-style approval prompt, one selected action, output of Verify and numeric Benchmark, no P1-number UX, and new Git-ignored repo `reports/models/qwen3.8-flash-next` for all **future** P1 execution receipts. P3 stage-C evidence gate now reads both paths and ranks by finished timestamp; a newer failure must block. New CPU tests include prompts, no duplicate menu, and migration safeguards. Source CI at [workflow 42313905291](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42313905291) passed **508/508 tests** across 23 groups at source commit `287c81d4a9225ef6e27e5641dda15890ea98ca28`; later label/docs commits require rechecking latest CI. No actual DGX UX re-execution, P3-C or PR merge. See [contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

## 2026-11-07 — FINAL SOURCE CI / DRAFT PR REVIEW CHECKPOINT

Source, regressions, permanent docs and read-only DGX audit workflow have been committed to existing `feature/recipe-wizard-handoff` and Draft PR #1. Source-tested HEAD `67ff9cc2e4ece0c89c911513673f7d5d55c98fa4`: GitHub Actions [push 42310408411](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42310408411) **SUCCESS, 501/501 CPU tests across 23 groups**; PR run 42310415255 also checked separately. Explicit [Draft PR review #5808289782](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1) recorded, with live DGX P1/ P3-C blockers, not approved/merged. The subsequent handoff documentation commit does not authorize runtime work; latest branch HEAD/CI must always be rechecked. Only permitted next operator check is `bash scripts/temporary/p1-post-b-audit.sh` after fast-forward pull and CI pass.

---

## 2026-11-07 — P3-B actual completion reconciliation and POST-B read-only audit

- Received user-supplied DGX actual P3-B success: canonical stage-B `PASS/executed=true/live_verified=true`, wrapper `P3_B_PASS_FLASH_NEXT_ACTIVE`, active `qwen3.8-flash-next`. Original wrapper report historically misnamed `p3-a-operator-20261106T223124Z-14861d75.json` and contains stale `approval_accepted=false`; preserve it unchanged.
- Source commit `23cf10de47ab85417e646a06245d8a70e0b2e849`: stage-aware operator evidence prefix, correct manually accepted approval vs execution dispatched fields, regression tests; no actual P3-B replay.
- Source commit `ea1a4ca1629acfd519fbfa839b615f45dd91c86e`: GitHub-tracked P1 POST-B audit (read-only only), exact raw rc3 diagnosis, private append-only receipts, latest-attempt P3-C evidence gate and fake-DGX tests. Initial CI reported SUCCESS; subsequent hardening commit `94622bc100a6f34b26603ac736b8b672ba26d24e` requires latest CI outcome check.
- Reconciled handoff CURRENT-STATE/NEXT-ACTIONS/EVIDENCE-LEDGER/DECISIONS and operating docs. Old records preserved below for chronology.
- Actual user-reported P1 post-B inspect-only PASS/Verify+Benchmark plan READY at `/home/inlc/blazux-p1-reports/20261106T224010Z-d2095867/result.json`. This is NOT a fresh post-B functional or performance execution. Full post-B rc3 evidence remains pending a **new DGX read-only audit**.
- P3-C NOT_RUN/NOT_AUTHORIZED. No Docker, GPU inference, service stop/start, model/cache deletion, PR merge, or old receipt overwrite performed by GitHub-only source work.

---

## 2026-11-06 — P3-B real read-only inspection PASS; implement independent 27B downtime/entry gate (489 CPU PASS)

Actual user DGX B inspector after P3-A returned `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`; verified running 27B API ID and container and preserved original Flash CID/image, P2/A hashes, `executed=false`. B originally inherited wrong Flash downtime ACK from shared canonical core; now B-specific `I_ACCEPT_27B_DOWNTIME` + `I_SEPARATELY_AUTHORIZE_P3_STAGE_B`, A/C unaffected. Created `p3-stage-b-operator.sh` and Python with default read-only, gated real B `--execute` requiring separate user scope approval + three exact terminal inputs, replan/expiry, independent Flash API check, no auto P1/C. Fake-DGX CPU PR [42190159738](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42190159738) SUCCESS **489/489** tests, source `59046c4e17a5094f2c80a84025a763c2a767edcb`. No GPU/Docker effects or user B consent from GitHub work; 27B remains live as of provided DGX evidence.

---

## 2026-11-06 — DGX P3-A real PASS; 27B active, prepare B read-only inspection

Actual operator-run persistent P3-A with exact latest plan and independently typed downtime/P3 entry acknowledgments succeeded: Wizard stage-A PASS/executed/live-verified; wrapper `P3_A_PASS_27B_ACTIVE`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`, no issues. Receipts `~/.local/state/blazux-wizard/p3/stage-a.json` and `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. 27B remains running. D-039 explicitly distinguishes this from prior stale-plan refused attempt and withholds B/C permission. Added tracked source/CPU-tested **read-only** B inspector verifying actual A receipt and preserved Flash identity through canonical Wizard API/plan; zero service mutation, no B execute mode, D-016 GitHub→DGX pull→single wrapper workflow. Post-B P1 verify and numeric benchmark + final C still pending; Draft PR not merged.

---

## 2026-11-06 — Fix P3-A exact confirmation UX and expired 10-minute plan refusal (459/459 CPU PASS)

User entered all three correct stage-A approvals, but plan `94b4deda...` expired at 16:30:00 KST (report 16:30:49 KST), Wizard refused `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT` with `executed=false`, no actual transition. Updated GitHub-tracked D-016 `p3_stage_a_operator.py` to display actual full required SHA/ACK literal at each terminal prompt, plan expiry KST and seconds left, fail before prompting with <120s left, replan read-only after manual input, and classify canonical stale refusal as `BLOCKED` rather than `OPERATOR_REVIEW_REQUIRED`. New fake-DGX tests assert exact prompts, short-window refusal, changed SHA refusal, no hidden retry. [CPU PR CI 459/459 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42181858236) at code `fb34ce0ce985824cecd9c63159bf6f1eed408279`. No model switching, service lifecycle, GPU or cache mutation from GitHub. D-016 operator fast-forward pull and single wrapper, fresh exact approvals still required.

---

## 2026-11-06 — P1 pre-A real DGX PASS; first persistent P3-A D-016 operator runner SOURCE tested

User ran the fixed GitHub-tracked P1 pre-A script on actual DGX HEAD `834f823a76556a37a982e3dbf7f243db3edad6df` and supplied `PRE_A_P1_REVIEW_READY`, no issues; historical/current expected own Flash collision 2/2, original verify PASS and measured benchmark PASS (3 samples, mean 38.2968 tok/s). Original condition for P3-A now satisfied for **eligibility**. Added GitHub-tracked `p3-stage-a-operator.sh` Python wrapper: default read-only, separate `--execute` with TTY and exact typed stage A plan ID, downtime and P3 entry acknowledgment; canonical Wizard does actual stop→start→observe, wrapper verifies 27B live model/image independently and writes 0600 local report. Fake DGX tests cover wrong IDs, foreign service, missing P1, expired plan, no TTY, cancel, success postcheck and failure/no retry. D-034 B→Flash, full post-B P1 rebenchmark and C→27B remain separately approved steps; no P3 actual GPU run or GitHub PR merge here.

---

## 2026-11-06 — Correct P1 pre-A cache diagnosis persisted JSON location (439 CPU PASS)

Operator's real pre-A audit with both historical/current rc3 exact own-model collisions and P1 verify+numeric benchmark PASS returned `BLOCKED` on asset audit and revision drift. Found both arose because temporary script read console-only `cache_diagnosis` rather than persisted `checks.cache_diagnosis.stdout`. Fixed to reuse original JSON reader, classify unobservable revision separately from actual mismatch, and fake-DGX test actual persisted schema and negative evidence paths. [CI 439/439 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42176224898) on code `9adc9ab282a91c02e959dcb5c62f98527b556391`. No DGX model, GPU or :8000 mutation; await D-016 single script recheck after pull.

---

## 2026-11-06 — P1 pre-A tracked audit / genuine identity schema fix, 435 CPU PASS

D-016 operator correction honored: GitHub tracked pre-A wrapper and unit tests first, DGX fast-forward pull then one wrapper; no ad hoc pasted Python. Wrapper reconciles local original P1 verify/bench receipts (3 samples, actual 38.2968 tok/s etc) with 2026-11-05/06 doctor/inventory raw outputs and fresh Flash service API; outputs private 0600 evidence with no GPU/Docker lifecycle. Corrected pre-A and post-B P3 P1 identity gate to match `require_model`'s real `{"health":"PASS","models":[...]}` rather than nonexistent `identity.status`. [Latest tested PR CI](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42173805888) **435/435 CPU PASS** at `75d22ce4303736ee84563a0f388a978379e4f228`. No actual DGX wrapper execution or P3-A transition occurred.

---

## 2026-11-06 — P1 numeric evidence received; D-016 script-first workflow restored

User supplied actual P1 benchmark receipt 3/3 PASS, 192 completion tokens, TTFT P50/P95 1.398707/1.751198s, latency P50/P95 1.687357/1.780142s and 38.2968 tokens/s mean. New actual 2026-11-06 P1 `--inspect-only` report source/Hybrid READY and API original ID; inspect-only BLOCKED actions are non-execution by design, not P1 failure. Doctor/inventory rc3 raw not yet available. D-016 mandates temporary script → GitHub push/CI → DGX pull → one wrapper, not pasted one-off terminal code. Added `p1-pre-a-readiness.sh` + Python and CPU fake DGX tests to reconcile both raw rc3 reports, original P1 receipts and fresh live API; writes private JSON, cannot perform actual model switching. Conditional P3-A approval remains pending evidence review; D-034 B then P1 rebenchmark then C still binding.

---

## 2026-11-06 — P1 pending audit / conditional P3-A approval unmet; correct active-service rc3 validation

Reviewed P1 operator proof: functional Flash-Next verify and bounded benchmark PASS, but numerical timing/tokens-per-second not supplied and doctor/inventory rc3 raw cause unresolved. User approval for Flash→27B is conditional on nothing remaining in P1, so no live switch. Audited `inventory.main`: an already running Flash container and occupied :8000 intentionally causes rc3 without read errors. Replaced post-B P1 diagnostic gate's impossible rc0 check with strict full doctor/plan JSON collision evidence for exact active Flash name/image/:8000, retaining historical reviewed disposition and new post-B verify and measured benchmark receipt prerequisites. Five negative CPU tests added (missing raw output, read errors, wrong image, wrong port, rc0 shortcut). [CI 418/418 PASS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42172127412) on source `26a6950`. No GPU or service action.

---

## 2026-11-06 — Correct P3 sequence-status wording; guard foreign GPU during rollback; 413 CPU PASS

Kept global P3 `sequence --plan` BLOCKED/no plan ID while displaying accurate existence of separately approval-gated A/B/C source adapters, not-yet-qualified DGX runtime. Hardened `p3_persistent_switch._restore` to abort original model restart if new unexpected GPU-enabled Docker containers appear after failed target stop; added bounded fake-Docker tests for collision and normal restoration. On source commit `02bf94c1628828ce22fa338dd5a8e5a0955f9179`, GitHub Actions [push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170050031) and [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42170056860) **413/413 CPU PASS**, 19 suites. An intermediate test fixture newline failure was resolved. No actual DGX P3 switch executed.

---

## 2026-11-06 — Actual P3-A read-only readiness observed on DGX; no transition executed

2026-11-06 DGX operator read-only observation: current Flash-Next `qwen38-flash` on :8000/v1, `LIVE_SERVICE_VERIFIED`, served ID `qwen3.8-flash-next`, image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, exact container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Manifest/API check array 8/8 true, `issues=[]`, `executed=false`; **GPU exclusivity and process ownership remain unverified**, and current identity is not historical rollback proof. `sequence --plan`: `status=BLOCKED` with only `P3_SEPARATE_OPERATOR_ENTRY_REQUIRED` by D-034 (expected), with successful local P2 receipt SHA-256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`, evidence path `/home/inlc/.local/state/blazux-wizard/p2/20261106T042642Z-0cacd3f29370.benchmark.json`. `stage-a --plan`: `status=READY_TO_REQUEST_TRANSITION_APPROVAL`, `issues=[]`, source `flash-next`, target `27b`, `plan_id=79be6bf05cb02306ec9155ade317e06c457238de427417ebab8946e35449247a`, expiry epoch `1793943600` (2026-11-06 14:40 KST), target image equal to preserved local Docker image ID, expected target container ID null (not yet created), `executed=false` and `operations_enabled=false`. **This was a plan only, not scoped downtime approval or P3 entry**; plan IDs must be regenerated when stale and must never be reused across stages. No GPU/Docker/service mutation was performed by these read-only queries.

Documentation-only evidence receipt; source P3 stages and CI are separate. No operational approval inferred from `READY_TO_REQUEST_TRANSITION_APPROVAL`.

---

## 2026-11-06 — Implement P3 A/B/C persistent switching source and P1 evidence gate; CPU CI green

Introduced `scripts/manager/p3_persistent_switch.py` with distinct guarded P3 phases A/B/C, fresh observed Docker/API source and preserved target identity checks, short-lived exact approval plan, safe stop-before-start, rollback attempts, private stage receipts, attempt lock and append-only service journal. Added `scripts/manager/p3_p1_evidence_gate.py` to require new post-B P1 functional, numerical benchmark and reviewed historical rc=3 root-cause proof before C. Wired `wizard/menus/switching/flash_next_27b.py`, interactive `wizard/console.py` **plan-only** stage choices and `wizard/main.py` help. Preserved legacy read-only `sequence --plan`, blocked retired `roundtrip`. Extended CPU regression in `tests/test_p3_persistent_cpu.py` and added it to CI YAML.

CI after fixes: [push 42168518712](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168518712) and [PR 42168524464](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42168524464) SUCCESS, **411/411 CPU tests**, 19 groups. Recorded failed interim runs and their corrected syntax/mock fixture causes in Actions history, no test weakening. New [P3 source runbook](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md) details approval and known limitations. **No actual DGX P3 transition or P1 rerun.**

---

## 2026-11-06 — Record actual P2 27B benchmark PASS and Flash-Next restored, close P2 stage

From operator-supplied DGX execution result: NVIDIA 27B model/API/inference and three bounded streaming requests succeeded (`BENCH_PASS_RESTORED_VERIFIED`); original Flash-Next was restored and independently observed by the Wizard as `LIVE_SERVICE_VERIFIED`. Recorded precise latency, TTFT, client throughput proxies and private DGX evidence paths in CURRENT-STATE and EVIDENCE-LEDGER. This corrects earlier plan-only `NOT_RUN` reporting without claiming direct inspection of private DGX files. No Docker/GPU state changed while editing sources. **P2 finished; P3 not auto-started; D-034 governs all future P3 stages.**

---

## 2026-11-06 — User changed P3 sequence; P2→P3 no-auto boundary enforced in source

Per D-034, retire old 2x temporary Flash-Next→27B→Flash-Next P3 plan/execute (now fail-closed even with past approval IDs). Add `scripts/manager/p3_transition_sequence.py` and `./wizard.sh switch flash-next-27b sequence --plan --json`: read-only, no executable plan, no automatic transition. P3 must be entered separately, establish verified active 27B, switch 27B→Flash-Next, resolve P1 deficiencies + real benchmark while Flash-Next running, then separately switch Flash-Next→27B as final state. The source code/CPU tests do NOT implement or verify permanent switching. P2 actual benchmark still awaited, and no operational Docker/GPU calls made while editing. D-033 superseded.

---

## 2026-11-06 — P2 exact-approved 27B benchmark and P3 gated two-roundtrip source implementations

Created `scripts/manager/p2_27b_benchmark.py` with separate benchmark plan/ack, 3 bounded streaming requests, client metrics and private final success+restore evidence, delegating all GPU/container transitions to existing approved one-shot executor. Wired `./wizard.sh model 27b benchmark --plan/--execute` and `scripts/serve_27b.sh --bench-*`. Added `scripts/manager/p3_27b_roundtrip.py` with plan blocked until real P2 benchmark PASS, exact separate approval and two sequential, original-ID-checked return-to-original cycles. Wired `./wizard.sh switch flash-next-27b roundtrip --plan/--execute`. Added CPU fake-backend tests and CI. **Source only: no new DGX GPU benchmark, P3 cycle or permanent service switch executed.** See [P2/P3 procedure](../docs/P2-27B-BENCHMARK-AND-P3-ROUNDTRIP.md).

---

## 2026-11-06 — Real DGX installed-model scan confirms preserved original Orcarouter

User ran Wizard `model list --installed --json` and supplied `READ_ONLY_INVENTORY`: 3 registered model snapshots (Flash-Next 11/11 shards, 27B 3/3, original Orcarouter 17/17; no missing weight shards), and 4 unregistered HF cache snapshot sightings. Legacy Orcarouter BF16/MTP recipe directory **present**. Current Flash-Next API `LIVE_SERVICE_VERIFIED`. No changes to GPU/service/weights. Orcarouter source presence is empirical; recipe/runtime qualification remains unverified. Record separately from prior actual 27B GPU `PASS_RESTORED` and from yet-to-run 27B benchmark.

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

## 2026-11-06 — REAL Qwen3.8-27B GPU PASS_RESTORED and unified Manifest-led Wizard status

Operator supplied actual DGX `--trial-execute` result: `executed=true`, `target_api_ready=true`, `inference_ok=true`, `trial=PASS`, `restoration.status=RESTORED`, `issues=[]`, `status=PASS_RESTORED`. This supersedes earlier source-only `NOT_RUN` statements. User requested canonical Manifest-based Wizard read-only status rather than ad hoc Docker/curl. Implemented `scripts/manager/service_status.py` and unified `./wizard.sh service manager status --json`; added CPU fake-backend tests and updated routing. Kept old `inventory`, `health`, `logs` non-mutating. Combined status NOT_RUN on real DGX until operator invocation; no further actual GPU model or service changes made during this source update. See `handoff/P2-27B-GPU-TRIAL-PASS-20261106.md`.

---

## 2026-11-06 — Qwen3.8-27B experimental GPU trial (explicit approval, restore original)

After actual DGX 9/9 CPU import/ModelOpt registry PASS, implemented `scripts/manager/p2_27b_gpu_trial.py` with exact 64-character fresh plan approval, downtime acknowledgment, bounded initial 27B launch (NVIDIA ModelOpt mixed, no MTP), health/model ID + tiny generation test, private logs and exact original Flash-Next `:8000` container restoration. Added `--trial-plan`/`--trial-execute` to dedicated `serve_27b.sh`. Unknown Docker state or competing GPU container blocks start/restoration; trial never removes original. CPU regression CI `ea28b0c0` 354/354 PASS. **Actual 27B GPU trial and rollback NOT_RUN yet**. Compared MiaAI-Lab/Unsloth, NVIDIA forum GB10 recipe, eugr and NVIDIA guide; checkpoint formats not interchangeable.

---

## 2026-11-06 — Resolve 27B CPU import check false-negative

Observed the operator's actual isolated CPU import with Qwen3.5 and ModelOpt classes all present, but TypeError when our test incorrectly invoked vLLM `ModelOptMixedPrecisionConfig.get_name()` without `self`. Replaced with public vLLM quantization factory lookup under `modelopt_mixed` and exact returned class identity, without constructing quant config or model. Added 3 extra CPU tests plus instance-method regression; CI `0a14f189` **336/336 PASS**. Test must be re-run on DGX; runtime/launch still blocked.

---

## 2026-11-06 — Post-split DGX accepted read-only 27B entrypoint; new opt-in CPU import probe

Reconciled real DGX fast-forward and actual `serve_27b.sh --status/--plan` JSON, including verified original Flash-Next API identity and identical original/target local vLLM 0.32 image IDs. Added isolated `scripts/manager/p2_27b_loader_import_audit.py`, `scripts/temporary/p2-27b-loader-import-audit.sh`, and 8 CPU tests. It imports installed vLLM Qwen3.5 and ModelOpt class and verifies `get_name()=modelopt_mixed` under restricted CPU runc (opt-in; not run on DGX yet); no inference/weights/GPU/cache/network/ports. Source CI `834c750` **333/333 PASS**; 27B GPU/service stop/start/switch remains blocked.

---

## 2026-11-06 — Separate dedicated Flash-Next/27B server entrypoints

Moved existing Flash-Next launch implementation into executable `scripts/serve_flash-next.sh` and routed `./flash serve` directly to it. Replaced `scripts/serve.sh` with compatible default Flash-Next dispatcher and explicit 27B selection; added executable `scripts/serve_27b.sh` exposing only `--plan`/`--status` (read-only) while GPU start/switch remains blocked. Added 10 CPU regressions, executable-mode checks and CI workflow coverage for both new files. Source CI `67a54afc`: 325/325 PASS. No inference service changes, commits/merges to main or 27B GPU launch.

---

## 2026-11-06 — Operator DGX 27B source PASS and separate blocked launch-preview

Recorded actual exact pinned ModelOpt layer counts FP8 208 + NVFP4 193, and installed image source 4/4 checks true from CPU-only runc. Added `scripts/manager/p2_27b_launch_preview.py` + 12 CPU tests and `--launch-preview` Wizard CLI, returning proposed explicit `modelopt_mixed` vLLM argv and source/API fingerprints. This is not approval/execution, includes immutable pinned revision, prohibits Flash-Next PLE/MTP inheritance, and keeps transition/rollback/GPU gates closed. CI `ae4490d6` 315/315 PASS. No DGX GPU or inference service mutation performed.

---

## 2026-11-06 — Immutable NVIDIA ModelOpt mixed precision audit in P2 runtime preflight

Added `scripts/manager/p2_27b_quant_audit.py` + nine CPU regressions. Existing Wizard runtime-preflight now reads bounded exact-pin `hf_quant_config.json`, reports producer/quantization mode/layer counts and blocks unexpected or unparseable mixes while preserving all prior image/host/runtime gates. GitHub source commit `cd63f25`: CI 303/303 PASS; no model, GPU, Docker service, download or cache mutations performed.

---

## 2026-11-06 — Audit installed vLLM 0.32 image source using CPU-only runc

Based on the new DGX preflight result, authored `scripts/manager/p2_27b_image_audit.py`, `scripts/temporary/p2-27b-image-audit.sh` and 8 CPU regressions to audit the exact local image's registered Qwen3.5 model class and ModelOpt NVFP4/FP8 source without importing vLLM/CUDA. The wrapper defaults to plan-only and requires an explicit CPU-only run flag; image ID pinned and Docker isolated with runc, no GPU or network. SOURCE commit `acf5d64` CI 294/294 PASS. Actual operator CPU-only image probe, GPU/27B service/bench and rollback NOT_RUN.

---

## 2026-11-06 — P2 download completion evidence and guarded runtime preflight

Reconciled operator's actual NVIDIA 27B 19/19 exit-0 download with stale handoff. Added read-only `p2_27b_qualification.py` for pinned source/config, host ARM64, Docker image/platform/label and current service observation, plus `model 27b status --inspect-runtime` command and isolated CPU regressions. Kept the candidate recipe intentionally invalid, GPU start/switch blocked, and Flash-Next service unchanged. NVIDIA 27B `SOURCE_FILES_PRESENT_PINNED_CANDIDATE` does not establish loader, GPU/API, benchmark, or rollback qualification. CI needs validation at new HEAD.

---## 2026-11-06 — Complete P1–P7 Wizard console and lifecycle source (D-021)

Added `wizard/console.py` (three primary screens, model Continue/all actions, full service and advanced P3/P4/P6/P7 plans), `wizard/workflow.py` (P1/P2/P5 action slots for inspect/download/prepare/start/wait/verify/benchmark/switch/rollback/recipe), `wizard/roadmap.py` (all seven release gates), and `scripts/manager/service_logs.py` (bounded opt-in read-only service logs). Wired CLI `workflow` and `roadmap`, extended service `logs` route and CPU CI tests; preserved original P1 guarded engine and P2 approved downloader. Corrected P1 shortcut routing so another active GPU model or unknown service observation cannot enter P1 guided startup. All new P2–P7 mutation adapters remain blocked until runtime/recovery qualification. No DGX operations performed.

## 2026-11-05 — Read-only local API health and stop-before-start/rollback preview

Added `scripts/manager/service_health.py` (fixed loopback :8000 GET /health and /v1/models, bounded response and timeout, served-ID match) and `scripts/manager/service_transition_preview.py` (fail-closed atomic handover preview and explicit recovery). Wired health into existing service CLI and simple root Service choice; attached transition preview to model selection when other model observed. Extended CPU unit tests and CI. No actual service/DGX/API/GPU calls in this development session. Download is user-owned and in progress per last evidence; not verified complete.

## 2026-11-05 — Model-first Wizard UI and read-only automatic lifecycle planner (D-020)

Created `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`; changed `wizard/main.py` TTY root to 3 choices and introduced machine `select MODEL --json` / `model choose MODEL --json`. Added `wizard/quickstart.py`: safe consolidated download/monitor/P1-guided/switch-blocked plans from actual service + pinned checkpoint observations. Updated live `service_manifest.py` to classify in-flight `qwen38-27b-dl` without triggering new downloads; added unqualified Orcarouter service policy entry. Preserved old stage CLI and Flash-Next P1 backend. Added new CPU regression suite and refreshed canonical docs/CI/DECISIONS. User-owned NVIDIA 27B download started; receipt and runtime **not verified**. No service/API/GPU or DGX worktree actions performed in this coding session.

## 2026-11-05 — Fix P2 guided download falsely expiring under its own lock

After a user entered the correct plan ID, the second preflight rejected the request because raw inode counts, floor free GiB and Docker uptime were hashed. Created `_approval_facts` containing stable model/revision/cache/image/host running-state/port occupancy plus time window. Retained all live minimum-disk, inode, transfer and Docker checks on revalidation. Added mock CPU tests reproducing the change while state lock is created and guarding safety-relevant image/state drift. No DGX download or service mutation was performed by this change.

## 2026-11-05 — P2 pinned NVIDIA downloader and single active model manifest foundations

Operator confirmed one active GPU model per DGX Spark, both NVIDIA Flash-Next and 27B on host port 8000. Added `runtimes/service-policy.json`, `service_manifest.py`, `service_journal.py`; service menu read-only inventory uses actual Docker/socket. Added exact-revision `p2_27b_download.py` Wizard download plans with live revalidation/lock/approval and bounded evidence, no GPU/port/service effects. Added interactive `download --guided`, CPU regressions and pinned snapshot recognition without refs/main. Source and CI separate from actual DGX download/GPU/switch. No service interrupted.

## 2026-11-05 — Service management UI and NVIDIA 27B download planning

Added independent `service manager` Wizard menu/CLI (source-only) while retaining `operations system` for P7. Added `download` action to NVIDIA 27B planning, default BLOCKED. CPU router tests cover menu/catalog and refusal of unapproved mutation. Documented NVIDIA DGX `NO_PINNED_LOCAL_SNAPSHOT`; no download, restart, Docker/GPU work run.

## 2026-11-05 — P2 model choice changed to NVIDIA

Operator selected `nvidia/Qwen3.8-27B-NVFP4` instead of RadixArk. Switched read-only Wizard cache inventory, fixture cache path, invalid candidate recipe and current documentation. Preserved RadixArk 3/3-shard DGX result as historical evidence; NVIDIA local presence and DGX/GPU acceptance NOT_RUN. No runtime mutation or download.

## 2026-11-05 — P2 bounded config metadata audit

Added read-only `config.json` model facts (architecture, model type, quantization, context, vision marker) to 27B Wizard inventory. Source inspection remains unqualified for vLLM 0.32 and never authorizes runtime mutations; malformed and >1MiB config are explicitly not source-ready. Added CPU fixtures. GitHub CI results must be recorded separately; no DGX command executed in this session.

# Handoff changelog (append-only)

## 2026-11-05 — H-018 — Observed P1 GPU PASS; begin P2 source-only read inventory

**Actual operator report (2026-11-05 KST)**: `/home/inlc/blazux-p1-reports/20261105T113110Z-fdc179fa/result.json` (operator terminal attachment) returns `api_model_ids=["qwen3.8-flash-next"]`, NVIDIA revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, `source_complete=true`, `hybrid_ready=true`, `source_issues=[]`, `hybrid_issues=[]`, and 11/11 source/Hybrid indexed shards present/resolvable. Wizard `verify=PASS`, `baseline_status=PASS`, `extended_status=PASS`; `default_completion`, `chat`, `tools`, and `vision` each PASS. Wizard `benchmark=PASS`, both action return codes 0. Verify evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113119Z-eca4ec724ede.json`; benchmark evidence: `/home/inlc/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`. **No actual latency / TTFT / tokens-per-second values were supplied**, so benchmark quality thresholds are NOT VERIFIED. `doctor=3` and `inventory_plan=3` remain open as operation checks; active `:8000` listener is observed, but their exact rejection reasons were not supplied. This confirms only current live P1 **functional probes and bounded benchmark**; full Wizard install/start lifecycle is not separately demonstrated.

**P2 27B source-only next step**: The existing candidate `recipes/qwen38-27b.candidate.yaml` names `RadixArk/Qwen3.8-27B-NVFP4` but deliberately fails recipe validation because immutable model revision, vLLM-0.32 architecture/loader qualification and image digest are not pinned. Public model listing confirms that repository exists and contains indexed safetensors (not an assertion that it runs on this DGX). Added `scripts/manager/p2_27b_inventory.py` and `./wizard.sh model 27b status --inspect-cache --json`: purely read-only local HF cache refs/index/shard/quantization summary, never downloads or inspects live Docker/GPU, never authorizes a model start. P2 runtime remains `NOT_RUN`/adapter `INTERFACE_ONLY`. The operator can run a **single Wizard status command** to tell whether 27B is locally present, before pinning recipe and planning disk/model changes. GPU testing granted for non-disruptive P1 did not authorize P2 model replacement or live service interruption.

- Distinguish high-level benchmark PASS from performance metric thresholds; operational doctor/inventory-plan exits remain 3, no P1 service lifecycle exit asserted. P2 candidate remains invalid/unpinned, operations blocked. No DGX action by assistant.


## 2026-11-05 — H-017 — Default Blazux baseline separated from optional Wizard probes

**Latest operator DGX result (2026-11-05):** `/home/inlc/blazux-p1-reports/20261105T103738Z-c4eb4031/result.json` summary from `--auto-gpu` at `805f8e3e`: source checkpoint and Hybrid are both READY, `source_issues=[]`, `hybrid_issues=[]`, 11 indexed source and Hybrid shards resolved, `api_model_ids=["qwen3.8-flash-next"]`, verify and benchmark plans each READY, yet **verify action returned FAIL** and benchmark BLOCKED by verification gate. Original console suppressed the Wizard's failure evidence location because it parsed the JSON outcome only on returncode 0, even though Wizard writes evidence for returncode 2. This is an actual attempted API/GPU verification with FAIL outcome, not evidence of a broken default Blazux model. Exact failing subprobe/error still unconfirmed until raw report is examined.

**Correct architecture:** Wizard must not substitute a new collection of optional assumptions for the default Blazux execution criterion. The original Blazux smoke `scripts/smoke-test.sh` exercises basic `/v1/completions` coherence and standard chat (with `/no_think`), plus other measurements. Previous Wizard `verify_api` instead required chat text within 48 tokens, a `tool_choice=required` response and a tiny synthetic vision input in one all-or-nothing call. Any one failed the entire P1 verify and hid the precise failure. That is a Wizard test-design/diagnostic flaw; it is NOT proven to be the particular observed failure cause. New source commit `391a2844f4c8549e282eae3e266806c89801ad1a` checks a Blazux-shaped ordinary completions baseline and standard chat separately, with up to 256 tokens and `/no_think`, while optional tool/vision probes return independent statuses. Baseline PASS+extensions FAIL ⇒ verify PARTIAL, but a bounded benchmark is still allowed and P1 full acceptance remains PARTIAL. Baseline FAIL ⇒ benchmark BLOCKED. Nonzero Wizard returncode no longer loses evidence/path/status. Bounded benchmark prompts now include `/no_think` to avoid reasoning-only 64-token output.

**SOURCE/CI validation (not DGX):** `391a2844f4c8549e282eae3e266806c89801ad1a`, GitHub push and PR checks 2/2 SUCCESS, each 15 manifest + 10 inventory + 13 launcher + 1 mode + 102 P1 + 32 router = **173/173 CPU tests PASS**. Real DGX execution against this fix has NOT_RUN; prior verify FAIL remains unresolved until this new code runs.


## 2026-11-05 — H-016 — Preserve default Blazux shared-metadata layout and preauthorize bounded P1 GPU tests

- Operator's latest actual DGX report showed expected API model ID `qwen3.8-flash-next`; original index/tokenizer and Hybrid tokenizer are symlinks resolving to existing files **outside** the model repo. 31,907,813-byte Hybrid index and `.prepared` exist, incomplete blob count=0. Older P1 checker falsely treated these metadata links as missing. This is a P1 source compatibility defect; no evidence that the full checkpoint needs re-downloading.
- New asset verifier accepts only nonempty **metadata** symlinks (`model.safetensors.index.json`, `tokenizer.json`) across the model-repo boundary; weight shards remain root-pinned, JSON index still parsed with 64MiB cap. Source/Hybrid symlink, dangling link and escaped shard regression fixtures added. Diagnostic records compatibility flag and target size without copying model files.
- User explicitly authorized GPU compute for non-disruptive P1 testing without per-action typed consent. Added `--auto-gpu` to the existing temporary wrapper. It checks expected served ID and health, takes current verify and benchmark hash IDs, invokes the original Wizard's same second-preflight protection, and never touches lifecycle/cache. P1 verify must PASS before bounded bench.
- This is source-only implementation; do not claim actual P1 GPU PASS until new DGX operator evidence. D-017, R1E added to permanent rules; P2–P7 and destructive actions remain separately blocked.
- **CI/source confirmation:** commit `0063b0e004902408f980c155076c098d49d4569e`, [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978150843/job/127081754127) and [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41978155433/job/127081768853), both **SUCCESS**. Each job ran 15 + 10 + 13 + 1 + 84 + 32 = **155/155 CPU tests PASS**. No actual DGX GPU/API/benchmark result has been observed for the fixed Wizard yet.


## 2026-11-05 — H-015 — P1 metadata audit bug corrected and file-level diagnosis added

- Blazux default NVIDIA checkpoint remains supported. NVIDIA Hugging Face `fc694b5` index is 31.3 MB; our P1 Python audit invented a 16 MiB JSON size ceiling, causing a false rejection for *otherwise valid indexes*. Changed to a bounded 64 MiB cap; added realistic >16MiB and still-over-limit regression tests. This is our new code defect, not an upstream Blazux limitation.
- The actual DGX `source_issues=[model.safetensors.index.json, tokenizer.json]` are from the **earlier `_good_file` predicate** and therefore do not prove that this size gate caused the user's failure. New read-only diagnostics now identify file absent/dangling symlink/empty/outside repo, size, source vs Hybrid, and report parsed API model IDs.
- `66c6c448c1922f958886fa4696c403a4b6227685` source commit CI 2/2 **SUCCESS**, 145/145 CPU tests per job. No GPU/bench re-run, download/repair or service change by assistant; real DGX file evidence still required.


## 2026-11-05 — H-014 — Download completed (operator report), P1 audit disagreement

- Operator confirms NVIDIA Flash-Next download finished. First actual DGX wrapper run on branch `dea7c5a`: Git clean, process scan no active setup, `/health` and `/v1/models` exit code 0; Doctor/inventory plan exit 3; Wizard verify/bench both BLOCKED on generic checkpoint incomplete and Hybrid unready. No Wizard GPU/benchmark calls made.
- Root cause **unknown**: P1 audit currently reads `refs/main` only, whereas `./flash` accepts `refs/master` or an alternate snapshot; it also treats any remaining `.incomplete` blob as blocking even when indexed files are present. A full copy of the raw report has not been supplied; do not assert either explanation as proven.
- Added read-only `scripts/temporary/p1_cache_diagnosis.py`, wired into the one-command wrapper, plus CPU fixtures. First CI run failed due an optional diagnostic missing in the pre-existing report fixture; follow-up makes the field optional and adds tests. GitHub CI fix commit `4c0041dd230e2abe22ba8379aca74068933ecece` 2/2 SUCCESS, 138/138 CPU PASS per job. No DGX changes executed by assistant.


## 2026-11-05 — H-013 — Temporary operator bundle safety and final CPU CI

- Fix commit `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b` checks an operator-owned setup/serve process again just before test execution, blocks report output under HF cache, adds two CPU regressions, and removes duplicated CI invocation (temporary test suite is included under `test_p1_*_cpu.py`).
- GitHub Actions **2/2 SUCCESS**, each with 15 manifest + 10 inventory + 13 Flash launch + 1 executable-mode + 60 P1 (41 earlier and 19 temporary) + 32 Wizard router = **131/131 unique CPU tests PASS**. [Push](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970955588/job/127058833280), [PR](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41970960007/job/127058848658).
- This is SOURCE/CI evidence, not a DGX runtime observation. Download, model service, GPU benchmarks and existing user processes were untouched by the assistant.

## 2026-11-05 — H-012 — Git-first temporary operator script rule and first P1 bundle

- User requested grouping post-download steps 1–3 into one script, committed in GitHub so the DGX operator only needs a Git Pull and single script invocation, with a separate temporary scripts directory. Follow-up explicitly requested that this **become a permanent documented project rule**.
- Added D-016 and OPERATING-RULES R1D: use `scripts/temporary/` for scoped tested throwaway wrappers; source commit + CPU checks → operator's own `git pull --ff-only` after preexisting processes finish → one wrapper for inspect → individually approved Wizard verify/bench → structured evidence. No implicit setup/download/stop/start/cleanup, no logs in Git/HF cache, no secret upload, no self-removal.
- Staged `scripts/temporary/p1-post-download.sh`, `p1_post_download.py`, README and mocked `tests/test_p1_temporary_cpu.py`; CI workflow and executable-bit test extended. **Runtime DGX operations NOT_RUN** in this GitHub-only session; result/CI to be verified at exact new HEAD.


## 2026-11-05 — H-011 — Rename numbered Wizard stages into capability groups

- User clarified that model P1/P2/P5 belong to one **Model management** menu with descriptive model submodules; P3/P6 belong to one **Model switching** menu with transition submodules; P4 storage and P7 operations are separate domains.
- Source commit `571e1c204d76bcb66b9e02cb1315ac775013a130`: move `wizard/menus/p1.py`–`p7.py` to `models/flash_next.py`, `models/qwen_27b.py`, `models/orcarouter_flash_next.py`, `switching/flash_next_27b.py`, `switching/orcarouter_27b.py`, `storage/flash_next_cleanup.py`, `operations/system.py`; update grouped two-level menu, CLI router, flat compatibility alias registry, 32 router CPU tests.
- **CI 2/2 SUCCESS**, 112/112 CPU tests per job; historical P1–P7 CLI flags and `wizard/p1.sh` remain compatible. No assistant DGX Docker, GPU, checkpoint/download, model switching or cleanup operation. Source-only P2–P7 still blocked.
- Active docs updated; D-015 supersedes D-014 numbered filename architecture, while original roadmap order P1→P7 remains unchanged.


## 2026-11-05 — H-010 — P1 JSON-mode hardening and final CPU CI

- Follow-up commit `43f5131b63b7e3f20cde0c409b3ddd672ddb349b` hardened P1: no guided prompt in `--json` mode, verified guided default for TTY, added two router regression tests, committed modular CLI contract/handoff.
- GitHub Actions push and PR `manifest` jobs both **SUCCESS**; per job 15 manifest + 10 inventory + 13 Flash launcher + 1 script mode + 41 P1 + 23 Wizard router = **103/103 CPU PASS**. [push job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961837000/job/127029761586); [PR job](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/41961842431/job/127029780582).
- No actual DGX Wizard GPU/API/benchmark operations, model switching, cleanup or gateway changes occurred. P2–P7 menu skeleton SOURCE_ONLY and execution BLOCKED. Original user download/setup/serve chain not interrupted.



## 2026-11-05 — H-009 — Build P1–P7 Wizard menu/router before operational phases

- User requests complete up-front Wizard **architecture** and per-stage/menu source modules rather than one monolithic file; direct CLI/JSON automation in addition to guided menu for user-mediated DGX operations.
- Added root executable `wizard.sh`, `wizard/main.py`, `wizard/menus/{common,p1,p2,p3,p4,p5,p6,p7}.py`; existing `wizard/p1.sh` retained as compatibility shim. P1 reuses existing guarded source workflow, P2–P7 status/plan interfaces explicitly `BLOCKED` for execution pending pinned recipes/source/runtime/rollback acceptance.
- First source commit `de784feeff0f92f36dcc359ce77167ebcdfc5bbe`, two GitHub Actions SUCCESS, **101 CPU tests per job** (21 new routing tests and 80 previous).
- Follow-up source hardens P1 JSON mode and adds two regression tests; verify final branch CI before release claim.
- No DGX Docker/GPU/service interaction, model download or deletion by assistant. User-supplied previous download/queued setup chain preserved. Actual P1–P7 runtime acceptance remains incomplete.


## 2026-11-05 — H-008 — P1 Wizard code batch and operator build/download evidence

- Operator-provided DGX log: Docker image `qwen38-flash-dgx:v0.32` built (image ID `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`), port :8000 free at earlier read-only scan, model download 9/25 = 36% in last visible line. OpenWebUI/Portainer kept running. Shell has queued `serve/wait/test` after `./flash setup default`.
- Added `scripts/manager/p1_assets.py` (read-only shard/index/cache/image integrity), `p1_wizard.py` (guarded actions, approval plan hashes, API smoke, immutable JSON evidence), `p1_bench.py` (bounded streaming TTFT/latency/tokens), `wizard/p1.sh` (guided and noninteractive), isolated mock CPU tests and GitHub Actions coverage.
- First source commit `c625a49276272e90d19ab6367f580a0230754890` applied; two GitHub Actions runs SUCCESS with 80/80 CPU tests each (41 new P1 + 39 baseline). No assistant-executed Docker, HF cache, GPU or API action. P1 runtime remains `NOT_RUN`. Do not start a duplicate download or interfere with existing operator setup.


## 2026-11-05 — H-007 — User reports NVIDIA Flash-Next checkpoint download in progress

- At 11:46 KST user reports `nvidia/Qwen3.8-Flash-Next-NVFP4` download is **still running**. This is USER_REPORTED, not independently inspected on DGX. Completion percentage, cache path, revision and storage remaining unknown.
- Recorded `DOWNLOAD_IN_PROGRESS` in CURRENT-STATE, priority guard in NEXT-ACTIONS and E-20261105-04 in evidence ledger. `DOWNLOAD_COMPLETE`, `HYBRID_READY`, GPU, API and benchmarks remain **NOT_VERIFIED / NOT_RUN**.
- Do not launch a competing download, `./flash setup default` or hybrid preparation while it may modify active weights/cache. P1 Wizard code and synthetic CPU tests can proceed while assets download.
- GitHub documentation change only: no Docker, image, download, cache or GPU operations performed by this session.

## 2026-11-05 — H-006 — Confirm all P1–P7 stages must be Wizard-driven

- User explicitly confirmed exact sequential target: Wizard Flash-Next install/run/bench → Wizard 27B install/run/bench → Wizard Flash-Next ↔ 27B switching → optional approved Flash-Next cleanup if storage insufficient → Wizard Orcarouter-Flash-Next install/run/bench → Wizard Orcarouter ↔ 27B switching → integrated Wizard operations release.
- Clarified `P4=SKIPPED_NOT_NEEDED` when disk allows; no automatic deletion. External port :8000 is the desired stable API entrypoint; actual DGX occupancy and activation remain NOT_OBSERVED.
- Promoted the sequence into `handoff/README.md`, `OPERATING-RULES.md`, `NEXT-ACTIONS.md`, `CURRENT-STATE.md`, `DECISIONS.md`, `SESSION-START-PROMPT.md` and master plan. First unfinished implementation remains **P1 Wizard end-to-end**, not merely manual `flash serve`.
- Documentation-only GitHub commit; no DGX, GPU, Docker operations, benchmark, deletion or model switch. Previously verified code HEAD `017319a`: 39/39 CPU tests in each of two successful GitHub Actions runs; recheck new commit checks separately.

## 2026-11-05 — H-005 — Restore executable bits and record CI failure

- Commit `7e8f4a109a04c130a5dba0d73e3ece0881d85478` had a real **CI FAIL**: manifest 15/15 PASS; inventory 10/10 PASS; shell launcher 9/13 PASS and 4/13 FAIL, exit 126 because `flash`/`scripts/serve.sh` lost executable permissions in GitHub tree update.
- Restored executable mode `100755` for both scripts; added a CPU regression test asserting launch scripts are executable and `bash -n` workflow checks. Rerun CI on new HEAD; preserve failed evidence instead of rewriting.
- No DGX, Docker runtime, GPU, API port or model state changed.

## 2026-11-05 — H-004 — Flash-Next on legacy :8000 and source-safe inventory

- User reports previous operating services deleted; current Docker/ports/images/weights on DGX **NOT OBSERVED**. Do not treat past Orcarouter container or model ID as current deployment state.
- Updated `flash`, `profiles/default.env`, `scripts/serve.sh` so NVIDIA Flash-Next default profile exposes host port 8000 and served name `qwen3.8-flash-next`. The upstream profile continues Hybrid+YaRN+MTP2; no SGLang.
- Replaced implicit `docker rm -f "$NAME"` with refusal to replace any existing exact Docker container name. No automatic removal on failed launch.
- Removed historical hard-coded 8000/name manifest bans. Added `scripts/manager/inventory.py` (read-only Docker/ss/disk/cache/mount reconciliation), Wizard `00-doctor.sh`/`10-plan.sh` wrappers, deterministic synthetic CPU tests, CI workflow coverage.
- This commit is SOURCE-only; tests CI verification to follow actual commit. No DGX GPU, cache mutations, download, Docker actions or API benchmark. Updated rules, decisions, contracts and runbook.

## 2026-11-04 — H-003 — N1 source-only manifest validation

- Added YAML recipe JSON Schema Draft 2020-12, CPU-only validator, pinned SHA/digest constraints, historical protected name/port denial, no approval bypass.
- Added deliberately invalid 27B candidate, synthetic fixture, 15 isolated CPU tests and new GitHub Actions CPU workflow. No Docker, GPU, actual DGX or model/cache/port changes.
- Ran: python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -q -> **15/15 PASS**; 27B candidate -> expected FAIL (exit 2); synthetic fixture -> schema PASS (exit 0) with launch_authorized=false.
- Updated CURRENT-STATE, NEXT-ACTIONS, EVIDENCE-LEDGER, DECISIONS and planning contracts. Draft PR #1 still requires CI readback and review; N2 and all operational testing remain outstanding.

## 2026-11-04 — H-002 — Documentation committed and draft PR opened

- Verified the new planning branch was 1 commit ahead of `main`, 10 tracked doc files, all under `docs/` and `handoff/`.
- Commit `76cd8dae16b0f34e47c353b56b6e9dbcc5fcde25` created the initial document set.
- Opened [Draft PR #1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1); no merge. At original commit check, GitHub showed 0 check-runs/0 PR workflow runs; **not CI PASS**.
- Corrected illustrative 27B recipe to keep PLE semantics `UNVERIFIED_FOR_27B` rather than assuming no PLE; still no runtime/CPU tests.
- Updated live handoff state, next actions and evidence. All work was GitHub-only.

## 2026-11-04 — H-001 — Recipe/Wizard migration planning initialized

- Confirmed user preference: **vLLM 0.32 only**, no SGLang, one large target at a time by default.
- Created planning branch `feature/recipe-wizard-handoff` from fork `main@b0aa8b77604139557169387b2fa8386355d8b651`.
- Preserved parallel `feature/orcarouter-bf16-adapter` design branch.
- Defined P0→P7 roadmap, manifest separation, wizard steps, protected runtime boundaries, gated checkpoint deletion and switch/rollback semantics.
- Added a standard entrypoint, living current state, evidence ledger, decisions, next tasks and new-conversation prompt under `handoff/`.
- **Tests:** documentation/source review only. No new CPU/CI/GPU/benchmark runs; no Docker, HF weights, model or service changes.
- PR/CI state should be read from GitHub; do not infer a merge.

## Future entry template

`YYYY-MM-DD — H-NNN — Subject`: exact changes, files, branch/commit, PR, test outcomes, external effects, remaining blockers. Newer entries should be placed **above** older entries while preserving them.
