# P5-D source-side manifest binding and Wizard read-only review (2026-11-20 KST)

## 2026-11-20 KST — operator-confirmed exact-source CPU acceptance: 138/138 PASS

**Evidence origin:** operator-supplied DGX terminal transcript from `~/Workspace/llm/blazux-orcarouter`, **not** a GitHub Actions runner or an assistant-executed test. The operator performed branch/clean-tree preflight, `git pull --ff-only origin feature/recipe-wizard-handoff`, and checked the exact source `TESTED_SHA=7c11d0d1a0921ef7b0f4134bd3d3c0d8ac4e5795`; printed `P5D_MANIFEST_WIZARD_CPU_RC=0`. All eight selected `unittest` module summaries explicitly reported `OK`:

| CPU unit test module | Tests | Result |
| --- | ---: | --- |
| `test_p5d_manifest_binding_cpu.py` | 5 | PASS |
| `test_p5d_live_audit_cpu.py` | 24 | PASS |
| `test_p5_readonly_attribution_cpu.py` | 9 | PASS |
| `test_p5d_p6e_cpu.py` | 20 | PASS |
| `test_manifest_registry_cpu.py` | 19 | PASS |
| `test_generic_operations_cpu.py` | 14 | PASS |
| `test_generic_console_cpu.py` | 11 | PASS |
| `test_wizard_router_cpu.py` | 36 | PASS |
| **Total (selected suites, non-overlapping methods)** | **138** | **138/138 PASS** |

The same operator run completed `python3 -B -m wizard manifest validate --json` with `status=PASS`, `issues=[]`, seven registered manifest files plus registry and cross-reference marked PASS, `scope=DECLARATIVE_MANIFEST_ONLY`. The unified CLI `python3 -B -m wizard operations generic p5d-source-binding-review --model orcarouter --json` returned `DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED`, `manifest_graph_validated=true`, PLE asset `orcarouter-bf16-ple`, declared BF16 / DISK_MMAP and pinned revision `3a3b63161c0745390e5270179af42e46efc70799`. Both explicitly returned `operations_enabled=false`, `production_released=false`; PLE residency and NAT ownership attestation remain false.

**Conclusion and SHA scoping:** `SOURCE_CPU_SELECTED_138_OF_138_OPERATOR_PASS_AT_7C11D0D / MANIFEST_GRAPH_PASS / WIZARD_P5D_BINDING_PASS`. This supersedes earlier selected-source CPU 50/50 for the covered suites, **not** the historical live DGX `BLOCKED_PARTIAL_PROVENANCE/RC3` result. No P5-D live audit on this SHA was included in the uploaded transcript, no real per-PLE RSS/PSS/inode/FD↔PID/NAT ownership observed, no GPU exclusivity authenticated. `GITHUB_ACTIONS_CI_UNVERIFIED / P5D_LIVE_ACCEPTANCE_BLOCKED / P6E_P7_P8_OPERATING_BLOCKED / PRODUCTION_RELEASE_BLOCKED`.

**Next bounded P5-D evidence:** the validated PLE manifest binding can now be used before a *separately approved read-only* host audit. Check exact per-PID `smaps_errno` (do not assume zero RSS when unreadable), all three namespace identifiers + start ticks, pinned snapshot file/inode aliases, raw Docker publish/bindings vs kernel NAT and container socket-FD owner. A failed permission check is an evidence gap and **must not** be fixed by automatic sudo, Docker exec, service restart, firewall change or cache mutation. Preserve separate explicit authorization for live audit, and store a private receipt only if approved. Do not repeat CI trigger test commits; see [Actions comparison](GITHUB-ACTIONS-OPERATOR-PUSH-COMPARISON-20261120.md).

---

## Latest real DGX read-only result

