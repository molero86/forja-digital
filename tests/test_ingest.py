from __future__ import annotations

import json
from pathlib import Path

from forja_digital_ingest.ingest import process_inbox


def test_process_valid_markdown(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir(parents=True)

    sample = """---
title: Demo project
problem: There is no shared booking system
target_user: Residents
desired_outcome: Shared booking flow
constraints: Limited budget
budget_level: low
urgency: medium
author: tester
---

Project description.
"""
    (inbox / "demo.md").write_text(sample, encoding="utf-8")

    stats = process_inbox(tmp_path)
    assert stats.processed == 1
    assert stats.accepted == 1
    assert stats.rejected == 0

    projects = list((tmp_path / "projects").iterdir())
    assert len(projects) == 1
    payload = json.loads((projects[0] / "initiative.json").read_text(encoding="utf-8"))
    assert payload["status"] == "NEW"
    assert payload["metadata"]["title"] == "Demo project"


def test_process_invalid_markdown(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir(parents=True)

    sample = """---
title: Missing fields
author: tester
---

Invalid body.
"""
    (inbox / "invalid.md").write_text(sample, encoding="utf-8")

    stats = process_inbox(tmp_path)
    assert stats.processed == 1
    assert stats.accepted == 0
    assert stats.rejected == 1

    errors = tmp_path / "rejected" / "invalid.errors.json"
    assert errors.exists()


def test_process_bom_utf8_markdown(tmp_path: Path) -> None:
    inbox = tmp_path / "inbox"
    inbox.mkdir(parents=True)

    sample = "\ufeff---\n"
    sample += "title: BOM project\n"
    sample += "problem: Input with BOM\n"
    sample += "target_user: Team\n"
    sample += "desired_outcome: Parse correctly\n"
    sample += "constraints: None\n"
    sample += "budget_level: low\n"
    sample += "urgency: low\n"
    sample += "author: tester\n"
    sample += "---\n\nBody\n"

    (inbox / "bom.md").write_text(sample, encoding="utf-8")

    stats = process_inbox(tmp_path)
    assert stats.processed == 1
    assert stats.accepted == 1
    assert stats.rejected == 0