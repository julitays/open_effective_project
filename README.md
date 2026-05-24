# OPEN Project Risk

MVP backend and read-only frontend for browsing structured CJM project data.

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

Yandex Serverless Container deployment is intentionally not covered here.
