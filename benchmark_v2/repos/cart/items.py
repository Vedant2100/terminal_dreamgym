"""Cart line items. Prices are integer cents."""
from dataclasses import dataclass


@dataclass
class LineItem:
    sku: str
    unit_cents: int
    quantity: int = 1

    @property
    def total(self) -> int:
        return self.unit_cents * self.quantity


class Cart:
    """A shopping cart keyed by SKU. Adding an existing SKU increases its quantity."""

    def __init__(self):
        self.items = {}

    def add(self, sku: str, unit_cents: int, quantity: int = 1) -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        if unit_cents < 0:
            raise ValueError("price cannot be negative")
        if sku in self.items:
            self.items[sku].quantity += quantity
        else:
            self.items[sku] = LineItem(sku, unit_cents, quantity)

    def remove(self, sku: str, quantity=None) -> None:
        """Remove `quantity` units of `sku` (all of them if None).

        Removing the last unit drops the line from the cart.
        """
        if sku not in self.items:
            raise KeyError(sku)
        item = self.items[sku]
        if quantity is None or quantity >= item.quantity:
            del self.items[sku]
        else:
            item.quantity -= quantity

    def subtotal(self) -> int:
        return sum(item.total for item in self.items.values())

    def count(self) -> int:
        return sum(item.quantity for item in self.items.values())

    def is_empty(self) -> bool:
        return not self.items
