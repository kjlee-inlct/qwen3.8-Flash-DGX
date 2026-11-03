# Handoff changelog (append-only)

## 2026-11-04 — H-001 — Recipe/Wizard migration planning initialized

- Confirmed user preference: **vLLM 0.32 only**, no SGLang, one large target at a time by default.
- Created planning branch `feature/recipe-wizard-handoff` from fork `main@b0aa8b77604139557169387b2fa8386355d8b651`.
- Preserved parallel `feature/orcarouter-bf16-adapter` design branch.
- Defined P0→P7 roadmap, manifest separation, wizard steps, protected runtime boundaries, gated checkpoint deletion and switch/rollback semantics.
- Added a standard entrypoint, living current state, evidence ledger, decisions, next tasks and new-conversation prompt under `handoff/`.
- **Tests:** documentation/source review only. No new CPU/CI/GPU/benchmark runs; no Docker, HF weights, model or service changes.
- PR/CI state should be read from GitHub; do not infer a merge.

## Future entry template

`YYYY-MM-DD — H-NNN — Subject`: exact changes, files, branch/commit, PR, test outcomes, external effects, remaining blockers. Newer entries should be placed **above** older entries while preserving them.
