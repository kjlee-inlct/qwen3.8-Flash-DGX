# Blazux DGX Spark — P1–P8 execution roadmap (2026-11-19 KST)

## 2026-11-19 KST — P5-D additional source-only hardening and CI gate

**Source commit `f8525988ea800eb44855558aa932a4ce1d1d3dab`:** PID identity checks now require positive start ticks and each explicit `netns`, `mntns`, `pidns` value; bounded `scandir` prevents pre-limit full snapshot enumeration; namespace TCP reads are capped; numeric `smaps_errno` reaches per-PID summaries. Four CPU-only regression tests were **ADDED BUT NOT EXECUTED**. Earlier 40/40 PASS belongs exclusively to operator source `4366f3b`, not to this new code.

**GitHub inspection:** feature branch had the CPU workflow and matching push/PR filters; `main` had no `.github/workflows/` directory. Last observed workflow run: 2026-11-12 KST at older `8b118c8`. New HEAD CI **UNVERIFIED**; root cause of missing runs not established. Default-branch registration is only a hypothesis.

**P5-D evidence stays blocked:** original DGX receipt was `BLOCKED_PARTIAL_PROVENANCE / RC3`, three unreadable smaps, blank namespaces, no matched socket FD owner and no proven NAT datapath. PLE per-file RSS/PSS, pinned tensor content identity, unique GB10 residency and kernel NAT owner remain **UNQUALIFIED**. No repeat real DGX probe, GPU workload, service mutation, sudo, Journal write or PR merge. Historical P5 visible GPU measurements are unchanged.

**Independent gates:** SOURCE_IMPLEMENTED=yes; CPU_TESTED=new HEAD not run; CI_VERIFIED=no; DGX_OBSERVED=historical receipt only; OPERATION_AUTHORIZED=no; PRODUCTION_RELEASED=no. Keep PR #1 Draft/Open. Next: CPU/Fake-DGX test execution, GitHub Actions workflow registration investigation, then separately approved read-only evidence collection if required. P6-E durable nonce/Journal v2, P7 proxy/storage, P8 recovery acceptance remain blocked by their own evidence and approvals.

---


## 2026-11-19 KST — original P5-D full receipt uploaded; analysis CORRECTED

The operator uploaded the actual private `orcarouter--20261119T004619880648Z--bd848453cb4f.json` (9,661 bytes), sourced from exact clean DGX SHA `4366f3b1476105c6f556e0e93c4f5e1da64f68fa`, 2026-11-19 00:46:16–00:46:19 UTC. Full per-PID review: all three Docker host PIDs `4016083/4016529/4016530` match container ID in cgroup, before/after Docker PID set stable, GPU compute PID 4016530 in Docker PID subset, API ID confirmed. **All three smaps captured ZERO bytes** (`SMAPS_UNREADABLE`); therefore per-file RSS/PSS **UNKNOWN due read failure**, *not zero*. Pinned source snapshot inode aliases `0` / directory unreadable; model content/PLE cannot be attributed. **All three PID netns/mntns/pidns were empty strings before AND after**; earlier `pid_identity_continuous=true` was misleading because equal empty strings do not prove namespace continuity. One container TCP LISTEN inode observed but no matching FD host PID; `PID_NETNS_DRIFT` in old code is a misclassification for empty reference namespace. Docker declared/effective port 8000 both true on bridge, but raw bindings are not saved; old `DOCKER_DECLARATION_MISMATCH` cannot prove real IP config mismatch (possible dual-stack normalization). `iptables-save` unavailable, no independently authenticated NAT owner or GPU exclusivity.

**Original run remains RC3 / BLOCKED_PARTIAL_PROVENANCE**, not an outage or release. The later source patches already require nonempty namespace IDs, classify smaps errors, close fd enumerators and tolerate only exact Docker dual-stack wildcard; these **were not executed** in the uploaded original run. **No automatic host rerun, sudo, GPU inference, service mutation, PR merge, Journal writes or production release.** Full details [P5-D private receipt evidence review](../docs/P5-D-READONLY-ONE-TURN-RESULT-20261119.md). Current source CPU/Actions after patches still unverified. Next source/read-only work: characterize errno and exact live Docker bindings under separate bounded operator execution only if needed; no new work without further approval.

