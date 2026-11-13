import pytest

from records import ParseError, parse


def test_parse_types():
    rows = parse("region,product,units,price\nwest,widget,3,2.50\n")
    assert rows == [{"region": "west", "product": "widget", "units": 3, "price": 2.5}]


def test_parse_header_case_and_spaces():
    rows = parse(" Region , PRODUCT ,Units,price\n west , widget ,3,2.50\n")
    assert rows == [{"region": "west", "product": "widget", "units": 3, "price": 2.5}]


def test_parse_skips_blank_lines():
    rows = parse("region,product,units,price\nwest,widget,3,2.50\n\n  \neast,gizmo,1,1.00\n")
    assert [r["region"] for r in rows] == ["west", "east"]


def test_parse_drops_unknown_columns():
    rows = parse("region,product,units,price,notes\nwest,widget,3,2.50,rush\n")
    assert "notes" not in rows[0]


def test_bad_number_reports_line():
    text = "region,product,units,price\nwest,widget,3,2.50\neast,gizmo,three,1.00\n"
    with pytest.raises(ParseError, match="line 3"):
        parse(text)


def test_bad_row_after_blank_line_keeps_line_number():
    text = "region,product,units,price\nwest,widget,3,2.50\n\neast,gizmo,1,cheap\n"
    with pytest.raises(ParseError, match="line 4"):
        parse(text)


def test_missing_column_raises():
    with pytest.raises(ParseError, match="price"):
        parse("region,product,units\nwest,widget,3\n")
