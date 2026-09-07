import numpy as np
import pandas as pd
from scipy import stats


def describe_returns(returns: pd.Series) -> dict:
    """
    Calculate descriptive statistics for a return series.
    """

    returns = returns.dropna()

    return {
        "count": len(returns),
        "mean": returns.mean(),
        "std": returns.std(),
        "min": returns.min(),
        "max": returns.max(),
        "skewness": stats.skew(returns),
        "kurtosis": stats.kurtosis(returns),
        "median": returns.median(),
    }


def jarque_bera_test(returns: pd.Series) -> dict:
    """
    Perform the Jarque-Bera test for normality.

    H0: The data follows a normal distribution.
    H1: The data does not follow a normal distribution.
    """

    returns = returns.dropna()

    statistic, p_value = stats.jarque_bera(returns)

    return {
        "statistic": statistic,
        "p_value": p_value,
        "normal_at_5_percent": p_value >= 0.05,
    }


def normal_distribution_parameters(
    returns: pd.Series,
) -> tuple[float, float]:
    """
    Return mean and standard deviation of the return series.
    """

    returns = returns.dropna()

    return returns.mean(), returns.std()