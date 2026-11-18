# P5 Orcarouter MTP0 — one-shot visible-TTFC GPU measurement (2026-11-19)

## 2026-11-19 KST — P5 1K/4K/7K saved FULL RESOURCE RECEIPT analyzed (READ-ONLY)

**Supersedes:** previously `P5_RESOURCE_FULL_RECEIPT_REVIEW_PENDING` is now **reviewed for the fields present in the user-uploaded JSON**, but does **not** supersede `PLE_RESIDENCY_NOT_OBSERVED`, independent port/GPU process ownership, or production release.

The operator uploaded the original full 38,619-byte private receipt `orcarouter--20261118T214659097604Z--86b3752c0029.json` from `/home/inlc/.local/state/blazux-wizard/model-measurements/`. This GitHub-side analysis opened and parsed the actual JSON without any DGX access, new inference, Docker/GPU changes or receipt mutation. Receipt action `benchmark-execute`; variant `P5_VISIBLE_NO_THINKING_ONESHOT_V1`, git SHA `bc0a9ea2346b85fa9f8e6ef132b765078b6385db`, 3/3 `MEASURED_VISIBLE`, `COLLECTED_UNQUALIFIED`, source-recorded API/serving identity and stable Docker ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, `benchmark_verified=false`, `production_released=false`. Resource interval `OBSERVED_INTERVAL`, **42.008 s** with **four** snapshots at 2026-11-18 21:46:16.020624, 21:46:29.233449, 21:46:43.025011, 21:46:58.028546 UTC (before and after each request; not continuous in-flight sensor capture). `cgroup_container_identity_continuous=true`, `cgroup_identity_discontinuity_detected=false`.

| Resource metric | Before | After 1K | After 4K | After 7K |
| --- | ---: | ---: | ---: | ---: |
| Sampled GPU utilization (%) | 0 | 66 | 74 | 75 |
| Sampled GPU power (W) | 9.86 | 20.43 | 20.98 | 21.22 |
| GPU temperature (°C) | 34 | 38 | 40 | 41 |
| Highest system thermal-zone temp (°C) | 35.1 | 43.4 | 45.5 | 46.6 |
| Host MemAvailable (GiB) | 29.777 | 29.794 | 28.729 | 28.731 |
| Container cgroup memory.current (GiB) | 22.914 | 22.924 | 22.579 | 22.581 |
| Container cgroup file cache (GiB) | 17.863 | 17.871 | 17.525 | 17.525 |
| Container cgroup anon (GiB) | 4.597 | 4.596 | 4.596 | 4.598 |
| Docker CLI `MemUsage` (GiB, distinct accounting) | 7.176 | 7.178 | 7.180 | 7.182 |
| cgroup pgmajfault (cumulative) | 118278 | 120282 | 120282 | 120282 |
| host io PSI some avg10 (%) | 0 | 0.53 | 0.18 | 0.03 |

**Interval/derived values:** host CPU busy **5.11%** for this 42.008 s; host vmstat major faults **47.705/s**, cgroup `pgmajfault_delta=2004` (all added between before and first after-1K sample, none in remaining intervals); `workingset_refault_file_delta=0`; host `pswpin/s=0`, `pswpout/s=0`, host swap used constant **1.307 GiB**. Host memory PSI `some.avg10` maximum **0.0%**; cgroup memory `events` `low/high/max/oom/oom_kill` deltas **all zero**. `nvme0n1` sampled cumulative counter-derived read **195401 bytes/s ≈ 0.186 MiB/s**, write **316600 bytes/s ≈ 0.302 MiB/s**, average read time **0.15 ms/I/O**, write **1.56 ms/I/O**; **not PLE-file-specific**, not a load bandwidth benchmark. Historical `memory.peak=39,753,752,576 bytes ≈ 37.024 GiB` cannot be attributed to this short session.

**Observed memory accounting:** from first to last, cgroup `memory.current` decreased approximately **0.333 GiB** and file cache `file` decreased approx **0.338 GiB**, while `anon` stayed near **4.60 GiB**. Host MemAvailable dropped **1.046 GiB**, with no observed swap traffic or memory PSI stall. These differences do not establish a memory leak, PLE eviction or saved GPU capacity: host and cgroup accounting differ; GB10 uses unified memory and `nvidia-smi memory.used/memory.total` were **null**, not zero; `process_smaps_rollup_status=NOT_OBSERVED`, `ple_specific_residency_status=NOT_OBSERVED`, `ple_specific_resident_bytes=null`. Do **not** sum Docker CLI's `MemUsage≈7.18GiB` with cgroup `memory.current≈22.58GiB`, or treat either as true exclusive model/PLE VRAM.

