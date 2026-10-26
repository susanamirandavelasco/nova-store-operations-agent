"""Combine independent eligibility checks without executing a return."""
from dataclasses import dataclass
from typing import Iterable

from nova.eligibility import EligibilityResult, EligibilityStatus


@dataclass(frozen=True)
class RuleEvaluation:
    rule_name: str
    result: EligibilityResult


@dataclass(frozen=True)
class CombinedEligibilityResult:
    status: EligibilityStatus
    evaluations: tuple[RuleEvaluation, ...]


def combine_eligibility_results(
    evaluations: Iterable[RuleEvaluation],
) -> CombinedEligibilityResult:
    """A confirmed failure outranks uncertainty, which outranks success.

    With no evaluated rules, there is insufficient evidence to recommend eligibility.
    """
    items = tuple(evaluations)
    if not items:
        return CombinedEligibilityResult(EligibilityStatus.NEEDS_REVIEW, items)

    statuses = {item.result.status for item in items}
    if EligibilityStatus.NOT_ELIGIBLE in statuses:
        status = EligibilityStatus.NOT_ELIGIBLE
    elif EligibilityStatus.NEEDS_REVIEW in statuses:
        status = EligibilityStatus.NEEDS_REVIEW
    else:
        status = EligibilityStatus.ELIGIBLE
    return CombinedEligibilityResult(status, items)
