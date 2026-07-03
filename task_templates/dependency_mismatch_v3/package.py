def format_user(user: dict[str, str]) -> str:
    return f"{user['name']} <{user['email']}>"


def format_order(order: dict[str, object]) -> str:
    return f"{order['id']}: ${order['total']:.2f}"


def parse_result(result: dict[str, object]) -> object:
    return result["value"]
