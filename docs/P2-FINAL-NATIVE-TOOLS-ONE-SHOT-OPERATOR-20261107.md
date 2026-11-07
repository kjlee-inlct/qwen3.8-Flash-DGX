# P2-FINAL — One-shot NVIDIA 27B Native Tool Calling DGX operator procedure

**Evidence status (updated 2026-11-07): REAL DGX one-shot native-tool inference PASS_RESTORED.** Actual operator TTY-approved trial returned `structured_tool_call=true`, `tool_result_continuation=true`, `streamed_tool_call=true`, `original_restored=true`, and `issues=[]`. Original `qwen38-27b` API/ordinary-journal postchecks passed. The originally planned procedure remains below for provenance; **do not repeat this already consumed one-shot test plan**. Full evidence: [P2-FINAL Native Tools LIVE evidence](P2-FINAL-NATIVE-TOOLS-LIVE-EVIDENCE-20261107.md). Open WebUI Native UI, production Wizard release and forced-error recovery remain unqualified.

This procedure is deliberately separate from historical P2/P3 A/B/C and the ordinary `./wizard.sh` production switch. It never replays old P3 or removes the original containers, images or Hugging Face cache. It uses vLLM `0.32.0` and original image, exactly one GPU model, port `:8000`, and a separately named `qwen38-27b-native-tools-v1` container.

## Step 1 — Source fast-forward and read-only exact-plan preflight

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status -sb
git pull --ff-only origin feature/recipe-wizard-handoff
bash -n scripts/temporary/p2-final-native-tools-operator.sh
bash scripts/temporary/p2-final-native-tools-operator.sh --plan
```

The `--plan` mode inspects source 27B/Flash containers, GPU/port identity, immutable historical P3 lineage and ordinary operating journal, re-renders the exact pinned NVIDIA template on CPU inside the current 27B Docker container, checks SHA-256 `c3cf9e34abf4f9e36c2d72165aa9c132d3e2a725b6c2586aaa3a8af9d7a81041`, and prints an independent, time-bound, exact 64-hex trial SHA. It cannot stop/start Docker or run GPU inference. Proceed ONLY with `status=READY_FOR_INDEPENDENT_NATIVE_TOOLS_TRIAL_APPROVAL`, `issues=[]`, `restore_original_after_trial=true` and a fresh approval window. **Any BLOCKED result means stop; do not bypass it with ad-hoc `docker run`.**

## Step 2 — Independently approved actual one-shot trial (service interruption)

**This WILL interrupt current `:8000` clients; Docker/host/OOM/SIGKILL errors may defeat automatic restoration.** Ensure a maintenance window and local operator availability. The user explicitly decides whether to execute after reading the plan. Run **only** when the planned downtime is accepted, and use the real terminal (not pipes or CI):

```bash
bash scripts/temporary/p2-final-native-tools-operator.sh --execute
```

This first **recalculates a fresh read-only plan**, prints a fresh SHA and expiry, and prompts independently for:

1. the **new** 64-character exact SHA printed by `--execute` (do not paste an old/expired plan ID);
2. `I_ACCEPT_P2_FINAL_NATIVE_TOOLS_DOWNTIME`;
3. `I_APPROVE_DISTINCT_27B_NATIVE_TOOLS_V1`.

Input via TTY only. Empty, stale, incorrect, expired or changed identity blocks without Docker stop. There are no command-line flags to auto-fill approval.

If separately authorized, the guarded one-shot executor:

- acquires dedicated trial and ordinary operating-switch locks; writes a private immutable **attempt marker before** mutations, blocking retries after uncertain interruption;
- checks the original preserved container/image and single-GPU exclusivity immediately before stopping `qwen38-27b`;
- waits for port 8000 to release, then creates a **distinct** `qwen38-27b-native-tools-v1` using the pinned vLLM image with `--chat-template`, `--enable-auto-tool-choice`, `--tool-call-parser qwen3_coder`, `--reasoning-parser qwen3`, with trial-only provenance labels;
- checks the new API and sends bounded localhost `tool_choice=auto`/tool result continuation and streamed `tool_calls` probes, **never executing a real external tool**;
- **stops the trial variant and restores original `qwen38-27b` automatically, even after trial success**, checking original API and chat health; private phase events/results are written under `~/.local/state/blazux-wizard/p2-final-tools-v1/`.

Expected result **only if actually observed on DGX:** `status=PASS_RESTORED`, `structured_tool_call=true`, `tool_result_continuation=true`, `streamed_tool_call=true`, `original_restored=true`. A `PARTIAL_RESTORED` or `FAIL_RESTORED` means the trial did not fully qualify; a `RECOVERY_FAILED` or evidence inconsistency means STOP and inspect actual Docker/API and immutable private files, do not blindly retry or remove original state. A normal successful one-shot still leaves the new variant container **stopped and preserved** for investigation. It is not the ongoing production model.

## Step 3 — Independent after-action read-only status

```bash
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

Require original `qwen38-27b` active and sole API model ID `qwen3.8-27b`, unchanged operational-switch journal. These postchecks are especially important because the trial uses a **new private journal**, not the ordinary Wizard's switch journal.

**Qualification boundary:** a real Native Tools one-shot structured tool-call PASS closes a new P2-FINAL subgate but does not release normal `PRODUCTION_EXECUTION_RELEASED=False`, validate Open WebUI Native, or qualify ongoing variant-aware service management. Production promotion or another trial needs an independent review, new approval and source change. Old P3 receipts and original containers/images/caches must remain untouched.

## Abort/recovery rules

The CLI cannot auto-retry an already attempted plan. No scripted `docker rm`, `docker rmi`, HF cache cleanup or old P3-C reruns are authorized. An operator must reconcile both original and variant states, current port/GPU/HTTP identity and the private attempt/event/result records. Always privilege the physical service state over a saved manifest or printed status.
