# 2026-11-07 — Third real DGX P3-D/E/F/G unified read-only acceptance

**Actual operator DGX evidence**: User fast-forwarded `feature/recipe-wizard-handoff` from `025fd36` to `1b785c6` and executed TWO read-only unified draft batches, first ordinary `--run`, then an operator-initiated `sudo -v` and `--run --sudo-ss`. Both produced JSON results. **No model transfers, Docker stop/start/rm, reinstall, benchmark, or fault injection** occurred. Production release remains OFF, and historic P3-A/B/C immutable.

## 1. Actual DGX results — ordinary (unprivileged) run

- `status=BLOCKED`; `blocked_stages=["P3-D"]`, `P3_DG_EXIT=3`, `acceptance_complete=false`.
- **D**: GPU exclusive process PID 2051842 verified, sole Docker model/port owner `qwen38-27b`. `ss_returncode=0`; IPv4 `0.0.0.0:8000` and IPv6 `[::]:8000` listening with no `users:/pid` visible; `HOST_PORT_PROCESS_PID_UNAVAILABLE`, `sudo_ss_requested=false`. This is insufficient PID evidence, **NOT a measured port conflict**.
- **E**: `status=DRAFT_REVIEW_REQUIRED`, sole issue `FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED`; preserved Flash checkpoint `fc694b54fb0174e0913e6adf86691ef85a4ead47-fp8hybrid` is `LOCAL_PREPARED_FP8HYBRID`, `hybrid_preparation_verified=true`. No canonical reinstall runtime; historically writable `/hf` and legacy argv normalizer are review advisories.
- **F**: **136/136 local CPU tests PASS** (28, 17, 21, 38, 32), lifecycle release flag `false`. This is not actual DGX lifecycle failover qualification.
- **G**: `PREVIEW_PASS_REAL_SWITCH_NOT_RUN`, `current_ids_from_live_docker=true`, journal `VERIFIED/COMMITTED`; source `27b/CANONICAL_RECIPE` → `flash-next/HISTORICAL_P3_INSTANCE`. No real model transfers/rollback.

## 2. Actual DGX results — explicit `--sudo-ss` read-only run

**The operator separately executed `sudo -v` with an interactive password prompt, then reran the normal user-owned script with `--sudo-ss`.** This is operator-authorized, limited socket PID inspection only, not permission to run the entire Wizard as root.

- Overall `status=DRAFT_PARTIAL_ACCEPTANCE_NOT_RELEASED`; `blocked_stages=[]`, `acceptance_complete=false`, `operations_enabled=false`, `production_released=false`, `real_switch_executed=false`.
- **P3-D `READ_ONLY_PASS`**, `issues=[]`, `gpu_process_exclusivity_verified=true`, `port_process_ownership_verified=true`.
- `ss` verified the two unchanged listening endpoints. IPv4 `0.0.0.0:8000` → `docker-proxy` PID **2051487**, IPv6 `[::]:8000` → `docker-proxy` PID **2051502**; both `port_pid_attribution=QUALIFIED_DOCKER_PROXY` against current Docker container IP/port. NVIDIA compute PID **2051842** belongs to active canonical 27B.
- **P3-E `DRAFT_REVIEW_REQUIRED`** with the same sole missing qualification. `source_revision=fc694b54fb0174e0913e6adf86691ef85a4ead47`; `checkpoint_variant=LOCAL_PREPARED_FP8HYBRID`; `hybrid_preparation_verified=true`. Docker image is `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, preserved Flash container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. `Entrypoint=["vllm","serve"]`, served ID `qwen3.8-flash-next`, GPU all, 8000, `max-model-len=500000`, `max-num-seqs=8`, `gpu-memory-utilization=0.80`, MTP 2, Yarn overrides and native-tools flags, `HF_HOME=/hf`, `HF_HUB_OFFLINE=1`, /hf host bind writable. `cmd_normalized=false` under the strict 27B-only parser: this does not invalidate the historically accepted Flash runtime.
- **P3-F** remains **136/136 local CPU PASS**; **P3-G** remains verified read-only preview. User did not run any actual P3-G switch or fault/restore.

## 3. Evidence assessment and next scope

**P3-D hardware read-only audit is confirmed PASS**, with GPU compute + Docker host proxy PID provenance verified. This does not automatically release the general switch. **P3-E has resolved its runtime identification and prepared hybrid-view evidence, but the canonical install/reinstall recipe is still NOT qualified or registered.** E's non-blocking `DRAFT_REVIEW_REQUIRED` is the correct result. **P3-F CPU-only source qualification PASS**, but actual lifecycle executor remains gated. **P3-G real-DGX preflight PASS**, but bidirectional/rollback/UX acceptance is **NOT RUN**.

Next source development: versioned Flash **draft** recipe/candidate comparison preserving hybrid checkpoint, environment, runtime flags, template mounts, vLLM 0.32 and current Docker identity; keep it unregistered and non-executable until reviewed/qualified. Then continue F guarded installer tests and separately approved G real trial. Do not automatically switch, erase immutable P3 receipts, delete images/cache, or promote a draft into `runtimes/service-policy.json`.

Note that the first unprivileged run can still return exit 3 due solely to absent socket PID visibility; the explicit `--sudo-ss` run has already provided actual D process attribution. Do not repeatedly request disruptive hardware trials to recover information we already have.
