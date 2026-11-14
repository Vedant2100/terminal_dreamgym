from table import render

FRUIT = [{"name": "apple", "qty": 3}, {"name": "kiwi", "qty": 12}]


def test_render_basic():
    assert render(FRUIT) == (
        "| Name  | Qty |\n"
        "| :---- | --: |\n"
        "| apple |   3 |\n"
        "| kiwi  |  12 |"
    )


def test_columns_in_order_of_first_appearance():
    rows = [{"b": 1}, {"a": 2, "b": 3}]
    assert render(rows).splitlines()[0].split() == ["|", "B", "|", "A", "|"]


def test_explicit_order_selects_columns():
    rows = [{"name": "apple", "qty": 3, "note": "fresh"}]
    assert render(rows, ["qty", "name"]).splitlines()[0] == "| Qty | Name  |"


def test_mixed_column_is_left_aligned():
    rows = [{"qty": 1}, {"qty": "n/a"}]
    assert render(rows).splitlines()[1] == "| :-- |"


def test_missing_values_are_blank_and_ignored_for_alignment():
    rows = [{"name": "alice", "qty": None}, {"name": "bob", "qty": 5}]
    assert render(rows) == (
        "| Name  | Qty |\n"
        "| :---- | --: |\n"
        "| alice |     |\n"
        "| bob   |   5 |"
    )


def test_spec_string_sets_alignment():
    rows = [{"name": "apple", "qty": 3}]
    assert render(rows, "name:^, qty:<") == (
        "|  Name | Qty |\n"
        "| :---: | :-- |\n"
        "| apple | 3   |"
    )


def test_width_counts_escaped_text():
    rows = [{"expr": "a|b"}]
    assert render(rows) == "| Expr |\n| :--- |\n| a\\|b |"


def test_header_wider_than_values():
    rows = [{"unit_price": 5}]
    assert render(rows) == "| Unit Price |\n| ---------: |\n|          5 |"


def test_decimals_option():
    rows = [{"pi": 3.14159}]
    assert render(rows, decimals=3).splitlines()[2] == "| 3.142 |"


def test_no_rows_with_columns():
    assert render([], ["a"]) == "| A   |\n| :-- |"
