"""A network of warehouses. Reservations are split across sites in priority order."""
from stock import InsufficientStock, Stock


class Network:
    def __init__(self, names):
        """names: warehouse names in priority order (the first is preferred)."""
        self.order = list(names)
        self.sites = {name: Stock() for name in self.order}

    def receive(self, site: str, sku: str, qty: int) -> None:
        if site not in self.sites:
            raise KeyError(f"unknown warehouse: {site}")
        self.sites[site].receive(sku, qty)

    def total_available(self, sku: str) -> int:
        return sum(stock.available(sku) for stock in self.sites.values())

    def low_stock(self, threshold: int) -> list:
        """SKUs whose network-wide available units are at or below threshold, sorted."""
        skus = {sku for stock in self.sites.values() for sku in stock.on_hand}
        return sorted(sku for sku in skus if self.total_available(sku) <= threshold)

    def allocate(self, sku: str, qty: int) -> list:
        """Reserve qty units, taking from warehouses in priority order.

        Returns a list of (site, units) pairs. Nothing is reserved if the network
        as a whole cannot cover the request.
        """
        have = self.total_available(sku)
        if qty > have:
            raise InsufficientStock(f"{sku}: want {qty}, network has {have}")
        plan = []
        remaining = qty
        for name in self.order:
            if remaining == 0:
                break
            take = min(remaining, self.sites[name].available(sku))
            if take > 0:
                self.sites[name].reserve(sku, take)
                plan.append((name, take))
                remaining -= take
        return plan

    def release(self, plan: list, sku: str) -> None:
        """Undo an allocation returned by allocate()."""
        for name, units in plan:
            self.sites[name].release(sku, units)
