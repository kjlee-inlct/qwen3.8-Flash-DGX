> **2026-11-20 P7 source-only update:** P7 source reconciliation now fails closed on repeated (whitespace-trimmed) `probe_id` across service/proxy/gateway/storage, without claiming independent evidence authentication. New negative CPU tests added. Git blob exact-match local isolated fixture **8/8 PASS** and modified P7 methods with stubbed model registry **7/7 PASS**, **not** the full Wizard CLI/repo suite or GitHub CI. See [P7 detail](../docs/P7-PROBE-ID-INDEPENDENCE-CONTRACT-20261120.md). Old P5-D 138/138 and permission 7/7 belong to their historical, distinct SHAs; P5-D PLE/NAT, P6-E operating, P7 actual integration, P8 recovery and production remain unaccepted. PR stays Draft/Open/Unmerged.

# Blazux DGX Spark — 새 세션 인수인계 / 실행 프롬프트 (2026-11-20 KST)

> **현재 판단의 기준:** 2026-11-20 현재 feature branch GitHub HEAD `fe62f7284d12a7556cd0dc4925c627289c207208`를 확인한 후 작성했습니다. 이 문서를 커밋하면 HEAD가 바뀌므로 새 세션에서는 **GitHub PR #1의 최신 HEAD를 다시 조회**해야 합니다. 문서 커밋을 신규 CPU 또는 CI 수용으로 간주하지 마십시오.

## 1. 재개할 프로젝트

- Development repo: https://github.com/kjlee-inlct/qwen3.8-Flash-DGX
- Upstream: https://github.com/blazux/qwen3.8-Flash-DGX
- Branch: `feature/recipe-wizard-handoff`; PR https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/pull/1 — **Draft/Open/Unmerged**, base `main`.
- DGX operator workspace: `~/Workspace/llm/blazux-orcarouter`, NVIDIA DGX Spark GB10 / Ubuntu ARM64.
- vLLM **0.32.0** 고정, SGLang 사용 금지, `ONE_ACTIVE_MODEL_ONLY` / :8000 OpenAI-compatible API 유지; OpenWebUI와 Ollama :11434는 불필요하게 변경하지 않음.
- 가장 최근 **운영자 로그상** 개발 trial container: `qwen38-orcarouter-qsa62318-lmhead-v3`, full ID `9c49950015a845357e90fabe74946565d41069362c083fe7982f54caa2b3beac`; served API ID `qwen3.8-flash-next-orca-uncensored-bf16`. 이는 기록 당시 관측 사실이지 새 세션 시작 시점의 실시간 상태 보장이 아님. Canonical container `qwen38-orcarouter`로의 승격은 별도 수용 필요.

## 2. 가장 최신 P5-D / Wizard / Manifest 수용 근거 — SHA를 혼동하지 말 것

| Source SHA | Evidence origin | Confirmed result | Not established |
| --- | --- | --- | --- |
| `7c11d0d1a0921ef7b0f4134bd3d3c0d8ac4e5795` | Operator DGX terminal log | P5-D / Manifest / Wizard **138/138 selected CPU unittest PASS**; 8 modules, 5+24+9+20+19+14+11+36. Manifest graph PASS, PLE source-binding CLI PASS | GitHub CI, live RSS/PSS, PLE/NAT owners |
| `fd338efa549a8c3bb54e65e5e033d2334d9e96e1` | Operator DGX read-only host audit | `BLOCKED_PARTIAL_PROVENANCE / RC3`; all 3 `/proc/PID/smaps` reads EACCES errno13; Docker IPv4/IPv6 wildcard port declarations consistent | PLE mapped RSS/PSS/inodes, 3-namespace PID continuity, FD owner, kernel NAT |
| `045947fccd33952ef4911c908ffb480d62b3d82b` | Operator DGX one-shot permission wrapper | New permission CPU **7/7 PASS** at exact source SHA; Manifest/Wizard binding PASS; `BLOCKED_PERMISSION_PREFLIGHT / RC3`; full expensive audit correctly skipped | CI, new memory evidence, privileged attestation |
| `fe62f7284d12a7556cd0dc4925c627289c207208` | GitHub read-only verified docs commit | Exact-SHA evidence and P5-D blocker recorded; no source-code change | New CPU/CI PASS on documentation HEAD |

