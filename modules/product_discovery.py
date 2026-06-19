"""Discover — Product Discovery Studio."""
from __future__ import annotations

import json
from typing import Any, Dict

import pandas as pd
import streamlit as st

from prompts.product_prompt import build_product_prompt
from services.evaluation_service import evaluate_output
from services.usage_metrics_service import elapsed_ms, now_ms, record_output_run, save_export_package_locally
from services.openai_service import call_model_json
from ui.openai_error_handler import render_openai_error
from services.product_discovery_service import (
    discovery_quality_summary,
    evaluate_discovery_output,
    parse_interpret_json,
    summarise_interpret_context,
)
from services.product_quality_service import build_pipeline_from_discovery, compute_prd_rule_completeness
from services.qa_coverage_service import validate_negative_test_coverage
from ui.evaluation_panel import render_evaluation
from ui.result_panel import render_result
from ui.visual_components import (
    render_card,
    render_demo_banner,
    render_metric_pill,
    render_quality_gate_card,
    render_score_bar,
    render_section_kicker,
    render_table_preview,
)

EXPECTED = [
    "executive_summary", "problem_statement", "jobs_to_be_done", "assumptions_to_test",
    "trade_off_analysis", "rice_prioritisation", "mvp_scope", "v2_scope", "dependencies",
    "success_metrics", "gherkin_acceptance_criteria", "qa_test_matrix", "jira_tickets", "prd_quality_gate",
    "compliance_pipeline", "decision_log", "what_would_invalidate_this_feature", "approval_workflow",
    "security_and_enterprise_controls", "negative_test_coverage", "qa_release_gate",
]


