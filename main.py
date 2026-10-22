"""Command-line interface for managing Best Buy products and orders."""

import textwrap

from products import LimitedProduct, NonStockedProduct, Product
from promotions import PercentDiscount, SecondHalfPrice, ThirdOneFree
from store import Store

LINE_WIDTH = 80
PRICE_COLOR = "\033[1;32m"
PROMOTION_COLOR = "\033[1;33m"
RESET_COLOR = "\033[0m"


def validate_input() -> str:
    """Prompt until the user enters a valid main-menu selection."""
    selection = input("Please choose a number:\n")

    while selection not in ["1", "2", "3", "4"]:
        print("Invalid selection. Please choose a number between 1 and 4.")
        selection = input("Please choose a number:\n")

    return selection


def _orderable_amount(
    product: Product, basket: dict[Product, int] | None = None
) -> int | None:
    """Return how many more units of a product can be added to the order.

    Returns None when there is no limit (non-stocked products).
    """
    if isinstance(product, NonStockedProduct):
        return None

    amount = product.get_quantity()
    if isinstance(product, LimitedProduct):
        amount = min(amount, product.maximum)

    if basket is not None:
        amount -= basket.get(product, 0)

    return amount


def list_products(
    store: Store, basket: dict[Product, int] | None = None
) -> list[Product]:
    """Display and return products with stock available for purchase.

    Parameters
    ----------
    store : Store
        Store reference
    basket : dict[Product,int] | None, optional
        Products and quantities already selected for the current order.

    Returns
    -------
    list[Product]
        Products with remaining available stock.

    """
    products: list[Product] = store.get_all_products()
    available_products = []

    for product in products:
        orderable = _orderable_amount(product, basket)

        if orderable is None or orderable > 0:
            available_products.append(product)
            prefix = f"{len(available_products)}. "
            indent = " " * len(prefix)
            details, _, promotion = str(product).partition("\n")
            wrapped = textwrap.fill(
                f"{prefix}{details}", width=LINE_WIDTH, subsequent_indent=indent
            )
            # Color after wrapping so escape codes don't count toward the width
            price = f"Price: {product.price}"
            print(
                wrapped.replace(
                    price, f"Price: {PRICE_COLOR}{product.price}{RESET_COLOR}", 1
                )
            )
            if promotion:
                print(f"{indent}{PROMOTION_COLOR}{promotion}{RESET_COLOR}")

    return available_products


def show_total_quantity(store: Store) -> None:
    """Display the total quantity of products currently in the store."""
    print(f"Total amount of items in store: {store.get_total_quantity()}")


def _select_product(store: Store, basket: dict[Product, int]) -> Product | None:
    """Prompt for and return a valid product, or None if the user leaves."""
    while True:
        print("\nAvailable items")
        print("-" * 6)
        products = list_products(store, basket)
        print("-" * 6)
        print("Type 'leave' if you want to cancel the order.")

        selection = input("Select a product #: \n")

        if selection.lower() == "leave":
            return None

        if not selection.isdigit():
            print("Please enter a valid product number.")
            continue

        product_number = int(selection)

        if product_number < 1 or product_number > len(products):
            print("Please select a product from the list.")
            continue

        return products[product_number - 1]


def _select_quantity(available_stock: int | None) -> int:
    """Prompt for and return a valid order quantity.

    The quantity is bounded by available_stock, or unbounded if it is None.
    """
    while True:
        quantity = input("How many would you like to order?: ")
        if not quantity.isdigit():
            print("Please enter a valid quantity.")
            continue

        if quantity == "0":
            print("Please enter a value > 0.")
            continue

        quantity = int(quantity)

        if available_stock is not None and quantity > available_stock:
            print(f"Sorry, only {available_stock} are available.")
            continue

        return quantity


def make_order(store: Store) -> None:
    """Collect an order interactively and display its summary."""
    basket: dict[Product, int] = {}

    while True:
        product = _select_product(store, basket)

        if product is None:
            return
        available_stock = _orderable_amount(product, basket)

        if available_stock == 0:
            print(
                "You have already added all available stock of this "
                "product to your order."
            )
            continue

        if available_stock is None:
            print(f"{product.name} selected!")
        else:
            print(f"{product.name} selected! Amount remaining: {available_stock}")

        quantity = _select_quantity(available_stock)

        basket[product] = basket.get(product, 0) + quantity

        continue_order = input("Would you like to add another product? (y/n): ")

        if continue_order.lower() == "n":
            break

    try:
        total = store.order(list(basket.items()))
    except ValueError as error:
        print(f"Order failed: {error}")
        return

    _print_order_summary(basket, total)


def _print_order_summary(basket: dict[Product, int], total: float) -> None:
    """Print summary of the order to screen."""
    print("\n" + "=" * 40)
    print("           ORDER SUMMARY")
    print("=" * 40)

    for index, (product, quantity) in enumerate(basket.items(), start=1):
        item_total = product.price * quantity
        discounted_total = product.total_price(quantity)
        print(f"\n{index}. {product.name}")
        print(f"   ${product.price:,.2f} × {quantity} = ${item_total:,.2f}")
        promotion = product.get_promotion()
        if promotion is not None and discounted_total != item_total:
            saved = item_total - discounted_total
            print(
                f"   {PROMOTION_COLOR}{promotion.name} -> "
                f"${discounted_total:,.2f}{RESET_COLOR}"
            )
            print(f"   {PRICE_COLOR}Saved ${saved:,.2f}{RESET_COLOR}")

    subtotal = sum(product.price * quantity for product, quantity in basket.items())

    print("\n" + "-" * 40)
    if subtotal != total:
        print(f"Subtotal: ${subtotal:,.2f}")
        print(f"{PRICE_COLOR}You save: ${subtotal - total:,.2f}{RESET_COLOR}")
    print(f"TOTAL: ${total:,.2f}")
    print("=" * 40)


def start(store: Store) -> None:
    """Run the interactive Best Buy main menu."""
    menu = {
        "1": list_products,
        "2": show_total_quantity,
        "3": make_order,
    }

    while True:
        print("\n" + "=" * 40)
        print("              BEST BUY")
        print("=" * 40)

        print("1. List all products in store")
        print("2. Show total amount in store")
        print("3. Make an order")
        print("4. Quit")

        print("-" * 40)

        selection = validate_input()
        print("-" * 30)

        if selection == "4":
            print("Goodbye!")
            break

        menu[selection](store)


def main() -> None:
    """Start the Best Buy command-line application."""
    # setup initial stock of inventory
    product_list = [
        Product("MacBook Air M2", price=1450, quantity=100),
        Product("Bose QuietComfort Earbuds", price=250, quantity=500),
        Product("Google Pixel 7", price=500, quantity=250),
        NonStockedProduct("Windows License", price=125),
        LimitedProduct("Promotional Teddy", price=100, quantity=250, maximum=3),
        LimitedProduct("Shipping", price=10, quantity=250, maximum=1),
    ]

    # setup promotions
    product_list[0].set_promotion(SecondHalfPrice("Second Half Price!"))
    product_list[1].set_promotion(ThirdOneFree("Third One Free!"))
    product_list[3].set_promotion(PercentDiscount("30% off!", percent=30))
    product_list[4].set_promotion(ThirdOneFree("Buy 2 Get 1 Free!"))

    best_buy = Store(product_list)
    start(best_buy)


if __name__ == "__main__":
    main()
