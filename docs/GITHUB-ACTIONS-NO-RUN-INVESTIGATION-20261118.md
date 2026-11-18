# GitHub Actions zero-run investigation — P6-E source-only CI (2026-11-18)

## Decision and scope

**Outcome:** `NO_RUN_REPRODUCED / PATH_FILTER_NOT_CAUSAL / TRIGGER_AUTHORITY_UNVERIFIED / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

Read-only GitHub connector investigation of `kjlee-inlct/qwen3.8-Flash-DGX`, branch `feature/recipe-wizard-handoff`, Draft/Open/unmerged PR #1 targeting `main`. This report documents evidence, excludes several proposed causes, and identifies the remaining authority-side checks. **No workflow dispatch, re-enable, settings mutation, default-branch edit, GitHub Actions rerun, PR merge, actual DGX operation, Journal change or recovery was performed.**

## Observed GitHub API evidence

| Signal | Observed |
| --- | --- |
| `GET /actions/runs?per_page=30` | `total_count=1640`; newest returned run is on 2026-11-11, no later run listed |
| Last successful `push` | Run `43107837772`, SHA `8b118c8b1ef7079fabe0b4edbc6d8a2860fd98d8`, created `2026-11-11T21:59:17Z`, `success` |
| Last successful `pull_request` | Run `43108072440`, same SHA, created `2026-11-11T22:00:50Z`, `success` |
| Current feature/PR HEAD at investigation | `a47a36a0be2d340e642544692e3666e6f11ac784`, 44 commits ahead of `8b118c8` |
| Exact-head `GET /actions/runs?head_sha=a47a36a...` | `total_count=0` |
| Exact-head `GET /commits/a47a36a.../check-runs` | `total_count=0` |
| Combined commit statuses at `a47a36a` | Empty statuses |
| First post-success source commit | `fcd6acccbd4d7d6687e9f4fa9ec9845afe39c5d4`, `2026-11-17T06:32:12Z`, included `handoff/**`, `scripts/manager/**`, `tests/**` and workflow YAML; its SHA-specific Actions run query also returned zero |
| PR #1 | `draft=true`, `state=open`, `merged=false`, `mergeable=true`; branch changes are visible |
| Repository | Public, non-archived; default branch `main`; GitHub connector reports repo admin permission |

**Important distinction:** `total_count=1640` is a repository-run count, not a successful-test count. Some earlier runs `1635`–`1638` still returned `queued` with unchanged timestamps from 2026-11-11 despite newer successful runs; this requires UI/authority inspection and is **not** sufficient to diagnose the no-run cause.

All 44 listed branch commits since the last successful run were attributed by the commits API to `kjlee-inlct` as author and committer; no `[skip ci]`, `[ci skip]`, `[no ci]` or `skip-checks: true` annotations were found in their messages. **Commit author/committer identity does not identify which token or pushing application generated the push event.** Do not infer that `GITHUB_TOKEN` was used.

## Workflow and filter investigation

- The feature branch contains `.github/workflows/recipe-manifest-cpu.yml` (`Recipe manifest CPU (source-only)`) with `on.push.paths`, `on.pull_request.paths` and `workflow_dispatch`; **no `branches` restriction** was present. Paths match new `handoff/**`, `scripts/manager/**`, `tests/test_mock_nonce_fence_v2_cpu.py`, `tests/test_p5d_p6e_cpu.py` and related files.
- The workflow existed at the previously successful SHA `8b118c8` (blob `a27021f9171626d8965188e7823d36458ee79f91`). At the first missing commit `fcd6accc` (blob `0017d254d4a8d22ca8a02530a8bfd7f2b6211508`), comparison found **only two new `run:` commands**, one unittest for fake nonce and one fake-only nonce CLI; no removed event or path trigger. A failing command would normally require the workflow to start and yield a job result; this does not explain **zero created run records**.
- Current blob `92d6514764a17c8a135cfcec1ea4b855bab752f2` adds only relevant path-filter entries and one read-only restart-review command beyond those two commands. No trigger deletion, new branch restriction or commit skip annotation was found.
- Fetching `main/.github/workflows/recipe-manifest-cpu.yml` returned 404. Thus `workflow_dispatch` default-branch precondition is not satisfied; GitHub documents that manual dispatch requires the workflow file on the default branch. **This is not proof that Push/PR triggers fail**, because the prior successful Push and PR runs came from the feature branch.
- PR was `mergeable=true`; a merge conflict is not supported as an explanation by current PR metadata.
- The record is `NO_RUN`, not `RUN_FAILED` or `TEST_FAILED`. Local operator-selected 45/45 CPU PASS at `2f5240d` cannot substitute for source-only GitHub Actions CI at any SHA.

## Not yet readable from this GitHub connector — root cause remains unproven

The connector permits read-only `/actions/runs` and `/commits/{sha}/check-runs` but rejects `/actions/workflows` and `/actions/permissions` as unsupported endpoints (`INVALID_ARGUMENT`, HTTP 400 from connector URL allowlist, **not GitHub API evidence of a disabled setting**). The following **must not** be asserted until independently collected:

1. `workflow.state` for workflow ID `406361282`: `active`, `disabled_manually`, or other state.
2. `actions/permissions.enabled`, allowed event/action policies, repository/account-level GitHub-controlled restriction, and any GitHub Actions UI banner.
3. The **push credential and source application** used after 2026-11-11 (user PAT, GitHub App installation token, or `GITHUB_TOKEN` inside a workflow). GitHub documents that pushes using a workflow's `GITHUB_TOKEN` normally suppress follow-on workflows; the fact that the commit shows the account owner is not evidence that this token caused the present event.
4. Account trust/abuse-policy restrictions, billing policy, GitHub operational issues or other upstream event-processing rules. These are possibilities, not findings.

**Ranked next diagnosis:** examine workflow/repository enabled state and GitHub account UI first; then event actor/token provenance; only then controlled user-originated Push/PR trigger under explicit decision. Do not rewrite the valid YAML, force a merge to `main`, disable CI filters, or create a live-operation workflow as an investigative workaround.

## Operator read-only authority checks

Use a GitHub CLI login with repository-owner/admin rights. These are reads; collect only the displayed JSON and HTTP error codes, never `gh auth token`, secrets or credentials.

```bash
REPO=kjlee-inlct/qwen3.8-Flash-DGX
gh auth status
gh api "repos/$REPO/actions/workflows/406361282" \
  --jq '{id,name,path,state,created_at,updated_at}'
gh api "repos/$REPO/actions/workflows" \
  --jq '{total_count,workflows:[.workflows[]|{id,name,path,state}]}'
gh api "repos/$REPO/actions/permissions" \
  --jq '{enabled,allowed_actions}'
gh api "repos/$REPO/actions/runs?branch=feature%2Frecipe-wizard-handoff&per_page=5" \
  --jq '{total_count,workflow_runs:[.workflow_runs[]|{id,head_sha,event,status,conclusion,created_at}]}'
gh api "repos/$REPO/commits/a47a36a0be2d340e642544692e3666e6f11ac784/check-runs" \
  --jq '{total_count}'
```

Also open repository **Settings → Actions → General**, **Actions → All workflows**, and the specific workflow page. Record any banner that Actions is disabled at repository or account level. If admin endpoints return `403`, that is an **authorization problem** for the reading identity, not proof the repository's Actions are disabled.

### Decision tree

- `permissions.enabled=false` or workflow `state=disabled_*`: **confirmed configuration block**; operator must review reason and intentionally approve remediation. Existing runs remain historical, no automatic backfill.
- `permissions.enabled=true` and `state=active` but an Actions UI banner says Actions is disabled at repository/account level: **possible GitHub-controlled restriction**; consult GitHub Support and retain screen/error text. Toggling Settings might not restore it.
- Enabled, active, no banner, no run: investigate push token/application provenance, event delivery and skip filters; consider a **separately approved, harmless human-token Push** to the existing feature branch to isolate API token effects. That is a new source event, not evidence for previous commits.
- Runs appear later: verify actual workflow, exact head, job steps, test summary, and conclusion. Older 45/45 selected operator CPU receipt remains separate from new CI receipt.

Official references:
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- https://docs.github.com/en/actions/concepts/security/github_token
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository

**Release gate remains:** `SOURCE_UPDATED / CPU_REGRESSION_PASS_AT_2F5240D_OPERATOR / CI_UNVERIFIED / PRODUCTION_BLOCKED`.
