from datetime import datetime, timedelta

from src.core.engine import BacktestEngine
from src.core.models import Bar, OrderSide
from src.strategies.base import Strategy
from src.core.models import Order


class BuyOnFirstBarStrategy(Strategy):

    def __init__(self):
        self.called = False

    def on_bar(self, bar):

        if not self.called:
            self.called = True

            return Order(
                symbol=bar.symbol,
                side=OrderSide.BUY,
                quantity=1,
            )

        return None


def test_order_executes_on_next_bar():

    first = datetime(2024, 1, 1)

    bars = [
        Bar(
            timestamp=first,
            symbol="TEST",
            open=100,
            high=110,
            low=90,
            close=105,
            volume=1000,
        ),
        Bar(
            timestamp=first + timedelta(days=1),
            symbol="TEST",
            open=200,
            high=210,
            low=190,
            close=205,
            volume=1000,
        ),
    ]

    strategy = BuyOnFirstBarStrategy()

    engine = BacktestEngine(
        initial_cash=1_000,
        strategy=strategy,
    )

    result = engine.run(bars)

    assert len(result.orders) == 1

    position = engine.portfolio.positions["TEST"]

    assert position.quantity == 1

    # The first bar generated the order,
    # but execution happened on the second bar.
    assert position.average_price == 200
