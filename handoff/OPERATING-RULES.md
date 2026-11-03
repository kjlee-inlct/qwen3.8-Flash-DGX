# Project operating rules (must follow in every conversation)

> Applies to `kjlee-inlct/qwen3.8-Flash-DGX` development, planning, deployment and handoff.

## R1 — Repo, branch and concurrent work

- Canonical new fork `kjlee-inlct/qwen3.8-Flash-DGX`; upstream `blazux/qwen3.8-Flash-DGX`. Preserve upstream behavior and periodically verify pinned upstream SHA before integration.
- Mainline `main` remains a stable base. Plan/handoff work: `feature/recipe-wizard-handoff`. Parallel Orcarouter adaptation: `feature/orcarouter-bf16-adapter`. Do not merge/cherry-pick either automatically without reading diff, resolving conflicts and checking regressions.
- Legacy `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark` and YSLAB references are **read-only historical sources**, not the new implementation base. Never silently replace new fork code with old vLLM patches.
- One coherent topic per branch; meaningful commits, draft PRs for unvalidated work, CI/readback. Record PR and Git SHA. No unverified claim of merge.

## R2 — Live operations, authorization boundaries

- Existing original Orcarouter service / API `:8000/v1`, its original Docker container, image, weights, HF cache, volume mounts, external integrations, model ID and restart policy are protected. The known historical container name is `qwen38-flash-orca-uncensored-bf16-mtp`; **verify current ID/image on DGX before use**.
- Do not **stop, kill, exec into, remove, recreate, rename, replace, retag, rebind, reconfigure or run a load test against** the original container without a separately scoped approval and rollback procedure.
- Do not use `./flash serve` with a protected `NAME`: upstream `scripts/serve.sh` has `docker rm -f "$NAME"`. Guard the name before invocation.
- Never perform GPU/model loading, Docker image replacement, gateway cutover, service stop, model/cache deletion or other disruptive resource actions without specific approval. An earlier blanket “yes” on an unrelated phase is not authorization.
- Read-only GitHub/source/test inspection and local CPU-only tests are allowed. DGX read-only inspections should be scoped and recorded, avoiding sensitive output.
- **vLLM 0.32 only** for all three model recipes. No SGLang integration.

## R3 — Destructive cleanup is separate

- Stage P4 `retire Flash-Next` means cleanup *candidate*, not advance permission to delete.
- Require specific cleanup plan ID, confirmed inventory, exact paths/digests, size estimates, disjoint protected roots, no running/bound/shared references, rollback capacity and explicit approval.
- Default `dry-run`; never `rm -rf` a whole workspace/Hub cache, `docker system prune -a` or delete unknown blobs/images.
- Keep recipe, config, benchmark, logs, source and provenance even after checkpoint deletion. Prevent cleanup of the last validated fallback.

## R4 — Verification and assertions

- Status vocabulary: `NOT_RUN`, `PASS`, `FAIL`, `BLOCKED`, `NOT_APPLICABLE`. Each status must carry **scope** `SOURCE/CPU/CI/GPU/API/SWITCH/RELEASE`.
- A source audit `PASS` is **not** GPU runtime `PASS`; upstream/other-author benchmarks are not local benchmarks; default branch compatibility does not imply 27B compatibility.
- Record full model repository revision, image digest, Git HEAD, recipe SHA, runtime config, host resources, command, seeds, comparison method, observed output, log/artifact location and timestamp for every claimed result.
- Orcarouter strict same-checkpoint logprob max absolute delta `1e-4` previously failed in Preview. Carry forward as `RELEASE_BLOCKED` until proven otherwise or a separately reviewed gate decision is recorded. Avoid comparing logprobs across different checkpoints.
- Test failures must be recorded, not concealed, renamed or marked `PASS` for task completion.

## R5 — Efficient development and update rules

- Prefer a meaningful **batch of related changes per conversation**: inspect → implement → write tests → run CPU checks → docs → commit → PR/verify.
- If needed, add or update scripts, manifests, tests and docs, rather than leaving long transient manual commands as the implementation.
- Keep `README.md` external references intact; cite aphex3k only for transferable tuning and benchmark methodology. No SGLang runtime.
- Every state-changing session ends with updated `handoff/CURRENT-STATE.md`, `handoff/NEXT-ACTIONS.md`, and `handoff/CHANGELOG.md`. If there are new tests, update `EVIDENCE-LEDGER.md`; if new policies, update `DECISIONS.md`.
- On a new chat, read handoff first, verify against GitHub and real runtime evidence, proceed directly with the next safe actions. If no tool/action is available, record `BLOCKED` honestly; do not fabricate execution.
- No secrets, personal tokens or private host-only strings in GitHub markdown, logs or PRs.

## R6 — Exit report format

Every meaningful handoff update must include: `WHAT CHANGED`; `SOURCE BRANCH + ACTUAL SHA`; `PR + CI`; `TESTS (PASS/FAIL/NOT_RUN by scope)`; `DGX STATE (observed vs historical)`; `BLOCKERS/APPROVAL`; `NEXT 1–3 ACTIONS`; `FILES UPDATED`. Unknown values must say unknown.
