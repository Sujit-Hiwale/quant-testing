import pandas as pd


def clean_market_data(
    data: pd.DataFrame
) -> pd.DataFrame:
    """
    Clean validated market data.

    The function deliberately performs
    only conservative transformations.
    """

    data = data.copy()

    # --------------------------------------------------------
    # Ensure Date is datetime
    # --------------------------------------------------------

    data["Date"] = pd.to_datetime(data["Date"])

    # --------------------------------------------------------
    # Sort chronologically
    # --------------------------------------------------------

    data = data.sort_values("Date")

    # --------------------------------------------------------
    # Remove duplicate dates
    # --------------------------------------------------------

    data = data.drop_duplicates(
        subset="Date",
        keep="first"
    )

    # --------------------------------------------------------
    # Remove rows with missing core market values
    # --------------------------------------------------------

    required_columns = [
        "Open",
        "High",
        "Low",
        "Close",
        "Volume",
    ]

    data = data.dropna(
        subset=required_columns
    )

    # --------------------------------------------------------
    # Reset index
    # --------------------------------------------------------

    data = data.reset_index(drop=True)

    return data