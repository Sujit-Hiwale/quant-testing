import streamlit as st

from components.sections import section
from components.cards import metric_row
from components.charts import (
    price_chart,
    returns_histogram,
    volatility_chart,
    drawdown_chart,
)
from components.status import render_validation_status

from components.research_dashboard import (
    render_verdict_card,
    render_walk_forward_windows,
    walk_forward_equity_chart,
    cost_sensitivity_chart,
    render_parameter_stability,
    render_research_metrics,
)

from src.core.data_adapter import dataframe_to_bars
from src.research.cost_sensitivity import (
    CostScenario,
    run_cost_sensitivity,
)
from src.strategies.sma_crossover import SMACrossoverStrategy
from src.portfolio.sizing import TargetExposureSizer
from src.research.walk_forward import run_walk_forward


PARAMETER_GRID = [
    {
        "fast_period": 10,
        "slow_period": 30,
    },
    {
        "fast_period": 20,
        "slow_period": 50,
    },
    {
        "fast_period": 30,
        "slow_period": 100,
    },
    {
        "fast_period": 50,
        "slow_period": 200,
    },
]


COST_SCENARIOS = [
    CostScenario(0, 0),
    CostScenario(5, 10),
    CostScenario(10, 20),
    CostScenario(20, 40),
    CostScenario(50, 100),
]


def _build_windows(data):
    timestamps = data["Date"].sort_values()

    if len(timestamps) < 500:
        return []

    years = sorted(
        timestamps.dt.year.dropna().unique()
    )

    if len(years) < 4:
        return []

    windows = []

    for offset in range(len(years) - 3):
        train_start = f"{years[offset]}-01-01"
        train_end = f"{years[offset + 2]}-01-01"

        test_start = train_end
        test_end = f"{years[offset + 3]}-01-01"

        windows.append(
            {
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
            }
        )

    return windows[-3:]


@st.cache_data(show_spinner=False)
def run_research(
    ticker: str,
    data,
):
    bars = dataframe_to_bars(
        data=data,
        symbol=ticker,
    )

    windows = _build_windows(data)

    walk_forward = None

    if windows:

        def strategy_factory(params):
            return SMACrossoverStrategy(
                symbol=ticker,
                fast_period=params["fast_period"],
                slow_period=params["slow_period"],
            )

        def position_sizer_factory():
            return TargetExposureSizer(
                target_exposure=1.0,
                cost_buffer_bps=20.0,
            )

        walk_forward = run_walk_forward(
            data=data,
            symbol=ticker,
            initial_cash=100_000.0,
            windows=windows,
            parameter_grid=PARAMETER_GRID,
            strategy_factory=strategy_factory,
            position_sizer_factory=position_sizer_factory,
            slippage_bps=5.0,
            fee_bps=10.0,
            warmup_bars=200,
        )

    cost_sensitivity = run_cost_sensitivity(
        bars=bars,
        strategy_factory=lambda: SMACrossoverStrategy(
            symbol=ticker,
            fast_period=10,
            slow_period=30,
        ),
        initial_cash=100_000.0,
        scenarios=COST_SCENARIOS,
        position_sizer_factory=lambda scenario: TargetExposureSizer(
            target_exposure=1.0,
            cost_buffer_bps=(
                scenario.slippage_bps
                + scenario.fee_bps
                + 10.0
            ),
        ),
    )

    return {
        "walk_forward": walk_forward,
        "cost_sensitivity": cost_sensitivity,
    }

def _build_verdict(result):
    metrics = result.aggregate_test_metrics

    window_count = len(result.windows)

    positive_windows = sum(
        1
        for window in result.windows
        if window.test_metrics.get("cagr", 0.0) > 0
    )

    strong_windows = sum(
        1
        for window in result.windows
        if window.test_metrics.get(
            "sharpe_ratio",
            0.0,
        ) >= 0.5
    )

    trade_count = metrics.get(
        "trade_count",
        0,
    )

    aggregate_sharpe = metrics.get(
        "sharpe_ratio",
        0.0,
    )

    aggregate_drawdown = metrics.get(
        "max_drawdown",
        0.0,
    )

    reasons = []
    positives = []

    if positive_windows > 0:
        positives.append(
            f"Positive OOS windows: "
            f"{positive_windows}/{window_count}"
        )

    if strong_windows > 0:
        positives.append(
            f"Strong OOS Sharpe windows: "
            f"{strong_windows}/{window_count}"
        )

    if aggregate_sharpe >= 0.5:
        positives.append(
            "POSITIVE_AGGREGATE_SHARPE"
        )
    else:
        reasons.append(
            "WEAK_OOS_SHARPE"
        )

    if trade_count < 30:
        reasons.append(
            "SMALL_TRADE_SAMPLE"
        )

    if aggregate_drawdown < -0.30:
        reasons.append(
            "HIGH_DRAWDOWN"
        )

    # ---------------------------------------------------------
    # Insufficient evidence
    # ---------------------------------------------------------

    if window_count < 2:
        status = "INSUFFICIENT EVIDENCE"

        recommendation = (
            "The available history contains too few "
            "independent out-of-sample windows to establish "
            "robustness."
        )

        reasons.insert(
            0,
            "INSUFFICIENT_OOS_WINDOWS",
        )

        return (
            status,
            recommendation,
            reasons,
            positives,
        )

    # ---------------------------------------------------------
    # Robustness verdict
    # ---------------------------------------------------------

    if (
        positive_windows == window_count
        and strong_windows >= 2
        and aggregate_sharpe >= 0.5
        and trade_count >= 30
    ):
        status = "PASS"

        recommendation = (
            "Strategy demonstrates encouraging "
            "out-of-sample robustness and may warrant "
            "further validation."
        )

    elif positive_windows >= 2:
        status = "WEAK"

        recommendation = (
            "Promising in parts of the sample, but not "
            "robust enough for deployment."
        )

    else:
        status = "FAIL"

        recommendation = (
            "Strategy does not currently demonstrate "
            "consistent out-of-sample robustness."
        )

        if positive_windows < window_count:
            reasons.append(
                "INCONSISTENT_OOS_PERFORMANCE"
            )

    return (
        status,
        recommendation,
        reasons,
        positives,
    )

