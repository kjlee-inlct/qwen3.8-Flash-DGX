## D-058 — 2026-11-07 — P2-FINAL Tool Calling, P3-C closed without replay

Per operator request, add **NVIDIA Qwen3.8-27B Tool Calling + reasoning parser + Open WebUI native tool cycle** as the FINAL P2 acceptance item. Verify official vLLM Qwen3.8-27B recipe flags `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3` against vLLM 0.32. Distinguish original checkpoint/API `nvidia/Qwen3.8-27B-NVFP4` / `qwen3.8-27b` from internal `Qwen3_5` architecture. Source candidate profile must be opt-in, preserve historical P2/P3 pinned container IDs and receipts, and NEVER auto-replace original Docker container. New separately approved migration and actual DGX tool cycling, streamed parsing and WebUI Native verification required to mark P2-FINAL PASS. Existing P2 download/loader/trial/benchmark already REAL PASS; appended Tool Calling acceptance remains OPEN. Historical **P3-C stage A/B/C already REAL PASS and CLOSED**, never rerun to close P2 Tool Calling or normal operating UX. Ordinary switching direction 27B→Flash and reverse Flash→27B both reported REAL PASS; reverse independent postcheck and normal main menu release still pending. Source record: `docs/P2-27B-FINAL-TOOL-CALLING-ACCEPTANCE-20261107.md`.

---

## D-057 — 2026-11-07 — Isolate ordinary recurrent model switches from one-off P3 acceptance (SOURCE ONLY)

