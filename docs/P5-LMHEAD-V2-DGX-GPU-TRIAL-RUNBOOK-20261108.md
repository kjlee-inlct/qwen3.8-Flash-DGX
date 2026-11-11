## CURRENT P5 DOCUMENT SUPERSESSION — 2026-11-09 actual v3 MTP0 overrides historical v2 runbook

The original v2 `qwen4exp-qsa62318-lmhead-v032-v2` failure involving `lm_head.weight_scale` is preserved below as a historical trial. Operator logs at 2026-11-09 00:55 KST show v3 `qwen4exp-qsa62318-lmhead-v032-v3` `PASS_LIVE_INFERENCE` MTP0 on :8000 as `DEVELOPMENT_TRIAL`, not canonical or production. Idle resource data and scope of P6 source-only/Fake-DGX tests are current in [P5 technical record](P5-ORCAROUTER-BF16PLE-VLLM032-ADOPTION-20261108.md) and [full document audit](HANDOFF-DOCUMENT-AUDIT-FULL-P5-20261108.md). Do not rerun an old v2 execute command, stop v3 or claim production switch/rollback qualification.

---

# P5 Orcarouter vLLM 0.32.0 — current DGX MTP0 trial, QSA + LM-head v3

## AUTHORITATIVE CURRENT P5 OPERATIONAL STATE — 2026-11-08 ~23:30 KST

This section supersedes the previous *v2 failure/v3 planned run* instructions further below. Its filename remains historical; follow the latest facts, not a prior failed plan.

**Actual operator DGX evidence:** `./wizard.sh service manager status --json` returned **`LIVE_P5_TRIAL_API_VERIFIED`**, `issues=[]`, `runtime_role=DEVELOPMENT_TRIAL`, `production_released=false`. Current v3 container `qwen38-orcarouter-qsa62318-lmhead-v3` is running and owns port 8000, image `sha256:088d8b7171d2fb1a54120727334c445991096e5ee4e684c5598d672d872d79d4`, container ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`; API ID `qwen3.8-flash-next-orca-uncensored-bf16`. **`./wizard.sh p5 trial verify --json` returned `PASS_LIVE_INFERENCE`**, chat content `READY`, no service mutation. **`p5 trial cleanup-execute` returned `PASS`**, removed exactly old exited(1) test containers `qwen38-orcarouter`, `qwen38-orcarouter-qsa62318`, `qwen38-orcarouter-qsa62318-lmhead`, with private archived Docker logs under `~/.local/state/blazux-wizard/p5-live-trial/cleanup/`. **Do not re-run cleanup.** Keep running v3 intact. No canonical production promotion or MTP2/tools/vision/benchmark qualification has occurred.

**NEW P5 PRIORITY: resource measurement and protection.** The 95.37 GiB BF16 PLE is file-backed via mmap; that mapping size is **not equivalent** to current resident RAM usage. Operator has **not** supplied a detailed RAM/Swap/PSI/CPU/GPU measurement of active v3. YSLAB pinned public reference `YSLAB-ai/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark@9492b78c6bc04638587b42f2ffeb0680b0fcb3ef` `src/recipe/runtime.py` implements a prelaunch `MemAvailable` gate of 100 GiB, runtime GPU memory utilization 0.80, 32 PLE mmap workers, no PLE prewarm. Its `benchmarks/stability.py` records `MemAvailable` and swap used. No automatic CPU frequency cap, cgroup hard-limit or PSI safety controller identified in inspected source. Current Blazux 0.32 MTP0 uses 0.70 GPU utilization, 16 workers, 8192 context, one max sequence; YSLAB figures/benchmarks are external **not Blazux measurements**.

**First next-session operator task: non-mutating DGX capacity snapshot, then recipe-owned protection proposal.** Suggested command (safe for active service; no sudo or Docker mutation):

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
./wizard.sh p5 trial status --json
free -h
cat /proc/pressure/memory
cat /proc/pressure/cpu
awk '/^(MemTotal|MemAvailable|MemFree|Cached|SReclaimable|SwapTotal|SwapFree|Dirty|Writeback):/ { print }' /proc/meminfo
docker stats --no-stream qwen38-orcarouter-qsa62318-lmhead-v3
docker inspect qwen38-orcarouter-qsa62318-lmhead-v3 --format '{{json .HostConfig}}'
nvidia-smi
for f in /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq; do
  test -r "$f" && printf '%s %s\n' "$f" "$(cat "$f")"
done
```

