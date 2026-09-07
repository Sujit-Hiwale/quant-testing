import pandas as pd
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.stattools import acf


def calculate_acf(
    series: pd.Series,
    lags: int = 30,
) -> pd.Series:
    """
    Calculate autocorrelation coefficients.
    """

    series = series.dropna()

    values = acf(
        series,
        nlags=lags,
        fft=True,
    )

    return pd.Series(
        values,
        index=range(len(values)),
        name="Autocorrelation",
    )


def ljung_box_test(
    series: pd.Series,
    lags: int = 20,
) -> pd.DataFrame:
    """
    Perform the Ljung-Box test for autocorrelation.

    H0: There is no autocorrelation up to the specified lag.
    H1: There is autocorrelation at one or more lags.
    """

    series = series.dropna()

    result = acorr_ljungbox(
        series,
        lags=lags,
        return_df=True,
    )

    return result