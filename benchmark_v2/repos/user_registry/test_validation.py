import pytest

from validation import ValidationError, check_password, check_username


def test_username_is_lowercased():
    assert check_username("Alice_1") == "alice_1"


def test_username_too_short_rejected():
    with pytest.raises(ValidationError):
        check_username("ab")


def test_reserved_username_rejected_in_any_case():
    with pytest.raises(ValidationError):
        check_username("Admin")


def test_password_needs_digit():
    with pytest.raises(ValidationError):
        check_password("abcdefgh", "zed")


def test_password_cannot_contain_username():
    with pytest.raises(ValidationError):
        check_password("myBOBpass1", "bob")


def test_password_of_minimum_length_ok():
    assert check_password("abcdef12", "zed") is None


def test_password_too_short_rejected():
    with pytest.raises(ValidationError):
        check_password("abc1234", "zed")
