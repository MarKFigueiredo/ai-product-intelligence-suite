"""Communicate — Release Readiness Copilot."""
from __future__ import annotations

from typing import Any, Dict

import pandas as pd
import streamlit as st

from prompts.release_prompt import build_release_prompt
from services.evaluation_service import evaluate_output
from services.usage_metrics_service import elapsed_ms, now_ms, record_output_run, save_export_package_locally
from services.openai_service import call_model_json
from ui.openai_error_handler import render_openai_error
from ui.evaluation_panel import render_evaluation
from ui.result_panel import render_result
from ui.visual_components import render_card, render_demo_banner, render_metric_pill, render_placeholder_panel, render_score_bar, render_table_preview

EXPECTED = [
    "customer_facing_release_note", "internal_support_note", "qa_checklist", "support_faq",
    "claim_safety_review", "sentence_risk_review", "audience_risk_scoring", "approval_workflow",
    "release_approval_checklist", "before_after_copy_examples", "interpret_discover_links",
]


def demo_output() -> Dict[str, Any]:
    return {
        "executive_summary": "This release introduces stronger SAF-T invoice validation and requires careful customer wording to avoid implying guaranteed legal compliance.",
        "customer_facing_release_note": "We added pre-export validation checks that help identify missing customer tax IDs, invalid dates, tax code issues and inconsistent totals before SAF-T export.",
        "internal_support_note": "Support should explain that the feature helps users identify selected data quality issues before export; it does not replace customer compliance review or legal advice.",
        "engineering_summary": "Pre-export validation now checks core invoice fields and returns blocking errors for critical missing or inconsistent data.",
        "customer_success_talking_points": ["Helps detect data quality issues earlier", "Improves confidence before export", "Customers should still review compliance obligations"],
        "interpret_discover_links": [
            {"upstream_item": "Interpret O1 — mandatory invoice fields", "release_asset": "Customer release note + QA checklist", "risk_or_note": "Avoid claiming full compliance guarantee"},
            {"upstream_item": "Discover pipeline R1/Jira/QA", "release_asset": "Support FAQ + before/after behaviour", "risk_or_note": "Explain which validations are in scope"},
        ],
        "before_after_behaviour": [{"before": "Issues surfaced late or after export", "after": "Critical missing fields are shown before export with a failure reason", "customer_impact": "Less rework and clearer error resolution"}],
        "before_after_copy_examples": [
            {"before_claim": "This ensures SAF-T compliance.", "risk": "Overclaims legal outcome", "after_safer_copy": "This helps identify selected SAF-T data issues before export."},
            {"before_claim": "No manual review is needed.", "risk": "Removes required customer accountability", "after_safer_copy": "Use the validation report alongside your normal compliance review."},
        ],
        "support_faq": [{"question": "Does this guarantee SAF-T compliance?", "answer": "No. It helps validate selected fields and should be used with normal compliance review."}],
        "qa_checklist": [{"check": "Missing CustomerTaxID blocks export", "owner": "QA", "status": "Not started", "risk_if_missed": "Invalid record may export"}],
        "known_limitations": ["Does not interpret all country-specific legal exceptions", "Scanned/source documents require human review", "Does not replace legal or compliance sign-off"],
        "audience_risk_scoring": [
            {"audience": "Customer", "risk_score": 72, "risk_reason": "Compliance wording may be overinterpreted", "recommended_tone": "Helpful but cautious"},
            {"audience": "Support", "risk_score": 58, "risk_reason": "Agents need escalation language", "recommended_tone": "Clear and procedural"},
            {"audience": "Legal/Compliance", "risk_score": 45, "risk_reason": "Needs wording approval before external release", "recommended_tone": "Evidence-based and bounded"},
        ],
        "sentence_risk_review": [
            {"sentence_or_claim": "Ensures full SAF-T compliance", "risk": "High", "reason": "Guarantees a legal outcome and exceeds validation scope", "safer_rewrite": "Helps validate selected SAF-T invoice fields before export", "risk_score": 92},
            {"sentence_or_claim": "Blocks invalid records", "risk": "Medium", "reason": "May imply every invalid case is detected", "safer_rewrite": "Blocks records that fail the configured validation checks", "risk_score": 63},
        ],
        "claim_safety_review": [{"risky_claim": "Ensures full compliance", "classification": "Overclaiming", "why_risky": "Guarantees legal outcome", "safer_rewrite": "Helps validate selected invoice fields before export", "risk_score": 88}],
        "what_not_to_say": ["This guarantees compliance", "No review is needed", "All SAF-T exceptions are covered"],
        "approval_workflow": [
            {"team": "Product", "approval_scope": "Feature scope and release narrative", "owner": "PM", "required_before_release": True, "status": "Required"},
            {"team": "QA", "approval_scope": "Validation matrix and regression coverage", "owner": "QA Lead", "required_before_release": True, "status": "Required"},
            {"team": "Support", "approval_scope": "FAQ, escalation path and macro", "owner": "Support Lead", "required_before_release": True, "status": "Required"},
            {"team": "Legal/Compliance", "approval_scope": "Customer-facing compliance claims", "owner": "Compliance Reviewer", "required_before_release": True, "status": "Required"},
        ],
        "release_approval_checklist": [
            {"approval_item": "Compliance wording reviewed", "owner": "Legal/Compliance", "required_before_release": True, "status": "Required"},
            {"approval_item": "Support FAQ reviewed", "owner": "Support", "required_before_release": True, "status": "Required"},
            {"approval_item": "QA seeded cases passed", "owner": "QA", "required_before_release": True, "status": "Required"},
        ],
        "screenshot_placeholders": [{"screenshot": "Before", "purpose": "Show old export flow", "caption": "Before validation errors were surfaced"}, {"screenshot": "After", "purpose": "Show validation report", "caption": "New validation report before export"}],
        "confluence_export_outline": [{"section": "Overview", "content": "Purpose and impact"}, {"section": "Support guidance", "content": "FAQ and escalation path"}, {"section": "Approvals", "content": "Product, QA, Support and Legal/Compliance sign-off"}],
        "zendesk_support_macro": "Thanks for contacting support. The SAF-T validation report helps identify selected data issues before export. Please review the listed records and confirm with your compliance team where needed.",
        "customer_escalation_note": {"when_to_escalate": "Customer asks whether the feature guarantees compliance or disputes a legal interpretation", "customer_safe_wording": "We can help explain what the validation checks do, but your compliance team should confirm filing obligations.", "compliance_boundary": "Support must not provide legal advice."},
        "open_questions": ["Which field errors should be translated into localized customer messages?"],
    }


def safety_score(data: Dict[str, Any]) -> int:
    rows = data.get("claim_safety_review", []) or data.get("sentence_risk_review", []) or []
    if not rows:
        return 82
    avg_risk = sum(int(r.get("risk_score", 65)) for r in rows) / len(rows)
    return max(0, min(100, int(100 - (avg_risk * 0.45))))


def render_claim_risk_table(data: Dict[str, Any]) -> None:
    rows = data.get("sentence_risk_review", []) or data.get("claim_safety_review", []) or []
    st.subheader("Claim → risk → reason → safer rewrite")
    if not rows:
        st.info("No sentence-level risk review generated yet.")
        return
    normalized = []
    for row in rows:
        normalized.append(
            {
                "claim": row.get("sentence_or_claim") or row.get("risky_claim"),
                "risk": row.get("risk") or row.get("classification"),
                "reason": row.get("reason") or row.get("why_risky"),
                "safer_rewrite": row.get("safer_rewrite"),
                "risk_score": row.get("risk_score"),
            }
        )
    st.dataframe(pd.DataFrame(normalized), width="stretch", hide_index=True)


def render_release_dashboard(data: Dict[str, Any]) -> None:
    score = safety_score(data)
    st.subheader("Release communication dashboard")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_score_bar("Claim safety score", score, "Higher = safer language")
    with c2:
        render_score_bar("Approval readiness", 75 if data.get("approval_workflow") or data.get("release_approval_checklist") else 35, "Checklist completion")
    with c3:
        render_score_bar("Support clarity", 82 if data.get("support_faq") else 45, "FAQ and support notes")
    with c4:
        high_risk = len([r for r in data.get("sentence_risk_review", []) or [] if int(r.get("risk_score", 0) or 0) >= 75])
        render_metric_pill("High-risk claims", str(high_risk), "bad" if high_risk else "good")

    tab_customer, tab_internal, tab_risky, tab_before_after, tab_approval, tab_upstream = st.tabs([
        "Customer Messaging", "Internal Notes", "Risky Claims", "Before/After", "Approval Workflow", "Interpret/Discover Links"
    ])
    with tab_customer:
        render_card("Customer-facing note", data.get("customer_facing_release_note", ""), "📣", "Customer")
        render_card("Customer Success talking points", data.get("customer_success_talking_points", []), "🤝", "CS")
        if data.get("support_faq"):
            st.dataframe(pd.DataFrame(data["support_faq"]), width="stretch", hide_index=True)
    with tab_internal:
        render_card("Internal support note", data.get("internal_support_note", ""), "🛟", "Support")
        render_card("Engineering summary", data.get("engineering_summary", ""), "🛠️", "Engineering")
        if data.get("customer_escalation_note"):
            render_card("Customer escalation / compliance boundary", data.get("customer_escalation_note"), "🚨", "Escalation")
        render_table_preview(data, ["qa_checklist"])
    with tab_risky:
        render_claim_risk_table(data)
        if data.get("claim_safety_review"):
            for row in data["claim_safety_review"]:
                st.markdown('<div class="alert-card">', unsafe_allow_html=True)
                st.write(f"**Risky / ambiguous wording:** {row.get('risky_claim', '')}")
                st.write(f"**Classification:** {row.get('classification', 'Risky / ambiguous')}")
                st.write(f"**Why risky:** {row.get('why_risky', '')}")
                st.success(f"Safer rewrite: {row.get('safer_rewrite', '')}")
                st.markdown('</div>', unsafe_allow_html=True)
        if data.get("what_not_to_say"):
            render_card("What not to say", data.get("what_not_to_say"), "🚫", "Risk guardrails")
    with tab_before_after:
        render_table_preview(data, ["before_after_behaviour", "before_after_copy_examples"])
        render_placeholder_panel("Screenshot placeholders", data.get("screenshot_placeholders", []) or [])
    with tab_approval:
        rows = data.get("approval_workflow", []) or data.get("release_approval_checklist", []) or []
        if rows:
            for row in rows:
                label = row.get("approval_scope") or row.get("approval_item") or "Approval item"
                owner = row.get("owner") or row.get("team") or "Owner"
                st.checkbox(f"{label} — {owner}", value=False, disabled=True, help="Portfolio prototype checklist item")
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)
        render_table_preview(data, ["audience_risk_scoring", "confluence_export_outline"])
    with tab_upstream:
        render_table_preview(data, ["interpret_discover_links"])
        st.caption("Use this to show how release messaging is grounded in the same obligations and PRD decisions used by Interpret and Discover.")


