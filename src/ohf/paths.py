"""Portable names and filesystem boundaries for public bundles."""
from __future__ import annotations

import re
from pathlib import Path, PurePosixPath

NAME_RE = re.compile(r"^[a-z][a-z0-9_-]{0,63}$")
IGNORED_PARTS = {".git", "__pycache__"}


def validate_name(name: str) -> str:
    if not isinstance(name, str) or NAME_RE.fullmatch(name) is None:
        raise ValueError("name must be 1-64 lowercase letters, digits, underscores or hyphens, starting with a letter")
    return name


def resource_path(root: Path, relative: str) -> Path:
    """Resolve a portable relative resource without traversing links or parents."""
    if not isinstance(relative, str) or not relative or "\\" in relative or "\x00" in relative:
        raise ValueError("resource path must be a non-empty POSIX relative path")
    parts = relative.split("/")
    if PurePosixPath(relative).is_absolute() or any(p in {"", ".", ".."} or ":" in p for p in parts):
        raise ValueError(f"unsafe resource path: {relative!r}")
    root = root.resolve()
    candidate = root.joinpath(*parts)
    current = root
    for part in parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"symlink resource is not allowed: {relative}")
    if not candidate.resolve().is_relative_to(root):
        raise ValueError(f"resource escapes bundle: {relative}")
    return candidate


def bundle_files(root: Path) -> list[Path]:
    """Enumerate regular files and reject links/special files before copying."""
    if root.is_symlink() or not root.is_dir():
        raise ValueError("bundle root must be a directory, not a symlink")
    root = root.resolve()
    files = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"symlink is not allowed: {relative.as_posix()}")
        if path.is_file():
            if path.suffix not in {".pyc", ".pyo"}:
                files.append(path)
        elif not path.is_dir():
            raise ValueError(f"special file is not allowed: {relative.as_posix()}")
    return files
