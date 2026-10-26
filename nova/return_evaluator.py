"""Evaluate a fictional return using three independent policy rules."""
from datetime import date

from nova.eligibility import evaluate_return_eligibility
from nova.eligibility_engine import (
    CombinedEligibilityResult,
    RuleEvaluation,
    combine_eligibility_results,
)
from nova.orders import Order
from nova.product_category import ProductCategory, evaluate_product_category
from nova.product_condition import ProductCondition, evaluate_product_condition


def evaluate_return(
    order: Order,
    evaluation_date: date,
    *,
    condition: ProductCondition,
    category: ProductCategory,
) -> CombinedEligibilityResult:
    """Recommend based on all three rules; never authorize or execute returns."""
    evaluations = [
        RuleEvaluation("plazo", evaluate_return_eligibility(order, evaluation_date)),
        RuleEvaluation("condición", evaluate_product_condition(condition)),
        RuleEvaluation("categoría", evaluate_product_category(category)),
    ]
    return combine_eligibility_results(evaluations)
