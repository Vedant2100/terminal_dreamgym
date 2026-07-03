from app import normalize_email, parse_price, parse_sku, slugify


def test_normalize_email_whitespace():
    assert normalize_email("  USER_v5@Example5.COM  ") == "user_v5@example5.com"


def test_parse_price_comma():
    assert parse_price("$5,234.50") == 5234.5


def test_slugify_punctuation():
    assert slugify("Hello World v5!") == "hello-world-v5"


def test_parse_price_currency_spacing():
    assert parse_price(" $ 5500.00 ") == 5500.0


def test_sku_preserves_semantic_comma():
    assert parse_sku("ABC_v5,123") == "ABC_v5,123"


def test_email_preserves_plus_tag():
    assert normalize_email(" User_v5+Tag@Example5.COM ") == "user_v5+tag@example5.com"
