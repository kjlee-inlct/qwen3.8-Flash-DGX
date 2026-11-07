# Ordinary Flash-Next ↔ NVIDIA 27B operating switch — DGX acceptance runbook

**Scope:** existing `./wizard.sh` source implementation only, with one dedicated operator-approved acceptance route. Do not confuse immutable P3 A/B/C one-off success with acceptance of ordinary recurring switch UX. As of this writing **real ordinary operating switch has NOT_RUN**; last operator-observed service is 27B on :8000. Open WebUI 27B tool-calling profile is explicitly out of scope.

## Fixed invariants

- NVIDIA DGX Spark, vLLM 0.32, no SGLang, one GPU inference model active at a time.
- Externally published OpenAI-compatible API stays `:8000/v1`, no simultaneous GPU model start.
- Preserve both originally pinned Flash-Next and NVIDIA 27B containers/images/checkpoints/HF caches. Never run `docker rm`, image prune, download again, or replay `stage-a/b/c` for operating acceptance.
- Open WebUI/Portainer containers stay up, but Open WebUI and clients may experience errors **during the one approved model transfer**.
- This document is a plan; it is NOT authorization to interrupt the active 27B. The actual operator must independently authorize each direction at the DGX TTY, with adequate maintenance scope and acknowledgement of possible failed restoration.

## Implemented Wizard interface

| Entry | Scope | Effect |
|---|---|---|
| `./wizard.sh` → `4. Switch active model` | Normal operator UX | Fresh current/target review. Production release remains source-locked. |
| `./wizard.sh` → select a model → `6. Guided operating switch` | Model-first alternative | Same guarded review and future three-exact-approval UX. |
| `./wizard.sh switch flash-next-27b operational --target flash-next --plan --json` | Read-only candidate | No transaction approval token or Docker mutation. |
| `./wizard.sh switch flash-next-27b operational guided --target flash-next` | Read-only guided CLI | Displays target, active model, unique candidate and release gate. |
| `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --plan --json` | Read-only acceptance preflight | Fresh exact source/container/image/P3 historical provenance, journal, port, 10-minute plan. |
| `bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --execute` | **Live DGX, trial-only** | Requires TTY and FOUR independently typed, current, exact approvals before ONE guarded transfer. Must not be run without separately approved downtime. |
| `python3 -m scripts.manager.operational_audit --json` | Read-only journal audit | Cross-checks append-only events, SHA chain, snapshot and committed receipt. |

Use `--target 27b` for the **separate**, independently authorized return direction. No automatic Flash→27B or second transfer follows a successful 27B→Flash trial.

## Before any live execution (read-only, can run on active DGX)

~~~bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
bash scripts/temporary/operational-switch-acceptance.sh --target flash-next --plan --json
~~~

**Expected prerequisites:** `LIVE_SERVICE_VERIFIED`, the served ID matches active original 27B, target preserved original Flash is stopped and pinned, P3 A/B/C historical receipts validate, no foreign GPU container, journal `EMPTY` or `VERIFIED` with resolved terminal phase, and trial plan `READY_FOR_SEPARATE_TRIAL_APPROVAL` with no issues and at least 180 seconds left. This is still **not** downtime permission. If plan is blocked, DO NOT use a historical SHA or force an execute.

## Independently consented first physical acceptance

Only with an explicitly approved temporary API interruption and recovery risk, the human at a real DGX TTY may choose the tracked wrapper with `--execute`. The wrapper independently generates its fresh plan and displays the source/target. The operator must type these four values **manually** in order; none is prefilled, passed as argv or piped:

1. `I_SEPARATELY_AUTHORIZE_SINGLE_OPERATING_ACCEPTANCE_TRIAL`
2. The exact newly displayed 64-character **independent execution** plan SHA (not the read-only preview SHA or any P3 SHA)
3. `I_ACCEPT_DGX_MODEL_SWITCH_DOWNTIME`
4. `I_APPROVE_FLASH_NEXT_AS_ACTIVE_MODEL` (for 27B→Flash) or `I_APPROVE_27B_AS_ACTIVE_MODEL` (for Flash→27B)

At the last approval the wrapper rechecks the current plan; the independently locked executor rechecks again immediately before any Docker stop. If the plan expires/changes, execution fails closed with no automatic refresh or reused approval. Plan windows are 10 minutes; if below 180 seconds, return to read-only plan at a later time.

After authorization, the isolated operating backend attempts exactly this transaction: immutable attempt marker → append-only operating journal → recheck original container → stop original → require free :8000 → verify preserved target container/image/label → start target → wait for /health and exact /v1/models → **one bounded non-tool chat completion from the requested target** → verify original remains stopped/preserved → COMMITTED + immutable receipt → journal audit. It never changes vLLM flags, recipes or Open WebUI tool settings.

## Outcome handling: no blind retry

| Status | Interpretation | Required operator response |
|---|---|---|
| `PASS` | One transfer committed and verified, including bounded chat | Keep new model active; separately review fresh plan/consent for reverse direction |
| `BLOCKED` / `CANCELLED` | Pre-dispatch refusal or incorrect TTY approval; no authorized stop | Review fresh current plan, expiry and blockers; no automatic retry |
| `FAIL_RESTORED` | Transition failed, original model recovery independently verified | Inspect private journal/receipt; do not automatically retry |
| `RECOVERY_FAILED` | Restoration uncertain or failed; current model unverified | Stop all further switching; inspect live Docker/API and private journal, reconcile manually |
| `COMMITTED_EVIDENCE_INCOMPLETE` | Target may be active but evidence chain incomplete | Do NOT auto-restore or repeat; reconcile exact API, containers and journal before further use |

On any uncertain outcome, the safe commands are read-only:

~~~bash
./wizard.sh service manager status --json
python3 -m scripts.manager.operational_audit --json
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker inspect qwen38-27b --format '{{.Id}} {{.State.Status}} {{.Image}}'
docker inspect qwen38-flash --format '{{.Id}} {{.State.Status}} {{.Image}}'
~~~

Never overwrite/delete the operational journal, attempt marker, completed receipt or original P3 receipts to "clear" an error. Never manually restart either GPU model if exclusivity and port state are unverified. The operator's original private receipt files must remain outside Git. Do not publish internal request payloads, confidential logs or private state records.

## Source/release acceptance boundary

The one-off acceptance entrypoint is an independent trial and **does not turn on the ordinary production menu**. The tracked production code intentionally has `PRODUCTION_EXECUTION_RELEASED=False`. To qualify routine production switching, operators must provide **actual DGX** evidence of both separately approved directions and selected failure/recovery cases. Review source/CPU CI, private journal consistency and operator UX after each run. Only then can a separately reviewed source change enable the production gate and be revalidated. A green Fake-DGX CI, historical P3 A/B/C, or a read-only plan **cannot** substitute for this step.

The source branch is `feature/recipe-wizard-handoff`, Draft PR #1 unmerged. Source-only GitHub commits do not change the active DGX Docker service.
