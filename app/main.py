import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="AI Quantitative Research Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# MOCK DATA
# Replace this later with src.data.loader
# ============================================================

@st.cache_data
def generate_mock_data():

    np.random.seed(42)

    dates = pd.date_range(
        start="2018-01-01",
        end="2026-01-01",
        freq="B"
    )

    returns = np.random.normal(
        loc=0.0004,
        scale=0.015,
        size=len(dates)
    )

    price = 1000 * np.exp(np.cumsum(returns))

    df = pd.DataFrame(
        {
            "Date": dates,
            "Close": price,
            "Return": returns,
        }
    )

    df["Volatility_20D"] = (
        df["Return"]
        .rolling(20)
        .std()
        * np.sqrt(252)
    )

    return df


data = generate_mock_data()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("Research Platform")

    st.caption(
        "AI • Statistics • Machine Learning • Quantitative Research"
    )

    st.divider()

    st.subheader("Asset")

    ticker = st.selectbox(
        "Select asset",
        [
            "RELIANCE.NS",
            "TCS.NS",
            "INFY.NS",
            "HDFCBANK.NS",
            "ICICIBANK.NS",
            "^NSEI",
        ],
    )

    period = st.selectbox(
        "Analysis period",
        [
            "1 Year",
            "3 Years",
            "5 Years",
            "All Available",
        ],
        index=3,
    )

    st.divider()

    st.subheader("Research Mode")

    mode = st.radio(
        "Mode",
        [
            "Overview",
            "Exploration",
            "Statistics",
            "Models",
            "Experiments",
        ],
    )

    st.divider()

    st.caption("Phase 1 • Research Prototype")


# ============================================================
# HEADER
# ============================================================

st.title("AI Quantitative Research Platform")

st.markdown(
    """
    **A research environment for market analysis, statistical modelling,
    machine learning and quantitative experimentation.**
    """
)

st.divider()


# ============================================================
# TOP METRICS
# ============================================================

latest_price = data["Close"].iloc[-1]

annual_return = (
    (data["Close"].iloc[-1] / data["Close"].iloc[0]) ** 
    (252 / len(data)) - 1
)

annual_volatility = (
    data["Return"].std() * np.sqrt(252)
)

observations = len(data)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Current Price",
        f"₹{latest_price:,.2f}",
    )

with col2:
    st.metric(
        "Annual Return",
        f"{annual_return * 100:.2f}%",
    )

with col3:
    st.metric(
        "Annual Volatility",
        f"{annual_volatility * 100:.2f}%",
    )

with col4:
    st.metric(
        "Observations",
        f"{observations:,}",
    )


st.divider()


# ============================================================
# PRICE CHART
# ============================================================

st.subheader(f"{ticker} — Price History")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["Close"],
        mode="lines",
        name="Close",
    )
)

fig.update_layout(
    height=450,
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# RETURNS + VOLATILITY
# ============================================================

left, right = st.columns(2)

with left:

    st.subheader("Return Distribution")

    fig_returns = go.Figure()

    fig_returns.add_trace(
        go.Histogram(
            x=data["Return"],
            nbinsx=80,
        )
    )

    fig_returns.update_layout(
        height=350,
        xaxis_title="Daily Return",
        yaxis_title="Frequency",
    )

    st.plotly_chart(
        fig_returns,
        use_container_width=True,
    )


with right:

    st.subheader("Rolling Volatility")

    fig_vol = go.Figure()

    fig_vol.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Volatility_20D"],
            mode="lines",
            name="20D Volatility",
        )
    )

    fig_vol.update_layout(
        height=350,
        xaxis_title="Date",
        yaxis_title="Annualized Volatility",
    )

    st.plotly_chart(
        fig_vol,
        use_container_width=True,
    )


# ============================================================
# STATISTICAL SUMMARY
# ============================================================

st.divider()

st.subheader("Statistical Summary")

summary = pd.DataFrame(
    {
        "Statistic": [
            "Mean Return",
            "Return Std. Dev.",
            "Minimum Return",
            "Maximum Return",
            "Median Return",
            "Skewness",
            "Kurtosis",
        ],
        "Value": [
            data["Return"].mean(),
            data["Return"].std(),
            data["Return"].min(),
            data["Return"].max(),
            data["Return"].median(),
            data["Return"].skew(),
            data["Return"].kurtosis(),
        ],
    }
)

summary["Value"] = summary["Value"].map(
    lambda x: f"{x:.6f}"
)

st.dataframe(
    summary,
    hide_index=True,
    use_container_width=True,
)


# ============================================================
# MODEL COMPARISON
# ============================================================

st.divider()

st.subheader("Model Comparison")

model_results = pd.DataFrame(
    {
        "Model": [
            "Historical Volatility",
            "GARCH",
            "Random Forest",
            "XGBoost",
        ],
        "RMSE": [
            0.0241,
            0.0218,
            0.0204,
            0.0197,
        ],
        "MAE": [
            0.0183,
            0.0169,
            0.0158,
            0.0151,
        ],
        "Training Time (s)": [
            0.01,
            1.42,
            4.87,
            3.21,
        ],
    }
)

st.dataframe(
    model_results,
    hide_index=True,
    use_container_width=True,
)


# ============================================================
# RESEARCH INSIGHT
# ============================================================

st.divider()

st.subheader("Research Insight")

st.info(
    """
    **Example research finding**

    XGBoost currently provides the lowest validation RMSE among the
    evaluated models. However, this result should not be interpreted
    as evidence of superior predictive ability until it survives
    strict temporal out-of-sample evaluation.

    Further experiments should investigate feature importance,
    regime stability and performance under changing market conditions.
    """
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Quantitative Research Platform • Phase 1 Prototype"
)