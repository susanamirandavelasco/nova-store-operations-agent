"""Tests for deterministic rule-result composition."""
from nova.eligibility import EligibilityResult, EligibilityStatus
from nova.eligibility_engine import RuleEvaluation, combine_eligibility_results

E = EligibilityStatus


def rule(name: str, status: EligibilityStatus) -> RuleEvaluation:
    return RuleEvaluation(name, EligibilityResult(status, f"{name}: {status.value}"))


def test_all_eligible():
    result = combine_eligibility_results([rule("plazo", E.ELIGIBLE), rule("categoría", E.ELIGIBLE)])
    assert result.status == E.ELIGIBLE


def test_review_overrides_eligible():
    result = combine_eligibility_results([rule("plazo", E.ELIGIBLE), rule("condición", E.NEEDS_REVIEW)])
    assert result.status == E.NEEDS_REVIEW


def test_confirmed_failure_overrides_review():
    result = combine_eligibility_results([
        rule("plazo", E.ELIGIBLE),
        rule("condición", E.NEEDS_REVIEW),
        rule("categoría", E.NOT_ELIGIBLE),
    ])
    assert result.status == E.NOT_ELIGIBLE


def test_confirmed_failure_overrides_eligible():
    result = combine_eligibility_results([rule("plazo", E.NOT_ELIGIBLE), rule("categoría", E.ELIGIBLE)])
    assert result.status == E.NOT_ELIGIBLE


def test_no_rules_needs_review():
    result = combine_eligibility_results([])
    assert result.status == E.NEEDS_REVIEW


def test_preserves_rule_explanations():
    evaluations = [rule("plazo", E.ELIGIBLE), rule("condición", E.NEEDS_REVIEW)]
    result = combine_eligibility_results(evaluations)
    assert result.evaluations == tuple(evaluations)
    assert result.evaluations[1].result.reason == "condición: NEEDS_REVIEW"
