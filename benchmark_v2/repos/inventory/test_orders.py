import pytest

from orders import Order
from stock import InsufficientStock
from warehouse import Network


def make_network():
    net = Network(["east", "west"])
    net.receive("east", "bolt", 10)
    net.receive("east", "nut", 10)
    net.receive("west", "bolt", 10)
    return net


def test_allocate_prefers_first_warehouse():
    net = Network(["east", "west"])
    net.receive("east", "bolt", 3)
    net.receive("west", "bolt", 10)
    assert net.allocate("bolt", 5) == [("east", 3), ("west", 2)]


def test_allocate_skips_empty_warehouse():
    net = Network(["east", "west"])
    net.receive("west", "bolt", 5)
    net.allocate("bolt", 3)
    assert net.sites["west"].available("bolt") == 2
    assert net.sites["east"].available("bolt") == 0


def test_allocate_insufficient_reserves_nothing():
    net = Network(["east", "west"])
    net.receive("east", "bolt", 2)
    net.receive("west", "bolt", 2)
    with pytest.raises(InsufficientStock):
        net.allocate("bolt", 5)
    assert net.total_available("bolt") == 4


def test_unknown_warehouse_raises():
    net = Network(["east"])
    with pytest.raises(KeyError):
        net.receive("north", "bolt", 1)


def test_low_stock_includes_threshold():
    net = Network(["east"])
    net.receive("east", "bolt", 2)
    net.receive("east", "nut", 5)
    net.receive("east", "washer", 9)
    assert net.low_stock(5) == ["bolt", "nut"]


def test_place_order_allocates_all_lines():
    net = make_network()
    order = Order("A1", {"bolt": 4, "nut": 2})
    assert order.place(net) is True
    assert net.total_available("bolt") == 16
    assert net.total_available("nut") == 8


def test_failed_order_rolls_back():
    net = make_network()
    order = Order("A2", {"bolt": 2, "nut": 50})
    assert order.place(net) is False
    assert order.status == "backordered"
    assert net.total_available("bolt") == 20


def test_ship_order_updates_on_hand():
    net = make_network()
    order = Order("A3", {"bolt": 3})
    order.place(net)
    order.ship(net)
    assert order.status == "shipped"
    assert net.sites["east"].on_hand["bolt"] == 7


def test_cannot_ship_backordered_order():
    net = make_network()
    order = Order("A4", {"nut": 50})
    order.place(net)
    with pytest.raises(RuntimeError):
        order.ship(net)


def test_picking_list_groups_by_site():
    net = make_network()
    order = Order("A5", {"bolt": 2, "nut": 3})
    order.place(net)
    assert order.picking_list() == {"east": {"bolt": 2, "nut": 3}}
