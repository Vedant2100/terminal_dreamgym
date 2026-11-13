"""Group records and compute per-group totals."""


def revenue(record: dict) -> float:
    return record["units"] * record["price"]


def group_totals(records: list, key: str) -> dict:
    """{group: {"units": int, "revenue": float, "count": int}} for each value of key."""
    groups = {}
    for record in records:
        totals = groups.setdefault(record[key], {"units": 0, "revenue": 0.0, "count": 0})
        totals["units"] += record["units"]
        totals["revenue"] += revenue(record)
        totals["count"] += 1
    return groups


def top_groups(totals: dict, n: int, by: str = "revenue") -> list:
    """Names of the n groups with the largest `by` value; ties go alphabetically."""
    ranked = sorted(totals.items(), key=lambda item: (-item[1][by], item[0]))
    return [name for name, _ in ranked[:n]]


def average_price(totals: dict) -> dict:
    """Revenue per unit for each group. Groups with no units get 0.0."""
    return {name: (t["revenue"] / t["units"] if t["units"] else 0.0) for name, t in totals.items()}
