"""Document versioning and impact UI."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from services.document_version_service import document_version_record, hero_document_version_diff
from services.usage_metrics_service import record_data_event


def render_document_versions_page(settings):
    st.subheader("📄 Document Versions & Impact")
    st.caption("Shows how imported source changes create document hashes, obligation diffs and downstream review impact.")
    diff = hero_document_version_diff()
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Previous document**")
        st.json(diff["previous_document"])
    with c2:
        st.markdown("**Current document**")
        st.json(diff["current_document"])
    st.markdown("### Obligation diff")
    d = diff["diff"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Added", d["added_count"])
    c2.metric("Changed", d["changed_count"])
    c3.metric("Removed", d["removed_count"])
    for label in ["added", "changed", "removed"]:
        rows = d.get(label, [])
        with st.expander(label.title(), expanded=bool(rows)):
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
    st.markdown("### Downstream impact")
    impact_rows = []
    for item in diff["impacted_downstream"]:
        impact_rows.append({"obligation_id": item["obligation_id"], "affected_count": len(item.get("impact", [])), "affected_ids": ", ".join(row.get("artifact_id", "") for row in item.get("impact", []))})
    st.dataframe(pd.DataFrame(impact_rows), width="stretch", hide_index=True)

    text = st.text_area("Try an import/version hash", value="Example SAF-T source text with invoice validation and accounting traceability obligations.", height=110)
    if st.button("Create local document version event"):
        rec = document_version_record(document_id="DOC-USER-IMPORT", version="draft", text=text, imported_by=settings.get("demo_user", "demo-user"))
        record_data_event(event_type="document_import", actor=settings.get("demo_user", "demo-user"), role=settings.get("role", "Product Manager"), workflow="Document Versions", object_type="document_version", obj=rec, metadata={"hash": rec["hash"]})
        st.success(f"Version hash created: {rec['hash'][:24]}…")
