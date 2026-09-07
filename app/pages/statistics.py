import streamlit as st
import plotly.graph_objects as go
import numpy as np
from scipy import stats
from datetime import date
from dateutil.relativedelta import relativedelta

from src.data.loader import load_market_data
from src.data.validator import validate_market_data
from src.data.cleaner import clean_market_data
from src.features.engineering import create_market_features
from src.stats.distributions import (
    describe_returns,
    jarque_bera_test,
)
from src.stats.time_series import (
    calculate_acf,
    ljung_box_test,
)

# ---------------------------------------------------------
# Page configuration
# ---------------------------------------------------------

st.set_page_config(
    page_title="Statistical Analysis",
    page_icon="📈",
    layout="wide",
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
        "^NSEI",
    ],
)

period = st.sidebar.selectbox(
    "Historical Period",
    [
        "1 Year",
        "3 Years",
        "5 Years",
        "10 Years",
        "All Available",
    ],
    index=2,
)


# ---------------------------------------------------------
# Date range
# ---------------------------------------------------------

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
        end=end_date.strftime("%Y-%m-%d"),
    )

except Exception as e:

    st.error(f"Failed to load market data: {e}")
    st.stop()


# ---------------------------------------------------------
# Validate
# ---------------------------------------------------------

validation = validate_market_data(data)

if validation["status"] != "PASS":

    st.error("Market data validation failed.")

    for error in validation["details"]:
        st.write(f"• {error}")

    st.stop()


# ---------------------------------------------------------
# Clean + features
# ---------------------------------------------------------

data = clean_market_data(data)
data = create_market_features(data)

returns = data["Log_Return"].dropna()


# ---------------------------------------------------------
# Header
# ---------------------------------------------------------

st.title("📈 Statistical Analysis")

st.caption(
    f"Statistical investigation of daily log returns for "
    f"**{ticker}**."
)


st.info(
    "Research question: Are daily returns approximately "
    "normally distributed?"
)


# =========================================================
# DESCRIPTIVE STATISTICS
# =========================================================

st.header("1. Return Distribution")

statistics = describe_returns(returns)


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Observations",
    f"{statistics['count']:,}",
)

col2.metric(
    "Mean",
    f"{statistics['mean'] * 100:.4f}%",
)

col3.metric(
    "Std. Deviation",
    f"{statistics['std'] * 100:.4f}%",
)

col4.metric(
    "Median",
    f"{statistics['median'] * 100:.4f}%",
)


# =========================================================
# DISTRIBUTION
# =========================================================

st.subheader("Daily Log-Return Distribution")

fig = go.Figure()

fig.add_trace(
    go.Histogram(
        x=returns,
        nbinsx=80,
        histnorm="probability density",
        name="Observed Returns",
    )
)


# Normal distribution for comparison

mean = returns.mean()
std = returns.std()

x = np.linspace(
    returns.min(),
    returns.max(),
    500,
)

normal_pdf = stats.norm.pdf(
    x,
    mean,
    std,
)

fig.add_trace(
    go.Scatter(
        x=x,
        y=normal_pdf,
        mode="lines",
        name="Normal Distribution",
    )
)

fig.update_layout(
    title="Observed Returns vs Normal Distribution",
    xaxis_title="Log Return",
    yaxis_title="Density",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)


# =========================================================
# SKEWNESS + KURTOSIS
# =========================================================

st.subheader("Distribution Shape")

col1, col2, col3 = st.columns(3)

col1.metric(
    "Skewness",
    f"{statistics['skewness']:.4f}",
)

col2.metric(
    "Excess Kurtosis",
    f"{statistics['kurtosis']:.4f}",
)

col3.metric(
    "Minimum Return",
    f"{statistics['min'] * 100:.2f}%",
)


st.caption(
    "Excess kurtosis is reported relative to the normal "
    "distribution, which has a value of 0."
)


# =========================================================
# JARQUE-BERA TEST
# =========================================================

st.header("2. Normality Test")

test = jarque_bera_test(returns)

col1, col2 = st.columns(2)

col1.metric(
    "Jarque-Bera Statistic",
    f"{test['statistic']:.4f}",
)

col2.metric(
    "p-value",
    f"{test['p_value']:.6g}",
)


alpha = 0.05

if test["p_value"] < alpha:

    st.error(
        "Reject H₀ at the 5% significance level. "
        "There is statistical evidence that the return "
        "distribution differs from a normal distribution."
    )

else:

    st.success(
        "Fail to reject H₀ at the 5% significance level. "
        "There is insufficient statistical evidence to "
        "reject normality."
    )


# =========================================================
# INTERPRETATION
# =========================================================

st.header("3. Interpretation")

