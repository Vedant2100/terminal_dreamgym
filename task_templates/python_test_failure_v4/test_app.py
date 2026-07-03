from app import normalize_email, parse_price, parse_sku, slugify


def test_normalize_email_whitespace():
    assert normalize_email("  USER_v4@Example4.COM  ") == "user_v4@example4.com"


def test_parse_price_comma():
    assert parse_price("$4,234.50") == 4234.5


def test_slugify_punctuation():
    assert slugify("Hello World v4!") == "hello-world-v4"


def test_parse_price_currency_spacing():
    assert parse_price(" $ 4500.00 ") == 4500.0


def test_sku_preserves_semantic_comma():
    assert parse_sku("ABC_v4,123") == "ABC_v4,123"


def test_email_preserves_plus_tag():
    assert normalize_email(" User_v4+Tag@Example4.COM ") == "user_v4+tag@example4.com"
