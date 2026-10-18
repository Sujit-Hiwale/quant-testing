import pandas as pd
import math

from src.research.walk_forward import (
    _chain_equity_curves,
)


def test_chain_equity_curves_compounds_returns():

    curves = [
        [
            {
                "timestamp": pd.Timestamp("2022-01-01"),
                "equity": 100_000,
            },
            {
                "timestamp": pd.Timestamp("2022-12-31"),
                "equity": 90_000,
            },
        ],
        [
            {
                "timestamp": pd.Timestamp("2023-01-01"),
                "equity": 100_000,
            },
            {
                "timestamp": pd.Timestamp("2023-12-31"),
                "equity": 120_000,
            },
        ],
    ]

    result = _chain_equity_curves(
        curves,
        initial_cash=100_000,
    )

    assert result[-1]["equity"] == 108_000


def test_chain_equity_curves_preserves_order():

    curves = [
        [
            {
                "timestamp": pd.Timestamp("2022-01-01"),
                "equity": 100_000,
            },
            {
                "timestamp": pd.Timestamp("2022-12-31"),
                "equity": 110_000,
            },
        ],
        [
            {
                "timestamp": pd.Timestamp("2023-01-01"),
                "equity": 100_000,
            },
            {
                "timestamp": pd.Timestamp("2023-12-31"),
                "equity": 90_000,
            },
        ],
    ]

    result = _chain_equity_curves(
        curves,
        initial_cash=100_000,
    )

    assert math.isclose(
        result[-1]["equity"],
        99_000,
        rel_tol=1e-12,
        abs_tol=1e-9,
    )