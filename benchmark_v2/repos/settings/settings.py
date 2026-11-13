"""Layered settings: defaults < config file < environment."""
from dataclasses import dataclass

from coerce import coerce
from sources import from_env, parse_text


@dataclass
class Field:
    name: str
    kind: str = "str"  # one of coerce.CONVERTERS
    default: object = None
    required: bool = False


class SettingsError(ValueError):
    """A setting has a value that cannot be converted."""


class MissingSetting(Exception):
    """One or more required settings have no value."""


def load(fields, text: str = "", fmt: str = "ini", environ=None) -> dict:
    """Resolve every field to a typed value.

    The environment wins over the file, which wins over the default. File and
    environment values are coerced to the field's kind; defaults are used as given.
    Required fields with no value raise MissingSetting naming all of them at once.
    """
    file_values = parse_text(text, fmt) if text.strip() else {}
    env_values = from_env(environ or {})
    result = {}
    missing = []
    for field in fields:
        if field.name in env_values:
            raw = env_values[field.name]
        elif field.name in file_values:
            raw = file_values[field.name]
        else:
            if field.required:
                missing.append(field.name)
            else:
                result[field.name] = field.default
            continue
        try:
            result[field.name] = coerce(raw, field.kind)
        except ValueError as exc:
            raise SettingsError(f"{field.name}: {exc}") from None
    if missing:
        raise MissingSetting("missing required settings: " + ", ".join(missing))
    return result
