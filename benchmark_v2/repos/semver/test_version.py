import pytest

from version import Version, parse, sort_versions


def test_parse_basic():
    assert parse("1.2.3") == Version(1, 2, 3)
    assert parse("v10.0.7").major == 10


def test_parse_prerelease_and_build():
    v = parse("2.0.0-rc.1+build.5")
    assert v.pre == ("rc", "1")
    assert v.build == "build.5"
    assert str(v) == "2.0.0-rc.1+build.5"


def test_parse_invalid_raises():
    for text in ["1.2", "1.2.3.4", "1.2.x"]:
        with pytest.raises(ValueError):
            parse(text)


def test_prerelease_sorts_before_release():
    assert parse("1.0.0-rc.1") < parse("1.0.0")
    assert parse("1.0.0") > parse("1.0.0-alpha")


def test_build_metadata_ignored_in_equality():
    assert parse("1.0.0+linux") == parse("1.0.0+mac")
    assert len({parse("1.0.0+a"), parse("1.0.0")}) == 1


def test_sort_versions_numeric():
    texts = ["1.10.0", "v1.2.0", "0.9.9", "1.2.10"]
    assert sort_versions(texts) == ["0.9.9", "v1.2.0", "1.2.10", "1.10.0"]
