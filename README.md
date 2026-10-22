# Best Buy Store

A simple command-line Best Buy store application written in Python.

The application allows users to:

* View available products
* Check the total quantity of products in the store
* Create an order by selecting products and quantities
* Benefit from product promotions (percentage discounts, second item half price, third item free)
* View an order summary with the total price
* Exit the application

## Project Structure

```text
.
├── main.py
├── products.py
├── promotions.py
├── store.py
├── requirements.txt
├── tests/
│   ├── test_products.py
│   └── test_store.py
└── README.md
```

### `products.py`

Contains the `Product` class, which manages individual products, including:

* Product name
* Price
* Quantity
* Active/inactive status
* Purchasing products
* An optional promotion, set with `set_promotion()`

It also provides `NonStockedProduct` (no quantity, e.g. a license) and `LimitedProduct` (a maximum quantity per order).

### `promotions.py`

Contains the `Promotion` abstract base class and its implementations. Each promotion's `apply_promotion(product, quantity)` returns the discounted total price:

| Promotion        | Effect                                      |
| ---------------- | ------------------------------------------- |
| `PercentDiscount` | Takes a percentage (0-100) off the price    |
| `SecondHalfPrice` | Every second item costs half price          |
| `ThirdOneFree`    | Every third item is free (buy 2, get 1)     |

Attach a promotion to a product:

```python
from promotions import PercentDiscount

product.set_promotion(PercentDiscount("30% off!", percent=30))
product.set_promotion(None)  # remove it
```

Promotions are shown in the product listing and as a discount line in the order summary.

### `store.py`

Contains the `Store` class, which manages the store's products and orders.

### `main.py`

Contains the command-line user interface, including the store inventory, menu, product listing, and ordering process.

### `tests/`

Contains unit tests for `Product` and `Store`, covering validation, purchasing, and order handling (including edge cases like ordering more stock than is available).

## Requirements

* Python 3.10+
* `pytest` (only needed to run the test suite — see [Testing](#testing))

Install with:

```bash
pip install -r requirements.txt
```

## How to Run

Clone the repository and navigate to the project directory.

Run:

```bash
python main.py
```

The application will display the main menu:

```text
========================================
              BEST BUY
========================================
1. List all products in store
2. Show total amount in store
3. Make an order
4. Quit
----------------------------------------
```

Follow the prompts to interact with the store.

## Testing

Unit tests are written with `pytest` and live in the `tests/` directory.

Run the full suite from the project root:

```bash
python3 -m pytest
```

Run a single test file:

```bash
python3 -m pytest tests/test_store.py
```

Run a single test:

```bash
python3 -m pytest tests/test_store.py::test_order_rejects_repeated_product_exceeding_stock
```

## Example Inventory

The application starts with the following products:

| Product                   |  Price | Quantity | Promotion         |
| ------------------------- | -----: | -------: | ----------------- |
| MacBook Air M2            | $1,450 |      100 | Second Half Price |
| Bose QuietComfort Earbuds |   $250 |      500 | Third One Free    |
| Google Pixel 7            |   $500 |      250 | -                 |
| Windows License           |   $125 |        - | 30% off           |
| Promotional Teddy         |   $100 |      250 | Third One Free    |
| Shipping                  |    $10 |      250 | -                 |

## Development

The project uses Python type hints and Ruff for code quality and linting.