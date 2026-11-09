## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-09 10:15 KST (P5–P8 model-agnostic update)

**Latest source CI verified:** code+workflow HEAD `29c28e4750adabbd421dcda64a432127d3f45659`, GitHub Push run [42553107135](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42553107135) and PR run [42553114059](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42553114059) both **SUCCESS**. Newly added CPU checks explicitly included: P5 session 8, P6/P8 extended transition 8, P7 reconciliation 6, Wizard TTY 1 = **23 added tests PASS**. Original 24 synthetic cases preserved, 66 extended synthetic cases PASS as expected. **CI does not validate real Docker/GPU/inference/recovery**. Subsequent documentation-only commits may advance branch HEAD; always query the live branch/PR on restart.

**Current P5 trial:** adapter `qwen4exp-qsa62318-lmhead-v032-v3` resolved `lm_head.weight_scale`. Orcarouter v3 remains DEVELOPMENT_TRIAL, not production. The newer 10:15 KST operator-provided *idle-only* telemetry and P5–P8 source-only implementation/acceptance supersession immediately below do not authorize any actual DGX service change.

[Model-independent P5–P8 source/acceptance contract](../docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md) · [Full document audit](../docs/HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md)

---

### 2026-11-10 P5-C + P6-D source-only observation / operating gate

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


## 2026-11-08 — P5 real DGX one-shot MTP0 trial (no restore)

Operator permitted stopping development 27B and specifically waived automatic 27B restoration if Orcarouter fails. Newly implemented `./wizard.sh p5 trial prepare|plan|execute|status` with built, isolated Blazux vLLM 0.32 candidate, BF16 PLE mmap, immutable base image/source pins, :8000 and one active GPU model, explicit exact plan approval `I_ACCEPT_P5_NO_ROLLBACK`, preserved HF caches/images/old stopped container and private evidence. Execution re-checks actual 27B served ID, source/candidate image digests, :8000 release and NVIDIA compute process inventory. The default production service transition rollback remains unchanged. MTP2, Native Tools and benchmark still require separate GPU qualification.

**Real DGX P5 not yet executed by this GitHub session.** User's latest DGX log: new PLE schema+manifests PASS, Orcarouter PLE BF16 metadata PASS, donor 31 BF16 SHA PASS, 57 CPU tests PASS; 27B still serving. The new GPU trial code first had 67 P5 CI CPU tests PASS; the latest extra source/image/GPU guard CI must be checked after commit. Runbook: `docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md`. No auto restoration, source deletion, P3 replay, P4 prune, P6 switch, P8 faults, or PR merge.

---

## P5 follow-up 2026-11-08: PLE schema v2 and cross-engine reference discipline

The operator allows development DGX service downtime and GPU experiments. Shared Wizard `runtimes/ple-assets.json` now schema v2 (model-specific dtype/scale/placement; Orcarouter pinned BF16 unchanged), `runtimes/ple-loader-profiles.json` is in the common registry as seventh manifest, and `scripts/manager/ple_format.py` plus transition preview require independent source mapping/GPU release and rollback during switches. External DGX references dolf3131 (pinned 45e3d477) and NVIDIA October FP4-Local forum provide **research only**; no alternative container/image adopted, and Blazux vLLM0.32 remains mandatory.

