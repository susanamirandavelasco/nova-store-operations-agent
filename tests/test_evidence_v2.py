"""Offline contract tests for evidence-verifier prompt versioning."""
import pytest

from nova.evaluate_evidence_v2 import CASES, metrics
from nova.llm_evidence_verifier import (
    LLMEvidenceVerifier, SYSTEM_PROMPT_V1, SYSTEM_PROMPT_V2,
)
from nova.policy_evidence import passage_by_source


def test_new_cases_are_unique_and_balanced_enough():
    assert len(CASES) == 12
    assert len({case.question for case in CASES}) == 12
    assert sum(case.expected for case in CASES) == 7


def test_metrics_perfect():
    assert metrics([case.expected for case in CASES]) == {
        "tp": 7, "fp": 0, "fn": 0, "tn": 5, "precision": 1.0, "recall": 1.0,
    }


def test_metrics_reject_missing_predictions():
    with pytest.raises(ValueError):
        metrics([True])


def test_prompt_versions_explicitly_define_yes_no_and_absence():
    assert SYSTEM_PROMPT_V1 != SYSTEM_PROMPT_V2
    assert "supported=true" in SYSTEM_PROMPT_V2
    assert "supported=false" in SYSTEM_PROMPT_V2
    assert "30 días naturales" in SYSTEM_PROMPT_V2


def test_verifier_defaults_to_v2_and_can_replay_v1():
    seen = []
    def fake(system, question, passage):
        seen.append(system)
        return '{"supported":false,"reason":"test"}'
    passage = passage_by_source("POL-RET-001#plazo")
    LLMEvidenceVerifier(fake).verify("¿Cuántos días?", passage)
    LLMEvidenceVerifier(fake, prompt=SYSTEM_PROMPT_V1).verify("¿Cuántos días?", passage)
    assert seen == [SYSTEM_PROMPT_V2, SYSTEM_PROMPT_V1]
