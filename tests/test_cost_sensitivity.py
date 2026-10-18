from datetime import datetime, timedelta

from src.core.models import Bar
from src.research.cost_sensitivity import (
    CostScenario,
    run_cost_sensitivity,
)


class AlwaysBuyStrategy:
    def __init__(self):
        self.done = False

    def on_bar(self, bar):
        from src.core.models import Order, OrderSide

        if self.done:
            return None

        self.done = True

        return Order(
            symbol=bar.symbol,
            side=OrderSide.BUY,
            quantity=1,
        )


def strategy_factory():
    return AlwaysBuyStrategy()


def make_bars():
    start = datetime(2024, 1, 1)

    return [
        Bar(
            timestamp=start + timedelta(days=i),
            symbol="TEST",
            open=100 + i,
            high=101 + i,
            low=99 + i,
            close=100 + i,
            volume=1000,
        )
        for i in range(5)
    ]


def test_cost_sensitivity_returns_one_result_per_scenario():
    scenarios = [
        CostScenario(0, 0),
        CostScenario(5, 10),
        CostScenario(20, 40),
    ]

    results = run_cost_sensitivity(
        bars=make_bars(),
        strategy_factory=strategy_factory,
        initial_cash=10_000,
        scenarios=scenarios,
    )

    assert len(results) == 3


def test_higher_costs_reduce_performance():
    scenarios = [
        CostScenario(0, 0),
        CostScenario(50, 100),
    ]

    results = run_cost_sensitivity(
        bars=make_bars(),
        strategy_factory=strategy_factory,
        initial_cash=10_000,
        scenarios=scenarios,
    )

    assert (
        results[1].metrics["total_return"]
        <= results[0].metrics["total_return"]
    )
