# P3-E — Flash-Next FP8-hybrid runtime source draft (not released)

**2026-11-07 KST | Source draft after real third DGX read-only audit.**

The user-operated DGX Spark third batch actually PASSed the **P3-D read-only GPU + port 8000 PID process audit**, with `--sudo-ss` attributing both `docker-proxy` PIDs to active 27B, while E was `DRAFT_REVIEW_REQUIRED`, F local **136/136 CPU PASS**, G current-ID/journal **PREVIEW PASS**. Exact third actual DGX evidence: [P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md](P3-D-G-THIRD-DGX-READONLY-ACCEPTANCE-20261107.md).

## Source addition

- `recipes/qwen38-flash-next.runtime.draft.json` — **explicitly `launch_allowed=false` and `register_as_runtime_recipe=false`**. This file is **NOT** `recipes/qwen38-flash-next.runtime.json`, and it is NOT registered under `runtimes/service-policy.json.models.flash-next.runtime_recipe`. It cannot be used by generic `load_desired("flash-next")` to launch/replace/install.
- `scripts/manager/flash_recipe_review.py` — read-only JSON loader with strict vLLM 0.32 / NVIDIA SHA / source variant / image / fixed :8000 / one-model hard gates, checks current `docker inspect` against **documented known fields** only; immutable SHA256 of draft content. Actual Docker argv is never executed as code and no Docker mutations are available from this module.
- `scripts/manager/p3_dg_acceptance.py::stage_e` includes a `source_draft_field_review` subsection. `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED` means *only reviewed fields* matched; `DRAFT_FIELD_MISMATCH_REVIEW_REQUIRED` lists specific mismatched fields and `DRAFT_REVIEW_UNAVAILABLE` denotes missing or untrusted source. All results still have `launch_allowed=false` and `executed=false`.
- `tests/test_flash_recipe_draft_cpu.py` — eight Fake-DGX tests for documented exact matches, image/argument/JSON/tool-template drift, malformed or accidentally executable draft and P3-E nonrelease status. The unified P3-F runner now contains **six** CPU suites (previously five), adding this new test file.

## Known pinned Flash source observations (not asserted independently reinstalled)

- Model: `nvidia/Qwen3.8-Flash-Next-NVFP4`, source revision `fc694b54fb0174e0913e6adf86691ef85a4ead47`, local prepared `-fp8hybrid` view; verified `.prepared` and essential file **presence** (not full model-weight checksums).
- Image `sha256:9479fc92a9244fcf137afb36ed778e07495e29663a81db193736fcaa1f15e137`, `Entrypoint=["vllm","serve"]`, served API `qwen3.8-flash-next`, port `8000`, GPU all, IPC host, 16 GiB SHM.
- vLLM Flash command: context 500000, 8 sequences, GPU utilization `0.80`, prefix caching, prompt-token details, chunked prefill and 8192 batch tokens. `-cc.cudagraph_mode=PIECEWISE` and `-cc.splitting_ops` are only checked as present, NOT fully requalified.
- Native tool flags `--enable-auto-tool-choice --tool-call-parser qwen3_coder --reasoning-parser qwen3`, effort alias template at `/qwen38/chat_template.jinja`, MTP `num_speculative_tokens=2`, Yarn `rope_parameters` as preserved in the full observed `--hf-overrides` JSON.
- Preserved writable `/hf` is described as observed, not automatically approved as a future install policy. The draft checks an independent **read-only effort-template bind** and `VLLM_FP8_HYBRID=1` environment; failure is a review mismatch, not an automatic override of the historical record.

## How to run the read-only source draft review on DGX

After clean local fast-forward:

```bash
cd ~/Workspace/llm/blazux-orcarouter
git status --short
git pull --ff-only origin feature/recipe-wizard-handoff

# The same single-entry D-G batch; the privileged socket check is OPTIONAL but
# already necessary in this environment to independently resolve :8000 PIDs.
sudo -v && bash scripts/temporary/p3-d-g-acceptance.sh --run --sudo-ss \
  --report /tmp/p3-d-g-flash-draft-$(date +%Y%m%dT%H%M%S).json
```

Check `stages.P3-E.source_draft_field_review.status`, `issues`, `draft_recipe_sha256` and `stages.P3-E.status`. If the comparator says `MATCHES_DOCUMENTED_FIELDS_REVIEW_REQUIRED`, this is only **read-only field match**. E still returns `DRAFT_REVIEW_REQUIRED` until an independently qualified **real** Flash reinstall-ready recipe is designed, source tests pass and an authorized actual DGX recreation/restore trial is performed.

**No live Flash/27B switch, container creation/removal, image/cache deletion, P3-A/B/C rerun, PR merge or executor release is authorized.**

## Remaining real acceptance for P3-E/F/G

1. Review every actual current Flash environment, host extra mount (including effort alias file source), model/FP8 extension provenance, cache mount write policy, CPU affinity, image build labels and P1 benchmark evidence. A match on this draft is explicitly NOT complete Docker spec replay.
2. Approve a specific versioned **installable** Flash recipe only after reviewing 1; implement a separate, bounded Flash creation adapter and its Fake-DGX failure/rollback tests. Do **not** reuse canonical 27B-only Docker builder with Flash args.
3. During a distinct approved maintenance window, stop running model, create qualified Flash container with clean current Docker ID, inspect API/Native Tools/MTP/Yarn/benchmark and rollback on failure; preserve model caches/image and historical P3 receipts. Do not auto-delete backup.
4. P3-G requires an independent authorized **real** bidirectional switch and controlled failure/restore/UX acceptance; until then `production_released=false`, `acceptance_complete=false`.
 
**Source CI:** [GitHub Actions 42373758262](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42373758262) SUCCESS, **854/854 CPU/Fake-DGX tests in 38 groups**, including the unified runner's `--cpu-only` and direct draft eight-test suite. These are *source only*, not proof of a new Flash install.
