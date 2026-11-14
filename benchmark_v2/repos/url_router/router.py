"""Route table: dispatch (method, path) to a handler and build URLs by route name."""
from dataclasses import dataclass

from patterns import Pattern


class NotFound(LookupError):
    status = 404

    def __init__(self, path: str):
        super().__init__(f"not found: {path}")


class MethodNotAllowed(LookupError):
    status = 405

    def __init__(self, allowed: list):
        super().__init__(f"method not allowed; allowed: {', '.join(allowed)}")
        self.allowed = allowed


@dataclass
class Route:
    pattern: Pattern
    methods: frozenset
    handler: object
    name: str


class Router:
    def __init__(self):
        self.routes = []
        self.by_name = {}

    def add(self, pattern: str, handler, methods=("GET",), name=None) -> Route:
        route = Route(Pattern(pattern), frozenset(m.upper() for m in methods), handler, name or handler.__name__)
        if route.name in self.by_name:
            raise ValueError(f"duplicate route name: {route.name}")
        self.routes.append(route)
        self.by_name[route.name] = route
        return route

    def match(self, method: str, path: str):
        """Return (handler, params) for the first route, in the order added, that fits.

        HEAD is accepted wherever GET is. If the path matches only under other
        methods, raise MethodNotAllowed with all of them (sorted); else NotFound.
        """
        method = method.upper()
        allowed = set()
        for route in self.routes:
            params = route.pattern.match(path)
            if params is None:
                continue
            if method in route.methods or (method == "HEAD" and "GET" in route.methods):
                return route.handler, params
            allowed |= route.methods
        if allowed:
            raise MethodNotAllowed(sorted(allowed))
        raise NotFound(path)

    def dispatch(self, method: str, path: str):
        """Call the handler and return (status, body); 404/405 become (status, message)."""
        try:
            handler, params = self.match(method, path)
        except (NotFound, MethodNotAllowed) as exc:
            return exc.status, str(exc)
        return 200, handler(**params)

    def url_for(self, name: str, **params) -> str:
        return self.by_name[name].pattern.build(**params)