**Scope limits:** GPU utilization/temperature/power are instantaneous readings *after* requests, not the workload's peak, per-token curve, or proof of stable clocks/throttling. CPU governors `performance` and sample frequencies 2808–3900 MHz do not verify throttling (`throttling_verified=false`). Each resource snapshot carries `model_identity_verified_by_api=false`; the benchmark's separate pre-run API identity gate is not an independently authenticated API+Docker+PID/smaps/PLE provenance chain. No validated host-port :8000 NAT listener PID or GPU exclusivity. All three visible-output streams ended with `finish_reason=length`, so no completed-answer quality assurance, and single samples are not reproducible performance qualification.

**Acceptance:** `P5_FULL_RESOURCE_RECEIPT_REVIEWED_4_SNAPSHOTS / P5_42S_NO_OBSERVED_OOM_SWAP_PRESSURE / P5_CGROUP_MAJORFAULTS_2004 / P5_PLE_RSS_AND_NAT_OWNER_UNVERIFIED / CI_UNVERIFIED / PRODUCTION_BLOCKED`. The P5 GPU one-shot authorization is **consumed**, no further inference/retry authorized. Next source/read-only work: exact pinned PLE file-path/inode/PID/worker smaps evidence; NAT host-port ownership without treating absence of `ss` PID as outage; CI workflow registration/permissions investigation; then P6-E/P7/P8 safety gates.

---

## 2026-11-19 06:46 KST — visible-output MTP0 1K/4K/7K GPU ONE-SHOT EXECUTED, 3/3 measured

**Supersession:** the prior 'GPU one-shot SOURCE READY / EXECUTION PENDING' was resolved by an **operator-supplied actual DGX transcript**. At Git SHA `bc0a9ea2346b85fa9f8e6ef132b765078b6385db`, operator completed an exact-head fast-forward pull (17ebc7f..bc0a9ea), clean-worktree guards and two CPU suites: `test_p5_visible_once_cpu.py` **8/8 PASS**, `test_model_measurements_cpu.py` **23/23 PASS**, 31/31 selected CPU tests. The one-shot real workload ran with `chat_template_kwargs.enable_thinking=false`; the transcript ends with `P5_VISIBLE_ONESHOT_COMMAND_COMPLETED`. Source-bound reported Git SHA is `bc0a9ea2346b85fa9f8e6ef132b765078b6385db`.

**Runtime:** existing Orcarouter MTP0 `qwen38-orcarouter-qsa62318-lmhead-v3`, Docker ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`; active max context 8192. **`container_id_continuous=true`, `service_mutated=false`, `production_released=false`.** The source code imposed 1K/4K/7K contexts, 256 output tokens each, concurrency 1 and zero auto-retry.

| Actual metric | 1K | 4K | 7K |
| --- | ---: | ---: | ---: |
| Tokenizer-input tokens | 995 | 4055 | 7105 |
| Server prompt tokens | 1007 | 4067 | 7117 |
| Server completion tokens | 256 | 256 | 256 |
| TTFT seconds | 0.52051 | 1.59565 | 2.80664 |
| TTFC seconds | **0.52051** | **1.59565** | **2.80664** |
| Post-first-token usage-derived TPS | 21.961 | 22.943 | 22.948 |
| End-to-end seconds | 12.13219 | 12.71006 | 13.91874 |
| Visible characters | 256 | 256 | 256 |
| Reasoning delta events / chars | 0 / 0 | 0 / 0 | 0 / 0 |
| Stream quality | VISIBLE_CONTENT_AND_USAGE_OBSERVED | VISIBLE_CONTENT_AND_USAGE_OBSERVED | VISIBLE_CONTENT_AND_USAGE_OBSERVED |
| Case status | MEASURED_VISIBLE | MEASURED_VISIBLE | MEASURED_VISIBLE |
| Finish reason | length | length | length |

Summary: `status=COLLECTED_UNQUALIFIED`, `requested_cases=3`, `visible_measured_cases=3`, `ttfc_observed_cases=3`, `tps_observed_cases=3`, `stop_issue=null`, `inference_executed=true`. This establishes the **limited live observation** of TTFC/TTFT and usage-based TPS with request-local thinking disabled. It does **not** demonstrate semantic answer correctness, full task completion, statistical throughput quality, high-concurrency/long-context endurance, or vLLM/PLE engine/runtime release qualification. `finish_reason=length` means each result hit the 256-token budget; no normal answer completion was shown.

**Private evidence** (operator host path, not independently fetched or validated by GitHub): `/home/inlc/.local/state/blazux-wizard/model-measurements/orcarouter--20261118T214659097604Z--86b3752c0029.json`. Private consumed-on-attempt marker `/home/inlc/.local/state/blazux-wizard/model-measurements/p5-visible-mtp0-v1--9c49950015a845357e90fabe.claim`. **The one-shot approval has been used and must not be replayed** even if later inspection finds a gap. The printed compact JSON omits the private receipt's full per-sample resource snapshots and interval, so numerical pre/post GPU, CPU, memory/cgroup, NVMe, PLE RSS or throttle conclusions **cannot** be made from this transcript alone. A separate **read-only** summary of the already-saved receipt may close the observational resource-metrics gap without additional GPU inference.

**Remaining acceptance gates:** GitHub Actions latest SHA CI absent; P5-D NAT/host-port PID ownership and independent GPU exclusivity unverified; PLE resident/physical unique RSS and pinned inode/worker coverage unverified; full resource/workload correlation review pending; Orcarouter adapter runtime qualifying, Tools/Vision/MTP2 and sustained performance pending; P6 operating Journal v2/nonce/executor, P7 independent integration, P8 fault/recovery and production release remain **BLOCKED**. Previous 1K/4K default-thinking 256-token results are preserved separately and must not be blended with this different workload as a controlled A/B speed comparison.

**Current classification:** `P5_VISIBLE_TTFT_TTFC_TPS_LIVE_3_OF_3_MEASURED / P5_ONE_SHOT_CONSUMED / P5_RESOURCE_FULL_RECEIPT_REVIEW_PENDING / P5_D_NAT_PLE_UNVERIFIED / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---

