"""Read-only evidence for P1 source checkpoint / Hybrid discrepancies."""
from __future__ import annotations
import json
import os
from pathlib import Path
from scripts.manager.p1_assets import audit_checkpoint, _audit_files, SHA40, SHARED_METADATA

REQUIRED_METADATA = ("model.safetensors.index.json", "tokenizer.json")


def probe_file(path: Path, repository: Path) -> dict:
    """Explain missing files, dangling HF symlinks and unexpected file sizes."""
    linked = path.is_symlink()
    try:
        path.lstat()
    except FileNotFoundError:
        return {"status": "MISSING", "symlink": False, "size_bytes": None}
    except OSError:
        return {"status": "STAT_UNAVAILABLE", "symlink": linked, "size_bytes": None}
    try:
        destination = path.resolve(strict=True)
        repo_root = repository.resolve(strict=True)
        if not destination.is_relative_to(repo_root):
            status, size = "TARGET_OUTSIDE_REPOSITORY", None
        elif not path.is_file():
            status, size = "NOT_REGULAR_FILE", None
        else:
            size = path.stat().st_size
            status = "PRESENT_NONEMPTY" if size else "ZERO_BYTES"
    except (OSError, RuntimeError):
        status, size = ("DANGLING_SYMLINK" if linked else "UNREADABLE"), None
    info = {"status": status, "symlink": linked, "size_bytes": size}
    if status == "TARGET_OUTSIDE_REPOSITORY" and linked:
        # Blazux follows existing metadata symlinks. These may be valid.
        # Never mark arbitrary external shard links compatible.
        try:
            info["p1_metadata_link_compatible"] = (
                path.name in SHARED_METADATA and path.stat().st_size > 0)
            info["resolved_target_size_bytes"] = path.stat().st_size
        except OSError:
            info["p1_metadata_link_compatible"] = False
            info["resolved_target_size_bytes"] = None
    if path.name == "model.safetensors.index.json" and size is not None:
        info["exceeds_old_16mib_gate"] = size > 16 * 1024 * 1024
        info["exceeds_current_64mib_gate"] = size > 64 * 1024 * 1024
    return info


def inspect(cache_root: Path) -> dict:
    cache = cache_root.expanduser().resolve()
    repo = cache / "hub/models--nvidia--Qwen3.8-Flash-Next-NVFP4"
    revisions = {}
    for ref in ("main", "master"):
        try:
            value = (repo / "refs" / ref).read_text().strip()
            revisions[ref] = value if SHA40.fullmatch(value) else None
        except OSError:
            revisions[ref] = None
    rows = []
    snap = repo / "snapshots"
    if snap.is_dir():
        try:
            names = sorted(p.name for p in snap.iterdir()
                           if p.is_dir() and SHA40.fullmatch(p.name))[:16]
        except OSError:
            names = []
        for rev in names:
            source = snap / rev
            hybrid = snap / (rev + "-fp8hybrid")
            try:
                source_issues = _audit_files(source, repo)
                hybrid_issues = _audit_files(hybrid, repo) if hybrid.is_dir() else []
            except (OSError, ValueError, TypeError):
                source_issues, hybrid_issues = ["audit_unavailable"], ["audit_unavailable"]
            rows.append({
                "revision": rev,
                "source_issues": source_issues,
                "source_metadata": {name: probe_file(source / name, repo)
                                    for name in REQUIRED_METADATA},
                "hybrid_metadata": {name: probe_file(hybrid / name, repo)
                                    for name in REQUIRED_METADATA},
                "hybrid_present": hybrid.is_dir(),
                "hybrid_marker_present": (hybrid / ".prepared").is_file(),
                "hybrid_issues": hybrid_issues,
            })
    try:
        incomplete_count = sum(1 for _ in (repo / "blobs").glob("*.incomplete"))
    except OSError:
        incomplete_count = None
    return {
        "type": "P1_READ_ONLY_CACHE_DIAGNOSIS",
        "uncompleted_blob_files": incomplete_count,
        "cache_root": str(cache),
        "refs": revisions,
        "snapshots": rows,
        "wizard_audit": audit_checkpoint(cache),
        "mutation_performed": False,
    }

def main() -> None:
    home = Path(os.environ.get("HF_CACHE", str(Path.home()/".cache/huggingface")))
    print(json.dumps(inspect(home), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
