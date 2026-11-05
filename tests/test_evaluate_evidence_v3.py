"""Offline checks: dataset integrity and exact three-way classification metrics."""
import pytest

from nova.evidence_verifier_v3 import Verdict
from nova.evaluate_evidence_v2 import CASES
from nova.evaluate_evidence_v3 import EXPECTED_VERDICTS, evaluate


def test_expected_labels_align_with_previous_support_labels():
    assert len(CASES) == len(EXPECTED_VERDICTS) == 12
    assert all(c.expected == (v is not Verdict.INSUFFICIENT)
               for c, v in zip(CASES, EXPECTED_VERDICTS))


def test_perfect_predictions():
    result = evaluate(list(EXPECTED_VERDICTS))
    assert result["exact_verdicts"] == 12
    assert result["fp"] == 0
    assert result["fn"] == 0


def test_wrong_polarity_counts_as_exact_error_even_when_supported():
    predictions = list(EXPECTED_VERDICTS)
    predictions[1] = Verdict.SUPPORTED_YES
    result = evaluate(predictions)
    assert result["exact_verdicts"] == 11
    assert result["fp"] == 0


def test_false_positive_is_detected():
    predictions = list(EXPECTED_VERDICTS)
    predictions[4] = Verdict.SUPPORTED_NO
    result = evaluate(predictions)
    assert result["fp"] == 1
    assert result["exact_verdicts"] == 11


def test_wrong_length_fails():
    with pytest.raises(ValueError):
        evaluate([Verdict.INSUFFICIENT])