원턴 권한 관측 세부:

- Auditor EUID **1001**; fresh model process PIDs `4016083`, `4016529`, `4016530` were real/effective **UID 0** each. 이 PID들은 관측 당시 값일 뿐 재사용하지 말 것.
- Before/after PID start ticks are stable across the sample; **full** PID identity continuity remains unqualified because `net/mnt/pid` namespace symlink values were all `UNQUALIFIED`. No specific namespace errno was retained: `UNQUALIFIED` ≠ confirmed EACCES or real PID drift.
- `/proc/PID/smaps`: **3/3 `EACCES(13)`** despite visible file mode `0o444`; `/proc/PID/fd`: **3/3 EACCES**; init `/proc/PID/root`: EACCES; manifest-pinned snapshot candidate directories: **2/2 EACCES**.
- procfs mount had no explicit `hidepid` / `subset` declaration; `ptrace_scope=1` was observed as a **policy hint**. Auditor/target credential mismatch is a likely access boundary, but **sole causal mechanism is not authenticated** (ptrace credential/dumpability, capabilities, LSM may affect access).
- Result `P5D_FULL_AUDIT_SKIPPED=PROCFS_OR_IDENTITY_BLOCKED`, `ready_for_full_readonly_audit=false`, `service_mutated=false`, `executed_inference=false`. `RC3` means insufficient evidence, **not** running service outage.
- Zero candidate mappings is an **unreadable/missing observation**, never zero measured RSS/PSS or absence of PLE tensor residency. Docker port declaration consistency is not kernel NAT ownership or :8000 process attestation.

## 3. Source implementation and CLI already present — do not duplicate

- Manifest source graph (7 manifest files plus cross-reference): `runtimes/manifest-registry.json`, `runtimes/service-policy.json`, `runtimes/model-discovery.json`, `runtimes/ple-assets.json`, `runtimes/ple-loader-profiles.json`, model recipes, `scripts/p5_vendor/compatibility.json`. Source validation must fail closed on missing/incorrect pins or model IDs.
- `scripts/manager/p5d_manifest_binding.py`: source-only Orcarouter PLE repo/revision/asset cross-reference. Correct status `DECLARATIVE_P5D_SOURCE_BOUND_NOT_LIVE_ATTESTED`. Registered PLE asset `orcarouter-bf16-ple`; declared BF16 / `DISK_MMAP`; HF repo `orcarouter/Qwen3.8-Flash-Next-Uncensored-NVFP4` revision `3a3b63161c0745390e5270179af42e46efc70799`.
- `scripts/manager/p5d_live_audit.py`: manifest preflight before host probes; bounded read-only /proc smaps/inode/net/FD, Docker port declarations, exact API, cgroup and continuity review. May return `BLOCKED_PARTIAL_PROVENANCE / RC3`; no authorizing side effects.
- `scripts/manager/p5d_permission_preflight.py`: fresh Docker/PID inspection, start-time continuity, bounded `smaps` sample, UID+smaps metadata, namespace link, FD, root, Yama/procfs hints and pinned snapshot directory check. Permission PASS is **not** live attestation.
- `scripts/manager/generic_operations.py` and `wizard/console.py`: `operations generic p5d-source-binding-review` and `p5d-permission-preflight` (`--model orcarouter --json`); common Wizard interactive menu items **14** (source PLE) and **15** (non-elevated procfs). No new execution permissions.
- `scripts/temporary/p5d-permission-diagnose-once.sh`: clean feature-branch gate + synthetic CPU + Manifest + source binding + permission checks; reruns full P5-D audit only when permission preflight qualifies. The latest run correctly skipped the audit; **do not keep re-running the wrapper to reproduce known EACCES**.
- Test modules: `test_p5d_manifest_binding_cpu.py`, `test_p5d_live_audit_cpu.py`, `test_p5_readonly_attribution_cpu.py`, `test_p5d_p6e_cpu.py`, `test_manifest_registry_cpu.py`, `test_generic_operations_cpu.py`, `test_generic_console_cpu.py`, `test_wizard_router_cpu.py`, `test_p5d_permission_preflight_cpu.py`.

