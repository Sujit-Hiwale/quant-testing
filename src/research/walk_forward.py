from dataclasses import dataclass
from typing import Any, Callable

import pandas as pd

from src.analytics.metrics import calculate_metrics
from src.core.data_adapter import dataframe_to_bars
from src.core.engine import BacktestEngine


@dataclass
class ParameterResult:
    parameters: dict[str, Any]
    metrics: dict[str, float]


@dataclass
class TrainTestResult:
    selected_parameters: dict[str, Any]

    train_metrics: dict[str, float]
    test_metrics: dict[str, float]

    train_final_equity: float
    test_final_equity: float

    oos_return_degradation: float
    oos_sharpe_degradation: float

    parameter_results: list[ParameterResult]


@dataclass
class WalkForwardWindow:
    window_number: int

    train_start: str
    train_end: str

    test_start: str
    test_end: str

    selected_parameters: dict[str, Any]

    train_metrics: dict[str, float]
    test_metrics: dict[str, float]


@dataclass
class WalkForwardResult:
    windows: list[WalkForwardWindow]

    combined_test_equity_curve: list[dict]
    combined_test_trades: list

    aggregate_test_metrics: dict[str, float]

    parameter_selection_counts: dict[str, int]


def _prepare_data(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy()

    frame["Date"] = pd.to_datetime(frame["Date"])

    frame = frame.sort_values("Date")

    frame = frame.drop_duplicates(
        subset=["Date"],
        keep="first",
    )

    return frame.reset_index(drop=True)


def _timestamp(value: str) -> pd.Timestamp:
    return pd.Timestamp(value)


def _slice(
    data: pd.DataFrame,
    start: str,
    end: str,
) -> pd.DataFrame:

    start_ts = _timestamp(start)
    end_ts = _timestamp(end)

    return data[
        (data["Date"] >= start_ts)
        & (data["Date"] < end_ts)
    ].copy()


def _slice_with_warmup(
    data: pd.DataFrame,
    evaluation_start: str,
    evaluation_end: str,
    warmup_bars: int,
) -> tuple[pd.DataFrame, int]:

    frame = _prepare_data(data)

    start_ts = _timestamp(evaluation_start)
    end_ts = _timestamp(evaluation_end)

    evaluation_mask = (
        (frame["Date"] >= start_ts)
        & (frame["Date"] < end_ts)
    )

    evaluation_indices = frame.index[evaluation_mask]

    if len(evaluation_indices) == 0:
        raise ValueError(
            f"No data exists between "
            f"{evaluation_start} and {evaluation_end}."
        )

    first_evaluation_index = int(
        evaluation_indices[0]
    )

    warmup_start_index = max(
        0,
        first_evaluation_index - warmup_bars,
    )

    selected = frame.iloc[
        warmup_start_index:
    ].copy()

    evaluation_start_position = (
        first_evaluation_index
        - warmup_start_index
    )

    return selected, evaluation_start_position


def _run_backtest(
    data: pd.DataFrame,
    symbol: str,
    initial_cash: float,
    parameters: dict[str, Any],
    strategy_factory: Callable[
        [dict[str, Any]],
        Any,
    ],
    position_sizer_factory: Callable[[], Any],
    slippage_bps: float,
    fee_bps: float,
):

    bars = dataframe_to_bars(
        data,
        symbol=symbol,
    )

    strategy = strategy_factory(parameters)

    position_sizer = position_sizer_factory()

    engine = BacktestEngine(
        initial_cash=initial_cash,
        strategy=strategy,
        position_sizer=position_sizer,
        slippage_bps=slippage_bps,
        fee_bps=fee_bps,
    )

    result = engine.run(bars)

    metrics = calculate_metrics(
        result.equity_curve,
        trades=result.trades,
    )

    return result, metrics


def _filter_equity_curve(
    equity_curve: list[dict],
    start: str,
    end: str,
) -> list[dict]:

    start_ts = _timestamp(start)
    end_ts = _timestamp(end)

    return [
        point
        for point in equity_curve
        if start_ts
        <= pd.Timestamp(point["timestamp"])
        < end_ts
    ]


def _filter_trades(
    trades,
    start: str,
    end: str,
):

    start_ts = _timestamp(start)
    end_ts = _timestamp(end)

    return [
        trade
        for trade in trades
        if start_ts
        <= pd.Timestamp(trade.entry_time)
        < end_ts
    ]


def _calculate_period_metrics(
    equity_curve: list[dict],
    trades,
) -> dict[str, float]:

    if not equity_curve:
        raise ValueError(
            "No equity observations available "
            "for evaluation period."
        )

    return calculate_metrics(
        equity_curve,
        trades=trades,
    )


def _chain_equity_curves(
    curves: list[list[dict]],
    initial_cash: float,
) -> list[dict]:

    """
    Chain independent walk-forward test periods into
    one synthetic OOS equity curve.

    Each test window is independently backtested with
    initial_cash. We therefore convert each window's
    equity into a return multiplier and compound those
    returns sequentially.
    """

    chained = []

    current_equity = float(initial_cash)

    for curve in curves:

        if not curve:
            continue

        first_equity = float(
            curve[0]["equity"]
        )

        if first_equity <= 0:
            raise ValueError(
                "Cannot chain an equity curve "
                "with non-positive starting equity."
            )

        for point in curve:

            window_equity = float(
                point["equity"]
            )

            multiplier = (
                window_equity
                / first_equity
            )

            chained_equity = (
                current_equity
                * multiplier
            )

            chained.append(
                {
                    "timestamp": point["timestamp"],
                    "equity": chained_equity,
                }
            )

        current_equity = float(
            chained[-1]["equity"]
        )

    return chained


def select_best_parameter(
    parameter_results: list[ParameterResult],
) -> ParameterResult:

    if not parameter_results:
        raise ValueError(
            "No parameter results available."
        )

    return max(
        parameter_results,
        key=lambda result: (
            result.metrics["sharpe_ratio"],
            result.metrics["cagr"],
        ),
    )


def run_train_test(
    data: pd.DataFrame,
    symbol: str,
    initial_cash: float,
    train_start: str,
    train_end: str,
    test_start: str,
    test_end: str,
    parameter_grid: list[dict[str, Any]],
    strategy_factory: Callable[
        [dict[str, Any]],
        Any,
    ],
    position_sizer_factory: Callable[[], Any],
    slippage_bps: float = 0.0,
    fee_bps: float = 0.0,
    warmup_bars: int = 0,
) -> TrainTestResult:

    data = _prepare_data(data)

    train_data = _slice(
        data,
        train_start,
        train_end,
    )

    if train_data.empty:
        raise ValueError(
            "Training dataset is empty."
        )

    test_data, _ = _slice_with_warmup(
        data,
        test_start,
        test_end,
        warmup_bars,
    )

    parameter_results = []

    for parameters in parameter_grid:

        _, metrics = _run_backtest(
            data=train_data,
            symbol=symbol,
            initial_cash=initial_cash,
            parameters=parameters,
            strategy_factory=strategy_factory,
            position_sizer_factory=position_sizer_factory,
            slippage_bps=slippage_bps,
            fee_bps=fee_bps,
        )

        parameter_results.append(
            ParameterResult(
                parameters=parameters,
                metrics=metrics,
            )
        )

    selected = select_best_parameter(
        parameter_results
    )

    train_result, train_metrics = _run_backtest(
        data=train_data,
        symbol=symbol,
        initial_cash=initial_cash,
        parameters=selected.parameters,
        strategy_factory=strategy_factory,
        position_sizer_factory=position_sizer_factory,
        slippage_bps=slippage_bps,
        fee_bps=fee_bps,
    )

    test_result, _ = _run_backtest(
        data=test_data,
        symbol=symbol,
        initial_cash=initial_cash,
        parameters=selected.parameters,
        strategy_factory=strategy_factory,
        position_sizer_factory=position_sizer_factory,
        slippage_bps=slippage_bps,
        fee_bps=fee_bps,
    )

    test_equity_curve = _filter_equity_curve(
        test_result.equity_curve,
        test_start,
        test_end,
    )

    test_trades = _filter_trades(
        test_result.trades,
        test_start,
        test_end,
    )

    test_metrics = _calculate_period_metrics(
        test_equity_curve,
        test_trades,
    )

    train_return = train_metrics["total_return"]
    test_return = test_metrics["total_return"]

    train_sharpe = train_metrics["sharpe_ratio"]
    test_sharpe = test_metrics["sharpe_ratio"]

    return_degradation = (
        (
            test_return - train_return
        )
        / abs(train_return)
        if abs(train_return) > 1e-12
        else 0.0
    )

    sharpe_degradation = (
        (
            test_sharpe - train_sharpe
        )
        / abs(train_sharpe)
        if abs(train_sharpe) > 1e-12
        else 0.0
    )

    return TrainTestResult(
        selected_parameters=selected.parameters,

        train_metrics=train_metrics,
        test_metrics=test_metrics,

        train_final_equity=(
            train_result.equity_curve[-1]["equity"]
        ),

        test_final_equity=(
            test_equity_curve[-1]["equity"]
        ),

        oos_return_degradation=return_degradation,
        oos_sharpe_degradation=sharpe_degradation,

        parameter_results=parameter_results,
    )


def run_walk_forward(
    data: pd.DataFrame,
    symbol: str,
    initial_cash: float,
    windows: list[dict[str, str]],
    parameter_grid: list[dict[str, Any]],
    strategy_factory: Callable[
        [dict[str, Any]],
        Any,
    ],
    position_sizer_factory: Callable[[], Any],
    slippage_bps: float = 0.0,
    fee_bps: float = 0.0,
    warmup_bars: int = 0,
) -> WalkForwardResult:

    data = _prepare_data(data)

    if not windows:
        raise ValueError(
            "At least one walk-forward window is required."
        )

    results: list[WalkForwardWindow] = []

    test_curves = []
    combined_test_trades = []

    parameter_selection_counts: dict[str, int] = {}

    for window_number, window in enumerate(
        windows,
        start=1,
    ):

        train_start = window["train_start"]
        train_end = window["train_end"]

        test_start = window["test_start"]
        test_end = window["test_end"]

        train_data = _slice(
            data,
            train_start,
            train_end,
        )

        if train_data.empty:
            raise ValueError(
                f"Window {window_number} training "
                "period contains no data."
            )

        test_data, _ = _slice_with_warmup(
            data,
            test_start,
            test_end,
            warmup_bars,
        )

        parameter_results = []

        for parameters in parameter_grid:

            _, metrics = _run_backtest(
                data=train_data,
                symbol=symbol,
                initial_cash=initial_cash,
                parameters=parameters,
                strategy_factory=strategy_factory,
                position_sizer_factory=position_sizer_factory,
                slippage_bps=slippage_bps,
                fee_bps=fee_bps,
            )

            parameter_results.append(
                ParameterResult(
                    parameters=parameters,
                    metrics=metrics,
                )
            )

        selected = select_best_parameter(
            parameter_results
        )

        train_result, train_metrics = _run_backtest(
            data=train_data,
            symbol=symbol,
            initial_cash=initial_cash,
            parameters=selected.parameters,
            strategy_factory=strategy_factory,
            position_sizer_factory=position_sizer_factory,
            slippage_bps=slippage_bps,
            fee_bps=fee_bps,
        )

        test_result, _ = _run_backtest(
            data=test_data,
            symbol=symbol,
            initial_cash=initial_cash,
            parameters=selected.parameters,
            strategy_factory=strategy_factory,
            position_sizer_factory=position_sizer_factory,
            slippage_bps=slippage_bps,
            fee_bps=fee_bps,
        )

        test_equity_curve = _filter_equity_curve(
            test_result.equity_curve,
            test_start,
            test_end,
        )

        test_trades = _filter_trades(
            test_result.trades,
            test_start,
            test_end,
        )

        test_metrics = _calculate_period_metrics(
            test_equity_curve,
            test_trades,
        )

        results.append(
            WalkForwardWindow(
                window_number=window_number,

                train_start=train_start,
                train_end=train_end,

                test_start=test_start,
                test_end=test_end,

                selected_parameters=selected.parameters,

                train_metrics=train_metrics,
                test_metrics=test_metrics,
            )
        )

        test_curves.append(
            test_equity_curve
        )

        combined_test_trades.extend(
            test_trades
        )

        parameter_key = (
            f"{selected.parameters['fast_period']}/"
            f"{selected.parameters['slow_period']}"
        )

        parameter_selection_counts[
            parameter_key
        ] = (
            parameter_selection_counts.get(
                parameter_key,
                0,
            )
            + 1
        )

    combined_test_equity_curve = (
        _chain_equity_curves(
            test_curves,
            initial_cash,
        )
    )

    aggregate_metrics = calculate_metrics(
        combined_test_equity_curve,
        trades=combined_test_trades,
    )

    return WalkForwardResult(
        windows=results,

        combined_test_equity_curve=(
            combined_test_equity_curve
        ),

        combined_test_trades=combined_test_trades,

        aggregate_test_metrics=aggregate_metrics,

        parameter_selection_counts=(
            parameter_selection_counts
        ),
    )