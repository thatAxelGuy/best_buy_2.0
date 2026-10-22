"""Define products and their inventory behavior."""

from promotions import Promotion


class Product:
    """Represent a product that can be purchased from inventory."""

    def __init__(
        self, name: str = "Product Name", price: float = 0.0, quantity: int = 0
    ) -> None:
        """Initialize a product with a name, price, and quantity.

        Raises
        ------
            ValueError
            If price or quantity is negative, or name is empty.

        """
        if not name:
            raise ValueError("Product name cannot be empty.")
        if price < 0:
            raise ValueError("Price cannot be negative.")
        if quantity < 0:
            raise ValueError("Quantity cannot be negative.")

        self.name: str = name
        self.price: float = price
        self._quantity: int = quantity
        self._active: bool = True
        self._promotion: Promotion | None = None

    def get_promotion(self) -> Promotion | None:
        """Return the products promotion or None if it has none."""
        return self._promotion

    def set_promotion(self, promotion: Promotion | None) -> None:
        """Set the products promotion. Pass None to remove it."""
        self._promotion = promotion

    def _promotion_label(self) -> str:
        """Return text describing the current promotion, or an empty string."""
        if self._promotion is None:
            return ""
        return f"\nPromotion: {self._promotion.name}"

    def get_quantity(self) -> int:
        """Return the product quantity."""
        return self._quantity

    def set_quantity(self, quantity: int) -> None:
        """Set the product quantity.

        If quantity reaches 0, deactivates the product.
        """
        if quantity < 0:
            raise ValueError("Quantity can't be negative")

        self._quantity = quantity
        if self._quantity == 0:
            self.deactivate()

    def is_active(self) -> bool:
        """Return whether the product is active."""
        return self._active

    def activate(self) -> None:
        """Activate the product."""
        self._active = True

    def deactivate(self) -> None:
        """Deactivate the product."""
        self._active = False

    def __str__(self) -> str:
        """Return a string that represents the product."""
        return (
            f"{self.name}, Price: {self.price}, "
            f"Quantity: {self.get_quantity()}"
            f"{self._promotion_label()}"
        )

    def _promotion_repr(self) -> str:
        """Return repr text for the current promotion, or an empty string."""
        if self._promotion is None:
            return ""
        return f", promotion={self._promotion!r}"

    def __repr__(self) -> str:
        """Return an unambiguous string that represents the product."""
        return (
            f"{type(self).__name__}(name={self.name!r}, price={self.price!r}, "
            f"quantity={self.get_quantity()!r}{self._promotion_repr()})"
        )

    def total_price(self, quantity: int) -> float:
        """Return the price of quantity of items."""
        if self._promotion is None:
            return self.price * quantity
        return self._promotion.apply_promotion(self, quantity)

    def buy(self, quantity: int) -> float:
        """Buy a given quantity of the product.

        * Returns the total price (float) of the purchase.
        * Updates the quantity of the product.
        * Raises an exception if amount bought would exceed
          available quantity or product is inactive.
        """
        if not self.is_active():
            raise ValueError("Product is inactive.")

        if quantity > self.get_quantity():
            raise ValueError("Not enough quantity available.")

        self.set_quantity(self.get_quantity() - quantity)
        return self.total_price(quantity)


class LimitedProduct(Product):
    """Represent a product that can only be bought up to a maximum."""

    def __init__(
        self,
        name: str = "Product Name",
        price: float | int = 0.0,
        quantity: int = 0,
        maximum: int = 1,
    ) -> None:
        """Initialize a limted product with a per purchase maximum.

        Raises
        ------
            ValueError
            If maximum is less than 1, or the base validation fails.

        """
        super().__init__(name, price, quantity)
        if maximum < 1:
            raise ValueError("Maximum per purchase must be at least 1.")

        self.maximum: int = maximum

    def __str__(self) -> str:
        """Return a string that represents the product."""
        return (
            f"{self.name}, Price: {self.price}, "
            f"Quantity: {self.get_quantity()}, "
            f"Limited to {self.maximum} per purchase"
            f"{self._promotion_label()}"
        )

    def __repr__(self) -> str:
        """Return an unambiguous string that represents the product."""
        return (
            f"{type(self).__name__}(name={self.name!r}, price={self.price!r}, "
            f"quantity={self.get_quantity()!r}, maximum={self.maximum!r}"
            f"{self._promotion_repr()})"
        )

    def buy(self, quantity: int) -> float:
        """Buy a quantity, enforcing the per purchase maximum.

        Raises
        ------
            ValueError
            If purchase quantity exceeds limited product maximum.

        """
        if quantity > self.maximum:
            raise ValueError(f"Only {self.maximum} per purchase allowed.")

        return super().buy(quantity)


class NonStockedProduct(Product):
    """Represent a non-physical product whose quantity is always 0."""

    def __init__(
        self, name: str = "Product Name", price: float | int = 0.0
    ) -> None:
        """Initialize a non-physical product with a quantity of 0."""
        super().__init__(name, price, quantity=0)
        self.activate()  # Zero quantity should not deactivate it

    def set_quantity(self, quantity: int) -> None:
        """Keep the quantity at zero.

        Raises
        ------
            ValueError
            If a non-zero quantity is given.

        """
        if quantity != 0:
            raise ValueError("Non-stocked products also have a quantity of 0")

    def __str__(self) -> str:
        """Return a string that represents the product."""
        return (
            f"{self.name}, Price: {self.price}, Quantity: 0 (not stocked)"
            f"{self._promotion_label()}"
        )

    def __repr__(self) -> str:
        """Return an unambiguous string that represents the product."""
        return (
            f"{type(self).__name__}(name={self.name!r}, price={self.price!r}"
            f"{self._promotion_repr()})"
        )

    def buy(self, quantity: int) -> float:
        """Buy a given quantity of the product.

        Returns
        -------
             the total price (float) of the purchase.
                * Updates the quantity of the product.
                * Raises an exception if amount bought would exceed
                available quantity or product is inactive.

        """
        if not self.is_active():
            raise ValueError("Product is inactive.")

        if quantity <= 0:
            raise ValueError("Purchase quantity must be positive.")

        return self.total_price(quantity)  # Do not change quantity on purchase
