# Reproducible, Git-tracked benchmark summaries

This folder intentionally contains **sanitized, metric-only** summaries of real DGX runs. The original operator evidence, request/response payloads, Docker metadata, plan approvals, host paths and GPU/service logs are **never committed**. Original immutable receipts remain on the DGX under `~/.local/state/blazux-wizard/` and Git-ignored `reports/`.

## Actual, independently approved DGX runs

| Model | Run UTC | Status | Mean tokens/s (measurement definition) | TTFT p50/p95 | Latency p50/p95 | Requests |
| --- | --- | --- | --- | --- | --- | --- |
| NVIDIA Flash-Next (`qwen3.8-flash-next`) | 2026-11-06 23:30:31 | PASS | **37.9527** (client-measured completion tokens / request E2E latency, averaged) | 1.384594 / 1.779602 s | 1.724560 / 1.813754 s | 3 |
| NVIDIA 27B (`qwen3.8-27b`) | 2026-11-06 04:26:42 | BENCH_PASS_RESTORED_VERIFIED | **7.9002** (client E2E), **11.1801** (decode proxy, NOT engine throughput) | 0.179349 / 28.977990 s | 5.818283 / 34.609889 s | 3 |

Links to committed sanitized records:
- [Flash-Next, post-P3-B benchmark](qwen3.8-flash-next/f506db4c76430674.json), source original SHA256 `f506db4c764306748dea7aa87d50b5d75a77dab846b7e742b9fbe1d6808ef8db`.
- [27B, bounded trial benchmark + original Flash restore](qwen3.8-27b/80f109dbd7c97460.json), source original SHA256 `80f109dbd7c9746065a36c8376f3ff440d1b0d58eee2024fcfad3f1733a82dc9`.

These source hashes were confirmed in actual user-supplied Wizard output; published metric-only values were transcribed from that operator evidence. **They are not new benchmark executions** and are not a substitute for original private JSON when authorizing service transitions. Sample size three, concurrency one and max tokens 64 are *bounded smoke/functional measurements*, not saturating-load or long-run performance comparisons. Methods differ, including a 27B trial/restore cycle; do not use the throughput figures as a normalized head-to-head model ranking.

## New runs: publish from an existing private original

The tracked `scripts/manager/benchmark_publication.py` script validates a **source receipt**, admits only explicitly permitted metrics and reproducibility fields, and outputs deterministic JSON without hosts, plan IDs, approval strings, prompts, completion text, private paths, containers, environment variables, or logs. It never calls Docker or the inference API.

```bash
cd ~/Workspace/llm/blazux-orcarouter

# PLAN ONLY: no output files written
python3 -m scripts.manager.benchmark_publication \
  --model flash-next \
  --source ~/.local/state/blazux-wizard/p1/<original-benchmark-receipt>.json \
  --plan

# Only when a source is approved to be PUBLIC: write local Git-trackable summary
python3 -m scripts.manager.benchmark_publication \
  --model flash-next \
  --source ~/.local/state/blazux-wizard/p1/<original-benchmark-receipt>.json \
  --write --approve-sha256 <the-current-source-64-character-SHA256>

# Human-review before normal Git staging/commit:
git diff -- benchmarks/published
git status --short benchmarks/published
```

For 27B use `--model 27b` and the original `~/.local/state/blazux-wizard/p2/<id>.benchmark.json`. Publication is **explicit** and separate from any GPU benchmark approval; simply running Verify/Benchmark never makes its private receipt public, never commits and never pushes. Published JSON must be reviewed before staging. The exporter never changes an existing tracked or untracked summary; if an existing digest-named summary differs from current allowlisted fields, it refuses overwrite and requires review.

To reproduce the two existing summaries without writing, use `--verify-published` on each matching original receipt; this compares content and full original source SHA but does not touch Git. This is suitable for checking that the transcribed records agree with the private originals before treating them as fully machine-verified.

### Schema / provenance

- `source_evidence_sha256`: SHA-256 of **original private JSON bytes**; path deliberately omitted.
- `model_id`, `model_repository`, `model_revision` (only when available in source/manifest).
- `measurement_time_utc`: source run's filename UTC timestamp, with seconds precision.
- `profile`: requests, max_tokens, concurrency, seed.
- `metrics`: allowlisted numeric TTFT, latency, E2E throughput, decode proxy and token count.
- `benchmark_status`, `execution_status`, `method`, `limitations`: transparent interpretation.

No personal or operational logs should be staged under this directory. The `results/` and `reports/` ignore policy remains in force.
