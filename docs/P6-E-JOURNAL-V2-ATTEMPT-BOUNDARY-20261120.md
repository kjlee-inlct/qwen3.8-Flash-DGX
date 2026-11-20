# P6-E Journal v2 — Attempt Boundary Replay and Terminal Re-entry (2026-11-20 KST)

## Observed source-contract gap
The V2 in-memory event proposal uses the historical V1 `service_journal.PHASES` state graph. In V1, `COMMITTED`, `RESTORED`, `CANCELLED`, `RECOVERY_FAILED`, and `FAILED` can transition back to `OBSERVED` for another operation. However V2 explicitly binds **a single proposed event chain** to an unchanged `plan_id`, `nonce`, source/target models, container IDs and V1 anchor. Before this source patch, `draft_v2_event` could extend `CANCELLED → OBSERVED` with the same plan/nonce, and `audit_v2_draft` could accept an internally consistent **self-rehashed** chain crossing the attempted operation boundary. This is a source-level replay/attempt-separation defect; it is *not* proof that the unimplemented operating nonce ledger is compromised.

## Source-only change
- Introduce `ATTEMPT_CLOSED_PHASES = {COMMITTED, RESTORED, CANCELLED, RECOVERY_FAILED}` and `_attempt_boundary_reuse(prior_phase, next_phase)`.
- Forbid any continuation after a closed phase within the **same V2 draft**. Also forbid `FAILED → OBSERVED` re-entry; `FAILED → ROLLBACK_STARTING` stays legal for repair within the same attempt.
- `draft_v2_event` rejects attempted re-entry with `ValueError("V2_DRAFT_ATTEMPT_BOUNDARY_REUSE")`.
- `audit_v2_draft` adds `V2_JOURNAL_ATTEMPT_BOUNDARY_REUSE` even when an untrusted predecessor hash, sequence index and event-body hash match.
- Existing legal phases including `OBSERVED → PLANNED`, `PLANNED → CANCELLED`, `OLD_STOPPING → FAILED`, `FAILED → ROLLBACK_STARTING` and rollback/commit transitions remain available. The restart reviewer inherits rejection from `audit_v2_draft`, and is always non-authorizing in any case.
- A future new attempt would need a **new externally trusted plan/nonce and independent approval**, but this source-only patch does not issue, authenticate or persist them. Hashes in a JSON fixture remain untrusted.

## New regression fixtures (added, not executed as full repository tests)
1. `test_v2_completed_cancelled_and_failed_attempts_do_not_reenter`: five legal V1 paths ending at `CANCELLED`, `RESTORED`, `COMMITTED`, `RECOVERY_FAILED`, or `FAILED`; valid in-attempt V2 chains still audit consistently, but an attempted `OBSERVED` continuation with the same plan/nonce must raise.
2. `test_v2_self_rehashed_attempt_reentry_chain_fails_closed`: self-rehash and link a forged `CANCELLED → OBSERVED` event with matching `previous_hash`, `event_index`, `plan_id` and `nonce`; audit must report `V2_JOURNAL_ATTEMPT_BOUNDARY_REUSE` despite matching per-event SHA256 and restart reviewer must remain blocked.

Existing V2 test module has **20** methods at historical tested SHA `25bf012a4a76d30508743d751d5693aaff33b943`; this change adds **2** new methods (**22 source test methods expected**). Mock nonce module remains **15** methods. Historical operator reported **35/35 OK** (15 + 20) at `25bf012...`, and that receipt was recorded in docs-only `5ea5e6bc730684d45ea551356df4944b2854d0a1`. Do not transfer 35/35 acceptance to the new code SHA.

## Evidence provenance
- Prior V2 implementation blob `3508f028f4fc09b73a3047701a4f886289089bb7`; new V2 blob `15acbe53a725a1161ce9f355fcf0cf912b9bf544`.
- Prior test blob `2371f8eba1a3457b0561470d7033f08b9fb26ee4`; new test blob `14379ea97d564d65179bb3e89048b69ca10165d8`.
- A local **isolated mirrored transition-state harness** using the confirmed V1 phase table and the same new attempt-boundary predicate ran **4/4 PASS** (0.001s): terminal re-entry cases, failed reset vs permitted rollback, existing positive transitions, and a self-rehashed synthetic chain. It is not execution of `scripts.manager.generic_journal_v2` with genuine repository dependencies, nor a whole-suite CI PASS.
- A full local clone was attempted but the local runtime could not resolve `github.com`. Thus actual repository `test_p5d_p6e_cpu.py`, `test_mock_nonce_fence_v2_cpu.py`, real Wizard CLI and Actions CI on the **new commit** are **NOT_RUN/UNVERIFIED**; no fabricated run ID. CPU artifact provenance remains separate from operator DGX history.
- Existing P5-D unprivileged audit permission barrier and actual PLE RSS/PSS, inode, FD↔PID and kernel NAT ownership remain BLOCKED/UNVERIFIED. Production P6-E operating Journal/nonce, P7 independent live integration, P8 actual recovery and release remain BLOCKED.

## Next CPU verification (safe, no operating writes)
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only
git rev-parse HEAD
git status --short
python3 -B -m unittest discover -s tests -p 'test_p5d_p6e_cpu.py' -v
echo "P6E_JOURNAL_TEST_RC=$?"
python3 -B -m unittest discover -s tests -p 'test_mock_nonce_fence_v2_cpu.py' -v
echo "P6E_NONCE_TEST_RC=$?"
```
Expected method counts: **22 Journal/P5-D–P6-E + 15 Fake Nonce = 37**. These are expected discovery counts only, not new-HEAD PASS. Maintain PR #1 Draft/Open/Unmerged and do not repeat P5-D no-sudo audits; no sudo, ptrace, sysctl, Docker, GPU inference, model switch, service restart, operating Journal write, Actions dispatch or changes to `main`.
