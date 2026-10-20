"""Fictional order lookup and deterministic corroboration.

No customer PII or live integrations. Verification is not authorization.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Protocol


@dataclass(frozen=True)
class Order:
    order_id: str
    product: str
    purchase_date: str  # ISO 8601 YYYY-MM-DD; fictitious dataset


class OrderRepository(Protocol):
    def get(self, order_id: str) -> Order | None: ...


class FakeOrderRepository:
    """Local test data; replace with a real tool adapter in a later session."""

    def __init__(self) -> None:
        self.orders = {
            "83921": Order("83921", "audífonos", "2026-10-18"),
            "65042": Order("65042", "televisor", "2026-10-10"),
        }

    def get(self, order_id: str) -> Order | None:
        return self.orders.get(order_id)


class VerificationStatus(str, Enum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"
    NOT_FOUND = "NOT_FOUND"
    NEED_MORE_DETAILS = "NEED_MORE_DETAILS"


@dataclass(frozen=True)
class VerificationResult:
    status: VerificationStatus
    order: Order | None = None


def verify_order(
    repository: OrderRepository,
    candidate_order_id: str,
    *,
    product: str | None = None,
    purchase_date: str | None = None,
) -> VerificationResult:
    """Corroborate a candidate against an order record, never infer a match."""
    if not candidate_order_id.isascii() or not candidate_order_id.isdigit():
        return VerificationResult(VerificationStatus.NOT_FOUND)

    order = repository.get(candidate_order_id)
    if order is None:
        return VerificationResult(VerificationStatus.NOT_FOUND)

    if product is None and purchase_date is None:
        return VerificationResult(VerificationStatus.NEED_MORE_DETAILS)

    if product is not None and order.product.casefold().strip() != product.casefold().strip():
        return VerificationResult(VerificationStatus.MISMATCH)
    if purchase_date is not None and order.purchase_date != purchase_date:
        return VerificationResult(VerificationStatus.MISMATCH)

    return VerificationResult(VerificationStatus.MATCH, order)
