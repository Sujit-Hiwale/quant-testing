import streamlit as st
import plotly.graph_objects as go

from components.sections import section
from components.cards import metric_row
from components.status import render_validation_status

from src.stats.distributions import (
    describe_returns,
    jarque_bera_test,
    normal_distribution_parameters,
)
from src.stats.time_series import (
    calculate_acf,
    ljung_box_test,
)


def render_research_statistics(context: dict) -> None:
    data = context["data"]
    validation = context["validation"]

    # ==================================================
    # Header
    # ==================================================

    section(
        "Statistical Analysis",
        f"Statistical diagnostics for {context['ticker']} "
        f"using the selected research dataset."
    )

    render_validation_status(validation)

    # ==================================================
    # Return Distribution
    # ==================================================

    section(
        "Return Distribution",
        "Descriptive statistics and distribution characteristics "
        "of daily returns."
    )

    returns = data["Return"].dropna()

    if returns.empty:
        st.warning("Not enough return observations for statistical analysis.")
        return

    description = describe_returns(returns)

    metric_row([
        {
            "label": "Mean",
            "value": f"{returns.mean() * 100:.4f}%",
            "description": "Average daily return",
        },
        {
            "label": "Std. Deviation",
            "value": f"{returns.std() * 100:.4f}%",
            "description": "Daily return dispersion",
        },
        {
            "label": "Skewness",
            "value": f"{returns.skew():.3f}",
            "description": "Distribution asymmetry",
        },
        {
            "label": "Kurtosis",
            "value": f"{returns.kurtosis():.3f}",
            "description": "Tail heaviness",
        },
    ])

    st.dataframe(
        description,
        use_container_width=True,
    )

    # ==================================================
    # Normality
    # ==================================================

    section(
        "Normality Analysis",
        "Tests whether observed returns are consistent with "
        "a normal distribution."
    )

    jb_result = jarque_bera_test(returns)

    if isinstance(jb_result, dict):
        statistic = jb_result.get("statistic")
        p_value = jb_result.get("p_value")
    else:
        statistic = getattr(jb_result, "statistic", None)
        p_value = getattr(jb_result, "pvalue", None)

    if p_value is not None:

        normality_status = (
            "Reject normality"
            if p_value < 0.05
            else "Cannot reject normality"
        )

        metric_row([
            {
                "label": "Jarque–Bera Statistic",
                "value": f"{statistic:.4f}",
                "description": "Normality test statistic",
            },
            {
                "label": "p-value",
                "value": f"{p_value:.4g}",
                "description": "Significance level: 5%",
            },
            {
                "label": "Result",
                "value": normality_status,
                "description": (
                    "Returns differ significantly from normality"
                    if p_value < 0.05
                    else "Insufficient evidence to reject normality"
                ),
            },
        ])

    # ==================================================
    # Normal Distribution Parameters
    # ==================================================

    section(
        "Normal Distribution Parameters",
        "Parameters of the normal distribution fitted to returns."
    )

    parameters = normal_distribution_parameters(returns)

    if isinstance(parameters, dict):

        mean_value = parameters.get("mean")
        std_value = parameters.get("std")

    else:

        mean_value = getattr(parameters, "mean", None)
        std_value = getattr(parameters, "std", None)

    if mean_value is not None and std_value is not None:

        metric_row([
            {
                "label": "Estimated Mean",
                "value": f"{mean_value:.6f}",
                "description": "μ",
            },
            {
                "label": "Estimated Std. Dev.",
                "value": f"{std_value:.6f}",
                "description": "σ",
            },
        ])

    # ==================================================
    # Autocorrelation
    # ==================================================

    section(
        "Return Autocorrelation",
        "Measures linear dependence between returns and their "
        "historical lags."
    )

    try:
        acf_values = calculate_acf(returns)

        if hasattr(acf_values, "values"):
            acf_values = acf_values.values

        acf_values = list(acf_values)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=list(range(len(acf_values))),
                y=acf_values,
                name="ACF",
            )
        )

        fig.update_layout(
            title="Autocorrelation of Daily Returns",
            xaxis_title="Lag",
            yaxis_title="Autocorrelation",
            hovermode="x unified",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    except Exception as exc:
        st.warning(f"Unable to calculate autocorrelation: {exc}")

    # ==================================================
    # Ljung-Box
    # ==================================================

    section(
        "Ljung–Box Test",
        "Tests whether a group of return autocorrelations is "
        "jointly different from zero."
    )

    try:
        lb_result = ljung_box_test(returns)

        st.dataframe(
            lb_result,
            use_container_width=True,
        )

    except Exception as exc:
        st.warning(f"Unable to perform Ljung–Box test: {exc}")

    # ==================================================
    # Volatility Clustering
    # ==================================================

    section(
        "Volatility Clustering",
        "Autocorrelation of squared returns can reveal persistence "
        "in volatility."
    )

    squared_returns = returns ** 2

    try:
        squared_acf = calculate_acf(squared_returns)

        if hasattr(squared_acf, "values"):
            squared_acf = squared_acf.values

        squared_acf = list(squared_acf)

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=list(range(len(squared_acf))),
                y=squared_acf,
                name="Squared Return ACF",
            )
        )

        fig.update_layout(
            title="Autocorrelation of Squared Returns",
            xaxis_title="Lag",
            yaxis_title="Autocorrelation",
            hovermode="x unified",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )

    except Exception as exc:
        st.warning(
            f"Unable to calculate squared-return autocorrelation: {exc}"
        )

    # ==================================================
    # Volatility Ljung-Box
    # ==================================================

    section(
        "Volatility Dependence Test",
        "Ljung–Box test applied to squared returns."
    )

    try:
        volatility_lb = ljung_box_test(squared_returns)

        st.dataframe(
            volatility_lb,
            use_container_width=True,
        )

    except Exception as exc:
        st.warning(
            f"Unable to perform volatility Ljung–Box test: {exc}"
        )

    # ==================================================
    # Raw Research Data
    # ==================================================

    section(
        "Statistical Dataset",
        "Return series used by the statistical diagnostics."
    )

    st.dataframe(
        data[
            [
                column
                for column in [
                    "Date",
                    "Close",
                    "Return",
                    "Log_Return",
                    "Volatility_20D",
                    "Volatility_60D",
                ]
                if column in data.columns
            ]
        ].tail(100),
        use_container_width=True,
    )