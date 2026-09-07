import streamlit as st


def inject_styles() -> None:
    """Inject the global visual system for the application."""

    st.markdown(
        """
        <style>

        /* =========================================================
           GLOBAL LAYOUT
           ========================================================= */

        .block-container {
            max-width: 1450px;
            padding-top: 2rem;
            padding-bottom: 4rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        /* Reduce excessive Streamlit vertical spacing */
        div[data-testid="stVerticalBlock"] {
            gap: 0.7rem;
        }

        /* =========================================================
           SIDEBAR
           ========================================================= */

        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(128, 128, 128, 0.16);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 2rem;
        }

        /* =========================================================
           APPLICATION HEADER
           ========================================================= */

        .app-kicker {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            opacity: 0.55;
            margin-bottom: 0.35rem;
        }

        .app-title {
            font-size: 2.15rem;
            font-weight: 750;
            line-height: 1.1;
            letter-spacing: -0.025em;
            margin: 0;
        }

        .app-subtitle {
            font-size: 0.95rem;
            opacity: 0.62;
            margin-top: 0.45rem;
        }

        /* =========================================================
           SECTION HEADERS
           ========================================================= */

        .section-title {
            font-size: 1.25rem;
            font-weight: 700;
            letter-spacing: -0.01em;
            margin-top: 2rem;
            margin-bottom: 0.2rem;
        }

        .section-subtitle {
            font-size: 0.86rem;
            opacity: 0.58;
            margin-bottom: 0.9rem;
        }

        /* =========================================================
           METRIC CARDS
           ========================================================= */

        .metric-card {
            min-height: 115px;
            padding: 1rem 1.05rem;
            border: 1px solid rgba(128, 128, 128, 0.17);
            border-radius: 14px;
            background: rgba(128, 128, 128, 0.045);
        }

        .metric-label {
            font-size: 0.76rem;
            font-weight: 600;
            opacity: 0.58;
            margin-bottom: 0.45rem;
        }

        .metric-value {
            font-size: 1.55rem;
            font-weight: 750;
            line-height: 1.1;
            letter-spacing: -0.02em;
        }

        .metric-description {
            font-size: 0.75rem;
            opacity: 0.5;
            margin-top: 0.5rem;
        }

        /* =========================================================
           STATUS
           ========================================================= */

        .status-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.3rem 0.7rem;
            border-radius: 999px;
            border: 1px solid rgba(128, 128, 128, 0.2);
            font-size: 0.74rem;
            font-weight: 650;
        }

        /* =========================================================
           NAVIGATION
           ========================================================= */

        .nav-label {
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            opacity: 0.5;
            margin-bottom: 0.25rem;
        }

        /* =========================================================
           STREAMLIT COMPONENT POLISH
           ========================================================= */

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128, 128, 128, 0.16);
            border-radius: 12px;
            padding: 0.8rem;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 10px;
        }

        button {
            border-radius: 9px !important;
        }

        /* =========================================================
           MOBILE
           ========================================================= */

        @media (max-width: 900px) {
            .block-container {
                padding-left: 1.2rem;
                padding-right: 1.2rem;
            }

            .app-title {
                font-size: 1.75rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )