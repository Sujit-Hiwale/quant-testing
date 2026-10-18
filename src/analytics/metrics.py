import math

import pandas as pd


def total_return(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0

    return equity.iloc[-1] / equity.iloc[0] - 1


def cagr(equity: pd.Series) -> float:
    if len(equity) < 2:
        return 0.0

    start = float(equity.iloc[0])
    end = float(equity.iloc[-1])

    if start <= 0 or end <= 0:
        return 0.0

    days = (equity.index[-1] - equity.index[0]).days

    if days <= 0:
        return 0.0

    years = days / 365.25

    return (end / start) ** (1 / years) - 1


def annualized_volatility(equity: pd.Series) -> float:
    returns = equity.pct_change().dropna()

    if len(returns) < 2:
        return 0.0

    return float(
        returns.std(ddof=1) * math.sqrt(252)
    )


def sharpe_ratio(
    equity: pd.Series,
    risk_free_rate: float = 0.0,
) -> float:
    returns = equity.pct_change().dropna()

    if len(returns) < 2:
        return 0.0

    daily_rf = (1 + risk_free_rate) ** (1 / 252) - 1
    excess_returns = returns - daily_rf

    volatility = excess_returns.std(ddof=1)

    if volatility == 0:
        return 0.0

    return float(
        excess_returns.mean()
        / volatility
        * math.sqrt(252)
    )


def sortino_ratio(
    equity: pd.Series,
    risk_free_rate: float = 0.0,
) -> float:
    returns = equity.pct_change().dropna()

    if len(returns) < 2:
        return 0.0

    daily_rf = (1 + risk_free_rate) ** (1 / 252) - 1
    excess_returns = returns - daily_rf

    downside = excess_returns[excess_returns < 0]

    if len(downside) == 0:
        return float("inf")

    downside_deviation = math.sqrt(
        (downside ** 2).mean()
    )

    if downside_deviation == 0:
        return 0.0

    return float(
        excess_returns.mean()
        / downside_deviation
        * math.sqrt(252)
    )


def max_drawdown(equity: pd.Series) -> float:
    if equity.empty:
        return 0.0

    running_max = equity.cummax()
    drawdown = equity / running_max - 1

    return float(drawdown.min())


def calculate_trade_metrics(trades) -> dict[str, float]:
    if not trades:
        return {
            "trade_count": 0,
            "win_rate": 0.0,
            "profit_factor": 0.0,
            "average_trade_return": 0.0,
            "average_holding_days": 0.0,
        }

    profits = [
        trade.net_pnl
        for trade in trades
        if trade.net_pnl > 0
    ]

    losses = [
        trade.net_pnl
        for trade in trades
        if trade.net_pnl < 0
    ]

    win_rate = len(profits) / len(trades)

    gross_profit = sum(profits)
    gross_loss = abs(sum(losses))

    if gross_loss == 0:
        profit_factor = float("inf") if gross_profit > 0 else 0.0
    else:
        profit_factor = gross_profit / gross_loss

    return {
        "trade_count": len(trades),
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "average_trade_return": (
            sum(trade.return_pct for trade in trades)
            / len(trades)
        ),
        "average_holding_days": (
            sum(trade.holding_days for trade in trades)
            / len(trades)
        ),
    }


def calculate_metrics(
    equity_curve: list[dict],
    trades=None,
) -> dict[str, float]:
    if not equity_curve:
        raise ValueError("Equity curve cannot be empty.")

    frame = pd.DataFrame(equity_curve)

    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"]
    )

    frame = frame.sort_values("timestamp")

    equity = frame.set_index("timestamp")["equity"]

    metrics = {
        "total_return": total_return(equity),
        "cagr": cagr(equity),
        "annualized_volatility": annualized_volatility(equity),
        "sharpe_ratio": sharpe_ratio(equity),
        "sortino_ratio": sortino_ratio(equity),
        "max_drawdown": max_drawdown(equity),
    }

    if trades is not None:
        metrics.update(
            calculate_trade_metrics(trades)
        )

    return metrics