Accepted development contract: keep P3-A/B/C immutable and never re-run or repurpose their stage execute commands for generic operating transitions. A new \`operational_switch.py\` may read/prove P3 A/B/C historical lineage but no old plan ID is an operational approval. Independently namespace recurring operations under \`~/.local/state/blazux-wizard/operational-switch\`; require a NEW exact short-lived plan, two distinct manual approvals, verified live source/API identity, pinned Docker target image/CID, stop-old-before-start, port 8000 release, single GPU model, append-only journal, one-use attempt marker, protected original model assets and exact API post-start verification. Recovery failures must not be reported as successful. 

Current \`operational_executor.py\` is **source-only and not exposed by \`./wizard.sh\`** until complete fake-DGX tests, separate real DGX operator consent and explicit qualification. No service mutation was performed. Read-only model menu preview and phase/evidence-separated dashboard are approved as SOURCE changes only. This decision supplements D-016/D-056 and does NOT supersede their stricter real-DGX approval boundary. Existing Draft PR remains unmerged.

---

## D-056 — 2026-11-07 — Treat actual P1/P2/P3 engine qualification and user-facing Wizard UX as separate acceptance gates

**Evidence-first confirmation:** On real DGX the existing `./wizard.sh` CLI and guarded backend for Flash P1 Verify/Benchmark and pinned NVIDIA 27B P2 trial/benchmark were exercised; actual P3-A Flash→27B, P3-B 27B→Flash, and P3-C Flash→27B all completed PASS. Actual final P3-C consumed three independent TTY acknowledgments and called the canonical `scripts.manager.p3_persistent_switch` route. It returned `P3_C_PASS_FINAL_27B_ACTIVE`, `post_switch_observed_model=27b`, `post_switch_status=LIVE_SERVICE_VERIFIED`, `issues=[]`, and wrote original `stage-c.json`; the current live 27B stays active on :8000. **Do not rerun this one-off acceptance sequence.** Original Flash container, image and HF caches must remain preserved.

**UX qualification is a DIFFERENT gate:** The main `./wizard.sh` interactive console (`wizard/console.py`) can select models, inspect current state, show P1 actions and historical Verify/Benchmark evidence; however `_stage_actions()` invokes P3 `stage-a/b/c --plan` only and explicitly states that execution did not begin. Thus success with `scripts/temporary/p3-stage-c-operator.sh --execute` validates the same canonical Wizard backend but NOT an actual *interactive menu* transfer, ordinary model selection-to-service-switch, recurrent Flash↔27B switching, or OpenWebUI/proxy/gateway integrations. CPU test PASS validates source guards, not usability evidence.

**Decision:** Preserve and freeze one-off P1–P3 success evidence. Treat model-centric interactive Wizard switching as the NEXT implementation milestone: design simple active-model → installed target → benchmark/history → downtime disclosure → fresh approved exact plan → canonical backend → live identity and recovery result flow; never show internal P1/P2/P3 as the primary navigation path. Requirements: one model active, port 8000 fixed, no accidental deletion, retries/rollback under journal/locks, human consent required, fail-closed on stale SHA, clear post-switch result. Implement/test this as a distinct repeatable operating transition and independently validate on DGX under its own new downtime consent; do not repurpose completed stage-c receipt or infer operator consent from previous acceptance. Keep Draft PR #1 unmerged pending review.

[Current state](CURRENT-STATE.md); [actual DGX final evidence](EVIDENCE-LEDGER.md).

---

## D-055 — 2026-11-07 — Bounded read-only Stage-C plan refresh instead of operator clock guessing

Actual DGX user attempts near 10:10 KST plan window boundary (10:08:14 and 10:09:30) both returned `P3_C_INSUFFICIENT_TIME_FOR_THREE_APPROVALS`, `executed=false`, `execution_dispatched=false`. This refusal correctly preserved source Flash service but required operators to manually guess the next boundary. Decision: modify ONLY tracked `scripts/temporary/p3_stage_c_operator.py` to read-only poll a NEW current canonical Stage-C plan for max 150 seconds when remaining time <120 seconds on a valid initial plan. Each polling observation checks all original A/B/P1/P2/model/service/port/provenance constraints; require a changed SHA (at the proper expiry boundary) and new expiry >=120s away. No wait for noninteractive/no TTY, `--plan` remains unchanged. Timeouts, source drift, earlier-than-boundary plan ID change, Ctrl+C and current Git changes block; no execution/approval state carried forward. Only after refresh, full new SHA and two separate TTY acknowledgments may allow canonical Wizard C execute (still locked/guarded). All actual service/canonical state semantics unchanged; P3-C not run by source work.

[Runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## D-053 / D-054 — 2026-11-07 — Git-public measured benchmark registry, no private raw evidence

**D-053: Git stores sanitized benchmark **facts**, not execution logs.** Public, versioned `benchmarks/published/<served-model-id>/<source-SHA16>.json` holds model repo, pinned revision, vLLM engine version, UTC source timestamp, hash of original private receipt, explicit small request profile and whitelisted latency/TTFT/throughput numeric metrics only. Initial entries are grounded in the user-supplied actual DGX Flash post-B (37.9527 mean tokens/s, receipt SHA `f506db4c...`) and 27B restored trial (7.9002 mean E2E, 11.1801 decode proxy, receipt SHA `80f109db...`). Interpret them as client-measured bounded three-request trials, not a normalized head-to-head ranking. NEVER commit raw `~/.local/state/blazux-wizard` receipts, ignored `reports/`, credentials, API paths, request/response samples, plan IDs/approvals, Docker/container IDs or private logs. Source hashes provide provenance and do not themselves prove numeric data matches original receipts until original-byte comparison on DGX.

**D-054: Future publication remains separate opt-in and fail-closed.** `python3 -m scripts.manager.benchmark_publication` performs allowlist-only local source conversion; `--plan` read-only, `--verify-published` compares expected published JSON to the original source, `--write` requires exact current original file SHA256, refuses overwrite and never Git stages/commits/pushes. `bash scripts/temporary/verify-published-benchmarks.sh` rechecks the two initial tracked summaries against original local private evidence. CI uses private fake CPU fixtures, cannot claim actual DGX byte verification. This does NOT change vLLM single-model runtime, host port 8000, P3-C exact SHA approval, or service rollback. Latest attempted C was CANCELLED before executor dispatch due leading bracket in input; no service mutation.

See [public benchmark registry](../benchmarks/published/README.md).

---

## D-050 / D-051 / D-052 — 2026-11-07 — Tracked P3-C final model operator

**D-050 (canonical C ready, execution not authorized):** Actual DGX `./wizard.sh switch flash-next-27b stage-c --plan --json` returned `READY_TO_REQUEST_TRANSITION_APPROVAL/issues=[]/p1_evidence.status=PASS/executed=false`, active original Flash `qwen38-flash` CID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`, preserved 27B CID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`, shared original image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, POST-B P1 Verify+Benchmark+diagnostics SHA proofs and unchanged P2 receipt hash. Its old short-window SHA `d5f200ff54e545877c6551d1c1eb46dcdb7ee3abdfeb6fbecb66c27b03d4eef7` is historical and not reusable. Optional evidence-copy operation was cancelled (`COPY` input, `copied=0/executed=false`); not a Stage C prerequisite.

**D-051 (new D-016 tracked C UX):** `scripts/temporary/p3-stage-c-operator.sh` + Python controller. `--plan` default read-only. `--execute` only after **independent operator approval of the LIVE Flash downtime**, a real TTY, fresh SHA printed in prompt, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, and independent `I_SEPARATELY_AUTHORIZE_FINAL_27B_STAGE_C`. Wrapper third literal is additional human authorization but is **not sent as `--enter-p3`**; canonical C expects null. Fresh plan and live identity rechecked before dispatch; canonical Wizard alone executes switch, locks, journal and best-effort rollback. C SUCCESS must independently pass served 27B API on :8000 AND immutable original `stage-c.json`. No automatic switch-back after successful C; preserve original Flash.

**D-052 (operator report separation):** Stage-C operator writes append-only private 0600 `<repo>/reports/transitions/flash-next--to--27b/p3-c-operator-<UTC>-<nonce>.json`, ignored by Git. This is **supplementary** to immutable `~/.local/state/blazux-wizard/p3/stage-c.json` and original P3 journal, lock and attempt marker (never copied away/deleted/moved for rollout). CPU fake-DGX tests and GitHub CI required before operator fast-forward pull. Source change does **not** authorize C execution, additional GPU tests, source/cache deletion, or Draft PR merge.

[Runbook](../docs/P3-STAGE-C-FINAL-27B-OPERATOR-20261107.md).

---

## D-047 / D-048 / D-049 — 2026-11-07 — Historical evidence view + staged copy migration / Stage C order

**D-047** Model-centric report catalog uses the service-policy Manifest `served_id` and reports Verify/Benchmark/GPU trials/transitions independently of internal P1/P2/P3. It reads legacy plus project `reports/`, verifies source file regularity/size/private mode, deduplicates exact SHA256 bytes and uses original UTC completion/filename time. NVIDIA 27B mean end-to-end throughput and decode proxy must be distinctly labeled, not conflated with Flash-Next measured throughput. It is strictly read-only and shall never call Docker or perform inference.

**D-048** P2/P3 report consolidation is **copy-only with current full plan approval**, not state relocation: new `./wizard.sh evidence migrate --plan|--guided` and Advanced 8. JSON bytes are copied with digest-bound names to project `reports/models/<served_id>`, `reports/transitions/<direction>`, and `reports/diagnostics/<served_id>`. Private 0700 folders, immutable O_EXCL 0600 records; originals, P2/P3 locks, stage state and journal, retry markers, raw target logs remain undisturbed and canonical. If preflight/source changes or destination collision, fail closed; later native writer mirroring/state relocation requires separate plan and actual DGX approval.

**D-049** Actual post-B Flash P1 Verify + Benchmark are PASS and P3-A/B are PASS. This qualifies considering Stage C **now**, not approving it. After fresh source CI and clean DGX pull run **only** `./wizard.sh switch flash-next-27b stage-c --plan --json`; check current live source, preserved 27B, P1 evidence PASS and required downtime ack. P3-C execution requires a **new** exact SHA and explicit Flash-Next downtime consent, regardless of report importer completion. No automatic service transition, forced stage retry, model deletion or PR merge.

[Detailed contract](../docs/MODEL-EVIDENCE-HISTORY-MIGRATION-20261107.md).

---

## D-044 / D-045 / D-046 — 2026-11-07 — Operator UX and model-centric evidence

**D-044 (evidence path):** New NVIDIA Flash-Next Wizard execution receipts are stored under Git-ignored `<repo>/reports/models/qwen3.8-flash-next/`, named by the *served model ID* rather than an unmemorable stage code. Keep unique append-only JSON (0600; directory 0700). Do not alter historical `~/.local/state/blazux-wizard/p1/` receipts. P3 stage-C evidence gate reads both roots and evaluates newest finished UTC action receipts, including FAIL; no historical PASS masking. P2/P3 state/locks/reports require their own safety-qualified migration, NOT moved now.

**D-045 (approval UX):** Model menu already selected the action; direct guarded entry performs only that action. Show `Type exactly [<current SHA>]` like P3; empty/wrong cancels, fresh plan revalidated immediately before execution. Show human-readable preflight/Verify outcomes/Benchmark metrics and evidence path. Keep machine JSON/CLI and exact-plan SHA safety boundaries intact. User-facing labels identify model/action, not P1/P2/P3 implementation phases.

**D-046 (source versus runtime):** User-provided 2026-11-06 post-B Flash Verify + Benchmark are *actual* PASS; their distinct approvals and real bounded measurements supersede prior `NOT_RUN` positions. New GitHub source UX changes and CPU-only CI are **not** DGX validation. P3-C authorization requires independent downtime approval even when the evidence prerequisite test passes. No unapproved GPU run or service modification, no automatic PR merge.

---

## D-043 — 2026-11-07 — POST-B P1 diagnostic is append-only; final P3-C remains separately approved

Use D-016 GitHub-tracked `scripts/temporary/p1-post-b-audit.sh` as the next **read-only** DGX action after CPU CI PASS and operator fast-forward pull. It reuses the P1 inspect-only collection and verifies actual P3-B receipt + current Flash service/API/source image, both exact doctor/inventory launch preflight raw JSON outputs (benign own Flash collision only), readiness of Verify/Benchmark plans and pinned original asset revision. Every attempt produces a new private 0600 `p1-diagnostics-<UTC>-<nonce>.json` outside Git/HF cache; no overwrites. P3-C gate assesses the newest diagnostic attempt (including BLOCKED), with legacy fixed-name fallback, and still requires **separately approved actual post-B P1 Verify and measured numeric Benchmark** newer than B. Source tests are not DGX/GPU evidence and this audit conveys no GPU or P3-C authorization. On any mismatch stop; preserve caches/containers/images and unmerged Draft PR.

## D-042 — 2026-11-07 — P3-B ACTUAL DGX PASS supersedes pre-execution planning; rectify operator bookkeeping

Actual operator terminal output confirms canonical P3-B `PASS/executed=true/live_verified=true`, wrapper `P3_B_PASS_FLASH_NEXT_ACTIVE`, `issues=[]`, independent live Flash API `qwen3.8-flash-next`; original Flash is last verified active model. Canonical `~/.local/state/blazux-wizard/p3/stage-b.json`. Historical wrapper report incorrectly named `p3-a-operator-20261106T223124Z-14861d75.json` and its `approval_accepted=false` persisted because imported A `persist()` used a hardcoded prefix and B never set the field after successful manual confirmation. Preserve the original records and document the inconsistency; change source to stage-aware new filename plus separate `approval_accepted` (manual typed inputs), `execution_dispatched` (core invoked) and `executed` (Wizard observed). P3-A/B actual completed, NO stage repetition. P1 POST-B read-only preflight PASS only; Verify/Benchmark/RC3 disposition pending. Final C stays NOT_RUN/NOT_AUTHORIZED.

---

## D-041 — 2026-11-06 — Operator EXPLICITLY APPROVED P3-B ONLY; live execution still requires fresh terminal triple-ack

After actual DGX P3-B read-only `READY_FOR_SEPARATE_P3_B_APPROVAL` with `issues=[]`, the operator responded **"승인"** to the direct, scoped question **"P3-B(현재 NVIDIA 27B 중단 → 원본 Flash-Next 복귀)를 승인하시겠습니까?"**. This is **explicit P3-B downtime permission only**, superseding the approval-waiting clause in D-040. It does NOT approve post-B P1 GPU verify/benchmark automatically or final P3-C, merging Draft PR, deletion, or any other service change. Existing tracked `scripts/temporary/p3-stage-b-operator.sh --execute` remains the ONLY operator command, after DGX fast-forward pull; its new stage-B exact plan ID, `I_ACCEPT_27B_DOWNTIME`, and `I_SEPARATELY_AUTHORIZE_P3_STAGE_B` are independent mandatory typed runtime approvals. No old P3-A SHA or 17:50-expired B inspection SHA may be reused. Canonical Wizard rechecks before stopping live :8000; failure recovery is best effort and no automatic retry or stage progression is permitted. This GitHub source/doc step does NOT execute B. Until operator supplies actual `P3_B_PASS_FLASH_NEXT_ACTIVE` with verified API, stage B remains NOT_RUN and last observed active model stays 27B. D-034 order still requires new, post-B Flash P1 functional Verify, numerical Benchmark and rc3 disposition before separate P3-C approval.

---

## D-040 — 2026-11-06 — Real P3-B read-only READY; independent 27B downtime and B-stage entry required

Operator supplied actual DGX output after fast-forward to `e5d4171d07838e565510b1127f4a0b27dcd8423f`, executing only `bash scripts/temporary/p3-stage-b-inspect.sh`. Result `status=READY_FOR_SEPARATE_P3_B_APPROVAL`, `issues=[]`, `executed=false`, `approval_accepted=false`, `operations_enabled=false`. Active API `qwen3.8-27b` and preserved source container `qwen38-27b` ID `6d9ede0904c2b8e9e632d45b51aba4acbaf4502ae648da60cca77677948b0e2d`; original preserved Flash-Next container ID `90f39a4dbccd0b5f97efa0ff163c61402ddace3dd3cb4da986a91dff7eb45ed5`. Both use runtime image digest `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`; distinguish MODELS by API ID/immutable container provenance, NOT by shared image digest. Prior successful P3-A plan `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4` linked to immutable stage-A receipt; P2 SHA `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9` matches. Operator's B read-only evidence `/home/inlc/blazux-p3-reports/p3-b-inspect-20261106T084156Z-f48d7da9.json`. The plan `7af40f009dd67975c77b98c03183833dd4997e16f9c9443bd11ea880f6d8162c` has expiration epoch `1793955000` (**2026-11-06 17:50 KST**) and is inspection evidence only. **Never reuse it for a future switch.**

**NO P3-B DOWNTIME APPROVAL WAS GIVEN.** Success of read-only B plan is not permission to stop 27B. Specific core UX/safety finding: `p3_persistent_switch.py` previously used `I_ACCEPT_FLASH_NEXT_DOWNTIME` for ALL stages, even though B stops **27B**. This was incorrect operator-facing approval semantics, despite being guarded. Source now requires B-specific **`I_ACCEPT_27B_DOWNTIME`** plus **`I_SEPARATELY_AUTHORIZE_P3_STAGE_B`**, alongside a freshly computed exact 64-character B-only plan SHA. A/C retain existing scoped ACK strings; B refuses reused A Flash ack or A entry. Only after a **new user decision explicitly authorizing B** may DGX operator invoke `scripts/temporary/p3-stage-b-operator.sh --execute` via D-016. Wrapper default `--plan` is read-only; execute demands real TTY and independent typed three fields, checks live 27B+actual A receipt+preserved Flash ID/image and fresh short-lived plan before/after inputs, then delegates only B to canonical Wizard, verifies Flash API after return, records local private evidence and never auto-runs P1/C. Host process GPU exclusivity and restoration after host/daemon failure remain unqualified. Until authorization, **leave 27B active** and preserve original Flash and 27B containers/images/caches and unmerged Draft PR. After separately approved B PASS, D-034 still demands new P1 functional and measured benchmark+diagnostic disposition, then separately approved C final 27B.

---

## D-039 — 2026-11-06 — P3-A REAL DGX PASS, 27B ACTIVE; P3-B approval NOT GIVEN

User's operator transcript on DGX `feature/recipe-wizard-handoff` HEAD `a3945bdc5cfec467478978c47b3a27bdafee84bd` confirms successful distinct P3-A Flash-Next→NVIDIA 27B persistent transition. Fresh stage-A plan `b6c7a32e249eaf45dd864719eb32822bf1e72a2d123b5d60e312d5fffec203a4`, TTL until 2026-11-06 16:50:00 KST, operator typed plan SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME`, `I_SEPARATELY_AUTHORIZE_P3_ENTRY` **independently**, all exact. Canonical Wizard `stage=a`, `executed=true`, `status=PASS`, `live_verified=true`, evidence `/home/inlc/.local/state/blazux-wizard/p3/stage-a.json`. Independent post-switch check `post_switch_status=LIVE_SERVICE_VERIFIED`, `post_switch_observed_model=27b`; operator wrapper `status=P3_A_PASS_27B_ACTIVE`, `issues=[]`, `execute_command_exit_code=0`. Local report `/home/inlc/blazux-p3-reports/p3-a-operator-20261106T074306Z-c99bf2ad.json`. The transition completed at approximately 2026-11-06 16:43 KST, with 27B deliberately LEFT ACTIVE. Prior D-038 expired-plan refusal is history and superseded by this *separate* successful new SHA. Original Flash preserved under existing P3-A source safeguards; inspect its precise stopped-container ID before B rather than assuming preservation from a source CI run.

