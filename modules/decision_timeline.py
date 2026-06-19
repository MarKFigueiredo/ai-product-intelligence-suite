"""Investigate — Decision Timeline Builder."""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from prompts.timeline_prompt import build_timeline_prompt
from services.evaluation_service import evaluate_output
from services.usage_metrics_service import elapsed_ms, now_ms, record_output_run, save_export_package_locally
from services.openai_service import call_model_json
from ui.openai_error_handler import render_openai_error
from ui.evaluation_panel import render_evaluation
from ui.result_panel import render_result
from ui.visual_components import render_card, render_demo_banner, render_metric_pill, render_score_bar, render_table_preview

EXPECTED = [
    "executive_one_page_brief", "customer_escalation_context", "chronological_timeline", "actor_map",
    "decision_audit_trail", "contradictions_or_inconsistencies", "risk_register", "postmortem_summary",
]

SAMPLE_NOTES = """
2026-01-10 09:00 | CUST-8841 | Customer escalated: SAF-T export completed despite missing CustomerTaxID on 37 invoices. Month-end filing due in 48 hours.
2026-01-10 10:30 | Support | Support reproduced export success with missing CustomerTaxID and flagged compliance-sensitive customer impact.
2026-01-10 12:10 | Product | Product initially marked validation feature as 'release ready' based on happy-path QA.
2026-01-11 09:45 | QA | QA confirmed negative test coverage did not include foreign customer tax ID exceptions.
2026-01-11 13:20 | Engineering | Engineering found validation ran after export file generation rather than before file creation.
2026-01-12 16:30 | Release Manager | Deployment paused pending blocking validation, support macro and compliance-safe release wording.
2026-01-13 11:00 | Compliance Reviewer | Confirmed support must not promise guaranteed SAF-T compliance; use bounded wording.
"""

SLACK_SAMPLE = """[2026-01-10 10:42] support-lead: Customer CUST-8841 says SAF-T export allowed missing tax ID. Filing deadline is Friday.
[2026-01-10 12:14] product-manager: We thought validation was release ready. Need to compare QA criteria with Interpret obligations.
[2026-01-11 09:45] qa-lead: Confirmed missing negative test for foreign customer tax IDs.
[2026-01-12 16:30] release-manager: Pausing rollout until we have blocking validation and approved customer wording.
"""

JIRA_SAMPLE = """JIRA-412 | Bug | SAF-T export missing CustomerTaxID validation | Status: Open | Owner: Engineering | Severity: High
JIRA-419 | Story | Add validation report before export | Status: In Progress | Owner: Product | Severity: Medium
JIRA-426 | Task | Approve compliance-safe release wording | Status: Open | Owner: Legal/Compliance | Severity: High
"""

GIT_SAMPLE = """commit a1b2c3d 2026-01-11 Move validation before export file generation
commit e4f5g6h 2026-01-12 Add foreign customer edge case tests
commit f7a8b9c 2026-01-13 Add support escalation macro copy
"""


