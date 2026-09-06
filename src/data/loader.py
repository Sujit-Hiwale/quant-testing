import yfinance as yf
import pandas as pd


def load_market_data(
    ticker: str,
    start: str,
    end: str
) -> pd.DataFrame:
    """
    Download historical market data for a ticker.

    Parameters
    ----------
    ticker : str
        Yahoo Finance ticker symbol.
        Example: RELIANCE.NS

    start : str
        Starting date in YYYY-MM-DD format.

    end : str
        Ending date in YYYY-MM-DD format.

    Returns
    -------
    pd.DataFrame
        Historical OHLCV data.
    """

    data = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False
    )

    if data.empty:
        raise ValueError(
            f"No data was returned for ticker: {ticker}"
        )

    # Flatten columns if yfinance returns a MultiIndex.
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    data.index.name = "Date"

    return data.reset_index()