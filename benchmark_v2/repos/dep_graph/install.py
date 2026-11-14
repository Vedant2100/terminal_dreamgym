"""Installation order: every package after the packages it depends on."""
import heapq

from graph import CycleError, DepGraph


def closure(graph: DepGraph, targets) -> set:
    """`targets` plus everything they depend on, directly or indirectly."""
    seen = set()
    stack = [t.lower() for t in targets]
    while stack:
        name = stack.pop()
        if name not in graph.deps:
            raise KeyError(f"unknown package: {name}")
        if name not in seen:
            seen.add(name)
            stack.extend(graph.deps[name])
    return seen


def install_order(graph: DepGraph, targets=None) -> list:
    """Packages in install order (Kahn's algorithm).

    Among packages that are ready at the same time, the alphabetically first
    goes first. With `targets`, only those packages and what they need are
    included. Raises CycleError with the cycle's path if there is one.
    """
    cycle = graph.find_cycle()
    if cycle:
        raise CycleError(cycle)
    needed = set(graph.deps) if targets is None else closure(graph, targets)
    # Number of not-yet-installed dependencies of each package.
    remaining = {n: len(graph.deps[n]) for n in graph.deps if n in needed}
    ready = [n for n, count in remaining.items() if count == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for parent in graph.dependents(node):
            if parent in remaining:
                remaining[parent] -= 1
                if remaining[parent] == 0:
                    heapq.heappush(ready, parent)
    return order
