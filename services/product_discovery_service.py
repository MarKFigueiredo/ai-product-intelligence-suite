"""Service helpers for the Discover workflow.

The Streamlit page should render inputs and outputs; parsing, upstream Interpret
context summarisation, rule gates and metric preparation live here so the
workflow remains unit-testable.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from services.evaluation_service import evaluate_output
from services.product_quality_service import build_pipeline_from_discovery, compute_prd_rule_completeness
from services.qa_coverage_service import validate_negative_test_coverage

DISCOVER_EXPECTED_SECTIONS = [
    "problem_statement",
    "personas",
    "assumptions_to_test",
    "mvp_scope",
    "success_metrics",
    "jira_tickets",
    "qa_test_matrix",
    "decision_log",
]


def parse_interpret_json(raw: str) -> Dict[str, Any] | None:
    if not raw or not raw.strip():
        return None
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {"items": parsed}
    except Exception:
        return None


def summarise_interpret_context(interpret_data: Dict[str, Any] | None, *, limit: int = 8) -> str:
    if not interpret_data:
        return "No Interpret output provided."
    payload = {
        "obligations": (interpret_data.get("obligation_extraction", []) or [])[:limit],
        "requirements": (interpret_data.get("product_requirements", []) or [])[:limit],
        "validation_rules": (interpret_data.get("validation_rules", []) or [])[:limit],
        "risks": (interpret_data.get("risks", []) or [])[:limit],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def discovery_quality_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    completeness = compute_prd_rule_completeness(data)
    negative_gate = validate_negative_test_coverage(data)
    pipeline_rows = build_pipeline_from_discovery(data)
    return {
        "completeness": completeness,
        "negative_gate": negative_gate,
        "pipeline_rows": pipeline_rows,
        "release_ready": completeness.get("score", 0) >= 80 and negative_gate.get("release_gate_status") == "Pass",
    }


def evaluate_discovery_output(data: Dict[str, Any], markdown: str = "") -> Dict[str, Any]:
    return evaluate_output(data, markdown or json.dumps(data, ensure_ascii=False), DISCOVER_EXPECTED_SECTIONS)
