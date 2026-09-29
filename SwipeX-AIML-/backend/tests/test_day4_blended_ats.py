from backend.app.models.schemas import JobDetail, ResumeRecord
from backend.app.services.ats_scorer import ats_scoring_engine
from backend.app.services.semantic_engine import semantic_matching_engine


def test_semantic_matching_engine_similarity():
    text_python_dev = "Senior Python developer with FastAPI, PostgreSQL, Docker, and REST API experience."
    text_python_job = "Looking for a Python Backend Engineer to build REST APIs with FastAPI and PostgreSQL."
    text_design_job = "Figma Product Designer needed for mobile UI/UX wireframing and prototyping."

    score_match = semantic_matching_engine.calculate_similarity(text_python_dev, text_python_job)
    score_mismatch = semantic_matching_engine.calculate_similarity(text_python_dev, text_design_job)

    assert score_match > score_mismatch
    assert score_match > 40.0


def test_blended_ats_scoring_formula():
    resume = ResumeRecord(
        resume_id="res_day4_test",
        user_id="user_day4",
        original_filename="alex_backend.pdf",
        file_path="/tmp/alex.pdf",
        file_type=".pdf",
        raw_text="Experienced Backend Software Engineer specializing in Python, FastAPI, PostgreSQL, and Docker. Built scalable microservices.",
        parsed_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "REST API", "Microservices"],
    )

    job = JobDetail(
        job_id="job_day4_backend",
        title="Python Backend Engineer",
        company="Tech Corp",
        description="We are hiring a Python Backend Engineer proficient in FastAPI, PostgreSQL, Docker, and Kubernetes.",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
    )

    blended_score, keyword_score, semantic_score, missing_skills, missing_keywords = (
        ats_scoring_engine.calculate_detailed_blended_score(resume, job)
    )

    assert blended_score > 0.0
    assert 0.0 <= keyword_score <= 100.0
    assert 0.0 <= semantic_score <= 100.0
    assert "Kubernetes" in missing_skills
    # Formula check: Blended = 0.5 * keyword + 0.5 * semantic
    expected_blended = round((keyword_score * 0.5) + (semantic_score * 0.5), 1)
    assert abs(blended_score - expected_blended) <= 0.1


def test_chromadb_indexing_and_vector_query():
    job_id = "job_test_chroma_101"
    job_text = "Senior Machine Learning Engineer specializing in PyTorch, NLP, and LLM fine-tuning."
    semantic_matching_engine.index_job(job_id=job_id, job_text=job_text)

    query_resume = "AI Researcher experienced with PyTorch, Natural Language Processing, and LLMs."
    results = semantic_matching_engine.query_similar_jobs(query_resume, top_k=5)

    assert len(results) > 0
    top_job_id, top_score = results[0]
    assert top_job_id == job_id
    assert top_score > 10.0
