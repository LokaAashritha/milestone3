from backend.app.models.schemas import ResumeRecord
from backend.app.services.recommendation_engine import recommendation_engine
from backend.app.services.resume_parser import resume_repo


def test_recommendations_no_user_or_no_resume():
    assert recommendation_engine.get_recommendations_for_user(None) == []
    assert recommendation_engine.get_recommendations_for_user("user_unknown_999") == []


def test_recommendations_ranking_for_python_engineer():
    resume = ResumeRecord(
        resume_id="res_py_user",
        user_id="user_python_dev",
        original_filename="alex.pdf",
        file_path="/tmp/alex.pdf",
        file_type=".pdf",
        raw_text="Senior Python Backend developer. FastAPI, PostgreSQL, Redis, Docker, REST API, Microservices, Git, AWS.",
        parsed_skills=[
            "Python",
            "FastAPI",
            "PostgreSQL",
            "Redis",
            "Docker",
            "REST API",
            "Microservices",
            "Git",
            "AWS",
        ],
    )
    resume_repo.save(resume)

    recs = recommendation_engine.get_recommendations_for_user("user_python_dev")
    assert len(recs) > 0
    top_rec = recs[0]
    assert top_rec.match_percentage > 0
    assert top_rec.generated_by in ["blended-v2", "heuristic-v0"]

    scores = [r.match_percentage for r in recs]
    assert scores == sorted(scores, reverse=True)


def test_recommendations_ranking_for_frontend_engineer():
    resume = ResumeRecord(
        resume_id="res_react_user",
        user_id="user_frontend_dev",
        original_filename="sarah.txt",
        file_path="/tmp/sarah.txt",
        file_type=".txt",
        raw_text="Frontend Developer specializing in React, Next.js, TypeScript, Tailwind CSS, Redux, Jest.",
        parsed_skills=["React", "Next.js", "TypeScript", "Tailwind CSS", "Redux", "Jest"],
    )
    resume_repo.save(resume)

    recs = recommendation_engine.get_recommendations_for_user("user_frontend_dev")
    assert len(recs) > 0
    assert recs[0].match_percentage > 0
