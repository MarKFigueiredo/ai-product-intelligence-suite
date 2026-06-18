"""UI for claim hygiene / skeptical reviewer audit."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd
import streamlit as st

from services.claim_hygiene_service import audit_portfolio_claims, safe_positioning_statement
from ui.visual_components import render_callout, render_kpi_grid, render_page_intro, render_status_badge, status_tone


def render_claim_hygiene_page(settings: Dict[str, Any]) -> None:
    render_page_intro(
        "Claim Hygiene Audit",
        "A skeptical-reviewer pass that highlights model, metric, production-readiness and hiring-outcome claims that need careful framing.",
        ["skeptical reviewer", "anti-overclaim", "scope discipline"],
    )
    audit = audit_portfolio_claims(Path.cwd())
    render_kpi_grid([
        {"label": "Files scanned", "value": audit["files_scanned"], "note": "Markdown, Python and JSON"},
        {"label": "Needs review", "value": audit["needs_review_total"], "note": "Unframed risky wording"},
        {"label": "High risk", "value": audit["high_risk_total"], "note": "Fix before publishing"},
        {"label": "Summary", "value": audit["summary"], "note": "Conservative scan"},
    ])
    render_callout(safe_positioning_statement(), "info", "Hiring impact wording")

    st.markdown("### Findings")
    findings = pd.DataFrame(audit["findings"])
    if findings.empty:
        st.success("No claim hygiene findings detected.")
        return
    needs = findings[findings["context"] == "Needs review"]
    framed = findings[findings["context"] != "Needs review"]
    if not needs.empty:
        st.warning("These items should be reviewed before publishing because the context may not be clear enough.")
        st.dataframe(needs[["source", "line", "rule_id", "label", "severity", "excerpt", "safer_guidance"]], width="stretch", hide_index=True)
    else:
        st.success("No unframed high/medium claim risks found by the scan.")

    with st.expander("Framed findings / acceptable contexts", expanded=False):
        if framed.empty:
            st.info("No framed findings.")
        else:
            st.dataframe(framed[["source", "line", "rule_id", "label", "context", "excerpt"]], width="stretch", hide_index=True)

    st.markdown("### Review checklist")
    for label in ["Synthetic metrics are labelled synthetic", "Local controls are labelled local", "Live connectors are optional", "No university/company endorsement is claimed", "No interview outcome is guaranteed"]:
        st.markdown(render_status_badge(label, "good"), unsafe_allow_html=True)
