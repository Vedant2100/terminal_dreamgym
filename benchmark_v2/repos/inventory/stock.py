"""Stock levels for one warehouse: on-hand and reserved units per SKU."""


class InsufficientStock(Exception):
    """Raised when a reservation asks for more units than are available."""


class Stock:
    def __init__(self):
        self.on_hand = {}
        self.reserved = {}

    def receive(self, sku: str, qty: int) -> None:
        """Add received units to on-hand stock. The quantity must be positive."""
        if qty <= 0:
            raise ValueError("quantity must be positive")
        self.on_hand[sku] = self.on_hand.get(sku, 0) + qty

    def available(self, sku: str) -> int:
        """Units that can still be reserved: on hand minus reserved."""
        return self.on_hand.get(sku, 0) - self.reserved.get(sku, 0)

    def reserve(self, sku: str, qty: int) -> None:
        """Hold units for an order. Reserving exactly what is available is fine."""
        if qty <= 0:
            raise ValueError("quantity must be positive")
        if qty > self.available(sku):
            raise InsufficientStock(f"{sku}: want {qty}, have {self.available(sku)}")
        self.reserved[sku] = self.reserved.get(sku, 0) + qty

    def release(self, sku: str, qty: int) -> None:
        """Return reserved units to available stock (e.g. a cancelled order)."""
        held = self.reserved.get(sku, 0)
        if qty > held:
            raise ValueError(f"{sku}: cannot release {qty}, only {held} reserved")
        self.reserved[sku] = held - qty

    def ship(self, sku: str, qty: int) -> None:
        """Ship reserved units: they leave both the reservation and on-hand stock."""
        self.release(sku, qty)
        self.on_hand[sku] -= qty
