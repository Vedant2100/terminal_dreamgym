from aggregate import average_price, group_totals, top_groups
from report import format_money, render

SALES = (
    "region,product,units,price\n"
    "west,widget,3,2.50\n"
    "east,gadget,10,150.00\n"
    "west,gizmo,1,0.25\n"
    "north,widget,2,2.50\n"
)


def test_group_totals():
    records = [
        {"region": "west", "units": 3, "price": 2.5},
        {"region": "west", "units": 1, "price": 0.25},
    ]
    assert group_totals(records, "region") == {"west": {"units": 4, "revenue": 7.75, "count": 2}}


def test_top_groups_ties_alphabetical():
    totals = {
        "west": {"units": 1, "revenue": 10.0, "count": 1},
        "east": {"units": 2, "revenue": 10.0, "count": 1},
        "north": {"units": 3, "revenue": 4.0, "count": 1},
    }
    assert top_groups(totals, 2) == ["east", "west"]


def test_average_price_zero_units():
    totals = {"west": {"units": 4, "revenue": 10.0, "count": 2}, "east": {"units": 0, "revenue": 0.0, "count": 1}}
    assert average_price(totals) == {"west": 2.5, "east": 0.0}


def test_format_money():
    assert format_money(1234.5) == "1,234.50"
    assert format_money(0) == "0.00"


def test_render_table():
    assert render(SALES).splitlines() == [
        "REGION       UNITS     REVENUE",
        "east            10    1,500.00",
        "north            2        5.00",
        "west             4        7.75",
        "TOTAL           16    1,512.75",
    ]


def test_render_top_keeps_grand_total():
    assert render(SALES, top=1).splitlines() == [
        "REGION       UNITS     REVENUE",
        "east            10    1,500.00",
        "TOTAL           16    1,512.75",
    ]


def test_render_key_is_case_insensitive():
    lines = render(SALES, key="Product").splitlines()
    assert lines[0].startswith("PRODUCT")
    assert lines[3] == "widget           5       12.50"


def test_render_quoted_field_with_comma():
    text = 'region,product,units,price\nwest,"Widget, large",2,5.00\neast,gizmo,1,1.00\n'
    lines = render(text, key="product").splitlines()
    assert lines[1].startswith("Widget, large")
    assert lines[-1] == "TOTAL            3       11.00"


def test_render_empty_input():
    assert render("").splitlines() == ["REGION       UNITS     REVENUE", "TOTAL            0        0.00"]