On SHA `fd338efa549a8c3bb54e65e5e033d2334d9e96e1`, the source-bound audit remained `BLOCKED_PARTIAL_PROVENANCE / RC3`: three host PIDs returned `smaps_errno=13` (EACCES), while Docker IPv4/IPv6 port declarations matched. This is a permission-limited measurement, **not** zero PLE residency or verified kernel NAT. See [permission blocker](P5-D-PROCFS-PERMISSION-BLOCKER-20261120.md). The 138/138 CPU PASS remains bound to earlier `7c11d0d`.

## Scope and rationale

P5-D previously duplicated the Orcarouter HF repository/revision in the host audit module. The shared seven-document Wizard manifest graph already records the model checkpoint, pinned revision, PLE asset, discovery, loader capability and runtime policy. A source-level drift could otherwise cause P5-D to scan files outside the declared PLE target. This change binds the P5-D host audit **before any host probe** to the complete validated registry and derives the exact HF repo/revision, provisional served ID and asset ID from the manifest, rather than a separate source constant.

- New `scripts/manager/p5d_manifest_binding.py`: source-only, bounded manifest-based source binding for a registered PLE asset; fail closed for missing/invalid model, asset, pin and graph. Does not query Docker, GPU, API, `/proc`, filesystem cache, or a service.
- `scripts/manager/p5d_live_audit.py`: refuses the live read-only observation preflight when manifest binding is invalid; otherwise uses the manifest-derived repo, revision, candidate path marker and expected API ID. Adds a manifest binding summary and pin origin to the non-authorizing receipt.
- Wizard CLI: `./wizard.sh operations generic p5d-source-binding-review --model orcarouter --json`. Model-first interactive common qualification menu **14** performs the same source-only review. The existing `./wizard.sh manifest validate --json` remains the authoritative full graph validator.
- CPU-only regressions: `tests/test_p5d_manifest_binding_cpu.py` plus additions to `tests/test_p5d_live_audit_cpu.py` and `tests/test_generic_console_cpu.py`. Negative fixtures assert no host probe on invalid source binding and use of manifest-supplied repo/revision instead of hardcoded values.

## Acceptance distinctions

- `DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED` + command RC0 means only that the **source manifest binding** is valid. It is NOT a PLE residency, inode, Docker port owner, GPU or production acceptance.
- `BLOCKED_MANIFEST_BINDING` (review) and `BLOCKED_MANIFEST_PREFLIGHT` (host audit) prevent a mismatched PLE/model pin from being treated as a valid audit; no host process capture is attempted in the latter case.
- The historical DGX private receipt still showed smaps unreadable on 3/3 PIDs, blank namespace IDs, PLE RSS/PSS unobserved, unmapped LISTEN inode↔PID and missing independent NAT ownership. The new manifest binding **does not repair operating-system permission gaps or retroactively qualify the live receipt**.
- Source edits and tests were created through GitHub connection. **No independent CPU execution, exact-head GitHub CI run, or new DGX read-only probe is claimed in this GitHub-only write.** Existing 50/50 P5-D operator CPU receipt belongs to older SHA `08d03b182c3a1be78a698312d1abcb5b2cef571e`.

## CPU verification commands (operator checkout, source-only)

```bash
git pull --ff-only
git rev-parse HEAD
python3 -B -m unittest discover -s tests -p 'test_p5d_manifest_binding_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_p5d_live_audit_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_generic_console_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_manifest_registry_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_generic_operations_cpu.py' -v
python3 -B -m wizard manifest validate --json
python3 -B -m wizard operations generic p5d-source-binding-review --model orcarouter --json
```

No `p5d-readonly-once.sh`, `--save`, sudo, Docker exec, GPU inference, model switching, operating Journal change, main update, PR merge or Production Release is authorized or performed by this source update.

**Next P5-D live acceptance remains separate:** explicit read-only operator authorization and a fresh P5-D receipt with per-PID smaps access classification, actual file RSS/PSS/inode and pinned snapshot aliases, valid namespace identity and independent NAT-to-container provenance. An RC3 on unqualified evidence must not be interpreted as a failed running service.
