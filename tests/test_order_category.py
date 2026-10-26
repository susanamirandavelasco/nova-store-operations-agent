"""Order-category data should be structured and default to unknown."""
from nova.orders import FakeOrderRepository, Order
from nova.product_category import ProductCategory


def test_headphones_have_electronics_category():
    order = FakeOrderRepository().get("83921")
    assert order is not None
    assert order.category == ProductCategory.ELECTRONICS


def test_television_has_electronics_category():
    order = FakeOrderRepository().get("65042")
    assert order is not None
    assert order.category == ProductCategory.ELECTRONICS


def test_legacy_order_without_category_defaults_to_unknown():
    order = Order("12345", "producto", "2026-10-20")
    assert order.category == ProductCategory.UNKNOWN
