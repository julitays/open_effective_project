from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook


INSTRUCTION_SHEET_NAME = "00_Инструкция"
TEMPLATE_SHEET_COLUMNS: dict[str, tuple[str, ...]] = {
    "01_Паспорт проекта": (
        "Project ID",
        "External project ID",
        "Рабочий код проекта",
        "Направление проекта",
        "Масштаб проекта",
        "Известные регионы",
        "Основная операционная модель",
        "Дополнительные операционные контуры",
        "Этап жизненного цикла",
        "Статус проекта",
        "Дата старта",
        "Краткое описание проекта",
    ),
    "02_ЛПР": (
        "LPR ID",
        "External LPR ID",
        "Роль / зона влияния",
        "Уровень влияния",
        "Статус активности",
        "Предполагаемое отношение к OPEN/услуге",
        "Основание вывода",
        "Комментарий для ручного уточнения",
    ),
    "03_Важности ЛПР": (
        "LPR ID",
        "External LPR ID",
        "Важность",
        "Критичность",
        "Источник вывода",
        "Доказательство / короткая цитата",
        "Период / источник",
        "Уверенность вывода",
    ),
    "04_Барьеры": (
        "Barrier ID",
        "Название барьера",
        "Тип барьера",
        "Временной статус",
        "Описание барьера",
        "Критичность",
        "Связанный LPR ID",
        "External LPR ID",
        "Связанная важность ЛПР",
        "Связанный KPI",
        "Источник",
        "Доказательство / короткая цитата",
        "Период первого появления",
        "Период последнего появления",
        "Статус барьера",
        "Статус актуальности",
        "Уверенность вывода",
    ),
    "05_Ожидания клиента": (
        "Expectation ID",
        "Ожидание клиента",
        "Тип ожидания",
        "Явное или неявное",
        "Критичность",
        "Связанный LPR ID",
        "External LPR ID",
        "Связанная важность ЛПР",
        "Связанный KPI",
        "Источник",
        "Доказательство / короткая цитата",
        "Статус актуальности",
        "Уверенность вывода",
    ),
    "06_KPI и критерии успеха": (
        "KPI ID",
        "Название KPI / критерия успеха",
        "Тип KPI",
        "Источник",
        "Статус актуальности",
        "Связанное ожидание клиента",
        "Связанный барьер",
        "Критичность для клиента",
        "Комментарий",
        "Требует подтверждения",
    ),
    "07_Каналы взаимодействия": (
        "Communication ID",
        "Сторона клиента: LPR ID или роль",
        "External LPR ID",
        "Сторона OPEN: роль",
        "Тема взаимодействия",
        "Канал",
        "Частота",
        "Критичность",
        "Источник",
        "Статус актуальности",
        "Комментарий",
    ),
    "08_Планы действий": (
        "Plan ID",
        "Связанный Barrier ID",
        "Связанное Expectation ID",
        "Тип действия",
        "Описание действия",
        "Ответственная роль",
        "Срок / период",
        "Статус",
        "Источник",
        "Статус подтверждения",
        "Ожидаемый эффект",
    ),
    "09_Что нужно дозапросить": (
        "Раздел CJM",
        "Что нужно узнать",
        "У кого запросить",
        "Зачем это нужно",
        "Приоритет",
        "Без этого можно продолжать MVP",
    ),
}

OPTIONAL_SHEET_COLUMNS: dict[str, tuple[str, ...]] = {
    "08_Цели проекта": (
        "Goal ID",
        "Project ID",
        "Тип цели",
        "Цель проекта",
        "Источник",
        "Связанный KPI / критерий",
        "Статус актуальности",
        "Уверенность вывода",
        "Комментарий",
    ),
}


@dataclass(slots=True)
class ExcelRow:
    sheet_name: str
    row_number: int
    values: dict[str, object]


@dataclass(slots=True)
class ExcelSheet:
    name: str
    headers: tuple[str, ...]
    rows: list[ExcelRow]


@dataclass(slots=True)
class CJMWorkbookData:
    file_path: Path
    sheets: dict[str, ExcelSheet]


def _clean_cell(value: object) -> object:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _headers_from_row(values: tuple[object, ...]) -> tuple[str, ...]:
    headers = [str(value).strip() if value is not None else "" for value in values]
    while headers and not headers[-1]:
        headers.pop()
    return tuple(headers)


def read_cjm_workbook(file_path: str | Path) -> CJMWorkbookData:
    path = Path(file_path)
    workbook = load_workbook(path, read_only=True, data_only=True)
    sheets: dict[str, ExcelSheet] = {}

    for worksheet in workbook.worksheets:
        row_iter = worksheet.iter_rows(values_only=True)
        first_row = next(row_iter, ())
        headers = _headers_from_row(first_row)
        rows: list[ExcelRow] = []

        for row_number, values in enumerate(row_iter, start=2):
            cells = tuple(_clean_cell(value) for value in values[: len(headers)])
            if not any(value not in (None, "") for value in cells):
                continue
            row_values = {header: cells[index] for index, header in enumerate(headers) if header}
            rows.append(ExcelRow(worksheet.title, row_number, row_values))

        sheets[worksheet.title] = ExcelSheet(worksheet.title, headers, rows)

    workbook.close()
    return CJMWorkbookData(file_path=path, sheets=sheets)
