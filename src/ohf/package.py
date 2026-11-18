"""Validate and create reproducible public archives with verifiable digests."""
from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import tarfile
import tempfile
from pathlib import Path

from .paths import bundle_files
from .validate import validate


def file_hashes(root: Path) -> dict[str, str]:
    return {path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in bundle_files(root)}


def content_hash(hashes: dict[str, str]) -> str:
    canonical = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def package(root: Path, output: Path, *, require_runtime_ready: bool = False) -> dict:
    validation = validate(root, require_runtime_ready=require_runtime_ready)
    if not validation["ok"]:
        raise ValueError("bundle validation failed: " + "; ".join(validation["errors"]))
    root = root.resolve()
    if output.is_symlink() or output.exists():
        raise FileExistsError(output)
    output = output.resolve()
    if output.is_relative_to(root):
        raise ValueError("archive output must be outside the bundle")
    if not output.parent.is_dir():
        raise ValueError("archive output parent directory does not exist")
    entries = bundle_files(root)
    hashes: dict[str, str] = {}
    descriptor, temporary = tempfile.mkstemp(prefix=".ohf-archive-", dir=output.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as raw:
            with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed:
                with tarfile.open(fileobj=compressed, mode="w", format=tarfile.PAX_FORMAT) as archive:
                    for path in entries:
                        data = path.read_bytes()
                        name = path.relative_to(root).as_posix()
                        hashes[name] = hashlib.sha256(data).hexdigest()
                        info = tarfile.TarInfo(name)
                        info.size = len(data)
                        info.mode = 0o755 if path.stat().st_mode & 0o111 else 0o644
                        info.mtime = 0
                        info.uid = info.gid = 0
                        info.uname = info.gname = ""
                        archive.addfile(info, io.BytesIO(data))
        archive_sha256 = hashlib.sha256(temporary_path.read_bytes()).hexdigest()
        # A competing writer must never be overwritten by publication of the archive.
        os.link(temporary_path, output)
    finally:
        temporary_path.unlink(missing_ok=True)
    return {"archive": str(output), "files": len(hashes), "files_sha256": hashes,
            "content_sha256": content_hash(hashes), "archive_sha256": archive_sha256,
            "validation": validation}