No `docker stop`, `docker rm`, `kill docker-proxy`, `cpupower frequency-set`, cgroup hard memory limit, kernel sysctl or system CPU governor changes on the running v3 without a *separate explicit operator plan/approval*. Design warning thresholds vs soft startup gate vs explicit resource caps separately; measure pressure first, preserve :8000 uptime and ONE_ACTIVE_MODEL_ONLY, vLLM 0.32.0, no SGLang. Stable later canonical service name is `qwen38-orcarouter` (Orcarouter Flash-Next); version suffixes remain disposable trial candidates. P8 final fault/recovery work remains deferred; PR #1 draft, no merge.

---


## LIVE OBSERVATION: v3 running on :8000; temporary name and cleanup workflow

**Operator DGX observation (2026-11-08 ~23:08 KST):** Docker
`qwen38-orcarouter-qsa62318-lmhead-v3` **Up 24 min** with
`0.0.0.0:8000->8000/tcp`; GET `/v1/models` returned
`qwen3.8-flash-next-orca-uncensored-bf16`.
This proves v3 is serving the expected model identity, but **chat inference remains
unverified until the live bounded verify returns PASS**. The old service-manager
status was BLOCKED because it only recognized the canonical name
`qwen38-orcarouter` and production policy rightly left its
`served_id` null. **The 8000 listener is live v3, not an orphan from 27B. NEVER
kill docker-proxy or delete the running trial.**

**Naming contract:** v1/v2/v3 are *disposable candidate identifiers*, not
final services. The existing stable canonical Docker service is
`qwen38-orcarouter` (operator-facing: **Orcarouter Flash-Next**).
The model API ID for MTP0 is
`qwen3.8-flash-next-orca-uncensored-bf16`.
Version/adapter revisions belong in image tags, recipe/manifest history, not in
the eventual canonical service container name. **Do not rename running v3 to the
canonical name without a separately approved lifecycle transition and verified
inference.** Canonical name currently belongs to an exited legacy failed trial;
that is one of the explicitly cleanup-eligible targets, not a production release.

**Read-only + bounded live inference without restarting Docker:**

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
./wizard.sh p5 trial verify --json
```

With successful Docker + health + expected model ID, service manager now shows
`LIVE_P5_TRIAL_API_VERIFIED` with
`runtime_role=DEVELOPMENT_TRIAL`, **never**
`LIVE_SERVICE_VERIFIED` for a canonical service. `p5 trial verify` submits a
bounded chat against the already-running v3, without stopping/starting Docker:
`PASS_LIVE_INFERENCE` is the real target; no production release implied.

**Retiring failed containers without touching live v3:** failed v1/QSA-only/v2
test containers ought not accumulate indefinitely. Cleanup is explicitly
approved, NOT an unconditional delete on failure: preserve private logs first.
This flow is distinct from unrelated 27B manifest retirement.

```bash
./wizard.sh p5 trial cleanup-plan --json \
  | tee /tmp/p5-cleanup-plan.json
# Review the exact target IDs/names. Do NOT approve until ready.
# Then use the fresh plan's 64-hex plan_id:
./wizard.sh p5 trial cleanup-execute \
  --approve-plan <FRESH_PLAN_ID> \
  --ack-cleanup I_APPROVE_P5_FAILED_TRIAL_CONTAINERS_ONLY --json
