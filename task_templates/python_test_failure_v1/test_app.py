from app import normalize_email, parse_price, parse_sku, slugify


def test_normalize_email_whitespace():
    assert normalize_email("  USER_v1@Example1.COM  ") == "user_v1@example1.com"


def test_parse_price_comma():
    assert parse_price("$1,234.50") == 1234.5


def test_slugify_punctuation():
    assert slugify("Hello World v1!") == "hello-world-v1"


def test_parse_price_currency_spacing():
    assert parse_price(" $ 1500.00 ") == 1500.0


def test_sku_preserves_semantic_comma():
    assert parse_sku("ABC_v1,123") == "ABC_v1,123"


def test_email_preserves_plus_tag():
    assert normalize_email(" User_v1+Tag@Example1.COM ") == "user_v1+tag@example1.com"
