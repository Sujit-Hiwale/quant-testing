import streamlit as st
import plotly.graph_objects as go
import numpy as np

from src.data.loader import load_market_data
from src.data.validator import validate_market_data
from src.data.cleaner import clean_market_data
from src.features.engineering import create_market_features


# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Market Analysis",
    page_icon="📊",
    layout="wide"
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

st.sidebar.title("Research Controls")

ticker = st.sidebar.selectbox(
    "Asset",
    [
        "RELIANCE.NS",
        "TCS.NS",
        "INFY.NS",
        "HDFCBANK.NS",
        "ICICIBANK.NS",
        "^NSEI"
    ]
)

period = st.sidebar.selectbox(
    "Historical Period",
    [
        "1 Year",
        "3 Years",
        "5 Years",
        "10 Years",
        "All Available"
    ],
    index=2
)


# ---------------------------------------------------------
# Determine date range
# ---------------------------------------------------------

from datetime import date
from dateutil.relativedelta import relativedelta

end_date = date.today()

if period == "1 Year":
    start_date = end_date - relativedelta(years=1)

elif period == "3 Years":
    start_date = end_date - relativedelta(years=3)

elif period == "5 Years":
    start_date = end_date - relativedelta(years=5)

elif period == "10 Years":
    start_date = end_date - relativedelta(years=10)

else:
    start_date = date(1990, 1, 1)


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

try:

    data = load_market_data(
        ticker=ticker,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d")
    )

except Exception as e:

    st.error(f"Failed to load market data: {e}")
    st.stop()


# ---------------------------------------------------------
# Validate data
# ---------------------------------------------------------

validation = validate_market_data(data)

if validation["status"] != "PASS":

    st.error("Market data validation failed.")

    for error in validation["details"]:
        st.write(f"• {error}")

    st.stop()


# ---------------------------------------------------------
# Clean data
# ---------------------------------------------------------

data = clean_market_data(data)


# ---------------------------------------------------------
# Feature engineering
# ---------------------------------------------------------

data = create_market_features(data)


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("📊 Market Analysis")

st.caption(
    f"Historical analysis of **{ticker}** using {period.lower()} "
    "of daily market data."
)


# ---------------------------------------------------------
# Dataset information
# ---------------------------------------------------------

st.success(
    f"Using {len(data):,} validated observations "
    f"from {data['Date'].min().date()} to {data['Date'].max().date()}."
)


# =========================================================
# PRICE ANALYSIS
# =========================================================

st.header("1. Price Analysis")

fig_price = go.Figure()

fig_price.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["Close"],
        name="Close",
        mode="lines"
    )
)

fig_price.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["SMA_20"],
        name="SMA 20",
        mode="lines"
    )
)

fig_price.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["SMA_50"],
        name="SMA 50",
        mode="lines"
    )
)

fig_price.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["SMA_200"],
        name="SMA 200",
        mode="lines"
    )
)

fig_price.update_layout(
    title="Price and Moving Averages",
    xaxis_title="Date",
    yaxis_title="Price",
    hovermode="x unified"
)

st.plotly_chart(
    fig_price,
    use_container_width=True
)


# =========================================================
# RETURN ANALYSIS
# =========================================================

st.header("2. Return Analysis")

col1, col2, col3, col4 = st.columns(4)

returns = data["Return"].dropna()

col1.metric(
    "Mean Daily Return",
    f"{returns.mean() * 100:.3f}%"
)

col2.metric(
    "Return Volatility",
    f"{returns.std() * 100:.3f}%"
)

col3.metric(
    "Best Day",
    f"{returns.max() * 100:.2f}%"
)

col4.metric(
    "Worst Day",
    f"{returns.min() * 100:.2f}%"
)


# ---------------------------------------------------------
# Return distribution
# ---------------------------------------------------------

fig_returns = go.Figure()

fig_returns.add_trace(
    go.Histogram(
        x=returns,
        nbinsx=80,
        name="Daily Returns"
    )
)