```

Only **exited nonzero**, exact-name allowlisted P5 containers
`qwen38-orcarouter`, `qwen38-orcarouter-qsa62318`, and
`qwen38-orcarouter-qsa62318-lmhead` can be removed. The Wizard verifies
pinned Orcarouter launch command, HF read-only mount, port binding, live v3
container ID and API model ID; logs and receipt are saved mode 0600 under
`~/.local/state/blazux-wizard/p5-live-trial/cleanup/` before **docker
rm only**. Docker images, checkpoints, PLE assets, existing logs and services
remain untouched. On incomplete/foreign identity it BLOCKS; never use
`docker rm -f` or `kill docker-proxy` to force cleanup.

---

## 2026-11-08 Orcarouter v3 — actual DGX loader failure fixed at source

**Confirmed live failure at 2026-11-08 13:27 UTC, v2 image `sha256:3e0afbb4...`:** 15/17 safetensors loaded, PLE BF16 mmap engaged, then the exact previous `ValueError: There is no module or parameter named 'lm_head.weight_scale'`; Docker exit=1, `OOMKilled=false`. Actual checkpoint has `lm_head.weight_scale` BF16 `[248320,1]`, `group_0` targets `lm_head`, not ignored.

**Root-cause patch:** vLLM 0.32's nested Qwen4Exp model passes `maybe_prefix(prefix, "lm_head")` (e.g. `model.language_model.lm_head`) into compressed-tensors. That name does NOT match the pinned checkpoint quant target `lm_head`; v2 forwarded `quant_config` but kept the incorrect quant-dispatch name, so `ParallelLMHead` instantiated only `weight`. New isolated **v3** patches only that constructor to `quant_config=self.quant_config, prefix="lm_head"`, per pinned YSLAB compatibility approach. It does not edit HF weights, change global vLLM, use SGLang, or replace old v2 images/failed containers.

**New candidate (NOT GPU verified):**
- Source: `src/p5_lm_head_quant_backport_v032_v3.py`, QSA #62318 unchanged
- Dockerfile: `Dockerfile.p5.qsa62318-lmhead-v3`
- Image: `blazux-p5-orcarouter:qsa62318-lmhead-v3-v032`
- Container: `qwen38-orcarouter-qsa62318-lmhead-v3`
- Adapter: `qwen4exp-qsa62318-lmhead-v032-v3`
- P5 MTP0, host port 8000, single active model, exact new-plan + no-auto-rollback acknowledgement required.

**Run on DGX:** clean `git pull --ff-only origin feature/recipe-wizard-handoff`; then `./wizard.sh p5 trial prepare --json` (offline scoped v3 image build), `./wizard.sh p5 trial plan --json` (read-only plan). If both PASS/READY, and the operator knowingly approves downtime/no automatic restore, execute the fresh `./wizard.sh p5 trial execute --approve-plan <FRESH_64_HEX_PLAN_ID> --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json`. Reuse **no previous plan ID**. Actual PASS requires running Orcarouter + API identity + chat inference, not metadata/CI alone. On failure preserve all existing containers and report the *new* v3 container's Docker logs.

---


**2026-11-08 current superseding instructions.** Earlier sections of `docs/P5-ORCAROUTER-MTP0-DGX-LIVE-NO-RESTORE-RUNBOOK-20261108.md` that refer to the QSA-only adapter/container are historical. Use **this** runbook for the next P5 experiment; never reuse an old plan ID.

## Current operator objective: START the Orcarouter model, not more document checks

**Priority is real MTP0 inference on `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` with Blazux vLLM 0.32.0 at port 8000.** The 2026-11-08 DGX checkpoint audit already passed: `lm_head.weight` F8_E4M3, `lm_head.weight_scale` BF16, `group_0` matching, no ignored head. The remaining loader behavior must be tested by **starting the model** rather than adding further source acceptance layers.

At source HEAD `a7e2ed7`, the 119 DGX CPU tests failed **one local document inventory equality test** (`test_p5_document_integrity_cpu.P5HandoffFullDocumentCPU.test_full_inventory_resolves_every_original_document`, `AssertionError`); this is **not model/quant/runtime evidence**. Likely local checkout contents differ from the GitHub CI checkout, but the precise file mismatch is not in the bounded report. Do not fix local documents as a precondition for model launch. That CI-only inventory regression must NOT block P5 runtime preparation or GPU trial. From `44093c2` the standalone preflight defaults to **manifest + pinned checkpoint only**; use `--with-tests` solely if debugging CPU regressions. The actual `p5 trial prepare` and `plan` still enforce pinned metadata, runtime image identity, :8000 and single-model exclusivity.

**Direct operator commands**, run on DGX after `git status --short` (ensure no local modifications) and `git pull --ff-only origin feature/recipe-wizard-handoff`:

```bash
set -euo pipefail
./wizard.sh p5 trial prepare --json | tee /tmp/p5-orcarouter-prepare.json
./wizard.sh p5 trial plan --json | tee /tmp/p5-orcarouter-plan.json
python3 - <<'PY'
import json
p=json.load(open('/tmp/p5-orcarouter-plan.json'))
assert p['status']=='READY_TO_APPROVE', p['issues']
print('Target:',p['details']['served_id'])
print('Exact plan ID:',p['plan_id'])
print('Approve intentionally only after reviewing stopped-27B/no-auto-rollback consequences.')
PY
```

**Only after an explicit operator approval of the fresh exact plan and potential downtime**, execute:

```bash
./wizard.sh p5 trial execute --approve-plan <FRESH_PLAN_ID> \
  --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json \
  | tee /tmp/p5-orcarouter-execute.json
