from datetime import date, timedelta
import pytest

from model import Batch, OrderLine

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_test_batch(batch_qty: int, order_qty: int):
    batch = Batch(ref_id="batch-001", sku="SMALL-TABLE", quantity=batch_qty)
    line = OrderLine(order_id="order-ref", sku="SMALL-TABLE", quantity=order_qty)

    return batch, line


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = make_test_batch(20, 2)
    batch = Batch(ref_id="batch-001", sku="SMALL-TABLE", quantity=20)
    line = OrderLine(order_id="order-ref", sku="SMALL-TABLE", quantity=2)

    batch.allocate_order_line(line)
    assert batch.quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch, line = make_test_batch(20, 4)

    can_allocate = batch.can_allocate_order_line(line)
    assert can_allocate


def test_cannot_allocate_if_available_smaller_than_required():
    batch, line = make_test_batch(2, 4)

    can_allocate = batch.can_allocate_order_line(line)
    assert not can_allocate


def test_can_allocate_if_available_equal_to_required():
    batch, line = make_test_batch(2, 2)

    can_allocate = batch.can_allocate_order_line(line)
    assert can_allocate


def test_prefers_warehouse_batches_to_shipments():
    warehouse_batch = Batch(ref_id="batch-001", sku="SMALL-TABLE", quantity=2)
    tomorrow_batch = Batch(
        ref_id="batch-002", sku="SMALL-TABLE", quantity=2, eta=tomorrow
    )
    batches = [tomorrow_batch, warehouse_batch]
    batches.sort()

    assert batches[0] == warehouse_batch


def test_prefers_earlier_batches():
    tomorrow_batch = Batch(
        ref_id="batch-002", sku="SMALL-TABLE", quantity=2, eta=tomorrow
    )
    later_batch = Batch(ref_id="batch-001", sku="SMALL-TABLE", quantity=2, eta=later)
    batches = [later_batch, tomorrow_batch]
    batches.sort()

    assert batches[0] == tomorrow_batch
