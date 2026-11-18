"""Load bundled JSON schemas without depending on a source-checkout cwd."""
from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError
from referencing.exceptions import Unresolvable


def load_schema(name: str) -> dict:
    schema = json.loads(files("ohf").joinpath("schemas", name).read_text(encoding="utf-8"))
    check_schema(schema)
    return schema


def check_schema(schema: object) -> None:
    """Keep validation offline: allow local JSON-pointer references only."""
    Draft202012Validator.check_schema(schema)
    def inspect(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"$ref", "$dynamicRef"} and (not isinstance(item, str) or not item.startswith("#")):
                    raise ValueError("schema references must be local JSON pointers; remote/external references are not resolved")
                inspect(item)
        elif isinstance(value, list):
            for item in value:
                inspect(item)
    inspect(schema)


def schema_errors(value: object, schema: object, label: str) -> list[str]:
    try:
        check_schema(schema)
    except (SchemaError, ValueError) as exc:
        return [f"{label}: invalid schema: {exc}"]
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    try:
        return [f"{label}{''.join('[' + str(p) + ']' for p in error.absolute_path)}: {error.message}"
                for error in sorted(validator.iter_errors(value), key=lambda e: str(list(e.absolute_path)))]
    except Unresolvable as exc:
        return [f"{label}: unresolved local schema reference: {exc}"]


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))
