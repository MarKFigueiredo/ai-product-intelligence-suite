"""Rule-based PRD completeness checks for the Discover workflow."""
from __future__ import annotations

from typing import Any, Dict, List

from services.qa_coverage_service import validate_negative_test_coverage


def compute_prd_rule_completeness(data: Dict[str, Any]) -> Dict[str, Any]:
    """Score PRD completeness with deterministic rules instead of LLM self-rating."""
    negative_gate = validate_negative_test_coverage(data)
    negative_ok = negative_gate.get("release_gate_status") == "Pass"
    negative_detail = (
        f"{negative_gate.get('negative_test_coverage_rate', 0)}% obligation-level negative coverage; "
        f"missing: {', '.join(negative_gate.get('missing_negative_coverage', []) or []) or 'none'}."
    )
    rules = [
        ("Problem statement", bool(data.get("problem_statement")), "Clear problem statement is present."),
        ("Persona / JTBD", bool(data.get("personas") or data.get("jobs_to_be_done")), "Persona or job-to-be-done exists."),
        ("Assumptions", bool(data.get("assumptions_to_test")), "Assumptions include validation method and risk."),
        ("Trade-off analysis", bool(data.get("trade_off_analysis")), "At least one product trade-off is documented."),
        ("Success metrics", bool(data.get("success_metrics")), "Success metrics include target and measurement method."),
        ("Jira handoff", bool(data.get("jira_tickets")), "Jira-ready delivery items are present."),
        ("QA coverage", bool(data.get("qa_test_matrix") or data.get("gherkin_acceptance_criteria")), "QA matrix or Gherkin criteria are present."),
        ("Mandatory negative test coverage", negative_ok, negative_detail),
        ("Obligation → requirement → Jira → QA pipeline", bool(data.get("compliance_pipeline")), "Traceability pipeline exists."),
        ("Decision log", bool(data.get("decision_log")), "Decision log captures rationale and status."),
        ("Invalidation criteria", bool(data.get("what_would_invalidate_this_feature")), "Feature kill/invalidating evidence is explicit."),
        ("Approval workflow", bool(data.get("approval_workflow")), "Cross-functional approvals are named."),
        ("Enterprise controls", bool(data.get("security_and_enterprise_controls")), "Security/compliance product controls are considered."),
    ]
    rows: List[Dict[str, Any]] = []
    passed = 0
    for name, ok, detail in rules:
        passed += 1 if ok else 0
        rows.append({"rule": name, "status": "Pass" if ok else "Missing", "detail": detail if ok else f"Missing: {detail}"})
    score = round((passed / len(rules)) * 100) if rules else 0
    return {
        "score": score,
        "passed": passed,
        "total": len(rules),
        "missing": [row["rule"] for row in rows if row["status"] == "Missing"],
        "rows": rows,
        "negative_test_gate": negative_gate,
        "method_note": "Deterministic rule-based completeness check. This complements, but does not rely on, the model-generated PRD quality gate. v19 blocks release-ready status when any obligation lacks mapped negative test coverage.",
    }


def build_pipeline_from_discovery(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return explicit pipeline rows or derive a compact fallback from Jira/QA rows."""
    explicit = data.get("compliance_pipeline")
    if isinstance(explicit, list) and explicit:
        return explicit
    tickets = data.get("jira_tickets", []) or []
    tests = data.get("qa_test_matrix", []) or data.get("gherkin_acceptance_criteria", []) or []
    rows: List[Dict[str, Any]] = []
    for idx, ticket in enumerate(tickets[:6]):
        test = tests[idx] if idx < len(tests) and isinstance(tests[idx], dict) else {}
        rows.append(
            {
                "obligation": "Needs explicit Interpret link",
                "requirement": ticket.get("summary") or ticket.get("description") or "Requirement",
                "jira": ticket.get("summary") or ticket.get("issue_type") or "Jira item",
                "qa": test.get("test_case") or test.get("scenario") or "QA scenario required",
                "status": "Derived fallback",
            }
        )
    return rows
