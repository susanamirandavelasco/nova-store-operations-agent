"""Product-condition rule tests."""
import pytest

from nova.eligibility import EligibilityResult, EligibilityStatus
from nova.eligibility_engine import RuleEvaluation, combine_eligibility_results
from nova.product_condition import ProductCondition, evaluate_product_condition

E = EligibilityStatus


@pytest.mark.parametrize(
    ("condition", "expected"),
    [
        (ProductCondition.SEALED, E.ELIGIBLE),
        (ProductCondition.OPENED, E.NEEDS_REVIEW),
        (ProductCondition.DAMAGED, E.NEEDS_REVIEW),
        (ProductCondition.UNKNOWN, E.NEEDS_REVIEW),
    ],
)
def test_product_condition(condition, expected):
    result = evaluate_product_condition(condition)
    assert result.status == expected
    assert result.reason


def test_unknown_condition_combines_to_review():
    result = combine_eligibility_results([
        RuleEvaluation("plazo", EligibilityResult(E.ELIGIBLE, "Dentro del plazo")),
        RuleEvaluation("condición", evaluate_product_condition(ProductCondition.UNKNOWN)),
    ])
    assert result.status == E.NEEDS_REVIEW


def test_invalid_condition_is_not_silently_accepted():
    with pytest.raises(ValueError):
        evaluate_product_condition("UNEXPECTED")