def demo_output() -> Dict[str, Any]:
    return {
        "executive_summary": "A source-aware validation feature for SAF-T invoice exports that converts Interpret obligations into Jira-ready requirements, QA tests and release guardrails.",
        "problem_statement": "Finance and compliance users lose time finding SAF-T invoice issues late in the reporting process, increasing rework, customer escalation and submission risk.",
        "jobs_to_be_done": [{"job": "Validate invoice data before export", "success_outcome": "Users know which records must be fixed before submission."}],
        "personas": [{"persona": "Compliance Analyst", "pain_point": "Late discovery of invalid records", "need": "Actionable validation report with audit evidence"}],
        "interpret_inputs_used": [
            {"obligation_id": "O1", "source": "Interpret", "how_used": "Converted mandatory field obligation into blocking validation requirement."},
            {"obligation_id": "O4", "source": "Interpret", "how_used": "Converted reporting obligation into validation report requirement and QA acceptance test."},
        ],
        "compliance_pipeline": [
            {
                "obligation": "O1 — Validate CustomerTaxID, InvoiceDate, TaxCode, InvoiceTotal and AccountID before SAF-T export",
                "requirement": "R1 — System validates mandatory invoice fields before export",
                "jira": "STORY — Validate critical SAF-T invoice fields",
                "qa": "TC1 — Missing CustomerTaxID is blocked before export; TC1-N2 — invalid tax code is rejected",
                "status": "Ready for engineering discovery after negative test evidence",
            },
            {
                "obligation": "O4 — Export report shows failed records and reasons",
                "requirement": "R2 — Generate validation report with failed invoice IDs and reasons",
                "jira": "STORY — Add pre-export validation report",
                "qa": "TC2 — Report lists failed invoice and failure reason; TC2-N1 — report rejects blank failure reason",
                "status": "Needs UX copy review",
            },
        ],
        "assumptions_to_test": [{"assumption": "Users prefer blocking errors over warning-only validation for critical legal fields", "why_it_matters": "Strict validation can delay exports", "validation_method": "Interview 5 compliance users and review support tickets", "risk_if_wrong": "Users bypass the tool or escalate support cases"}],
        "trade_off_analysis": [{"decision": "Block export vs warn only", "option_a": "Block invalid records", "option_b": "Warn and allow export", "recommendation": "Block critical legal fields, warn on non-critical fields."}],
        "rice_prioritisation": [{"item": "Critical field validation", "reach": 8, "impact": 9, "confidence": 8, "effort": 3, "rice_score": 192}],
        "mvp_scope": ["Validate CustomerTaxID, InvoiceDate, TaxCode, AccountID, totals", "Generate downloadable validation report", "Persist validation run and reviewer decision metadata"],
        "v2_scope": ["Country-specific rule packs", "Bulk correction suggestions", "Direct Jira/Confluence workflow sync"],
        "out_of_scope": ["Automated legal interpretation", "Direct submission to tax authority", "Replacing human compliance review"],
        "dependencies": [{"dependency": "Invoice data model", "owner": "Engineering", "risk": "Missing normalized tax code field"}],
        "success_metrics": [{"metric": "Pre-export validation error detection", "target": ">95% of seeded critical issues detected before export", "measurement_method": "QA seed dataset + production monitoring"}],
        "data_model_impact": [{"object_or_field": "CustomerTaxID", "change": "Required validation metadata and failure reason", "risk": "Country-specific format exceptions"}],
        "api_integration_impact": [{"interface": "SAF-T export service", "impact": "Add pre-export validation step", "open_question": "Should validation be synchronous or queued?"}],
        "gherkin_acceptance_criteria": [
            {"scenario": "O1 negative — Missing customer tax ID", "given": "An invoice has no CustomerTaxID", "when": "The user runs SAF-T validation", "then": "The invoice is blocked with a clear error message"},
            {"scenario": "O4 negative — Missing report reason", "given": "A failed invoice exists without a failure reason", "when": "The validation report is generated", "then": "The report generation is blocked or flags the missing reason"},
        ],
        "qa_test_matrix": [
            {"obligation_id": "O1", "test_case": "Invalid VAT code", "type": "Negative", "expected_result": "Validation error shown and export blocked", "priority": "High"},
            {"obligation_id": "O4", "test_case": "Failed invoice without failure reason", "type": "Negative", "expected_result": "Report flags missing reason before release-ready", "priority": "High"},
        ],
        "negative_test_coverage": [
            {"obligation_id": "O1", "negative_test": "Missing CustomerTaxID, invalid TaxCode and inconsistent InvoiceTotal are rejected before export", "owner": "QA", "evidence_required": "Automated seeded regression dataset"},
            {"obligation_id": "O4", "negative_test": "Validation report cannot omit failed record ID, severity or reason", "owner": "QA", "evidence_required": "Report schema test + screenshot/export evidence"},
        ],
        "qa_release_gate": {"status": "Pass", "rule": "Every obligation must have at least one mapped negative test", "negative_test_coverage_rate": 100},
        "jira_tickets": [{"issue_type": "Story", "summary": "Validate critical SAF-T invoice fields", "description": "As a compliance analyst, I need critical invoice fields validated before export.", "acceptance_criteria": "Gherkin scenarios pass", "priority": "High", "component": "Compliance Export", "labels": "saft,validation,compliance"}],
        "prd_quality_gate": {"score": 88, "missing_items": ["Production error baseline"], "recommendation": "Ready for engineering discovery after SME review."},
        "decision_log": [
            {"decision": "Block critical errors", "reason": "Compliance risk outweighs speed for mandatory fields", "status": "Recommended", "owner": "Product", "evidence": "Interpret O1/O2"},
            {"decision": "Keep legal review in workflow", "reason": "Feature assists validation but does not guarantee compliance", "status": "Accepted", "owner": "Compliance", "evidence": "Release claim safety review"},
        ],
        "what_would_invalidate_this_feature": [
            {"signal": "Users routinely override blocking errors", "threshold": ">20% override requests in pilot", "product_response": "Switch some rules to warnings or improve correction UX"},
            {"signal": "QA seed data reveals unsupported mandatory exceptions", "threshold": "Any high-severity false negative", "product_response": "Stop rollout until rule pack is corrected"},
        ],
        "approval_workflow": [
            {"team": "Product", "approval": "PRD traceability and scope", "required_before": "Engineering handoff", "status": "Required"},
            {"team": "QA", "approval": "Rule-level test matrix", "required_before": "Release candidate", "status": "Required"},
            {"team": "Support", "approval": "FAQ and escalation macro", "required_before": "Customer rollout", "status": "Required"},
            {"team": "Legal/Compliance", "approval": "Customer-facing compliance wording", "required_before": "External release", "status": "Required"},
        ],
        "security_and_enterprise_controls": [
            {"control": "Audit log", "requirement": "Persist run hash, output hash, reviewer verdict and export timestamp", "risk_if_missing": "Cannot evidence review path"},
            {"control": "RBAC", "requirement": "Only Compliance Reviewer can approve obligations", "risk_if_missing": "Unqualified sign-off"},
        ],
        "open_questions": ["Which errors should be warnings rather than blockers?", "What retention period applies to validation evidence?"],
    }