def render(settings: Dict[str, Any]) -> None:
    render_demo_banner(settings.get("demo_mode", False))
    st.header("Communicate — Release Readiness Copilot")
    st.caption("Audience-specific release communication, claim safety scoring, approval workflow and support assets.")

    with st.form("release_form"):
        technical_notes = st.text_area("Technical change notes", value="Changed invoice validation logic for Portuguese SAF-T exports. The system now validates CustomerTaxID, InvoiceDate, TaxCode, AccountID and invoice totals before generating the SAF-T file. Invalid records are blocked and displayed in a validation report.", height=160)
        product_context = st.text_input("Product context", value="Enterprise billing/compliance module used by finance teams and customer support.")
        audience = st.text_input("Target audiences", value="Customers, Support, QA, Engineering, Customer Success, Compliance")
        release_type = st.selectbox("Release type", ["Minor feature", "Compliance update", "Breaking change", "Bug fix", "Major release"], index=1)
        compliance_sensitivity = st.selectbox("Compliance sensitivity", ["Low", "Medium", "High"], index=2)
        upstream_context = st.text_area("Optional Interpret/Discover JSON or summary", value="", height=95, help="Paste upstream obligations, PRD pipeline or Jira/QA context to align release messaging.")
        submitted = st.form_submit_button("Generate release readiness package", type="primary")

    if not submitted:
        st.info("Use the default SAF-T validation release example or paste your own technical notes. The preview includes sentence-level risk, approvals and upstream links.")
        render_release_dashboard(demo_output())
        return

    inputs = {"technical_notes": technical_notes, "product_context": product_context, "audience": audience, "release_type": release_type, "compliance_sensitivity": compliance_sensitivity, "upstream_context": upstream_context or "No upstream context provided.", "language": settings["language"], "detail": settings["detail"]}
    prompt = build_release_prompt(inputs)
    try:
        start_ms = now_ms()
        data = call_model_json(prompt, settings["model"], settings["max_output_tokens"], demo_output(), settings["demo_mode"])
        latency = elapsed_ms(start_ms)
        evaluation_for_metrics = evaluate_output(data, __import__("json").dumps(data, ensure_ascii=False), EXPECTED)
        record_output_run(
            workflow="Communicate",
            settings=settings,
            input_payload=inputs,
            output_payload=data,
            evaluation=evaluation_for_metrics,
            latency_ms=latency,
            source_count=1 if inputs else 0,
            metadata={"package_title": "Release Readiness Package"},
        )
        tab_dash, tab_full, tab_eval = st.tabs(["📣 Release dashboard", "📦 Full package & exports", "🛡️ Evaluation"])
        with tab_dash:
            render_release_dashboard(data)
        with tab_full:
            markdown = render_result(data, "Release Readiness Package")
            if st.button("Save structured export locally", key="save_release_export", width="stretch"):
                path = save_export_package_locally(
                    workflow="Communicate",
                    title="Release Readiness Package",
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
