"""UI rendering helpers for OpenAI-related errors."""

from __future__ import annotations

import streamlit as st


def render_openai_error(error: Exception) -> None:
    """Render a user-facing OpenAI error message in the app UI."""

    st.error("The AI request failed.")

    message = str(error)
    lowered = message.lower()

    if "insufficient_quota" in message or "quota" in lowered:
        st.info("This usually means API billing/credits are not active or your quota was reached. Try Demo Mode first.")
    elif "model" in lowered and "not" in lowered:
        st.info("The selected model may not be available to your account. Try a smaller/default model.")
    elif "api" in lowered and "key" in lowered:
        st.info("Check your environment configuration and API key permissions.")

    st.code(message)
