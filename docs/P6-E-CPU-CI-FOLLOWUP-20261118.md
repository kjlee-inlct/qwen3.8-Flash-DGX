# P6-E CPU receipt, Actions trigger diagnosis and fake replay hardening (2026-11-18)

## Follow-up — Actions no-run investigation results (2026-11-18)

The source-only workflow previously produced **1,640 historical runs**, most recently Push/PR SUCCESS at `8b118c8` on 2026-11-11. From that SHA to feature HEAD `a47a36a`, **44 commits** were added without a newer run record. Exact-head Actions runs/check-runs/statuses were empty; the first missing P6-E source commit `fcd6accc` also had zero runs. PR is mergeable. Workflow path filters and skip-CI checks did not explain the problem. GitHub connector does **not** permit reading Actions enabled state, workflow state or repository Actions permissions; therefore **root cause remains unverified**. For complete evidence, competing hypotheses and read-only admin diagnostic commands, see [Actions zero-run investigation](GITHUB-ACTIONS-NO-RUN-INVESTIGATION-20261118.md).

The operator's 45/45 PASS at `2f5240d` remains valid **only** as a selected CPU test receipt, not CI. No workflow dispatch, repo settings change, source test execution, PR merge, operating service or Journal action occurred in the investigation.

<!-- GITHUB_ACTIONS_ZERO_RUN_INVESTIGATION_20261118 -->

---


## 2026-11-18 update — new-HEAD selected CPU regression 45/45 PASS (operator receipt)

**Superseding selected-CPU result:** The operator supplied a complete terminal transcript after `git pull --ff-only`, showing fast-forward `4fc3aa8..2f5240d`, `git rev-parse HEAD = 2f5240d3a5652ce44af51b4b323b0d8d88a105bd`, and **empty `git status --short` before running the tests**. The following selected CPU modules were executed on that checkout:

| Test command pattern | Tests | unittest summary | Shell exit |
| --- | ---: | --- | --- |
| `test_generic_operations_cpu.py` | 14 | `Ran 14 tests`, `OK` | `GENERIC_RC=0` |
| `test_mock_nonce_fence_v2_cpu.py` | 12 | `Ran 12 tests`, `OK` | `NONCE_RC=0` |
| `test_p5d_p6e_cpu.py` | 19 | `Ran 19 tests`, `OK` | `P6E_RC=0` |
| **Selected total** | **45/45 PASS** | **0 reported failures/errors** | **All three RC=0** |

Evidence class: `OPERATOR_SUPPLIED_CPU_45_OF_45_PASS_RC0_SHA_BOUND_CLEAN_TREE`. **This is a SHA-bound operator-supplied terminal receipt, not independently authenticated GitHub Actions or the full repository suite.** Empty `git status --short` establishes the checkout was clean *before* testing; the transcript does not show a second status check afterwards. The earlier **43/43** receipt at `4fc3aa8` remains historical and is superseded for the **selected CPU regression state** by this exact `2f5240d` observation. Subsequent docs-only commits do not constitute a new independent test run.

