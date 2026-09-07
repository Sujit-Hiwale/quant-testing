import plotly.express as px
import plotly.graph_objects as go


def _apply_base_layout(fig):
    """
    Apply the application's common Plotly configuration.
    """

    fig.update_layout(

        margin=dict(
            l=10,
            r=10,
            t=85,
            b=35,
        ),

        hovermode="x unified",

        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="left",
            x=0,
            font=dict(size=12),
        ),
    )

    return fig


def price_chart(
    data,
    show_sma: bool = True,
):
    """
    Create the standard price chart.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Close"],
            name="Close",
            mode="lines",
        )
    )

    if show_sma:
        for column in ["SMA_20", "SMA_50", "SMA_200"]:
            if column in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data["Date"],
                        y=data[column],
                        name=column,
                        mode="lines",
                    )
                )

    fig.update_layout(
        title="Price history",
        yaxis_title="Price",
        xaxis_title="",
    )

    return _apply_base_layout(fig)


def returns_histogram(data):
    """
    Create the daily return distribution chart.
    """

    fig = px.histogram(
        data,
        x="Return",
        nbins=60,
        title="Daily return distribution",
    )

    fig.update_layout(
        xaxis_title="Daily return",
        yaxis_title="Observations",
    )

    return _apply_base_layout(fig)


def volatility_chart(data):
    """
    Create rolling volatility chart.
    """

    fig = go.Figure()

    for column in [
        "Volatility_20D",
        "Volatility_60D",
    ]:
        if column in data.columns:
            fig.add_trace(
                go.Scatter(
                    x=data["Date"],
                    y=data[column],
                    name=column,
                    mode="lines",
                )
            )

    fig.update_layout(
        title="Rolling annualized volatility",
        yaxis_title="Volatility",
        xaxis_title="",
    )

    return _apply_base_layout(fig)


def drawdown_chart(data):
    """
    Create historical drawdown chart.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Drawdown"],
            name="Drawdown",
            mode="lines",
            fill="tozeroy",
        )
    )

    fig.update_layout(
        title="Historical drawdown",
        yaxis_title="Drawdown",
        xaxis_title="",
    )

    return _apply_base_layout(fig)


def volume_chart(data):
    """
    Create trading volume chart.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=data["Date"],
            y=data["Volume"],
            name="Volume",
        )
    )

    fig.update_layout(
        title="Trading volume",
        yaxis_title="Volume",
        xaxis_title="",
    )

    return _apply_base_layout(fig)

def volume_ratio_chart(data):
    """
    Create the volume-to-20-day-average ratio chart.
    """

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["Date"],
            y=data["Volume_Ratio"],
            name="Volume Ratio",
            mode="lines",
        )
    )

    fig.add_hline(
        y=1,
        line_dash="dash",
    )

    fig.update_layout(
        title="Volume Relative to 20-Day Average",
        yaxis_title="Volume Ratio",
        xaxis_title="",
    )

    return _apply_base_layout(fig)