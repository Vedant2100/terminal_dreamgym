"""Read raw settings from INI or JSON text and from an environment mapping.

Every source returns a flat dict with lower-case keys.
"""
import configparser
import json


def parse_ini(text: str, section: str = "app") -> dict:
    """Keys of one INI section as strings. A missing section gives {}."""
    parser = configparser.ConfigParser()
    parser.read_string(text)
    if not parser.has_section(section):
        return {}
    return dict(parser.items(section))


def parse_json(text: str) -> dict:
    """A JSON object; values keep their JSON types."""
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("settings JSON must be an object")
    return {key.lower(): value for key, value in data.items()}


def parse_text(text: str, fmt: str) -> dict:
    if fmt == "ini":
        return parse_ini(text)
    if fmt == "json":
        return parse_json(text)
    raise ValueError(f"unknown format: {fmt}")


def from_env(environ: dict, prefix: str = "APP_") -> dict:
    """APP_MAX_WORKERS=4 becomes {'max_workers': '4'}.

    An empty variable counts as unset, so it does not hide the file value.
    """
    values = {}
    for key, value in environ.items():
        if key.startswith(prefix) and value != "":
            values[key[len(prefix):].lower()] = value
    return values
