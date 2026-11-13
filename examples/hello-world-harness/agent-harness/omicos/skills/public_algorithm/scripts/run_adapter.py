#!/usr/bin/env python3
"""Dry-run public adapter. Replace only after the contract is reviewed."""
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    args = parser.parse_args()
    request = json.loads(Path(args.request).read_text(encoding="utf-8"))
    result = {
        "schema_version": "1.0",
        "status": "dry_run",
        "artifacts": [],
        "warnings": ["No algorithm entry point has been reviewed or executed."],
        "limitations": ["This scaffold is not a scientific result and is not a production deployment."],
        "request_echo": {"analysis": request.get("analysis")},
    }
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
