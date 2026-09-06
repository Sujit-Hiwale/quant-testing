import pandas as pd


REQUIRED_COLUMNS = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


def validate_market_data(
    data: pd.DataFrame
) -> dict:
    """
    Validate a market-data DataFrame.

    Returns a dictionary containing
    validation results.
    """

    results = {}

    # --------------------------------------------------------
    # Required columns
    # --------------------------------------------------------

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    results["missing_columns"] = missing_columns

    # Stop further OHLC checks if required columns are absent.
    if missing_columns:
        results["status"] = "FAIL"
        results["error"] = (
            f"Missing required columns: {missing_columns}"
        )
        return results

    # --------------------------------------------------------
    # Basic information
    # --------------------------------------------------------

    results["rows"] = len(data)

    # --------------------------------------------------------
    # Missing values
    # --------------------------------------------------------

    results["missing_values"] = (
        data[REQUIRED_COLUMNS]
        .isna()
        .sum()
        .sum()
    )

    # --------------------------------------------------------
    # Duplicate dates
    # --------------------------------------------------------

    results["duplicate_dates"] = (
        data["Date"]
        .duplicated()
        .sum()
    )

    # --------------------------------------------------------
    # Date ordering
    # --------------------------------------------------------

    results["date_sorted"] = data["Date"].is_monotonic_increasing

    # --------------------------------------------------------
    # Invalid OHLC relationships
    # --------------------------------------------------------

    invalid_ohlc = (
        (data["High"] < data["Low"])
        |
        (data["Open"] > data["High"])
        |
        (data["Open"] < data["Low"])
        |
        (data["Close"] > data["High"])
        |
        (data["Close"] < data["Low"])
    )

    results["invalid_ohlc"] = invalid_ohlc.sum()

    # --------------------------------------------------------
    # Invalid volume
    # --------------------------------------------------------

    results["negative_volume"] = (
        data["Volume"] < 0
    ).sum()

    # --------------------------------------------------------
    # Overall status
    # --------------------------------------------------------

    passed = (
        len(missing_columns) == 0
        and results["missing_values"] == 0
        and results["duplicate_dates"] == 0
        and results["date_sorted"]
        and results["invalid_ohlc"] == 0
        and results["negative_volume"] == 0
    )

    results["status"] = "PASS" if passed else "FAIL"

    return results