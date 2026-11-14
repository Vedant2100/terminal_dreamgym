"""A package dependency graph."""
from manifest import parse


class CycleError(Exception):
    """Raised for a dependency cycle; `cycle` is the path, e.g. ['a', 'b', 'a']."""

    def __init__(self, cycle: list):
        super().__init__("dependency cycle: " + " -> ".join(cycle))
        self.cycle = cycle


class DepGraph:
    def __init__(self, deps: dict):
        # Every dependency is a node, even if it is never declared itself.
        self.deps = {name: list(ds) for name, ds in deps.items()}
        for ds in deps.values():
            for dep in ds:
                self.deps.setdefault(dep, [])

    @classmethod
    def from_text(cls, text: str) -> "DepGraph":
        return cls(parse(text))

    def dependents(self, name: str, transitive: bool = False) -> list:
        """Sorted packages that depend on `name` directly (or also indirectly)."""
        if name not in self.deps:
            raise KeyError(name)
        found = set()
        frontier = [name]
        while frontier:
            current = frontier.pop()
            for pkg, ds in self.deps.items():
                if current in ds and pkg not in found:
                    found.add(pkg)
                    if transitive:
                        frontier.append(pkg)
        return sorted(found)

    def find_cycle(self):
        """One cycle as a closed path [a, b, ..., a], or None.

        Depth-first search visiting nodes and dependencies in sorted order; the
        path starts at the first node of the cycle that the search reached.
        """
        white, grey, black = 0, 1, 2
        color = dict.fromkeys(self.deps, white)
        stack = []

        def visit(node):
            color[node] = grey
            stack.append(node)
            for dep in sorted(self.deps[node]):
                if color[dep] == grey:
                    return stack[stack.index(dep):] + [dep]
                if color[dep] == white:
                    found = visit(dep)
                    if found:
                        return found
            stack.pop()
            color[node] = black
            return None

        for node in sorted(self.deps):
            if color[node] == white:
                found = visit(node)
                if found:
                    return found
        return None
