# SwipeX Integrated Workspace

This repository contains the integrated SwipeX gateway and frontend, plus the standalone intern services.

## What To Upload

Commit these source folders and files:

- `Backend_swipex/`: FastAPI gateway, authentication, jobs, companies, swipes, saved jobs, recommendations, resumes, ATS routes, Alembic migration, and seed script.
- `Swipex-Frontend/`: Vite/React frontend, API client, pages, public assets, `package.json`, and `package-lock.json`.
- `SwipeX-AIML-/`: standalone resume parsing, ATS, and recommendation service when the AIML intern work must be reviewed separately.
- `SwipeX_Job_Data_Service/`: standalone job/data intelligence service when the data intern work must be reviewed separately.
- `.env.example` files, requirements files, migration files, tests, and README files.

Do not commit `.env`, `integ/`, `node_modules/`, `dist/`, local database files, uploads, logs, or IDE folders. The root `.gitignore` excludes them.

## Integrated Architecture

```text
Swipex-Frontend :5173
        |
        | VITE_API_BASE_URL=http://localhost:8000/api/v1
        v
Backend_swipex :8000
        |
        v
PostgreSQL (Docker, localhost:5432)
```

The frontend uses `Backend_swipex` as the canonical gateway. The AIML and job/data folders are standalone intern services and can be demonstrated independently.

## Prerequisites

- Windows 10/11
- Python 3.11+
- Node.js and npm
- Docker Desktop

## Start PostgreSQL

Create the shared development database once. Docker Desktop must be running:

```cmd
docker run --name swipex-postgres -e POSTGRES_USER=swipex -e POSTGRES_PASSWORD=swipex_dev_pass -e POSTGRES_DB=swipex_gateway -p 5432:5432 -d postgres:16-alpine
```

If the container already exists:

```cmd
docker start swipex-postgres
```

## Start Integrated Backend

```cmd
cd /d "C:\path\to\Swipex Integrate\Backend_swipex"
py -3.11 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
copy .env.example .env
```

Review `.env`, then initialize the fresh database:

```cmd
python app\seed.py
python -m alembic stamp head
```

`seed.py` creates the application tables and seed data. `alembic stamp head` records the checked-in resume migration after those tables exist. Do not run `alembic upgrade head` against a database already created by `seed.py`.

Start the gateway:

```cmd
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Verify:

```text
http://127.0.0.1:8000/health
http://127.0.0.1:8000/docs
```

## Start Integrated Frontend

Open a second Command Prompt:

```cmd
cd /d "C:\path\to\Swipex Integrate\Swipex-Frontend"
npm install
set VITE_API_BASE_URL=http://localhost:8000/api/v1
npm run dev -- --host localhost --port 5173
```

Open `http://localhost:5173/register`.

## Individual Intern Services

### AIML service

Use Python 3.11+ because the project uses `datetime.UTC` and `pandas==3.0.5`:

```cmd
cd /d "C:\path\to\Swipex Integrate\SwipeX-AIML-"
py -3.11 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r backend\requirements.txt
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8002
```

Docs and health:

```text
http://127.0.0.1:8002/docs
http://127.0.0.1:8002/health
```

Tests:

```cmd
python -m pytest -q
python -m ruff check backend
```

### Job/data intelligence service

```cmd
cd /d "C:\path\to\Swipex Integrate\SwipeX_Job_Data_Service"
py -3.11 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8004
```

Docs and health:

```text
http://127.0.0.1:8004/docs
http://127.0.0.1:8004/health
```

Tests:

```cmd
python -m pytest -q
```

## Verification Checklist

- `GET /health` returns `200`.
- Registration returns `201`.
- Login returns a JWT and the frontend stores `swipex_auth_token`.
- `GET /api/v1/auth/me` returns `200`.
- Jobs, companies, recommendations, and resumes return `200`.
- Resume upload returns `201`.
- Swipe and saved-job operations return `201` or `204` as appropriate.
- Browser Network requests use `http://localhost:8000/api/v1`.
- Frontend build succeeds with `npm run build`.

## GitHub Handoff

From the workspace root:

```cmd
git init
git add .
git status
git commit -m "Prepare SwipeX integrated workspace"
git branch -M main
git remote add origin https://github.com/<org>/<repo>.git
git push -u origin main
```

Before pushing, confirm that `git status` does not list `.env`, `integ`, `node_modules`, `dist`, database files, or uploaded files.
