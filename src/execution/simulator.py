from src.core.models import Bar, Fill, Order, OrderSide


class ExecutionSimulator:
    def __init__(
        self,
        slippage_bps: float = 0.0,
        fee_bps: float = 0.0,
    ):
        if slippage_bps < 0:
            raise ValueError("slippage_bps cannot be negative.")

        if fee_bps < 0:
            raise ValueError("fee_bps cannot be negative.")

        self.slippage_bps = slippage_bps
        self.fee_bps = fee_bps

    def execute(self, order: Order, bar: Bar) -> Fill:
        if order.symbol != bar.symbol:
            raise ValueError("Order symbol does not match market bar.")

        if order.quantity <= 0:
            raise ValueError("Order quantity must be positive.")

        if order.order_type.value != "MARKET":
            raise ValueError("Only market orders are supported.")

        base_price = float(bar.open)

        # Slippage works against the trader.
        if order.side == OrderSide.BUY:
            execution_price = base_price * (
                1 + self.slippage_bps / 10_000
            )
        elif order.side == OrderSide.SELL:
            execution_price = base_price * (
                1 - self.slippage_bps / 10_000
            )
        else:
            raise ValueError(f"Unsupported order side: {order.side}")

        notional = execution_price * order.quantity
        fee = notional * self.fee_bps / 10_000

        return Fill(
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=execution_price,
            timestamp=bar.timestamp,
            fee=fee,
        )
