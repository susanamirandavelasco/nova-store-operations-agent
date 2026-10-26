"""Fictional return-window evaluation; not full return authorization."""
from dataclasses import dataclass
from datetime import date
from enum import Enum

from nova.orders import Order


class EligibilityStatus(str, Enum):
    ELIGIBLE = "ELIGIBLE"
    NOT_ELIGIBLE = "NOT_ELIGIBLE"
    NEEDS_REVIEW = "NEEDS_REVIEW"


@dataclass(frozen=True)
class EligibilityResult:
    status: EligibilityStatus
    reason: str


def evaluate_return_eligibility(
    order: Order, evaluation_date: date, *, window_days: int = 30
) -> EligibilityResult:
    """Evaluate only the calendar-day return window, not other conditions."""
    if window_days < 0:
        raise ValueError("window_days must be nonnegative")
    try:
        purchase_date = date.fromisoformat(order.purchase_date)
    except (ValueError, TypeError):
        return EligibilityResult(EligibilityStatus.NEEDS_REVIEW, "Fecha de compra inválida")

    elapsed_days = (evaluation_date - purchase_date).days
    if elapsed_days < 0:
        return EligibilityResult(EligibilityStatus.NEEDS_REVIEW, "Fecha de compra futura")
    if elapsed_days > window_days:
        return EligibilityResult(
            EligibilityStatus.NOT_ELIGIBLE,
            f"Han transcurrido {elapsed_days} días; el límite es {window_days}",
        )
    return EligibilityResult(
        EligibilityStatus.ELIGIBLE,
        f"Dentro del plazo: {elapsed_days} de {window_days} días",
    )
