def normalize_email(email: str) -> str:
    return email.lower()


def parse_price(value: str) -> float:
    return float(value.replace("$", ""))


def parse_sku(value: str) -> str:
    return value.replace(",", "")


def slugify(text: str) -> str:
    return text.lower().replace(" ", "-")
