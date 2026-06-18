"""About page for Marco Figueiredo."""
from __future__ import annotations

import streamlit as st

from ui.visual_components import render_card, render_metric_pill


def render_about_me() -> None:
    """Render a professional About Me page for the portfolio."""
    st.markdown(
        """
<div class="hero">
  <span class="badge">AI Product Manager</span>
  <span class="badge">Enterprise software</span>
  <span class="badge">Compliance-heavy workflows</span>
  <h1>About Marco Figueiredo</h1>
  <p>I turn complex documents, regulatory ambiguity and critical enterprise workflows into clear, auditable and scalable AI-assisted product systems.</p>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown("## Product thesis")
    st.write(
        "I work at the intersection of applied AI, compliance, governance, risk and enterprise product execution. "
        "My strongest edge is converting regulatory complexity, technical ambiguity and multi-stakeholder workflows into products that reduce risk, accelerate teams and build organizational trust."
    )

    st.markdown("## What I recently built")
    st.write(
        "I built the AI Product Intelligence Suite, a modular portfolio platform designed to compress the discovery → compliance → release → incident investigation cycle for compliance-heavy enterprise software teams."
    )

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_metric_pill("Discovery", "-80%", "good")
    with c2:
        render_metric_pill("Compliance analysis", "-90%", "good")
    with c3:
        render_metric_pill("Release readiness", "-85%", "good")
    with c4:
        render_metric_pill("Incident reconstruction", "-90%", "good")
    st.caption("Impact numbers are portfolio hypotheses based on synthetic workflows, not independently validated production metrics.")

    st.markdown("## The four product workflows")
    a, b = st.columns(2)
    with a:
        render_card(
            "Interpret — Compliance-to-Product Studio",
            [
                "RAG, traceability matrix and citation support checking",
                "Turns regulatory documents into obligations, requirements, validation rules and QA scenarios",
                "Designed for source-grounded, human-reviewed compliance workflows",
            ],
            "🔍",
        )
        render_card(
            "Discover — Product Discovery Studio",
            [
                "Assumptions, validation plans, trade-offs and RICE prioritization",
                "Jira-ready tickets, Gherkin acceptance criteria and QA matrices",
                "Designed to turn ambiguity into implementation-ready scope",
            ],
            "🧠",
        )
    with b:
        render_card(
            "Communicate — Release Readiness Copilot",
            [
                "Audience-specific release communication",
                "Claim safety review, risk scoring and safer rewrites",
                "Designed for Support, Customer Success, Product Marketing and Engineering handoff",
            ],
            "📣",
        )
        render_card(
            "Investigate — Decision Timeline Builder",
            [
                "Incident timelines, actor maps and contradiction detection",
                "Executive one-page briefs and postmortem summaries",
                "Designed for Product Ops, escalations and decision audit trails",
            ],
            "🕵️",
        )

    st.markdown("## How I think about product")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            """
**Analytical rigor**  
Compliance, risk, grounding, validation and auditability.

**Structure**  
Traceability, workflows, schemas, evaluation and governance.

**Speed**  
AI-assisted automation, reusable pipelines and end-to-end product operations.
"""
        )
    with c2:
        st.markdown(
            """
**Clarity**  
Communication by audience, documentation quality and engineering handoff.

**Responsible AI**  
Human review flags, rule-verified support scores, source coverage and limitations.

**Enterprise readiness**  
Outputs that survive audits, incidents, releases and stakeholder review.
"""
        )

    st.markdown("## Superpower")
    st.success(
        "I transform regulatory complexity into clear, scalable and auditable product systems — reducing risk, accelerating teams and creating trust."
    )

    st.markdown("## What I am looking for")
    st.write(
        "I am interested in teams that take AI seriously in enterprise environments: fintech, govtech, healthtech, regulated platforms and companies where auditability, governance, reliability and product quality are not optional."
    )

    st.markdown("## Contact")
    st.markdown(
        """
<div class="cta-box">
  <b>Want to discuss AI product workflows for regulated enterprise environments?</b><br/>
  Email: <a href="mailto:marco.figueiredo@outlook.com">marco.figueiredo@outlook.com</a>
</div>
""",
        unsafe_allow_html=True,
    )
