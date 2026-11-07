## 2026-11-07 — Canonical 27B Native Tools runtime recipe (supersedes separate variant switch design)

The user chose **one canonical `qwen38-27b` container**, not persistent original-vs-native two-container switching. New `recipes/qwen38-27b.runtime.json` pins the ACTUALLY DGX-verified `qwen3_coder`, `qwen3`, NVIDIA Jinja, exact vLLM image and :8000 launch profile. Desired `runtimes/service-policy.json` now references this canonical recipe; it does NOT mean existing Docker `Config.Cmd` was changed.

The separate `recipes/qwen38-27b-native-tools-v1.candidate.yaml` remains a historical incomplete trial candidate, **not the production recipe**. The existing `recipes/qwen38-27b.candidate.yaml` remains intentionally invalid/historical; neither should be launched. One-shot native tool inference was REAL DGX PASS, but canonical migration is **NOT_RUN** until explicit fresh operator TTY approval.

Use `bash scripts/temporary/p2-27b-native-recipe-migrate.sh --plan` first, then `--execute` only after downtime and verified-old-container-deletion acknowledgement; successful migration validates normal chat/tools/SSE, completes a fresh 3-request benchmark, atomically replaces **only the latest active benchmark pointer** and deletes ONLY verified stopped old backup Docker container. Existing benchmark receipts, P3 A/B/C receipts, images and HF caches survive. `--status` is a separate read-only post migration audit. See [canonical runtime migration runbook](../docs/P2-27B-CANONICAL-NATIVE-RECIPE-MIGRATION-20261107.md).

---

## 2026-11-07 — P2-FINAL Native Tools V1 separate candidate (NOT LAUNCHABLE)

`recipes/qwen38-27b-native-tools-v1.candidate.yaml` declares a distinct container name `qwen38-27b-native-tools-v1` using the same pinned NVIDIA 27B and :8000 **only after** stopping the original. This second YAML is deliberately schema-INCOMPLETE (unverified exact image/source), source-only and NOT in the live service manifest. Never use `docker run` from a preview. Use `bash scripts/serve_27b.sh --tools-variant-plan` for fail-closed read-only inspection (expected exit code 3); see `docs/P2-27B-NATIVE-TOOLS-V1-PROTECTED-VARIANT-20261107.md`. Original `qwen38-27b`, P3 receipts, Flash and HF caches remain protected. A source recipe cannot grant downtime consent.

---

# Recipe registry (P0/N1: source schema only)

Recipes are YAML checked against schemas/recipe.schema.json by
scripts/manager/manifest.py. This branch does not provide a model loader,
wizard switch action, or permission to modify the running service.

The 27B candidate qwen38-27b.candidate.yaml is deliberately invalid until
actual source/pins/PLE are verified. Synthetic test SHA values under
tests/fixtures are placeholders, not a model or image. Validity of a recipe
means structural checks only; it does NOT prove checkpoint provenance,
model support, operational safety, or permission to launch.

Install CPU-only requirements-manager.txt, then run:

    python3 -m unittest discover -s tests -p 'test_manager_manifest_cpu.py' -v
    python3 -m scripts.manager.manifest validate recipes/qwen38-27b.candidate.yaml

Candidate exit status MUST be 2 (FAIL). Even exit 0 cannot authorize
Docker actions, model downloads, GPU use or deletion.
The former static Orcarouter name/8000 bans were removed on 2026-11-05 after user reported removal. N2 inventory now checks actual Docker container names and socket listeners; source format PASS is never permission to launch.

## P2 27B local cache discovery (source-only; no download)

`nvidia/Qwen3.8-27B-NVFP4` is the currently selected candidate checkpoint ID. The prior RadixArk DGX inspection is historical and is not NVIDIA cache evidence. Its published
model files are not proof of pinned vLLM-0.32 support or local availability.
To inspect *existing* files and symlinks without Docker, sockets, model download
or GPU calls, run:

```bash
./wizard.sh model 27b status --inspect-cache --json
```

The JSON `inspection` reports refs/main/master, indexed shard file existence,
quantization metadata presence and incomplete transfer counts. A
`SOURCE_FILES_PRESENT_UNPINNED` result is deliberately **not** P2 READY.
The candidate recipe still fails schema validation until exact source SHA,
model revision, architecture support, image SHA256 digest and runtime
compatibility have actual evidence. All `prepare`, `start`, `verify`,
`benchmark` actions remain BLOCKED.

## NVIDIA 27B pinned acquisition (updated 2026-11-05)

The P2 selected repository is `nvidia/Qwen3.8-27B-NVFP4`. Its immutable source revision is `482ca0f3832238542f8f5295dde86b5f22711d80`, as verified on the official Hugging Face tree. The candidate recipe pins this revision and desired `:8000` port, but **remains intentionally INVALID** until source runtime SHA, image digest, architecture/quantization loader, PLE/MTP and DGX API validation are reviewed. `nvidia/Qwen3.8-Flash-Next-NVFP4` uses the same host API port when active; both cannot run concurrently. Pinned source download is separate and can run while Flash-Next serves.

Read-only plan: `./wizard.sh model 27b plan --for-action download --json`. Guided operator approval: `./wizard.sh model 27b download --guided` (must type fresh full plan ID). Both are backed by the same Wizard download implementation. SOURCE and CPU verification are not actual DGX download/GPU readiness. Consult `docs/P2-27B-WIZARD-OPERATIONS.md` and `runtimes/service-policy.json`.

