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
The protected name/port checks are provisional until N2 read-only inventory.
