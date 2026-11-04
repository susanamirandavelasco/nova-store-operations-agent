"""Optional semantic policy retrieval; no LLM-generated answers or eligibility decisions."""
from math import isfinite, sqrt
from typing import Protocol

from nova.policy_retrieval import POLICIES, PolicyAnswer, PolicyPassage


class Embedder(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...


def cosine_similarity(left: list[float], right: list[float]) -> float:
    """Reject invalid vectors instead of treating them as meaningful evidence."""
    if not left or len(left) != len(right):
        raise ValueError("Embedding vectors must have equal nonzero dimensions")
    if not all(isfinite(v) for v in left + right):
        raise ValueError("Embedding vectors must be finite")
    left_norm = sqrt(sum(v * v for v in left))
    right_norm = sqrt(sum(v * v for v in right))
    if left_norm == 0 or right_norm == 0:
        raise ValueError("Zero embedding vectors are invalid")
    return sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)


class SemanticPolicyRetriever:
    """Small in-memory index; similarity is not proof of factual relevance."""

    def __init__(
        self,
        embedder: Embedder,
        passages: tuple[PolicyPassage, ...] = POLICIES,
        *,
        min_similarity: float = 0.75,
        ambiguity_margin: float = 0.03,
    ) -> None:
        if not 0 <= min_similarity <= 1 or not 0 <= ambiguity_margin <= 1:
            raise ValueError("Thresholds must be between zero and one")
        self.embedder = embedder
        self.passages = passages
        self.min_similarity = min_similarity
        self.ambiguity_margin = ambiguity_margin
        self.vectors = embedder.embed([p.text for p in passages]) if passages else []
        if len(self.vectors) != len(passages):
            raise ValueError("Embedder returned an unexpected number of vectors")
        if self.vectors:
            dimensions = len(self.vectors[0])
            for vector in self.vectors:
                cosine_similarity(vector, vector)
                if len(vector) != dimensions:
                    raise ValueError("Policy embedding dimensions differ")

    def answer(self, question: str) -> PolicyAnswer:
        fallback = PolicyAnswer("No encontré información suficiente en las políticas disponibles.")
        if not question.strip() or not self.passages:
            return fallback
        query_vectors = self.embedder.embed([question])
        if len(query_vectors) != 1:
            raise ValueError("Embedder must return exactly one query vector")
        scores = sorted(
            ((cosine_similarity(query_vectors[0], vector), passage)
             for passage, vector in zip(self.passages, self.vectors)),
            key=lambda pair: pair[0],
            reverse=True,
        )
        best_score, best_passage = scores[0]
        if best_score < self.min_similarity:
            return fallback
        if len(scores) > 1 and best_score - scores[1][0] < self.ambiguity_margin:
            return PolicyAnswer(
                "La consulta coincide con varias políticas. ¿Puedes precisar tu pregunta?"
            )
        return PolicyAnswer(best_passage.text, best_passage.source_id, best_passage.title)


class OpenAIEmbedder:
    """Optional paid adapter; requires openai package and OPENAI_API_KEY."""

    def __init__(self, model: str = "text-embedding-3-small") -> None:
        self.model = model

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        from openai import OpenAI
        result = OpenAI().embeddings.create(model=self.model, input=texts)
        if len(result.data) != len(texts):
            raise ValueError("Embedding API returned an unexpected result count")
        ordered = sorted(result.data, key=lambda item: item.index)
        if [item.index for item in ordered] != list(range(len(texts))):
            raise ValueError("Embedding API indices are incomplete")
        return [item.embedding for item in ordered]
