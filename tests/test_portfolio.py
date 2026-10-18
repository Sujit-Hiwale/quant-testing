from datetime import datetime

from src.core.models import Fill, OrderSide
from src.portfolio.portfolio import Portfolio


def test_buy_reduces_cash():

    portfolio = Portfolio(
        initial_cash=100_000
    )

    fill = Fill(
        symbol="TEST",
        side=OrderSide.BUY,
        quantity=10,
        price=100,
        timestamp=datetime(2024, 1, 1),
    )

    portfolio.apply_fill(fill)

    assert portfolio.cash == 99_000
    assert portfolio.positions["TEST"].quantity == 10


def test_sell_creates_realized_profit():

    portfolio = Portfolio(
        initial_cash=100_000
    )

    buy = Fill(
        symbol="TEST",
        side=OrderSide.BUY,
        quantity=10,
        price=100,
        timestamp=datetime(2024, 1, 1),
    )

    sell = Fill(
        symbol="TEST",
        side=OrderSide.SELL,
        quantity=10,
        price=120,
        timestamp=datetime(2024, 1, 2),
    )

    portfolio.apply_fill(buy)
    portfolio.apply_fill(sell)

    assert portfolio.cash == 100_200
    assert portfolio.realized_pnl == 200
    assert portfolio.positions["TEST"].quantity == 0
