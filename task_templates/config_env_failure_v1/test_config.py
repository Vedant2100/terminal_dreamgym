import json

import pytest

from app import MissingRequiredConfig, load_settings


def write_config(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_request_timeout_key():
    assert load_settings(env={})["timeout"] == 11


def test_missing_optional_region_defaults(tmp_path):
    config = write_config(tmp_path / "config.json", {"request_timeout": 7, "auth": {"token": "t"}})
    assert load_settings(config, env={})["region"] == "us-east-1"


def test_nested_auth_token():
    assert load_settings(env={})["api_key"] == "local-token-v1"


def test_missing_required_api_key_fails_loudly(tmp_path):
    config = write_config(tmp_path / "config.json", {"request_timeout": 3, "region": "us-west-1"})
    with pytest.raises(MissingRequiredConfig):
        load_settings(config, env={})


def test_request_timeout_type_is_int(tmp_path):
    config = write_config(
        tmp_path / "config.json",
        {"request_timeout": "15", "auth": {"token": "t"}, "region": "us-west-1"},
    )
    assert load_settings(config, env={})["timeout"] == 15