```

The execute route checks actual startup, API model identity and bounded chat inference; `PASS_GPU_TRIAL` is the concrete next goal. Failure may leave :8000 down and old 27B stopped (no automatic restore); old checkpoint/images/failed-container logs must remain untouched. Do not retry using an expired plan. Do not merge PR #1 or claim production acceptance merely from source tests.

## Actual DGX preflight observation — 2026-11-08

**Operator measurement on source HEAD `596a6839`:** manifest PASS; pinned quant metadata PASS; LM-head **not ignored**, matches **`group_0`**, weight **F8_E4M3 [248320,2560]** in shard 17/17, scale **BF16 [248320,1]** in shard 16/17. These are verified **metadata only**; runtime weight registration and GPU readiness remain false/unverified. Simple `ignore`/target-missing hypotheses do not explain this checkpoint.

**Blocking local result:** `cpu_tests.count=117`, `exit_code=1`, `status=BLOCKED`, preflight issue `P5_PREFLIGHT_CPU_TESTS_FAILED`. The old preflight did not expose failing IDs; exact cause is not known from the provided JSON. Never call those 117 locally executed tests PASS. GitHub CI on the previous HEAD did pass the CPU tests separately.

**New safe diagnostic:** the one-shot JSON now provides `cpu_tests.failing_test_ids`, `cpu_tests.reported_failure_counts`, and `cpu_tests.exception_types` on CPU failure, never raw unbounded stderr. After fast-forward, re-run the **same read-only preflight** below, inspect those fields and fix the identified test before image preparation. This does **not** authorize GPU execution or turn v2 adapter into a qualified loader.

## New read-only checkpoint gate — 2026-11-08

**Run this before `p5 trial prepare`.** The checkpoint was not independently readable from this GitHub session (gated HF source); the latest GPU failure must not be promoted to PASS based on external model cards.

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
git rev-parse HEAD

python3 -m scripts.manager.p5_checkpoint_preflight --json \
  | tee /tmp/p5-lmhead-checkpoint-preflight.json
```

This single CPU-only, no-Docker/no-GPU/no-network judge runs manifest validation, the pinned `config.json` and `model.safetensors.index.json` audit, bounded safetensors **header-only** reads for `lm_head.weight` and `lm_head.weight_scale`, and `test_p5_*_cpu.py` regressions. It does **not** read weight payloads or change a cache. It returns `PASS_SOURCE_ONLY` only when its checks pass; even this means **no GPU registration, MTP0 inference or PLE mmap qualification**. `BLOCKED` (exit 3) forbids image preparation and approval planning.

