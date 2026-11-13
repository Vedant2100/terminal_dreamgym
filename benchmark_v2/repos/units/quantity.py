"""Quantities such as '12.5 km' or '-40 °F': parsing, conversion and formatting."""
import re
from dataclasses import dataclass

from convert import convert
from units import canonical, dimension

_QUANTITY = re.compile(r"^\s*([-+]?\d+(?:\.\d+)?)\s*([^\d\s].*?)\s*$")


@dataclass(frozen=True)
class Quantity:
    value: float
    unit: str

    def to(self, unit: str) -> "Quantity":
        return Quantity(convert(self.value, self.unit, unit), canonical(unit))

    def __add__(self, other: "Quantity") -> "Quantity":
        """Sum in this quantity's unit."""
        return Quantity(self.value + convert(other.value, other.unit, self.unit), self.unit)


def parse_quantity(text: str) -> Quantity:
    """'12.5 km' -> Quantity(12.5, 'km'). Raises ValueError for malformed text
    and KeyError for an unknown unit."""
    match = _QUANTITY.match(text)
    if not match:
        raise ValueError(f"not a quantity: {text!r}")
    unit = canonical(match.group(2))
    dimension(unit)
    return Quantity(float(match.group(1)), unit)


def format_quantity(q: Quantity, precision: int = 2) -> str:
    """'12.50 km'. Celsius and Fahrenheit get a degree sign ('21.5 °C'); kelvin does not."""
    text = f"{q.value:.{precision}f}"
    if float(text) == 0:
        text = f"{0:.{precision}f}"  # never show '-0.00'
    unit = "°" + q.unit if q.unit in ("C", "F") else q.unit
    return f"{text} {unit}"
