"""Create a deterministic tar archive of a generated bundle."""
from __future__ import annotations

import hashlib
import tarfile
from pathlib import Path


def package(root: Path, output: Path) -> dict:
    root = root.resolve()
    output = output.resolve()
    if output.exists():
        raise FileExistsError(output)
    entries = sorted(p for p in root.rglob("*") if p.is_file() and ".git" not in p.parts)
    digest = hashlib.sha256()
    with tarfile.open(output, "w:gz") as archive:
        for path in entries:
            data = path.read_bytes()
            digest.update(path.relative_to(root).as_posix().encode())
            digest.update(data)
            archive.add(path, arcname=path.relative_to(root).as_posix(), recursive=False)
    return {"archive": str(output), "files": len(entries), "content_sha256": digest.hexdigest()}
