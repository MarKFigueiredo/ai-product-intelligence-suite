"""Prompt for Decision Timeline Builder."""
from __future__ import annotations

import json
from typing import Dict


def build_timeline_prompt(inputs: Dict[str, str]) -> str:
    schema = {
        "executive_one_page_brief": {"what_happened": "string", "why_it_matters": "string", "current_risk": "string", "decision_needed": "string", "recommended_next_action": "string"},
        "customer_escalation_context": {"customer": "string", "escalation_id": "string", "business_impact": "string", "compliance_boundary": "string", "current_owner": "string"},
        "chronological_timeline": [{"date": "string", "timestamp": "string", "event": "string", "event_type": "Decision/Communication/Risk/Evidence/Open question/Dependency/Customer impact/Compliance impact", "actor": "string", "owner": "string", "source_or_note": "string", "severity": "Low/Medium/High", "severity_score": 1}],
        "actor_map": [{"actor": "string", "role": "string", "involvement": "string", "open_question": "string"}],
        "decision_audit_trail": [{"decision": "string", "date": "string", "timestamp": "string", "owner": "string", "evidence": "string", "open_risk": "string", "next_action": "string"}],
        "contradictions_or_inconsistencies": [{"item": "string", "why_it_matters": "string", "severity": "Low/Medium/High", "severity_score": 1, "recommended_check": "string"}],
        "risk_register": [{"risk": "string", "severity_score": 1, "likelihood": "Low/Medium/High", "impact": "Low/Medium/High", "mitigation": "string", "owner": "string", "due_date": "string"}],
        "missing_information": ["string"],
        "postmortem_summary": {"root_cause_hypothesis": "string", "contributing_factors": ["string"], "what_went_well": ["string"], "what_failed": ["string"], "prevention_actions": [{"action": "string", "owner": "string", "due_date": "string", "evidence_required": "string"}]},
        "recommended_next_actions": [{"action": "string", "owner": "string", "priority": "Low/Medium/High", "due_date": "string", "evidence_required": "string"}],
    }
    return f"""
You are an AI Decision Timeline Builder for Product Ops, customer escalations, release incidents, compliance changes and postmortems.
Return ONLY valid JSON matching this schema:
{json.dumps(schema, indent=2)}

Incident / decision notes:
{inputs.get('raw_notes','')}

Incident mode: {inputs.get('incident_mode','')}
Business context: {inputs.get('business_context','')}
Stakeholders: {inputs.get('stakeholders','')}
Output language: {inputs.get('language','English')}
Detail level: {inputs.get('detail','Standard')}

Premium requirements:
- Do not frame this as a legal tool. Frame it as Product Ops / incident intelligence.
- Parse logs, Slack/Jira/Git-style notes when present.
- Create a stronger customer escalation context and explicit compliance boundary.
- Every timeline event must include owner, timestamp and severity_score from 1 to 10.
- Detect contradictions semantically, not only exact wording.
- Include actor map, decision audit trail, severity scoring, executive one-page brief and actionable postmortem.
- Recommended actions must include owner, due date and evidence_required.
"""
