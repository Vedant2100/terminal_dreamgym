"""Parse dependency declarations, one 'package -> dep1, dep2' per line."""


class ParseError(ValueError):
    def __init__(self, lineno: int, message: str):
        super().__init__(f"line {lineno}: {message}")
        self.lineno = lineno  # 1-based


def parse(text: str) -> dict:
    """Return {package: [dependencies]} in declaration order.

    Blank lines and '#' comments (whole-line or trailing) are ignored. A bare
    'pkg' declares a package with no dependencies. Names are lower-cased. A
    package declared on several lines gets the dependencies of all of them,
    each listed once.
    """
    graph = {}
    for lineno, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        name, _, rest = line.partition("->")
        name = name.strip().lower()
        if not name:
            raise ParseError(lineno, "missing package name")
        deps = [d.strip().lower() for d in rest.split(",") if d.strip()]
        if name in deps:
            raise ParseError(lineno, f"{name} depends on itself")
        entry = graph.setdefault(name, [])
        for dep in deps:
            if dep not in entry:
                entry.append(dep)
    return graph
