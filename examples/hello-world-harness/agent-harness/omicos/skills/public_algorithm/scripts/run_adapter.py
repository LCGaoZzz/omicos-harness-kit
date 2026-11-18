#!/usr/bin/env python3
"""Validate a request and emit an honest dry-run result. No algorithm is run."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError
from referencing.exceptions import Unresolvable


def _schema(path: Path) -> dict:
    schema = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    def local_refs(value: object) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"$ref", "$dynamicRef"} and (not isinstance(item, str) or not item.startswith("#")):
                    raise ValueError("external schema references are not supported")
                local_refs(item)
        elif isinstance(value, list):
            for item in value:
                local_refs(item)
    local_refs(schema)
    return schema


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    parent = Path(__file__).resolve().parent
    schemas = (parent if (parent / "schemas").is_dir() else parent.parent) / "schemas"
    try:
        request = json.loads(Path(args.request).read_text(encoding="utf-8"))
        Draft202012Validator(_schema(schemas / "request.schema.json"), format_checker=FormatChecker()).validate(request)
        result = {
            "schema_version": "1.0",
            "status": "dry_run",
            "artifacts": [],
            "warnings": ["No algorithm entry point has been executed."],
            "limitations": ["Contract validation is not runtime integration or a scientific result."],
        }
        Draft202012Validator(_schema(schemas / "result.schema.json"), format_checker=FormatChecker()).validate(result)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    except (SchemaError, ValidationError) as exc:
        parser.error(exc.message)
    except Unresolvable as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
