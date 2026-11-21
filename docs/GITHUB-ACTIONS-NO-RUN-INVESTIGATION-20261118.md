# GitHub Actions zero-run investigation — P6-E source-only CI (2026-11-18)

## 2026-11-18 operator Git Push 93473ed: zero Actions, Nov 11 incident correlation

### Reproducible feature-branch trigger probe (operator-run; source-only)

The operator ran `git pull --ff-only`, then locally created and committed `handoff/CI-PUSH-TRIGGER-PROBE-20261118.md` and successfully pushed to `https://github.com/kjlee-inlct/qwen3.8-Flash-DGX.git`. GitHub REST independently confirmed:

- **Probe SHA** `93473eda06769614ef259a1ab6acdc6e9db13b4b`, message `ci: probe human git push trigger`, commit timestamp `2026-11-18T02:37:58Z`.
- Change is **one new file with two lines in `handoff/**`**, which is an existing `on.push.paths` filter match; Push/PR branch restrictions are absent.
- PR #1 head moved to `93473ed`, Draft/Open, `mergeable=true`.
- At the operator's first immediate check and subsequent connector readback, repository Actions runs remained **1640**, **zero workflow runs for probe SHA**, **zero check runs**, empty combined statuses. Remote accepted the Push; absence of any run is not evidence of failing CPU tests.
- This rules out **connector-only commit creation as a sufficient explanation**. However, the actual credential backing the local HTTPS Git Push was **not inspected**; author/committer identity alone is insufficient to establish a PAT, SSH key, GitHub App token, or other event authorization. Avoid asserting that `GITHUB_TOKEN` was definitely or definitely not involved.

### Four orphaned pre-incident Actions records, independently confirmed

Run `43096807109` (Push 20:34:00 UTC), `43096812698` (PR 20:34:04), `43097090510` (Push 20:36:50), and `43097097266` (PR 20:36:53) all date to **2026-11-11**, and **each remains `queued`, `conclusion=null`, `run_attempt=1`, no timestamp advancement and `GET /jobs` reports `total_count=0`**. They belong to workflow `406361282`.

GitHub officially reported an incident affecting **Webhooks, Actions, Pages, Copilot** from **2026-11-11 20:48 to 21:21 UTC**, later marking the queue backlog processed: https://www.githubstatus.com/incidents/dvy0t3mvh1lg . The four repository records are **~12–14 minutes before the published start**. Similar `queued`+zero-jobs records beginning **20:25–20:41 UTC** and failing cancellation were reported by other users: https://github.com/orgs/community/discussions/212794 . Some participants quoted purported support advice that incomplete run state survived the incident; **those statements are third-party reports, not a support diagnosis of this repository**. The previously successful Push+PR at 21:59/22:00 UTC additionally proves the repository has run workflows after the incident's recorded recovery.

**Evidence-based interpretation:** `ORPHANED_QUEUED_JOBS_ZERO` is **observed** for these four run IDs; `NOV11_PLATFORM_INCIDENT_TEMPORAL_CORRELATION` is **strong but not causally verified**; why newer events through **2026-11-18** do not create fresh runs remains an **independent unresolved issue**. A queue or runner outage normally does not explain lack of run creation by itself; do not equate the two symptoms.

### Priority diagnosis and safe escalation

1. **Stop repeated source-only trigger probes** now that a matching-path ordinary `git push` reproduces no-run. Do not remove/rewrite the 4 orphaned runs or modify workflow settings without an approved recovery plan.
2. Review the repository Actions UI and account notices for event-processing warnings, execution restrictions, usage/billing limits, or security enforcement. `state=active`, `enabled=true`, `allowed_actions=all` have already been confirmed for workflow/repository but may not reveal backend enforcement. Recheck `gh run list` after the propagation period; never call the initial immediate response a permanent absence without subsequent checks.
3. For GitHub Support, supply `kjlee-inlct/qwen3.8-Flash-DGX`, workflow ID `406361282`, four orphaned run IDs and their `queued`+zero-jobs snapshots, official incident `dvy0t3mvh1lg`, last successes `43107837772` and `43108072440`, missing Push SHA `93473ed` and the relevant created timestamps, enabled policy JSON, and the matching `handoff/**` filter. Request *both* orphaned run/check-suite reconciliation **and** investigation of new Push/PR event processing. Do not supply secrets.
4. Avoid unconditional `workflow_dispatch` advice: the workflow YAML is **absent from default branch `main`**, so dispatch preconditions do not hold. `main` last changed 2026-11-02, before the 2026-11-11 feature-branch PR/Push successes, reinforcing that this absence alone does not explain the recent stopping of both trigger types.
5. CI remains `UNVERIFIED` until a real run is created for an exact current source HEAD and logs/conclusion are verified. Keep P6-E source CPU **45/45 PASS only at tested `2f5240d`**; no production authorization.

