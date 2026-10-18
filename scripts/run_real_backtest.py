from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.analytics.benchmark import buy_and_hold_equity_curve
from src.analytics.metrics import calculate_metrics
from src.analytics.verdict import generate_verdict
from src.core.data_adapter import dataframe_to_bars
from src.core.engine import BacktestEngine
from src.data.cleaner import clean_market_data
from src.data.loader import load_market_data
from src.data.validator import validate_market_data
from src.execution.simulator import ExecutionSimulator
from src.portfolio.sizing import (
    FixedQuantitySizer,
    TargetExposureSizer,
)
from src.strategies.sma_crossover import SMACrossoverStrategy


TICKER = "RELIANCE.NS"
START = "2020-01-01"
END = "2025-01-01"

INITIAL_CASH = 100_000

SLIPPAGE_BPS = 5.0
FEE_BPS = 10.0


def percent(value: float) -> str:
    return f"{value * 100:.2f}%"


def run_experiment(
    name: str,
    bars,
    initial_cash: float,
    position_sizer,
):
    strategy = SMACrossoverStrategy(
        symbol=TICKER,
        fast_period=20,
        slow_period=50,
    )

    engine = BacktestEngine(
        initial_cash=initial_cash,
        strategy=strategy,
        position_sizer=position_sizer,
    )

    engine.execution = ExecutionSimulator(
        slippage_bps=SLIPPAGE_BPS,
        fee_bps=FEE_BPS,
    )

    result = engine.run(bars)

    metrics = calculate_metrics(
        result.equity_curve,
        trades=result.trades,
    )

    return engine, result, metrics


def print_experiment_result(
    name: str,
    engine,
    result,
    metrics,
):
    print()
    print("=" * 64)
    print(name)
    print("=" * 64)

    final_equity = result.equity_curve[-1]["equity"]

    print(f"Initial equity : ₹{INITIAL_CASH:,.2f}")
    print(f"Final equity   : ₹{final_equity:,.2f}")
    print(f"Total return   : {percent(metrics['total_return'])}")
    print(f"CAGR           : {percent(metrics['cagr'])}")
    print(
        f"Volatility     : "
        f"{percent(metrics['annualized_volatility'])}"
    )
    print(f"Sharpe         : {metrics['sharpe_ratio']:.2f}")
    print(f"Sortino        : {metrics['sortino_ratio']:.2f}")
    print(f"Max drawdown   : {percent(metrics['max_drawdown'])}")

    print()
    print(f"Trades         : {metrics['trade_count']}")
    print(f"Win rate       : {percent(metrics['win_rate'])}")
    print(f"Profit factor  : {metrics['profit_factor']:.2f}")
    print(
        f"Avg trade      : "
        f"{percent(metrics['average_trade_return'])}"
    )
    print(
        f"Avg holding    : "
        f"{metrics['average_holding_days']:.1f} days"
    )

    print(f"Total fees     : ₹{engine.portfolio.total_fees:,.2f}")


def print_trade_ledger(result):
    print()
    print("=" * 64)
    print("TRADE LEDGER")
    print("=" * 64)

    if not result.trades:
        print("No completed trades.")
        return

    for index, trade in enumerate(result.trades, start=1):
        print(
            f"{index:02d}. "
            f"{trade.entry_time.date()} → "
            f"{trade.exit_time.date()} | "
            f"{trade.quantity} shares | "
            f"₹{trade.entry_price:.2f} → "
            f"₹{trade.exit_price:.2f} | "
            f"P&L ₹{trade.net_pnl:.2f} | "
            f"{percent(trade.return_pct)}"
        )


