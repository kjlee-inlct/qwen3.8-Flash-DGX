# P3–P5 one-turn scoped closeout and remaining operational acceptance (2026-11-18)

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

## 2026-11-19 KST / 2026-11-18 19:17 UTC — APPROVED MTP0 256-token ONE-SHOT EXECUTED

**New operator-supplied actual DGX output supersedes all prior `256_TOKEN_PENDING` statements in this document only as of this timestamp.** The operator ran the bounded one-shot `benchmark-execute --model orcarouter --contexts-k 1,4 --max-output-tokens 256 --ack-live-inference I_ACCEPT_ACTIVE_MODEL_INFERENCE --save --summary-only --json` against the already-active MTP0 trial. Shell printed `P5_PREFLIGHT_PASS`, the 64-char Docker ID, the benchmark result, and `P5_MTP0_ONESHOT_COMPLETED` after a container-ID continuity check. Tested source Git SHA in the saved benchmark result: `17ebc7f7ba2dcfc27c6dca265952dc99cb85e3ee`; the preceding operator shell checked this exact SHA and a clean worktree. Exact active Docker ID: `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`, name `qwen38-orcarouter-qsa62318-lmhead-v3`, host init PID 4016083 (volatile).

Receipt: `/home/inlc/.local/state/blazux-wizard/model-measurements/orcarouter--20261118T191809604958Z--61a970733d8c.json` (stored on DGX, not fetched or independently authenticated by GitHub). Start timestamp `2026-11-18T19:17:43.621227+00:00`; saved filename timestamp approximately 19:18:09Z. `COLLECTED_UNQUALIFIED`, `container_id_continuous=true`, `measured_cases=2/2`, `reasoning_only_cases=2`, `ttft_observed_cases=2`, `tps_observed_cases=2`, `ttfc_observed_cases=0`. This **consumes the previously approved one-shot inference allowance**. Do **not** run it again without new explicit operator approval, fresh identity evidence and a new bounded protocol.

| Observed per-case metric | 1K context | 4K context |
|---|---:|---:|
| `tokenizer_input_tokens` | 1021 | 4081 |
| `prompt_tokens_reported` (server) | 1072 | 4132 |
| `completion_tokens_reported` (server) | 256 | 256 |
| `ttft_seconds` | 0.52965 | 1.70999 |
| `generation_tps_after_first_token` | 22.405 | 22.604 |
| `end_to_end_seconds` | 11.91080 | 12.99106 |
| `ttfc_seconds` | null | null |
| `reasoning_delta_events` | 256 | 256 |
| `reasoning_characters` | 1179 | 1191 |
| `visible_characters` | 0 | 0 |
| `stream_metrics_quality` | REASONING_ONLY_NO_VISIBLE_CONTENT | REASONING_ONLY_NO_VISIBLE_CONTENT |
| `finish_reason` | length | length |
| `status` | MEASURED_REASONING_ONLY | MEASURED_REASONING_ONLY |

Both streamed results observed `reasoning_field_observed=reasoning`, `stream_done_observed=true`, and `token_count_source=SSE_USAGE`. This **live-validates vLLM 0.32 `delta.reasoning` first-token capture and post-first-token usage-based TPS** at this source/runtime, correcting the older 128-token run's TTFT/TPS nulls. TPS is a usage-derived post-TTFT rate, **not** direct inter-token timestamp sampling. No visible content arrived within the 256-token budgets, so first-visible-content latency `TTFC` remains **NOT_OBSERVED**, not zero and not an instrument failure. `finish_reason=length` means the requests terminated at the capped budget. These are two single samples, not statistical repeatability or full performance qualification.

**Still blocked/unverified:** loaded visible-answer latency; independently authenticated PID-to-container/NAT host :8000 owner; GPU exclusivity; PLE-specific resident memory; current HEAD GitHub Actions CI; runtime recipe/image qualification; P6-E operating Journal/live Executor; P7/P8 real integration/fault/recovery; and production release. The log shows **no service restart/switch, Docker config change, operating Journal write or cache deletion**, but this GitHub-side review is not independently privileged host attestation. Preserve all historical receipts and their SHA/timestamp, including the 128-token `COLLECTED_UNQUALIFIED` result. PR #1 remains Draft/Open/Unmerged.

**Status:** `P5_MTP0_256_LIVE_INFERENCE_COMPLETED / P5_SSE_REASONING_TTFT_TPS_MEASURED / P5_TTFC_NOT_OBSERVED / P5_ONESHOT_APPROVAL_CONSUMED / P5_LOADED_QUALIFICATION_PENDING / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---

## 2026-11-19 KST — operator live preflight and 1K/4K 256-token PLAN, NO inference

Operator provided a fresh DGX shell transcript at local HEAD `17ebc7f7ba2dcfc27c6dca265952dc99cb85e3ee` with **empty `git status --porcelain`**. This is a clean source-tree observation made **after** the 65 targeted CPU test transcript; earlier CPU stdout itself lacked SHA, so do not retrospectively assert exact test-SHA cryptographic binding.

`./wizard.sh service manager status --json` returned `LIVE_P5_TRIAL_API_VERIFIED`, `API_IDENTITY_CONFIRMED`, `observed_model=orcarouter`, `runtime_role=DEVELOPMENT_TRIAL`, `p5_development_trial=true`, `expected_served_id=qwen3.8-flash-next-orca-uncensored-bf16`, `host_port=8000`, and `issues=[]`. Active container `qwen38-orcarouter-qsa62318-lmhead-v3` published `0.0.0.0:8000->8000/tcp` / `[::]:8000`, image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`, status `Up 10 days`. The status output **does not expose the fresh full Docker container ID**, and reports `gpu_exclusivity_verified=false`, `port_process_ownership_verified=false`, `operations_enabled=false`, `production_released=false`. Manifest validation PASS is declarative, `runtime_qualified=false`, not a release approval.

Read-only `./wizard.sh operations measurements benchmark-plan --model orcarouter --contexts-k 1,4 --max-output-tokens 256 --json` returned `PLAN_ONLY_ACK_REQUIRED`, concurrency 1, repeat 1, contexts [1,4], output cap 256, no inference, no mutation. This **matches the prior narrowly approved one-shot active MTP0 trial**. The previous `measurements history` contained only the 128-token old benchmark plus inventory, not a saved 256-token result, but unsaved attempts remain possible. Before any execution, an operator must establish that no other attempt used the one-shot approval and revalidate exact live ID/API/Docker from the active host. Only `benchmark-execute` with the exact `I_ACCEPT_ACTIVE_MODEL_INFERENCE` ack causes a bounded real inference workload, not `benchmark-plan`. Do not auto-retry or change the live service.