**P3-B (27B→Flash-Next) is a new service interruption, NOT implicitly authorized** by P3-A or by sharing the success log. Do NOT run `stage-b --execute`, shut down 27B, restart Flash, create a P1 GPU workload, or advance to C automatically. Only read-only stage-B checks are permissible pending a new explicit stage-B scoped decision. D-016 tracked wrapper `scripts/temporary/p3-stage-b-inspect.sh` uses the *actual private stage-A receipt*, fresh Wizard service manager status and canonical `stage-b --plan`, compares immutable original/target IDs and image provenance and saves local read-only evidence. It exposes **no execute mode**. A READY preflight is **not** downtime approval, nor production rollback qualification. After B is separately authorized and successfully executed, D-034 requires full new P1 functional verify and numeric rebenchmark plus diagnostic disposition before an independently approved C, final 27B active. Draft PR #1 remains open/unmerged; do not delete model images/checkpoints or perform unattended service changes.

---

## D-038 — 2026-11-06 — User must see exact approval values; expired P3-A plan refusals are not recovery attempts

Operator entered correct P3-A SHA, `I_ACCEPT_FLASH_NEXT_DOWNTIME` and `I_SEPARATELY_AUTHORIZE_P3_ENTRY`, but Wizard rejected `P3_STALE_PLAN_OR_CHANGED_PREFLIGHT`, `executed=false`, no Docker service mutation. Plan `94b4dedae21eb72b12443029257931e123e33404c32898d9ae2bad52954c064f` expired `2026-11-06 16:30:00 KST`; recorded operator report `20261106T073049Z` is 16:30:49 KST. Expiry is the leading explanation, without asserting exclusion of other preflight drift. Original service / model remains protected and no P3 stage completed. User specifically requires **showing the exact input characters** at each terminal confirmation, not an abstract "type acknowledgment exactly" prompt.

