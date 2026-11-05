# Project operating rules (must follow in every conversation)

> Applies to `kjlee-inlct/qwen3.8-Flash-DGX` development, planning, deployment and handoff.

## R1 — Repo, branch and concurrent work

- Canonical new fork `kjlee-inlct/qwen3.8-Flash-DGX`; upstream `blazux/qwen3.8-Flash-DGX`. Preserve upstream behavior and periodically verify pinned upstream SHA before integration.
- Mainline `main` remains a stable base. Plan/handoff work: `feature/recipe-wizard-handoff`. Parallel Orcarouter adaptation: `feature/orcarouter-bf16-adapter`. Do not merge/cherry-pick either automatically without reading diff, resolving conflicts and checking regressions.
- Legacy `kjlee-inlct/Qwen3.8-Flash-Next-NVFP4-BF16PLE-DGX-Spark` and YSLAB references are **read-only historical sources**, not the new implementation base. Never silently replace new fork code with old vLLM patches.
- One coherent topic per branch; meaningful commits, draft PRs for unvalidated work, CI/readback. Record PR and Git SHA. No unverified claim of merge.

## R1A — User-confirmed sequential Wizard delivery contract (2026-11-05)

**확정된 우선순위(2026-11-05):** **P1 Flash-Next 설치·구동·벤치(Wizard) → P2 27B 설치·구동·벤치(Wizard) → P3 Flash-Next ↔ 27B 반복 전환·원복(Wizard) → P4 Flash-Next 선택적 제거(용량 부족 시, Wizard + 정확한 대상/별도 승인) → P5 Orcarouter-Flash-Next 설치·구동·벤치(Wizard) → P6 Orcarouter ↔ 27B 반복 전환(Wizard) → P7 통합 운영 검증/완성.** 단계 수행의 기본 UI는 **Wizard**이며, 기존 `flash`/Python 스크립트는 내부 실행기로 재사용한다. 각 단계는 **구현 SOURCE/CPU**와 **실제 DGX/GPU/API/벤치 PASS**를 별도로 기록한다. **P1 Wizard end-to-end 미완성**, 현 단계에서 다음 개발 최우선이다. 단계 순서를 자의적으로 바꾸거나 직접 CLI 성공만으로 Wizard 단계 완료 처리하지 않는다.

- Do not advance a milestone merely because source/CPU CI succeeded: require actual **Wizard-driven DGX** installation, API/benchmark and evidence for P1/P2/P5; switch and restore verification for P3/P6.
- Existing `flash`, scripts and Python manager are allowed as **subprocess engines** invoked by the Wizard, not as substitutes for a complete Wizard entrypoint. Both interactive and batch/noninteractive operations should share validation, plans, gates and evidence. Wizard should reject implicit destructive defaults.
- Keep external host API `:8000/v1` where feasible and consistently manage served-model IDs. No simultaneous assumption that two heavy models fit GPU memory. Any change to external clients/port/gateway requires explicit operator review.
- P4 is conditional: if sufficient space exists, record **SKIPPED_NOT_NEEDED** rather than delete weights. If required, enforce exact-path dry-run and explicit separate approval, verified safe fallback, no shared-cache blob deletion and rollback plan. Preserve source, recipes, tests, logs and evidence.

## R2 — Live operations, authorization boundaries

- **Superseded observed-operational assumption (2026-11-05):** user reports all previous operating services deleted. The old Orcarouter container `qwen38-flash-orca-uncensored-bf16-mtp` and old `:8000/v1` are **historical**, no longer presumed active or statically reserved. Still perform fresh read-only Docker/socket/volume inspection on DGX; a user report does not prove the port and name are free. Preserve any actually existing unrelated containers, image assets, weights, HF cache, integrations or mounted storage.
- Do not stop/kill/exec/remove/replace/retag/rebind/reconfigure any **observed existing container**, or mutate shared cache/models, without separately scoped approval. Refuse a name conflict: no implicit docker rm -f. Do not treat deletion of old services as authorization to remove other resources.
- This fork removes the implicit `docker rm -f "$NAME"` from `scripts/serve.sh`, replacing it with an exact-name collision refusal; still verify collision checks and race behavior before approving operational launch. Existing upstream scripts in other worktrees may retain the destructive behavior.
- Current user request authorizes **implementing** new Blazux default source/config for port 8000. Do not infer approval for GPU/model loading, Docker image replacement, gateway cutover, service stop, model/cache deletion or other disruptive resource actions. Before deployment obtain actual DGX preflight/port/image evidence and a scoped operation/rollback agreement.
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
