import streamlit as st


def render_app_header(
    mode: str,
    ticker: str,
) -> None:
    """
    Render the main application header.
    """

    left, right = st.columns([5, 1])

    with left:
        st.markdown(
            '<div class="app-kicker">Quant Testing</div>',
            unsafe_allow_html=True,
        )

        if mode == "User":
            st.markdown(
                '<div class="app-title">Market Intelligence</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="app-subtitle">
                    {ticker} · decision-focused market intelligence
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:
            st.markdown(
                '<div class="app-title">Research Workspace</div>',
                unsafe_allow_html=True,
            )

            st.markdown(
                f"""
                <div class="app-subtitle">
                    {ticker} · statistical evidence and quantitative research
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown(
            f"""
            <div style="
                text-align: right;
                padding-top: 0.7rem;
            ">
                <span class="status-pill">
                    {mode} mode
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )