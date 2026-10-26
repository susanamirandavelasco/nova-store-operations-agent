"""Category rule tests and integration with rule composition."""
import pytest

from nova.eligibility import EligibilityResult, EligibilityStatus
from nova.eligibility_engine import RuleEvaluation, combine_eligibility_results
from nova.product_category import ProductCategory, evaluate_product_category

E = EligibilityStatus


@pytest.mark.parametrize(
    ("category", "expected"),
    [
        (ProductCategory.ELECTRONICS, E.ELIGIBLE),
        (ProductCategory.PERSONAL_CARE, E.NOT_ELIGIBLE),
        (ProductCategory.UNKNOWN, E.NEEDS_REVIEW),
    ],
)
def test_product_category(category, expected):
    result = evaluate_product_category(category)
    assert result.status == expected
    assert result.reason


def test_excluded_category_overrides_uncertain_condition():
    result = combine_eligibility_results([
        RuleEvaluation("plazo", EligibilityResult(E.ELIGIBLE, "Dentro del plazo")),
        RuleEvaluation("condición", EligibilityResult(E.NEEDS_REVIEW, "Condición desconocida")),
        RuleEvaluation("categoría", evaluate_product_category(ProductCategory.PERSONAL_CARE)),
    ])
    assert result.status == E.NOT_ELIGIBLE
    assert len(result.evaluations) == 3


def test_unknown_category_does_not_imply_eligible():
    result = combine_eligibility_results([
        RuleEvaluation("plazo", EligibilityResult(E.ELIGIBLE, "Dentro del plazo")),
        RuleEvaluation("categoría", evaluate_product_category(ProductCategory.UNKNOWN)),
    ])
    assert result.status == E.NEEDS_REVIEW


def test_unrecognized_category_is_rejected():
    with pytest.raises(ValueError):
        evaluate_product_category("UNRECOGNIZED")
