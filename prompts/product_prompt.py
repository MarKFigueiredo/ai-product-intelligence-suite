"""Prompt for Product Discovery Studio."""
from __future__ import annotations

import json
from typing import Dict


def build_product_prompt(inputs: Dict[str, str]) -> str:
    schema = {
        "executive_summary": "string",
        "problem_statement": "string",
        "jobs_to_be_done": [{"job": "string", "success_outcome": "string"}],
        "personas": [{"persona": "string", "pain_point": "string", "need": "string"}],
        "interpret_inputs_used": [{"obligation_id": "O1", "source": "Interpret", "how_used": "string"}],
        "compliance_pipeline": [{"obligation": "string", "requirement": "string", "jira": "string", "qa": "string", "status": "Ready/Needs review/Blocked"}],
        "assumptions_to_test": [{"assumption": "string", "why_it_matters": "string", "validation_method": "string", "risk_if_wrong": "string"}],
        "trade_off_analysis": [{"decision": "string", "option_a": "string", "option_b": "string", "recommendation": "string"}],
        "rice_prioritisation": [{"item": "string", "reach": 1, "impact": 1, "confidence": 1, "effort": 1, "rice_score": 1}],
        "mvp_scope": ["string"],
        "v2_scope": ["string"],
        "out_of_scope": ["string"],
        "dependencies": [{"dependency": "string", "owner": "string", "risk": "string"}],
        "success_metrics": [{"metric": "string", "target": "string", "measurement_method": "string"}],
        "data_model_impact": [{"object_or_field": "string", "change": "string", "risk": "string"}],
        "api_integration_impact": [{"interface": "string", "impact": "string", "open_question": "string"}],
        "gherkin_acceptance_criteria": [{"scenario": "string", "given": "string", "when": "string", "then": "string"}],
        "qa_test_matrix": [{"obligation_id": "O1", "test_case": "string", "type": "Positive/Negative/Edge", "expected_result": "string", "priority": "string"}],
        "negative_test_coverage": [{"obligation_id": "O1", "negative_test": "string", "owner": "QA", "evidence_required": "string"}],
        "qa_release_gate": {"status": "Pass/Blocked", "rule": "Every obligation requires at least one mapped negative test", "negative_test_coverage_rate": 1},
        "jira_tickets": [{"issue_type": "Epic/Story/Task", "summary": "string", "description": "string", "acceptance_criteria": "string", "priority": "string", "component": "string", "labels": "string"}],
        "prd_quality_gate": {"score": 1, "missing_items": ["string"], "recommendation": "string"},
        "decision_log": [{"decision": "string", "reason": "string", "status": "string", "owner": "string", "evidence": "string"}],
        "what_would_invalidate_this_feature": [{"signal": "string", "threshold": "string", "product_response": "string"}],
        "approval_workflow": [{"team": "Product/QA/Support/Legal/Compliance/Engineering", "approval": "string", "required_before": "string", "status": "Required/Optional/Done"}],
        "security_and_enterprise_controls": [{"control": "string", "requirement": "string", "risk_if_missing": "string"}],
        "open_questions": ["string"],
    }
    return f"""
You are a Principal Product Manager designing AI-assisted workflows for enterprise software.
Return ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Create a rigorous product discovery package.

Feature idea: {inputs.get('feature_idea','')}
Domain: {inputs.get('domain','')}
Persona: {inputs.get('persona','')}
Business context: {inputs.get('business_context','')}
Compliance context: {inputs.get('compliance_context','')}
Output language: {inputs.get('language','English')}
Detail level: {inputs.get('detail','Standard')}

Upstream Interpret output, if provided. Treat this as the source of obligations that should become product requirements, Jira tickets and QA tests:
{inputs.get('interpret_context','No Interpret output provided.')}

Premium requirements:
- Strongly link to Interpret by showing obligation → requirement → Jira → QA in compliance_pipeline.
- Use upstream Interpret obligations automatically when provided. If none are provided, still create a plausible pipeline and mark it as Needs review.
- Add a decision_log with owner, rationale and evidence.
- Add what_would_invalidate_this_feature with measurable signals and product response.
- Include assumption testing, trade-offs, RICE, success metrics, MVP/V2 split, dependencies.
- Create Jira-ready tickets with realistic fields.
- Use Gherkin acceptance criteria and QA test matrix.
- Mandatory negative test coverage: every obligation in compliance_pipeline must have at least one mapped negative/edge/failure test before the feature can be marked release-ready. Include obligation_id in QA rows.
- Add negative_test_coverage and qa_release_gate. If any obligation lacks negative coverage, set qa_release_gate.status to Blocked and name the missing obligation.
- Include approval workflow for Product, QA, Support and Legal/Compliance.
- Include security_and_enterprise_controls where this feature would need authentication, RBAC, audit, retention or secure storage.
- Include PRD quality gate, but do not rely only on model scoring. The application will also compute rule-based PRD completeness.
- Be specific to compliance-heavy enterprise software where relevant.
"""
