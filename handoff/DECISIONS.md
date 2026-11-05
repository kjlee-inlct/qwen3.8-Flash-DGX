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

| D-012 | 2026-11-05 | **User reaffirmed Wizard-first sequential P1–P7 delivery:** P1 Flash-Next implement+benchmark via Wizard → P2 27B implement+benchmark via Wizard → P3 bidirectional Flash-Next/27B switch via Wizard → P4 optional Flash-Next cleanup if disk constrained, via Wizard and exact approval → P5 Orcarouter-Flash-Next implement+benchmark via Wizard → P6 Orcarouter/27B switch via Wizard → P7 integrated operation. All steps must be Wizard-operable; CLI is underlying execution only; source CI ≠ DGX bench PASS. Preserve :8000/v1 external endpoint where feasible; vLLM 0.32 only, no SGLang. | DECIDED / ROADMAP LOCK; supersedes any task ordering that bypasses Wizard or promotes Orcarouter before P1–P3 verification; no GPU/deletion permission implied |

| D-013 | 2026-11-05 | While operator-owned `./flash setup default` is downloading, implement P1 Wizard source only; do not run competing download/prepare/start. Wizard must verify complete shards and image label, detect active setup, refuse Docker/name/port conflicts, use a fresh exact SHA-256 plan approval, keep benchmark bounded and record JSON evidence. Source CI ≠ DGX qualification. | DECIDED / SOURCE_IMPLEMENTED, GPU/delete not implicitly approved |

| D-014 | 2026-11-05 | User requested full P1–P7 **Wizard interface scaffold up front**, separately debug model-specific P1–P7 execution later. Use modular `wizard/menus/pN.py` files, shared router/contracts and both interactive `./wizard.sh` and headless `--stage/--action/--json` CLI. P1 retains existing approval/preflight implementation; P2–P7 default to read-only status/plan with no operational adapter/approval acceptance. Keep P1→P7 acceptance order unchanged. | DECIDED / SOURCE_IMPLEMENTED; GPU, switch, cleanup, gateway NOT_AUTHORIZED by scaffolding |

| D-015 | 2026-11-05 | **Supersedes D-014's numbered source-file layout:** classify Wizard by capability. Top-level Model management (P1/P2/P5), Model switching (P3/P6), Storage (P4), Operations (P7); descriptive submodules under `wizard/menus/models/`, `switching/`, `storage/`, `operations/`. Keep P identifiers and direct `./wizard.sh pN ...` / `--stage pN` as compatibility aliases. Group+item CLI and nested interactive menu use same handlers and guards. | DECIDED / SOURCE+CI PASS; DGX runtime NOT_RUN, P2–P7 execution BLOCKED |

| D-016 | 2026-11-05 | For repeatable user-mediated DGX workflows, develop **one Git-tracked temporary script per bounded milestone** in `scripts/temporary/`, accompanied by a CPU-only fake test, README lifecycle and handoff. User workflow is GitHub commit/CI → finish existing operator setup/serve tasks → `git pull --ff-only` → invoke one wrapper for preflight → separately approved Wizard verify/benchmark → evidence summary. Default read-only; no script-level auto-git-update, implicit operational approval, cache deletion, service disruption or secret log uploads. Temporary wrappers must be retired only by a reviewed commit after evidence is recorded; shared logic belongs in permanent Wizard modules. | DECIDED / SOURCE IMPLEMENTATION IN PROGRESS; DGX/GPU NOT_RUN |

### Design choices not yet finalized

- Remaining runtime/service/inventory contract fields and wizard flags. The source-only N1 recipe schema has been implemented.
- Whether 27B NVFP4/BF16-head vLLM 0.32 support can use stock backend or requires an opt-in patch; exact checkpoint and draft engine mode.
- Proxy/gateway implementation and host port layout; any port or model alias changes require operational approval.
- GPU benchmark thresholds, allowable downtimes, retention policies and available disk capacity.
- Integration strategy and merge ordering of Orcarouter adapter and this management branch.

### When creating a decision

Add a dated ID, why, alternatives, evidence, affected files/branches, rollback if relevant and approval boundary. If reversing a decision, append a superseding ID; never silently overwrite.
