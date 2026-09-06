import pandas as pd

from src.data.validator import validate_market_data
from src.data.cleaner import clean_market_data


def test_valid_market_data():

    data = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                ]
            ),
            "Open": [100, 102, 103],
            "High": [105, 106, 107],
            "Low": [98, 100, 101],
            "Close": [102, 104, 106],
            "Volume": [1000, 1200, 1500],
        }
    )

    result = validate_market_data(data)

    assert result["status"] == "PASS"


def test_cleaning_duplicates():

    data = pd.DataFrame(
        {
            "Date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-01",
                    "2024-01-02",
                ]
            ),
            "Open": [100, 100, 102],
            "High": [105, 105, 106],
            "Low": [98, 98, 100],
            "Close": [102, 102, 104],
            "Volume": [1000, 1000, 1200],
        }
    )

    cleaned = clean_market_data(data)

    assert len(cleaned) == 2