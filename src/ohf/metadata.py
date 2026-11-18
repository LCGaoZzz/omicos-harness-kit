"""Parse skill metadata with safe YAML and actionable errors."""
from __future__ import annotations

import yaml


class UniqueKeyLoader(yaml.SafeLoader):
    def construct_mapping(self, node, deep=False):
        self.flatten_mapping(node)
        mapping = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key in mapping:
                raise ValueError("SKILL.md: metadata keys must be unique strings")
            mapping[key] = self.construct_object(value_node, deep=deep)
        return mapping


def skill_metadata(content: str) -> dict:
    lines = content.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("SKILL.md: YAML frontmatter is required")
    closing = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if closing is None:
        raise ValueError("SKILL.md: YAML frontmatter is not closed")
    try:
        metadata = yaml.load("\n".join(lines[1:closing]), Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"SKILL.md: invalid YAML frontmatter: {exc}") from exc
    if not isinstance(metadata, dict):
        raise ValueError("SKILL.md: frontmatter must be an object")
    for key in ("name", "description"):
        if not isinstance(metadata.get(key), str) or not metadata[key].strip():
            raise ValueError(f"SKILL.md: {key} must be a non-empty string")
    return metadata
