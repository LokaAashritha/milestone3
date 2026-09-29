```markdown
# SwipeX Milestone 3 API Contracts (Draft — Day 1)

Status: **DRAFT — not yet frozen.** Freeze target: Day 2 EOD, per the Milestone 3 SRS integration checkpoints. Anyone building against this before freeze should expect small field-name changes.

Base URL: `/api/v1` (unchanged from Milestone 2)
Protected endpoints require `Authorization: Bearer <access_token>` (unchanged JWT scheme from Milestone 1/2 — see `app/auth.py`)

---

## 1. Resume Service

### `POST /api/v1/resumes/upload`

- **Auth:** Job Seeker role only (reuses the existing `require_job_seeker` dependency from `app/auth.py` — no new RBAC code needed here).
- **Request:** `multipart/form-data`
  | Field | Type | Notes |
  |---|---|---|
  | `file` | file | PDF or DOCX only. **Max size: 10MB.** Reject invalid formats with `400`, file size exceeding limit with `413`. |
- **Behavior:** creates a new resume version row owned by the current user. Does not overwrite previous versions — this is additive, matching the "multiple versions" requirement (FR-01).
- **Response `201`:**
```json
{
  "id": "b1a2c3d4-0000-4444-8888-abcdefabcdef",
  "user_id": "4f9c2e3d-1111-4444-8888-123456789abc",
  "file_name": "asha_resume_v3.pdf",
  "file_type": "pdf",
  "version_number": 3,
  "is_active_version": true,
  "parsed_status": "pending",
  "parsed_text": null,
  "extracted_skills": null,
  "uploaded_at": "2026-09-22T10:00:00Z"
}

```

* **Responses:** `201` created; `400` wrong file type; `401` unauthenticated; `403` authenticated non-job-seeker; `413` file size exceeds 10MB limit.

### `GET /api/v1/resumes`

* **Auth:** Job Seeker role only. Ownership is automatic — only the current user's own versions are ever returned (same pattern as `GET /api/v1/swipes` filtering by `user_id == current_user.id`).
* **Query params:** `active_only` (boolean, optional, default `false`)
* **Response `200`:** array of the same shape as the upload response, newest first.
* **Responses:** `200` list (possibly empty); `401` unauthenticated; `403` non-job-seeker.

### `GET /api/v1/resumes/{id}`

* **Auth:** Job Seeker role only, **and** ownership-checked — a user can only fetch their own resume, never another user's.
* **Response `200`:** same shape as above, with `parsed_text` and `extracted_skills` populated once parsing has completed (`parsed_status: "done"`).
* **Responses:** `200` found; `401` unauthenticated; `403` non-job-seeker; `404` not found **or** belongs to someone else (we return `404`, not `403`, for a resume owned by another user — same "don't reveal existence" pattern already used for swipes in Milestone 2).

---

## 2. ATS Scoring Service

### `POST /api/v1/ats/score`

* **Auth:** Job Seeker role only, ownership-checked on `resume_id`.
* **Request:**

```json
{
  "resume_id": "b1a2c3d4-0000-4444-8888-abcdefabcdef",
  "job_id": "8f6c2e9d-5c45-4a9d-9df3-6f8fcb8ab123"
}

```

* **Response `200`:**

```json
{
  "resume_id": "b1a2c3d4-0000-4444-8888-abcdefabcdef",
  "job_id": "8f6c2e9d-5c45-4a9d-9df3-6f8fcb8ab123",
  "match_score": 74.5,
  "missing_skills": ["Docker", "AWS"],
  "missing_keywords": ["containerization", "CI/CD"],
  "scored_at": "2026-09-22T10:05:00Z"
}

```

* **Business rule (FR-04):** `missing_skills` and `missing_keywords` are only populated when `match_score < 80`. At or above 80, both are returned as empty arrays — not omitted, so the frontend never has to handle a missing field.
* **Responses:** `200` scored; `400` resume not yet parsed (`parsed_status != "done"`); `401` unauthenticated; `403` non-job-seeker or resume not owned by caller (see note below — we use `404` here instead, matching the resume ownership pattern); `404` resume or job not found.

---

## 3. AI Recommendations Upgrade (existing endpoint, response extended)

### `GET /api/v1/recommendations` — **no URL change, no new router.** This is the same Milestone 2 endpoint, upgraded in place.

* **Auth:** unchanged from Milestone 2 (`get_current_user`, any authenticated role that the existing endpoint already allows).
* **New response fields**, added to each item in `recommendations[]` alongside the existing `job`, `match_score`, and `match_reasons`:

```json
{
  "job": { "...": "existing JobCard shape, unchanged" },
  "match_score": 82.0,
  "match_reasons": ["Matches 4/5 required skills: python, fastapi, sql, postgresql"],
  "semantic_match_score": 88.2,
  "recommendation_tags": ["Strong Skill Match", "High Semantic Similarity"]
}

```

* `semantic_match_score` (float, 0–100, nullable): the embedding-based similarity score from Intern 4's upgraded engine. Nullable so the endpoint keeps working even before the semantic engine is wired in.
* `recommendation_tags` (string array): short, human-readable labels the frontend can render as chips on the job card.
* `engine` (top-level field, already exists): will report a new value, e.g. `"semantic-ats-blended-v1"`, once Intern 4's upgrade lands — the existing `"heuristic-fallback-v1"` and `"external-ml-engine"` values stay valid as fallbacks, unchanged.
* **No breaking changes:** every Milestone 2 field stays exactly as-is. This is purely additive, so the Milestone 2 frontend keeps working even before Intern 1 wires up the new fields.

---

## Database Migration Note (for Intern 3, informational — not this doc's owner)

New tables anticipated: `resumes` (or `resume_versions`), storing `id (UUID)`, `user_id (UUID, FK)`, `file_name`, `file_type`, `version_number`, `is_active_version (Boolean)`, `parsed_status`, `parsed_text (Text, nullable)`, `extracted_skills (JSON, nullable)`, `uploaded_at`. This mirrors the existing `Job`/`Swipe` model conventions already in `app/models.py` (UUID primary keys, `Boolean` flags with `server_default`, `func.now()` timestamps) so it fits the codebase's existing style.

```

```