from __future__ import annotations

import argparse
from pathlib import Path

from forja_digital_ingest.ingest import process_inbox


def main() -> int:
    parser = argparse.ArgumentParser(description="Forja Digital inbox ingestion")
    parser.add_argument("--base-dir", default=".", help="Project root with inbox folder")
    args = parser.parse_args()

    base_dir = Path(args.base_dir).resolve()
    stats = process_inbox(base_dir)

    print(
        f"Processed={stats.processed} Accepted={stats.accepted} Rejected={stats.rejected}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
