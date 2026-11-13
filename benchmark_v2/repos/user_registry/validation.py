"""Username and password rules."""
import re

# Checked against the normalised (lower-cased) username.
USERNAME_RE = re.compile(r"^[a-z0-9_]{3,20}$")
RESERVED = {"admin", "root", "system"}
MIN_PASSWORD = 8


class ValidationError(ValueError):
    """Raised when a username, password or role breaks a rule."""


def normalize_username(name: str) -> str:
    """Usernames are compared case-insensitively, ignoring surrounding spaces."""
    return name.strip().lower()


def check_username(name: str) -> str:
    """Validate a username and return its normalised form."""
    key = normalize_username(name)
    if not USERNAME_RE.match(key):
        raise ValidationError("username must be 3-20 letters, digits or underscores")
    if key in RESERVED:
        raise ValidationError(f"username {key!r} is reserved")
    return key


def check_password(password: str, username: str) -> None:
    """At least MIN_PASSWORD characters, a letter and a digit, and not containing
    the username (in any case)."""
    problems = []
    if len(password) < MIN_PASSWORD:
        problems.append(f"must be at least {MIN_PASSWORD} characters")
    if not any(ch.isalpha() for ch in password):
        problems.append("needs a letter")
    if not any(ch.isdigit() for ch in password):
        problems.append("needs a digit")
    if normalize_username(username) in password.lower():
        problems.append("must not contain the username")
    if problems:
        raise ValidationError("password " + "; ".join(problems))