def main():
    print("=" * 64)
    print("QUANTLAB REAL MARKET BACKTEST")
    print("=" * 64)

    print(f"Ticker    : {TICKER}")
    print(f"Period    : {START} → {END}")
    print(f"Cash      : ₹{INITIAL_CASH:,.2f}")
    print(f"Slippage  : {SLIPPAGE_BPS:.1f} bps")
    print(f"Fees      : {FEE_BPS:.1f} bps")
    print()

    # ---------------------------------------------------------
    # Data
    # ---------------------------------------------------------

    print("[1/5] Loading market data...")

    data = load_market_data(
        ticker=TICKER,
        start=START,
        end=END,
    )

    print(f"      Raw rows: {len(data):,}")

    print("[2/5] Cleaning market data...")

    data = clean_market_data(data)

    print(f"      Clean rows: {len(data):,}")

    print("[3/5] Validating market data...")

    validation = validate_market_data(data)

    print(f"      Status: {validation['status']}")

    if validation["status"] != "PASS":
        print("      Validation failed:")
        print(validation)
        return

    print("[4/5] Converting to engine bars...")

    bars = dataframe_to_bars(
        data=data,
        symbol=TICKER,
    )

    print(f"      Bars: {len(bars):,}")

    # ---------------------------------------------------------
    # Benchmark
    # ---------------------------------------------------------

    benchmark_curve = buy_and_hold_equity_curve(
        data=data,
        initial_cash=INITIAL_CASH,
    )

    benchmark_metrics = calculate_metrics(
        benchmark_curve,
    )

    # ---------------------------------------------------------
    # Experiments
    # ---------------------------------------------------------

    print("[5/5] Running portfolio sizing experiments...")

    experiments = [
        (
            "EXPERIMENT 1 — Fixed 10 Shares",
            FixedQuantitySizer(10),
        ),
        (
            "EXPERIMENT 2 — 25% Portfolio Exposure",
            TargetExposureSizer(0.25),
        ),
        (
            "EXPERIMENT 3 — 100% Portfolio Exposure",
            TargetExposureSizer(1.00),
        ),
    ]

    experiment_results = []

    for name, position_sizer in experiments:
        engine, result, metrics = run_experiment(
            name=name,
            bars=bars,
            initial_cash=INITIAL_CASH,
            position_sizer=position_sizer,
        )

        experiment_results.append(
            {
                "name": name,
                "engine": engine,
                "result": result,
                "metrics": metrics,
            }
        )

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    for experiment in experiment_results:
        print_experiment_result(
            experiment["name"],
            experiment["engine"],
            experiment["result"],
            experiment["metrics"],
        )

    # ---------------------------------------------------------
    # Benchmark
    # ---------------------------------------------------------

    print()
    print("=" * 64)
    print("BUY & HOLD BENCHMARK")
    print("=" * 64)

    print(
        f"Total return   : "
        f"{percent(benchmark_metrics['total_return'])}"
    )

    print(
        f"CAGR           : "
        f"{percent(benchmark_metrics['cagr'])}"
    )

    print(
        f"Volatility     : "
        f"{percent(benchmark_metrics['annualized_volatility'])}"
    )

    print(
        f"Sharpe         : "
        f"{benchmark_metrics['sharpe_ratio']:.2f}"
    )

    print(
        f"Max drawdown   : "
        f"{percent(benchmark_metrics['max_drawdown'])}"
    )

    # ---------------------------------------------------------
    # Research verdict for each experiment
    # ---------------------------------------------------------

    print()
    print("=" * 64)
    print("RESEARCH VERDICTS")
    print("=" * 64)

    for experiment in experiment_results:
        verdict = generate_verdict(
            experiment["metrics"],
            benchmark_metrics,
        )

        print()
        print(experiment["name"])
        print(f"Status         : {verdict.status}")

        if verdict.reasons:
            print("Reasons:")
            for reason in verdict.reasons:
                print(f"  ✗ {reason}")

        if verdict.positives:
            print("Positive characteristics:")
            for positive in verdict.positives:
                print(f"  ✓ {positive}")

        print(f"Recommendation : {verdict.recommendation}")

    # ---------------------------------------------------------
    # Trade ledger for the 100% exposure experiment
    # ---------------------------------------------------------

    full_exposure = experiment_results[-1]

    print_trade_ledger(
        full_exposure["result"],
    )

    print()
    print("=" * 64)
    print("END OF RESEARCH RUN")
    print("=" * 64)


if __name__ == "__main__":
    main()