# OPEN Project Risk

MVP backend and frontend for browsing and lightly editing existing structured
CJM project data.

## Docker local run

The Docker image builds the React frontend with a relative API URL
(`/api/v1`) and serves the production frontend through FastAPI.

Required environment variables:

- `PORT` - container HTTP port, `8000` locally.
- `ENV` - runtime environment name, for local checks use `local`.
- `DEBUG` - use `false` for container checks.
- `DATABASE_URL` - PostgreSQL/Supabase connection string.
- `DEMO_AUTH_ENABLED` - `true` to protect the demo with login and session cookie.
- `DEMO_AUTH_USERNAME` - demo username when auth is enabled.
- `DEMO_AUTH_PASSWORD` - demo password when auth is enabled.
- `SECRET_KEY` - secret value used to sign the demo session cookie.

Build the image:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk"
docker build -t open-project-risk:local .
```

Run the container on port `8000`:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk"
$env:DATABASE_URL = "<DATABASE_URL>"
docker run --rm -p 8000:8000 `
  -e PORT=8000 `
  -e ENV=local `
  -e DEBUG=false `
  -e DATABASE_URL="$env:DATABASE_URL" `
  open-project-risk:local
```

Run the container with demo-auth enabled:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk"
$env:DATABASE_URL = "<DATABASE_URL>"
docker run --rm -p 8000:8000 `
  -e PORT=8000 `
  -e ENV=local `
  -e DEBUG=false `
  -e DATABASE_URL="$env:DATABASE_URL" `
  -e DEMO_AUTH_ENABLED=true `
  -e DEMO_AUTH_USERNAME="demo" `
  -e DEMO_AUTH_PASSWORD="change-me" `
  -e SECRET_KEY="change-this-secret" `
  open-project-risk:local
```

If port `8000` is already occupied locally, keep the container port as `8000`
and change only the host port:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk"
$env:DATABASE_URL = "<DATABASE_URL>"
docker run --rm -p 8010:8000 `
  -e PORT=8000 `
  -e ENV=local `
  -e DEBUG=false `
  -e DATABASE_URL="$env:DATABASE_URL" `
  open-project-risk:local
```

Check the application:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/projects
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/projects
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/projects/project_001
```

When using the alternate host port from the example above, replace `8000` with
`8010` in the check URLs.

## Demo auth

Demo auth is a minimal MVP protection layer for showing the project by link. It
is not a full corporate authorization system.

When `DEMO_AUTH_ENABLED=false`, local development works without login.

When `DEMO_AUTH_ENABLED=true`:

- `/login`, `/logout`, `/api/v1/health`, `/assets/*`, and `/favicon.ico` stay open;
- frontend routes such as `/`, `/projects`, and `/projects/project_001` require a session;
- API routes such as `/api/v1/projects` and `/api/v1/projects/project_001/cjm` require a session;
- `/docs` and `/openapi.json` are protected;
- the session is stored in a signed `HttpOnly` cookie;
- the password is read only from environment variables and is not stored in the cookie.

Environment variables:

```powershell
$env:DEMO_AUTH_ENABLED = "true"
$env:DEMO_AUTH_USERNAME = "demo"
$env:DEMO_AUTH_PASSWORD = "change-me"
$env:SECRET_KEY = "change-this-secret"
$env:SESSION_COOKIE_NAME = "open_project_risk_session"
$env:SESSION_TTL_SECONDS = "86400"
```

Log out:

```powershell
Invoke-WebRequest -UseBasicParsing -Method Post http://127.0.0.1:8000/logout
```

## CJM web-first workspace

The demo MVP now treats Supabase as the source of truth. CJM records are created,
edited, and archived through the web/API flow; Excel import is no longer part of
the product workflow.

Supported sections:

- project passport;
- goals;
- LPR profiles;
- barriers;
- client expectations;
- KPI and success criteria;
- communication points.

Supported API actions:

- `POST` creates new project/CJM records;
- `PATCH` updates only passed fields;
- `POST .../archive` hides a record from the workspace without deleting audit
  history.

Bulk editing, Excel import, action plans, survey-history ingestion, insights,
and AI workflows are not active in the MVP workspace.

Run locally and open a project:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\frontend"
npm run dev
```

Then open:

```text
http://127.0.0.1:5173/projects/project_001
```

With demo-auth enabled, PATCH endpoints require a valid session cookie. Without
a session, protected API updates return `401`.

The extended context screen is available at:

```text
http://127.0.0.1:5173/projects/project_001/context-mockup
```

## Yandex Serverless deploy

The deploy script creates and updates a separate Yandex Serverless Container for
OPEN Project Risk:

- container name: `open-project-risk-web`;
- image repository: `open-project-risk-web`;
- API prefix: `/api/v1`.

It does not use or update the Bot360 container or Bot360 image repository.

Prepare local deploy settings:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk"
Copy-Item .\deploy\deploy_open_project_risk_serverless.local.example.ps1 .\deploy\deploy_open_project_risk_serverless.local.ps1
notepad .\deploy\deploy_open_project_risk_serverless.local.ps1
```

Fill these values in the local file:

- `YC_FOLDER_ID` if it is not configured in `yc config`;
- `DATABASE_URL`;
- `DEMO_AUTH_USERNAME`;
- `DEMO_AUTH_PASSWORD`;
- `SECRET_KEY`.

The local file `deploy_open_project_risk_serverless.local.ps1` is ignored by
Git. Do not commit real secrets.

For the first demo deploy keep `MIN_INSTANCES=0`. Setting it to `1` enables
provisioned container workers and may fail if the Yandex Cloud quota
`serverless.containersWorkersProvisioned.count` is not approved.

For Yandex Serverless Container the Docker image defaults to `PORT=8080`.
Do not pass `PORT` through `yc --environment`: it is reserved by Yandex.
Local Docker runs can still override it with `-e PORT=8000` when publishing
`8000:8000`.

Run deploy:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk"
pwsh .\deploy\deploy_open_project_risk_serverless.ps1
```

The script:

- logs in to Yandex Container Registry through `yc iam create-token`;
- builds the Docker image;
- tags and pushes `cr.yandex/crpj9tkd4nn6hsiuodlm/open-project-risk-web:<buildstamp>`;
- finds or creates the `open-project-risk-web` serverless container;
- deploys a new revision with demo-auth environment variables;
- allows public invoke for the container URL;
- runs smoke checks:
  - `/api/v1/health` returns `200`;
  - `/login` returns `200`;
  - `/api/v1/projects` without session returns `401`;
  - `/projects` redirects to `/login` or shows the login page;
- removes old images from only the `open-project-risk-web` repository, keeping
  the latest 5 images.

After deploy, open:

```text
https://<CONTAINER_ID>.containers.yandexcloud.net/login
https://<CONTAINER_ID>.containers.yandexcloud.net/projects
https://<CONTAINER_ID>.containers.yandexcloud.net/api/v1/health
```

Demo-auth is enabled by setting:

```powershell
$DEMO_AUTH_ENABLED = 'true'
```