**Updated classification:** `ACTIONS_ACTIVE / ACTIONS_ENABLED / GIT_PUSH_NO_RUN_REPRODUCED / FOUR_QUEUED_ZERO_JOBS / INCIDENT_CORRELATED_NOT_PROVEN / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---


## 2026-11-18 operator Actions authority readback: active/enabled/all

The operator executed these **read-only** GitHub CLI API calls on `lc-gx10-pc` on 2026-11-18 and pasted their JSON responses:

```bash
gh api "repos/$REPO/actions/workflows/406361282" --jq '{id,name,path,state}'
# {"id":406361282,"name":"Recipe manifest CPU (source-only)","path":".github/workflows/recipe-manifest-cpu.yml","state":"active"}

gh api "repos/$REPO/actions/permissions" --jq '{enabled,allowed_actions}'
# {"allowed_actions":"all","enabled":true}
```

**Updated findings:** workflow registration and activation are now **CONFIRMED ACTIVE**; repository Actions is **CONFIRMED ENABLED** with `allowed_actions=all`. These findings rule out *current* `disabled_manually` and repository `enabled=false`. They do **not** prove the settings were unchanged during the missing 2026-11-12 through 2026-11-18 events, that GitHub's account/event delivery is healthy, or that any prior push was emitted by an eligible token. The GitHub connector rechecked total workflow runs after the prior five documentation commits: still **1640**, newest the same successful 2026-11-11 runs.

GitHub's official trigger documentation distinguishes two token cases: an event generated by a workflow-scoped `GITHUB_TOKEN` generally does not create new Push/PR workflow runs; an independently authorized PAT or GitHub App installation access token **can** trigger them. **A GitHub API-created commit is not automatically suppressed.** The GitHub commit author/committer `kjlee-inlct` does **not** reveal the actual pushing token. The token/event hypothesis is therefore still **UNCONFIRMED**.

### Next reproducible isolation step — separately operator-executed, source-only

The existing `on.push.paths` matches `handoff/**`. An **empty commit does not change a matching file and is not an adequate trigger probe**. After ensuring this development working tree is clean and up to date, the operator may choose to execute one human-authenticated Git Push that adds a small unique Markdown record under `handoff/`, then check for a new Push and PR run. This changes only GitHub source documentation; **no DGX runtime action, Journal mutation, model service change, PR merge or workflow settings modification** is required.

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only
git branch --show-current
git rev-parse HEAD
printf '%s\n' '# CI Push Trigger Probe' '' '2026-11-18 operator-originated Git push; source-only; no deployment.' > handoff/CI-PUSH-TRIGGER-PROBE-20261118.md
git add handoff/CI-PUSH-TRIGGER-PROBE-20261118.md
git commit -m "ci: test human-originated push trigger through handoff path"
git push origin feature/recipe-wizard-handoff
gh run list --repo kjlee-inlct/qwen3.8-Flash-DGX --workflow recipe-manifest-cpu.yml --limit 8 --json databaseId,headSha,event,status,conclusion,createdAt,url
```

**Preconditions:** confirm `git branch --show-current` is `feature/recipe-wizard-handoff`; do not proceed if `git status --short` is nonempty or `git pull --ff-only` fails. Do not print or share any access token. Human `git push` may use either SSH or PAT, so confirm its origin when interpreting the result. `git push` is a deliberate source change, **not part of this read-only investigation**.

- **New run appears from human Push:** CI event delivery is working for that credential at that moment. Review whether connector-origin commits use a distinct identity/integration or were committed during an earlier inactive period. Obtain exact run logs and checkout SHA; previous SHAs remain without CI receipts.
- **No new run despite a matching changed file:** inspect GitHub Actions UI notices, push webhook/event delivery (when accessible), and contact GitHub Support with repo/workflow ID, UTC timestamps, new commit SHA, runs API result and observed settings. Do not guess that CPU tests failed.
- **Run appears but fails:** review its actual job logs; *only then* diagnose a test or environment failure. A new run at a later commit is **not** CI evidence for an older commit.
- `workflow_dispatch` is not a substitute here because the workflow file is absent from the default branch `main`; do not merge simply to enable manual dispatch.

**Revised classification:** `ACTIONS_WORKFLOW_ACTIVE / REPOSITORY_ACTIONS_ENABLED / NO_RUN_REPRODUCED / PUSH_ORIGIN_UNVERIFIED / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---


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