D-016 scoped change: P3-A wrapper prints the actual current plan ID, full downtime and separate entry ACK values, KST expiry and time remaining. Fail before human prompts if less than 120 seconds remain. After input, read-only plan refresh must yield same full plan SHA with >15s remaining or block before mutation; canonical Wizard still performs its own live preflight. Show nested Wizard `executed=false` stale refusal as `BLOCKED` rather than `OPERATOR_REVIEW_REQUIRED`. Never reuse stale SHA, silently regenerate an approved hash, automate ACK input or chain P3-B/C. New real-world DGX trial requires fresh user TTY input per D-037; no blanket service change allowed. Source CPU CI PASS is not runtime model qualification.

---

## D-037 — 2026-11-06 — Operator's P1-clear conditional P3-A authorization becomes eligible; stage-A exact interactive gates still mandatory

User explicitly authorized **Flash-Next→NVIDIA 27B** conditional on no remaining **pre-A P1** deficiencies. Actual DGX operator output from tracked `p1-pre-a-readiness.sh`, source HEAD `834f823a76556a37a982e3dbf7f243db3edad6df`, now confirms `status=PRE_A_P1_REVIEW_READY`, `issues=[]`: both historical/current `doctor` and `inventory-plan` rc3 are `EXPECTED_ACTIVE_FLASH_COLLISION` (2/2 each), original Flash API/immutable image checked, P1 functional Verify PASS, original P1 benchmark PASS (TTFT P50=1.398707s, latency P50=1.687357s, mean=38.2968 tokens/s, 3 requests). Original local receipt `/home/inlc/blazux-p1-reports/p1-pre-a-20261106T065104Z-aaed31b2.json`. **The original user's condition is met for considering P3-A entry**, superseding the *pre-A* hold in D-035/D-036. Do NOT claim post-B P1 or actual P3 switching was completed: `p3_a_executed=false`, `p3_a_execution_authorized=false` in the **read-only receipt by design**, and actual P3-A/B/C remain NOT_RUN.

