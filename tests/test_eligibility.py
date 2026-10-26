"""Return-window evaluation is deterministic and independent of the LLM."""
from datetime import date

from nova.eligibility import EligibilityStatus, evaluate_return_eligibility
from nova.orders import Order


def order(purchase_date: str) -> Order:
    return Order("test", "audífonos", purchase_date)


def test_within_window():
    result = evaluate_return_eligibility(order("2026-10-01"), date(2026, 10, 20))
    assert result.status == EligibilityStatus.ELIGIBLE


def test_exactly_30_days_is_within_window():
    result = evaluate_return_eligibility(order("2026-09-26"), date(2026, 10, 26))
    assert result.status == EligibilityStatus.ELIGIBLE


def test_35_days_exceeds_window():
    result = evaluate_return_eligibility(order("2026-09-21"), date(2026, 10, 26))
    assert result.status == EligibilityStatus.NOT_ELIGIBLE


def test_future_purchase_needs_review():
    result = evaluate_return_eligibility(order("2026-11-01"), date(2026, 10, 26))
    assert result.status == EligibilityStatus.NEEDS_REVIEW


def test_invalid_purchase_date_needs_review():
    result = evaluate_return_eligibility(order("not-a-date"), date(2026, 10, 26))
    assert result.status == EligibilityStatus.NEEDS_REVIEW
