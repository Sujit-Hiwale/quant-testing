import streamlit as st

from components.sections import section
from components.cards import metric_row
from components.charts import (
    price_chart,
    volatility_chart,
    drawdown_chart,
)
from components.status import render_validation_status


def render_user_overview(context: dict) -> None:
    data = context["data"]
    validation = context["validation"]

    # --------------------------------------------------
    # Page introduction
    # --------------------------------------------------

    section(
        "Market Overview",
        f"Decision-oriented view of {context['ticker']} "
        f"over the selected {context['period'].lower()} period."
    )

    render_validation_status(validation)

    # --------------------------------------------------
    # Key metrics
    # --------------------------------------------------

    latest_price = data["Close"].iloc[-1]

    if len(data) > 1:
        first_price = data["Close"].iloc[0]
        total_return = (latest_price / first_price) - 1
    else:
        total_return = 0.0

    latest_volatility = data["Volatility_20D"].dropna()

    if not latest_volatility.empty:
        current_volatility = latest_volatility.iloc[-1]
    else:
        current_volatility = float("nan")

    current_drawdown = data["Drawdown"].iloc[-1]

    metric_row([
        {
            "label": "Latest Price",
            "value": f"₹{latest_price:,.2f}",
            "description": "Most recent closing price",
        },
        {
            "label": "Period Return",
            "value": f"{total_return * 100:.2f}%",
            "description": "Change over selected period",
        },
        {
            "label": "20D Volatility",
            "value": (
                f"{current_volatility * 100:.2f}%"
                if current_volatility == current_volatility
                else "N/A"
            ),
            "description": "Annualized rolling volatility",
        },
        {
            "label": "Current Drawdown",
            "value": f"{current_drawdown * 100:.2f}%",
            "description": "Decline from running peak",
        },
    ])

    # --------------------------------------------------
    # Price
    # --------------------------------------------------

    section(
        "Price Trend",
        "Historical price and moving-average structure."
    )

    st.plotly_chart(
        price_chart(data),
        use_container_width=True,
    )

    # --------------------------------------------------
    # Risk
    # --------------------------------------------------

    section(
        "Risk",
        "Recent volatility and drawdown behavior."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            volatility_chart(data),
            use_container_width=True,
        )

    with col2:
        st.plotly_chart(
            drawdown_chart(data),
            use_container_width=True,
        )

    # --------------------------------------------------
    # Key observations
    # --------------------------------------------------

    section(
        "Key Observations",
        "Simple evidence derived from the current dataset."
    )

    observations = []

    if "SMA_20" in data.columns and "SMA_50" in data.columns:
        sma20 = data["SMA_20"].iloc[-1]
        sma50 = data["SMA_50"].iloc[-1]

        if sma20 > sma50:
            observations.append(
                "The 20-day moving average is above the 50-day "
                "moving average."
            )
        elif sma20 < sma50:
            observations.append(
                "The 20-day moving average is below the 50-day "
                "moving average."
            )

    if current_drawdown < -0.10:
        observations.append(
            "The asset is currently more than 10% below its "
            "running historical peak."
        )
    elif current_drawdown < 0:
        observations.append(
            "The asset is currently below its running historical peak."
        )
    else:
        observations.append(
            "The asset is currently at its running historical peak."
        )

    if not latest_volatility.empty:
        if current_volatility > 0.40:
            observations.append(
                "Recent annualized volatility is relatively elevated."
            )
        elif current_volatility < 0.20:
            observations.append(
                "Recent annualized volatility is relatively contained."
            )
        else:
            observations.append(
                "Recent annualized volatility is in a moderate range."
            )

    for observation in observations:
        st.markdown(f"- {observation}")

    # --------------------------------------------------
    # Research link
    # --------------------------------------------------

    st.caption(
        "For the underlying statistics, distributions, diagnostics, "
        "and dataset details, switch to Research mode."
    )