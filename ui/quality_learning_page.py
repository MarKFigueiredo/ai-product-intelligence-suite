"""Quality learning UI."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from services.quality_learning_service import workflow_learning_summary
from services.usage_metrics_service import export_usage_zip_bytes


def render_quality_learning_page(settings):
    st.subheader("📈 Quality Learning Loop")
    st.caption("Turns persisted usage metrics into product learning: trends, blockers, handoffs and workflow mix.")
    summary = workflow_learning_summary()
    c1, c2, c3 = st.columns(3)
    c1.metric("Workflow runs", summary["runs_total"])
    c2.metric("Release block events", summary["release_block_events"])
    c3.metric("Export/handoff signals", summary["export_or_handoff_events"])

    st.markdown("### Workflow mix")
    st.dataframe(pd.DataFrame(summary["workflow_mix"]), width="stretch", hide_index=True)
    st.markdown("### Quality metric trends")
    trends = summary["metric_trends"]
    if trends:
        st.dataframe(pd.DataFrame(trends), width="stretch", hide_index=True)
    else:
        st.info("No quality trends yet. Run workflows or use the seed script to populate local usage metrics.")
    zip_bytes = export_usage_zip_bytes()
    st.download_button("Download current usage evidence ZIP", zip_bytes, "usage_evidence_dataset.zip", mime="application/zip")
