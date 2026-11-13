"""Compile route patterns like '/users/<int:id>/posts/<slug>' to regexes.

A parameter is '<name>' (a str parameter) or '<kind:name>' with a kind from
converters.CONVERTERS. Everything outside parameters is matched literally.
"""
import re

from converters import CONVERTERS

PARAM_RE = re.compile(r"<(?:(?P<kind>\w+):)?(?P<name>\w+)>")


class Pattern:
    def __init__(self, text: str):
        if not text.startswith("/"):
            raise ValueError(f"pattern must start with '/': {text!r}")
        self.text = text
        self.params = {}  # name -> converter, in order of appearance
        parts = []
        pos = 0
        for m in PARAM_RE.finditer(text):
            parts.append(re.escape(text[pos:m.start()]))
            kind, name = m["kind"] or "str", m["name"]
            if kind not in CONVERTERS:
                raise ValueError(f"unknown converter: {kind}")
            converter = CONVERTERS[kind]
            if name in self.params:
                raise ValueError(f"duplicate parameter: {name}")
            self.params[name] = converter
            parts.append(f"(?P<{name}>{converter.regex})")
            pos = m.end()
        parts.append(re.escape(text[pos:]))
        self.regex = re.compile("".join(parts))

    def match(self, path: str):
        """Converted parameters if the whole path matches, otherwise None."""
        m = self.regex.fullmatch(path)
        if m is None:
            return None
        return {name: conv.to_python(m[name]) for name, conv in self.params.items()}

    def build(self, **values) -> str:
        """Fill in every parameter. Missing or unexpected names raise ValueError."""
        missing = set(self.params) - set(values)
        extra = set(values) - set(self.params)
        if missing or extra:
            raise ValueError(f"{self.text}: missing {sorted(missing)}, unexpected {sorted(extra)}")
        return PARAM_RE.sub(lambda m: self.params[m["name"]].to_url(values[m["name"]]), self.text)
