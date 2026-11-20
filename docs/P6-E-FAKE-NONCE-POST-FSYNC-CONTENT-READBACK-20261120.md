# P6-E — Post-fsync bounded content readback for Fake Nonce marker (2026-11-20 KST)

## Existing provenance checkpoint
Operator-provided shell results at **source SHA `f0e48a5a43824468618aa494ad03cc06f09c10c7`**:
- `test_mock_nonce_fence_v2_cpu.py`: `Ran 14 tests in 0.077s / OK`.
- `test_p5d_p6e_cpu.py`: `Ran 20 tests in 0.014s / OK`.
- Combined **34/34 OK**; test-method counts confirmed by direct GitHub reads of the two source files. No explicit `echo $?` or clean-worktree receipt; classify as `OPERATOR_REPORTED_EXACT_SHA_CPU_34_OF_34_OK_RC_NOT_CAPTURED`. GitHub Actions Runs/Check Runs/Commit Status all **zero** at that SHA (CI UNVERIFIED). Evidence recorded in separate documentation-only commit `d624376a49d047f7d9d728156ec53f837e516dd1`.

## Follow-up source-only flaw and correction
The preceding Fake Nonce `fake_nonce_claim` checked the *name/inode*, 0600 mode/owner/link count and length after file+directory `fsync`. A concurrent same-UID writer to the fake directory could replace the **contents of the same inode with equal-length data** (for example `"api_host_port":8000` to `8001`) after the file `fsync` but before the claim result; name/inode/size would remain consistent and the function could report success despite untrusted contents. No real DGX Journal or operating nonce was involved.

Change:
- Keep the file `fstat` recorded at the original file `fsync` and the existing post-directory-`fsync` name/inode checks.
- Open the named fake marker a second time via the *same pinned private directory FD*, read-only with `O_NOFOLLOW`/`O_NONBLOCK`; limit the read to `len(expected_raw)+1`.
- Require reopened `(st_dev, st_ino)` identity, owner, 0600 permissions, regular file, one link, exact length and **exact expected bytes**, plus metadata consistency before/after read and final path identity. A mismatch or read error falls through the existing `BLOCKED_FAKE_NONCE_IO` / `FAKE_NONCE_DURABILITY_OR_ROOT_IDENTITY_UNKNOWN` handling. An ambiguous file is never unlinked or automatically retried.
- Add `test_same_inode_same_size_content_swap_after_fsync_blocks_claim` (one new `unittest` method) injecting an equal-length in-place byte mutation during the second `fsync` call. It asserts fail-closed marker creation, unchanged inode, marker retained, and subsequent replay rejection.

## Test/evidence boundary
- Previous source blob: `0c015922e4d24d4e4df2a0b8f946d49198f42ae9`; new source blob: `a8a7099e9a2040d3be2230d2dfccebd683eae5c0`.
- Previous test blob: `a671dbb2088a4f1f124b436d3a539d889588d4c6`; new test blob: `7c3d001dc0c1bd0625611d8561ddc635c8239e23`.
- An **isolated, manually mirrored readback primitive harness** ran locally: `Ran 4 tests in 0.003s / OK`; normal unchanged content PASS, in-place equal-length rewrite blocked, equal-byte new inode blocked, symlink replacement blocked. This is **not** execution of the exact complete repository source module.
- The new `test_mock_nonce_fence_v2_cpu.py` now has **15** test methods in source. The *entire test module*, `test_p5d_p6e_cpu.py`, Wizard and Actions CI at this new source change are **NOT_RUN/UNVERIFIED**. The prior operator **34/34** at `f0e48a5...` cannot be transferred to a new SHA, even if a docs-only commit separates them.

## Safety and limits
This is a bounded **point-in-time synthetic file consistency check**, not a cryptographically authenticated operating journal or a permanent defense against adversarial later writes. Do not claim real durable nonce, actual approval/replay prevention or automatic recovery. Existing P5-D permission diagnostics (UID 1001 vs model root, EACCES), PLE RSS/PSS/inode/PID/NAT attribution and live P6-E/P7/P8/production gates remain BLOCKED/UNVERIFIED. No sudo, ptrace, Docker/GPU inference, service restart, operating Journal mutation, Actions dispatch/settings, `main` or PR merge.

## Next exact-SHA operator CPU command
On the clean source-only checkout (no live probes), run and record exact `git rev-parse HEAD`, `git status --short`, and *complete* test summaries with separate shell status:
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only
git rev-parse HEAD
git status --short
python3 -B -m unittest discover -s tests -p 'test_mock_nonce_fence_v2_cpu.py' -v
echo "P6E_NONCE_TEST_RC=$?"
python3 -B -m unittest discover -s tests -p 'test_p5d_p6e_cpu.py' -v
echo "P6E_JOURNAL_TEST_RC=$?"
```
Expected discovery counts on this new revision are **15** and **20**, but expected does not mean executed or passed. CI remains UNVERIFIED until an actual matching run ID is observed; do not dispatch or force CI merely to manufacture the check.
