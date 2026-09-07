import streamlit as st


def render_validation_status(validation: dict) -> None:
    """
    Display dataset validation status.
    """

    status = validation.get("status", "UNKNOWN")

    if status == "PASS":
        st.success("Dataset validation passed.")

    elif status == "FAIL":
        st.error("Dataset validation failed.")

        details = validation.get("details", [])

        if details:
            for detail in details:
                st.write(f"• {detail}")

    else:
        st.warning("Dataset validation status is unknown.")


def render_data_error(message: str | None) -> None:
    """
    Display a standardized data-loading error.
    """

    if message:
        st.error(
            f"Unable to load market data.\n\n{message}"
        )
    else:
        st.error("Unable to load market data.")