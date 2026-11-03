# Evidence ledger — observed facts and test reports

Use an append-only entry for every meaningful result. Never substitute README claims or previous chats for locally reproduced tests.

## Entry template

| Field | Value |
|---|---|
| ID / KST | `E-YYYYMMDD-NN` / timestamp |
| Model / recipe / revision | full id + immutable revision |
| Git HEAD / branch | exact actual SHA and branch |
| Runtime image / host | immutable digest, vLLM version, GPU/driver/OS |
| Scope | SOURCE / CPU / CI / GPU / API / SWITCH / RELEASE |
| Exact invocation | command/environment; redact secrets |
| Inputs | test names, prompt/seed hashes, dataset scope |
| Result | PASS / FAIL / BLOCKED / NOT_RUN / NOT_APPLICABLE |
| Artifacts | paths/URLs/digests |
| Limits | scope, caveats, unresolved mismatches |

## E-20261104-01 — source-only planning baseline

- **Scope:** SOURCE / GitHub metadata and public source inspection, **not** GPU.
- **Repo:** `kjlee-inlct/qwen3.8-Flash-DGX`.
- **Source commit:** `blazux/qwen3.8-Flash-DGX@b0aa8b77604139557169387b2fa8386355d8b651`; user fork main same at branch creation.
- **Source observations:** `flash` and `profiles` cover NVIDIA and RadixArk Flash-Next; `scripts/serve.sh` removes container matching `NAME`; `feature/orcarouter-bf16-adapter` already holds a design doc; aphex3k 27B recipe uses SGLang, **not** local vLLM 0.32 proof.
- **Result:** `PASS_SOURCE_INSPECTION` for cited facts; `NOT_RUN` for CPU tests, CI, DGX runtime/benchmark.
- **Artifacts:** [Blazux source](https://github.com/blazux/qwen3.8-Flash-DGX/tree/b0aa8b77604139557169387b2fa8386355d8b651), [Orcarouter parallel branch design](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/blob/feature/orcarouter-bf16-adapter/docs/MODEL-CATALOG-AND-ORCAROUTER-ADOPTION.md), [27B external reference](https://github.com/aphex3k/Qwen3.8-27B-on-DGX-Spark).
- **Limits:** No current disk, container, memory or actual 27B vLLM evidence.

## E-20261104-02 — new planning branch and documentation

- **Scope:** GitHub SOURCE / documentation-only.
- **Branch base:** `feature/recipe-wizard-handoff` created from `b0aa8b77604139557169387b2fa8386355d8b651`.
- **Result:** Docs creation to be verified by GitHub branch readback and draft PR. **No CPU, CI, GPU or service tests run.** This entry does not qualify any runtime.
- **Artifacts:** `docs/MODEL-RECIPE-WIZARD-PLAN.md`, `docs/MANIFEST-CONTRACTS.md`, `handoff/*`.
- **Limits:** Manifest examples, wizard commands and state machines are designs, not implemented software.

## Historic evidence not transferred

Old Preview/YSLAB projects reported Orcarouter BF16 PLE/MTP results; those are **reference evidence only**, not proof of the new vLLM 0.32 fork. Historical Preview strict same-token logprob `1e-4` release blocker remains unresolved. DGX status is unobserved this session.

## Update policy

Append new measured entries, never replace failures. When rerunning a test, give it a new ID and reference prior entry. If an entry proves wrong, add an explicit correction with link; do not rewrite history. Publish non-sensitive artifact locations and keep credentials/private data out.
