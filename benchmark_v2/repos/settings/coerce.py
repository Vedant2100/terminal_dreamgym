"""Convert raw setting values (usually strings) to typed values."""

TRUE_WORDS = {"1", "true", "yes", "on"}
FALSE_WORDS = {"0", "false", "no", "off"}


def to_bool(value) -> bool:
    """Accept real bools and the words above, in any letter case."""
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in TRUE_WORDS:
        return True
    if text in FALSE_WORDS:
        return False
    raise ValueError(f"not a boolean: {value!r}")


def to_int(value) -> int:
    """Whole numbers only: '2.5' is an error, not 2."""
    return int(str(value).strip())


def to_list(value) -> list:
    """Split a comma-separated string into stripped, non-empty items. Lists pass through."""
    if isinstance(value, list):
        return list(value)
    return [item.strip() for item in str(value).split(",") if item.strip()]


CONVERTERS = {"str": str, "int": to_int, "bool": to_bool, "list": to_list}


def coerce(value, kind: str):
    """Convert value to `kind`. Bad values and unknown kinds raise ValueError."""
    if kind not in CONVERTERS:
        raise ValueError(f"unknown setting type: {kind}")
    return CONVERTERS[kind](value)
