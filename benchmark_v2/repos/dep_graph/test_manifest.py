import pytest

from manifest import ParseError, parse


def test_parse_basic():
    assert parse("a -> b, c\nb -> c\nd") == {"a": ["b", "c"], "b": ["c"], "d": []}


def test_comments_and_blank_lines_ignored():
    text = "# packages\n\na -> b  # needs b\n"
    assert parse(text) == {"a": ["b"]}


def test_names_are_lowercased():
    assert parse("Web -> Lib, CORE") == {"web": ["lib", "core"]}


def test_self_dependency_reports_line_number():
    with pytest.raises(ParseError) as exc:
        parse("a -> b\nb -> b")
    assert exc.value.lineno == 2


def test_missing_package_name_is_error():
    with pytest.raises(ParseError):
        parse("-> b")
