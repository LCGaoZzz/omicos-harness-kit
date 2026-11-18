"""Public/private boundary checks for generated bundles."""
from __future__ import annotations

import re
from pathlib import Path
from .paths import bundle_files

SECRET_PATTERNS = [
    re.compile(r"gh" + r"[pousr]_" + r"[A-Za-z0-9_\-]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_\-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|secret|token)\s*[:=]\s*['\"][^'\"]{12,}['\"]"),
]
PRIVATE_PATH_PATTERNS = [
    re.compile("/" + "data" + "/users/"),
    re.compile("/" + "home" + "/[^/]+/"),
    re.compile(r"[A-Za-z]:\\Users\\"),
    re.compile(r"git\.chatgpt-team\.site"),
]
PRIVATE_ASSET_TERMS = {
    "omicos" + "-core",
    "private" + "_mcp",
    "internal" + "_catalog",
    "production" + "_secret",
}


def scan_file(path: Path) -> list[str]:
    try:
        text = path.read_text(encoding="utf-8", errors="strict")
    except OSError:
        return ["file could not be read for boundary validation"]
    except UnicodeError:
        return []
    findings: list[str] = []
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            findings.append(f"secret-like pattern: {pattern.pattern}")
    for pattern in PRIVATE_PATH_PATTERNS:
        if pattern.search(text):
            findings.append(f"private path/host pattern: {pattern.pattern}")
    lowered = text.lower()
    for term in PRIVATE_ASSET_TERMS:
        if term in lowered:
            findings.append(f"private asset term: {term}")
    return findings


def scan_tree(root: Path) -> dict:
    findings: list[dict[str, str]] = []
    try:
        files = bundle_files(root)
    except (OSError, ValueError) as exc:
        return {"ok": False, "findings": [{"path": ".", "finding": str(exc)}]}
    root = root.resolve()
    for path in files:
        for finding in scan_file(path):
            findings.append({"path": path.relative_to(root).as_posix(), "finding": finding})
    return {"ok": not findings, "findings": findings}