The `p5 trial prepare` and `p5 trial plan` metadata gate now invokes the same pinned head audit; plan/execute cannot bypass it. Specifically, a checkpoint containing a FP8 scale but listing LM-head in `quantization_config.ignore`, lacking an explicit head-target FP8 group, or having inconsistent indexed safetensors headers is **BLOCKED**. Generic `Linear` targets alone do not establish matching for `ParallelLMHead` in vLLM 0.32. The audit is intentionally fail-closed and may require further engine ABI work even on a metadata PASS. Do **not** edit or rewrite checkpoint weights/config to force a pass.

If this tool returns a blocking code, share the redacted JSON fields `checkpoint.lm_head`, `checkpoint.issues` and `cpu_tests` for source analysis. No approval or GPU run should be attempted until the mismatch is resolved in a new isolated, versioned adapter.

## Evidence boundary and latest observed failure

- **Actual operator-provided DGX, checkout `247d31de79da9fda3b2dcea41d7c96141d5a766b`**: QSA #62318 derived image built and MTP0 GPU trial launched. The initial QKV/indexer quantization exception no longer blocked constructor creation; safetensors shard progress reached 15/17 before a *new* `ValueError: There is no module or parameter named 'lm_head.weight_scale' in Qwen4ExpForCausalLM`. Available LM-head params: only `lm_head.weight`. Trial receipt: `~/.local/state/blazux-wizard/p5-live-trial/trial-20261108T054106528164Z.json`, `FAIL_NO_ROLLBACK`, `gpu_verified=false`, `ORCAROUTER_CONTAINER_EXITED`. This confirms **neither GPU load nor inference success**, and does not prove BF16 PLE mmap activation.
- Container `qwen38-orcarouter-qsa62318` exited(1), original failed `qwen38-orcarouter` exited(1), original `qwen38-27b` exited(0); last observed :8000 unserved. This is *last reported observation*, not current live inventory. Never silently restart 27B or remove the preserved containers.
- **GitHub source candidate v2**: `src/p5_qsa_quant_backport_v032.py` remains the #62318 / Blazux FP8-hybrid QSA fix; `src/p5_lm_head_quant_backport_v032.py` additionally injects `quant_config=self.quant_config` into the vLLM 0.32.0 Qwen4Exp LM-head constructor in a **new, isolated image**. vLLM 0.32's ParallelLMHead already has relevant linear metadata, so do not apply the YSLAB *older-development-image* metadata patch globally. The new source fix is **CPU/CI validated, not yet DGX-build/GPU qualified**.
- **Quantization warning:** constructor wiring alone does **not** guarantee that `lm_head.weight_scale` is registered. The pinned checkpoint's actual `quantization_config` targets, `ignore` list and weight keys must be inspected. If `lm_head` is ignored while a scale tensor exists, treat as a **blocked format/loader mismatch**; do not silently remove an ignore entry, rename/discard a scale tensor, or assume a legacy recipe solves it. A forum-posted configuration is external evidence, not proof of this pinned snapshot.

## Immutable recipe and image identity

| Field | Current P5 v2 candidate |
| --- | --- |
| Branch | `feature/recipe-wizard-handoff`, fetch fresh HEAD |
| Engine | Blazux vLLM **0.32.0**, no SGLang |
| Candidate adapter | `qwen4exp-qsa62318-lmhead-v032-v2` |
| Candidate Dockerfile | `Dockerfile.p5.qsa62318-lmhead` |
| Candidate image tag | `blazux-p5-orcarouter:qsa62318-lmhead-v032` |
| Candidate container | `qwen38-orcarouter-qsa62318-lmhead` |
| Old QSA-only candidate | `qwen38-orcarouter-qsa62318` — PRESERVE |
| Base image | exact SHA256 ID from existing `qwen38-27b` container; unchanged |
| Checkpoint | `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4@3a3b63161c0745390e5270179af42e46efc70799` |
| Serving | host `:8000/v1`, `ONE_ACTIVE_MODEL_ONLY`, MTP0 |
| Recovery | development **no automatic restoration** on trial failure |
| Release | false; MTP2, Tools, Vision, benchmarks, P6 switch, P8 fault tests unqualified |

