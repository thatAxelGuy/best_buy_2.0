"""Tests for the Store class."""

import pytest

from products import Product
from store import Store


@pytest.fixture
def sample_store() -> Store:
    """Create a store containing sample products for testing."""
    products = [
        Product("MacBook Air M2", price=1450, quantity=100),
        Product("Bose Earbuds", price=250, quantity=500),
    ]
    return Store(products)


def test_get_total_quantity(sample_store: Store) -> None:
    """Verify that the store reports the total quantity of all products."""
    assert sample_store.get_total_quantity() == 600


def test_get_all_products_excludes_inactive(sample_store: Store) -> None:
    """Verify that inactive products are excluded from the product list."""
    products = sample_store.get_all_products()
    products[0].set_quantity(0)  # deactivates it
    active = sample_store.get_all_products()
    assert products[0] not in active


def test_add_product(sample_store: Store) -> None:
    """Verify that a product can be added to the store."""
    pixel = Product("Google Pixel 7", price=500, quantity=250)
    sample_store.add_product(pixel)
    assert pixel in sample_store.get_all_products()


def test_remove_product(sample_store: Store) -> None:
    """Verify that a product can be removed from the store."""
    mac = sample_store.products[0]
    sample_store.remove_product(mac)
    assert mac not in sample_store.get_all_products()


def test_order_success(sample_store: Store) -> None:
    """Verify that ordering products succeeds and updates stock quantities."""
    mac, bose = sample_store.products
    total = sample_store.order([(mac, 1), (bose, 2)])
    assert total == 1450 + 2 * 250
    assert mac.get_quantity() == 99
    assert bose.get_quantity() == 498


def test_order_rejects_repeated_product_exceeding_stock(sample_store: Store) -> None:
    """Reject an order that requests the same product beyond available stock."""
    mac = sample_store.products[0]  # 100 in stock
    with pytest.raises(ValueError):
        sample_store.order([(mac, 80), (mac, 80)])
    # nothing should have been deducted since validation ran before purchase
    assert mac.get_quantity() == 100


def test_order_inactive_product_raises(sample_store: Store) -> None:
    """Verify that ordering an inactive product raises a ValueError."""
    mac = sample_store.products[0]
    mac.deactivate()
    with pytest.raises(ValueError):
        sample_store.order([(mac, 1)])
