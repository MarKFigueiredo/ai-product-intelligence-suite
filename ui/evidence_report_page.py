"""Real usage evidence report UI."""
from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from services.evidence_report_service import generate_real_usage_evidence_markdown, save_real_usage_evidence_report
from services.usage_metrics_service import export_usage_json_bytes, export_usage_zip_bytes, usage_summary


def render_evidence_report_page(settings: Dict[str, Any]) -> None:
    st.header("📈 Real Usage Evidence Report")
    st.markdown("Generate a hiring-friendly evidence report from the local SQLite usage metrics store.")
    summary = usage_summary()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Runs", summary.get("runs_total", 0))
    c2.metric("Data events", summary.get("data_events_total", 0))
    c3.metric("Workflows", summary.get("workflows_total", 0))
    c4.metric("Avg latency", f"{summary.get('avg_latency_ms', 0)} ms")
    report = generate_real_usage_evidence_markdown()
    st.download_button("Download report markdown", report, "REAL_USAGE_EVIDENCE_REPORT.md", mime="text/markdown")
    st.download_button("Download usage JSON", export_usage_json_bytes(), "usage_metrics_export.json", mime="application/json")
    st.download_button("Download usage ZIP", export_usage_zip_bytes(), "usage_metrics_export.zip", mime="application/zip")
    if st.button("Save report locally"):
        path = save_real_usage_evidence_report()
        st.success(f"Saved: {path}")
    with st.expander("Preview report", expanded=True):
        st.markdown(report)
