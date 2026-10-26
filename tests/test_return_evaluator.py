"""Integration tests for the three-rule return evaluator."""
from datetime import date

from nova.eligibility import EligibilityStatus
from nova.orders import Order
from nova.product_category import ProductCategory
from nova.product_condition import ProductCondition
from nova.return_evaluator import evaluate_return

E = EligibilityStatus


def make_order(purchase_date: str) -> Order:
    return Order("83921", "audífonos", purchase_date)


def test_all_rules_pass():
    result = evaluate_return(
        make_order("2026-10-16"), date(2026, 10, 26),
        condition=ProductCondition.SEALED, category=ProductCategory.ELECTRONICS,
    )
    assert result.status == E.ELIGIBLE
    assert [item.rule_name for item in result.evaluations] == ["plazo", "condición", "categoría"]


def test_unknown_condition_requires_review():
    result = evaluate_return(
        make_order("2026-10-16"), date(2026, 10, 26),
        condition=ProductCondition.UNKNOWN, category=ProductCategory.ELECTRONICS,
    )
    assert result.status == E.NEEDS_REVIEW


def test_expired_window_overrides_unknown_condition():
    result = evaluate_return(
        make_order("2026-09-01"), date(2026, 10, 26),
        condition=ProductCondition.UNKNOWN, category=ProductCategory.ELECTRONICS,
    )
    assert result.status == E.NOT_ELIGIBLE


def test_excluded_category_overrides_unknown_condition():
    result = evaluate_return(
        make_order("2026-10-16"), date(2026, 10, 26),
        condition=ProductCondition.UNKNOWN, category=ProductCategory.PERSONAL_CARE,
    )
    assert result.status == E.NOT_ELIGIBLE


def test_unknown_category_requires_review():
    result = evaluate_return(
        make_order("2026-10-16"), date(2026, 10, 26),
        condition=ProductCondition.SEALED, category=ProductCategory.UNKNOWN,
    )
    assert result.status == E.NEEDS_REVIEW


def test_explanations_are_preserved():
    result = evaluate_return(
        make_order("2026-10-16"), date(2026, 10, 26),
        condition=ProductCondition.SEALED, category=ProductCategory.ELECTRONICS,
    )
    assert len(result.evaluations) == 3
    assert all(item.result.reason for item in result.evaluations)