def _parse_json_input(raw: str) -> Dict[str, Any] | None:
    return parse_interpret_json(raw)


def _summarise_interpret_context(interpret_data: Dict[str, Any] | None) -> str:
    return summarise_interpret_context(interpret_data)


def render_discovery_cards(data: Dict[str, Any]) -> None:
    st.subheader("Product Discovery Workspace")
    c1, c2, c3 = st.columns(3)
    with c1:
        render_card("Assumptions", data.get("assumptions_to_test", []), "🧪", "Needs validation")
        render_card("MVP Scope", data.get("mvp_scope", []), "🎯", "Build now")
    with c2:
        render_card("Trade-offs", data.get("trade_off_analysis", []), "⚖️", "Decision support")
        render_card("Dependencies", data.get("dependencies", []), "🔗", "Delivery risk")
    with c3:
        render_card("Jira Tickets", data.get("jira_tickets", []), "🎫", "Exportable")
        render_card("QA Matrix", data.get("qa_test_matrix", []), "✅", "Ready for QA")

    gate = data.get("prd_quality_gate", {}) if isinstance(data.get("prd_quality_gate"), dict) else {}
    render_quality_gate_card(
        "Model PRD Quality Gate",
        gate.get("score", 75),
        gate.get("missing_items", []),
        gate.get("recommendation", "Review assumptions, metrics and edge cases before engineering handoff."),
    )

    completeness = compute_prd_rule_completeness(data)
    st.subheader("Rule-based PRD completeness")
    cols = st.columns(4)
    with cols[0]:
        render_metric_pill("Completeness", f"{completeness['score']}%", "good" if completeness["score"] >= 80 else "mid" if completeness["score"] >= 60 else "bad")
    with cols[1]:
        render_metric_pill("Rules passed", f"{completeness['passed']}/{completeness['total']}", "good")
    with cols[2]:
        render_metric_pill("Missing rules", str(len(completeness["missing"])), "bad" if completeness["missing"] else "good")
    with cols[3]:
        render_metric_pill("Scoring method", "Rules", "good")
    st.caption(completeness["method_note"])
    st.dataframe(pd.DataFrame(completeness["rows"]), width="stretch", hide_index=True)

    negative_gate = validate_negative_test_coverage(data)
    st.subheader("Mandatory negative test coverage")
    ncols = st.columns(4)
    with ncols[0]:
        render_metric_pill("Negative coverage", f"{negative_gate['negative_test_coverage_rate']}%", "good" if negative_gate["release_gate_status"] == "Pass" else "bad")
    with ncols[1]:
        render_metric_pill("Release gate", negative_gate["release_gate_status"], "good" if negative_gate["release_gate_status"] == "Pass" else "bad")
    with ncols[2]:
        render_metric_pill("Obligations covered", f"{negative_gate['obligations_with_negative_test']}/{negative_gate['obligations_total']}", "good" if not negative_gate["missing_negative_coverage"] else "bad")
    with ncols[3]:
        render_metric_pill("Unmapped negative tests", str(negative_gate["unmapped_negative_tests"]), "mid" if negative_gate["unmapped_negative_tests"] else "good")
    st.caption(negative_gate["policy"])
    if negative_gate["rows"]:
        st.dataframe(pd.DataFrame(negative_gate["rows"]), width="stretch", hide_index=True)
    if negative_gate["missing_negative_coverage"]:
        st.error("Release-ready should be blocked until negative tests are added for: " + ", ".join(negative_gate["missing_negative_coverage"]))

    pipeline_rows = build_pipeline_from_discovery(data)
    if pipeline_rows:
        st.subheader("Compliance pipeline: obligation → requirement → Jira → QA")
        st.dataframe(pd.DataFrame(pipeline_rows), width="stretch", hide_index=True)

    if data.get("what_would_invalidate_this_feature"):
        st.subheader("What would invalidate this feature?")
        st.dataframe(pd.DataFrame(data["what_would_invalidate_this_feature"]), width="stretch", hide_index=True)

    if data.get("approval_workflow"):
        st.subheader("Approval workflow")
        st.dataframe(pd.DataFrame(data["approval_workflow"]), width="stretch", hide_index=True)

    if data.get("rice_prioritisation"):
        st.subheader("RICE Prioritisation")
        df = pd.DataFrame(data["rice_prioritisation"])
        st.dataframe(df, width="stretch", hide_index=True)
        if "rice_score" in df.columns:
            chart_df = df[["item", "rice_score"]].set_index("item")
            st.bar_chart(chart_df)


