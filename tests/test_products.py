"""Tests for the Product class."""

import pytest

from products import LimitedProduct, NonStockedProduct, Product


def test_create_valid_product() -> None:
    """Verify that a valid product is created with the expected attributes."""
    product = Product("MacBook Air M2", price=1450, quantity=100)
    assert product.name == "MacBook Air M2"
    assert product.price == 1450
    assert product.get_quantity() == 100
    assert product.is_active()


def test_create_product_negative_price_raises() -> None:
    """Verify that creating a product with a negative price raises an error."""
    with pytest.raises(ValueError):
        Product("MacBook Air M2", price=-10, quantity=100)


def test_create_product_negative_quantity_raises() -> None:
    """Verify that creating a product with a negative quantity raises an error."""
    with pytest.raises(ValueError):
        Product("MacBook Air M2", price=1450, quantity=-5)


def test_create_product_empty_name_raises() -> None:
    """Verify that creating a product with an empty name raises an error."""
    with pytest.raises(ValueError):
        Product("", price=1450, quantity=100)


def test_product_zero_quantity_deactivates() -> None:
    """Verify that setting a product's quantity to zero deactivates it."""
    product = Product("Pixel 7", price=500, quantity=10)
    product.set_quantity(0)
    assert not product.is_active()


def test_set_quantity_negative_raises() -> None:
    """Verify that setting a negative quantity raises an error."""
    product = Product("Pixel 7", price=500, quantity=10)
    with pytest.raises(ValueError):
        product.set_quantity(-1)


def test_product_buy_reduces_quantity_and_returns_price() -> None:
    """Verify that buying a product reduces quantity and returns price."""
    product = Product("Bose Earbuds", price=250, quantity=10)
    total = product.buy(3)
    assert total == 750
    assert product.get_quantity() == 7


def test_buy_more_than_available_raises() -> None:
    """Verify that buying more than available quantity raises an error."""
    product = Product("Bose Earbuds", price=250, quantity=5)
    with pytest.raises(ValueError):
        product.buy(10)


def test_buy_inactive_product_raises() -> None:
    """Verify that trying to buy inactive products raises an error."""
    product = Product("Bose Earbuds", price=250, quantity=0)  # auto-deactivates
    with pytest.raises(ValueError):
        product.buy(1)


def test_buy_more_than_maximum_of_limited_product_raises() -> None:
    """Verify that trying to buy more than the maximum amount raises an error."""
    limited_product = LimitedProduct("Limited", price=100.0, maximum=1)
    with pytest.raises(ValueError):
        limited_product.buy(2)

def test_non_stocked_product_quantity_not_zero_raises() -> None:
    """Verif that trying to set a non-zero quantity raises an error."""
    non_stocked_product = NonStockedProduct("Non-stocked", price=100)
    with pytest.raises(ValueError):
        non_stocked_product.set_quantity(1)
