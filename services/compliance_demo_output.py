"""Pure demo-output artifact builder for the compliance studio.

This module was extracted from the Streamlit compliance studio page so
the demo artifact payload can be tested independently from UI rendering.
"""

from __future__ import annotations

from __future__ import annotations
from typing import Any, Dict, List
import pandas as pd
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
from services.openai_service import call_model_json, embed_texts
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

def build_demo_output() -> Dict[str, Any]:
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
