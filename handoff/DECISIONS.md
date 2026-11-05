# Decision record — accepted constraints vs proposals

Record what has been **decided** and what still needs approval. Proposals in docs are not automatically accepted implementations.

| ID | Date | Decision | Status / boundary |
|---|---|---|---|
| D-001 | 2026-11-04 | Use **Blazux vLLM 0.32 only**, no SGLang engine; aphex3k is tuning/benchmark reference | DECIDED |
| D-002 | 2026-11-04 | Keep NVIDIA/RadixArk existing Blazux capability while adding Orcarouter and 27B via model-specific opt-in recipes | DECIDED as target architecture; NOT_IMPLEMENTED |
| D-003 | 2026-11-04 | Create new `feature/recipe-wizard-handoff` branch from fork `main`; preserve `feature/orcarouter-bf16-adapter` separately | DECIDED / branch created |
| D-004 | 2026-11-04 | P0→P7 order: Flash-Next benchmark, 27B benchmark, switch test, **conditional Flash-Next cleanup**, Orcarouter benchmark, switch test, release gate | DECIDED as roadmap; all GPU work gated |
| D-005 | 2026-11-04 | Manage model as recipes, manifests, bounded wizard steps, service/proxy/gateway, Docker and storage inventory | DECIDED as design target; NOT_IMPLEMENTED |
| D-006 | 2026-11-04 | Preserve current original Orcarouter container, its API clients, data/image; explicit scoped approval before stateful GPU ops, restart or deletion | DECIDED / hard safety rule |
| D-007 | 2026-11-04 | Model deletion may be necessary due to storage; approve **exact candidate plan**, not automatic stage advancement | DECIDED / no deletion authorized |
| D-008 | 2026-11-04 | Single large active GPU model by default; stable gateway later, not at the expense of operating port `:8000` | DESIGN ASSUMPTION pending capacity/operations tests |
| D-009 | 2026-11-04 | Existing numerical strict `1e-4` Orcarouter release gate remains unresolved; no implied release PASS | DECIDED / release block |

| D-010 | 2026-11-04 | Implement N1 recipe with YAML + JSON Schema Draft 2020-12, CPU PyYAML/jsonschema verifier, required full pinned source/model SHA and Docker image digest, vLLM 0.32 only, and no launch/deletion approval bypass. 27B candidate stays invalid. | DECIDED / SOURCE_ONLY; not runtime authorization |

| D-011 | 2026-11-05 | User reports old services removed and asks Blazux default NVIDIA Flash-Next to occupy previous host API `:8000/v1`; model ID uses Blazux `qwen3.8-flash-next` (not the old Orcarouter identifier); keep vLLM 0.32 default profile and no SGLang. Remove static ban on 8000 and historic container name, replacing with live Docker/socket collision check. Never implicitly rm -f a container. | DECIDED / SOURCE_CHANGE; actual host deployment NOT_OBSERVED/NOT_RUN, supersedes D-006 and D-008 **only for presumed presence and reserved port**, not for protection of any actual resources |

### Design choices not yet finalized

- Remaining runtime/service/inventory contract fields and wizard flags. The source-only N1 recipe schema has been implemented.
- Whether 27B NVFP4/BF16-head vLLM 0.32 support can use stock backend or requires an opt-in patch; exact checkpoint and draft engine mode.
- Proxy/gateway implementation and host port layout; any port or model alias changes require operational approval.
- GPU benchmark thresholds, allowable downtimes, retention policies and available disk capacity.
- Integration strategy and merge ordering of Orcarouter adapter and this management branch.

### When creating a decision

Add a dated ID, why, alternatives, evidence, affected files/branches, rollback if relevant and approval boundary. If reversing a decision, append a superseding ID; never silently overwrite.