[Source commit d395368](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d395368645b04ebc4d2367f33314ea07fb68ff1b) / [CI #42436269922 SUCCESS](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42436269922). GPU P5 remains NOT_RUN; this GitHub session did not stop 27B despite downtime permission. Exact new docs `docs/P5-PLE-FORMAT-AND-DGX-SPARK-REFERENCE-ADOPTION-20261108.md`; check current HEAD/PR/CI. Read-only DGX validation is next; no deletion, unapproved GPU executor, P3 replay or Draft PR merge.

---

## 2026-11-08 — Wizard shared manifest registry / Orcarouter BF16 PLE asset (READ-ONLY)

Implemented `runtimes/manifest-registry.json` and shared `scripts/manager/manifest_registry.py`: schema-1 strict bounded JSON, duplicate/nonfinite/symlink rejection, cross-checks for service-policy, model-discovery, canonical 27B recipe, unqualified Orcarouter recipe, pinned YSLAB compatibility and new `runtimes/ple-assets.json` PLE asset. PLE ID `orcarouter-bf16-ple` is referenced consistently in P5 recipe, service policy, model discovery. Common `scripts/manager/ple_assets.py` validates pinned 128 BF16 table headers, 320001536 rows and width160; its metadata PASS is **not** mmap/GPU PASS.

Wizard `manifest status|validate --json`, `model list --installed --json`, `p5 status/doctor --json`, `service manager status --json` and model-first selector expose manifest/PLE registration and independent observed state. No hidden asset movement, image build, start/stop, deletion or model switch. Initial code commit [a17b3618](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/a17b3618fab98aa5b849359d464c0d7698fae4a0) passed [CI #42433160630](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42433160630): 996 executed CPU test cases across 44 invocations (duplicates included). Follow-up model-selector/docs requires CI separately.

2026-11-08 operator-provided DGX `8f8ad0c` evidence: 27B `LIVE_SERVICE_VERIFIED` at :8000, Orcarouter PLE 128 BF16 tensors PASS, MTP donor 31 tensors and three pinned SHA256 PASS; the **new registry code was not run on DGX**. Actual Orcarouter runtime/MTP2/API/benchmark/restore NOT_RUN, release false. Preserve 27B, all HF caches and receipts, :8000/ONE_ACTIVE_MODEL_ONLY, OpenWebUI/Portainer. No P3 replay, P4 deletion, P6 transition, P8 fault/recovery or Draft PR merge. Architecture and commands: `docs/WIZARD-MANIFEST-REGISTRY-AND-PLE-ASSETS-20261108.md`.

---

## 2026-11-08 — P5 vLLM 0.32 source patch candidate; image not built

Verified the official `vllm-project/vllm@v0.32.0` Qwen4Exp `model.py` and `mtp.py` static anchors (one occurrence each). v0.32 `CompressedTensorsConfig.ignore` is separate from `ignored_layers` and `exclude_modules`, requiring a scoped remap for donor MTP BF16 bypass.

`src/p5_patch_qwen4exp_v032.py` is the **P5-only optional source patch** for quantized LM head, compressed-tensors ignore remap, and strict 31/31 native BF16 MTP name/dtype guard. Other models are unaffected when `VLLM_P5_ORCAROUTER` is unset. The source candidate requires exactly installed vLLM 0.32.0 and fail-closed anchor matching. `Dockerfile.p5.candidate` has no fixed base; its required `P5_QUALIFIED_BASE_IMAGE` must be provided only after independently verified Blazux v0.32 image pin and explicit image-build permission. `P5_EXPLICIT_IMAGE_BUILD=1` permits source patching *inside that isolated candidate image build only*; **no image has been built or loaded**. `tests/test_p5_vllm032_patch_cpu.py` validates pure-source patch behavior without Docker/GPU. Actual ARM64 ABI, GPU model load, MTP0/MTP2 API, OpenWebUI and benchmark remain **NOT_RUN**.

This is not permission to run `docker build`, generate a multi-GB BF16 MTP overlay, interrupt the active 27B on :8000 or merge Draft PR #1. Existing standalone source-only one-shot `--gpu-trial` stays BLOCKED. Await final CI for this addition before reporting test PASS.

---

## 2026-11-08 — P5 SOURCE implementation and CPU/Fake-DGX acceptance

The P5 source batch was committed as [33adec1](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/33adec182e97a8eac0d5584bdf73f1448bdd84f2); [GitHub Actions 42429745463](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42429745463) **SUCCESS**, including 20/20 P5 CPU tests and integrated one-shot `--cpu-only --json` PASS. It implements the pinned P5 candidate recipe, imported licensed YSLAB metadata/immutable-overlay source tools, direct BF16 PLE and three-donor/31 BF16 MTP audits, separate MTP0/MTP2 candidate profiles, Wizard stage and safety gates, `scripts/temporary/p5-one-shot-acceptance.sh`. A subsequent source enhancement adds detailed per-case CPU JSON and profile preview and must pass its own CI.

**Not runtime-qualified:** actual Blazux vLLM 0.32 CUDA/quantized-lm-head/compressed-tensors/MTP loader ABI, on-DGX PLE and donor audits, overlay generation, GPU model loading, native Tools, streaming, benchmarks, strict numerical parity and 27B restoration are **NOT_RUN**. Vendor overlay *code* included but no CLI execution/asset write approved. The recipe has `launch_allowed=false`, `register_as_runtime_recipe=false`, unknown runtime image ID. `--gpu-trial` always BLOCKED, no execution approval generated. Preserve existing 27B at :8000, single-model service, HF caches, other images, WebUI, Portainer; do not replay P3, delete P4 assets, start P6/P8 or merge Draft PR #1. Actual DGX is not connected to this session. Read-only runbook: `docs/P5-SOURCE-ACCEPTANCE-AND-DGX-READONLY-RUNBOOK-20261108.md`.

---

## 2026-11-08 — Current start: P5 Orcarouter BF16PLE + vLLM 0.32

For the **next conversation**, copy `handoff/START-NEXT-P5-20261108.md`. Source/acceptance contract: `docs/P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md`; document presence/compatibility audit: `docs/HANDOFF-DOCUMENT-AUDIT-P5-20261108.md`. These supersede older P4-A starter instructions for the **next phase**. P4-A/B/C real read-only PASS/CLOSED, actual deletion unapproved; P5 not yet implemented or real-trialed, P6 and P8 not run. This handoff only prepared docs. Existing HEAD/CI/PR should be re-fetched at new conversation start.

---

## 2026-11-08 — Current P4-B/C one-shot actual DGX dry-run: PASS / no deletion

Operator-side one-shot report: 13/13 Fake-DGX local PASS, P4-B `READ_ONLY_REVIEW_COMPLETE`, P4-C `DRY_RUN_COMPLETE_RELEASE_GATED`, combined `READ_ONLY_DRY_RUN_PASS`. Nine resource records reviewed, none selected or executed; no approved reclaimable bytes. 2 rehearsal steps PASS, 2 deferred to P5/P8, 1 live adapter NOT_RELEASED, 1 actual delete/postcheck NOT_EXECUTED. The **only** acceptance is real DGX read-only review/rehearsal, not production cleanup. Evidence: `docs/P4-BC-DGX-READONLY-DRY-RUN-EVIDENCE-20261108.md`. Prior P4-A actual inventory PASS remains closed; P5/P8 live work NOT_RUN. PR #1 remains Draft/Open/Unmerged.

---

## 2026-11-08 — P4-B/C combined dry-run source implemented; DGX run next

User directed P4-B asset/candidate review and P4-C cleanup transaction rehearsal in a single read-only script. Source `scripts/manager/p4_bc_dry_run.py`, `scripts/temporary/p4-bc-dry-run.sh`, Wizard `storage flash-next dry-run --json`; 13 Fake-DGX tests. CI [42403828742](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42403828742) SUCCESS, **902/902 CPU/Fake-DGX PASS (41 groups)**. Actual combined DGX run **PENDING**; prior P4-A real inventory PASS remains valid. P4-C live adapter **absent**, `P4_C_LIVE_EXECUTION_RELEASED=False`; no deletion now, only after separately approved P5 issue or P8 acceptance. [Design/runbook](../docs/P4-BC-ONE-SHOT-DRY-RUN-20261108.md). No P3 replay, P8 execution, or PR merge.

---
## 2026-11-08 — P4-A actual DGX capacity inventory: READ_ONLY PASS / COMPLETE

Operator ran `./wizard.sh storage flash-next inventory --json` at checkout `a29cd6e`: `READ_ONLY_INVENTORY_COMPLETE`, `issues=[]`, `active_api_verified=true`, 27B active, stopped Flash preserved, Orcarouter model cache present without a container, one GPU and one port-8000 owner, all four Docker capacity categories. File-system total **982,819,848,192 bytes**, free **324,880,961,536 bytes** (~**33.06% free**); both HF cache roots returned the *same* filesystem total/free, so never add those values. Root allocated bytes **267,995,971,584** and **192,507,006,976**; known model-repository allocated sizes: Flash **75,967,504,384**, 27B **21,932,584,960**, Orcarouter **177,686,446,080**. Docker displayed reclaimable: containers **182.7MB**, build cache **2.088MB**, images/volumes **0B**; **not** verified safe reclaimable bytes. See `docs/P4-A-DGX-READONLY-CAPACITY-EVIDENCE-20261108.md` for bounded source, units, and non-additivity caveats. No deletion or service mutation; **P4-B/C NOT_STARTED/NOT_APPROVED**, **P8 NOT_RUN/NOT_RELEASED**. Do not repeat P3-A/B/C/G.

---

## 2026-11-08 — Current next-session checkpoint: P4-A read-only inventory

Latest current branch audit and new conversation starter:
- `docs/HANDOFF-DOCUMENT-AUDIT-20261108.md` (all 34 required core documents/recipes present; previous dated audits are historical).
- `handoff/START-NEXT-P4A-20261108.md` (current comprehensive copy/paste starter).
P3 E/F source, metadata and CPU handoff complete; P4-A **source implemented**, actual DGX inventory pending; P4-B/C unauthorized; P8 real reinstall/recovery/final operating signoff pending. Latest pre-audit GitHub state: branch `99ee6b8`, 887/887 CPU PASS / 40 groups, PR #1 Draft/Open/Unmerged. Re-fetch after any doc commit.

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

## 2026-11-08 — Latest P3-E/F DGX read-only evidence and source extension

Operator's latest DGX read-only `--sudo-ss` P3-D/E/F/G output: **P3-D READ_ONLY_PASS**, independently attributed docker-proxy IPv4 PID `2560693` and IPv6 PID `2560708`, GPU PID `2560905`, no detected GPU ownership conflict. **P3-E DRAFT_REVIEW_REQUIRED** despite `cmd_normalized=true` using `FLASH_FP8HYBRID_READ_ONLY_V1`, `cmd_normalization_error=null`, draft-field `issues=[]`, because canonical reinstall remains unqualified. **P3-F 153/153 DGX-local CPU PASS**. P3-G preview in this particular runner does not invalidate previously completed real bidirectional G. `blocked_stages=[]` with total `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` is expected.

GitHub source: [03cbe4c](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/03cbe4cc45a750322c4f99616c85f1061f7b2288), [2b44ccc](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/2b44ccc0237fa34742e28608ad089cb3ca90fe55), and [8e8fcec](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/8e8fcec5acb280e01445a2bd773fc9f4ecedf2f6). Source-only CI [42390619936](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42390619936): **870/870 PASS, 39 groups**, including 5 new Flash host asset tests. New read-only `python3 -m scripts.manager.flash_host_assets --json` preflight checks local Flash `-fp8hybrid` index references, metadata/template SHA-256 and existing shard sizes without hashing massive weights or printing secrets. This is **not** a reinstall qualification or launch adapter. See `docs/P3-E-FLASH-HOST-ASSET-PREFLIGHT-20261108.md`. P3-G historical real PASS/CLOSED; P8 recovery/final signoff NOT_RUN.

---

## 2026-11-08 — P3-E/F source safety hardening checkpoint

Source change: [d68106a](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/d68106a24c4c6071acff7a4d98d74e04c6ecbfe1). Actual GitHub Actions [42386939625](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42386939625): **862/862 PASS in 38 CPU/Fake-DGX groups** (856 baseline + 6 new). This is **SOURCE-ONLY**; no fresh DGX test or service change. Full scope: `docs/P3-E-F-SOURCE-HARDENING-20261108.md`.

Continue with **P3-E Flash canonical reinstall qualification** and **P3-F generic lifecycle**. E remains `DRAFT_REVIEW_REQUIRED`; F production execution remains locked. P3 A/B/C/G remain REAL PASS/CLOSED; P8 remains NOT_RUN/NOT_RELEASED. Consult CURRENT-STATE, NEXT-ACTIONS, EVIDENCE-LEDGER and DECISIONS below; old sections are historical, not fresh observations.

---

## 2026-11-07 — P3-A–G EVIDENCE AUDIT / P3-G CLOSED; P8 OWNS FAULT & FINAL RELEASE

**New canonical audit:** `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md` and `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`. Stage results: **P3-A/B/C** original immutable one-off real DGX PASS/CLOSED (A Flash→27B, B 27B→Flash, C Flash→27B); **D** real read-only GPU+IPv4/IPv6 host :8000 PID ownership PASS from operator `--sudo-ss` run (pre-latest switch); **E** Flash source `-fp8hybrid` prepared view and versioned draft-field match, but **canonical Flash reinstall recipe UNQUALIFIED** (`DRAFT_REVIEW_REQUIRED`, `launch_allowed=false`); **F** six Fake-DGX/CPU suites **144/144 local PASS**, but `PRODUCTION_LIFECYCLE_RELEASED=false` and generic live install/reinstall not accepted; **G** actual independent 27B→Flash→27B TTY-approved ordinary two-way transfers **REAL PASS/CLOSED** with two receipts, API identities, final 27B `diff=[]`, journal VERIFIED/COMMITTED 28 events, last actual active `qwen38-27b` on port 8000. **P3-A–G aggregate = PARTIAL (E open, F source only)** despite G closed. The user explicitly moved intentional failure injection, automatic restore and final operational/UX/production signoff to **P8** (NEW, NOT_RUN, not authorized to execute). P7 is integration only. Preserve old receipts, model assets and `ONE_ACTIVE_MODEL_ONLY`; no P3 A/B/C/G replays or fault injection to perform this audit. Latest P8-source registration CI [42384120480](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42384120480) SUCCESS 856/856 CPU tests 38 groups (source evidence only). Basic post-switch service manager `gpu_exclusivity_verified=false` and `port_process_ownership_verified=false` are **NOT PROBED** by that command, not conflicts; do not overclaim fresh D audit. The single-script D–G read-only runner prints G preview even after separate real G PASS by design.

**Authoritative latest stage scope:** `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md` and `docs/P3-A-G-EVIDENCE-AUDIT-20261107.md`. P3-G closed REAL two-way, P3-E Flash canonical reinstall open, P3-F CPU-only PASS. P7 component integration, P8 intentional fault/restore + final operating/UX release pending. Older P1-P7 and G fault/UX descriptions historical.

---

## 2026-11-07 — P3-G FIRST LIVE SWITCH 27B → FLASH-NEXT: REAL PASS

**ACTUAL DGX execution (operator terminal evidence, not CPU/source-only):** Existing one-off `scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` was approved via all FOUR TTY inputs (independent SHA, exact downtime and target acknowledgment). Fresh approval SHA `365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654`; **`Live transition result: PASS`**, observed active `flash-next`; private completed receipt reported at `/home/inlc/.local/state/blazux-wizard/operational-switch/completed-365099fea62bc06bb78006bbf66ef93670cf3ec72d7d50202afe23395c8a3654.json`. Operator postcheck `./wizard.sh service manager status --json`: `LIVE_SERVICE_VERIFIED`, expected/observed model ID `qwen3.8-flash-next`, port 8000, running `qwen38-flash`, 8/8 service checks true, issues=[]. `operational_audit --json`: `VERIFIED/COMMITTED`, `event_count=21`, issues=[]; final event hash `4f54d29d50ee976b123f63c6d8c4c4a96e0a340309566a29133bd4fa70f28b3e`. The status command's `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `previous_trial_provenance_verified=false` mean those extra proofs were NOT assessed by that status route; do not misreport them as actual failed measurements or as new PASS. `manifest_status=OBSERVED_UNQUALIFIED` does NOT qualify Flash canonical reinstall recipe. `operations_enabled=false` remains.

**Acceptance:** P3-G real 27B→Flash **PASS**. **Last observed live active model: flash-next.** P3-G real Flash→27B **NOT_RUN**, deliberate failure/rollback **NOT_RUN**, full P3-G & production switching release **NOT_COMPLETE**. No unapproved model recreation/removal, no P3 A/B/C replay. Full report `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md`. Reverse is a **new, separately approved one-switch TTY execution**; no reuse of prior SHA/automatic chain.

**Handoff current anchor:** Last observed DGX active model is Flash-Next after actual P3-G forward PASS (not merely earlier read-only preview). Reverse Flash→27B NOT_RUN, production release still disabled. See `docs/P3-G-FIRST-LIVE-27B-TO-FLASH-PASS-20261107.md` for evidence and independent reverse-trial plan.

---

## 2026-11-07 — OPERATOR AUTHORIZED P3-G REAL SWITCH DOWNTIME (EXECUTION NOT YET RUN)

The operator shared a third unified real DGX **read-only** batch: P3-D GPU/port PID `READ_ONLY_PASS` (sudo-ss process ownership), P3-E source-draft documented fields `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` with canonical reinstall unqualified, P3-F **144/144 DGX-local CPU tests PASS**, P3-G `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `blocked_stages=[]`, overall `DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED` and `P3_DG_EXIT=0`. The operator then explicitly requested **“P3-G 허용”** followed by **“문서 업데이트 + 서비스 중단 허용.”** Accordingly **P3-G one-off actual DGX 27B→preserved Flash→canonical 27B switching is authorized to INTERRUPT THE ACTIVE API** in the context of two separate *manually approved* operating acceptance trials. No live switch has been executed by this document, and the approval does **not bypass four exact input prompts per transfer** (fresh independent SHA, exact downtime and model acknowledgments, true TTY) nor approve image/container removal/reinstall, forced fault injection, P3-A/B/C replay or production release. Each switch may fail to restore after a host/Docker outage. Do NOT pipe or automate the four approval strings. First run a **read-only fresh plan**, then operator executes **27B→Flash**, validates actual API+Docker+journal evidence, and *only then* separately approves **Flash→27B**. No blind retry on failure. Full authorization and per-step commands: `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`.

**P3-G actual downtime authorized, execution NOT YET observed.** Read `docs/P3-G-LIVE-DOWNTIME-APPROVAL-AND-RUNBOOK-20261107.md`. Existing `scripts/temporary/operational-switch-acceptance.sh` provides one-switch real TTY trial, separate four exact operator acknowledgements and new SHA per direction. No auto-chain; no P3 A/B/C replay, no Flash reinstall or production enable. First trial target flash-next (current model 27B), inspect evidence, then separately target 27b. Evidence currently D read-only pass, E draft-only match, F local 144 PASS, G preview PASS.

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

## 2026-11-07 — CURRENT P3-A-G TRACKING

The user adopted **P3-D/E/F/G** as formal continuation of historical P3-A/B/C (all already passed, no replay). Read `docs/P3-D-G-UNIFIED-WIZARD-DRAFT-ACCEPTANCE-20261107.md` first for each gate and local `bash scripts/temporary/p3-d-g-acceptance.sh --run` automatic CPU + read-only DGX judge. D unknown process visibility is BLOCKED rather than invented PASS; E Flash canonical recipe unqualified until reviewed, F CPU-only does not release executor, G preview does not execute a real switch or rollback. P4 remains optional, then P5/6/7 as before.

---

## 2026-11-07 — LATEST DGX ACTUAL READ-ONLY ACCEPTANCE: CURRENT-ID SWITCH PREVIEW PASS

Read `docs/WIZARD-27B-OPERATIONAL-PREVIEW-DGX-PASS-20261107.md` for the second operator DGX read-only report after pulling 4189a79: canonical 27B `diff=[]`, `advisories=[]`; ordinary 27B -> preserved Flash-Next switch preflight `READY_FOR_OPERATOR_REVIEW_ONLY`, `issues=[]`, current IDs and source/target lineage validated; service `LIVE_SERVICE_VERIFIED`. **This is a PREVIEW PASS only**, not GPU exclusivity or port ownership and not actual model switch/rollback acceptance. Code CI 814/814 PASS. Never treat a preview plan hash as execution approval.

---

## 2026-11-07 — LATEST DGX READ-ONLY evidence and current-ID-aware switch code

Operator's actual DGX post-pull Wizard: 27B `diff=[]`, `issues=[]`, API `LIVE_SERVICE_VERIFIED`, container ID `00094794475a9eaa62296c9e9fcb880bf6f3e01abdb77e3dd3ac5f964d5b2d4a`; cache host `/home/inlc/.cache/huggingface` mounted `/hf:ro`. New source fixes ordinary switch stale P3 Docker ID assumptions, with qualified canonical 27B provenance and explicit optional read-only host cache comparison. CI 42367665200 SUCCESS: 814/814 CPU/Fake-DGX tests (36 groups), no actual DGX mutation. Start with `docs/WIZARD-27B-LIVE-DRIFT-CURRENT-ID-20261107.md`, `handoff/CURRENT-STATE.md` and `handoff/NEXT-ACTIONS.md`. Production release gates unchanged False; historical P2/P3/cleanup real evidence preserved.

---

## 2026-11-07 — LATEST SOURCE-ONLY Wizard lifecycle implementation

New generic 27B recipe drift comparator, read-only Wizard lifecycle CLI and interactive menu option 7, and guarded container-only lifecycle/rollback scaffold were implemented on feature/recipe-wizard-handoff. GitHub Actions CI 42355750124: **799/799 CPU/Fake-DGX PASS (36 groups)**. No DGX service mutation was authorized or performed; production dispatch remains hard-blocked. Read docs/WIZARD-LIFECYCLE-SOURCE-IMPLEMENTATION-20261107.md and newest entries in CURRENT-STATE.md / NEXT-ACTIONS.md for source-vs-real status and remaining blockers. The previously recorded canonical live 27B and P3-C evidence below remains historical, not a fresh live probe.

---

## 2026-11-07 — HANDOFF DOCUMENT AUDIT / NEXT CONVERSATION READY

The user starts the next development phase in a separate conversation. **Audit verified all 8 handoff docs, 12 implementation docs and 5 recipe/manifest/benchmark indices exist (25/25), plus both published benchmark collection directories and current source/evidence files.** The pre-audit HEAD `9ec7420b74369e7a76785577dc543f9dafb8897d` had GitHub Actions run `42352654468` SUCCESS, **757/757 CPU tests in 34 groups**. This CI is source-only. New documentation commits advance HEAD; inspect GitHub afresh.

A new **complete standalone** prompt is in `handoff/START-NEXT-WIZARD-LIFECYCLE-20261107.md` and prominently at the top of `handoff/SESSION-START-PROMPT.md`; older prompts below are ARCHIVED / superseded. Missing-document/staleness audit: `docs/HANDOFF-DOCUMENT-AUDIT-20261107.md`. Next implementation contract: `docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md`.

**Latest actual DGX:** canonical NVIDIA 27B native-tool recipe, 3/3 benchmark v2, Open WebUI Native user-confirmed PASS, two old diagnostic containers removed via verified Wizard manifest cleanup; original `qwen38-27b` runs at :8000 with served `qwen3.8-27b`, Flash container stopped, Open WebUI/Portainer running. P3-C historical PASS/CLOSED, P8 conditional migration ticket INACTIVE. Do not restart the old P2 Tool HTTP-400 diagnosis; it was resolved. Old original 27B Docker container IDs recorded in P3 stage receipts remain HISTORICAL. `PRODUCTION_EXECUTION_RELEASED=False` for main Wizard generic switch; post-ID-change real guided switch/recovery acceptance still open.

**Next target:** general Wizard lifecycle/recipe-diff detection at install/start/restart/switch, scoped container remove/reinstall/recreate with fresh approval, new runtime receipt and rollback. No global deletion prohibition on canonical 27B or Flash. No live DGX mutation is authorized by this documentation step. The canonical `recipes/qwen38-27b.runtime.json` file's exact SHA is tied to current approved benchmark pointer: do NOT silently edit this file to fix text/metadata. Preserve old P3/bench receipts, images/caches, vLLM 0.32, one GPU model, port 8000, Draft PR #1.

---

## SUPERSEDING VERIFIED STATE — 2026-11-07, AFTER DGX REAL ACCEPTANCE

**LATEST FACTS override older diagnostic/HTTP-400/source-only text further down.** The initial NVIDIA 27B API HTTP 400 and absent native parser flags were RESOLVED via a user-approved RECREATION of the canonical `qwen38-27b` from pinned `recipes/qwen38-27b.runtime.json` (vLLM 0.32.0, modelopt_mixed, port 8000, `qwen3_coder` / `qwen3` / exact NVIDIA Jinja). Actual DGX native `tool_calls`, tool result continuation, streaming, normal chat, benchmark v2 **PASS** (3/3, mean client E2E 10.957 tok/s, p50 TTFT 0.165412 s), and Open WebUI Native **user-confirmed PASS**. Original old container's verified stopped backup was deleted after full success; new canonical `qwen38-27b` is operational. P3-C one-off already REAL PASS/CLOSED; old P3 Docker IDs are historical, not current execution identity.

Wizard manifest cleanup then actually removed the two *stopped historical test containers*, `qwen38-27b-failed-6d9ede0904c2` and `qwen38-27b-native-tools-v1`. Live `cleanup --execute` and independent `cleanup --status` returned `MANIFEST_RETIRED_CONTAINERS_CLEANED`, `issues=[]`, both absent, active canonical 27B preserved; `service manager status --json` returned `LIVE_SERVICE_VERIFIED` with API `qwen3.8-27b` at :8000. The recorded cleanup was completed, NOT a pending removal. `qwen38-flash` remains stopped; Open WebUI and Portainer remain running.

**Next work is NOT P2 native-tool HTTP-400 troubleshooting.** It is general Wizard model lifecycle / recipe diff-aware install, removal, reinstallation and same-name recreation, current-Docker-ID-aware model switching and independent production release acceptance. Canonical 27B and Flash are removable/reinstallable upon independently approved actions; no global deletion ban. Such generic lifecycle functionality and the post-container-ID-change operating switch are **NOT YET RELEASED OR REAL-DGX QUALIFIED**. Keep `PRODUCTION_EXECUTION_RELEASED=False`; one active GPU model and port 8000; preserve historical journal/receipts/images/model files unless explicitly scoped.

Details: [27B real PASS](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-LIVE-PASS-20261107.md), [actual cleanup PASS](../docs/WIZARD-MANIFEST-RETIRED-CONTAINER-CLEANUP-LIVE-PASS-20261107.md), [new Wizard lifecycle scope](../docs/WIZARD-RECIPE-DRIFT-MODEL-LIFECYCLE-NEXT-20261107.md). Do NOT edit the canonical recipe JSON cosmetically without a versioned/requalified migration: its exact SHA is bound into the current latest benchmark pointer.

---

## START HERE — 2026-11-07 LATEST: P2 Tool Calling HTTP 400 CONFIRMED; ordinary switch real bidirectional PASS

**Latest operator's real DGX at source HEAD `09c6780`**: fresh source fast-forward completed; **NVIDIA 27B is ACTIVE** on `:8000/v1` (`qwen38-27b`, `qwen3.8-27b`, `LIVE_SERVICE_VERIFIED`, `issues=[]`). The *independent ordinary operating journal* is `VERIFIED/COMMITTED`, **14 events**, `issues=[]`. This corroborates BOTH real ordinary operating switch directions `27B→Flash` and `Flash→27B` PASS. Historical P3-A/B/C and P3-C final PASS remain **CLOSED**; never rerun them. **Normal main Wizard execution remains gated** (`PRODUCTION_EXECUTION_RELEASED=False`); actual production menu acceptance and real forced-failure recovery are distinct and still outstanding.

**P2-FINAL tool support remains OPEN**: operator directly inspected preserved `qwen38-27b` Docker `Config.Cmd`, which has `modelopt_mixed`/BF16/context 8192, **NO `--enable-auto-tool-choice`, `--tool-call-parser`, or `--reasoning-parser`**. `serve_27b.sh --tools-profile` displays correct opt-in source flags `qwen3_coder` + `qwen3`; `serve_27b.sh --tools-probe` returns **`BLOCKED/LOCAL_API_HTTP_ERROR_400`**, structured tool cycle **NOT PASS**. Git source change does not retrofit existing container. Do not guess the exact HTTP 400 body, or claim migration/Parser/Open WebUI Native PASS. Next task is **safe separate tool-enabled model recipe/variant and rollback design**, with vLLM 0.32, one active model and `:8000` unchanged. Any actual runtime mutation requires new operator downtime consent. Original containers/images/HF caches and private receipts preserved. Draft PR #1 stays unmerged.

Read **[current state](CURRENT-STATE.md)**, **[next actions](NEXT-ACTIONS.md)**, **[evidence ledger](EVIDENCE-LEDGER.md)**, **[new conversation starter](SESSION-START-PROMPT.md)**, and **[P2-FINAL acceptance](../docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md)** before older snapshots. Earlier lines below (P3-C NOT_RUN, Flash active, first direction outstanding) are historical, NOT current. Latest branch SHA/CI should always be queried from GitHub.

---

## 2026-11-07 — START HERE: P3-C 실제 DGX PASS, NVIDIA 27B ACTIVE, 이제 Wizard UX 개발

**가장 최신 확정 상태:** P1 Flash-Next Verify/Benchmark와 P3-B 후 P1 재검증/진단, P2 NVIDIA 27B trial/benchmark, P3-A/B/C 실제 양방향 stage 순차 실행이 전부 PASS. 최종 `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_observed_model=27b`, `post_switch_status=LIVE_SERVICE_VERIFIED` at port 8000. **원본 모델/컨테이너/HF 캐시 보존; P3-A/B/C 재실행 금지.** Git 공개 모델별 benchmark 원본 대조는 2/2 VERIFIED. 이 아래 오래된 `P3-C NOT_RUN`, `Flash active`, `benchmark comparison pending` 문구는 당시 이력이며 **현재 상태가 아님**.

**새 대화는 [최신 시작 프롬프트](SESSION-START-PROMPT.md)에서 시작하세요.** [P1–P7 실제 백엔드/UX 별도 검증 표](../docs/P1-P7-WIZARD-ACCEPTANCE-STATUS-20261107.md)를 우선 참고. 대화형 `./wizard.sh`의 P3 메뉴는 계획 조회만 하므로, **다음 개발은 통합 Wizard 운영 UX + 반복 가능한 일반 Flash↔27B 전환**, 실제 27B 라이브 서비스 운영은 별도 명시적 승인 전 변경 금지. Draft PR #1은 미병합이며 GitHub HEAD/CI는 새 세션에서 다시 조회.

---

## 2026-11-07 — MODEL BENCHMARK RESULTS NOW IN GIT AS SANITIZED SUMMARIES

User requested storing benchmark results in Git. Current branch now tracks real operator-reported metric-only summaries at `benchmarks/published/qwen3.8-flash-next/f506db4c76430674.json` (post-B Flash mean 37.9527 tok/s; original private JSON SHA `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db`) and `benchmarks/published/qwen3.8-27b/80f109dbd7c97460.json` (27B E2E 7.9002 tok/s; decode proxy 11.1801; original SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`). These came from the user's actual DGX logs, not fresh GPU measurement. No private raw JSON, prompts, paths, tokens/approvals, container IDs or logs committed. `scripts/manager/benchmark_publication.py` is a guarded allowlist exporter (read-only plan/verify; explicit hash-approved local write; NO auto Git add/commit/push). `bash scripts/temporary/verify-published-benchmarks.sh` cross-checks Git summaries against original DGX receipts WITHOUT service changes. **Source CPU tests pass; real original-byte cross-check is pending operator pull/run.** See `benchmarks/published/README.md`.

User also tried Stage-C `--execute`, but typed a leading `[` with the SHA; wrapper returned **CANCELLED/executed=false/execution_dispatched=false/approval_accepted=false**. Flash-Next stayed the observed live source; **P3-C NOT_RUN**. Future C approvals require NEW current 64-hex SHA without the displayed brackets, then two distinct exact downtime/final-C literal inputs. Never reuse historical plan ID or infer authorization. Current Draft PR #1 unmerged; the agent only committed source/sanitized measurement summaries.

---

## 2026-11-07 — STAGE-C CANONICAL READ-ONLY READY; TRACKED C OPERATOR SOURCE IMPLEMENTED

The latest **actual operator DGX** command `./wizard.sh switch flash-next-27b stage-c --plan --json` returned **READY_TO_REQUEST_TRANSITION_APPROVAL**, `issues=[]`, `p1_evidence.status=PASS`, correct active original `flash-next` and preserved target `27b` CIDs/images, with `executed=false`. This is a real read-only plan, **not** C downtime permission. The old C plan SHA `d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7` had a short expiry and is NEVER reused. User also entered `COPY` at optional evidence import's exact-plan prompt; result **CANCELLED/copied=0**, unrelated to C.

To honor original D-016 operation model, source-tracked `scripts/temporary/p3-stage-c-operator.sh` and Python controller provide default `--plan` (non-disruptive) and separately approved `--execute` (human TTY, fresh C-only SHA, exact Flash downtime and independent final-C confirmation; canonical Wizard alone changes Docker). 27B final API and original canonical `stage-c.json` checked again; new operator report is private ignored project `reports/transitions/flash-next--to--27b/`, immutable P3 operational state remains in original local state directory. CPU fake-DGX tests in `tests/test_p3_stage_c_operator_cpu.py`. After current GitHub HEAD CI success and clean DGX fast-forward pull, request **`bash scripts/temporary/p3-stage-c-operator.sh --plan` first**. The actual `--execute` requires a NEW separate operator decision to interrupt Flash. No automatic execution, model deletion, migration, PR merge, or P3-A/B repetition. [Operator C runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## 2026-11-07 — NEXT: MODEL HISTORY + P2/P3 COPY-ONLY CONSOLIDATION; P3-C READ-ONLY PLAN

User asked to add per-model past Verify/Benchmark/history in the main Wizard and phase in project-local P2/P3 evidence. Implemented read-only catalog `scripts/manager/evidence_catalog.py`, integrated `Select model → 4 Past results` and `Advanced → 8 Exact-approved report COPY`; machine CLI `./wizard.sh evidence list --model flash-next --kind benchmark`, `./wizard.sh evidence migrate --plan|--guided`. P1/P2/P3 old source receipts, runtime locks/journal remain unchanged; project reports ignored by Git. New copy uses fresh 64-char approval, revalidation, 0600 O_EXCL, 0700 directories, hash dedup; P3-C safety-critical evidence gate still reads canonical state. See [migration contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md).

Actual DGX ZIP still grounds P3-A/B PASS and POST-B P1 Verify+Benchmark PASS; last observed Flash-Next active :8000. **P3-C is the next eligible operating stage, but is NOT_AUTHORIZED/NOT_RUN and its *new live preflight* has NOT yet been supplied.** Once latest GitHub code/CPU CI passes and user clean-pulls, request ONLY `./wizard.sh switch flash-next-27b stage-c --plan --json`. If `READY_TO_REQUEST_TRANSITION_APPROVAL` with `issues=[]` and P1 gate PASS, separately seek actual Flash downtime authorization. Do not automatically execute C, repeat A/B, clean caches or merge Draft PR #1. Older messages claiming POST-B P1 NOT_RUN superseded.

---

## 2026-11-07 — CURRENT operator state: Post-B Flash Verify + Benchmark REAL PASS, UX source fixes

The operator supplied a ZIP containing actual Flash-Next GPU Verify and Benchmark executed after successful P3-B. Both PASS with distinct explicit SHA approvals; measured 3-request mean 37.9527 tokens/sec, TTFT p50 1.384594 sec, latency p50 1.724560 sec. Last known actual API served `qwen3.8-flash-next` on :8000. Older statements that POST-B P1 is NOT_RUN are superseded. `P3-C` is still NOT_AUTHORIZED; no model switch/restart/repeat inferred.

The open Draft PR #1 working branch includes a model-centric interactive UX change: operator sees the exact approval SHA, avoids the duplicate action selection, sees Verify and Benchmark metrics, and stores future P1 receipts under Git-ignored project `reports/models/qwen3.8-flash-next`. Historical receipts stay immutable; gate reads both legacy and project paths. Source CI includes new approval/UI and mixed-path tests. **Never confuse CPU CI success with actual DGX UX rerun.** See [current state](CURRENT-STATE.md), [next actions](NEXT-ACTIONS.md), [evidence ledger](EVIDENCE-LEDGER.md), [operating decisions](DECISIONS.md), [UX/evidence contract](../docs/WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

## 2026-11-07 — CURRENT: P3-A/B actual DGX PASS; Flash-Next restored; POST-B P1 pending

**Supersedes all older headings below that say "P3-B NOT_RUN" or "27B ACTIVE".** Operator-provided actual DGX P3-B output: `P3_B_PASS_FLASH_NEXT_ACTIVE`, `executed=true`, `wizard_result.status=PASS`, `live_verified=true`, `post_switch_status=LIVE_SERVICE_VERIFIED`, and original served ID `qwen3.8-flash-next`. The immutable Wizard receipt is `~/.local/state/blazux-wizard/p3/stage-b.json`. The old B operator report was **misnamed** `~/blazux-p3-reports/p3-a-operator-20261106T223124Z-14861d75.json` due to imported A persistence; do not delete or rename it. Source fix now uses B-specific filenames and reports independent manual consent and execution dispatch.

POST-B P1 `p1-post-download.sh --inspect-only` on actual DGX was READY/PASS **for source, API and Verify/Benchmark plans only** (report `~/blazux-p1-reports/20261106T224010Z-d2095867/result.json`). Verify execution, Benchmark execution and full post-B doctor/inventory raw diagnosis are **NOT_RUN/NOT_YET_QUALIFIED**. The read-only D-016 `bash scripts/temporary/p1-post-b-audit.sh` was implemented and CPU-tested; DGX run still pending. P3-C NOT_RUN/NOT_AUTHORIZED. Preserve port 8000, single active GPU model, original containers/image/cache and Draft PR #1.

---

> **2026-11-06 LATEST REAL P3-B INSPECTION: READY, 27B ACTIVE, B NOT APPROVED.** User ran tracked stage-B read-only inspector after P3-A. Result `READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`, live API `qwen3.8-27b`, original Flash preserved identity. `~/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. Core B gate now uses **`I_ACCEPT_27B_DOWNTIME`** (not old Flash ACK) and independently **`I_SEPARATELY_AUTHORIZE_P3_STAGE_B`**. New D-016 `scripts/temporary/p3-stage-b-operator.sh` defaults read-only, with a separately approved `--execute` route only after user explicitly consents to new 27B downtime. **Do not treat inspection PASS as B approval.** P3-B actual transition NOT_RUN, post-B P1 and C NOT_RUN. Keep 27B LIVE, preserve models/containers, no Draft PR merge. See [D-040](DECISIONS.md), [next actions](NEXT-ACTIONS.md), [stage B operator runbook](../scripts/temporary/README.md).

> **LATEST 2026-11-06 — REAL P3-A PASS; NVIDIA 27B ACTIVE, STOP BEFORE B.** Operator executed `p3-stage-a-operator.sh --execute` on DGX, actual Wizard `stage=a,status=PASS,executed=true,live_verified=true`, independently verified Manifest/API `27b`, final wrapper `P3_A_PASS_27B_ACTIVE`, `issues=[]`; operator report `~/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json` and immutable Wizard receipt `~/.local/state/blazux-wizard/p3/stage-a.json`. Previous older paragraphs claiming A NOT_RUN are **historical**, superseded here. **P3-B (27B→Flash-Next) is NOT approved/executed**, nor are post-B P1 rebenchmark and C. New D-016 `scripts/temporary/p3-stage-b-inspect.sh` is **read-only only** and needs GitHub source CI then DGX pull; no B executor or GPU start/stop through it. See [state](CURRENT-STATE.md), [decision D-039](DECISIONS.md) and [runbook](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md). No auto B, cache deletion or PR merge.

> **NEW P1 PRE-A CLEARANCE + P3-A OPERATOR BOUNDARY (2026-11-06):** operator's actual DGX `scripts/temporary/p1-pre-a-readiness.sh` output at `20261106T065104Z` was `PRE_A_P1_REVIEW_READY`, `issues=[]`: source + P1 functional and measured benchmark PASS, historical/current rc3 proved own active Flash collision. User's earlier conditional approval is eligible **only for P3-A**. A dedicated GitHub-tracked D-016 `scripts/temporary/p3-stage-a-operator.sh` is now the operator interface: `--plan` read-only, `--execute` TTY with full current plan hash and individually typed downtime and P3-entry acknowledgments, one stage only with independent 27B API recheck. **Actual P3-A/B/C NOT_RUN**. Preserve all original assets, don't auto-chain or merge Draft PR. See [current state](CURRENT-STATE.md), [D-037](DECISIONS.md), [P3 runbook](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md).

> **LATEST actual P2 / staged P3 source (2026-11-06):** User-supplied DGX bounded NVIDIA 27B streaming benchmark 3/3 PASS, overall `BENCH_PASS_RESTORED_VERIFIED`, original Flash-Next `RESTORED` and fresh Wizard `LIVE_SERVICE_VERIFIED`; P2 **COMPLETED/STOP**. Earlier paragraphs below claiming P2 benchmark NOT_RUN are historical. P3 D-034 stage A/B/C source executor and P1 measured evidence gate now exist and have CPU CI tests, **but actual P3 switch still NOT_RUN/NOT_QUALIFIED and must not run without separate stage-specific downtime approvals**. New runbook: [docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md](../docs/P3-PERSISTENT-SWITCH-SOURCE-20261106.md). Do not interpret this source update as permission to interrupt :8000, start GPU models or merge PR #1.

> **LATEST P2/P3 OPERATOR RULE (2026-11-06):** P2 actual 27B benchmark must finish and **STOP**; NEVER auto-enter P3. P3 requires a fresh explicit operator decision, separate approved establishment of active 27B, **27B→Flash-Next** verification, **P1 deficiencies addressed + actual Flash-Next rebenchmark**, and finally a separately approved **Flash-Next→27B** transition with **27B active as final state**. The former P3 `roundtrip` plan/execute is **RETIRED and BLOCKED**. Source-only new read-only command `./wizard.sh switch flash-next-27b sequence --plan --json` does not execute any transition; persistent switch backend still missing. See [binding P3 sequence](../docs/P3-MANUAL-TRANSITION-SEQUENCE-20261106.md), [operating rules](OPERATING-RULES.md), [newest current state](CURRENT-STATE.md) and [D-034](DECISIONS.md). Previous roundtrip procedures below are superseded. No GPU/service mutation has been performed for this rule change.

> **2026-11-06 LATEST ACTUAL GPU EVIDENCE:** NVIDIA Qwen3.8-27B startup/API/small text inference on DGX **PASS** and original Flash-Next normal-path restore **RESTORED**, zero issues (`PASS_RESTORED`). This supersedes historical `NOT_RUN` notes below; benchmark and repeat switching not yet qualified. **Live status now uses Manifest + API via `./wizard.sh service manager status --json`**, no separate raw Docker/curl commands. See [real P2 GPU evidence and Wizard workflow](P2-27B-GPU-TRIAL-PASS-20261106.md). No further service interruption authorized by this report.

> **2026-11-06 P2 superseding update:** Operator completed the NVIDIA 27B exact-revision download (19/19, exit 0, \`SOURCE_FILES_PRESENT_PINNED_CANDIDATE\`; GPU \`NOT_RUN\`). New read-only qualification: \`./wizard.sh model 27b status --inspect-runtime --json\`. Older 84% transfer comments below are historical, not current. No service switch/27B start is authorized. See \`CURRENT-STATE.md\`, \`EVIDENCE-LEDGER.md\`.

> **2026-11-06 full Wizard SOURCE handoff (D-021):** `./wizard.sh` now runs complete operator console `wizard/console.py`: 1 model → recommended next / all lifecycle actions, 2 service status/health/logs and guarded start/stop/restart/rollback/proxy/gateway, 3 advanced P3/P4/P6/P7 + readiness dashboard. `./wizard.sh workflow 27b --json`, `./wizard.sh workflow 27b --for-action start --json`, and `./wizard.sh roadmap --json` expose machine-readable plans. P1 and P2 execution backends **unchanged**, P2–P7 real runtime/switch/cleanup still **BLOCKED**. Full spec: [../docs/UNIFIED-MODEL-WIZARD-DESIGN.md](../docs/UNIFIED-MODEL-WIZARD-DESIGN.md). User's DGX 27B transfer started but no completion receipt yet; avoid pull while it runs.

# Handoff index — START HERE

> **2026-11-05 current Wizard UI decision (D-020):** `./wizard.sh` now presents **1 Select/run model, 2 Service, 3 Advanced, 0 Exit**. `./wizard.sh select 27b --json` produces a read-only consolidated lifecycle plan. Old P1–P7, model/switch/storage/operations/service commands remain supported, and the P1 guarded backend is retained verbatim. Approved design: [../docs/UNIFIED-MODEL-WIZARD-DESIGN.md](../docs/UNIFIED-MODEL-WIZARD-DESIGN.md). DGX user-reported pinned NVIDIA 27B download **started** (`Fetching 19 files: 84%`); receipt, runtime and switching **NOT_VERIFIED**. No DGX commands from source work; do not change the worktree under an active download.



**Canonical starting point for every new ChatGPT, human or agent work session on this fork.** These files live on the **new planning branch** `feature/recipe-wizard-handoff` until merged. Do not assume they are on `main`.

## Confirmed delivery order (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

## Wizard CLI first-class entrypoint

**Wizard architecture decision (2026-11-05):** Implement all P1–P7 **menu/CLI modules first** and then integrate/debug actual runtime in P1→P7 order. Root operator entry is `./wizard.sh`; `wizard/menus/models/`, `switching/`, `storage/`, and `operations/` own per-menu behavior, with `wizard/main.py` and `wizard/menus/common.py` for routing and safe source contracts. Scripts accept explicit stage/action arguments and emit JSON and stable exit codes for operator-mediated DGX tests. Only P1 calls the existing guarded backend today; P2–P7 are SOURCE-ONLY plans and must never execute merely because a menu exists. No SGLang; vLLM 0.32 only.

CLI reference: [../docs/WIZARD-CLI-CONTRACT.md](../docs/WIZARD-CLI-CONTRACT.md). Current stage readiness: [CURRENT-STATE.md](CURRENT-STATE.md).

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

### User-operated DGX temporary command bundles (D-016/R1D)

Prefer a **Git-committed, CI-tested, single-entry temporary script** in `scripts/temporary/` over pasting many shell commands. The operator completes any previous setup, then `git pull --ff-only`, runs one wrapper, and returns reviewed JSON evidence. See [OPERATING-RULES.md](OPERATING-RULES.md) R1D and [scripts/temporary/README.md](../scripts/temporary/README.md). Initial P1 bundle: source/CI PASS 131/131 tests/job ×2 at `b9f9a1b`, actual DGX execution NOT_RUN.

## Read order (mandatory)

1. **[CURRENT-STATE.md](CURRENT-STATE.md)** — latest known project, branch/HEAD, active stage, blockers and verification status.
2. **[OPERATING-RULES.md](OPERATING-RULES.md)** — do-not-touch boundary, evidence standards, update obligations.
3. **[NEXT-ACTIONS.md](NEXT-ACTIONS.md)** — tasks in priority order and exit conditions.
4. **[DECISIONS.md](DECISIONS.md)** — fixed decisions vs proposals.
5. **[EVIDENCE-LEDGER.md](EVIDENCE-LEDGER.md)** — what was actually tested, source vs DGX.
6. **[CHANGELOG.md](CHANGELOG.md)** — append-only significant updates.
7. **[../docs/MODEL-RECIPE-WIZARD-PLAN.md](../docs/MODEL-RECIPE-WIZARD-PLAN.md)** and **[../docs/MANIFEST-CONTRACTS.md](../docs/MANIFEST-CONTRACTS.md)** — scope, staging, interfaces and cleanup contract.

Use [SESSION-START-PROMPT.md](SESSION-START-PROMPT.md) for a new conversation. Do not paste full context repeatedly if GitHub can be read.

## Source-of-truth hierarchy

1. Fresh **read-only actual DGX evidence** and verified GitHub refs/CI (for runtime/git facts).
2. `CURRENT-STATE.md` and `EVIDENCE-LEDGER.md` (for previously observed facts; preserve timestamps).
3. Reviewed committed plan, contracts and decisions.
4. Legacy Preview/YSLAB documents and earlier chat summaries (historical context, **not** proof of this fork).
5. Assumptions must be labelled `UNVERIFIED`; no upgrade to PASS without evidence.

When refs disagree, do not silently merge/overwrite: record the discrepancy, refresh with tools and fix source documents in the same PR.

## Handoff closing checklist

On any session that changes GitHub, documents, tests, requirements or verified state:
- commit implementation and documentation, or record precisely why they cannot be committed;
- update `CURRENT-STATE.md` and `NEXT-ACTIONS.md` **in the same change set**; update ledger/decisions/changelog if affected;
- refresh actual branch, commit, PR and CI status using GitHub tool; never write a self-referential “this file contains its own HEAD” claim;
- include exact commands, what ran, test results, artifact/log links, what did **not** run, next safe action;
- open or update PR as appropriate; **do not merge merely because documentation exists**;
- end with a short handoff summary linking these files.

`CURRENT-STATE.md` is a **living snapshot**, not a history. Put the history in `CHANGELOG.md` and evidence in `EVIDENCE-LEDGER.md`. No secrets or credentials in these files. File and branch names are stable interfaces for future sessions.
