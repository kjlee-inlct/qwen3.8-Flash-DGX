> **CURRENT, 2026-11-06 (D-021):** Full P1–P7 TTY Wizard implemented as one **model-first console**; see `wizard/console.py`, `wizard/workflow.py`, and `wizard/roadmap.py`. Older domain-based PRIMARY menu text below is preserved as historical contract. The old model/switch/storage/operations/legacy P1–P7 CLI handlers **remain supported**. Source UI complete does **not** mean P2–P7 execution is approved or DGX qualified. `nvidia/Qwen3.8-27B-NVFP4` download was operator-reported STARTED, completion unknown.

### Current operator menu (source)

```text
Blazux Wizard — one GPU model / port 8000
1. Select / run model
   1. NVIDIA Flash-Next
   2. NVIDIA 27B
   3. Orcarouter Flash-Next
   After selection: 1 Continue recommended step / 2 All model actions / 3 Refresh
   Model actions: inspect, download, prepare, start, wait, verify,
                  benchmark, switch, rollback, recipe
2. Service health / status / logs
   status, health, logs (read-only); start, stop, restart, rollback,
   proxy, gateway (guarded and blocked until executor qualified)
3. Advanced / recipes / storage
   P3 switch pair selection, P4 selective cleanup, P6 switch pair,
   P7 proxy/gateway/acceptance plan, legacy stage tools, readiness dashboard
0. Exit
```

CLI entrypoints:
```bash
./wizard.sh
./wizard.sh select 27b --json
./wizard.sh workflow 27b --json
./wizard.sh workflow 27b --for-action start --json
./wizard.sh roadmap --json
./wizard.sh service manager status --json
./wizard.sh service manager health --json
./wizard.sh service manager logs --json
./wizard.sh model 27b status --inspect-cache --json
./wizard.sh model 27b download --guided    # only after no transfer running
./wizard.sh p1 plan --for-action verify --json
./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json
```

**Approval and execution:** P1 individual guarded actions call the existing P1 backend; a P2 missing-checkpoint download calls the existing exact revision/plan approval backend. The source UI does not synthesize approvals or pass `--execute`; P2–P7 runtime actions remain `BLOCKED`. Current service status is derived from live Docker/socket, while API model identity uses bounded `GET /health` + `GET /v1/models`; service logs use an opt-in bounded `docker logs --tail 40` only for the observed managed container. Running containers are not GPU verification. All reports are read-only and release `PASS` requires actual DGX/benchmark/recovery evidence.

# Blazux P1–P7 Wizard — CLI and menu contract

**2026-11-05.** Single operator-facing entrypoint: `./wizard.sh` or `python3 -m wizard`. **Execution engine: vLLM 0.32 only; SGLang excluded.** All stages have separate modules in `wizard/menus/models/flash_next.py` … `p7.py`. They share the central router in `wizard/main.py`, common fail-closed contract in `wizard/menus/common.py`, and external `:8000/v1` target.

## Primary domain-based navigation (current)

**Current navigation contract (2026-11-05, D-015):** Wizard primary menus are **Model management** (`model flash-next` = P1; `model 27b` = P2; `model orcarouter-flash-next` = P5), **Model switching** (`switch flash-next-27b` = P3; `switch orcarouter-27b` = P6), **Storage management** (`storage flash-next` = P4) and **System operations** (`operations system` = P7). Source files live in explanatory category directories, not numbered `pN.py` files. **P1–P7 are retained as stable roadmap identifiers and backwards-compatible CLI aliases**, not the primary UI/file organization. The P1 core remains guarded; P2–P7 remain source-only and execution BLOCKED.

```bash
./wizard.sh                                   # four primary menus, then submenu choice
./wizard.sh list --json                       # grouped catalog + P1–P7 stage metadata
./wizard.sh model flash-next status --json
./wizard.sh model 27b status --json
./wizard.sh model orcarouter-flash-next status --json
./wizard.sh switch flash-next-27b plan --for-action switch --from-model flash-next --to-model 27b --json
./wizard.sh switch orcarouter-27b plan --for-action switch --from-model orcarouter --to-model 27b --json
./wizard.sh storage flash-next status --json
./wizard.sh operations system status --json
# Equivalent automation syntax:
./wizard.sh --group model --item flash-next --action status --json
# Backward compatibility:
./wizard.sh p1 status --json
./wizard.sh --stage p3 --action switch --from-model flash-next --to-model 27b --json
```

The catalog reports both `groups` and a flat `stages` list. P-stage IDs remain stable for evidence/handoff and existing scripts. **P2–P7 actions still return BLOCKED**; a direct CLI interface is not authorization to execute unvalidated work.

## Supported entry modes

| Mode | Example | Behavior |
|---|---|---|
| Interactive | `./wizard.sh` | Choose P1–P7. P1 opens existing per-step confirmation menu. Others expose safe inspection/plan choices only |
| List | `./wizard.sh list --json` | Returns all seven modules and implementation states |
| Status | `./wizard.sh p1 status --json` | P1 current local inventory/model check; may report blockers without failing the inspection |
| Direct stage/action | `./wizard.sh --stage p1 --action plan --for-action verify --json` | Same P1 handler as interactive UI |
| P2 plan | `./wizard.sh p2 plan --for-action prepare --json` | Structured BLOCKED response until 27B compatibility and adapter acceptance |
| P3 switch plan | `./wizard.sh p3 plan --for-action switch --from-model flash-next --to-model 27b --json` | Structured BLOCKED; never changes live services |
| P4 storage plan | `./wizard.sh p4 plan --for-action retire --target flash-next --json` | Structured BLOCKED; no deletion |
| P5/P6/P7 | `./wizard.sh p5 status --json` | Stage-specific read-only inspection/plan interface |

