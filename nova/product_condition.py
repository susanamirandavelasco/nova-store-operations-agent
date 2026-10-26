"""Deterministic evaluation of a fictional product-condition policy."""
from enum import Enum

from nova.eligibility import EligibilityResult, EligibilityStatus


class ProductCondition(str, Enum):
    SEALED = "SEALED"
    OPENED = "OPENED"
    DAMAGED = "DAMAGED"
    UNKNOWN = "UNKNOWN"


def evaluate_product_condition(condition: ProductCondition) -> EligibilityResult:
    """A sealed product passes this rule; other conditions need policy review.

    This check alone never authorizes a return.
    """
    if condition == ProductCondition.SEALED:
        return EligibilityResult(
            EligibilityStatus.ELIGIBLE,
            "Producto sellado: cumple la condición del piloto",
        )
    if condition == ProductCondition.OPENED:
        return EligibilityResult(
            EligibilityStatus.NEEDS_REVIEW,
            "Producto abierto: falta una política específica",
        )
    if condition == ProductCondition.DAMAGED:
        return EligibilityResult(
            EligibilityStatus.NEEDS_REVIEW,
            "Producto dañado: requiere evaluación según política",
        )
    if condition == ProductCondition.UNKNOWN:
        return EligibilityResult(
            EligibilityStatus.NEEDS_REVIEW,
            "Condición del producto desconocida",
        )
    raise ValueError("Condición del producto no reconocida")
