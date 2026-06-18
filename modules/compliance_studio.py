"""Interpret — Compliance-to-Product Studio.

Run-specific quality metrics are computed from the current generated output and
retrieved source chunks. Precision/recall require an optional reviewer-provided
gold set, so synthetic demo numbers are not presented as product performance.

The module keeps the core compliance-to-product review controls: source quotes,
rule-based citation checks, citation explorer, version diff, human review queue,
and benchmark panel against hand-written synthetic gold obligations.
"""
from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd
import streamlit as st

from prompts.compliance_prompt import build_compliance_prompt
from core.pipeline import run_interpret_review_discover_pipeline
from services.citation_verifier import (
    build_human_review_queue,
    build_obligation_support_matrix,
    grounding_heatmap_items,
    grounding_summary,
    highlight_claim_terms,
    rule_based_version_diff,
    verify_citations_advanced,
)
from services.cost_service import estimate_run_cost
from services.evaluation_service import evaluate_output
from services.export_service import dict_to_markdown
from services.enterprise_controls_service import can, document_version_record, record_audit_event, signed_report_manifest
from services.interpret_benchmark_service import compare_generated_to_gold, load_gold_obligations
from services.interpret_metrics_service import calculate_interpret_quality_metrics, metrics_as_rows, parse_gold_benchmark_text
from services.openai_service import call_model_json, embed_texts, render_openai_error
from services.usage_metrics_service import elapsed_ms, now_ms, record_output_run, save_export_package_locally
from services.human_feedback_service import record_human_reviews, summarize_feedback_inventory
from services.qa_coverage_service import validate_negative_test_coverage
from services.run_history_service import (
    append_review_report,
    append_run_history,
    build_final_review_report,
    build_reviewer_items,
    compare_recent_runs,
    load_run_history,
    stable_hash as run_stable_hash,
    summarise_interpret_run,
)
from services.rag_service import (
    SourceChunk,
    chunk_text,
    extract_text_from_upload,
    highlight_terms,
    rank_chunks,
    source_coverage,
)
from ui.evaluation_panel import render_evaluation
from ui.result_panel import render_result
from ui.visual_components import (
    render_demo_banner,
    render_grounding_heatmap,
    render_metric_pill,
    render_score_bar,
    render_standard_export_bar,
    render_table_preview,
)

EXPECTED = [
    "executive_summary",
    "obligation_extraction",
    "traceability_matrix",
    "product_requirements",
    "validation_rules",
    "qa_test_cases",
    "source_quote_candidates",
    "human_review_queue",
    "risks",
    "decision_log",
]

SAMPLE_DOC = """
Invoices included in a Portuguese SAF-T export must include the customer tax identification number, invoice date, tax code, invoice total and customer account reference where applicable. Records with missing tax identifiers or inconsistent totals should be corrected before export. The product should maintain sufficient validation evidence to support user review and audit checks. Export reports must show which invoice records failed validation and why.
"""

PREVIOUS_DOC = """
Invoices included in a Portuguese SAF-T export should include invoice date, tax code and invoice total. Validation of customer tax identifiers is recommended before submission.
"""