A P1 PRE-A evidence PASS alone is never a daemon/GPU or port-mutation permit; the operator must additionally complete *fresh action-scoped* stage-A plan and independently type the **full exact plan ID**, downtime acknowledgment `I_ACCEPT_FLASH_NEXT_DOWNTIME` and separate entry acknowledgment `I_SEPARATELY_AUTHORIZE_P3_ENTRY` at the DGX terminal. These strings and source target must be read back from the live plan, not synthesized or reused from P2. Only stage A is included in this conditional approval. A successful A leaves **27B active** and stops, with **no automatic B**, service recovery best-effort on failure, no host GPU exclusivity/daemon fault recovery guarantee. B, post-B P1 functional+numerical rebenchmark, and C are independently staged and approved per D-034. Preserve original Flash container/image/checkpoint and unmerged Draft PR.

D-016 workflow: use tracked `scripts/temporary/p3-stage-a-operator.sh` from the GitHub branch after tested push and DGX `git pull --ff-only`. Default `--plan` is read-only; `--execute` requires TTY and exact three interactive tokens, then invokes **the canonical Wizard** stage-A guarded execute, independently rechecks 27B active API, writes local private evidence, and never advances to B. No hidden Docker mutation in the wrapper itself and no copy-pasted multi-command Python snippets.

---

## D-036 — 2026-11-06 — P1 numerical metrics now supplied; require tracked read-only pre-A audit before conditional approval

Supersedes **only the "P1 benchmark numerical metrics absent" claim** in D-035: user shared actual local original P1 Wizard receipt `~/.local/state/blazux-wizard/p1/20261105T113125Z-586b2b46d93e.json`, status PASS with 3 samples / 192 completion tokens, TTFT P50=1.398707s/P95=1.751198s, E2E latency P50=1.687357s/P95=1.780142s, mean throughput=38.2968 tokens/s. The new 2026-11-06 P1 `--inspect-only` report has source/Hybrid READY, both plans READY, API `qwen3.8-flash-next`, no setup process and clean tree. `actions.verify/benchmark.status=BLOCKED` with `reason=inspection_only` is intentionally read-only, **not P1 evidence regression**. Raw `doctor=3`, `inventory_plan=3` outputs from historic/current reports were not included in the pasted summary and need examination. The user reaffirmed D-016: a tracked, tested temporary script must be pushed to GitHub before asking DGX operator to pull and invoke it. `p1-pre-a-readiness.sh` reconciles old+new raw rc3 output, original verified receipts and fresh current Manifest/API with no GPU. As long as this pre-A reconciliation is incomplete, the operator's conditional P3-A approval has not been established; no GPU start/stop or P3 --execute. D-034 post-B P1 functional and measured rebenchmark remains mandatory before final C.

---

## D-035 — 2026-11-06 — Operator's conditional P3-A permission is NOT satisfied while P1 work remains

