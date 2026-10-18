from datetime import datetime

import pandas as pd

from src.core.models import Bar


REQUIRED_COLUMNS = [
    "Date",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
]


def dataframe_to_bars(
    data: pd.DataFrame,
    symbol: str,
) -> list[Bar]:
    """
    Convert a cleaned market-data DataFrame into engine Bar objects.

    Expected columns:
        Date, Open, High, Low, Close, Volume
    """
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]

    if missing:
        raise ValueError(
            f"Cannot convert market data to bars. Missing columns: {missing}"
        )

    if data.empty:
        raise ValueError("Cannot convert empty market data to bars.")

    bars: list[Bar] = []

    for row in data.itertuples(index=False):
        timestamp = pd.Timestamp(row.Date).to_pydatetime()

        bars.append(
            Bar(
                timestamp=timestamp,
                symbol=symbol,
                open=float(row.Open),
                high=float(row.High),
                low=float(row.Low),
                close=float(row.Close),
                volume=float(row.Volume),
            )
        )

    return bars
