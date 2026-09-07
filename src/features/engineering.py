import numpy as np
import pandas as pd


def create_market_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Create basic features from OHLCV market data.
    """

    data = data.copy()

    # --------------------------------------------------------
    # Returns
    # --------------------------------------------------------

    data["Return"] = data["Close"].pct_change()

    data["Log_Return"] = np.log(
        data["Close"] / data["Close"].shift(1)
    )

    # --------------------------------------------------------
    # Moving averages
    # --------------------------------------------------------

    data["SMA_20"] = (
        data["Close"]
        .rolling(20)
        .mean()
    )

    data["SMA_50"] = (
        data["Close"]
        .rolling(50)
        .mean()
    )

    data["SMA_200"] = (
        data["Close"]
        .rolling(200)
        .mean()
    )

    # --------------------------------------------------------
    # Rolling volatility
    # --------------------------------------------------------

    data["Volatility_20D"] = (
        data["Log_Return"]
        .rolling(20)
        .std()
        * np.sqrt(252)
    )

    data["Volatility_60D"] = (
        data["Log_Return"]
        .rolling(60)
        .std()
        * np.sqrt(252)
    )

    # --------------------------------------------------------
    # Volume features
    # --------------------------------------------------------

    data["Volume_SMA_20"] = (
        data["Volume"]
        .rolling(20)
        .mean()
    )

    data["Volume_Ratio"] = (
        data["Volume"] /
        data["Volume_SMA_20"]
    )

    # --------------------------------------------------------
    # Drawdown
    # --------------------------------------------------------

    rolling_max = data["Close"].cummax()

    data["Drawdown"] = (
        data["Close"] / rolling_max - 1
    )

    return data