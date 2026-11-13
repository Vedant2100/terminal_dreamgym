"""Tax rates by product category."""

RATES = {"standard": 0.20, "reduced": 0.05, "zero": 0.0}


def tax_for(cents: int, category: str) -> int:
    """Tax in cents for an amount in cents. Unknown categories are an error."""
    if category not in RATES:
        raise KeyError(f"unknown tax category: {category}")
    return round(cents * RATES[category])
