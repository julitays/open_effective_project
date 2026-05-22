# CJM MVP import process

The manual import process is a validate-first workflow for anonymized structured
CJM Excel files. It does not accept survey-history, AI-summary, or ID-directory
sheets. Reports are written to `.\data\import_reports\` as JSON.

## 1. Create the template

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\generate_cjm_mvp_template.py
```

The generated workbook is:

```text
.\data\templates\cjm_mvp_collection_template.xlsx
```

## 2. Fill one project file

Create a working copy under the local import folder, for example:

```text
.\data\imports\cjm_project_001.xlsx
```

Fill only anonymized project and LPR codes. Do not add columns such as `ФИО`,
`Имя`, `Телефон`, `Email`, `Название клиента`, or `Название проекта`.
`External project ID` is required in the project passport; `External LPR ID` is
allowed when it is a source CSV ID rather than personal data.
If a restored CJM contains a separate `08_Цели проекта` sheet, the importer
accepts it as an optional extension and loads its valid rows into project goals.

## 3. Run validation and dry-run

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\import_cjm_mvp_excel.py --file .\data\imports\cjm_project_001.xlsx --dry-run
```

Dry-run reads the workbook, validates sheet structure, maps Russian values to
internal MVP codes, writes a report, and does not write database rows.

The report includes:

- rows read and valid rows by sheet;
- error and warning counts;
- issue details with sheet and row;
- project, LPR, barrier, and expectation identifiers planned for create/update.

## 4. Read errors and warnings

The command prints the report path. Open the JSON report under:

```text
.\data\import_reports\
```

Errors stop commit. Warnings are allowed when they describe incomplete but
non-critical context. A plan without a resolvable `Barrier ID` becomes a commit
error. Action rows marked as `AI-гипотеза` are reported and skipped by commit.

## 5. Commit the import

After dry-run has no critical errors and `DATABASE_URL` points to the target
PostgreSQL/Supabase environment:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\import_cjm_mvp_excel.py --file .\data\imports\cjm_project_001.xlsx --commit
```

Commit repeats validation before writing. It upserts the project, LPR profiles,
manual importance factors, barriers, expectations, KPIs, communication points,
and action plans that fit the current MVP schema.
