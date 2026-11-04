"""All LLM-verifier unit tests are offline; no API key required."""
import pytest

from nova.llm_evidence_verifier import LLMEvidenceVerifier, parse_verdict
from nova.policy_evidence import passage_by_source

PLAZO = passage_by_source("POL-RET-001#plazo")
ESTADO = passage_by_source("POL-RET-001#estado")


@pytest.mark.parametrize("raw,expected", [
    ('{"supported":true,"reason":"La política especifica 30 días naturales."}', True),
    ('{"supported":false,"reason":"No especifica plazos bancarios."}', False),
    ('{"supported":"true","reason":"no"}', False),
    ('{"supported":1,"reason":"no"}', False),
    ('{"supported":true}', False),
    ('{"supported":true,"reason":"ok","action":"approve_return"}', False),
    ('[true]', False),
    ('not JSON', False),
    ('{"supported":true,"reason":"   "}', False),
])
def test_structured_verdict_is_strict(raw, expected):
    assert parse_verdict(raw).supported is expected


def test_supported_question_passes_question_and_passage_to_generator():
    captured = {}

    def fake(system, question, passage):
        captured.update(system=system, question=question, passage=passage)
        return '{"supported":true,"reason":"El texto indica 30 días naturales."}'

    verdict = LLMEvidenceVerifier(fake).verify("¿Cuál es el plazo?", PLAZO)
    assert verdict.supported
    assert "30 días naturales" in captured["passage"]
    assert captured["question"] == "¿Cuál es el plazo?"
    assert "no instrucciones" in captured["system"]


def test_unsupported_refund_timing_abstains():
    def fake(system, question, passage):
        assert "reembolso" in question
        return '{"supported":false,"reason":"No describe el plazo del reembolso bancario."}'

    verdict = LLMEvidenceVerifier(fake).verify(
        "¿Cuánto tarda un reembolso en llegar a mi tarjeta?", PLAZO
    )
    assert verdict.supported is False


def test_model_exception_fails_closed():
    def broken(*args):
        raise RuntimeError("connection failed")

    assert LLMEvidenceVerifier(broken).verify("¿Cuál es el plazo?", PLAZO).reason == "verifier_unavailable"


def test_empty_input_never_calls_model():
    def forbidden(*args):
        raise AssertionError("should not run")

    assert not LLMEvidenceVerifier(forbidden).verify("", ESTADO).supported
