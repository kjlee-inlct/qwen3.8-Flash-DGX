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
