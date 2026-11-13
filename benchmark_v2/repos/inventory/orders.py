"""Orders: every line is allocated or none is; then the order ships or is cancelled."""
from stock import InsufficientStock


class Order:
    def __init__(self, order_id: str, lines: dict):
        """lines maps SKU to quantity."""
        self.order_id = order_id
        self.lines = dict(lines)
        self.allocations = {}  # sku -> list of (site, units)
        self.status = "new"

    def place(self, network) -> bool:
        """Allocate all lines. If any line cannot be filled, release the lines
        already allocated, mark the order 'backordered' and return False."""
        for sku, qty in self.lines.items():
            try:
                self.allocations[sku] = network.allocate(sku, qty)
            except InsufficientStock:
                self.cancel(network)
                self.status = "backordered"
                return False
        self.status = "allocated"
        return True

    def cancel(self, network) -> None:
        for sku, plan in self.allocations.items():
            network.release(plan, sku)
        self.allocations = {}
        self.status = "cancelled"

    def ship(self, network) -> None:
        if self.status != "allocated":
            raise RuntimeError(f"order {self.order_id} is {self.status}, cannot ship")
        for sku, plan in self.allocations.items():
            for site, units in plan:
                network.sites[site].ship(sku, units)
        self.status = "shipped"

    def picking_list(self) -> dict:
        """What to pick at each site: {site: {sku: units}}."""
        out = {}
        for sku, plan in self.allocations.items():
            for site, units in plan:
                out.setdefault(site, {})[sku] = units
        return out
