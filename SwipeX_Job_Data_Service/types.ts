/**
 * SwipeX — Frontend TypeScript Definitions
 * Prepared by: Shubham Ugale (Job & Data Intelligence)
 * For: Frontend Swipe Deck, Search UI, Company Pages & Saved Jobs
 */

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
 * Full Job Details (Used in Job Detail Modal / View)
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

/**
 * Milestone 3: Resume Management & Versions
 */
export type ParsedStatus = "pending" | "processing" | "done" | "failed";

export interface ResumeVersion {
  id: string;
  user_id: string;
  file_name: string;
  file_type: "pdf" | "docx";
  file_size?: number;
  version_number: number;
  is_active_version: boolean;
  parsed_status: ParsedStatus;
  parsed_text: string | null;
  extracted_skills: string[] | null;
  uploaded_at: string;
  parsed_at?: string | null;
}

/**
 * Milestone 3: ATS Compatibility Scoring
 */
export interface ATSScorePayload {
  resume_id: string;
  job_id: string | number;
}

export interface ATSScoreResponse {
  resume_id: string;
  job_id: string;
  match_score: number;
  missing_skills: string[];
  missing_keywords: string[];
  scored_at: string;
}

