# Temporary operator scripts — maintained GitHub workflow

Temporary scripts here are **tracked, tested, and short-lived**. They replace large
pasted terminal command blocks for DGX Spark operations. This directory is **not**
a place for production services, permanent recipes, datasets, caches or GPU logs.

## Mandatory process (D-016)

1. Inspect the exact current GitHub branch/HEAD, existing DGX state and operator
   restrictions. Prepare one coherent temporary wrapper for a specific session or
   milestone. Use descriptive names, not `p1.py` or `test.sh`.
2. Commit wrapper, CPU fake-subprocess tests and docs to
   `feature/recipe-wizard-handoff`; inspect GitHub Actions, PR and HEAD. Never
   mark CPU CI as DGX GPU/API/BENCH success.
3. Operator **finishes existing running setup/serve/wait/test first**. Only then,
   with a clean worktree, operator runs `git fetch` / `git pull --ff-only` on
   the intended branch, then invokes **one** wrapper from this directory.
   The wrapper must **not** perform `git pull` or reset/clean the repo itself.
4. One wrapper orchestrates **(1) inspection/preflight → (2) individual
   approved Wizard actions → (3) evidence gathering/summary**. Default dry-run
   or interactive review. No silent approval; each live API/GPU/action needs a
   fresh, exact action-specific plan ID and a second Wizard preflight.
5. Write timestamped, unique, permission-restricted logs and JSON evidence
   **outside Git and HF cache**; print the folder/file path. Don't store secrets,
   copies of model weights, confidential prompts or access tokens. Don't upload
   host-only logs to GitHub automatically. User sends reviewed results back.
6. Record command, Git HEAD, check results, source/runtime distinction, blockers
   and evidence path into handoff; run CPU-only CI, commit PR review. Keep the
   temporary wrapper until the handoff has sufficient reproducible evidence.
   Retire/archive it by a separate documented, reviewed commit (no automatic
   deletion). Preserve permanent recipes, tests, logs and validated runbooks.

**Hard exclusions:** `git reset --hard`, `git clean -fd`, `docker rm`,
container stop/restart, `./flash setup`, downloading the checkpoint, deleting
HF cache, proxy/gateway cutover, model switching and any other destructive work
must never be automatically hidden inside a temporary wrapper. A temporary
script must call the existing Wizard for actual runtime operations and reuse
its explicit approval/rollback guards, not bypass them.

## Current temporary script

- **File:** `p1-post-download.sh` → `p1_post_download.py`
- **Purpose:** single-invocation Flash-Next post-download P1 inspection, bounded
  verified text/tool/vision probes and sequential 3-request SSE benchmark,
  ending in a consolidated JSON report.
- **Use:** AFTER the original operator-owned `./flash setup default` and queued
  `./flash serve default`, `./flash wait`, `./flash test` all exit.
- **Invoke (safe read-only):**
  ```bash
  git fetch origin
  git switch feature/recipe-wizard-handoff
  git pull --ff-only origin feature/recipe-wizard-handoff
  bash scripts/temporary/p1-post-download.sh --inspect-only
  ```
- **Invoke (single interactive wrapper for phases 1–3):**
  ```bash
  bash scripts/temporary/p1-post-download.sh
  ```
  When current plan is READY, the script requests the **full current
  `plan_id` separately** for verify and benchmark. Any missing/incorrect
  approval skips that action. Benchmark requires verify PASS **in that run**.
  Non-TTY defaults to inspection-only behavior unless both exact plans have
  been separately passed as `--approve-verify` and `--approve-benchmark`.
- **Output:** `~/blazux-p1-reports/<UTC>-<id>/result.json` (permissions 0600,
  directory 0700), includes all check exit codes, guarded plans and result
  references to the Wizard's own evidence files at
  `~/.local/state/blazux-wizard/p1/`.
- **Status:** SOURCE/CPU CI verified at `b9f9a1bce6d7aad30ad6648d6c6e7edf35f3712b` (2/2 jobs SUCCESS, 131/131 CPU tests/job); **actual DGX runtime checks still NOT_RUN**. BLOCKED and PARTIAL are not GPU PASS.
