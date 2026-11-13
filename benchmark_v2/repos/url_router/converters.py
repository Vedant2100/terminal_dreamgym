"""Path parameter converters: a regex, conversion to Python, and back to URL text."""
import re
from urllib.parse import quote, unquote


class Converter:
    """Default 'str' converter: one path segment, percent-decoded."""

    regex = r"[^/]+"

    def to_python(self, text: str):
        return unquote(text)

    def to_url(self, value) -> str:
        # A str parameter is a single segment, so '/' must be encoded too.
        return quote(str(value), safe="")


class IntConverter(Converter):
    regex = r"\d+"

    def to_python(self, text: str):
        return int(text)

    def to_url(self, value) -> str:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"not a non-negative int: {value!r}")
        return str(value)


class SlugConverter(Converter):
    regex = r"[a-z0-9]+(?:-[a-z0-9]+)*"

    def to_url(self, value) -> str:
        if not re.fullmatch(self.regex, str(value)):
            raise ValueError(f"not a slug: {value!r}")
        return str(value)


class PathConverter(Converter):
    """Like str, but may span several segments; slashes are kept when building."""

    regex = r".+"

    def to_url(self, value) -> str:
        return quote(str(value), safe="/")


CONVERTERS = {"str": Converter(), "int": IntConverter(), "slug": SlugConverter(), "path": PathConverter()}
