# Blazux DGX Spark — P1–P8 execution roadmap (2026-11-19 KST)

This is the **current actionable roadmap** rather than a historical completion override. Stage receipts in `handoff/EVIDENCE-LEDGER.md`, original dated runbooks and exact commit-bound logs remain the evidence source. Avoid interpreting an old "PENDING" line as current after a newer receipt. Draft PR #1 is **Open / Unmerged**, with no authorization to merge or release.

```text
M0 — CPU CI / reproducible evidence and exact SHA
        |
        +------------------+
        |                  |
M1 — P5 observed      M2 — P6 journal/nonce
     measurements          safety SOURCE
        |                  |
        +---------+--------+
                  |
M3 — P7 actual gateway/proxy/storage/Wizard checks
                  |
M4 — P8 bounded approved fault/restore and final Go/No-Go
```

## Status

| Phase | Accepted scope | What is still not accepted |
| --- | --- | --- |
| P1 Flash-Next | Actual DGX pinned runtime/API/Tools/Vision, bounded benchmark/backend historical PASS | Generic Wizard lifecycle and future release UX separately |
| P2 NVIDIA 27B | Actual DGX pinned download/runtime/API, historical bounded benchmark/restore PASS | Native tool recipe and generic lifecycle operator UX separately |
| P3 Flash↔27B | Historical A/B/C/G real bidirectional transitions PASS/CLOSED, D read-only checks and F source tests | P3-E reinstall, *general* model-independent recovery/executor not released; do not replay original stages |
| P4 Storage | Actual read-only capacity inventory A and safe dry-run B/C PASS | Deletion/reinstall optional, no automatic approval |
| P5 Orcarouter MTP0 | Existing active v3 development trial/API, P5-C correlation; 256-token reasoning 1K/4K TTFT **0.52965s / 1.70999s**, post-first TPS **22.405 / 22.604**, stable Docker ID; 65 targeted CPU tests PASS with exact CPU run SHA not in receipt | TTFC still unobserved in default-thinking; current newly authorized visible-TTFC one-shot **CODE READY / OPERATOR EXECUTION PENDING**. PLE unique RSS, NAT host listener identity, GPU exclusivity, loaded memory thresholds, MTP2/Tools/Vision and runtime qualification separate |
| P6 generic Journal | A/B/C/D/E source + Fake-DGX contracts, fsync/nonce/replay negatives, read-only always-blocked gates | Real independently authenticated durable operating Journal v2 and nonce, authorized executor/live transfer/auto-resume blocked |
| P7 Integration | Model-agnostic source service/proxy/gateway/storage and Wizard review implemented | Independently observed real component/endpoint/identity continuity |
| P8 Recovery/Signoff | 24 baseline + 66 extended + 48 fake-disk synthetic cases (distinct matrices), source-only review | Approved real fault injection, rollback, live restore observation, final Go/No-Go, production release |

## Recommended order

1. **M0 CI** — establish actual Actions workflow registration/permissions/actor; after 2026-11-11 historical success SHA `8b118c8`, recent feature commits have no observed Actions runs. Do not count old green runs as new-HEAD PASS or merge to force workflow. Run/read CPU tests on exact clean SHA and label operator receipts separately.
2. **M1 P5** — complete currently approved bounded visible-TTFC one-shot on existing Orcarouter MTP0 *without restarting it*; preserve prior 256-token default-thinking receipt. CPU source/tests first. Integrate before/after resources, private receipt and Qwen request-local no-thinking control. Then source/read-only bounded PLE smaps/inode/worker-set and Docker NAT host-process evidence; never infer PLE unique physical residency from sum of process RSS. Model-agnostic metrics shared across the registry; quantization/MTP/PLE/Tools/Vision stay per-adapter.
3. **M2 P6-E** — source/Fake-DGX only: independently trusted fresh approval binding, nonce no-replay across crashes, Journal v2 crash consistency, state continuity, bounded read-only restart reviewer. Keep real Executor permanently blocked until separate qualified deployment and authorization.
4. **M3 P7** — independently capture live service, Proxy, Gateway, OpenWebUI, Storage, :8000/v1 and served-ID continuity in safe/read-only mode; model selection UX may show only evidence-appropriate statuses.
5. **M4 P8** — only under a different scoped downtime/fault approval, verify exact real model transition, fault injection, automated rollback and final integrated operator signoff. No real recovery claim from Fake-DGX simulations.

## Security and acceptance invariants

- DGX Spark GB10; **vLLM 0.32.0**, **no SGLang**, **ONE_ACTIVE_MODEL_ONLY**, host `:8000/v1`; preserve current OpenWebUI/Portainer, images, caches, PLE files, original operating journals and old evidence.
- Model switch, service restart/stop, Docker mutation, CPU governor/cgroup actuation, persistent operating Journal migration, cleanup, fault injection, PR merge and production release each require **separate explicit approval**.
- Private resource/benchmark evidence != cryptographic authentication or proof of independent GPU/port process ownership. RC3 `BLOCKED_PARTIAL_PROCESS_EVIDENCE` denotes non-authorizing observation, **not** an outage.
- Current verdict: `P1-P4_SCOPED_HISTORY_ACCEPTED / P5_MTP0_REASONING_TTFT_TPS_MEASURED / P5_VISIBLE_ONESHOT_SOURCE_READY_NOT_EXECUTED / P6-E_SOURCE_ONLY / P7_REAL_PENDING / P8_REAL_PENDING / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

Relevant docs: `docs/P1-P8-WIZARD-ACCEPTANCE-STATUS-20261107.md`, `docs/P3-P5-ONE-TURN-CLOSEOUT-20261118.md`, `docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md`, `docs/P8-FAULT-RECOVERY-FINAL-OPERATIONS-ACCEPTANCE-PLAN-20261107.md`, `handoff/NEXT-ACTIONS.md`.
