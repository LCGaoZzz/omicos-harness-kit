#!/usr/bin/env python3
"""Compatibility wrapper; prefer `ohf install BUNDLE --workspace WORKSPACE`."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ohf.install import install
from ohf.validate import validate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument("--workspace", type=Path)
    destination.add_argument("--destination", type=Path, help="deprecated alias: destination is now a workspace containing skills/")
    parser.add_argument("--replace", action="store_true")
    parser.add_argument("--require-runtime-ready", action="store_true")
    args = parser.parse_args()
    try:
        workspace = args.workspace or args.destination
        if args.destination is not None:
            checked = validate(args.bundle, require_runtime_ready=args.require_runtime_ready)
            if not checked["ok"]:
                raise ValueError("bundle validation failed: " + "; ".join(checked["errors"]))
            print("--destination is deprecated; it denotes the workspace, and the skill is installed under skills/<name>/.", file=sys.stderr)
            workspace.mkdir(parents=True, exist_ok=True)
        result = install(args.bundle, workspace, replace=args.replace,
                         require_runtime_ready=args.require_runtime_ready)
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