## Operator sequence

First update the checkout and run CPU/read-only checks. The following `prepare` builds and labels an **offline derived image** if absent; it is NOT read-only, but it does not launch a GPU model or change the canonical Blazux source image. Do not run it if image building is no longer permitted.

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
git rev-parse HEAD

./wizard.sh manifest validate --json
# Full CPU/document suite is optional and tracked in CI, not required for launch.
./wizard.sh p5 trial status --json

./wizard.sh p5 trial prepare --json | tee /tmp/p5-lmhead-v2-prepare.json
./wizard.sh p5 trial plan --json | tee /tmp/p5-lmhead-v2-plan.json
```

Stop if manifest, pinned model metadata, prepare, or plan is not PASS/READY. The optional CPU/document suite is not a runtime startup gate. Confirm **all** of: `prepare.status == PASS`, `plan.status == READY_TO_APPROVE`, `plan.issues == []`, `plan.details.adapter == qwen4exp-qsa62318-lmhead-v032-v2`, original base image digest matches, new candidate digest differs, source identity matches, port/GPU exclusivity gates pass and plan SHA/expiry is fresh. Source may be running 27B or previously exited(0); a running unknown model or an occupied idle :8000 is a hard block.

Inspect the *actual pinned* config and weight map **read-only** before another GPU attempt. Never edit the HF snapshot:

```bash
python3 - <<'PY'
import json
from scripts.manager.p5_live_trial import SNAPSHOT
cfg = json.loads((SNAPSHOT / 'config.json').read_text())
q = cfg.get('quantization_config', {})
ignore = q.get('ignore', [])
groups = q.get('config_groups', {})
print({
  'ignore_lm_head': 'lm_head' in ignore,
  'lm_head_target_groups': [
    key for key, group in groups.items()
    if any('lm_head' in str(target) for target in group.get('targets', []))
  ],
  'quant_format': q.get('format'),
})
PY
```

**Do not equate the above diagnostic with approval or CPU proof that a scale is loadable.** If it reveals an unresolved target/ignore mismatch, stop; first identify the actual LM-head tensor shape/dtype/scheme and source loader path. Do not approve GPU trial merely because `prepare` and `plan` pass.

Only after successful checks and the operator's explicit decision to use the development DGX, obtain a **fresh** plan and approve the exact transaction using the existing Wizard interface:

```bash
./wizard.sh p5 trial plan --json
# Then, only with a VERIFIED fresh 64-hex plan ID:
./wizard.sh p5 trial execute --approve-plan <FRESH_64_HEX_PLAN_ID> \
  --ack-downtime I_ACCEPT_P5_NO_ROLLBACK --json
```

This intentionally can leave port 8000 unserved on failure. It never authorizes deleting containers/cache, merging PR #1, P3 replay, P4 live deletion, P6 generic switches or P8 fault/recovery.

## Evidence and acceptance

After a trial, record `git rev-parse HEAD`, `./wizard.sh p5 trial status --json`, `docker ps -a --filter 'name=qwen38-'`, `docker logs --tail 1000 qwen38-orcarouter-qsa62318-lmhead`, the private P5 trial receipt, `/v1/models` and inference result if serving. Avoid tokens or other secrets in Git. `PASS_GPU_TRIAL` requires actual started model + confirmed API identity + bounded Chat response; it does NOT establish MTP2, benchmark, Tool or production release.

## Source-of-truth priority

Actual **latest** DGX report > committed current recipe/manifest/Wizard code > current top-of-file handoff and this runbook > historical P5/P4 starter examples and external YSLAB/forum work. Never promote an old `NOT_RUN` statement into current truth when a later failed trial exists; never misreport a failed GPU attempt as a pass.
