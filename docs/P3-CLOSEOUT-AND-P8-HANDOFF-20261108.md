## 2026-11-08 — Actual DGX P3-E/F read-only closeout complete; P4-A inventory NEXT

**Observed on actual DGX after fast-forward to `0421b46`:** P3-E `flash_host_assets` status `LOCAL_ASSET_METADATA_OBSERVED_REINSTALL_UNQUALIFIED`, issues=[], 31,907,813-byte index, 299,845 weight-map entries (400,000 cap), **11 shards** total apparent size **129,771,270,410 bytes**, metadata hashes and mounted template SHA-256 observed. Checkpoint weights not hashed (`large_shard_hashes_verified=false`), pinned published revision bytes not independently verified (`verified_model_revision=false`), reinstall not qualified. P3-F real DGX **168/168 CPU PASS (7 suites)**, `PRODUCTION_LIFECYCLE_RELEASED=false`. Current `qwen38-27b` API `qwen3.8-27b`, host :8000, 8/8 service checks true and `LIVE_SERVICE_VERIFIED`; service-status command does not independently validate GPU/PID ownership. All commands read-only and no service mutation.

**P3 disposition:** A/B/C/G historical actual operator-approved PASS/CLOSED; D independent read-only PASS historically; E source/host-asset metadata handoff COMPLETED but **not** real reinstall; F source/CPU handoff COMPLETED but **not** production lifecycle. **P8 remains owner** of full Flash recipe/install validation, actual reinstall/rollback, deliberately induced failure/automatic recovery and final release (all real work NOT_RUN). No replay, no automatic source launch.

**New operator instruction supersedes prior P4 hold ONLY for read-only P4-A:** implement capacity and current-state inventory via Wizard *before* considering any deletion. P4-B candidates and P4-C cleanup remain not started and unauthorized. Read `docs/P4-A-STORAGE-CAPACITY-AND-ASSET-INVENTORY-20261108.md`. P4-A is SOURCE IMPLEMENTED, DGX CAPACITY OBSERVATION NOT_RUN. Latest P4-A CPU/Fake-DGX CI [42395243458](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42395243458): **887/887 PASS, 40 groups**; no real disk capacities have been measured by the new Wizard in the conversation.

---

# P3 closeout and P8 acceptance handoff — 2026-11-08

## Scope decision

**P3 closeout only. P4 is NOT_STARTED / OPERATOR_HOLD.** The premature P4 module, CPU tests, and CI additions were fully reverted at commit [1110681](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/1110681f451bc72470454bbbee1e1d79d6406a1d), [CI 42393129150](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42393129150) SUCCESS. Do not work on P4 until separately directed. Source-preparation handoff does not release the production lifecycle or assert successful canonical reinstall.

## Stage closure matrix

| Stage | Evidence already verified | Remaining P3 closeout | P8 handoff | Verdict |
| --- | --- | --- | --- | --- |
| P3-A/B/C | Original operator-approved one-off real DGX transfers; immutable historical receipts | Source and receipt references only; **no replay** | None | REAL PASS / CLOSED |
| P3-D | Independent GPU PID and IPv4/IPv6 docker-proxy :8000 ownership read-only PASS with opted-in sudo ss | Record exact latest evidence; **no repeat required** | None | READ_ONLY_PASS (at measured time) |
| **P3-E** | NVIDIA Flash-Next source rev `fc694b54fb0174e0913e6adf86691ef85a4ead47`, prepared `-fp8hybrid`, strict Flash command flags, 500k/Yarn/MTP2/native tools and documented-field comparison PASS; unregistered nonlaunchable draft | **Read-only DGX `flash_host_assets --json` after 400k-key source fix**, to inspect real index-referenced shard presence/size and template hash. Preserve any remaining blocker in evidence | Complete image/cache/template/env/network/security/restart provenance, canonical executable Flash recipe qualification, independently approved real fresh reinstall | SOURCE PREPARED, HOST RECHECK PENDING, **NOT REAL REINSTALL QUALIFIED** |
| **P3-F** | 20 core lifecycle CPU tests and related Fake-DGX suites, stop/start/backup/failure truthfulness, no silent release; GitHub source CI PASS | Recheck **current 7-suite CPU-only** on DGX; retain current HEAD + actual count and `PRODUCTION_LIFECYCLE_RELEASED=False`. This is **no Docker/GPU operation** | Actual Flash installation/recreation/rollback/restart/idempotence/port+GPU provenance, production adapter enablement and evidence | SOURCE_CPU_PASS_NOT_RELEASED, LOCAL RECHECK RECOMMENDED |
| P3-G | Independent real 27B→Flash→27B successful transfers, two distinct operator approvals, exact served IDs, journal VERIFIED/COMMITTED, final 27B diff=[] | Preserve historical evidence; **no replay** | Deliberate injected failure and proven **automatic source restoration** (not repeat of successful G) | REAL PASS / CLOSED |
| **P4** | None required for P3 | **Do not start P4** | Not prerequisite for closing P3 source scope | **NOT_STARTED / OPERATOR_HOLD** |

