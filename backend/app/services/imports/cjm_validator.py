from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

from app.services.imports.cjm_excel_reader import (
    CJMWorkbookData,
    ExcelRow,
    TEMPLATE_SHEET_COLUMNS,
)
from app.services.imports.cjm_mappings import (
    map_action_status,
    map_action_type,
    map_barrier_status,
    map_barrier_time_status,
    map_barrier_type,
    map_communication_channel,
    map_communication_frequency,
    map_criticality,
    map_direction,
    map_expectation_type,
    map_explicitness,
    map_importance_factor_type,
    map_lifecycle_stage,
    map_operational_model,
    map_plan_confirmation_status,
    map_project_scale,
    map_project_status,
    normalize_label,
)

Severity = Literal["error", "warning"]
Mode = Literal["dry-run", "commit"]

PROJECT_CODE_PATTERN = re.compile(r"^project_[A-Za-z0-9][A-Za-z0-9_-]*$")
LPR_CODE_PATTERN = re.compile(r"^lpr_[A-Za-z0-9][A-Za-z0-9_-]*$")
FORBIDDEN_PII_COLUMNS = {
    normalize_label(value)
    for value in (
        "ФИО",
        "Имя",
        "Телефон",
        "Email",
        "E-mail",
        "Название клиента",
        "Название проекта",
    )
}
PROHIBITED_SHEETS = {
    normalize_label(value)
    for value in (
        "04_История опросов",
        "История опросов",
        "AI-резюме",
        "AI резюме",
        "Справочник_ID",
        "Справочник ID",
    )
}


@dataclass(slots=True)
class ValidationIssue:
    severity: Severity
    sheet_name: str
    row_number: int | None
    message: str
    field_name: str | None = None
    raw_value: object | None = None

    def as_dict(self) -> dict[str, object | None]:
        return {
            "severity": self.severity,
            "sheet_name": self.sheet_name,
            "row_number": self.row_number,
            "message": self.message,
            "field_name": self.field_name,
            "raw_value": self.raw_value,
        }


@dataclass(slots=True)
class NormalizedRow:
    sheet_name: str
    row_number: int
    values: dict[str, object]


@dataclass(slots=True)
class ValidationResult:
    file_path: Path
    mode: Mode
    rows_read: dict[str, int]
    rows_valid: dict[str, int]
    normalized_sheets: dict[str, list[NormalizedRow]]
    issues: list[ValidationIssue] = field(default_factory=list)
    identifiers: dict[str, set[str]] = field(
        default_factory=lambda: {
            "project_ids": set(),
            "lpr_ids": set(),
            "barrier_ids": set(),
            "expectation_ids": set(),
        }
    )
    primary_project_id: str | None = None

    @property
    def errors_count(self) -> int:
        return sum(issue.severity == "error" for issue in self.issues)

    @property
    def warnings_count(self) -> int:
        return sum(issue.severity == "warning" for issue in self.issues)

    @property
    def has_errors(self) -> bool:
        return self.errors_count > 0

    def add_issue(
        self,
        severity: Severity,
        sheet_name: str,
        row_number: int | None,
        message: str,
        field_name: str | None = None,
        raw_value: object | None = None,
    ) -> None:
        self.issues.append(
            ValidationIssue(
                severity=severity,
                sheet_name=sheet_name,
                row_number=row_number,
                message=message,
                field_name=field_name,
                raw_value=raw_value,
            )
        )


