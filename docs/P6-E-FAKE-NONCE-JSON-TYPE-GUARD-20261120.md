# P6-E — Fake nonce marker JSON type equality hardening (2026-11-20 KST)

## Defect and scope
The existing `scripts/manager/mock_nonce_fence_v2.py` writes a fake nonce marker to a private, explicitly prefixed fake directory (the CLI demo uses `TemporaryDirectory`) and audits it as untrusted local fixture data. The read-back audit previously used Python dictionary equality:

```python
if type(actual) is not dict or actual != expected:
    raise ValueError("FAKE_MARKER_IDENTITY_OR_HASH_MISMATCH")
```

This has a real source-only fail-open ambiguity: Python treats `True == 1`, `1 == True`, `8000 == 8000.0`, and `2 == 2.0` as true. A marker with changed JSON primitive types and **unchanged `record_hash`** could be accepted as `PASS_FAKE_NONCE_MARKER_CONSISTENCY`, because semantic record equality did not verify the original field types. This is not evidence of a flaw in the real, unimplemented production nonce ledger.

## Source patch
- Added `_exact_record_fields(actual, expected)` requiring `type(actual) is dict`, an identical key set, each value's **exact Python primitive type** and identical value.
- The `fake_nonce_audit` read-back now uses this comparison and returns the existing non-authorizing `BLOCKED_FAKE_NONCE_AUDIT` and `FAKE_MARKER_IDENTITY_OR_HASH_MISMATCH` on type drift.
- The patch retains the previous 0600 single-link regular-file, private directory descriptor, symlink, stat identity, 4096-byte limit, hash equality, duplicate JSON-key and nonfinite-number protections. Nothing alters `fake_nonce_claim`, lifecycle permissions, actual service journal, Docker, port 8000, vLLM 0.32.0, or registered-model dispatch.
- A new `test_same_value_wrong_json_type_marker_fails_closed` runs five subcases: `requires_independent_approval=True→1`, `requires_live_revalidation=True→1`, `max_active_gpu_models=1→True`, `api_host_port=8000→8000.0`, and `schema_version=2→2.0`. Each asserts blocked audit, unchanged marker/replay rejection, and no operating authorization.

## Evidence and exact provenance
- Prior Git source blob `5e4635cdc2e4376375cf13ed3855914280bcca8a`; prior test blob `dc5d8eefb50623ce2dece917277652fa08887be4`.
- Created new Git source blob `8a7b0f2c69bed0fabb9031d17dc5e7008c6910a1` and new test blob `c0659778720716a1f98ee80882dee85c876e9fc0`.
- **Local isolated CPU schema/helper harness 8/8 PASS**, `Ran 8 tests in 0.001s / OK`, including all five type-equality examples and key-set/normal/negative fixtures. It reproduced old permissive equality and ran the copied new helper body. **This harness is not the entire repository module**, does not exercise full `fake_nonce_audit` or the Wizard CLI, and does not grant a full-source test SHA.
- Full `tests/test_mock_nonce_fence_v2_cpu.py`, `tests/test_p5d_p6e_cpu.py`, entire Wizard and Actions CI on this commit: **NOT_RUN/UNVERIFIED** in this session. Do not upgrade the 8/8 isolated result into new HEAD CI PASS or claim the 5 new subtests were actually executed by the repository suite. Historical 138/138 P5-D and 7/7 permission evidence are separate operator SHA-bound evidence.

## Acceptance boundary
- Only an **isolated fake marker type guard** was modified; real operating Journal v2 durability, independently attested nonce lease, approval authentication, replay fence and restart executor remain BLOCKED.
- P5-D real PLE RSS/PSS/inode/PID mapping and kernel NAT ownership remain BLOCKED/UNVERIFIED after UID1001→root-procfs permission barrier; no repeated no-sudo audit.
- P7 real service/proxy/gateway/storage acceptance, P8 real recovery and production release remain BLOCKED/PENDING.
- No privileged access, Docker, GPU inference, operating Journal writes, CI dispatch, GitHub Actions settings changes, `main` changes or PR merge were authorized or performed.

## Follow-up exact-source CPU check
On the operator's clean feature-branch checkout, with no service changes, record `git rev-parse HEAD` and `git status --short`, then execute:
```bash
python3 -B -m unittest discover -s tests -p 'test_mock_nonce_fence_v2_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_p5d_p6e_cpu.py' -v
```
The mock test creates only `blazux-p6e-fake-*` temporary fixture files. The real operating Journal and service must remain untouched. Record each suite's full `Ran N tests`, `OK` and shell exit status at the exact SHA. CI requires a genuine matching Actions Run ID; do not force another trigger test.
