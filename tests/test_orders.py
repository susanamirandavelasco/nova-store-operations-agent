from nova.orders import (
    FakeOrderRepository, VerificationStatus, verify_order,
)


def test_existing_order_without_details_is_not_verified():
    result = verify_order(FakeOrderRepository(), "83921")
    assert result.status == VerificationStatus.NEED_MORE_DETAILS
    assert result.order is None


def test_matching_product_verifies_order():
    result = verify_order(FakeOrderRepository(), "83921", product="AUDÍFONOS")
    assert result.status == VerificationStatus.MATCH
    assert result.order is not None
    assert result.order.order_id == "83921"


def test_matching_date_verifies_order():
    result = verify_order(FakeOrderRepository(), "83921", purchase_date="2026-10-18")
    assert result.status == VerificationStatus.MATCH


def test_mismatch_does_not_expose_order():
    result = verify_order(FakeOrderRepository(), "83921", product="televisor")
    assert result.status == VerificationStatus.MISMATCH
    assert result.order is None


def test_nonexistent_order():
    result = verify_order(FakeOrderRepository(), "00000", product="audífonos")
    assert result.status == VerificationStatus.NOT_FOUND


def test_non_numeric_candidate():
    result = verify_order(FakeOrderRepository(), "83921x", product="audífonos")
    assert result.status == VerificationStatus.NOT_FOUND


def test_one_matching_detail_does_not_override_conflicting_detail():
    result = verify_order(
        FakeOrderRepository(), "83921",
        product="audífonos", purchase_date="2026-10-10",
    )
    assert result.status == VerificationStatus.MISMATCH
