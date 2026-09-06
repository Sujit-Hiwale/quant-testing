import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

from src.data.loader import load_market_data
from src.data.validator import validate_market_data
from src.data.cleaner import clean_market_data


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
            "SBIN.NS",
            "ITC.NS",
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
# DETERMINE DATE RANGE
# ============================================================

from datetime import date

end_date = date.today()

if period == "1 Year":
    start_date = date(
        end_date.year - 1,
        end_date.month,
        end_date.day,
    )

elif period == "3 Years":
    start_date = date(
        end_date.year - 3,
        end_date.month,
        end_date.day,
    )

elif period == "5 Years":
    start_date = date(
        end_date.year - 5,
        end_date.month,
        end_date.day,
    )

else:
    start_date = date(2010, 1, 1)


# ============================================================
# LOAD REAL MARKET DATA
# ============================================================

with st.spinner(f"Loading {ticker} market data..."):

    try:

        data = load_market_data(
            ticker=ticker,
            start=str(start_date),
            end=str(end_date),
        )

    except Exception as error:

        st.error(
            f"Unable to load market data: {error}"
        )

        st.stop()


# ============================================================
# VALIDATE DATA
# ============================================================

validation = validate_market_data(data)

if validation["status"] == "FAIL":

    st.error("Data validation failed.")

    st.json(validation)

    st.stop()


# ============================================================
# CLEAN DATA
# ============================================================

data = clean_market_data(data)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

# Daily simple return
data["Return"] = data["Close"].pct_change()

# Daily log return
data["Log_Return"] = np.log(
    data["Close"] / data["Close"].shift(1)
)

# 20-day annualized rolling volatility
data["Volatility_20D"] = (
    data["Log_Return"]
    .rolling(20)
    .std()
    * np.sqrt(252)
)

# Remove the first row created by pct_change()
data = data.dropna(
    subset=["Return", "Log_Return"]
).reset_index(drop=True)


# ============================================================
# HEADER
# ============================================================

st.title("AI Quantitative Research Platform")

st.markdown(
    f"""
    **Research environment for {ticker}**

    Historical market data • Statistical analysis • Machine learning
    • Quantitative experimentation
    """
)

st.divider()


# ============================================================
# DATA STATUS
# ============================================================

if validation["status"] == "PASS":

    st.success(
        f"✓ Market data loaded and validated successfully "
        f"({len(data):,} observations)"
    )


# ============================================================
# TOP METRICS
# ============================================================

latest_price = data["Close"].iloc[-1]

annual_return = (
    (data["Close"].iloc[-1] / data["Close"].iloc[0])
    ** (252 / len(data))
    - 1
)

annual_volatility = (
    data["Log_Return"].std()
    * np.sqrt(252)
)

observations = len(data)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Latest Price",
        f"₹{latest_price:,.2f}",
    )


with col2:

    st.metric(
        "Annualized Return",
        f"{annual_return * 100:.2f}%",
    )


with col3:

    st.metric(
        "Annualized Volatility",
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

    st.subheader("20-Day Rolling Volatility")


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
# CURRENT DATASET
# ============================================================

st.divider()

st.subheader("Dataset Preview")


st.dataframe(
    data.tail(20),
    hide_index=True,
    use_container_width=True,
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "AI Quantitative Research Platform • Phase 1 • "
    "Real Market Data"
)