**Do not equate a menu's presence with an implemented operation.** The router is implemented for P1–P7 in SOURCE/CI. Only P1 delegates to the previous guarded P1 engine. P2–P7 are **INTERFACE_ONLY**, with `operations_enabled=false`, `executed=false`, `plan_id=null` and a nonempty blocker list on any action plan.

## Machine interface conventions

- Preferred syntax: `./wizard.sh <p1..p7> <status|plan|action> [options] --json`. Alternative: `./wizard.sh --stage p3 --action switch [options] --json`.
- Every P2–P7 object contains `schema_version=1`, stage ID, state, implementation, prerequisites, blocker reasons and `executed=false`. P1 has its original JSON shape from `p1_wizard.py`; harmonizing detailed P1 schemas is later implementation work, not an undocumented guarantee.
- Exit 0: an inspection or supported plan succeeded; inspect the **status field** because `status` can still display BLOCKED readiness.
- Exit 2: syntax/unknown stage errors (P1's own action failures may also use 2).
- Exit 3: operation blocked, unimplemented or approval/plan not valid. Other nonzero codes are errors and must not be interpreted as PASS.
- `--json` never requests user input; `guided` with `--json` is rejected. A non-TTY invocation with no arguments prints stage inventory rather than prompting. `--dry-run` with `--execute` is refused.
- `--execute` has **no effect** on unimplemented P2–P7 except a BLOCKED response, even if a fake `--approve-plan` value is supplied. The common router does not perform any Docker/GPU/network/deletion operation.
- The P1 backend is **different**: it may really prepare/start/verify/benchmark after a current, full matching SHA-256 `plan_id`, a second preflight, and an operator's explicit decision. It refuses incomplete checkpoint, active download/setup, insufficient Hybrid preparation, wrong image, occupied port or container name.

## P1 operator workflow after existing setup finishes

The uploaded DGX terminal log showed a successful vLLM 0.32 Docker build, model download **9/25 files (36%) at last visible line**, and a user shell with `./flash setup default`, then `./flash serve default`, `./flash wait`, `./flash test` queued. **Do not interrupt that shell, change the active worktree, duplicate setup or launch another service.** Once all have exited, inspect (read-only):

```bash
git status --short --branch
git pull --ff-only
./wizard.sh list --json
./wizard.sh p1 status --json
./wizard.sh p1 plan --for-action verify --json
```

If `qwen38-flash` is already running, **skip** P1 `prepare` and `start` and use the current exact per-action plan to approve `verify` then `benchmark`, when separately scoped. Example P1 commands:

```bash
./wizard.sh p1 plan --for-action verify --json
./wizard.sh p1 verify --execute --approve-plan FULL_CURRENT_VERIFY_PLAN_ID --json

./wizard.sh p1 plan --for-action benchmark --requests 3 --max-tokens 64 --seed 1234 --json
./wizard.sh p1 benchmark --execute --approve-plan FULL_CURRENT_BENCH_PLAN_ID \
    --requests 3 --max-tokens 64 --seed 1234 --json
```

Those examples are **not authorizations to run them now**. They require a completed, healthy checkpoint/service, a new matching plan hash, and deliberate operator approval. Execution evidence goes to `~/.local/state/blazux-wizard/p1/` unless overridden. No automatic rollback exists yet; no action automatically deletes HF cache or Docker resources.

## Stage boundary table

| Stage | Menu module | Next integration required |
|---|---|---|
| P1 NVIDIA Flash-Next | `wizard/menus/models/flash_next.py` | Actual DGX P1 Wizard functional and benchmark acceptance, rollback proof |
| P2 27B | `wizard/menus/models/qwen_27b.py` | Pinned recipe, vLLM 0.32 source/CPU compatibility, model preparation/bench |
| P3 Flash-Next ↔ 27B | `wizard/menus/switching/flash_next_27b.py` | Transactional switch, readiness gate, repeat A→B→A and rollback |
| P4 optional Flash-Next cleanup | `wizard/menus/storage/flash_next_cleanup.py` | Capacity check, canonical exact candidates, shared refs, independently approved delete path; otherwise SKIP |
| P5 Orcarouter | `wizard/menus/models/orcarouter_flash_next.py` | BF16 PLE/MTP overlay adapter, numeric qualification and benchmark |
| P6 Orcarouter ↔ 27B | `wizard/menus/switching/orcarouter_27b.py` | Bidirectional switch/rollback, verified API model IDs |
| P7 integrated operations | `wizard/menus/operations/system.py` | Service/proxy/gateway/storage managers, audit, production rollout and rollback |

The accepted execution/acceptance order remains P1→P2→P3→conditional P4→P5→P6→P7. Source scaffolding for later stages does **not** authorize skipping earlier runtime gates.

## Next implementation tasks

1. Fix source/CI failures and make machine interface consistent across commands (including P1 payload versioning), while preserving legacy P1 scripts.
2. Complete DGX P1 verification/benchmark using **existing** downloaded/serving assets and record JSON evidence.
3. Implement P2-specific vLLM 0.32 pinned source adapter and CPU compatibility tests, then progress along the stage order; P3/P4/P5/P6/P7 adapters stay disabled until validated.
