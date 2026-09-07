import streamlit as st


TICKERS = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "ITC.NS",
    "^NSEI",
]


PERIODS = [
    "1 Year",
    "3 Years",
    "5 Years",
    "10 Years",
    "All Available",
]


def render_sidebar_branding() -> None:
    """
    Render the common sidebar branding.
    """

    st.sidebar.markdown("## Quant Testing")

    st.sidebar.caption(
        "Research-grade quantitative market intelligence"
    )


def render_asset_selector(
    current_ticker: str,
) -> str:
    """
    Render the shared asset selector.
    """

    return st.sidebar.selectbox(
        "Asset",
        TICKERS,
        index=(
            TICKERS.index(current_ticker)
            if current_ticker in TICKERS
            else 0
        ),
        key="global_ticker_selector",
    )


def render_period_selector(
    current_period: str,
) -> str:
    """
    Render the shared lookback-period selector.
    """

    return st.sidebar.selectbox(
        "Lookback period",
        PERIODS,
        index=(
            PERIODS.index(current_period)
            if current_period in PERIODS
            else 0
        ),
        key="global_period_selector",
    )


def render_mode_switch(
    current_mode: str,
) -> str:
    """
    Render the application-level User / Research switch.

    This is intentionally kept separate from page navigation.
    """

    mode = st.radio(
        "Application mode",
        ["User", "Research"],
        index=(
            0 if current_mode == "User"
            else 1
        ),
        horizontal=True,
        key="global_mode_selector",
        label_visibility="collapsed",
    )

    return mode


def render_research_navigation(
    current_page: str,
) -> str:
    """
    Render navigation for Research mode.
    """

    pages = [
        "Overview",
        "Analysis",
        "Statistics",
        "Models",
        "Experiments",
    ]

    return st.segmented_control(
        "Research section",
        pages,
        default=current_page if current_page in pages else "Overview",
        key="research_navigation",
        label_visibility="collapsed",
    ) or "Overview"