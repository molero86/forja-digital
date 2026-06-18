from __future__ import annotations

from dataclasses import dataclass

import yaml


@dataclass
class ParsedMarkdown:
    metadata: dict
    body: str


def parse_frontmatter(raw_text: str) -> ParsedMarkdown:
    text = raw_text.lstrip("\ufeff")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        return ParsedMarkdown(metadata={}, body=raw_text)

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break

    if end_idx is None:
        raise ValueError("Invalid frontmatter delimiters")

    yaml_block = "\n".join(lines[1:end_idx])
    body = "\n".join(lines[end_idx + 1 :])

    data = yaml.safe_load(yaml_block) or {}
    if not isinstance(data, dict):
        raise ValueError("Frontmatter must be a key/value object")

    return ParsedMarkdown(metadata=data, body=body)