## Operator approval and bound

The operator explicitly approved **GPU use for P5 measurement** in the conversation on 2026-11-19 KST. This is *not* approval to switch or restart models, change Docker/cgroups, delete files, alter the operating Journal, execute fault injection or merge the Draft PR. The exact one-shot plan introduced for that permission is:

- Model: **currently active** `orcarouter` MTP0, vLLM 0.32.0, OpenAI API `http://127.0.0.1:8000/v1` and registered exact served ID only.
- Three synthetic-context prompts: **1K, 4K, 7K** target input tokens; one request per context, concurrency **1**, output cap **256 tokens** each (at most 768 completion tokens overall); no fallback or automatic retry.
- Each request includes `chat_template_kwargs: {"enable_thinking": false}`, a vLLM/Qwen request-time flag **not** a change to the engine's chat template or launch flags. The custom Orcarouter adapter must prove it respects this during execution; reasoning-only or no-visible-content stops remaining requests and reports incomplete.
- Exact API/served ID/64-digit Docker ID/max context from the existing `_identity_gate` **before** inference; tokenization, output window and Docker ID checked. Stop if active runtime differs or if a single inference fails. A unique private `O_EXCL` **claim marker** is written before the first GPU request and never automatically removed. It intentionally consumes a one-shot attempt even after partial failure. This is private measurement state **not** an operating switch Journal.
- Existing read-only resource snapshots **before and after each case** and `resource_interval`, in the private full receipt. These are sequential samples; they **cannot** independently prove in-flight GPU utilization, unique per-PLE RSS or host NAT process ownership. vLLM GB10 GPU memory is shared host memory; do not double count.
- Measurement report: per-context server token usage, TTFT, **TTFC**, post-first-token usage-derived TPS, E2E, `delta.reasoning` presence, visible character count, finish reason, SSE done, source SHA, container ID, pre/post snapshots, private receipt, explicit fail-closed status. **No prompts/answers/reasoning text saved**.
- Existing approved 1K/4K **256-token default-thinking** benchmark was completed already and its old approval is consumed. This new authorization is distinct and is **only for this bounded visible/no-thinking attempt**. No replay without new permission.

## One terminal transaction (operator on the running DGX)

```bash
set -euo pipefail
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only
git status --porcelain
test -z "$(git status --porcelain)" || { echo "BLOCKED: dirty tree"; exit 3; }
python3 -B -m unittest discover -s tests -p 'test_p5_visible_once_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_model_measurements_cpu.py' -v
./wizard.sh service manager status --json
python3 -B -m scripts.manager.p5_visible_once \
  --ack-live-inference I_ACCEPT_ACTIVE_MODEL_INFERENCE --json
```

**Important:** The last command triggers up to **three** real GPU inferences. The script exits 3 on any block or incomplete measurement. Do not retry if `p5-visible-mtp0-v1--*.claim` exists or if an execution failed after a claim. The current GitHub documentation/code update is not proof these tests or inference have run on DGX.

## Admission

- If **3/3 visible** with non-null TTFC and observed server usage plus stable Docker identity: accept `P5_VISIBLE_METRICS_COLLECTED_UNQUALIFIED` **only**, preserving resource/port/PLE/production gaps.
- If the model ignores `enable_thinking=false`, API refuses an argument, tokenization fails or a stream lacks visible content: `INCOMPLETE_MEASUREMENT`, no replay; classify as adapter feature limitation or needed separate design, not a host service outage.
- Independent NIC/NAT process ownership, GPU exclusivity, PLE unique RSS and P6/P7/P8 production acceptance remain separate gates.

See `docs/P3-P5-ONE-TURN-CLOSEOUT-20261118.md` for previous default-thinking 256-token results and `docs/P1-P8-EXECUTION-ROADMAP-20261119.md` for milestones.
