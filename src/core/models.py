from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"


@dataclass(frozen=True)
class Bar:
    timestamp: datetime
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True)
class Order:
    symbol: str
    side: OrderSide
    quantity: int
    order_type: OrderType = OrderType.MARKET


@dataclass(frozen=True)
class Fill:
    symbol: str
    side: OrderSide
    quantity: int
    price: float
    timestamp: datetime
    fee: float = 0.0


@dataclass(frozen=True)
class Trade:
    symbol: str
    entry_time: datetime
    exit_time: datetime
    quantity: int
    entry_price: float
    exit_price: float
    entry_fee: float
    exit_fee: float

    @property
    def gross_pnl(self) -> float:
        return (
            self.exit_price - self.entry_price
        ) * self.quantity

    @property
    def net_pnl(self) -> float:
        return (
            self.gross_pnl
            - self.entry_fee
            - self.exit_fee
        )

    @property
    def return_pct(self) -> float:
        invested = (
            self.entry_price * self.quantity
            + self.entry_fee
        )

        if invested <= 0:
            return 0.0

        return self.net_pnl / invested

    @property
    def holding_days(self) -> int:
        return (self.exit_time - self.entry_time).days
