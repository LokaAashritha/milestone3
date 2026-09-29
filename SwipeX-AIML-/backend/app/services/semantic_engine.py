import math
import re
from typing import Any

from backend.app.core.config import settings

STOP_WORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are",
    "as", "at", "be", "because", "been", "before", "being", "below", "between", "both", "but",
    "by", "can", "did", "do", "does", "doing", "down", "during", "each", "few", "for", "from",
    "further", "had", "has", "have", "having", "he", "her", "here", "hers", "herself", "him",
    "himself", "his", "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or",
    "other", "our", "ours", "ourselves", "out", "over", "own", "same", "she", "should", "so",
    "some", "such", "than", "that", "the", "their", "theirs", "them", "themselves", "then",
    "there", "these", "they", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves"
}


class SemanticMatchingEngine:
    """Milestone 3 Day 4: Semantic Similarity Engine with Vector Store (ChromaDB) & Embedding Fallback.

    Computes 384-dim dense embedding vector cosine similarity between resumes and job descriptions using
    sentence-transformers, with ChromaDB vector storage and a robust TF-IDF fallback engine for deterministic offline testing.
    """

    def __init__(self):
        self._st_model = None
        self._chroma_client = None
        self._chroma_collection = None
        self._in_memory_index: dict[str, str] = {}
        self._initialize_optional_components()

    def _initialize_optional_components(self):
        # Attempt loading sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            self._st_model = SentenceTransformer(settings.EMBEDDING_MODEL_NAME)
        except Exception:
            self._st_model = None

        # Attempt connecting to ChromaDB vector store
        try:
            import chromadb
            self._chroma_client = chromadb.HttpClient(
                host=settings.CHROMADB_HOST, port=settings.CHROMADB_PORT
            )
            self._chroma_collection = self._chroma_client.get_or_create_collection("swipex_jobs")
        except Exception:
            try:
                import chromadb
                self._chroma_client = chromadb.Client()
                self._chroma_collection = self._chroma_client.get_or_create_collection("swipex_jobs")
            except Exception:
                self._chroma_client = None
                self._chroma_collection = None

    def tokenize(self, text: str) -> list[str]:
        if not text:
            return []
        words = re.findall(r"\b[a-zA-Z0-9+#.-]+\b", text.lower())
        return [w for w in words if w not in STOP_WORDS and len(w) > 1]

    def compute_tf(self, tokens: list[str]) -> dict[str, float]:
        tf: dict[str, float] = {}
        if not tokens:
            return tf
        total = float(len(tokens))
        for token in tokens:
            tf[token] = tf.get(token, 0.0) + 1.0
        for token in tf:
            tf[token] = tf[token] / total
        return tf

    def calculate_tfidf_similarity(self, text1: str, text2: str) -> float:
        tokens1 = self.tokenize(text1)
        tokens2 = self.tokenize(text2)

        if not tokens1 or not tokens2:
            return 0.0

        tf1 = self.compute_tf(tokens1)
        tf2 = self.compute_tf(tokens2)

        all_words: set[str] = set(tf1.keys()).union(set(tf2.keys()))

        dot_product = sum(tf1.get(w, 0.0) * tf2.get(w, 0.0) for w in all_words)
        norm1 = math.sqrt(sum(v * v for v in tf1.values()))
        norm2 = math.sqrt(sum(v * v for v in tf2.values()))

        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0

        cosine_sim = dot_product / (norm1 * norm2)
        # Scaled to range 0-100 for natural intuitive scores
        score = min(100.0, max(0.0, float(cosine_sim * 100.0 * 1.5)))
        return round(score, 1)

    def calculate_similarity(self, text1: str, text2: str) -> float:
        if not text1 or not text2:
            return 0.0

        if self._st_model is not None:
            try:
                emb1 = self._st_model.encode(text1, convert_to_tensor=True)
                emb2 = self._st_model.encode(text2, convert_to_tensor=True)
                from sentence_transformers import util
                sim = util.cos_sim(emb1, emb2).item()
                score = min(100.0, max(0.0, float(sim * 100.0)))
                return round(score, 1)
            except Exception:
                pass

        return self.calculate_tfidf_similarity(text1, text2)

    def index_job(self, job_id: str, job_text: str, metadata: dict[str, Any] | None = None) -> None:
        self._in_memory_index[job_id] = job_text
        if self._chroma_collection is not None:
            try:
                self._chroma_collection.upsert(
                    ids=[job_id],
                    documents=[job_text],
                    metadatas=[metadata or {}]
                )
            except Exception:
                pass

    def query_similar_jobs(self, resume_text: str, top_k: int = 10) -> list[tuple[str, float]]:
        results: list[tuple[str, float]] = []
        if self._chroma_collection is not None:
            try:
                res = self._chroma_collection.query(
                    query_texts=[resume_text],
                    n_results=min(top_k, len(self._in_memory_index) or top_k)
                )
                if res and "ids" in res and res["ids"]:
                    ids = res["ids"][0]
                    distances = res.get("distances", [[]])[0]
                    for j_id, dist in zip(ids, distances, strict=False):
                        sim = max(0.0, (1.0 - float(dist)) * 100.0) if dist is not None else 50.0
                        results.append((j_id, round(sim, 1)))
                    return results
            except Exception:
                pass

        # Fallback in-memory search
        for job_id, job_text in self._in_memory_index.items():
            sim = self.calculate_similarity(resume_text, job_text)
            results.append((job_id, sim))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]


semantic_matching_engine = SemanticMatchingEngine()
