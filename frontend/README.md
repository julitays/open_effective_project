# OPEN Project Risk frontend

Minimal read-only React UI for browsing anonymized CJM projects from the backend
API.

## Setup in Windows PowerShell

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\frontend"
Copy-Item .env.example .env
npm install
```

`.env.example` points to the local FastAPI read-only API:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000/api/v1
```

## Run

Start the backend in a separate PowerShell terminal:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\backend"
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

Start the frontend:

```powershell
Set-Location "d:\OPEN Project Risk\open-project-risk\frontend"
npm run dev
```

Open:

```text
http://127.0.0.1:5173/projects
```

Check:

- `project_001` and `project_002` appear on the project list;
- `/projects/project_001` opens CJM tabs;
- `/projects/project_002` opens CJM tabs.
