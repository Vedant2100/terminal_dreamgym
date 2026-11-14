import pytest

from items import Cart


def test_add_same_sku_merges_quantity():
    cart = Cart()
    cart.add("apple", 120, 2)
    cart.add("apple", 120, 3)
    assert len(cart.items) == 1
    assert cart.count() == 5


def test_subtotal():
    cart = Cart()
    cart.add("apple", 250, 2)
    cart.add("pear", 100)
    assert cart.subtotal() == 600


def test_remove_some_units():
    cart = Cart()
    cart.add("apple", 120, 3)
    cart.remove("apple", 1)
    assert cart.items["apple"].quantity == 2


def test_remove_without_quantity_drops_line():
    cart = Cart()
    cart.add("apple", 120, 3)
    cart.remove("apple")
    assert "apple" not in cart.items


def test_add_rejects_zero_quantity():
    cart = Cart()
    with pytest.raises(ValueError):
        cart.add("apple", 120, 0)
