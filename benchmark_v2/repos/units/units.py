"""Unit tables and unit-name lookup."""

# Linear units: factor to the dimension's base unit (metre, kilogram).
LENGTH = {"mm": 0.001, "cm": 0.01, "m": 1.0, "km": 1000.0, "in": 0.0254, "ft": 0.3048, "mi": 1609.344}
MASS = {"mg": 1e-6, "g": 0.001, "kg": 1.0, "oz": 0.028349523125, "lb": 0.45359237}

# Temperatures: (scale, offset) such that kelvin = (value + offset) * scale.
TEMPERATURE = {"K": (1.0, 0.0), "C": (1.0, 273.15), "F": (5 / 9, 459.67)}

# Spelled-out names and symbols with a degree sign. Keys are lower case.
ALIASES = {
    "metre": "m", "meter": "m", "metres": "m", "meters": "m",
    "kilometre": "km", "kilometer": "km", "kilometres": "km", "kilometers": "km",
    "gram": "g", "grams": "g", "kilogram": "kg", "kilograms": "kg",
    "pound": "lb", "pounds": "lb", "lbs": "lb",
    "°c": "C", "celsius": "C", "°f": "F", "fahrenheit": "F", "kelvin": "K",
}


def canonical(name: str) -> str:
    """The table symbol for a unit name.

    Symbols are case-sensitive ('mm' is not 'Mm'); aliases match in any case.
    """
    key = name.strip()
    return ALIASES.get(key.lower(), key)


def dimension(unit: str) -> str:
    """'length', 'mass' or 'temperature'. Unknown units raise KeyError."""
    for dim, table in (("length", LENGTH), ("mass", MASS), ("temperature", TEMPERATURE)):
        if unit in table:
            return dim
    raise KeyError(f"unknown unit: {unit}")