skewness = statistics["skewness"]
kurtosis = statistics["kurtosis"]

if abs(skewness) < 0.5:
    skew_text = "approximately symmetric"
elif skewness > 0:
    skew_text = "positively skewed"
else:
    skew_text = "negatively skewed"


if kurtosis > 1:
    kurtosis_text = "heavy-tailed relative to a normal distribution"
elif kurtosis < -1:
    kurtosis_text = "light-tailed relative to a normal distribution"
else:
    kurtosis_text = "not strongly different in tail weight from normality"


st.write(
    f"""
    The observed return distribution is **{skew_text}**
    with a skewness of **{skewness:.3f}**.

    Its excess kurtosis is **{kurtosis:.3f}**, indicating that
    the distribution is **{kurtosis_text}**.

    The Jarque-Bera test produces a p-value of
    **{test['p_value']:.6g}** at a significance level of
    **5%**.
    """
)

# =========================================================
# AUTOCORRELATION
# =========================================================

st.header("4. Time-Series Dependence")

st.info(
    "Research question: Are returns independent over time, "
    "or does information from previous days persist?"
)


# ---------------------------------------------------------
# ACF of returns
# ---------------------------------------------------------

st.subheader("Autocorrelation of Returns")

acf_returns = calculate_acf(
    returns,
    lags=30,
)

fig_acf = go.Figure()

fig_acf.add_trace(
    go.Bar(
        x=acf_returns.index,
        y=acf_returns.values,
        name="Return ACF",
    )
)

fig_acf.add_hline(y=0)

fig_acf.update_layout(
    title="Autocorrelation Function — Daily Log Returns",
    xaxis_title="Lag",
    yaxis_title="Autocorrelation",
)

st.plotly_chart(
    fig_acf,
    use_container_width=True,
)


# ---------------------------------------------------------
# Ljung-Box test — returns
# ---------------------------------------------------------

st.subheader("Ljung-Box Test — Returns")

lb_returns = ljung_box_test(
    returns,
    lags=20,
)

st.dataframe(
    lb_returns,
    use_container_width=True,
)

p_value_returns = lb_returns["lb_pvalue"].iloc[-1]

if p_value_returns < 0.05:

    st.warning(
        f"The Ljung-Box test gives a p-value of "
        f"{p_value_returns:.6g}. We reject the null hypothesis "
        "of no autocorrelation at the 5% level."
    )

else:

    st.success(
        f"The Ljung-Box test gives a p-value of "
        f"{p_value_returns:.6g}. We fail to reject the null "
        "hypothesis of no autocorrelation at the 5% level."
    )


# =========================================================
# VOLATILITY CLUSTERING
# =========================================================

st.header("5. Volatility Clustering")

st.info(
    "Research question: Does high volatility tend to be "
    "followed by high volatility, and low volatility by low volatility?"
)


# Squared returns

squared_returns = returns ** 2


# ---------------------------------------------------------
# ACF of squared returns
# ---------------------------------------------------------

st.subheader("Autocorrelation of Squared Returns")

acf_squared = calculate_acf(
    squared_returns,
    lags=30,
)

fig_squared = go.Figure()

fig_squared.add_trace(
    go.Bar(
        x=acf_squared.index,
        y=acf_squared.values,
        name="Squared Return ACF",
    )
)

fig_squared.add_hline(y=0)

fig_squared.update_layout(
    title="Autocorrelation Function — Squared Log Returns",
    xaxis_title="Lag",
    yaxis_title="Autocorrelation",
)

st.plotly_chart(
    fig_squared,
    use_container_width=True,
)


# ---------------------------------------------------------
# Ljung-Box — squared returns
# ---------------------------------------------------------

st.subheader("Ljung-Box Test — Squared Returns")

lb_squared = ljung_box_test(
    squared_returns,
    lags=20,
)

st.dataframe(
    lb_squared,
    use_container_width=True,
)

p_value_squared = lb_squared["lb_pvalue"].iloc[-1]

if p_value_squared < 0.05:

    st.success(
        f"The Ljung-Box test gives a p-value of "
        f"{p_value_squared:.6g}. There is statistical evidence "
        "of dependence in squared returns, consistent with "
        "volatility clustering."
    )

else:

    st.info(
        f"The Ljung-Box test gives a p-value of "
        f"{p_value_squared:.6g}. We fail to reject the null "
        "hypothesis of no autocorrelation in squared returns."
    )


# =========================================================
# RAW DATA
# =========================================================

with st.expander("View Return Data"):

    st.dataframe(
        data[
            [
                "Date",
                "Close",
                "Return",
                "Log_Return",
            ]
        ].tail(200),
        use_container_width=True,
    )