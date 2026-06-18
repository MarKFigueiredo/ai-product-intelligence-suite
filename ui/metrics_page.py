"""Usage metrics and data portability page."""
from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from services.usage_metrics_service import (
    export_usage_json_bytes,
    export_usage_zip_bytes,
    flatten_run_for_csv,
    import_usage_payload,
    list_data_events,
    list_metric_snapshots,
    list_workflow_runs,
    rows_to_csv_bytes,
    usage_summary,
)
from ui.visual_components import render_metric_pill, render_section_kicker


def _runs_df():
    rows = list_workflow_runs(limit=500)
    return pd.DataFrame([flatten_run_for_csv(r) for r in rows]) if rows else pd.DataFrame()


def render_usage_metrics_page(settings: dict | None = None) -> None:
    settings = settings or {}
    actor = settings.get("demo_user", "demo-user")
    role = settings.get("role", "Product Manager")

    st.header("Usage Metrics & Data")
    st.caption(
        "v19 stores metrics created by real app usage in local SQLite: workflow runs, derived quality metrics, mandatory negative test coverage, imports, exports and connector events. "
        "Synthetic benchmark numbers remain separate and labelled as synthetic."
    )

    summary = usage_summary()
    cols = st.columns(4)
    with cols[0]:
        render_metric_pill("Saved runs", str(summary.get("runs_total", 0)), "good" if summary.get("runs_total") else "mid")
    with cols[1]:
        render_metric_pill("Data events", str(summary.get("data_events_total", 0)), "good" if summary.get("data_events_total") else "mid")
    with cols[2]:
        render_metric_pill("Workflows used", str(summary.get("workflows_total", 0)), "good" if summary.get("workflows_total") else "mid")
    with cols[3]:
        render_metric_pill("Avg latency", f"{summary.get('avg_latency_ms', 0)} ms", "neutral")

    if summary.get("by_workflow"):
        render_section_kicker("Workflow-level summary")
        st.dataframe(pd.DataFrame(summary["by_workflow"]), width="stretch", hide_index=True)

    tabs = st.tabs(["Runs", "Metric snapshots", "Data events", "Import / Export"])

    with tabs[0]:
        st.subheader("Persisted workflow runs")
        df = _runs_df()
        if df.empty:
            st.info("No usage runs recorded yet. Generate a package in Interpret, Discover, Communicate or Investigate to populate this table.")
        else:
            st.dataframe(df, width="stretch", hide_index=True)
            st.download_button("Download runs CSV", rows_to_csv_bytes(df.to_dict("records")), "real_usage_runs.csv", "text/csv", width="stretch")

    with tabs[1]:
        st.subheader("Metric snapshots")
        rows = list_metric_snapshots(limit=1000)
        if rows:
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
            st.download_button("Download metric snapshots CSV", rows_to_csv_bytes(rows), "real_metric_snapshots.csv", "text/csv", width="stretch")
        else:
            st.info("No metric snapshots yet.")

    with tabs[2]:
        st.subheader("Imports, exports and connector events")
        events = list_data_events(limit=500)
        if events:
            flat_events = []
            for event in events:
                row = {k: v for k, v in event.items() if k != "metadata"}
                row.update({f"metadata_{k}": v for k, v in (event.get("metadata") or {}).items() if isinstance(v, (str, int, float, bool)) or v is None})
                flat_events.append(row)
            st.dataframe(pd.DataFrame(flat_events), width="stretch", hide_index=True)
            st.download_button("Download data events CSV", rows_to_csv_bytes(flat_events), "real_data_events.csv", "text/csv", width="stretch")
        else:
            st.info("No data events yet. Saving exports/imports/connectors will populate this table.")

    with tabs[3]:
        st.subheader("Export complete local usage dataset")
        st.download_button("Download usage JSON", export_usage_json_bytes(), "ai_pm_real_usage_metrics.json", "application/json", width="stretch")
        st.download_button("Download usage ZIP package", export_usage_zip_bytes(), "ai_pm_real_usage_metrics_package.zip", "application/zip", width="stretch")

        st.subheader("Import usage dataset")
        uploaded = st.file_uploader("Import usage JSON exported from this app", type=["json"])
        if uploaded is not None:
            try:
                payload = json.loads(uploaded.read().decode("utf-8"))
                result = import_usage_payload(payload, actor=actor, role=role)
                st.success(f"Imported {result['imported_runs']} runs from schema {result['schema_version']}.")
            except Exception as error:
                st.error(f"Could not import usage metrics: {error}")

        st.info(
            "This page is intentionally about real usage telemetry. It will be empty in a fresh clone until someone actually runs workflows, saves exports, imports a dataset or creates connector outbox files."
        )
