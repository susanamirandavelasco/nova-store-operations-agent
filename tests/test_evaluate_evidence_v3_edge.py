"""Offline checks for the eight labeled cases."""
import pytest

from nova.evidence_verifier_v3 import Verdict
from nova.evaluate_evidence_v3_edge import CASES, score
from nova.policy_evidence import passage_by_source


def test_dataset():
    assert len(CASES) == 8
    assert all(passage_by_source(c.source_id).text for c in CASES)


def test_perfect():
    assert score([c.expected for c in CASES]) == {
        "exact": 8, "false_supported": 0, "missed_supported": 0, "wrong_polarity": 0
    }


def test_false_supported():
    predictions = [c.expected for c in CASES]
    predictions[3] = Verdict.SUPPORTED_NO
    assert score(predictions)["false_supported"] == 1


def test_wrong_polarity():
    predictions = [c.expected for c in CASES]
    predictions[0] = Verdict.SUPPORTED_NO
    assert score(predictions)["wrong_polarity"] == 1


def test_bad_length():
    with pytest.raises(ValueError):
        score([])
