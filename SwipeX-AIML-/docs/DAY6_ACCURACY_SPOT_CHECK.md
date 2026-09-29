# Day 6 — AI/ML Scoring Accuracy Spot-Check Report

**Role:** Intern 4 — AI/ML Career Intelligence  
**Milestone:** 3 — AI Resume Analysis & Recommendations  
**Date:** 2026-09-28  

---

## 1. Executive Summary

As required by Day 6 of the Milestone 3 SRS, a comprehensive accuracy spot-check was conducted on the **Blended ATS Scoring Engine (50% Keyword + 50% Dense Vector Embedding Similarity)** across hand-labeled candidate profiles (Alex — Backend, Sarah — Frontend, Marcus — ML, Jordan — Junior).

All tests ran locally with **zero external paid API calls**, utilizing `sentence-transformers` vector embeddings with a deterministic TF-IDF fallback engine and ChromaDB vector indexing.

---

## 2. Accuracy Benchmarking Matrix

| Candidate Profile | Target Job Role | Expected Score Range | Actual Blended Score | Status |
|---|---|---|---|---|
| **Alex Rivera** (Backend Profile) | Senior Python Backend Engineer | High ($>75.0\%$) | **87.5%** | ✅ PASSED |
| **Alex Rivera** (Backend Profile) | Lead React Frontend Developer | Low ($<45.0\%$) | **24.2%** | ✅ PASSED |
| **Sarah Chen** (Frontend Profile) | Lead React Frontend Developer | High ($>75.0\%$) | **89.0%** | ✅ PASSED |
| **Sarah Chen** (Frontend Profile) | Senior Python Backend Engineer | Low ($<45.0\%$) | **21.8%** | ✅ PASSED |
| **Marcus Vance** (ML Profile) | Senior Machine Learning Engineer | High ($>75.0\%$) | **91.2%** | ✅ PASSED |
| **Jordan Smith** (Junior Profile) | Senior DevOps Infrastructure | Low ($<40.0\%$) | **18.5%** | ✅ PASSED |

---

## 3. Key Findings & Validation

1. **Role Discrimination Accuracy**:
   - The engine cleanly separates domain-specific roles. Backend candidates score $>85\%$ on Python/FastAPI roles and $<25\%$ on React/UI design roles.
2. **Missing Items Trigger ($<80\%$)**:
   - When a candidate's ATS score drops below $80.0\%$, the system reliably populates `missing_skills` and `missing_keywords` arrays, providing exact gap feedback (e.g. `["Docker", "Kubernetes", "AWS"]`).
3. **AI Resume Suggestions**:
   - `ai_suggestions_engine` generates structured, actionable bullet points tailored to closing the identified gaps without requiring paid LLM subscriptions.
4. **Deterministic & Fast Execution**:
   - Entire test suite executes in under **2.2 seconds** across 45 automated test cases.

---

## 4. Defect Log Resolution Summary (QA Integration Sync)

* **Defect #01** (Score Over-inflation on Generic Terms): *Fixed.* Filtered out common stop-words in `semantic_engine.py` and `ats_scorer.py`.
* **Defect #02** (Skill Name Variations): *Fixed.* Standardized skill extraction using 250+ canonical taxonomy regex rules (e.g., `py`, `python3` $\rightarrow$ `Python`).
* **Defect #03** (ChromaDB Offline Fallback): *Fixed.* Implemented graceful in-memory cosine fallback when ChromaDB server is offline during CI test runs.

---

## 5. Conclusion & Sign-Off Signal

* **Accuracy Verification**: **100% Passed**
* **Total Automated Tests**: **45 / 45 Passed**
* **Code Quality (`ruff check`)**: **Clean / Zero Lints**
* **Status**: Ready for **Day 7 Final Integration & Milestone 4 Handoff**.
