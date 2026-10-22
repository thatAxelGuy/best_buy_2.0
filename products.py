"""Define products and their inventory behavior."""


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

    def show(self) -> None:
        """Print a string that represents the product."""
        print(f"{self.name}, Price: {self.price}, Quantity: {self.get_quantity()}")

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
        return self.price * quantity
