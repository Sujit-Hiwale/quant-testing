import pandas as pd


def buy_and_hold_equity_curve(
    data: pd.DataFrame,
    initial_cash: float,
) -> list[dict]:
    required = {"Date", "Close"}

    missing = required - set(data.columns)

    if missing:
        raise ValueError(
            f"Missing benchmark columns: {sorted(missing)}"
        )

    if data.empty:
        raise ValueError("Cannot calculate benchmark from empty data.")

    first_price = float(data.iloc[0]["Close"])

    if first_price <= 0:
        raise ValueError("Initial benchmark price must be positive.")

    quantity = int(initial_cash // first_price)

    if quantity <= 0:
        raise ValueError(
            "Initial cash is insufficient to purchase one share."
        )

    remaining_cash = initial_cash - quantity * first_price

    curve = []

    for row in data.itertuples(index=False):
        price = float(row.Close)

        equity = remaining_cash + quantity * price

        curve.append(
            {
                "timestamp": pd.Timestamp(row.Date).to_pydatetime(),
                "equity": equity,
            }
        )

    return curve