def demo_output() -> Dict[str, Any]:
    return {
        "executive_summary": "The uploaded guidance creates product obligations around pre-export validation of invoice identifiers, dates, VAT/tax codes, totals, account references and validation evidence. Human compliance review remains required.",
        "obligation_extraction": [
            {
                "obligation_id": "O1",
                "obligation": "Validate critical invoice fields before SAF-T export",
                "mandatory_fields": "Customer tax ID, invoice date, tax code, invoice total, customer account reference",
                "deadline_or_timing": "Before export/submission",
                "exceptions": "Account reference appears applicable where relevant",
                "source": "[S1]",
                "quote_support": "Invoices included in a Portuguese SAF-T export must include the customer tax identification number, invoice date, tax code, invoice total and customer account reference where applicable.",
                "model_confidence": "High",
                "human_review": "Review AccountID applicability",
            },
            {
                "obligation_id": "O2",
                "obligation": "Correct missing tax identifiers or inconsistent totals before export",
                "mandatory_fields": "Customer tax identifier and invoice total consistency",
                "deadline_or_timing": "Before export",
                "exceptions": "None stated in the source excerpt",
                "source": "[S1]",
                "quote_support": "Records with missing tax identifiers or inconsistent totals should be corrected before export.",
                "model_confidence": "High",
                "human_review": "Confirm whether this is blocking or warning-only",
            },
            {
                "obligation_id": "O3",
                "obligation": "Maintain validation evidence to support user review and audit checks",
                "mandatory_fields": "Validation evidence, review status, audit evidence",
                "deadline_or_timing": "At validation/export time",
                "exceptions": "None stated in the source excerpt",
                "source": "[S1]",
                "quote_support": "maintain sufficient validation evidence to support user review and audit checks",
                "model_confidence": "High",
                "human_review": "Confirm evidence retention expectations",
            },
            {
                "obligation_id": "O4",
                "obligation": "Export reports must show which invoice records failed validation and why",
                "mandatory_fields": "Failed invoice record identifier, failure reason",
                "deadline_or_timing": "When export validation report is generated",
                "exceptions": "None stated in the source excerpt",
                "source": "[S1]",
                "quote_support": "Export reports must show which invoice records failed validation and why.",
                "model_confidence": "High",
                "human_review": "Confirm report format and user workflow",
            },
        ],
        "traceability_matrix": [
            {
                "source": "[S1]",
                "obligation": "Critical fields must be present and consistent",
                "product_impact": "Add pre-export validation workflow",
                "data_field": "CustomerTaxID, InvoiceDate, TaxCode, InvoiceTotal, AccountID",
                "validation_rule": "Block or flag export for missing tax ID or inconsistent total",
                "test_case": "Invoice without CustomerTaxID is blocked or flagged",
                "release_note": "New SAF-T validation checks help users identify incomplete invoice records before export",
                "quote_support": "Records with missing tax identifiers or inconsistent totals should be corrected before export.",
                "model_confidence": "High",
            }
        ],
        "product_requirements": [
            {
                "requirement_id": "R1",
                "requirement": "System must validate mandatory invoice fields before SAF-T export",
                "source": "[S1]",
                "quote_support": "Invoices included in a Portuguese SAF-T export must include the customer tax identification number, invoice date, tax code, invoice total and customer account reference where applicable.",
                "implementation_readiness": "Ready after compliance review",
            }
        ],
        "validation_rules": [
            {
                "rule_id": "VR1",
                "field": "CustomerTaxID",
                "logic": "Must not be blank for taxable invoices before SAF-T export",
                "failure_message": "Customer tax ID is required before SAF-T export",
                "source": "[S1]",
                "quote_support": "must include the customer tax identification number",
            }
        ],
        "qa_test_cases": [
            {
                "test_id": "TC1-N1",
                "obligation_id": "O1",
                "type": "Negative",
                "scenario": "Missing tax ID",
                "steps": "Create invoice without tax ID; run validation",
                "expected_result": "Record is blocked or appears in validation report before export",
                "source": "[S1]",
            },
            {
                "test_id": "TC2-N1",
                "obligation_id": "O2",
                "type": "Negative",
                "scenario": "Inconsistent invoice total",
                "steps": "Create invoice where line totals do not equal invoice total; run validation",
                "expected_result": "Record is blocked or flagged before export",
                "source": "[S1]",
            },
            {
                "test_id": "TC3-N1",
                "obligation_id": "O3",
                "type": "Negative",
                "scenario": "Missing validation evidence",
                "steps": "Run validation and remove evidence metadata before report finalization",
                "expected_result": "Report cannot be finalized until evidence metadata is restored or reviewed",
                "source": "[S1]",
            },
            {
                "test_id": "TC4-N1",
                "obligation_id": "O4",
                "type": "Negative",
                "scenario": "Failed invoice without failure reason",
                "steps": "Generate validation report with a failed invoice record and blank reason",
                "expected_result": "Report flags the missing reason before export package is marked ready",
                "source": "[S1]",
            },
        ],
        "version_comparison": [
            {
                "change_type": "Changed",
                "old_obligation": "Tax ID validation recommended",
                "new_obligation": "Missing tax IDs should be corrected before export",
                "product_action": "Increase severity to blocking or review-required validation",
                "risk": "Medium",
            }
        ],
        "source_quote_candidates": [
            {
                "claim": "Tax ID and totals require validation before export",
                "citation": "[S1]",
                "quote_support": "Records with missing tax identifiers or inconsistent totals should be corrected before export.",
            }
        ],
        "human_review_queue": [
            {"item": "Confirm whether AccountID is mandatory for all customers", "reason": "Source says where applicable", "reviewer": "Compliance"},
            {"item": "Confirm whether missing identifiers should block export or produce a warning", "reason": "Source says corrected before export but does not specify UI severity", "reviewer": "Product/Compliance"},
        ],
        "source_coverage_summary": "1 of 1 selected chunks used. Scanned PDFs and tables may require manual review.",
        "decision_log": [
            {"decision": "Treat missing CustomerTaxID as blocking", "owner": "Product + Compliance", "reason": "Source says records with missing tax identifiers should be corrected before export", "evidence": "O2 / S1", "status": "Needs compliance sign-off"},
            {"decision": "Route AccountID applicability to reviewer", "owner": "Product", "reason": "Source says customer account reference applies where applicable", "evidence": "O1 / S1", "status": "Open"}
        ],
        "risks": [
            {"risk": "Over-blocking invoices due to jurisdiction-specific exceptions", "severity": "Medium", "mitigation": "Allow rule configuration by country/entity"}
        ],
        "open_questions": ["Which invoice types are exempt from AccountID validation?"],
    }


def _prepare_sources(
    text: str,
    name: str,
    query: str,
    top_k: int,
    embedding_model: str,
    demo_mode: bool,
) -> tuple[List[SourceChunk], List[SourceChunk]]:
    all_chunks = chunk_text(text, doc_name=name)
    if not all_chunks:
        return [], []
    try:
        chunk_embeddings = embed_texts([c.text for c in all_chunks], embedding_model, demo_mode)
        query_embedding = embed_texts([query], embedding_model, demo_mode)[0]
        ranked = rank_chunks(query, all_chunks, chunk_embeddings, query_embedding, top_k=top_k)
    except Exception:
        ranked = rank_chunks(query, all_chunks, None, None, top_k=top_k)
    return all_chunks, ranked


def _source_by_id(sources: List[SourceChunk]) -> Dict[str, SourceChunk]:
    return {s.id: s for s in sources}


def _parse_uploaded_gold(uploaded_gold: Any) -> tuple[Dict[str, Any] | None, str]:
    if not uploaded_gold:
        return None, ""
    try:
        text = uploaded_gold.getvalue().decode("utf-8")
        benchmark = parse_gold_benchmark_text(text, filename=getattr(uploaded_gold, "name", "uploaded_gold"))
        count = len(benchmark.get("gold_obligations", []) or [])
        return benchmark, f"Loaded {count} gold obligations from {getattr(uploaded_gold, 'name', 'uploaded file')}."
    except Exception as error:
        return None, f"Could not parse gold obligations file: {error}"


