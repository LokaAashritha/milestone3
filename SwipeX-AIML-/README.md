SwipeX — Career Intelligence Service

Milestone 1 | AI/ML Module | Team-2

==================================================

Overview
--------

SwipeX is a job discovery platform with a swipe-based UI. This service handles the AI/ML side: resume parsing, ATS compatibility scoring, and job recommendations. Milestone 1 is fully rule-based using open-source Python libraries. No trained models, no cloud APIs, nothing paid.

--------------------------------------------------

API Endpoints
-------------

POST   /api/v1/resume/upload
GET    /api/v1/resume/{resume_id}/ats-score?job_id=<id>
GET    /api/v1/recommendations?user_id=<id>
GET    /health
GET    /docs

--------------------------------------------------

Tech Stack
----------

Framework: FastAPI
Validation: Pydantic v2
PDF parsing: pdfplumber, pypdf
Scoring engine: Custom regex taxonomy
Testing: pytest, httpx
Linting: ruff

--------------------------------------------------

Setup
-----

git checkout Team-2

python3 -m venv .venv
source .venv/bin/activate

pip install -r backend/requirements.txt

--------------------------------------------------

Run Server
----------

uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

Swagger UI is at http://localhost:8000/docs
Health check is at http://localhost:8000/health

--------------------------------------------------

Run Tests
---------

pytest -v
ruff check backend/

28 tests total. All pass on a clean install.

--------------------------------------------------

Project Structure
-----------------

backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── resume.py
│   │       │   └── recommendations.py
│   │       └── router.py
│   ├── core/
│   │   └── config.py
│   ├── data/
│   │   ├── seed_jobs.json
│   │   └── sample_resumes/
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── skill_extractor.py
│   │   ├── resume_parser.py
│   │   ├── ats_scorer.py
│   │   ├── recommendation_engine.py
│   │   └── job_service_client.py
│   ├── storage/
│   │   └── resumes/
│   └── main.py
└── tests/
    ├── conftest.py
    ├── test_skill_extractor.py
    ├── test_resume_parser.py
    ├── test_ats_scorer.py
    ├── test_recommendations.py
    └── test_api_endpoints.py

--------------------------------------------------

File Descriptions
-----------------

backend/app/main.py
FastAPI application entry point. Registers the CORS middleware, mounts the v1 router, and exposes /health and / routes. Run this file to start the server.

backend/app/core/config.py
Central settings using Pydantic BaseModel. Holds upload directory path, max file size (10 MB), allowed file types (.pdf, .txt), scoring weights (70/30), and the engine tag heuristic-v0. All other files import from here so configuration is never scattered.

backend/app/models/schemas.py
Frozen Pydantic schemas that define the exact API response contracts. Any change here breaks integration with Gateway, Frontend, and QA.
- ResumeUploadResponse — returned by POST upload
- ATSScoreResponse — returned by GET ats-score
- JobRecommendationItem — each item in GET recommendations
- ResumeRecord — internal model stored after parsing
- JobDetail — job posting data shape
- ErrorResponse — standard error format

backend/app/services/skill_extractor.py
The taxonomy engine. Contains SKILL_TAXONOMY, a dictionary of 250+ canonical skill names mapped to regex patterns and aliases. For example k8s and kubernetes both resolve to Kubernetes.
SkillExtractor.extract_skills(text) runs all compiled regex patterns against the input text and returns a sorted list of matched canonical skill names.
SkillExtractor.normalize_skills(skills_list) takes a raw list of strings and maps each one to the canonical taxonomy entry where possible.
A singleton skill_extractor is exported and reused across the service.

backend/app/services/resume_parser.py
Handles everything from file receipt to storage.
ResumeRepository is an in-memory store keyed by resume_id and also maintains a user_id -> list[resume_id] index so the latest resume per user can be fetched quickly.
ResumeParserService.validate_and_extract_text() checks file size, extension, and content before extraction.
extract_text_from_pdf() uses pdfplumber as the primary extractor and falls back to pypdf if it fails.
extract_text_from_txt() tries multiple encodings: utf-8, utf-8-sig, latin-1, cp1252, ascii.
parse_and_store_upload() is the full pipeline: read bytes, validate, save to disk with a UUID filename, run skill extraction, save the ResumeRecord, return the response.
Singletons resume_repo and resume_parser_service are exported for use by the API layer.

backend/app/services/ats_scorer.py
Computes a numeric ATS compatibility score between a resume and a job.
Scoring is a weighted formula:
- 70% from skill overlap: what fraction of the job's listed skills appear in the resume's parsed skills
- 30% from keyword overlap: what fraction of meaningful words in the job title and description appear in the resume body text
Final score is clamped to 0–100 and rounded to one decimal place. The list of job skills missing from the resume is returned alongside the score.
get_ats_score(resume_id, job_id) fetches both records, raises 404 if either is missing, then calls calculate_score().
Singleton ats_scoring_engine is exported.

backend/app/services/recommendation_engine.py
Scores every available job against the user's latest uploaded resume using ATSScoringEngine.calculate_score(), then sorts the results descending by match_percentage. Ties are broken alphabetically by job_id.
If the user has no uploaded resume, it returns an empty list with 200 OK rather than an error.
Singleton recommendation_engine is exported.

