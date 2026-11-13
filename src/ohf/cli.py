"""Command line interface for Omicos Harness Kit."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from .inspect import inspection_plan
from .package import package
from .policy import scan_tree
from .scaffold import generate
from .validate import validate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ohf", description="Public Omicos-compatible harness compiler")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect_p = sub.add_parser("inspect", help="create an evidence-only inspection plan")
    inspect_p.add_argument("repo_url")
    inspect_p.add_argument("--name")
    inspect_p.add_argument("--output", type=Path)
    init_p = sub.add_parser("init", help="generate a neutral harness scaffold")
    init_p.add_argument("--repo", required=True)
    init_p.add_argument("--name", required=True)
    init_p.add_argument("--output", type=Path, required=True)
    validate_p = sub.add_parser("validate", help="validate a generated bundle")
    validate_p.add_argument("root", type=Path)
    package_p = sub.add_parser("package", help="create a deterministic public bundle archive")
    package_p.add_argument("root", type=Path)
    package_p.add_argument("--output", type=Path, required=True)
    scan_p = sub.add_parser("boundary-scan", help="scan a tree for public/private boundary violations")
    scan_p.add_argument("root", type=Path)
    return parser


def emit(value: dict, output: Path | None = None) -> int:
    text = json.dumps(value, indent=2, ensure_ascii=False)
    if output:
        output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "inspect":
            return emit(inspection_plan(args.repo_url, args.name), args.output)
        if args.command == "init":
            manifest = generate(args.repo, args.name, args.output)
            print(json.dumps({"ok": True, "output": str(args.output.resolve()), "id": manifest["id"]}, indent=2))
            return 0
        if args.command == "validate":
            result = validate(args.root)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["ok"] else 2
        if args.command == "boundary-scan":
            result = scan_tree(args.root)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result["ok"] else 2
        if args.command == "package":
            result = package(args.root, args.output)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0
    except (OSError, ValueError, FileExistsError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
