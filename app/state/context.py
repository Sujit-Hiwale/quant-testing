from datetime import date

import streamlit as st
from dateutil.relativedelta import relativedelta

from src.data.loader import load_market_data
from src.data.validator import validate_market_data
from src.data.cleaner import clean_market_data
from src.features.engineering import create_market_features


DEFAULT_TICKER = "RELIANCE.NS"
DEFAULT_PERIOD = "1 Year"
DEFAULT_MODE = "User"

PERIOD_YEARS = {
    "1 Year": 1,
    "3 Years": 3,
    "5 Years": 5,
    "10 Years": 10,
}


def initialize_state() -> None:
    """Initialize application-wide Streamlit state."""

    if "mode" not in st.session_state:
        st.session_state.mode = DEFAULT_MODE

    if "ticker" not in st.session_state:
        st.session_state.ticker = DEFAULT_TICKER

    if "period" not in st.session_state:
        st.session_state.period = DEFAULT_PERIOD

    if "research_page" not in st.session_state:
        st.session_state.research_page = "Overview"


def get_date_range(period: str) -> tuple[date, date]:
    """Convert a UI period into start and end dates."""

    end_date = date.today()

    if period == "All Available":
        return date(2010, 1, 1), end_date

    years = PERIOD_YEARS.get(period, 1)

    start_date = end_date - relativedelta(years=years)

    return start_date, end_date


@st.cache_data(show_spinner=False)
def load_research_data(
    ticker: str,
    start: date,
    end: date,
) -> dict:
    """
    Load, validate, clean and engineer market data.

    Raw validation is retained for diagnostics, while
    cleaned validation determines whether the dataset
    is suitable for downstream analysis.
    """

    # --------------------------------------------------
    # 1. Load
    # --------------------------------------------------

    raw_data = load_market_data(
        ticker=ticker,
        start=start.isoformat(),
        end=end.isoformat(),
    )

    # --------------------------------------------------
    # 2. Validate raw data
    # --------------------------------------------------

    raw_validation = validate_market_data(raw_data)

    # --------------------------------------------------
    # 3. Clean
    # --------------------------------------------------

    cleaned_data = clean_market_data(raw_data)

    # --------------------------------------------------
    # 4. Validate cleaned data
    # --------------------------------------------------

    cleaned_validation = validate_market_data(cleaned_data)

    # --------------------------------------------------
    # 5. Feature engineering
    # --------------------------------------------------

    data = create_market_features(cleaned_data)

    return {
        "raw": raw_data,
        "raw_validation": raw_validation,
        "cleaned": cleaned_data,
        "validation": cleaned_validation,
        "data": data,
    }


def get_app_context() -> dict:
    """
    Build the shared application context used by
    every page.
    """

    initialize_state()

    ticker = st.session_state.ticker
    period = st.session_state.period
    mode = st.session_state.mode

    start_date, end_date = get_date_range(period)

    try:

        result = load_research_data(
            ticker=ticker,
            start=start_date,
            end=end_date,
        )

        return {
            "mode": mode,
            "ticker": ticker,
            "period": period,
            "start": start_date,
            "end": end_date,

            "raw": result["raw"],

            # Validation after cleaning is the
            # validation shown to the application.
            "validation": result["validation"],

            # Keep raw validation available for
            # future Research/Data pages.
            "raw_validation": result["raw_validation"],

            "cleaned": result["cleaned"],
            "data": result["data"],

            "error": None,
        }

    except Exception as exc:

        return {
            "mode": mode,
            "ticker": ticker,
            "period": period,
            "start": start_date,
            "end": end_date,

            "raw": None,
            "raw_validation": None,
            "validation": None,
            "cleaned": None,
            "data": None,

            "error": str(exc),
        }