def demo_output() -> Dict[str, Any]:
    return {
        "executive_one_page_brief": {
            "what_happened": "A customer escalation revealed that SAF-T export validation ran too late and missed missing CustomerTaxID cases.",
            "why_it_matters": "Invalid records could be exported near a customer filing deadline, creating support and compliance-sensitive risk.",
            "current_risk": "High until blocking validation, negative tests and approved customer wording are complete.",
            "decision_needed": "Release hotfix now with known scope, or delay until full validation report and wording approvals are complete.",
            "recommended_next_action": "Ship blocking validation after QA evidence and Legal/Compliance-approved support wording are attached to the incident record.",
        },
        "customer_escalation_context": {
            "customer": "CUST-8841",
            "escalation_id": "ESC-SAF-T-2026-001",
            "business_impact": "37 invoices potentially exported with missing tax identifiers; filing deadline within 48 hours.",
            "compliance_boundary": "Support can explain product behaviour and workaround; compliance/legal interpretation remains with the customer and reviewer.",
            "current_owner": "Support Lead + Product Manager",
        },
        "chronological_timeline": [
            {"date": "2026-01-10", "timestamp": "2026-01-10 09:00", "event": "Customer escalated export issue with missing CustomerTaxID on 37 invoices", "event_type": "Customer impact", "actor": "Customer", "owner": "Support Lead", "source_or_note": "CUST-8841 ticket", "severity": "High", "severity_score": 9},
            {"date": "2026-01-10", "timestamp": "2026-01-10 12:10", "event": "Product marked validation feature release-ready based on incomplete QA scope", "event_type": "Decision", "actor": "Product", "owner": "PM", "source_or_note": "Product note", "severity": "High", "severity_score": 8},
            {"date": "2026-01-11", "timestamp": "2026-01-11 09:45", "event": "QA confirmed missing foreign customer negative test coverage", "event_type": "Risk", "actor": "QA", "owner": "QA Lead", "source_or_note": "QA finding", "severity": "High", "severity_score": 8},
            {"date": "2026-01-12", "timestamp": "2026-01-12 16:30", "event": "Release paused pending validation fix and compliance-safe wording", "event_type": "Decision", "actor": "Release Manager", "owner": "Release Manager", "source_or_note": "Release channel", "severity": "Medium", "severity_score": 6},
        ],
        "actor_map": [
            {"actor": "Support", "role": "Escalation intake", "involvement": "Collected customer impact and workaround needs", "open_question": "Was impact limited to one customer?"},
            {"actor": "Product", "role": "Scope owner", "involvement": "Mapped obligation gap to feature scope", "open_question": "Were Interpret obligations used in PRD completeness checks?"},
            {"actor": "QA", "role": "Validation", "involvement": "Detected missing negative coverage", "open_question": "Which seeded datasets must become regression tests?"},
            {"actor": "Legal/Compliance", "role": "Wording reviewer", "involvement": "Approved compliance boundary and customer-safe wording", "open_question": "What exact statement can support use externally?"},
        ],
        "decision_audit_trail": [
            {"decision": "Pause release until blocking validation and wording review are complete", "date": "2026-01-12", "timestamp": "2026-01-12 16:30", "owner": "Release Manager", "evidence": "Customer impact + QA gap + compliance wording risk", "open_risk": "Customer deadline pressure", "next_action": "Attach QA evidence and approved support macro"},
            {"decision": "Support must not promise guaranteed SAF-T compliance", "date": "2026-01-13", "timestamp": "2026-01-13 11:00", "owner": "Compliance Reviewer", "evidence": "Compliance-safe wording review", "open_risk": "Agents may overstate feature outcome", "next_action": "Publish Zendesk macro"},
        ],
        "contradictions_or_inconsistencies": [
            {"item": "Feature was marked release-ready before negative customer tax ID tests passed", "why_it_matters": "Readiness criteria did not map to regulatory obligations", "severity": "High", "severity_score": 8, "recommended_check": "Require obligation-linked QA evidence before release-ready status"},
            {"item": "Validation existed but ran after file generation", "why_it_matters": "Implementation location contradicted product requirement to validate before export", "severity": "High", "severity_score": 9, "recommended_check": "Add architecture review for validation placement"},
        ],
        "risk_register": [
            {"risk": "Known validation gap reaches production", "severity_score": 9, "likelihood": "Medium", "impact": "High", "mitigation": "Blocking validation before file generation and regression tests", "owner": "Engineering", "due_date": "2026-01-14"},
            {"risk": "Support overpromises compliance outcome", "severity_score": 7, "likelihood": "Medium", "impact": "High", "mitigation": "Approved support macro and escalation boundary", "owner": "Support Lead", "due_date": "2026-01-13"},
        ],
        "missing_information": ["Number of affected tenants", "Whether any exported files were submitted externally", "Full list of field-level validation exceptions"],
        "postmortem_summary": {
            "root_cause_hypothesis": "Incomplete traceability from Interpret obligations to PRD completeness and QA release readiness.",
            "contributing_factors": ["Validation placement was reviewed too late", "Negative tests did not include foreign customer edge cases", "Support wording was not approved before escalation"],
            "what_went_well": ["Support escalated quickly", "QA identified a concrete missing test scenario", "Release manager paused rollout before wider exposure"],
            "what_failed": ["Release-ready status did not require obligation-linked evidence", "Implementation allowed validation after export generation"],
            "prevention_actions": [
                {"action": "Add obligation → requirement → Jira → QA gate to release checklist", "owner": "Product", "due_date": "2026-01-20", "evidence_required": "Checklist with linked Jira/QA IDs"},
                {"action": "Add seeded regression dataset for missing tax ID and foreign customer exceptions", "owner": "QA", "due_date": "2026-01-18", "evidence_required": "Passing automated tests"},
                {"action": "Publish compliance-safe customer escalation macro", "owner": "Support", "due_date": "2026-01-13", "evidence_required": "Macro URL / Confluence page"},
            ],
        },
        "recommended_next_actions": [
            {"action": "Patch validation to run before file generation", "owner": "Engineering", "priority": "High", "due_date": "2026-01-14", "evidence_required": "Code review + passing regression tests"},
            {"action": "Review all customer-facing claims", "owner": "Legal/Compliance", "priority": "High", "due_date": "2026-01-13", "evidence_required": "Approved release copy"},
        ],
    }


def render_actor_map(actors: List[Dict[str, Any]]) -> None:
    st.subheader("Actor map")
    if not actors:
        st.info("No actor map generated yet.")
        return
    chips = "".join(f"<span class='actor-chip'>👤 {a.get('actor','Actor')} · {a.get('role','Role')}</span>" for a in actors)
    st.markdown(chips, unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(actors), width="stretch", hide_index=True)


def _severity_icon(event: Dict[str, Any]) -> str:
    score = int(event.get("severity_score") or 0)
    if score >= 8:
        return "🔴"
    if score >= 5:
        return "🟠"
    return "🟢"


def render_timeline_visual(events: List[Dict[str, Any]]) -> None:
    st.subheader("Temporal incident dashboard")
    if not events:
        st.info("No timeline generated yet.")
        return
    for event in events:
        icon = _severity_icon(event)
        st.markdown(
            f"""
            <div class="timeline-event">
              <b>{icon} {event.get('timestamp') or event.get('date','')}</b> — {event.get('event','Event')}<br/>
              <span class="small-muted">Owner: {event.get('owner','N/A')} · Actor: {event.get('actor','N/A')} · Type: {event.get('event_type','N/A')} · Severity: {event.get('severity','N/A')} / {event.get('severity_score','?')}/10 · Source: {event.get('source_or_note','N/A')}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    df = pd.DataFrame(events)
    if not df.empty and "severity_score" in df.columns:
        st.write("Severity score by event")
        chart_df = df[["timestamp", "severity_score"]].set_index("timestamp")
        st.bar_chart(chart_df)


def render_timeline_dashboard(data: Dict[str, Any]) -> None:
    brief = data.get("executive_one_page_brief", {}) if isinstance(data.get("executive_one_page_brief"), dict) else {}
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: render_metric_pill("Events", str(len(data.get("chronological_timeline", []) or [])), "good")
    with c2: render_metric_pill("Actors", str(len(data.get("actor_map", []) or [])), "mid")
    with c3: render_metric_pill("Contradictions", str(len(data.get("contradictions_or_inconsistencies", []) or [])), "bad" if data.get("contradictions_or_inconsistencies") else "good")
    with c4: render_metric_pill("Risks", str(len(data.get("risk_register", []) or [])), "bad" if data.get("risk_register") else "good")
    max_sev = max([int(e.get("severity_score") or 0) for e in data.get("chronological_timeline", []) or []] or [0])
    with c5: render_metric_pill("Max severity", f"{max_sev}/10", "bad" if max_sev >= 8 else "mid" if max_sev >= 5 else "good")

    st.subheader("Executive one-page brief")
    b1, b2 = st.columns(2)
    with b1:
        render_card("What happened", brief.get("what_happened", ""), "📌")
        render_card("Why it matters", brief.get("why_it_matters", ""), "💡")
    with b2:
        render_card("Decision needed", brief.get("decision_needed", ""), "🧭")
        render_card("Recommended next action", brief.get("recommended_next_action", ""), "✅")

    escalation = data.get("customer_escalation_context", {}) if isinstance(data.get("customer_escalation_context"), dict) else {}
    if escalation:
        st.subheader("Customer escalation / compliance boundary")
        render_card("Escalation context", escalation, "🚨", escalation.get("escalation_id", "Escalation"))

    left, right = st.columns([1.6, 1])
    with left:
        render_timeline_visual(data.get("chronological_timeline", []) or [])
    with right:
        render_actor_map(data.get("actor_map", []) or [])
        st.subheader("Contradiction detector")
        rows = data.get("contradictions_or_inconsistencies", []) or []
        if rows:
            for row in rows:
                st.markdown(f"<div class='alert-card'><b>{row.get('severity','Risk')} / {row.get('severity_score','?')}/10</b>: {row.get('item','')}</div>", unsafe_allow_html=True)
        else:
            st.success("No contradictions detected in the generated brief.")

    render_table_preview(data, ["decision_audit_trail", "risk_register", "recommended_next_actions"])
    postmortem = data.get("postmortem_summary", {}) if isinstance(data.get("postmortem_summary"), dict) else {}
    actions = postmortem.get("prevention_actions", []) if isinstance(postmortem, dict) else []
    if actions:
        st.subheader("Actionable postmortem prevention actions")
        st.dataframe(pd.DataFrame(actions), width="stretch", hide_index=True)


def render(settings: Dict[str, Any]) -> None:
    render_demo_banner(settings.get("demo_mode", False))
    st.header("Investigate — Decision Timeline Builder")
    st.caption("Product Ops incident intelligence: temporal dashboard, actor map, contradiction detector, audit trail and postmortem.")

    with st.expander("Incident inputs and simulated source parsers", expanded=True):
        incident_mode = st.selectbox("Incident mode", ["Customer escalation", "Failed release", "Compliance change", "SLA breach", "Product decision log", "Support escalation"], index=0)
        source_type = st.selectbox("Simulated source parser", ["Manual notes", "Slack-style log", "Jira-style tickets", "Git commit log", "Combined sample"], index=4)
        if source_type == "Slack-style log":
            default_notes = SLACK_SAMPLE
        elif source_type == "Jira-style tickets":
            default_notes = JIRA_SAMPLE
        elif source_type == "Git commit log":
            default_notes = GIT_SAMPLE
        elif source_type == "Combined sample":
            default_notes = SAMPLE_NOTES + "\n" + SLACK_SAMPLE + "\n" + JIRA_SAMPLE + "\n" + GIT_SAMPLE
        else:
            default_notes = SAMPLE_NOTES
        raw_notes = st.text_area("Notes / logs / tickets", value=default_notes, height=260)
        business_context = st.text_input("Business context", value="Enterprise compliance product incident")
        stakeholders = st.text_input("Stakeholders", value="Customer, Support, Product, QA, Engineering, Release Manager, Legal/Compliance")
        submitted = st.button("Generate decision intelligence brief", type="primary")

    if not submitted:
        st.info("Use the synthetic customer escalation example or paste sanitized incident notes. The preview now includes stronger incident severity, owners, timestamps and compliance/customer escalation links.")
        render_timeline_dashboard(demo_output())
        return

    inputs = {"raw_notes": raw_notes, "incident_mode": incident_mode, "business_context": business_context, "stakeholders": stakeholders, "language": settings["language"], "detail": settings["detail"]}
    prompt = build_timeline_prompt(inputs)
    try:
        start_ms = now_ms()
        data = call_model_json(prompt, settings["model"], settings["max_output_tokens"], demo_output(), settings["demo_mode"])
        latency = elapsed_ms(start_ms)
        evaluation_for_metrics = evaluate_output(data, __import__("json").dumps(data, ensure_ascii=False), EXPECTED)
        record_output_run(
            workflow="Investigate",
            settings=settings,
            input_payload=inputs,
            output_payload=data,
            evaluation=evaluation_for_metrics,
            latency_ms=latency,
            source_count=1 if inputs else 0,
            metadata={"package_title": "Decision Timeline Brief"},
        )
        tab_dash, tab_full, tab_eval = st.tabs(["🕵️ Incident dashboard", "📦 Full package & exports", "🛡️ Evaluation"])
        with tab_dash:
            render_timeline_dashboard(data)
        with tab_full:
            markdown = render_result(data, "Decision Timeline Brief")
            if st.button("Save structured export locally", key="save_timeline_export", width="stretch"):
                path = save_export_package_locally(
                    workflow="Investigate",
                    title="Decision Timeline Brief",
                    payload=data,
                    actor=settings.get("demo_user", "demo-user"),
                    role=settings.get("role", "Product Manager"),
                )
                st.success(f"Saved local export package: {path}")
        with tab_eval:
            markdown = markdown if "markdown" in locals() else ""
            evaluation = evaluate_output(data, markdown, EXPECTED)
            render_evaluation(evaluation)
    except Exception as error:
        render_openai_error(error)
