from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from shutil import move

from forja_digital_ingest.frontmatter import parse_frontmatter

REQUIRED_FIELDS = [
    "title",
    "problem",
    "target_user",
    "desired_outcome",
    "constraints",
    "budget_level",
    "urgency",
    "author",
]

LAYOUT_DIRS = ["inbox", "processing", "archive", "rejected", "projects"]


@dataclass
class RunStats:
    processed: int = 0
    accepted: int = 0
    rejected: int = 0


def ensure_layout(base_dir: Path) -> None:
    for item in LAYOUT_DIRS:
        (base_dir / item).mkdir(parents=True, exist_ok=True)


def slugify(value: str, max_len: int = 40) -> str:
    clean = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return (clean[:max_len] or "initiative").rstrip("-")


def validate_metadata(metadata: dict) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        val = metadata.get(field)
        if not isinstance(val, str) or not val.strip():
            errors.append(f"Missing or empty required field: {field}")
    return errors


def process_file(base_dir: Path, source_file: Path) -> tuple[bool, str]:
    processing_dir = base_dir / "processing"
    archive_dir = base_dir / "archive"
    rejected_dir = base_dir / "rejected"
    projects_dir = base_dir / "projects"

    processing_file = processing_dir / source_file.name
    move(str(source_file), str(processing_file))

    raw_text = processing_file.read_text(encoding="utf-8")
    try:
        parsed = parse_frontmatter(raw_text)
    except Exception as exc:  # pragma: no cover
        parsed = None
        errors = [f"Frontmatter parse error: {exc}"]
    else:
        errors = validate_metadata(parsed.metadata)

    if errors:
        rejected_target = rejected_dir / processing_file.name
        move(str(processing_file), str(rejected_target))

        error_file = rejected_dir / f"{rejected_target.stem}.errors.json"
        error_file.write_text(json.dumps({"errors": errors}, indent=2), encoding="utf-8")
        return False, rejected_target.name

    assert parsed is not None
    now = datetime.now(UTC)
    initiative_id = f"{now.strftime('%Y%m%d-%H%M%S')}-{slugify(parsed.metadata['title'])}"

    project_root = projects_dir / initiative_id
    project_root.mkdir(parents=True, exist_ok=False)

    initiative_payload = {
        "initiative_id": initiative_id,
        "status": "NEW",
        "created_at": now.isoformat(),
        "source_file": processing_file.name,
        "metadata": parsed.metadata,
    }
    (project_root / "initiative.json").write_text(
        json.dumps(initiative_payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    (project_root / "input.md").write_text(parsed.body.strip() + "\n", encoding="utf-8")
    (project_root / "opportunity-brief.md").write_text(
        "# Opportunity Brief\n\nPending automatic enrichment.\n",
        encoding="utf-8",
    )

    archived_name = f"{initiative_id}__{processing_file.name}"
    move(str(processing_file), str(archive_dir / archived_name))
    return True, initiative_id


def process_inbox(base_dir: Path) -> RunStats:
    ensure_layout(base_dir)

    inbox_dir = base_dir / "inbox"
    stats = RunStats()

    for md_file in sorted(inbox_dir.glob("*.md")):
        stats.processed += 1
        ok, _ = process_file(base_dir, md_file)
        if ok:
            stats.accepted += 1
        else:
            stats.rejected += 1

    return stats