Operator instruction: "Flash-Next에서 추가로 해야하는거 있나요? P1 에서 안한거 있는지 점검 후 없다면 27B 전환을 승인합니다." This is **conditional**, not blanket downtime/P3-A permission. Based on retained actual DGX P1 history, verify=PASS (baseline/extended completion, chat, tools, vision), benchmark=PASS (3 bounded requests), but actual numerical P1 TTFT/latency/tokens-per-second measurements have **not been supplied**; historic doctor and inventory-plan rc=3 stdout/stderr are still missing; post-P3-B P1 rerun is by definition NOT_RUN. **Therefore the condition is NOT MET and P3-A is NOT AUTHORIZED to execute.** Keep live Flash-Next, all assets and :8000 unchanged. D-034 still requires actual post-B P1 functional/numeric evidence before C. No automatic stage progression.

Source code review identified an independent logic error: `scripts.manager.inventory.main` returns rc=3 when `qwen38-flash` and its listening :8000 already exist even if `inspect_host.status=PASS` and `errors=[]`. Historical rc=3 might reflect an expected collision but cannot be asserted without original JSON. `p3_p1_evidence_gate.py` previously required rc=0 for both doctor and inventory, an incompatible success gate with the active source after B. Source corrected to accept **only rc=3 with both full parsed inventory documents proving that exact active Flash image/container owns :8000, no read errors, correct launch-preview target and consistent collision flags**, plus still-required reviewed disposition, timestamps, new functional and measured benchmark receipts. No actual P1 completion or operator permission is implied by CPU CI.

---

## D-034 — 2026-11-06 — P2 stops; P3 separately entered; Flash-Next P1 remediation then final 27B (OVERRIDES D-033)

User explicitly specifies: **P2 completion MUST NOT automatically enter P3**. P3 must first verify 27B as the source state, then **27B → Flash-Next** transition. Only after that succeeds, **address P1 deficiencies and rebenchmark Flash-Next** using actual measured evidence. Then **Flash-Next → 27B** transition and verification; final expected active model is **27B**. Because P2 currently restores original Flash-Next, 27B must be made active through its own approved gate before the requested 27B→Flash-Next verification. Do not imply this preliminary activation is automatic. Independent plan/approval/restore on each transition; pause at each phase, no auto chaining. Old P3 two temporary roundtrips conflict with this order and are retired/fail-closed. New read-only `sequence --plan` is not a persistent switch executor, never issues an execution plan or starts GPU. D-033 is explicitly superseded. No new live downtime authorized.

---

## D-033 — 2026-11-06 — P3 acceptance starts with two temporary verified roundtrips, not permanent switch

P3 first acceptance instrument is **exactly two** sequential Flash-Next → temporary NVIDIA 27B → original Flash-Next cycles using the existing proven one-shot recovery executor. It is **blocked absent actual P2 benchmark receipt** `BENCH_PASS_RESTORED_VERIFIED` and additionally requires **new P3-specific plan ID plus explicit downtime acknowledgment**. After every cycle, recheck actual original container identity, running state and Manifest-based API served ID; on first failure never begin another cycle. Reporting P3 temporary-roundtrip PASS must **not** be called persistent production model-switch readiness. Persistent switch, failure injection and recoverability remain later independent work. No service, image or model change authorized by source-level readiness.

## D-032 — 2026-11-06 — P2 benchmark must reuse the proven exact-identity restoration path

The actual 27B DGX smoke `PASS_RESTORED` means do not repeat source import probes. Add bounded 3-request/64-token **benchmark-specific** approval that cannot reuse the first smoke trial's plan ID. Reuse the original one-shot target launch, exclusive GPU container policy, preserved original identity and mandatory original restore; capture client metrics, not generated text, and local 0600 evidence including fresh Manifest/API check after restore. Mark client TTFT, decode/prefill **proxies** separately from engine speed, and memory point sample distinctly from peak. Any result absent real measured data or independent return-to-Flash proof is not benchmark PASS. Disruptive execution still needs fresh exact plan and new typed downtime approval; no user "continue" instruction by itself grants a service interruption.

---

## D-031 — 2026-11-06 — Wizard must use Manifest-led live service status as primary operator interface

After real one-shot Qwen3.8-27B GPU `PASS_RESTORED`, the user chose **Manifest-based Wizard** instead of manual `docker ps` + `curl` for verifying original Flash-Next recovery and future switching. Keep a **single** `./wizard.sh service manager status --json` command with fresh actual Docker/socket observation + declared `runtimes/service-policy.json` expectations + localhost `/health` and `/v1/models` exact model ID. Return `LIVE_SERVICE_VERIFIED` or fail closed `BLOCKED`, never infer operation authority or API identity from a stale manifest. Preserve `inventory`, `health`, `logs` for diagnostics. Do not conflate current API verification with prior trial provenance, GPU exclusivity, permanent switch readiness, memory/latency measurements or user authorization to stop production. No Docker or GPU mutation from any status command.

---

## D-029 — 2026-11-06 — Permit FIRST 27B GPU trial only via exact-approved, bounded, restoring experiment

A real DGX CPU-only ModelOpt registration pass justifies trying GPU startup instead of further speculative CPU checks. This is **not** permission to interrupt the running Flash-Next without operator acknowledgment. Implement 27B **experimental one-shot** guarded CLI, with default read-only planning and exact full SHA plan ID + typed interruption acknowledgment. A trial deliberately stops original `qwen38-flash` and must try restoring the **existing same original container** regardless of target launch success. No parallel GPU models, permanent model transition, cache deletion, image rebuild/pull, or reuse of Flash-Next PLE/MTP options. Protect on unknown Docker target/GPU status; if recovery cannot be verified, show failure and require operator intervention. Original service may be disrupted temporarily and power/daemon failure can defeat auto-recovery.

