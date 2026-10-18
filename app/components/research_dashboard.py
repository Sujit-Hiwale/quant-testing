import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from components.cards import metric_row


def render_verdict_card(
    status,
    recommendation,
    reasons,
    positives,
):
    status_colors = {
        "PASS": "#22c55e",
        "WEAK": "#f59e0b",
        "FAIL": "#ef4444",
        "INSUFFICIENT EVIDENCE": "#94a3b8",
    }

    status_color = status_colors.get(
        status,
        "#94a3b8",
    )

    positive_items = "".join(
        f"<li>{item}</li>"
        for item in positives
    )

    failure_items = "".join(
        f"<li>{item}</li>"
        for item in reasons
    )

    html = f"""
<div style="
    padding:1.25rem;
    border:1px solid rgba(128,128,128,.16);
    border-radius:16px;
    background:rgba(128,128,128,.035);
    border-left:4px solid {status_color};
">

    <div style="
        font-size:.67rem;
        font-weight:800;
        letter-spacing:.1em;
        opacity:.45;
    ">
        RESEARCH VERDICT
    </div>

    <div style="
        margin-top:.35rem;
        font-size:1.45rem;
        font-weight:850;
        color:{status_color};
    ">
        {status}
    </div>

    <div style="
        margin-top:.35rem;
        font-size:.92rem;
        opacity:.72;
    ">
        {recommendation}
    </div>

    <div style="
        display:grid;
        grid-template-columns:
            repeat(auto-fit,minmax(220px,1fr));
        gap:1.2rem;
        margin-top:1rem;
    ">

        <div>
            <div style="
                font-size:.67rem;
                font-weight:800;
                letter-spacing:.1em;
                opacity:.45;
            ">
                POSITIVES
            </div>

            <ul style="
                margin-top:.45rem;
                padding-left:1.2rem;
                opacity:.72;
            ">
                {positive_items or "<li>None identified</li>"}
            </ul>
        </div>

        <div>
            <div style="
                font-size:.67rem;
                font-weight:800;
                letter-spacing:.1em;
                opacity:.45;
            ">
                FAILURE CONDITIONS
            </div>

            <ul style="
                margin-top:.45rem;
                padding-left:1.2rem;
                opacity:.72;
            ">
                {failure_items or "<li>None identified</li>"}
            </ul>
        </div>

    </div>

</div>
"""

    st.html(html)

def render_walk_forward_windows(windows):
    if not windows:
        st.info("No walk-forward windows available.")
        return

    cards = []

    for window in windows:
        metrics = window.test_metrics

        cagr = metrics.get("cagr", 0.0)
        sharpe = metrics.get("sharpe_ratio", 0.0)
        max_drawdown = metrics.get("max_drawdown", 0.0)
        trade_count = metrics.get("trade_count", 0)

        if sharpe >= 0.5 and cagr > 0:
            status = "PASS"
            status_color = "#22c55e"
        elif cagr > 0:
            status = "WEAK"
            status_color = "#f59e0b"
        else:
            status = "FAIL"
            status_color = "#ef4444"

        selected_parameters = window.selected_parameters

        cards.append(
            f"""
<div style="
    flex:1;
    min-width:210px;
    padding:1rem;
    border:1px solid rgba(128,128,128,.16);
    border-radius:14px;
    background:rgba(128,128,128,.035);
    border-top:3px solid {status_color};
">

    <div style="
        font-size:.67rem;
        font-weight:800;
        letter-spacing:.1em;
        opacity:.45;
    ">
        WINDOW {window.window_number}
    </div>

    <div style="
        margin-top:.3rem;
        font-size:.78rem;
        opacity:.55;
    ">
        {window.test_start}
        →
        {window.test_end}
    </div>

    <div style="
        margin-top:.7rem;
        font-size:1.15rem;
        font-weight:800;
        color:{status_color};
    ">
        {status}
    </div>

    <div style="
        display:grid;
        grid-template-columns:1fr 1fr;
        gap:.7rem;
        margin-top:.8rem;
    ">

        <div>
            <div style="font-size:.66rem;opacity:.45;">
                CAGR
            </div>
            <div style="font-weight:750;">
                {cagr * 100:.2f}%
            </div>
        </div>

        <div>
            <div style="font-size:.66rem;opacity:.45;">
                SHARPE
            </div>
            <div style="font-weight:750;">
                {sharpe:.2f}
            </div>
        </div>

        <div>
            <div style="font-size:.66rem;opacity:.45;">
                MAX DD
            </div>
            <div style="font-weight:750;">
                {max_drawdown * 100:.2f}%
            </div>
        </div>

        <div>
            <div style="font-size:.66rem;opacity:.45;">
                TRADES
            </div>
            <div style="font-weight:750;">
                {trade_count}
            </div>
        </div>

    </div>

    <div style="
        margin-top:.8rem;
        font-size:.7rem;
        opacity:.45;
    ">
        Selected: {selected_parameters}
    </div>

</div>
"""
        )

    html = f"""
<div style="
    display:flex;
    flex-wrap:wrap;
    gap:1rem;
    width:100%;
">
    {''.join(cards)}
</div>
"""

    st.html(html)

