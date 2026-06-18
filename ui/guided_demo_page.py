"""Guided portfolio demo UI with compact visual hierarchy and evidence-first review."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import streamlit as st

from services.evidence_report_service import generate_real_usage_evidence_markdown, save_real_usage_evidence_report
from services.lineage_service import detect_stale_artifacts, hero_lineage_state, impact_analysis, timeline_events
from services.portfolio_demo_service import (
    GUIDED_STEPS,
    PERSONA_REVIEW_PATHS,
    REAL_VS_SIMULATED,
    SKILL_EVIDENCE,
    evidence_drawer_items,
    hero_output_shape,
    release_gate_dashboard,
)
from services.run_comparison_service import latest_run_comparison
from services.usage_metrics_service import record_output_run, save_export_package_locally
from ui.visual_components import (
    render_callout,
    render_compact_card_grid,
    render_kpi_grid,
    render_page_intro,
    render_status_badge,
    render_vertical_timeline,
    status_tone,
)


def _gate_table(gate: Dict[str, Any]) -> pd.DataFrame:
    rows = []
    for row in gate["gates"]:
        rows.append({"Gate": row["gate"], "Status": row["status"], "Why it matters": row["reason"]})
    return pd.DataFrame(rows)


def render_guided_demo_page(settings: Dict[str, Any]) -> None:
    output = hero_output_shape()
    gate = release_gate_dashboard(output)

    render_page_intro(
        "Guided Portfolio Demo",
        "A 90-second review path for the SAF-T/e-invoicing hero workflow: source → obligation → review → requirement → QA → safer release communication → audit evidence.",
        ["portfolio case study", "human-reviewed", "audit-aware"],
    )

    render_kpi_grid([
        {"label": "Hero workflow", "value": "8 steps", "note": "Focused path, deep evidence on demand"},
        {"label": "Release status", "value": gate["overall_status"], "note": gate["overall_reason"][:54]},
        {"label": "Negative QA", "value": f"{gate['negative_gate']['negative_test_coverage_rate']}%", "note": "Mandatory coverage gate"},
        {"label": "Review mode", "value": "Human-in-loop", "note": "Corrections affect downstream artefacts"},
    ])

    tabs = st.tabs([
        "Overview",
        "Hero workflow",
        "Release gates",
        "Evidence",
        "Timeline & staleness",
        "Run comparison",
        "Hiring signal",
        "Real vs simulated",
    ])

    with tabs[0]:
        st.markdown("### Choose the reviewer lens")
        persona = st.selectbox("Persona", list(PERSONA_REVIEW_PATHS.keys()), index=1)
        row = PERSONA_REVIEW_PATHS[persona]
        render_compact_card_grid([
            {"title": "Review goal", "icon": "🎯", "badge": persona, "body": row["goal"]},
            {"title": "Start here", "icon": "▶", "body": row["start_here"]},
            {"title": "Look for", "icon": "✓", "body": row["look_for"]},
        ], columns=3)
        render_callout(
            "The current UX intentionally reduces density: first show the decision, then let reviewers open evidence, lineage and tables only when needed.",
            "info",
            "Design principle",
        )

    with tabs[1]:
        st.markdown("### Hero workflow")
        step_labels = [f"Step {step['step']}/8 — {step['title']}" for step in GUIDED_STEPS]
        selected_step = st.select_slider("Progress", options=step_labels, value=step_labels[0])
        selected_index = step_labels.index(selected_step)
        st.progress((selected_index + 1) / len(GUIDED_STEPS), text=selected_step)
        current_step = GUIDED_STEPS[selected_index]
        render_compact_card_grid([
            {"title": selected_step, "icon": current_step["step"], "badge": "current", "body": current_step["outcome"]}
        ], columns=1)
        with st.expander("Show all 8 steps", expanded=False):
            step_cards = [
                {"title": f"Step {step['step']}/8 — {step['title']}", "icon": step["step"], "body": step["outcome"]}
                for step in GUIDED_STEPS
            ]
            render_compact_card_grid(step_cards, columns=4)
        st.divider()
        st.markdown("### Before / after requirement")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Before — vague**")
            st.warning("The system should validate SAF-T invoice data before export.")
        with c2:
            st.markdown("**After — scoped and testable**")
            st.success((output.get("product_requirements") or [{}])[0].get("requirement", ""))

    with tabs[2]:
        st.markdown("### Release Gate Dashboard")
        st.markdown(
            f"Overall status: {render_status_badge(gate['overall_status'], status_tone(gate['overall_status']))}",
            unsafe_allow_html=True,
        )
        st.caption(gate["overall_reason"])
        st.dataframe(_gate_table(gate), width="stretch", hide_index=True)
        neg = gate["negative_gate"]
        render_kpi_grid([
            {"label": "Obligations", "value": neg["obligations_total"], "note": "Must be covered"},
            {"label": "Negative tests", "value": neg["negative_tests_total"], "note": "Failure/edge paths"},
            {"label": "Negative coverage", "value": f"{neg['negative_test_coverage_rate']}%", "note": "Per obligation"},
            {"label": "Gate", "value": neg["release_gate_status"], "note": "Blocks happy-path only releases"},
        ])
        with st.expander("Show obligation-level negative coverage", expanded=False):
            st.dataframe(pd.DataFrame(neg["rows"]), width="stretch", hide_index=True)

    with tabs[3]:
        st.markdown("### Evidence drawer")
        st.caption("Evidence appears on demand so the main review path stays readable.")
        for item in evidence_drawer_items(output):
            title = f"{item['artifact_type']} · {item['artifact_id']}"
            tone = status_tone(item["support_status"])
            with st.expander(f"{title} — {item['support_status']}"):
                c1, c2 = st.columns([1.4, 1])
                with c1:
                    st.markdown(render_status_badge(item["support_status"], tone), unsafe_allow_html=True)
                    st.markdown("**Source / claim excerpt**")
                    st.write(item.get("source_excerpt"))
                    if item.get("safer_rewrite"):
                        st.markdown("**Safer rewrite**")
                        st.success(item["safer_rewrite"])
                with c2:
                    st.markdown(f"**Source hash:** `{item.get('source_hash', '')[:20]}…`")
                    st.markdown(f"**Reviewer decision:** {item.get('reviewer_decision')}")
                    st.markdown(f"**Linked requirement:** {item.get('linked_requirement')}")
                    st.markdown(f"**Linked QA:** {item.get('linked_qa')}")
                    st.markdown(f"**Last modified:** `{item.get('last_modified')}`")

    with tabs[4]:
        st.markdown("### Timeline & staleness")
        state = hero_lineage_state()
        events = timeline_events(state)
        stale = detect_stale_artifacts(state["artifacts"], state["links"])
        c1, c2 = st.columns([1.05, .95])
        with c1:
            render_vertical_timeline(events, "Visual timeline")
        with c2:
            st.markdown("### Stale artefacts")
            if stale:
                st.dataframe(pd.DataFrame(stale), width="stretch", hide_index=True)
            else:
                st.success("No stale artefacts detected.")
            changed = st.selectbox("Simulate changed upstream artefact", [a["artifact_id"] for a in state["artifacts"]], index=2)
            impact = impact_analysis(changed, state)
            render_callout(f"{changed} affects {impact['affected_count']} downstream artefact(s).", "warning", "Impact analysis")
            st.dataframe(pd.DataFrame(impact["affected_artifacts"]), width="stretch", hide_index=True)

    with tabs[5]:
        st.markdown("### Run comparison")
        comparison = latest_run_comparison()
        if not comparison["available"]:
            st.info(comparison["reason"])
            st.caption("Use the app workflows or the seed script to create local usage runs, then return here.")
        else:
            st.markdown(f"Comparing `{comparison['run_a']['run_id']}` → `{comparison['run_b']['run_id']}`")
            st.dataframe(pd.DataFrame(comparison["comparison"]), width="stretch", hide_index=True)
        if st.button("Record this guided demo as a real local usage run"):
            record = record_output_run(
                workflow="Guided Portfolio Demo",
                settings=settings,
                input_payload={"hero_case_hash": output.get("input_document_hash")},
                output_payload=output,
                latency_ms=0,
                source_count=1,
                metadata={"ui_event": "guided_demo_recorded", "release_gate_status": gate["overall_status"]},
            )
            st.success(f"Recorded run: {record['run_id']}")

    with tabs[6]:
        st.markdown("### What this proves")
        st.dataframe(pd.DataFrame(SKILL_EVIDENCE), width="stretch", hide_index=True)
        if st.button("Export hero demo package locally"):
            path = save_export_package_locally(
                workflow="Guided Portfolio Demo",
                title="hero_demo_portfolio_package",
                payload={"hero_output": output, "release_gate": gate, "skill_evidence": SKILL_EVIDENCE},
                actor=settings.get("demo_user", "demo-user"),
                role=settings.get("role", "Product Manager"),
            )
            st.success(f"Saved local export package: {path}")
        report = generate_real_usage_evidence_markdown()
        st.download_button("Download current real usage evidence report", report, "REAL_USAGE_EVIDENCE_REPORT.md", mime="text/markdown")
        if st.button("Save REAL_USAGE_EVIDENCE_REPORT.md locally"):
            path = save_real_usage_evidence_report()
            st.success(f"Saved: {path}")

    with tabs[7]:
        st.markdown("### What is real vs simulated")
        st.dataframe(pd.DataFrame(REAL_VS_SIMULATED), width="stretch", hide_index=True)
        render_callout(
            "This table is intentionally visible. It prevents overclaiming and makes the prototype easier for Engineering, Security and Compliance reviewers to trust.",
            "good",
            "Claim hygiene",
        )
