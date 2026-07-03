from app import normalize_email, parse_price, parse_sku, slugify


def test_normalize_email_whitespace():
    assert normalize_email("  USER_v3@Example3.COM  ") == "user_v3@example3.com"


def test_parse_price_comma():
    assert parse_price("$3,234.50") == 3234.5


def test_slugify_punctuation():
    assert slugify("Hello World v3!") == "hello-world-v3"


def test_parse_price_currency_spacing():
    assert parse_price(" $ 3500.00 ") == 3500.0


def test_sku_preserves_semantic_comma():
    assert parse_sku("ABC_v3,123") == "ABC_v3,123"


def test_email_preserves_plus_tag():
    assert normalize_email(" User_v3+Tag@Example3.COM ") == "user_v3+tag@example3.com"
