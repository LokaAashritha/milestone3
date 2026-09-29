def generate_ats_score(
    resume_text: str,
    resume_skills: list,
    job_description: str,
    job_skills: list
) -> dict:
    job_skills_set = set(job_skills or [])
    resume_skills_set = set(resume_skills or [])

    if job_skills_set:
        matched_skills = job_skills_set.intersection(resume_skills_set)
        match_score = float(round((len(matched_skills) / len(job_skills_set)) * 100, 2))
    else:
        match_score = 85.0

    missing_skills = list(job_skills_set - resume_skills_set)
    missing_keywords = ["keyword_1", "keyword_2"] if match_score < 80.0 else []

    return {
        "match_score": match_score,
        "summary": "Match score generated based on skill requirement overlap.",
        "missing_skills": missing_skills,
        "missing_keywords": missing_keywords,
    }


def generate_ai_suggestions(
    resume_skills: list,
    job_skills: list,
    missing_skills: list,
    missing_keywords: list
) -> dict:
    """
    Mock AI engine for Task 5.1.
    Simulates Intern 4's AI suggestions module.
    """
    suggestions = []

    if missing_skills:
        suggestions.append({
            "category": "Skill Alignment",
            "suggestion": f"Incorporate missing core skills into your skills section: {', '.join(missing_skills[:3])}."
        })

    if missing_keywords:
        suggestions.append({
            "category": "Keyword Optimization",
            "suggestion": f"Add relevant keywords to your experience bullet points: {', '.join(missing_keywords)}."
        })

    suggestions.append({
        "category": "Formatting & Clarity",
        "suggestion": "Quantify your achievements using measurable metrics (e.g., 'Increased performance by 25%')."
    })

    return {
        "overall_feedback": "Your resume has a strong base, but targeted keyword additions will boost your ATS match score.",
        "suggestions": suggestions
    }

def generate_recommendation_scores(resume_skills: list, job_skills: list) -> dict:
    """
    Mock Recommendation Matching Engine for Task 5.2.
    Generates semantic match scores and dynamic recommendation tags.
    """
    job_skills_set = set(job_skills or [])
    resume_skills_set = set(resume_skills or [])

    if job_skills_set:
        overlap = len(job_skills_set.intersection(resume_skills_set))
        semantic_score = float(round((overlap / len(job_skills_set)) * 100, 2))
    else:
        semantic_score = 75.0

    # Generate dynamic badges/tags based on match metrics
    tags = []
    if semantic_score >= 80.0:
        tags.append("Top Skill Fit")
    if semantic_score >= 60.0:
        tags.append("Strong Keyword Match")
    else:
        tags.append("Growth Opportunity")

    # Add secondary context tags
    tags.append("Low Competition")

    return {
        "semantic_match_score": semantic_score,
        "recommendation_tags": tags,
    }