def render_research_overview(context: dict) -> None:
    data = context["data"]
    validation = context["validation"]

    section(
        "Quantitative Research",
        f"{context['ticker']} · {context['period']} · "
        "out-of-sample strategy evaluation",
    )

    render_validation_status(validation)

    metric_row(
        [
            {
                "label": "Observations",
                "value": f"{len(data):,}",
                "description": "Validated research rows",
            },
            {
                "label": "Latest Price",
                "value": f"₹{data['Close'].iloc[-1]:,.2f}",
                "description": "Most recent close",
            },
            {
                "label": "Maximum Drawdown",
                "value": f"{data['Drawdown'].min() * 100:.2f}%",
                "description": "Historical market drawdown",
            },
            {
                "label": "Dataset End",
                "value": data["Date"].max().strftime("%d %b %Y"),
                "description": "Latest observation",
            },
        ]
    )

    section(
        "Strategy Research",
        "Walk-forward testing determines whether the observed edge "
        "survives unseen market periods.",
    )

    with st.spinner("Running quantitative research..."):
        research = run_research(
            ticker=context["ticker"],
            data=data,
        )

    result = research["walk_forward"]

    if result is None:
        st.warning(
            "The selected dataset does not contain enough history "
            "for rolling walk-forward research. "
            "Performance and execution-cost analysis are still available."
        )
    else:
        status, recommendation, reasons, positives = _build_verdict(
            result
        )

        render_verdict_card(
            status=status,
            recommendation=recommendation,
            reasons=reasons,
            positives=positives,
        )

        render_research_metrics(
            result.aggregate_test_metrics
        )

        section(
            "Walk-Forward Robustness",
            "Each test window is evaluated on data that was not used "
            "to select its parameters.",
        )

        render_walk_forward_windows(
            result.windows
        )

        st.plotly_chart(
            walk_forward_equity_chart(
                result.combined_test_equity_curve
            ),
            use_container_width=True,
        )

        section(
            "Parameter Stability",
            "Stable parameters across independent training windows "
            "reduce dependence on a single historical regime.",
        )

        render_parameter_stability(
            result.parameter_selection_counts
        )

    section(
        "Execution Cost Sensitivity",
        "Full-sample sensitivity of the selected 10/30 strategy "
        "to increasing transaction costs.",
    )

    st.plotly_chart(
        cost_sensitivity_chart(
            research["cost_sensitivity"]
        ),
        use_container_width=True,
    )

    section(
        "Market Context",
        "Historical market behaviour underlying the strategy research.",
    )

    st.plotly_chart(
        price_chart(data),
        use_container_width=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        section(
            "Return Distribution",
            "Distribution of daily percentage returns.",
        )

        st.plotly_chart(
            returns_histogram(data),
            use_container_width=True,
        )

    with col2:
        section(
            "Rolling Volatility",
            "Annualized rolling volatility estimates.",
        )

        st.plotly_chart(
            volatility_chart(data),
            use_container_width=True,
        )

    section(
        "Drawdown",
        "Distance from the historical running maximum.",
    )

    metric_row(
        [
            {
                "label": "Maximum Drawdown",
                "value": f"{data['Drawdown'].min() * 100:.2f}%",
                "description": "Largest observed decline",
            },
            {
                "label": "Current Drawdown",
                "value": f"{data['Drawdown'].iloc[-1] * 100:.2f}%",
                "description": "Current distance from peak",
            },
        ]
    )

    st.plotly_chart(
        drawdown_chart(data),
        use_container_width=True,
    )

    with st.expander(
        "Research Dataset",
        expanded=False,
    ):
        st.caption(
            "Most recent observations and engineered features."
        )

        st.dataframe(
            data.tail(50),
            use_container_width=True,
            hide_index=True,
        )