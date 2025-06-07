from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass(frozen=True)
class OrderLine:
    def __init__(self, order_id: str, sku: str, quantity: int):
        self.order_id = order_id
        self.sku = sku
        self.quantity = quantity


class Batch:
    def __init__(
        self, *, ref_id: str, sku: str, quantity: int, eta: Optional[date] = None
    ):
        self.ref_id = ref_id
        self.sku = sku
        self.quantity = quantity
        self._allocated_order_lines = set()
        self.eta = eta

    def __lt__(self, other):
        if self.eta is None:
            return True
        elif self.eta < other.eta:
            return True
        return False

    def can_allocate_order_line(self, order_line: OrderLine) -> bool:
        if self.sku == order_line.sku and self.quantity >= order_line.quantity:
            return True
        return False

    def allocate_order_line(self, order_line: OrderLine) -> None:
        assert self.can_allocate_order_line(order_line)

        order_id = order_line.order_id
        if order_id in self._allocated_order_lines:
            return
        self.quantity -= order_line.quantity
        self._allocated_order_lines.add(order_id)

    def deallocate_order_line(self, order_line: OrderLine) -> None:
        if (order_id := order_line.order_id) not in self._allocated_order_lines:
            return
        self.quantity += order_line.quantity
        self._allocated_order_lines.remove(order_id)
