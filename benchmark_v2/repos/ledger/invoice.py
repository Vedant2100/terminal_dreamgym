"""Invoices made of lines, with an optional percentage discount."""
from dataclasses import dataclass, field

from money import format_cents, to_cents
from tax import tax_for


@dataclass
class Line:
    description: str
    unit_cents: int
    quantity: int = 1
    category: str = "standard"

    @property
    def subtotal(self) -> int:
        return self.unit_cents * self.quantity


@dataclass
class Invoice:
    lines: list = field(default_factory=list)
    discount_percent: int = 0

    def add(self, description: str, amount: str, quantity: int = 1, category: str = "standard") -> None:
        if quantity <= 0:
            raise ValueError("quantity must be positive")
        self.lines.append(Line(description, to_cents(amount), quantity, category))

    def subtotal(self) -> int:
        return sum(line.subtotal for line in self.lines)

    def discount(self) -> int:
        return self.subtotal() * self.discount_percent // 100

    def tax(self) -> int:
        # Tax is charged on each line after the discount.
        total = 0
        for line in self.lines:
            discounted = line.subtotal - line.subtotal * self.discount_percent // 100
            total += tax_for(discounted, line.category)
        return total

    def discount_label(self) -> str:
        """The discount as shown on the invoice: a negative amount, e.g. '-$2.60'."""
        return format_cents(-self.discount())

    def total(self) -> int:
        return self.subtotal() - self.discount() + self.tax()

    def summary(self) -> dict:
        return {
            "subtotal": format_cents(self.subtotal()),
            "discount": self.discount_label(),
            "tax": format_cents(self.tax()),
            "total": format_cents(self.total()),
        }
