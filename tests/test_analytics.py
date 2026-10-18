from datetime import datetime, timedelta

import pandas as pd

from src.analytics.metrics import calculate_metrics
from src.core.models import Trade


def test_trade_net_pnl_includes_fees():
    trade = Trade(
        symbol="TEST",
        entry_time=datetime(2024, 1, 1),
        exit_time=datetime(2024, 1, 11),
        quantity=10,
        entry_price=100,
        exit_price=120,
        entry_fee=10,
        exit_fee=10,
    )

    assert trade.gross_pnl == 200
    assert trade.net_pnl == 180
    assert trade.holding_days == 10


def test_trade_return():
    trade = Trade(
        symbol="TEST",
        entry_time=datetime(2024, 1, 1),
        exit_time=datetime(2024, 1, 11),
        quantity=10,
        entry_price=100,
        exit_price=110,
        entry_fee=0,
        exit_fee=0,
    )

    assert abs(trade.return_pct - 0.10) < 1e-9


def test_metrics_include_trade_statistics():
    dates = [
        datetime(2024, 1, 1) + timedelta(days=i)
        for i in range(5)
    ]

    equity = [
        100_000,
        101_000,
        100_500,
        102_000,
        103_000,
    ]

    curve = [
        {
            "timestamp": date,
            "equity": value,
        }
        for date, value in zip(dates, equity)
    ]

    trade = Trade(
        symbol="TEST",
        entry_time=dates[0],
        exit_time=dates[-1],
        quantity=10,
        entry_price=100,
        exit_price=110,
        entry_fee=0,
        exit_fee=0,
    )

    metrics = calculate_metrics(
        curve,
        trades=[trade],
    )

    assert metrics["trade_count"] == 1
    assert metrics["win_rate"] == 1.0
    assert metrics["profit_factor"] == float("inf")