fig_returns.update_layout(
    title="Distribution of Daily Returns",
    xaxis_title="Daily Return",
    yaxis_title="Frequency"
)

st.plotly_chart(
    fig_returns,
    use_container_width=True
)


# =========================================================
# VOLATILITY ANALYSIS
# =========================================================

st.header("3. Volatility & Risk")

fig_vol = go.Figure()

fig_vol.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["Volatility_20D"],
        name="20D Volatility",
        mode="lines"
    )
)

fig_vol.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["Volatility_60D"],
        name="60D Volatility",
        mode="lines"
    )
)

fig_vol.update_layout(
    title="Rolling Annualized Volatility",
    xaxis_title="Date",
    yaxis_title="Volatility",
    hovermode="x unified"
)

st.plotly_chart(
    fig_vol,
    use_container_width=True
)


# =========================================================
# DRAWDOWN
# =========================================================

st.subheader("Drawdown")

drawdown = data["Drawdown"].dropna()

max_drawdown = drawdown.min()

col1, col2 = st.columns(2)

col1.metric(
    "Maximum Drawdown",
    f"{max_drawdown * 100:.2f}%"
)

col2.metric(
    "Current Drawdown",
    f"{drawdown.iloc[-1] * 100:.2f}%"
)


fig_drawdown = go.Figure()

fig_drawdown.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["Drawdown"] * 100,
        name="Drawdown",
        mode="lines",
        fill="tozeroy"
    )
)

fig_drawdown.update_layout(
    title="Historical Drawdown",
    xaxis_title="Date",
    yaxis_title="Drawdown (%)"
)

st.plotly_chart(
    fig_drawdown,
    use_container_width=True
)


# =========================================================
# VOLUME ANALYSIS
# =========================================================

st.header("4. Volume Analysis")

fig_volume = go.Figure()

fig_volume.add_trace(
    go.Bar(
        x=data["Date"],
        y=data["Volume"],
        name="Volume"
    )
)

fig_volume.update_layout(
    title="Trading Volume",
    xaxis_title="Date",
    yaxis_title="Volume"
)

st.plotly_chart(
    fig_volume,
    use_container_width=True
)


# ---------------------------------------------------------
# Volume ratio
# ---------------------------------------------------------

fig_volume_ratio = go.Figure()

fig_volume_ratio.add_trace(
    go.Scatter(
        x=data["Date"],
        y=data["Volume_Ratio"],
        name="Volume Ratio",
        mode="lines"
    )
)

fig_volume_ratio.add_hline(
    y=1,
    line_dash="dash"
)

fig_volume_ratio.update_layout(
    title="Volume Relative to 20-Day Average",
    xaxis_title="Date",
    yaxis_title="Volume Ratio"
)

st.plotly_chart(
    fig_volume_ratio,
    use_container_width=True
)


# =========================================================
# BASIC STATISTICAL SUMMARY
# =========================================================

st.header("5. Statistical Summary")

summary = data[
    [
        "Close",
        "Return",
        "Log_Return",
        "Volatility_20D",
        "Volatility_60D",
        "Volume",
        "Drawdown"
    ]
].describe().T

summary["skewness"] = data[
    [
        "Close",
        "Return",
        "Log_Return",
        "Volatility_20D",
        "Volatility_60D",
        "Volume",
        "Drawdown"
    ]
].skew()

summary["kurtosis"] = data[
    [
        "Close",
        "Return",
        "Log_Return",
        "Volatility_20D",
        "Volatility_60D",
        "Volume",
        "Drawdown"
    ]
].kurt()

st.dataframe(
    summary,
    use_container_width=True
)


# =========================================================
# RESEARCH DATASET
# =========================================================

st.header("6. Research Dataset")

st.caption(
    "Derived features generated from the validated market dataset."
)

st.dataframe(
    data.tail(100),
    use_container_width=True,
    height=400
)