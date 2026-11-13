#!/usr/bin/env python3
"""Copy a reviewed public bundle into a user-selected workspace.

This is a local file operation. It does not deploy to a production runtime.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    source = args.bundle.resolve()
    target = args.destination.resolve()
    if not (source / "harness-manifest.json").is_file():
        raise SystemExit("bundle is missing harness-manifest.json")
    if target.exists() and any(target.iterdir()):
        raise SystemExit(f"destination is not empty: {target}")
    target.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        if path.name == "validation":
            continue
        destination = target / path.name
        if path.is_dir():
            shutil.copytree(path, destination)
        else:
            shutil.copy2(path, destination)
    print(json.dumps({"ok": True, "destination": str(target), "production_deployed": False}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
