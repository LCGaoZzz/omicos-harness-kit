"""Install a complete skill into an existing workspace without executing it."""
from __future__ import annotations

import copy
import hashlib
import json
import os
import shutil
import tempfile
import uuid
from pathlib import Path

from .contracts import read_json
from .package import content_hash, file_hashes
from .paths import bundle_files, resource_path
from .validate import skill_directory, validate


def install(root: Path, workspace: Path, *, replace: bool = False,
            require_runtime_ready: bool = False) -> dict:
    validation = validate(root, require_runtime_ready=require_runtime_ready)
    if not validation["ok"]:
        raise ValueError("bundle validation failed: " + "; ".join(validation["errors"]))
    root = root.resolve()
    workspace = workspace.resolve()
    if not workspace.is_dir():
        raise ValueError("workspace must be an existing directory in the active execution environment")
    manifest = read_json(root / "harness-manifest.json")
    skill = skill_directory(root, manifest)
    skills_root = resource_path(workspace, "skills")
    target = resource_path(workspace, "skills/" + manifest["name"])
    if target.exists() and not replace:
        raise FileExistsError(f"skill already exists; use --replace to preserve a backup and replace it: {target}")
    if target.exists() and not target.is_dir():
        raise ValueError("existing skill destination is not a directory")
    if target.exists():
        bundle_files(target)
    skills_root.mkdir(parents=True, exist_ok=True)
    staging_root = resource_path(skills_root, ".ohf-staging")
    staging_root.mkdir(exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="skill-", dir=staging_root))
    backup = None
    published = False
    try:
        for source in bundle_files(skill):
            relative = source.relative_to(skill).as_posix()
            if relative in {"harness-manifest.json", "installation-receipt.json"}:
                continue
            destination = resource_path(stage, relative)
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination, follow_symlinks=False)
        local_manifest = copy.deepcopy(manifest)
        local_manifest["layout"] = "skill"
        local_manifest["contracts"] = {kind: resource_path(root, path).relative_to(skill).as_posix()
                                       for kind, path in manifest["contracts"].items()}
        (stage / "harness-manifest.json").write_text(json.dumps(local_manifest, indent=2) + "\n", encoding="utf-8")
        local_validation = validate(stage, require_runtime_ready=require_runtime_ready)
        if not local_validation["ok"]:
            raise ValueError("installed skill validation failed: " + "; ".join(local_validation["errors"]))
        hashes = file_hashes(stage)
        receipt = {"schema_version": "1.0", "skill_id": manifest["name"],
                   "contract_version": manifest["contract_version"], "files_sha256": hashes,
                   "content_sha256": content_hash(hashes),
                   "source_manifest_sha256": hashlib.sha256((root / "harness-manifest.json").read_bytes()).hexdigest(),
                   "validation": local_validation, "agents_installed": False,
                   "production_deployed": False, "discovery_verified": False}
        (stage / "installation-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        if target.exists():
            backup = resource_path(skills_root, ".ohf-backups/" + manifest["name"] + "/" + uuid.uuid4().hex)
            backup.parent.mkdir(parents=True, exist_ok=True)
            os.replace(target, backup)
        try:
            os.replace(stage, target)
            published = True
        except BaseException:
            if backup is not None:
                try:
                    os.replace(backup, target)
                except OSError as exc:
                    raise ValueError(f"replacement and restoration failed; previous version remains in backup: {backup}") from exc
            raise
        return {"ok": True, "skill_id": manifest["name"], "workspace": str(workspace),
                "destination": str(target), "backup": str(backup) if backup else None,
                "validation": local_validation, "content_sha256": receipt["content_sha256"],
                "agents_installed": False, "production_deployed": False, "discovery_verified": False,
                "next_step": "Refresh skills in the product's active workspace; file installation does not grant entitlement or prove discovery."}
    finally:
        if not published and stage.exists():
            shutil.rmtree(stage)
