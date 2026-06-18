"""Lineage and staleness page."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import streamlit as st

from services.lineage_service import detect_stale_artifacts, hero_lineage_state, impact_analysis, timeline_events


def render_lineage_page(settings: Dict[str, Any]) -> None:
    st.header("🧬 Lineage & Staleness")
    st.markdown("Show how source or reviewer changes propagate through obligation → requirement → Jira → QA → release → audit.")
    state = hero_lineage_state()
    st.subheader("Artefacts")
    st.dataframe(pd.DataFrame(state["artifacts"]), width="stretch", hide_index=True)
    st.subheader("Links")
    st.dataframe(pd.DataFrame(state["links"]), width="stretch", hide_index=True)
    stale = detect_stale_artifacts(state["artifacts"], state["links"])
    st.subheader("Stale artefacts")
    if stale:
        st.dataframe(pd.DataFrame(stale), width="stretch", hide_index=True)
    else:
        st.success("No stale artefacts detected.")
    changed = st.selectbox("Changed artefact", [row["artifact_id"] for row in state["artifacts"]], index=2)
    impact = impact_analysis(changed, state)
    st.subheader("Impact analysis")
    st.write(f"Changing `{changed}` affects {impact['affected_count']} downstream artefact(s).")
    st.dataframe(pd.DataFrame(impact["affected_artifacts"]), width="stretch", hide_index=True)
    st.subheader("Timeline")
    st.dataframe(pd.DataFrame(timeline_events(state)), width="stretch", hide_index=True)
