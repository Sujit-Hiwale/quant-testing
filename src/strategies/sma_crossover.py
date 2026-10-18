from collections import deque

from src.core.models import Bar, Order, OrderSide
from src.strategies.base import Strategy


class SMACrossoverStrategy(Strategy):
    def __init__(
        self,
        symbol: str,
        fast_period: int = 20,
        slow_period: int = 50,
    ):
        if fast_period >= slow_period:
            raise ValueError(
                "fast_period must be smaller than slow_period."
            )

        self.symbol = symbol
        self.fast_period = fast_period
        self.slow_period = slow_period

        self.prices = deque(maxlen=slow_period)
        self.in_position = False

    def on_bar(self, bar: Bar) -> Order | None:
        if bar.symbol != self.symbol:
            return None

        self.prices.append(bar.close)

        if len(self.prices) < self.slow_period:
            return None

        prices = list(self.prices)

        fast_sma = (
            sum(prices[-self.fast_period:])
            / self.fast_period
        )

        slow_sma = sum(prices) / self.slow_period

        if fast_sma > slow_sma and not self.in_position:
            self.in_position = True

            return Order(
                symbol=self.symbol,
                side=OrderSide.BUY,
                quantity=1,
            )

        if fast_sma < slow_sma and self.in_position:
            self.in_position = False

            return Order(
                symbol=self.symbol,
                side=OrderSide.SELL,
                quantity=1,
            )

        return None