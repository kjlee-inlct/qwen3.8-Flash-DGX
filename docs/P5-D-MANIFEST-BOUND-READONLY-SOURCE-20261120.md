# P5-D source-side manifest binding and Wizard read-only review (2026-11-20 KST)

## Scope and rationale

P5-D previously duplicated the Orcarouter HF repository/revision in the host audit module. The shared seven-document Wizard manifest graph already records the model checkpoint, pinned revision, PLE asset, discovery, loader capability and runtime policy. A source-level drift could otherwise cause P5-D to scan files outside the declared PLE target. This change binds the P5-D host audit **before any host probe** to the complete validated registry and derives the exact HF repo/revision, provisional served ID and asset ID from the manifest, rather than a separate source constant.

- New \`scripts/manager/p5d_manifest_binding.py\`: source-only, bounded manifest-based source binding for a registered PLE asset; fail closed for missing/invalid model, asset, pin and graph. Does not query Docker, GPU, API, \`/proc\`, filesystem cache, or a service.
- \`scripts/manager/p5d_live_audit.py\`: refuses the live read-only observation preflight when manifest binding is invalid; otherwise uses the manifest-derived repo, revision, candidate path marker and expected API ID. Adds a manifest binding summary and pin origin to the non-authorizing receipt.
- Wizard CLI: \`./wizard.sh operations generic p5d-source-binding-review --model orcarouter --json\`. Model-first interactive common qualification menu **14** performs the same source-only review. The existing \`./wizard.sh manifest validate --json\` remains the authoritative full graph validator.
- CPU-only regressions: \`tests/test_p5d_manifest_binding_cpu.py\` plus additions to \`tests/test_p5d_live_audit_cpu.py\` and \`tests/test_generic_console_cpu.py\`. Negative fixtures assert no host probe on invalid source binding and use of manifest-supplied repo/revision instead of hardcoded values.

## Acceptance distinctions

- \`DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED\` + command RC0 means only that the **source manifest binding** is valid. It is NOT a PLE residency, inode, Docker port owner, GPU or production acceptance.
- \`BLOCKED_MANIFEST_BINDING\` (review) and \`BLOCKED_MANIFEST_PREFLIGHT\` (host audit) prevent a mismatched PLE/model pin from being treated as a valid audit; no host process capture is attempted in the latter case.
- The historical DGX private receipt still showed smaps unreadable on 3/3 PIDs, blank namespace IDs, PLE RSS/PSS unobserved, unmapped LISTEN inode↔PID and missing independent NAT ownership. The new manifest binding **does not repair operating-system permission gaps or retroactively qualify the live receipt**.
- Source edits and tests were created through GitHub connection. **No independent CPU execution, exact-head GitHub CI run, or new DGX read-only probe is claimed in this GitHub-only write.** Existing 50/50 P5-D operator CPU receipt belongs to older SHA \`08d03b182c3a1be78a698312d1abcb5b2cef571e\`.

## CPU verification commands (operator checkout, source-only)

\`\`\`bash
git pull --ff-only
git rev-parse HEAD
python3 -B -m unittest discover -s tests -p 'test_p5d_manifest_binding_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_p5d_live_audit_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_generic_console_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_manifest_registry_cpu.py' -v
python3 -B -m unittest discover -s tests -p 'test_generic_operations_cpu.py' -v
python3 -B -m wizard manifest validate --json
python3 -B -m wizard operations generic p5d-source-binding-review --model orcarouter --json
\`\`\`

No \`p5d-readonly-once.sh\`, \`--save\`, sudo, Docker exec, GPU inference, model switching, operating Journal change, main update, PR merge or Production Release is authorized or performed by this source update.

**Next P5-D live acceptance remains separate:** explicit read-only operator authorization and a fresh P5-D receipt with per-PID smaps access classification, actual file RSS/PSS/inode and pinned snapshot aliases, valid namespace identity and independent NAT-to-container provenance. An RC3 on unqualified evidence must not be interpreted as a failed running service.
