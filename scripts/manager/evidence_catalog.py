"""Safe read-only model history and explicit copy-only legacy evidence import.

The service policy manifest owns the model IDs. Legacy phase directories are
read sources, NEVER targets for deletion/rewrite. Locks, retry markers and
transition journals are intentionally excluded from evidence imports.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SERVICE_POLICY = ROOT / "runtimes/service-policy.json"
REPORTS = ROOT / "reports"
LEGACY = Path.home() / ".local/state/blazux-wizard"
LEGACY_OPERATOR = Path.home() / "blazux-p3-reports"
MAX_BYTES = 1048576
HEX64 = re.compile(r"^[0-9a-f]{64}$")
STAGES = {"a": ("flash-next", "27b"),
          "b": ("27b", "flash-next"),
          "c": ("flash-next", "27b")}


def model_ids(policy: Path = SERVICE_POLICY) -> dict[str, str]:
    raw = json.loads(policy.read_text(encoding="utf-8"))
    entries = raw.get("models")
    if not isinstance(entries, dict):
        raise ValueError("MODEL_POLICY_INVALID")
    result = {}
    for key, entry in entries.items():
        if isinstance(entry, dict):
            served = entry.get("served_id")
            if isinstance(served, str) and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}", served):
                result[key] = served
            elif (served is None and isinstance(key, str)
                  and re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}", key)):
                # Unqualified placeholders are discoverable, not executable.
                result[key] = key
    return result


def _private_bytes(path: Path, root: Path) -> bytes:
    if root.is_symlink() or path.is_symlink() or not path.is_file():
        raise ValueError("EVIDENCE_LINK_OR_MISSING")
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("EVIDENCE_ESCAPES_SOURCE")
    st = path.stat()
    if st.st_size < 1 or st.st_size > MAX_BYTES or st.st_mode & 0o077:
        raise ValueError("EVIDENCE_SIZE_OR_PERMISSIONS")
    return path.read_bytes()


def _document(path: Path, root: Path) -> tuple[dict, bytes, str]:
    raw = _private_bytes(path, root)
    doc = json.loads(raw)
    if not isinstance(doc, dict):
        raise ValueError("EVIDENCE_NOT_JSON_OBJECT")
    return doc, raw, hashlib.sha256(raw).hexdigest()


def _json_candidates(root: Path, pattern: str) -> list[Path]:
    if root.is_symlink() or not root.is_dir():
        return []
    return [p for p in sorted(root.glob(pattern)) if p.name.endswith(".json")]


def _sources(*, legacy: Path, operator: Path, reports: Path,
             ids: dict[str, str]) -> list[tuple[Path, Path, str, str]]:
    """Items: path, trust root, destination relative to reports, source label."""
    flash = ids.get("flash-next", "qwen3.8-flash-next")
    model27 = ids.get("27b", "qwen3.8-27b")
    out: list[tuple[Path, Path, str, str]] = []
    for key, model in (("p1", flash), ("p2", model27)):
        root = legacy / key
        for path in _json_candidates(root, "*.json"):
            out.append((path, root, "models/" + model, "legacy-" + key))
    p2extra = legacy / "p2" / "evidence"
    for path in _json_candidates(p2extra, "*.json"):
        out.append((path, p2extra, "models/" + model27, "legacy-27b-download"))
    p3 = legacy / "p3"
    for stage, (start, target) in STAGES.items():
        path = p3 / ("stage-" + stage + ".json")
        if path.exists() or path.is_symlink():
            out.append((path, p3,
                        "transitions/" + start + "--to--" + target,
                        "legacy-switch-" + stage))
    for path in _json_candidates(p3, "p1-diagnostics-*.json"):
        out.append((path, p3, "diagnostics/" + flash, "legacy-flash-diagnostics"))
    # Historic P3 operator reports are reporting artifacts, never state.
    for path in _json_candidates(operator, "*.json"):
        out.append((path, operator, "transitions/legacy-operator",
                    "legacy-transition-operator"))
    # Project-native files may be already present: those are indexed by history
    # but are never imported back into themselves.
    return out


def _destination(reports: Path, relative: str, name: str, digest: str) -> Path:
    if not HEX64.fullmatch(digest):
        raise ValueError("DIGEST_INVALID")
    path = reports / relative
    return path / ("import-" + digest[:16] + "-" + name)


def _records(*, legacy: Path, operator: Path, reports: Path,
             ids: dict[str, str], include_project: bool = True
             ) -> tuple[list[dict[str, Any]], list[str]]:
    found: list[dict[str, Any]] = []
    issues: list[str] = []
    src = _sources(legacy=legacy, operator=operator, reports=reports, ids=ids)
    if include_project and reports.is_symlink():
        issues.append("UNTRUSTED_PROJECT_REPORTS_SYMLINK")
        include_project = False
    if include_project:
        # Only known narrow report trees; never scan arbitrary repo paths.
        for key, model in ids.items():
            root = reports / "models" / model
            for path in _json_candidates(root, "*.json"):
                src.append((path, root, "models/" + model, "project-model"))
        for folder in ("transitions", "diagnostics"):
            root = reports / folder
            if root.is_dir() and not root.is_symlink():
                for sub in root.iterdir():
                    if sub.is_dir() and not sub.is_symlink():
                        for path in _json_candidates(sub, "*.json"):
                            src.append((path, sub, folder + "/" + sub.name,
                                        "project-" + folder))
    for path, root, relative, origin in src:
        try:
            doc, raw, digest = _document(path, root)
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError):
            issues.append("UNTRUSTED_OR_UNREADABLE:" + origin + "/" + path.name)
            continue
        model = None
        action = None
        category = "other"
        metric = None
        summary: dict[str, Any] = {}
        involved_model_ids: list[str] = []
        status = doc.get("status")
        if relative.startswith("models/"):
            model = relative.split("/", 1)[1]
            involved_model_ids = [model]
            action = doc.get("action")
            if action in ("verify", "benchmark"):
                category = action
            elif (path.name.endswith(".benchmark.json") or
                  (isinstance(doc.get("benchmark"), dict) and doc.get("benchmark"))):
                category, action = "benchmark", "benchmark"
                status = status or (doc.get("benchmark") or {}).get("status")
            elif doc.get("trial") is not None:
                category, action = "trial", "trial"
                status = status or doc.get("trial")
            elif action == "download":
                category = "download"
            else:
                category = "model_event"
            result = doc.get("result")
            if category == "verify" and isinstance(result, dict):
                summary = {
                    "baseline_status": result.get("baseline_status"),
                    "extended_status": result.get("extended_status"),
                    "probes": {key: (val.get("status") if isinstance(val, dict) else None)
                               for key, val in (result.get("probes") or {}).items()
                               if key in ("default_completion", "chat", "tools", "vision")},
                }
            bench = result.get("benchmark") if isinstance(result, dict) else None
            bench = bench or doc.get("benchmark")
            if isinstance(bench, dict):
                metrics = bench.get("metrics") or {}
                if isinstance(metrics, dict):
                    # 27B explicitly reports *two different* throughputs.
                    # Do not present decode proxy as real end-to-end throughput.
                    summary = {key: metrics.get(key) for key in (
                        "ttft_p50_sec", "ttft_p95_sec",
                        "latency_p50_sec", "latency_p95_sec",
                        "mean_tokens_per_sec", "mean_e2e_tokens_per_sec",
                        "mean_decode_tokens_per_sec_proxy",
                        "total_completion_tokens") if metrics.get(key) is not None}
                    metric = metrics.get("mean_tokens_per_sec")
                    if metric is None:
                        metric = metrics.get("mean_e2e_tokens_per_sec")
                summary.update({
                    "requests": bench.get("requests"),
                    "concurrency": bench.get("concurrency"),
                    "max_tokens": bench.get("max_tokens"),
                    "benchmark_status": bench.get("status")})
        elif relative.startswith("transitions/"):
            category = "transition"
            action = doc.get("stage") or "transition"
            if action in STAGES:
                source, target = STAGES[action]
            else:
                source, target = doc.get("source_model"), doc.get("target_model")
                if source not in ids or target not in ids:
                    source = target = None
            involved_model_ids = [ids[x] for x in (source, target) if x in ids]
            model = ids.get(target) if target in ids else None
            summary = {"from_model": source, "to_model": target,
                       "live_verified": doc.get("live_verified")}
            status = status or ("PASS" if doc.get("live_verified") is True else None)
        elif relative.startswith("diagnostics/"):
            category, action = "diagnostics", "diagnostics"
            model = relative.split("/", 1)[1]
            involved_model_ids = [model]
        stamp = (doc.get("finished_at_utc") or doc.get("finished_utc")
                 or doc.get("started_at_utc") or doc.get("started_utc"))
        if not isinstance(stamp, str):
            # Copies have a NEW mtime. Prefer the source UTC filename to avoid
            # falsely dating an old P2 benchmark or legacy P3 operator run.
            observed = re.search(r"(\d{8}T\d{6}Z)", path.name)
            if observed:
                stamp = datetime.strptime(observed.group(1), "%Y%m%dT%H%M%SZ").replace(
                    tzinfo=timezone.utc).isoformat()
            else:
                stamp = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
        try:
            parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
            stamp = parsed.astimezone(timezone.utc).isoformat() if parsed.tzinfo else ""
        except (ValueError, OverflowError):
            stamp = ""
        found.append({
            "timestamp_utc": stamp,
            "model_id": model,
            "involved_model_ids": involved_model_ids,
            "summary": summary,
            "action": str(action) if action is not None else "unknown",
            "category": category, "status": str(status or "UNKNOWN"),
            "mean_tokens_per_sec": metric if type(metric) in (int, float) else None,
            "source": origin, "path": str(path), "sha256": digest,
            "imported": path.name.startswith("import-"),
            "destination": str(_destination(reports, relative, path.name, digest))
                if not origin.startswith("project-") else None,
        })
    return found, issues


def history(*, model: str | None = None, kind: str = "all", limit: int = 20,
            legacy: Path = LEGACY, operator: Path = LEGACY_OPERATOR,
            reports: Path = REPORTS, policy: Path = SERVICE_POLICY) -> dict:
    if not 1 <= limit <= 100:
        return {"status": "BLOCKED", "issues": ["INVALID_HISTORY_LIMIT"], "executed": False}
    ids = model_ids(policy)
    if model is not None and model not in ids and model not in ids.values():
        return {"status": "BLOCKED", "issues": ["UNKNOWN_MODEL_ID"], "executed": False}
    wanted = ids.get(model, model)
    if kind not in ("all", "verify", "benchmark", "trial", "transition", "download", "diagnostics"):
        return {"status": "BLOCKED", "issues": ["UNKNOWN_EVIDENCE_CATEGORY"], "executed": False}
    records, issues = _records(legacy=legacy, operator=operator, reports=reports, ids=ids)
    # Imported duplicates and their original are the SAME evidence. Prefer
    # project-local provenance, keeping a verified original source reference.
    unique: dict[str, dict] = {}
    for rec in records:
        if wanted and wanted not in rec["involved_model_ids"]:
            continue
        if kind != "all" and rec["category"] != kind:
            continue
        key = rec["sha256"]
        if key not in unique or rec["source"].startswith("project-"):
            unique[key] = rec
    selected = sorted(unique.values(),
                      key=lambda d: (d["timestamp_utc"], d["path"]), reverse=True)
    return {"status": "READ_ONLY_HISTORY", "executed": False,
            "model": wanted or "all", "category": kind,
            "count": len(selected), "records": selected[:limit],
            "issues": sorted(set(issues))}


def migration_plan(*, legacy: Path = LEGACY, operator: Path = LEGACY_OPERATOR,
                   reports: Path = REPORTS, policy: Path = SERVICE_POLICY) -> dict:
    ids = model_ids(policy)
    entries = []
    issues = []
    if reports.is_symlink():
        return {"status": "BLOCKED", "executed": False, "approved": False,
                "issues": ["REPORTS_DIRECTORY_SYMLINK"], "plan_id": None,
                "entries": [], "copy_count": 0, "already_copied": 0}
    for path, root, relative, origin in _sources(
            legacy=legacy, operator=operator, reports=reports, ids=ids):
        try:
            _, _, digest = _document(path, root)
            dest = _destination(reports, relative, path.name, digest)
            if not dest.resolve().is_relative_to(reports.resolve()):
                raise ValueError("OUTPUT_ESCAPES_REPORTS")
            if dest.exists() or dest.is_symlink():
                existing = _private_bytes(dest, dest.parent)
                if hashlib.sha256(existing).hexdigest() != digest:
                    raise ValueError("DESTINATION_HASH_CONFLICT")
                state = "ALREADY_COPIED"
            else:
                state = "COPY"
            entries.append({"source": str(path), "destination": str(dest),
                            "sha256": digest, "state": state, "source_type": origin})
        except (OSError, ValueError, UnicodeError, json.JSONDecodeError) as exc:
            issues.append("MIGRATION_SOURCE_INVALID:" + origin + "/" + path.name +
                          ":" + type(exc).__name__)
    entries.sort(key=lambda x: (x["source_type"], x["source"]))
    signature = hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"status": "BLOCKED" if issues else "READY_TO_REQUEST_COPY_APPROVAL",
            "plan_id": signature if not issues else None,
            "executed": False, "approved": False, "issues": issues,
            "copy_count": sum(x["state"] == "COPY" for x in entries),
            "already_copied": sum(x["state"] == "ALREADY_COPIED" for x in entries),
            "entries": entries,
            "notice": "COPY ONLY. Never delete original P2/P3 evidence, locks, journals or state. "
                      "P3-C still requires its own separate downtime approval."}


def copy_approved(plan_id: str | None, *, legacy: Path = LEGACY,
                  operator: Path = LEGACY_OPERATOR, reports: Path = REPORTS,
                  policy: Path = SERVICE_POLICY) -> dict:
    if not isinstance(plan_id, str) or not HEX64.fullmatch(plan_id):
        return {"status": "BLOCKED", "executed": False,
                "issues": ["EXACT_MIGRATION_PLAN_APPROVAL_REQUIRED"]}
    plan = migration_plan(legacy=legacy, operator=operator, reports=reports, policy=policy)
    if plan["status"] != "READY_TO_REQUEST_COPY_APPROVAL" or plan["plan_id"] != plan_id:
        return {"status": "BLOCKED", "executed": False,
                "issues": ["MIGRATION_PLAN_CHANGED_OR_BLOCKED"]}
    written = []
    try:
        if reports.is_symlink():
            raise ValueError("REPORTS_DIRECTORY_SYMLINK")
        # Ensure private roots, not only private leaf folders. Existing
        # non-private ancestors are rejected, never chmod'd silently.
        for parent in (reports, reports / "models", reports / "transitions",
                       reports / "diagnostics"):
            if parent.exists() and (parent.is_symlink()
                                    or not parent.is_dir()
                                    or parent.stat().st_mode & 0o077):
                raise ValueError("REPORT_ROOT_PERMISSIONS_UNSAFE")
        for item in plan["entries"]:
            if item["state"] == "ALREADY_COPIED":
                continue
            source, dest = Path(item["source"]), Path(item["destination"])
            # Re-read each source just before copying. No bytes are trusted
            # from a stale preflight and no destination is ever overwritten.
            raw = _private_bytes(source, source.parent)
            if hashlib.sha256(raw).hexdigest() != item["sha256"]:
                raise ValueError("SOURCE_CHANGED_DURING_COPY")
            # mkdir(parents=True) can create intermediate ancestors as 0755.
            # Build every report directory at 0700 and reject any preexisting
            # public/symlinked ancestor rather than silently chmod'ing it.
            directory = reports
            for component in ("", *dest.parent.relative_to(reports).parts):
                if component:
                    directory = directory / component
                directory.mkdir(mode=0o700, parents=(directory == reports),
                                exist_ok=True)
                if (directory.is_symlink() or not directory.is_dir()
                        or directory.stat().st_mode & 0o077):
                    raise ValueError("UNSAFE_REPORT_DIRECTORY")
            fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, "wb") as stream:
                stream.write(raw)
                stream.flush()
                os.fsync(stream.fileno())
            written.append(str(dest))
    except (OSError, ValueError) as exc:
        return {"status": "PARTIAL_REVIEW_REQUIRED", "executed": bool(written),
                "copied": len(written), "files": written,
                "issues": [type(exc).__name__], "notice": "No original was modified. "
                          "Do not force or overwrite a conflicted destination."}
    return {"status": "COPY_COMPLETE", "executed": bool(written), "copied": len(written),
            "already_copied": plan["already_copied"], "files": written,
            "issues": [], "notice": "Original legacy state and receipts preserved."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only model evidence history and explicit copy-only migration")
    sub = parser.add_subparsers(dest="action", required=True)
    show = sub.add_parser("list")
    show.add_argument("--model")
    show.add_argument("--kind", default="all")
    show.add_argument("--limit", type=int, default=20)
    migrate = sub.add_parser("migrate")
    mode = migrate.add_mutually_exclusive_group(required=True)
    mode.add_argument("--plan", action="store_true")
    mode.add_argument("--execute", action="store_true")
    mode.add_argument("--guided", action="store_true")
    migrate.add_argument("--approve-plan")
    args = parser.parse_args(argv)
    if args.action == "list":
        doc = history(model=args.model, kind=args.kind, limit=args.limit)
    elif args.plan:
        doc = migration_plan() if not args.approve_plan else {
            "status": "BLOCKED", "issues": ["PLAN_CANNOT_INCLUDE_APPROVAL"],
            "executed": False}
    elif args.guided:
        if args.approve_plan:
            doc = {"status": "BLOCKED", "issues": ["GUIDED_EXACT_MANUAL_APPROVAL_ONLY"],
                   "executed": False}
        else:
            preflight = migration_plan()
            print("Legacy evidence import (copy only, originals untouched)", flush=True)
            print("Status: " + preflight["status"], flush=True)
            print("Copy: " + str(preflight["copy_count"])
                  + " | Already copied: " + str(preflight["already_copied"]), flush=True)
            if preflight["issues"]:
                print("Issues: " + ", ".join(preflight["issues"]), flush=True)
            if preflight["status"] != "READY_TO_REQUEST_COPY_APPROVAL":
                doc = preflight
            else:
                print("Current import plan: " + preflight["plan_id"], flush=True)
                try:
                    typed = input(
                        "Type exactly [" + preflight["plan_id"]
                        + "] to COPY (Enter cancels): ").strip()
                except (EOFError, KeyboardInterrupt):
                    typed = ""
                if typed != preflight["plan_id"]:
                    doc = {"status": "CANCELLED", "executed": False,
                           "issues": [], "copied": 0}
                else:
                    doc = copy_approved(typed)
    else:
        doc = copy_approved(args.approve_plan)
    print(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if doc["status"] in ("READ_ONLY_HISTORY", "READY_TO_REQUEST_COPY_APPROVAL",
                                    "COPY_COMPLETE", "CANCELLED") else 3


if __name__ == "__main__":
    raise SystemExit(main())
