# 🎯 SwipeX — Job & Data Intelligence Service (Milestone 3)

> **Domain:** Job & Data Intelligence (Author: Shubham Ugale)  
> **Platform:** SwipeX — Swipe-Based Intelligent Job Discovery Platform  
> **Status:** Milestone 3 Completed, Fully Tested (44/44 Passing) & Production-Ready  

---

## 📌 1. Module Overview & Responsibilities
This microservice serves as the **core data backbone** for the SwipeX platform across Milestones 1, 2, and 3:
1. **Relational Schemas:** Production schemas for `companies`, `jobs`, `swipes`, `saved_jobs`, `resumes`, and `resume_skills` with composite indexes.
2. **Comprehensive Seed Dataset:** **323 curated job postings** across **29 employers** (MNCs, Startups, and Newly Founded AI startups) with structured `required_skills` and domain `keywords`.
3. **Resume Service & Versioning:** Multi-version resume upload (PDF/DOCX, 10MB limit), automatic version incrementing, default version toggling, and disk file storage layer (`app/core/storage.py`).
4. **ATS Compatibility Scoring (FR-03 / FR-04):** Blended ATS scoring formula comparing parsed resume skills and domain keywords against job requirements, strictly identifying `missing_skills` and `missing_keywords` whenever `match_score < 80%`.
5. **Freshness & Competition Intelligence:** Rule-based computation (`app/core/intelligence.py`) for live applicant competition tags and posting freshness badges.
6. **Faceted Search & Discovery APIs:** Dedicated smart search API (`/jobs/search`), company profiles (`/companies`), and candidate bookmarks (`/saved-jobs`).
7. **Fast Caching Layer:** Redis cache with automatic in-memory fallback.
8. **Data Protection:** Automated database snapshot backup and restore utility (`db_backup_restore.py`) covering all tables.
9. **100% Test Coverage:** 44 passing automated unit tests in `pytest`.

---

## 🚀 2. REST API Endpoints Overview

### Resumes & ATS Scoring (Milestone 3 Core)
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/resumes/upload` | **Upload Resume:** Multipart upload (PDF/DOCX, max 10MB, auto-versioning) |
| `GET` | `/api/v1/resumes` | **List Versions:** All uploaded resume versions for user (`?active_only=true`) |
| `GET` | `/api/v1/resumes/{id}` | **Resume Detail:** Metadata, parsed text, and extracted skills |
| `POST` | `/api/v1/resumes/{id}/parse` | **Parse Trigger:** Store parsed text, extracted skills, and normalize into `resume_skills` |
| `PATCH` | `/api/v1/resumes/{id}/activate` | **Set Active:** Mark specific version as active/default |
| `POST` | `/api/v1/ats/score` | **ATS Scoring:** Blended compatibility score + missing skills/keywords when `< 80%` |

### Jobs, Companies & Swipes (Milestone 1 & 2 Baselines)
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/jobs` | Browse paginated job feed with multi-criteria filters |
| `GET` | `/api/v1/jobs/search` | **Smart Search:** Full-text keyword search across skills, titles, and descriptions |
| `GET` | `/api/v1/jobs/{job_id}` | Detailed job view with company info, freshness, and competition score |
| `POST` | `/api/v1/swipes` | Record swipe action (Right = Apply/Save, Left = Skip) |
| `GET` | `/api/v1/swipes/history` | User swipe history |
| `GET` | `/api/v1/swipes/summary` | User swipe metrics summary |
| `GET` | `/api/v1/companies` | List companies & startups (filter by `type`, `industry`, `newly_founded`) |
| `GET` | `/api/v1/companies/{id}` | Detailed company profile with all active jobs posted by the employer |
| `POST` | `/api/v1/saved-jobs` | Bookmark / Save a job with candidate notes |
| `GET` | `/api/v1/saved-jobs` | Retrieve user bookmarked jobs with card summaries |
| `DELETE` | `/api/v1/saved-jobs/{job_id}` | Remove job from bookmarked list |

---

## 🛠️ 3. Quick Start & Local Execution

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Service
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger UI: **`http://localhost:8000/docs`**
- Alternative ReDoc: **`http://localhost:8000/redoc`**

### Run Automated Tests
```bash
python -m pytest -v
```
*(All 44 test cases pass with 100% success rate)*

### Database Backup & Restore Utility
```bash
# Create JSON snapshot backup
python app/scripts/db_backup_restore.py --backup

# Restore from snapshot
python app/scripts/db_backup_restore.py --restore backups/<backup_file>.json
```

---

## 🤝 4. Milestone 4 Handoff Notes (Analytics, Notifications & Dashboards)

As documented in `DATA_DICTIONARY.md`, Milestone 4 modules can directly leverage:
- **Module 8 (Candidate Tracking):** Candidate right-swipes (`SwipeActionType.APPLY`) linked to `Resume.id` with snapshot ATS `match_score`.
- **Module 9 (Smart Notifications):** Skill gap alerts triggered whenever a saved job has `match_score < 80%` identifying exact missing keywords.
- **Module 10 (Recruiter Talent Analytics):** Inverted index aggregation on `resume_skills` to visualize market demand vs talent availability.
