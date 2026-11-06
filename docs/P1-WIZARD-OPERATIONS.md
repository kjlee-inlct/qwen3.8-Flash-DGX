## 2026-11-07 — Actual POST-B Flash-Next Verify/Benchmark PASS; user-facing Wizard UX update

**Supersedes all older claims below that POST-B P1 GPU work is NOT_RUN.** The operator supplied an actual DGX evidence archive with post-B Verify **PASS** (baseline and extended: completions, chat, tools, vision) at 2026-11-06T23:26:27Z and a separately SHA-approved Benchmark **PASS** at 2026-11-06T23:30:31Z: 3 requests, max 64 tokens, seed 1234, concurrency 1, throughput **37.9527 tokens/sec**, TTFT p50/p95 **1.384594/1.779602 sec**, latency p50/p95 **1.724560/1.813754 sec**, 192 generated tokens. Original immutable receipt names: `20261106T232627Z-82b4aebbdd13.json`, `20261106T233031Z-66af25d31aab.json` in the OLD `~/.local/state/blazux-wizard/p1/` path. Both latest post-B doctor/inventory diagnostics were PASS for expected own-container rc3 collision. Do not repeat or modify these operations without another explicit approval. **P3-C remains separately NOT_AUTHORIZED.**

**New UX after CI and operator fast-forward pull:** `./wizard.sh` → `1` Select / run model → `1` NVIDIA Flash-Next → `2` All model actions → `6` Verify or `7` Benchmark → `y` → **review named-model plan and type current SHA at `Type exactly [<current plan_id>] (Enter cancels):`**. No duplicated P1 action selection. After execution, Verify feature statuses and Benchmark metrics are shown without opening JSON manually. Do not assume the source UX change has been revalidated on DGX until the operator actually tests it.

**New evidence default:** `<repo>/reports/models/qwen3.8-flash-next/<UTC>-<unique>.json` (0600, append-only, ignored by Git); `--evidence-dir` remains available. Existing legacy receipts are never moved or rewritten, and P3-C evidence gate reads both paths and selects the actual newest finished timestamp. P2/P3 state/locks remain at their original locations pending reviewed migration. See [full contract](WIZARD-OPERATOR-UX-EVIDENCE-CONTRACT.md).

---

> **2026-11-07 POST-B P1 SCOPE:** After successful actual P3-B 27B→Flash return, the operator's `p1-post-download.sh --inspect-only` report `/home/inlc/blazux-p1-reports/20261106T224010Z-d2095867/result.json` confirms original Flash/Hybrid assets, API model identity, clean branch and Verify/Benchmark plan READY. Its `actions.*=BLOCKED/reason=inspection_only` means **NOT_RUN**, not a failed GPU check. Newly tracked `bash scripts/temporary/p1-post-b-audit.sh` does read-only doctor/inventory raw JSON rc3 reconciliation and persists append-only private 0600 diagnostics after verifying actual B receipt. It never runs actual Verify or Benchmark, does not approve P3-C and does not affect vLLM 0.32 or API :8000. Distinct fresh Wizard plan IDs and explicit operator approvals remain mandatory for each actual P1 GPU action. Existing original P1 numerics are pre-B history, not valid post-B samples.

---

# P1 NVIDIA Flash-Next Wizard operator runbook

Source commit: c625a49276272e90d19ab6367f580a0230754890. Two GitHub Actions jobs PASS, 80/80 CPU tests per job. Actual DGX Wizard GPU/API/benchmark remains NOT_RUN.

Target: nvidia/Qwen3.8-Flash-Next-NVFP4, vLLM 0.32.0, Hybrid / YaRN / MTP2, host API :8000/v1, model ID qwen3.8-flash-next, container qwen38-flash.

## Current DGX evidence (time bounded)

2026-11-05 user-supplied DGX log: vLLM 0.32 Docker image build finished; model download 9/25 files (36%) at last visible line. OpenWebUI and Portainer remained running; port 8000 was free at the earlier scan. The operator entered flash setup, serve, wait and test sequentially, so subsequent commands may run without assistant action. Do not modify the worktree, restart the process, repeat setup, or replace an already running container before the original chain ends. These are time-bounded facts, not proof of full download or API readiness.

Docker image build succeeded in uploaded terminal output: sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137. Download was still in progress at 36% in the final visible line. This is not a complete checkpoint, Hybrid preparation or API proof. Do not compete with the operator-owned shell process. Any queued serve/wait/test may execute as soon as setup completes.

## Combined post-download operator command

To avoid pasting three separate command blocks, use the tracked temporary bundle
after GitHub code/CI is confirmed and the operator's original setup/serve/wait/test
chain has **fully exited**:

```bash
cd ~/Workspace/llm/blazux-orcarouter
git fetch origin
git switch feature/recipe-wizard-handoff
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p1-post-download.sh
```

Default interactive TTY runs phase 1 inspection, asks for a separate **full current
plan ID** to authorize P1 verify and benchmark only when READY, then writes
`~/blazux-p1-reports/<UTC>-<id>/result.json`. If you want **read-only only**,
run `bash scripts/temporary/p1-post-download.sh --inspect-only`. No TTY means
no automatic approval. Model setup/serve/switch, GPU inference without explicit
consent and HF cache deletion are never hidden in this wrapper.
See `scripts/temporary/README.md` and D-016. If the original setup is still
running, do **not** pull or invoke the script yet.

## Operator-approved P1 GPU verification without typed per-step hash (D-017)

