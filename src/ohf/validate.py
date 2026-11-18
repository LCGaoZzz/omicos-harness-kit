"""Validate package contracts offline, without claiming runtime integration."""
from __future__ import annotations

import re
from pathlib import Path

from jsonschema.exceptions import SchemaError

from .contracts import check_schema, load_schema, read_json, schema_errors
from .paths import resource_path
from .metadata import skill_metadata
from .policy import scan_tree


def skill_directory(root: Path, manifest: dict) -> Path:
    if manifest.get("layout", "bundle") == "skill":
        return root
    return resource_path(root, "agent-harness/omicos/skills/" + manifest["name"])


def _readiness(manifest: dict, skill: Path) -> list[str]:
    blockers = []
    source = manifest["source"]
    execution = manifest["execution"]
    entrypoint = manifest["entrypoint"]
    if execution["mode"] != "reviewed":
        blockers.append("execution mode is dry-run")
    if execution["source_execution"] != "reviewed":
        blockers.append("source execution review is not recorded")
    if not source.get("commit"):
        blockers.append("source commit is not pinned")
    license_info = source["license"]
    if license_info["status"] != "confirmed" or not str(license_info.get("evidence") or "").strip():
        blockers.append("confirmed license evidence is missing")
    if entrypoint["kind"] == "command":
        if not entrypoint.get("command") or any(not part.strip() for part in entrypoint["command"]):
            blockers.append("command entrypoint is empty")
    elif entrypoint["kind"] == "python_module":
        if not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", entrypoint.get("module") or ""):
            blockers.append("Python module entrypoint is invalid")
    else:
        blockers.append("algorithm entrypoint is unresolved")
    if manifest.get("unresolved"):
        blockers.append("unresolved contract fields remain")
    if not execution.get("resource_limits"):
        blockers.append("resource limits are missing")
    validation = execution.get("validation")
    if not validation:
        blockers.append("runtime validation evidence is missing")
    else:
        try:
            evidence = resource_path(skill, validation["evidence_path"])
            if not evidence.is_file() or evidence.stat().st_size == 0:
                blockers.append("runtime validation evidence file is missing or empty")
        except ValueError as exc:
            blockers.append(str(exc))
    return blockers


def validate(root: Path, *, request: Path | None = None, result: Path | None = None,
             require_runtime_ready: bool = False) -> dict:
    root = Path(root)
    errors: list[str] = []
    manifest = None
    schemas: dict[str, object] = {}
    boundary = scan_tree(root)
    errors.extend(item["path"] + ": " + item["finding"] for item in boundary["findings"])
    if boundary["ok"]:
        root = root.resolve()
        try:
            manifest = read_json(resource_path(root, "harness-manifest.json"))
            errors.extend(schema_errors(manifest, load_schema("harness-manifest.schema.json"), "manifest"))
        except (OSError, ValueError) as exc:
            errors.append(f"manifest: {exc}")
    skill = None
    if manifest is not None and not errors:
        try:
            skill = skill_directory(root, manifest)
            content = resource_path(skill, "SKILL.md").read_text(encoding="utf-8")
            metadata = skill_metadata(content)
            if metadata["name"] != manifest["name"]:
                errors.append("SKILL.md: name must match the manifest name")
            for kind, relative in manifest["contracts"].items():
                path = resource_path(root, relative)
                if not path.is_relative_to(skill):
                    raise ValueError(f"{kind} must be inside the skill directory")
                schema = read_json(path)
                if not isinstance(schema, dict) or schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                    raise ValueError(f"{kind} must be a Draft 2020-12 schema object")
                check_schema(schema)
                schemas[kind] = schema
            evidence = manifest["execution"].get("validation", {}).get("evidence_path")
            if evidence:
                resource_path(skill, evidence)
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"skill contract: {exc}")
        except SchemaError as exc:
            errors.append(f"skill contract: invalid schema: {exc.message}")
    for label, supplied, schema_key in (("request", request, "request_schema"), ("result", result, "result_schema")):
        if supplied is not None:
            if schema_key not in schemas:
                errors.append(f"{label}: bundle schema is unavailable")
            else:
                try:
                    errors.extend(schema_errors(read_json(Path(supplied)), schemas[schema_key], label))
                except (OSError, ValueError) as exc:
                    errors.append(f"{label}: {exc}")
    scaffold_valid = not errors
    blockers = _readiness(manifest, skill) if scaffold_valid else ["package contract is invalid"]
    runtime_ready = scaffold_valid and not blockers
    if require_runtime_ready and not runtime_ready:
        errors.append("runtime readiness required: " + "; ".join(blockers))
    return {
        "ok": not errors,
        "status": "runtime_ready" if runtime_ready else ("scaffold_valid" if scaffold_valid else "invalid"),
        "scaffold_valid": scaffold_valid,
        "runtime_ready": runtime_ready,
        "runtime_readiness_basis": "declared_contract_and_recorded_evidence_only",
        "integration_verified": False,
        "readiness_blockers": blockers,
        "errors": errors,
        "boundary": boundary,
    }
