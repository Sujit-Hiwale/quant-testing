from math import floor

from src.core.models import OrderSide
from src.portfolio.portfolio import Portfolio


class PositionSizer:
    def quantity(
        self,
        portfolio: Portfolio,
        symbol: str,
        price: float,
        side: OrderSide,
    ) -> int:
        raise NotImplementedError


class FixedQuantitySizer(PositionSizer):
    def __init__(self, quantity: int):
        if quantity <= 0:
            raise ValueError("quantity must be positive.")

        self.quantity_value = quantity

    def quantity(
        self,
        portfolio: Portfolio,
        symbol: str,
        price: float,
        side: OrderSide,
    ) -> int:
        if side == OrderSide.SELL:
            position = portfolio.positions.get(symbol)
            return position.quantity if position else 0

        return self.quantity_value


class TargetExposureSizer(PositionSizer):
    def __init__(
        self,
        target_exposure: float,
        cost_buffer_bps: float = 20.0,
    ):
        if not 0 < target_exposure <= 1:
            raise ValueError(
                "target_exposure must be between 0 and 1."
            )

        if cost_buffer_bps < 0:
            raise ValueError(
                "cost_buffer_bps cannot be negative."
            )

        self.target_exposure = target_exposure
        self.cost_buffer_bps = cost_buffer_bps

    def quantity(
        self,
        portfolio: Portfolio,
        symbol: str,
        price: float,
        side: OrderSide,
    ) -> int:
        if price <= 0:
            raise ValueError("price must be positive.")

        position = portfolio.positions.get(symbol)

        if side == OrderSide.SELL:
            return position.quantity if position else 0

        equity = portfolio.equity({symbol: price})

        target_value = equity * self.target_exposure

        current_quantity = (
            position.quantity
            if position
            else 0
        )

        current_value = current_quantity * price

        additional_value = (
            target_value - current_value
        )

        if additional_value <= 0:
            return 0

        # Leave a small buffer for the difference between
        # signal price and execution price plus transaction costs.
        effective_price = price * (
            1 + self.cost_buffer_bps / 10_000
        )

        quantity = floor(
            additional_value / effective_price
        )

        # Never generate an order that cannot be funded.
        while quantity > 0:
            estimated_cost = (
                quantity
                * effective_price
            )

            if estimated_cost <= portfolio.cash:
                break

            quantity -= 1

        return quantity