def _is_blank(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def _text(value: object) -> str:
    return "" if _is_blank(value) else str(value).strip()


def _required(
    result: ValidationResult,
    row: ExcelRow,
    field_name: str,
    message: str | None = None,
) -> str:
    value = _text(row.values.get(field_name))
    if not value:
        result.add_issue(
            "error",
            row.sheet_name,
            row.row_number,
            message or f"Поле '{field_name}' обязательно.",
            field_name,
            row.values.get(field_name),
        )
    return value


def _validate_project_code(
    result: ValidationResult,
    sheet_name: str,
    row_number: int,
    field_name: str,
    value: str,
) -> None:
    if value and not PROJECT_CODE_PATTERN.fullmatch(value):
        result.add_issue(
            "error",
            sheet_name,
            row_number,
            "Project ID должен быть обезличенным кодом вида project_001.",
            field_name,
            value,
        )


def _validate_lpr_code(
    result: ValidationResult,
    sheet_name: str,
    row_number: int,
    field_name: str,
    value: str,
) -> None:
    if value and not LPR_CODE_PATTERN.fullmatch(value):
        result.add_issue(
            "error",
            sheet_name,
            row_number,
            "LPR ID должен быть обезличенным кодом вида lpr_001.",
            field_name,
            value,
        )


def _linked_lpr_codes(value: object) -> list[str]:
    return [
        part.strip()
        for part in re.split(r"\s*[;,]\s*", _text(value))
        if part.strip()
    ]


def _validate_linked_lpr_codes(
    result: ValidationResult,
    row: ExcelRow,
    field_name: str,
    value: str,
) -> None:
    if not value:
        return

    codes = _linked_lpr_codes(value)
    invalid = [code for code in codes if not LPR_CODE_PATTERN.fullmatch(code)]
    if invalid == ["несколько ЛПР"]:
        result.add_issue(
            "warning",
            row.sheet_name,
            row.row_number,
            "Связь с несколькими ЛПР описана текстом без внутренних LPR ID.",
            field_name,
            value,
        )
        return

    if invalid:
        result.add_issue(
            "error",
            row.sheet_name,
            row.row_number,
            "Связанный LPR ID должен быть одним или несколькими обезличенными кодами вида lpr_001.",
            field_name,
            value,
        )


def _map_field(
    result: ValidationResult,
    row: ExcelRow,
    field_name: str,
    mapper: object,
    *,
    required: bool = False,
    default: str | None = None,
) -> str | None:
    raw_value = row.values.get(field_name)
    if _is_blank(raw_value):
        if required:
            result.add_issue(
                "error",
                row.sheet_name,
                row.row_number,
                f"Поле '{field_name}' обязательно.",
                field_name,
                raw_value,
            )
        return default

    mapped = mapper(raw_value)  # type: ignore[operator]
    if mapped is None:
        result.add_issue(
            "error",
            row.sheet_name,
            row.row_number,
            f"Значение поля '{field_name}' не входит в MVP-справочник.",
            field_name,
            raw_value,
        )
    return mapped


def _append_if_valid(
    result: ValidationResult,
    row: ExcelRow,
    normalized: dict[str, object],
    errors_before_row: int,
    *,
    target_sheet_name: str | None = None,
) -> None:
    if result.errors_count == errors_before_row:
        sheet_name = target_sheet_name or row.sheet_name
        result.normalized_sheets[sheet_name].append(
            NormalizedRow(sheet_name, row.row_number, normalized)
        )
        result.rows_valid[sheet_name] += 1


def _validate_passport_row(result: ValidationResult, row: ExcelRow) -> None:
    errors_before = result.errors_count
    project_code = _required(result, row, "Project ID")
    external_project_id = _required(result, row, "External project ID")
    _validate_project_code(result, row.sheet_name, row.row_number, "Project ID", project_code)

    normalized = dict(row.values)
    normalized["Project ID"] = project_code
    normalized["External project ID"] = external_project_id
    normalized["Направление проекта"] = _map_field(
        result, row, "Направление проекта", map_direction
    )
    normalized["Масштаб проекта"] = _map_field(
        result, row, "Масштаб проекта", map_project_scale, default="unknown"
    )
    normalized["Основная операционная модель"] = _map_field(
        result, row, "Основная операционная модель", map_operational_model
    )
    normalized["Этап жизненного цикла"] = _map_field(
        result, row, "Этап жизненного цикла", map_lifecycle_stage, default="unknown"
    )
    normalized["Статус проекта"] = _map_field(
        result, row, "Статус проекта", map_project_status, default="unknown"
    )
    _append_if_valid(result, row, normalized, errors_before)


def _validate_lpr_row(result: ValidationResult, row: ExcelRow) -> None:
    errors_before = result.errors_count
    lpr_code = _required(result, row, "LPR ID")
    _validate_lpr_code(result, row.sheet_name, row.row_number, "LPR ID", lpr_code)
    _required(result, row, "Роль / зона влияния")

    normalized = dict(row.values)
    normalized["LPR ID"] = lpr_code
    _append_if_valid(result, row, normalized, errors_before)


def _validate_importance_row(result: ValidationResult, row: ExcelRow) -> None:
    errors_before = result.errors_count
    lpr_code = _required(result, row, "LPR ID")
    _validate_lpr_code(result, row.sheet_name, row.row_number, "LPR ID", lpr_code)
    factor_text = _required(result, row, "Важность")
    factor_type = map_importance_factor_type(factor_text)
    if factor_text and factor_type is None:
        factor_type = "other"
        result.add_issue(
            "warning",
            row.sheet_name,
            row.row_number,
            "Важность не сопоставлена со справочником, будет загружена как other.",
            "Важность",
            factor_text,
        )

    normalized = dict(row.values)
    normalized["LPR ID"] = lpr_code
    normalized["Важность"] = factor_text
    normalized["_factor_type"] = factor_type
    normalized["Критичность"] = _map_field(
        result, row, "Критичность", map_criticality, default="unknown"
    )
    _append_if_valid(result, row, normalized, errors_before)


def _validate_barrier_row(result: ValidationResult, row: ExcelRow) -> None:
    errors_before = result.errors_count
    barrier_code = _required(result, row, "Barrier ID")
    _required(result, row, "Название барьера")
    linked_lpr = _text(row.values.get("Связанный LPR ID"))
    _validate_linked_lpr_codes(result, row, "Связанный LPR ID", linked_lpr)

    normalized = dict(row.values)
    normalized["Barrier ID"] = barrier_code
    normalized["Связанный LPR ID"] = linked_lpr or None
    normalized["Тип барьера"] = _map_field(
        result, row, "Тип барьера", map_barrier_type, required=True
    )
    normalized["Временной статус"] = _map_field(
        result, row, "Временной статус", map_barrier_time_status, required=True
    )
    normalized["Критичность"] = _map_field(
        result, row, "Критичность", map_criticality, required=True
    )
    normalized["Статус барьера"] = _map_field(
        result, row, "Статус барьера", map_barrier_status, default="unknown"
    )
    _append_if_valid(result, row, normalized, errors_before)


def _validate_expectation_row(result: ValidationResult, row: ExcelRow) -> None:
    errors_before = result.errors_count
    expectation_code = _required(result, row, "Expectation ID")
    _required(result, row, "Ожидание клиента")
    linked_lpr = _text(row.values.get("Связанный LPR ID"))
    _validate_linked_lpr_codes(result, row, "Связанный LPR ID", linked_lpr)

    normalized = dict(row.values)
    normalized["Expectation ID"] = expectation_code
    normalized["Связанный LPR ID"] = linked_lpr or None
    normalized["Тип ожидания"] = _map_field(
        result, row, "Тип ожидания", map_expectation_type, required=True
    )
    normalized["Явное или неявное"] = _map_field(
        result, row, "Явное или неявное", map_explicitness, default="unknown"
    )
    normalized["Критичность"] = _map_field(
        result, row, "Критичность", map_criticality, required=True
    )
    _append_if_valid(result, row, normalized, errors_before)


def _validate_kpi_row(result: ValidationResult, row: ExcelRow) -> None:
    errors_before = result.errors_count
    normalized = dict(row.values)
    normalized["KPI ID"] = _required(result, row, "KPI ID")
    _required(result, row, "Название KPI / критерия успеха")
    normalized["Критичность для клиента"] = _map_field(
        result, row, "Критичность для клиента", map_criticality, default="unknown"
    )
    _append_if_valid(result, row, normalized, errors_before)


def _validate_communication_row(result: ValidationResult, row: ExcelRow) -> None:
    errors_before = result.errors_count
    normalized = dict(row.values)
    normalized["Communication ID"] = _required(result, row, "Communication ID")
    _required(result, row, "Тема взаимодействия")
    normalized["Канал"] = _map_field(
        result, row, "Канал", map_communication_channel, default="unknown"
    )
    normalized["Частота"] = _map_field(
        result, row, "Частота", map_communication_frequency, default="unknown"
    )
    normalized["Критичность"] = _map_field(
        result, row, "Критичность", map_criticality, default="unknown"
    )
    _append_if_valid(result, row, normalized, errors_before)


def _validate_plan_row(result: ValidationResult, row: ExcelRow, mode: Mode) -> None:
    errors_before = result.errors_count
    normalized = dict(row.values)
    normalized["Plan ID"] = _required(result, row, "Plan ID")
    barrier_code = _text(row.values.get("Связанный Barrier ID"))
    if not barrier_code:
        result.add_issue(
            "warning" if mode == "dry-run" else "error",
            row.sheet_name,
            row.row_number,
            "План устранения должен ссылаться на Barrier ID для commit-загрузки.",
            "Связанный Barrier ID",
            row.values.get("Связанный Barrier ID"),
        )
    normalized["Связанный Barrier ID"] = barrier_code or None
    normalized["Тип действия"] = _map_field(
        result, row, "Тип действия", map_action_type, required=True
    )
    normalized["Статус"] = _map_field(
        result, row, "Статус", map_action_status, default="unknown"
    )
    normalized["Статус подтверждения"] = _map_field(
        result,
        row,
        "Статус подтверждения",
        map_plan_confirmation_status,
        required=True,
    )
    if normalized["Статус подтверждения"] == "ai_hypothesis":
        result.add_issue(
            "warning",
            row.sheet_name,
            row.row_number,
            "AI-гипотеза останется в отчете и будет пропущена commit-импортом планов.",
            "Статус подтверждения",
            row.values.get("Статус подтверждения"),
        )
    _required(result, row, "Описание действия")
    _required(result, row, "Ответственная роль")
    _append_if_valid(result, row, normalized, errors_before)


def _validate_follow_up_row(result: ValidationResult, row: ExcelRow) -> None:
    errors_before = result.errors_count
    normalized = dict(row.values)
    _required(result, row, "Раздел CJM")
    _required(result, row, "Что нужно узнать")
    target_sheet_name = "09_Что нужно дозапросить" if row.sheet_name == "08_Что нужно дозапросить" else None
    _append_if_valid(result, row, normalized, errors_before, target_sheet_name=target_sheet_name)


def _scan_pii_headers(result: ValidationResult, workbook: CJMWorkbookData) -> None:
    for sheet_name, sheet in workbook.sheets.items():
        for header in sheet.headers:
            if normalize_label(header) in FORBIDDEN_PII_COLUMNS:
                result.add_issue(
                    "error",
                    sheet_name,
                    1,
                    "Найдена запрещенная колонка с персональными или клиентскими данными.",
                    header,
                    header,
                )


def _scan_prohibited_sheets(result: ValidationResult, workbook: CJMWorkbookData) -> None:
    for sheet_name in workbook.sheets:
        if normalize_label(sheet_name) in PROHIBITED_SHEETS:
            result.add_issue(
                "error",
                sheet_name,
                None,
                "Этот лист не входит в структурированный CJM-шаблон и не импортируется.",
            )


def _sheet_name_aliases(workbook: CJMWorkbookData) -> dict[str, str]:
    aliases: dict[str, str] = {}
    if "09_Что нужно дозапросить" not in workbook.sheets and "08_Что нужно дозапросить" in workbook.sheets:
        aliases["09_Что нужно дозапросить"] = "08_Что нужно дозапросить"
    return aliases


def _initialize_result(workbook: CJMWorkbookData, mode: Mode) -> ValidationResult:
    sheet_aliases = _sheet_name_aliases(workbook)
    rows_read = {
        sheet_name: (
            len(workbook.sheets[sheet_name].rows)
            if sheet_name in workbook.sheets
            else len(workbook.sheets[sheet_aliases[sheet_name]].rows)
            if sheet_name in sheet_aliases
            else 0
        )
        for sheet_name in TEMPLATE_SHEET_COLUMNS
    }
    return ValidationResult(
        file_path=workbook.file_path,
        mode=mode,
        rows_read=rows_read,
        rows_valid={sheet_name: 0 for sheet_name in TEMPLATE_SHEET_COLUMNS},
        normalized_sheets={sheet_name: [] for sheet_name in TEMPLATE_SHEET_COLUMNS},
    )


def _validate_cross_references(result: ValidationResult) -> None:
    passport_rows = result.normalized_sheets["01_Паспорт проекта"]
    passport_ids = {_text(row.values.get("Project ID")) for row in passport_rows}
    passport_ids.discard("")

    if not passport_ids:
        result.add_issue(
            "error",
            "01_Паспорт проекта",
            None,
            "В шаблоне нужен один паспорт проекта с Project ID.",
            "Project ID",
        )
    elif len(passport_ids) > 1:
        result.add_issue(
            "error",
            "01_Паспорт проекта",
            None,
            "Один импортный файл должен содержать один Project ID в паспорте проекта.",
            "Project ID",
            sorted(passport_ids),
        )
    else:
        result.primary_project_id = next(iter(passport_ids))

    lpr_ids = {
        _text(row.values.get("LPR ID"))
        for row in result.normalized_sheets["02_ЛПР"]
        if _text(row.values.get("LPR ID"))
    }
    barrier_ids = {
        _text(row.values.get("Barrier ID"))
        for row in result.normalized_sheets["04_Барьеры"]
        if _text(row.values.get("Barrier ID"))
    }
    expectation_ids = {
        _text(row.values.get("Expectation ID"))
        for row in result.normalized_sheets["05_Ожидания клиента"]
        if _text(row.values.get("Expectation ID"))
    }

    result.identifiers["lpr_ids"].update(lpr_ids)
    result.identifiers["barrier_ids"].update(barrier_ids)
    result.identifiers["expectation_ids"].update(expectation_ids)
    if result.primary_project_id:
        result.identifiers["project_ids"].add(result.primary_project_id)

    for sheet_name in ("03_Важности ЛПР",):
        for row in result.normalized_sheets[sheet_name]:
            lpr_code = _text(row.values.get("LPR ID"))
            if lpr_code and lpr_code not in lpr_ids:
                result.add_issue(
                    "warning",
                    row.sheet_name,
                    row.row_number,
                    "LPR ID не найден на листе '02_ЛПР'; commit проверит существующие профили в БД.",
                    "LPR ID",
                    lpr_code,
                )

    for row in result.normalized_sheets["08_Планы действий"]:
        barrier_code = _text(row.values.get("Связанный Barrier ID"))
        if barrier_code and barrier_code not in barrier_ids:
            result.add_issue(
                "warning",
                row.sheet_name,
                row.row_number,
                "Barrier ID не найден на листе '04_Барьеры'; commit проверит БД.",
                "Связанный Barrier ID",
                barrier_code,
            )


def validate_cjm_workbook(workbook: CJMWorkbookData, mode: Mode = "dry-run") -> ValidationResult:
    result = _initialize_result(workbook, mode)
    sheet_aliases = _sheet_name_aliases(workbook)
    _scan_pii_headers(result, workbook)
    _scan_prohibited_sheets(result, workbook)

    for sheet_name, expected_columns in TEMPLATE_SHEET_COLUMNS.items():
        sheet = workbook.sheets.get(sheet_name) or workbook.sheets.get(sheet_aliases.get(sheet_name, ""))
        if sheet_name == "08_Планы действий" and sheet is None:
            continue
        if sheet is None:
            result.add_issue(
                "error",
                sheet_name,
                None,
                "В Excel отсутствует обязательный лист шаблона.",
            )
            continue

        missing_columns = [column for column in expected_columns if column not in sheet.headers]
        if missing_columns:
            result.add_issue(
                "error",
                sheet_name,
                1,
                "В листе отсутствуют обязательные колонки шаблона.",
                raw_value=missing_columns,
            )

    validators = {
        "01_Паспорт проекта": _validate_passport_row,
        "02_ЛПР": _validate_lpr_row,
        "03_Важности ЛПР": _validate_importance_row,
        "04_Барьеры": _validate_barrier_row,
        "05_Ожидания клиента": _validate_expectation_row,
        "06_KPI и критерии успеха": _validate_kpi_row,
        "07_Каналы взаимодействия": _validate_communication_row,
        "09_Что нужно дозапросить": _validate_follow_up_row,
        "08_Что нужно дозапросить": _validate_follow_up_row,
    }

    for sheet_name, sheet in workbook.sheets.items():
        if sheet_name == "08_Планы действий":
            for row in sheet.rows:
                _validate_plan_row(result, row, mode)
            continue
        validator = validators.get(sheet_name)
        if validator is None:
            continue
        for row in sheet.rows:
            validator(result, row)

    _validate_cross_references(result)
    return result
