# 📑 SwipeX — Schema Notes & Data Models (Day 1 / Milestone 2)

> **Author:** Shubham Ugale (Intern — Job & Data Intelligence)  
> **Prepared For:** Frontend & User Experience Team / Integration Lead  
> **Purpose:** Comprehensive documentation of all database models, API field contracts, data types, UI formatting notes, and TypeScript interfaces for seamless frontend swipe deck & search integration.

---

## 📌 Executive Summary for Frontend / Integration

This document outlines the exact shape of all data models powering the **Swipe Deck**, **Job Cards**, **Filters Panel**, **Company Pages**, and **Saved Jobs**.

### Key Highlights for UI Developers:
- **Image / Logo:** Always provided as `company_logo_url` (with valid fallback image URL).
- **Salary Display:** Pre-formatted human-readable string `salary_range` (e.g., `"₹14 LPA - ₹24 LPA"`) is provided directly by the API, alongside raw integer values `salary_min` and `salary_max`.
- **Skill Tags:** Stored and returned as a clean `string[]` array `skills` (e.g., `["React", "TypeScript", "Tailwind CSS"]`).
- **Dynamic Badges:**
  - `freshness_label`: `"Just Posted"` (green), `"Recently Posted"` (blue), `"This Week"`, or `"Active"`.
  - `competition_level`: `"Low"` (green / early applicant), `"Medium"` (yellow), `"High"` (orange).
  - `is_early_applicant`: `boolean` flag (`true` when `< 15 applicants`).
  - `is_newly_founded`: `boolean` flag to render startup discovery tags.

---

## 🗄️ 1. Complete Field Specifications

### 1.1 Job Card & Listing Model (`Job`)
Used by: **Swipe Deck**, **Job Card Component**, **Search & Filter Results**, **Job Detail Modal**.

| Field Name | Type | Sample Value | UI Usage & Component Guidelines |
|---|---|---|---|
| `job_id` | `number` | `1` | Primary key identifier for swipe actions & detail view |
| `title` | `string` | `"Frontend Engineer (React.js & Tailwind)"` | Primary heading on Job Card |
| `company` | `string` | `"Razorpay"` | Company name on card header |
| `company_id` | `number` | `6` | Used for routing to company profile: `/companies/${company_id}` |
| `company_type` | `string` | `"Startup"` | Tag badge: `"MNC"` \| `"Startup"` \| `"Newly Founded"` |
| `company_logo_url` | `string \| null` | `"https://upload.wikimedia.org/..."` | Card avatar/logo (Render fallback icon if null) |
| `is_newly_founded` | `boolean` | `false` | Renders a "✨ Early Startup" discovery badge |
| `type` | `string` | `"Full-time"` | Job type pill: `"Full-time"`, `"Internship"`, `"Contract"` |
| `workplace_type` | `string` | `"Hybrid"` | Workplace badge: `"Remote"`, `"On-site"`, `"Hybrid"` |
| `location` | `string` | `"Bengaluru, Karnataka, India"` | Location text with map pin icon |
| `salary_range` | `string` | `"₹14 LPA - ₹24 LPA"` | **Pre-formatted** CTC string for instant display |
| `salary_min` | `number` | `1400000` | Used for slider filter comparisons |
| `salary_max` | `number` | `2400000` | Used for slider filter comparisons |
| `salary_currency` | `string` | `"INR"` | Currency unit (`"INR"`, `"USD"`) |
| `skills` | `string[]` | `["React", "TypeScript", "Tailwind CSS"]` | Chip/Tag list rendered at the bottom of the Job Card |
| `experience_level`| `string` | `"Mid-level"` | Experience tag: `"Fresher"`, `"Entry-level"`, `"Mid-level"`, `"Senior"` |
| `competition_level`| `string`| `"Medium"` | Competition badge: `"Low"` (Green), `"Medium"` (Yellow), `"High"` (Red) |
| `applicant_count` | `number` | `34` | "34 candidates applied" indicator |
| `is_early_applicant`| `boolean`| `false` | Shows "🔥 Be an early applicant!" badge when `true` (`< 15 applicants`) |
| `is_fresher_friendly`| `boolean`| `false` | Renders "🎓 Fresher Friendly" chip |
| `freshness_label` | `string` | `"Recently Posted"` | Time badge: `"Just Posted"`, `"Recently Posted"`, `"Active"` |
| `posted_days_ago` | `number` | `2` | Number of days since publication |
| `posted_at` | `string` | `"2026-09-11T10:30:00Z"` | ISO-8601 UTC timestamp |

#### Extended Fields (Available in `GET /api/v1/jobs/{job_id}` Detail View):
| Field Name | Type | Description |
|---|---|---|
| `description` | `string` | Full job overview markdown / text |
| `responsibilities` | `string` | Bulleted list of day-to-day role responsibilities |
| `requirements` | `string` | Prerequisite skills, degrees, and qualifications |
| `competition_score`| `number` | Normalized score `0.0 - 100.0` for competition gauge bars |
| `company_profile` | `CompanyDetail` | Nested full company object |

