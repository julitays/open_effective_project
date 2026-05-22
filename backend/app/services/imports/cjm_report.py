from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.services.imports.cjm_validator import ValidationResult

BACKEND_DIR = Path(__file__).resolve().parents[3]
DEFAULT_REPORT_DIR = BACKEND_DIR / "data" / "import_reports"


def build_report_payload(
    validation: ValidationResult,
    *,
    mode: str,
    status: str,
    database_counts: dict[str, dict[str, int]] | None = None,
) -> dict[str, object]:
    sheet_summary = {
        sheet_name: {
            "rows_read": validation.rows_read[sheet_name],
            "rows_valid": validation.rows_valid[sheet_name],
            "errors": sum(
                issue.severity == "error" and issue.sheet_name == sheet_name
                for issue in validation.issues
            ),
            "warnings": sum(
                issue.severity == "warning" and issue.sheet_name == sheet_name
                for issue in validation.issues
            ),
        }
        for sheet_name in validation.rows_read
    }
    planned_upserts = {
        key: sorted(values) for key, values in validation.identifiers.items()
    }

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "file": str(validation.file_path),
        "mode": mode,
        "status": status,
        "summary": {
            "rows_total": sum(validation.rows_read.values()),
            "rows_valid": sum(validation.rows_valid.values()),
            "errors_count": validation.errors_count,
            "warnings_count": validation.warnings_count,
        },
        "sheet_summary": sheet_summary,
        "planned_create_or_update_ids": planned_upserts,
        "database_counts": database_counts or {},
        "issues": [issue.as_dict() for issue in validation.issues],
    }


def write_import_report(
    validation: ValidationResult,
    *,
    mode: str,
    status: str,
    database_counts: dict[str, dict[str, int]] | None = None,
    report_dir: str | Path = DEFAULT_REPORT_DIR,
) -> Path:
    report_path = Path(report_dir)
    report_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    output_path = report_path / f"{validation.file_path.stem}_{mode}_{timestamp}.json"
    payload = build_report_payload(
        validation,
        mode=mode,
        status=status,
        database_counts=database_counts,
    )
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
