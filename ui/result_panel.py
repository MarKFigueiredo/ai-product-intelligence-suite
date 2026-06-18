"""Result display and exports."""
from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from services.export_service import extract_named_tables, rows_to_df
from ui.visual_components import render_standard_export_bar


def render_result(data: Dict[str, Any], title: str) -> str:
    """Render output, tables, standardized export bar and raw JSON."""
    markdown = render_standard_export_bar(data, title)
    tab_output, tab_tables, tab_json = st.tabs(["📄 Output", "📊 Structured tables", "{} JSON"])

    with tab_output:
        st.markdown(markdown)

    tables = extract_named_tables(data)
    with tab_tables:
        if not tables:
            st.info("No structured tables found in this output.")
        for name, rows in tables.items():
            st.subheader(name.replace("_", " ").title())
            st.dataframe(rows_to_df(rows), width="stretch", hide_index=True)

    with tab_json:
        st.json(data)
    return markdown
