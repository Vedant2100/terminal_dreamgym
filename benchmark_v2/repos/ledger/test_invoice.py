import pytest

from invoice import Invoice
from tax import tax_for


def test_tax_categories():
    assert tax_for(1000, "standard") == 200
    assert tax_for(1000, "reduced") == 50
    assert tax_for(1000, "zero") == 0


def test_unknown_tax_category_raises():
    with pytest.raises(KeyError):
        tax_for(1000, "luxury")


def test_subtotal_and_discount():
    inv = Invoice(discount_percent=10)
    inv.add("widget", "10.00", quantity=2)
    inv.add("manual", "6.00", category="reduced")
    assert inv.subtotal() == 2600
    assert inv.discount() == 260


def test_total_taxes_after_discount():
    inv = Invoice(discount_percent=10)
    inv.add("widget", "10.00", quantity=2)
    inv.add("manual", "6.00", category="reduced")
    # widget: 2000 - 200 = 1800, tax 360; manual: 600 - 60 = 540, tax 27
    assert inv.tax() == 387
    assert inv.total() == 2600 - 260 + 387


def test_discount_label_is_negative():
    inv = Invoice(discount_percent=10)
    inv.add("widget", "10.00")
    assert inv.discount_label() == "-$1.00"


def test_quantity_must_be_positive():
    inv = Invoice()
    with pytest.raises(ValueError):
        inv.add("widget", "1.00", quantity=0)


def test_empty_invoice_summary():
    assert Invoice().summary() == {"subtotal": "$0.00", "discount": "$0.00", "tax": "$0.00", "total": "$0.00"}
