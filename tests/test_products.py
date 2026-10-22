"""Tests for the Product class."""

import pytest

from products import LimitedProduct, NonStockedProduct, Product
from promotions import PercentDiscount, SecondHalfPrice, ThirdOneFree


def test_create_valid_product() -> None:
    """Verify that a valid product is created with the expected attributes."""
    product = Product("MacBook Air M2", price=1450, quantity=100)
    assert product.name == "MacBook Air M2"
    assert product.price == 1450
    assert product.get_quantity() == 100
    assert product.is_active()


@pytest.mark.parametrize(
    ("name", "price", "quantity"),
    [
        ("MacBook Air M2", -10, 100),
        ("MacBook Air M2", 1450, -5),
        ("", 1450, 100),
    ],
    ids=["negative-price", "negative-quantity", "empty-name"],
)
def test_create_invalid_product_raises(name: str, price: float, quantity: int) -> None:
    """Verify that creating a product with invalid arguments raises an error."""
    with pytest.raises(ValueError):
        Product(name, price, quantity)


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
    """Verify that trying to set a non-zero quantity raises an error."""
    non_stocked_product = NonStockedProduct("Non-stocked", price=100)
    with pytest.raises(ValueError):
        non_stocked_product.set_quantity(1)


# Promotions


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [(1, 100), (2, 150), (3, 250), (4, 300), (5, 400)],
)
def test_second_half_price_total(quantity: int, expected: float) -> None:
    """Verify that every second item is charged at half price."""
    product = Product("Second Half Off", price=100, quantity=10)
    product.set_promotion(SecondHalfPrice("Second Half Price!"))
    assert product.total_price(quantity) == expected


@pytest.mark.parametrize(
    ("quantity", "expected"),
    [(1, 100), (2, 200), (3, 200), (5, 400), (6, 400)],
)
def test_third_one_free_total(quantity: int, expected: float) -> None:
    """Verify that every third item is free."""
    product = Product("Third One Free", price=100, quantity=10)
    product.set_promotion(ThirdOneFree("Buy 2 Get 1 Free"))
    assert product.total_price(quantity) == expected


@pytest.mark.parametrize(
    ("percent", "expected"),
    [(0, 500), (30, 350), (50, 250), (100, 0)],
)
def test_percent_discount_total(percent: float, expected: float) -> None:
    """Verify that the percentage is taken off the total price."""
    product = Product("Percent Off", price=100, quantity=10)
    product.set_promotion(PercentDiscount(f"{percent}% off", percent))
    assert product.total_price(5) == pytest.approx(expected)


@pytest.mark.parametrize("percent", [-1, 101])
def test_percent_discount_rejects_wrong_percentage(percent: float) -> None:
    """Verify that percent values outside of 0 - 100 are rejected."""
    with pytest.raises(ValueError, match="between 0 and 100"):
        PercentDiscount("Invalid", percent)


def test_product_str_and_repr() -> None:
    """Verify the string and repr output of a plain product."""
    product = Product("Phone", price=500, quantity=3)
    assert str(product) == "Phone, Price: 500, Quantity: 3"
    assert repr(product) == "Product(name='Phone', price=500, quantity=3)"


def test_product_repr_includes_promotion() -> None:
    """Verify that a product repr includes its promotion."""
    product = Product("Phone", price=500, quantity=3)
    product.set_promotion(PercentDiscount("30% off!", percent=30))
    assert repr(product) == (
        "Product(name='Phone', price=500, quantity=3, "
        "promotion=PercentDiscount(name='30% off!', percent=30))"
    )


def test_limited_product_repr() -> None:
    """Verify the repr output of a limited product."""
    product = LimitedProduct("Teddy", price=100, quantity=5, maximum=2)
    assert repr(product) == (
        "LimitedProduct(name='Teddy', price=100, quantity=5, maximum=2)"
    )


def test_non_stocked_product_repr() -> None:
    """Verify the repr output of a non-stocked product."""
    product = NonStockedProduct("License", price=125)
    assert repr(product) == "NonStockedProduct(name='License', price=125)"


def test_promotion_str_and_repr() -> None:
    """Verify the string and repr output of promotions."""
    promotion = ThirdOneFree("Third One Free!")
    assert str(promotion) == "Third One Free!"
    assert repr(promotion) == "ThirdOneFree(name='Third One Free!')"
    assert repr(SecondHalfPrice("Half")) == "SecondHalfPrice(name='Half')"
