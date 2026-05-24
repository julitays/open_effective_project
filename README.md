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

Yandex Serverless Container deployment is intentionally not covered here.
