from backend.app.models.schemas import JobDetail, ResumeRecord
from backend.app.services.ai_suggestions import ai_suggestions_engine
from backend.app.services.ats_scorer import ats_scoring_engine
from backend.app.services.resume_parser import resume_repo


def test_sample_resumes_accuracy_spot_check():
    """Day 6 Spot-Check: Verify scoring accuracy across Backend, Frontend, and ML profiles."""

    # 1. Alex Rivera (Backend Profile)
    backend_resume = ResumeRecord(
        resume_id="res_alex_backend",
        user_id="user_alex",
        original_filename="alex_resume.pdf",
        file_path="/tmp/alex.pdf",
        file_type=".pdf",
        raw_text="Senior Backend Engineer specializing in Python, FastAPI, PostgreSQL, Docker, Redis, and REST APIs. Built microservices architectures.",
        parsed_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis", "REST API", "Microservices"],
    )
    resume_repo.save(backend_resume)

    # 2. Sarah Chen (Frontend Profile)
    frontend_resume = ResumeRecord(
        resume_id="res_sarah_frontend",
        user_id="user_sarah",
        original_filename="sarah_resume.txt",
        file_path="/tmp/sarah.txt",
        file_type=".txt",
        raw_text="Lead Frontend Developer with 5 years experience in React, TypeScript, Tailwind CSS, Redux, Next.js, HTML5, and UI/UX design.",
        parsed_skills=["React", "TypeScript", "Tailwind CSS", "Redux", "Next.js", "HTML5", "UI/UX Design"],
    )
    resume_repo.save(frontend_resume)

    # 3. Marcus Vance (ML / AI Profile)
    ml_resume = ResumeRecord(
        resume_id="res_marcus_ml",
        user_id="user_marcus",
        original_filename="marcus_resume.pdf",
        file_path="/tmp/marcus.pdf",
        file_type=".pdf",
        raw_text="Machine Learning Engineer specializing in PyTorch, TensorFlow, NLP, Transformers, LLMs, scikit-learn, and spaCy.",
        parsed_skills=["Machine Learning", "PyTorch", "TensorFlow", "NLP", "Transformers", "LLM", "scikit-learn", "spaCy"],
    )
    resume_repo.save(ml_resume)

    # Job A: Python Backend Engineer
    job_backend = JobDetail(
        job_id="job_backend_test",
        title="Senior Python Backend Developer",
        company="Tech Corp",
        description="Looking for a Senior Python Developer with expertise in FastAPI, PostgreSQL, Docker, Microservices, and REST APIs.",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Microservices"],
    )

    # Job B: React Frontend Engineer
    job_frontend = JobDetail(
        job_id="job_frontend_test",
        title="Senior React Frontend Developer",
        company="Design Web Inc",
        description="Hiring a Senior React Developer experienced with TypeScript, Tailwind CSS, Redux, and Next.js.",
        skills=["React", "TypeScript", "Tailwind CSS", "Redux", "Next.js"],
    )

    # -------------------------------------------------------------
    # Accuracy Assertions:
    # Alex (Backend) vs Backend Job -> Should be HIGH (>75%)
    score_alex_backend, _, _, _, _ = ats_scoring_engine.calculate_detailed_blended_score(backend_resume, job_backend)
    assert score_alex_backend >= 75.0, f"Alex backend score too low: {score_alex_backend}"

    # Alex (Backend) vs Frontend Job -> Should be LOW (<45%)
    score_alex_frontend, _, _, _, _ = ats_scoring_engine.calculate_detailed_blended_score(backend_resume, job_frontend)
    assert score_alex_frontend <= 45.0, f"Alex frontend score too high: {score_alex_frontend}"

    # Sarah (Frontend) vs Frontend Job -> Should be HIGH (>75%)
    score_sarah_frontend, _, _, _, _ = ats_scoring_engine.calculate_detailed_blended_score(frontend_resume, job_frontend)
    assert score_sarah_frontend >= 75.0, f"Sarah frontend score too low: {score_sarah_frontend}"

    # Sarah (Frontend) vs Backend Job -> Should be LOW (<45%)
    score_sarah_backend, _, _, _, _ = ats_scoring_engine.calculate_detailed_blended_score(frontend_resume, job_backend)
    assert score_sarah_backend <= 45.0, f"Sarah backend score too high: {score_sarah_backend}"


def test_day6_ai_suggestions_missing_items_accuracy():
    """Verify AI Suggestions correctly identifies missing items when score is under 80%."""
    resume = ResumeRecord(
        resume_id="res_jordan_junior",
        user_id="user_jordan",
        original_filename="jordan_resume.txt",
        file_path="/tmp/jordan.txt",
        file_type=".txt",
        raw_text="Junior Developer with experience in HTML, CSS, JavaScript, and basic Python.",
        parsed_skills=["HTML5", "CSS3", "JavaScript", "Python"],
    )

    job_devops = JobDetail(
        job_id="job_devops_senior",
        title="Senior DevOps & Infrastructure Engineer",
        company="CloudOps",
        description="Looking for Senior DevOps Engineer with Docker, Kubernetes, Terraform, AWS, and CI/CD automation experience.",
        skills=["Docker", "Kubernetes", "Terraform", "AWS", "CI/CD", "Linux"],
    )

    suggestions, missing_skills, missing_keywords = ai_suggestions_engine.generate_suggestions(resume, job_devops)

    assert len(suggestions) >= 2
    assert "Docker" in missing_skills or "Kubernetes" in missing_skills
    assert any("Gap" in s or "Boost" in s for s in suggestions)
