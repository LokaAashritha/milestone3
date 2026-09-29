# SwipeX Milestone 2 API Contracts

Base URL: `/api/v1`

Protected endpoints require `Authorization: Bearer <access_token>`.
The generated OpenAPI document is available at `/openapi.json` and Swagger UI at `/docs`.

## Shared Schemas

### JobCard

```json
{
  "id": "8f6c2e9d-5c45-4a9d-9df3-6f8fcb8ab123",
  "company_id": "7a8a1b2c-3d4e-4f5a-8b9c-0d1e2f3a4b56",
  "company_name": "Acme Labs",
  "title": "Backend Engineer Intern",
  "description": "Build APIs with Python and PostgreSQL.",
  "location": "Bengaluru",
  "job_type": "internship",
  "experience_level": "entry",
  "salary_min": "15000.00",
  "salary_max": "25000.00",
  "skills_required": ["Python", "FastAPI", "PostgreSQL"],
  "fresher_friendly": true,
  "low_competition": true,
  "applicant_count": 6,
  "is_active": true,
  "posted_at": "2026-09-18T10:30:00Z",
  "created_at": "2026-09-18T10:30:00Z",
  "posted_time": "2 days ago",
  "competition_level": "Low"
}
```

`job_type` is one of `full_time`, `part_time`, `contract`, `internship`, or `remote`.
`competition_level` is computed from `applicant_count`: `Low` (<10), `Medium` (10-50), or `High` (>50).

### PaginatedJobsResponse

```json
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "results": [/* JobCard */]
}
```

### ErrorResponse

```json
{ "detail": "Human-readable error message" }
```

## 1. Swipe Deck Feed

### `GET /api/v1/jobs`

Returns active jobs for the swipe deck. Query parameters:

| Parameter | Type | Default | Notes |
|---|---|---:|---|
| `page` | integer | `1` | Minimum `1` |
| `page_size` | integer | `20` | `1` to `100` |
| `keyword` | string | omitted | Title or description |
| `location` | string | omitted | Partial match |
| `job_type` | enum | omitted | See `JobCard` |
| `company_id` | UUID | omitted | Company filter |
| `skill` | string[] | omitted | Repeat query parameter |
| `salary_min` / `salary_max` | number | omitted | Salary overlap |
| `sort_by` | enum | `posted_at` | `posted_at`, `salary_min`, `salary_max`, `applicant_count` |
| `sort_order` | enum | `desc` | `asc` or `desc` |

Responses: `200` `PaginatedJobsResponse`; `400` invalid query; `401` missing or invalid token.

## 2. Advanced Job Search

### `GET /api/v1/jobs/search`

Returns active jobs ordered by `created_at` descending. Supported filter query parameters:

`page`, `page_size`, `keyword`, `salary_min`, `salary_max`, `job_type`, `experience_level`, `fresher_friendly`, `low_competition`, `recently_posted`.

`recently_posted=true` means `created_at` is within the last 30 days. The three filter-chip fields are explicitly returned on every `JobCard`: `fresher_friendly`, `low_competition`, and `created_at`.

Responses: `200` `PaginatedJobsResponse`; `400` when `salary_min > salary_max`; `401` unauthenticated.

Example:

```http
GET /api/v1/jobs/search?keyword=python&job_type=internship&fresher_friendly=true&low_competition=true&recently_posted=true&page=1&page_size=10
```

## 3. Swipe Actions and Undo

### `POST /api/v1/swipes`

Job Seeker role only. Request body:

```json
{
  "job_id": "8f6c2e9d-5c45-4a9d-9df3-6f8fcb8ab123",
  "action": "apply"
}
```

`action` is one of `apply`, `save`, or `skip`. Repeating a swipe updates the existing `(user_id, job_id)` row. The implementation locks the job and existing swipe with `.with_for_update()` so `applicant_count` remains consistent.

Response `201`:

```json
{
  "id": "c0a8012e-7f8b-4a8c-9e4f-4d7c1c2a1111",
  "user_id": "4f9c2e3d-1111-4444-8888-123456789abc",
  "job_id": "8f6c2e9d-5c45-4a9d-9df3-6f8fcb8ab123",
  "action": "apply",
  "created_at": "2026-09-20T09:00:00Z",
  "updated_at": "2026-09-20T09:00:00Z"
}
```

Responses: `201` created/updated; `400` inactive job; `401` unauthenticated; `404` job not found; `409` duplicate insert race; `403` authenticated non-job-seeker.

### `DELETE /api/v1/swipes/{job_id}`

Deletes the current user's swipe for the given job and reverses `applicant_count` when the action was `apply`. The job row and swipe row are locked during the transaction.

Responses: `204` success; `401` unauthenticated; `404` swipe not found; `403` authenticated non-job-seeker.

## 4. Company Listings

### `GET /api/v1/companies`

Returns company summaries with active/all job count. Optional query parameters: `industry`, `location`, `keyword`.

Response `200`:

```json
[
  {
    "id": "7a8a1b2c-3d4e-4f5a-8b9c-0d1e2f3a4b56",
    "name": "Acme Labs",
    "about": "Developer tools startup",
    "industry": "Software",
    "location": "Bengaluru",
    "website": "https://acme.example",
    "logo_url": "https://acme.example/logo.png",
    "created_at": "2026-01-10T08:00:00Z",
    "job_count": 4
  }
]
```

Responses: `200` list; `401` unauthenticated.

### `GET /api/v1/companies/{id}`

Returns the company profile and nested active `jobs`, each serialized as a `JobCard`.

Responses: `200` company detail; `401` unauthenticated; `404` company not found.

## 5. Auth Claims and Current User

Access JWTs issued by register, login, and refresh contain these application claims in addition to standard `sub`, `iat`, `exp`, `jti`, and `type` claims:

```json
{
  "id": "4f9c2e3d-1111-4444-8888-123456789abc",
  "email": "candidate@example.com",
  "role": "job_seeker",
  "skills": ["Python", "FastAPI", "SQL"]
}
```

`role` is one of `job_seeker`, `recruiter`, or `admin`. The access token is returned as `access_token`; clients should treat the token as opaque and use `/auth/me` as the authoritative profile endpoint.

### `GET /api/v1/auth/me`

Response `200`:

```json
{
  "id": "4f9c2e3d-1111-4444-8888-123456789abc",
  "email": "candidate@example.com",
  "full_name": "Asha Candidate",
  "role": "job_seeker",
  "skills": ["Python", "FastAPI", "SQL"],
  "company_id": null,
  "created_at": "2026-01-10T08:00:00Z"
}
```

Responses: `200` current user; `401` missing, expired, or invalid token.

## Database Migration Note

`fresher_friendly`, `low_competition`, `experience_level`, and `created_at` are now model fields. Fresh databases receive them through `create_all`; existing databases require a migration before deploying the new controllers, for example:

```sql
ALTER TABLE jobs ADD COLUMN experience_level VARCHAR(100);
ALTER TABLE jobs ADD COLUMN fresher_friendly BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE jobs ADD COLUMN low_competition BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE jobs ADD COLUMN created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP;
```
