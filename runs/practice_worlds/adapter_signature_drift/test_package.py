from app import get_result_value, render_order, render_user, render_user_list
from package import format_user


def test_format_user_signature_drift():
    assert render_user("Ada", "ada@example.com") == "Ada <ada@example.com>"


def test_parse_result_shape_drift():
    assert get_result_value({"data": {"value": 42}}) == 42


def test_format_order_signature_drift():
    assert render_order("A-1", 12.5) == "A-1: $12.50"


def test_do_not_break_new_dependency_contract():
    assert format_user({"name": "Grace", "email": "grace@example.com"}) == "Grace <grace@example.com>"
    assert render_user_list([{"name": "Grace", "email": "grace@example.com"}]) == [
        "Grace <grace@example.com>"
    ]
