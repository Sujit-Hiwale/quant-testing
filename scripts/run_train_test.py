import os
import sys

ROOT = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, ROOT)

from src.data.loader import load_market_data
from src.data.cleaner import clean_market_data
from src.data.validator import validate_market_data

from src.portfolio.sizing import TargetExposureSizer
from src.research.walk_forward import run_walk_forward
from src.strategies.sma_crossover import SMACrossoverStrategy
from src.research.cost_sensitivity import (
    CostScenario,
    run_cost_sensitivity,
)
from src.core.data_adapter import dataframe_to_bars

TICKER = "RELIANCE.NS"

START = "2020-01-01"
END = "2025-01-01"

INITIAL_CASH = 100_000

SLIPPAGE_BPS = 5.0
FEE_BPS = 10.0

WARMUP_BARS = 200


PARAMETER_GRID = [
    {"fast_period": 10, "slow_period": 30},
    {"fast_period": 20, "slow_period": 50},
    {"fast_period": 30, "slow_period": 100},
    {"fast_period": 50, "slow_period": 200},
]


WINDOWS = [
    {
        "train_start": "2020-01-01",
        "train_end": "2022-01-01",
        "test_start": "2022-01-01",
        "test_end": "2023-01-01",
    },
    {
        "train_start": "2021-01-01",
        "train_end": "2023-01-01",
        "test_start": "2023-01-01",
        "test_end": "2024-01-01",
    },
    {
        "train_start": "2022-01-01",
        "train_end": "2024-01-01",
        "test_start": "2024-01-01",
        "test_end": "2025-01-01",
    },
]

COST_SCENARIOS = [
    CostScenario(slippage_bps=0.0, fee_bps=0.0),
    CostScenario(slippage_bps=5.0, fee_bps=10.0),
    CostScenario(slippage_bps=10.0, fee_bps=20.0),
    CostScenario(slippage_bps=20.0, fee_bps=40.0),
    CostScenario(slippage_bps=50.0, fee_bps=100.0),
]

def strategy_factory(parameters):
    return SMACrossoverStrategy(
        symbol=TICKER,
        fast_period=parameters["fast_period"],
        slow_period=parameters["slow_period"],
    )


def position_sizer_factory():
    return TargetExposureSizer(
        target_exposure=1.0,
        cost_buffer_bps=20.0,
    )


def print_metrics(title, metrics):
    print()
    print(title)
    print("-" * 60)

    print(
        f"Total return   : "
        f"{metrics['total_return']:.2%}"
    )

    print(
        f"CAGR           : "
        f"{metrics['cagr']:.2%}"
    )

    print(
        f"Volatility     : "
        f"{metrics['annualized_volatility']:.2%}"
    )

    print(
        f"Sharpe         : "
        f"{metrics['sharpe_ratio']:.2f}"
    )

    print(
        f"Sortino        : "
        f"{metrics['sortino_ratio']:.2f}"
    )

    print(
        f"Max drawdown   : "
        f"{metrics['max_drawdown']:.2%}"
    )

    print(
        f"Trades         : "
        f"{metrics.get('trade_count', 0)}"
    )


