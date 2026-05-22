# CJM MVP Excel template specification

The CJM MVP workbook is a structured project CJM file. It is not a survey
history transport. Historical surveys and an older CJM can be used by a human to
restore the structured CJM, but survey response history is not collected in this
workbook.

Generate the template:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\generate_cjm_mvp_template.py
```

Generated path:

```text
.\data\templates\cjm_mvp_collection_template.xlsx
```

## Workbook rules

- First sheet: `00_Инструкция`.
- Data sheets use Russian names and headers.
- The first row is frozen, filters are enabled, and columns are widened for
  manual work.
- Supported dictionary columns have Excel list validation where practical.
- `External project ID` is required in the project passport.
- `External LPR ID` is allowed only as an external source ID, not as a name.
- There are no survey-history, AI-summary, ID-directory, Insights, or strategic
  significance sheets.
- Do not add `ФИО`, `Имя`, `Телефон`, `Email`, `Название клиента`, or
  `Название проекта` columns.

## Sheets

### `01_Паспорт проекта`

Columns: `Project ID`, `External project ID`, `Рабочий код проекта`,
`Направление проекта`, `Масштаб проекта`, `Известные регионы`,
`Основная операционная модель`, `Дополнительные операционные контуры`,
`Этап жизненного цикла`, `Статус проекта`, `Дата старта`,
`Краткое описание проекта`.

### `02_ЛПР`

Columns: `LPR ID`, `External LPR ID`, `Роль / зона влияния`,
`Уровень влияния`, `Статус активности`,
`Предполагаемое отношение к OPEN/услуге`, `Основание вывода`,
`Комментарий для ручного уточнения`.

### `03_Важности ЛПР`

Columns: `LPR ID`, `External LPR ID`, `Важность`, `Критичность`,
`Источник вывода`, `Доказательство / короткая цитата`,
`Период / источник`, `Уверенность вывода`.

### `04_Барьеры`

Columns: `Barrier ID`, `Название барьера`, `Тип барьера`,
`Временной статус`, `Описание барьера`, `Критичность`,
`Связанный LPR ID`, `External LPR ID`, `Связанная важность ЛПР`,
`Связанный KPI`, `Источник`, `Доказательство / короткая цитата`,
`Период первого появления`, `Период последнего появления`,
`Статус барьера`, `Статус актуальности`, `Уверенность вывода`.

### `05_Ожидания клиента`

Columns: `Expectation ID`, `Ожидание клиента`, `Тип ожидания`,
`Явное или неявное`, `Критичность`, `Связанный LPR ID`, `External LPR ID`,
`Связанная важность ЛПР`, `Связанный KPI`, `Источник`,
`Доказательство / короткая цитата`, `Статус актуальности`,
`Уверенность вывода`.

### `06_KPI и критерии успеха`

Columns: `KPI ID`, `Название KPI / критерия успеха`, `Тип KPI`, `Источник`,
`Статус актуальности`, `Связанное ожидание клиента`, `Связанный барьер`,
`Критичность для клиента`, `Комментарий`, `Требует подтверждения`.

### `07_Каналы взаимодействия`

Columns: `Communication ID`, `Сторона клиента: LPR ID или роль`,
`External LPR ID`, `Сторона OPEN: роль`, `Тема взаимодействия`, `Канал`,
`Частота`, `Критичность`, `Источник`, `Статус актуальности`, `Комментарий`.

### `08_Планы действий`

Columns: `Plan ID`, `Связанный Barrier ID`, `Связанное Expectation ID`,
`Тип действия`, `Описание действия`, `Ответственная роль`, `Срок / период`,
`Статус`, `Источник`, `Статус подтверждения`, `Ожидаемый эффект`.

Allowed manual values for `Статус подтверждения` are:

- `Подтвержденный план`;
- `Черновик`;
- `AI-гипотеза`;
- `Требует согласования`.

`AI-гипотеза` stays in the workbook and report and is skipped by commit import
instead of becoming an approved plan row.

### `09_Что нужно дозапросить`

Columns: `Раздел CJM`, `Что нужно узнать`, `У кого запросить`,
`Зачем это нужно`, `Приоритет`, `Без этого можно продолжать MVP`.

## Current persistence boundary

The importer writes structured project, LPR, importance, barrier, expectation,
KPI, communication, and action-plan fields that fit the current MVP schema.
Manual context fields such as known regions, evidence snippets, actuality
statuses, confidence notes, and confirmation comments remain in the filled
workbook and JSON report when there is no dedicated database field yet.
