"""Version constraints like '>=1.2.0,<2.0.0', '^1.2' or '~1.4.2', and picking versions."""
import operator

from version import Version, bump, parse

_OPS = {">=": operator.ge, "<=": operator.le, ">": operator.gt, "<": operator.lt,
        "==": operator.eq, "!=": operator.ne, "=": operator.eq}


def _partial(text: str) -> Version:
    """'1' -> 1.0.0 and '1.2' -> 1.2.0; full versions are parsed as they are."""
    parts = text.strip().split(".")
    parts += ["0"] * (3 - len(parts))
    return parse(".".join(parts))


def _caret(v: Version) -> list:
    # ^1.2.3 := >=1.2.3,<2.0.0   ^0.2.3 := >=0.2.3,<0.3.0   ^0.0.3 := >=0.0.3,<0.0.4
    if v.major > 0:
        upper = Version(v.major + 1, 0, 0)
    elif v.minor > 0:
        upper = Version(0, v.minor + 1, 0)
    else:
        upper = Version(0, 0, v.patch + 1)
    return [(">=", v), ("<", upper)]


def parse_constraint(text: str) -> list:
    """A list of (operator, Version) terms; a version must satisfy all of them."""
    terms = []
    for part in text.split(","):
        part = part.strip()
        if part.startswith("^"):
            terms += _caret(_partial(part[1:]))
        elif part.startswith("~"):
            low = _partial(part[1:])
            terms += [(">=", low), ("<", bump(low, "minor"))]
        else:
            op = next((o for o in (">=", "<=", "==", "!=", ">", "<", "=") if part.startswith(o)), "==")
            terms.append((op, _partial(part[len(op):] if part.startswith(op) else part)))
    return terms


def satisfies(version, constraint: str, include_pre: bool = False) -> bool:
    """True if version meets every term. Pre-releases only match with include_pre."""
    v = parse(version) if isinstance(version, str) else version
    if v.pre and not include_pre:
        return False
    return all(_OPS[op](v, bound) for op, bound in parse_constraint(constraint))


def best_match(available: list, constraint: str, include_pre: bool = False):
    """The highest version string in available that satisfies constraint, or None."""
    matches = [text for text in available if satisfies(text, constraint, include_pre)]
    return max(matches, key=parse) if matches else None


def resolve(requirements: dict, index: dict) -> dict:
    """Pick a version for each {name: constraint} from index {name: [versions]}.

    Raises KeyError for a package missing from the index and LookupError when
    no listed version satisfies the constraint.
    """
    chosen = {}
    for name, constraint in requirements.items():
        if name not in index:
            raise KeyError(f"unknown package: {name}")
        best = best_match(index[name], constraint)
        if best is None:
            raise LookupError(f"no version of {name} satisfies {constraint!r}")
        chosen[name] = best
    return chosen
