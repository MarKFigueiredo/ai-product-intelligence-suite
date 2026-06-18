"""Portfolio landing and hero case study pages."""
from __future__ import annotations

import streamlit as st

from config import APP_NAME
from ui.visual_components import render_card, render_compact_card_grid, render_kpi_grid, render_score_bar, render_callout


def render_landing_page() -> None:
    """Render a public-facing portfolio landing page inside Streamlit."""
    st.markdown(
        f"""
<div class="hero">
  <h1>{APP_NAME}</h1>
  <p>Portfolio case study: turning ambiguous compliance inputs into auditable, testable and measurable product decisions.</p>
  <span class="badge">Portfolio, not commercial product</span>
  <span class="badge">SAF-T/e-invoicing hero case</span>
  <span class="badge">Human review gates</span>
  <span class="badge">Real local usage metrics</span>
</div>
""",
        unsafe_allow_html=True,
    )

    render_callout(
        "This is designed to demonstrate product judgment, AI workflow design, QA discipline, enterprise readiness awareness and communication clarity. It does not claim production SaaS readiness or guaranteed hiring outcomes.",
        "info",
        "Positioning",
    )

    st.markdown("### Fast review summary")
    render_kpi_grid([
        {"label": "Core thesis", "value": "AI + compliance", "note": "Ambiguity → decisions"},
        {"label": "Hero case", "value": "SAF-T PT", "note": "One deep workflow"},
        {"label": "Quality gate", "value": "Negative QA", "note": "Blocks happy-path only"},
        {"label": "Evidence", "value": "Local metrics", "note": "Runs, exports, hashes"},
    ])

    st.markdown("### Product map")
    render_compact_card_grid([
        {"title": "Interpret", "icon": "🔍", "badge": "source-grounded", "body": "Extract obligations from source text, preserve evidence, and route weak/missing items to human review."},
        {"title": "Discover", "icon": "🧠", "badge": "productization", "body": "Convert reviewed obligations into requirements, Jira-shaped tickets, QA cases and rule-based completeness checks."},
        {"title": "Communicate", "icon": "📣", "badge": "risk-aware", "body": "Convert risky release claims into safer customer-facing language with scope and approval boundaries."},
        {"title": "Investigate", "icon": "🕵️", "badge": "learning loop", "body": "Show what would happen if a gap is missed: incident timeline, owners, severity and prevention actions."},
    ], columns=4)

    st.markdown("### Hero case study — SAF-T PT + e-invoicing")
    col_a, col_b = st.columns([1.1, 1])
    with col_a:
        st.markdown(
            """
**Context:** A synthetic enterprise software team needs to translate compliance guidance into product, QA and release artefacts.

**The workflow demonstrates:**
- obligations extracted from source text;
- reviewer corrections and downstream impact;
- requirement rewrite from vague to testable;
- Jira-style handoff and QA coverage;
- mandatory negative tests;
- risky release note vs safer rewrite;
- audit-ready final report.
"""
        )
    with col_b:
        st.markdown("#### Readiness signals")
        render_score_bar("Evidence support", 82, "Portfolio sample / rule-based checks")
        render_score_bar("Negative QA coverage", 100, "Mapped demo obligations")
        render_score_bar("Production SaaS readiness", 48, "Explicitly not claimed")
        st.info("Scores are portfolio/demo signals unless marked as real local usage metrics. Human review remains required.")

    st.markdown("### Who should review what")
    c1, c2 = st.columns(2)
    with c1:
        render_card("Hiring Manager", ["Guided Demo", "Product Strategy", "What this demonstrates", "Claim Hygiene Audit"], "👤")
        render_card("QA / Compliance", ["Negative Coverage Policy", "Evidence Drawer", "Approval Workflow", "Version Impact"], "✅")
    with c2:
        render_card("Engineering Lead", ["Real vs simulated", "Connector Handoff Center", "Usage Metrics", "Architecture docs"], "🛠️")
        render_card("Recruiter", ["Portfolio Review Guide", "90-second walkthrough", "About Me", "Hero case summary"], "🚀")

    st.markdown("### About the builder")
    st.write(
        "Built by Marco Figueiredo as a portfolio case study for AI Product Management in compliance-heavy enterprise software. "
        "The project demonstrates how AI outputs can be framed as reviewed, traceable product decisions rather than unsupported automation."
    )

    st.markdown("### Contact")
    st.markdown(
        """
<div class="cta-box">
  <b>Want to review the case study?</b><br/>
  Email: <a href="mailto:marco.figueiredo@outlook.com">marco.figueiredo@outlook.com</a>
</div>
""",
        unsafe_allow_html=True,
    )


def render_portfolio_landing() -> None:
    render_landing_page()
