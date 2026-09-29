from backend.app.services.skill_extractor import skill_extractor


def test_extract_programming_languages():
    text = "Proficient in Python, Java, TypeScript, Go and Rust."
    skills = skill_extractor.extract_skills(text)
    assert "Python" in skills
    assert "Java" in skills
    assert "TypeScript" in skills
    assert "Go" in skills
    assert "Rust" in skills
    assert "JavaScript" not in skills


def test_extract_frameworks_and_tools():
    text = (
        "Built web apps with FastAPI, React, Next.js, and Docker deployed to AWS with Kubernetes."
    )
    skills = skill_extractor.extract_skills(text)
    expected = ["AWS", "Docker", "FastAPI", "Kubernetes", "Next.js", "React"]
    for s in expected:
        assert s in skills


def test_multi_word_skill_extraction():
    text = "Experience with Machine Learning, Natural Language Processing, CI/CD pipelines, and Tailwind CSS."
    skills = skill_extractor.extract_skills(text)
    assert "Machine Learning" in skills
    assert "NLP" in skills
    assert "CI/CD" in skills
    assert "Tailwind CSS" in skills


def test_alias_normalization():
    text = "Used k8s for orchestration, postgres for database, and sklearn for modeling."
    skills = skill_extractor.extract_skills(text)
    assert "Kubernetes" in skills
    assert "PostgreSQL" in skills
    assert "scikit-learn" in skills


def test_empty_or_whitespace_text():
    assert skill_extractor.extract_skills("") == []
    assert skill_extractor.extract_skills("   \n\t  ") == []
    assert skill_extractor.extract_skills(None) == []


def test_normalize_skills_list():
    raw_list = ["k8s", "fastapi", "react.js", "CustomSkill123"]
    normalized = skill_extractor.normalize_skills(raw_list)
    assert "Kubernetes" in normalized
    assert "FastAPI" in normalized
    assert "React" in normalized
    assert "CustomSkill123" in normalized
