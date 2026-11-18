# P5 Orcarouter MTP0 — one-shot visible-TTFC GPU measurement (2026-11-19)

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
