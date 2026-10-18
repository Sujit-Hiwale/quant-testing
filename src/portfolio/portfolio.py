from dataclasses import dataclass, field

from src.core.models import Fill, OrderSide


@dataclass
class Position:
    quantity: int = 0
    average_price: float = 0.0


@dataclass
class Portfolio:
    initial_cash: float
    cash: float = field(init=False)
    positions: dict[str, Position] = field(default_factory=dict, init=False)
    realized_pnl: float = field(default=0.0, init=False)
    total_fees: float = field(default=0.0, init=False)

    def __post_init__(self):
        if self.initial_cash <= 0:
            raise ValueError("Initial cash must be greater than zero.")

        self.cash = float(self.initial_cash)

    def apply_fill(self, fill: Fill) -> None:
        position = self.positions.setdefault(fill.symbol, Position())

        if fill.side == OrderSide.BUY:
            self._buy(position, fill)

        elif fill.side == OrderSide.SELL:
            self._sell(position, fill)

        else:
            raise ValueError(f"Unsupported order side: {fill.side}")

        self.total_fees += fill.fee

    def _buy(self, position: Position, fill: Fill) -> None:
        cost = fill.price * fill.quantity
        total_cost = cost + fill.fee

        if total_cost > self.cash:
            raise ValueError("Insufficient cash for order.")

        new_quantity = position.quantity + fill.quantity

        if new_quantity > 0:
            position.average_price = (
                (position.quantity * position.average_price) + cost
            ) / new_quantity

        position.quantity = new_quantity
        self.cash -= total_cost

    def _sell(self, position: Position, fill: Fill) -> None:
        if fill.quantity > position.quantity:
            raise ValueError("Cannot sell more shares than held.")

        proceeds = fill.price * fill.quantity

        self.realized_pnl += (
            (fill.price - position.average_price) * fill.quantity
            - fill.fee
        )

        position.quantity -= fill.quantity
        self.cash += proceeds - fill.fee

        if position.quantity == 0:
            position.average_price = 0.0

    def market_value(self, prices: dict[str, float]) -> float:
        value = 0.0

        for symbol, position in self.positions.items():
            price = prices.get(symbol)

            if price is None:
                continue

            value += position.quantity * price

        return value

    def equity(self, prices: dict[str, float]) -> float:
        return self.cash + self.market_value(prices)
