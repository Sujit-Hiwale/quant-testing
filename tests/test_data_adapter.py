from datetime import datetime

import pandas as pd
import pytest

from src.core.data_adapter import dataframe_to_bars


def test_dataframe_to_bars():
    data = pd.DataFrame(
        {
            "Date": [
                "2024-01-01",
                "2024-01-02",
            ],
            "Open": [100, 105],
            "High": [110, 112],
            "Low": [95, 101],
            "Close": [105, 110],
            "Volume": [1000, 1200],
        }
    )

    bars = dataframe_to_bars(data, "TEST")

    assert len(bars) == 2
    assert bars[0].symbol == "TEST"
    assert bars[0].open == 100
    assert bars[0].close == 105
    assert bars[1].timestamp == datetime(2024, 1, 2)


def test_dataframe_to_bars_rejects_missing_columns():
    data = pd.DataFrame(
        {
            "Date": ["2024-01-01"],
            "Open": [100],
            "Close": [105],
        }
    )

    with pytest.raises(ValueError):
        dataframe_to_bars(data, "TEST")


def test_dataframe_to_bars_rejects_empty_data():
    data = pd.DataFrame(
        columns=[
            "Date",
            "Open",
            "High",
            "Low",
            "Close",
            "Volume",
        ]
    )

    with pytest.raises(ValueError):
        dataframe_to_bars(data, "TEST")
