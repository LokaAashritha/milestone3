Milestone 2 — Matching Engine v0 Design & Feature Specification

Intern 4 — AI/ML Career Intelligence

1. Overview
The Matching Engine provides a heuristic-ranked recommendation feed of job listings for candidate users. In Milestone 2, it establishes the contract and baseline scoring logic ahead of the full NLP/ML ATS-aware model scheduled for Milestone 3.

2. Feature Set Specification
The Matching Engine evaluates candidate-job compatibility across four primary feature signals:
- Skill Overlap (Weight: 70%): Measures canonical skill keyword intersection between candidate resume skills and job required skills.
- Contextual Keyword Overlap (Weight: 30%): Evaluates occurrence of job title and description terms in the candidate resume text.
- Location & Remote Preference Signal: Identifies remote vs. location fit.
- Experience Level & Role Alignment: Matches candidate profile experience level to job requirements.

3. Heuristic Scoring Formula (v0)
Skill Ratio = |Candidate Skills ∩ Job Skills| / |Job Skills|
Keyword Ratio = |Candidate Terms ∩ Job Terms| / |Job Terms|

Raw Score = (Skill Ratio * 0.70) + (Keyword Ratio * 0.30)
Final Match Score = Round(Clamp(Raw Score * 100, 0, 100), 1)

4. API Endpoint Contract
Endpoint: GET /api/v1/recommendations?user_id={id}
Response Schema: List of JobRecommendationItem
- job_id: string
- match_percentage: float (0.0 to 100.0)
- generated_by: "heuristic-v0"

5. Schema Handoff to Intern 3 (Job & Data Intelligence)
Required fields on Job entity:
- job_id (string)
- title (string)
- company (string)
- skills (list[string])
- description (string)
- location (string)
- remote (boolean)
- posted_at (datetime)
