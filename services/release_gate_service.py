"""Release/readiness gate aggregation for compliance-to-product workflows."""
from __future__ import annotations

from typing import Any, Dict, List

from services.citation_verifier import grounding_summary
from services.qa_coverage_service import validate_negative_test_coverage


def evaluate_release_gate(output: Dict[str, Any], citation_rows: List[Dict[str, Any]] | None = None) -> Dict[str, Any]:
    citation_rows = citation_rows or []
    negative_gate = validate_negative_test_coverage(output)
    grounding = grounding_summary(citation_rows) if citation_rows else {
        "checked_claims": 0,
        "weak_or_missing_claims": 0,
        "human_review_required": False,
    }
    blockers: List[str] = []
    warnings: List[str] = []
    if negative_gate.get("release_gate_status") != "Pass":
        blockers.append("Mandatory negative test coverage is incomplete.")
    if grounding.get("weak_or_missing_claims", 0):
        warnings.append("Some claims have weak or missing source support.")
    if output.get("risks"):
        warnings.append("Risk register contains unresolved items.")
    status = "Blocked" if blockers else "Review required" if warnings else "Pass"
    return {
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "negative_test_gate": negative_gate,
        "grounding_summary": grounding,
    }
