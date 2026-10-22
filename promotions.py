"""Define promotions that can be applied to products."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from products import Product


class Promotion(ABC):
    """Represent a promotion that affects the price of a product."""

    def __init__(self, name: str) -> None:
        """Initialize the promotion with a name."""
        self.name: str = name

    @abstractmethod
    def apply_promotion(self, product: Product, quantity: int) -> float:
        """Return the discounted total price for buying quantity of product."""


class PercentDiscount(Promotion):
    """Take a percentage of the total price."""

    def __init__(self, name: str, percent: float) -> None:
        """Initialize the promotion with a name and a percentage from 0 to 100.

        Raises
        ------
            ValueError
            If percentage is outside of 0 to 100 range.

        """
        super().__init__(name)
        if not 0 <= percent <= 100:
            raise ValueError("Percent must be between 0 and 100.")

        self.percent: float = percent

    def apply_promotion(self, product: Product, quantity: int) -> float:
        """Return the price with the percentage taken off."""
        return product.price * quantity * (1 - self.percent / 100)


class SecondHalfPrice(Promotion):
    """Sell every second item at half price."""

    def apply_promotion(self, product: Product, quantity: int) -> float:
        """Return price with every second item at half price."""
        half_price_items = quantity // 2
        return product.price * (
            quantity - half_price_items * 0.5
        )  # subtract half price of every second item


class ThirdOneFree(Promotion):
    """Buy 2 get 1 free: Every third item costs nothing."""

    def apply_promotion(self, product: Product, quantity: int) -> float:
        """Return the total price with the third item being free."""
        free_items = quantity // 3
        return product.price * (quantity - free_items)