backend/app/services/job_service_client.py
Adapter between this service and job data. On startup it reads seed_jobs.json and caches all jobs in memory. When Intern 2's job service is live, this is the file to update — swap _load_seed_jobs() for an HTTP call or database query.
Exposes get_job(job_id), list_jobs(), and add_or_update_job().

backend/app/api/v1/endpoints/resume.py
Two routes:
POST /resume/upload — accepts a multipart file and optional user_id (form field or X-User-ID header). Delegates to ResumeParserService. Returns resume_id and parsed_skills.
GET /resume/{resume_id}/ats-score — requires job_id as a query param. Delegates to ATSScoringEngine. Returns match_score, missing_keywords, generated_by.

backend/app/api/v1/endpoints/recommendations.py
Single route:
GET /recommendations — accepts user_id (query param or X-User-ID header) and limit. Delegates to RecommendationEngine. Returns a list of JobRecommendationItem.

backend/app/api/v1/router.py
Aggregates both endpoint routers into api_v1_router. This is what Intern 1 imports and mounts in the Gateway app.

backend/app/data/seed_jobs.json
Eight synthetic job postings covering Python backend, React frontend, DevOps, data engineering, ML, full-stack, mobile, and QA roles. Used as the default job source until Intern 2's service is ready.

backend/app/data/sample_resumes/
Four sample resumes for testing:
- resume_backend_alex.pdf — Python/FastAPI/PostgreSQL/Docker profile
- resume_frontend_sarah.txt — React/TypeScript/Tailwind profile
- resume_ml_marcus.pdf — PyTorch/TensorFlow/NLP profile
- resume_junior_jordan.txt — entry-level mixed-stack profile

backend/tests/conftest.py
Pytest fixtures shared across all test files. Provides client (FastAPI TestClient), sample_data_dir, and four fixtures pointing to the sample resume files. Also has an autouse fixture that clears the in-memory repo before and after every test to prevent state leakage.

backend/tests/test_skill_extractor.py
Unit tests for SkillExtractor. Covers programming language detection, multi-word skill extraction, alias normalization (k8s, postgres, sklearn), empty/null input handling, and the normalize_skills method.

backend/tests/test_resume_parser.py
Unit tests for ResumeParserService. Covers successful PDF and TXT extraction, empty file rejection, unsupported extension rejection, corrupted PDF handling, and the full upload pipeline including repository storage and user lookup.

backend/tests/test_ats_scorer.py
Unit tests for ATSScoringEngine. Covers a perfect skill match resulting in score >= 80, a frontend resume against a backend job resulting in score < 30 with correct missing keywords, and 404 handling for nonexistent resume and job IDs.

backend/tests/test_recommendations.py
Unit tests for RecommendationEngine. Covers empty list on missing user ID, empty list when no resume uploaded, correct top recommendation for a Python engineer profile (job_py_01), correct top recommendation for a frontend profile (job_react_02), and descending sort order validation.

backend/tests/test_api_endpoints.py
End-to-end API tests using FastAPI's TestClient. Covers PDF upload, TXT upload, Gateway header (X-User-ID) upload, invalid extension rejection, empty file rejection, ATS score calculation and response shape, 404 on nonexistent resume, recommendations for a new user (empty), recommendations after upload, and OpenAPI schema validation.

pyproject.toml
Ruff linter configuration (line length, rule sets) and pytest configuration (test paths, python paths). Both tools read from this file.

pytest.ini
Sets testpaths = backend/tests and pythonpath = . so pytest can resolve backend.* imports without needing the package to be installed.

backend/requirements.txt
Pinned dependencies:
fastapi
uvicorn
pydantic
pdfplumber
pypdf
pytest
httpx
ruff

--------------------------------------------------

Scoring Formula
---------------

skill_score   = (matched_skills / total_job_skills) * 0.70
keyword_score = (matched_keywords / total_job_keywords) * 0.30
final_score   = round(clamp((skill_score + keyword_score) * 100, 0, 100), 1)

missing_keywords is the sorted list of job skills not found in the resume.
All responses are tagged generated_by: heuristic-v0 to signal this is the rule-based version.

--------------------------------------------------

Upload Constraints
------------------

- Accepted formats: .pdf, .txt
- Max file size: 10 MB
- Files are saved to backend/app/storage/resumes/ with UUID-based names to avoid collisions
- Original filename is stored in the ResumeRecord for reference

--------------------------------------------------

Team Notes
----------

Intern 1 (Gateway) — Import api_v1_router from backend.app.api.v1.router and mount it with prefix /api/v1. Forward X-User-ID on authenticated requests.

Intern 2 (Jobs) — job_service_client.py currently loads from seed_jobs.json. Replace _load_seed_jobs() with a call to your service when it is ready. The JobDetail schema in schemas.py is the expected shape.

Intern 4 (Frontend) — Three endpoints to wire: POST /api/v1/resume/upload for resume submission, GET /api/v1/resume/{id}/ats-score?job_id=<id> for score display, GET /api/v1/recommendations?user_id=<id> for the recommendation feed.

Intern 5 (QA) — Run pytest backend/tests/ -v in the CI pipeline. All 28 tests must pass before merge.
