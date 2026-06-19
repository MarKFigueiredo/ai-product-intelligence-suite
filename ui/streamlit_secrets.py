"""Bridge selected app secrets into environment variables for pure services."""

from __future__ import annotations

import os
from collections.abc import Iterable

import streamlit as st


def sync_streamlit_secrets_to_env(keys: Iterable[str] = ("OPENAI_API_KEY",)) -> None:
    """Copy selected UI secrets into environment variables when not already set.

    Services read configuration from the environment. The Streamlit-specific
    secrets mechanism remains isolated in the UI layer.
    """

    for key in keys:
        if os.getenv(key):
            continue

        try:
            value = str(st.secrets.get(key, "")).strip()
        except Exception:
            value = ""

        if value:
            os.environ[key] = value
