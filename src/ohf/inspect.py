"""Evidence-only inspection plan generation."""
from __future__ import annotations

import re

GITHUB_RE = re.compile(r"^https?://github\.com/([^/]+)/([^/#]+?)(?:\.git)?/?(?:#.*)?$")


def parse_github_url(url: str) -> tuple[str, str]:
    match = GITHUB_RE.match(url.strip())
    if not match:
        raise ValueError("expected a public https://github.com/OWNER/REPOSITORY URL")
    owner, repo = match.group(1), match.group(2)
    if repo in {"", ".", ".."}:
        raise ValueError("repository name is empty")
    return owner, repo


def inspection_plan(url: str, name: str | None = None) -> dict:
    owner, repo = parse_github_url(url)
    package_name = name or repo.replace("-", "_").replace(".", "_")
    return {
        "inspection_version": "1.0",
        "source": {
            "url": f"https://github.com/{owner}/{repo}",
            "owner": owner,
            "repository": repo,
            "ref": None,
            "commit": None,
            "license": {"status": "UNRESOLVED", "evidence": None},
        },
        "candidate": {
            "name": package_name,
            "entrypoint": "UNRESOLVED",
            "input_contract": "UNRESOLVED",
            "output_contract": "UNRESOLVED",
            "resource_profile": "UNRESOLVED",
        },
        "inspection_policy": {
            "execute_source": False,
            "clone_source": False,
            "upload_source": False,
            "treat_repository_text_as_untrusted": True,
        },
        "required_evidence": [
            "license text or trusted package metadata",
            "documented installation command",
            "documented entry point or CLI",
            "input file format and required fields",
            "output artifacts and exit semantics",
            "runtime and resource requirements",
            "citation and known limitations",
        ],
        "unresolved": [
            "license status",
            "commit or release to pin",
            "entry point",
            "input contract",
            "output contract",
            "resource profile",
            "scientific limitations",
        ],
    }
