"""Offline evaluation bookkeeping tests."""
import pytest

from nova.evaluate_evidence_verifiers import CASES, score


def test_dataset_balanced_and_unique():
    assert len(CASES) == 20
    assert len({c.question for c in CASES}) == 20
    assert sum(c.supported for c in CASES) == 10
    assert sum(not c.supported for c in CASES) == 10


def test_perfect_predictions():
    result = score([case.supported for case in CASES])
    assert result == {"tp": 10, "fp": 0, "fn": 0, "tn": 10, "precision": 1.0, "coverage": 1.0}


def test_all_positive_predictions():
    result = score([True] * len(CASES))
    assert result["tp"] == 10
    assert result["fp"] == 10
    assert result["precision"] == 0.5


def test_mismatched_predictions_rejected():
    with pytest.raises(ValueError):
        score([True])
