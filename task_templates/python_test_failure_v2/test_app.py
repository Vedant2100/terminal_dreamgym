from app import normalize_email, parse_price, parse_sku, slugify


def test_normalize_email_whitespace():
    assert normalize_email("  USER_v2@Example2.COM  ") == "user_v2@example2.com"


def test_parse_price_comma():
    assert parse_price("$2,234.50") == 2234.5


def test_slugify_punctuation():
    assert slugify("Hello World v2!") == "hello-world-v2"


def test_parse_price_currency_spacing():
    assert parse_price(" $ 2500.0 ") == 2500.0


def test_sku_preserves_semantic_comma():
    assert parse_sku("ABC_v2,123") == "ABC_v2,123"


def test_email_preserves_plus_tag():
    assert normalize_email(" User_v2+Tag@Example2.COM ") == "user_v2+tag@example2.com"
