from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from app.services.imports.cjm_validator import ValidationResult

BACKEND_DIR = Path(__file__).resolve().parents[3]
DEFAULT_REPORT_DIR = BACKEND_DIR / "data" / "import_reports"


def _build_importance_mapping_summary(validation: ValidationResult) -> list[dict[str, object]]:
    summary: dict[tuple[str, str], dict[str, object]] = {}

    for row in validation.normalized_sheets["03_Важности ЛПР"]:
        raw_value = str(row.values.get("Важность") or "").strip()
        mapped_value = str(row.values.get("_factor_type") or "other")
        key = (raw_value, mapped_value)
        item = summary.setdefault(
            key,
            {
                "raw_importance_value": raw_value,
                "mapped_value": mapped_value,
                "count": 0,
                "example_lpr_id": str(row.values.get("LPR ID") or "").strip(),
            },
        )
        item["count"] = int(item["count"]) + 1

    return sorted(
        summary.values(),
        key=lambda item: (str(item["mapped_value"]), str(item["raw_importance_value"])),
    )


def build_report_payload(
    validation: ValidationResult,
    *,
    mode: str,
    status: str,
    database_counts: dict[str, dict[str, int]] | None = None,
    force: bool = False,
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
    unmapped_importance_factors = [
        issue.as_dict()
        for issue in validation.issues
        if issue.issue_type == "unmapped_importance_factor"
    ]
    manual_update_protection = [
        issue.as_dict()
        for issue in validation.issues
        if issue.issue_type == "manual_update_protection"
    ]

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "file": str(validation.file_path),
        "mode": mode,
        "status": status,
        "force": force,
        "summary": {
            "rows_total": sum(validation.rows_read.values()),
            "rows_valid": sum(validation.rows_valid.values()),
            "errors_count": validation.errors_count,
            "warnings_count": validation.warnings_count,
        },
        "sheet_summary": sheet_summary,
        "planned_create_or_update_ids": planned_upserts,
        "unmapped_importance_factors": unmapped_importance_factors,
        "manual_update_protection": manual_update_protection,
        "importance_factor_mapping_summary": _build_importance_mapping_summary(validation),
        "database_counts": database_counts or {},
        "issues": [issue.as_dict() for issue in validation.issues],
    }


def write_import_report(
    validation: ValidationResult,
    *,
    mode: str,
    status: str,
    database_counts: dict[str, dict[str, int]] | None = None,
    force: bool = False,
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
        force=force,
    )
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
