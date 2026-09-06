import streamlit as st

from src.data.loader import load_market_data
from src.data.validator import validate_market_data
from src.data.cleaner import clean_market_data


st.title("Market Data")

st.caption(
    "Historical market-data ingestion and validation"
)


# ------------------------------------------------------------
# Controls
# ------------------------------------------------------------

col1, col2, col3 = st.columns(3)

with col1:
    ticker = st.selectbox(
        "Ticker",
        [
            "RELIANCE.NS",
            "TCS.NS",
            "INFY.NS",
            "HDFCBANK.NS",
            "ICICIBANK.NS",
            "^NSEI",
        ]
    )

with col2:
    start_date = st.date_input(
        "Start date",
        value=None
    )

with col3:
    end_date = st.date_input(
        "End date",
        value=None
    )


# ------------------------------------------------------------
# Download
# ------------------------------------------------------------

if st.button("Fetch Market Data"):

    if start_date is None or end_date is None:
        st.warning("Please select both dates.")
        st.stop()

    with st.spinner("Fetching market data..."):

        try:

            data = load_market_data(
                ticker=ticker,
                start=str(start_date),
                end=str(end_date)
            )

        except Exception as error:

            st.error(
                f"Failed to fetch data: {error}"
            )

            st.stop()


    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    validation = validate_market_data(data)


    # --------------------------------------------------------
    # Validation summary
    # --------------------------------------------------------

    st.subheader("Data Quality")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Rows",
            validation.get("rows", 0)
        )

    with c2:
        st.metric(
            "Missing Values",
            validation.get("missing_values", 0)
        )

    with c3:
        st.metric(
            "Duplicate Dates",
            validation.get("duplicate_dates", 0)
        )

    with c4:
        st.metric(
            "Invalid OHLC",
            validation.get("invalid_ohlc", 0)
        )


    if validation["status"] == "PASS":

        st.success("✓ Data validation passed.")

    else:

        st.error("✗ Data validation failed.")

        st.json(validation)

        st.stop()


    # --------------------------------------------------------
    # Cleaning
    # --------------------------------------------------------

    data = clean_market_data(data)


    # --------------------------------------------------------
    # Preview
    # --------------------------------------------------------

    st.subheader("Dataset Preview")

    st.dataframe(
        data.head(50),
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------------
    # Dataset information
    # --------------------------------------------------------

    st.subheader("Dataset Information")

    info_col1, info_col2 = st.columns(2)

    with info_col1:

        st.write(
            f"**Ticker:** {ticker}"
        )

        st.write(
            f"**Observations:** {len(data):,}"
        )

    with info_col2:

        st.write(
            f"**First date:** "
            f"{data['Date'].min().date()}"
        )

        st.write(
            f"**Last date:** "
            f"{data['Date'].max().date()}"
        )


    # --------------------------------------------------------
    # Raw data download
    # --------------------------------------------------------

    csv = data.to_csv(index=False)

    st.download_button(
        label="Download Clean Dataset",
        data=csv,
        file_name=f"{ticker}_historical.csv",
        mime="text/csv"
    )