def walk_forward_equity_chart(equity_curve: list[dict]):
    if not equity_curve:
        return go.Figure()

    frame = pd.DataFrame(equity_curve)

    frame["timestamp"] = pd.to_datetime(frame["timestamp"])

    figure = go.Figure()

    figure.add_trace(
        go.Scatter(
            x=frame["timestamp"],
            y=frame["equity"],
            mode="lines",
            name="OOS Equity",
            line=dict(width=2.2),
            hovertemplate=(
                "%{x|%d %b %Y}"
                "<br>₹%{y:,.2f}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        height=390,
        margin=dict(l=10, r=10, t=20, b=10),
        hovermode="x unified",
        xaxis_title=None,
        yaxis_title="Portfolio Value",
        showlegend=False,
    )

    return figure


def cost_sensitivity_chart(results):
    if not results:
        return go.Figure()

    labels = [
        f"{result.slippage_bps:g}/{result.fee_bps:g}"
        for result in results
    ]

    cagr = [
        result.metrics.get("cagr", 0.0) * 100
        for result in results
    ]

    sharpe = [
        result.metrics.get("sharpe_ratio", 0.0)
        for result in results
    ]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=cagr,
            mode="lines+markers",
            name="CAGR",
            hovertemplate=(
                "Costs: %{x} bps"
                "<br>CAGR: %{y:.2f}%"
                "<extra></extra>"
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=sharpe,
            mode="lines+markers",
            name="Sharpe",
            yaxis="y2",
            hovertemplate=(
                "Costs: %{x} bps"
                "<br>Sharpe: %{y:.2f}"
                "<extra></extra>"
            ),
        )
    )

    fig.update_layout(
        title="Transaction-Cost Sensitivity",
        xaxis_title="Slippage / Fee (bps)",
        yaxis_title="CAGR (%)",
        yaxis2=dict(
            title="Sharpe Ratio",
            overlaying="y",
            side="right",
        ),
        hovermode="x unified",
        height=420,
        margin=dict(
            l=20,
            r=20,
            t=60,
            b=20,
        ),
    )

    return fig

def render_parameter_stability(
    parameter_counts: dict[str, int],
) -> None:
    if not parameter_counts:
        st.info("No parameter selections available.")
        return

    frame = (
        pd.DataFrame(
            [
                {
                    "Parameters": parameter,
                    "Selections": count,
                }
                for parameter, count in parameter_counts.items()
            ]
        )
        .sort_values(
            "Selections",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    st.dataframe(
        frame,
        use_container_width=True,
        hide_index=True,
    )


def render_research_metrics(metrics: dict) -> None:
    metric_row(
        [
            {
                "label": "OOS CAGR",
                "value": f"{metrics['cagr'] * 100:.2f}%",
                "description": "Combined out-of-sample growth",
            },
            {
                "label": "OOS Sharpe",
                "value": f"{metrics['sharpe_ratio']:.2f}",
                "description": "Risk-adjusted OOS return",
            },
            {
                "label": "Max Drawdown",
                "value": f"{metrics['max_drawdown'] * 100:.2f}%",
                "description": "Worst OOS portfolio decline",
            },
            {
                "label": "OOS Trades",
                "value": f"{metrics.get('trade_count', 0)}",
                "description": "Completed out-of-sample trades",
            },
        ]
    )