## 4. Independent P5–P8 and CI acceptance gates

| Gate | Current classification |
| --- | --- |
| Manifest / Wizard declarative source binding | PASS at operator-tested SHAs; not production-qualified |
| P5-D source CPU regression | Operator 138/138 PASS at `7c11d0d`; new permission 7/7 PASS at `045947f` (distinct run/SHA) |
| P5-D live provenance | **BLOCKED**: smaps/file RSS/PSS, inode, namespace/FD↔PID, kernel NAT owner |
| P5 benchmarking | Previous specific MTP0 text/API/no-thinking visible GPU observation exists, **not** comprehensive load, accurate completion, PLE residency, statistical reproducibility, or production acceptance |
| P6-E persistent Journal v2 / nonce and replay fence | Source/Fake-DGX concepts present; **live durable operating acceptance BLOCKED** |
| P7 Proxy / Gateway / Storage independent verification | PENDING / NOT ACCEPTED |
| P8 real fault injection, restore and recovery signoff | **BLOCKED**, Fake-DGX is not a real recovery pass |
| GitHub Actions latest exact-SHA CI | **UNVERIFIED** — no matching new runs/checks observed at last document HEAD; do not claim PASS |
| PR #1 merge / production | **BLOCKED**, leave Draft/Open/Unmerged |

GitHub Actions tracking is **documented and parked** at `docs/GITHUB-ACTIONS-OPERATOR-PUSH-COMPARISON-20261120.md`. A normal operator HTTPS `git push` at `2b97762a9da9287d4e111a8e86fd8cc5089ab496` produced no matching Push/PR workflow run/check. Workflow active and repo Actions enabled were separately observed in historical authenticated operator evidence; missing `main` workflow file alone did not prove the cause (older feature Push/PR runs worked). Do **not** assume connector-suppressed `GITHUB_TOKEN` events or the GitHub platform were the root cause. Do not launch another synthetic trigger test or manual CI dispatch without new approval.

## 5. Operational safety / permissions

- **No** arbitrary DGX model switching, Docker/GPU manipulation, service restart, cache deletion/overwrite, privileged procfs reads, sudo, ptrace attach, sysctl changes, host firewall/NAT edits, operating Journal writes, P6-E restart, P8 real recovery, `main` commit or PR merge unless separately expressly approved.
- Keep Hugging Face caches protected; no implicit rollback or cleanup. Keep one active model and :8000 API, vLLM 0.32.0, OpenWebUI and Ollama stable.
- Distinguish permissions of read-only host inspection from source-only work. No-sudo EACCES barrier is already diagnosed. Privileged read-only forensic collection may be planned in source, but must **not be executed** without a fresh, narrow operator authorization.
- `status=PASS` for Manifest or CPU does not imply `runtime_qualified=true`, actual PLE/NAT/GPU verification, or release. `RC3` must not be escalated into an outage or given a false zero measurement.
- `main` and PR merge remain forbidden without separate approval. GitHub Actions settings/dispatch also off limits.

## 6. Next session execution contract

