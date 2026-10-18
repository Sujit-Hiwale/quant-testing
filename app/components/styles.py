import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>

        /* =========================================================
           GLOBAL
        ========================================================= */

        .block-container {
            max-width: 1500px;
            padding-top: 1.6rem;
            padding-bottom: 5rem;
            padding-left: 3rem;
            padding-right: 3rem;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.65rem;
        }

        section[data-testid="stSidebar"] {
            border-right: 1px solid rgba(128,128,128,0.13);
        }

        section[data-testid="stSidebar"] > div {
            padding-top: 1.7rem;
        }

        /* subtle research-terminal background */

        .main .block-container::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: -1;

            background-image:
                linear-gradient(
                    rgba(128,128,128,0.025) 1px,
                    transparent 1px
                ),
                linear-gradient(
                    90deg,
                    rgba(128,128,128,0.025) 1px,
                    transparent 1px
                );

            background-size: 42px 42px;

            mask-image: linear-gradient(
                to bottom,
                black,
                transparent 85%
            );
        }

        /* =========================================================
           PAGE HEADER
           ========================================================= */

        .app-kicker {
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.15em;
            text-transform: uppercase;
            opacity: 0.48;
            margin-bottom: 0.4rem;
        }

        .app-title {
            font-size: 2.35rem;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -0.035em;
            margin: 0;
            animation: fadeUp 0.55s ease-out both;
        }

        .app-subtitle {
            font-size: 0.92rem;
            opacity: 0.55;
            margin-top: 0.55rem;
            animation: fadeUp 0.65s ease-out both;
        }

        /* =========================================================
           SECTION HEADERS
           ========================================================= */

        .section-title {
            font-size: 1.22rem;
            font-weight: 760;
            letter-spacing: -0.018em;
            margin-top: 2.15rem;
            margin-bottom: 0.18rem;
        }

        .section-subtitle {
            font-size: 0.82rem;
            opacity: 0.52;
            margin-bottom: 0.85rem;
        }

        /* =========================================================
           METRIC CARDS
           ========================================================= */

        .metric-card {
            position: relative;
            min-height: 112px;
            padding: 1rem 1.05rem;

            border: 1px solid rgba(128,128,128,0.14);
            border-radius: 15px;

            background:
                linear-gradient(
                    145deg,
                    rgba(128,128,128,0.065),
                    rgba(128,128,128,0.025)
                );

            overflow: hidden;

            animation: metricIn 0.55s cubic-bezier(.2,.8,.2,1) both;

            transition:
                transform 180ms ease,
                border-color 180ms ease,
                box-shadow 180ms ease;
        }

        .metric-card::after {
            content: "";
            position: absolute;
            width: 90px;
            height: 90px;
            right: -35px;
            top: -35px;

            border-radius: 50%;

            background: rgba(120,160,255,0.08);
            filter: blur(12px);

            pointer-events: none;
        }

        .metric-card:hover {
            transform: translateY(-3px);

            border-color: rgba(128,128,128,0.28);

            box-shadow:
                0 12px 30px rgba(0,0,0,0.08);
        }

        .metric-label {
            font-size: 0.71rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            opacity: 0.52;
            margin-bottom: 0.45rem;
        }

        .metric-value {
            font-size: 1.55rem;
            font-weight: 800;
            line-height: 1.1;
            letter-spacing: -0.025em;
        }

        .metric-description {
            font-size: 0.72rem;
            opacity: 0.46;
            margin-top: 0.48rem;
        }

        /* =========================================================
           STATUS
           ========================================================= */

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.45rem;

            padding: 0.32rem 0.72rem;

            border-radius: 999px;
            border: 1px solid rgba(128,128,128,0.2);

            font-size: 0.71rem;
            font-weight: 700;

            animation: fadeUp 0.5s ease-out both;
        }

        .status-dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            background: currentColor;
            box-shadow: 0 0 10px currentColor;
        }

        /* =========================================================
           RESEARCH VERDICT
           ========================================================= */

        .verdict-card {
            position: relative;

            padding: 1.45rem 1.55rem;
            margin: 0.7rem 0 1.2rem;

            border-radius: 18px;

            border: 1px solid rgba(128,128,128,0.18);

            background:
                linear-gradient(
                    135deg,
                    rgba(128,128,128,0.075),
                    rgba(128,128,128,0.025)
                );

            overflow: hidden;

            animation:
                verdictIn 0.7s cubic-bezier(.2,.8,.2,1) both;
        }

        .verdict-card::before {
            content: "";

            position: absolute;
            left: 0;
            top: 0;
            bottom: 0;
            width: 4px;

            background: currentColor;
            opacity: 0.75;
        }

        .verdict-status {
            font-size: 2rem;
            font-weight: 850;
            letter-spacing: -0.035em;
        }

        .verdict-label {
            font-size: 0.68rem;
            font-weight: 800;
            letter-spacing: 0.13em;
            text-transform: uppercase;
            opacity: 0.5;
        }

        .verdict-recommendation {
            font-size: 0.88rem;
            opacity: 0.65;
            margin-top: 0.55rem;
        }

        /* =========================================================
           NAVIGATION
           ========================================================= */

        .nav-label {
            font-size: 0.68rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            opacity: 0.45;
            margin-bottom: 0.3rem;
        }

        /* =========================================================
           STREAMLIT COMPONENTS
           ========================================================= */

        div[data-testid="stMetric"] {
            border: 1px solid rgba(128,128,128,0.14);
            border-radius: 13px;
            padding: 0.8rem;
            background: rgba(128,128,128,0.025);

            transition:
                transform 180ms ease,
                border-color 180ms ease;
        }

        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px);
            border-color: rgba(128,128,128,0.25);
        }

        div[data-testid="stDataFrame"] {
            border-radius: 12px;
            overflow: hidden;
        }

        button {
            border-radius: 9px !important;
            transition:
                transform 150ms ease,
                box-shadow 150ms ease !important;
        }

        button:hover {
            transform: translateY(-1px);
        }

        /* Plotly containers */

        div[data-testid="stPlotlyChart"] {
            animation: chartIn 0.65s ease-out both;
        }

        /* =========================================================
           ANIMATIONS
           ========================================================= */

        @keyframes fadeUp {
            from {
                opacity: 0;
                transform: translateY(8px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes metricIn {
            from {
                opacity: 0;
                transform: translateY(12px) scale(0.985);
            }

            to {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
        }

        @keyframes chartIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @keyframes verdictIn {
            from {
                opacity: 0;
                transform: translateY(14px);
            }

            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        /* =========================================================
           RESPONSIVE
           ========================================================= */

        @media (max-width: 1100px) {
            .block-container {
                padding-left: 1.5rem;
                padding-right: 1.5rem;
            }

            .app-title {
                font-size: 2rem;
            }
        }

        @media (max-width: 700px) {
            .block-container {
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .app-title {
                font-size: 1.7rem;
            }

            .section-title {
                margin-top: 1.5rem;
            }
        }

        /* respect accessibility settings */

        @media (prefers-reduced-motion: reduce) {
            *,
            *::before,
            *::after {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )