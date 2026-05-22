from __future__ import annotations

import argparse
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.imports.cjm_importer import CJMImporter  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate or import a CJM MVP Excel file.")
    parser.add_argument("--file", required=True, type=Path, help="Path to the filled Excel file.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true", help="Validate and create a report only.")
    mode.add_argument("--commit", action="store_true", help="Validate and write valid data to the DB.")
    args = parser.parse_args()

    import_mode = "commit" if args.commit else "dry-run"
    result = CJMImporter().run(args.file, import_mode)
    print(f"Mode: {result.mode}")
    print(f"Status: {result.status}")
    print(f"Rows read: {sum(result.validation.rows_read.values())}")
    print(f"Valid rows: {sum(result.validation.rows_valid.values())}")
    print(f"Errors: {result.validation.errors_count}")
    print(f"Warnings: {result.validation.warnings_count}")
    print(f"Report: {result.report_path}")

    return 1 if result.validation.has_errors or result.status == "commit_failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
