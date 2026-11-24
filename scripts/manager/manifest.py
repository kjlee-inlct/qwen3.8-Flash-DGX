#!/usr/bin/env python3
"""Fail-closed recipe YAML/JSON schema validation. NEVER runs Docker or GPU.

CPU dependencies: PyYAML>=6,<7 and jsonschema>=4.18,<5.
Run: python3 -m scripts.manager.manifest validate recipes/qwen38-27b.candidate.yaml
Exit: 0=valid source shape (NOT permission to launch), 2=invalid, 3=blocked/dependency/io.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "schemas" / "recipe.schema.json"
MAX_RECIPE_SIZE = 256 * 1024
# Port/name protection is a runtime inventory decision, not a static ban.
# N2 inventory checks live Docker and socket ownership before any launch plan.


class RecipeError(ValueError):
    """Invalid recipe syntax, schema or mandatory safety property."""


def _dependencies():
    try:
        import yaml
        from jsonschema import Draft202012Validator
    except ImportError as exc:
        raise RuntimeError("Install CPU-only requirements-manager.txt") from exc
    return yaml, Draft202012Validator


def load_recipe(path: Path) -> Any:
    yaml, _ = _dependencies()
    if not path.is_file():
        raise RuntimeError("Recipe path must be an existing regular file")
    if path.stat().st_size > MAX_RECIPE_SIZE:
        raise RecipeError("recipe exceeds 256 KiB limit")

    class NoDuplicateSafeLoader(yaml.SafeLoader):
        def construct_mapping(self, node, deep=False):
            self.flatten_mapping(node)
            mapping = {}
            for key_node, value_node in node.value:
                key = self.construct_object(key_node, deep=deep)
                if not isinstance(key, str):
                    raise RecipeError("non-string YAML key")
                if key in mapping:
                    raise RecipeError("duplicate YAML key")
                mapping[key] = self.construct_object(value_node, deep=deep)
            return mapping

    # Reject aliases and anchors rather than attempting to resolve arbitrary YAML graphs.
    class NoAliasSafeLoader(NoDuplicateSafeLoader):
        def compose_node(self, parent, index):
            if self.check_event(yaml.AliasEvent):
                raise RecipeError("YAML aliases are unsupported")
            event = self.peek_event()
            if getattr(event, "anchor", None) is not None:
                raise RecipeError("YAML anchors are unsupported")
            return super().compose_node(parent, index)

    try:
        return yaml.load(path.read_text(encoding="utf-8"), Loader=NoAliasSafeLoader)
    except yaml.YAMLError as exc:
        raise RecipeError("invalid YAML syntax or unsafe tag") from exc
    except UnicodeError as exc:
        raise RecipeError("invalid UTF-8 recipe") from exc


def validate_recipe(data: Any, *, schema_path: Path = SCHEMA) -> list[str]:
    _, validator_type = _dependencies()
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator_type.check_schema(schema)
    errors = list(validator_type(schema).iter_errors(data))
    messages = [f"schema:{'/'.join(map(str, err.absolute_path)) or '$'}:{err.validator}"
                for err in errors]
    if isinstance(data, dict):
        runtime = data.get("runtime")
        if isinstance(runtime, dict):
            ref, digest = runtime.get("image_ref"), runtime.get("image_digest")
            if isinstance(ref, str) and isinstance(digest, str) and "@" in ref and ref.rsplit("@", 1)[1] != digest:
                messages.append("semantic:runtime/image_ref:image_digest_mismatch")
    return sorted(set(messages))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a recipe; no launch, downloads or mutations")
    parser.add_argument("command", choices=["validate"])
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        issues = validate_recipe(load_recipe(args.path))
    except RecipeError as exc:
        print(json.dumps({"status": "FAIL", "scope": "SOURCE", "issues": [str(exc)]}))
        return 2
    except (RuntimeError, OSError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "scope": "CPU", "issues": [type(exc).__name__]}))
        return 3
    status = "PASS" if not issues else "FAIL"
    print(json.dumps({"status": status, "scope": "SOURCE", "validation_only": True,
                      "launch_authorized": False, "issues": issues}, sort_keys=True))
    return 0 if not issues else 2


if __name__ == "__main__":
    sys.exit(main())
