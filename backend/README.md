# OPEN Project Risk backend

This directory contains the backend scaffold for the MVP of **OPEN Project Risk**,
an internal AI-analyst workflow for early project-risk detection from anonymized
CJM data, client surveys, decision-maker comments, barriers, expectations, KPI
tracking, and action plans.

The first step is intentionally narrow: FastAPI, PostgreSQL-ready SQLAlchemy
models, Alembic migrations, Pydantic schemas, and a health endpoint. The MVP
scaffold does not include a frontend, bot, authorization, Airflow, OpenAI
integration, the "Insights" block, or a strategic project significance field.

## Data safety

Only anonymized data belongs in this codebase, examples, fixtures, migration
history, and data sent to external services. Use `project_code` values such as
`project_001` and `lpr_code` values such as `lpr_001`; do not place real project
names, client names, decision-maker names, or personal data in source files.

`survey_answers.original_comment_text` stores the original comment available to
the MVP storage boundary. That comment is expected to be anonymized before it is
loaded.

## Local setup in Windows PowerShell

From the repository workspace:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Update `DATABASE_URL` in `.env` for the PostgreSQL database used for local
development. `.env.example` contains placeholders only. The local `.venv`
directory and `.env` file are intentionally excluded from Git.

## Run the backend

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

The versioned API prefix is `/api/v1`.

## Alembic migrations

The scaffold already includes the `initial_mvp_schema` migration. Apply it after
`DATABASE_URL` points to the target PostgreSQL database:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python -m alembic upgrade head
```

For later model changes, create a migration with:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python -m alembic revision --autogenerate -m "describe_change"
```

Review generated migration files before applying them.

## Health check

With the backend running:

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/health" -Method Get
```

Expected response:

```text
status service
------ -------
ok     open-project-risk-api
```

## CJM MVP manual import

The manual intake layer generates a Russian structured CJM workbook, validates a
filled copy, writes JSON reports, and loads valid CJM MVP data only when commit
mode is requested. It does not import survey-history, AI-summary, or ID-directory
sheets from the CJM file. Filled import files and reports stay local under
`data`.

Create the template:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\generate_cjm_mvp_template.py
```

Put a filled anonymized file here:

```text
.\data\imports\cjm_project_001.xlsx
```

Validate and inspect the dry-run report:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\import_cjm_mvp_excel.py --file .\data\imports\cjm_project_001.xlsx --dry-run
```

Commit the same file after dry-run has no critical errors:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\import_cjm_mvp_excel.py --file .\data\imports\cjm_project_001.xlsx --commit
```

Read back the imported CJM project:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\check_cjm_project.py --project project_001
```

Reference docs:

- `docs/cjm_mvp_data_dictionary.md`
- `docs/cjm_excel_template_spec.md`
- `docs/cjm_import_process.md`
