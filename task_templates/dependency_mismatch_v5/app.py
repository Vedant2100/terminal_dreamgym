from package import format_order, format_user, parse_result


def render_user(name: str, email: str) -> str:
    return format_user(name, email)


def render_user_list(users: list[dict[str, str]]) -> list[str]:
    return [format_user(user["name"], user["email"]) for user in users]


def render_order(order_id: str, total: float) -> str:
    return format_order(order_id, total)


def get_result_value(result: dict[str, object]) -> object:
    return parse_result(result)
