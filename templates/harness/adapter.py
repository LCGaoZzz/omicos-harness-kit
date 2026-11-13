#!/usr/bin/env python3
"""Minimal dry-run adapter template.

This file intentionally does not execute an arbitrary third-party package. Add an
isolated execution path only after the manifest and contract have been reviewed.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    print(json.dumps({
        "schema_version": "1.0",
        "status": "dry_run",
        "artifacts": [],
        "warnings": ["The algorithm entry point is unresolved."],
        "limitations": ["Dry-run output is not a scientific result."],
        "request_echo": {"analysis": request.get("analysis")},
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
