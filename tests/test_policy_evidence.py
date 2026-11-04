"""Evidence verification remains offline and independent of the chat workflow."""
import pytest

from nova.policy_evidence import assess_evidence, answer_if_supported, passage_by_source
from nova.policy_retrieval import PolicyPassage

PLAZO = passage_by_source("POL-RET-001#plazo")
ESTADO = passage_by_source("POL-RET-001#estado")


@pytest.mark.parametrize("question", [
    "¿Cuál es el plazo de devolución?",
    "¿Puedo regresar algo que compré hace tres semanas?",
    "¿El conteo de días es natural o hábil?",
])
def test_deadline_evidence_is_supported(question):
    assert answer_if_supported(question, PLAZO).source_id == PLAZO.source_id


@pytest.mark.parametrize("question", [
    "¿Qué sucede si abrí la caja?",
    "¿Un artículo usado necesita revisión?",
    "Si rompí el sello, ¿la devolución está garantizada?",
])
def test_condition_evidence_is_supported(question):
    assert answer_if_supported(question, ESTADO).source_id == ESTADO.source_id


@pytest.mark.parametrize("question,passage", [
    ("¿Cuánto tarda un reembolso en llegar a mi tarjeta?", PLAZO),
    ("¿Cuál es el horario de la sucursal?", PLAZO),
    ("¿Cuánto cuesta el envío?", PLAZO),
    ("¿Qué garantía da el fabricante?", ESTADO),
    ("¿Cuál es el plazo de devolución?", ESTADO),
    ("¿Qué pasa si abrí la caja?", PLAZO),
    ("", PLAZO),
])
def test_unsupported_question_abstains_without_source(question, passage):
    answer = answer_if_supported(question, passage)
    assert answer.source_id is None
    assert "evidencia suficiente" in answer.text


def test_cannot_claim_evidence_when_policy_fact_is_missing():
    altered = PolicyPassage(PLAZO.source_id, PLAZO.title, "Texto sin el plazo.", PLAZO.keywords)
    assert not assess_evidence("¿Cuál es el plazo de devolución?", altered).supported