def main():

    print("=" * 70)
    print("QUANTLAB ROLLING WALK-FORWARD RESEARCH")
    print("=" * 70)

    print()
    print(f"Ticker        : {TICKER}")
    print(f"Full period   : {START} → {END}")
    print(f"Initial cash  : ₹{INITIAL_CASH:,.2f}")
    print(f"Slippage      : {SLIPPAGE_BPS:.1f} bps")
    print(f"Fees          : {FEE_BPS:.1f} bps")
    print(f"Warm-up bars  : {WARMUP_BARS}")

    print()
    print("[1/3] Loading market data...")

    data = load_market_data(
        ticker=TICKER,
        start=START,
        end=END,
    )

    print(f"      Rows: {len(data):,}")

    print("[2/3] Cleaning and validating...")

    data = clean_market_data(data)

    validation = validate_market_data(data)

    print(
        f"      Validation: "
        f"{validation['status']}"
    )

    if validation["status"] != "PASS":
        raise ValueError(
            f"Market data validation failed: {validation}"
        )

    bars = dataframe_to_bars(
        data=data,
        symbol=TICKER,
    )
    print("[3/3] Running rolling walk-forward research...")

    result = run_walk_forward(
        data=data,
        symbol=TICKER,
        initial_cash=INITIAL_CASH,

        windows=WINDOWS,

        parameter_grid=PARAMETER_GRID,

        strategy_factory=strategy_factory,
        position_sizer_factory=position_sizer_factory,

        slippage_bps=SLIPPAGE_BPS,
        fee_bps=FEE_BPS,

        warmup_bars=WARMUP_BARS,
    )

    cost_results = run_cost_sensitivity(
        bars=bars,
        strategy_factory=lambda: SMACrossoverStrategy(
            symbol=TICKER,
            fast_period=10,
            slow_period=30,
        ),
        initial_cash=INITIAL_CASH,
        scenarios=COST_SCENARIOS,
    )

    print()
    print("=" * 70)
    print("WALK-FORWARD WINDOWS")
    print("=" * 70)

    for window in result.windows:

        selected = window.selected_parameters

        train = window.train_metrics
        test = window.test_metrics

        print()
        print(
            f"WINDOW {window.window_number}"
        )

        print(
            f"Train : "
            f"{window.train_start} → "
            f"{window.train_end}"
        )

        print(
            f"Test  : "
            f"{window.test_start} → "
            f"{window.test_end}"
        )

        print(
            f"Selected parameters : "
            f"{selected['fast_period']}/"
            f"{selected['slow_period']}"
        )

        print()
        print(
            f"Train CAGR   : "
            f"{train['cagr']:.2%}"
        )

        print(
            f"Train Sharpe : "
            f"{train['sharpe_ratio']:.2f}"
        )

        print(
            f"Train DD     : "
            f"{train['max_drawdown']:.2%}"
        )

        print()
        print(
            f"OOS CAGR     : "
            f"{test['cagr']:.2%}"
        )

        print(
            f"OOS Sharpe   : "
            f"{test['sharpe_ratio']:.2f}"
        )

        print(
            f"OOS DD       : "
            f"{test['max_drawdown']:.2%}"
        )

        print(
            f"OOS Trades   : "
            f"{test.get('trade_count', 0)}"
        )

    print()
    print("=" * 70)
    print("TRANSACTION-COST SENSITIVITY")
    print("=" * 70)

    print()
    print(
        f"{'Costs':<20}"
        f"{'CAGR':>12}"
        f"{'Sharpe':>12}"
        f"{'Max DD':>12}"
    )

    print("-" * 56)

    for cost_result in cost_results:
        scenario = cost_result.scenario
        metrics = cost_result.metrics

        label = (
            f"{scenario.slippage_bps:.0f} / "
            f"{scenario.fee_bps:.0f} bps"
        )

        print(
            f"{label:<20}"
            f"{metrics['cagr']:>11.2%}"
            f"{metrics['sharpe_ratio']:>12.2f}"
            f"{metrics['max_drawdown']:>12.2%}"
        )
    print()
    print("=" * 70)
    print("PARAMETER STABILITY")
    print("=" * 70)

    for parameters, count in sorted(
        result.parameter_selection_counts.items()
    ):
        print(
            f"{parameters:<10} "
            f"selected {count} time(s)"
        )

    print()
    print("=" * 70)
    print("COMBINED OUT-OF-SAMPLE PERFORMANCE")
    print("=" * 70)

    print_metrics(
        "ALL WALK-FORWARD TEST PERIODS",
        result.aggregate_test_metrics,
    )

    print()
    print("=" * 70)
    print("RESEARCH VERDICT")
    print("=" * 70)

    metrics = result.aggregate_test_metrics

    positive_windows = sum(
        1
        for window in result.windows
        if window.test_metrics["total_return"] > 0
    )

    strong_sharpe_windows = sum(
        1
        for window in result.windows
        if window.test_metrics["sharpe_ratio"] >= 0.5
    )

    total_windows = len(result.windows)

    print(
        f"Positive OOS windows : "
        f"{positive_windows}/{total_windows}"
    )

    print(
        f"OOS Sharpe >= 0.50   : "
        f"{strong_sharpe_windows}/{total_windows}"
    )

    print(
        f"Aggregate OOS Sharpe  : "
        f"{metrics['sharpe_ratio']:.2f}"
    )

    print(
        f"Aggregate OOS CAGR    : "
        f"{metrics['cagr']:.2%}"
    )

    print(
        f"Aggregate OOS DD      : "
        f"{metrics['max_drawdown']:.2%}"
    )

    if (
        positive_windows == total_windows
        and strong_sharpe_windows >= total_windows * 0.67
        and metrics["sharpe_ratio"] >= 0.5
    ):
        print()
        print(
            "PROMISING — the strategy demonstrates "
            "consistent out-of-sample behavior."
        )

    elif (
        positive_windows >= total_windows * 0.67
        and metrics["sharpe_ratio"] >= 0.3
    ):
        print()
        print(
            "WEAK — some evidence of robustness exists, "
            "but the edge is not yet strong enough."
        )

    else:
        print()
        print(
            "FAIL — the strategy does not demonstrate "
            "consistent out-of-sample robustness."
        )

    print()
    print("=" * 70)
    print("END OF WALK-FORWARD RESEARCH")
    print("=" * 70)


if __name__ == "__main__":
    main()