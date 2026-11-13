"""Validate generated bundles without executing algorithm code."""
from __future__ import annotations

import json
from pathlib import Path
from .policy import scan_tree

REQUIRED = [
    "harness-manifest.json",
    "README.md",
    "agent-harness/omicos/agents",
    "agent-harness/omicos/skills",
]


def validate(root: Path) -> dict:
    root = root.resolve()
    errors: list[str] = []
    manifest = None
    manifest_path = root / "harness-manifest.json"
    if not manifest_path.is_file():
        errors.append("missing harness-manifest.json")
    else:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid harness-manifest.json: {exc}")
    for relative in REQUIRED[1:]:
        if not (root / relative).exists():
            errors.append(f"missing {relative}")
    if manifest:
        for key in ("manifest_version", "kit_version", "contract_version", "id", "name", "source", "entrypoint", "execution", "provenance"):
            if key not in manifest:
                errors.append(f"manifest missing key: {key}")
        if manifest.get("provenance", {}).get("source_copied") is True:
            errors.append("manifest claims source_copied=true")
        if manifest.get("provenance", {}).get("user_data_copied") is True:
            errors.append("manifest claims user_data_copied=true")
        if manifest.get("execution", {}).get("production_deployed") is True:
            errors.append("public kit cannot claim production deployment")
    boundary = scan_tree(root)
    errors.extend(item["path"] + ": " + item["finding"] for item in boundary["findings"])
    return {"ok": not errors, "errors": errors, "boundary": boundary}
