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


def render_research_overview(context: dict) -> None:
    data = context["data"]
    validation = context["validation"]

    # --------------------------------------------------
    # Introduction
    # --------------------------------------------------

    section(
        "Research Overview",
        f"Analytical overview of {context['ticker']} "
        f"using the selected historical dataset."
    )

    render_validation_status(validation)

    # --------------------------------------------------
    # Dataset metrics
    # --------------------------------------------------

    metric_row([
        {
            "label": "Observations",
            "value": f"{len(data):,}",
            "description": "Rows in research dataset",
        },
        {
            "label": "Start",
            "value": data["Date"].min().strftime("%d %b %Y"),
            "description": "First observation",
        },
        {
            "label": "End",
            "value": data["Date"].max().strftime("%d %b %Y"),
            "description": "Latest observation",
        },
        {
            "label": "Latest Price",
            "value": f"₹{data['Close'].iloc[-1]:,.2f}",
            "description": "Most recent close",
        },
    ])

    # --------------------------------------------------
    # Price analysis
    # --------------------------------------------------

    section(
        "Price History",
        "Historical close price and moving averages."
    )

    st.plotly_chart(
        price_chart(data),
        use_container_width=True,
    )

    # --------------------------------------------------
    # Return + volatility
    # --------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        section(
            "Return Distribution",
            "Distribution of daily percentage returns."
        )

        st.plotly_chart(
            returns_histogram(data),
            use_container_width=True,
        )

    with col2:

        section(
            "Rolling Volatility",
            "Annualized rolling volatility estimates."
        )

        st.plotly_chart(
            volatility_chart(data),
            use_container_width=True,
        )

    # --------------------------------------------------
    # Drawdown
    # --------------------------------------------------

    section(
        "Drawdown",
        "Distance from the historical running maximum."
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
            "description": "Current distance from peak",
        },
    ])

    st.plotly_chart(
        drawdown_chart(data),
        use_container_width=True,
    )

    # --------------------------------------------------
    # Dataset preview
    # --------------------------------------------------

    section(
        "Research Dataset",
        "Most recent observations and engineered features."
    )

    st.dataframe(
        data.tail(50),
        use_container_width=True,
    )