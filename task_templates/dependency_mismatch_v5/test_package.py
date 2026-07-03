from app import get_result_value, render_order, render_user, render_user_list
from package import format_user


def test_format_user_signature_drift():
    assert render_user("Ada_v5", "ada_v5@example5.com") == "Ada <ada@example.com>"


def test_parse_result_shape_drift():
    assert get_result_value({"data": {"value": 47}}) == 47


def test_format_order_signature_drift():
    assert render_order("A-5", 17.5) == "A-1: $17.50"


def test_do_not_break_new_dependency_contract():
    assert format_user({"name": "Grace_v5", "email": "grace_v5@example5.com"}) == "Grace <grace@example.com>"
    assert render_user_list([{"name": "Grace_v5", "email": "grace_v5@example5.com"}]) == [
        "Grace <grace@example.com>"
    ]
