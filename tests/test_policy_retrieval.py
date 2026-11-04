"""Tests for the intentionally limited policy retrieval baseline."""
from nova.policy_retrieval import PolicyRetriever


def test_return_deadline_has_citable_source():
    answer = PolicyRetriever().answer("¿Cuál es el plazo en días para una devolución?")
    assert "30 días" in answer.text
    assert answer.source_id == "POL-RET-001#plazo"
    assert answer.title is not None


def test_opened_product_policy_is_not_an_eligibility_decision():
    answer = PolicyRetriever().answer("¿Qué pasa con un producto abierto?")
    assert "revisión humana" in answer.text
    assert answer.source_id == "POL-RET-001#estado"
    assert "ELIGIBLE" not in answer.text


def test_unsupported_question_abstains_without_fake_citation():
    answer = PolicyRetriever().answer("¿Cuál es el horario de la sucursal?")
    assert "No encontré información suficiente" in answer.text
    assert answer.source_id is None


def test_empty_question_abstains():
    answer = PolicyRetriever().answer("  ")
    assert answer.source_id is None


def test_ambiguous_question_asks_for_clarification():
    answer = PolicyRetriever().answer("¿Qué dice la política sobre plazo y estado?")
    assert "precisar" in answer.text
    assert answer.source_id is None