**Current decision:** `SOURCE_UPDATED / CPU_REGRESSION_PASS_NEW_HEAD / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

**CI still open:** No same-HEAD GitHub Actions PASS has been established by this operator transcript; existing zero-run/trigger diagnosis below remains an unresolved investigation, not proof of a CI job failure. Inspect Actions enablement, policy, triggering actor, branch workflow registration and exact commit checks separately.

**Safety boundary:** CPU/Fake-DGX and source-only evidence cannot approve an executor, independent evidence authority, real persistent Journal v2 migration or nonce replay fence, automatic recovery, or production release. No real DGX service change, model switch, operating Journal mutation, automatic recovery or PR merge was performed as part of this documentation update.

---

## Scope and immovable safety boundary

Repository `kjlee-inlct/qwen3.8-Flash-DGX`, branch `feature/recipe-wizard-handoff`, Draft/Open PR #1. This review and follow-up affect only source, tests and handoff documentation. No Docker command, real DGX service switch, inference run, GPU/port reallocation, operating Journal mutation, durable production nonce, authorization, automatic recovery or PR merge was performed. vLLM 0.32.0 / ONE_ACTIVE_MODEL_ONLY / port 8000 / no SGLang remain unchanged.

## Operator-provided SHA-bound CPU receipt

The operator pasted an actual terminal transcript showing `git rev-parse HEAD` = `4fc3aa8e0a0cb3b69c6337b6c34b701578b132cc`, with blank `git status --short` output before the three unit-test commands. Results:

| Test file | Count | Result |
| --- | ---: | --- |
| `test_generic_operations_cpu.py` | 14 | OK |
| `test_mock_nonce_fence_v2_cpu.py` | 10 | OK |
| `test_p5d_p6e_cpu.py` | 19 | OK |
| **Total** | **43** | **43 PASS** |

Evidence class: `OPERATOR_SUPPLIED_CPU_43_OF_43_PASS_SHA_BOUND_CLEAN_TREE`. This validates only these three modules at this exact SHA, **not** independently signed provenance, entire CI, real DGX, operating authority or later source commits. In the first two-module commands, `NONCE_RC=0` and `P6E_RC=0` were captured at predecessor `beba719`; the latest 43-test transcript shows unittest `OK` for all three modules. The exact subsequent GitHub branch head must never inherit this PASS automatically.

## GitHub Actions read-only diagnosis

- Latest source branch head at investigation was `4fc3aa8`. Full Actions run search by this exact SHA yielded `total_count=0`; `check-runs` and combined commit statuses were also empty.
- Most recent returned workflow run was the existing `Recipe manifest CPU (source-only)` success on 2026-11-11, head `8b118c8b1ef7079fabe0b4edbc6d8a2860fd98d8`. Earlier executions existed for both Push and PR events on the same feature branch.
- `.github/workflows/recipe-manifest-cpu.yml` exists on feature branch. The `on.push.paths` and `on.pull_request.paths` rules match `scripts/manager/**`, `handoff/**` and relevant tests. Path filters alone do not explain the zero-run outcome.
- Default branch is `main`, and `main/.github` and the workflow file returned 404. This prevents asserting that default-branch-only `workflow_dispatch` is registered; **it is not conclusive proof** of missing Push/PR triggers.
- Connector read-only access cannot fetch `/actions/workflows` or `/actions/permissions`; activation status, repository policy, workflow state and initiating token identity are **UNVERIFIED**. No settings change or manual dispatch occurred.
- No demonstrated Actions failure: absence of a run record is distinct from a failed job.

If the operator has suitable read permission, examine the following read-only endpoints, ideally retaining response bodies and timestamps:

```bash
gh api repos/kjlee-inlct/qwen3.8-Flash-DGX/actions/workflows
gh api repos/kjlee-inlct/qwen3.8-Flash-DGX/actions/permissions
gh api 'repos/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs?branch=feature%2Frecipe-wizard-handoff&per_page=10'
gh api 'repos/kjlee-inlct/qwen3.8-Flash-DGX/commits/4fc3aa8e0a0cb3b69c6337b6c34b701578b132cc/check-runs'
```

Also inspect the Actions UI workflow status and repository settings, actor/token used for pushes, workflow activation state and organization/account restrictions. `GITHUB_TOKEN` recursive-trigger suppression is a **hypothesis**, not a finding about these pushes. Do not merge to main or dispatch a live-operation workflow as an investigative shortcut.

## Post-receipt source-only P6-E hardening

Following the 43-test receipt, these **new untested branch commits** were created:

- `29453eda5f2d4426dd650af6699f0970ff20b1fb`: reject ambiguous duplicate JSON keys and nonfinite tokens when inspecting a fake nonce marker; additionally compare inode metadata `ctime_ns` across the bounded audit read.
- `81cf2adb3d54bac5b9bae950a8aa0686055049c1`: add tests for duplicate-key marker rejection and injected failure at file or directory `fsync`. A failed fake write must keep its marker and block replay.
- `36ca445725371eda1dd371836d3029460ea735a3`: test context-manager syntax correction.

These changes touch `mock_nonce_fence_v2.py` and its CPU tests only. All writes in the mock remain within a per-test private temporary directory; its `PASS_FAKE_*` results cannot authorize operations. The expanded mock test suite now defines **12 methods**; together with the older 14+19 methods the **expected** selected scope is 45, not a verified 45/45 pass.

## P6-E next safety contracts — acceptance design, not released code

1. **Independent evidence authority**: define immutable scope binding (source and target model/container IDs, plan digest, API port, policy, actor, nonce, monotonic/expiry bounds, boot ID and manifest revision); require separately configured signature trust roots and verifiable signer provenance. A user-supplied `verified=true`, locally recomputed hash, hash-chained synthetic event, or injected JSON must never become authority.
2. **Crash consistency**: make a dedicated Fake-DGX fault-injection matrix for each write, `fsync`, atomic rename, directory `fsync`, and snapshot publication boundary. Persist intent/nonce before any possible side effect. After uncertain write or torn state, freeze; no silent cleanup or auto-resume. Actual power-loss guarantees remain UNVERIFIED.
3. **Replay fence**: model atomic nonce reservation, global one-time use across plan/model pairs, concurrent-process contention, restart retention, marker corruption and symlink/hardlink/rename attacks. Keep a recovered marker spent until an independent, auditable operator procedure exists.
4. **Scoped approval**: externally verified signature, expiry, exact plan digest, model identities, authorized downtime and execution scope; revalidate live Docker/API/port/GPU ownership at a protected boundary. A valid structural JSON document is insufficient.
5. **Executor separation**: do not bridge the read-only review to production execution. No real journal v2 migration, autonomous recovery, production release, P5 loaded benchmark, P7 independent live acceptance or P8 real recovery without separate operator authorization and evidence.

## Safe next verification

On the development checkout (no runtime operations):

```bash
git pull --ff-only
git rev-parse HEAD
git status --short
python3 -m unittest discover -s tests -p 'test_generic_operations_cpu.py' -v
python3 -m unittest discover -s tests -p 'test_mock_nonce_fence_v2_cpu.py' -v
python3 -m unittest discover -s tests -p 'test_p5d_p6e_cpu.py' -v
```

Expected selected test count at the new source SHA: 14 + 12 + 19 = **45**, pending actual execution. Capture full `OK`, return codes, exact SHA and clean-tree status; then independently inspect same-head Actions. `BLOCKED_V2_RESTART_NOT_AUTHORIZED` and exit 3 for read-only restart review with absent or untrusted evidence are expected fail-closed outcomes.

**Classification at this document commit:** previous `CPU_REGRESSION_PASS_43_AT_4FC3AA8`; new source `CPU_REGRESSION_PENDING`; `CI_UNVERIFIED`; `PRODUCTION_BLOCKED`.
