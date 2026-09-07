import streamlit as st


def metric_card(
    label: str,
    value: str,
    description: str = "",
) -> None:
    """
    Render a single application metric card.
    """

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_row(items: list[dict]) -> None:
    """
    Render multiple metric cards in a single row.

    Example:
        metric_row([
            {
                "label": "Latest Price",
                "value": "2,450",
                "description": "Latest available close",
            },
            ...
        ])
    """

    if not items:
        return

    columns = st.columns(len(items))

    for column, item in zip(columns, items):
        with column:
            metric_card(
                label=item["label"],
                value=item["value"],
                description=item.get("description", ""),
            )