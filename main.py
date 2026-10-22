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
                f"{prefix}{details}",
                width=LINE_WIDTH,
                subsequent_indent=indent,
            )
            # Color after wrapping so escape codes don't count toward the width
            price = f"Price: {product.price}"
            print(
                wrapped.replace(
                    price,
                    f"Price: {PRICE_COLOR}{product.price}{RESET_COLOR}",
                    1,
                )
            )
            if promotion:
                print(f"{indent}{PROMOTION_COLOR}{promotion}{RESET_COLOR}")

    return available_products


def show_total_quantity(store: Store) -> None:
    """Display the total quantity of products currently in the store."""
    print(f"Total amount of items in store: {store.get_total_quantity()}")


def _prompt_number(
    prompt: str,
    *,
    minimum: int = 1,
    maximum: int | None = None,
    cancel_word: str = "back",
    invalid: str = "Please enter a valid number.",
    too_low: str | None = None,
    too_high: str | None = None,
) -> int | None:
    """Prompt until the user enters a whole number within the given bounds.

    Returns None if the user types cancel_word. The too_low and too_high
    messages fall back to invalid when not given.
    """
    while True:
        text = input(prompt)

        if text.strip().lower() == cancel_word:
            return None

        if not text.isdigit():
            print(invalid)
            continue

        number = int(text)

        if number < minimum:
            print(too_low or invalid)
            continue

        if maximum is not None and number > maximum:
            print(too_high or invalid)
            continue

        return number


def _select_product(
    store: Store, basket: dict[Product, int]
) -> Product | None:
    """Prompt for and return a valid product, or None if the user leaves."""
    print("\nAvailable items")
    print("-" * 6)
    products = list_products(store, basket)
    print("-" * 6)
    print("Type 'leave' to finish or cancel the order.")

    number = _prompt_number(
        "Select a product #: \n",
        maximum=len(products),
        cancel_word="leave",
        invalid="Please enter a valid product number.",
        too_low="Please select a product from the list.",
        too_high="Please select a product from the list.",
    )

    return None if number is None else products[number - 1]


def _select_quantity(available_stock: int | None) -> int | None:
    """Prompt for and return a valid order quantity.

    The quantity is bounded by available_stock, or unbounded if it is None.
    Returns None if the user types 'back'.
    """
    return _prompt_number(
        "How many would you like to order? ('back' to return): ",
        maximum=available_stock,
        invalid="Please enter a valid quantity.",
        too_low="Please enter a value > 0.",
        too_high=f"Sorry, only {available_stock} are available.",
    )


def _confirm(question: str) -> bool:
    """Ask a yes/no question until the user answers y or n."""
    while True:
        answer = input(f"{question} (y/n): ").strip().lower()

        if answer in ("y", "n"):
            return answer == "y"

        print("Please answer 'y' or 'n'.")


def _basket_subtotal(basket: dict[Product, int]) -> float:
    """Return the order total before promotions."""
    return sum(
        product.price * quantity for product, quantity in basket.items()
    )


def _basket_total(basket: dict[Product, int]) -> float:
    """Return the order total with promotions applied."""
    return sum(
        product.total_price(quantity) for product, quantity in basket.items()
    )


def _edit_basket(basket: dict[Product, int]) -> None:
    """Let the user change or remove a basket item; 'back' changes nothing."""
    items = list(basket)

    number = _prompt_number(
        "Item # to change ('back' to return): ",
        maximum=len(items),
        invalid="Please select an item from the basket.",
    )

    if number is None:
        return

    product = items[number - 1]

    # the item's own line is replaced, so the limit ignores the basket
    limit = _orderable_amount(product)

    quantity = _prompt_number(
        f"New quantity for {product.name} (0 to remove, 'back' to return): ",
        minimum=0,
        maximum=limit,
        invalid="Please enter a valid quantity.",
        too_high=f"Sorry, only {limit} are available.",
    )

    if quantity is None:
        return

    if quantity == 0:
        del basket[product]
    else:
        basket[product] = quantity


def _review_basket(store: Store, basket: dict[Product, int]) -> bool:
    """Let the user review and adjust the basket before checking out.

    Returns True if the order is finished (placed or cancelled) and False
    if the user wants to keep shopping.
    """
    while True:
        if not basket:
            print("Your basket is empty.")
            return False

        _print_order_summary(basket, _basket_total(basket), "YOUR BASKET")
        print("a. Add another product")
        print("r. Remove or change an item")
        print("c. Check out")
        print("x. Cancel order")
        choice = input("Please choose: ").strip().lower()

        if choice == "a":
            return False

        if choice == "r":
            _edit_basket(basket)

        elif choice == "c":
            if not _confirm(f"Place order for ${_basket_total(basket):,.2f}?"):
                continue

            try:
                total = store.order(list(basket.items()))
            except ValueError as error:
                print(f"Order failed: {error}")
                print("Your basket was kept, so you can adjust it.")
                continue

            _print_order_summary(basket, total)
            return True

        elif choice == "x":
            if _confirm("Discard your basket and cancel the order?"):
                print("Order cancelled.")
                return True

        else:
            print("Please choose a, r, c or x.")


def make_order(store: Store) -> None:
    """Collect an order interactively and display its summary."""
    basket: dict[Product, int] = {}

    while True:
        product = _select_product(store, basket)

        if product is None:
            if not basket:
                return

            if _review_basket(store, basket):
                return

            continue

        available_stock = _orderable_amount(product, basket)

        if available_stock is None:
            print(f"{product.name} selected!")
        else:
            print(
                f"{product.name} selected! Amount remaining: {available_stock}"
            )

        quantity = _select_quantity(available_stock)

        if quantity is None:
            continue

        basket[product] = basket.get(product, 0) + quantity

        if _review_basket(store, basket):
            return


def _print_order_summary(
    basket: dict[Product, int], total: float, title: str = "ORDER SUMMARY"
) -> None:
    """Print a summary of the order to screen."""
    print("\n" + "=" * 40)
    print(title.center(40).rstrip())
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

    subtotal = _basket_subtotal(basket)

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
        LimitedProduct(
            "Promotional Teddy", price=100, quantity=250, maximum=3
        ),
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