**Current classification** `P5D_FULL_RECEIPT_REVIEWED / P5D_API_DOCKER_PID_CGROUP_CORRELATED / P5D_SMAPS_UNREADABLE_3_OF_3 / P5D_NETNS_VALUES_EMPTY / P5D_PLE_AND_NAT_OWNER_UNVERIFIED / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---

## 2026-11-19 KST — actual P5-D one-turn RC3 source-bound; diagnosis and safe source fixes

Operator ran `scripts/temporary/p5d-readonly-once.sh` on clean source SHA `4366f3b1476105c6f556e0e93c4f5e1da64f68fa`: P5-D live audit CPU **14/14 PASS**, P5 attribution CPU **7/7 PASS**, P5-D/P6-E CPU **19/19 PASS**, **40/40 selected PASS**. `P5D_SERVICE_PREFLIGHT_PASS`, `service_api_model_id_confirmed=true`, Docker ID and PID-set continuity confirmed; **actual live P5-D `BLOCKED_PARTIAL_PROVENANCE` / RC3**. Container netns returned empty `""`; one container-side :8000 socket inode found but no matching FD host PID. Docker declared/effective port 8000 both present but strict compare `DOCKER_DECLARATION_MISMATCH`. `iptables-save` unavailable; `SMAPS_UNREADABLE`, pinned snapshot directory unreadable, mapped candidate files 0; PLE RSS/PSS and unique residency remain unobserved. One passing CPU test emitted `ResourceWarning` from unclosed scandir iterator (not an operator runtime service failure).

**After this operator run**, source-only patches close scandir; distinguish empty/unqualified namespace from actual mismatch, check nonempty identity; classify smaps read errors; accept only Docker's exact IPv4 wildcard + IPv6 `::` extension while rejecting unexpected bindings; probe pinned cache mount already ending in `/hub`; emit per-PID summary issues and add negative CPU fixtures. **No new source SHA CI, CPU execution or repeat real DGX read-only test is verified.** The earlier RC3 is preserved and not retroactively converted to PASS. New source is not a production gate.

Already-saved full JSON (not yet provided here): `/home/inlc/.local/state/blazux-wizard/model-measurements/orcarouter--20261119T004619880648Z--bd848453cb4f.json`. **Next:** upload/read the existing receipt first; no GPU inference or service mutation needed, do not rerun automatically. [Detailed evidence and subsequent source changes](../docs/P5-D-READONLY-ONE-TURN-RESULT-20261119.md). PR #1 Draft/Open/Unmerged; PLE/NAT ownership, P6-E/P7/P8 and production blocked.

---

## 2026-11-19 KST — P5-D bounded read-only one-turn audit SOURCE IMPLEMENTED, DGX execution pending

User requested P5-D **PLE file-mapping RSS/PSS and inode↔PID plus Docker host :8000 NAT process attribution in one operator turn**, with *read-only* host behavior. Added:
- `scripts/manager/p5d_live_audit.py`: fixed `orcarouter` scope, first/last P5-D read-only ownership probes, exact Docker ID/init PID/host PID set, `/proc/PID/stat` starttime plus net/mount/PID namespace continuity, cgroup ID relationship, streamed bounded `/proc/PID/smaps` per-file RSS/PSS and dev/inode→task root stat, optional immutable pinned Hugging Face snapshot inode alias (not a content checksum or verified PLE identity), `/proc/PID/net/tcp{,6}` LISTEN inode→`/proc/PID/fd/*` host PID correlation, Docker publish/bridge IP, optional unprivileged `iptables-save -t nat` candidate, localhost read-only /v1/models exact ID. Does **not** authenticate kernel DNAT path, unique PLE physical residency, independent GPU exclusivity or production authority.
- `tests/test_p5d_live_audit_cpu.py`: **14 new synthetic test methods committed, NOT YET EXECUTED on operator DGX/CI**.
- `scripts/temporary/p5d-readonly-once.sh`: operator one-turn shell wrapper, clean Git source guard, 3 CPU modules (new 14, existing P5 attribution 7 and P5-D/P6-E 19 expected methods), active service/API preflight, and single `--save --json` read-only host audit. Exit 3 means **blocked/incomplete evidence**, not service failure; no sudo, retry or GPU inference.
- Updated `.github/workflows/recipe-manifest-cpu.yml` CPU suite and Push/PR path filters. Workflow **new HEAD CI not verified**; historically zero new workflow runs after 2026-11-11.
- [P5-D exact one-turn runbook](../docs/P5-D-READONLY-ONE-TURN-20261119.md).

**Operator entry:** `cd ~/Workspace/llm/blazux-orcarouter && git pull --ff-only && bash scripts/temporary/p5d-readonly-once.sh`. Print exact Git SHA and result; optionally upload private JSON `evidence_file` for per-PID/file details. Host read probes may be permission-blocked; this does not authorize sudo or a kernel rule change. On insufficient evidence keep `BLOCKED_PARTIAL_PROVENANCE`, not a false PASS. All previous 1K/4K/7K GPU approvals consumed, no new inference; P6-E/P7/P8, PR merge and production remain blocked.

**Status:** `P5_D_READONLY_ONE_TURN_SOURCE_READY / CPU_NOT_YET_VERIFIED / REAL_DGX_AUDIT_PENDING / PLE_UNIQUE_RSS_AND_KERNEL_NAT_PATH_NOT_ATTESTED / CI_UNVERIFIED / PRODUCTION_BLOCKED`.

---

## 2026-11-19 KST — uploaded full P5 resource JSON REVIEWED (supersedes resource-review pending)

Reviewed original `orcarouter--20261118T214659097604Z--86b3752c0029.json`: 4 snapshots spanning **42.008s** and `OBSERVED_INTERVAL`, stable Docker ID at clean trial SHA `bc0a9ea`, prior nonthinking 3/3 TTFC/TPS recorded separately. Sampled GPU utilization **0→66→74→75%**, GPU power **9.86→20.43→20.98→21.22W**, GPU temperature **34→38→40→41°C**; peak *observed system zone* 46.6°C. Host CPU busy **5.11%**. Host minimum MemAvailable **28.729GiB**; host used swap stable **1.307GiB** and **zero swap-in/swap-out** observed, memory PSI some avg10 **0%**, cgroup high/max/oom/kill event deltas all zero. Container cgroup `memory.current` **22.914→22.581GiB**, file cache `file` **17.863→17.525GiB**, anon near **4.60GiB**. Cgroup major-fault count rose **2004** in first measured segment only, with `workingset_refault_file_delta=0`. NVMe mean read/write over the window **195401 / 316600 bytes/s** from host cumulative counters, not PLE-specific. Docker CLI `MemUsage~7.18GiB` uses different accounting from cgroup `memory.current~22.58GiB`; do not merge or call either VRAM. `PLE-specific RSS=null` and `smaps_rollup=null`, no independent port/NAT process, GPU exclusivity or throttling proof. Four GPU values are **after-case point samples**, not in-flight peak utilization. Production and CI remain blocked.

[Full resource review](../docs/P5-VISIBLE-GPU-ONE-SHOT-20261119.md).

---

## Current update: P5 visible measurement COMPLETE (2026-11-19 06:46 KST (2026-11-18 21:46 UTC))

**M1 P5 visible TTFC is now observed (scope-limited)**: operator ran the separate authorized one-shot, 1K/4K/7K `MEASURED_VISIBLE` 3/3, TTFC=TTFT 0.52051/1.59565/2.80664 seconds and post-first TPS 21.961/22.943/22.948. 31 selected CPU tests PASS on clean source SHA `bc0a9ea2346b85fa9f8e6ef132b765078b6385db`. All three completions ended with `finish_reason=length`; accuracy/task completion and production qualification are unverified. One-shot approval is **consumed**: no replay. M1 next target is **read-only resource receipt review, then independently grounded PLE RSS and NAT/GPU ownership**. M0 CI remains unverified; M2 P6-E, M3 P7, M4 P8 remain approval-gated. [Detailed measurement](P5-VISIBLE-GPU-ONE-SHOT-20261119.md).

---

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
