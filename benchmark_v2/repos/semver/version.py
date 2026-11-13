"""Semantic versions: MAJOR.MINOR.PATCH with optional -prerelease and +build parts."""
import re
from dataclasses import dataclass
from functools import total_ordering

_VERSION = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z.-]+))?(?:\+([0-9A-Za-z.-]+))?$")


def _pre_key(pre: tuple) -> tuple:
    # A release sorts after all of its pre-releases. Numeric identifiers compare
    # as numbers and sort before alphanumeric ones; a shorter prefix sorts first.
    if not pre:
        return (1,)
    return (0, tuple((0, int(p), "") if p.isdigit() else (1, 0, p) for p in pre))


@total_ordering
@dataclass(frozen=True, eq=False)
class Version:
    major: int
    minor: int
    patch: int
    pre: tuple = ()
    build: str = ""

    def _key(self) -> tuple:
        # Build metadata never affects ordering or equality.
        return (self.major, self.minor, self.patch, _pre_key(self.pre))

    def __eq__(self, other) -> bool:
        return self._key() == other._key()

    def __lt__(self, other) -> bool:
        return self._key() < other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    def __str__(self) -> str:
        text = f"{self.major}.{self.minor}.{self.patch}"
        if self.pre:
            text += "-" + ".".join(self.pre)
        if self.build:
            text += "+" + self.build
        return text


def parse(text: str) -> Version:
    """Parse '1.2.3', 'v1.2.3', '1.0.0-rc.1' or '1.0.0+build.7'. Raises ValueError."""
    match = _VERSION.match(text.strip())
    if not match:
        raise ValueError(f"invalid version: {text!r}")
    major, minor, patch, pre, build = match.groups()
    return Version(int(major), int(minor), int(patch), tuple(pre.split(".")) if pre else (), build or "")


def bump(version: Version, part: str) -> Version:
    """The next release: lower parts reset to 0, pre-release and build dropped."""
    if part == "major":
        return Version(version.major + 1, 0, 0)
    if part == "minor":
        return Version(version.major, version.minor + 1, 0)
    if part == "patch":
        return Version(version.major, version.minor, version.patch + 1)
    raise ValueError(f"unknown part: {part}")


def sort_versions(texts: list) -> list:
    """Sort version strings from lowest to highest, keeping their original spelling."""
    return sorted(texts, key=parse)
