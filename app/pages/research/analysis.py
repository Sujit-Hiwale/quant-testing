import streamlit as st

from components.sections import section
from components.cards import metric_row
from components.charts import (
    price_chart,
    returns_histogram,
    volatility_chart,
    drawdown_chart,
    volume_chart,
    volume_ratio_chart,
)
from components.status import render_validation_status


def render_research_analysis(context: dict) -> None:
    data = context["data"]
    validation = context["validation"]

    # ==================================================
    # Dataset
    # ==================================================

    section(
        "Dataset",
        f"Detailed market analysis for {context['ticker']}."
    )

    render_validation_status(validation)

    # ==================================================
    # Price Analysis
    # ==================================================

    section(
        "Price Analysis",
        "Historical closing price and moving-average structure."
    )

    metric_row([
        {
            "label": "Latest Close",
            "value": f"₹{data['Close'].iloc[-1]:,.2f}",
            "description": "Most recent closing price",
        },
        {
            "label": "20D SMA",
            "value": (
                f"₹{data['SMA_20'].iloc[-1]:,.2f}"
                if data["SMA_20"].notna().any()
                else "N/A"
            ),
            "description": "20-day moving average",
        },
        {
            "label": "50D SMA",
            "value": (
                f"₹{data['SMA_50'].iloc[-1]:,.2f}"
                if data["SMA_50"].notna().any()
                else "N/A"
            ),
            "description": "50-day moving average",
        },
        {
            "label": "200D SMA",
            "value": (
                f"₹{data['SMA_200'].iloc[-1]:,.2f}"
                if data["SMA_200"].notna().any()
                else "N/A"
            ),
            "description": "200-day moving average",
        },
    ])

    st.plotly_chart(
        price_chart(data),
        use_container_width=True,
    )

    # ==================================================
    # Return Analysis
    # ==================================================

    section(
        "Return Analysis",
        "Distribution and descriptive characteristics of returns."
    )

    returns = data["Return"].dropna()

    metric_row([
        {
            "label": "Mean Return",
            "value": f"{returns.mean() * 100:.3f}%",
            "description": "Average daily return",
        },
        {
            "label": "Return Std. Dev.",
            "value": f"{returns.std() * 100:.2f}%",
            "description": "Daily return dispersion",
        },
        {
            "label": "Best Day",
            "value": f"{returns.max() * 100:.2f}%",
            "description": "Largest positive return",
        },
        {
            "label": "Worst Day",
            "value": f"{returns.min() * 100:.2f}%",
            "description": "Largest negative return",
        },
    ])

    st.plotly_chart(
        returns_histogram(data),
        use_container_width=True,
    )

    # ==================================================
    # Volatility & Risk
    # ==================================================

    section(
        "Volatility & Risk",
        "Rolling estimates of annualized market volatility."
    )

    metric_row([
        {
            "label": "Current 20D Volatility",
            "value": (
                f"{data['Volatility_20D'].iloc[-1] * 100:.2f}%"
                if data["Volatility_20D"].notna().any()
                else "N/A"
            ),
            "description": "Annualized",
        },
        {
            "label": "Current 60D Volatility",
            "value": (
                f"{data['Volatility_60D'].iloc[-1] * 100:.2f}%"
                if data["Volatility_60D"].notna().any()
                else "N/A"
            ),
            "description": "Annualized",
        },
    ])

    st.plotly_chart(
        volatility_chart(data),
        use_container_width=True,
    )

    # ==================================================
    # Drawdown
    # ==================================================

    section(
        "Drawdown",
        "Historical declines from previous running peaks."
    )

    metric_row([
        {
            "label": "Maximum Drawdown",
            "value": f"{data['Drawdown'].min() * 100:.2f}%",
            "description": "Largest observed decline",
        },
        {
            "label": "Current Drawdown",
            "value": f"{data['Drawdown'].iloc[-1] * 100:.2f}%",
            "description": "Current decline from peak",
        },
    ])

    st.plotly_chart(
        drawdown_chart(data),
        use_container_width=True,
    )

    # ==================================================
    # Volume Analysis
    # ==================================================

    section(
        "Volume Analysis",
        "Trading activity and relative volume behavior."
    )

    metric_row([
        {
            "label": "Latest Volume",
            "value": f"{data['Volume'].iloc[-1]:,.0f}",
            "description": "Most recent trading volume",
        },
        {
            "label": "20D Avg. Volume",
            "value": (
                f"{data['Volume_SMA_20'].iloc[-1]:,.0f}"
                if data["Volume_SMA_20"].notna().any()
                else "N/A"
            ),
            "description": "20-day average volume",
        },
        {
            "label": "Volume Ratio",
            "value": (
                f"{data['Volume_Ratio'].iloc[-1]:.2f}×"
                if data["Volume_Ratio"].notna().any()
                else "N/A"
            ),
            "description": "Volume relative to 20D average",
        },
    ])

    st.plotly_chart(
        volume_chart(data),
        use_container_width=True,
    )

    st.plotly_chart(
        volume_ratio_chart(data),
        use_container_width=True,
    )

    # ==================================================
    # Statistical Summary
    # ==================================================

    section(
        "Statistical Summary",
        "Descriptive statistics for the principal research variables."
    )

    columns = [
        "Close",
        "Return",
        "Log_Return",
        "Volatility_20D",
        "Volatility_60D",
        "Volume",
        "Volume_Ratio",
        "Drawdown",
    ]

    available_columns = [
        column
        for column in columns
        if column in data.columns
    ]

    summary = data[available_columns].describe().T

    summary["skew"] = data[available_columns].skew()
    summary["kurtosis"] = data[available_columns].kurtosis()

    st.dataframe(
        summary,
        use_container_width=True,
    )

    # ==================================================
    # Research Dataset
    # ==================================================

    section(
        "Research Dataset",
        "Latest observations including engineered features."
    )

    st.dataframe(
        data.tail(100),
        use_container_width=True,
    )