from cells import format_cell


def test_pipe_is_escaped():
    assert format_cell("a|b") == "a\\|b"


def test_newline_becomes_space():
    assert format_cell("two\nlines") == "two lines"


def test_int_has_thousands_separators():
    assert format_cell(1234567) == "1,234,567"


def test_float_always_shows_decimals():
    assert format_cell(1234.5) == "1,234.50"
    assert format_cell(2.0) == "2.00"


def test_bool_is_yes_or_no():
    assert format_cell(True) == "yes"
    assert format_cell(False) == "no"


def test_none_is_blank():
    assert format_cell(None) == ""
