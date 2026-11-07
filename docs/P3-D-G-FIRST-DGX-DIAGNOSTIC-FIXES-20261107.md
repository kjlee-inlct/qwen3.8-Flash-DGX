# P3-D–G — First actual DGX unified draft verdict and targeted diagnostic fixes (2026-11-07)

## Evidence boundary

The operator fast-forwarded the repository and ran the first `scripts/temporary/p3-d-g-acceptance.sh --plan` and `--run` on the real DGX Spark. The operator supplied the full stage-verdict JSON. This records **actual read-only DGX evidence**, NOT real model-switch/rollback, release, or GPU benchmark. The Docker/API/HF checkpoint service was not modified by the acceptance runner.

## Original DGX observations (before diagnostic fixes)

| Stage | Actual verdict | Evidence | Correct interpretation |
| --- | --- | --- | --- |
| P3-D | BLOCKED | Active model 27B, only Docker GPU container `qwen38-27b`, only Docker host-port 8000 owner `qwen38-27b`, NVIDIA compute PID 2051842 and `gpu_process_exclusivity_verified=true`; host port PID unverified and `HOST_PORT_8000_LISTENER_NOT_UNAMBIGUOUS` | No GPU conflict shown; port OS socket/PID audit **incomplete**, not proof of port theft |
| P3-E | BLOCKED | `FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED`, `FLASH_RUNTIME_CONFIG_UNPARSEABLE`, no observed candidate | The code reused the narrow canonical-27B command parser for Flash; preserved Flash Docker metadata needs a separate legacy parser. Reinstall qualification still missing |
| P3-F | SOURCE_CPU_PASS_NOT_RELEASED | Five suites: 28+17+21+38+15 = **119/119 PASS**, `issues=[]`, lifecycle release gate false | Source-only CPU simulation; real DGX lifecycle/rollback not approved |
| P3-G | PREVIEW_PASS_REAL_SWITCH_NOT_RUN | Source 27B `CANONICAL_RECIPE`; target Flash `HISTORICAL_P3_INSTANCE`; current Docker IDs read fresh; journal `VERIFIED/COMMITTED`, `issues=[]` | Real DGX read-only preflight PASS, no 27B→Flash→27B execution |

Overall status was `BLOCKED` due to D/E, and `acceptance_complete=false`. This aggregate outcome does not invalidate the earlier P3-A/B/C historical PASS or the actual live API `LIVE_SERVICE_VERIFIED`.

## Corrective source implementation

1. **P3-D**: `ss -H -ltnp sport = :8000` may show two expected listening sockets (IPv4 `0.0.0.0:8000` and IPv6 `[::]:8000`), formerly misclassified as ambiguous by `len(rows) != 1`. The reader now parses LOCAL port specifically, accepts up to four matching listener rows, requires each socket to expose PID data, and reports socket rows, PID attribution, `ss` status and errors. A peer-only `:8000` cannot be counted as a local listener. Missing/unknown PIDs remain BLOCKED.
2. **P3-D Docker proxy**: Host port publishing can be implemented by host-cgroup `docker-proxy` (which is NOT a process in the model container cgroup). A read-only `/proc/PID/cmdline` plus current Docker `NetworkSettings.Networks`/HostConfig binding check can now associate the proxy only when protocol, host port, container port, exact container IP and host binding match. This is not accepted from a process name alone. A foreign/unverifiable proxy remains BLOCKED.
3. **P3-E Flash parsing**: The original Flash serving script has many additional flags not covered by the canonical-27B normalizer. The P3-E audit now records exact `Config.Cmd`, entrypoint, argv parsing status, pinned snapshot/served ID/port, GPU request, host cache source, env and mount without inventing a 27B recipe. Noncanonical argv is a visible `FLASH_LEGACY_COMMAND_NEEDS_MODEL_SPECIFIC_NORMALIZER` advisory, provided required identity and Docker attributes can be independently inspected. Unsafe/missing model identity or historical provenance remain BLOCKED.
4. **P3-E legacy writable cache**: `scripts/serve_flash-next.sh` uses `-v "$HF_CACHE:/hf"` (no `:ro`), so an observed writable Flash mount may be historical valid state; it is now a `FLASH_LEGACY_HF_MOUNT_WRITABLE_REINSTALL_REVIEW` advisory, NOT an automatic match to a secure reinstall recipe. A qualified future recipe must explicitly decide cache mode and preserve old model assets. Nothing remounts or rewrites the cache here.
5. **P3-E canonical gating**: Until Flash has a versioned reviewed and actual-DGX-qualified runtime recipe, `FLASH_CANONICAL_REINSTALL_RECIPE_NOT_QUALIFIED` remains and P3-E may be `DRAFT_REVIEW_REQUIRED`, never `REAL PASS`. G actual transfers and rollback remain separately authorized.

**Source CI**: GitHub Actions [42371091647](https://github.com/kjlee-inlct/qwen3.8-Flash-DGX/actions/runs/42371091647) **SUCCESS: 838/838 CPU tests in 37 groups**. Includes regression tests for IPv4/IPv6, absent listener PIDs, dockerd proxy current container IP, unknown/malicious proxy, legacy Flash argv, writable /hf and mismatched model path/served ID. These results are **not** hardware requalification.

## Next DGX read-only retest (safe)

After a clean worktree and pulling `feature/recipe-wizard-handoff`, run:

```bash
bash scripts/temporary/p3-d-g-acceptance.sh --run \
  --report /tmp/p3-d-g-readonly-v2-$(date +%Y%m%dT%H%M%S).json
```

Expected F is CPU PASS and G is preview PASS if the current service and journal did not drift. D will PASS **only when** all host port listeners (including Docker proxies if used) are fully attributable by actual proc/Docker metadata; otherwise new `observed_port_listener_rows`, `port_pid_attribution` and `ss_returncode` disclose the blocker without mutation. E is expected to contain a complete observed Flash candidate and remain `DRAFT_REVIEW_REQUIRED` until the canonical Flash recipe is qualified. **No unconditional promise of D or E PASS** based on earlier partial observations.

P3-C historical PASS/CLOSED remains untouched, current 27B is not restarted/reinstalled, the usual model lifecycle/operating execution gates remain disabled. The batch cannot conduct a live switch/fault injection or automatically release D–G.
