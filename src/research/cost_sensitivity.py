from dataclasses import dataclass
from typing import Callable

from src.analytics.metrics import calculate_metrics
from src.core.engine import BacktestEngine
from src.core.models import Bar
from src.portfolio.sizing import PositionSizer, TargetExposureSizer


@dataclass(frozen=True)
class CostScenario:
    slippage_bps: float
    fee_bps: float


@dataclass(frozen=True)
class CostSensitivityResult:
    slippage_bps: float
    fee_bps: float
    metrics: dict[str, float]


def run_cost_sensitivity(
    bars: list[Bar],
    strategy_factory: Callable[[], object],
    initial_cash: float,
    scenarios: list[CostScenario],
    position_sizer_factory: Callable[[CostScenario], PositionSizer]
    | None = None,
) -> list[CostSensitivityResult]:
    if not bars:
        raise ValueError("Cannot run cost sensitivity with no bars.")

    if initial_cash <= 0:
        raise ValueError("initial_cash must be greater than zero.")

    results: list[CostSensitivityResult] = []

    for scenario in scenarios:
        if position_sizer_factory is not None:
            position_sizer = position_sizer_factory(scenario)
        else:
            position_sizer = TargetExposureSizer(
                target_exposure=1.0,
                cost_buffer_bps=(
                    scenario.slippage_bps
                    + scenario.fee_bps
                    + 10.0
                ),
            )

        engine = BacktestEngine(
            initial_cash=initial_cash,
            strategy=strategy_factory(),
            position_sizer=position_sizer,
            slippage_bps=scenario.slippage_bps,
            fee_bps=scenario.fee_bps,
        )

        result = engine.run(bars)

        metrics = calculate_metrics(
            result.equity_curve,
            result.trades,
        )

        results.append(
            CostSensitivityResult(
                slippage_bps=scenario.slippage_bps,
                fee_bps=scenario.fee_bps,
                metrics=metrics,
            )
        )

    return results