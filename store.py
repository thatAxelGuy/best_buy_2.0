"""Provide the Store class for managing products and orders."""
from products import Product


class Store:
    """Represent a store containing a collection of products."""

    def __init__(self, products: list[Product]) -> None:
        """Initialize the store with a list of products."""
        self.products: list[Product] = products

    def add_product(self, product: Product) -> None:
        """Add a product to the store."""
        self.products.append(product)

    def remove_product(self, product: Product) -> None:
        """Remove a product from the store."""
        if product in self.products:
            self.products.remove(product)

    def get_total_quantity(self) -> int:
        """Return how many items are in the store in total."""
        return sum(product.get_quantity() for product in self.products)

    def get_all_products(self) -> list[Product]:
        """Return all products in the store that are active."""
        return [product for product in self.products if product.is_active()]

    @staticmethod
    def order(shopping_list: list[tuple[Product, int]]) -> float:
        """Process a list of product and quantity tuples.

        Buy the products and return the total price of the order.
        Raises ValueError before any purchase is made if any item
        in the list cannot be fulfilled.
        """
        reserved: dict[Product, int] = {}
        for product, quantity in shopping_list:
            if not product.is_active():
                raise ValueError(f"{product.name} is inactive.")

            reserved[product] = reserved.get(product, 0) + quantity
            if reserved[product] > product.get_quantity():
                raise ValueError(f"Not enough stock of {product.name}.")

        total_price = 0.0

        for product, quantity in shopping_list:
            total_price += product.buy(quantity)

        return total_price
