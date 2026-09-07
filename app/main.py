import streamlit as st

from components.styles import inject_styles
from components.layout import (
    render_sidebar_branding,
    render_asset_selector,
    render_period_selector,
    render_mode_switch,
    render_research_navigation,
)
from components.header import render_app_header
from components.status import render_data_error

from state.context import initialize_state, get_app_context

from pages.user.overview import render_user_overview
from pages.research.overview import render_research_overview
from pages.research.analysis import render_research_analysis
from pages.research.statistics import render_research_statistics

st.set_page_config(
    page_title="AI Quantitative Research Platform",
    page_icon="📊",
    layout="wide",
)


# --------------------------------------------------
# Application initialization
# --------------------------------------------------

initialize_state()
inject_styles()

render_sidebar_branding()

st.session_state.ticker = render_asset_selector(
    st.session_state.ticker
)

st.session_state.period = render_period_selector(
    st.session_state.period
)


# --------------------------------------------------
# Shared application context
# --------------------------------------------------

context = get_app_context()

if context["error"]:
    render_data_error(context["error"])
    st.stop()


# --------------------------------------------------
# Header
# --------------------------------------------------

render_app_header(
    mode=context["mode"],
    ticker=context["ticker"],
)


# --------------------------------------------------
# Mode switch
# --------------------------------------------------

st.session_state.mode = render_mode_switch(
    context["mode"]
)

context["mode"] = st.session_state.mode


# --------------------------------------------------
# Navigation
# --------------------------------------------------

if context["mode"] == "Research":
    st.session_state.research_page = render_research_navigation(
        st.session_state.research_page
    )

    context["research_page"] = st.session_state.research_page


# --------------------------------------------------
# Router
# --------------------------------------------------

if context["mode"] == "User":

    render_user_overview(context)


elif context["mode"] == "Research":

    if context["research_page"] == "Overview":
        render_research_overview(context)

    elif context["research_page"] == "Analysis":
        render_research_analysis(context)

    elif context["research_page"] == "Statistics":
        render_research_statistics(context)

    elif context["research_page"] == "Models":
        st.info("Models page coming next.")

    elif context["research_page"] == "Experiments":
        st.info("Experiments page coming next.")