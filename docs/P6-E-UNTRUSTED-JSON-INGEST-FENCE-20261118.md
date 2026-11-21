# P6-E untrusted JSON ingest fence — source-only (2026-11-18)

## Scope and baseline

- Repository: `kjlee-inlct/qwen3.8-Flash-DGX`, branch `feature/recipe-wizard-handoff`, PR #1 remains Draft/Open/unmerged.
- Starting verified GitHub HEAD: `4e93c6f9e1c0ef14cc55fab7aae378689828c6f8`.
- Verified source/test patch commits (before final documentation commits): initial reader hardening `a15467e22e9bb0d42faf1dff57456891fd64cdee`; added test cases `fd711ebc878864a6ef8d9dcb55a3b6c793339977`; continuation fix `b3e297405a56283e8a144bff8eafab0f24f85400`; explicit JSON depth cap `5b20101e417d0c5391a367a2917813e171bcb1cc`; swapped-file denial assertion refinement `838661e0ed37940ffa4623bab15e6a81b83f93da`.
- Baseline operator-supplied `test_mock_nonce_fence_v2_cpu.py` 10/10 OK RC0 + `test_p5d_p6e_cpu.py` 19/19 OK RC0 = **29/29 reported PASS, SHA/working-tree unbound**. This source change does not retroactively bind that receipt.
- Last operator DGX evidence: 2026-11-12 Orcarouter v3 `DEVELOPMENT_TRIAL`, P5-D `BLOCKED_PARTIAL_PROCESS_EVIDENCE` due to unresolved host port-listener ownership (not a service outage).

## Source changes (unexecuted as of documentation)

1. `scripts/manager/generic_operations.py`: `_load_evidence` now opens the supplied absolute file once with `O_NOFOLLOW` and `O_NONBLOCK`; requires an ordinary regular file; pins inode/device and verifies file size plus mutation timestamps; caps bytes read at 1 MiB even if file grows. Unsupported `O_NOFOLLOW` fails closed.
2. JSON decoding rejects duplicate keys at *every nesting level*, nonfinite `NaN/Infinity`, malformed UTF-8 and semantic nesting deeper than 64 container levels. Root must remain a JSON object.
3. `tests/test_generic_operations_cpu.py`: four new negative test methods cover ambiguous/nonfinite/invalid input, excessive/non-regular data (FIFO), path replacement during descriptor reading, and Wizard restart-review CLI fail-closed behavior without runtime probes.
4. `journal-v2-restart-review` and existing Wizard CLI aliases remain unchanged. Correctly formed input remains **untrusted**; no structural integrity finding can authenticate operator approval, Docker/GPU/port ownership, nonce consumption, persistent Journal durability, or enable recovery.

## Evidence and acceptance

- Source inspection: checked against the feature branch; new test methods **added but not executed** in this session.
- Isolated algorithm reconstruction smoke test (not a checkout of these GitHub files): **4/4 PASS**, checking ordinary JSON, malformed/ambiguous JSON, bounded/deep/FIFO inputs, and filename-inode replacement. This cannot establish actual repository test execution or CI and must not be labeled `CPU_UNIT_TEST_REPOSITORY_PASS`.
- Exact-head GitHub Actions: **UNVERIFIED**. The most recent returned Action run on 2026-11-11 was successful for `8b118c8`; no new run/check was found for starting HEAD `4e93c6f`. The workflow exists in feature branch and has Push/PR path rules that include these edited files, but the same path does not exist at `main`. This limits default-branch workflow-dispatch discovery; it does not prove why later Push/PR runs are absent.
- No actual DGX, inference, service interruption, model transition, operating Journal/Nonce ledger write, live recovery, production release, PR merge, or cache deletion occurred through this change.

## Reproduction checklist (CPU only)

```bash
git rev-parse HEAD
git status --short
python3 -m unittest discover -s tests -p 'test_generic_operations_cpu.py' -v
python3 -m unittest discover -s tests -p 'test_mock_nonce_fence_v2_cpu.py' -v
python3 -m unittest discover -s tests -p 'test_p5d_p6e_cpu.py' -v
python3 -m wizard operations generic journal-v2-restart-review --from-model orcarouter --to-model 27b --json
# Restart review is expected to return exit code 3 / BLOCKED when no evidence is passed.
```

Do not label source inspection or simulated/fake tests as an independently verified real DGX acceptance result. Investigate Actions repository settings/eligibility and actual run triggers without mutating `main` or merging PR #1. For operating Journal v2, independent authenticated nonce and approval, and real recovery, keep explicit approval barriers.
