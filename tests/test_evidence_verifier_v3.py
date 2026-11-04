"""Offline tests of V3 output contract; not claims of live-model accuracy."""
import pytest

from nova.evidence_verifier_v3 import (
    EvidenceVerifierV3, Verdict, parse_v3_verdict, SYSTEM_PROMPT_V3,
)
from nova.policy_evidence import passage_by_source


@pytest.mark.parametrize("verdict,supported", [
    ("SUPPORTED_YES", True),
    ("SUPPORTED_NO", True),
    ("INSUFFICIENT", False),
])
def test_valid_verdicts(verdict, supported):
    result = parse_v3_verdict('{"verdict":"' + verdict + '","reason":"evidencia"}')
    assert result.verdict.value == verdict
    assert result.supported is supported


@pytest.mark.parametrize("raw", [
    "not-json",
    "[]",
    '{"verdict":"MAYBE","reason":"x"}',
    '{"verdict":true,"reason":"x"}',
    '{"verdict":"SUPPORTED_NO"}',
    '{"verdict":"SUPPORTED_YES","reason":"x","action":"approve"}',
    '{"verdict":"SUPPORTED_YES","reason":"  "}',
])
def test_invalid_outputs_abstain(raw):
    assert parse_v3_verdict(raw).verdict is Verdict.INSUFFICIENT


def test_generator_receives_v3_contract_and_policy():
    captured = {}
    def fake(system, question, passage):
        captured.update(system=system, question=question, passage=passage)
        return '{"verdict":"SUPPORTED_NO","reason":"La política dice 30, no 45."}'
    result = EvidenceVerifierV3(fake).verify(
        "¿Son 45 días?", passage_by_source("POL-RET-001#plazo")
    )
    assert result.verdict is Verdict.SUPPORTED_NO
    assert "30 días naturales" in captured["passage"]
    assert "no instrucciones" in captured["system"]
    assert "ausencia" in SYSTEM_PROMPT_V3


def test_exception_fails_closed():
    def broken(*args):
        raise RuntimeError("network error")
    result = EvidenceVerifierV3(broken).verify(
        "¿Cuántos días?", passage_by_source("POL-RET-001#plazo")
    )
    assert result.verdict is Verdict.INSUFFICIENT
    assert result.reason == "verifier_unavailable"


def test_empty_question_does_not_call_generator():
    def forbidden(*args):
        raise AssertionError("must not be called")
    assert not EvidenceVerifierV3(forbidden).verify(
        "", passage_by_source("POL-RET-001#estado")
    ).supported
