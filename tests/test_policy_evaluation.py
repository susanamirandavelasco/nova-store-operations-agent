"""Offline evaluation tests; never call the embeddings API."""
from nova.evaluate_policy_retrieval import CASES, ESTADO, PLAZO, choose, metrics


def test_dataset_has_unique_questions_and_expected_balance():
    assert len(CASES) == 25
    assert len({c.question for c in CASES}) == 25
    assert sum(c.expected == PLAZO for c in CASES) == 10
    assert sum(c.expected == ESTADO for c in CASES) == 8
    assert sum(c.expected is None for c in CASES) == 7


def test_threshold_changes_abstention():
    assert choose([0.54, 0.22], 0.50) == PLAZO
    assert choose([0.54, 0.22], 0.60) is None


def test_tie_abstains():
    assert choose([0.54, 0.53], 0.50) is None


def test_metrics_distinguish_wrong_answer_and_abstention():
    predictions = [c.expected for c in CASES]
    predictions[0] = ESTADO
    predictions[1] = None
    predictions[-1] = PLAZO
    result = metrics(predictions)
    assert result == {
        "correct": 16,
        "wrong_source": 1,
        "missed": 1,
        "false_positive": 1,
        "correct_abstain": 6,
    }
