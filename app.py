"""Main Streamlit entry point for the AI Product Intelligence Suite.

Version display is sourced from config.APP_NAME to avoid stale hard-coded labels.
"""
from __future__ import annotations

import streamlit as st

from config import APP_NAME, APP_TAGLINE, CSS
from modules import compliance_studio, decision_timeline, product_discovery, release_readiness
from ui.about_page import render_about_me
from ui.enterprise_page import render_enterprise_readiness_page
from ui.guided_demo_page import render_guided_demo_page
from ui.connector_handoff_page import render_connector_handoff_page
from ui.evidence_report_page import render_evidence_report_page
from ui.approval_workflow_page import render_approval_workflow_page
from ui.document_versions_page import render_document_versions_page
from ui.quality_learning_page import render_quality_learning_page
from ui.claim_hygiene_page import render_claim_hygiene_page
from ui.lineage_page import render_lineage_page
from ui.metrics_page import render_usage_metrics_page
from ui.portfolio_page import render_landing_page, render_portfolio_landing
from ui.limitations_page import render_limitations_page
from ui.sidebar import render_sidebar
from ui.streamlit_secrets import sync_streamlit_secrets_to_env
sync_streamlit_secrets_to_env()


def main() -> None:
    st.set_page_config(page_title=APP_NAME, page_icon="🧭", layout="wide")
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="hero">
            <h1>🧭 {APP_NAME}</h1>
            <p>{APP_TAGLINE}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    settings = render_sidebar()

    if settings["workflow"] == "guided_demo":
        render_guided_demo_page(settings)
    elif settings["workflow"] == "landing_page":
        render_landing_page()
    elif settings["workflow"] == "about_me":
        render_about_me()
    elif settings["workflow"] == "product_discovery":
        product_discovery.render(settings)
    elif settings["workflow"] == "compliance_studio":
        compliance_studio.render(settings)
    elif settings["workflow"] == "release_readiness":
        release_readiness.render(settings)
    elif settings["workflow"] == "decision_timeline":
        decision_timeline.render(settings)
    elif settings["workflow"] == "limitations":
        render_limitations_page()
    elif settings["workflow"] == "enterprise_readiness":
        render_enterprise_readiness_page(settings)
    elif settings["workflow"] == "usage_metrics":
        render_usage_metrics_page(settings)
    elif settings["workflow"] == "lineage":
        render_lineage_page(settings)
    elif settings["workflow"] == "connector_handoff":
        render_connector_handoff_page(settings)
    elif settings["workflow"] == "evidence_report":
        render_evidence_report_page(settings)
    elif settings["workflow"] == "approval_workflow":
        render_approval_workflow_page(settings)
    elif settings["workflow"] == "document_versions":
        render_document_versions_page(settings)
    elif settings["workflow"] == "quality_learning":
        render_quality_learning_page(settings)
    elif settings["workflow"] == "claim_hygiene":
        render_claim_hygiene_page(settings)
    else:
        render_portfolio_landing()


if __name__ == "__main__":
    main()