### P3-E exact latest source/DGX evidence

- DGX operator read-only observed `model.safetensors.index.json` **31,907,813 bytes**, valid `weight_map` OBJECT with **299,845 keys**. Old 100,000 key cap blocked before enumerating shards; zero reported shard count therefore means **unexamined**, not missing/corrupt.
- Source [1a05eb2](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/commit/1a05eb2dfacda960527ba94da544e5f545d8793f) raised this parser's hard cap to 400,000 while retaining 128 MiB index byte maximum, 256 shard maximum, path containment, 8 MiB small metadata and 256 KiB template limits. [CI 42392758148](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42392758148) **880/880 CPU/Fake-DGX PASS, 39 groups**. **Real DGX rerun after the 400k fix has not been supplied**.
- Flash source draft remains `recipes/qwen38-flash-next.runtime.draft.json` with `launch_allowed=false` and `register_as_runtime_recipe=false`; no qualified canonical Flash recipe and no real reinstall result.

### P3-F source-only status

- `scripts/manager/model_lifecycle.py` release gate `PRODUCTION_LIFECYCLE_RELEASED=False`. Its real Docker creation adapter is still 27B-only; Fake-DGX orchestration does not prove Flash launch.
- Last operator DGX local P3-F six-suite result **153/153 CPU PASS** predates the newly added `test_flash_host_assets_cpu.py` seventh suite and subsequent fixes. Source CI 880 PASS is separate evidence, not a claim for the current local count.
- Remaining source closeout: one `--cpu-only` run of current seven suites on DGX and documentation of exact result. No P3-F real installation or fault injection needed to close **source-only** scope.

## Operator's two proposed final P3 checks — read-only

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff
python3 -m scripts.manager.flash_host_assets --json
python3 -m scripts.manager.p3_dg_acceptance --cpu-only
./wizard.sh service manager status --json
```

- On clean Flash asset evidence, mark E `SOURCE_READ_ONLY_PREPARED_HANDOFF` only, never `REAL_REINSTALL_PASS`. On error, preserve `failed_stage`, `failure_reason_code` as an explicit unresolved prerequisite. Do not adjust limits/model files automatically.
- On successful current seven-suite CPU result, mark F `SOURCE_CPU_HANDOFF_COMPLETE` only, never `PRODUCTION_RELEASED`.
- Record final P3 evidence ledger and draft PR; no P3-G replay and no P4 implementation.

## P8 execution and release prerequisites (NOT_RUN)

1. **P8-R0 — full runtime specification (source only):** Flash exact Docker command/context/Yarn/MTP/native tool parser, immutable image provenance (local image ID != registry digest), inherited vs runtime Env, cache and template bytes/permissions/writable legacy HF bind, network/security/restart/IPC, desired-vs-observed drift; lifecycle/approval/backup negative tests.
2. **P8-R1 — independently authorized real Flash reinstall:** Fresh exact plan SHA, active 27B/API/port/GPU ownership preflight, preserved prior source image/cache/container, distinct TTY downtime approval and bounded fresh create/start with recovery design. **No P3-G consent reuse.**
3. **P8-R2 — live functional/idempotence acceptance:** Flash served ID, API/chat/completions/tools/vision as applicable, benchmark, journal/receipt consistency, repeatability and authorized reversion to 27B. Distinguish manual restoration from automatic recovery; uncertain restore is FAIL.
4. **P8-R3 — separately authorized fault/auto-recovery and final go-live:** Controlled failure, actual automatic original restoration, hard timeout/rollback evidence, Wizard UX/security and final operator signoff, after relevant P5/P6/P7 integration gates. P8 real fault and release remain NOT_RUN/NOT_RELEASED.

R0–R3 are planning labels and cannot dispatch execution. Existing P8 Wizard commands remain INTERFACE_ONLY/BLOCKED.

## Non-negotiable operating rules

Single active GPU inference model (`ONE_ACTIVE_MODEL_ONLY`); vLLM 0.32, no SGLang; host :8000 fixed. Preserve original 27B recipe bytes, cached models, Docker image assets, historical receipts/journal. No P3 A/B/C/G replay, no P4 work or cleanup, no P8 live fault injection/reinstall or release-gate flip without a fresh explicit operator approval. PR #1 remains Open/Draft/unmerged.
