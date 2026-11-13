import pytest

from settings import Field, MissingSetting, SettingsError, load

FIELDS = [
    Field("host", default="localhost"),
    Field("port", "int", default=8000),
    Field("debug", "bool", default=False),
    Field("tags", "list", default=[]),
]
INI = "[app]\nport = 8080\ndebug = yes\n"


def test_defaults_only():
    assert load(FIELDS) == {"host": "localhost", "port": 8000, "debug": False, "tags": []}


def test_file_overrides_defaults():
    values = load(FIELDS, INI)
    assert values["port"] == 8080
    assert values["debug"] is True


def test_env_overrides_file():
    assert load(FIELDS, INI, environ={"APP_PORT": "9090"})["port"] == 9090


def test_empty_env_var_falls_back_to_file():
    assert load(FIELDS, INI, environ={"APP_PORT": ""})["port"] == 8080


def test_env_list_value():
    assert load(FIELDS, environ={"APP_TAGS": "web, api"})["tags"] == ["web", "api"]


def test_bool_is_case_insensitive():
    fields = [Field("cache", "bool", default=True)]
    assert load(fields, "[app]\ncache = Off\n") == {"cache": False}


def test_json_source_keeps_types():
    values = load(FIELDS, '{"port": 9000, "tags": ["a", "b"]}', fmt="json")
    assert values["port"] == 9000
    assert values["tags"] == ["a", "b"]


def test_json_keys_case_insensitive():
    assert load(FIELDS, '{"Host": "example.org"}', fmt="json")["host"] == "example.org"


def test_ini_without_app_section_uses_defaults():
    assert load(FIELDS, "[other]\nport = 1\n")["port"] == 8000


def test_missing_required_lists_all():
    fields = [Field("db_url", required=True), Field("secret_key", required=True)]
    with pytest.raises(MissingSetting, match="db_url, secret_key"):
        load(fields)


def test_invalid_value_names_field():
    with pytest.raises(SettingsError, match="port"):
        load(FIELDS, environ={"APP_PORT": "eighty"})


def test_unknown_kind_is_settings_error():
    with pytest.raises(SettingsError):
        load([Field("ratio", "float")], "[app]\nratio = 0.5\n")
