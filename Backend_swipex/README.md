# Job Swipe Backend — Gateway API (Milestone 1 + Milestone 2)

A single, cohesive FastAPI backend combining:

- **Milestone 1**: Auth, JWT, RBAC, Gateway Core
- **Milestone 2**: Job Listings, Advanced Search, Swipes Engine, Dynamic Metrics, Recommendation Gateway
- **Gateway stubs**: Resume and ATS routes are registered for future implementation

## Tech Stack

- Python 3.11+, FastAPI
- PostgreSQL + SQLAlchemy ORM
- PyJWT + passlib[bcrypt] for auth
- Swagger UI / OpenAPI (auto-generated at `/docs`)

## Project Structure

```
job-swipe-backend/
├── requirements.txt
├── .env.example
├── README.md
└── app/
    ├── main.py                 # FastAPI app entry point
    ├── routes.py                # Central API gateway (mounts all sub-routers)
    ├── database.py               # Engine / session / Base / get_db
    ├── models.py                 # SQLAlchemy models: User, Company, Job, Swipe
    ├── schemas.py                 # Pydantic request/response schemas
    ├── auth.py                     # JWT + password hashing + RBAC dependencies
    ├── utils.py                     # posted_time / competition_level helpers
    ├── seed.py                       # Seed script (dummy users/companies/jobs)
    └── controllers/
        ├── auth_controller.py         # /api/v1/auth
        ├── job_controller.py           # /api/v1/jobs
        ├── company_controller.py        # /api/v1/companies
        ├── swipe_controller.py           # /api/v1/swipes
        ├── recommendation_controller.py   # /api/v1/recommendations
        ├── resume_controller.py          # /api/v1/resumes (stub)
        └── ats_controller.py             # /api/v1/ats (stub)
```

## Setup

### 1. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set `DATABASE_URL` to point at a running PostgreSQL instance, e.g.:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/job_swipe_db
```

Make sure the target database exists first:

```bash
createdb job_swipe_db
```

Also set strong, random values for `JWT_SECRET_KEY` and `JWT_REFRESH_SECRET_KEY` in production.

The recommendation gateway can optionally call an external matching service. If needed, add these variables to `.env`:

```
MATCHING_ENGINE_URL=http://localhost:9000/recommend
MATCHING_ENGINE_TIMEOUT_SECONDS=2.0
```

If `MATCHING_ENGINE_URL` is omitted or unavailable, the backend uses its local heuristic fallback.

### 4. Seed the database

This creates all tables (if they don't exist) and inserts dummy companies, jobs, and test user accounts:

```bash
python app/seed.py
```

Seeded test accounts (all use password `Password123`):

| Email                        | Role        |
|------------------------------|-------------|
| admin@jobswipe.dev            | admin       |
| recruiter@jobswipe.dev        | recruiter   |
| recruiter2@jobswipe.dev       | recruiter   |
| jobseeker@jobswipe.dev        | job_seeker  |
| jobseeker2@jobswipe.dev       | job_seeker  |
| jobseeker3@jobswipe.dev       | job_seeker  |

### 5. Run the server

```bash
uvicorn app.main:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

## API Overview

All routes are mounted under the `/api/v1` gateway prefix.

### Auth (`/api/v1/auth`)
- `POST /register` — create a new account (job_seeker / recruiter / admin)
- `POST /login` — get access + refresh JWT tokens
- `POST /refresh` — exchange a refresh token for a new access token
- `GET /me` — get the current authenticated user's profile

### Jobs (`/api/v1/jobs`)
- `GET /` — paginated, multi-parameter search (keyword, location, job_type, company_id, skill, salary_min/max, sorting)
- `GET /{job_id}` — job detail, including dynamic `posted_time` and `competition_level`
- `POST /` — create a job (Recruiter / Admin only)
- `PATCH /{job_id}` — update a job (Recruiter / Admin only, ownership enforced)
- `DELETE /{job_id}` — delete a job (Recruiter / Admin only, ownership enforced)

### Companies (`/api/v1/companies`)
- `GET /` — list companies (filter by industry / location / keyword)
- `GET /{company_id}` — company profile + its active job listings
- `POST /` — create a company (Recruiter / Admin only)
- `PATCH /{company_id}` — update a company (Recruiter / Admin only, ownership enforced)
- `DELETE /{company_id}` — delete a company (Admin only)

### Swipes (`/api/v1/swipes`)
- `POST /` — record `apply` / `save` / `skip` on a job (**Job Seeker only**); re-swiping the same job updates the existing record and reconciles `applicant_count`
- `GET /` — list current user's swipe history (optionally filtered by action)
- `GET /{swipe_id}` — get a single swipe
- `DELETE /{job_id}` — undo the current user's swipe for a job

### Recommendations (`/api/v1/recommendations`)
- `GET /?limit=10` — personalized job recommendations for the current user, generated by the decoupled `MatchingEngineService` (see below)

### Resumes (`/api/v1/resumes`)
- `GET /` — temporary routing stub; returns a confirmation message

### ATS Scoring (`/api/v1/ats`)
- `POST /score` — temporary routing stub; returns a confirmation message

## Architecture Notes

### RBAC

Every protected route uses a FastAPI dependency (`get_current_user`, or `require_roles(...)` / the pre-built `require_job_seeker`, `require_recruiter_or_admin`, `require_admin`) that validates the JWT bearer token and checks the user's role. `GET` endpoints on jobs and companies simply require authentication (any role); mutation endpoints enforce the specific role restrictions described in the milestone spec.

### Dynamic Job Intelligence Metrics

`app/utils.py` computes two fields on every job response, on the fly (never stored in the DB):

- `posted_time`: a relative, human-readable string derived from `posted_at` (e.g. "2 days ago").
- `competition_level`: `"Low"` (`applicant_count < 10`), `"Medium"` (`10–50`), `"High"` (`> 50`).

### Decoupled Matching Engine (Recommendation Gateway)

`app/controllers/recommendation_controller.py` defines `MatchingEngineService`, a modular wrapper with **zero hard dependency** on an external Data Science service:

1. If `MATCHING_ENGINE_URL` is configured in the environment, it first attempts an HTTP call to the external ML engine.
2. If that URL is unset, unreachable, times out, or returns malformed data, it **transparently falls back** to a local heuristic scorer (plain Python — skill-overlap ratio, recency boost, low-competition boost) that always returns a valid, explainable response.

This guarantees `/api/v1/recommendations` never breaks the frontend, whether or not the ML team's service exists yet in a given environment.

### Swipe Engine & Applicant Count

The `Swipe` model has a `UniqueConstraint` on `(user_id, job_id)`. Swiping the same job twice **updates** the existing swipe's action rather than creating a duplicate row, and `Job.applicant_count` is incremented/decremented so it always reflects the number of users whose current swipe action is `apply`.

## Running Tests / Interactive Exploration

The fastest way to explore every endpoint is via the interactive Swagger UI at `/docs` — click **Authorize**, paste in an access token obtained from `/api/v1/auth/login`, and try any endpoint directly in the browser.