def _gold_template_json() -> str:
    return """{
  "name": "Run-specific gold obligations for this document",
  "gold_obligations": [
    {
      "id": "G1",
      "obligation": "Customer tax identification number must be present before SAF-T export.",
      "required_terms": ["customer tax identification", "SAF-T export"],
      "expected_source": "S1",
      "expected_quote": "Invoices included in a Portuguese SAF-T export must include the customer tax identification number."
    }
  ]
}
"""


def render_compliance_dashboard(
    data: Dict[str, Any],
    current_text: str,
    query: str,
    sources: List[SourceChunk],
    all_chunks: List[SourceChunk],
    prev_sources: List[SourceChunk],
    citation_rows: List[Dict[str, Any]],
) -> None:
    coverage = source_coverage(all_chunks, sources)
    summary = grounding_summary(citation_rows)
    top_metrics = st.columns(5)
    with top_metrics[0]:
        render_metric_pill("Used chunks", f"{coverage.get('used_chunks', 0)}/{coverage.get('total_chunks', 0)}", "good")
    with top_metrics[1]:
        render_metric_pill("Avg support", f"{summary.get('average_support_score', 0)}%", "good" if summary.get("average_support_score", 0) >= 75 else "mid")
    with top_metrics[2]:
        render_metric_pill("Weak claims", str(summary.get("weak_or_missing_claims", 0)), "bad" if summary.get("weak_or_missing_claims") else "good")
    with top_metrics[3]:
        render_metric_pill("Human review", "Required" if summary.get("human_review_required") else "Optional", "mid" if summary.get("human_review_required") else "good")
    with top_metrics[4]:
        render_metric_pill("Risks", str(len(data.get("risks", []) or [])), "bad" if data.get("risks") else "good")

    feedback = data.get("_human_feedback", {}) if isinstance(data.get("_human_feedback"), dict) else {}
    if feedback:
        adjusted = feedback.get("obligations_adjusted_by_feedback", 0)
        used = feedback.get("feedback_examples_used", 0)
        if adjusted or used:
            st.info(f"Human feedback flywheel: {adjusted} obligation(s) adjusted using {used} prior reviewer example(s). This is local few-shot guidance, not model training.")

    st.caption("Support scores below are computed by deterministic rule-based checks. They are not model self-scores and do not replace human compliance review.")
    render_grounding_heatmap(grounding_heatmap_items(citation_rows), "Rule-based grounding heatmap")

    support_matrix = build_obligation_support_matrix(data, citation_rows)
    left, center, right = st.columns([1.04, 1.25, 1.04])
    with left:
        st.subheader("Source document highlights")
        st.markdown('<div class="source-panel">', unsafe_allow_html=True)
        preview = current_text[:5200] + ("..." if len(current_text) > 5200 else "")
        st.markdown(highlight_terms(preview, query), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with center:
        st.subheader("Obligations with source quotes")
        if support_matrix:
            for item in support_matrix:
                tone = "good" if int(item.get("support_score") or 0) >= 75 else "mid" if int(item.get("support_score") or 0) >= 55 else "bad"
                with st.container(border=True):
                    st.markdown(f"**{item.get('obligation_id')} — {item.get('obligation')}**")
                    st.write(f"**Source:** {item.get('source')} · **Support:** {item.get('support_score')}% · **Status:** {item.get('support_status')}")
                    render_score_bar("Quote support", int(item.get("support_score") or 0), item.get("support_status", ""))
                    st.caption(f"Quote: {item.get('best_supporting_quote')}")
                    if item.get("review_required"):
                        st.warning(f"Review: {item.get('review_reason')}")
                    else:
                        st.success("No immediate issue detected by rule-based checks.")
        else:
            st.info("No obligations generated yet.")
    with right:
        st.subheader("Citation explorer")
        if sources:
            source_ids = [s.id for s in sources]
            selected_source_id = st.selectbox("Jump to cited source", source_ids, key="citation_source_select_dashboard")
            selected_source = _source_by_id(sources).get(selected_source_id)
            related_rows = [r for r in citation_rows if r.get("citation") == selected_source_id]
            selected_claim = ""
            if related_rows:
                labels = [f"{r.get('section')} #{r.get('row')} — {str(r.get('claim'))[:56]}" for r in related_rows]
                selected_idx = st.selectbox("Highlight claim terms", range(len(labels)), format_func=lambda i: labels[i], key="claim_select_dashboard")
                selected_claim = str(related_rows[selected_idx].get("claim", ""))
            if selected_source:
                st.write(f"**Why selected:** retrieved by `{selected_source.method}` using the query focus and document similarity. Demo Mode uses deterministic local vectors; API Mode uses the configured embedding model.")
                st.write(f"**Alternative chunks considered:** {max(0, len(all_chunks)-len(sources))} not selected in top-k.")
                st.markdown('<div class="source-panel">', unsafe_allow_html=True)
                if selected_claim:
                    st.markdown(highlight_claim_terms(selected_source.text[:1300], selected_claim), unsafe_allow_html=True)
                else:
                    st.write(selected_source.text[:1300] + ("..." if len(selected_source.text) > 1300 else ""))
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No retrieved citations available.")

    st.subheader("Traceability and QA matrices")
    render_table_preview(data, ["traceability_matrix", "validation_rules", "qa_test_cases", "product_requirements"])

    negative_gate = validate_negative_test_coverage(data)
    st.subheader("Mandatory negative test coverage")
    cols = st.columns(4)
    with cols[0]:
        render_metric_pill("Negative coverage", f"{negative_gate['negative_test_coverage_rate']}%", "good" if negative_gate["release_gate_status"] == "Pass" else "bad")
    with cols[1]:
        render_metric_pill("Release gate", negative_gate["release_gate_status"], "good" if negative_gate["release_gate_status"] == "Pass" else "bad")
    with cols[2]:
        render_metric_pill("Covered obligations", f"{negative_gate['obligations_with_negative_test']}/{negative_gate['obligations_total']}", "good" if not negative_gate["missing_negative_coverage"] else "bad")
    with cols[3]:
        render_metric_pill("Negative tests", str(negative_gate["negative_tests_total"]), "good" if negative_gate["negative_tests_total"] else "bad")
    st.caption(negative_gate["policy"])
    if negative_gate["rows"]:
        st.dataframe(pd.DataFrame(negative_gate["rows"]), width="stretch", hide_index=True)
    if negative_gate["missing_negative_coverage"]:
        st.error("Do not mark release-ready until mapped negative tests exist for: " + ", ".join(negative_gate["missing_negative_coverage"]))

    if prev_sources:
        st.subheader("Visual diff preview")
        st.caption("Rule-based diff of obligation-like sentences. Full diff is available in the Version Diff tab.")
        diff_rows = rule_based_version_diff("\n".join(s.text for s in prev_sources), "\n".join(s.text for s in sources))
        st.dataframe(pd.DataFrame(diff_rows[:8]), width="stretch", hide_index=True)


def render_source_quote_matrix(data: Dict[str, Any], citation_rows: List[Dict[str, Any]], sources: List[SourceChunk]) -> None:
    st.subheader("Source quote matrix")
    st.caption("Every extracted obligation should have a citation and a best supporting quote. Weak rows are routed to human review.")
    matrix = build_obligation_support_matrix(data, citation_rows)
    if matrix:
        st.dataframe(pd.DataFrame(matrix), width="stretch", hide_index=True)
        csv = pd.DataFrame(matrix).to_csv(index=False).encode("utf-8")
        st.download_button("Download obligation source quote matrix CSV", csv, "obligation_source_quote_matrix.csv", "text/csv", key="download_obligation_source_quote_matrix_csv")
    else:
        st.info("No obligation support matrix available.")

    st.subheader("Citation deep link / source inspector")
    if not citation_rows:
        st.info("No citation rows found.")
        return
    labels = [f"{i+1}. {r.get('citation')} · {r.get('support_score')}% · {str(r.get('claim'))[:90]}" for i, r in enumerate(citation_rows)]
    selected = st.selectbox("Select a claim to inspect", range(len(labels)), format_func=lambda i: labels[i], key="deep_link_citation_select")
    row = citation_rows[selected]
    source = _source_by_id(sources).get(row.get("citation"))
    c1, c2 = st.columns([1.04, 1.25])
    with c1:
        st.markdown("**Generated claim**")
        st.write(row.get("claim"))
        st.markdown("**Rule-based result**")
        render_score_bar("Support", int(row.get("support_score") or 0), row.get("verification_status", ""))
        st.write(f"**Review reason:** {row.get('review_reason')}")
        st.write(f"**Matched terms:** {row.get('matched_terms', '')}")
    with c2:
        st.markdown("**Cited source chunk with highlighted claim terms**")
        if source:
            st.markdown('<div class="source-panel">', unsafe_allow_html=True)
            st.markdown(highlight_claim_terms(source.text, str(row.get("claim", ""))), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("The cited source ID was not found in the selected source set.")


def render_citation_verifier(data: Dict[str, Any], sources: List[SourceChunk], citation_rows: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    """Render rule-based citation support checking and quote-level grounding."""
    citation_rows = citation_rows if citation_rows is not None else verify_citations_advanced(data, sources)
    summary = grounding_summary(citation_rows)
    cols = st.columns(5)
    with cols[0]:
        render_metric_pill("Checked claims", str(summary.get("verified_claims", 0)), "good")
    with cols[1]:
        avg = int(summary.get("average_support_score", 0) or 0)
        render_metric_pill("Avg support", f"{avg}%", "good" if avg >= 75 else "mid" if avg >= 55 else "bad")
    with cols[2]:
        weak = int(summary.get("weak_or_missing_claims", 0) or 0)
        render_metric_pill("Weak/missing", str(weak), "bad" if weak else "good")
    with cols[3]:
        render_metric_pill("Quote integrity", f"{summary.get('quote_integrity_rate', 0)}%", "good" if summary.get("quote_integrity_rate", 0) >= 75 else "mid")
    with cols[4]:
        render_metric_pill("Human review", "Required" if summary.get("human_review_required") else "Optional", "mid" if summary.get("human_review_required") else "good")

    render_grounding_heatmap(grounding_heatmap_items(citation_rows), "Quote-level grounding heatmap")

    if citation_rows:
        st.subheader("Rule-based citation support table")
        display_cols = [
            "section", "row", "claim_key", "claim", "citation", "exists", "support_score",
            "verification_status", "review_required", "review_reason", "quote_present_in_source",
            "supporting_quote", "matched_terms", "source_score", "retrieval_method",
        ]
        df = pd.DataFrame(citation_rows)
        st.dataframe(df[[c for c in display_cols if c in df.columns]], width="stretch", hide_index=True)
        with st.expander("Support score components", expanded=False):
            score_cols = ["claim", "support_score", "token_containment", "jaccard", "char_ngram", "modal_alignment", "missing_numbers", "review_reason"]
            st.dataframe(df[[c for c in score_cols if c in df.columns]], width="stretch", hide_index=True)
        with st.expander("How this works", expanded=False):
            st.write(
                "The verifier checks that each cited source ID exists, checks whether the model-proposed quote is actually present in the source, "
                "selects the best supporting sentence, and calculates a conservative support score from lexical overlap, character n-grams, "
                "modality alignment and number/negation checks. It is a review aid, not legal validation."
            )
    else:
        st.info("No citation rows found. Generate a structured compliance package first.")
    return citation_rows


def render_version_diff(previous_text: str, current_text: str, data: Dict[str, Any], prev_sources: List[SourceChunk], sources: List[SourceChunk]) -> None:
    st.subheader("Version diff — obligation impact")
    st.caption("This combines model-proposed version comparison with a deterministic sentence-level diff of obligation-like statements.")
    if data.get("version_comparison"):
        st.markdown("**Model-proposed comparison**")
        st.dataframe(pd.DataFrame(data["version_comparison"]), width="stretch", hide_index=True)

    diff_rows = rule_based_version_diff(previous_text or "\n".join(s.text for s in prev_sources), current_text or "\n".join(s.text for s in sources))
    if diff_rows:
        st.markdown("**Rule-based diff**")
        st.dataframe(pd.DataFrame(diff_rows), width="stretch", hide_index=True)
        for item in diff_rows:
            if item.get("change_type") in {"Added", "Removed", "Changed"}:
                with st.container(border=True):
                    st.markdown(f"**{item.get('change_type')} — similarity {item.get('similarity')}%**")
                    if item.get("previous_item"):
                        st.write(f"Previous: {item.get('previous_item')}")
                    if item.get("current_item"):
                        st.write(f"Current: {item.get('current_item')}")
                    st.caption(item.get("product_impact_hint"))
    else:
        st.info("No comparable obligation-like sentences found.")


def render_human_review_queue(data: Dict[str, Any], citation_rows: List[Dict[str, Any]]) -> None:
    st.subheader("Human review queue")
    queue = build_human_review_queue(data, citation_rows)
    if not queue:
        st.success("No review items detected by the model or rule-based checks. A human compliance review is still recommended for real use.")
        return
    df = pd.DataFrame(queue)
    st.dataframe(df, width="stretch", hide_index=True)
    high = len([r for r in queue if str(r.get("priority", "")).lower() == "high"])
    cols = st.columns(3)
    with cols[0]:
        render_metric_pill("Open review items", str(len(queue)), "mid")
    with cols[1]:
        render_metric_pill("High priority", str(high), "bad" if high else "good")
    with cols[2]:
        render_metric_pill("Primary owner", "Compliance/Product", "mid")
    st.download_button("Download human review queue CSV", df.to_csv(index=False).encode("utf-8"), "human_review_queue.csv", "text/csv", key="download_human_review_queue_csv")


def render_quality_metrics_panel(data: Dict[str, Any], citation_rows: List[Dict[str, Any]], gold_benchmark: Dict[str, Any] | None = None) -> None:
    st.subheader("Interpret quality metrics")
    st.caption(
        "Citation support, unsupported-claim and human-review rates are calculated from the actual current run. "
        "Obligation precision/recall are calculated only when you provide an independent gold obligations file for this document."
    )
    payload = calculate_interpret_quality_metrics(data, citation_rows, benchmark=gold_benchmark)

    if gold_benchmark:
        st.success(f"Using run-specific gold set: {gold_benchmark.get('name', 'uploaded gold')} · {len(gold_benchmark.get('gold_obligations', []) or [])} obligations")
    else:
        st.warning("Obligation precision and recall are N/A until you upload a reviewer-written gold obligations file for this document. The other three metrics are calculated from the current run.")

    metric_cols = st.columns(5)
    for col, metric in zip(metric_cols, payload.get("metrics", [])):
        with col:
            render_metric_pill(metric["metric"], metric["display_value"], metric.get("tone", "neutral"))
            st.caption(f"{metric.get('fraction', 'N/A')} · {metric.get('status', '')}")

    st.info(payload.get("method_note", ""))

    st.markdown("**Metric definitions and limitations**")
    metric_rows = pd.DataFrame(metrics_as_rows(payload))
    st.dataframe(metric_rows, width="stretch", hide_index=True)

    with st.expander("How each metric is calculated", expanded=False):
        st.markdown(
            """
- **Obligation precision**: generated obligations that match the uploaded reviewer-written gold set / generated obligations. If no gold set is provided, this is **N/A**.
- **Obligation recall**: uploaded gold obligations recovered by the generated output / total uploaded gold obligations. If no gold set is provided, this is **N/A**.
- **Citation support rate**: checked claims with an existing cited source and rule-based support score at or above the support threshold / checked claims. This is calculated from the actual current run.
- **Unsupported claim rate**: checked claims with missing sources or very weak textual support / checked claims. Lower is better. This is calculated from the actual current run.
- **Human review rate**: checked claims flagged for human review / checked claims. Lower is not always better in regulated workflows; surfacing uncertainty is preferable to hiding it. This is calculated from the actual current run.

These are intentionally not model self-scores. Precision/recall require independent gold labels; citation-related rates are deterministic checks against the retrieved sources used in the run.
"""
        )

    counts = payload.get("citation_counts", {})
    st.markdown("**Citation quality breakdown**")
    breakdown = pd.DataFrame([
        {"bucket": "Supported", "count": counts.get("supported_claims", 0), "meaning": "Existing citation and support score above threshold"},
        {"bucket": "Partial", "count": counts.get("partial_claims", 0), "meaning": "Some textual overlap, but not strong enough for full support"},
        {"bucket": "Unsupported", "count": counts.get("unsupported_claims", 0), "meaning": "Missing citation or very weak textual support"},
        {"bucket": "Human review", "count": counts.get("human_review_claims", 0), "meaning": "Routed to review due to weak support, quote, number or modality issue"},
    ])
    st.dataframe(breakdown, width="stretch", hide_index=True)

    st.download_button(
        "Download Interpret quality metrics CSV",
        metric_rows.to_csv(index=False).encode("utf-8"),
        "interpret_quality_metrics.csv",
        "text/csv",
        key="download_interpret_quality_metrics_csv",
    )


def render_benchmark_panel(data: Dict[str, Any], citation_rows: List[Dict[str, Any]] | None = None) -> None:
    st.subheader("Interpret benchmark — synthetic gold obligations")
    st.caption("This benchmark avoids self-scoring by comparing generated obligations against a hand-written synthetic gold set.")
    try:
        benchmark = load_gold_obligations()
        results = compare_generated_to_gold(data, benchmark)
    except Exception as error:
        st.error(f"Could not load benchmark: {error}")
        return
    cols = st.columns(4)
    with cols[0]:
        render_metric_pill("Obligation precision", f"{results['precision_proxy']}%", "good" if results["precision_proxy"] >= 70 else "mid")
    with cols[1]:
        render_metric_pill("Obligation recall", f"{results['recall_proxy']}%", "good" if results["recall_proxy"] >= 70 else "mid")
    with cols[2]:
        render_metric_pill("F1 proxy", f"{results['f1_proxy']}%", "good" if results["f1_proxy"] >= 70 else "mid")
    with cols[3]:
        render_metric_pill("Gold obligations", str(results["gold_count"]), "neutral")
    st.write(results["method_note"])
    st.markdown("**Match matrix**")
    st.dataframe(pd.DataFrame(results["match_matrix"]), width="stretch", hide_index=True)
    if results["missing_gold_obligations"]:
        st.markdown("**Missing gold obligations**")
        st.dataframe(pd.DataFrame(results["missing_gold_obligations"]), width="stretch", hide_index=True)
    with st.expander("Generated obligations vs gold obligations", expanded=False):
        st.dataframe(pd.DataFrame(results.get("generated_matrix", [])), width="stretch", hide_index=True)



def render_reviewer_and_run_history(
    data: Dict[str, Any],
    citation_rows: List[Dict[str, Any]],
    current_text: str,
    sources: List[SourceChunk],
    settings: Dict[str, Any],
) -> None:
    st.subheader("Reviewer mode and persistent run history")
    st.caption(
        "Reviewer mode turns generated obligations into explicit correct/incorrect/needs-review decisions. "
        "Run history stores privacy-conscious metadata and metrics locally so runs can be compared over time."
    )

    reviewer_items = build_reviewer_items(data, citation_rows)
    if reviewer_items:
        st.markdown("**Reviewer mode — obligation verdicts**")
        decisions: List[Dict[str, Any]] = []
        for idx, item in enumerate(reviewer_items):
            with st.container(border=True):
                st.write(f"**{item.get('obligation_id')} — {item.get('claim')}**")
                st.write(f"Citation: {item.get('citation')} · Support: {item.get('support_score')}% · Status: {item.get('support_status')}")
                if item.get("best_supporting_quote"):
                    st.caption(f"Quote: {item.get('best_supporting_quote')}")
                options = ["Correct", "Needs review", "Incorrect"]
                default = item.get("default_status", "Needs review")
                default_idx = options.index(default) if default in options else 1
                status = st.radio(
                    "Reviewer verdict",
                    options,
                    index=default_idx,
                    horizontal=True,
                    key=f"review_status_{item.get('obligation_id')}_{idx}",
                )
                comment = st.text_input(
                    "Reviewer comment / evidence needed",
                    value=item.get("review_reason", ""),
                    key=f"review_comment_{item.get('obligation_id')}_{idx}",
                )
                correction = st.text_input(
                    "Optional corrected wording",
                    value="",
                    key=f"review_correction_{item.get('obligation_id')}_{idx}",
                    help="Saved corrections can be reused as local few-shot examples in future runs.",
                )
                decisions.append({
                    "obligation_id": item.get("obligation_id"),
                    "artifact_id": item.get("obligation_id"),
                    "artifact_type": "obligation",
                    "status": status,
                    "comment": comment,
                    "corrected_text": correction,
                    "original_text": item.get("claim", ""),
                })
    else:
        st.info("No obligation-level reviewer items were available for this run.")
        decisions = []

    report = build_final_review_report(data, citation_rows, decisions)
    st.markdown("**Final report — supported, weak, missing, reviewed**")
    cols = st.columns(4)
    summary = report.get("summary", {})
    with cols[0]:
        render_metric_pill("Supported", str(summary.get("supported", 0)), "good")
    with cols[1]:
        render_metric_pill("Weak", str(summary.get("weak", 0)), "mid")
    with cols[2]:
        render_metric_pill("Missing", str(summary.get("missing", 0)), "bad" if summary.get("missing") else "good")
    with cols[3]:
        render_metric_pill("Reviewed", str(summary.get("reviewed", 0)), "good" if summary.get("reviewed") else "mid")

    actor = settings.get("demo_user", "demo-user")
    role = settings.get("role", "Product Manager")
    inventory = summarize_feedback_inventory(domain="SAF-T invoice export validation")
    st.markdown("**Human feedback flywheel**")
    fcols = st.columns(3)
    with fcols[0]:
        render_metric_pill("Stored reviews", str(inventory.get("human_reviews_total", 0)), "good" if inventory.get("human_reviews_total", 0) else "mid")
    with fcols[1]:
        render_metric_pill("Reusable examples", str(inventory.get("feedback_examples_available", 0)), "good" if inventory.get("feedback_examples_available", 0) else "mid")
    with fcols[2]:
        applied = data.get("_human_feedback", {}) if isinstance(data.get("_human_feedback"), dict) else {}
        render_metric_pill("Adjusted this run", str(applied.get("obligations_adjusted_by_feedback", 0)), "mid" if applied.get("obligations_adjusted_by_feedback", 0) else "neutral")
    if decisions and st.button("Save reviewer decisions to human feedback flywheel", width="stretch"):
        saved = record_human_reviews(
            decisions,
            domain="SAF-T invoice export validation",
            document_hash=run_stable_hash(current_text),
            reviewer_role=role,
            reviewer_name=actor,
        )
        st.success(f"Saved {len(saved)} human review decision(s). Future runs can retrieve these as local few-shot examples.")

    c1, c2, c3, c4 = st.columns(4)
    report_json = __import__("json").dumps(report, ensure_ascii=False, indent=2)
    doc_version = document_version_record(
        document_name="interpret_current_source",
        content=current_text,
        uploaded_by=actor,
        role=role,
        version_label="current-run",
    )
    manifest = signed_report_manifest(
        report=report,
        signer=actor,
        signer_role=role,
        document_hash=doc_version["document_hash"],
        approval_status="Signed" if can(role, "sign_report") else "Draft only - role cannot sign",
    )
    manifest_json = __import__("json").dumps(manifest, ensure_ascii=False, indent=2)
    with c1:
        st.download_button("Download final review report JSON", report_json.encode("utf-8"), "interpret_final_review_report.json", "application/json", width="stretch", key="download_interpret_final_review_report_json")
    with c2:
        st.download_button("Download signed manifest", manifest_json.encode("utf-8"), "interpret_signed_report_manifest.json", "application/json", width="stretch", key="download_interpret_signed_manifest_json")
        if not can(role, "sign_report"):
            st.caption(f"Role `{role}` cannot sign in the RBAC simulation; manifest is marked draft-only.")
    with c3:
        if st.button("Save review report locally", width="stretch"):
            path = append_review_report(report)
            record_audit_event(
                actor=actor,
                role=role,
                action="save_review_report",
                workflow="Interpret",
                document_hash=doc_version["document_hash"],
                output=report,
                metadata={"report_id": report.get("report_id"), "role_can_sign": can(role, "sign_report")},
            )
            st.success(f"Saved review report and SQLite audit event: {path}")
    with c4:
        input_hash = run_stable_hash({"current_text": current_text, "sources": [s.id for s in sources]})
        run_record = summarise_interpret_run(
            data,
            citation_rows,
            model=settings.get("model", "unknown"),
            demo_mode=bool(settings.get("demo_mode", True)),
            input_hash=input_hash,
            source_count=len(sources),
        )
        if st.button("Save run metrics locally", width="stretch"):
            path = append_run_history(run_record)
            record_audit_event(
                actor=actor,
                role=role,
                action="save_run_metrics",
                workflow="Interpret",
                document_hash=doc_version["document_hash"],
                output=run_record,
                metadata={"run_id": run_record.get("run_id")},
            )
            st.success(f"Saved run metrics and SQLite audit event: {path}")

    with st.expander("Document version hash and signed report manifest", expanded=False):
        st.json({"document_version": doc_version, "signed_report_manifest": manifest})

    runs = load_run_history(limit=20)
    st.markdown("**Compare metrics between runs**")
    if runs:
        compare_rows = compare_recent_runs(runs)
        st.dataframe(pd.DataFrame(compare_rows), width="stretch", hide_index=True)
    else:
        st.info("No saved run metrics yet. Save the current run to start a comparison history.")

    if data.get("decision_log"):
        st.markdown("**Decision log**")
        st.dataframe(pd.DataFrame(data.get("decision_log", [])), width="stretch", hide_index=True)

def _render_full_workflow_tabs(
    data: Dict[str, Any],
    current_text: str,
    previous_text: str,
    query: str,
    sources: List[SourceChunk],
    all_chunks: List[SourceChunk],
    prev_sources: List[SourceChunk],
    gold_benchmark: Dict[str, Any] | None = None,
    settings: Dict[str, Any] | None = None,
) -> None:
    pipeline = run_interpret_review_discover_pipeline(
        data,
        sources=sources,
        domain="SAF-T invoice export validation",
        include_feedback=True,
    )
    data = pipeline.output
    citation_rows = pipeline.citation_rows
    if pipeline.steps:
        with st.expander("Core pipeline status — Interpret → Review → Discover", expanded=False):
            st.dataframe(pd.DataFrame(pipeline.steps), width="stretch", hide_index=True)
    tabs = st.tabs([
        "🔍 Dashboard",
        "📊 Quality Metrics",
        "📌 Source Quote Matrix",
        "🧾 Citation Support",
        "🔁 Version Diff",
        "👥 Human Review",
        "🧑‍⚖️ Reviewer & History",
        "🧪 Benchmark",
        "📦 Full Package",
        "🛡️ Evaluation",
    ])
    with tabs[0]:
        render_compliance_dashboard(data, current_text, query, sources, all_chunks, prev_sources, citation_rows)
    with tabs[1]:
        render_quality_metrics_panel(data, citation_rows, gold_benchmark)
    with tabs[2]:
        render_source_quote_matrix(data, citation_rows, sources)
    with tabs[3]:
        render_citation_verifier(data, sources, citation_rows)
    with tabs[4]:
        render_version_diff(previous_text, current_text, data, prev_sources, sources)
    with tabs[5]:
        render_human_review_queue(data, citation_rows)
    with tabs[6]:
        render_reviewer_and_run_history(data, citation_rows, current_text, sources, settings or {})
    with tabs[7]:
        render_benchmark_panel(data, citation_rows)
    with tabs[8]:
        markdown = render_result(data, "Compliance-to-Product Package")
        render_standard_export_bar(data, "Compliance-to-Product Package")
        if st.button("Save structured export locally", key="save_interpret_export", width="stretch"):
            path = save_export_package_locally(
                workflow="Interpret",
                title="Compliance-to-Product Package",
                payload=data,
                actor=(settings or {}).get("demo_user", "demo-user"),
                role=(settings or {}).get("role", "Product Manager"),
            )
            st.success(f"Saved local export package: {path}")
    with tabs[9]:
        markdown = ""
        try:
            from services.export_service import dict_to_markdown
            markdown = dict_to_markdown(data, "Compliance-to-Product Package")
        except Exception:
            markdown = str(data)
        coverage = source_coverage(all_chunks, sources)
        evaluation = evaluate_output(data, markdown, EXPECTED, coverage, citation_rows)
        render_evaluation(evaluation, citation_rows)


def render(settings: Dict[str, Any]) -> None:
    render_demo_banner(settings.get("demo_mode", False))
    st.header("Interpret — Compliance-to-Product Studio")
    st.caption(
        "Hero project: RAG, traceability, exact source quotes, rule-based citation support checks, human review queue, version diff and benchmark panel."
    )

    with st.expander("Upload and retrieval controls", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            uploaded = st.file_uploader("Current compliance document", type=["pdf", "txt", "md"])
        with col2:
            previous = st.file_uploader("Previous version for comparison", type=["pdf", "txt", "md"])
        uploaded_gold = st.file_uploader("Optional gold obligations for precision/recall", type=["json", "csv"], help="Upload reviewer-written expected obligations for this exact document. Without this, obligation precision/recall are N/A; citation metrics still run on current output and sources.")
        with st.expander("Gold obligations template", expanded=False):
            st.caption("Use this only when you want true run-specific obligation precision/recall. The gold set should be written independently of the model output.")
            st.code(_gold_template_json(), language="json")
            st.download_button("Download gold obligations template", _gold_template_json().encode("utf-8"), "gold_obligations_template.json", "application/json", key="download_gold_obligations_template_json")
        current_text = st.text_area("Or paste current document text", value=SAMPLE_DOC, height=145)
        previous_text = st.text_area("Optional previous version text", value=PREVIOUS_DOC, height=95)
        business_context = st.text_input("Business context", value="Enterprise logistics/accounting software")
        target_module = st.text_input("Target product/module", value="SAF-T invoice export validation")
        persona = st.text_input("Primary persona", value="Compliance analyst / Product Manager")
        focus = st.text_input("Retrieval focus query", value="mandatory invoice fields validation rules reporting requirements exceptions audit evidence")
        submitted = st.button("Generate compliance-to-product package", type="primary")

    if uploaded:
        extracted, name = extract_text_from_upload(uploaded)
        if extracted:
            current_text = extracted
            current_name = name
        else:
            current_name = "pasted_current_document"
    else:
        current_name = "pasted_current_document"
    if previous:
        extracted_prev, prev_name = extract_text_from_upload(previous)
        if extracted_prev:
            previous_text = extracted_prev
            previous_name = prev_name
        else:
            previous_name = "pasted_previous_document"
    else:
        previous_name = "pasted_previous_document"

    gold_benchmark, gold_message = _parse_uploaded_gold(uploaded_gold) if 'uploaded_gold' in locals() else (None, "")
    if gold_message:
        if gold_benchmark:
            st.success(gold_message)
        else:
            st.warning(gold_message)

    query = " ".join([business_context, target_module, persona, focus])

    with st.expander("Run cost estimate", expanded=False):
        st.json(estimate_run_cost(settings["model"], current_text + "\n" + query, settings["max_output_tokens"]))

    all_chunks, sources = _prepare_sources(current_text, current_name, query, settings["top_k"], settings["embedding_model"], settings["demo_mode"])
    prev_all, prev_sources = _prepare_sources(previous_text, previous_name, query, 4, settings["embedding_model"], settings["demo_mode"]) if previous_text.strip() else ([], [])

    with st.expander("RAG source explorer", expanded=False):
        for src in sources:
            with st.expander(f"{src.id} — score {src.score:.3f} — {src.doc_name}", expanded=src.id == "S1"):
                st.markdown(highlight_terms(src.text, query), unsafe_allow_html=True)
        st.json(source_coverage(all_chunks, sources))

    if not submitted:
        st.info("Upload/paste a document and generate the package. Demo Mode avoids API cost. The preview below uses synthetic output and rule-based checks.")
        sample = demo_output()
        _render_full_workflow_tabs(sample, current_text, previous_text, query, sources, all_chunks, prev_sources, gold_benchmark, settings)
        return

    inputs = {
        "business_context": business_context,
        "target_module": target_module,
        "persona": persona,
        "focus": focus,
        "language": settings["language"],
        "detail": settings["detail"],
    }
    prompt = build_compliance_prompt(inputs, sources, prev_sources)
    try:
        start_ms = now_ms()
        data = call_model_json(prompt, settings["model"], settings["max_output_tokens"], demo_output(), settings["demo_mode"])
        latency = elapsed_ms(start_ms)
        pipeline_for_metrics = run_interpret_review_discover_pipeline(
            data,
            sources=sources,
            domain="SAF-T invoice export validation",
            include_feedback=True,
        )
        data = pipeline_for_metrics.output
        citation_rows_for_metrics = pipeline_for_metrics.citation_rows
        markdown_for_metrics = dict_to_markdown(data, "Compliance-to-Product Package")
        evaluation_for_metrics = evaluate_output(data, markdown_for_metrics, EXPECTED, source_coverage(all_chunks, sources), citation_rows_for_metrics)
        record_output_run(
            workflow="Interpret",
            settings=settings,
            input_payload={"inputs": inputs, "current_hash": run_stable_hash(current_text), "previous_hash": run_stable_hash(previous_text)},
            output_payload=data,
            evaluation=evaluation_for_metrics,
            citation_rows=citation_rows_for_metrics,
            latency_ms=latency,
            source_count=len(sources),
            metadata={"target_module": target_module, "source_document": current_name},
        )
        _render_full_workflow_tabs(data, current_text, previous_text, query, sources, all_chunks, prev_sources, gold_benchmark, settings)
    except Exception as error:
        render_openai_error(error)
