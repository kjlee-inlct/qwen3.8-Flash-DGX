"""Read-only Manifest-based cache inventory, including protected legacy Orcarouter.

No downloads, container modifications, HF cache writes, recipes registration,
GPU use, model loads or file moves. SOURCE_FILES_PRESENT is NOT GPU-qualified.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
from typing import Any

from scripts.manager.p2_27b_inventory import _indexed_shards, _file_info
from scripts.manager import manifest_registry
from scripts.manager.ple_assets import (ASSET_ID as PLE_ASSET_ID, inspect_ple_asset,
                                        asset_spec as read_ple_spec)
from scripts.manager.service_manifest import policy
from scripts.manager.service_status import inspect_live_status

ROOT = Path(__file__).resolve().parents[2]
DISCOVERY_MANIFEST = ROOT / "runtimes" / "model-discovery.json"
REV = re.compile(r"^[a-f0-9]{40}$")
MODEL_ID = re.compile(r"^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$")
MAX_REVISIONS = 16
MAX_OTHER_REPOS = 80


def _roots(doc: dict, home: Path, env: dict[str, str]) -> list[Path]:
    raw = list(doc.get("cache_roots", []))
    if doc.get("include_hf_cache_environment") and env.get("HF_CACHE"):
        raw.insert(0, env["HF_CACHE"])
    if doc.get("include_hf_cache_environment") and env.get("HF_HOME"):
        raw.insert(0, env["HF_HOME"])
    result = []
    for item in raw:
        if not isinstance(item, str) or not item.strip():
            continue
        path = (home / item[2:]) if item.startswith("~/") else Path(item)
        if not path.is_absolute():
            continue
        path = path.expanduser()
        if path not in result:
            result.append(path)
    return result


def _revisions(repo_path: Path, pinned: str | None) -> list[str]:
    revisions = []
    if pinned and REV.fullmatch(pinned):
        revisions.append(pinned)
    for tag in ("main", "master"):
        path = repo_path / "refs" / tag
        try:
            revision = path.read_text(encoding="utf-8").strip()
        except (OSError, UnicodeError):
            continue
        if REV.fullmatch(revision) and revision not in revisions:
            revisions.append(revision)
    snap_dir = repo_path / "snapshots"
    try:
        # Bounded directory traversal, no recursive search or weight reads.
        with os.scandir(snap_dir) as items:
            for item in items:
                if len(revisions) >= MAX_REVISIONS:
                    break
                if REV.fullmatch(item.name) and item.is_dir(follow_symlinks=False):
                    if item.name not in revisions:
                        revisions.append(item.name)
    except OSError:
        pass
    return revisions[:MAX_REVISIONS]


def _snapshot(snapshot: Path, revision: str) -> dict[str, Any]:
    config = _file_info(snapshot / "config.json")
    tokenizer = _file_info(snapshot / "tokenizer.json")
    names, errors = _indexed_shards(snapshot)
    shard_status = [_file_info(snapshot / n)["status"] for n in names]
    missing = sum(s != "PRESENT" for s in shard_status)
    complete = (config["status"] == "PRESENT"
                and tokenizer["status"] == "PRESENT"
                and bool(names) and not errors and missing == 0)
    return {
        "revision": revision,
        "snapshot": str(snapshot),
        "state": ("SOURCE_FILES_PRESENT_UNQUALIFIED" if complete
                  else "SNAPSHOT_INCOMPLETE_OR_UNVERIFIED"),
        "source_files_present": complete,
        "metadata_present": {
            "config": config["status"] == "PRESENT",
            "tokenizer": tokenizer["status"] == "PRESENT",
            "weight_index": not errors,
        },
        "indexed_shard_count": len(names),
        "missing_or_unreadable_shards": missing,
        "issues": errors,
        "runtime_qualified": False,
    }


def _other_repos(roots: list[Path], known: set[str]) -> tuple[list[dict], bool]:
    found = []
    truncated = False
    for root in roots:
        try:
            with os.scandir(root / "hub") as entries:
                for item in entries:
                    if len(found) >= MAX_OTHER_REPOS:
                        truncated = True
                        break
                    if not item.name.startswith("models--") or not item.is_dir(follow_symlinks=False):
                        continue
                    # Extra discoveries are unverified names, not install claims.
                    ident = item.name[len("models--"):].replace("--", "/", 1)
                    if ident in known or not MODEL_ID.fullmatch(ident):
                        continue
                    candidate = root / "hub" / item.name
                    revs = _revisions(candidate, None)
                    if not revs:
                        continue
                    found.append({
                        "repo_id": ident, "cache_root": str(root),
                        "revisions_observed": revs,
                        "state": "UNREGISTERED_CACHE_SNAPSHOT_OBSERVED",
                    })
        except OSError:
            continue
    return found, truncated


def installed_models(*, manifest: dict | None = None, home: Path | None = None,
                     environment: dict[str, str] | None = None,
                     service_inspector=inspect_live_status) -> dict[str, Any]:
    config = (manifest_registry.load("model_discovery")
              if manifest is None else manifest)
    if config.get("schema_version") != 1 or not isinstance(config.get("models"), dict):
        raise ValueError("invalid model discovery manifest")
    if config.get("ple_asset_manifest") not in (None, "runtimes/ple-assets.json"):
        raise ValueError("INVALID_PLE_ASSET_MANIFEST_LOCATION")
    home = Path.home() if home is None else Path(home)
    env = os.environ if environment is None else environment
    roots = _roots(config, home, env)
    try:
        service = service_inspector()
    except (OSError, RuntimeError, ValueError) as exc:
        service = {"status": "BLOCKED", "observed_model": None,
                   "issues": ["SERVICE_READ_FAILED:" + type(exc).__name__]}
    active_verified = service.get("status") == "LIVE_SERVICE_VERIFIED"
    observed = service.get("observed_model")
    registered = policy().get("models", {})
    results = []
    for model, spec in config["models"].items():
        repo_id = spec.get("repo_id")
        pin = spec.get("pinned_revision")
        if not isinstance(repo_id, str) or not MODEL_ID.fullmatch(repo_id):
            raise ValueError("invalid model repo ID in discovery manifest")
        if pin is not None and (not isinstance(pin, str) or not REV.fullmatch(pin)):
            raise ValueError("invalid revision in discovery manifest")
        repo_dir = "models--" + repo_id.replace("/", "--", 1)
        sightings = []
        for cache in roots:
            location = cache / "hub" / repo_dir
            if not location.is_dir():
                continue
            for rev in _revisions(location, pin):
                snap = location / "snapshots" / rev
                if snap.is_dir():
                    sightings.append({"cache_root": str(cache),
                                      **_snapshot(snap, rev)})
        view = spec.get("recipe_view")
        if isinstance(view, str) and view.startswith("~/"):
            view = str(home / view[2:])
        else:
            view = None
        view_seen = bool(view is not None and Path(view).is_dir())
        ready = any(x["source_files_present"] for x in sightings)
        result_state = ("SOURCE_FILES_PRESENT_UNQUALIFIED" if ready else
                        "SNAPSHOT_INCOMPLETE_OR_UNVERIFIED" if sightings else
                        "RECIPE_VIEW_ONLY_SOURCE_UNVERIFIED" if view_seen else
                        "NOT_FOUND_IN_CONFIGURED_ROOTS")
        asset_id = spec.get("ple_asset_id")
        if asset_id is not None and asset_id != PLE_ASSET_ID:
            raise ValueError("UNKNOWN_REGISTERED_PLE_ASSET")
        ple = inspect_ple_asset(asset_id=asset_id, roots=roots) if asset_id else None
        if ple is not None and (ple.get("source_repo") != repo_id
                                or ple.get("revision") != pin):
            raise ValueError("MODEL_PLE_PIN_MISMATCH")
        results.append({
            "model": model, "repo_id": repo_id,
            "service_manifest_registered": model in registered,
            "manifest_revision": pin,
            "source_state": result_state,
            "ple_asset": ple,
            "source_files_present": ready,
            "cache_snapshots": sightings,
            "legacy_recipe_view": {
                "path": view, "directory_present": view_seen,
                "runtime_qualified": False,
            } if view is not None else None,
            "currently_observed_running": observed == model,
            "active_api_identity_verified": active_verified and observed == model,
            "installation_authorized": False, "runtime_qualified": False,
        })
    unregistered, truncated = _other_repos(
        roots, {row["repo_id"] for row in results})
    integrity = manifest_registry.validate() if manifest is None else None
    return {
        "schema_version": 1, "stage": "models", "action": "list-installed",
        "status": ("READ_ONLY_INVENTORY" if integrity is None or
                   integrity["status"] == "PASS" else "BLOCKED"),
        "issues": [] if integrity is None else list(integrity["issues"]),
        "scope": "CONFIGURED_CACHE_ROOTS_ONLY",
        "manifest": str(DISCOVERY_MANIFEST),
        "manifest_integrity": integrity,
        "ple_asset_manifest": ("runtimes/ple-assets.json"
                               if any(s.get("ple_asset_id") for s in config["models"].values())
                               else None),
        "cache_roots_checked": [str(p) for p in roots],
        "models": results, "other_cached_repos": unregistered,
        "other_cached_repos_truncated": truncated,
        "active_model_observed": observed,
        "active_api_identity_verified": active_verified,
        "service_status": service.get("status"),
        "service_issues": service.get("issues", []),
        "executed": False, "operations_enabled": False,
        "notice": ("Source file existence is not proof of installation provenance, "
                   "recipe registration, runtime support or launch authorization. "
                   "No cache or running service has been modified."),
    }