Keep NVIDIA `nvidia/Qwen3.8-27B-NVFP4` ModelOpt FP8/NVFP4 separate from community Unsloth compressed-tensors examples; checkpoint's internal `Qwen3_5ForConditionalGeneration` is *only a loader identifier*, not the model product name. Start with ctx8192/one sequence/0.70 GPU/eager, no MTP/YaRN; qualify kernels/API first, optimize later.

---

## D-028 — 2026-11-06 — Verify ModelOpt mixed name through public registry, not instance method

The installed vLLM 0.32 `ModelOptMixedPrecisionConfig.get_name(self)` is an **instance** method. The initial CPU-only audit's class-level zero-argument call yielded a self-binding TypeError unrelated to model compatibility. Correct strategy: import `vllm.model_executor.layers.quantization`, call `get_quantization_config("modelopt_mixed")` (no config or model instantiation), and verify identity to the imported `ModelOptMixedPrecisionConfig`. Preserve fail-closed checks and exact raw DGX evidence. No method-call issue may be treated as GPU kernel/load failure; no source-only/CPU result can authorize GPU transition.

---

## D-027 — 2026-11-06 — Opt-in CPU loader import is distinct from GPU runtime acceptance

After actual DGX read-only `serve_27b.sh --status/--plan` success, separately check installed Python imports of vLLM Qwen3.5 and `ModelOptMixedPrecisionConfig`, plus the declared quantization name `modelopt_mixed`, in a bounded **operator-opted-in CPU-only runc container**. Do not mount model cache, publish ports, request GPUs, start the vLLM engine, call inference or modify the original Flash-Next process. The wrapper must default to `--plan`. Import failure in this restricted environment is ambiguous; even a clean import/class/name result does not qualify GB10 GPU kernels, checkpoint loading, memory fit, API, benchmarks or rollback. GPU/start/transition requires separately scoped approval.

---

## D-026 — 2026-11-06 — Serving scripts split per model, preserve legacy call path

Choose model-specific serving entrypoints: `scripts/serve_flash-next.sh` contains original Flash-Next PLE/MTP/QSA implementation; `scripts/serve_27b.sh` is an independent NVIDIA ModelOpt entrypoint (initially plan/status only); `scripts/serve.sh` remains default-compatible Flash-Next dispatcher with optional explicit `27b` selection. `./flash serve` retains existing Flash-Next behavior and tests. Do not inherit Flash-Next-only PLE/MTP/hybrid settings into 27B and never allow 27B to start/switch without separately approved, exact-plan executor with tested old-service restore. `serve.sh` with no args is **not** a harmless preview: it keeps legacy Flash-Next start behavior. Prefer explicit `scripts/serve_27b.sh --plan` for P2 read-only evidence.

---

## D-025 — 2026-11-06 — P2 27B dedicated initial-run preview without implicit transition

Once operator-supplied 27B pinned source metadata (FP8 208/NVFP4 193) and installed vLLM 0.32 source registry/ModelOpt AST checks pass, develop a **separate 27B runner** instead of reusing Flash-Next `scripts/serve.sh` (PLE/MTP/QSA defaults). The new `model 27b plan --for-action start --launch-preview` returns a **non-executable, unapproved** argv with exact local image ID, pinned snapshot path, `modelopt_mixed`, conservative *unvalidated* 8192 context/1 sequence/0.70 GPU memory/eager. Preview inspects original Flash-Next container image and localhost API identity but never calls Docker run/stop. No `plan_id`, no `--execute` override, no `operations_enabled`. A registry digest/validated recipe, GPU memory/kernels, exact source recovery and separate stop-before-start approval are still required. A preview command displayed in JSON must **never be copied to the shell**.

---

## D-024 — 2026-11-06 — Quantization source audit is a distinct release gate

Verify the local immutable NVIDIA 27B `hf_quant_config.json` rather than assuming the main-branch model card reflects downloaded revision. Require a bounded read-only `MIXED_PRECISION` description with layer-level FP8 and NVFP4 for source shape audit. Missing/invalid/unrecognized metadata blocks further qualification; valid metadata is still **not** proof of ModelOpt GPU kernel support, image import, memory capacity, runtime functionality or service transfer approval. No GPU launch and no implicit cleanup.

---

## D-023 — 2026-11-06 — Installed image source audit before P2 GPU runtime

Use a **separately invoked, explicitly CPU-only, isolated Docker runc image-source audit** to inspect patched vLLM 0.32 model registration/Qwen3.5 classes and ModelOpt NVFP4/FP8 before building/enabling a 27B launcher. A local image ID is not a registry digest, source symbols are not executed kernel proof, and neither gives service start authorization. The default operation is `--plan`; `--execute-cpu-only` uses no network, GPU or published ports, temporarily creates one runc container and removes it upon exit, and never touches Flash-Next. GPU start/old-service stop/transition and cache deletion remain separately gated.

---

## D-022 — 2026-11-06 — P2 download is evidence, not 27B runtime approval

Operator-supplied immutable NVIDIA 27B download PASS (19/19; exit 0; pinned source candidate) supersedes stale in-progress entries. Preserve exactly one active GPU inference model and host port 8000; never re-download without missing/corrupt evidence. Approve adding a **read-only** runtime preflight interface without enabling a GPU start, implicit service switch or recipe validity. The existing Flash-Next-specific serve script and hybrid/MTP defaults must not be repurposed as a validated 27B launcher. Actual 27B vLLM 0.32 loader, ModelOpt NVFP4/FP8, memory, image digest and safe rollback remain independent gates; P2 GPU service requires separate explicit authorization.

---# Decision record — accepted constraints vs proposals

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

