"""Fictional NovaRetail product-category return rule."""
from enum import Enum

from nova.eligibility import EligibilityResult, EligibilityStatus


class ProductCategory(str, Enum):
    ELECTRONICS = "ELECTRONICS"
    PERSONAL_CARE = "PERSONAL_CARE"
    UNKNOWN = "UNKNOWN"


def evaluate_product_category(category: ProductCategory) -> EligibilityResult:
    """Evaluate only the category policy, not full return eligibility."""
    if category == ProductCategory.ELECTRONICS:
        return EligibilityResult(
            EligibilityStatus.ELIGIBLE,
            "La categoría electrónica admite devoluciones en el piloto",
        )
    if category == ProductCategory.PERSONAL_CARE:
        return EligibilityResult(
            EligibilityStatus.NOT_ELIGIBLE,
            "La categoría cuidado personal está excluida por la política del piloto",
        )
    if category == ProductCategory.UNKNOWN:
        return EligibilityResult(
            EligibilityStatus.NEEDS_REVIEW,
            "Categoría desconocida: requiere clasificación o revisión",
        )
    raise ValueError("Categoría de producto no reconocida")
