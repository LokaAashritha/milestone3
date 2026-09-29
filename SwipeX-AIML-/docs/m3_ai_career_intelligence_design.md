# Milestone 3 — AI Resume Analysis & Recommendations Architecture Specification

**Intern 4 — AI/ML Career Intelligence**  
*Document Version:* 1.0.0 — Day 1 Architecture & Design Baseline  
*Target Stack:* Free, Open-Source Python NLP Libraries (`pdfplumber`, `pypdf`, `python-docx`, `spaCy`, `sentence-transformers`, `ChromaDB`)

---

## 1. Overview & Objectives

Milestone 3 replaces the baseline heuristic stub with full AI/NLP capability for:
1. **Multi-Format Text Extraction**: Extracting clean plain text from PDF (`.pdf`), Word (`.docx`), and Plain Text (`.txt`) resume uploads.
2. **NLP Skill & Entity Extraction**: Named Entity Recognition using `spaCy` NER blended with a curated canonical skill taxonomy (250+ skills).
3. **Blended ATS Scoring Engine**: Blending exact keyword/skill diffing ($50\%$) with vector-embedding semantic similarity ($50\%$).
4. **AI Resume Optimization Suggestions**: Generating targeted action items for resumes scoring below the $80\%$ ATS threshold, featuring an LLM integration with a 100% free template fallback generator.
5. **Semantic-Aware Recommendation Engine**: Upgrading the recommendation feed by combining ChromaDB vector similarity with Milestone 2 candidate swipe signals (`like`, `save`, `skip`).

---

## 2. AI/NLP Technology Stack Selection (100% Free & Open-Source)

| Capability | Primary Library | Fallback / Secondary Library | Notes |
|---|---|---|---|
| **Text Extraction (PDF)** | `pdfplumber` | `pypdf` | Robust multi-column layout text extraction |
| **Text Extraction (DOCX)** | `python-docx` | Raw text stream | Full Microsoft Word document parsing |
| **Skill Extraction (NER)** | `spaCy` (`en_core_web_sm`) | Canonical Regex Taxonomy | Named Entity Recognition + 250+ skill rules |
| **Semantic Similarity** | `sentence-transformers` (`all-MiniLM-L6-v2`) | TF-IDF Vectorizer | 384-dimensional dense text embeddings |
| **Vector Storage** | `ChromaDB` | In-Memory Cosine Store | Vector similarity indexing and retrieval |
| **AI Suggestions** | Free LLM API / Local Prompt Generator | Rule-Based Template Engine | Zero-cost guaranteed suggestion generator |

---

## 3. Blended ATS Scoring Formula (v2)

For any given candidate resume ($R$) and target job ($J$):

$$\text{Skill Ratio} = \frac{|R_{\text{skills}} \cap J_{\text{skills}}|}{|J_{\text{skills}}|}$$

$$\text{Keyword Ratio} = \frac{|R_{\text{keywords}} \cap J_{\text{keywords}}|}{|J_{\text{keywords}}|}$$

$$\text{Keyword Match Score} = (\text{Skill Ratio} \times 0.70) + (\text{Keyword Ratio} \times 0.30)$$

$$\text{Semantic Similarity Score} = \text{CosineSimilarity}(\text{Embedding}(R_{\text{text}}), \text{Embedding}(J_{\text{text}})) \times 100$$

$$\text{Blended ATS Score} = \text{Round}\Big(\text{Clamp}\big((\text{Keyword Match Score} \times 0.50) + (\text{Semantic Similarity Score} \times 0.50), 0, 100\big), 1\Big)$$

### Missing Items & Threshold Trigger:
- **Threshold**: $80.0\%$
- If $\text{Blended ATS Score} < 80.0\%$, the engine returns:
  1. `missing_skills`: List of required job skills not found in candidate skills.
  2. `missing_keywords`: List of key terms from job title/description missing from resume body.
  3. `ai_suggestions`: 3–5 actionable bullet points explaining how to rewrite the resume to reach $80\%+$.

---

## 4. API & Module Interface Contracts (Day 1 Freeze)

### A. Resume Parse Trigger API (`POST /api/v1/resumes/{id}/parse`)
- **Caller**: Intern 2 (Backend Service)
- **Input**: `resume_id` (string), `file_path` (string), `file_type` (`.pdf`, `.docx`, `.txt`)
- **Output**: `parsed_skills: list[str]`, `raw_text: str`

### B. Blended ATS Score API (`POST /api/v1/ats/score`)
- **Caller**: Intern 2 (Backend Service) / Intern 1 (Frontend UI)
- **Input**: `resume_id` (string), `job_id` (string)
- **Output**:
  - `match_score`: float (0.0 to 100.0)
  - `keyword_score`: float
  - `semantic_score`: float
  - `missing_skills`: list[str]
  - `missing_keywords`: list[str]
  - `ai_suggestions`: list[str]

### C. Upgraded Recommendation Feed (`GET /api/v1/recommendations`)
- **Caller**: Intern 1 (Frontend UI)
- **Output**: List of `JobRecommendationItem` with `reason_tags` and `generated_by: "semantic-v2"`

---

## 5. Day-Wise Handoff Schedule Matrix

| Day | Module Built by Intern 4 | Provided To |
|---|---|---|
| **Day 1** | Architecture Spec & Interface Schemas | Self & Team (Contract Freeze) |
| **Day 2** | Text Extraction (PDF/DOCX) & spaCy Skill NER | Intern 2 (`POST /resumes/{id}/parse`) |
| **Day 3** | Keyword ATS Scoring Engine v1 | Intern 2 (`POST /ats/score`) |
| **Day 4** | Sentence-Transformers & ChromaDB Semantic Matcher | Intern 2 (Blended Scoring function) |
| **Day 5** | AI Resume Suggestions & Semantic Recommendation Feed | Intern 1 (UI Panels), Intern 2 (Gateway) |
| **Day 6** | Automated Pytest Suite & Spot-Check Accuracy Report | Intern 5 (CI Integration) |
| **Day 7** | Final Sign-Off & Milestone 4 Handoff | Educator / Mentor Demo |
