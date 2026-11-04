"""Deterministic embedding fixtures; no network calls or OpenAI charges."""
import pytest

from nova.semantic_policy_retrieval import SemanticPolicyRetriever, cosine_similarity


class FakeEmbedder:
    def embed(self, texts):
        vectors = {
            "Las devoluciones ordinarias se solicitan dentro de los 30 días naturales posteriores a la compra.": [1.0, 0.0],
            "El estado del producto debe verificarse. Un artículo abierto puede requerir revisión humana; no se garantiza su aceptación.": [0.0, 1.0],
            "¿Puedo regresar algo que compré hace tres semanas?": [0.98, 0.02],
            "¿Qué pasa si ya abrí la caja?": [0.02, 0.98],
            "¿A qué hora cierra la tienda?": [-1.0, 0.0],
            "Pregunta ambigua": [1.0, 1.0],
        }
        return [vectors[text] for text in texts]


def test_semantic_query_without_lexical_keywords_finds_deadline():
    answer = SemanticPolicyRetriever(FakeEmbedder()).answer(
        "¿Puedo regresar algo que compré hace tres semanas?"
    )
    assert "30 días" in answer.text
    assert answer.source_id == "POL-RET-001#plazo"


def test_opened_box_matches_condition_policy():
    answer = SemanticPolicyRetriever(FakeEmbedder()).answer("¿Qué pasa si ya abrí la caja?")
    assert answer.source_id == "POL-RET-001#estado"


def test_unrelated_query_abstains_without_citation():
    answer = SemanticPolicyRetriever(FakeEmbedder()).answer("¿A qué hora cierra la tienda?")
    assert answer.source_id is None


def test_near_tie_asks_for_clarification():
    # 0.707 similarity to both passages is below the default 0.75 cutoff.
    # Lower the cutoff only for this fixture to isolate the tie-handling rule.
    answer = SemanticPolicyRetriever(FakeEmbedder(), min_similarity=0.70).answer("Pregunta ambigua")
    assert "precisar" in answer.text
    assert answer.source_id is None


@pytest.mark.parametrize("left,right", [
    ([], []), ([0.0, 0.0], [1.0, 0.0]),
    ([1.0], [1.0, 0.0]), ([float("nan")], [1.0]),
])
def test_invalid_vectors_fail_closed(left, right):
    with pytest.raises(ValueError):
        cosine_similarity(left, right)


def test_cosine_similarity_of_same_direction_is_one():
    assert cosine_similarity([1.0, 0.0], [2.0, 0.0]) == pytest.approx(1.0)


def test_blank_question_does_not_call_embedding_model():
    class NoQueryEmbedder(FakeEmbedder):
        def embed(self, texts):
            assert texts != [""]
            return super().embed(texts)
    assert SemanticPolicyRetriever(NoQueryEmbedder()).answer("").source_id is None
