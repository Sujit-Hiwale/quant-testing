import streamlit as st


def section(
    title: str,
    subtitle: str | None = None,
) -> None:
    """
    Render a consistent application section heading.
    """

    st.markdown(
        f'<div class="section-title">{title}</div>',
        unsafe_allow_html=True,
    )

    if subtitle:
        st.markdown(
            f'<div class="section-subtitle">{subtitle}</div>',
            unsafe_allow_html=True,
        )


def divider() -> None:
    """Render a subtle section divider."""

    st.markdown(
        """
        <div style="
            height: 1px;
            background: rgba(128,128,128,0.14);
            margin: 1.5rem 0;
        "></div>
        """,
        unsafe_allow_html=True,
    )