def render(settings: Dict[str, Any]) -> None:
    render_demo_banner(settings.get("demo_mode", False))
    st.header("Discover — Product Discovery Studio")
    st.caption("A structured PM workspace that can consume Interpret outputs and turn obligations into requirements, Jira tickets, QA and approval workflows.")

    with st.form("product_form"):
        feature_idea = st.text_area("Feature idea", value="Build a feature that validates SAF-T invoice data before submission to the Portuguese tax authority.", height=110)
        domain = st.text_input("Domain", value="Tax compliance / logistics ERP")
        persona = st.text_input("Primary persona", value="Compliance analyst")
        business_context = st.text_area("Business context", value="Enterprise logistics and accounting software used by finance teams in Portugal.", height=90)
        compliance_context = st.text_area("Compliance context", value="SAF-T PT invoice export, VAT reporting, customer tax ID validation.", height=80)
        interpret_json = st.text_area("Optional Interpret JSON output", value="", height=100, help="Paste the JSON exported by Interpret to auto-link obligations to PRD, Jira and QA.")
        submitted = st.form_submit_button("Generate product discovery package", type="primary")

    interpret_data = _parse_json_input(interpret_json)
    if interpret_json.strip() and interpret_data:
        st.success("Interpret output detected. Obligations, requirements and validation rules will be used as upstream product input.")
    elif interpret_json.strip() and not interpret_data:
        st.warning("Could not parse Interpret JSON. The prompt will continue without upstream Interpret context.")

    if not submitted:
        render_section_kicker("Preview")
        st.info("Use the default SAF-T example or paste Interpret JSON from the Compliance Studio. The output now includes pipeline, invalidation criteria, approvals and rule-based PRD completeness.")
        sample = demo_output()
        render_discovery_cards(sample)
        return

    inputs = {
        "feature_idea": feature_idea,
        "domain": domain,
        "persona": persona,
        "business_context": business_context,
        "compliance_context": compliance_context,
        "interpret_context": _summarise_interpret_context(interpret_data),
        "language": settings["language"],
        "detail": settings["detail"],
    }
    prompt = build_product_prompt(inputs)
    try:
        start_ms = now_ms()
        data = call_model_json(prompt, settings["model"], settings["max_output_tokens"], demo_output(), settings["demo_mode"])
        latency = elapsed_ms(start_ms)
        evaluation_for_metrics = evaluate_discovery_output(data)
        record_output_run(
            workflow="Discover",
            settings=settings,
            input_payload=inputs,
            output_payload=data,
            evaluation=evaluation_for_metrics,
            latency_ms=latency,
            source_count=1 if interpret_data else 0,
            metadata={"domain": domain, "used_interpret_input": bool(interpret_data)},
        )
        tab_workspace, tab_full, tab_eval = st.tabs(["🧠 Workspace", "📦 Full package & exports", "🛡️ Quality gate"])
        with tab_workspace:
            render_discovery_cards(data)
            render_table_preview(data, ["gherkin_acceptance_criteria", "jira_tickets", "qa_test_matrix", "negative_test_coverage", "security_and_enterprise_controls"])
        with tab_full:
            markdown = render_result(data, "Product Discovery Package")
            if st.button("Save structured export locally", key="save_discover_export", width="stretch"):
                path = save_export_package_locally(
                    workflow="Discover",
                    title="Product Discovery Package",
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