---

### 1.2 Company & Startup Profile Model (`Company`)
Used by: **Company Listing Page**, **Startup Discovery Grid**, **Company Detail Page**.

| Field Name | Type | Sample Value | UI Usage |
|---|---|---|---|
| `id` | `number` | `6` | Unique company ID |
| `name` | `string` | `"Razorpay"` | Company title |
| `slug` | `string` | `"razorpay"` | URL slug for clean routing |
| `company_type` | `string` | `"Startup"` | `"MNC"` \| `"Startup"` \| `"Newly Founded"` |
| `is_newly_founded` | `boolean` | `false` | Filter toggle chip: "Newly Founded Startups" |
| `industry` | `string` | `"Fintech & Payments"` | Category chip (e.g. Fintech, AI, E-commerce) |
| `headquarters` | `string` | `"Bengaluru, Karnataka, India"` | Location text |
| `funding_stage` | `string` | `"Series F / Unicorn"` | Funding badge: `"Seed"`, `"Series A"`, `"Bootstrapped"`, `"Public"` |
| `logo_url` | `string` | `"https://upload.wikimedia.org/..."` | Company brand logo |
| `website` | `string` | `"https://razorpay.com/jobs"` | External link to careers page |
| `description` | `string` | `"Leading financial solutions..."` | About the company paragraph |
| `founded_year` | `number` | `2014` | Inception year |
| `employee_count_range`| `string`| `"1000-5000"` | Team size pill |
| `active_jobs_count` | `number` | `12` | Total active jobs posted by this company |
| `jobs` | `JobSummary[]` | `[...]` | Array of job cards for this company |

---

### 1.3 Swipe Interaction Model (`Swipe`)
Used by: **Swipe Deck Gestures**, **Swipe Action Recording**, **Undo Action**, **Swipe History**.

#### A. Record Swipe Request Body (`POST /api/v1/swipes`):
```json
{
  "job_id": 1,
  "direction": "right",
  "action_type": "apply",
  "notes": "Applied via swipe deck"
}
```
*Note: `direction` must be `"right"` or `"left"`. `action_type` can be `"apply"`, `"save"`, or `"skip"`.*

#### B. Swipe Record Response (201 Created):
| Field Name | Type | Sample Value | Description |
|---|---|---|---|
| `swipe_id` | `number` | `101` | Unique ID of recorded swipe |
| `user_id` | `string` | `"demo-user-1"` | Authenticated candidate ID |
| `job_id` | `number` | `1` | ID of swiped job card |
| `direction` | `string` | `"right"` | `"right"` (liked/applied) or `"left"` (skipped) |
| `action_type` | `string` | `"apply"` | `"apply"` \| `"save"` \| `"skip"` |
| `swiped_at` | `string` | `"2026-09-13T14:20:00Z"` | ISO-8601 timestamp |
| `message` | `string` | `"Swipe recorded successfully"` | Confirmation text |

---

### 1.4 Bookmarking / Saved Jobs Model (`SavedJob`)
Used by: **Saved Jobs Tab**, **Bookmark Button on Card**, **Application History**.

| Field Name | Type | Sample Value | Description |
|---|---|---|---|
| `id` | `number` | `15` | Unique bookmark entry ID |
| `user_id` | `string` | `"demo-user-1"` | Candidate ID |
| `job_id` | `number` | `1` | Bookmarked job ID |
| `notes` | `string \| null` | `"Review portfolio before applying"` | User's private notes |
| `saved_at` | `string` | `"2026-09-13T12:00:00Z"` | Timestamp |
| `job` | `JobSummary` | `{ ... }` | Full embedded job summary object |

---

## 💻 2. Frontend TypeScript Interfaces (Copy-Paste Ready)

Frontend developers can directly copy these type definitions into `types/job.ts`:

