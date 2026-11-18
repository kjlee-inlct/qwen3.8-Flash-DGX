# P5 Orcarouter MTP0 — one-shot visible-TTFC GPU measurement (2026-11-19)

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