The GitHub feature branch advanced by documentation to `69a6c156ad2b88966c19bda72661bd1a0e208f05` before this update; local DGX source remains the earlier clean `17ebc7f`. There is no need to force a docs-only pull solely to perform the originally source-tested bounded workload. Do not claim new-HEAD Actions CI, PLE RSS, port/GPU exclusivity, MTP2 or production acceptance.

**Status:** `P5_MTP0_256_PLAN_AND_SERVICE_PREFLIGHT_PASS / P5_LIVE_INFERENCE_NOT_EXECUTED_BY_PLAN / DOCKER_FULL_ID_NOT_IN_STATUS_OUTPUT / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---

## 2026-11-19 KST / 2026-11-18 UTC — operator four-suite CPU regression + measurement history receipt

The operator returned full stdout for the four targeted CPU suites previously requested. **All 65 selected tests passed with exit code zero**: `test_p5_readonly_attribution_cpu.py` **7/7** (`P5_ATTRIBUTION_CPU_RC=0`), `test_p5d_p6e_cpu.py` **19/19** (`P5D_P6E_CPU_RC=0`), `test_p5_resource_diagnostics_cpu.py` **16/16** (`P5_RESOURCE_CPU_RC=0`), and `test_model_measurements_cpu.py` **23/23** (`P5_MEASUREMENT_CPU_RC=0`). These were run on the DGX host's Python environment by the operator, but the shared stdout **does not include the preceding `git rev-parse HEAD` / clean worktree check**, so attribution to exact source SHA `17ebc7f7...` remains **UNVERIFIED**. This is targeted CPU PASS, **not** full-repo CPU, GitHub Actions CI, GPU provenance, or production acceptance.

The operator also ran the read-only `operations measurements history --model orcarouter --json` query. It returned `READ_ONLY_HISTORY`, `count=2`, `inference_executed=false`, `service_mutated=false`:

| Local saved record | Git SHA recorded in receipt | Outcome |
| --- | --- | --- |
| 2026-11-18T10:27:35Z `benchmark-execute` | `2cb426f8346024267f3b361fe23cc0eaa477964b` | MTP0 1K/4K **128 completion tokens each**, `COLLECTED_UNQUALIFIED`; TTFT/TTFC/TPS null; 8K skipped |
| 2026-11-11T21:12:57Z `inventory` | `5a48e9ca417b939b1cc51b2933c3086472033b6a` | `READ_ONLY_PARTIAL`; idle resource/config evidence, not inference |

**No 1K/4K 256-output-token benchmark receipt is present in these two saved history records.** This narrows the duplicate-execution check but **cannot exclude an unsaved or external manual run**. The previous single-use approval is not an authorization to retry without checking for other execution evidence and exact current Docker/API/model identity. This assistant did not run a live benchmark or inspect private DGX files directly.

Continue with (1) exact `git rev-parse HEAD` and `git status --porcelain` receipt, (2) source-SHA-bound repeat of CPU tests **only if needed** (no inference), (3) new-HEAD CI investigation, and (4) controlled review of one-shot 256-token approval after checking for any unsaved execution. Docker NAT port ownership, independent PLE RSS, P6-E production Journal/executor, P7/P8 and production remain blocked. Historical 128-token and P3/P4 evidence is retained.

**State:** `P5_TARGETED_CPU_65_PASS_SHA_UNBOUND / P5_HISTORY_2_RECORDS_NO_256_RECEIPT / CI_UNVERIFIED / P5_D_NAT_PLE_NOT_AUTHENTICATED / PRODUCTION_BLOCKED`.

---

## 2026-11-18 source-only follow-up — NAT publishing and PLE smaps attribution (not DGX verified)

**GitHub source changes (Draft PR #1, not merged):** `scripts/manager/p5_readonly_attribution.py` adds an isolated, non-mutating Docker `HostConfig.PortBindings` ↔ `NetworkSettings.Ports` port-8000 declaration reviewer and a pure per-PID `/proc/<pid>/smaps` file-mapping RSS/PSS parser. `process_ownership.ownership_review` now includes `port_publication`; when both Docker declarations contradict it adds `DOCKER_PUBLISHED_8000_DECLARATION_MISMATCH`. These fields **do not** authorize a host-port owner, NAT datapath, GPU exclusivity, service release, restart or any P6 transition. A matching bridge declaration is only `DOCKER_DECLARATION_CONSISTENT_NOT_HOST_VERIFIED`; an absent host listener still yields the existing `PORT_8000_HOST_LISTENER_PID_UNAVAILABLE_OR_NAT` and RC3.

The PLE helper is **source-only**: it parses exact caller-supplied file paths for *one* process and reports `mapped_rss_bytes` / `mapped_pss_bytes`, while retaining `checkpoint_paths_authenticated=false`, `pid_container_membership_authenticated=false` and `ple_unique_resident_bytes=null`. It does **not** read live smaps or authenticate raw text provenance, checkpoint revisions, Docker namespace identity, mapping file inode, all workers or unique physical residency. It must not populate the existing `ple_resident_bytes` metric. A bounded read-only capture with exact pinned paths, independent PID/Docker identity before/after and multi-worker coverage still needs separate design/verification.

**CPU evidence:** seven synthetic tests in `tests/test_p5_readonly_attribution_cpu.py` passed in an isolated local Python module copy; Git blob SHA matches the committed helper/test bytes. This is **not** repository-wide regression, GitHub Actions CI, or DGX execution. Exact repo test and CI remain pending. No new 256-output-token inference receipt was available to this GitHub session; check `./wizard.sh operations measurements history --model orcarouter --json` **read-only** on DGX before any consideration of the previously approved single-use live benchmark. Do not auto-rerun.

**CI investigation:** one CPU workflow file exists on the feature branch, path filters include `handoff/**`, `scripts/manager/**` and `tests/test_p5_*_cpu.py`; default `main` did not expose `.github/workflows` via the contents API. The repository Actions runs feed still ended with the historical 2026-11-11 SHA `8b118c8`, and the investigated prior HEAD `c1bd76b` had zero runs/check-status entries. This is a **possible workflow registration/default-branch blocker**, not a verified causal diagnosis or CI PASS. Do not change `main`, merge PR #1 or enable production just to force CI.

**Carry-forward status:** `P5_D_NAT_DECLARATION_SOURCE_ONLY` / `PLE_SMAPS_PARSER_SOURCE_ONLY` / `P5_MTP0_256_EVIDENCE_PENDING` / `CI_UNVERIFIED` / `PRODUCTION_BLOCKED`.

---

## 2026-11-18 12:13Z operator P5-D ownership, inventory and idle resource receipts — executed read-only

**Latest operator-host evidence** (supersedes only "P5-D follow-up read-only pending" and does **not** imply the separate approved 256-token inference was run): the user executed `ownership-capture --model orcarouter --json`, `measurements inventory --model orcarouter --summary-only --json`, and `resources snapshot --model orcarouter --summary-only --json` at the existing DGX. The inventory receipt bound to git SHA `7509a4ec095005418d9974bac07542be7def884e` and timestamp `2026-11-18T12:13:12.345679+00:00`; the idle resource snapshot is `2026-11-18T12:13:14.332388+00:00`. These are user-shared stdout receipts, **not** cryptographically independent acceptance.

| Read-only evidence | Observed | Interpretation |
| --- | --- | --- |
| P5-D `ownership-capture` | `BLOCKED_PARTIAL_PROCESS_EVIDENCE`, `P5_D_RC=3`, **sole issue** `PORT_8000_HOST_LISTENER_PID_UNAVAILABLE_OR_NAT` | Correctly fail-closed; **not proof of service outage** |
| Docker identity | Container `qwen38-orcarouter-qsa62318-lmhead-v3`, full ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`, init PID **4016083**, `docker_identity_match=true` | Current observed Docker identity matched; PID is a transient observation, **not an authorization** |
| P5-D Docker/GPU PID relation | Docker host PIDs `{4016083,4016529,4016530}`; GPU compute PID `{4016530}`; `gpu_pid_subset_of_container=true` | Consistent process subsets; **not independent GPU exclusivity**, and **not proof of host port owner** |
| Host port process | `host_port_8000_listener_pids=[]`, `host_port_pid_to_container_verified=false` | NAT, docker-proxy differences or host inspection privilege can explain missing listener PID; leave port-process ownership `false` |
| Inventory | `READ_ONLY_PARTIAL`, `P5_INVENTORY_RC=0`; observed runtime flags `dtype=bfloat16`, `enforce-eager`, `gpu-memory-utilization=0.7`, `kv-cache-dtype=bfloat16`, `max-model-len=8192`, `max-num-seqs=1`; `VLLM_PLE_MMAP=1`, `VLLM_PLE_MMAP_PREWARM=0` | Reported live configuration for this container; recipe's `runtime_settings_proven=false` remains a distinction from fully qualified runtime |
| KV cache | Runtime-log reported available **9.83 GiB**, capacity **197,352 tokens** | Logged capacity, not independently measured GPU memory or free context |
| Memory | cgroup `memory.current=24586199040 B` (approx **22.90 GiB**), `memory.peak=39753752576 B` (approx **37.03 GiB**), cgroup swap **0 B** | Peak is cumulative cgroup high-water mark, not proof that the new 12:13Z idle snapshot reached that peak |
| PLE residency | Declared `102400491520 B` (**95.37 GiB**) mmap, `DECLARED_NOT_RESIDENT`; `ple_resident_bytes=null`, process RSS/PSS `null` | PLE-file-specific residency and true process memory remain **unobserved**; do not equate declared file size to RSS |
| Single idle snapshot | `OBSERVED_PARTIAL`, `P5_RESOURCE_RC=0`, GPU utilization **0%**, temperature **35°C**, power **9.83W**, host MemAvailable **31981281280 B**, advisory thresholds uncalibrated, no service mutation | A one-sample idle observation, **not a live performance interval or benchmark acceptance** |

P5-D independently verifies neither the GPU's actual kernel allocation exclusivity nor host-port-to-container ownership. Previous 2026-11-12 P5-D was also partial with missing :8000 host listener PID; the new 2026-11-18 receipt **reproduces the expected NAT/host-listener limitation**, not a demonstrated new failure. Do not issue automatic service restarts, privileged host rewiring, NAT rules changes or sudo attempts as a workaround. No model load, live inference, deletion, operating Journal write, or PR merge is authorized or evidenced by these three read-only commands.

**Remaining separate authorization:** the previously approved one-shot **1K/4K, max 256 output tokens** active MTP0 timing remeasurement **has not been supplied** in this attachment. The corrected `delta.reasoning` parser has CPU PASS at 7509a4e, but **new loaded TTFT/TTFC/TPS are still unobserved**. The one-shot runbook remains in this document; it will require fresh service/API gate and approved bounded execution, and should not be automatically retried if already used on the DGX. The P5-D improvement path is separate, design/review a fail-closed **read-only** NAT-port attribution and **actual mapped PLE file-specific RSS** auditor; do not claim success before independent host evidence. CI still unverified, production blocked.

**Status:** `P5_D_READONLY_EXECUTED_PARTIAL_NAT / P5_RUNTIME_CONFIG_AND_KV_REPORTED / PLE_RSS_NOT_OBSERVED / P5_MTP0_256_TIMING_REMEASURE_PENDING_EVIDENCE / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---


## 2026-11-18 subsequent operator approval: MTP0 active-model timing remeasurement + read-only P5-D (execution pending)

**New explicit operator instruction:** "진행 승인" after the exact-SHA `7509a4ec095005418d9974bac07542be7def884e` operator CPU PASS (23/23 timing tests, P3-P5 selected CPU 6/6 RC0). This approval is interpreted narrowly: **one more** bounded inference measurement on the **already running** Orcarouter BF16PLE **MTP0** model with **1K/4K** targets, **256 maximum generated tokens per case**, repeat=1, concurrency=1, fixed localhost port 8000 and exact acknowledgment; plus read-only P5-D process ownership and resource inventory. Explicitly **NO** MTP2 activation, model switch, GPU model launch, Docker mutation, service stop/restart, CPU/cgroup/memory setting change, HF cleanup, operating Journal write, recovery, PR merge or production release. The benchmark itself cannot start or switch a model.

**Why 1K/4K and 256:** the prior 128-token 1K/4K inference saturated the completion budget with `finish_reason=length` and no visible content; the updated vLLM-0.32 SSE collector now reads `delta.reasoning` for reasoning TTFT. A 256-token output cap may improve the chance of visible answer content (TTFC), but does **not** guarantee it. 8K is omitted: active max_model_len=8192 cannot accommodate 8192 input plus output tokens.

**Execution environment limitation:** The GitHub connector can review and commit source but does not provide a DGX host shell. The approved live step is **NOT EXECUTED by the assistant**; an operator must run the following on the existing DGX. Avoid additional local scripts, persistent daemon tasks and auto-retries. `--save` writes a private *measurement* receipt in `~/.local/state/blazux-wizard/model-measurements/`, **not** the operating Journal.

### Fail-closed operator command — one-shot, no auto-retry

```bash
# Run on the DGX host. This HEREDOC creates no script on disk.
bash <<'P5_MTP0_APPROVED'
set -euo pipefail
cd ~/Workspace/llm/blazux-orcarouter

git pull --ff-only
test -z "$(git status --porcelain)" || {
  echo "BLOCKED: unclean source tree"; exit 3;
}
git merge-base --is-ancestor 7509a4ec095005418d9974bac07542be7def884e HEAD || {
  echo "BLOCKED: original tested SSE parser is not an ancestor"; exit 3;
}
git diff --quiet 7509a4ec095005418d9974bac07542be7def884e HEAD -- \
  scripts/manager/measurement_bench.py tests/test_model_measurements_cpu.py || {
  echo "BLOCKED: benchmark source differs from CPU-tested revision"; exit 3;
}
echo "P5_SOURCE_HEAD=$(git rev-parse HEAD)"

STATUS_JSON="$(./wizard.sh service manager status --json)"
printf '%s\n' "$STATUS_JSON" | python3 -c '
import json,sys
s=json.load(sys.stdin)
passed=(s.get("status")=="LIVE_P5_TRIAL_API_VERIFIED"
        and s.get("observed_model")=="orcarouter"
        and s.get("runtime_role")=="DEVELOPMENT_TRIAL"
        and s.get("p5_development_trial") is True
        and s.get("expected_served_id")=="qwen3.8-flash-next-orca-uncensored-bf16"
        and s.get("host_port")==8000 and s.get("issues")==[])
print("P5_PREFLIGHT_PASS" if passed else "P5_PREFLIGHT_BLOCKED")
if not passed:
    print("status:",s.get("status"),"issues:",s.get("issues"))
sys.exit(0 if passed else 3)
'

./wizard.sh operations measurements benchmark-plan \
  --model orcarouter --contexts-k 1,4 --max-output-tokens 256 --json

# Actual inference: approved active model only; sends two bounded requests.
# Summarized stdout includes all per-context metrics and private receipt path.
./wizard.sh operations measurements benchmark-execute \
  --model orcarouter --contexts-k 1,4 --max-output-tokens 256 \
  --ack-live-inference I_ACCEPT_ACTIVE_MODEL_INFERENCE \
  --save --summary-only --json
echo "P5_MTP0_REMEASUREMENT_COMPLETED"
P5_MTP0_APPROVED
```

The script stops before live inference if the active model/served ID/port, worktree, or inspected source revision differs. The CLI has an additional independent service/API/Docker identity gate; on failure it returns `BLOCKED` and does not generate tokens. The source guard checks only the benchmark code and its CPU tests; it cannot substitute for current host attestation or independent CI.

### P5-D and PLE residency: separately approved READ-ONLY observations

```bash
cd ~/Workspace/llm/blazux-orcarouter
./wizard.sh operations generic ownership-capture --model orcarouter --json
echo "P5_D_OWNERSHIP_RC=$?"
./wizard.sh operations measurements inventory --model orcarouter --summary-only --json
echo "P5_INVENTORY_RC=$?"
./wizard.sh operations resources snapshot --model orcarouter --json
echo "P5_RESOURCE_RC=$?"
```

The P5-D helper uses bounded `docker inspect`, `docker top`, `ss -H -ltnp sport = :8000`, and `nvidia-smi --query-compute-apps=pid`; it neither modifies Docker nor executes inference. A `BLOCKED_PARTIAL_PROCESS_EVIDENCE` or no `ss` host listener PID **may be normal Docker NAT**, not proof of service failure. Even a consistent GPU Docker PID subset is **not independent GPU exclusivity or authenticated port ownership**. Source snapshots do not establish GPU kernel ownership, model launch authorization or operating release.

The current `resource_diagnostics.snapshot` reports `ple_specific_resident_bytes=null` and `process_smaps_rollup_bytes` may also be null, because process-wide `smaps_rollup` cannot identify PLE file residency. **Do not substitute declared ~95.37 GiB PLE mmap bytes, cgroup memory, host cache, or GB10 GPU shared memory for PLE-specific RSS.** No privileged `/proc/<pid>/smaps` scan, kernel changes, memory prewarm or additional model load is approved in these instructions; a separately designed, bounded, file-path-and-container-ID-verified read-only PLE mapping auditor would be required for real PLE-specific attribution.

**Expected classification:** `P5_MTP0_256_INFERENCE_APPROVED_NOT_YET_EXECUTED` until a matching operator receipt is provided. If TTFT/TPS become numeric, record the actual values and `stream_metrics_quality`; if only reasoning is generated, `MEASURED_REASONING_ONLY` and `TTFC=null` remain valid but **not a visible-answer latency result**. P5 independent GPU/port owner, PLE RSS, interval peak, MTP2, CI and production release remain separately gated. This scope-specific approval expires after the single bounded execution, not an open-ended authorization to replay.

---


## 2026-11-18 operator-approved Orcarouter MTP0 loaded benchmark — measured usage, SSE timing defect

**Operator-supplied actual DGX execution** at `2cb426f8346024267f3b361fe23cc0eaa477964b` (repository document/source HEAD at observation), UTC **2026-11-18 10:27:35–10:27:50**, in existing `qwen38-orcarouter-qsa62318-lmhead-v3` container ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`, image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`, host PID reported `4016083`. Preflight `P5_BENCHMARK_PREFLIGHT_PASS` and `benchmark-plan` returned `PLAN_ONLY_ACK_REQUIRED`. The operator then used the **explicit inference-only ACK** and `--save` for **one 1K/4K/8K bounded set, concurrency=1, repeat=1, output cap=128, active service only**. The benchmark JSON reports `inference_executed=true`, `service_mutated=false`, `container_id_continuous=true`, `status=COLLECTED_UNQUALIFIED`, `benchmark_verified=false`, `production_released=false`. A private local evidence receipt was created: `orcarouter--20261118T102750567863Z--aa19648b06f8.json` under the user model-measurements state directory. Operator terminal's ending `P5_BENCHMARK_RC=0+` has an extraneous pasted `+`, so treat it as a shell-log formatting anomaly, not a separate numeric result. Do not claim independent cryptographic proof from operator-supplied JSON.

### Actual bounded observations — **not full performance acceptance**

| Target | Tokenizer prompt | SSE prompt usage | SSE completion | End-to-end | TTFT | TTFC | after-first TPS | Result |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- | --- |
| 1K | 1021 | 1072 | 128 | **6.45791 s** | `null` | `null` | `null` | `MEASURED` / SSE DONE |
| 4K | 4081 | 4132 | 128 | **7.49535 s** | `null` | `null` | `null` | `MEASURED` / SSE DONE |
| 8K | — | — | — | — | — | — | — | `SKIPPED_ACTIVE_CONTEXT_LIMIT` |

Active API advertised `max_model_len=8192`; requested 8192 input tokens +128 output budget exceeds that bound, so skipping 8K is **expected, not a failing inference**. Both completed cases have `finish_reason=length`, `visible_characters=0`, `stream_done_observed=true`, and complete server usage. **Neither case establishes TTFT, TTFC or true post-first generation TPS**. Dividing completion count by total time is an end-to-end rate, NOT this metric; do not substitute it.

Two bounded before/after read-only resource snapshots (not a continuous interval or peak) reported: GPU utilization **0% to 71%**, GPU temperature **34 to 39 °C**, GPU power **9.87 to 20.41 W**; cgroup `memory.current` **24,557,510,656 to 24,587,689,984 B** (approximately 22.871 to 22.899 GiB, +28.8 MiB), host available memory approximately **29.779 to 29.796 GiB**; cgroup `memory.events.oom=0` and `oom_kill=0` at both snapshots; container swap `0` and host swap unchanged. These samples do **not** certify zero OOM through all unsampled intervals, peak memory, or exclusive GPU allocation. `ple_declared_mmap_bytes=102400491520` (**95.37 GiB declared file mapping**) is **not** PLE RSS or actually-resident GPU memory; `ple_specific_resident_bytes=null`, process RSS/PSS and GPU UMA memory used were `null`, independent port owner proof remains unresolved.

### Root cause strongly indicated by exact vLLM 0.32.0 API contract

The **existing source** `scripts/manager/measurement_bench.py::_stream_chat` reads `delta.reasoning_content` and `delta.content`, but the **official vLLM v0.32.0 reasoning streaming API** documents `delta.reasoning` for thinking tokens: https://docs.vllm.ai/en/v0.32.0/features/reasoning_outputs/ . This precise field mismatch can yield `TTFT=null` and `TPS=null` with nonzero `completion_tokens` if all streamed tokens are reasoning. The captured log does NOT contain individual SSE chunks, so precise per-chunk cause is **high-confidence hypothesis, not independently observed live proof**. Separately, both cases exhausted the output cap with `finish_reason=length`; **TTFC may legitimately remain null** if no visible answer content was generated even after parsing is fixed.

**Post-observation SOURCE ONLY patch, no additional live inference:** the metrics parser now supports vLLM `delta.reasoning` plus legacy `delta.reasoning_content`, counts reasoning delta events/chars but never saves content, and includes bounded `stream_metrics_quality` with reasoning-only vs usage-only classifications. Its post-first TPS excludes the first generated token from the numerator; server completion usage includes reasoning tokens. Benchmark cases may now be `MEASURED_REASONING_ONLY` or `INCOMPLETE_METRICS`, rather than treating an SSE usage-only record as complete by default. Summary counts report TTFT/TTFC/TPS availability and reasoning-only cases, without promoting benchmark verification, runtime release, model switching or operation privileges. Added targeted source-only tests to `tests/test_model_measurements_cpu.py` for 0.32 reasoning-only, mixed reasoning/content, usage-only missing deltas, and evidence summary classification.

**The SOURCE PATCH and NEW CPU tests have not yet been executed on DGX or in GitHub Actions.** Historical P5 152/152 source PASS is bound to **`8ec6bc2`**, before this new benchmark parser patch. The exact benchmark was executed at **`2cb426f`**, also before this patch; its `null` timings must not be silently backfilled. GitHub Actions issue remains unqualified and PR #1 stays Draft/Open. Do not rerun inference automatically: the operator's preceding one-shot approval was for the completed bounded trial only. A fresh, separately scoped operator authorization is needed for another loaded test (and any larger token cap such as 256); no model stop/switch, deletion, Journal, auto-recovery or PR merge is authorized.

**Current status:** `P5_MTP0_LIVE_INFERENCE_EXECUTED_2_OF_3 / SSE_TIMINGS_NOT_OBSERVED / P5_SSE_032_SOURCE_FIX_CPU_PENDING / P5_D_OWNERSHIP_AND_PLE_RSS_PENDING / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---


## 2026-11-18 P3–P5 operator CPU follow-up — 8ec6bc2, selected scope PASS

**Latest SHA-bound operator execution receipt (supersedes prior 8b8f5a0 failures and "new-source CPU pending" statements, not the CI gate):** `git pull --ff-only` advanced the operator's local development checkout to **`8ec6bc2f148cf77bf0ed6e9ce0d54a91d1baf569`**; `git status --short` returned no tracked/untracked changes. The operator subsequently ran all four approved source-only commands:

| Command | Operator result | Process RC |
| --- | --- | --- |
| `python3 -B -m unittest discover -s tests -p 'test_p5_document_integrity_cpu.py' -v` | **8/8 PASS** | `P5_DOC_RC=0` |
| `python3 -B -m unittest discover -s tests -p 'test_p3_p5_closeout_cpu.py' -v` | **11/11 PASS** | `CLOSEOUT_TEST_RC=0` |
| `python3 -B -m unittest discover -s tests -p 'test_p5_*_cpu.py' -v` | **152/152 PASS** | `P5_CPU_RC=0` |
| `python3 -B -m scripts.manager.p3_p5_closeout --cpu-only --json` | `CPU_SELECTED_PASS_NOT_CI`, **six of six tasks `accepted=true`**, `receipts_collected=6` | `P3_P5_CPU_RC=0` |

The combined source CPU receipt independently reports `source_head=8ec6bc2f148cf77bf0ed6e9ce0d54a91d1baf569`, `clean_before_run=true`, `source_cpu_selected_pass=true`, P3-D~G CPU contract `CPU_ONLY_SOURCE_PASS_NOT_DGX`, P4-A **9/9 PASS**, P4-B/C **13/13 PASS**, P5 source CPU **152/152 PASS** (inner unittest RC0, `failed_cases=[]`), P5 model measurements **18/18 PASS**, P5 benchmark session **8/8 PASS**. The directly executed 8-document and 11-closeout tests are **part of the wider source verification scope** and must not be presented as disjoint additional tests. Earlier test harness faults (local historical P3 reports incorrectly included in document inventory; fully qualified module names not recognized by fake subprocess runner) are now **resolved at the tested SHA**. The ten private P3 operating report JSON files have not been deleted or modified.

**Acceptance boundary:** This is **operator-supplied, clean SHA-bound CPU/Fake-DGX selected-scope PASS**, not GitHub Actions or independently authenticated real DGX production acceptance. The receipt still has `actual_p3_p4_p5_complete=false`, `ci_verified=false`, `production_released=false`, `operations_enabled=false`, `inference_executed=false`, `real_model_switch_executed=false`, `live_deletion_executed=false`, and `operating_journal_written=false`. Existing historical P3 A/B/C/G live switch and P4-A/B/C read-only receipts retain their original dated scope. The earlier `--read-only` collection at **8b8f5a0** returned **5/5 collected** but `READ_ONLY_COLLECTED_WITH_GAPS`, `RC=3`: P3-D/G process/API/port ownership and canonical Flash reinstall not qualified, current P4-A inventory partial, P5 inventory partial and P5 GPU plan intentionally blocked. **No updated read-only run was supplied** in this latest transcript. P5 loaded TTFT/TTFC/TPS, validated benchmark resource interval, PLE file-specific residency, independent GPU/host port owner proof, MTP2 and production promotion remain pending separate approval and evidence.

GitHub Actions still reports **1640 runs**, latest successful workflow run tied to 2026-11-11 SHA `8b118c8`. Current source SHA has **no CI success receipt**, and PR #1 remains Draft/Open/unmerged. Documentation-only follow-up commits do not retroactively make the tested SHA's selected CPU receipt a CI run, nor does the latest test result cover those future commits. **Decision:** `P3_P4_P5_SELECTED_CPU_PASS_AT_8EC6BC2 / HISTORIC_P3_SWITCH_CLOSED / HISTORIC_P4_READONLY_CLOSED / CURRENT_READONLY_GAPS / P5_LIVE_ACCEPTANCE_PENDING / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---


## 2026-11-18 operator exact-SHA regression: 8b8f5a0, localized two test-harness bugs

**Operator-supplied terminal receipt** at `8b8f5a0132e8b1f27f9ec4b1cd53c5e82c7f1aea`; `git pull --ff-only` fast-forwarded from `9a79c8d` and `git status --short` showed no changes.

| Operator command/result | Observed |
| --- | --- |
| `test_p5_document_integrity_cpu.py` | `Ran 6 tests`, **1 FAIL**, RC1: `test_full_inventory_resolves_every_original_document` |
| `test_p5_*_cpu.py` | `Ran 150 tests`, **1 FAIL**, RC1: same document inventory test; other 149 PASS |
| `test_p3_p5_closeout_cpu.py` | `Ran 11 tests`, **6 FAIL**, RC1: each fake command dispatch did not recognize `scripts.manager.p3_dg_acceptance` |
| `p3_p5_closeout --cpu-only` | `INCOMPLETE_OR_BLOCKED`, RC3, source-P3 CPU/P4-A 9/P4-BC 13/measurements 18/session 8 passed; P5 source failed on the one document inventory test |
| `p3_p5_closeout --read-only` | `READ_ONLY_COLLECTED_WITH_GAPS`, RC3; all **5/5 receipts collected**, not all accepted |

The P5 document inventory failure identifies **ten** local files under `reports/transitions/flash-next--to--27b/p3-c-operator-*.json`. These are operator transition receipts physically on the host, not members of the repository's frozen source document inventory, and their presence does not justify deleting or editing them. The old test scanned `ROOT.rglob("*")` and therefore unintentionally included those local files. **Fix:** enumerate `git ls-files --cached --full-name -z` with bounded output and safety/path checks; keep the immutable **169 tracked historical files + three known later baseline files + five explicitly approved new documents** equality requirement. A new isolated temp-directory test verifies a real on-disk but unindexed private receipt is excluded; another test rejects unsafe paths. No private reports touched.

The six P3–P5 integration unit failures have the same mock fixture cause: tests matched bare `"p3_dg_acceptance" in cmd` while the real command array contains the **full element** `"scripts.manager.p3_dg_acceptance"`. Corrected exact module command elements for P3, P4, P5, and model measurements; kept all safety/denial assertions. This **does not** weaken CPU acceptance or admit blocked outcomes.

The operator's read-only record is **more informative, not an operational PASS**:
- P3-D `BLOCKED`: `ACTIVE_API_IDENTITY_NOT_VERIFIED`, `ACTIVE_DOCKER_CONTAINER_UNKNOWN`, `DOCKER_GPU_EXCLUSIVITY_NOT_VERIFIED`, `DOCKER_HOST_8000_OWNER_NOT_EXCLUSIVE`, `HOST_PORT_PROCESS_PID_UNAVAILABLE`. P3-G `BLOCKED`: `SOURCE_ACTIVE_MODEL_UNKNOWN_OR_UNSUPPORTED`, `SOURCE_API_AND_MANIFEST_UNVERIFIED`. Historical P3 transfer was between NVIDIA Flash and 27B; with a different active service this read-only runner cannot validate the previous P3 configuration and must fail closed. No service outage has been established.
- P3-E `DRAFT_REVIEW_REQUIRED`: `FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED`; P3-F `SOURCE_CPU_PASS_NOT_RELEASED`. These keep P8 and production gates closed.
- P4-B+C `READ_ONLY_DRY_RUN_BLOCKED`: P4-A `READ_ONLY_INVENTORY_PARTIAL`, `CURRENT_P4_A_COMPLETE_EVIDENCE_REQUIRED`, `P4_B_COMPLETE_REVIEW_REQUIRED`. This is a current-snapshot acceptance gap; earlier P4-A/B/C historical read-only PASS is not overwritten.
- P5 source-plan `BLOCKED` with `P5_GPU_ABI_AND_ROLLBACK_UNQUALIFIED` is **expected fail-closed**; model inventory `READ_ONLY_PARTIAL` and benchmark plan `PLAN_ONLY_ACK_REQUIRED` are not measured loaded-performance results.

**Post-receipt source commits are not yet covered by operator CPU reruns or CI.** The GitHub Actions zero-run issue remains unresolved. Next operator-side safe check: `python3 -B -m unittest discover -s tests -p 'test_p5_document_integrity_cpu.py' -v`, `... -p 'test_p5_*_cpu.py' -v`, `... -p 'test_p3_p5_closeout_cpu.py' -v`, then `python3 -B -m scripts.manager.p3_p5_closeout --cpu-only --json` on a new clean HEAD. Read-only retry is **not required** to validate these two test-harness fixes. Do not delete any private P3 reports, stop services, switch models, run inference, change operational Journal or merge PR #1.

**Decision:** `TESTED_8B8F_P5_149_OF_150 / TESTED_8B8F_CLOSEOUT_5_OF_11 / FIXED_TEST_HARNESS_SOURCE_CPU_PENDING / READONLY_GAPS_RETAINED / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---


## 2026-11-18 P3-P5 operator 9a79c8 integrated run receipt and source correction

### Operator CPU receipt — **partial, not PASS**

On a clean source checkout at `9a79c8df4240c99836b0b0cf54ec3a88003686c6`, the operator ran the new `p3_p5_closeout --cpu-only` collector: `INCOMPLETE_OR_BLOCKED`, shell `P3_P5_CPU_RC=3`. Individual tasks: P3-D~G CPU contract accepted `CPU_ONLY_SOURCE_PASS_NOT_DGX` RC0; P4-A **9/9 CPU PASS** RC0; P4-B/C **13/13 CPU PASS** RC0; **P5 source CPU FAIL RC3** with `P5_CPU_TESTS_FAILED`; P5 measurement **18/18 CPU PASS** RC0; P5 benchmark session **8/8 CPU PASS** RC0. No new-HEAD CI result exists. This transcript does not include the P5 inner `test_cases` / unittest `failure_details`, so it does not prove which individual test methods failed.

### Operator read-only receipt — blocked snapshot, not a service failure

The same source SHA and clean tree ran `p3_p5_closeout --read-only` and returned `INCOMPLETE_OR_BLOCKED`, shell `P3_P5_READONLY_RC=3`. P3 D/G stages were `BLOCKED`; P4-B+C status was `READ_ONLY_DRY_RUN_BLOCKED`, but the original collector incorrectly classified its valid fail-closed RC3 JSON as `INVALID_EXIT_OR_STATUS`. P5 static source plan `BLOCKED` RC3 is expected because launch/ABI/rollback authority is unavailable; P5 inventory `READ_ONLY_PARTIAL` is an actual partial observation; P5 benchmark `PLAN_ONLY_ACK_REQUIRED` is a valid *plan*, not live benchmark data. The original collector also showed `accepted=true` for a blocked P3 observational task because it conflated valid evidence collection with qualified acceptance. **None of these results establish a malfunction of the active inference service.** Historical P3 A/B/C/G successes and P4 read-only success remain historical receipts, not proof of the 2026-11-18 host state.

### Source-side investigation and corrections after the observed receipt — **not yet rerun**

GitHub tree at the **tested SHA** contained **177** document-like files under the frozen P5 audit criterion: the historical 169, original authorized additions `HANDOFF-DOCUMENT-AUDIT-FULL-P5`, `P5-P8-MODEL-AGNOSTIC-OPERATIONS`, `P5-D-P6-E-READ-ONLY-PROVENANCE-JOURNAL-V2`, **plus 5 newer scoped docs**: Actions no-run investigation, P3-P5 one-turn closeout, P6-E CPU CI follow-up, P6-E untrusted JSON ingest fence, and the operator CI Push probe. The old `test_p5_document_integrity_cpu.py` asserted exactly the original three additions, so its full-inventory equality **necessarily fails on the tested SHA**. Its additional checks assumed historical supersession markers stayed within the first 180 characters, while newer chronological handoff entries were prepended; static inspection also showed current primary/secondary documents still retain the original marker and adapter/scale references elsewhere. This is a **confirmed source-contract mismatch**, without claiming it was the sole cause of the failed P5 suite.

Source changes now:
- Extend the explicit allowed **incremental** file inventory with the five known new documents; keep the original 169/169 immutable-presence assertion, duplicate check, and repository-wide Markdown link check. Search historical supersession content in the entire document rather than treating one old heading's byte offset as the current-state authority. Add a test that the current P3-P5 evidence-scoped document explicitly remains non-authorizing.
- Distinguish true nonzero `unittest` exit (`P5_CPU_TESTS_FAILED`) from zero-exit verbose output mismatch (`P5_CPU_RESULT_PARSE_MISMATCH`), preserving strict fail-closed behavior. Add three synthetic tests covering fail, parse drift and pass; these tests themselves are **not** an actual P5 runner receipt.
- In the collector, preserve valid `RC3` blocked receipts with `collected=true`, **never `accepted=true`** for blocked P3/P4/P5; extract only bounded structured stage status/issues and P5 failed-test names/counts, not raw logs. Distinguish a clean read-only evidence collection with gaps (`READ_ONLY_COLLECTED_WITH_GAPS`, RC3) from unparseable/incomplete output. The always-partial P5 model inventory is explicitly a gap, not a benchmark PASS.
- Expand closeout unit guards from nine to eleven tests, add three P5 diagnostics tests, and register `tests/test_p5_*_cpu.py` in PR path filters. No DGX runtime executor, inference, model switch, Docker mutation, operating Journal write, automatic recovery, cache delete or PR merge was performed.

**Required verification:** at a newly pulled clean source SHA, run direct P5 CPU suite to preserve the actual unittest failure line if any; then rerun combined CPU and read-only collectors. A new `P5_CPU_TESTS_FAILED` proves at least one test method still fails; `P5_CPU_RESULT_PARSE_MISMATCH` distinguishes a suite output parser defect; `CPU_SELECTED_PASS_NOT_CI` must only follow genuine P3/P4/P5 selected CPU PASS. Read-only `WITH_GAPS` is a valid truthfulness result (RC3), not something to bypass. Existing Actions no-run remains unresolved. **No P3/P4/P5 live production acceptance is implied.**

**Current decision:** `TESTED_9A79_CPU_PARTIAL_P5_FAILED / TESTED_9A79_DGX_READONLY_BLOCKED / SOURCE_FIXES_UNVERIFIED / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---


## Verdict

**P3-A/B/C/G are already real-DGX historical PASS/CLOSED; P3-D read-only PASS; P3-E/F are completed only within source/host-read-only and CPU handoff.** P3-E canonical Flash reinstallation and new generalized transition release are not qualified and remain assigned to the separately gated P8 production lifecycle. Do not rerun previously successful operating transitions to manufacture a fresh P3 PASS.

**P4-A and P4-B/C are already real-DGX read-only PASS/CLOSED** with nine reviewed resource records, zero deletion candidates and zero approvals. Live deletion is **NOT_RUN / NOT_AUTHORIZED**, not a remaining mandatory action when storage is sufficient. Never infer reclaimable bytes from Docker category estimates.

**P5 Orcarouter v3 BF16PLE MTP0 real inference/API was observed as a DEVELOPMENT_TRIAL.** P5-C sequential correlation was collected. P5-D actual DGX observation on 2026-11-12 returned `BLOCKED_PARTIAL_PROCESS_EVIDENCE` because an independent host port-8000 listener PID was not available under Docker/NAT; Docker/GPU PID subsets were consistent. This **is not evidence of a failed service**. Fully qualified loaded TTFT/TTFC/TPS, calibrated context lengths, resource interval, file-specific PLE RSS, independent GPU/port ownership, MTP2 overlay and general production promotion are **NOT ACCEPTED**.

The selected P6-E-related CPU **45/45 PASS** was provided by the operator at source SHA `2f5240d` and does not cover newer P3–P5 closeout source, the full repository test suite or current-head Actions. GitHub Actions has no new runs after 2026-11-11; CI is `UNVERIFIED`. PR #1 stays Draft/Open/unmerged.

## New reusable source-safe collector

- `scripts/manager/p3_p5_closeout.py` only orchestrates established P3/P4/P5 read-only/CPU modules. It has **no** mode to enable inference, switch models, load GPU weights, delete cache, modify Docker, migrate operating Journal or trigger recovery.
- `--plan`: returns a non-authorizing plan without subprocess calls or filesystem writes.
- `--cpu-only`: P3-D/G source CPU runner, P4-A/P4-B+C regression files, P5 source CPU runner, and P5 measurements/session contract CPU regression files. Insists on actual test summary/zero return code; it cannot assert DGX or CI PASS.
- `--read-only`: P3-D/E/F/G read-only inspection, P4-A/B/C read-only inventory/rehearsal, P5 source plan, P5 model measurement inventory, and P5 bounded benchmark **plan**. P5 source plan intentionally returns status `BLOCKED`/code 3 because GPU trial authorization remains withheld; this is collected as an expected non-authorizing result, not falsely promoted to PASS.
- Optional `--read-only --with-p5-asset-hashes` invokes the existing heavier P5 read-only cache and donor shard audit. **Warning: this can read large checkpoint shards**, so schedule it as an explicit I/O operation, not as the default.
- `tests/test_p3_p5_closeout_cpu.py` adds nine mock CPU tests for plan-only, fake regression results, failure/dirty-tree denial, commands allowlist, invalid JSON and rejection of live flags. The workflow's Push/PR path filters and CPU job were updated. **These nine new tests and full CI remain unexecuted / unverified until a valid run receipt exists.**

### Operator execution on the existing development checkout (no live inference or service mutation)

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only
git rev-parse HEAD
python3 -B -m scripts.manager.p3_p5_closeout --plan --json
python3 -B -m scripts.manager.p3_p5_closeout --cpu-only --json
echo "P3_P5_CPU_RC=$?"
python3 -B -m scripts.manager.p3_p5_closeout --read-only --json
echo "P3_P5_READONLY_RC=$?"
```

Review the JSON `tasks`, `source_head`, `clean_before_run` and `status`; an overall `READ_ONLY_COLLECTED_NOT_RELEASED` confirms **collection**, never end-to-end acceptance. No automatic report file is written; redirect outputs locally only if the operator chooses and redact sensitive metadata before sharing. `--cpu-only` may take multiple minutes because it executes the existing P3/P5 suites; `--read-only` also repeats the P3 CPU runner. Use `--plan` first when resources are uncertain.

### P5 loaded workload — separate operator action and consent

```bash
./wizard.sh service manager status --json
./wizard.sh operations measurements inventory --model orcarouter --json
./wizard.sh operations measurements benchmark-plan --model orcarouter --contexts-k 1,4,8 --max-output-tokens 128 --json
```

The above is read-only / planning. **Only after the operator separately approves bounded inference and confirms Orcarouter v3 is already the active model**, the existing opt-in command may collect (but never automatically qualify) loaded SSE metrics:

```bash
./wizard.sh operations measurements benchmark-execute --model orcarouter --contexts-k 1,4,8 --max-output-tokens 128 --ack-live-inference I_ACCEPT_ACTIVE_MODEL_INFERENCE --save --json
```

The benchmark executor never starts or switches a model; it requires exact live API ID and full Docker container identity. It may skip cases above the observed active model context limit and does not itself provide independently authenticated P5-D ownership or a synchronized P5-B resource session. Approval for inference is **not** approval for stop/switch, downtime, Journal migration, recovery, deletion or production release. PLE RSS needs file-specific measurements rather than engine log inferred KV capacity.

## Acceptance boundary and next action

| Area | Historical evidence | Accepted here | Still blocked |
| --- | --- | --- | --- |
| P3 | A/B/C/G real one-off PASS, D read-only PASS, E metadata / F 168 CPU | Historical scope preserved; P3 source-only closeout tooling | Canonical Flash reinstall, new generalized executor, full Wizard release; defer to P8 |
| P4 | A host inventory + B/C one-shot dry-run PASS | Read-only storage scope **CLOSED** | Deletion only if capacity mandates it and exact resource separately approved |
| P5 | Orcarouter v3 MTP0 inference; C correlation; D partial PID | Source-only prep and operator read-only/CPU collector | Loaded model session, true GPU/port ownership, PLE RSS, Tools/Vision, MTP2, promotion |
| CI | Last workflow success 2026-11-11 | New test registered in YAML | New source-head Actions job/result not generated |

P5 cannot be called `REAL_ACCEPTANCE_PASS` based on this source-only change. P6-E independent authority, P7 cross-component checks and P8 recovery/release continue blocked as documented. P1/2 accepted backend baseline, vLLM 0.32.0, ONE_ACTIVE_MODEL_ONLY, port 8000, OpenWebUI/Portainer and every existing cache/image/PLE asset are preserved.

**Decision:** `P3_HISTORICAL_SWITCH_CLOSED_P8_REINSTALL_PENDING / P4_READ_ONLY_CLOSED_NO_DELETE / P5_DEVELOPMENT_TRIAL_LOADED_PENDING / NEW_SOURCE_CPU_PENDING / CI_UNVERIFIED / PRODUCTION_BLOCKED`.
