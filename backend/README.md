# OPEN Project Risk backend

This directory contains the backend scaffold for the MVP of **OPEN Project Risk**,
an internal workflow for early project-risk detection from anonymized CJM data,
decision-maker context, barriers, expectations, KPI tracking, communications,
and project effectiveness context.

The first step is intentionally narrow: FastAPI, PostgreSQL-ready SQLAlchemy
models, Alembic migrations, Pydantic schemas, and a health endpoint. The MVP
scaffold does not include a frontend, bot, authorization, Airflow, OpenAI
integration, the "Insights" block, or a strategic project significance field.

## Data safety

Only anonymized data belongs in this codebase, examples, fixtures, migration
history, and data sent to external services. Use `project_code` values such as
`project_001` and `lpr_code` values such as `lpr_001`; do not place real project
names, client names, decision-maker names, or personal data in source files.

Supabase is the source of truth for MVP project data. New project records should
be created through the web/API flow, not through workbook imports.

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

## CJM web-first API

The MVP no longer uses Excel as an intake path. Supabase is the source of truth:
the web/API layer creates, edits, and archives CJM records.

Read back a CJM project:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\check_cjm_project.py --project project_001
```

## CJM read/write API

Start the backend:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Check health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
```

Check project list:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/projects
```

Check the full CJM object:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/projects/project_001/cjm
```

Check the extended project-effectiveness context:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/projects/project_001/effectiveness
```

Create a goal:

```powershell
Invoke-RestMethod `
  -Method Post `
  -ContentType "application/json" `
  -Uri "http://127.0.0.1:8000/api/v1/projects/project_001/goals" `
  -Body '{"goal_text":"Новая цель проекта","goal_type":"service","priority":"high"}'
```

Archive a goal:

```powershell
Invoke-RestMethod `
  -Method Post `
  -ContentType "application/json" `
  -Uri "http://127.0.0.1:8000/api/v1/projects/project_001/goals/goal_001/archive" `
  -Body '{"archive_reason":"Больше не актуально"}'
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Reference docs:

- `docs/cjm_mvp_data_dictionary.md`