**Scope:** user explicitly authorized only nondisruptive P1 GPU verification
and bounded benchmark without per-step hash prompts. After `git pull`
on the active branch use:

```bash
bash scripts/temporary/p1-post-download.sh --auto-gpu
```

The temporary bundle still calls the existing Wizard execution entrypoint
with a **fresh exact plan_id per action** and checks the currently served
`qwen3.8-flash-next` API ID and its current checkpoint/image state before
doing anything. It will not stop/start/replace Docker services, download,
modify Hybrid files or run if the current plan is BLOCKED. The operator's
previous report identified source index/tokenizer and Hybrid tokenizer as
existing external symlink targets; this compatibility fix is distinct from
any claim of GPU proof. Return the generated JSON report for P1 acceptance.

## First, read-only inspection AFTER the original shell chain finishes

```bash
bash wizard/p1.sh status
bash wizard/p1.sh plan --for-action verify
bash wizard/p1.sh plan --for-action benchmark --requests 3 --max-tokens 64 --seed 1234
```

If qwen38-flash is already running, SKIP prepare and start. The Wizard can adopt/verify its existing service. A BLOCKED plan while downloading or when assets are incomplete is correct.

## Interactive Wizard

```bash
bash wizard/p1.sh
```

The menu offers prepare, start, wait, verify and benchmark. A plan is read-only; it prints a full SHA-256 plan_id, required asset/runtime facts and blocker reasons. To run one step, an operator must type the FULL plan_id. Any other answer cancels. The Wizard rechecks its preflight immediately before execution.

## Exact noninteractive action approval examples

These are NOT a request to execute while the existing download/setup process is active. Use only after checking fresh plans and getting approval for that exact action.

```bash
# If existing setup already prepared Hybrid, skip this entire step.
bash wizard/p1.sh plan --for-action prepare
bash wizard/p1.sh prepare --execute --approve-plan FULL_PREPARE_PLAN_ID

# If the queued serve already launched a container, skip start.
bash wizard/p1.sh plan --for-action start
bash wizard/p1.sh start --execute --approve-plan FULL_START_PLAN_ID

bash wizard/p1.sh plan --for-action wait
bash wizard/p1.sh wait --execute --approve-plan FULL_WAIT_PLAN_ID

bash wizard/p1.sh plan --for-action verify
bash wizard/p1.sh verify --execute --approve-plan FULL_VERIFY_PLAN_ID

bash wizard/p1.sh plan --for-action benchmark --requests 3 --max-tokens 64 --seed 1234
bash wizard/p1.sh benchmark --execute --approve-plan FULL_BENCH_PLAN_ID --requests 3 --max-tokens 64 --seed 1234
```

Never paste all execution commands as a block; approvals are action-specific and must be refreshed individually.

## Safety, benchmark and evidence limits

- Checkpoint readiness requires full 40-hex refs/main SHA, essential tokenizer/config/index, all index-referenced nonzero safetensors shards, no dangling/cross-cache links or incomplete blobs; Hybrid needs a complete sibling -fp8hybrid snapshot and .prepared marker.
- Image readiness requires local sha256 image ID and the Blazux qwen38.base=v0.32 label. Port/container facts are read-only and must be rechecked before start; an existing name is not removed automatically.
- The Wizard NEVER downloads weights, invokes flash setup, removes/stops/prunes containers or cache, switches models, or launches API inference without a matching plan approval. Prepare only invokes scripts/prepare-hybrid.sh, start invokes flash serve default, wait invokes flash wait.
- API verification checks local /health, /v1/models, text chat, tool calls and a small original PNG vision probe; this is real inference and requires explicit authorization.
- Benchmark is a bounded sequential SSE test: 1-20 requests (default 3), 1-256 max tokens (default 64), seed 1234. Records TTFT and latency p50/p95 and measured usage-based token throughput. Missing usage returns PARTIAL rather than estimating a number.
- Every executed action produces a unique JSON evidence record under ~/.local/state/blazux-wizard/p1/ by default, or --evidence-dir. No prompt contents or tokens are logged. PREPARED_PENDING_AUDIT and STARTED_PENDING_HEALTH are not model qualification.
- There is no automatic rollback or confirmed full-load production benchmark yet. Retain failed containers/logs; any recovery/removal requires separate operator approval. P1 exits only with real DGX Wizard functional + benchmark proof and rollback evidence; then P2 27B via Wizard.

## 2026-11-05 — Default Blazux first, optional tool/vision second (D-018)

User's real DGX report `20261105T103738Z-c4eb4031` confirms
original source/Hybrid assets READY and model ID correct, yet old
combined Wizard verify FAIL with no evidence printed in summary.
Do not say native Blazux model failed based on that alone.

After source commit `391a2844`, Wizard separates `baseline_status`
(regular /v1/completions and standard chat) from `extended_status`
(strict tool and tiny synthetic image), and the temporary script
retains evidence even when Wizard exits with rc=2. If baseline passes
but an extra probe fails, the short 3-request benchmark is still
permitted and the report says verify=PARTIAL. P1 full acceptance
requires remaining features independently passing.

Before repeating a GPU run, examine the previously recorded
`result.json.actions.verify.command` locally for the original
failure's stdout/stderr and exit code. The next operator-only
invocation remains:

```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only origin feature/recipe-wizard-handoff
bash scripts/temporary/p1-post-download.sh --auto-gpu
```

Do not setup/download/prepare/restart containers to fix a Wizard-only
probe discrepancy.