| D-016 | 2026-11-05 | For repeatable user-mediated DGX workflows, develop **one Git-tracked temporary script per bounded milestone** in `scripts/temporary/`, accompanied by a CPU-only fake test, README lifecycle and handoff. User workflow is GitHub commit/CI → finish existing operator setup/serve tasks → `git pull --ff-only` → invoke one wrapper for preflight → separately approved Wizard verify/benchmark → evidence summary. Default read-only; no script-level auto-git-update, implicit operational approval, cache deletion, service disruption or secret log uploads. Temporary wrappers must be retired only by a reviewed commit after evidence is recorded; shared logic belongs in permanent Wizard modules. | DECIDED / SOURCE+CPU CI VERIFIED; DGX/GPU NOT_RUN |

| D-017 | 2026-11-05 | User confirmed Blazux default NVIDIA Flash-Next must remain compatible and authorized **bounded non-disruptive P1 GPU/API verify+benchmark without separate interactive plan-hash typing**. Correct new P1 checker false positives for existing shared metadata cross-repository symlinks (`tokenizer.json`, `model.safetensors.index.json`), retaining strict shard checks and bounded JSON index. Use `scripts/temporary/p1-post-download.sh --auto-gpu`, deriving live action-specific plan IDs and letting the Wizard revalidate each one. No change to permissions for service start/stop, setup/download, Hybrid repair, cache deletion, model switches or gateway. API model ID shows some server is active; preserve it. | DECIDED / SOURCE+CI PASS at 0063b0e (2/2 jobs, 155 tests/job); DGX GPU verdict PENDING |

| D-018 | 2026-11-05 | Preserve native Blazux default Flash-Next acceptance in Wizard: mandatory /v1/completions + standard chat baseline, separate tool/vision probes, mark partial advanced failures without blocking bounded baseline benchmark, retain nonzero-rc Wizard evidence, keep model/server untouched. Original DGX verify failure still needs evidence to identify precise cause. | DECIDED / SOURCE+CI PASS 391a2844 / DGX RECHECK PENDING |

## D-019 — Single active GPU model, fixed API :8000 and manifest-first orchestration (2026-11-05)

**DECIDED by operator:** At any given time DGX Spark hosts **one active GPU inference model**. Both NVIDIA Flash-Next and NVIDIA Qwen3.8-27B must expose the same host API `:8000/v1` when active. **27B start requires Flash-Next stop, port release, identity verification and approved rollback**; never run both GPU models or bind a second external port as an implicit workaround. Conversely, 27B → Flash-Next requires the same ordered stop/start/verify/restore discipline. Download is a separate **network/disk-only** operation allowed while Flash-Next serves (no GPU use, service stop, host port binding or API cutover). Maintain a versioned committed desired policy `runtimes/service-policy.json` and a live observed manifest from Docker/socket inventory; historical manifest records are evidence, not proof of current reality. State transitions must be lock-protected, auditable, checkpoint/image-preserving and explicitly plan-approved. Approval for download does **not** approve service stop, GPU startup or model switch. **SOURCE implemented / DGX transition NOT_RUN**, P3 acceptance remains separate.

## D-020 — Model-first consolidated Wizard (accepted 2026-11-05)

Operator approved `./wizard.sh` with only **1 Select/run model, 2 Service, 3 Advanced, 0 Exit** and model choices **Flash-Next / NVIDIA 27B / Orcarouter**. Wizard detects missing assets, in-flight download, active model and runtime readiness to propose the minimum required steps. It may invite checkpoint-only download through the existing P2 exact-plan gate. **Service switching (stop current model → free host :8000 → start new → API identity verification → rollback) remains separately gated and NOT_IMPLEMENTED/NOT_RUN.** Retain old Flash-Next P1 backend and all CLI names; this supersedes D-015 only for the interactive primary menu, not its stable internal category routes. Git desired policy/actual observation/event journal remain distinct. Per operator terminal, pinned NVIDIA 27B download **started** (`Fetching 19 files: 84%`); completion not evidenced. Full design: `docs/UNIFIED-MODEL-WIZARD-DESIGN.md`.

## D-021 — Full P1–P7 Wizard source-first delivery (operator accepted 2026-11-06)

Operator instructed **finish the entire Wizard interface now**, even if P2–P7 execution is not yet enabled; qualify and debug real adapters progressively as P2 onward develops. This explicitly approves full menus/action plans/status/roadmap and backend interface wiring in GitHub, **not** Docker/GPU/runtime/service mutation. Root menu remains model-first (D-020), all model actions are available for planning. Implement `wizard/console.py`, `wizard/workflow.py`, `wizard/roadmap.py`, bounded service log viewer and tests. Preserve original P1 `p1_wizard.py`, exact-approval P2 pinned downloader, all P1–P7 CLI aliases, one active GPU model, stable host `:8000/v1`, and separately scoped approval before any stop/start/switch/recovery. No in-flight 27B download disturbance. SOURCE complete does not imply runtime/gateway/recovery PASS; Draft PR remains open until qualifying DGX evidence.

### Design choices not yet finalized

- Remaining runtime/service/inventory contract fields and wizard flags. The source-only N1 recipe schema has been implemented.
- Whether 27B NVFP4/BF16-head vLLM 0.32 support can use stock backend or requires an opt-in patch; exact checkpoint and draft engine mode.
- Proxy/gateway implementation and host port layout; any port or model alias changes require operational approval.
- GPU benchmark thresholds, allowable downtimes, retention policies and available disk capacity.
- Integration strategy and merge ordering of Orcarouter adapter and this management branch.

### When creating a decision

Add a dated ID, why, alternatives, evidence, affected files/branches, rollback if relevant and approval boundary. If reversing a decision, append a superseding ID; never silently overwrite.