1. Start by fetching **live latest GitHub** PR #1 HEAD, base, Draft/Open state and working branch; compare with source SHAs above; read the documents below before making changes. Historic commits are evidence anchors, not presumed latest HEAD.
2. Follow the user's latest approved task. If not separately approved, prioritize **source-only/Fake-DGX/CPU** improvements and precise release-gate documentation. Do not restart no-sudo P5-D probes. If user wants actual PLE RSS/PSS or kernel NAT owner, first define minimal **privileged read-only** evidence scope, rights and non-mutation invariants and obtain explicit approval; do not treat this handoff as approval.
3. Avoid duplicate implementations: inspect existing Wizard/Manifest/P5-D code, operator scripts, CPU tests and recent docs first. Maintain declarative manifest graph, one-active-model constraint and fail-closed behavior. Prefer a generic, extensible registered-model design to hardcoded two-model switches; the live P5-D audit is currently scoped to Orcarouter and must not pretend otherwise.
4. For an approved source task: implement focused patch -> add negative CPU/Fake-DGX tests -> **execute if a real runner is available** (otherwise label NOT_RUN) -> GitHub commit on feature branch with expected-SHA/fast-forward checks -> re-fetch exact commit/PR HEAD -> check actual Actions run and check-run IDs; if 0, classify `CI_UNVERIFIED`, never PASS.
5. Record SHA-bound evidence and status in `handoff/NEXT-ACTIONS.md`, `handoff/DECISIONS.md`, topic-specific docs and this handoff if appropriate. Never replace old audit logs with a newer assumed result. Distinguish operator-provided stdout, independent GitHub/API observations, synthetic fixtures and actual live DGX evidence.
6. Operator terminal commands are issued only when they are necessary and properly authorized, bounded in scope, non-destructive, with clear expected results and no automatic privileged fallback. A single well-scoped reproducible invocation is preferable to repeated trial-and-error.

## 7. Must-read permanent references (on newest feature SHA)

- `handoff/NEXT-ACTIONS.md`, `handoff/DECISIONS.md`, `handoff/SESSION-START-PROMPT.md`, and **this document**.
- `docs/P5-D-ONE-TURN-PERMISSION-DIAGNOSIS-20261120.md` — exact-SHA 7/7 test and EACCES/UID barrier.
- `docs/P5-D-PROCFS-PERMISSION-BLOCKER-20261120.md` — historical full audit and current limited permission evidence.
- `docs/P5-D-MANIFEST-BOUND-READONLY-SOURCE-20261120.md` — 138/138 source CPU and PLE manifest source contract.
- `docs/GITHUB-ACTIONS-OPERATOR-PUSH-COMPARISON-20261120.md` — unresolved no-run incident and parked Actions work.
- `docs/P1-P8-EXECUTION-ROADMAP-20261119.md`, `docs/P5-D-P6-E-READ-ONLY-PROVENANCE-JOURNAL-V2-20261110.md`, `docs/P5-P8-MODEL-AGNOSTIC-OPERATIONS-20261109.md`, `docs/MANIFEST-CONTRACTS.md`, `docs/WIZARD-CLI-CONTRACT.md`.

## 8. Paste-into-new-session task directive

위 GitHub Repository와 영구 문서의 **최신 상태**를 직접 확인하고 Blazux DGX Spark / P5-D–P8 개발을 이어서 진행해 주세요. 단순 계획 작성으로 끝내지 말고, 이미 승인된 안전한 소스 범위라면 기존 구현을 먼저 검토한 뒤 코드·테스트·Wizard·Manifest·문서를 실제 수정하고 feature 브랜치에 커밋하세요. 다만 `smaps` EACCES 3/3이 UID 1001→0 권한 경계에서 재현됐으므로 비승격 P5-D 실측을 무의미하게 반복하지 마세요. 새로운 권한 승격이나 GPU/Docker/서비스/운영 Journal 작업은 별도 명시 승인이 필요합니다. CPU 검증 138/138와 7/7은 서로 다른 SHA의 **운영자 제공 증거**, GitHub Actions의 최신 CI는 UNVERIFIED이며, PR #1은 Draft/Open/Unmerged입니다. 작업별 수행·미수용 게이트·정확한 SHA를 계속 기록하고, main 변경·PR 머지·Production Release를 하지 마세요.