```typescript
// ==========================================
// SwipeX Data Models & API Contracts
// ==========================================

export type CompanyType = "MNC" | "Startup" | "Newly Founded";
export type JobType = "Full-time" | "Part-time" | "Internship" | "Contract";
export type WorkplaceType = "Remote" | "On-site" | "Hybrid";
export type ExperienceLevel = "Fresher" | "Entry-level" | "Mid-level" | "Senior" | "Lead";
export type CompetitionLevel = "Low" | "Medium" | "High";
export type FreshnessLabel = "Just Posted" | "Recently Posted" | "This Week" | "Active";
export type SwipeDirection = "right" | "left";
export type SwipeActionType = "apply" | "save" | "skip";

/**
 * Job Card Summary (Used in Swipe Deck, Search Feeds, & Company Pages)
 */
export interface JobSummary {
  job_id: number;
  title: string;
  company: string;
  company_id: number;
  company_type: CompanyType;
  is_newly_founded: boolean;
  company_logo_url: string | null;
  type: JobType;
  workplace_type: WorkplaceType;
  location: string;
  salary_range: string;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string;
  skills: string[];
  experience_level: ExperienceLevel;
  competition_level: CompetitionLevel;
  applicant_count: number;
  is_fresher_friendly: boolean;
  posted_at: string;
  freshness_label: FreshnessLabel;
  posted_days_ago: number;
  is_early_applicant: boolean;
}

/**
 * Full Job Details (Used in Job Detail Modal / Page)
 */
export interface JobDetail extends JobSummary {
  id: number;
  role_category?: string;
  description: string;
  responsibilities?: string;
  requirements?: string;
  salary_period: string;
  experience_years_min: number;
  experience_years_max: number;
  competition_score: number;
  expires_at?: string | null;
  company: CompanySummary;
}

/**
 * Company Profile
 */
export interface CompanySummary {
  id: number;
  name: string;
  slug: string;
  company_type: CompanyType;
  is_newly_founded: boolean;
  industry: string;
  headquarters: string;
  funding_stage?: string;
  logo_url?: string | null;
  website?: string | null;
  description?: string | null;
  founded_year?: number | null;
  employee_count_range?: string | null;
  created_at: string;
}

export interface CompanyDetailWithJobs extends CompanySummary {
  active_jobs_count: number;
  jobs: JobSummary[];
}

/**
 * Swipe Action Payload
 */
export interface SwipePayload {
  job_id: number;
  direction: SwipeDirection;
  action_type?: SwipeActionType;
  notes?: string;
  user_id?: string;
}

export interface SwipeResponse {
  swipe_id: number;
  user_id: string;
  job_id: number;
  direction: SwipeDirection;
  action_type: SwipeActionType;
  swiped_at: string;
  message: string;
}

export interface SavedJobItem {
  id: number;
  user_id: string;
  job_id: number;
  notes?: string | null;
  saved_at: string;
  job?: JobSummary;
}
```

---

## 🎨 3. UI Badge & Color System Guidelines

To ensure aesthetic consistency across components:

| Category | Value | Recommended Tailwind CSS Classes |
|---|---|---|
| **Freshness** | `"Just Posted"` (`< 24h`) | `bg-emerald-500/10 text-emerald-400 border border-emerald-500/20` |
| | `"Recently Posted"` (`<= 3d`) | `bg-blue-500/10 text-blue-400 border border-blue-500/20` |
| | `"Active"` (`> 7d`) | `bg-zinc-500/10 text-zinc-400 border border-zinc-500/20` |
| **Competition** | `"Low"` (`< 25 applicants`) | `bg-green-500/10 text-green-400 border border-green-500/20` |
| | `"Medium"` (`25-100 applicants`) | `bg-amber-500/10 text-amber-400 border border-amber-500/20` |
| | `"High"` (`> 100 applicants`) | `bg-rose-500/10 text-rose-400 border border-rose-500/20` |
| **Early Bird** | `is_early_applicant = true` | `bg-gradient-to-r from-orange-500 to-amber-500 text-white font-medium` |
| **Startup** | `is_newly_founded = true` | `bg-purple-500/10 text-purple-400 border border-purple-500/20` |
| **Workplace** | `"Remote"` | `bg-indigo-500/10 text-indigo-400 border border-indigo-500/20` |

---

## 🔗 4. API Endpoints Reference Cheat-Sheet

| Action | HTTP Method | Endpoint | Query Parameters |
|---|---|---|---|
| **Swipe Feed** | `GET` | `/api/v1/jobs` | `type`, `location`, `remote`, `salary_min`, `salary_max`, `skills`, `fresher_friendly`, `newly_founded`, `page`, `page_size` |
| **Smart Search** | `GET` | `/api/v1/jobs/search` | `q` (free text), `location`, `skills`, `company_type`, `low_competition_only`, `is_fresh_only` |
| **Job Details** | `GET` | `/api/v1/jobs/{job_id}` | *(None)* |
| **Record Swipe** | `POST` | `/api/v1/swipes` | *(Request Body: `{ job_id, direction, action_type }`)* |
| **Swipe History**| `GET` | `/api/v1/swipes/history`| `direction`, `action_type`, `user_id`, `limit` |
| **Companies List**| `GET` | `/api/v1/companies` | `type`, `industry`, `newly_founded`, `search`, `page`, `page_size` |
| **Company Page**| `GET` | `/api/v1/companies/{id}` | *(None - returns profile + active jobs)* |
| **Save a Job** | `POST` | `/api/v1/saved-jobs` | *(Request Body: `{ job_id, notes }`)* |
| **List Saved** | `GET` | `/api/v1/saved-jobs` | `user_id` |
| **Unsave Job** | `DELETE`| `/api/v1/saved-jobs/{job_id}` | `user_id` |

---

*Contact **Shubham Ugale** (Job & Data Intelligence) for any additional mock payloads or schema adjustments.*
