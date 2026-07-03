from app import normalize_email, parse_price, parse_sku, slugify


def test_normalize_email_whitespace():
    assert normalize_email("  USER@Example.COM  ") == "user@example.com"


def test_parse_price_comma():
    assert parse_price("$1,234.50") == 1234.50


def test_slugify_punctuation():
    assert slugify("Hello, World!") == "hello-world"


def test_parse_price_currency_spacing():
    assert parse_price(" $ 2,500.00 ") == 2500.00


def test_sku_preserves_semantic_comma():
    assert parse_sku("ABC,123") == "ABC,123"


def test_email_preserves_plus_tag():
    assert normalize_email(" User+Tag@Example.COM ") == "user+tag@example.com"
