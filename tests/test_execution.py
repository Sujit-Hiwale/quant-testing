from datetime import datetime

from src.core.models import (
    Bar,
    Order,
    OrderSide,
)
from src.execution.simulator import ExecutionSimulator


def test_market_order_executes_at_bar_open():

    bar = Bar(
        timestamp=datetime(2024, 1, 2),
        symbol="TEST",
        open=105,
        high=110,
        low=100,
        close=108,
        volume=1000,
    )

    order = Order(
        symbol="TEST",
        side=OrderSide.BUY,
        quantity=10,
    )

    simulator = ExecutionSimulator()

    fill = simulator.execute(
        order,
        bar
    )

    assert fill.price == 105
    assert fill.quantity == 10
