> **2026-11-20 14:04 KST operator CPU supersession:** Actual operator terminal summary at source `f0e48a5a43824468618aa494ad03cc06f09c10c7`: `test_mock_nonce_fence_v2_cpu.py` **14/14 OK (0.077s)**, `test_p5d_p6e_cpu.py` **20/20 OK (0.014s)**, combined **34/34**. GitHub source test counts match. Shell exit code and clean tree not separately printed; Actions runs/checks/statuses **0**, CI **UNVERIFIED**. These tests supersede earlier `NOT_RUN` for this source SHA, not real operating nonce/Journal acceptance.

# P6-E — Fake nonce post-fsync path/inode continuity (2026-11-20 KST)

## Prior gap and scoped behavior
Before this patch, `fake_nonce_claim` performed an exclusive `O_EXCL` marker create, wrote and fsynced the file, fsynced its directory, and checked **only the root directory inode** before returning `PASS_FAKE_NONCE_MARKER_CREATED`. A concurrent writer with access to that disposable fake directory could replace the marker path in the interval after the original file closed but before the success return. The earlier root check would not notice a marker-file path swap. This is a fake-fixture consistency gap, not an attested production exploit or authority issue.

## Source-only change
- Capture the created file's `os.fstat()` identity immediately after its file `fsync`, before close.
- After directory `fsync`, call `os.stat(filename, dir_fd=directory_fd, follow_symlinks=False)` and require the named file to be a regular file, the same `(st_dev, st_ino)`, owned by the current user, exactly mode 0600, with one hard link and expected byte size.
- An absent, symlinked, retargeted or replaced file follows existing fail-closed `BLOCKED_FAKE_NONCE_IO` / `FAKE_NONCE_DURABILITY_OR_ROOT_IDENTITY_UNKNOWN` handling. No automatic unlink, retry, operating approval, recovery, or execution. Existing root identity check is retained.
- Added `test_marker_swap_after_directory_fsync_blocks_claim` with two negative `os.fsync`-injection cases: a dangling symlink replacement, and a different inode with identical bytes while the original inode is held in place. Both must return blocked and retain the marker/replay-fence behavior.
- This improves a bounded **point-in-time post-fsync check**, not a guarantee against arbitrary future tampering or an authenticated durable operating nonce ledger.

## Evidence provenance
- Source previous blob `8a7b0f2c69bed0fabb9031d17dc5e7008c6910a1`, new blob `0c015922e4d24d4e4df2a0b8f946d49198f42ae9`.
- Test previous blob `c0659778720716a1f98ee80882dee85c876e9fc0`, new blob `a671dbb2088a4f1f124b436d3a539d889588d4c6`.
- An **isolated, manually mirrored post-fsync filesystem harness** was executed in a private temporary directory: `Ran 4 tests in 0.020s; OK` (normal claim, symlink swap, identical-byte different-inode swap, replacement identity demonstration). This independently reproduces the intended check but is **NOT** execution of the repository's full module or the newly added repository unittest.
- The complete `test_mock_nonce_fence_v2_cpu.py`, `test_p5d_p6e_cpu.py`, real Wizard CLI, all-P6 suites and Actions CI at the new commit are **NOT_RUN/UNVERIFIED**. The development runtime could read GitHub connector files and create Git commits but lacked a network-resolvable clone of the repository. Historical P5-D 138/138, permission 7/7, and previous isolated P6-E 8/8 have different evidence origins; do not add them or treat as a new-HEAD test PASS.

## Acceptance and follow-up
- Mock-only fake-disk integrity improved; real durable Journal v2 migration, authenticated approval, operating nonce ledger, replay fence, automatic restart/executor remain BLOCKED.
- Known P5-D UID 1001 vs root process `smaps`/FD EACCES and unverified PLE RSS/PSS/inode and kernel NAT ownership remain BLOCKED/UNVERIFIED. Do not repeat unprivileged audit.
- P7 service/proxy/gateway/storage actual independent acceptance, P8 real recovery, `main`/merge and Production Release remain BLOCKED/NOT ACCEPTED.
- **Next operator CPU-only action (not a live DGX probe):**
```bash
cd ~/Workspace/llm/blazux-orcarouter
git pull --ff-only
git rev-parse HEAD
git status --short
python3 -B -m unittest discover -s tests -p 'test_mock_nonce_fence_v2_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_p5d_p6e_cpu.py' -v
```
Record the exact checkout SHA and each test summary / process exit code. No sudo, Docker/GPU/service changes, operating Journal writes, Actions manual dispatch or trigger comparison, `main` modification, PR merge or cache cleanup.
